# Design — Plataforma operacional (ISS-023)

Pacote visual **FULL** que **substitui** o retrofit N52 (`ISS-022`). Objetivo: corrigir o visual “sofrível” pós-N52 e definir o **Refresh de candidatos** antes de qualquer código em `src/`.

## Rastreio

| Item | Valor |
|------|-------|
| Issue | **ISS-023** — `docs/ISSUES.md` |
| Issue relacionada (parcial) | ISS-022 / N52 |
| Fonte de verdade de dados | `docs/OPERATOR-PANEL-MAP.md` |
| Próximo passo PMO | **`/pmo plan N53`** (UI shell + tokens + rotas) |

## Documentos

| Arquivo | Conteúdo |
|---------|----------|
| [DESIGN.md](DESIGN.md) | Tokens v2, componentes, IA global, refresh (produto), WCAG, split N53/N54 |
| [mockups/panel-shell.md](mockups/panel-shell.md) | Shell lateral, topbar, responsivo |
| [mockups/login.md](mockups/login.md) | Entrada operador |
| [mockups/central.md](mockups/central.md) | Freio, semáforo, mercados |
| [mockups/sinais.md](mockups/sinais.md) | Cockpit + **estados do botão Atualizar candidatos** |
| [mockups/ordens.md](mockups/ordens.md) | Ordens paper abertas |
| [mockups/historico.md](mockups/historico.md) | Fills confirmados |
| [mockups/estrategias.md](mockups/estrategias.md) | Catálogo fases |
| [mockups/prodigy.md](mockups/prodigy.md) | Ranking research |
| [mockups/performance.md](mockups/performance.md) | P&L bruto paper |
| [mockups/analise-google.md](mockups/analise-google.md) | TimesFM research |

## Restrições (operador)

- UI em **português**; código/commits em inglês.
- **`LIVE_TRADING_ENABLED=false`** visível no shell.
- **Aprovar** provedor ≠ **fill** na corretora.
- **Refresh** candidatos ≠ envio de ordem; sem chave C2 no browser; fail-closed.
- Métricas: só campos recuperados; ausente = **indisponível** (nunca zero fabricado).
- **WCAG 2.1 AA** mínimo.
- **Zero** alteração em `src/` nesta entrega de design.

## Histórico

- `mockups/panel-overview.md` (N52) — **obsoleto**; use `panel-shell.md`.

## Handoff

1. Revisão operador nos wireframes.
2. **`/pmo plan N53`** — implementação visual + estrutura HTML compartilhada.
3. **`/pmo plan N54`** (ou tarefas N53.x) — API/job refresh + testes, se separado no plano.