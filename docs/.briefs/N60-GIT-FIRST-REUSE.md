# N60.0 Git First — Histórico fechado não aborta a fonte Collective2 (ISS-024)

> Rock PLAN N60 · 2026-11-19 · frente `front/sinais-raw-path` · **no vendor bump** · **LIVE false**  
> Plan-time inventory (planner Grok). EXECUTE (N60.0) re-checks `git ls-remote` and records confirmation; do not bump.  
> **Não** usa os identificadores N45–N47.  
> N59 já em `main` (PR **#79** merge `2d609f08e9d1bf364b95ef67d10f37ac137f145b`). Reuse the N54–N59 POST/job — **isolate closed-trades collect from SearchStrategies success**. Do not add a parallel package.  
> Closed trades feed the existing 15-day rank. They are not a new threshold. Active-order snapshot stays the N59 diagnostic.  
> ISS-025 TradingView scan stays **OUT**.

## Why this sprint

Operator confirmed on the panel after N59 #79 on air (2026-11-19):

1. Orange banner still shows `collective2_refresh_failed:HTTPError` — **not** `collective2_active_orders_snapshot_failed:*`.
2. **Atualizar** stays on «Atualizando candidatos…» while the POST runs or hangs. The operator reads that as «the button does nothing».
3. Queue shows Collective2 rows with every metric «indisponível».
4. Prior lab: SearchStrategies HTTP 200 / 846 IDs. Snapshot 5 IDs → 403; all 846 → 414. N59 isolated that snapshot. The remaining path is `_live_refresh_collective2` calling `_invoke_c2_closed_trades_collect(scan_ids, …)` for the full SearchStrategies page **inside** the same `try` that appends `sources_ok` `'collective2'`.
5. `urllib.error.HTTPError` subclasses `OSError`, so the outer `except` records `collective2_refresh_failed:HTTPError` and the C2 source dies before the filter/queue from that scan.

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| SearchStrategies | GET `/Strategies/SearchStrategies` (N58) | **keep** — success is what marks the C2 source ok |
| Closed trades | `PATHS['closed_trades']` = `GetStrategyHistoricalClosedTrades`; `fetch(path, params, token)` per `StrategyId` | **adapt** — per-id skip-on-error, persist partial files, time budget per POST; never one call with the whole page |
| Rank 15d | `prodigy_rank.calculate` | **call** — do not change constants; run on whatever files landed |
| Active-order snapshot | `_run_collective2_active_orders_snapshot` (N59) | **keep** — do not put scan page IDs back |
| Paper-copy allowlist | `load_c2_paper_copy_approved_ids` | **keep** as copy gate |
| Button script | `_CANDIDATES_RELOAD_SCRIPT` | **adapt** — AbortSignal/timeout on the existing POST; no new status route |
| TradingView search | Does not exist (ADR-012) | **OUT** — ISS-025 |
| trader-* vendor | `src/original.py` | **do not call** |
| New bulk query / new C2 client for 846 IDs | Would invent an endpoint | **forbidden** |

## What the current code already does (do not "fix" the wrong layer)

- `_panel_c2_closed_trades_collect` loops IDs and **swallows** `OSError` (hence `HTTPError`) per ID when `c2_history_collect.fetch is _C2_API4_HTTP_FETCH`. That path is silent: no partial issue, and it still sits inside the outer `try` that owns `sources_ok`.
- `_invoke_c2_closed_trades_collect` **else** branch (when `fetch` was replaced) calls `bound_fetch(list(strategy_ids), …)` — one shot for the whole page. Any `HTTPError` there hits the outer `except`.
- `fetch` uses `urlopen(..., timeout=25)` with **no** job-level stop. Hundreds of IDs can hold the POST.
- `_CANDIDATES_RELOAD_SCRIPT` sets «Atualizando candidatos…», `fetch` with **no** `AbortSignal`, and only clears `aria-busy` in `finally` after the browser `fetch` settles. A hung POST leaves the button looking stuck.
- `_live_criteria_job` already calls `_live_refresh_prodigy` after Collective2. If the C2 `try` returns early on `HTTPError`, new trade files were not written, so rank/queue stay on stale or empty raw («indisponível»).

N60 must make SearchStrategies success the `sources_ok` condition, surface `collective2_closed_trades_partial_failed:*`, persist partial raw, keep the rank call, and end the infinite loading label. Another identical silent `continue` is not the sprint.

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` (plan-time 2026-11-19) | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` **matches pin** |
| Local `vendor/day-trader-skill` | Directory exists; `git -C` **toplevel is this worktree** (`0db61454` is the front HEAD, not a vendor commit). Do **not** bump. |

Upstream has no PanelShell, no live-criteria job, no closed-trades panel collect. Load trader-* only via `src/original.py`.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests |
|------------|-----------------|----------|-----------|-------|
| C2 HTTP GET | `c2_history_collect.fetch` | **call** | Per-id `StrategyId`; timeout already 25s | mock HTTPError on one ID, success on another |
| SearchStrategies | GET `/Strategies/SearchStrategies` | **keep** | Eligibility universe; its HTTPError stays `collective2_refresh_failed` | mock 200 Results |
| Closed trades | `PATHS['closed_trades']` | **adapt** | Isolate from `sources_ok`; skip-on-error; persist partial | partial issue, queue from good files |
| Rank 15d | `prodigy_rank.calculate` | **call** | Do not change constants | eligible queue |
| Live C2 job | `_live_refresh_collective2` | **adapt** | Collect today shares the scan `try` | HTTPError must not abort source |
| Active-order snapshot | `_run_collective2_active_orders_snapshot` | **keep** | N59 isolation | N59 tests stay green |
| Paper-copy IDs | `load_c2_paper_copy_approved_ids` | **keep** | Appear ≠ copy | empty allowlist |
| Queue | `build_preapproval_queue` | **keep** | Still only `PRODIGY_CANDIDATE_RESEARCH` | files that landed |
| Button | `_CANDIDATES_RELOAD_SCRIPT` | **adapt** | AbortSignal on existing POST | script leaves loading on AbortError |
| TV origins | `_unique_tradingview_origins` | **keep** | ISS-025 | no invented TV HTTP |
| trader-* | `src/original.py` | **do not call** | Not copy/rank/collect | — |

## Honest gaps

### Closed trades are the rank input, not a second client

`GetStrategyHistoricalClosedTrades` is already per strategy ID. Do **not** invent a bulk query, page size, or new Collective2 path to "speed up 846 IDs". Bound the **job** (stop scheduling new IDs when a wall-clock budget elapses; persist the remainder; resume on the next click). The budget is operational and must **not** be stored as `WINDOW_DAYS` or `MIN_TRADES`.

### Silent per-id swallow hid the operator message

Continuing after `OSError` without an issue makes a partial collect look like success, while an escaped `HTTPError` looks like the whole source died (`collective2_refresh_failed`). N60 needs a **distinct** code: `collective2_closed_trades_partial_failed:*`.

### The button hang is the browser wait, not a missing route

Do not add a job-status endpoint. Put a deadline on the existing `fetch` POST and an honest Portuguese message when it aborts. The server must also return inside that deadline (time budget), or the abort only unsticks the label while the worker keeps running — still record the partial and return.

### N58/N59 tests hid this

Scan tests mock closed-trades collect as success (or never raise `HTTPError` from inside the shared `try` after a good SearchStrategies). The on-air `collective2_refresh_failed:HTTPError` path was not the N59 snapshot case.

## Compatibility / license / security

- MIT vendor via `src/original.py` only; pin unchanged.
- Never print, log, or embed `C2_API4_KEY` / Alpaca keys. Partial-collect issue strings: exception type + optional HTTP code only — **no** URL, Bearer, or ID dump.
- `LIVE_TRADING_ENABLED=false`. Refresh ≠ approve ≠ fill.
- **Forbidden:** mapping closed-trades HTTPError to `collective2_refresh_failed` after SearchStrategies succeeded; one `fetch` call with the full scan page; inventing Feature 4 thresholds; putting scan IDs back into the active-order snapshot; SearchHistoricalStrategies / GetLeaderBoard; TV search HTTP; auto-approve; LIVE true; steal N45–N47; parallel package beside `src/`.
- «Finalizado» only after merge to `main`.

## Plan-time confirmation (2026-11-19)

| Check | Result |
|-------|--------|
| Worktree | `/home/igor/cursor/trading-lab.fronts/sinais-raw-path` |
| Branch | `front/sinais-raw-path` |
| N59 | PR **#79** MERGED (`2d609f0`) |
| ISS-024 | Open; add N60; keep OPEN |
| F-023 | corrigido — `N60PartialClosedTradesCollectTests` (EXECUTE 2026-11-19) |

## EXECUTE confirmation (N60.0)

Pin `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` re-checked at EXECUTE 2026-11-19; **no vendor bump**. Inventory above unchanged; implement isolation in `v4_web_dashboard._live_refresh_collective2` + button `AbortController` in `panel_ops_html`.
| TV scan | **OUT** → ISS-025 unchanged |
| Steal N45–N47 | **No** |
| LIVE | **false** |
| `--root` default | **unchanged** `/app/reports` |
| Upstream SHA vs pin | **match** `3d0f4ef` |
| Local vendor checkout | **not an independent HEAD** (git toplevel walks up) |
