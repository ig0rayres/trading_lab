# Mapa operador — onde está cada coisa no painel

> Sprint **N53** em `main` (PR **#71**, 2026-11-18) — visual v2 · **N54**/**N55**/**N56**/**N57** em `main` (#73–#77) · **N58–N60** frente `sinais-raw-path`: Atualizar varre Collective2 via `SearchStrategies` + histórico fechado por ID + Feature 4 / 15d; falha parcial no histórico → `collective2_closed_trades_partial_failed:*` (fonte Collective2 **não** morre se a listagem passou); botão Atualizar com prazo de espera no browser (~45s); disco = cache; TV varredura **OUT** (ISS-025) · **Atualizar candidatos** → `POST /api/signals/candidates/refresh` (`mode: live_criteria`); releitura = `GET /api/signals/reload` (`mode: disk_reread`) · `LIVE_TRADING_ENABLED=false`  
> Épico histórico do painel único: **ISS-007** (permanece aberto). Orientação: **ISS-016** (mapa existe; chamado de orientação continua registrado).  
> Não confundir semáforo no ar, fila ou HTTP 200 com **fill** na corretora.

## Duas superfícies no mesmo processo

O serviço publicado no EasyPanel (**`trading-lab`**, comando **`v4-ops`**) escuta na porta interna **8765** (HTTPS na frente, conforme `docs/DASHBOARD-OPERATIONS.md` e `EASYPANEL.md`). O **mesmo** processo expõe **dois** modos de HTML:

| Superfície | Nome técnico | Quando o navegador vê |
|------------|--------------|------------------------|
| **Menu do dia a dia** | `panel_ops_html` (`src/panel_ops_html.py`) | Depois de `GET /login`, com cookie de operador (`DASHBOARD_OPERATOR_SESSION` no ambiente do container). `GET /` vira **Central** com menu lateral. |
| **Command Panel v1** (página única) | `render_page` (`src/v4_web_dashboard.py`) | `GET /` **somente** quando a variável de sessão de operador **não** está definida (modo bearer/HTML legado). Com sessão de operador ligada, esta página **não** aparece em `/` — o menu da Central toma o lugar. |

Rotas do menu (após login): **`/`** (Central), **`/sinais`**, **`/estrategias`**, **`/analise-google`**, **`/ordens`**, **`/historico`**, **`/prodigy`**, **`/performance`**. Ainda não há item de menu para Tá Barato nem melhoria contínua (eventos de evolução).

JSON de monitoramento (Bearer, como antes): **`GET /api/status`** — inclui `command_panel`, `platform_health` e chaves citadas abaixo, **independente** de qual superfície HTML você usaria.

### Selos usados neste mapa

| Selo | Significado |
|------|-------------|
| **VISÍVEL** | Área com tela ou seção HTML que o operador consegue ver no fluxo indicado. |
| **VAZIO-COMUM** | Tela existe, mas o texto vazio padrão do código aparece até haver dado. |
| **NÃO-EXISTE-AINDA** | Área ainda sem rota ou seção no menu do dia a dia; no máximo contadores na página única ou API. |
| **SÓ-API-OU-JSONL** | Dado só em `GET /api/status`, ficheiros `*.jsonl` ou relatório diário — sem secção HTML no menu do dia a dia. |

---

## 1. Central (freio, semáforo, mercados, limites)

| Campo | Detalhe |
|-------|---------|
| **Onde clicar** | Menu lateral → **Central**, ou `GET /` após login. |
| **Superfície** | **Menu do dia a dia** (`render_central_page`) com **PanelShell v2** (sidebar escura, topbar `Paper · Live desligado`, tokens `docs/design/DESIGN.md`). No Command Panel v1 há semáforo e cartões de contagem, mas **sem** a faixa de freio da Central. |
| **Fonte de dados** | `build_panel_bundle` / `panel_ops_data` + bloco de saúde (`platform_health`); âncoras e flags via APIs de painel. |
| **Com dado** | Faixa do freio (Ativar/Liberar conforme estado), tabela de mercados/âncoras, bloco de saúde da plataforma, trecho de sinais recentes na página. |
| **Vazio (texto real no código)** | Semáforo: `Aguardando primeira checagem automática (v4-ops)` · Sinais na Central: `Sem sinais recentes` |
| **Selo** | **VISÍVEL** no menu do dia a dia |

---

## 2. Sinais

| Campo | Detalhe |
|-------|---------|
| **Onde clicar** | Menu → **Sinais**, ou `GET /sinais`. API: `GET /api/signals` — mantém `signals[]` (Feature 9) e acrescenta objeto `copy`. Linha muted **Versão do painel** (`APP_GIT_SHA` do build; `unknown` sem arg). **`GET /healthz`** e **`GET /api/status`** expõem `app_git_sha` + `upstream_commit` (pin do vendor). **Atualizar candidatos** (**N54**–**N61** / ISS-024): botão dispara **`POST /api/signals/candidates/refresh`** (sessão obrigatória) — aplica critérios Feature 4 / Prodígio 15d **no servidor**; o browser cancela a espera após ~45s (mensagem honesta, fila anterior mantida). **Collective2 (**N58**/**N59**/**N60**):** com chave no ambiente, GET `/Strategies/SearchStrategies` lista IDs na plataforma, busca histórico fechado **por ID** (`GetStrategyHistoricalClosedTrades`, sem chamada em lote com a página inteira), persiste o parcial em `{root}/providers/raw`, filtra com `prodigy_rank.calculate` — **sem** allowlist para aparecer; falha de um ID ou corte por tempo do job → `collective2_closed_trades_partial_failed:*` e `status: partial`, **sem** `collective2_refresh_failed` se a listagem passou; instantâneo de ordens ativas (**N59**) só para IDs da **lista nomeada de cópia paper** (diagnóstico N50, **não** elegibilidade Feature 4) — falha vira `collective2_active_orders_snapshot_failed:*` e **não** derruba a fonte `collective2` nem a fila da varredura; ID elegível pode surgir **sem** arquivo bruto prévio; glob `{root}/providers/raw/*_closed_trades.json` (**N57**) é **cache** complementar, **não** a história do botão; **sem** `SearchHistoricalStrategies` / `GetLeaderBoard` como filtro. **Prodígio:** `calculate` no volume canônico (`{root}/providers/raw`, `--root /app/reports`). **TradingView:** **sem varredura** de marketplace (**ISS-025**) — só origens já ingeridas; aviso honesto no refresh. Fila Prodígio pós-refresh: só `PRODIGY_CANDIDATE_RESEARCH`; `closed_trades_15d=0` / `UNSCORABLE` fora da fila Prodígio. Resposta `mode: live_criteria`, `orders_sent: 0`, `execution_authorized: false`; cooldown 429 `REFRESH_COOLDOWN`; sem chave C2 → `partial` + `issues` (ex. `C2_API4_KEY_missing`) + demais plataformas preservadas; último refresh em `copy.candidates_refresh` (`intelligence/candidates-refresh-latest.json`); ao lado do aviso (**N61**): `refreshed_at` + `sources_ok` (mesmo sem erros); falha da listagem → `collective2_refresh_failed:…:{código HTTP}` quando existir; aviso velho de listagem some no início do POST; **uma** repetição imediata só em HTTP 429/5xx (403/414 não repetem); botão **AbortController** ~45s (N60). Fila pós-refresh: Collective2 elegível/pendente + Prodígio elegível + TradingView (origens ingeridas). **Lista nomeada** / env / livro-razão = portão da **cópia paper** (`approved_for_paper_copy`), **não** visibilidade na pré-aprovação. **Releitura em disco** (N53): **`GET /api/signals/reload`** — `mode: disk_reread`; **sem** varredura. Atualizar **≠** Aprovar/Rejeitar **≠** fill. Live desligado. |
| **Superfície** | **Menu do dia a dia** — mesma rota `/sinais` (**N48–N53**); cockpit (**N52** / ISS-022) + shell visual (**N53** / ISS-023): **Pré-aprovação** (métricas de pesquisa completas + botão refresh) → **Em operação / assinados** → inventário → **Collective2** → pool Prodígio → critérios → **auditoria** por último. Desenho: `docs/design/mockups/sinais.md`. **Não** é página separada no Command Panel v1. |
| **Selo** | **VISÍVEL** |

### Inbox pérola — pré-aprovação (**N51** / **N62** / ISS-021)

| Campo | Detalhe |
|-------|---------|
| **Ação** | Logado: botões **Aprovar** / **Rejeitar** por linha. API: `POST /api/signals/providers` corpo `{platform, provider_id, action: approve\|reject}` — **401** sem sessão; **503** sem livro-razão / migration `003`. |
| **Fila** | `copy.preapproval.queue[]` (**N62**): até **10** linhas `platform: prodigy` — candidatos pérola com `reported_pnl_sum` > 0 na janela 15d; sem Collective2 pendente nem TradingView nesta fila. Bloco de métricas (**N52**): `win_rate_pct`, `shrunk_win_rate_pct`, `profit_factor_reported`, `reported_pnl_sum`, `net_return_pct`, `max_drawdown_pct`, `prodigy_score`/`score`, `status` — cada um rotulado pesquisa; ausente = **indisponível** (nunca zero inventado). |
| **Persistência** | Tabela `signal_provider_approvals` (migration `003`). Rejeição no painel vence `config/c2_paper_copy_allowlist.json` / `C2_PAPER_COPY_APPROVED_IDS`. JSON/env são semente quando não há linha no livro-razão. |
| **Não faz** | Não envia ordem; não chama Alpaca/C2; Live desligado. |

### Em operação / assinados (**N50** título; conteúdo N48/N49)

| Campo | Detalhe |
|-------|---------|
| **Subtítulo (sempre)** | `Cópia de terceiros (TradingView / provedores). Não é fill.` |
| **Fonte de dados** | Pacote `copy` em `build_panel_bundle`: ordens abertas e histórico com `strategy_key=signal_copy`; JOIN ledger `paper_orders` → `risk_decisions` → `signal_events` para **origem**; overlay honesto de `signal_id` via `paper/signal-orders.jsonl` (`client_order_id`); performance agregada da família; cópias Prodígio só pesquisa (`research_copies`); estado Collective2. |
| **Com dado** | Tabela «em operação» com colunas **Origem** e **Sinal**; histórico da família de cópia; totais **brutos** por `strategy_key` com rótulo `gross_unverified_costs`. **Sem** engenharia reversa do hash de idempotência. |
| **Vínculo ausente** | `origem desconhecida` e `sem vínculo com sinal` — não inventar P&L por sinal. |
| **Vazio — operação** | `Nenhuma cópia de terceiro em operação.` |
| **Vazio — performance nesta cópia** | `Sem fills confirmados nesta cópia.` |
| **Collective2** | IDs efetivos = decisão `approved` no livro-razão ∪ semente (JSON/env) quando não há linha; rejeição exclui mesmo na semente. Vazio: `Collective2: cópia paper fechada — nenhum provedor na lista nomeada.` Candidatos de pesquisa **não** viram aprovação sozinhos; use a fila de pré-aprovação. Instantâneo **não** é ticket. Painel **não** chama API C2. |
| **Selo** | **VISÍVEL** · vazio honesto = **VAZIO-COMUM** |

### Inventário de sinais (**N49**)

| Campo | Detalhe |
|-------|---------|
| **Fonte** | `copy.inventory` — chave por origem + `signal_id` / `signal_event_id` quando `provenance_status=linked`. |
| **Performance por sinal** | Somente **fill confirmado**; rótulo `gross_unverified_costs`; fila / `queued_intent` **não** entra. |
| **Vazio** | `Nenhum sinal neste inventário.` |

### Critérios de adoção (**N49**)

| Campo | Detalhe |
|-------|---------|
| **Texto** | Reuso **Feature 4 / 9 / 10** (`copy.adoption.criteria_pt`): cópia de terceiros; Prodígio janela 15 dias, ≥5 operações em ≥3 dias, R$ 20 paper inicial, fases, Collective2 lista nomeada (vazio = fechado), sem promoção automática, Live desligado. |
| **Fases** | Catálogo `signal_copy` / `prodigy_15d` somente leitura (mesmo bloco que Estratégias). |

### Collective2 — marketplace (**N50**)

| Campo | Detalhe |
|-------|---------|
| **Objeto API** | `copy.collective2`: `approved_ids`, `approved_for_paper_copy`, `status`, `subscribed`, `candidates` (pesquisa), `active_orders_snapshot` opcional (não-ticket). |
| **Config** | `config/c2_paper_copy_allowlist.json` commitado; operador pode somar IDs via `C2_PAPER_COPY_APPROVED_IDS`. Controla **cópia paper** (`approved_ids`, `approved_for_paper_copy`) — **não** esconde candidatos Collective2 na pré-aprovação quando os arquivos brutos canônicos já existem (**N57**). |
| **H10** | Dez candidatos históricos **não** entram sozinhos na lista. |

### Candidatos Prodígio (pesquisa) (**N49** + **N50** título)

| Campo | Detalhe |
|-------|---------|
| **Fonte** | `copy.prodigy_pool` via `_load_prodigy_opportunities` (`intelligence/prodigy-top10-latest.json`) — **research_tip**; não chama `prodigy_rank.calculate`. Coluna **Provedor** = `provider` ou `provider_id` do JSON gravado. |
| **Vazio** | `Nenhum candidato de pesquisa no pool.` |
| **Rótulo** | `Pesquisa — não autoriza ordem / não promove.` |

### Auditoria de ingresso (seção inferior)

| Campo | Detalhe |
|-------|---------|
| **Subtítulo (sempre)** | `Auditoria de ingresso — origem, destino e motivo. Não é fill.` |
| **Fonte de dados** | Ledger `signal_events` ou, em fallback, `webhooks/journal.jsonl` (`load_panel_signals`). |
| **Com dado** | Tabela hora, origem, ativo, mercado, destino (fila / ordem / bloqueado), motivo quando bloqueado. |
| **Vazio** | `Nenhum sinal neste destino.` |
| **Selo** | **VISÍVEL** · vazio honesto = **VAZIO-COMUM** |

---

## 3. Estratégias (catálogo de fases)

| Campo | Detalhe |
|-------|---------|
| **Onde clicar** | Menu → **Estratégias**, ou `GET /estrategias`. API: `GET /api/estrategias` (sessão de operador, como `/api/signals`). |
| **Superfície** | **Menu do dia a dia** — `render_strategies_page` (`src/panel_ops_html.py`). Command Panel v1 mantém a tabela «Estratégias (catálogo)» na página única legada. |
| **Fonte de dados** | `build_panel_bundle` → `strategy_catalog` via `list_strategy_states` (`src/panel_ops_data.py`); catálogo persistido em `strategy_states` quando o ledger responde. |
| **Com dado** | Tabela com chave, fase (pesquisa / sombra / paper) e paper permitido (sim/não). |
| **Vazio** | `Catálogo indisponível (ledger)` (tabela inteira; ledger ausente ou lista vazia). |
| **Promoção de fase** | **Nenhum** controle na tela nova — rodapé: «Promoção de fase: somente operador (fora deste menu).» O `PATCH /api/strategies/{key}` existente **não** é exposto nesta página. |
| **Selo** | **VISÍVEL** no menu do dia a dia · vazio honesto = **VAZIO-COMUM** · tabela no Command Panel v1 = **VISÍVEL** só nessa superfície |

---

## 4. Prodígio

| Campo | Detalhe |
|-------|---------|
| **Onde clicar** | Menu → **Prodígio**, ou `GET /prodigy`. |
| **Superfície** | Menu do dia a dia **e** tabela «Oportunidades Prodígio» no Command Panel v1 (mesma família de dados, HTML diferente). |
| **Fonte de dados** | Ranking / oportunidades de pesquisa (`prodigy-rank`, relatórios); cópias em `prodigy_copied_signals` / ledger conforme `panel_ops_data`. |
| **Com dado** | Linhas de rank e tabela de cópias registradas. |
| **Vazio** | Rank: `Execute prodigy-rank (research)` · Cópias: `Nenhuma cópia registrada` (menu). No v1: `Execute prodigy-rank ou aguarde relatório` |
| **Selo** | **VISÍVEL** · rank vazio = **VAZIO-COMUM** até correr `prodigy-rank` (research) |

---

## 5. Performance

| Campo | Detalhe |
|-------|---------|
| **Onde clicar** | Menu → **Performance**, ou `GET /performance`. API: `GET /api/performance`. |
| **Superfície** | Menu do dia a dia; no Command Panel v1 aparecem cartões (P&L bruto, contagens) — **não** substitui a página do menu. |
| **Fonte de dados** | `performance_from_ledger` e/ou `performance_from_snapshots` (`paper/order-snapshots.jsonl`); só **fills confirmados** entram no grosso rotulado. |
| **Com dado** | Total bruto e linhas por operação/snapshot. |
| **Vazio** | Total: `Indisponível` · Tabela: `Sem fills confirmados` |
| **Selo** | **VISÍVEL** (métrica **bruta**, custos não verificados — ver rótulo no código) |

---

## 6. Ordens abertas Alpaca paper

| Campo | Detalhe |
|-------|---------|
| **Onde clicar** | Menu → **Ordens**, ou `GET /ordens`. API: `GET /api/orders` (sessão de operador, como `/api/signals`). |
| **Superfície** | **Menu do dia a dia** — `render_orders_page` (`src/panel_ops_html.py`). Command Panel v1 mantém cartões **«Ordens monitoradas»** e **«Posições ainda abertas»** (contadores na página única legada). |
| **Fonte de dados** | `build_panel_bundle` → lista `open_orders` (`src/panel_ops_data.py`): snapshots `paper/order-snapshots.jsonl` e, se houver DSN, linhas do ledger — **sem** poll HTTP Alpaca pelo painel; **sem** POST de ordem pelo painel. |
| **Com dado** | Tabela com ID cliente, ativo, lado, status, corretora, quantidade restante, estratégia. |
| **Vazio** | `Nenhuma ordem aberta no paper.` |
| **Selo** | **VISÍVEL** no menu do dia a dia · vazio honesto = **VAZIO-COMUM** · contadores no Command Panel v1 = **VISÍVEL** só nessa superfície |

---

## 7. Histórico / fills

| Campo | Detalhe |
|-------|---------|
| **Onde clicar** | Menu → **Histórico**, ou `GET /historico`. API: `GET /api/history` (sessão de operador). |
| **Superfície** | **Menu do dia a dia** — `render_history_page` (`src/panel_ops_html.py`). Command Panel v1: cartão **«Ordens encerradas com resultado bruto»**; JSON `command_panel.history` e `financial_health.paper_fills_recorded`. |
| **Fonte de dados** | `build_panel_bundle` → lista `order_history` (mesma regra de fill que Performance): snapshots + ledger; fila / `queued_intent` **não** entra como fill. |
| **Com dado** | Tabela com ID cliente, ativo, lado, resultado bruto rotulado, estratégia. |
| **Vazio** | `Nenhum fill confirmado no histórico.` (rodapé da página: fila e HTTP 200 não entram.) |
| **Selo** | **VISÍVEL** no menu do dia a dia · vazio honesto = **VAZIO-COMUM** |

---

## 8. Tá Barato (sombra / homologação)

| Campo | Detalhe |
|-------|---------|
| **Onde clicar** | **Não** está no `_nav` do menu. Secção **«Tá Barato — sombra / homolog»** só no Command Panel v1 (`render_page`). |
| **Superfície** | **Command Panel v1** apenas. Homologação shadow→paper continua fora do painel (**G-FORM / N17.2** operador). |
| **Fonte de dados** | `ta_barato_shadow` via `trading_dashboard_data._load_ta_barato_shadow` e ciclo `v4-cycle` com `--opportunity-input`. |
| **Com dado** | Tabela de oportunidades sombra no HTML v1. |
| **Vazio** | `Execute v4-cycle com --opportunity-input ou aguarde relatório` |
| **Selo** | **VISÍVEL** só no Command Panel v1 · no menu do dia a dia = **NÃO-EXISTE-AINDA** |

---

## 9. TimesFM / Google (pesquisa)

| Campo | Detalhe |
|-------|---------|
| **Onde clicar** | Menu → **Análise Google**, ou `GET /analise-google`. API: `GET /api/analise-google` (sessão de operador, como `/api/signals`). |
| **Superfície** | **Menu do dia a dia** — `render_analise_google_page` (`src/panel_ops_html.py`). Relatório diário e `timesfm_context` continuam research-only; **não** há secção equivalente no Command Panel v1. |
| **Fonte de dados** | `load_panel_timesfm` em `build_panel_bundle` (`src/panel_ops_data.py`): último `evolution/daily/*.json` com bloco `timesfm`, ou `build_timesfm_block` (adaptador opcional). |
| **Com dado** | Tabela de dicas com rótulos `dica de pesquisa` / `sugestão`; subtítulo `Dica de pesquisa — não autoriza ordem. Live desligado.`; rodapé `Esta análise é só pesquisa. Não autoriza ordem.` |
| **Vazio** | Indisponível: `Análise Google indisponível: modelo ou dependência ausente.` + linha `Motivo: …` · Relatório OK sem linhas: `Nenhuma dica de pesquisa neste relatório.` |
| **Envio de ordem** | **Nenhum** — pesquisa **não** autoriza ordem; JSON expõe `execution_authorized=false`. |
| **Selo** | **VISÍVEL** no menu do dia a dia · modelo/relatório ausente = **VAZIO-COMUM** (fail-closed com motivo) |

---

## 10. Melhoria contínua (evolução)

| Campo | Detalhe |
|-------|---------|
| **Onde clicar** | **Não** está no menu do dia a dia. No Command Panel v1: secção **Melhoria contínua** (catálogo de fases está na área **3** e no v1). |
| **Superfície** | **Command Panel v1**; também chaves em `GET /api/status` (`continuous_improvement`; `strategy_catalog` espelha área 3). |
| **Fonte de dados** | `evolution/decisions.jsonl` para eventos de melhoria contínua — **não** misturado com a tela **Estratégias** do menu. |
| **Com dado** | Lista de eventos de evolução no HTML v1. |
| **Vazio** | `Nenhum evento em evolution/decisions.jsonl` |
| **Selo** | **VISÍVEL** só no Command Panel v1 · menu do dia a dia = **NÃO-EXISTE-AINDA** · JSON = **SÓ-API-OU-JSONL** |

---

## Como ver o Command Panel v1 hoje

No deploy típico com **sessão de operador** configurada (dia a dia EasyPanel), após login você **não** vê `render_page` em `/`. Para inspecionar a página única legada, é preciso o modo **sem** `DASHBOARD_OPERATOR_SESSION` (bearer/HTML) — **não** é o fluxo padrão pós-N18. Em qualquer modo, **`GET /api/status`** continua a espelhar o conteúdo agregado do Command Panel.

## Fora deste mapa (decisão de sprint)

- **Ordens** e **Histórico** no menu — entregue em **N41** / **ISS-017** onda 1; **Estratégias** (`/estrategias`) — entregue em **N42** / **ISS-017** onda 2; **Análise Google** (`/analise-google`) — entregue em **N43** / **ISS-017** onda 3 (só pesquisa); **N44** — roteiro de homologação US+cripto pelo menu (`docs/HOMOLOGATION.md` § Sprint N44, áreas **5–7** + Sinais + Performance); folha `docs/TEST-EVIDENCE.md` § Sprint N44; **N48** — tela **Sinais** com **cópia de terceiros** + **auditoria de ingresso** na mesma rota (`ISS-018`; mapa §2); campanha continua em `docs/.briefs/CAMPAIGN-PLATFORM-DELIVERY.brief.md`.
- Rebuild da imagem EasyPanel, **passeio N44** na corretora paper, credenciais demo (**ISS-010** / N29.5), homologação Tá Barato — **operador**.
- Dinheiro real: permanece **desligado**.

## Referências honestas

- Inventário Git First: `docs/.briefs/N40-GIT-FIRST-REUSE.md`
- Folha do dia a dia: `docs/DASHBOARD-OPERATIONS.md`
- Promessa MVP-OP (épico): `docs/ISSUES.md` — **ISS-007** (não fechado por este mapa)