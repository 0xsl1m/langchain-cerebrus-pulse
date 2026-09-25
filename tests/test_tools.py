"""LangChain tools against a mocked Cerebrus Pulse API (F074, F026).

HTTP is mocked with httpx.MockTransport under the SDK client; payments are
signed locally by the real x402 client with a fake, never-funded key. Nothing
touches the network and no payment can settle.
"""

import base64
import json
import re
from decimal import Decimal
from pathlib import Path

import httpx
import pytest
from cerebrus_pulse import INDICATIVE_PRICES_USD, CerebrusPulse
from cerebrus_pulse.payment import DEFAULT_ALLOWED_PAYTO
from langchain_core.tools import BaseTool

import langchain_cerebrus_pulse as lcp
from langchain_cerebrus_pulse import (
    CerebrusFundingTool,
    CerebrusListCoinsTool,
    CerebrusPulseTool,
    CerebrusScreenerTool,
    CerebrusSentimentTool,
)

ROOT = Path(__file__).resolve().parent.parent
TOOLS = [getattr(lcp, name) for name in lcp.__all__]
PAID_TOOLS = [t for t in TOOLS if t is not CerebrusListCoinsTool]
DUMMY_KEY = "0x" + "11" * 32  # obviously fake, never funded
PAY_TO = DEFAULT_ALLOWED_PAYTO  # the SDK's default payee, so a payTo change is made once
BASE_USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"

# Real engine output for /funding (gateway service/response_examples.json).
FUNDING = {
    "coin": "BTC", "records": 23, "lookback_hours": 24, "avg_funding_rate": 8.1e-06,
    "annualized_pct": 0.89, "current": 1.25e-05, "min": -7.23e-06, "max": 1.25e-05,
    "positive_pct": 82.6, "endpoint": "funding",
    "meta": {"provider": "Cerebrus Pulse", "offering": "pulse_funding", "execution_ms": 0.0},
}


def key(tool_cls) -> str:
    """The SDK method / price key for a tool: cerebrus_cex_dex -> cex_dex."""
    return tool_cls.model_fields["name"].default.removeprefix("cerebrus_")


def gateway_402(request: httpx.Request, usd: str, pay_to: str = PAY_TO) -> httpx.Response:
    """A 402 as the gateway sends it: v2 terms in PAYMENT-REQUIRED plus a v1 body."""
    amount = str(int(Decimal(usd) * 1_000_000))
    offer = {"scheme": "exact", "network": "eip155:8453", "asset": BASE_USDC,
             "amount": amount, "payTo": pay_to, "maxTimeoutSeconds": 300,
             "extra": {"name": "USD Coin", "version": "2"}}
    required = {"x402Version": 2, "resource": {"url": str(request.url)}, "accepts": [offer]}
    body = {"x402Version": 1, "error": "Payment required", "accepts": [{
        "scheme": "exact", "network": "base", "maxAmountRequired": amount,
        "resource": str(request.url), "description": "", "mimeType": "application/json",
        "payTo": pay_to, "maxTimeoutSeconds": 300, "asset": BASE_USDC,
        "extra": {"name": "USD Coin", "version": "2"}}]}
    header = base64.b64encode(json.dumps(required).encode()).decode()
    return httpx.Response(402, json=body, headers={"PAYMENT-REQUIRED": header})


class FakeAPI:
    """Paid paths answer 402 until a PAYMENT-SIGNATURE arrives, then ``data``."""

    def __init__(self, data: dict, pay_to: str = PAY_TO):
        self.data = data
        self.pay_to = pay_to
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if request.url.path in ("/coins", "/health"):
            return httpx.Response(200, json=self.data)
        if request.headers.get("PAYMENT-SIGNATURE"):
            return httpx.Response(200, json=self.data)
        path = request.url.path.strip("/").split("/")[0].replace("-", "_")
        price = INDICATIVE_PRICES_USD["stress" if path == "arb" else path]
        return gateway_402(request, str(price), self.pay_to)


def client_for(api: FakeAPI, **kwargs) -> CerebrusPulse:
    client = CerebrusPulse(**kwargs)
    client._transport = httpx.MockTransport(api)
    return client


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in ("CEREBRUS_MAX_PAYMENT_USD", "CEREBRUS_MAX_SPEND_USD",
                 "CEREBRUS_ALLOWED_PAYTO", "CEREBRUS_ALLOWED_PAYTO_SOLANA"):
        monkeypatch.delenv(name, raising=False)


# ── Package metadata ────────────────────────────────────────────────────────

def test_version_comes_from_the_package_metadata():
    from importlib.metadata import version

    assert lcp.__version__ == version("langchain-cerebrus-pulse")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{lcp.__version__}"' in pyproject


def test_sdk_floor_has_every_method_the_tools_call():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert '"cerebrus-pulse>=0.4.0,<0.5"' in pyproject
    source = (ROOT / "src" / "langchain_cerebrus_pulse" / "tools.py").read_text(encoding="utf-8")
    for method in set(re.findall(r"self\._api\(\)\.(\w+)\(", source)):
        assert callable(getattr(CerebrusPulse, method)), method
    assert len(TOOLS) == 14


# ── What the model sees ─────────────────────────────────────────────────────

@pytest.mark.parametrize("tool_cls", PAID_TOOLS, ids=key)
def test_descriptions_quote_the_indicative_price(tool_cls):
    description = tool_cls().description
    assert f"about ${INDICATIVE_PRICES_USD[key(tool_cls)]} USDC" in description
    assert "indicative" in description
    assert "Cost: $" not in description
    assert "discount" not in description


def test_free_tool_has_no_price():
    assert "Free" in CerebrusListCoinsTool().description
    assert "$" not in CerebrusListCoinsTool().description


def test_input_docs_match_the_api():
    pulse_args = CerebrusPulseTool().args
    assert "5m, 15m, 1h, 4h, 1d, 1w" in pulse_args["timeframes"]["description"]
    assert "(1-50)" in CerebrusScreenerTool().args["top_n"]["description"]


def test_sentiment_description_matches_the_bucketed_label():
    description = CerebrusSentimentTool().description
    assert "bucketed label" in description
    assert "fear/greed" not in description


def test_every_tool_is_a_current_langchain_tool():
    for tool_cls in TOOLS:
        tool = tool_cls()
        assert isinstance(tool, BaseTool)
        assert tool.name.startswith("cerebrus_")


# ── Calling the API ─────────────────────────────────────────────────────────

def test_tool_uses_the_given_client_and_returns_engine_data():
    api = FakeAPI(FUNDING)
    tool = CerebrusFundingTool(client=client_for(api, wallet_key=DUMMY_KEY))

    out = json.loads(tool.invoke({"coin": "BTC", "lookback_hours": 24}))

    assert out["current"] == 1.25e-05
    assert out["records"] == 23
    assert api.requests[-1].url.path == "/funding/BTC"


def test_without_a_wallet_a_paid_tool_returns_the_402_terms():
    api = FakeAPI(FUNDING)
    tool = CerebrusFundingTool(client=client_for(api))

    out = json.loads(tool.invoke({"coin": "BTC"}))

    assert out["payment_required"] is True
    assert out["price_usd"] == "0.01"  # read from the 402, not hard-coded
    assert out["payment_terms"][0]["pay_to"] == PAY_TO
    assert out["payment_terms"][0]["network"] == "eip155:8453"
    assert len(api.requests) == 1


def test_the_price_reported_is_whatever_the_402_says():
    client = CerebrusPulse()
    client._transport = httpx.MockTransport(lambda request: gateway_402(request, "0.07"))

    out = json.loads(CerebrusFundingTool(client=client).invoke({"coin": "BTC"}))

    assert out["price_usd"] == "0.07"


def test_a_paying_client_pays_with_payment_signature():
    api = FakeAPI({"coin": "BTC", "price": {"current": 84512.5}, "timeframes": {}})
    client = client_for(api, wallet_key=DUMMY_KEY)

    out = json.loads(CerebrusPulseTool(client=client).invoke({"coin": "BTC"}))

    assert out["price"]["current"] == 84512.5
    paid = api.requests[-1]
    assert "PAYMENT-SIGNATURE" in paid.headers
    assert "X-PAYMENT" not in paid.headers
    assert client.spent_usd == Decimal("0.025")


def test_tools_sharing_a_client_share_its_budget():
    api = FakeAPI({"sentiment": {"label": "bullish", "as_of": 1790269024.0}})
    client = client_for(api, wallet_key=DUMMY_KEY, max_spend_usd="0.03")

    CerebrusPulseTool(client=client).invoke({"coin": "BTC"})
    out = json.loads(CerebrusSentimentTool(client=client).invoke({}))

    assert out["payment_required"] is True
    assert "CEREBRUS_MAX_SPEND_USD" in out["reason"]
    assert client.spent_usd == Decimal("0.025")


def test_parallel_tool_calls_stay_inside_the_shared_budget():
    # create_agent's ToolNode runs one message's tool calls in parallel threads.
    agents = pytest.importorskip("langchain.agents")
    from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
    from langchain_core.messages import AIMessage, ToolMessage

    class ScriptedModel(GenericFakeChatModel):
        def bind_tools(self, tools, **kwargs):
            return self

    calls = [{"name": "cerebrus_pulse", "args": {"coin": "BTC"}, "id": f"call_{i}"}
             for i in range(6)]
    model = ScriptedModel(messages=iter([
        AIMessage(content="", tool_calls=calls), AIMessage(content="done")]))
    api = FakeAPI({"coin": "BTC", "timeframes": {}})
    client = client_for(api, wallet_key=DUMMY_KEY, max_spend_usd="0.05")

    agent = agents.create_agent(model, tools=[CerebrusPulseTool(client=client)])
    result = agent.invoke({"messages": [{"role": "user", "content": "Full market overview"}]})

    outs = [json.loads(m.content) for m in result["messages"] if isinstance(m, ToolMessage)]
    blocked = [o for o in outs if o.get("payment_required")]
    assert len(outs) == 6 and len(blocked) == 4
    assert all("CEREBRUS_MAX_SPEND_USD" in o["reason"] for o in blocked)
    assert client.spent_usd == Decimal("0.050")
    assert sum(1 for r in api.requests if r.headers.get("PAYMENT-SIGNATURE")) == 2


def test_a_payment_to_an_unknown_payee_is_refused():
    api = FakeAPI(FUNDING, pay_to="0x000000000000000000000000000000000000dEaD")
    client = client_for(api, wallet_key=DUMMY_KEY)

    out = json.loads(CerebrusFundingTool(client=client).invoke({"coin": "BTC"}))

    assert "CEREBRUS_ALLOWED_PAYTO" in out["reason"]
    assert not any("PAYMENT-SIGNATURE" in r.headers for r in api.requests)


def test_free_tool_works_without_a_client():
    tool = CerebrusListCoinsTool()
    assert tool.client is None
    api = FakeAPI({"coins": ["BTC", "ETH"]})
    tool = CerebrusListCoinsTool(client=client_for(api))
    assert json.loads(tool.invoke({})) == {"coins": ["BTC", "ETH"], "count": 2}


def test_client_is_not_serialized():
    tool = CerebrusListCoinsTool(client=CerebrusPulse())
    assert "client" not in tool.model_dump()


# ── README ──────────────────────────────────────────────────────────────────

def test_readme_uses_the_current_agent_api():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "from langchain.agents import create_agent" in readme
    assert "AgentExecutor" not in readme
    assert "create_tool_calling_agent" not in readme


def test_readme_price_table_matches_the_sdk():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    rows = dict(re.findall(r"^\| `(Cerebrus\w+Tool)` \| \$([0-9.]+) \|", readme, re.M))
    expected = {t.__name__: INDICATIVE_PRICES_USD[key(t)] for t in PAID_TOOLS}
    assert {k: Decimal(v) for k, v in rows.items()} == expected
    assert "discount" not in readme


def test_readme_agent_example_runs_with_create_agent():
    agents = pytest.importorskip("langchain.agents")
    from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
    from langchain_core.messages import AIMessage, ToolMessage

    class ScriptedModel(GenericFakeChatModel):
        def bind_tools(self, tools, **kwargs):
            return self

    model = ScriptedModel(messages=iter([
        AIMessage(content="", tool_calls=[
            {"name": "cerebrus_funding", "args": {"coin": "BTC"}, "id": "call_1"}]),
        AIMessage(content="BTC funding is mildly positive."),
    ]))
    api = FakeAPI(FUNDING)
    client = client_for(api, wallet_key=DUMMY_KEY)
    tools = [tool(client=client) for tool in (CerebrusListCoinsTool, CerebrusFundingTool)]

    agent = agents.create_agent(model, tools=tools, system_prompt="You are a crypto analyst.")
    result = agent.invoke({"messages": [{"role": "user", "content": "BTC funding?"}]})

    tool_messages = [m for m in result["messages"] if isinstance(m, ToolMessage)]
    assert json.loads(tool_messages[0].content)["current"] == 1.25e-05
    assert result["messages"][-1].content == "BTC funding is mildly positive."
    assert client.spent_usd == Decimal("0.01")
