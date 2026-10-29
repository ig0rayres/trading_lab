# Historical replay protocol v0.6

`history` reuses upstream entry, exit, sizing, and risk rules. Its own logic is only historical orchestration, OHLC quality checks, conservative OHLC barrier replay, summaries and caching.

## Recommended first run

```sh
/app/scripts/run.sh verify
/app/scripts/run.sh history --symbols TSLA,NVDA,AMD --days 30 --output /app/reports/history/v06-first-run
cat /app/reports/history/v06-first-run/summary.json
```

Before calling this a strategy, require a substantially larger **point-in-time** historical dataset and a separated forward-testing period. Free Yahoo 5-minute history is constrained and cannot deliver a robust multi-year backtest; do not claim statistical edge from 2–8 weeks.

## Safety and reproducibility gates

- No today's watchlist: selection must be fixed *before* the test dates; do not optimize symbol list from current hits. A present-day fixed universe still has survivorship bias.
- No partial sessions: every complete 5-minute slot is required; missing or duplicate bars are rejected for that symbol/day. Null Yahoo OHLCs are treated as missing even though the original visualization helper can replace missing OHLC with close.
- Entry is the next candle's **open**, after the breakout bar closed. Hypothetical fills need realistic slippage sensitivity testing.
- Stop and target from original exit module. If the same bar crosses both, stop wins. If a bar opens below stop, exit at open; closing flat at 15:55 (or 12:55 early close) on the previous bar close.
- Output explicitly includes risk audit PASS/BLOCK. It does not order or fill trades and does not enforce aggregate same-day simultaneous exposure.
- `UPSTREAM_COMMIT` optional pin enforces exact source revision. The upstream commit SHA is included in the summary and all trade rows.
- Cache is per symbol, request range and local New York date. `--refresh` refetches on a single day; pass `--offline-dir` for frozen input archives.

## How to read metrics

`win_rate_pct`, `mean_net_r`, `profit_factor` aggregate per-trade *independent* hypothetical outcomes. `risk_pass` and `risk_blocked` are **hypothetical individual audit outcomes**. There is no market-liquidity cap, commissions model validation, multi-asset portfolio risk, real broker confirmation or real orders. The earlier/later calendar split is descriptive only; it is *not* proof of out-of-sample profitability.
