# N51.0 Git First — Panel pre-approval queue and reused research metrics

> Rock PLAN N51 · 2026-11-17 · frente `front/n27-alpaca-loop` · **no vendor bump** · **not Clear/OANDA** · **LIVE false**  
> Plan-time inventory (planner Grok). EXECUTE (N51.0) re-checks `git ls-remote` and records confirmation; do not bump.  
> **Não** usa os identificadores N45–N47.  
> Operator path: **authenticated panel approve/reject**. N50 JSON/env allowlist is **seed/fallback only**.

## Why this sprint

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| Pre-approval queue for every new signal-provider | N50 named C2 allowlist is JSON/env; operator rejected that as the day-to-day path | **This sprint** — pending queue + panel approve/reject; same row shape for C2, Prodígio, TradingView, future |
| Decision metrics that weigh approval | `prodigy_rank` already emits `win_rate_pct`, `shrunk_win_rate_pct`, `profit_factor_reported`, `reported_pnl_sum`, `prodigy_score`; `provider_rank` emits `win_rate_pct`, `net_return_pct`, `max_drawdown_pct`, `score` | **This sprint** — display recovered fields, label research; missing field = indisponível; **do not invent a composite “assertividade” formula** |
| Persist approvals across rebuild | `control_flags` is risk anchors only (N50 forbade mutating it); `trigger_changes` is gate audit, not provider adoption | **This sprint** — new ledger table `signal_provider_approvals`; do not alter risk anchors |
| N50 JSON/env allowlist | `load_c2_paper_copy_approved_ids` unions committed JSON + `C2_PAPER_COPY_APPROVED_IDS` | **Seed/fallback** when ledger has no row for that `(platform, provider_id)`; a ledger reject **wins** over seed |
| Approval places an order | Dashboard POST today is login + supervised strategy-parameters only; `do_POST` else 405 Read only | **Forbidden** — approve ≠ fill; no Alpaca/C2 HTTP from the panel |
| Invent scoring / LIVE / steal N45–N47 | Feature 4, campaign stubs | **Forbidden** |

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` | **`3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd`** (plan-time `git ls-remote` 2026-11-17) — **matches pin** |
| Local `vendor/day-trader-skill` | Submodule **recorded** at pin `3d0f4ef` (`git submodule status` shows `-3d0f4ef…`, not initialized). Worktree directory has **no** checkout files. Do **not** bump. Do **not** treat an empty folder as reviewed main. Docker still clones the pin at image build. |

Upstream has no operator Central, no `/sinais`, no provider-approval queue, no panel session. Do not copy scoring. Do not enable live. Do not load `trader-entry|exit|budget|risk|scanner` except via `src/original.py`.

If GitHub is unreachable at EXECUTE, stop claiming current `main`. Re-run `git ls-remote`; if it still matches the pin, proceed without bump.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests / evidence |
|------------|-----------------|----------|-----------|------------------|
| Panel session | `src/v4_web_dashboard.py` `operator_session_authorized`, cookie `trading_lab_session` | **call** | Platform-level auth already in front of `/sinais` and `/api/signals` | `tests/test_panel_ops.py` unauthenticated redirect/401 |
| Authenticated mutation | `do_POST` `/api/strategy-parameters/{propose,apply,undo}` + `do_PATCH` triggers | **copy_pattern** | Existing JSON body + 401/422 + `respond_mutation`; else 405 Read only | `tests/test_n28_supervised_adjustment.py` |
| N50 C2 allowlist | `load_c2_paper_copy_approved_ids`, `config/c2_paper_copy_allowlist.json`, env overlay | **extend as seed/fallback** | Operator forbade file/env/rebuild as the daily path; keep as backend seed | N50 empty + one-id tests |
| C2 copy block | `_build_collective2_block`, `copy.collective2` | **extend** — `approved_ids` from ledger ∪ seed-without-row; rejected excluded | Empty queue still closed copy | N50 HTML banners |
| Prodígio rank fields | `src/prodigy_rank.py` `calculate` → `win_rate_pct`, `shrunk_win_rate_pct`, `profit_factor_reported`, `reported_pnl_sum`, `prodigy_score`, `status`, `copy_approved: False` | **do not call from panel**; **reuse JSON fields already on disk** | Feature 4 formula still pendente; rank ≠ approval | `tests/test_prodigy_rank.py`; `mode':'PRODIGY_RANK_RESEARCH_ONLY'` |
| Provider rank (180d) | `src/provider_rank.py` `analyze` → `win_rate_pct`, `net_return_pct`, `max_drawdown_pct`, `score`, `eligible` | **do not call from panel**; overlay when JSON present | `eligible` is **not** paper-copy approval (H10) | `PROVIDER_RANKING_RESEARCH_ONLY` |
| C2 research candidates | `_load_c2_research_candidates` | **extend** — pass through recovered metric keys when present; do not invent | Today only `provider_id` / `name` / `label` | N50 candidate table |
| Prodígio pool | `_build_prodigy_pool` / `_load_prodigy_opportunities` | **extend display** — same recovered fields; still `research_tip` | N50 already maps `provider` or `provider_id` | N50 provider-visible tests |
| TradingView ingest | Feature 9 `signals` audit + HMAC webhook | **queue candidates from unique origin**; **do not rewrite Gate A authenticity** | Approval is provider adoption, not a fill; webhook secret stays Gate A | Feature 9 origin/destination/reject_reason remains |
| Ledger migrate | `src/ledger_migrate.py` 001+002; `migrations/002_triggers_up.sql` `CREATE TABLE` pattern | **extend** with `003_signal_provider_approvals`; do not rewrite 001/002; do not alter `control_flags` | Operator: ledger if needed so rebuild does not wipe decisions | `tests/test_ledger_migration.py` file tests |
| `trigger_changes` | gate field audit | **do not reuse as approval store** | Wrong domain; constraint lists only control/market/strategy | DATABASE.md §6.4 |
| Paper submit | `process_after_gate_b`, Alpaca POST | **Do not call from panel** | Approval ≠ fill | Feature 7 tests |
| trader-* | `src/original.py` | **Do not touch** | MIT loader | `tests/test_vendor_verify.py` |
| HMAC copy module | `signal_copy` | **Do not import from panel** | Secret | N48 guard |

## Honest field map (do not invent)

Operator asked for assertiveness / win% / gain that **weigh** approval. Recovered names:

| Operator label (PT) | Recovered field | Source JSON | If absent |
|---------------------|-----------------|-------------|-----------|
| Percentual de acertos (pesquisa) | `win_rate_pct` | prodigy_rank / provider_rank | `indisponível` — not 0 |
| Percentual encolhido (pesquisa) | `shrunk_win_rate_pct` | prodigy_rank | omit column or indisponível |
| Fator de lucro reportado (pesquisa) | `profit_factor_reported` | prodigy_rank | indisponível |
| Soma P/L reportada (pesquisa) | `reported_pnl_sum` | prodigy_rank | indisponível |
| Retorno líquido % (pesquisa) | `net_return_pct` | provider_rank | indisponível |
| Drawdown máximo % (pesquisa) | `max_drawdown_pct` | provider_rank | indisponível |
| Score pesquisa | `prodigy_score` or `score` | respective file | indisponível |
| Status pesquisa | `status` / `eligible` | rank JSON | never treat as approval |

**Gap:** there is **no** recovered field named `assertividade`. Do not compute a new composite. Show `win_rate_pct` as percentual de acertos and say so in REQUIREMENTS + map.

**Gap:** TradingView ingest rows typically have **no** rank JSON — all metric cells indisponível.

**Gap:** N51 does **not** block TradingView HMAC ingest at Gate A. Queue + eligibility apply to **copy adoption** (C2/Prodígio subscribed + panel operating labels). Document that webhook authenticity stays Feature 9.

Rank `eligible` / `PRODIGY_CANDIDATE_RESEARCH` / `copy_approved` from calculate (always false/empty) **never** auto-approves.

## Compatibility / license / security

- MIT vendor via `src/original.py` only; no bump (pin = GitHub `main` at plan-time).
- Never print, log, or embed `C2_API4_KEY`, `SIGNAL_COPY_SECRET`, or broker keys.
- Approval rows store platform + provider_id + status only — no secrets.
- `LIVE_TRADING_ENABLED=false`. Phase does not rise from PnL. Approval does not POST an order.

## Plan-time confirmation (2026-11-17)

| Check | Result |
|-------|--------|
| Branch | `front/n27-alpaca-loop` — proceed (not a foreign `sprint/X`) |
| `docs/VENDOR-PIN.md` SHA | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — **unchanged** (no bump) |
| `git ls-remote` `Jakeschincariol/day-trader-skill` `refs/heads/main` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — matches pin |
| Local vendor git | submodule not initialized; directory empty — **≠ claim of reviewed local HEAD** |
| `src/` in this plan-time inventory | **zero** product edits |
| Policy source | `docs/REQUIREMENTS.md` v0.5 Feature 4 named allowlist — **update in N51.1 to panel pre-approval**; do not invent scores |
