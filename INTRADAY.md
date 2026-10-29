# Intraday partial replay

Deploy the zip with EasyPanel Source Upload, retain /app/reports and /app/vendor mounts.
Run `/app/scripts/run.sh test-local`, then `/app/scripts/run.sh orb-batch --date 2026-10-26 --intraday`.
Read `/app/reports/orb/intraday-2026-10-26/summary.json` and `trades.csv`.

This mode discards incomplete candles, refreshes current-day Yahoo cached data and marks unresolved positions to market at the latest completed bar. The results are NOT final, cannot establish strategy profitability, and should not be ranked as final completed trades. The final run (without `--intraday`) uses `/app/reports/orb/batch-2026-10-26` and refreshes current-day data as well.
