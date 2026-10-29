# EasyPanel upgrade — Trading Lab v0.6

**Keep the existing service, volume mounts and database untouched.** Do not create an additional service, PostgreSQL database, public domain, or HTTP port. This package uses the Dockerfile and has an idle long-running command by default. The ZIP contains one project folder; configure the build context to that folder if EasyPanel does not strip it automatically.

1. In existing EasyPanel `trading-lab`, replace the source ZIP with v0.6 and select Dockerfile build; do **not** delete `/app/reports` or `/app/vendor`.
2. Environment must contain `LIVE_TRADING_ENABLED=false`. No broker credentials. Keep `/app/reports` and `/app/vendor` persistent mounts.
3. Deploy once.
4. Shell: `/app/scripts/run.sh verify`. This executes 21 local offline tests, exercises the real original modules using a deterministic synthetic fixture, and runs the upstream repository's own tests. If the original repository has been updated, parity may fail; do not force it to pass without inspecting the upstream changes.
5. Shell: `/app/scripts/run.sh history --days 30 --symbols TSLA,NVDA,AMD --output /app/reports/history/v06-first-run`.
6. Shell: `cat /app/reports/history/v06-first-run/summary.json`.
7. Optional offline comparator for v0.5: `/app/scripts/run.sh orb-parity --date 2026-10-26`. It will report mismatches if original rounding or entry logic differs.

### If `verify` says the original repository is missing

The original `day-trader-skill` checkout must exist under `/app/vendor/day-trader-skill`; earlier v0.5 testing confirmed it on your service. If you migrated/recreated the vendor volume, review the source before allowing its first fetch:

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
