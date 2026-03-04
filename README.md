# LangChain Cerebrus Pulse

LangChain tools for [Cerebrus Pulse](https://pulse.openclaw.ai) — real-time crypto intelligence for AI agents.

## Install

```bash
pip install langchain-cerebrus-pulse
```

## Quick Start

```python
from langchain_cerebrus_pulse import (
    CerebrusPulseTool,
    CerebrusSentimentTool,
    CerebrusFundingTool,
    CerebrusBundleTool,
    CerebrusListCoinsTool,
    CerebrusScreenerTool,
    CerebrusOITool,
    CerebrusSpreadTool,
    CerebrusCorrelationTool,
)

# Add to your agent's tools
tools = [
    CerebrusListCoinsTool(),      # Free
    CerebrusPulseTool(),          # $0.02/query
    CerebrusSentimentTool(),      # $0.01/query
    CerebrusFundingTool(),        # $0.01/query
    CerebrusBundleTool(),         # $0.04/query
    CerebrusScreenerTool(),       # $0.04/query — scan all coins
    CerebrusOITool(),             # $0.01/query
    CerebrusSpreadTool(),         # $0.008/query
    CerebrusCorrelationTool(),    # $0.03/query
]
```

## With a LangChain Agent

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_cerebrus_pulse import CerebrusPulseTool, CerebrusBundleTool, CerebrusListCoinsTool

llm = ChatOpenAI(model="gpt-4o")
tools = [CerebrusListCoinsTool(), CerebrusPulseTool(), CerebrusBundleTool()]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a crypto analyst with access to real-time Hyperliquid data via Cerebrus Pulse."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

result = executor.invoke({"input": "What's the technical outlook for BTC and ETH?"})
print(result["output"])
```

## Available Tools

| Tool | Cost | Description |
|------|------|-------------|
| `CerebrusListCoinsTool` | Free | List 30+ available Hyperliquid perpetuals |
| `CerebrusPulseTool` | $0.02 | Technical analysis (RSI, EMAs, Bollinger, trend, regime, confluence) |
| `CerebrusSentimentTool` | $0.01 | Market sentiment (fear/greed, momentum, funding bias) |
| `CerebrusFundingTool` | $0.01 | Funding rates with historical data |
| `CerebrusBundleTool` | $0.04 | All data combined (20% discount) |
| `CerebrusScreenerTool` | $0.04 | Scan 30+ coins: signals, trends, vol regime, confluence |
| `CerebrusOITool` | $0.01 | Open interest: delta, percentile, trend, divergence |
| `CerebrusSpreadTool` | $0.008 | Spread: slippage estimates at various sizes, liquidity score |
| `CerebrusCorrelationTool` | $0.03 | BTC-alt correlation matrix with regime classification |

## Links

- [Cerebrus Pulse Docs](https://pulse.openclaw.ai/overview)
- [Python SDK](https://github.com/0xsl1m/cerebrus-pulse-python)
- [MCP Server](https://github.com/0xsl1m/cerebrus-pulse-mcp)

## License

MIT
