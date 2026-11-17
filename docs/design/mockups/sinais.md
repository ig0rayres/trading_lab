# Wireframe: Sinais (Cockpit de Decisão)

> **Rota:** `/sinais`
> **Objetivo:** Facilitar a tomada de decisão (aprovar/rejeitar) expondo métricas vitais, e separar claramente o que está operando do que é apenas auditoria.

## Layout Estrutural

```text
+-----------------------------------------------------------------------------------+
| [ Menu Lateral ] |  Sinais (Cópia de Terceiros)                                   |
| - Central        |  Gerencie assinaturas e provedores externos.                   |
| - Ordens         |                                                                |
| - Histórico      |  +----------------------------------------------------------+  |
| - SINAIS (Ativo) |  | [1] Pré-Aprovação de Provedores (Fila de Decisão)        |  |
| - Estratégias    |  |----------------------------------------------------------|  |
| - Prodígio       |  | Candidatos aguardando sua análise. Aprovar libera paper. |  |
| - Performance    |  |                                                          |  |
| - Análise Google |  | Plataforma | Nome (ID) | Métricas Vitais | Ações       |  |
|                  |  |------------|-----------|-----------------|-------------|  |
|                  |  | collective2| Easy Value| Assert: 65.4%   | [Aprovar]   |  |
|                  |  |            | (132169)  | PF: 1.82        | [Rejeitar]  |  |
|                  |  |            |           | DD: -12.4%      |             |  |
|                  |  |            |           | Score: N/D      |             |  |
|                  |  |------------|-----------|-----------------|-------------|  |
|                  |  | prodigy    | ETF Timer | Assert: 100.0%  | [Aprovar]   |  |
|                  |  |            | (304153)  | PF: N/D         | [Rejeitar]  |  |
|                  |  |            |           | Ret: 5812.72    |             |  |
|                  |  |            |           | Score: 95.2     |             |  |
|                  |  +----------------------------------------------------------+  |
|                  |                                                                |
|                  |  +----------------------------------------------------------+  |
|                  |  | [2] Em Operação / Assinados (Inventário)                 |  |
|                  |  |----------------------------------------------------------|  |
|                  |  | Sinais autorizados postando ordens paper.                |  |
|                  |  |                                                          |  |
|                  |  | Origem     | ID do Sinal      | Fills | Resultado Bruto|  |
|                  |  |------------|------------------|-------|----------------|  |
|                  |  | tradingview| 2c3051ec-6e93... | 0     | -              |  |
|                  |  +----------------------------------------------------------+  |
|                  |                                                                |
|                  |  +----------------------------------------------------------+  |
|                  |  | [3] Origens e Auditoria (Research / Fechados)            |  |
|                  |  |----------------------------------------------------------|  |
|                  |  | > Collective2 (Cópia fechada - Nenhum provedor ativo)    |  |
|                  |  | > Pool Prodígio (Research-only)                          |  |
|                  |  | > Critérios de Adoção (Feature 4/9)                      |  |
|                  |  | > Auditoria de Ingresso (Sinais crus recebidos)          |  |
|                  |  +----------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

## Componentes Chave

### 1. Bloco "Métricas Vitais" (Pré-Aprovação)
Em vez de espalhar métricas em 10 colunas que quebram o layout, agrupamos os dados vitais em um bloco de texto estruturado na coluna `Métricas Vitais`:

```html
<div class="metrics-block">
  <span class="metric"><strong>Assertividade:</strong> 65.4%</span>
  <span class="metric"><strong>Fator Lucro:</strong> 1.82</span>
  <span class="metric"><strong>Drawdown Max:</strong> -12.4%</span>
  <span class="metric"><strong>Score:</strong> 85.0</span>
</div>
```
*(Nota: Valores ausentes devem mostrar "N/D" ou "-" para não poluir visualmente com a palavra "indisponível" repetida).*

### 2. Ações (Aprovar / Rejeitar)
- Botão `Aprovar`: Azul escuro (`--action-primary`).
- Botão `Rejeitar`: Vermelho sutil ou outlined (`--action-danger`), para evitar clique acidental.
- Status 'pending' vira um badge visual discreto.

### 3. Empty States Humanizados
- **Fila de Pré-Aprovação Vazia:**
  `<div class="empty-state">Nenhum provedor aguardando análise no momento. Novos candidatos aparecerão aqui.</div>`
- **Inventário Vazio:**
  `<div class="empty-state">Nenhuma cópia de terceiro em operação. Aprove um provedor acima para iniciar.</div>`
