---
name: panel-triggers
description: >
  Change a trading trigger from the panel and record the previous value. Use when: kill switch, risk anchor, market control, strategy phase, PATCH /api/triggers. Don't use when: placing an order, webhook ingest, live trading.
disable-model-invocation: false
scope: project
created-by: tech-lead
---

# Panel Triggers

Panel author. Writes triggers only. Never submits an order.

## Prerequisites

- `docs/api-spec.yaml` paths `PATCH /api/triggers`, `PATCH /api/markets/{market}`, and `PATCH /api/strategies/{strategy_key}`
- `docs/db-schema.dbml` tables `control_flags`, `market_controls`, `strategy_states`, and `trigger_changes`
- `docs/DATABASE.md` section 6 for the starting cent values
- Existing `src/v4_web_dashboard.py`. Extend that file. Do not add a second HTTP server.

## Main Flow

1. **Read the current row** — load the flag, market, or strategy phase before changing it
   -> Details: `references/trigger-writes.md`
2. **Reject a forbidden change** — no new strategy, no live switch, no secret in the body
   -> Details: `references/trigger-writes.md`
3. **Write the value and the audit row** — one update and one `trigger_changes` insert
   -> Details: `references/trigger-writes.md`

## Rules

- Communication: Brazilian Portuguese with the operator. Code and comments in English.
- A trigger PATCH does not insert `paper_orders` and does not import a broker client.
- Bearer auth alone cannot authorize the write.
- Do not store a DSN, a broker key, or a webhook secret in `trigger_changes`.
- Do not loosen an anchor when the database read fails.
