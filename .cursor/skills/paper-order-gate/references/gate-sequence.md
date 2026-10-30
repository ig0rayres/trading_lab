# Gate sequence

> Part of `paper-order-gate`. Return to [hub](../SKILL.md).

## 1. Before any broker call

Read the signal and the risk decision. If either row is missing, or `decision` is not `paper_allowed`, or `control_flags.kill_switch_on` is true, return a rejection and do not call the broker.

## 2. Paper host only

The base URL must be the Alpaca paper host already referenced by `src/v4_readiness.py` (`https://paper-api.alpaca.markets`). A live host is a stop.

## 3. After the broker responds

Store `broker_order_id` and fills. On process restart, reload the ledger before accepting new work. A correction is a new ledger row, not an edit that hides the old fill.
