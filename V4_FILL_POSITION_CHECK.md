# v4 fill-to-position consistency gate

Command: `scripts/run.sh v4-fill-position-check --activities <alpaca-activities.json> --positions <alpaca-positions.json> --output <check.json>`.

- Accepts the output from v4-alpaca-activities and a raw Alpaca `GET /v2/positions` array.
- Checks only fill net quantities against current long positions, using exact Decimal math.
- Duplicate fills/positions, shorts, invalid values, and unexpected source identifiers are rejected.
- A match **never** sets `broker_reconciled`, `realized_pnl_verified`, or `execution_authorized` to true; fees, historical completeness, cash, financing and corporate actions remain blockers.
- Returns exit 2 on differences, exit 0 on quantity consistency (not trading readiness).
- This is an offline/read-only utility. It does not query brokers or submit orders.
