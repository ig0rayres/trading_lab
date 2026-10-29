# v1.7 - Shadow Journal (no orders)

After 16:15 New York time (not during the active trading session), every healthy scheduled radar run now attempts to store ONE prospective observation per **market candle day** at `/app/reports/shadow/observations.jsonl`. The journal never changes a recorded day's earlier decision even if multiple scans occur on that day. It stores close, blockers, score, and NO_TRADE, then computes 5/10/20 **later observed daily scans** close-to-close changes and same-window SPY returns in `/app/reports/shadow/summary.json`.

This **is not a trading simulation or performance proof**: positions are never opened, no hypothetical fills are assumed, there are no true order P&Ls, and no stop fills or gap assumptions are invented. With all 12 symbols flagged NO_TRADE it is correct to show zero trades and zero trading P&L. Returns of declined ideas quantify opportunity cost and allow auditing overly strict filters, not investment performance. Scores do not remove blockers.

Requires healthy SEC/Yahoo/news sources, healthy Paper read-only audit with no open orders or positions, same session date for all assets, and `LIVE_TRADING_ENABLED=false`. A degraded run is skipped rather than making an unsupported decision. Stop and investigate if a preexisting Alpaca position/order is observed. Even though the journal is read-only, keep Alpaca credentials secret and use Paper endpoint only.

## EasyPanel

Deploy full package preserving environment and persistent `/app/reports` volume. Set container arguments `radar-daemon --interval-minutes 30`, NOT `idle`, to enable scheduled research. Script entrypoint remains `/app/scripts/run.sh`. Verify with:

```
/app/scripts/run.sh test-local
/app/scripts/run.sh paper-audit
/app/scripts/run.sh swing-radar
/app/scripts/run.sh shadow-journal
cat /app/reports/shadow/summary.json
```

Note: `swing-radar` manual command updates the latest report, `shadow-journal` is the explicit manual snapshot. The daemon attempts this automatically after the 16:15 New York end-of-day scan if sources and broker audit pass; earlier intraday attempts are skipped. No holiday calendar; data may be from incomplete intraday candles and day may be overwritten by provider feed corrections. Daily sampling will have missing sessions if unavailable. Scheduled reports are not proof of an investment edge.
