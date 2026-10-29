# Swing radar v1.5 — unattended, READ ONLY

The default container command is still `idle`: **the radar does not run automatically until you set the EasyPanel startup command to `radar-daemon`**. This preserves backwards compatibility.

## EasyPanel

1. Deploy the full ZIP contents as the application source/build context; **preserve `/app/reports` as a persistent volume**, and `/app/vendor` if previously populated. Review bind mounts before replacing files.
2. Retain existing ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL=https://paper-api.alpaca.markets, ALPACA_PAPER_TRADE=true, LIVE_TRADING_ENABLED=false. Add `USD_BRL_REFERENCE` explicitly as BRL per 1 USD (for example `5.00` is ONLY an illustrative placeholder, **not a verified market quote**). Do not post secrets or paste them into a public repo.
3. Run `test-local`, then `paper-audit` and `swing-radar` as one-shot commands to check environment and data providers.
4. For monitoring without operator intervention, set the EasyPanel **startup command/arguments** to `radar-daemon --interval-minutes 30` (in deployments using the Dockerfile ENTRYPOINT, set CMD args; **do not** replace ENTRYPOINT with `python`). This keeps a process running. On startup it waits for its scheduled trading window. The run schedule is New York weekdays 09:30–16:00 ET, every 30 minutes, plus one after-close pass at 16:15 ET. It uses ZoneInfo for daylight saving but **does not track US exchange holidays**.
5. Read `/app/reports/swing/latest.json` for last run and `health`. Report is updated atomically. `NO_MARKET_DATA`, `PARTIAL_DATA`, or Paper flags mean data must be reviewed before any decisions. If the container restarts, the scheduler restarts; **no missed-run catch-up**. The schedule depends on the container being alive, with functioning network.

## Scope and provenance

- News: Google News RSS per ticker; headlines with keyword tags; **no publisher verification, semantic sentiment classifier, or guaranteed breaking-news latency**. Headline titles can be ambiguous. Original `trader-news` is a conceptual reference, not a bound real-time feed.
- Technical: Yahoo public daily candles (unofficial/subject to blocking), SMA20/SMA50, RSI14, ATR14, recent move, relative volume and 20-day high/low. Daily candles during the market session can be partial. No live intraday order triggers.
- Fundamentals: SEC public companyfacts, last reported values with filing date and form, **not period-normalized financial comparisons**, not a full valuation or analyst consensus. `trader-analyst`, `trader-scanner`, `trader-risk`, `trader-budget` inform the read-only design; original project is not an authenticated trade signal.
- Ranking: simple transparent **attention score** = priority to review, **not alpha/expected returns, a researched profitable strategy, an entry signal, or a recommendation**. Every candidate is `NO_TRADE` and `order_eligible=false`.
- Broker: Alpaca Paper `/v2/account`, `/v2/positions`, `/v2/orders?status=open&limit=500`, all GET via the v1.4 audit. Orders are neither sent nor cancelled; risk caps are **diagnostics only**, not enforced on a future trading route.
- Financial policies: capital equivalent to BRL 5,000, 1% planned per idea, no more than three simultaneous positions, no shorts, no leverage, no live orders. User-supplied FX reference may become stale.

No claim of profits, validated alpha, trades, accurate real-time news, or operational availability should be inferred from local tests. The legacy research commands remain intact.
