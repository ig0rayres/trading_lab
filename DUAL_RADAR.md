# Trading Lab v1.9: dual research radar

Day strategy: 15-minute ORB, 5-minute completed Yahoo bars only; no profitability validation.
Swing strategy: existing conservative fundamentals/news/technical research, unchanged.
Output: `/app/reports/day/latest.json`, `/app/reports/swing/latest.json`, `/app/reports/shadow/`.
`NO_TRADE` and `order_eligible=false` are mandatory for both engines. No order endpoint is implemented.

## EasyPanel
Keep secrets and existing persistent `/app/reports` volume. One replica, start command:
`/app/scripts/run.sh dual-daemon --interval-minutes 30`

Do not run `radar-daemon` and `dual-daemon` concurrently. The unified daemon performs both scans at each interval and the existing shadow journal after 16:15 ET. NYSE holidays and early-close rules are not fully implemented: reports cannot authorize trades. Do not interpret a setup as a buy signal.

Validation after deployment:
`/app/scripts/run.sh test-local`
`/app/scripts/run.sh paper-audit`
`/app/scripts/run.sh day-radar`
`/app/scripts/run.sh swing-radar`

Day feed is an unofficial delayed Yahoo endpoint; `PARTIAL_DATA` means some symbols unavailable. Preserve stop-on-error semantics. Existing v1.8 replay remains technical-only. Historical news point-in-time reconstruction, broker execution guards, order sizing, fill slippage and fee modeling still require work. A 1% theoretical stop is NOT a guaranteed worst-case loss. No day strategy is approved for trading.
