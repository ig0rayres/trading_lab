# N48.0 Git First — alinhar Sinais à cópia de terceiros

> Rock PLAN N48 · 2026-11-17 · frente `front/n27-alpaca-loop` · **no vendor bump** · **not Clear/OANDA** · **Collective2 closed** · **LIVE false**  
> Plan-time inventory (rechecked planner Grok). EXECUTE (N48.0) re-checks `git ls-remote` and records confirmation; do not bump.

## Why this sprint

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| Daily-menu `/sinais` as third-party copy / operating view | Route exists (N25) but HTML is ingest audit only (origin, destination, reason) | **This sprint** — extend `/sinais` + `GET /api/signals` |
| Ingest audit (Feature 9) | `load_panel_signals` + tests already green | **Keep** as a labeled section — do not delete |
| Parallel `/copy` or `/provedores` surface | Would split the operator concept of Sinais | **Forbidden** — same page |
| Invent per-signal fill / costs | Ledger performance is by `strategy_key`; costs often incomplete | **Forbidden** — gross label; honest empty |
| Collective2 paper-copy | `approved_for_paper_copy` false | **Closed** — show closed, never operating |
| Tá Barato / B3 / OANDA | Campaign stubs N45–N47 | **Do not steal IDs**; out of this sprint |
| Panel POST / live | `LIVE_TRADING_ENABLED=false` | **Forbidden** |

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` | **`3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd`** (plan-time `git ls-remote` 2026-11-17) — **matches pin** |
| Local `vendor/day-trader-skill` | Submodule **recorded** at pin `3d0f4ef` (`git submodule status` shows `-3d0f4ef…`, not initialized). Worktree directory has **no** checkout files. Do **not** bump. Do **not** treat an empty folder as reviewed main. Docker still clones the pin at image build. |

Upstream has no operator Central, no `/sinais`, no signal-copy HTML. Search of vendor tree for operator panel / `signal_copy` dashboard: **no matches** (empty checkout). Do not copy scoring. Do not enable live. Do not load `trader-entry|exit|budget|risk|scanner` except via `src/original.py`.

If GitHub is unreachable at EXECUTE, stop claiming current `main`. Re-run `git ls-remote`; if it still matches the pin, proceed without bump.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests / evidence |
|------------|-----------------|----------|-----------|------------------|
| Ingest audit rows | `src/panel_ops_data.py` `load_panel_signals`, `normalize_signal_row`, `signal_destination`, `blocked_context` | **keep / call — do not replace** | Feature 9 already exposes origin, destination, reject reason | `tests/test_panel_ops.py` `test_load_panel_signals_exposes_origin_destination_and_reject_reason` |
| Third-party ticket schema | `src/signal_copy.py` `ALLOWED`, `validate`, `preflight`, `sign` | **do not reimplement; do not call `validate` from the panel** (needs secret) | Copy family identity is `strategy_key=signal_copy`; TradingView is a provider, not a second strategy | `tests/test_signal_copy.py` |
| Prodígio copied rows | `src/panel_ops_data.py` `prodigy_copied_signals` | **call — label research, not operating** | Rows from `evolution/decisions.jsonl` with `kind=signal_copy`; label `research_copy_not_order_auth` | `test_snapshot_panel_ops_prodigy_ranking_and_copied_signals` |
| Performance by family | `performance_from_ledger`, `performance_from_snapshots`, `PERFORMANCE_LABEL_GROSS` | **call / filter — do not invent fills or costs** | Feature 10: confirmed fills only; gross when costs incomplete; group by `strategy_key` | `test_performance_excludes_unfilled_orders` |
| Open orders / history | `load_panel_open_orders`, `load_panel_order_history`, `order_row_from_snapshot` | **filter by copy `strategy_key`** | Rows have `strategy_key`, symbol, side, status. **No `provider`. No `signal_id`.** Do not invent those fields | N41 panel tests |
| Daily menu shell | `src/panel_ops_html.py` `render_signals_page`, `_nav` | **extend same route** | Operator already clicks Sinais; add copy section + keep audit | `tests/test_panel_ops.py` HTTP |
| JSON | `src/v4_web_dashboard.py` `serve_panel_json` `/api/signals` | **extend payload** — keep `signals[]` | Feature 9 tests read `signals`; add `copy` object | `test_api_signals_json_origin_destination_reject_reason` |
| Panel bundle | `src/panel_ops_data.py` `build_panel_bundle` | **extend** | Attach `signal_copy` view next to existing `signals` | N25 / N41 / N42 |
| Collective2 research | `src/c2_signal_feed.py`, `src/c2_history_collect.py` | **do not call from panel; do not approve** | Feature 4: no C2 provider `approved_for_paper_copy` | REQUIREMENTS Feature 4 |
| Paper submit | `src/paper_gateway_queue.py`, `src/signal_paper_runner.py` | **Do not call from panel** | Dashboard stays read-only | Feature 7 tests |
| Clear / OANDA adapters | `src/demo_broker_adapters.py` | **Do not touch** | ISS-010 / N29.5; N45–N47 stay stubs | N34 tests |
| trader-* | `src/original.py` | **Do not touch** | MIT loader | `tests/test_vendor_verify.py` |
| Prodígio HTML page | `render_prodigy_page` | **Do not move operating copy there** | Rank remains research; Sinais is the copy concept | N25 |

## Honest data gap (do not paper over)

- `/sinais` subtitle today: `Não é fill — auditoria de destino e motivo.` Columns: hora, origem, ativo, mercado, destino, motivo. That is **ingest audit**, not «what we copy / what is operating».
- `GET /api/signals` today returns only `{signals: [...]}` (`serve_panel_json`). Extend with `copy`; do not drop `signals`.
- `load_panel_signals` SELECT on `signal_events` is `source, symbol, market, status, reject_code, received_at` — **no** `strategy_key`, **no** `signal_id`, **no** costs. Do **not** add a table or column in N48.
- Paper order rows (`order_row_from_snapshot`, ledger open/history) carry `strategy_key` and **do not** carry `provider` or `signal_id`. Per-provider operating tables and per-signal P&L **cannot** be joined honestly. Family `signal_copy` totals only.
- Copy operating view filters **existing** `open_orders` / `order_history` / `performance` where `strategy_key=signal_copy`.
- `prodigy_copied_signals` is research (`research_copy_not_order_auth`) and is the **only** existing list with `provider`. Show as research copies, never as operating.
- `PERFORMANCE_LABEL_GROSS` (`gross_unverified_costs`) stays whenever costs are incomplete. Do not invent fees, net, or percentil.
- Collective2 stays closed: banner `Collective2: cópia fechada — nenhum provedor aprovado.` Never list C2 as operating.
- Empty operating copy is valid: `Nenhuma cópia de terceiro em operação.` Empty copy performance: `Sem fills confirmados nesta cópia.` Ingest empty stays `Nenhum sinal neste destino.`
- DESIGN.md Sinais filters (Todos/Ordem/Barrado/Fila) are **not** in today's HTML. N48 does **not** add them; ingest table stays as N25 built it.
- HTTP 200, queue, and `queued_intent` are **not** fills.

## Compatibility / license / security

- MIT vendor via `src/original.py` only; no bump (pin = GitHub `main` at plan-time).
- No tokens, `.env`, or EasyPanel secret values in HTML or tests. Do not call `signal_copy.validate` from the dashboard (HMAC secret).
- `LIVE_TRADING_ENABLED=false`. Panel does not POST orders. Phase does not rise from PnL.

## Plan-time confirmation (2026-11-17)

| Check | Result |
|-------|--------|
| `docs/VENDOR-PIN.md` SHA | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — **unchanged** (no bump) |
| `git ls-remote` `Jakeschincariol/day-trader-skill` `refs/heads/main` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — matches pin |
| Local vendor git | submodule not initialized; directory empty — **≠ claim of reviewed local HEAD** |
| `src/` in this plan-time inventory | **zero** product edits |
| Planner recheck `git ls-remote` 2026-11-17 | pin still equals GitHub `main`; no bump |
