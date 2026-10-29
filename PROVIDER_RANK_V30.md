# Trading Lab v3.0 - Provider Ranking (offline)

This build adds an independent historical provider ranking. It does NOT auto-subscribe or execute provider signals. No provider has yet been validated or selected using real trade-by-trade data.

## Use

Provide JSON containing `providers`. For each provider specify `id`, `verified` (true only after independently checking source records), `asset_classes: ["us_equity"]`, `track_record_start` (UTC ISO8601), and `trades` with `closed_at` UTC ISO8601, `net_pnl_pct` (return on allocated provider capital after costs), `risk_pct` (positive original trade risk percentage). Example shape:

```json
{"providers":[{"id":"example-provider-NOT-VERIFIED", "verified":false, "asset_classes":["us_equity"], "track_record_start":"2026-01-01T00:00:00Z", "trades":[]}]}
```

Then run:

```sh
/app/scripts/run.sh provider-rank --input /app/data/providers-history.json
```

Result `/app/reports/providers/latest.json`: ranked top ten and prioritized up to three **eligible** providers. Eligibility requires independently verified history, at least 180 days of track record, at least 30 closed trades in window, positive net return and no more than 20% observed maximum closed-trade equity drawdown. These are preliminary research cutoffs, not guarantees, and closed-trade drawdown may understate intratrade or mark-to-market risk. A selection does not authorize copying orders.

The following are NOT implemented: authenticated webhook server, real provider subscription or historical feed ingestion, daily loss budgeting across all engines, reliable operational order monitoring, autonomous Alpaca Paper sending, and trade reconciliation between signal and broker fills. Keep Paper execution OFF pending validation and explicit authorization.

Ranking is retrospective. Avoid selecting winners based only on last six months. Compare forward out-of-sample Paper results, costs, copy latency, feasible instrument/capital, and correlation among top providers before any live trading.
