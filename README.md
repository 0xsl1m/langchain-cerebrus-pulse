
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

LangChain tools for [Cerebrus Pulse](https://cerebruspulse.xyz) — real-time crypto intelligence for AI agents. 50+ Hyperliquid perpetuals via x402 micropayments.

## Install

```bash
pip install langchain-cerebrus-pulse
```

## Quick Start

```python
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

# Add to your agent's tools
tools = [
    CerebrusListCoinsTool(),      # Free
    CerebrusPulseTool(),          # $0.025/query
    CerebrusScreenerTool(),       # $0.06/query — scan all coins
    CerebrusLiquidationsTool(),   # $0.03/query — liquidation heatmap
    CerebrusStressTool(),         # $0.015/query — market stress index
    CerebrusCexDexTool(),         # $0.02/query — CEX-DEX divergence
    CerebrusBasisTool(),          # $0.02/query — Chainlink basis
    CerebrusDepegTool(),          # $0.01/query — USDC peg health
    CerebrusSentimentTool(),      # $0.01/query
    CerebrusFundingTool(),        # $0.01/query
    CerebrusOITool(),             # $0.01/query
    CerebrusSpreadTool(),         # $0.008/query
    CerebrusCorrelationTool(),    # $0.03/query
    CerebrusBundleTool(),         # $0.05/query
]
```

## With a LangChain Agent

```python
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_cerebrus_pulse import (
    CerebrusListCoinsTool, CerebrusPulseTool,
    CerebrusLiquidationsTool, CerebrusStressTool,
)

llm = ChatOpenAI(model="gpt-4o")
tools = [
    CerebrusListCoinsTool(),
    CerebrusPulseTool(),
    CerebrusLiquidationsTool(),
    CerebrusStressTool(),
]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a crypto analyst with access to real-time Hyperliquid data via Cerebrus Pulse."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)

result = executor.invoke({"input": "Where are the BTC liquidation clusters and what's the cascade risk?"})
print(result["output"])
```

## Available Tools (14)

| Tool | Cost | Description |
|------|------|-------------|
| `CerebrusListCoinsTool` | Free | List 50+ available Hyperliquid perpetuals |
| `CerebrusPulseTool` | $0.025 | Technical analysis (RSI, EMAs, Bollinger, trend, regime, confluence) |
| `CerebrusScreenerTool` | $0.06 | Scan 50+ coins: signals, trends, vol regime, confluence |
| `CerebrusLiquidationsTool` | $0.03 | Liquidation heatmap by leverage tier with cascade risk |
| `CerebrusStressTool` | $0.015 | Cross-chain market stress index (8 chains) |
| `CerebrusCexDexTool` | $0.02 | CEX-DEX price divergence (Coinbase vs Chainlink/Uniswap) |
| `CerebrusBasisTool` | $0.02 | Chainlink basis: HL perp oracle vs Chainlink spot |
| `CerebrusDepegTool` | $0.01 | USDC collateral health via Chainlink oracle |
| `CerebrusSentimentTool` | $0.01 | Market sentiment (fear/greed, momentum, funding bias) |
| `CerebrusFundingTool` | $0.01 | Funding rates with historical data |
| `CerebrusOITool` | $0.01 | Open interest: delta, percentile, trend, divergence |
| `CerebrusSpreadTool` | $0.008 | Spread: slippage estimates at various sizes, liquidity score |
| `CerebrusCorrelationTool` | $0.03 | BTC-alt correlation matrix with regime classification |
| `CerebrusBundleTool` | $0.05 | All data combined (9% discount) |

## Links

- [Cerebrus Pulse Docs](https://cerebruspulse.xyz/overview)
- [Python SDK](https://github.com/0xsl1m/cerebrus-pulse-python)
- [MCP Server](https://github.com/0xsl1m/cerebrus-pulse-mcp)

## Disclaimer

Cerebrus Pulse provides market data and technical indicators for **informational purposes only**. Nothing provided by these tools or the underlying API constitutes financial advice, investment advice, or trading advice. AI-generated analysis, signals, and sentiment labels are algorithmic outputs — not recommendations to buy, sell, or hold any asset. Cryptocurrency trading involves substantial risk of loss. You are solely responsible for your own trading decisions.

## License

MIT
