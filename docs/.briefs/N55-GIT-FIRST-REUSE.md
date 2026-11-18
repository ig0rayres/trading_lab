# N55.0 Git First — Fila multiplataforma após critérios ao vivo (ISS-024)

> Rock PLAN N55 · 2026-11-18 · frente `front/sinais-live-criteria` · **no vendor bump** · **LIVE false**  
> Plan-time inventory (planner Grok). EXECUTE (N55.0) re-checks `git ls-remote` and records confirmation; do not bump.  
> **Não** usa os identificadores N45–N47.  
> N54 já em `main` (PR **#73**, merge `20d23ae`). Reuse the N54 POST/job — **adapt**, do not add a parallel package.

## Why this sprint

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| POST live-criteria job | N54: `serve_signals_candidates_refresh` + `_live_criteria_job` | **extend** — do not add a second job module |
| GET disk reread | N54: `serve_signals_reload` `mode: disk_reread` | **keep** |
| Rank Prodígio 15d | `prodigy_rank.calculate` (`WINDOW_DAYS=15`, `MIN_TRADES=5`, ≥3 days, `PRODIGY_CANDIDATE_RESEARCH`) | **call** — never invent score |
| Collective2 HTTP | `c2_history_collect.fetch` + `c2_signal_feed.snapshot` | **call** from server job only |
| Fila pré-aprovação | `build_preapproval_queue` une C2 JSON + Prodígio + origens TV | **extend** — surface **eligible** rows of **all three** platforms; fail of one source must not drop the others |
| Persist rank | `_persist_prodigy_rank` writes `prodigy-top10` **and** `provider-research` from the same rank | **adapt** — empty calculate must **not** wipe prior research JSON |
| Busca TradingView | Não existe no produto | **forbidden** |
| C2 marketplace search | Não existe (`c2_signal_feed` só `fetch_orders`/`snapshot` por ID) | **forbidden** — IDs from named list + prior research + raw files |
| Tabela cooldown | N54 in-process | **keep** |

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` (plan-time 2026-11-18) | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` **matches pin** |
| Local `vendor/day-trader-skill` | May be uninitialized — do **not** bump |

Upstream has no PanelShell, no preapproval queue, no ISS-024 job. Load trader-* only via `src/original.py`.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests |
|------------|-----------------|----------|-----------|-------|
| Live-criteria POST | `v4_web_dashboard.serve_signals_candidates_refresh` / `_live_criteria_job` | **extend** | N54 contract stays; N55 fixes assembly + partial honesty | `N54LiveCriteriaRefreshHttpTests` + N55.3 |
| Rank Prodígio 15d | `src/prodigy_rank.py` `calculate` | **call** | Eligible = existing `PRODIGY_CANDIDATE_RESEARCH`; do not change constants | `tests/test_prodigy_rank.py` |
| C2 history | `src/c2_history_collect.py` `fetch` | **call** | Adapter-shaped `{sid}_{kind}.json` in `reports/providers/raw` | mock opener; no live net |
| C2 snapshot | `src/c2_signal_feed.py` `snapshot` | **call** | Research snapshot ≠ ticket | `tests/test_c2_signal_feed.py` |
| C2 named list | `load_c2_paper_copy_approved_ids` + `_merged_c2_strategy_ids` | **call** | Empty list + missing key = issue, not invented IDs | N50/N51 + N55.3 |
| Queue | `panel_ops_data.build_preapproval_queue` | **extend** | Union Collective2 + Prodígio + TradingView; filter Prodígio to Feature 4 status already in code | N55.3 multi-platform |
| TV origins | `_unique_tradingview_origins` | **call** | ADR-012; metrics may stay `indisponível` | existing N51 + N55.3 |
| CTA | `panel_ops_html._CANDIDATES_RELOAD_SCRIPT` | **extend** | Partial warning must survive reload; keep POST | N55.2/N55.3 |
| trader-* vendor | `src/original.py` | **do not call** from this job | Not copy/rank logic | — |

## EasyPanel emptiness (honest, no SSH)

If the deployed queue shows only one TradingView origin with metrics unavailable, the code paths below explain it — **do not invent scores** to fill the table.

| Symptom | Required on the server (operator / volume) | What N55 code must do |
|---------|--------------------------------------------|------------------------|
| Collective2 missing | `C2_API4_KEY` in **server** env only; named IDs in allowlist/env **or** prior research JSON **or** raw `{sid}_closed_trades.json` | `issues` include `C2_API4_KEY_missing` (or empty-ID issue); **keep** Prodígio + TV rows; do not wipe prior C2 JSON |
| Prodígio raw/rank empty | Files `reports/providers/raw/{sid}_closed_trades.json` (adapter shape already used by `prodigy_rank`) | Issue naming **raw providers** required; **do not persist** empty rank over previous JSON; do not invent `prodigy_score` |
| TradingView only | Webhook ingest already produced `signals[]` origins | Keep those rows; metrics unavailable is honest; F-018 must emit `issues` instead of silent `return` |
| One source fails | — | `status: partial`; other `sources_ok` still assemble the queue |

There is **no** Collective2 “list all strategies” API in this tree and **no** TradingView search API. N55 documents that gap; it does not add one.

## Honest N54 leftover (why the operator still sees one TV row)

1. `_live_refresh_prodigy` always `_persist_prodigy_rank` after `calculate`. Empty raw → empty JSON **overwrites** prior research.
2. `_persist_prodigy_rank` copies the same rank into `provider-research-top10-latest.json`, which `build_preapproval_queue` then loads as **collective2**.
3. `_live_refresh_tradingview` swallows errors (F-018) and still marks `tradingview` ok.
4. POST JSON `issues` vanish after `location.reload()` — `/sinais` has no partial banner.

N55 adapts these four; it does **not** replace the N54 route.

## Compatibility / license / security

- MIT vendor via `src/original.py` only; pin unchanged.
- Never print, log, or embed `C2_API4_KEY` / Alpaca keys.
- `LIVE_TRADING_ENABLED=false`. Refresh ≠ approve ≠ fill.
- **Forbidden:** TradingView search HTTP; C2 key in browser; parallel package beside `src/`; steal N45–N47.
- «Finalizado» only after merge to `main`.

## Plan-time confirmation (2026-11-18)

| Check | Result |
|-------|--------|
| Worktree | `/home/igor/cursor/trading-lab.fronts/sinais-live-criteria` |
| Branch | `front/sinais-live-criteria` fast-forwarded to `origin/main` `20d23ae` (PR **#73**) |
| ISS-024 | Open; sprint field → N55 |
| Steal N45–N47 | **No** |
| LIVE | **false** |
| Upstream SHA vs pin | **match** `3d0f4ef` |
