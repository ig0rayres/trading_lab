# V4 Risk Preview integration

Research decisions can now be passed through a fail-closed portfolio risk preview.

- `scripts/run.sh v4-decision-cycle --market-cycle /app/reports/market.json --output /app/reports/decisions.json --risk-output /app/reports/risk-preview.json`
- Optional `--risk-snapshot` and `--risk-tickets` allow testing a proposed entry against a supplied reconciled portfolio snapshot. These inputs are never assumed authentic.
- The risk preview explicitly forces `verified=False` and `trading_mode=RESEARCH` for all proposed tickets, regardless of their source claims.
- No Paper or live order execution is included or authorized by this reporting module.
- Future work: signed broker reconciliation, idempotent execution handoff, live API integration tests, operational dashboard.

Local validation on 2026-10-29: 306 pytest tests passed. No external feeds or broker operations were exercised in this test run.
