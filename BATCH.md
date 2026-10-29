# ORB batch - EasyPanel v0.4

Upgrades the existing EasyPanel application. **Keep the existing persistent volumes** `/app/reports` and `/app/vendor`; do not recreate or delete them. No HTTP port, database credentials or brokerage credentials required.

1. EasyPanel > research > Source > Upload: upload this archive; choose Dockerfile and Deploy, keeping volumes and env vars.
2. Shell: `/app/scripts/run.sh test-local` (expected 8 tests).
3. After the US session ends and Yahoo has posted final candles (try after ~16:10 New York time), Shell:
   `/app/scripts/run.sh orb-batch --date 2026-10-26`
4. Outputs are in `/app/reports/orb/batch-2026-10-26/`: `trades.csv`, `summary.json`, `errors.json`, `cache/`.
5. Concise result: `cat /app/reports/orb/batch-2026-10-26/summary.json`; errors: `head -c 3000 /app/reports/orb/batch-2026-10-26/errors.json`.

Connectivity test only: `/app/scripts/run.sh orb-batch --limit 3`. This can be run earlier, but no trades are expected before the entire session becomes available. If you ran early, delete only incomplete fetched cache files from `/app/reports/orb/batch-2026-10-26/cache/` before retrying; the script caches by ticker and does not refresh intraday cached data.

CAUTION: this is a single-session exploratory replay, **not an unbiased historical backtest**. Daily selection was based on a previous close; results cannot justify trading without a reconstructed historical universe, walk-forward splits, and realistic market data. Trades are per-share hypothetical results, not a portfolio. Trades.csv is not a brokerage ticket. No broker connection exists.

This program calls Yahoo's unofficial market-data service and caches raw JSON. Treat any quote inconsistency, missing bars, partial session, or provider failure as no trade. It does not change the upstream source.
