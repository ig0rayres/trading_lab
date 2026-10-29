# V4 dashboard (read-only)

Start in container: `./scripts/run.sh v4-dashboard --root /app/reports --host 127.0.0.1 --port 8765`

Routes: `/` (HTML), `/api/status` (JSON), `/healthz` (liveness).

The server does not import broker submission code, has no trading controls and rejects POST. It binds to loopback by default. Do not publish it without an authenticated reverse proxy; binding remotely requires `DASHBOARD_ALLOW_REMOTE=true` but does not provide authentication on its own.

Metrics reflect persisted observations only. Empty data is displayed as unavailable, not zero profit. P&L is gross and does not include complete costs. This does not deliver broker-backed reconciliation, automatic Paper trade execution, or completed production acceptance.
