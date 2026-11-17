# N49.0 Git First — proveniência ordem↔sinal, inventário e critérios visíveis

> Rock PLAN N49 · 2026-11-17 · frente `front/n27-alpaca-loop` · **no vendor bump** · **not Clear/OANDA** · **Collective2 closed** · **LIVE false**  
> Plan-time inventory (planner Grok). EXECUTE (N49.0) re-checks `git ls-remote` and records confirmation; do not bump.  
> **Não** usa os identificadores N45–N47.

## Why this sprint

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| Open paper order → which signal opened it | Ledger already has `paper_orders.risk_decision_id` → `risk_decisions.signal_event_id` → `signal_events`; panel SELECT omits the join | **This sprint** — honest join (or overlay stored ticket id); never invent |
| Inventory of subscribed/operating signals + per-signal performance | N48 `copy` is family totals only; Feature 10 already fill-only by `strategy_key` | **This sprint** — group confirmed fills by provenance; unknown bucket when unlinked |
| Adoption criteria on the Sinais feature | Text **already** in REQUIREMENTS Feature 4 / 9 / 10; not on `/sinais` | **This sprint** — surface existing text + catalog phases; **do not redefine** |
| Prodígio pool of new/well-performing candidates | `prodigy_rank.calculate` + `intelligence/prodigy-top10-latest.json` + `_load_prodigy_opportunities` | **Reuse** — research-labeled; no new score; no auto-promote |
| Per-signal P&L without fill | Feature 10 forbids | **Forbidden** |
| Collective2 paper-copy | `approved_for_paper_copy` false | **Closed** |
| Tá Barato / B3 / OANDA | Campaign stubs N45–N47 | **Do not steal IDs** |
| Panel POST / live | `LIVE_TRADING_ENABLED=false` | **Forbidden** |

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` | **`3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd`** (plan-time `git ls-remote` 2026-11-17) — **matches pin** |
| Local `vendor/day-trader-skill` | Submodule **recorded** at pin `3d0f4ef` (`git submodule status` shows `-3d0f4ef…`, not initialized). Worktree directory has **no** checkout files. Do **not** bump. Do **not** treat an empty folder as reviewed main. Docker still clones the pin at image build. |

Upstream has no operator Central, no `/sinais`, no order↔signal panel join. Do not copy scoring. Do not enable live. Do not load `trader-entry|exit|budget|risk|scanner` except via `src/original.py`.

If GitHub is unreachable at EXECUTE, stop claiming current `main`. Re-run `git ls-remote`; if it still matches the pin, proceed without bump.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests / evidence |
|------------|-----------------|----------|-----------|------------------|
| Ledger FK chain | `migrations/001_ledger_up.sql` `risk_decisions.signal_event_id`; `paper_orders.risk_decision_id`; `docs/DATABASE.md` | **call / join — do not add a column** | Provenance already exists in SQL; the panel SELECT drops it | `tests/test_paper_gateway_queue.py` JOIN `se ON se.id = rd.signal_event_id` |
| Persist Gate B → order | `src/paper_gateway_queue.py` `persist_risk_decision`, `_lookup_signal_event_id` | **do not reimplement; do not call from panel** | Worker already links `signal_events` ↔ `paper_orders` | `test_persist_uses_queue_stem_when_signal_id_hashed` |
| Gate A row | `src/gate_a_signal.py` `record_signal_event` (`source` = provider; `idempotency_key` = sha256(provider\|signal_id)) | **join `source` as origin; do not reverse the hash** | Ticket `signal_id` is **not** a SQL column | Gate A tests |
| Ticket overlay | `src/signal_paper_runner.py` `DEFAULT_LEDGER` `paper/signal-orders.jsonl` records `provider` + `signal_id` + `client_order_id` | **overlay by `client_order_id` when the line exists** | Honest persist-from-existing-file; hashed webhook ids stay hashed | Feature 7 / gateway tests |
| Snapshot rows | `src/panel_ops_data.py` `order_row_from_snapshot`; `src/paper_monitor.py` `analyze` | **surface fields if already on the snap; unknown otherwise** | Monitor snapshots lack `signal_id` today — do not invent | N41 panel tests |
| N48 copy bundle | `build_panel_copy`, `build_panel_bundle` `copy` | **extend** | Keep operating/history/family performance/Collective2/research_copies | `tests/test_panel_ops.py` N48 |
| Ingest audit | `load_panel_signals` | **keep** | Feature 9 origin/destination/reason | Feature 9 tests |
| Fill-only performance | `performance_from_ledger`, `performance_from_snapshots`, `PERFORMANCE_LABEL_GROSS` | **group by provenance after fill filter — do not invent fills** | Feature 10 | `test_performance_excludes_unfilled_orders` |
| Prodígio rank file | `src/prodigy_rank.py` `calculate` (`WINDOW_DAYS=15`, `MIN_TRADES=5`, ≥3 days in formula) | **do not call from panel; do not edit constants** | Feature 4 already states the 15d window; formula still “pendente” as product copy | Rank is research-only |
| Prodígio panel loader | `src/trading_dashboard_data.py` `_load_prodigy_opportunities` (`intelligence/prodigy-top10-latest.json`) | **call** — pool on `/sinais`, label `research_tip` | Feature 9 ranking + copied | `test_snapshot_panel_ops_prodigy_ranking_and_copied_signals` |
| Copied research rows | `prodigy_copied_signals` | **call — not operating** | Distinct from paper inventory | N25 / N48 |
| Catalog phases | `load_panel_strategy_catalog` / `strategy_catalog.list_strategy_states` | **call** — show `signal_copy` / `prodigy_15d` phases; no PATCH | Feature 4 states; N42 read-only | N42 tests |
| HTML / JSON | `render_signals_page`; `GET /api/signals` | **extend same route** | No `/copy`; keep N48 sections | N48 HTTP tests |
| Collective2 | `approved_for_paper_copy` false | **keep closed banner** | Feature 4 | N48 string tests |
| Paper submit | `process_after_gate_b`, Alpaca POST | **Do not call from panel** | Dashboard stays read-only | Feature 7 tests |
| trader-* | `src/original.py` | **Do not touch** | MIT loader | `tests/test_vendor_verify.py` |

## Honest data gap (do not paper over)

- N48 `/sinais` operating table has client id, symbol, side, status, qty — **no origin, no `signal_id`**. Family totals only.
- `open_orders_from_ledger` SELECT is `po.*` + `rd.strategy_key` — **omits** `rd.signal_event_id` and `signal_events.source`.
- `signal_events` has **no** `signal_id` column. Identity in SQL is `signal_events.id` + `source` + hashed `idempotency_key`. Ticket id, when shown, must come from an **existing** journal line (`signal-orders.jsonl`) or a snap that already stored it.
- Do **not** reverse SHA-256. Do **not** add a SQL column in N49 unless the join + overlay cannot express origin at all (they can).
- Historical snaps / orders without join and without journal overlay: Portuguese **origem desconhecida** / **sem vínculo com sinal**. Those rows **must not** get invented per-signal P&L (Feature 10). Put them in an unknown bucket or omit from per-signal totals.
- Webhook path may store a **hashed** `signal_id` (`tradingview_webhook`); surface the stored value, do not claim the pre-hash ticket.
- `build_panel_bundle` sets `prodigy.ranking` to `None`; Command Panel later attaches `_load_prodigy_opportunities`. N49 must reuse that loader for the Sinais pool, not re-score.
- `PERFORMANCE_LABEL_GROSS` stays whenever costs are incomplete.
- Collective2 stays closed. Rank/pool is **research** — Feature 4: rank→ingest does not promote phase.
- Adoption copy is **verbatim product language** from Feature 4 (15d window, ≥5 ops, ≥3 days, net positive, drawdown/consistency, formula pending, R$ 20, default research, no auto-promote, C2 closed, phases, LIVE off). Feature 9 list + Feature 10 fill-only. **Do not invent new adoption numbers.**
- HTTP 200, queue, and `queued_intent` are **not** fills.
- Empty inventory is valid: honest Portuguese, not fake signals.

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
| Criteria source | `docs/REQUIREMENTS.md` `### Feature 4: Catálogo de estratégias e promoção de estado`; `### Feature 9: Sinais e Prodígio`; `### Feature 10: Performance` — **reused, not invented** |
