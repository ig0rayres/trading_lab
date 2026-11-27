# N41.0 Git First — ordens abertas + histórico no menu do dia a dia

> Rock PLAN N41 · 2026-11-17 · frente `front/n27-alpaca-loop` · **no vendor bump** · **not Clear/OANDA** · **TimesFM out** · **LIVE false**  
> **EXECUTE (N41.0 — 2026-11-17):** reuse inventory confirmed; pin `3d0f4ef` matches GitHub `main` (`git ls-remote`); local vendor `2a005905` ≠ pin — no bump; zero `src/` edits.

## Why this sprint

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| Dedicated open-orders + fills screens on the login menu | Data exists as **counts** and jsonl/ledger; **no** `/ordens` or `/historico` | **This sprint** |
| Strategy catalog on the login menu | HTML only on Command Panel v1 | **N42** (campaign stub) |
| TimesFM HTML | `timesfm_context.py` research-only | **N43** — never order auth |
| Clear / OANDA live | Fail-closed adapters; no operator creds | **Forbidden** until N29.5 |
| New project / rewrite | Product already exists | **Forbidden** |

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` | **`3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd`** (N41.0 EXECUTE `git ls-remote` 2026-11-17) — **matches pin** |
| Local `vendor/day-trader-skill` | Present on this worktree at `2a005905f8415f01e220996e4aa55f4e796b4c16` — **not** the pin. Do **not** bump. Do **not** treat local HEAD as reviewed main. |

Upstream has no operator Central, no Command Panel, no `/ordens` HTML. Do not copy scoring. Do not enable live. Do not load `trader-entry|exit|budget|risk|scanner` except via `src/original.py`.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests / evidence |
|------------|-----------------|----------|-----------|------------------|
| Snapshot counts + latest MONITORED rows | `src/trading_dashboard_data.py` `read_jsonl`, `summary()` (`paper/order-snapshots.jsonl`, `paper_orders_monitored`, `closed_orders_with_pnl`) | **Reuse / extend — do not fork a second jsonl parser** | N16 Command Panel already walks snapshots; today it **counts**, N41 needs **rows** | `tests/test_v4_capabilities.py` summary counts |
| Ledger counts | `src/ledger_reconcile.py` `ledger_snapshot()` | **Do not reuse as the list** | Returns table **counts** only (`paper_orders`, `paper_fills`, `paper_queued_intent`) | existing ledger tests |
| Signal list pattern | `src/panel_ops_data.py` `load_panel_signals`, `build_panel_bundle` | **copy_pattern** | Ledger SELECT with jsonl fallback; empty ≠ missing screen | `tests/test_panel_ops.py` `PanelOpsDataTests` |
| Performance fills | `src/panel_ops_data.py` `performance_from_ledger` / `performance_from_snapshots` | **call / same fill rule** | History must exclude unfilled / `queued_intent`; gross label already exists | Feature 10 nodeids |
| Daily menu shell | `src/panel_ops_html.py` `_nav`, `OPERATOR_PANEL_PATHS`, `render_signals_page` | **extend / copy_pattern** | Add Ordens + Histórico the same way Sinais was added (N25) | `tests/test_panel_ops.py` HTTP |
| Route split | `src/v4_web_dashboard.py` `serve_operator_panel`, `serve_panel_json`, `operator_panel_route` | **extend** | Cookie session; 404 today for unknown paths | `test_root_redirects_to_login_without_cookie`, `test_api_signals_requires_session` |
| Command Panel v1 cards | `src/v4_web_dashboard.py` `render_page` count cards | **Do not replace** | Keep v1; N41 is the **login menu**, not a rewrite of `render_page` | N16 / ISS-007 |
| Paper submit | `src/paper_gateway_queue.py`, `src/signal_paper_runner.py` | **Do not call from panel** | Dashboard stays read-only; no POST order | Feature 7 tests |
| Clear / OANDA adapters | `src/demo_broker_adapters.py` | **Do not touch** | ISS-010 / N29.5 | N34 tests |
| TimesFM | `src/timesfm_context.py` | **Do not touch** | Research-only; N43 | `tests/test_timesfm_context.py` |
| trader-* | `src/original.py` | **Do not touch** | MIT loader | `tests/test_vendor_verify.py` |

## Honest data gap (do not paper over)

- `command_panel.history` is `{postgres_ledger_counts: ledger}` — **counts**, not rows.
- `summary()` keeps latest MONITORED snapshot per `client_order_id` then counts open vs closed — **rows exist in memory**, not in the login HTML.
- There is **no** Alpaca HTTP list on the dashboard today. N41 must **not** add a live broker poll from the panel. Empty list when jsonl/ledger has no rows is correct.
- `paper_queued_intent` is **not** a fill (Feature 6 / Feature 10).

## Compatibility / license / security

- MIT vendor via `src/original.py` only; no bump.
- No tokens, `.env`, or EasyPanel secret values in HTML or tests.
- `LIVE_TRADING_ENABLED=false`. HTTP 200 / queue / semaphore ≠ fill.

---

## EXECUTE confirmation (N41.0 — 2026-11-17)

| Check | Result |
|-------|--------|
| `docs/VENDOR-PIN.md` SHA | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — **unchanged** (no bump) |
| `git ls-remote` `Jakeschincariol/day-trader-skill` `refs/heads/main` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — matches pin |
| Local `vendor/day-trader-skill` | `2a005905f8415f01e220996e4aa55f4e796b4c16` — **≠ pin** (expected; no bump) |
| `src/` in N41.0 | **zero** edits |
