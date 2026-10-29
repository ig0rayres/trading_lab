# v1.2 candidate research: four daily adaptations and one explicitly blocked intraday study

Run after deploy (network to Yahoo required):

```sh
/app/scripts/run.sh candidate-research --from 2021-01-01 --to 2026-10-23 --split 2025-01-01 --output /app/reports/candidates/v12
```

`--csv-dir /app/reports/daily-input` for offline CSV files named `SPY.csv`, etc., with `date,open,close` adjusted price columns. Raw, unadjusted CSV are not suitable.

**These are research hypotheses, not reproductions of the five academic papers.**
- TSMOM ETF: equal weight 12-month-positive ETFs, long-or-cash; daily signal, not original vol-scaled futures.
- 52-week high: long two nearest-to-high stocks from today's static symbol universe; **survivorship biased**.
- Turn of month: SPY long on last session of month and first three sessions, else cash.
- Pairs: selected fixed pairs, daily ratio deviation z>2, equal dollar long/short; no locate/borrow/margin costs, **optimistic**. Not original distance-strategy replication.
- Intraday ETF: **not evaluated**. Requires multi-year 5m data for a meaningful comparison.

All daily strategy decisions at an observed close apply to next close-to-close daily return; daily adjusted-close proxy is not an executable close/open fill model. Bid-ask, taxes, funding and USD/BRL costs require separate modeling. Split is descriptive, not a truly unseen holdout if inspected repeatedly. Output is **never an instruction to trade**.

One-way fee in basis points applies to absolute portfolio weight changes, with end liquidation. Report `summary.json`, `daily_returns.csv`, downloaded price cache. Docker unchanged beyond new scripts. `LIVE_TRADING_ENABLED` guard remains.
