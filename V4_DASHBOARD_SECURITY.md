# Dashboard v4: access and operational state

- Default binding: 127.0.0.1:8765 (private).
- For remote binding, set `DASHBOARD_ALLOW_REMOTE=true` and a random `DASHBOARD_BEARER_TOKEN` of at least 32 characters. All GET endpoints including `/healthz` then require `Authorization: Bearer <token>`.
- Prefer HTTPS with authenticated reverse proxy in front; bearer auth is not TLS. Do not expose the dashboard directly on HTTP over the Internet.
- Dashboard displays last persisted research cycle from `reports/v4/v4_manifest.json`. A research result never means an executable order is authorized or broker-confirmed.
- This component does not submit any orders; `LIVE_TRADING_ENABLED` must remain false.
- No broker Paper end-to-end acceptance has been demonstrated by the 381 local tests.
