# N39.0 Git First — closeout docs N37 platform health (ISS-014)

> Rock PLAN N39 · 2026-11-17 · frente `front/n27-alpaca-loop` · **no vendor bump** · **no `src/`** · **do not steal N37**  
> **EXECUTE (2026-11-17):** inventário confirmado; pin `3d0f4ef` bate GitHub `main`; zero bump; carimbos N39.1–N39.4 aplicados.

## Why this sprint (not N21, not Clear/OANDA)

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| N37 / ISS-014 saúde automática | **Code already on `origin/main`** — tasks `[x]`; Status still `em execucao` | **This sprint** — docs stamp + close ISS-014 |
| N21 ciclo fill / P&L | Tasks already `[x]`; tests on disk (`test_paper_fill_cycle`, `test_ledger_loss_anchor`, `test_paper_restart_no_duplicate`) | **Not a code gap.** Status `planejada` is leftover paper; out of N39 |
| ISS-011 restante | N17.2 G-FORM + ISS-010 / N29.5 | **Operator-gated** — note only |
| EasyPanel rebuild `trading-lab` | Human | **Operator-gated** — note only |
| Clear / OANDA adapters | Out of campaign | **Forbidden** |
| LIVE trading / invented scoring | Forbidden | **Forbidden** |

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| Local `vendor/day-trader-skill` | **empty / absent** on this worktree — not a git checkout; treat pin above as the only local SHA |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` | **`3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd`** (checked 2026-11-17 via `git ls-remote`) — **matches pin** |

No vendor upgrade. Upstream has no Central semaphore and no `platform_health`. Do not copy scoring. Do not enable live.

## Reuse inventory (cite only — zero `src/`)

| Capability | Path / function | Decision | Rationale | Tests / evidence |
|------------|-----------------|----------|-----------|------------------|
| Platform health probes | `src/platform_health.py` `run_probes`, `load_health_snapshot`, `write_worker_stamp` | **Cite — do not edit** | N37 code on main | `tests/test_platform_health.py` `PlatformHealthTests.test_run_probes_writes_snapshot`, `test_webhook_skipped_without_url`, `test_worker_stamp_enables_ok_worker`, `test_stale_queue_degraded`, `test_aggregate_overall_down_beats_degraded` |
| Status API field | `src/v4_web_dashboard.py` `platform_health` on snapshot / `/api/status` | **Cite — do not edit** | Feature 6 observability | `BuildSnapshotHealthTest.test_build_snapshot_includes_platform_health` |
| Central semaphore | `src/panel_ops_html.py` `_platform_health_block` | **Cite — do not edit** | Integrated with N38 brake strip | `tests/test_panel_ops.py`; DIARY N38 |
| Supervisor wiring | `scripts/v4_ops_main.sh` + `tests/test_v4_ops_layout.py` | **Cite — do not edit** | Probe loop in `v4-ops` | `test_v4_ops_layout` asserts `platform_health.py` |
| Operational defaults ON | `src/operational_defaults.py` / migrate seed | **Cite — do not edit** | N37.4; follow-up `ae916c6` isolated demo-off tests | `tests/test_operational_defaults.py` |
| trader-entry/exit/budget/risk/scanner | `src/original.py` | **Do not touch** | MIT loader | `tests/test_vendor_verify.py` |
| Clear / OANDA | `src/demo_broker_adapters.py` | **Do not touch** | ISS-010 / N29.5 | existing gate tests |
| N21 fill cycle | `tests/test_paper_fill_cycle.py` etc. | **Defer** | Already delivered; not ISS-014 | nodeids N21.* |

## Evidence to stamp (N39.1 — do not invent)

| Sprint | Index/Status today | Stamp `concluida`? | Cite |
|--------|--------------------|--------------------|------|
| **N37** | index `em execucao`; section `em execucao`; tasks `[x]` | **Yes** | feat `76f76b3` `feat(observability): platform health probes and operational defaults (N37)`; follow-up `ae916c6` `test: isolate demo-off gate checks from N37 migrate defaults`; PR **#52** MERGED `2026-11-17T13:14:04Z` (`https://github.com/ig0rayres/trading_lab/pull/52`); GitHub mergeCommit `3bebe1c7d3236690c67533ef916cbc5be3206d92`; nodeids above. **Do not steal N37 ID.** |
| **N38** | index `concluida`; section header still `planejada` | **Section Status only** | Closeout already cites PR **#54**; set section `> Status: planejada` → `concluida`. Do not rewrite N38 tasks. |
| **N21** | index `planejada`; tasks `[x]` | **No** | Leftover paper; not this honesty gap |
| **N17** | `planejada`; N17.2 `[ ]` | **No** | G-FORM operator |
| **N29** | `planejada`; N29.5 `[ ]` | **No** | EasyPanel creds operator |

## Gap (this sprint only)

| Gap | New code? | Notes |
|-----|-----------|-------|
| ROADMAP N37 Status vs merged PR #52 | **Docs** | Stamp `concluida` with SHA/PR/nodeid |
| ISS-014 still `em execucao` | **Docs** | Close with the same citations |
| DIARY N37 only records ID collision | **Docs** | Add real health delivery; keep collision note |
| TEST-EVIDENCE has no N37 row | **Docs** | One section; pytest ≠ EasyPanel rebuild ≠ fill |
| N38 section Status `planejada` vs index `concluida` | **Docs one-liner** | Align header only |
| Clear / OANDA / scoring / LIVE / N21 stamp | **No** | Forbidden or deferred |

## Security / invariants

- `LIVE_TRADING_ENABLED=false`.
- Closing ISS-014 does **not** mean the operator rebuilt EasyPanel or saw the semaphore in production.
- HTTP 200 / queue / panel-on-air / `OK_RESEARCH_ONLY` are not fills.
- B3_EQUITY / FOREX stay `NO_DEMO_ACCOUNT_PATH` (zero Alpaca POST).

## Deferred (out of N39)

- EasyPanel rebuild `trading-lab` (operator).
- N29.5 demo credentials in EasyPanel only (operator).
- N17.2 G-FORM / Tá Barato shadow→paper (operator).
- Stamping N21 `concluida`.
- Any `src/` change.
- Closing ISS-011, ISS-010, or ISS-013.
