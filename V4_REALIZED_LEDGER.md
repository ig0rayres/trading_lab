# V4 FIFO realized ledger (read only)

Run: `scripts/run.sh v4-realized-ledger --input /app/reports/activities.json --output /app/reports/realized-ledger.json`.

Input must be a complete list of **individual** fill activities, ordered chronologically, with unique IDs, timestamps, uppercase symbols, side buy/sell, quantities, prices, and explicitly supplied fees. Include `currency` (`USD` or `BRL`) and `complete: true`. Sample:

```json
{"currency":"USD","complete":true,"activities":[{"id":"f1","timestamp":"2026-10-29T16:00:00Z","symbol":"AAPL","side":"buy","qty":"1","price":"100","fee":"0"},{"id":"f2","timestamp":"2026-10-29T16:30:00Z","symbol":"AAPL","side":"sell","qty":"1","price":"102","fee":"0"}]}
```

The module applies FIFO cost basis and prorates fees on partial fills, while retaining the unclosed lots. It is read-only and does not submit orders. Repeated calls to the same complete input deterministically recompute the same results; it does not independently authenticate activity IDs, time order, fee correctness, corporate actions or completeness. The `complete:true` assertion is supplied by the caller, not broker-verified. Short selling, multi-currency conversions, broker-specific fees and intraday financing are NOT supported. This is an independently CALCULATED value (`realized_pnl_verified:false`), **not a confirmed broker P&L**; no dashboard may label it as verified or aggregate USD and BRL without explicit FX evidence. The broker activity-fetch and comparison with position/balance changes are still pending.
