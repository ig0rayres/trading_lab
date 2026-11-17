# N44.0 Git First — homologar US + cripto pelo painel (runbook)

> Rock PLAN N44 · 2026-11-17 · frente `front/n27-alpaca-loop` · **no vendor bump** · **not Clear/OANDA** · **no Live** · **no invented fills** · **LIVE false**  
> Plan-time inventory. EXECUTE (N44.0) re-checks `git ls-remote` and records confirmation; do not bump.

## Why this sprint

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| Operator walk: signal → open order → fill or refusal → performance (US equity + crypto, Alpaca paper) | Loop + N41 lists already exist; EasyPanel rebuild is operator | **This sprint — docs / runbook** |
| New `/ordens` `/historico` screens | Delivered N41 | **Done — do not reopen unless walk proves lists blind** |
| Strategy catalog on login menu | `/estrategias` delivered N42 | **Done** |
| TimesFM HTML | `/analise-google` delivered N43 | **Done** — research-only |
| Alpaca HTTP poll from the panel | Explicitly OUT of N41 | **Forbidden** |
| Invent fills / treat pytest as fill | Contract forbids | **Forbidden** |
| Clear / OANDA | Fail-closed adapters; no operator creds | **Forbidden** until N29.5 (N46/N47) |
| Tá Barato family screen | G-FORM | **N45** — blocked on N17.2 |
| Live button / `LIVE_TRADING_ENABLED=true` | Permanent out | **Forbidden** |
| New project / rewrite | Product already exists | **Forbidden** |

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` | **`3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd`** (plan-time `git ls-remote` 2026-11-17) — **matches pin** |
| Local `vendor/day-trader-skill` | Submodule **recorded** at pin `3d0f4ef` (`git submodule status` shows `-3d0f4ef…`, not initialized). Worktree directory has **no** `.git` and **no** checkout files. Do **not** bump. Do **not** treat an empty folder as reviewed main. Docker still clones the pin at image build. |

Upstream has no operator Central, no Command Panel, no `/ordens` HTML, no EasyPanel runbook. Do not copy scoring. Do not enable live. Do not load `trader-entry|exit|budget|risk|scanner` except via `src/original.py`.

If GitHub is unreachable at EXECUTE, stop claiming current `main`. Re-run `git ls-remote`; if it still matches the pin, proceed without bump.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests / evidence |
|------------|-----------------|----------|-----------|------------------|
| Open-order list | `src/panel_ops_data.py` `load_panel_open_orders`, `open_orders_from_snapshots`, `open_orders_from_ledger` | **Reuse — do not rewrite** | N41 already lists rows (or honest empty). Panel does **not** poll Alpaca HTTP | `tests/test_panel_ops.py` `test_build_panel_bundle_*`, HTTP `/ordens` |
| History / fills list | `load_panel_order_history`, `order_history_from_snapshots`, `order_history_from_ledger` | **Reuse — do not rewrite** | Same fill rule as Performance; `queued_intent` excluded from history | Feature 10 + N41 nodeids |
| Empty copy | `src/panel_ops_html.py` `render_orders_page` / `render_history_page` | **Reuse verbatim** | `Nenhuma ordem aberta no paper.` · `Nenhum fill confirmado no histórico.` | N41 HTML tests |
| Performance (gross, fills only) | `performance_from_ledger` / `performance_from_snapshots` | **Reuse** | Campaign walk ends on this page; no new metric | Feature 10 |
| Signals + refusal reason | `load_panel_signals`, `/sinais` | **Reuse** | Refusal with reason **counts** as a walk outcome | N25 |
| Paper submit loop (US + crypto) | `src/signal_paper_runner.py`, `src/paper_gateway_queue.py` | **Do not call from panel** · **do not extend in N44** | Feature 7 pytest already `[x]` for US_EQUITY + CRYPTO; dashboard stays read-only | `test_n30_us_equity_demo_on_paper_submitted`, `test_n30_crypto_risk_candidate_uses_signal_market`, `N30Feature7AlpacaPaperLoopTest` |
| Feature 5 historical fill | Alpaca paper AAPL buy @349.85 filled 2026-10-29 qty 1 | **Cite as historical evidence, not as the crypto walk** | May appear in Histórico after rebuild **if** jsonl/ledger still on the volume; does **not** close the crypto pass | `docs/TEST-EVIDENCE.md` § N20 · `docs/REQUIREMENTS.md` Feature 5 |
| Feature 7 named crypto path | `DEMO_ACCOUNT_PATH_CRYPTO=alpaca_paper` | **Reuse env name only — never paste values** | Pytest ≠ broker fill | REQUIREMENTS G-MKT |
| Homologation runbook shell | `docs/HOMOLOGATION.md` Feature 5 / G-MKT sections | **extend — add N44 panel walk section** | Do not fork a second product runbook | N12 / N35 |
| Evidence sheet | `docs/TEST-EVIDENCE.md` | **extend — pending rows** | Operator fills; agent does not invent | N9 / N20 |
| Day-to-day leaf | `docs/DASHBOARD-OPERATIONS.md` | **pointer only** | Rebuild + login already documented | N18 / N41–N43 |
| Operator map | `docs/OPERATOR-PANEL-MAP.md` §§5–7 | **pointer only** | Lists already VISÍVEL / VAZIO-COMUM | N41 |
| Clear / OANDA adapters | `src/demo_broker_adapters.py` | **Do not touch** | ISS-010 / N29.5 | N34 tests |
| TimesFM | `src/timesfm_context.py` | **Do not touch** | Research-only; N43 | N43 tests |
| trader-* | `src/original.py` | **Do not touch** | MIT loader | `tests/test_vendor_verify.py` |

## When code is IN vs OUT

| Situation | Code in N44? |
|-----------|----------------|
| Lists show rows from snapshots/ledger, or the documented empty string | **OUT** — this is the honest N41 surface |
| Published image is old (pre-N41 menu) | **OUT** — operator rebuild EasyPanel `trading-lab` |
| Operator has not produced a new signal / fill this week | **OUT** — pending evidence row; do not invent |
| Walk shows Alpaca paper fill (or jsonl/ledger row) for a symbol **and** Ordens/Histórico stay empty | **STOP** — proven blindness. Do **not** patch in N44. Open `/pmo plan` (Sprint F). |
| Ledger rows hardcode `market: 'US_EQUITY'` even for crypto symbols | **OUT of N44** — labeling gap, **not** proven blindness (symbol still lists). Record only if the walk misses the **row**. |

**Plan-time conclusion:** N44 is **not** a code sprint. No M task. No `src/` diff.

## Honest data gap (do not paper over)

- N41 lists read **jsonl + ledger**, not a live Alpaca book. Empty list with the Portuguese empty string is correct when those stores have no rows on the published volume.
- Feature 7 US+crypto `[x]` is **pytest**. Feature 5 `[x]` is **one** AAPL fill (2026-10-29). Neither is a 2026-11-17 panel walk for US **and** crypto.
- `open_orders_from_ledger` / `order_history_from_ledger` set `market` to `US_EQUITY`. Snapshot path uses `snap.get('market') or 'US_EQUITY'`. Crypto **rows can still appear** by symbol. Do not treat the hardcoded market as “lists are blind” without a missed row.
- HTTP 200, `PAPER_GATEWAY_QUEUE_ONLY`, queue, semaphore, pytest green, EasyPanel rebuild, and “panel is up” are **not** fills.
- B3 / FOREX remain fail-closed until N29.5. Zero Alpaca POST from those markets.

## Compatibility / license / security

- MIT vendor via `src/original.py` only; no bump (pin = GitHub `main` at plan-time).
- No tokens, `.env`, or EasyPanel secret values in HTML, runbook, or evidence rows (redacted ids only).
- `LIVE_TRADING_ENABLED=false`. No Live button.

## Plan-time confirmation (2026-11-17)

| Check | Result |
|-------|--------|
| `docs/VENDOR-PIN.md` SHA | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — **unchanged** (no bump) |
| `git ls-remote` `Jakeschincariol/day-trader-skill` `refs/heads/main` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — matches pin |
| Local vendor git | submodule not initialized; directory empty — **≠ claim of reviewed local HEAD** |
| Worktree vs N43 closeout | HEAD `4d26b37` (`docs(sprint-N43): closeout after PR 63 merge` restamp); PR **#64** merged |
| `src/` in this plan-time inventory | **zero** product edits |

## EXECUTE confirmation (N44.0 — 2026-11-17)

| Check | Result |
|-------|--------|
| `git ls-remote` `Jakeschincariol/day-trader-skill` `refs/heads/main` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — **matches pin** (re-checked at EXECUTE) |
| Vendor bump | **none** |
| `src/` in N44 EXECUTE | **zero** product edits (docs-only sprint) |
