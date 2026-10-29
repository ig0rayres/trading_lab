# Day replay v2.1: LONG and SHORT

Run ` /app/scripts/run.sh day-replay --sessions 20 ` inside EasyPanel. This makes *read-only* Yahoo historical queries, not broker requests.

The Yahoo 5-minute timestamp is the **start** of each bar. A 09:45 bar is only available at 09:50. The replay enters at the next bar open (09:50), not the confirmation close. It requires contiguous 5m bars and 09:30/09:35/09:40 opening range. Stop at opposite opening-range boundary; target 2R. Risk US$10 per hypothetical position with US$1000 allocation and integer shares, 5bp per side in friction. Any gap across stop is exited at open; same bar stop/target tie is treated as stop. Studies independently; not a multi-position portfolio. No historical verified news, borrow fees or shortability. It is NOT a backtest of complete strategy, nor execution authorization. Incomplete sessions skipped; Yahoo is unofficial and may be adjusted/lagged. No orders are sent.

Outputs `/app/reports/day/historical-long-short.json`. For live radar `confirmation_available_at_ny` reports end of candle; `first_confirmation_bar_ny` remains candle start to preserve backward compatibility.
