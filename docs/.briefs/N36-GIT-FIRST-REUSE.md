# N36.0 Git First — Central kill-switch copy (no logic change)

> Rock PLAN N36 · 2026-11-17 · frente `front/n27-alpaca-loop` · **no vendor bump** · **no LIVE** · **no Clear/OANDA HTTP**  
> Refino copy-only após FAIL: «Liberar operação demo» / «operação demo permitida» colidem com `demo_operation_on`.

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| Local `vendor/day-trader-skill` | **empty / absent** on this worktree — not a git checkout; treat pin above as the only SHA |
| GitHub `Jakeschincariol/day-trader-skill` `main` | **not re-checked** (fail-closed: do not claim current main) |

No vendor upgrade. Upstream has no operator Central HTML and no Portuguese kill-switch labels. Do not copy scoring. Do not enable live.

## Why this is copy, not a second kill switch

| Already on disk | Confusing today | N36 does |
|-----------------|-----------------|----------|
| `render_central_page` PATCH `{kill_switch_on:on}` via `id=kill-on` / `kill-off` | Buttons «Ligar parada» / «Desligar parada» read like power on/off | Replace visible strings only; keep ids and JSON body |
| Status `Parada geral ligada` / `Operando` | Sounds like the lab is running vs stopped | «Freio de emergência ativo» / «Freio liberado (outros limites ainda valem)» |
| `kill_switch_active` + `_demo_panel_block` return `KILL_SWITCH` | Semantics already: true blocks new demo orders | **Do not touch** |
| `demo_operation_on` (default false) → `_demo_panel_block` returns `DEMO_OPERATION_OFF` | Separate flag from the kill switch | **Out of N36** — not renamed; kill false does **not** turn this on |
| `tests/test_panel_ops.py` asserts «Central» and «Live desligado»; cycle test patches the flag | No assertion on button labels | Add string tests; keep cycle test |
| `DASHBOARD-OPERATIONS.md` «Ligar parada geral» | Same confusion in the operator sheet | Align that one line |

**Not N36:** new Live button, changing `kill_switch_on` meaning, renaming or toggling `demo_operation_on`, DESIGN.md prototype, env-runbook «Ligar» for `TRADING_LAB_KILL_SWITCH`, N29.5 homolog.

## Reuse inventory (MUST)

| Capability | Path / function | Decision | Rationale | Tests / evidence |
|------------|-----------------|----------|-----------|------------------|
| Central HTML | `src/panel_ops_html.py` `render_central_page` | **Adapt strings only** | Single source of the confusing labels | `tests/test_panel_ops.py` `test_login_sets_cookie_and_opens_central` |
| Dashboard routing | `src/v4_web_dashboard.py` `serve_operator_panel` | **Call — do not fork a second page** | Already renders Central | same HTTP tests |
| Kill flag persistence | `PATCH /api/triggers` body `kill_switch_on` | **Do not change** | Append-only `control_flags` | `tests/test_panel_triggers.py` |
| Gate B kill | `src/gate_b_risk.py` `kill_switch_active` | **Do not touch** | Blocks new paper | `tests/test_gate_b_risk.py` `test_kill_switch_env` |
| Paper loop block | `src/signal_paper_runner.py` `_demo_panel_block` | **Do not touch** | `kill_switch_on=true` → `KILL_SWITCH`; `kill_switch_on=false` only clears that gate | `test_n34_kill_switch_blocks_before_adapter_http` |
| Demo operation flag | `src/risk_control_flags.py` `demo_operation_on: False` + `_demo_panel_block` `DEMO_OPERATION_OFF` | **Do not touch / OUT** | Separate flag; default off; kill false does not set it true | `tests/test_risk_control_flags.py`; `tests/test_signal_paper_runner.py` |
| Reject mapping | `src/panel_ops_data.py` `ANCHOR_FIELD_BY_REJECT['KILL_SWITCH']` | **Do not touch** | No button copy here | `tests/test_panel_ops.py` blocked_context |
| Default kill flag | `src/risk_control_flags.py` `kill_switch_on: False` | **Reuse** | Default = brake released (kill gate off) | cycle + Central render |
| trader-entry/exit/budget/risk/scanner | `src/original.py` | **Do not touch** | MIT loader; no panel | `tests/test_vendor_verify.py` |

## Security / invariants

- `LIVE_TRADING_ENABLED=false`. No Live button.
- `kill_switch_on=true` still BLOCKS new demo orders.
- `kill_switch_on=false` only clears the kill gate. It does **not** turn on `demo_operation_on` (default off → `DEMO_OPERATION_OFF`).
- PATCH payload stays `{kill_switch_on: true|false}`. Button ids stay `kill-on` / `kill-off`.
- Kill-switch copy must not say «operação demo permitida» or «Liberar operação demo».
- No secrets, no vendor bump, no real Clear/OANDA HTTP, no invented scoring.
- HTTP 200 / queue / panel-on-air still not a fill.

## Deferred (out of N36)

- `demo_operation_on` copy, rename, or toggle (separate flag; not this sprint).
- N29.5 live homolog (operator creds).
- DESIGN.md historical prototype copy.
- HOMOLOGATION env kill-switch «Ligar/Desligar» (worker env, not Central buttons).
- REQUIREMENTS criterion wording «Parada geral pelo painel» (acceptance already `[x]`).
