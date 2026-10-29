# Trading Lab v3.2 — Continuous Review

Read-only historical-provider adapter. Runs daily/weekly/monthly advisory review in a single command:

```sh
/app/scripts/run.sh continuous-review
```

Reads `/app/reports/providers/raw/*_closed_trades.json` and matching daily equity. Writes `/app/reports/intelligence/provider-180d-latest.json`, `provider-observations.json`, and cadence reports. No API access or brokerage orders. The Collective2 strategy equity represents provider capital, NOT Trading Lab capital. No provider is approved for Paper based solely on provider history. Missing or ambiguous equity keys fail closed.

To schedule, invoke via an external EasyPanel scheduler daily; reports for all three cadences are generated each invocation. This is historical-provider review only; it is not a completed Alpaca fill-to-P&L integration or automatic gateway suspension.

## v3.2.1 source diagnostics
If `INVALID_OR_MISSING_SOURCE_DATA` occurs, the provider report now includes
`source_error_type` and `source_error_detail`, and first-record field names
(`equity_field_names`, `trade_field_names`) where available. The adapter also
supports ISO dates, date-only strings and Microsoft JSON `/Date(ms)/` timestamps.
No risk controls or execution permissions have been relaxed. No API keys or
financial values are printed by the field-name diagnostics.
