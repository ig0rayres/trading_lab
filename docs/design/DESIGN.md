# Design System & Information Architecture (Retrofit N52)

> Issue: ISS-022
> Escopo: Redesign UX Sinais e Planejamento Visual da Plataforma Operacional

## 1. Tokens Visuais Extraídos & Evoluídos (Lab Ops Aesthetic)

**Princípio:** Clareza > Decoração. Foco em contraste e hierarquia para tomada de decisão (WCAG AA). 
Evitados clichês "purple-AI" ou "cream-terracotta".

### Cores (Variáveis CSS)
| Propósito | Token Proposto | Valor (Light) | Uso |
|-----------|----------------|---------------|-----|
| Fundo principal | `--bg-canvas` | `#F8FAFC` (Slate 50) | Fundo da tela do painel |
| Fundo cartão | `--bg-card` | `#FFFFFF` | Áreas de conteúdo, tabelas |
| Texto primário | `--text-primary` | `#0F172A` (Slate 900) | Títulos, dados principais |
| Texto secundário| `--text-muted` | `#64748B` (Slate 500) | Rótulos de tabela, notas explicativas |
| Borda estrutural| `--border-subtle` | `#E2E8F0` (Slate 200) | Linhas de tabela, divisórias |
| Ação primária | `--action-primary` | `#0369A1` (Sky 700) | Botão Aprovar, ações principais |
| Ação perigo/recusar | `--action-danger` | `#B91C1C` (Red 700) | Botão Rejeitar, Kill switch |
| Badge/Status Neutro | `--status-research`| `#F1F5F9` (Slate 100) / Text: `#475569` | Rótulos 'research_only', 'pending' |
| Badge/Status Ativo | `--status-active` | `#ECFDF5` (Emerald 50) / Text: `#065F46` | 'Em operação', 'Aprovado' |
| Aviso/Warning | `--status-warning`| `#FFFBEB` (Amber 50) / Text: `#92400E` | Faixas de aviso, Freio amarelo |

### Tipografia
- **Font-Family:** Sistema (San Francisco, Inter, Roboto). Legibilidade tabular para números.
- **Sizes:** 
  - `--text-xs`: 12px (Metadados, IDs técnicos)
  - `--text-sm`: 14px (Corpo padrão, tabelas)
  - `--text-base`: 16px (Títulos de cartão)
  - `--text-lg`: 18px (Títulos de página)
- **Weights:** 400 (Corpo), 500 (Rótulos de coluna), 600 (Títulos de página/ações)

### Espaçamentos e Estrutura
- **Gap/Padding Tabela:** 12px (vertical) x 16px (horizontal). Maior "breathing room" que a versão atual.
- **Raio de Borda (Border Radius):** 4px (`--radius-sm`) para inputs/badges, 8px (`--radius-md`) para cartões.

---

## 2. Planejamento de Arquitetura de Informação (Painel de Operações)

O painel deve refletir o `docs/OPERATOR-PANEL-MAP.md` e a hierarquia mental do operador de trading:

### Menu Lateral (Navegação Global)
*   **Central:** Visão geral de saúde, paradas de emergência (kill switch), e links rápidos.
*   **Ordens:** Fila em tempo real (pendentes/abertas) → *Execução atual*.
*   **Histórico:** Ledger de fills confirmados → *Passado imutável*.
*   **Sinais:** Cockpit de decisão (Cópia de terceiros) e Inventário. → *O que está direcionando a conta*.
*   **Estratégias:** Catálogo nativo e fases (Research/Shadow/Paper).
*   **Prodígio:** Descoberta e ranking de candidatos.
*   **Performance:** P&L agregado paper-only.
*   **Análise Google:** Dicas e previsões (research rotulado, sem ordem).

### Hierarquia da Tela Sinais (Decisão vs Operação)

A tela `/sinais` deixa de ser uma salada de auditoria e passa a focar na **Tomada de Decisão** primeiro, e **Monitoramento** depois.

**Nova Estrutura (Top-Down):**

1.  **Fila de Pré-Aprovação (O foco principal da ação)**
    *   *Propósito:* Onde o operador decide o que entra (Gate).
    *   *Conteúdo:* Tabela de candidatos pendentes de qualquer origem (C2, Prodígio).
    *   *Dados Vitais Visíveis:* Assertividade, Fator de Lucro, Retorno Líquido, Drawdown.
    *   *Ação:* Aprovar (Primary) / Rejeitar (Danger).

2.  **Em Operação / Assinados (Inventário)**
    *   *Propósito:* O que está atualmente rodando e tem permissão para postar ordens (paper/live).
    *   *Conteúdo:* Lista de sinais com vínculo direto (Origem + ID) e status da cópia.
    *   *Dados:* Total de fills, P&L bruto.

3.  **Filas de Origem & Auditoria (Pesquisa/Baixa Frequência)**
    *   *Propósito:* Transparência e auditoria de blocos rejeitados ou apenas em research.
    *   *Conteúdo:* C2 (Lista nomeada fechada), Prodígio (Candidatos em pool), Auditoria de Ingresso bruta.

---

## 3. Plano de Implementação (N52)

A sprint N52 focará na reescrita de `src/panel_ops_html.py` para aplicar este design system sem alterar a lógica de backend ou rotas (`panel_ops_data.py`).

1.  **Refatorar CSS base:** Mover estilos inline caóticos para bloco `<style>` usando os tokens definidos acima.
2.  **Redesign `/sinais` (ISS-022):** Implementar o mockup `docs/design/mockups/sinais.md`. Substituir a tabela genérica de "Pré-aprovação" por cards/tabelas com métricas formatadas (`shrunk_win_rate_pct`, `profit_factor_reported`, etc).
3.  **Melhorar Feedback Visual:** Empty states humanizados (ex: "Nenhum provedor pendente de análise na fila" em vez de tabelas vazias feias).
