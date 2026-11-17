# N50.0 Git First — Collective2 allowlist, Sinais layout, Prodígio provider

> Rock PLAN N50 · 2026-11-17 · frente `front/n27-alpaca-loop` · **no vendor bump** · **not Clear/OANDA** · **LIVE false**  
> Plan-time inventory (planner Grok). EXECUTE (N50.0) re-checks `git ls-remote` and records confirmation; do not bump.  
> **Não** usa os identificadores N45–N47.  
> Collective2: **named allowlist**, default empty — **not** a silent approve-all of H10’s ten candidates.

## Why this sprint

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| Enable Collective2 as a signal marketplace | Feed + history + rank already exist; Feature 4 / H10 keep copy closed until `approved_for_paper_copy` | **This sprint** — per-provider named allowlist + REQUIREMENTS 0.5; default still closed |
| Panel surface for C2 when approved | N48/N49 hardcode `collective2.approved_for_paper_copy: false` and one closed banner | **This sprint** — show approved IDs as subscribed; empty list = closed copy |
| Reorganize `/sinais` salad | Page already has copy + inventory + adoption + Prodígio pool + ingest audit on one scroll | **This sprint** — explicit ACTIVE / audit / Prodígio research headings |
| Prodígio pool Provedor `None` | `prodigy_rank.calculate` emits `provider_id`; `_load_prodigy_opportunities` maps `row.get('provider')` only | **This sprint** — map `provider` or `provider_id`; do not rescore |
| Synthesize Gate A tickets from C2 active orders | `c2_signal_feed` forbids it (`execution_authorized: False`) | **Out** — display snapshot if already on disk; never invent a ticket |
| Bulk-approve H10 ten candidates | `provider_rank` / `prodigy_rank.copy_approved` stay false | **Forbidden** |
| Invent fill / new score / LIVE | Feature 4/10 | **Forbidden** |
| Tá Barato / B3 / OANDA | Campaign stubs N45–N47 | **Do not steal IDs** |

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` | **`3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd`** (plan-time `git ls-remote` 2026-11-17) — **matches pin** |
| Local `vendor/day-trader-skill` | Submodule **recorded** at pin `3d0f4ef` (`git submodule status` shows `-3d0f4ef…`, not initialized). Worktree directory has **no** checkout files. Do **not** bump. Do **not** treat an empty folder as reviewed main. Docker still clones the pin at image build. |

Upstream has no operator Central, no `/sinais`, no Collective2 allowlist, no Prodígio HTML pool. Do not copy scoring. Do not enable live. Do not load `trader-entry|exit|budget|risk|scanner` except via `src/original.py`.

If GitHub is unreachable at EXECUTE, stop claiming current `main`. Re-run `git ls-remote`; if it still matches the pin, proceed without bump.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests / evidence |
|------------|-----------------|----------|-----------|------------------|
| C2 active-order poller | `src/c2_signal_feed.py` `snapshot`, `fetch_orders`, `sanitized_record` | **do not call from panel**; **may read** `reports/providers/signals/active-orders-latest.json` if already on disk | Feed is read-only; `orders_sent: 0`; active orders are **not** tickets (`C2_SIGNAL_FEED_V36.md`) | CLI `scripts/run.sh c2-signal-feed`; no panel import of `fetch_orders` |
| C2 history collect | `src/c2_history_collect.py` `fetch` | **do not call from panel** | Needs env key; history ≠ real-time signal | CLI `c2-history` |
| Provider rank (180d) | `src/provider_rank.py` `analyze` (`eligible`, `paper_priority_top_3`) | **research only — never treat `eligible` as paper-copy approval** | H10: 10 candidates, 0 eligible; ranking overfits | `PROVIDER_RANKING_RESEARCH_ONLY` |
| Prodígio rank | `src/prodigy_rank.py` `calculate` (`provider_id`, `copy_approved: False`, `WINDOW_DAYS=15`, `MIN_TRADES=5`) | **do not call from panel; do not edit constants; reuse `provider_id` field** | Feature 4 formula still “pendente”; `copy_approved` stays false until named allowlist | `tests/test_prodigy_rank.py` |
| Prodígio loader (bug) | `src/trading_dashboard_data.py` `_load_prodigy_opportunities` L180 `row.get('provider')` | **extend** — `provider` or `provider_id`; keep `research_tip` | Rank JSON uses `provider_id`; HTML Provedor column reads `provider` | `/sinais` pool + `/prodigy` table |
| N48/N49 copy bundle | `build_panel_copy`, `copy.collective2` hardcoded closed | **extend** — named allowlist; keep operating/history/inventory/adoption/pool | Empty allowlist ⇒ still closed; non-empty ⇒ those IDs only | `tests/test_panel_ops.py` N48/N49 |
| Sinais HTML | `render_signals_page` (copy, inventory, adoption, pool, audit) | **extend same route** — reorder headings ACTIVE vs audit vs Prodígio | No `/copy`; no order POST | N48/N49 HTTP tests |
| Feature 4 / H10 | `docs/REQUIREMENTS.md` Feature 4, §7 Fora de Escopo, §5 Integrações, H10 | **update policy** (v0.5) — named allowlist; keep H10 as historical observation | Operator asked to enable C2 without inventing scores | N50.1 |
| Allowlist persist | no SQL column today (`control_flags` is risk anchors only) | **new committed JSON** `config/c2_paper_copy_allowlist.json` `approved_ids: []` plus optional env overlay of numeric IDs | No migration; default empty; do not seed H10 ten | tests with empty + one named id |
| Paper submit | `process_after_gate_b`, Alpaca POST | **Do not call from panel** | Dashboard stays read-only | Feature 7 tests |
| trader-* | `src/original.py` | **Do not touch** | MIT loader | `tests/test_vendor_verify.py` |
| HMAC copy module | `signal_copy` | **Do not import from panel** | Secret | N48 guard |

## Honest data gap (do not paper over)

- H10 remains: at that observation, 10 Collective2 candidates, **0 eligible**, copy closed. N50 does **not** rewrite that measurement into “all eligible”.
- Example strategy IDs in `C2_SIGNAL_FEED_V36.md` are **poll examples**, not approvals. Do not copy them into the allowlist.
- `prodigy_rank` / `provider_rank` `eligible` or `PRODIGY_CANDIDATE_RESEARCH` is **not** `approved_for_paper_copy`.
- Active-order snapshot is **not** a subscriber-licensed ticket (`c2_signal_feed` warning). N50 may **list** a snapshot that already exists on disk, labeled as not a ticket. It must **not** call Gate A / `signal_paper_runner` from the panel.
- Empty allowlist is the honest default: marketplace visible, paper-copy still closed.
- `_load_prodigy_opportunities` currently stores `provider: None` whenever the rank file only has `provider_id` — that is the Provedor `None` bug. Fix the mapping; do not invent names.
- N49 `/sinais` already stacks five `h2` blocks; operator still sees a salad. Reorder and rename; do not add a parallel route.
- `PERFORMANCE_LABEL_GROSS` stays whenever costs are incomplete. HTTP 200 / queue / `queued_intent` are **not** fills.
- `LIVE_TRADING_ENABLED=false`. Panel does not POST orders.

## Compatibility / license / security

- MIT vendor via `src/original.py` only; no bump (pin = GitHub `main` at plan-time).
- Never print, log, or embed `C2_API4_KEY` (or any broker/webhook secret). Panel must not call Collective2 HTTP.
- Allowlist contains **numeric strategy IDs only**, no keys.
- `LIVE_TRADING_ENABLED=false`. Phase does not rise from PnL.

## Plan-time confirmation (2026-11-17)

| Check | Result |
|-------|--------|
| `docs/VENDOR-PIN.md` SHA | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — **unchanged** (no bump) |
| `git ls-remote` `Jakeschincariol/day-trader-skill` `refs/heads/main` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — matches pin |
| Local vendor git | submodule not initialized; directory empty — **≠ claim of reviewed local HEAD** |
| `src/` in this plan-time inventory | **zero** product edits |
| Policy source | `docs/REQUIREMENTS.md` Feature 4, H10, §5 Integrações, §7 Fora de Escopo — **update in N50.1, do not invent scores** |
