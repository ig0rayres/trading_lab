# v3.9 — Paper monitoring pilot, no autonomous trading

## Changes
- Read-only broker reconciliation now supports `nf-`+24 hex and `demo-`+20 hex IDs; rejects other IDs.
- Includes bracket exit legs and fill details in reconciliation.
- `paper-monitor` performs one read-only broker reconciliation, computes **gross** realized P&L from confirmed exit fills (excluding fees/slippage/FX), and appends a UTC snapshot to `/app/reports/paper/order-snapshots.jsonl`.
- No orders are sent, canceled or modified. This is a **manual one-shot** monitor; periodic scheduling has not been installed.

## Example (on existing webhook service after deploying)
`/app/scripts/run.sh paper-monitor --client-order-id demo-6b7ddf6dca1247d09cfb`

Use a persistent `/app/reports/paper` mount, otherwise snapshots can disappear on redeploy. Avoid placing the snapshot under the temporary filesystem. Do NOT replace the existing `/app/reports/webhooks` volume.

## Still not complete
- The main research daemon is separate from the webhook worker; no verified signal producer → News First decision → signed queue bridge.
- `signal_paper_runner.py` does NOT enforce verified news. It accepts signed external signals (subject to risk gates) and requires `PAPER_SIGNAL_AUTO_ENABLED=true`, `PAPER_SIGNAL_ACCOUNT_ACK` and `PAPER_DAILY_RISK_CONFIRMED`. Keep `PAPER_SIGNAL_AUTO_ENABLED=false` until source-quality and daily loss checks are implemented and independently tested.
- Risk policy currently diverges across `paper_gateway.py` (R$5k/R$50), `signal_copy.py` (R$5k/R$50) and `signal_paper_runner.py` (R$10k/variable R$20-50). DO NOT silently increase ceilings or enable automation.
- Evolution daily has no automated capture of rejected candidates or broker fills; the default webhook path is `/app/reports/webhooks/journal.jsonl`, whereas production's real volume was bound to `/app/webhook-source`. To read it in principal, set `TV_QUEUE_DIR=/app/webhook-source/pending` **only on main** (if verified) or adapt the producer path. No config is modified by this ZIP.
- `paper_monitor.py` is a snapshot ledger seed for the future dashboard, not a live dashboard.
