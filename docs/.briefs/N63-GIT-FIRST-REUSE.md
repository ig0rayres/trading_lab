# N63 — Git First reuse (SINAIS-3F frente 1)

> `plan_only` until `/pmo sprint iniciar N63`.

## Capability

Inbox pérola como **sessão principal** da tela Sinais: layout + critérios visíveis + seções secundárias recolhidas.

## Reuse (do not reimplement)

| Component | Path | Decision |
|-----------|------|----------|
| Pearl queue | `src/panel_ops_data.py` `build_preapproval_queue` | **reuse** — N62; no ranking change |
| Pearl section HTML | `src/panel_ops_html.py` `_signals_preapproval_section_html` | **extend** — wrapper hero + critérios |
| Page composition | `src/panel_ops_html.py` `render_signals_page` | **adapt** — order + collapsible secondary |
| Panel shell | `src/panel_ops_html.py` `_wrap_panel_page` | **reuse** — optional subtitle tweak |
| Tests | `tests/test_panel_ops.py` `N62InboxPearlTests`, `N53PanelShellRefreshTests` | **extend** — hierarchy nodeids |
| Criteria text | `docs/REQUIREMENTS.md` Feature 4/9 | **reuse** — excerpt only, no new thresholds |

## Gaps (N63)

- Visual hierarchy: pérola ≠ “mais uma seção” na salada.
- Bloco critérios visível (ISS-019/022).
- Secondary sections below fold / `<details>` / `aria` landmarks.

## Out of scope

- `signal_provider_approvals` semantics (N64).
- Paper copy loop (N65).
- `prodigy_rank` constants.

## Vendor

Pinned `day-trader-skill` via `src/original.py` — **not touched**.