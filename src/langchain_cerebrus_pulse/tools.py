"""LangChain tool wrappers for Cerebrus Pulse API."""

from __future__ import annotations

import json
from typing import Optional

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from cerebrus_pulse import CerebrusPulse
from cerebrus_pulse.client import CerebrusPulseError


def _get_client() -> CerebrusPulse:
    return CerebrusPulse()


class PulseInput(BaseModel):
    coin: str = Field(description="Coin ticker (e.g., BTC, ETH, SOL)")
    timeframes: str = Field(default="1h,4h", description="Comma-separated: 15m, 1h, 4h")


class FundingInput(BaseModel):
    coin: str = Field(description="Coin ticker (e.g., BTC, ETH, SOL)")
    lookback_hours: int = Field(default=24, description="Hours of history (1-168)")


class BundleInput(BaseModel):
    coin: str = Field(description="Coin ticker (e.g., BTC, ETH, SOL)")
    timeframes: str = Field(default="1h,4h", description="Comma-separated: 15m, 1h, 4h")


class CerebrusListCoinsTool(BaseTool):
    name: str = "cerebrus_list_coins"
    description: str = (
        "List all available coins on Cerebrus Pulse. "
        "Returns tickers for 30+ Hyperliquid perpetuals. Free, no payment required."
    )

    def _run(self) -> str:
        try:
            coins = _get_client().coins()
            return json.dumps({"coins": coins, "count": len(coins)})
        except CerebrusPulseError as e:
            return json.dumps({"error": str(e)})


class CerebrusPulseTool(BaseTool):
    name: str = "cerebrus_pulse"
    description: str = (
        "Get multi-timeframe technical analysis for a Hyperliquid perpetual. "
        "Returns RSI, EMAs (20/50/200), ATR, Bollinger Bands, VWAP, Z-score, "
        "trend direction, confluence scoring, derivatives (funding, OI, spread), "
        "and market regime. Cost: $0.02 USDC via x402."
    )
    args_schema: type[BaseModel] = PulseInput

    def _run(self, coin: str, timeframes: str = "1h,4h") -> str:
        try:
            result = _get_client().pulse(coin, timeframes)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return json.dumps({"error": str(e)})


class CerebrusSentimentTool(BaseTool):
    name: str = "cerebrus_sentiment"
    description: str = (
        "Get aggregated crypto market sentiment. Returns overall sentiment, "
        "fear/greed, momentum, and funding bias. Not coin-specific. "
        "Cost: $0.01 USDC via x402."
    )

    def _run(self) -> str:
        try:
            result = _get_client().sentiment()
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return json.dumps({"error": str(e)})


class CerebrusFundingTool(BaseTool):
    name: str = "cerebrus_funding"
    description: str = (
        "Get funding rate analysis for a Hyperliquid perpetual. "
        "Returns current rate, annualized %, historical min/max/average. "
        "Cost: $0.01 USDC via x402."
    )
    args_schema: type[BaseModel] = FundingInput

    def _run(self, coin: str, lookback_hours: int = 24) -> str:
        try:
            result = _get_client().funding(coin, lookback_hours)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return json.dumps({"error": str(e)})


class CerebrusBundleTool(BaseTool):
    name: str = "cerebrus_bundle"
    description: str = (
        "Get complete analysis bundle: technical analysis + sentiment + funding "
        "in one call. 20% discount vs individual endpoints. "
        "Cost: $0.04 USDC via x402."
    )
    args_schema: type[BaseModel] = BundleInput

    def _run(self, coin: str, timeframes: str = "1h,4h") -> str:
        try:
            result = _get_client().bundle(coin, timeframes)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return json.dumps({"error": str(e)})
