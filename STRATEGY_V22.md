# v2.2 — Strategy comparison (research only)

Run `scripts/run.sh strategy-compare --sessions 8` for a small first smoke test, followed by `--sessions 20` (note Yahoo API may be slow).

Output: `/app/reports/day/strategy-comparison.json`.

Includes 6 **predeclared** ORB variants vs baseline for both directions, chronological 70/30 train/validation, minimum 30 evaluated train cases for selecting a candidate, and explicit no-trade gating. It is **not** a live signal filter, an execution engine, a walk-forward study, or proof of positive expectancy. No orders. Setups with low volume are excluded from that variant's traded sample but retained as skipped cases in denominators. Each ticker is fetched only once.

Do not use `validation` to pick a winner or change thresholds; record new data out of sample.
