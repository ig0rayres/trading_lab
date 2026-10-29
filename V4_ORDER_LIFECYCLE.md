# V4 Paper Order Lifecycle — read-only

`./scripts/run.sh v4-order-lifecycle --input /app/reports/alpaca-order-snapshot.json --output /app/reports/order-observation.json`

Input format: `{"orders": [<full Alpaca REST order objects including optional nested legs>]}`. The file must be from a trustworthy **GET** read of the Alpaca Paper account; this module does not download it or authenticate its source. It does not send, cancel, amend, or authorize any orders. It rejects bad statuses, inconsistent fill quantities, duplicate broker IDs, and mismatched symbols across bracket legs. Missing bracket legs produce blocking audit issues rather than proof of protection.

## Limitations

This is an order **observation**, not complete broker reconciliation. A filled entry does not imply an exited position. No positions, cash, fees, settlement, or realized daily/weekly P&L are verified. The module always emits `broker_reconciled=false`, `execution_authorized=false`, `orders_sent=0`. Portfolio risk remains fail-closed. For genuine reconciliation we still need exhaustive broker order/activity ingestion with cursoring, persistent order-to-fill journal, positions, fees, stop-state verification, market-specific paper executors and operational API tests.

The `V4_ORDER_LIFECYCLE` module is new and does not change live deployment or other services.
