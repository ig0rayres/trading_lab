# N58 plan-time — Collective2 API4 listing vs recovered client

> Frente `front/sinais-raw-path` · 2026-11-19 · Git First (planner). Not product code.

## Recovered client (this repo)

`src/c2_history_collect.py` talks to `https://api4-general.collective2.com` with GET + Bearer. Paths in `PATHS`:

- `/Strategies/GetStrategyHistoricalDailyEquity`
- `/Strategies/GetStrategyHistoricalEquity`
- `/Strategies/GetStrategyHistoricalClosedTrades`

Each call requires `StrategyId`. `src/c2_signal_feed.py` adds `/Strategies/GetStrategyActiveOrders` with `StrategyIds`. There is **no** recovered search, roster, or leaderboard call.

`c2_history_collect.fetch` is **GET-only** (`urllib.request.Request` + query string, timeout 25s).

## Official API4 (docs inventory, 2026-11-19)

General API v4 on the same host documents:

| Endpoint | Verb | Role | N58 decision |
|----------|------|------|----------------|
| `/Strategies/SearchStrategies` | GET | Paginated list of strategies **available to the user** (live, publicly subscribable). Optional name / security-type filters. `Results[].StrategyId`, `IsAlive`, `IsPrivate`. `Pagination.next_cursor`. | **adapt** — ID universe for Atualizar. Reuse existing `fetch`. Do **not** use name/score/cost as Feature 4. |
| `/Strategies/SearchHistoricalStrategies` | POST | Optional up to **six Collective2 statistics** (`GetHistoricalStrategiesStatsList`) plus graveyard flag. | **forbidden** — C2 stats ≠ recovered `WINDOW_DAYS` / `MIN_TRADES` / 3-day / shrunk win-rate; recovered client has no POST helper. |
| `/Strategies/GetLeaderBoard` | GET | Curated public leaderboard. | **forbidden** — not Feature 4 / Prodígio 15d. |
| `/Strategies/GetStrategyDetails` | GET | Per-id C2 Score, drawdown, returns. | **do not use as eligibility** — would invent non-recovered thresholds. History + `prodigy_rank.calculate` remains the filter. |
| `/Strategies/GetStrategyHistoricalClosedTrades` | GET | Already in `PATHS`. | **call** after SearchStrategies IDs. |

Pagination (official): `Cursor`, `Limit` (documented max 1000, default 1000), `AscendingOrder`; stop when `next_cursor` empty. Cursors expire (~1h).

## Minimal adaptation (no invented marketplace)

1. One GET `SearchStrategies` per Atualizar (reuse `fetch`; omit invented `Limit` — API default). Persist `Pagination.next_cursor` on the existing candidates-refresh snapshot so the next click continues. If `next_cursor` remains, record an honest incomplete issue — do not pretend the whole catalog was scanned.
2. For IDs on that page, GET `GetStrategyHistoricalClosedTrades` only (the dataset `prodigy_rank.calculate` already globs). Skip daily/monthly equity on the scan path.
3. Eligibility = recovered Prodígio 15d in `prodigy_rank` (`WINDOW_DAYS = 15`, `MIN_TRADES = 5`, ≥3 active days, shrunk win-rate > 55, no `NO_RECENT_CLOSED_TRADE`). Do **not** copy C2 Score / leaderboard / historical-stat filters.
4. Skip `IsPrivate=true` (API test/private flag). Do not invent MonthlyCost or Score cutoffs.
5. Allowlist / env / ledger approve stay the **paper-copy** gate. Scan IDs may appear as pending without allowlist.
6. Stop the history loop on the recovered 25s HTTP timeout; persist what was written; honest issue.

## TradingView

No search/list endpoint in recovered `tradingview_webhook.py` / worker / live-criteria job. ADR-012: ingested origins only. **OUT of N58 scan** until a search contract exists (ISS-025).
