"""LangChain tool wrappers for Cerebrus Pulse API."""

from __future__ import annotations

import json
from typing import Optional

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from cerebrus_pulse import (
    INDICATIVE_PRICES_USD,
    CerebrusPulse,
    CerebrusPulseError,
    PaymentBlocked,
    PaymentRequired,
)


def _cost(endpoint: str) -> str:
    """Price text for a tool description. Indicative: the API's 402 terms decide."""
    return (
        f"Paid: about ${INDICATIVE_PRICES_USD[endpoint]} USDC per call via x402 "
        "(indicative; the API's payment terms set the price)."
    )


def _error(e: CerebrusPulseError) -> str:
    """Error JSON for the agent. A 402 carries the price and payee the API asked for."""
    out: dict = {"error": str(e)}
    if isinstance(e, PaymentRequired):
        out["payment_required"] = True
        if e.price_usd is not None:
            out["price_usd"] = str(e.price_usd)
        out["payment_terms"] = [
            {"network": t.network, "pay_to": t.pay_to,
             "price_usd": str(t.price_usd) if t.price_usd is not None else None}
            for t in e.terms
        ]
        if isinstance(e, PaymentBlocked):
            out["reason"] = e.reason
    return json.dumps(out)


class _CerebrusTool(BaseTool):
    """Shared by every tool: the Cerebrus Pulse client to call.

    Pass one client, built with a wallet, to all tools so paid tools pay
    automatically and share one spend budget. Without one, each call uses an
    unpaid client and paid tools return the API's payment terms.
    """

    client: Optional[CerebrusPulse] = Field(default=None, exclude=True)

    def _api(self) -> CerebrusPulse:
        return self.client if self.client is not None else CerebrusPulse()


_TIMEFRAMES = "Comma-separated, from 5m, 15m, 1h, 4h, 1d, 1w (default 1h,4h)"


class PulseInput(BaseModel):
    coin: str = Field(description="Coin ticker (e.g., BTC, ETH, SOL)")
    timeframes: str = Field(default="1h,4h", description=_TIMEFRAMES)


class FundingInput(BaseModel):
    coin: str = Field(description="Coin ticker (e.g., BTC, ETH, SOL)")
    lookback_hours: int = Field(default=24, description="Hours of history (1-168)")


class BundleInput(BaseModel):
    coin: str = Field(description="Coin ticker (e.g., BTC, ETH, SOL)")
    timeframes: str = Field(default="1h,4h", description=_TIMEFRAMES)


class ScreenerInput(BaseModel):
    top_n: int = Field(default=30, description="Number of top coins (1-50)")


class CoinInput(BaseModel):
    coin: str = Field(description="Coin ticker (e.g., BTC, ETH, SOL)")


class CerebrusListCoinsTool(_CerebrusTool):
    name: str = "cerebrus_list_coins"
    description: str = (
        "List all available coins on Cerebrus Pulse. "
        "Returns tickers for 30+ Hyperliquid perpetuals. Free, no payment required."
    )

    def _run(self) -> str:
        try:
            coins = self._api().coins()
            return json.dumps({"coins": coins, "count": len(coins)})
        except CerebrusPulseError as e:
            return _error(e)


class CerebrusPulseTool(_CerebrusTool):
    name: str = "cerebrus_pulse"
    description: str = (
        "Get multi-timeframe technical analysis for a Hyperliquid perpetual. "
        "Returns RSI, EMAs (20/50/200), ATR, Bollinger Bands, VWAP, Z-score, "
        "trend direction, confluence scoring, derivatives (funding, OI, spread), "
        "and market regime. " + _cost("pulse")
    )
    args_schema: type[BaseModel] = PulseInput

    def _run(self, coin: str, timeframes: str = "1h,4h") -> str:
        try:
            result = self._api().pulse(coin, timeframes)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return _error(e)


class CerebrusSentimentTool(_CerebrusTool):
    name: str = "cerebrus_sentiment"
    description: str = (
        "Get aggregated crypto market sentiment as a bucketed label "
        "(very_bearish, bearish, neutral, bullish, very_bullish) with its timestamp. "
        "Not coin-specific. " + _cost("sentiment")
    )

    def _run(self) -> str:
        try:
            result = self._api().sentiment()
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return _error(e)


class CerebrusFundingTool(_CerebrusTool):
    name: str = "cerebrus_funding"
    description: str = (
        "Get funding rate analysis for a Hyperliquid perpetual. "
        "Returns the current, average, min and max rate over the lookback window, "
        "annualized %, and the share of positive samples. " + _cost("funding")
    )
    args_schema: type[BaseModel] = FundingInput

    def _run(self, coin: str, lookback_hours: int = 24) -> str:
        try:
            result = self._api().funding(coin, lookback_hours)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return _error(e)


class CerebrusBundleTool(_CerebrusTool):
    name: str = "cerebrus_bundle"
    description: str = (
        "Get complete analysis bundle: technical analysis + sentiment + funding "
        "in one call. " + _cost("bundle")
    )
    args_schema: type[BaseModel] = BundleInput

    def _run(self, coin: str, timeframes: str = "1h,4h") -> str:
        try:
            result = self._api().bundle(coin, timeframes)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return _error(e)


class CerebrusScreenerTool(_CerebrusTool):
    name: str = "cerebrus_screener"
    description: str = (
        "Scan all 30+ coins for top trading signals. Returns RSI, trend, "
        "volatility regime, funding bias, confluence, and OI trend. " + _cost("screener")
    )
    args_schema: type[BaseModel] = ScreenerInput

    def _run(self, top_n: int = 30) -> str:
        try:
            result = self._api().screener(top_n)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return _error(e)


class CerebrusOITool(_CerebrusTool):
    name: str = "cerebrus_oi"
    description: str = (
        "Get open interest analysis for a Hyperliquid perpetual. "
        "Returns OI delta, percentile, trend, and price-OI divergence. " + _cost("oi")
    )
    args_schema: type[BaseModel] = CoinInput

    def _run(self, coin: str) -> str:
        try:
            result = self._api().oi(coin)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return _error(e)


class CerebrusSpreadTool(_CerebrusTool):
    name: str = "cerebrus_spread"
    description: str = (
        "Get spread and liquidity analysis for a Hyperliquid perpetual. "
        "Returns bid-ask spread, slippage at various sizes, liquidity score. "
        + _cost("spread")
    )
    args_schema: type[BaseModel] = CoinInput

    def _run(self, coin: str) -> str:
        try:
            result = self._api().spread(coin)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return _error(e)


class CerebrusCorrelationTool(_CerebrusTool):
    name: str = "cerebrus_correlation"
    description: str = (
        "Get BTC-altcoin correlation matrix for top 15 Hyperliquid perpetuals. "
        "Returns correlations, regime, and sector averages. " + _cost("correlation")
    )

    def _run(self) -> str:
        try:
            result = self._api().correlation()
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return _error(e)


class StressInput(BaseModel):
    limit: int = Field(default=10, description="Recent scans to analyze (1-50)")


class CerebrusStressTool(_CerebrusTool):
    name: str = "cerebrus_stress"
    description: str = (
        "Get market stress index from cross-chain arbitrage detection across 8 chains. "
        "Returns stress level (LOW/MODERATE/HIGH/EXTREME), score, spread statistics, "
        "and chain routes with price dislocations. " + _cost("stress")
    )
    args_schema: type[BaseModel] = StressInput

    def _run(self, limit: int = 10) -> str:
        try:
            result = self._api().stress(limit)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return _error(e)


class CerebrusCexDexTool(_CerebrusTool):
    name: str = "cerebrus_cex_dex"
    description: str = (
        "Get CEX-DEX price divergence for a token. Compares Coinbase vs "
        "Chainlink/Uniswap prices. Returns spread in bps and direction. " + _cost("cex_dex")
    )
    args_schema: type[BaseModel] = CoinInput

    def _run(self, coin: str) -> str:
        try:
            result = self._api().cex_dex(coin)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return _error(e)


class CerebrusBasisTool(_CerebrusTool):
    name: str = "cerebrus_basis"
    description: str = (
        "Get Chainlink basis analysis — Hyperliquid perp oracle vs Chainlink spot. "
        "Returns basis in bps, direction, and contrarian signal. " + _cost("basis")
    )
    args_schema: type[BaseModel] = CoinInput

    def _run(self, coin: str) -> str:
        try:
            result = self._api().basis(coin)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return _error(e)


class CerebrusDepegTool(_CerebrusTool):
    name: str = "cerebrus_depeg"
    description: str = (
        "Get USDC collateral health via Chainlink oracle. "
        "Reports peg status, deviation, risk level, and Arbitrum sequencer status. "
        + _cost("depeg")
    )

    def _run(self) -> str:
        try:
            result = self._api().depeg()
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return _error(e)


class CerebrusLiquidationsTool(_CerebrusTool):
    name: str = "cerebrus_liquidations"
    description: str = (
        "Get estimated liquidation heatmap for a Hyperliquid perpetual. "
        "Maps liquidation clusters across leverage tiers (3x-50x) for longs and shorts. "
        "Returns cascade risk, estimated USD at each zone, and nearest cluster. "
        + _cost("liquidations")
    )
    args_schema: type[BaseModel] = CoinInput

    def _run(self, coin: str) -> str:
        try:
            result = self._api().liquidations(coin)
            return json.dumps(result.raw, indent=2)
        except CerebrusPulseError as e:
            return _error(e)
