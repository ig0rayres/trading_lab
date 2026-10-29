# V4 Alpaca Paper activity ingestion (read-only)

Command: `v4-alpaca-activities --output /app/reports/paper/activities.json`.

Requires the existing ALPACA_* Paper credentials and explicit USD_BRL_REFERENCE.
The implementation permits only GET requests against the Alpaca PAPER host.
All reports are incomplete/unaudited and explicitly disallow order execution.
Broker activity metadata alone does not prove beginning-of-history completeness,
actual commissions/fees, portfolio reconciliation, or verified realized P&L.

Offline validation: `PYTHONPATH=src:. pytest -q`.

Remaining acceptance gates: live Paper read-only API check, broker position
match, fee source verification, equity/crypto/B3 consolidated risk attestation,
automated order lifecycle, authenticated provider integration, dashboard UI,
and deployment validation. None of these is claimed completed by this module.
