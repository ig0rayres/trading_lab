# Planejamento Visual (Overview do Painel)

> Mapeamento de Arquitetura de Informação para as rotas do Painel Operacional, alinhado com `docs/OPERATOR-PANEL-MAP.md`.

## Estrutura Global (Shell)

O painel segue um layout clássico de dashboard administrativo:
- **Navegação Lateral (Esquerda):** Menu fixo com links para as seções. Largura fixa (~240px). Fundo escuro ou cinza muito claro para contraste.
- **Área de Conteúdo (Direita):** Container fluido para as tabelas e dados. Fundo branco/off-white (`--bg-canvas`).
- **Barra Superior (Opcional/Central):** Status global da plataforma (Semáforo de saúde).

## Mapeamento de Telas (IA)

### 1. `/` (Central)
- **Foco:** Saúde e Controle de Emergência.
- **Visual:** Grande bloco de status (Verde/Amarelo/Vermelho) para a plataforma.
- **Ação Crítica:** Botão de "Freio de Emergência" (Kill Switch) isolado e com alto contraste (Vermelho).

### 2. `/ordens` (Ordens)
- **Foco:** O que está acontecendo *agora*.
- **Visual:** Tabela de alta densidade.
- **Colunas chave:** Ativo, Lado (Buy/Sell), Qtd, Preço, Status (New, Accepted, Pending).
- **Cores:** Badges para status (Verde para Filled, Amarelo para Pending, Vermelho para Canceled/Rejected).

### 3. `/historico` (Histórico)
- **Foco:** O que já aconteceu (Auditoria imutável).
- **Visual:** Tabela similar a `/ordens`, mas focada em fills confirmados e preço de execução.

### 4. `/sinais` (Sinais)
- **Foco:** Cockpit de Decisão (Cópia de Terceiros).
- **Visual:** Dividido em seções claras (Pré-Aprovação no topo, Inventário no meio, Auditoria no fundo).
- *Ver mockup detalhado em `mockups/sinais.md`.*

### 5. `/estrategias` (Estratégias)
- **Foco:** Catálogo nativo e gestão de risco.
- **Visual:** Cards ou tabela mostrando a estratégia e sua *Fase* atual.
- **Cores:** Badges de fase (Cinza para `research`, Amarelo para `shadow`, Azul para `paper_limited`).

### 6. `/prodigio` (Prodígio)
- **Foco:** Descoberta de oportunidades.
- **Visual:** Ranking de candidatos (tabela ordenada por score/assertividade).
- **Ação:** Visualização passiva (pesquisa), dados rotulados como `research_only`.

### 7. `/performance` (Performance)
- **Foco:** P&L Agregado (Paper).
- **Visual:** Resumo numérico (Total P&L, Fator de Lucro) e tabela de posições abertas.

### 8. `/analise-google` (Análise Google)
- **Foco:** Inteligência e previsão (TimesFM).
- **Visual:** Bloco de texto/dicas rotuladas claramente como "Sugestão/Pesquisa" (Aviso visual: "Não gera ordens").
