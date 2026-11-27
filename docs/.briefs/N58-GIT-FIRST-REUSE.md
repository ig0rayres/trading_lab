# N58.0 Git First — Atualizar varre Collective2; TradingView sem busca (ISS-024)

> Rock PLAN N58 · 2026-11-19 · frente `front/sinais-raw-path` · **no vendor bump** · **LIVE false**  
> Plan-time inventory (planner Grok). EXECUTE (N58.0) re-checks `git ls-remote` and records confirmation; do not bump.  
> **Não** usa os identificadores N45–N47.  
> N57 já em `main` (PR **#77** merge `5ea662c`). Reuse the N54–N57 POST/job — **scan Collective2 via official SearchStrategies**, then Feature 4 / Prodígio 15d locally. Do not add a parallel package.  
> Allowlist / `C2_PAPER_COPY_APPROVED_IDS` / ledger approve remains the **paper-copy** gate, not the gate to *appear*.  
> Disk glob (N57) is **not** the product story for Atualizar.

## Why this sprint

Operator restated Atualizar (supersedes N57 disk inventory as definition of done):

1. Fixed eligibility each candidate must meet — reuse Feature 4 / Prodígio 15d already in `prodigy_rank` (`WINDOW_DAYS`, `MIN_TRADES`, ≥3 days, shrunk win-rate > 55, no stale last trade). **Do not invent thresholds.**
2. Button **Atualizar candidatos** = **scan homologated platforms** for strategies that meet those rules. Same spirit for Prodígio classification. **No allowlist** required to appear. **No** “only what’s already in cache/raw” as the product story. LIVE false; approve ≠ fill.

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| C2 SearchStrategies (official API4 GET) | Not called in recovered client | **adapt** — ID universe via existing `c2_history_collect.fetch` |
| C2 history-by-id | `PATHS` closed/daily/monthly equity | **call** closed_trades only on the scan path (what `prodigy_rank.calculate` reads) |
| C2 SearchHistoricalStrategies (POST, ≤6 C2 stats) | No POST helper; stats ≠ Feature 4 | **forbidden** |
| C2 GetLeaderBoard / GetStrategyDetails.Score | Not in recovered client | **forbidden** as eligibility |
| Prodígio 15d | `prodigy_rank.calculate` | **call** — do not change constants |
| C2 ID merge / raw glob | `_merged_c2_strategy_ids` / `discover_c2_strategy_ids_from_raw` (N57) | **keep as cache**, not as Atualizar definition of done |
| Preapproval queue | `build_preapproval_queue` | **adapt** — C2+Prodígio rows must meet recovered eligibility; unscorable raw IDs are not “scanned candidates” |
| Paper-copy gate | `load_c2_paper_copy_approved_ids` | **keep** |
| TradingView search | Does not exist (ADR-012 ingest only) | **OUT** — ISS-025; keep ingested origins; do not invent a TV search API |
| trader-* vendor | `src/original.py` | **do not call** from this job |

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` (plan-time 2026-11-19) | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` **matches pin** |
| Local `vendor/day-trader-skill` | Directory exists but **empty** (`git -C` walks up to this worktree). Do **not** bump. |

Upstream has no PanelShell, no preapproval queue, no ISS-024 job, no SearchStrategies wrapper. Load trader-* only via `src/original.py`.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests |
|------------|-----------------|----------|-----------|-------|
| C2 HTTP GET | `c2_history_collect.fetch` | **call** | Same host, Bearer, 25s timeout | mock; no live host |
| SearchStrategies | Official GET `/Strategies/SearchStrategies` | **adapt** | Recovered client is history-by-id only; official list exists — wire it, do not invent a storefront | mock Results + next_cursor |
| Closed trades | `PATHS['closed_trades']` | **call** | Rank already globs `*_closed_trades.json` | Feature 4 pass/fail fixtures |
| Rank 15d | `prodigy_rank.calculate` | **call** | Eligibility already coded | `UNSCORABLE` stays out |
| Live C2 job | `_live_refresh_collective2` | **adapt** | Today fetches merged/disk IDs only | Search mock called without allowlist |
| Queue | `build_preapproval_queue` | **adapt** | N57 listed every raw C2 ID as pending; operator wants eligibility | only `PRODIGY_CANDIDATE_RESEARCH` (or equivalent recovered status) |
| Refresh snapshot | `intelligence/candidates-refresh-latest.json` | **extend** | Persist C2 `next_cursor` + incomplete issue | second POST continues cursor |
| Paper-copy | `load_c2_paper_copy_approved_ids` | **keep** | Appear ≠ copy | `approved_for_paper_copy` false when empty |
| TV origins | `_unique_tradingview_origins` | **keep** | ADR-012; scan TV is ISS-025 | no invented TV HTTP |
| Raw glob N57 | `discover_c2_strategy_ids_from_raw` | **keep as cache** | Not the Atualizar story | regression: still must not require allowlist |
| trader-* | `src/original.py` | **do not call** | Not copy/rank logic | — |

## Honest gaps

### Collective2 — listing exists; recovered code does not call it

N57 forbade “invented marketplace search” because the **recovered client** only had history-by-id. Official API4 **does** expose `SearchStrategies` (GET, same host as `fetch`). N58 wires that list as the scan universe, then applies **recovered** Prodígio 15d on closed trades.

That is **not** a Collective2 storefront, not GetLeaderBoard, and not SearchHistoricalStrategies with C2’s six statistics.

### Collective2 — history-by-id is still the eligibility engine

SearchStrategies does **not** filter by recovered Feature 4 numbers. Minimal adaptation: list IDs → `GetStrategyHistoricalClosedTrades` → `prodigy_rank.calculate`. Do not substitute C2 Score.

### Collective2 — one POST cannot download the whole catalog

`fetch` timeout is 25s. One SearchStrategies call per Atualizar; persist `next_cursor`; history for IDs on **that** page; incomplete issue if more pages remain. Operator clicks Atualizar again to continue. Do not invent a custom page size in product copy.

### TradingView — no search API (blocker)

Recovered path is webhook ingest (`tradingview_webhook.ingest`) plus `_unique_tradingview_origins`. **No** TV search/list in this tree or in vendor pin. N58 **does not invent one**. Scan TV is **OUT** (ISS-025) until a contract exists. Ingested origins remain visible and are **not** sold as a scan.

## Compatibility / license / security

- MIT vendor via `src/original.py` only; pin unchanged.
- Never print, log, or embed `C2_API4_KEY` / Alpaca keys.
- `LIVE_TRADING_ENABLED=false`. Refresh ≠ approve ≠ fill.
- **Forbidden:** SearchHistoricalStrategies stats as Feature 4; GetLeaderBoard as eligibility; TV search HTTP; auto-approve; fill committed allowlist to show rows; change `WINDOW_DAYS` / `MIN_TRADES`; parallel package beside `src/`; steal N45–N47; LIVE true.
- «Finalizado» only after merge to `main`.

## Plan-time confirmation (2026-11-19)

| Check | Result |
|-------|--------|
| Worktree | `/home/igor/cursor/trading-lab.fronts/sinais-raw-path` |
| Branch | `front/sinais-raw-path` |
| N57 | PR **#77** MERGED (`5ea662c`) |
| ISS-024 | Open; add N58; keep OPEN |
| TV scan | **OUT** → ISS-025 |
| Steal N45–N47 | **No** |
| LIVE | **false** |
| `--root` default | **unchanged** `/app/reports` |
| Upstream SHA vs pin | **match** `3d0f4ef` |
