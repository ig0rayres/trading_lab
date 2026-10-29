# v1.0: exploratory strategy research

This release does **not** reproduce a published strategy yet. It introduces two explicitly defined, auditable candidate hypotheses, using the existing original Yahoo parser and strict 5-minute session gate. Publication reproduction requires independently pinning the exact original implementation, data and execution assumptions.

- `vwap_fade`: first completed bar recovering after a candle closes at least 1.2% below session VWAP; enter next candle open; stop at preceding 3-bar low, otherwise VWAP touch or preclose flat. Long only. No look-ahead in signal calculation.
- `pair_ratio_z`: previous 20 complete matched sessions' closing log-price ratio z-score exceeds 1.5; trade next session open, equal-dollar long one leg / short other, flat near the close. **Not** cointegration. Simplified borrow-free short is unrealistically optimistic; do not treat as executable performance.

All prices include independently configured fees and slippage both sides. Neither strategy simulates a portfolio. Do not optimize parameters on the reported window and claim an edge. Do not connect to a broker.

```sh
/app/scripts/run.sh external-research --days 55 \
  --symbols AAPL,MSFT,NVDA,AMD,TSLA,META,AMZN,GOOGL \
  --pairs AAPL:MSFT,NVDA:AMD \
  --output /app/reports/external/v10
cat /app/reports/external/v10/summary.json
```

For a true publication reproduction, use a separately licensed longer-term historical data feed, pin source commit and date ranges, and document any differences with author's reported outcome. This v1.0 intentionally does not mislabel a new hypothesis as a reproduction.
