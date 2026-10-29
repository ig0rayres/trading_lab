# v2.0 - Bidirectional ORB research (no orders)

Day radar now detects **LONG** first close above the high of the first three complete 5-minute bars and **SHORT** first close below their low. Each direction reports separately in `directions.LONG` and `directions.SHORT`, and `research_setups`. Legacy `research_setup` remains the LONG setup only for existing consumers.

This is a *detector*, not a validated profitable strategy. A given ticker may show both directional breakouts at different times. No trader is authorized to enter. No short borrow or availability checks are performed. A short may require margin and whole shares and faces unbounded losses and gap/recall risks. The user-defined R$5k capital budget / R$50 planned stop risk / three positions are research constraints, **not executable risk enforcement**. Neither paper nor live orders are submitted.

Commands:

```sh
/app/scripts/run.sh test-local
/app/scripts/run.sh paper-audit
/app/scripts/run.sh day-radar
/app/scripts/run.sh swing-radar
```

Retain existing EasyPanel command `/app/scripts/run.sh dual-daemon --interval-minutes 30`, with one replica and `/app/reports` persistent.

`/app/reports/day/latest.json` has per-ticker first confirmation time for both directions. `setups` in terminal output counts directional detections, not distinct assets; `long_setups` and `short_setups` split them.

Swing scanner remains LONG research only. A future separate, point-in-time verified short swing model requires its own risk tests.
