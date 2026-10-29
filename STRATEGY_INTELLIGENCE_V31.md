# Strategy Intelligence v3.1

Periodic read-only evaluation; not connected to Paper gateway. No broker orders.

Input: `/app/data/strategy-observations.json` with `{ "strategies": [{ "id":"example", "evidence_verified":true, "execution_reconciled":true, "prior_paper_approved":false, "trades":[{"closed_at":"2026-10-28T12:00:00Z", "net_pnl_brl":10}] }] }`.

Run: `/app/scripts/run.sh strategy-intelligence --cadence daily --input /app/data/strategy-observations.json` (or weekly/monthly). Persist reports on a volume mapped to `/app/reports`. Trigger with external scheduler daily/weekly/monthly; **no scheduler is started by this build**.

Suspension is an advisory report and **does not yet prevent orders**. A real enforcement gate and actual broker-reconciled data remain mandatory before automatic execution. The R$150 loss threshold is a prototype measured over the cadence window, not an account-wide intraday loss limit.
