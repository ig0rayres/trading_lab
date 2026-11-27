# Design System — Painel Operacional Trading Lab

> Issue: **ISS-023** (substitui pacote N52 / ISS-022)  
> Modo: **RETROFIT** · Escopo: plataforma inteira (`panel_ops_html`)  
> Engine: Beesy nativo (tokens + wireframes) · Dark mode: **não** (light-only até decisão explícita)  
> `LIVE_TRADING_ENABLED=false` · Aprovar ≠ fill · Refresh ≠ ordem

## 1. Identidade visual

**Estilo:** operacional / laboratório (ops lab) — denso onde há tabela, arejado onde há decisão.  
**Tom:** confiança auditável; pesquisa sempre rotulada; ação destrutiva isolada.  
**Público:** operador único em sessão diária; leitura prolongada de tabelas e números de pesquisa.

**Anti-padrões:** gradientes “AI purple”, cards flutuantes sem hierarquia, métricas sem rótulo `pesquisa`, zeros para campo ausente.

### Referências (conceituais, não URLs inventadas)

| Referência | O que reutilizar |
|-----------|------------------|
| Grafana / ops consoles | sidebar escura, conteúdo claro, badges de saúde |
| Stripe Dashboard (tabelas) | alinhamento tabular, cabeçalhos fixos, empty states curtos |
| WCAG 2.1 AA | contraste 4,5:1 corpo; 3:1 UI; foco visível em todo controle |

---

## 2. Design tokens (v2 — pós-N52)

Substituem tokens N52 no bloco `_PANEL_CSS` (implementação futura). Sem hardcode de hex no HTML por linha — só variáveis.

### 2.1 Cores (light)

| Token | Valor | Uso |
|-------|-------|-----|
| `--color-canvas` | `#F1F5F9` | Fundo área principal |
| `--color-surface` | `#FFFFFF` | Cards, tabelas |
| `--color-sidebar` | `#0F172A` | Nav lateral |
| `--color-sidebar-muted` | `#94A3B8` | Itens inativos no menu |
| `--color-sidebar-active` | `#E2E8F0` | Texto item ativo |
| `--color-sidebar-active-bg` | `#1E293B` | Fundo item ativo |
| `--color-foreground` | `#0F172A` | Títulos, células |
| `--color-muted` | `#64748B` | Subtítulos, hints |
| `--color-border` | `#CBD5E1` | Bordas tabela/card |
| `--color-ring` | `#0284C7` | Focus ring (3px) |
| `--color-primary` | `#0369A1` | CTA primário (aprovar, entrar) |
| `--color-primary-fg` | `#FFFFFF` | Texto em primário |
| `--color-destructive` | `#B91C1C` | Rejeitar, freio |
| `--color-destructive-fg` | `#FFFFFF` | Texto em destrutivo |
| `--color-success-bg` | `#ECFDF5` | Semáforo OK / badge paper |
| `--color-success-fg` | `#065F46` | |
| `--color-warning-bg` | `#FFFBEB` | Aviso research / fila |
| `--color-warning-fg` | `#92400E` | |
| `--color-danger-bg` | `#FEF2F2` | Erro refresh / bloqueio |
| `--color-danger-fg` | `#991B1B` | |
| `--color-research-bg` | `#F8FAFC` | Faixa “somente pesquisa” |
| `--color-research-border` | `#94A3B8` | Borda tracejada research |

**Contraste verificado (AA):** `--color-primary` em `--color-primary-fg`; `--color-foreground` em `--color-surface`; links `--color-primary` em fundo claro.

### 2.2 Tipografia

| Propriedade | Valor |
|-------------|-------|
| UI | `Inter, system-ui, sans-serif` |
| IDs / hashes / JSON | `ui-monospace, SFMono-Regular, Menlo, monospace` |
| Base | `16px` (`--text-base`) |
| Escala | `--text-xs` 12px · `--text-sm` 14px · `--text-lg` 18px · `--text-xl` 20px |
| Peso | 400 corpo · 500 rótulos coluna · 600 título página · 700 freio apenas |

`font-variant-numeric: tabular-nums` em colunas numéricas (Performance, métricas pesquisa).

### 2.3 Espaçamento e radius

| Token | Valor | Uso |
|-------|-------|-----|
| `--space-1` | 4px | Gap ícone-texto |
| `--space-2` | 8px | Padding badge |
| `--space-3` | 12px | Célula tabela compacta |
| `--space-4` | 16px | Padding card |
| `--space-6` | 24px | Entre seções na página |
| `--radius-sm` | 4px | Input, badge |
| `--radius-md` | 8px | Card, botão |
| `--radius-lg` | 12px | Modal login |

### 2.4 Elevação

| Token | Uso |
|-------|-----|
| `--shadow-sm` | `0 1px 2px rgb(15 23 42 / 0.06)` | Card leve |
| `--shadow-md` | `0 4px 12px rgb(15 23 42 / 0.08)` | Dropdown / toast |

---

## 3. Componentes (HTML nativo no painel)

| Componente | Variantes | Regras |
|------------|-----------|--------|
| `PanelShell` | sidebar + topbar contexto | Ver `mockups/panel-shell.md` |
| `PageHeader` | título + subtítulo + slot ações | Uma `h1` por rota |
| `ResearchBanner` | fixo opcional | Texto mapa: *não autoriza ordem* / *não é fill* |
| `DataTable` | zebra off; header sticky | Empty = string real do mapa |
| `MetricCluster` | pré-aprovação | Só chaves recuperadas; ausente = **indisponível** |
| `Badge` | fase estratégia, status ordem, research | Nunca “0” inventado |
| `Button` | primary · outline · destructive · ghost | Refresh = **secondary/outline**, não primário |
| `EmptyState` | ícone opcional + copy do mapa | Sem ilustração pesada |
| `Toast` / `InlineAlert` | success · error · info | Refresh feedback |
| `KillSwitch` | isolated destructive | Só Central |

---

## 4. Arquitetura de informação (alinhada a `OPERATOR-PANEL-MAP.md`)

### 4.1 Ordem mental do operador

```
Controle → Execução agora → Passado → Decisão cópia → Catálogo → Pesquisa → P&L paper
```

### 4.2 Menu lateral (após login)

Ordem fixa no `_nav` (rótulos PT face ao operador):

| # | Rótulo | Rota | Papel |
|---|--------|------|-------|
| 1 | Central | `/` | Freio, semáforo, atalhos |
| 2 | Ordens | `/ordens` | Paper aberto **agora** |
| 3 | Histórico | `/historico` | Fills confirmados |
| 4 | Sinais | `/sinais` | Cockpit cópia + pré-aprovação + refresh |
| 5 | Estratégias | `/estrategias` | Catálogo fases (somente leitura) |
| 6 | Prodígio | `/prodigy` | Rank research |
| 7 | Performance | `/performance` | Grosso paper, custos não verificados |
| 8 | Análise Google | `/analise-google` | TimesFM research |

**Fora do menu (mapa):** Tá Barato, Melhoria contínua — Command Panel v1 apenas; não desenhar no shell v2.

### 4.3 Hierarquia global de página

1. **Topbar contextual** — selo ambiente: `Paper · Live desligado`; hora última renderização do bundle (se exposta).
2. **PageHeader** — título + subtítulo honesto do mapa.
3. **ResearchBanner** (quando a rota exige).
4. **Conteúdo primário** — tabela/card de decisão ou execução.
5. **Conteúdo secundário** — auditoria, critérios, rodapé legal (“fila ≠ fill”).

### 4.4 Rota `/sinais` — IA v0.7 (ISS-024)

**Objetivo da página:** pesquisar e pré-aprovar cópia de terceiros; acompanhar operação e inventário; critérios e auditoria sempre visíveis. Fluxo mental do operador (Feature 9):

```text
Candidatos → Decisão (Aprovar/Rejeitar) → Operação → Inventário
Critérios e Auditoria: referência transversal (não são “passo 5” depois de fill)
```

#### Cinco marcos na página (ordem de scroll — `h2` + `id` estável)

| # | Marco (`h2`) | `id` sugerido | Papel | Fonte API |
|---|--------------|---------------|-------|-----------|
| 1 | **Pré-aprovação** | `sinais-preaprovacao` | Fila de **provedores** candidatos; decisão Aprovar/Rejeitar; CTA refresh | `copy.preapproval.queue[]` |
| 2 | **Em operação / assinados** | `sinais-operacao` | Cópia paper **agora** (ordens abertas + família `signal_copy`); subtítulo *Não é fill.* | `copy.operating`, histórico família |
| 3 | **Inventário** | `sinais-inventario` | **Sinais** rastreados com performance **só após fill**; distinto de “provedor aprovado” | `copy.inventory` |
| 4 | **Critérios de adoção** | `sinais-criterios` | Texto Feature 4 / 9 / 10 (`copy.adoption.criteria_pt`); somente leitura | `copy.adoption` |
| 5 | **Auditoria de ingresso** | `sinais-auditoria` | Trilha origem/destino/motivo; **última** seção; *Não é fill.* | `signals[]` (Feature 9) |

**Sub-regiões dentro de Operação (não são marcos `h2` separados — evita menu longo):**

- **Collective2** — bloco `h3` sob Operação ou logo após Inventário (mapa atual): lista nomeada, `approved_ids`, cópia fechada quando vazio.
- **Candidatos Prodígio (pesquisa)** — bloco `h3` com faixa `ResearchBanner` + badge `Pesquisa — não autoriza ordem`; não confundir com fila de pré-aprovação.

#### Distinção obrigatória (confusão operador)

| Conceito | O que é | Onde aparece | Badge / copy |
|----------|---------|--------------|--------------|
| **Linha na fila de pré-aprovação** | Provedor **candidato** (C2 / Prodígio / TV) aguardando decisão | Seção 1 | `Decisão pendente` · métricas **(pesquisa)** |
| **Provedor aprovado** | Decisão gravada no livro-razão; libera roteamento paper — **≠ fill** | C2 / overlay operação | `Aprovado para paper` (verde suave, token paper) |
| **Linha no inventário** | **Sinal** (`signal_id` / evento) com proveniência ligada; P&L só com fill | Seção 3 | `Inventário · fill confirmado` ou vazio honesto |
| **Pool Prodígio** | Ranking **research_tip**; não promove sozinho | Sub de Operação | `Pesquisa` tracejado |
| **Auditoria** | Evento de **ingresso** (webhook/journal) | Seção 5 | Destino: fila / ordem / barrado |

Callout compacto acima do inventário (sempre visível quando há dado em ≥2 seções):

> **Provedor aprovado** decide quem pode copiar; **inventário** lista sinais com resultado paper — são listas diferentes.

Métricas pré-aprovação: `win_rate_pct`, `shrunk_win_rate_pct`, `profit_factor_reported`, `reported_pnl_sum`, `net_return_pct`, `max_drawdown_pct`, `prodigy_score`/`score`, `status` — rótulo **(pesquisa)**; ausente = **indisponível**.

**PageHeader `/sinais`:** título + subtítulo mapa; topbar shell (N53): selo **`Paper · Live desligado`** (`--color-success-bg` / `--color-success-fg`); sem roxo, sem gradiente “AI”.

**Aprovar / Rejeitar:** coluna **Ações** à direita na tabela pré-aprovação; alvo tátil ≥44×44px; Rejeitar com `--color-destructive` outline, separado ≥8px do Aprovar (primário).

### 4.5 Atualizar candidatos — dois modos honestos (N53 × N54 / ISS-024)

Um único CTA **`Atualizar candidatos`** no cabeçalho da seção **Pré-aprovação** (não primário). O operador precisa entender **o que o servidor fez** — não misturar “job ao vivo” com “só reler disco”.

| Modo | Quando (implementação) | Endpoint (servidor) | O que comunicar na UI |
|------|------------------------|---------------------|------------------------|
| **Releitura disco** | **N53** (entregue) | `GET /api/signals/reload` | Status: `Fonte: bundle em disco · critérios ao vivo não executados` |
| **Critérios ao vivo** | **N54+** (ISS-024) | `POST` job allowlisted (cooldown) | Status: `Fonte: critérios Feature 4 / Prodígio 15d aplicados no servidor (C2 server-side; TV escopo mínimo)` |

Regras de produto (ambos os modos):

| Regra | Detalhe |
|-------|---------|
| O que faz (alvo N54) | Servidor aplica critérios nas fontes C2 (sem browser) e TV (origens já ingeridas — **sem** API de busca TV inventada); regrava JSON de pesquisa; re-monta bundle |
| O que faz hoje (N53) | Só `build_panel_bundle` / releitura em disco — **não** substitui ISS-024; UI não pode insinuar “plataforma consultada” |
| O que não faz | Não aprova; não rejeita; não envia ordem; não promove fase; não inventa score |
| Fail-closed | 503 / erro job / sem chave C2 → `InlineAlert` danger + fila anterior intacta + modo `fail-closed` |
| Browser | **Nunca** chama HTTP Collective2; chave só server-side |
| Pós-sucesso | Toast + carimbo `Atualizado às HH:MM · <fonte>` na linha de status do refresh (`aria-live="polite"`) |

Estados UX canônicos: **idle · running · success · fail-closed** — detalhe visual em `mockups/sinais.md`.

---

## 5. Acessibilidade (WCAG 2.1 AA)

- Foco visível: `outline: 3px solid var(--color-ring)` em links e botões.
- Alvo mínimo 44×44px em Aprovar / Rejeitar / Atualizar candidatos / Entrar.
- Tabelas: `<th scope="col">`; métricas não só por cor (rótulo + valor).
- `aria-live="polite"` na região de feedback do refresh.
- Semáforo: ícone + texto (não só cor).
- Contraste sidebar: texto ativo `#E2E8F0` em `#1E293B`.

---

## 6. Mapa rota → mockup

| Rota | Mockup |
|------|--------|
| Shell | `mockups/panel-shell.md` |
| `/login` | `mockups/login.md` |
| `/` | `mockups/central.md` |
| `/sinais` | `mockups/sinais.md` |
| `/ordens` | `mockups/ordens.md` |
| `/historico` | `mockups/historico.md` |
| `/estrategias` | `mockups/estrategias.md` |
| `/prodigy` | `mockups/prodigy.md` |
| `/performance` | `mockups/performance.md` |
| `/analise-google` | `mockups/analise-google.md` |

---

## 7. Plano de implementação (pós-design)

1. **N53 (sugerido):** `_PANEL_CSS` tokens v2 + `PanelShell` + todas as rotas HTML (sem mudar significado de `panel_ops_data`).
2. **N54 (sugerido):** job POST critérios ao vivo (ISS-024) + cooldown; mesmo CTA em `/sinais` com copy `critérios-ao-vivo`.
3. Paridade: strings vazias e rótulos **idênticos** ao `OPERATOR-PANEL-MAP.md`.
4. Regressão: `tests/test_panel_ops.py` (layout/snippets), sem assert de P&L inventado.

**Não editar nesta fase:** `src/` (design only).