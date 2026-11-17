# N43.0 Git First — análise Google (TimesFM) no menu do dia a dia

> Rock PLAN N43 · 2026-11-17 · frente `front/n27-alpaca-loop` · **no vendor bump** · **not Clear/OANDA** · **no phase promotion** · **no paper submit from panel** · **LIVE false**  
> Plan-time inventory. EXECUTE (N43.0) re-checks `git ls-remote` and records confirmation; do not bump.

## Why this sprint

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| TimesFM HTML on the login menu | Adapter + daily report exist; **no** `/analise-google` in `_nav` | **This sprint** — research-only, fail-closed |
| Strategy catalog on the login menu | `/estrategias` delivered N42 | **Done** — do not reopen |
| Orders / history lists | `/ordens` `/historico` delivered N41 | **Done** — do not reopen |
| Tá Barato family screen | Catalog row exists; formula still G-FORM | **N45** — blocked on N17.2 |
| Clear / OANDA | Fail-closed adapters; no operator creds | **Forbidden** until N29.5 |
| Parameter apply / undo | Central `POST /api/strategy-parameters` | **OUT** — not this page |
| New project / rewrite | Product already exists | **Forbidden** |

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` | **`3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd`** (plan-time `git ls-remote` 2026-11-17) — **matches pin** |
| Local `vendor/day-trader-skill` | Submodule **recorded** at pin `3d0f4ef` (`git submodule status` shows `-3d0f4ef…`, not initialized). Worktree directory has **no** `.git` and **no** checkout files. Do **not** bump. Do **not** treat an empty folder as reviewed main. Docker still clones the pin at image build. |

Upstream has no operator Central, no Command Panel, no TimesFM HTML, no `/analise-google`. Search of vendor tree for TimesFM / operator panel: **no matches** (empty checkout). Do not copy scoring. Do not enable live. Do not load `trader-entry|exit|budget|risk|scanner` except via `src/original.py`. Do not vendor-copy TimesFM weights into this repo.

If GitHub is unreachable at EXECUTE, stop claiming current `main`. Re-run `git ls-remote`; if it still matches the pin, proceed without bump.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests / evidence |
|------------|-----------------|----------|-----------|------------------|
| Official TimesFM adapter | `src/timesfm_context.py` `build_timesfm_block`, `run_timesfm_forecast`, `_unavailable` | **call — do not reimplement the model** | N31.2 already fail-closes (`UNAVAILABLE`, no numeric `forecast`); labels `research_tip`; `paper_allowed` / `execution_authorized` false | `tests/test_timesfm_context.py`, `tests/test_n31_g_ajuste_guardrails.py` |
| Official package | PyPI `timesfm` · `google-research/timesfm` · import `timesfm` / `timesfm3.mlx.TimesFM3Forecaster` | **reuse official API only** | Recorded in `docs/.briefs/N31-GIT-FIRST-REUSE.md`; default image must **not** require the package | N31.0 |
| Daily report snapshot | `src/evolution_engine.py` `review()` → `timesfm` + `tips`; writes `evolution/daily/{day}.json` only from CLI `main()` | **read the JSON if present — do not call `review()` / `main()` on dashboard GET** | `review()` itself is read-only, but the CLI writes the daily file; a GET must not start inference or rewrite reports | `tests/test_evolution_engine.py` |
| Suggestion surfaces | `src/trading_dashboard_data.py` `_latest_evolution_daily_tips`, `SUGGESTION_ITEM_LABELS`, `command_panel.continuous_improvement` | **copy_pattern for tip shape; do not dump `decisions.jsonl` on the new page** | Feature 11 tips already labeled; area 10 (melhoria contínua) stays Command Panel v1 | `tests/test_n28_suggestion_labels.py` |
| Daily menu shell | `src/panel_ops_html.py` `_nav`, `OPERATOR_PANEL_PATHS`, `render_strategies_page` / `render_signals_page` | **extend / copy_pattern** | Same shell as Sinais (N25), Ordens (N41), Estratégias (N42) | `tests/test_panel_ops.py` HTTP |
| Panel bundle | `src/panel_ops_data.py` `build_panel_bundle` | **extend** | Put a `timesfm` / research-tips block on the same bundle | N25 / N41 / N42 |
| Route split | `src/v4_web_dashboard.py` `serve_operator_panel`, `serve_panel_json`, `operator_panel_route` | **extend** | Cookie session; 404 today for `/analise-google` | `test_nav_includes_estrategias_menu_link` |
| DESIGN «Sugestões» | `docs/design/DESIGN.md` §4 sidebar | **adapt label** | Wireframe says Sugestões; campanha / ROADMAP name the item **Análise Google** so it is not confused with Central parameter apply | N16 / ISS-007 |
| Paper submit | `src/paper_gateway_queue.py`, `src/signal_paper_runner.py` | **Do not call from panel** | Dashboard stays read-only | Feature 7 tests |
| Phase PATCH | `src/v4_web_dashboard.py` `apply_strategy_patch` | **Do not call** | N42 already GET-only for catalog | `tests/test_panel_triggers.py` |
| Clear / OANDA adapters | `src/demo_broker_adapters.py` | **Do not touch** | ISS-010 / N29.5 | N34 tests |
| Supervised parameters | `POST /api/strategy-parameters` | **Do not touch** | Feature 11 apply/undo is Central, not this menu page | N28 |
| trader-* | `src/original.py` | **Do not touch** | MIT loader | `tests/test_vendor_verify.py` |
| Command Panel v1 evolution list | `src/v4_web_dashboard.py` `render_page` melhoria contínua | **Do not replace v1** | Login menu is what the operator opens after N18 | N16 / ISS-007 |

## Honest data gap (do not paper over)

- Login menu `_nav` has Central, Sinais, Estratégias, Ordens, Histórico, Prodígio, Performance — **no** Análise Google.
- `build_timesfm_block` already returns `timesfm_status=UNAVAILABLE` and empty `tips` when `TIMESFM_ENABLED` is off (default), checkpoint missing, series short, or import/runtime fails. It never fabricates `forecast` / `forecast_values`.
- Latest `evolution/daily/*.json` may already contain a `timesfm` object. The new page **displays** that snapshot (or a fresh fail-closed adapter call when no file exists). It does **not** run `evolution_engine.main()` and does **not** load TimesFM weights on every GET when a snapshot exists.
- Default lab image does **not** install `timesfm`. Missing dependency = Portuguese reason on the page, not a fake series, not a 404 that looks like the area vanished.
- Forecast metadata (`model_id`, `horizon`, `forecast_shape`) is research context. It is **not** an entry, stop, Tá Barato percentil, or Prodígio score.
- `command_panel.continuous_improvement` mixes daily tips with `decisions.jsonl`. N43 shows TimesFM + labeled `research_tip` / `suggestion` from the daily snapshot. The event log stays on Command Panel v1 (map area 10).

## Compatibility / license / security

- MIT vendor via `src/original.py` only; no bump (pin = GitHub `main` at plan-time).
- TimesFM **code** Apache-2.0; some **3.0 checkpoints** may be non-commercial — do not add the package to the required image; operator enables `TIMESFM_ENABLED` + `TIMESFM_CHECKPOINT` (prefer 2.5) outside this sprint.
- No tokens, `.env`, Hugging Face tokens, or EasyPanel secret values in HTML or tests.
- `LIVE_TRADING_ENABLED=false`. HTTP 200 / queue / semaphore ≠ fill. Research tip ≠ order authorization.

## Plan-time confirmation (2026-11-17)

| Check | Result |
|-------|--------|
| `docs/VENDOR-PIN.md` SHA | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — **unchanged** (no bump) |
| `git ls-remote` `Jakeschincariol/day-trader-skill` `refs/heads/main` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — matches pin |
| Local vendor git | submodule not initialized; directory empty — **≠ claim of reviewed local HEAD** |
| Worktree vs `origin/front/n27-alpaca-loop` | HEAD `efaa1ad` (N42 stamp); this plan writes docs + session only |
| `src/` in this plan-time inventory | **zero** product edits |
