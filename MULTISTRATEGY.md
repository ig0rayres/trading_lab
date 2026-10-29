# Trading Lab v0.8: Multi-strategy research

The research runner calls the **original** GitHub modules. It does not implement its own entry scanner, exit planner, position-size calculator, or risk checker. Only orchestration, historical data integrity, and result accounting are local. No broker API is present.

## Run (in EasyPanel container)

```sh
/app/scripts/run.sh test-local
/app/scripts/run.sh multistrategy --days 55 --symbols TSLA,NVDA,AMD --output /app/reports/multistrategy/v08
cat /app/reports/multistrategy/v08/summary.json
```

## Eight registered hypotheses

- `orb_15_mid`: original 15-minute ORB; midpoint stop.
- `orb_15_low`: same ORB; low of opening range as stop.
- `orb_15_volume15`: same ORB; volume of trigger bar at least 1.5x opening-range average; midpoint stop.
- `prev_high_breakout`: original entry level trigger above previous **completed** session high; percentage stop 1% from actual simulated entry.
- `high20_breakout`: level trigger above the high of the preceding 20 complete sessions; 1% stop.
- `bull_flag_breakout`: original daily scanner's `bull_flag` tag computed at end of *previous* session, followed by level trigger over previous session high; 1% stop.
- `ma20_reclaim_breakout`: prior-session `reclaim_ma20` tag, then previous session high level trigger; 1% stop.
- `oversold_bounce_breakout`: prior-session `oversold_bounce` tag, then previous session high level trigger; 1% stop.

Every hypothesis tests 1R and 2R targets and applies the same cost model. The daily pattern qualifiers are **research combinations**, not prebuilt full entry strategies from upstream. Upstream provides the daily tags and the level trigger independently; this runner joins them explicitly.

IMPORTANT: Upstream `find_setups` requires 30 previous complete daily closes. The Yahoo 5m history is limited to ~60 calendar days, so some filtered strategies may have few or no signals; inspect `summary.json` and `errors.json`. Do not interpret a small or empty sample as evidence of an edge. The prior-20-high hypothesis also requires 20 previous complete sessions. Do not broaden a run from today's preselected watchlist: use a fixed universe declared in advance. `--offline-dir` allows longer archived inputs subject to the same point-in-time constraints.

## Interpretation

The 8 strategies have correlated observations, and target variations are not independent. All results are exploratory; descriptive 70/30 chronological splits are not a held-out evaluation. No full portfolio simulation, no execution fills, no broker, no live capital. Pick a small number of hypotheses, collect truly new periods and validate out of sample. In particular, the same-day signal does not imply that its prior-day tag was knowable in advance; the runner computes it using only sessions strictly before that trading date.
