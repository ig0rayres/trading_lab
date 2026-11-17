# Mapa operador — onde está cada coisa no painel

> Sprint **N41** (2026-11-17) · somente leitura · `LIVE_TRADING_ENABLED=false` · mapa base **N40** / **ISS-016**  
> Épico histórico do painel único: **ISS-007** (permanece aberto). Orientação: **ISS-016** (mapa existe; chamado de orientação continua registrado).  
> Não confundir semáforo no ar, fila ou HTTP 200 com **fill** na corretora.

## Duas superfícies no mesmo processo

O serviço publicado no EasyPanel (**`trading-lab`**, comando **`v4-ops`**) escuta na porta interna **8765** (HTTPS na frente, conforme `docs/DASHBOARD-OPERATIONS.md` e `EASYPANEL.md`). O **mesmo** processo expõe **dois** modos de HTML:

| Superfície | Nome técnico | Quando o navegador vê |
|------------|--------------|------------------------|
| **Menu do dia a dia** | `panel_ops_html` (`src/panel_ops_html.py`) | Depois de `GET /login`, com cookie de operador (`DASHBOARD_OPERATOR_SESSION` no ambiente do container). `GET /` vira **Central** com menu lateral. |
| **Command Panel v1** (página única) | `render_page` (`src/v4_web_dashboard.py`) | `GET /` **somente** quando a variável de sessão de operador **não** está definida (modo bearer/HTML legado). Com sessão de operador ligada, esta página **não** aparece em `/` — o menu da Central toma o lugar. |

Rotas do menu (após login): **`/`** (Central), **`/sinais`**, **`/prodigy`**, **`/performance`**, **`/ordens`**, **`/historico`**. Ainda não há item de menu para Tá Barato, catálogo de fases nem melhoria contínua.

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
| **Superfície** | **Menu do dia a dia** (`render_central_page`). No Command Panel v1 há semáforo e cartões de contagem, mas **sem** a faixa de freio da Central. |
| **Fonte de dados** | `build_panel_bundle` / `panel_ops_data` + bloco de saúde (`platform_health`); âncoras e flags via APIs de painel. |
| **Com dado** | Faixa do freio (Ativar/Liberar conforme estado), tabela de mercados/âncoras, bloco de saúde da plataforma, trecho de sinais recentes na página. |
| **Vazio (texto real no código)** | Semáforo: `Aguardando primeira checagem automática (v4-ops)` · Sinais na Central: `Sem sinais recentes` |
| **Selo** | **VISÍVEL** no menu do dia a dia |

---

## 2. Sinais

| Campo | Detalhe |
|-------|---------|
| **Onde clicar** | Menu → **Sinais**, ou `GET /sinais`. API: `GET /api/signals`. |
| **Superfície** | **Menu do dia a dia** — **não** é página separada no Command Panel v1. |
| **Fonte de dados** | Ledger `signal_events` ou, em fallback, `webhooks/journal.jsonl` (`load_panel_signals`). |
| **Com dado** | Tabela por destino (fila, ordem, bloqueado) com motivo de bloqueio quando aplicável. |
| **Vazio** | `Nenhum sinal neste destino.` |
| **Selo** | **VISÍVEL** |

---

## 3. Prodígio

| Campo | Detalhe |
|-------|---------|
| **Onde clicar** | Menu → **Prodígio**, ou `GET /prodigy`. |
| **Superfície** | Menu do dia a dia **e** tabela «Oportunidades Prodígio» no Command Panel v1 (mesma família de dados, HTML diferente). |
| **Fonte de dados** | Ranking / oportunidades de pesquisa (`prodigy-rank`, relatórios); cópias em `prodigy_copied_signals` / ledger conforme `panel_ops_data`. |
| **Com dado** | Linhas de rank e tabela de cópias registradas. |
| **Vazio** | Rank: `Execute prodigy-rank (research)` · Cópias: `Nenhuma cópia registrada` (menu). No v1: `Execute prodigy-rank ou aguarde relatório` |
| **Selo** | **VISÍVEL** · rank vazio = **VAZIO-COMUM** até correr `prodigy-rank` (research) |

---

## 4. Performance

| Campo | Detalhe |
|-------|---------|
| **Onde clicar** | Menu → **Performance**, ou `GET /performance`. API: `GET /api/performance`. |
| **Superfície** | Menu do dia a dia; no Command Panel v1 aparecem cartões (P&L bruto, contagens) — **não** substitui a página do menu. |
| **Fonte de dados** | `performance_from_ledger` e/ou `performance_from_snapshots` (`paper/order-snapshots.jsonl`); só **fills confirmados** entram no grosso rotulado. |
| **Com dado** | Total bruto e linhas por operação/snapshot. |
| **Vazio** | Total: `Indisponível` · Tabela: `Sem fills confirmados` |
| **Selo** | **VISÍVEL** (métrica **bruta**, custos não verificados — ver rótulo no código) |

---

## 5. Ordens abertas Alpaca paper

| Campo | Detalhe |
|-------|---------|
| **Onde clicar** | Menu → **Ordens**, ou `GET /ordens`. API: `GET /api/orders` (sessão de operador, como `/api/signals`). |
| **Superfície** | **Menu do dia a dia** — `render_orders_page` (`src/panel_ops_html.py`). Command Panel v1 mantém cartões **«Ordens monitoradas»** e **«Posições ainda abertas»** (contadores na página única legada). |
| **Fonte de dados** | `build_panel_bundle` → lista `open_orders` (`src/panel_ops_data.py`): snapshots `paper/order-snapshots.jsonl` e, se houver DSN, linhas do ledger — **sem** poll HTTP Alpaca pelo painel; **sem** POST de ordem pelo painel. |
| **Com dado** | Tabela com ID cliente, ativo, lado, status, corretora, quantidade restante, estratégia. |
| **Vazio** | `Nenhuma ordem aberta no paper.` |
| **Selo** | **VISÍVEL** no menu do dia a dia · vazio honesto = **VAZIO-COMUM** · contadores no Command Panel v1 = **VISÍVEL** só nessa superfície |

---

## 6. Histórico / fills

| Campo | Detalhe |
|-------|---------|
| **Onde clicar** | Menu → **Histórico**, ou `GET /historico`. API: `GET /api/history` (sessão de operador). |
| **Superfície** | **Menu do dia a dia** — `render_history_page` (`src/panel_ops_html.py`). Command Panel v1: cartão **«Ordens encerradas com resultado bruto»**; JSON `command_panel.history` e `financial_health.paper_fills_recorded`. |
| **Fonte de dados** | `build_panel_bundle` → lista `order_history` (mesma regra de fill que Performance): snapshots + ledger; fila / `queued_intent` **não** entra como fill. |
| **Com dado** | Tabela com ID cliente, ativo, lado, resultado bruto rotulado, estratégia. |
| **Vazio** | `Nenhum fill confirmado no histórico.` (rodapé da página: fila e HTTP 200 não entram.) |
| **Selo** | **VISÍVEL** no menu do dia a dia · vazio honesto = **VAZIO-COMUM** |

---

## 7. Tá Barato (sombra / homologação)

| Campo | Detalhe |
|-------|---------|
| **Onde clicar** | **Não** está no `_nav` do menu. Secção **«Tá Barato — sombra / homolog»** só no Command Panel v1 (`render_page`). |
| **Superfície** | **Command Panel v1** apenas. Homologação shadow→paper continua fora do painel (**G-FORM / N17.2** operador). |
| **Fonte de dados** | `ta_barato_shadow` via `trading_dashboard_data._load_ta_barato_shadow` e ciclo `v4-cycle` com `--opportunity-input`. |
| **Com dado** | Tabela de oportunidades sombra no HTML v1. |
| **Vazio** | `Execute v4-cycle com --opportunity-input ou aguarde relatório` |
| **Selo** | **VISÍVEL** só no Command Panel v1 · no menu do dia a dia = **NÃO-EXISTE-AINDA** |

---

## 8. TimesFM / Google (pesquisa)

| Campo | Detalhe |
|-------|---------|
| **Onde clicar** | **Sem** secção HTML em qualquer superfície (`timesfm_context.py` — research-only). |
| **Superfície** | Nenhuma página; contexto entra no relatório diário de evolução, não autoriza ordem. |
| **Fonte de dados** | `src/timesfm_context.py`, `evolution_engine` (relatório diário); estado típico `timesfm_status: UNAVAILABLE` até dependência opcional existir. |
| **Com dado** | Campos no relatório/JSON de evolução, não no menu. |
| **Vazio** | UNAVAILABLE / ausência de bloco no HTML. |
| **Selo** | **SÓ-API-OU-JSONL** (pesquisa; **não** é sinal de trading) |

---

## 9. Melhoria contínua / catálogo de fases

| Campo | Detalhe |
|-------|---------|
| **Onde clicar** | **Não** está no menu. No Command Panel v1: **`h2` Estratégias (catálogo)** + secção **Melhoria contínua**. |
| **Superfície** | **Command Panel v1**; também chaves em `GET /api/status` (`strategy_catalog`, `continuous_improvement`). Promoção de fase = operador fora do painel. |
| **Fonte de dados** | Ledger / catálogo de estratégias; `evolution/decisions.jsonl` para eventos de melhoria contínua. |
| **Com dado** | Tabela chave / fase / paper permitido; lista de eventos de evolução. |
| **Vazio** | Catálogo: `Catálogo indisponível (ledger)` · Melhoria: `Nenhum evento em evolution/decisions.jsonl` |
| **Selo** | **VISÍVEL** no Command Panel v1 · menu = **NÃO-EXISTE-AINDA** · JSON = **SÓ-API-OU-JSONL** |

---

## Como ver o Command Panel v1 hoje

No deploy típico com **sessão de operador** configurada (dia a dia EasyPanel), após login você **não** vê `render_page` em `/`. Para inspecionar a página única legada, é preciso o modo **sem** `DASHBOARD_OPERATOR_SESSION` (bearer/HTML) — **não** é o fluxo padrão pós-N18. Em qualquer modo, **`GET /api/status`** continua a espelhar o conteúdo agregado do Command Panel.

## Fora deste mapa (decisão de sprint)

- **Ordens** e **Histórico** no menu — entregue em **N41** / **ISS-017** onda 1; campanha continua em `docs/.briefs/CAMPAIGN-PLATFORM-DELIVERY.brief.md`.
- Rebuild da imagem EasyPanel, credenciais demo (**ISS-010** / N29.5), homologação Tá Barato — **operador**.
- Dinheiro real: permanece **desligado**.

## Referências honestas

- Inventário Git First: `docs/.briefs/N40-GIT-FIRST-REUSE.md`
- Folha do dia a dia: `docs/DASHBOARD-OPERATIONS.md`
- Promessa MVP-OP (épico): `docs/ISSUES.md` — **ISS-007** (não fechado por este mapa)