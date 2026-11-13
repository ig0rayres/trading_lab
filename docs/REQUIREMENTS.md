# Requisitos — Trading Lab

> Gerado em: 2026-10-29 · Revisado em: 2026-11-13 (v0.4, G-MKT shortlist de contas demo)
> Status: Em Revisão
> Fonte: adendo técnico de 29/10/2026, que detalha o handoff da mesma data. O snapshot de código na raiz é o MVP de pesquisa mais novo que estava disponível (`ba36049`). Contagens de teste citadas em nomes de ZIP não foram reexecutadas aqui.

---

## 1. Visão Geral

**Descrição**: Sistema modular e multi-mercado (ações EUA, B3 e cripto) para identificar oportunidades de day trade e swing trade, LONG e SHORT quando o mercado permitir, classificar sinais, simular, reconciliar e medir resultado líquido.

**Problema que resolve**: Decisão apressada em cima de backtest isolado, de notícia lida no sentimento, ou de um HTTP 200 tratado como ordem executada. O operador precisa de uma trilha em que cada promoção de estado tenha evidência, e em que rejeição também fique registrada.

**Para quem**: O operador do laboratório, que pesquisa e, só depois, opera em paper.

**Objetivo de negócio**: Errar rápido e barato. A escada é Research, Shadow, Paper limitado, Paper validado. Live permanece desligado. Nenhuma promoção acontece só porque um número de teste subiu ou uma requisição retornou 200.

**Objetivo revisado (v0.3, 2026-11-03)**: A plataforma opera sozinha nas contas demo de B3, cripto e forex, com as estratégias já definidas, sem o operador disparar cada ordem. A Alpaca paper continua sendo a conta já ligada no código e não cobre B3 nem forex. As âncoras de risco seguram a operação: quando uma estoura, a plataforma para sozinha e avisa. O operador acompanha e ajusta tudo por um painel central, sem comando no Exec do EasyPanel. Do ponto de vista operacional, demo e real seguem as mesmas regras; só o destino da ordem muda, e o destino real continua desligado até autorização explícita do operador, separada deste documento.

**Cenário**: LEGADO

---

## 2. Stakeholders

| Nome / Papel | Tipo | Prioridade | O que importa para ele |
|---|---|---|---|
| Operador do laboratório | Decisor, usuário final e patrocinador | Alta | Um pacote único, testado e implantável. Sem sequência de mini-ZIPs e deploys manuais. Sem dinheiro real antes da evidência. |

---

## 3. Usuários e Personas

| Persona | Contexto | Principal frustração (hoje) | Objetivo | Nível técnico |
|---|---|---|---|---|
| Operador do laboratório | Pessoa única que acompanha pesquisa, paper e o que está no EasyPanel | Sinais, filas e HTTP 200 aparecem como se o robô tivesse operado. Várias builds com contagens diferentes, sem uma base canônica comprovada. Em 2026-11-03: operar exige comandos colados no Exec e token no curl; o painel só mostra. | Não operar à mão. Ver o estado real (pesquisa, sombra ou paper), o motivo de cada rejeição e o P&L reconciliado com a corretora, e ajustar risco e estratégias num lugar só. | Semi-técnico |

---

## 4. Features (MVP)

O MVP de produto, para este documento, é o laboratório até paper reconciliado. O que o Git já contém é o ciclo de pesquisa. O restante entra como requisito, com o grau de evidência explícito. Não é lista do que já passou.

### Feature 1: Ciclo de pesquisa e shadow

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have
- **Evidência**: Reportado no snapshot importado. O scheduler não importa código de envio de ordem. Pytest desta máquina ainda não rodou.

**Fluxo principal:**
1. O ciclo lê o universo configurado (hoje: AAPL, MSFT, BBAS3, BBDC4, ITUB4, BTCBRL, ETHBRL).
2. Coleta dado público, gera decisão e preview de risco em modo Research/Shadow.
3. Grava relatórios e um manifesto cuja integridade o dashboard só exibe se os componentes conferem.
4. Nenhuma ordem sai.

**Fluxo alternativo:**
- Fonte externa indisponível: o estado fica `FAILED_OR_BLOCKED` ou `PARTIAL_OR_BLOCKED`, visível, sem ordem.

**Fluxo de exceção:**
- `LIVE_TRADING_ENABLED` diferente de false: o processo recusa e sai.
- Manifesto antigo não pode continuar parecendo sucesso depois de ciclo falho.

**Regras de negócio:**
- `OK_RESEARCH_ONLY` prova execução do radar naquela amostra, não prova paper.
- ORB e mean reversion permanecem em Research/Shadow. ORB não vira estratégia principal de paper.

**Critérios de aceite:**
- [x] `pytest` com evidência em CI (GitHub Actions run [41041762290](https://github.com/ig0rayres/trading_lab/actions/runs/41041762290), commit `f597f8b`, job **test** verde). Contagens 224–395 de ZIPs não substituem isso.
- [x] Com live desligado, um ciclo termina sem ordem enviada (`tests/test_v4_scheduler.py` `test_readonly_success`, `test_live_guard`; `tests/test_v4_run_once.py` `test_full_readonly_path`; matriz N11 em `docs/TEST-EVIDENCE.md`).
- [x] Ciclo falho não deixa manifesto de sucesso anterior visível como confiável (`test_failed_cycle_invalidates_previous_manifest`, `test_main_once_failure_clears_stale_manifest`; `tests/test_v4_report_integrity.py`).

### Feature 2: Gate A — autenticidade do sinal

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have
- **Evidência**: Decidido. Webhook TradingView retornou HTTP 200 e `PAPER_GATEWAY_QUEUE_ONLY` em relato: isso é fila, não ordem.

**Fluxo principal:**
1. Entra evento de mercado, notícia, TradingView ou sinal externo, com procedência.
2. O gate confere assinatura ou segredo, fonte, timestamp UTC, frescor, schema, símbolo, direção e idempotência.
3. Sinal autêntico segue. Sinal inválido para, com código de motivo, sem ordem.

**Fluxo de exceção:**
- Token ausente, inválido ou curto demais; payload malformado; replay; timestamp futuro; entrega duplicada; ticker não reconhecido.

**Regras de negócio:**
- Verdadeiro significa autêntico, fresco, coerente e permitido. Não significa que vai dar lucro.
- Segredos não entram em documentação nem em log. O requisito de tamanho citado no serviço foi token de webhook com pelo menos 32 caracteres e segredo de copy com pelo menos 24. Os valores não são registrados aqui.

**Critérios de aceite:**
- [x] Sinal inválido é rejeitado e nenhuma ordem é criada (`tests/test_tradingview_webhook.py`, `orders_sent` ausente ou 0 no caminho de fila).
- [x] O mesmo evento entregue duas vezes não abre duas posições (`DUPLICATE_IGNORED` + idempotência na fila).
- [x] Com `LEDGER_DATABASE_URL`, a trilha em `signal_events` guarda motivo (`reject_code`), status e timestamp (`tests/test_gate_a_signal.py`).

### Feature 3: Gate B — risco e permissão de paper

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have
- **Evidência**: Decidido como política. Não é recomendação de operar no teto.

**Fluxo principal:**
1. Sinal que passou no Gate A entra na política da estratégia e no risco.
2. O gate só libera paper se mercado, calendário, dado, stop, spread, liquidez e limites globais estiverem aceitos, e se o kill switch estiver livre.
3. A fase da estratégia (research, shadow, paper limitado, paper validado) precisa permitir aquela ordem.

**Regras de negócio:**
- Capital paper de referência: R$ 5.000.
- Risco inicial: R$ 50 por operação (1%). Teto configurável: R$ 100 por operação.
- No máximo 3 posições simultâneas.
- Risco agregado até R$ 200.
- Perda diária R$ 200. Perda semanal R$ 500.
- Sem alavancagem.
- Prodigy experimental: teto inicial separado de R$ 20, só paper limitado, sem promoção automática.
- SHORT só se o mercado e a corretora permitirem.
- Calendário de NY e B3, feriado e horário de verão fazem parte do gate. O relato `NY weekdays, holidays not filtered` é bloqueio aberto, não detalhe cosmético.

**Critérios de aceite:**
- [x] Ordem que estoura qualquer limite acima é recusada com motivo, sem ida à corretora (`tests/test_gate_b_risk.py`, `tests/test_paper_gateway_queue.py`; worker `orders_sent: 0`).
- [x] Kill switch acionado impede ordem nova (`TRADING_LAB_KILL_SWITCH` / `control_flags`; teste em `test_gate_b_risk.py`).
- [x] Fora da sessão NYSE ou com 3+ posições abertas (Alpaca read), o sinal não vira fila paper (`OUTSIDE_SESSION`, `MAX_POSITIONS` em `gate_b_risk.py`).

Limites numéricos de paper (BRL 5000 / 50 / 3 posições): **`src/gate_b_risk.py`** + Feature 3 acima — não duplicados em `ENGINEERING_RULES.md` (reuso upstream `trader-risk`).

### Feature 4: Catálogo de estratégias e promoção de estado

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have
- **Evidência**: Decidido o contrato. Fórmulas numéricas de momentum, “Tá Barato Demais” e Prodigy não foram recuperadas. Não inventar limiar.

**Famílias:**
- News First: notícia é hipótese, com timestamp, veículo, tickers, categoria, frescor e confiança. Não é compra ou venda pelo tom do texto. Rejeitar notícia velha, ticker indefinido, rumor sem fonte, movimento já no preço, divergência com o preço e liquidez ruim.
- Momentum: força, rompimento e continuidade com barra fechada. Limiares numéricos finais não estão decididos até saírem do código.
- Tá Barato Demais: nome interno de desconto/distorção, por mercado (EUA, B3, cripto), com parâmetros próprios. Não é “caiu, compra”. Fórmula, percentis e gatilhos não foram recuperados.
- Signal copy: normalizar sinal de terceiro. Mérito econômico é um filtro depois da autenticidade. Collective2 observado: 10 candidatos, nenhum com histórico de seis meses verificado, nenhum aprovado para paper-copy, zero ordens.
- Prodigy 15 dias: candidatos fortes e recentes, janela móvel de 15 dias, mínimo de 5 operações em pelo menos 3 dias, retorno líquido positivo, drawdown e consistência. Fórmula de pontuação ainda pendente. Risco paper inicial R$ 20.
- ORB e mean reversion: shadow/research. ORB 1R e 2R reportados com média R e profit factor negativos. Sem edge intraday validado.

**Estados persistentes:** RESEARCH, SHADOW, PAPER_LIMITED, PAPER_VALIDATED. LIVE desabilitado. Um estado não sobe por lucratividade aparente nem por HTTP 200.

**Critérios de aceite:**
- [x] ORB não é selecionável como estratégia principal de paper (Gate B `STRATEGY_NOT_PAPER`; N7).
- [x] Nenhum provedor Collective2 entra em copy enquanto `approved_for_paper_copy` for falso (inalterado; N7 não toca C2).
- [x] Estratégia sem fórmula recuperada não ganha limiar inventado neste repositório (N7: fases seed only; sem scoring).

### Feature 5: Paper ponta a ponta

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have para homologar. Não está comprovado no snapshot.
- **Evidência**: Módulos de gateway, webhook, ledger e atividades Alpaca existem no código. A ponte completa não foi homologada. Conta paper citada em captura não prova envio de ordem.

**Fluxo principal:**
1. Sinal autêntico passa nos dois gates.
2. A fila de paper envia à conta Alpaca Paper, nunca à conta live.
3. A corretora devolve aceite, rejeição, fill parcial ou fill cheio.
4. O reconciliador grava ids (incluindo prefixos `nf-` e `demo-` quando existirem), posição e P&L.
5. Reinício do processo não duplica ordem nem perde o ledger.

**Fluxo de exceção:**
- Timeout, rejeição da corretora, fill parcial, cancelamento, posição que já existia, API fora.

**Critérios de aceite (homologação):**
- [x] Fill real Alpaca + posição coerente na corretora (passo operador; `docs/HOMOLOGATION.md`). **Evidência 2026-11-11:** Alpaca paper AAPL buy limit @349.85 em 2026-10-29 **filled** qty 1; posição aberta AAPL qty 1 (avg 349.85) conferida no Exec e na UI. MSFT/NVDA submits posteriores sem fill não contam. Ver `docs/TEST-EVIDENCE.md` § N20.
- [x] Sinal inválido não gera ordem (Gates A+B; CI).
- [x] Duplicata não reabre posição (idempotência + testes).
- [x] Reinício não perde trilha ledger (Postgres append-only; worker atômico).
- [x] `PAPER_GATEWAY_QUEUE_ONLY` ≠ homologação completa (`docs/HOMOLOGATION.md`).
- [x] Reconcile read-only → `paper_fills` com flag `PAPER_RECONCILE_LEDGER_APPLY` (`test_ledger_reconcile.py`).

### Feature 6: Observabilidade e parada

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have

**Fluxo principal:**
1. O operador vê último ciclo, fila, sinais aceitos e rejeitados, ordens paper e P&L.
2. Log não contém segredo.
3. Existe parada de emergência que impede ordem nova.

**Critérios de aceite:**
- [x] Dashboard local (`127.0.0.1`) não exige auth; remoto exige bearer ≥32 (`v4_web_dashboard.py`).
- [x] Kill switch visível em `/api/status` (`kill_switch_on`) e testável via env/Postgres sem ordem real.

> Features 7–11 entram na revisão v0.2 (2026-11-03). Fill paper na corretora (Feature 5) está `[x]` (AAPL 2026-10-29); performance e aprendizado ainda exigem o laço de ledger das ondas seguintes.

### Feature 7: Operação autônoma na conta demo

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have

**Fluxo principal:**
1. Um sinal chega (copy, Prodígio ou estratégia interna em fase paper).
2. Gate A e Gate B decidem sem o operador.
3. Se aprovado, a plataforma envia a ordem para a conta demo e acompanha até fill, cancelamento ou expiração.
4. O resultado fica no ledger e aparece no painel.

**Fluxo de erro:**
- Âncora de risco estourada: a plataforma para de abrir ordem nova e registra o motivo. O operador vê no painel.
- Ordem sem fill no prazo: a plataforma cancela, registra e não reenvia sozinha o mesmo sinal.
- Falha de comunicação com a corretora: nenhuma ordem nova até a conciliação voltar a bater.

**Âncoras de risco (valores atuais, editáveis só pelo operador):**

| Âncora | Valor |
|--------|-------|
| Capital de referência | R$ 5.000 |
| Risco por operação | R$ 50 |
| Posições simultâneas | 3 |
| Risco agregado aberto | R$ 200 |
| Perda máxima no dia | R$ 200 |
| Perda máxima na semana | R$ 500 |

**Critérios de aceite:**
- [ ] Sinal válido vira ordem na conta demo sem ação manual do operador.
- [ ] Nenhuma ordem sai com qualquer âncora estourada.
- [ ] Perda do dia ou da semana no teto para a operação até o próximo período e registra o motivo.
- [ ] Host de destino é sempre o paper; existir uma chave live no ambiente não muda isso.
- [ ] Reinício do serviço retoma a operação sem duplicar ordem.

**G-MKT — corretoras demo nomeadas (2026-11-13, operador):**

| Mercado | Conta demo escolhida | Observação |
|---------|----------------------|------------|
| B3 | Clear — Smart Trader API (ambiente **simulado**) | REST/WS; posição, ordem e status. Day trade Clear. **Não** Alpaca. |
| Cripto | Alpaca Paper (já ligada) | Mantém o caminho paper existente. |
| Forex | OANDA fxTrade **Practice** (API v20) | REST practice; ordem + fill. **Não** Alpaca. |

O identificador concreto da conta (login/account id) e as chaves ficam só no ambiente EasyPanel — nunca no Git. Enquanto a conta de um mercado não estiver criada/credenciada, esse mercado permanece visível e **barrado** com motivo (`NO_DEMO_ACCOUNT_PATH` ou equivalente). Conta real continua sem botão.

### Feature 8: Central de controle no painel

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have

**Fluxo principal:**
1. O operador entra no painel com login.
2. Vê e altera as âncoras de risco.
3. Liga ou desliga cada estratégia existente e aciona a parada geral.

**Critérios de aceite:**
- [ ] Toda alteração vale a partir da próxima ordem e fica registrada com data e valor anterior.
- [ ] A plataforma nunca afrouxa uma âncora sozinha; só o operador altera.
- [ ] Parada geral pelo painel impede ordem nova em até um ciclo.
- [ ] Nenhuma operação do dia a dia exige Exec no EasyPanel.
- [ ] Acesso exige autenticação; o painel não abre sem login.

### Feature 9: Sinais e Prodígio

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have

**Critérios de aceite:**
- [ ] Lista de sinais recebidos com origem, destino (ordem, barrado, fila) e motivo da rejeição.
- [ ] Ranking Prodígio dos provedores e quais sinais ele copiou.
- [ ] Sinal barrado mostra qual gate e qual âncora barrou.

### Feature 10: Performance

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have

**Critérios de aceite:**
- [ ] Resultado por estratégia e total, calculado só a partir de fill confirmado na corretora.
- [ ] Ordem sem fill não entra no resultado.
- [ ] Indicação de quais valores ainda são brutos (sem custo completo).

### Feature 11: Sugestões e ajuste supervisionado

- **Persona**: Operador do laboratório
- **Prioridade**: Should-have

**Fluxo principal:**
1. As estratégias encontram oportunidades; o painel mostra como sugestão, com a estratégia de origem.
2. A plataforma registra cada erro (perda, ordem barrada, sinal sem fill) ligado à estratégia.
3. A partir desses registros, ajusta parâmetros das estratégias.

**Critérios de aceite:**
- [ ] Sugestão aparece marcada como sugestão e nunca é tratada como ordem autorizada por si só.
- [ ] Ajuste automático só altera parâmetros que já existem na estratégia original, dentro da faixa que ela define.
- [ ] Todo ajuste fica registrado com antes, depois e motivo, e pode ser desfeito pelo painel.
- [ ] Ajuste automático nunca altera as âncoras de risco.

---

## 5. Integrações

| Sistema | Tipo | Direção | Autenticação | Fallback |
|---|---|---|---|---|
| Dados públicos de ação e cripto (Yahoo e Binance citados no MVP) | API de leitura | Entrada | Nenhuma no MVP de pesquisa | Ciclo marcado como falho ou parcial. Sem ordem. |
| Alpaca Paper | API de corretora paper (cripto + ação US já ligada) | Bidirecional | Chave paper, fora do repositório | Sem chave, não há submit. Nunca usar chave live. B3 e forex **não** usam este host. |
| Clear Smart Trader (simulado) | API de corretora demo B3 | Bidirecional | API_KEY / SECRET / RSA no portal Clear, fora do repositório | Sem credencial simulada, mercado B3 fica barrado com motivo. Nunca apontar URL real com token simulado. |
| OANDA fxTrade Practice | API de corretora demo forex | Bidirecional | Personal access token practice, fora do repositório | Sem conta Practice, mercado forex fica barrado com motivo. Nunca usar host fxTrade live. |
| TradingView | Webhook | Entrada | Segredo do webhook | Pedido sem segredo válido é rejeitado no Gate A. |
| Collective2 | Pesquisa e possível copy | Entrada | Acesso ainda não verificado | Nenhum provedor aprovado. Copy permanece fechado. |
| News | Feed de notícias | Entrada | Conforme a fonte, sem gravar segredo | Ausência de notícia não autoriza ordem. |
| day-trader-skill | Biblioteca de reuso | Entrada de código | Não se aplica | Sem o checkout pinado em `vendor/`, não afirmar paridade. Não reescrever entry, exit, budget, risk e scanner. |
| EasyPanel (`trading-lab` e `trading-lab-webhook`) | Deploy já existente | Operação | Fora deste repo | Não substituir esses dois serviços com este snapshot. App novo, se existir, é separado e sem volume compartilhado. |
| Postgres | Banco previsto | Persistência | DSN fora do repo | Estado atual das migrations não foi verificado nesta importação. |

**Autenticação do sistema**: um operador. Segredos de webhook e de paper ficam no ambiente, nunca no Git. Não há cadastro público.

---

## 6. Requisitos Não-Funcionais

| Categoria | Requisito | Meta |
|---|---|---|
| Segurança | Live desligado. Segredo fora de log, ZIP e markdown. | Falha fechada se a flag de live não for false. |
| Integridade | Idempotência de sinal e de ordem. Manifesto não mente após falha. | Duplicata não cria segunda posição. |
| Auditoria | Toda rejeição tem código, timestamp e entrada sanitizada. | Trilha recuperável depois do restart. |
| Calendário | Sessão EUA e B3, feriado e horário de verão. | Sinal fora da sessão não vira ordem. |
| Entrega | Um pacote consolidado, com teste e rollback. | Sem série de micro-deploys para o operador executar. |
| Performance | Tempo de resposta | A definir. Não há meta numérica no handoff. |
| Disponibilidade | Uptime | A definir. O requisito atual é ciclo observável e parada, não um percentual. |
| Escalabilidade | Usuários simultâneos | Um operador. |

---

## 7. Fora de Escopo

- Operação com dinheiro real (LIVE).
- Tratar ORB como edge validado ou como estratégia principal de paper.
- Assinar ou copiar provedor Collective2. Os dez candidatos observados estão reprovados para paper-copy.
- Inventar percentil, RSI, volume ou score de “Tá Barato Demais”, momentum ou Prodigy que não esteja no código recuperado.
- Substituir os serviços EasyPanel atuais por este ZIP.
- Publicar dashboard sem autenticação.
- Somar contagens de teste de ZIPs diferentes e apresentá-las como uma suíte única.
- Cadastrar estratégia nova pelo painel (segundo momento, decisão do operador em 2026-11-03).
- Ajuste automático que crie parâmetro ou limiar inexistente na estratégia original.

---

## 8. Premissas

- A base de código deste repositório é o snapshot de pesquisa v4 importado em 29/10/2026, não o container que porventura ainda roda no EasyPanel.
- A pasta `trading-lab-v4-mvp-implantavel` é anterior e não é a base.
- Paper de referência continua R$ 5.000, com os tetos da seção do Gate B.
- Reuso do `day-trader-skill` continua obrigatório onde aquelas funções já existirem. O vendor não veio no ZIP.
- “Reportado como implementado” não é o mesmo que homologado.

---

## 9. Dúvidas em Aberto

| # | Dúvida | Impacto | Status |
|---|---|---|---|
| 1 | Fórmula, percentis e gatilhos de “Tá Barato Demais” | Alto | Aberta. Não inventar. |
| 2 | Limiares numéricos finais de momentum | Alto | Aberta até leitura do código, sem promover a regra. |
| 3 | Fórmula de empate, drawdown e consistência do Prodigy 15d | Médio | Aberta. |
| 4 | Qual imagem está de fato no EasyPanel (`trading-lab` e webhook), com SHA | Alto | Aberta. Export não veio. |
| 5 | Commit pinado do `day-trader-skill` em `vendor/` | Alto | Aberta. |
| 6 | Prazo de calendário para a homologação paper | Médio | Respondida 2026-11-03: operação autônoma na conta demo nas próximas semanas, sem data fixa. |
| 7 | Postgres: há migration e dado, ou só intenção de infra | Médio | Aberta. |
| 8 | Método do ajuste automático (Feature 11): o que conta como erro, com que frequência ajustar, quando desfazer | Alto | Aberta. Fase de arquitetura. |
| 9 | Login do painel no lugar do Bearer manual | Alto | Aberta. Fases de arquitetura e DevOps. |
| 10 | Painel deixa de ser somente leitura e passa a alterar risco e estratégias | Alto | Aberta. Decisão de arquitetura; a regra atual do painel é read-only. |
| 11 | G-MKT: qual corretora demo por mercado (B3 / cripto / forex) | Alto | Respondida 2026-11-13: Clear Smart Trader simulado (B3); Alpaca Paper (cripto); OANDA Practice (forex). Pendente: abrir/credenciar contas e colocar ids só no env. |

---

## 10. Mapa do Legado

### Stack Atual

- **Frontend**: dashboard de leitura em Python, sem framework web de produto. Não publicar sem autenticação.
- **Backend**: Python 3.12 (`python:3.12-slim`), scripts em `src/`, entrada `scripts/run.sh`. Sem `requirements.txt` ou `pyproject.toml`.
- **Banco**: Postgres citado como infra prevista. Não verificado neste clone.
- **Testes**: `pytest.ini` + CI `.github/workflows/ci.yml`; suíte verde na Actions (2026-10-30, run 41041762290).
- **Git**: repositório local `master`, commit `ba36049`. Sem remote. O GitHub `Jakeschincariol/day-trader-skill` é dependência de reuso, não este repositório.

### Features Existentes

| Feature | Manter | Modificar | Remover | Observação |
|---|---|---|---|---|
| Scheduler de pesquisa, 15 min, universo de 7 símbolos | sim | | | Não envia ordem. |
| Pipeline, risco preview, shadow, manifesto com hash | sim | | | Pesquisa apenas. |
| Webhook, News First, copy, gateway paper, ledger | sim | sim | | Existem no código. Não estão ligados ao ciclo do MVP e não estão homologados. |
| ORB como candidato de pesquisa | sim | | | Fica em shadow. Resultado reportado é negativo. |
| Serviços EasyPanel atuais | sim | | | Não substituir com este pacote. |

### Migração de Dados

- **Volume**: relatórios sintéticos de smoke no repo. Volume real de `/app/reports` e banco do EasyPanel não foram copiados.
- **Estratégia**: coexistência. Este repo é a base Git. Os serviços já publicados continuam até uma release única, supervisionada.
- **Riscos**: operar em cima do ZIP errado; achar que fila é fill; promover ORB; perder o vendor upstream.

### Evidências numéricas que permanecem relato

Estas linhas não são aprovação. Servem para não perder o que já foi medido.

| ID | O que foi visto | Leitura |
|---|---|---|
| H01–H03 | 5.944 tickers, 897 com dado, 271 setups, 95 sinais ORB | Detecção, não execução. |
| H04–H06 | ORB 1R e 2R com média R e profit factor negativos; replay AMAT desfavorável | Sem edge intraday validado. |
| H08 | Webhook HTTP 200, `PAPER_GATEWAY_QUEUE_ONLY` | Fila, não ordem. |
| H09 | Radar `OK_RESEARCH_ONLY`, 12 candidatos, 0 ordens | Pesquisa naquela amostra. |
| H10 | Collective2, 10 candidatos, 0 elegíveis | Copy fechado. |
| H11–H12 | Reconciliação `nf-`/`demo-` e atividades Alpaca reportadas | P&L com a corretora ainda não fechado. |

---

## Histórico de Revisões

| Data | Versão | Alteração | Autor |
|---|---|---|---|
| 2026-10-29 | 0.1 | Versão inicial a partir do adendo de 29/10/2026 e do snapshot importado | Analista de Requisitos (IA) |
| 2026-11-03 | 0.2 | Operação autônoma na conta demo; âncoras de risco confirmadas; central de controle no painel; Features 7–11; cadastro de estratégia nova adiado | Analista de Requisitos (IA) com o operador |
| 2026-11-13 | 0.4 | G-MKT: Clear Smart Trader simulado (B3), Alpaca Paper (cripto), OANDA Practice (forex); integrações e Feature 7 atualizados | Analista de Requisitos (IA) com o operador |
