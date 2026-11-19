# N59.0 Git First — Ordens ativas não abortam a varredura Collective2 (ISS-024)

> Rock PLAN N59 · 2026-11-19 · frente `front/sinais-raw-path` · **no vendor bump** · **LIVE false**  
> Plan-time inventory (planner Grok). EXECUTE (N59.0) re-checks `git ls-remote` and records confirmation; do not bump.  
> **Não** usa os identificadores N45–N47.  
> N58 já em `main` (PR **#78** merge `e7de7b6797cf39a755348d872d2a3db3ae46c541`). Reuse the N54–N58 POST/job — **isolate active-order snapshot from SearchStrategies + closed_trades + Feature 4**. Do not add a parallel package.  
> Active-order snapshot is **read-only diagnostic**, not Feature 4 eligibility.  
> ISS-025 TradingView scan stays **OUT**.

## Why this sprint

Operator confirmed on EasyPanel after N58:

1. `SearchStrategies` alone → HTTP 200, 846 Results.
2. `c2_signal_feed.snapshot` with 5 IDs → HTTP 403; with all 846 → HTTP 414.
3. `_live_refresh_collective2` calls `snapshot(snap_ids, ...)` **inside the same try** as the scan → the C2 source fails with `collective2_refresh_failed:HTTPError` even when search + closed trades already succeeded.

`urllib.error.HTTPError` subclasses `OSError` in Python 3, so the existing `except (OSError, ValueError, ...)` **does** catch it — and that is the bug: it skips `sources_ok.append('collective2')` and reports the whole source dead.

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| SearchStrategies + closed_trades + `prodigy_rank.calculate` | N58 wired | **keep** — this is eligibility |
| `c2_signal_feed.snapshot` / `GetStrategyActiveOrders` | Recovered diagnostic CLI | **adapt** — isolate; never pass the scan page; prefer skip on live-criteria when no named copy IDs |
| Feature 4 / Prodígio 15d constants | `prodigy_rank` | **call** — do not change |
| Paper-copy allowlist | `load_c2_paper_copy_approved_ids` | **keep** as copy gate; optional snapshot limiter only |
| TradingView search | Does not exist (ADR-012) | **OUT** — ISS-025 |
| trader-* vendor | `src/original.py` | **do not call** |
| Batching/encoding 846 IDs into `GetStrategyActiveOrders` | Would invent a new client | **forbidden** |

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` (plan-time 2026-11-19) | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` **matches pin** |
| Local `vendor/day-trader-skill` | Directory exists but **empty** (`git -C` walks up to this worktree). Do **not** bump. |

Upstream has no PanelShell, no live-criteria job, no `c2_signal_feed.snapshot`. Load trader-* only via `src/original.py`.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests |
|------------|-----------------|----------|-----------|-------|
| C2 HTTP GET | `c2_history_collect.fetch` | **call** | Scan path unchanged | N58 mocks remain |
| SearchStrategies | GET `/Strategies/SearchStrategies` | **keep** | Eligibility universe | mock 200 Results |
| Closed trades | `PATHS['closed_trades']` | **keep** | Rank input | Feature 4 pass/fail |
| Rank 15d | `prodigy_rank.calculate` | **call** | Do not change constants | eligible queue |
| Live C2 job | `_live_refresh_collective2` | **adapt** | Snapshot today shares the scan `try` | 414 must not abort |
| Active-order snapshot | `c2_signal_feed.snapshot` | **isolate / skip on scan** | Diagnostic; URL with 846 `StrategyIds` is 414; 403 is access, not eligibility | HTTPError 414 recorded; queue remains |
| Paper-copy IDs | `load_c2_paper_copy_approved_ids` | **keep** | Appear ≠ copy; may limit snapshot IDs | empty → no scan-page snapshot |
| Queue | `build_preapproval_queue` | **keep** | Still only `PRODIGY_CANDIDATE_RESEARCH` | empty allowlist |
| TV origins | `_unique_tradingview_origins` | **keep** | ISS-025 | no invented TV HTTP |
| trader-* | `src/original.py` | **do not call** | Not copy/rank/snapshot | — |

## Honest gaps

### Active orders are not Feature 4

`GetStrategyActiveOrders` is a read-only watcher (`execution_authorized: false`). N50 already labels it as **not a ticket**. N58 incorrectly unioned the SearchStrategies page into `snap_ids`. That is diagnostic scope creep, not eligibility.

### HTTP 414 is a URL limit, not a ranking signal

`fetch_orders` encodes every ID as a `StrategyIds` query parameter. Hundreds of IDs overflow the request line. Do **not** invent a page size, batcher, or new Collective2 client to “make snapshot work” for 846 IDs during Atualizar.

### HTTP 403 on a handful of IDs is access, not eligibility

Five IDs returning 403 does not mean SearchStrategies or closed trades failed. Record an honest snapshot issue and continue.

### N58 tests hid this

`tests/test_panel_ops.py` patches `c2_signal_feed.snapshot` with `_n54_mock_c2_snapshot` (always succeeds). The EasyPanel 414/403 path was never exercised.

## Compatibility / license / security

- MIT vendor via `src/original.py` only; pin unchanged.
- Never print, log, or embed `C2_API4_KEY` / Alpaca keys. Snapshot issue strings: exception type + optional HTTP code only — **no** URL, Bearer, or ID dump.
- `LIVE_TRADING_ENABLED=false`. Refresh ≠ approve ≠ fill.
- **Forbidden:** treating snapshot failure as `collective2_refresh_failed`; passing the SearchStrategies page into snapshot; inventing Feature 4 thresholds; SearchHistoricalStrategies / GetLeaderBoard; TV search HTTP; auto-approve; LIVE true; steal N45–N47; parallel package beside `src/`.
- «Finalizado» only after merge to `main`.

## Plan-time confirmation (2026-11-19)

| Check | Result |
|-------|--------|
| Worktree | `/home/igor/cursor/trading-lab.fronts/sinais-raw-path` |
| Branch | `front/sinais-raw-path` |
| N58 | PR **#78** MERGED (`e7de7b6`) |
| ISS-024 | Open; add N59; keep OPEN |
| TV scan | **OUT** → ISS-025 unchanged |
| Steal N45–N47 | **No** |
| LIVE | **false** |
| `--root` default | **unchanged** `/app/reports` |
| Upstream SHA vs pin | **match** `3d0f4ef` |
