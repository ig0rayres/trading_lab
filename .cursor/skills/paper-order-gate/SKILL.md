---
name: paper-order-gate
description: >
  Place or reconcile an Alpaca paper order only after Gate A and Gate B. Use when: paper order, alpaca fill, reconcile ledger. Don't use when: research scheduler, market data, live trading.
disable-model-invocation: false
scope: project
created-by: tech-lead
---

# Paper Order Gate

Paper-gateway author. Refuses a broker call that did not pass both gates, and refuses a live account.

## Prerequisites

- `docs/ARCHITECTURE.md` ADR-004 and the paper-gateway module
- `docs/db-schema.dbml` tables `signal_events`, `risk_decisions`, `paper_orders`, `paper_fills`, `ledger_entries`
- `LIVE_TRADING_ENABLED=false`
- Existing modules under `src/` (`paper_gateway.py`, `v4_alpaca_reconcile.py`, `v4_realized_ledger.py`). Extend those files. Do not add a second client.

## Main Flow

1. **Confirm Gate A** — the signal row is accepted and idempotent
   -> Details: `references/gate-sequence.md`
2. **Confirm Gate B** — `decision` is `paper_allowed` and the kill switch is off
   -> Details: `references/gate-sequence.md`
3. **Submit paper only** — Alpaca paper host, then persist ack, fill, and ledger
   -> Details: `references/gate-sequence.md`

## Rules

- Communication: Brazilian Portuguese with the operator. Code and comments in English.
- One order per accepted risk decision. A duplicate event must not open a second position.
- Queue-only and HTTP 200 are not fills.
- Do not set `deleted_at` on orders, fills, or ledger rows.
