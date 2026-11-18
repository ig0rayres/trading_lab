# N53.0 Git First — Plataforma visual + refresh honesto (ISS-023)

> Rock PLAN N53 · 2026-11-18 · frente `front/n27-alpaca-loop` · **no vendor bump** · **LIVE false**  
> Plan-time inventory (planner Grok). EXECUTE (N53.0) re-checks `git ls-remote` and records confirmation; do not bump.  
> **Não** usa os identificadores N45–N47.  
> Design DONE em `docs/design/` (DESIGN.md v2, panel-shell, mockups por rota). Sprint **N54** = job refresh POST; **não** roubar escopo N54 aqui.

## Why this sprint

| Candidate | Code-ready? | Decision |
|-----------|-------------|----------|
| Visual “sofrível” pós-N52 | N52 entregou cockpit Sinais + tokens parciais; designer v2 cobre **todas** as rotas | **This sprint** — tokens v2 + PanelShell + HTML/CSS por mockup |
| Botão «Atualizar candidatos» | Ausente no HTML; mockup `sinais.md` R0–R6 definidos | **N53** — botão visível + `GET` autenticado que só relê disco/bundle (**sem** `prodigy_rank.calculate`, sem C2 no browser) |
| Job pesado / POST refresh | Mapa e DESIGN §7 separam N54 | **N54** — POST + job allowlisted + testes de job; N53 pode responder 501 só se GET impossível (prefer GET reload) |
| `panel_ops_data` semantics | Bundle já montado por `build_panel_bundle` | **Do not change meaning** — só apresentação; refresh = nova leitura do mesmo loader |
| N52 cockpit Sinais | Hierarquia e métricas já em `render_signals_page` | **Preserve** — N53 re-skin + refresh CTA; não inverter ordem nem inventar métricas |
| Panel-overview obsoleto | `panel-overview.md` substituído por `panel-shell.md` + rotas | **Use** mockups por rota em `docs/design/mockups/` |

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| GitHub `Jakeschincariol/day-trader-skill` `refs/heads/main` | EXECUTE must re-check; plan-time assumes **matches pin** (same as N52) |
| Local `vendor/day-trader-skill` | Submodule may be uninitialized — do **not** bump from empty folder |

Upstream has no PanelShell, no ISS-023 refresh UX, no full-route mockups. Do not load trader-* except `src/original.py`.

## Reuse inventory

| Capability | Path / function | Decision | Rationale | Tests |
|------------|-----------------|----------|-----------|-------|
| Panel HTML | `src/panel_ops_html.py` `render_*_page`, `_nav`, `_PANEL_CSS` | **extend** | Single module for all operator routes; shared CSS | `tests/test_panel_ops.py` |
| Panel data | `src/panel_ops_data.py` `build_panel_bundle` | **call** — no semantic change | Refresh honest = call bundle builder again | existing N48–N52 tests |
| HTTP router | `src/v4_web_dashboard.py` `GET /api/signals`, auth cookie | **extend** — add `GET /api/signals/reload` (name fixed in EXECUTE) | Auth same as signals; relê bundle | new tests N53.4 |
| Approve/reject | `POST /api/signals/providers` | **keep** | approve ≠ fill | N51 tests |
| Design tokens v2 | `docs/design/DESIGN.md` §2 | **copy_pattern** → `_PANEL_CSS` | Replace N52 token names with v2 (`--color-canvas`, etc.) | CSS var asserts |
| PanelShell | `docs/design/mockups/panel-shell.md` | **copy_pattern** | Sidebar escura, topbar Paper·Live desligado | snippet tests all routes |
| Per-route mockups | `docs/design/mockups/*.md` | **copy_pattern** | Central, Sinais, Ordens, … login | layout snippets |
| Sinais refresh UX | `docs/design/mockups/sinais.md` R0–R3 | **implement UI** in N53; R4 cooldown optional stub | N54 wires job depth | button + aria-live |
| prodigy_rank.calculate | `src/prodigy_rank.py` | **forbidden from panel** | N54 job only | — |
| C2 HTTP from browser | — | **forbidden** | Fail-closed | — |

## Honest refresh contract (N53 vs N54)

| Layer | N53 | N54 |
|-------|-----|-----|
| Botão | Visível, outline, copy do mockup | Mantém; pode habilitar cooldown R4 |
| API | `GET` autenticado: reexecuta `build_panel_bundle` / releitura JSON em disco | `POST` job allowlisted se necessário |
| Scores | **Nunca** calcular no painel | Job server-side com mapa |
| Erro | R3 fail-closed; fila anterior intacta | 503 migration/job |

## Compatibility / license / security

- MIT vendor via `src/original.py` only; no bump without parity tests.
- Never expose C2/Alpaca keys in HTML or browser fetch.
- `LIVE_TRADING_ENABLED=false`. Refresh ≠ approve ≠ fill.
- «Finalizado» only after merge to `main`.

## Plan-time confirmation (2026-11-18)

| Check | Result |
|-------|--------|
| Branch | `front/n27-alpaca-loop` |
| ISS-023 | Design package on disk |
| Steal N45–N47 | **No** |
| LIVE | **false** |