# Trading Lab v2.3 — News-first data quality gate

This release is deliberately **not** a news strategy or a live signal generator. It tests Alpaca's historical news coverage using existing environment credentials and an allowlisted read-only GET on `https://data.alpaca.markets/v1beta1/news`.

Run in EasyPanel:

```
/app/scripts/run.sh news-audit --start 2026-09-01 --end 2026-10-01 --symbols AAPL,MSFT,NVDA --pages 3
```

Output: `/app/reports/news/coverage.json`. The summary prints article count, provider, per-symbol coverage, coverage completeness and missing timestamp statistics. `PARTIAL_PAGINATED_COVERAGE` means the configured page limit was reached; it is NOT complete news history. `BLOCKED_DATA_ACCESS` means no access or an invalid response; inspect `http_status` without displaying keys.

Safety: no POST, no broker endpoint, no account/order mutation, `authorized_to_trade=false`. No earnings event can be traded or approved based on these articles alone. Before historical earnings-based replay, separately obtain actual results, **point-in-time analyst expectations**, and **verified first-public availability**; confirm data licensing and market timestamp conventions.

Research thesis: post-earnings continuation over 1/3/5 sessions, initially LONG, only evaluated after the point-in-time coverage and data-quality gates pass. No automatic promotion of strategy variants based on reused validation sets.
