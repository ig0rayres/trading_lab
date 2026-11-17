# N42.0 Git First — estratégias e fases no menu do dia a dia

> Rock PLAN N42 · 2026-11-17 · frente `front/n27-alpaca-loop` · **no vendor bump** · **not Clear/OANDA** · **TimesFM out** · **no phase promotion from the new page** · **LIVE false**  
> Plan-time inventory. EXECUTE (N42.0) re-checks `git ls-remote` and records confirmation; do not bump.

## Why this sprint

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| Strategy catalog on the login menu | Rows already in `strategy_states` + Command Panel v1 table; **no** `/estrategias` in `_nav` | **This sprint** |
| TimesFM HTML | `timesfm_context.py` research-only | **N43** — never order auth |
| Tá Barato family screen | Catalog row exists; formula still G-FORM | **N45** — blocked on N17.2 |
| Clear / OANDA | Fail-closed adapters; no operator creds | **Forbidden** until N29.5 |
| Promote phase from the new page | `PATCH /api/strategies/{key}` already exists for Central/API tests | **OUT** — new page is GET-only |
| New project / rewrite | Product already exists | **Forbidden** |

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` | **`3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd`** (plan-time `git ls-remote` 2026-11-17) — **matches pin** |
| Local `vendor/day-trader-skill` | Submodule **recorded** at pin `3d0f4ef` (`git submodule status` shows `-3d0f4ef…`, not initialized). Worktree directory has **no** `.git` and **no** checkout files. Do **not** bump. Do **not** treat an empty folder as reviewed main. Docker still clones the pin at image build. |

Upstream has no operator Central, no Command Panel, no `/estrategias` HTML. Search of vendor tree for operator panel / `strategy_states` / Command Panel: **no matches** (empty checkout). Do not copy scoring. Do not enable live. Do not load `trader-entry|exit|budget|risk|scanner` except via `src/original.py`.

If GitHub is unreachable at EXECUTE, stop claiming current `main`. Re-run `git ls-remote`; if it still matches the pin, proceed without bump.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests / evidence |
|------------|-----------------|----------|-----------|------------------|
| Persistent phases | `src/strategy_catalog.py` `list_strategy_states`, `KNOWN_STRATEGY_KEYS`, `DEFAULT_PHASE_BY_KEY`, `NEVER_PAPER_KEYS` | **call — do not reimplement SELECT/seed** | Feature 4 already seeds seven keys; dashboard must not UPDATE phase | `tests/test_strategy_catalog.py` |
| Command Panel v1 table | `src/v4_web_dashboard.py` `render_page` (`h2` Estratégias (catálogo); columns chave / fase / paper permitido) | **copy_pattern for columns; do not replace v1** | Catalog HTML exists on the legacy page; login menu is what the operator opens after N18 | N16 / ISS-007 |
| Catalog JSON | `src/trading_dashboard_data.py` `_load_strategy_catalog` / `command_panel.strategy_catalog` | **copy_pattern** | `{status, strategies, note}`; `LEDGER_UNAVAILABLE` → empty list, not invented rows | `/api/status` |
| Daily menu shell | `src/panel_ops_html.py` `_nav`, `OPERATOR_PANEL_PATHS`, `render_signals_page` / `render_orders_page` | **extend / copy_pattern** | Add Estratégias the same way Sinais (N25) and Ordens (N41) were added | `tests/test_panel_ops.py` HTTP |
| Panel bundle | `src/panel_ops_data.py` `build_panel_bundle` | **extend** | Put `strategy_catalog` on the same bundle as signals/orders | N25 / N41 |
| Route split | `src/v4_web_dashboard.py` `serve_operator_panel`, `serve_panel_json`, `operator_panel_route` | **extend** | Cookie session; 404 today for `/estrategias` | `test_nav_after_login_lists_ordens_and_historico` |
| Existing phase PATCH | `src/v4_web_dashboard.py` `apply_strategy_patch`, `PATCH /api/strategies/{key}` | **Do not call from the new page** | New screen is read-only; do not delete the existing PATCH (Central/API tests) | `tests/test_panel_triggers.py` |
| Supervised parameters | `GET /api/strategy-parameters`, POST propose | **Do not touch** | Feature 11 adjustments are not this wave | N28 / N31 |
| Paper submit | `src/paper_gateway_queue.py`, `src/signal_paper_runner.py` | **Do not call from panel** | Dashboard stays read-only | Feature 7 tests |
| Clear / OANDA adapters | `src/demo_broker_adapters.py` | **Do not touch** | ISS-010 / N29.5 | N34 tests |
| TimesFM | `src/timesfm_context.py` | **Do not touch** | Research-only; N43 | `tests/test_timesfm_context.py` |
| trader-* | `src/original.py` | **Do not touch** | MIT loader | `tests/test_vendor_verify.py` |
| Continuous improvement events | `command_panel.continuous_improvement` / `evolution/decisions.jsonl` | **Do not add to this page** | Map area 9 mixed catalog + evolution; N42 is catalog/phases only | N28.1 / N31 |

## Honest data gap (do not paper over)

- Login menu `_nav` has Central, Sinais, Ordens, Histórico, Prodígio, Performance — **no** Estratégias.
- `list_strategy_states()` already returns `{strategy_key, phase, paper_allowed, promotion: operator_only}`. N42 must **display** that, not invent scores or auto-promote.
- Without `LEDGER_DATABASE_URL`, `list_strategy_states()` returns `None` → empty catalog copy (`Catálogo indisponível (ledger)`). That is honest, not a reason to hardcode seven fake rows.
- `PATCH /api/strategies/{key}` can change phase from the API/Central tests. The **new HTML page must not** expose a promote control. Auto-promotion from PnL / HTTP 200 remains forbidden (Feature 4).
- Tá Barato appears as catalog key `ta_barato` in **research**. That is not the N45 family screen and not a recovered formula.

## Compatibility / license / security

- MIT vendor via `src/original.py` only; no bump (pin = GitHub `main` at plan-time).
- No tokens, `.env`, or EasyPanel secret values in HTML or tests.
- `LIVE_TRADING_ENABLED=false`. HTTP 200 / queue / semaphore ≠ fill. Phase does not rise from PnL.

## Plan-time confirmation (2026-11-17)

| Check | Result |
|-------|--------|
| `docs/VENDOR-PIN.md` SHA | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — **unchanged** (no bump) |
| `git ls-remote` `Jakeschincariol/day-trader-skill` `refs/heads/main` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — matches pin |
| Local vendor git | submodule not initialized; directory empty — **≠ claim of reviewed local HEAD** |
| Worktree vs `origin/main` | merge-base is this front’s N41 stamp; GitHub merge commits sit on `main` — **no vendor bump**, no content merge required to plan |
| `src/` in this plan-time inventory | **zero** product edits |

---

## EXECUTE confirmation (N42.0 — 2026-11-17)

| Check | Result |
|-------|--------|
| `docs/VENDOR-PIN.md` SHA | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — **unchanged** (no bump) |
| `Dockerfile` `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — matches pin |
| `git ls-remote` `Jakeschincariol/day-trader-skill` `refs/heads/main` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — **matches pin** (EXECUTE re-check) |
| Local `vendor/day-trader-skill` | Submodule **not initialized** (`-3d0f4ef…` in `git submodule status`); worktree directory **empty** — **≠** reviewed local HEAD; Docker build still clones pin |
| `src/` in N42.0 | **zero** edits |

---

## N42.4 closeout (docs — 2026-11-17)

| Artefato | Atualização |
|----------|-------------|
| `docs/OPERATOR-PANEL-MAP.md` | Área **3** Estratégias **VISÍVEL**; vazio `Catálogo indisponível (ledger)`; sem promoção de fase na UI do menu |
| `docs/DASHBOARD-OPERATIONS.md` | Menu inclui **Estratégias**; rotas `/estrategias` e `/api/estrategias` |
| `docs/ISSUES.md` | **ISS-017** nota onda 2 entregue; épico **aberto**; **ISS-007 / ISS-010 / ISS-011** inalterados |
| `docs/ROADMAP.md` | N42 `concluida`; tasks N42.0–N42.4 `[x]` |
| `docs/DIARY.md` | Secção **Sprint N42** |
