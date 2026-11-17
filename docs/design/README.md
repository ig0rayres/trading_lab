# Design Retrofit (N52) - Painel Operacional

Este diretório contém o planejamento visual e de arquitetura de informação para a refatoração da interface do operador, resolvendo os problemas apontados na issue **ISS-022**.

## Documentos Produzidos

1. **[DESIGN.md](DESIGN.md):** Define os tokens visuais (cores, tipografia, espaçamentos) e a arquitetura de informação top-down para o painel, com foco em usabilidade para operações de trading (clareza > decoração).
2. **[mockups/sinais.md](mockups/sinais.md):** Wireframe detalhado para a reestruturação da rota `/sinais`, transformando-a de uma "salada de tabelas" em um verdadeiro cockpit de decisão (Fila de Pré-Aprovação → Inventário → Auditoria).
3. **[mockups/panel-overview.md](mockups/panel-overview.md):** Visão geral da arquitetura de informação para todas as rotas do painel, alinhada com o mapa operacional atual.

## Contexto e Restrições

- **Issue Relacionada:** ISS-022 (`docs/ISSUES.md`).
- **Restrições Aplicadas:**
  - Nenhuma alteração no código Python (`src/`) foi feita nesta etapa de planejamento.
  - O design foca na reutilização dos dados já fornecidos pela API/backend (sem invenção de P&L ou métricas compostas inexistentes).
  - A interface reforça o estado `LIVE_TRADING_ENABLED=false` (foco em paper trading e research).
  - O conceito de "Aprovar" um provedor não foi confundido com "Gerar um Fill" (aprovação apenas autoriza o roteamento paper).

## Próximos Passos (Implementação N52)

O planejamento visual está concluído. O próximo passo é executar o comando `/pmo plan` ou delegar a implementação da sprint N52 para aplicar estas mudanças no arquivo `src/panel_ops_html.py`.

A implementação deve focar em:
1. Extrair os estilos inline para um bloco `<style>` unificado usando os tokens de `DESIGN.md`.
2. Reestruturar o HTML de `render_signals_page` para seguir o layout de `mockups/sinais.md`.
3. Adicionar empty states humanizados e badges de status visuais.
