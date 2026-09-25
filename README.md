
```
     ░█████╗░███████╗██████╗░███████╗██████╗░██████╗░██╗░░░██╗░██████╗
     ██╔══██╗██╔════╝██╔══██╗██╔════╝██╔══██╗██╔══██╗██║░░░██║██╔════╝
     ██║░░╚═╝█████╗░░██████╔╝█████╗░░██████╦╝██████╔╝██║░░░██║╚█████╗░
     ██║░░██╗██╔══╝░░██╔══██╗██╔══╝░░██╔══██╗██╔══██╗██║░░░██║░╚═══██╗
     ╚█████╔╝███████╗██║░░██║███████╗██████╦╝██║░░██║╚██████╔╝██████╔╝
     ░╚════╝░╚══════╝╚═╝░░╚═╝╚══════╝╚═════╝░╚═╝░░╚═╝░╚═════╝░╚═════╝░

     ─────╮    ╭──╮         ╭──╮    ╭──╮         ╭──╮    ╭─────
          │    │  │         │  │    │  │         │  │    │
     ─────╯────╯  ╰─────────╯  ╰────╯  ╰─────────╯  ╰────╯─────

              ██████╗░██╗░░░██╗██╗░░░░░░██████╗███████╗
              ██╔══██╗██║░░░██║██║░░░░░██╔════╝██╔════╝
              ██████╔╝██║░░░██║██║░░░░░╚█████╗░█████╗░░
              ██╔═══╝░██║░░░██║██║░░░░░░╚═══██╗██╔══╝░░
              ██║░░░░░╚██████╔╝███████╗██████╔╝███████╗
              ╚═╝░░░░░░╚═════╝░╚══════╝╚═════╝░╚══════╝

          crypto intelligence for AI agents · x402 micropayments
```

# LangChain Cerebrus Pulse

LangChain tools for [Cerebrus Pulse](https://cerebruspulse.xyz) — real-time crypto intelligence for AI agents. 50+ Hyperliquid perpetuals, paid per call in USDC over [x402](https://x402.org).

## Install

```bash
pip install langchain-cerebrus-pulse          # tools; paid ones report the price instead of paying
pip install "langchain-cerebrus-pulse[pay]"   # + automatic payment in USDC on Base
pip install "langchain-cerebrus-pulse[svm]"   # + automatic payment in USDC on Solana too
```

Requires `langchain-core` 1.x and the [`cerebrus-pulse`](https://github.com/0xsl1m/cerebrus-pulse-python) SDK 0.4.

## Quick Start

Build one `CerebrusPulse` client and hand it to every tool. With a wallet key it pays for paid tools automatically, and all tools share its spend limits.

```python
import os
from cerebrus_pulse import CerebrusPulse
from langchain_cerebrus_pulse import (
    CerebrusListCoinsTool,
    CerebrusPulseTool,
    CerebrusSentimentTool,
    CerebrusFundingTool,
    CerebrusBundleTool,
    CerebrusScreenerTool,
    CerebrusOITool,
    CerebrusSpreadTool,
    CerebrusCorrelationTool,
    CerebrusLiquidationsTool,
    CerebrusStressTool,
    CerebrusCexDexTool,
    CerebrusBasisTool,
    CerebrusDepegTool,
)

# A dedicated, low-balance Base wallet holding a little USDC. Omit wallet_key
# and paid tools return the API's price and payee instead of data.
client = CerebrusPulse(
    wallet_key=os.environ["CEREBRUS_WALLET_KEY"],
    max_payment_usd="0.10",  # most one call may cost
    max_spend_usd="1.00",    # most this client may spend in total
)

tools = [
    tool(client=client)
    for tool in (
        CerebrusListCoinsTool, CerebrusPulseTool, CerebrusScreenerTool,
        CerebrusLiquidationsTool, CerebrusStressTool, CerebrusCexDexTool,
        CerebrusBasisTool, CerebrusDepegTool, CerebrusSentimentTool,
        CerebrusFundingTool, CerebrusOITool, CerebrusSpreadTool,
        CerebrusCorrelationTool, CerebrusBundleTool,
    )
]
```

The spend limits also read `CEREBRUS_MAX_PAYMENT_USD`, `CEREBRUS_MAX_SPEND_USD` and `CEREBRUS_ALLOWED_PAYTO`; payments only go to the API's published payee. See the [SDK README](https://github.com/0xsl1m/cerebrus-pulse-python#paying-for-endpoints-x402) for Solana and the full list.

## With a LangChain Agent

```python
from langchain.agents import create_agent

agent = create_agent(
    "openai:gpt-4o",  # any chat model that supports tool calling
    tools=tools,
    system_prompt="You are a crypto analyst with access to real-time Hyperliquid data via Cerebrus Pulse.",
)

result = agent.invoke({
    "messages": [
        {"role": "user", "content": "Where are the BTC liquidation clusters and what's the cascade risk?"}
    ]
})
print(result["messages"][-1].content)
print(f"Spent: ${client.spent_usd}")
```

When a paid tool cannot pay, it returns JSON the model can read: `{"error": ..., "payment_required": true, "price_usd": "0.03", "payment_terms": [...]}`. A refusal by the spend limits adds a `reason`, and nothing is signed.

## Available Tools (14)

Prices are indicative, per call, in USDC, as the API published them on 2026-09-24. The API sets the price: its 402 terms say what is charged, and the client's `max_payment_usd` caps what is paid.

| Tool | Price | Description |
|------|------|-------------|
| `CerebrusListCoinsTool` | Free | List 50+ available Hyperliquid perpetuals |
| `CerebrusPulseTool` | $0.025 | Technical analysis (RSI, EMAs, Bollinger, trend, regime, confluence) |
| `CerebrusScreenerTool` | $0.06 | Scan 50+ coins: signals, trends, vol regime, confluence |
| `CerebrusLiquidationsTool` | $0.03 | Liquidation heatmap by leverage tier with cascade risk |
| `CerebrusStressTool` | $0.02 | Cross-chain market stress index (8 chains) |
| `CerebrusCexDexTool` | $0.02 | CEX-DEX price divergence (Coinbase vs Chainlink/Uniswap) |
| `CerebrusBasisTool` | $0.02 | Chainlink basis: HL perp oracle vs Chainlink spot |
| `CerebrusDepegTool` | $0.01 | USDC collateral health via Chainlink oracle |
| `CerebrusSentimentTool` | $0.01 | Market sentiment as a bucketed label (very_bearish … very_bullish) |
| `CerebrusFundingTool` | $0.01 | Funding rate: current, average, min, max, annualized |
| `CerebrusOITool` | $0.015 | Open interest: delta, percentile, trend, divergence |
| `CerebrusSpreadTool` | $0.015 | Spread: slippage estimates at various sizes, liquidity score |
| `CerebrusCorrelationTool` | $0.05 | BTC-alt correlation matrix with regime classification |
| `CerebrusBundleTool` | $0.05 | Pulse, sentiment and funding in one call |

## Links

- [Cerebrus Pulse Docs](https://cerebruspulse.xyz/overview)
- [Python SDK](https://github.com/0xsl1m/cerebrus-pulse-python)
- [MCP Server](https://github.com/0xsl1m/cerebrus-pulse-mcp)

## Disclaimer

Cerebrus Pulse provides market data and technical indicators for **informational purposes only**. Nothing provided by these tools or the underlying API constitutes financial advice, investment advice, or trading advice. AI-generated analysis, signals, and sentiment labels are algorithmic outputs — not recommendations to buy, sell, or hold any asset. Cryptocurrency trading involves substantial risk of loss. You are solely responsible for your own trading decisions.

## License

MIT
