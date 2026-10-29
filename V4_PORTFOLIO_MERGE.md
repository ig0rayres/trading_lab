# V4 cross-market portfolio observation (read-only)

`python -m v4_portfolio_merge --alpaca FILE --b3 FILE --crypto FILE --output FILE`

The Alpaca input must be a partial `v4_broker_snapshot` report. B3/crypto inputs are Shadow observations with `mode: SHADOW` and lists of `positions`, each containing `market`, `symbol`, `notional_brl`, and optional `planned_risk_brl`.

This is **not** execution reconciliation: shadow positions are not certified fills, the Alpaca account does not attest cross-market balances, broker order reservation and stops remain unverified, P&L is missing, and FX is a reference. All outputs carry `complete=false`, `broker_reconciled=false`, `execution_authorized=false`, `orders_sent=0`. No live API and no orders are invoked. It fails closed on invalid money, malformed inputs, or duplicate positions across sources. Production authorization requires actual broker-side fills/stops, verified FX, P&L and atomic risk reservation across venues.

Local validation: 317 pytest tests passing plus 3 subtests, October 29, 2026. No external API tested. Do not deploy over current running services.
