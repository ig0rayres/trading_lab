# Trading Lab v3.6: Collective2 active-order discovery (read-only)

This adds an actual authenticated Collective2 API4 poller for *active strategy orders*.
Active orders do **not** necessarily equal new subscriber-visible signals, fill events,
trade entries, protective stops, or authorized copies. Treat the first snapshot
as a baseline. Later differences are *changes*, not automatic BUY instructions.

Example:

```
/app/scripts/run.sh c2-signal-feed --strategy-id 30415311 --strategy-id 132169961 --strategy-id 148311109
```

Saves `/app/reports/providers/signals/active-orders-latest.json`. Requires
`C2_API4_KEY` already configured. No orders, subscriptions, changes to API access,
or broker-side actions. The Paper runner remains disabled by default.

## Before copying trades

1. Verify subscription entitlements to actual actionable C2 signals.
2. Verify real-time delivery and legal access, not merely publicly visible orders.
3. Require a supplied protective stop, valid limit and verified fresh quote.
4. Complete the Paper daily-risk gate and broker order lifecycle reconciliation.
5. Explicitly authorize Paper-only automation after tests; real trading remains disabled.

Do not treat historical closed trades as real-time signals.
