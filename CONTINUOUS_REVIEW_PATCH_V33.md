# Trading Lab v3.3 - permanent C2 parser correction

- Collective2 `ResponseStatus.ErrorCode` `200` and `"200"` are accepted as a successful response. Unknown codes fail closed.
- Use `EquityWithCosts` as the preferred numerical field, preserving the historical date and calculation rules.
- Adds a descriptive `provider-research-top10-latest.json` output ranked by simple 180-day equity ratio. This is NOT a risk-adjusted, cash-flow-adjusted or copy-eligible ranking.
- No Paper or real orders are submitted by the continuous-review command.
- Current provider history is stored on the EasyPanel server, not included in this ZIP; preserve `/app/reports/providers/raw` across deployments (persistent volume).
- Run `/app/scripts/run.sh continuous-review`.
- Existing daily/weekly/monthly reports are NOT automatic scheduling and NOT order-blocking gates.
