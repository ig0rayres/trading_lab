# Overnight/daytime research v1.3

Reference: Salotra et al. (2026), *Risks* 14(4), 84, DOI 10.3390/risks14040084.

Six rule combinations are represented as (overnight, daytime):
- long_cash: (+1, 0)
- cash_long: (0, +1)
- cash_reversal: (0, opposite of current day's close-to-open direction)
- reversal_cash: (opposite of prior session's open-to-close direction, 0)
- long_reversal: (+1, opposite of current day's overnight direction)
- long_long: (+1, +1) passive control.

Positions are selected from available information: prior day open/close for the next overnight position; today's open relative to prior close for the same day's daytime position. Daily adjusted open/close is parsed using the existing candidate_research module.

This is an exploratory, **partial rule reproduction only**: 6 of the paper's 24 strategies, local Yahoo cache rather than WRDS, simple per-change execution costs. Not a validated reproduction of the study's published returns. `long_reversal` and `cash_reversal` require short selling for some sessions, so borrowing and margin costs are missing. All strategies approximate fills at the printed adjusted open or close, without auction impact. Results cannot justify orders.

Use cached data from candidate research, and request sectors which you have actually collected. The v1.2 cache only contained SPY/QQQ/IWM/GLD/TLT and 7 stocks, so the sector ETFs must be collected in a separate **data retrieval step** before the full paper's sector comparison. This command deliberately refuses missing data instead of silently inventing a longer series.

```
/app/scripts/run.sh overnight-research --cache-dir /app/reports/candidates/v12/cache --symbols SPY --from 2021-01-01 --to 2026-10-23 --split 2025-01-01 --cost-bps 2,5,10 --output /app/reports/overnight/v13
cat /app/reports/overnight/v13/summary.json
```

See `errors` for absent symbol caches. Results are separate by ETF, strategy, and cost; do not cherry-pick favorable sector/cost combinations or describe 2025-2026 as independent after examination.
