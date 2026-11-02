# Command Panel v1 (MVP-OP-1.0 / ISS-007)

Read-only extension of `v4_web_dashboard.py` and `trading_dashboard_data.py`.

## Surfaces

| Area | Source | Notes |
|------|--------|-------|
| Performance / paper snapshots | `paper/order-snapshots.jsonl` | P&L gross only; no fees |
| Ledger history counts | `ledger_reconcile.ledger_snapshot()` | Requires `LEDGER_DATABASE_URL` |
| Open queue signal | `paper_queued_intent` count | **Not a fill** |
| Strategy catalog | `strategy_states` via `list_strategy_states()` | No promotion from UI |
| Prodigy opportunities | `reports/intelligence/prodigy-top10-latest.json` | Run `prodigy-rank` first |
| Continuous improvement | `evolution/decisions.jsonl` | Tips only |
| Kill switch | `gate_b_risk.kill_switch_active()` | Also in `/api/status` |

## API

`GET /api/status` includes `command_panel` and `operational_acceptance`:

- `operational_acceptance` is **true** only when ledger reports `paper_fills > 0` **and** closed monitored snapshots exist for this reports root.
- Operator must still verify broker reconciliation before treating performance as homologated.

## Auth

Unchanged: loopback without bearer; remote requires `DASHBOARD_ALLOW_REMOTE=true` and `DASHBOARD_BEARER_TOKEN` (≥32 chars).

## Deploy

Merged **PR #14** (`main` `3ae522a+`): rebuild EasyPanel image once. Snapshot smoke inside container does not require a running HTTP server.

### EasyPanel HTTP (operador)

1. Same env as webhook where ledger keys live: `LEDGER_DATABASE_URL`, `DASHBOARD_BEARER_TOKEN`, `DASHBOARD_ALLOW_REMOTE=true`, `LIVE_TRADING_ENABLED=false`.
2. Run process: `/app/scripts/run.sh v4-dashboard --root /app/reports --host 0.0.0.0 --port 8765` (long-lived — separate process or operador-approved start override; **do not** add a third EasyPanel app).
3. Publish port **8765** behind HTTPS; all GET routes require bearer when remote.

Details: `EASYPANEL.md` § Command Panel.

Does not replace Feature 5 operator fill (P-001b optional).
