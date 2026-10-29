# V4 Research scheduler (no order submission)

Runs the existing `v4-run-once` pipeline at a configured interval and saves `v4_scheduler.json` next to the market/decision/risk reports. Uses a filesystem lock to prevent overlapping scheduler processes on a shared volume. Upstream failures appear as `FAILED_OR_BLOCKED` and a nonzero code on `--once`; subsequent periodic attempts continue. A timeout stops the child research command. No broker order submission is imported or enabled.

Example (inside the container):

`./scripts/run.sh v4-scheduler --universe /app/config/universe.json --output-dir /app/reports/v4 --interval-seconds 900 --timeout-seconds 180`

Operational prerequisites: persist `/app/reports`, provision a reviewed universe at `/app/config/universe.json`, and test external market data access. This does **not** establish live data authenticity or operational Paper acceptance. Do not replace the existing production services or enable real trading based on this scheduler.
