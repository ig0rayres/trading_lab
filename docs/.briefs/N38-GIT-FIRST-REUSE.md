# N38.0 Git First — Central brake-state strip (presentation only)

> Rock PLAN N38 · 2026-11-17 · frente `front/n27-alpaca-loop` · **no vendor bump** · **no LIVE** · **no Clear/OANDA HTTP**  
> Follow-on of N36 copy. Kill logic unchanged. Visual state only.

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| Local `vendor/day-trader-skill` | **empty / absent** on this worktree — not a git checkout; treat pin above as the only SHA |
| GitHub `Jakeschincariol/day-trader-skill` `main` | **not re-checked** (fail-closed: do not claim current main) |

No vendor upgrade. Upstream has no operator Central HTML and no Portuguese brake strip. Do not copy scoring. Do not enable live.

## Why this is presentation, not a second kill switch

| Already on disk | Confusing after N36 | N38 does |
|-----------------|---------------------|----------|
| N36 copy: «Freio de emergência ativo» / «Freio liberado (outros limites ainda valem)»; buttons «Ativar freio» / «Liberar freio» | Both buttons always visible; `.warn` yellow in both states; status lives in muted line | One halt-light strip; state class + one primary CTA; hide the no-op action |
| `render_central_page` PATCH `{kill_switch_on:on}` via `id=kill-on` / `kill-off` | Clicking Liberar when already released looks like nothing happened | Hide Liberar when released (no-op remains by design if PATCH false is sent) |
| `kill_switch_active` + `_demo_panel_block` return `KILL_SWITCH` | Semantics already: true blocks new demo orders | **Do not touch** |
| `demo_operation_on` (default false) → `DEMO_OPERATION_OFF` | Separate flag from the kill switch | **Out of N38** — not renamed |
| `RenderCentralPageFreioCopyTests` asserts **both** button labels always | Would fail the single-CTA lock | Rewrite assertions: state class + one CTA; keep old-copy absence + Live |
| `DASHBOARD-OPERATIONS.md` «Liberar freio usa o outro botão» | Still describes two equal buttons | One button per state |

**Not N38:** new Live button, changing `kill_switch_on` meaning, renaming or toggling `demo_operation_on`, full Central redesign, N29.5 homolog, ISS-013 close (copy already shipped).

## Reuse inventory (MUST)

| Capability | Path / function | Decision | Rationale | Tests / evidence |
|------------|-----------------|----------|-----------|------------------|
| Central HTML / CSS | `src/panel_ops_html.py` `_PANEL_CSS` + `render_central_page` | **Adapt presentation in place** | Single source of the always-yellow dual-button strip | `tests/test_panel_ops.py` `RenderCentralPageFreioCopyTests` |
| Dashboard routing | `src/v4_web_dashboard.py` `serve_operator_panel` | **Call — do not fork a second page** | Already renders Central | same HTTP tests |
| Kill flag persistence | `PATCH /api/triggers` body `kill_switch_on` | **Do not change** | Append-only `control_flags` | `tests/test_panel_triggers.py` |
| Gate B kill | `src/gate_b_risk.py` `kill_switch_active` | **Do not touch** | Blocks new paper | `tests/test_gate_b_risk.py` `test_kill_switch_env` |
| Paper loop block | `src/signal_paper_runner.py` `_demo_panel_block` | **Do not touch** | `kill_switch_on=true` → `KILL_SWITCH` | `test_n34_kill_switch_blocks_before_adapter_http` |
| Demo operation flag | `src/risk_control_flags.py` `demo_operation_on: False` | **Do not touch / OUT** | Separate flag; kill false does not set it true | `tests/test_risk_control_flags.py` |
| Reject mapping | `src/panel_ops_data.py` `ANCHOR_FIELD_BY_REJECT['KILL_SWITCH']` | **Do not touch** | No button copy here | `tests/test_panel_ops.py` blocked_context |
| Default kill flag | `src/risk_control_flags.py` `kill_switch_on: False` | **Reuse** | Default = brake released | Central render missing-flag case |
| trader-entry/exit/budget/risk/scanner | `src/original.py` | **Do not touch** | MIT loader; no panel | `tests/test_vendor_verify.py` |

## Security / invariants

- `LIVE_TRADING_ENABLED=false`. No Live button.
- `kill_switch_on=true` still BLOCKS new demo orders.
- `kill_switch_on=false` only clears the kill gate. It does **not** turn on `demo_operation_on`.
- PATCH payload stays `{kill_switch_on: true|false}`. Present button id stays `kill-on` (released) or `kill-off` (active).
- Click Liberar when already released is a no-op by design; N38 makes that obvious by hiding the button.
- No secrets, no vendor bump, no real Clear/OANDA HTTP, no invented scoring.
- HTTP 200 / queue / panel-on-air still not a fill.

## Deferred (out of N38)

- `demo_operation_on` copy, rename, or toggle.
- N29.5 live homolog (operator creds).
- Full Central redesign beyond the brake strip.
- Closing ISS-013 (N36 copy shipped; operator close).
