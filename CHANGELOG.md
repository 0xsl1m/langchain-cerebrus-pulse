# Changelog

## 0.4.0 (unreleased)

### Added
- Paid tools can pay. Every tool takes `client=`: pass one
  `cerebrus_pulse.CerebrusPulse(wallet_key=...)` to all tools and they pay in
  USDC over x402 inside that client's spend limits and shared budget. Install
  with `pip install "langchain-cerebrus-pulse[pay]"` (Base) or `[svm]` (also
  Solana).
- When a paid tool cannot pay, its JSON result carries `payment_required`,
  the `price_usd` from the API's 402 terms, the `payment_terms`, and a
  `reason` when the spend limits refused.

### Changed
- Requires `cerebrus-pulse>=0.4.0,<0.5` (was `>=0.1.0`, which allowed SDKs
  without the stress, cex_dex, basis, depeg and liquidations methods, and with
  the broken /funding and /sentiment parsers) and `langchain-core>=1.0,<2`.
- Tool descriptions quote the SDK's indicative prices and say they are
  indicative. Seven hard-coded prices were wrong, and the bundle's "20%
  discount" claim is gone.
- `__version__` comes from the package metadata (it said 0.3.1 in 0.3.2).

### Fixed
- Timeframes are documented as 5m, 15m, 1h, 4h, 1d, 1w, and the screener's
  `top_n` as 1-50.
- The sentiment tool describes the bucketed label the API returns.
- The README agent example uses `langchain.agents.create_agent`;
  `AgentExecutor` and `create_tool_calling_agent` are gone from langchain 1.x.
