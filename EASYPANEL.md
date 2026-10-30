# EasyPanel — Trading Lab (N6+)

**Keep the existing EasyPanel project (hashia): two apps, one image.** Do not add a third service or enable live trading.

| App | Start (typical) | Notes |
|-----|-----------------|-------|
| `trading-lab` | Dockerfile `CMD` → `v4-scheduler` | Research scheduler; ledger DSN optional |
| `trading-lab-webhook` | `/app/scripts/run.sh tv-webhook --port 8080` (+ worker loop if configured) | Public HTTPS; `LEDGER_DATABASE_URL` + paper read keys here |

**N6 image:** vendor @ SHA in `docs/VENDOR-PIN.md` is **baked in the Dockerfile** at build time. Persist **`/app/reports` only**. Do **not** mount an empty directory on `/app/vendor` — it hides the baked tree and breaks `load_original`. Remove startup `git clone` hacks after the first successful N6 deploy.

1. Rebuild **both** apps from the same Dockerfile tag/SHA after merge to `main`.
2. Environment must contain `LIVE_TRADING_ENABLED=false`. Paper Alpaca keys only on webhook/worker as today.
3. On webhook (ledger): `/app/scripts/run.sh ledger-migrate apply` with `LEDGER_DATABASE_URL` — seeds **7** rows in `strategy_states` (safe to re-run; does not overwrite existing phases).
4. Deploy once.
5. Shell: `/app/scripts/run.sh verify`. This executes 21 local offline tests, exercises the real original modules using a deterministic synthetic fixture, and runs the upstream repository's own tests. If the original repository has been updated, parity may fail; do not force it to pass without inspecting the upstream changes.
6. Shell: `/app/scripts/run.sh history --days 30 --symbols TSLA,NVDA,AMD --output /app/reports/history/v06-first-run`.
7. Shell: `cat /app/reports/history/v06-first-run/summary.json`.
8. Optional offline comparator for v0.5: `/app/scripts/run.sh orb-parity --date 2026-10-26`. It will report mismatches if original rounding or entry logic differs.

### If `verify` says the original repository is missing

After **N6**, `/app/vendor/day-trader-skill` should exist inside the image. If a volume overlay emptied it, remove the `/app/vendor` mount and redeploy. Break-glass only:

```sh
ALLOW_GITHUB_FETCH=true /app/scripts/run.sh upstream-tests
/app/scripts/run.sh verify
```

This downloads third-party Python code into `/app/vendor` and runs its tests. Keep the container isolated from production credentials. For reproducibility, inspect the SHA printed by the command and set `UPSTREAM_COMMIT=...` in your service environment to **lock** that revision; v0.6 refuses a different revision rather than automatically updating to main.

### Files and commands

- `history`: real historical 5-minute data over past sessions; outputs in `/app/reports/history/...`.
- `orb-batch`: original v0.5 batch engine unchanged; uses saved scanner watchlist and previous day's data.
- `orb-parity`: offline comparison of v0.5 with actual GitHub module outputs.
- `verify`: full test suite + actual GitHub module integration.
- `test-local`: offline local tests only, without needing the vendor mount.

Neither deployment nor `history` performs real or paper broker orders.
