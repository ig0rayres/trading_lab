# Trading Lab v3.7 — TradingView webhook queue / Paper pilot

Collective2 historical analysis stays unchanged. No subscription required for TradingView alerts created by the user or an authorized provider.

## Environment variables
- `TV_WEBHOOK_TOKEN`: random `secrets.token_urlsafe(48)`, used only in HTTPS URL. Do not put API keys or broker secrets in the TradingView JSON.
- `SIGNAL_COPY_SECRET`: random `secrets.token_urlsafe(48)`; for internal signing only.
- `LIVE_TRADING_ENABLED=false`
- `PAPER_SIGNAL_AUTO_ENABLED=false`, `PAPER_EXECUTION_ENABLED=false` initially.
- `USD_BRL_REFERENCE`: reference FX; `ALPACA_API_KEY` and `ALPACA_SECRET_KEY` available.

## Deployment
Configure EasyPanel separate HTTP service command `/app/scripts/run.sh tv-webhook --port 8080`, internal port `8080`, publicly reachable through HTTPS reverse proxy (public 443). Persistent mount at `/app/reports`; share it with the worker service. Worker command `/app/scripts/run.sh tv-worker --once`, scheduled every minute for piloting. TradingView imposes ~3 sec response timeout and public HTTP(S) ports 80/443.

Webhook URL: `https://YOUR-DOMAIN/webhook/YOUR_TV_WEBHOOK_TOKEN`

JSON in TradingView alert (user's own alerts / authorized provider). Substitute a real unique alert id; Use the TradingView `{{timenow}}` placeholder for `sent_at_utc`; use `"TV_{{ticker}}_{{timenow}}"` for unique `signal_id` (the receiver hashes this to an internal alphanumeric ID). For a valid order, entry, stop and target must come from a real strategy/alert, not fabricated values. Example **static template for format only, not for submitting**:
```
{"provider":"tradingview","signal_id":"ALERT_20261028_000001","symbol":"AAPL","side":"buy","asset_class":"us_equity","sent_at_utc":"2026-10-28T18:00:00Z","entry":"250.00","stop":"245.00","target":"260.00","quantity":1,"ttl_seconds":30}
```
No alert will pass once timestamp expires. All fields must be explicitly populated. Do not send fictitious values to simulate real trades.

Test only: `curl -s https://YOUR-DOMAIN/health`; monitor `/app/reports/webhooks/journal.jsonl`. Queue ingress never places orders. Worker is PREVIEW_ONLY until all execution gates are explicitly enabled, and legacy risk code still has the conservative 5k limit. `PAPER_DAILY_RISK_CONFIRMED` should NOT be enabled until actual daily realized P&L enforcement exists. Consequently **autonomous order submission is NOT approved in this build**. Explicit account authorization alone is insufficient. No live trading mode exists.

Security: opaque token is in webhook URL, require TLS, limit proxy access / logs, rotate on leak, run separate service, rate-limit upstream, verify origin where feasible. TradingView does not sign payload itself. The token is a shared secret, so it must be treated as a credential.
