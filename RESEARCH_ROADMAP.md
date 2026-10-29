# Trading Lab v0.9: evidence-first research workflow

**Key correction:** The upstream `Jakeschincariol/day-trader-skill` is a toolbox for discovering signals, planning entries/exits, and simulating trades; it does **not** publish a validated profitable trading strategy. Preserve and reuse the modules; do not infer an edge from passing its tests.

## External code evaluated for potential reuse (not bundled, not validated)

| Project | Role | License | Decision |
| --- | --- | --- | --- |
| https://github.com/Jakeschincariol/day-trader-skill | Signal scanner, entry/exit, risk | MIT | Retain pinned upstream |
| https://github.com/QuantConnect/Lean | Event-driven portfolio backtests, fill/cost models | Apache-2.0 | Assess as **separate** research engine after data access is settled; do not pretend integrated |
| https://github.com/kernc/backtesting.py | Quick single-instrument strategy prototyping | AGPL-3.0 | Do not bundle without licensing review |

These are *engines and utilities*, not independently validated profitable strategies. A strategy candidate only qualifies once a full set of executable rules, data provenance, transaction costs, and reproducible baselines are available.

## Candidate acceptance pipeline

1. **Find published implementation**: exact source URL, immutable commit, license, full entry/exit/stop and parameters, date/universe used.
2. **Reproduce** original published backtest without optimizing it or changing costs, including an independent calculation of trades/metrics.
3. **Attack biases**: hindsight in universe membership, intrabar ordering, survivorship, splits, data gaps, leverage, overlapping trades, fees and spreads.
4. **Run untouched time-split and multiple market regimes**. No parameter choice after looking at that holdout.
5. **Portfolio simulation** with cash, max exposure, trade overlap, realistic lot sizes and execution friction suitable for small capital.
6. **Paper trading only** after genuine out-of-sample evidence. No broker included in this research Docker image.

## v0.9 scope

- Carry forward v0.8's original-source integrated `history`, `multistrategy`, `timemachine-audit` commands.
- New `research-audit`: **read-only** conservative evidence screen that ingests existing v0.8 reports and publishes per-strategy reasons for rejection or further validation.
- Do not silently add a strategy or mark one profitable just because a few trades show positive mean.
- The new evidence screen is **not a walk-forward engine**, brokerage simulator, or proof of positive expectancy.

Run: `/app/scripts/run.sh research-audit --report /app/reports/multistrategy/v08-expanded --output /app/reports/research/v09-screen.json`

Next technical milestone: reproducible published strategy reference + sufficient legally sourced point-in-time data + untouched holdout. This requires data and exact code; it is not claimed complete in v0.9.
