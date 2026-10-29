# Trading Lab Evolution Engine v3.8 — read-only foundation

This version adds a **daily evidence report**, not automatic strategy optimization. It does **not** submit orders, change risk thresholds or automatically promote strategy settings.

## Deploy without altering existing running commands

This is an incremental build of the v3.7 archive: update the image in EasyPanel only after backup. **Keep your currently working webhook startup command and environment.** The new command below is a separate, manually triggered task and is not automatically scheduled by this ZIP.

```sh
/app/scripts/run.sh evolution-daily --date 2026-10-28
```

Outputs to `/app/reports/evolution/daily/YYYY-MM-DD.json`. To persist reports, mount `/app/reports/evolution` or a persistent parent volume. The live webhook journal is expected at `/app/reports/webhooks/journal.jsonl` (set `TV_QUEUE_DIR` if needed). If the scheduler runs in a separate container, it must see the *same persistent journal*, not just an identically named folder.

## Track decisions BEFORE the filters

Store JSON events in `/app/reports/evolution/decisions.jsonl`, using the `--record-decision` command and a local file:

```json
{"at":"2026-10-28T20:00:00Z","signal_id":"strategyA-000001","strategy_id":"strategyA","symbol":"AAPL","decision":"REJECTED","reason":"NO_VOLUME_CONFIRMATION","policy_version":"pilot-1"}
```

```sh
/app/scripts/run.sh evolution-daily --record-decision /app/data/decision.json
```

Accepted/observed signals are also supported. Capture each original candidate **before any filtering** with its strategy version and reason. Do not put tokens or credentials in events. Logging a rejected candidate is not equivalent to measuring its hypothetical P&L.

## Missing parts (explicit)

- Automated collection of all candidate signals *before* filtering is **not wired** to existing strategy producers yet.
- Rejected entry performance requires independently sourced historical price-path data with timestamps, fees, spread and slippage.
- Actual Paper fills and exits need broker reconciliation; PREVIEW_ONLY is **not** performance evidence.
- Statistical testing, champion/challenger scoring, and promotion/rollback are not implemented in this release.
- Daily schedule is **not** installed by this artifact. Run via EasyPanel scheduled job or cron after verifying persistent mounts.
- Legacy risk code still contains a R$5,000 capital setting and must be reconciled with the proposed R$10,000 / R$100 policy before enabling Paper order submission.

**Safety:** keep `LIVE_TRADING_ENABLED=false`, `PAPER_EXECUTION_ENABLED=false`, `PAPER_SIGNAL_AUTO_ENABLED=false`. Do not turn on live trades.
