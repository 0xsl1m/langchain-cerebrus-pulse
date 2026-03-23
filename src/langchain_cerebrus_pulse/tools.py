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


class ScreenerInput(BaseModel):
    top_n: int = Field(default=30, description="Number of top coins (1-30)")


class CoinInput(BaseModel):
    coin: str = Field(description="Coin ticker (e.g., BTC, ETH, SOL)")


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


class CerebrusScreenerTool(BaseTool):
    name: str = "cerebrus_screener"
    description: str = (
        "Scan all 30+ coins for top trading signals. Returns RSI, trend, "
        "volatility regime, funding bias, confluence, and OI trend. "
        "Cost: $0.04 USDC via x402."
    )
    args_schema: type[BaseModel] = ScreenerInput

    def _run(self, top_n: int = 30) -> str:
        try:
            result = _get_client().screener(top_n)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return json.dumps({"error": str(e)})


class CerebrusOITool(BaseTool):
    name: str = "cerebrus_oi"
    description: str = (
        "Get open interest analysis for a Hyperliquid perpetual. "
        "Returns OI delta, percentile, trend, and price-OI divergence. "
        "Cost: $0.01 USDC via x402."
    )
    args_schema: type[BaseModel] = CoinInput

    def _run(self, coin: str) -> str:
        try:
            result = _get_client().oi(coin)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return json.dumps({"error": str(e)})


class CerebrusSpreadTool(BaseTool):
    name: str = "cerebrus_spread"
    description: str = (
        "Get spread and liquidity analysis for a Hyperliquid perpetual. "
        "Returns bid-ask spread, slippage at various sizes, liquidity score. "
        "Cost: $0.008 USDC via x402."
    )
    args_schema: type[BaseModel] = CoinInput

    def _run(self, coin: str) -> str:
        try:
            result = _get_client().spread(coin)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return json.dumps({"error": str(e)})


class CerebrusCorrelationTool(BaseTool):
    name: str = "cerebrus_correlation"
    description: str = (
        "Get BTC-altcoin correlation matrix for top 15 Hyperliquid perpetuals. "
        "Returns correlations, regime, and sector averages. "
        "Cost: $0.03 USDC via x402."
    )

    def _run(self) -> str:
        try:
            result = _get_client().correlation()
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return json.dumps({"error": str(e)})


class StressInput(BaseModel):
    limit: int = Field(default=10, description="Recent scans to analyze (1-50)")


class CerebrusStressTool(BaseTool):
    name: str = "cerebrus_stress"
    description: str = (
        "Get market stress index from cross-chain arbitrage detection across 8 chains. "
        "Returns stress level (LOW/MODERATE/HIGH/EXTREME), score, spread statistics, "
        "and chain routes with price dislocations. Cost: $0.015 USDC via x402."
    )
    args_schema: type[BaseModel] = StressInput

    def _run(self, limit: int = 10) -> str:
        try:
            result = _get_client().stress(limit)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return json.dumps({"error": str(e)})


class CerebrusCexDexTool(BaseTool):
    name: str = "cerebrus_cex_dex"
    description: str = (
        "Get CEX-DEX price divergence for a token. Compares Coinbase vs "
        "Chainlink/Uniswap prices. Returns spread in bps and direction. "
        "Cost: $0.02 USDC via x402."
    )
    args_schema: type[BaseModel] = CoinInput

    def _run(self, coin: str) -> str:
        try:
            result = _get_client().cex_dex(coin)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return json.dumps({"error": str(e)})


class CerebrusBasisTool(BaseTool):
    name: str = "cerebrus_basis"
    description: str = (
        "Get Chainlink basis analysis — Hyperliquid perp oracle vs Chainlink spot. "
        "Returns basis in bps, direction, and contrarian signal. "
        "Cost: $0.02 USDC via x402."
    )
    args_schema: type[BaseModel] = CoinInput

    def _run(self, coin: str) -> str:
        try:
            result = _get_client().basis(coin)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return json.dumps({"error": str(e)})


class CerebrusDepegTool(BaseTool):
    name: str = "cerebrus_depeg"
    description: str = (
        "Get USDC collateral health via Chainlink oracle. "
        "Reports peg status, deviation, risk level, and Arbitrum sequencer status. "
        "Cost: $0.01 USDC via x402."
    )

    def _run(self) -> str:
        try:
            result = _get_client().depeg()
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return json.dumps({"error": str(e)})
