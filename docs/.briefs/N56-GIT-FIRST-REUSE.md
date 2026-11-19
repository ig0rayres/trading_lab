# N56.0 Git First — Caminho dos arquivos brutos no volume de relatórios (ISS-024)

> Rock PLAN N56 · 2026-11-19 · frente `front/sinais-raw-path` · **no vendor bump** · **LIVE false**  
> Plan-time inventory (planner Grok). EXECUTE (N56.0) re-checks `git ls-remote` and records confirmation; do not bump.  
> **Não** usa os identificadores N45–N47.  
> N55 já em `main` (PR **#74** código; PR **#75** closeout docs `25f52ce`). Reuse the N54/N55 POST/job — **fix the join**, do not add a parallel package.  
> **Não** mudar o default `--root /app/reports` como atalho.

## Why this sprint

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| Dashboard `--root` | `v4_web_dashboard.main` default `/app/reports`; `scripts/v4_ops_main.sh` `DASHBOARD_ROOT` | **keep** — operator-confirmed volume; not a workaround knob |
| Job Prodígio | `_live_refresh_prodigy` joins `root/'reports'/'providers'/'raw'` | **fix** → `root/'providers'/'raw'` (`/app/reports/providers/raw`) |
| Job Collective2 | `_live_refresh_collective2` same doubled join + `.../signals` | **fix** same canonical layout |
| Rank Prodígio 15d | `prodigy_rank.calculate` (`WINDOW_DAYS=15`, `MIN_TRADES=5`, ≥3 days, `PRODIGY_CANDIDATE_RESEARCH` / `UNSCORABLE`) | **call** — never invent score or change constants |
| Adapter raw | `strategy_data_adapter` `--raw-dir` default `/app/reports/providers/raw` | **call** — already the real volume path |
| Fila pré-aprovação | `build_preapproval_queue` keeps Prodígio only when `status == PRODIGY_CANDIDATE_RESEARCH` | **keep** — eligible rows only |
| Dual read fallback | `panel_ops_data._load_c2_active_orders_snapshot` tries `reports/providers/signals` **and** `providers/signals` | **keep** read fallback; **write** canonical |
| Busca TradingView | Não existe | **forbidden** — ingested origins only |
| C2 marketplace search | Não existe | **forbidden** — named IDs + `C2_API4_KEY` on the server |
| trader-* vendor | `src/original.py` | **do not call** from this job |

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` (plan-time 2026-11-19) | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` **matches pin** |
| Local `vendor/day-trader-skill` | Directory exists but **empty** (`git -C` walks up to this worktree — do **not** treat `25f52ce` as vendor SHA). Do **not** bump. |

Upstream has no PanelShell, no preapproval queue, no ISS-024 job, no `--root` join. Load trader-* only via `src/original.py`.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests |
|------------|-----------------|----------|-----------|-------|
| Reports root | `v4_web_dashboard.main --root` default `/app/reports`; `v4_ops_main.sh` `DASHBOARD_ROOT` | **keep** | Real volume; changing the flag hides the join bug | N56.2 must not require a different `--root` |
| Intelligence JSON | `_intelligence_dir` = `root/'intelligence'` → `/app/reports/intelligence` | **keep** | Already correct under the reports volume | existing N54/N55 persist tests |
| Prodígio raw join | `_live_refresh_prodigy` | **adapt** | Today: `/app/reports/reports/providers/raw` (empty). Canonical: `/app/reports/providers/raw` | N56.2: files at `providers/raw` found; doubled path unused |
| C2 history write | `_live_refresh_collective2` `raw_dir` + `snap_dir` | **adapt** | Same doubled join; C2 history must land where `calculate` reads | mock opener; no live net |
| Rank 15d | `prodigy_rank.calculate` | **call** | Eligible = existing `PRODIGY_CANDIDATE_RESEARCH`; `UNSCORABLE` + `closed_trades_15d=0` stay out of the queue | `tests/test_prodigy_rank.py` + N56.2 |
| Queue filter | `build_preapproval_queue` | **keep** | Do not loosen to OBSERVATION/UNSCORABLE | operator data: 3 providers 15d=0 correctly absent |
| C2 key | `os.environ.get('C2_API4_KEY')` | **keep** | Missing key → `C2_API4_KEY_missing`; never invent IDs | N55 tests remain |
| TV origins | `_unique_tradingview_origins` | **keep** | ADR-012; no search API | existing N55 |
| trader-* | `src/original.py` | **do not call** | Not copy/rank logic | — |

## Honest emptiness vs missing files (operator 2026-11-19)

| Symptom | What is true | What N56 must do |
|---------|--------------|------------------|
| Job looks empty | Join `root/'reports'/...` with `--root=/app/reports` → `/app/reports/reports/providers/raw` | Fix join to `root/'providers'/'raw'`. Do **not** change `--root`. Do **not** mkdir the doubled path as a workaround. |
| Files on disk | `/app/reports/providers/raw/{sid}_closed_trades.json` | `calculate` must read that directory |
| Three providers `UNSCORABLE`, `closed_trades_15d=0` | Feature 4 / Prodígio 15d already in `prodigy_rank` | **Correctly absent** from the Prodígio queue until fresh Collective2 history exists. Do **not** emit `prodigy_raw_missing` when files exist. Do **not** invent a score. |
| Collective2 empty | Needs server `C2_API4_KEY` + named IDs | Keep `C2_API4_KEY_missing`; never print the key |
| TradingView | Ingested origins only | Keep ADR-012; no search API |

Tests today write fixtures to `root/'reports'/'providers'/'raw'` (`_n54_write_prodigy_raw_trades`). That encodes the bug and stays green. N56.2 must move fixtures to `root/'providers'/'raw'` and assert the doubled path is not the input to `calculate`.

## Compatibility / license / security

- MIT vendor via `src/original.py` only; pin unchanged.
- Never print, log, or embed `C2_API4_KEY` / Alpaca keys.
- `LIVE_TRADING_ENABLED=false`. Refresh ≠ approve ≠ fill.
- **Forbidden:** change `--root` default as workaround; TradingView search HTTP; C2 key in browser; parallel package beside `src/`; steal N45–N47; invent Feature 4 thresholds.
- «Finalizado» only after merge to `main`.

## Plan-time confirmation (2026-11-19)

| Check | Result |
|-------|--------|
| Worktree | `/home/igor/cursor/trading-lab.fronts/sinais-raw-path` |
| Branch | `front/sinais-raw-path` @ `origin/main` `25f52cea7b4d1398919339c115f3216795a575f9` (PR **#75**) |
| ISS-024 | Open; sprint field → N56 |
| Steal N45–N47 | **No** |
| LIVE | **false** |
| `--root` default | **unchanged** `/app/reports` |
| Upstream SHA vs pin | **match** `3d0f4ef` |
