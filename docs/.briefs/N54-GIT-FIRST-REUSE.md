# N54.0 Git First — Critérios ao vivo de candidatos (ISS-024)

> Rock PLAN N54 · 2026-11-18 · frente `front/sinais-live-criteria` · **no vendor bump** · **LIVE false**  
> Plan-time inventory (planner Grok). EXECUTE (N54.0) re-checks `git ls-remote` and records confirmation; do not bump.  
> **Não** usa os identificadores N45–N47.  
> Fases analista / designer / arquiteto / contratos DONE. N53 GET reload já em `main` (#71).

## Why this sprint

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| Botão Atualizar candidatos | N53: visível + `GET /api/signals/reload` relê `build_panel_bundle` | **Keep GET**; add `mode: disk_reread` |
| Job critérios ao vivo | Contrato OpenAPI v0.3.0 + ADR-011; **sem** handler POST ainda | **adapt** — novo POST em `v4_web_dashboard.py` que **só orquestra** módulos existentes (não pacote paralelo) |
| Ranking Prodígio 15d | `prodigy_rank.calculate` + `tests/test_prodigy_rank.py` | **call** — never invent score |
| Collective2 HTTP | `c2_signal_feed` + `c2_history_collect.fetch` + tests | **call** from server job only |
| Fila pré-aprovação | `build_preapproval_queue` já une C2 JSON + Prodígio + origens TV | **call** after rewrite JSON |
| Busca TradingView | Não existe no produto | **forbidden** — ADR-012 origens já ingeridas |
| Tabela cooldown | Arquitetura §13.2: sem DDL N54 | **in-process** ~30s (mockup S4) |

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` (plan-time 2026-11-18) | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` **matches pin** |
| Local `vendor/day-trader-skill` | May be uninitialized — do **not** bump |

Upstream has no PanelShell, no ISS-024 refresh job, no OpenAPI `candidates/refresh`. Load trader-* only via `src/original.py`.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests |
|------------|-----------------|----------|-----------|-------|
| Rank Prodígio 15d | `src/prodigy_rank.py` `calculate` (`WINDOW_DAYS=15`, `MIN_TRADES=5`) | **call** | Feature 4 / 9; writes `prodigy-top10-latest.json` | `tests/test_prodigy_rank.py` |
| C2 history read-only | `src/c2_history_collect.py` `fetch` | **call** | Adapter-compatible `{sid}_{kind}.json` wrapper | extend with mock opener |
| C2 active orders | `src/c2_signal_feed.py` `snapshot` / `fetch_orders` | **call** | Research snapshot ≠ ticket | `tests/test_c2_signal_feed.py` |
| C2 named list | `panel_ops_data.load_c2_paper_copy_approved_ids` | **call** | IDs to poll; empty = honest issues, no invented providers | existing N50/N51 |
| Data adapter | `src/strategy_data_adapter.py` `load` | **call** (via rank) | Expects `strategy_id`+`dataset`+`raw.Results` | prodigy tests write that shape |
| Bundle | `panel_ops_data.build_panel_bundle` / `build_preapproval_queue` / `_unique_tradingview_origins` | **call** | TV min + queue rebuild after JSON rewrite | `tests/test_panel_ops.py` |
| POST providers | `signals_providers_post` | **keep** | approve ≠ fill; refresh must not call it | N51 tests |
| Panel CTA | `panel_ops_html._CANDIDATES_RELOAD_SCRIPT` | **extend** — POST live-criteria; same button id | mockups S0–S4 | N54.3 |
| Job HTTP | `src/v4_web_dashboard.py` — **new** `serve_signals_candidates_refresh` (or equivalent) + `do_POST` route | **adapt** | Orquestra `calculate` / `fetch` / `snapshot` / queue rebuild; C2 só processo com env; zero TV search no browser | N54.1 contract tests |
| GET reload | `serve_signals_reload` (`src/v4_web_dashboard.py`) | **adapt** — add `mode: disk_reread`, `execution_authorized: false`; **forbid** `prodigy_rank.calculate` in body | ADR-011 dual mode | N53 tests + slice assert |
| trader-* vendor | `src/original.py` | **do not call** from this job | Not copy/rank logic | — |

## Honest refresh contract (N53 vs N54)

| Layer | N53 (keep) | N54 (this sprint) |
|-------|------------|-------------------|
| Botão | Mesmo CTA outline | Hint + status = critérios ao vivo; S4 cooldown |
| GET `/api/signals/reload` | Releitura bundle | + `mode: disk_reread` |
| POST `/api/signals/candidates/refresh` | Ausente | Job allowlisted; `mode: live_criteria` |
| Scores | Nunca no GET | Só `prodigy_rank.calculate` no job |
| C2 | Nunca no browser | Só processo com `C2_API4_KEY` |
| TV | Origens no bundle | União das mesmas origens; sem API de busca |
| Aprovações / ordens | Intocadas | Intocadas |

## Compatibility / license / security

- MIT vendor via `src/original.py` only; pin unchanged.
- Never print, log, or embed `C2_API4_KEY` / Alpaca keys.
- `LIVE_TRADING_ENABLED=false`. Refresh ≠ approve ≠ fill.
- Job must not import `c2_signal_feed` from browser JS (there is none — HTML fetch same-origin only).
- **Forbidden:** invent TradingView symbol/search HTTP API; expose or read `C2_API4_KEY` in browser/inline script (server env only).
- «Finalizado» only after merge to `main`.

## Plan-time confirmation (2026-11-18)

| Check | Result |
|-------|--------|
| Branch | `front/sinais-live-criteria` |
| Base | `main` with N53 #71 + closeout #72 |
| ISS-024 | Open; sprint field → N54 |
| Steal N45–N47 | **No** |
| LIVE | **false** |
| Upstream SHA vs pin | **match** |

## N54.0 EXECUTE confirmation (2026-11-18)

| Check | Result |
|-------|--------|
| Worktree | `/home/igor/cursor/trading-lab.fronts/sinais-live-criteria` |
| Branch | `front/sinais-live-criteria` (`19ba17ca…` at confirm time) |
| `git ls-remote` `day-trader-skill` `main` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — **matches** `docs/VENDOR-PIN.md` + Dockerfile `ARG UPSTREAM_COMMIT` |
| Local `vendor/day-trader-skill` | **uninitialized** — pin doc authoritative; **no bump** |
| Cited symbols present in `src/` | `prodigy_rank.calculate`, `c2_history_collect.fetch`, `c2_signal_feed.snapshot`, `panel_ops_data.build_preapproval_queue`, `panel_ops_data._unique_tradingview_origins`, `v4_web_dashboard.serve_signals_reload` |
| POST job decision | **adapt** dashboard handler; underlying rank/C2/queue = **call**; TV = **forbidden** new API |
| ROADMAP checkboxes | untouched (parent) |

### POST `live_criteria` — reuse vs adapt vs new (one line)

**adapt** HTTP entry in `v4_web_dashboard.py` + **call** existing `calculate` → write prodigy JSON → **call** `c2_history_collect.fetch` / `c2_signal_feed.snapshot` (server, `C2_API4_KEY` env) → **call** `build_preapproval_queue` with `_unique_tradingview_origins` on in-bundle signals — **new** only: route, cooldown guard, response `mode: live_criteria`.
