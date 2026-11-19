# N57.0 Git First — Collective2 na fila a partir dos arquivos brutos (ISS-024)

> Rock PLAN N57 · 2026-11-19 · frente `front/sinais-raw-path` · **no vendor bump** · **LIVE false**  
> Plan-time inventory (planner Grok). EXECUTE (N57.0) re-checks `git ls-remote` and records confirmation; do not bump.  
> **Não** usa os identificadores N45–N47.  
> N56 já em `main` (PR **#76** merge `554625e`; stamp `5edd2c8`). Reuse the N54/N55/N56 POST/job — **discover C2 IDs from canonical raw**, do not add a parallel package.  
> Allowlist / `C2_PAPER_COPY_APPROVED_IDS` / ledger approve remains the **paper-copy** gate, not the gate to *appear* in the preapproval queue.

## Why this sprint

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| Canonical raw glob | `prodigy_rank.calculate` already globs `{raw}/*_closed_trades.json` numeric prefixes | **copy_pattern** for C2 ID discovery — never change `WINDOW_DAYS` / `MIN_TRADES` |
| C2 ID merge | `_merged_c2_strategy_ids` unions **allowlist + research JSON only** | **adapt** — union canonical raw IDs (+ research JSON); allowlist optional extra for fetch, not required to show |
| Live C2 fetch | `_live_refresh_collective2` + `c2_history_collect` / `_invoke_c2_history_collect` | **call** — fetch/update discovered IDs when `C2_API4_KEY` is set |
| Canonical raw path | `_providers_raw_dir` = `root/'providers'/'raw'` (N56 / #76) | **call** — do not revert doubled `reports/` join |
| Preapproval queue | `build_preapproval_queue` adds C2 from research JSON + allowlist seed | **adapt** — add discovered raw IDs as **pending** (`source: discovered`); do not auto-approve |
| Paper-copy gate | `load_c2_paper_copy_approved_ids` / `resolve_c2_paper_copy_approved_ids` | **keep** — empty allowlist ⇒ `approved_for_paper_copy` false |
| Rank Prodígio 15d | `PRODIGY_CANDIDATE_RESEARCH` filter in the queue | **keep** — same raw files may be C2-pending and still absent from Prodígio |
| Busca TradingView | Não existe | **forbidden** — ingested origins only |
| C2 marketplace search | Não existe | **forbidden** — no invented listing API |
| trader-* vendor | `src/original.py` | **do not call** from this job |

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` (plan-time 2026-11-19) | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` **matches pin** |
| Local `vendor/day-trader-skill` | Directory exists but **empty** (`git -C` walks up to this worktree). Do **not** bump. |

Upstream has no PanelShell, no preapproval queue, no ISS-024 job, no allowlist. Load trader-* only via `src/original.py`.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests |
|------------|-----------------|----------|-----------|-------|
| Raw ID glob | `prodigy_rank.calculate` `base.glob('*_closed_trades.json')` | **copy_pattern** | Same numeric prefix rule; do not reimplement rank | N57.2: raw IDs appear as Collective2 pending |
| Canonical dir | `_providers_raw_dir` (N56) | **call** | Volume `{root}/providers/raw` already fixed | N56 suite remains green |
| C2 ID merge | `_merged_c2_strategy_ids` | **adapt** | Today misses raw; ops: sources_ok + empty C2 queue | mock fetch receives discovered IDs |
| C2 research JSON | `_load_c2_research_rows` / `_load_c2_research_candidates` (skip `PRODIGY_RANK_RESEARCH_ONLY`) | **call** | Eligible source if present | existing N55 research fixture still unions |
| Queue | `build_preapproval_queue` | **adapt** | Show pending C2 from raw/research without allowlist | empty allowlist + three raw IDs |
| Paper-copy seed | `load_c2_paper_copy_approved_ids` | **keep** | Gate for named operation, not queue visibility | `approved_for_paper_copy` false when empty |
| Ledger approve | `upsert_signal_provider_approval` | **keep** | Refresh must not write approve | no ledger mutation on POST refresh |
| History fetch | `c2_history_collect` via `_invoke_c2_history_collect` | **call** | Update discovered IDs when key present | mock; no live host |
| Empty-id honesty | `_live_refresh_collective2` always `sources_ok.append('collective2')` even with `ids=[]` | **adapt** | Ops saw sources_ok with no rows | empty discovery + key → honest issue, not fake ok |
| TV origins | `_unique_tradingview_origins` | **keep** | ADR-012 | existing N55 |
| trader-* | `src/original.py` | **do not call** | Not copy/rank logic | — |

## Operator evidence (2026-11-19, after N56 #76)

| Symptom | What is true | What N57 must do |
|---------|--------------|------------------|
| Allowlist env empty; `config/c2_paper_copy_allowlist.json` empty | Seed lists are empty — **correct** for paper-copy closed | Do **not** require filling them to *show* candidates |
| Refresh `sources_ok` includes `collective2` | Key was present; `_merged_c2_strategy_ids` returned `[]` so fetch wrote nothing; job still marked ok | Discover IDs from canonical raw; if none, honest issue (not silent ok) |
| Raw has `132169961`, `148311109`, `30415311` | Canonical `{root}/providers/raw/{sid}_closed_trades.json` | Queue lists those IDs as Collective2 **pending**; live refresh fetches them |
| Same files `UNSCORABLE` / `closed_trades_15d=0` | Feature 4 / Prodígio 15d (N56) | Stay **out** of the Prodígio queue; **in** Collective2 as candidates |
| Paper-copy | Allowlist / env / ledger approve | Unchanged gate; approve ≠ fill; do not auto-approve |

## Compatibility / license / security

- MIT vendor via `src/original.py` only; pin unchanged.
- Never print, log, or embed `C2_API4_KEY` / Alpaca keys.
- `LIVE_TRADING_ENABLED=false`. Refresh ≠ approve ≠ fill.
- **Forbidden:** seed allowlist as a prerequisite to appear; auto-approve; write operator IDs into committed allowlist; TradingView search HTTP; C2 marketplace search; change Feature 4 constants; parallel package beside `src/`; steal N45–N47.
- «Finalizado» only after merge to `main`.

## Plan-time confirmation (2026-11-19)

| Check | Result |
|-------|--------|
| Worktree | `/home/igor/cursor/trading-lab.fronts/sinais-raw-path` |
| Branch | `front/sinais-raw-path` |
| N56 | PR **#76** MERGED (`554625e`); front stamp `5edd2c8` |
| ISS-024 | Open; sprint field → N57 |
| Steal N45–N47 | **No** |
| LIVE | **false** |
| `--root` default | **unchanged** `/app/reports` |
| Upstream SHA vs pin | **match** `3d0f4ef` |
