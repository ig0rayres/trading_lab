# Ingest rules

> Part of `signal-ingest`. Return to [hub](../SKILL.md).

## 1. Secret

Primary contract (`POST /webhooks/tradingview`): header **`X-Webhook-Token`**, value from `TV_WEBHOOK_TOKEN` (or legacy alias `TV_WEBHOOK_SECRET`). Minimum 32 characters. Missing or wrong → **401** without queue side effects.

Legacy EasyPanel path `POST /webhook/{token}`: same secret in the URL path; invalid → **404** (no token oracle).

News First (`news_first_sim`) and signed copy (`signal_copy.preflight`) append **`signal_events`** when `LEDGER_DATABASE_URL` is set. Still no broker.

## 2. Idempotency

`idempotency_key` is unique. A replay returns the stored `signal_events` row and does not create another one.

## 3. Stop line

This skill ends at `signal_events`. Risk and the broker belong to `paper-order-gate`.
