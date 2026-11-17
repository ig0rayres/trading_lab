# N52.0 Git First — Sinais decision cockpit (ISS-022)

> Rock PLAN N52 · 2026-11-17 · frente `front/n27-alpaca-loop` · **no vendor bump** · **LIVE false**  
> Plan-time inventory (planner Grok). EXECUTE (N52.0) re-checks `git ls-remote` and records confirmation; do not bump.  
> **Não** usa os identificadores N45–N47.  
> Design já entregue em `docs/design/` (`/designer`). Esta sprint **implementa** o cockpit `/sinais`, não redesenha as outras rotas.

## Why this sprint

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| `/sinais` as decision cockpit | N51 put pre-approval **below** operating; table shows only `win_rate_pct` + `reported_pnl_sum` | **This sprint** — reorder: decision first → operating/inventory → research/audit last; render **all** recovered keys |
| All recovered research metrics | `PREAPPROVAL_METRIC_KEYS` already overlays them; HTML ignores most | **This sprint** — HTML `metrics-block`; missing = `indisponível`; **no invented formula** |
| Visual tokens | `_PANEL_CSS` is a compact inline block; `docs/design/DESIGN.md` lists tokens | **This sprint** — extract tokens into `_PANEL_CSS`; other routes keep their HTML |
| Panel-overview IA | `docs/design/mockups/panel-overview.md` maps Central, Ordens, … | **Later sprints** — N52 may only add shared CSS variables; do not redesign those pages |
| Change `panel_ops_data` | Overlay already includes every operator-listed key | **Do not change** unless EXECUTE proves a listed key never reaches HTML |
| Approval places an order | `POST /api/signals/providers` is adoption only | **Forbidden** — approve ≠ fill |
| Invent scoring / LIVE / steal N45–N47 | Feature 4, campaign stubs | **Forbidden** |

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` | **`3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd`** (plan-time `git ls-remote` 2026-11-17) — **matches pin** |
| Local `vendor/day-trader-skill` | Submodule **recorded** at pin `3d0f4ef` (`git submodule status` shows `-3d0f4ef…`, not initialized). Worktree directory has **no** checkout files. Do **not** bump. Do **not** treat an empty folder as reviewed main. Docker still clones the pin at image build. |

Upstream has no operator Central, no `/sinais`, no CSS design system, no provider-approval queue. Do not copy scoring. Do not enable live. Do not load `trader-entry|exit|budget|risk|scanner` except via `src/original.py`.

If GitHub is unreachable at EXECUTE, stop claiming current `main`. Re-run `git ls-remote`; if it still matches the pin, proceed without bump.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests / evidence |
|------------|-----------------|----------|-----------|------------------|
| Pre-approval HTML | `src/panel_ops_html.py` `_signals_preapproval_section_html`, `_format_research_metric` | **extend** | Already formats missing as `indisponível`; only two keys rendered | `tests/test_panel_ops.py` `test_n51_html_preapproval_section` |
| Section order | `render_signals_page` concatenates operating then preapproval then inventory then C2/pool/adoption/audit | **extend** — reorder helpers, do not rewrite loaders | ISS-022 hierarchy; keep inner `h2` titles so N48–N51 copy still matches | `test_n50` operating before audit |
| Metric overlay | `src/panel_ops_data.py` `PREAPPROVAL_METRIC_KEYS`, `_overlay_research_metrics` | **call** — do not rewrite unless a listed key is absent | Keys already: `win_rate_pct`, `shrunk_win_rate_pct`, `profit_factor_reported`, `reported_pnl_sum`, `net_return_pct`, `max_drawdown_pct`, `prodigy_score`, `score`, `status` (+ `eligible`/`copy_approved` must **not** display as paper approval) | `test_n51_preapproval_metrics_reused_not_zero` |
| Approve / reject | `_PROVIDER_APPROVAL_SCRIPT`, `POST /api/signals/providers` | **call** — keep | N51 already authenticates; N52 is presentation | `test_n51_post_providers_*` |
| Panel CSS | `_PANEL_CSS` in `panel_ops_html.py` | **extend** with DESIGN.md tokens | Shared vars allowed; do not restyle brake-strip colors (N38) | Central still has `brake-strip--active` / `--released` |
| Design tokens | `docs/design/DESIGN.md` | **copy_pattern** into CSS variables | Designer already done; no second design pass | Visual: `--bg-canvas`, `--action-primary`, `--action-danger` |
| Sinais wireframe | `docs/design/mockups/sinais.md` | **copy_pattern** for layout + empty states | Operator ISS-022 + designer | Empty-state Portuguese strings |
| Panel overview | `docs/design/mockups/panel-overview.md` | **do not implement pages** | IA guide for later; shared CSS vars only if needed | Out of N52 HTML recorte |
| prodigy_rank fields | `src/prodigy_rank.py` | **do not call from panel** | Reuse JSON already overlaid | `PRODIGY_RANK_RESEARCH_ONLY` |
| trader-* | `src/original.py` | **Do not touch** | MIT loader | `tests/test_vendor_verify.py` |
| Paper submit | `process_after_gate_b` | **Do not call from panel** | Approval ≠ fill | Feature 7 tests |

## Honest field map (do not invent)

Operator ISS-022 + parent: show **all** recovered keys in pre-approval. Canonical missing label: **`indisponível`** (designer `N/D` is the same meaning; tests use `indisponível`).

| Operator label (PT) | Recovered field | If absent |
|---------------------|-----------------|-----------|
| Percentual de acertos (pesquisa) | `win_rate_pct` | `indisponível` — not 0 |
| Percentual encolhido (pesquisa) | `shrunk_win_rate_pct` | `indisponível` |
| Fator de lucro reportado (pesquisa) | `profit_factor_reported` | `indisponível` |
| Soma P/L reportada (pesquisa) | `reported_pnl_sum` | `indisponível` |
| Retorno líquido % (pesquisa) | `net_return_pct` | `indisponível` |
| Drawdown máximo % (pesquisa) | `max_drawdown_pct` | `indisponível` |
| Score pesquisa | `prodigy_score` or `score` (whichever present) | `indisponível` |
| Status pesquisa | `status` | `indisponível`; never treat as paper-copy approval |

**Gap:** there is **no** recovered field named `assertividade`. Do not compute a composite. Show `win_rate_pct` as percentual de acertos.

**Gap:** `eligible` / `copy_approved` may exist on the overlay — **do not** paint them as “aprovado para cópia”. Panel status of the queue row remains `pending|approved|rejected`.

**Gap:** queue items have `provider_id`, not a separate `name`. Research JSON may have `name` on disk; **do not** require a `panel_ops_data` change to invent names. Identifier column = platform + id.

## Compatibility / license / security

- MIT vendor via `src/original.py` only; no bump (pin = GitHub `main` at plan-time).
- Never print, log, or embed `C2_API4_KEY`, `SIGNAL_COPY_SECRET`, or broker keys.
- `LIVE_TRADING_ENABLED=false`. Approval does not POST an order.
- Delivery «finalizado» only after merge to `main` (operator rule).

## Plan-time confirmation (2026-11-17)

| Check | Result |
|-------|--------|
| Branch | `front/n27-alpaca-loop` — proceed (not a foreign `sprint/X`) |
| `docs/VENDOR-PIN.md` SHA | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — **unchanged** (no bump) |
| `git ls-remote` `Jakeschincariol/day-trader-skill` `refs/heads/main` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` — matches pin |
| Local vendor git | submodule not initialized; directory empty — **≠ claim of reviewed local HEAD** |
| `src/` in this plan-time inventory | **zero** product edits |
| Design artifacts | `docs/design/DESIGN.md`, `mockups/sinais.md`, `mockups/panel-overview.md`, `README.md` present |
| Policy source | ISS-022 + N51 overlay; HTML gap only |
