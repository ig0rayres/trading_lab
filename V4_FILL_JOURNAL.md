# V4 Fill Observation Journal — internal development stage

Run: `./scripts/run.sh v4-fill-journal --input /app/reports/alpaca-order-snapshot.json --journal /app/reports/fill-observations.json`

Input: Alpaca Paper GET **order snapshot** JSON, with `orders` array including `id`, `symbol`, `side`, `status`, `qty`, `filled_qty`, `filled_avg_price` and optional `legs`. Always treat it as **unattested** until the ingestion origin is verified. A broker order's cumulative `filled_qty` is observed per order ID; identical snapshots are idempotent and increases yield incremental observed quantities. Hash-chain verifies accidental alteration (not a cryptographic guarantee against a malicious writer who can rewrite the whole file). Journal is written atomically and rejects corrupt progress. Run one writer only; concurrent writes are not supported.

**Restrictions:** No broker API call, no order submission, no execution authorization, no assumption that all historical orders are returned, no verified trade closure, no verified fees or P&L, no daily/weekly realized loss verification, no broker reconciled flag. This tool cannot be used to bypass the central risk fail-closed state. Do not deploy as a complete autonomous execution feature.

Validation: `PYTHONPATH=.:src pytest -q` (334 tests passed on Oct 29 2026); CLI smoke tested with offline sample. Existing EasyPanel deployments not modified.
