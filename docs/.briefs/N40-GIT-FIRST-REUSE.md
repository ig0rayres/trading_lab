# N40.0 Git First — mapa operador «onde está cada coisa» (docs-only)

> Rock PLAN N40 · 2026-11-17 · frente `front/n27-alpaca-loop` · **no vendor bump** · **zero `src/`** · **not the orders-screen sprint**  
> Pin rechecked at plan-time against `docs/VENDOR-PIN.md`; local vendor checkout still absent on this worktree.

## Why this sprint (not orders UI, not a new project)

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| Operator map of existing panel surfaces | **Docs gap** — ISS-007 promised a single panel; day-to-day login shows a different HTML shell | **This sprint** |
| Dedicated open-orders / fills screen | No `/ordens` route in operator nav | **Out** — operator chose map, not the screen |
| New project / rewrite | Product already exists | **Forbidden** |
| Clear / OANDA / LIVE / invented scores | Campaign OUT | **Forbidden** |

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| Local `vendor/day-trader-skill` | **empty / absent** on this worktree — not a git checkout; treat pin above as the only local SHA |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` | Recheck in N40.0 EXECUTE (`git ls-remote`). N39 same-day check was **`3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd`** (matches pin). If GitHub is unreachable, **stop claiming current main** — do not bump. |

No vendor upgrade. Upstream has no operator Central, no Command Panel HTML, no TimesFM panel page. Do not copy scoring. Do not enable live.

## Reuse inventory (cite only — zero `src/` in EXECUTE)

| Capability | Path / function | Decision | Rationale | Tests / evidence |
|------------|-----------------|----------|-----------|------------------|
| Operator shells + nav | `src/panel_ops_html.py` `_nav`, `render_central_page`, `render_signals_page`, `render_prodigy_page`, `render_performance_page` | **Cite — do not edit** | Menu is only Central / Sinais / Prodígio / Performance | `tests/test_panel_ops.py` |
| Operator data | `src/panel_ops_data.py` `build_panel_bundle`, `load_panel_signals`, `performance_from_ledger` / `performance_from_snapshots`, `prodigy_copied_signals` | **Cite — do not edit** | Signals from ledger `signal_events` or `webhooks/journal.jsonl`; fills from ledger or `paper/order-snapshots.jsonl` | `PanelOpsDataTests` |
| Command Panel v1 HTML | `src/v4_web_dashboard.py` `render_page` | **Cite — do not edit** | Single page: semaphore, count cards, catalog, Prodígio, Tá Barato, melhoria contínua | N16.7 / ISS-007 |
| Route split | `src/v4_web_dashboard.py` `make_handler` / `serve_operator_panel` / `serve_public_get` | **Cite — do not edit** | If operator session env is set, `GET /` is Central after cookie; Command Panel v1 HTML is **not** that menu | `test_root_redirects_to_login_without_cookie` |
| Command Panel JSON | `src/trading_dashboard_data.py` `command_panel` (`financial_health`, `strategy_catalog`, `opportunities`, `ta_barato_shadow`, `continuous_improvement`, `history`) | **Cite — do not edit** | `/api/status` still carries these keys | N16 / N28.1 labels |
| TimesFM research | `src/timesfm_context.py` + `src/evolution_engine.py` daily report | **Cite — do not edit** | No HTML section in either shell | `tests/test_timesfm_context.py` |
| trader-entry/exit/budget/risk/scanner | `src/original.py` | **Do not touch** | MIT loader | `tests/test_vendor_verify.py` |
| Clear / OANDA | `src/demo_broker_adapters.py` | **Do not touch** | ISS-010 / N29.5 | existing gate tests |

## Two UIs (must appear in the operator map)

| Surface | When the browser sees it | Port / deploy |
|---------|--------------------------|---------------|
| **Operator shells** (`panel_ops_html`) | After `/login` when `DASHBOARD_OPERATOR_SESSION` is set — EasyPanel day-to-day | Image `trading-lab` CMD `v4-ops`; internal **8765**; HTTPS in front (`docs/DASHBOARD-OPERATIONS.md`, `EASYPANEL.md`) |
| **Command Panel v1** (`render_page`) | `GET /` **only if** operator session env is **unset** (bearer HTML). If session is set, `/` is Central, not this page | Same process / same 8765. JSON remains `GET /api/status` (`command_panel`, `platform_health`) |

## Honest status vocabulary (executor must use these four labels)

`VISÍVEL` · `VAZIO-COMUM` · `NÃO-EXISTE-AINDA` · `SÓ-API-OU-JSONL`

Do not invent a fifth. Do not mark a menu item VISÍVEL if it only exists on the other surface.

## Draft statuses (cite code; do not upgrade in EXECUTE)

| Area | Operator shells (login menu) | Command Panel v1 HTML | Empty copy already in code | Draft status |
|------|------------------------------|-----------------------|----------------------------|--------------|
| Central (freio, semáforo, mercados, limites) | `GET /` / `/central` | Semáforo + health line + count cards (no brake strip) | Semáforo: `Aguardando primeira checagem automática (v4-ops)`; sinais: `Sem sinais recentes` | **VISÍVEL** on operator menu |
| Sinais | Menu `GET /sinais` | Not a page | `Nenhum sinal neste destino.` | **VISÍVEL** |
| Prodígio | Menu `GET /prodigy` | Table «Oportunidades Prodígio» | Rank: `Execute prodigy-rank (research)`; copies: `Nenhuma cópia registrada` | **VISÍVEL**; empty rank **VAZIO-COMUM** until `prodigy-rank` |
| Performance | Menu `GET /performance` | Count cards + gross P&L | `Sem fills confirmados` / `Indisponível` | **VISÍVEL** (gross, fills only) |
| Ordens abertas Alpaca paper | **No nav item, no `/ordens`** | Cards «Ordens monitoradas» / «Posições ainda abertas» (counts, not a list) | Counts can be 0 | **NÃO-EXISTE-AINDA** as a screen; v1 = counts only |
| Histórico / fills | **No nav item** | Cards «Ordens encerradas…»; `financial_health.paper_fills_recorded`; JSON `history` | 0 fills | **NÃO-EXISTE-AINDA** as a screen; **SÓ-API-OU-JSONL** (`/api/status`, jsonl, ledger) |
| Tá Barato | **Not in `_nav`** | Section «Tá Barato — sombra / homolog» | `Execute v4-cycle com --opportunity-input ou aguarde relatório` | **VISÍVEL** only on Command Panel v1; operator menu **NÃO-EXISTE-AINDA** |
| Análise Google / TimesFM | **Not in HTML** | **Not in `render_page`** | Daily report `timesfm_status: UNAVAILABLE` | **SÓ-API-OU-JSONL** (research; not order auth) |
| Melhoria contínua / catálogo fases | **Not in `_nav`** | `h2` Estratégias + Melhoria contínua | Catalog: `Catálogo indisponível (ledger)`; evo: `Nenhum evento em evolution/decisions.jsonl` | **VISÍVEL** only on Command Panel v1; operator menu **NÃO-EXISTE-AINDA**. JSON also `/api/status` |

## Gap (this sprint only)

| Gap | New code? | Notes |
|-----|-----------|-------|
| Operator does not know which URL is which | **Docs** | Map both surfaces; name EasyPanel 8765 |
| ISS-007 map lists areas as if one UI | **Docs** | Do not close ISS-007; add ISS-016 |
| Open orders / history promised in MVP-OP-1.0 | **Docs honesty** | Label NÃO-EXISTE-AINDA — do **not** build the screen here |
| Clear / OANDA / scoring / LIVE | **No** | Forbidden |

## Compatibility / license / security

- MIT vendor via `src/original.py` only; no bump.
- Map must not print tokens, `.env`, or EasyPanel secret values.
- `LIVE_TRADING_ENABLED=false`. HTTP 200 / queue / semaphore ≠ fill.

---

## EXECUTE confirmation (N40.0 — 2026-11-17)

| Check | Result |
|-------|--------|
| `docs/VENDOR-PIN.md` SHA | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — **unchanged** (no bump) |
| `git ls-remote` `Jakeschincariol/day-trader-skill` `refs/heads/main` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — matches pin |
| Local `vendor/day-trader-skill` | absent on this worktree — pin table is the only local SHA |
| `src/` in EXECUTE | **zero** edits |
