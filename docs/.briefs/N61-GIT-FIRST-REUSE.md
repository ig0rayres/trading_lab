# N61.0 Git First — Versão do painel e aviso honesto da listagem (ISS-024)

> Rock PLAN N61 · 2026-11-25 · frente `front/sinais-raw-path` · **no vendor bump** · **LIVE false**  
> Plan-time inventory (planner Grok). EXECUTE (N61.0) re-checks `git ls-remote` and records confirmation; do not bump.  
> **Não** usa os identificadores N45–N47.  
> N60 já em `main` remoto (`git ls-remote origin refs/heads/main` = `42642134715ef899f487c9a92608c1052e16323d`; N60 code `f71c763`). Parent: PR **#80** MERGED. Reuse the N54–N60 POST/job — **label the running image and make SearchStrategies failures honest**. Do not add a parallel package.  
> Closed trades stay the N60 partial path. Active-order snapshot stays the N59 diagnostic.  
> ISS-025 TradingView scan stays **OUT**.

## Why this sprint

Operator on EasyPanel after the N60 deploy (2026-11-19), still true for the parent on 2026-11-25 (view-source and `candidates-refresh-latest.json` were not pasted):

1. Orange banner still shows `collective2_refresh_failed:HTTPError` — no HTTP status number.
2. **Atualizar** still sits on «Atualizando candidatos…».
3. Collective2 metrics still «indisponível».
4. Three hypotheses, all in scope until the panel can tell them apart: (1) image is not N60; (2) the refresh JSON is stale; (3) SearchStrategies really raised `HTTPError` and N60 correctly refused to mark the source ok.

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| Vendor pin | `UPSTREAM_COMMIT` / `docs/VENDOR-PIN.md` | **keep** — this is **not** the trading-lab git SHA |
| App image id | No `APP_GIT_SHA` today. `/healthz` is `{"status":"alive","orders_enabled":false}`. `build_snapshot` has no git field | **adapt** — same ARG/ENV pattern as `UPSTREAM_COMMIT`, different name; surface on `/healthz`, `/api/status`, and Sinais |
| SearchStrategies issue | `collective2_refresh_failed:{type}` in `_live_refresh_collective2` and `_live_criteria_job` | **adapt** — copy `_collective2_active_orders_snapshot_issue` (type + `code` when present) |
| Refresh JSON | `persist_candidates_refresh` / `load_candidates_refresh` | **call** — write `refreshed_at` at start; drop prior `collective2_refresh_failed:*`; keep cursor and pending ids |
| One retry | Not present | **adapt** — only `HTTPError` 429 or 500–599, one extra call, no sleep |
| Closed trades | N60 per-id + `collective2_closed_trades_partial_failed` | **keep** |
| Active-order snapshot | N59 | **keep** |
| Button script | `_CANDIDATES_RELOAD_SCRIPT` already has `AbortController` (~45s) | **keep** — regress only |
| Banner | `_candidates_refresh_warning_html` lists issues only | **adapt** — show `refreshed_at` and `sources_ok` beside it |
| TradingView search | Does not exist (ADR-012) | **OUT** — ISS-025 |
| trader-* vendor | `src/original.py` | **do not call** |
| EasyPanel API | Not in this repo | **forbidden** |

## What the current code already does (do not "fix" the wrong layer)

- N60 already isolates closed-trades `HTTPError` from `sources_ok`. A banner that still says `collective2_refresh_failed:HTTPError` is the **SearchStrategies** (or pre-search) path, or a JSON file written before N60, or an image that does not contain N60.
- `_collective2_active_orders_snapshot_issue` already appends `:{code}` when `exc.code` is set. SearchStrategies except blocks do not.
- `serve_signals_candidates_refresh` already persists `refreshed_at` **after** the job returns. A hung POST never reaches that write, so the previous issue stays on disk. The button abort (N60) does not reload the page; it only clears the loading label in the browser that has the new script.
- `/healthz` cannot prove the image. `UPSTREAM_COMMIT` proves the vendor pin only.
- Do not add a job-status route, a broker host, or a second Collective2 client.

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` (plan-time 2026-11-25, `git ls-remote`) | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` **matches pin** |
| Local `vendor/day-trader-skill` | Directory exists; `git -C` **toplevel is this worktree** (front HEAD, not a vendor commit). Do **not** bump. |
| Trading-lab `origin` `refs/heads/main` (plan-time `git ls-remote`) | `42642134715ef899f487c9a92608c1052e16323d` |

Upstream has no PanelShell, no live-criteria job, no image fingerprint for this app. Load trader-* only via `src/original.py`.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests |
|------------|-----------------|----------|-----------|-------|
| Vendor pin env | `Dockerfile` `ARG UPSTREAM_COMMIT` | **copy_pattern** | New `APP_GIT_SHA` default `unknown`; do not reuse the vendor value as the app id | Dockerfile text has both names; healthz shows them separately |
| Liveness | `serve_public_get` `/healthz` | **extend** | Operator and agent already call it | env set → sha; empty → `unknown`; `orders_enabled` false |
| Status snapshot | `build_snapshot` | **extend** | `/api/status` already returns this object | field `app_git_sha` |
| Sinais shell | `render_signals_page` | **extend** | Operator looks here, not only at healthz | version line visible |
| CI image build | `.github/workflows/ci.yml`, `docker-smoke.yml` | **extend** | Pass `--build-arg APP_GIT_SHA` from the commit SHA; do not drop or narrow existing steps | workflow still builds; ARG default keeps a bare `docker build` valid |
| Search issue shape | `_collective2_active_orders_snapshot_issue` | **copy_pattern** | Type + code, no URL | 403 → `collective2_refresh_failed:HTTPError:403` |
| Search call | `_invoke_c2_search_strategies` | **extend** | One retry on 5xx/429 only | call count 2 vs 1 |
| Refresh file | `persist_candidates_refresh` | **call** | Start write + existing end write | stale issue gone; `refreshed_at` changes |
| Closed trades | N60 collect | **keep** | Partial issue stays distinct | N60 tests stay green |
| Snapshot | `_run_collective2_active_orders_snapshot` | **keep** | N59 | N59 tests stay green |
| Button | `_CANDIDATES_RELOAD_SCRIPT` | **keep** | Abort already clears loading | N60 script test stays green |
| Banner | `_candidates_refresh_warning_html` | **extend** | Add time and sources next to the list | HTML contains both |
| Rank 15d | `prodigy_rank` constants | **keep** | Do not change | source still `WINDOW_DAYS = 15` |
| TV origins | `_unique_tradingview_origins` | **keep** | ISS-025 | no invented TV HTTP |
| trader-* | `src/original.py` | **do not call** | Not copy/rank/fingerprint | — |
| Provider approve POST | `signals_providers_post` | **keep** | Already calls `upsert_signal_provider_approval`; refresh must not | refresh slice has no upsert |

## Honest gaps

### The vendor pin is not the deploy fingerprint

`UPSTREAM_COMMIT` stays the day-trader-skill pin. `APP_GIT_SHA` is this repository's commit, injected at image build the same way. Empty means `unknown`. Do not read EasyPanel's digest from inside the app and do not call the EasyPanel API.

### A finished POST already stores `refreshed_at`

The hole is a refresh that never finishes, and an issue string with no status code. Write at **start** (supersede `collective2_refresh_failed:*`, keep `c2_search_next_cursor` and `c2_closed_trades_pending_ids`) and keep the existing write at the end. Do not delete raw trade files.

### Retry is one extra call, not a new threshold

Only `urllib.error.HTTPError` whose `code` is 429 or 500–599. No `time.sleep`. No new module constant that could be confused with `WINDOW_DAYS` or `MIN_TRADES`. 403/414 stay single-shot. The issue recorded is the last error, with code.

### The button hang is already handled in source

N60 `AbortController` cannot appear in an old image. N61 does not reimplement it. Tests must still fail if the loading label becomes the abort message's only missing piece. The version line is how the operator sees that the image lacks N60/N61.

## Compatibility / license / security

- MIT vendor via `src/original.py` only; pin unchanged.
- Never print, log, or embed `C2_API4_KEY` / Alpaca keys. Issue strings: exception type + optional HTTP code only — **no** URL, Bearer, or ID dump.
- `LIVE_TRADING_ENABLED=false`. `/healthz` `orders_enabled` stays false. Refresh ≠ approve ≠ fill.
- **Forbidden:** treating `UPSTREAM_COMMIT` as the app SHA; EasyPanel API deploy; retry on 403/414; retry loops; `sleep` backoffs; inventing Feature 4 thresholds; TV search HTTP; auto-approve; LIVE true; steal N45–N47; parallel package beside `src/`.
- «Finalizado» only after merge to `main` and operator homologation. ISS-024 stays open in this plan.

## Plan-time confirmation (2026-11-25)

| Check | Result |
|-------|--------|
| Worktree | `/home/igor/cursor/trading-lab.fronts/sinais-raw-path` |
| Branch | `front/sinais-raw-path` |
| Remote trading-lab `main` | `42642134715ef899f487c9a92608c1052e16323d` |
| N60 | Parent: PR **#80** MERGED; code commit `f71c763` |
| ISS-024 | Open; add N61; keep OPEN |
| F-024 | aberto (this plan; not corrigido) |
| Vendor `main` vs pin | **match** `3d0f4ef` |
| Local vendor checkout | **not an independent HEAD** |
| `sprint_atual` | **left N60** |
| TV scan | **OUT** → ISS-025 unchanged |
| Steal N45–N47 | **No** |
| LIVE | **false** |
| `--root` default | **unchanged** `/app/reports` |
