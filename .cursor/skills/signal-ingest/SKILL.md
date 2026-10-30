---
name: signal-ingest
description: >
  Accept an external signal without placing an order. Use when: tradingview webhook, signal ingest, idempotency key. Don't use when: paper submit, broker client, live trading.
disable-model-invocation: false
scope: project
created-by: tech-lead
---

# Signal Ingest

Ingress author. Records an authentic signal and stops. Does not call the broker.

## Prerequisites

- `docs/api-spec.yaml` path `POST /webhooks/tradingview`
- `docs/db-schema.dbml` table `signal_events`
- Existing `src/tradingview_webhook.py` and `src/tradingview_worker.py`. Extend those files.
- Webhook secret only from the environment. Never from a markdown file or a log line.

## Main Flow

1. **Check the secret** — missing or short secret rejects the request
   -> Details: `references/ingest-rules.md`
2. **Deduplicate** — same `idempotency_key` returns the existing row
   -> Details: `references/ingest-rules.md`
3. **Store and stop** — write `signal_events`. Do not import the paper gateway
   -> Details: `references/ingest-rules.md`

## Rules

- Communication: Brazilian Portuguese with the operator. Code and comments in English.
- A 200 response means the event was received, not that an order was sent.
- Do not log the webhook token or the raw payload when it may contain a secret.
