> **v3.9 Paper monitor pilot:** See `PAPER_MONITOR_V39.md` for read-only broker reconciliation and current automation gaps.

## v2.3 News-first coverage audit

See [NEWS_FIRST_V23.md](NEWS_FIRST_V23.md). New safe command: `news-audit`; this checks data access only, it does not generate trading signals.

## v2.1 — ORB LONG/SHORT replay (research only)

See [DAY_REPLAY.md](DAY_REPLAY.md). Run `/app/scripts/run.sh day-replay --sessions 20` and inspect `/app/reports/day/historical-long-short.json`. No orders.

# Trading Lab v0.8 - Multi-strategy research

Research only. **Never places live or paper orders.** Preserve `/app/vendor` and `/app/reports` volumes from the previous EasyPanel deployment. This version extends v0.7 without removing previous commands and reports.

The primary new command is `multistrategy`. See `MULTISTRATEGY.md` for all eight hypotheses, data requirements, and limitations.

```sh
/app/scripts/run.sh test-local
/app/scripts/run.sh multistrategy --days 55 --symbols TSLA,NVDA,AMD --output /app/reports/multistrategy/v08
cat /app/reports/multistrategy/v08/summary.json
```

This runner reuses *original* `trader-entry`, `trader-exit`, `trader-budget`, `trader-risk` and `trader-scanner` Python functions from the existing `Jakeschincariol/day-trader-skill` checkout. The qualifying scanner signals and level-based triggers are combined in this project and **are not** complete published upstream strategies. Monte Carlo uses original `trader-timemachine` via the previous v0.7 `timemachine-audit` command.

Historical Yahoo 5-minute bars are unofficial and typically limited to 60 calendar days. Fixed present-day ticker universes have survivorship bias. Strategy comparisons in this window are exploratory and do not authorize trading capital.

## v0.9 research audit (read-only)

See `RESEARCH_ROADMAP.md`. The `research-audit` command screens existing v0.8 studies, counts data diagnostics, and **never** approves live trading. Example:

```sh
/app/scripts/run.sh research-audit --report /app/reports/multistrategy/v08-expanded --output /app/reports/research/v09-screen.json
```

This release is a research process upgrade. It **does not** claim a new profitable strategy, a longer historical dataset, or integration with LEAN.

## v1.0 independent research hypotheses

Read `EXTERNAL_RESEARCH.md` for the new `external-research` command: VWAP mean-reversion and a log-price-ratio pairs experiment. These are **new hypotheses**, not a claimed reproduction of a published strategy, nor validated edge. They do not change previous commands.

## Candidate research v1.2
See [CANDIDATES.md](CANDIDATES.md) for four daily exploratory strategies and the explicitly withheld intraday candidate. Usage: `/app/scripts/run.sh candidate-research --from 2021-01-01 --to 2026-10-23 --split 2025-01-01 --output /app/reports/candidates/v12`.

## v1.3: Overnight/daytime exploratory rule reproduction

New `overnight-research` uses previously cached adjusted Yahoo daily OHLC to evaluate six pre-specified overnight/daytime rules at several transaction cost levels. See `OVERNIGHT_RESEARCH.md`. This does **not** claim to reproduce the publication's WRDS database or its published performance. No broker or live trades.

## v1.4: Alpaca paper read-only audit

Run `paper-audit` to inspect a PAPER account using allowlisted GET requests only. See `PAPER_READ_ONLY.md` for required environment and safety limitations. This version does not place or enable orders.


## v1.5 continuous research monitor
See [SWING_RADAR.md](SWING_RADAR.md). Startup default remains `idle`; to enable automatic read-only monitoring set EasyPanel CMD to `radar-daemon --interval-minutes 30`. **No orders sent.**

## v1.7 Shadow Journal

See [SHADOW_JOURNAL.md](SHADOW_JOURNAL.md) for prospective NO_TRADE decision logging, daily de-duplication and future 5/10/20-observation comparisons against SPY. `shadow-journal` makes no broker requests or orders and uses existing saved radar report. The `radar-daemon` command logs one eligible daily snapshot automatically. Never interpret observational returns as simulated trade fills or proof of profits.

## v2.0: LONG + SHORT day setup detection
See [DUAL_LONG_SHORT.md](DUAL_LONG_SHORT.md). NO_TRADE only, no orders.
