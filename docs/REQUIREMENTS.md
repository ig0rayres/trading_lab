# Requisitos — Trading Lab

> Gerado em: 2026-10-29 · Revisado em: 2026-11-25 (v0.7.8, Sinais — rascunho de aceite N61 versão do painel + aviso da listagem com número e hora; ISS-024 aberto)
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
- `news_first` permanece em **research** (N30.4): notícia é hipótese; ciclo e auditoria Gate A apenas — o contrato **não** exige ordem paper para esta família.
- `orb` e `mean_reversion` permanecem **NEVER_PAPER** (`NEVER_PAPER_KEYS` em `src/strategy_catalog.py`; fase seed shadow). Gate B rejeita mesmo se a linha no banco for `paper_*` (`STRATEGY_NOT_PAPER` / `STRATEGY_ORB_NOT_SELECTABLE`). ORB não vira estratégia principal de paper.

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
- News First: notícia é hipótese, com timestamp, veículo, tickers, categoria, frescor e confiança. Não é compra ou venda pelo tom do texto. Permanece **research** (N30.4); sem ordem paper automática — ciclo/Gate A apenas.
- Momentum: força, rompimento e continuidade com barra fechada. Limiares numéricos finais não estão decididos até saírem do código.
- Tá Barato Demais: nome interno de desconto/distorção, por mercado (EUA, B3, cripto), com parâmetros próprios. Não é “caiu, compra”. Fórmula, percentis e gatilhos não foram recuperados.
- Signal copy: normalizar sinal de terceiro. Mérito econômico é um filtro depois da autenticidade. **Pré-aprovação no painel autenticado** é o caminho do dia a dia para Collective2, Prodígio e TradingView (e fontes futuras no mesmo formato): aprovar/rejeitar persiste no livro-razão (`signal_provider_approvals`); aprovação **não** envia ordem. `config/c2_paper_copy_allowlist.json` e `C2_PAPER_COPY_APPROVED_IDS` são **semente/reserva** quando não houver linha no livro-razão; rejeição no painel vence a semente. Métricas de pesquisa (`win_rate_pct`, `reported_pnl_sum`, etc.) aparecem na fila com rótulo pesquisa; campo ausente = indisponível (sem fórmula nova). Relato H10 permanece histórico; elegível no ranking **não** é aprovação de cópia. **Atualizar candidatos** (ISS-024): o servidor aplica os critérios de seleção **nas fontes** (Collective2: listagem oficial `SearchStrategies` + histórico fechado + Feature 4 / Prodígio 15d; arquivos em `{root}/providers/raw` são **cache**, não substituem a varredura; TradingView = escopo mínimo honesto a partir de ingest/origens já vistas — **sem** varredura de marketplace até ISS-025); releitura só de JSON em disco **não** satisfaz o aceite. Job/refresh ≠ ordem; chave Collective2 só no servidor.
- Prodigy 15 dias: candidatos fortes e recentes, janela móvel de 15 dias, mínimo de 5 operações em pelo menos 3 dias, retorno líquido positivo, drawdown e consistência. Fórmula de pontuação ainda pendente. Risco paper inicial R$ 20. Fase default **research**; rank→ingest (N30) não promove fase sozinho.
- ORB e mean reversion: shadow/research; **NEVER_PAPER** no catálogo (N30.4). ORB 1R e 2R reportados com média R e profit factor negativos. Sem edge intraday validado.

**Estados persistentes:** RESEARCH, SHADOW, PAPER_LIMITED, PAPER_VALIDATED. LIVE desabilitado. Um estado não sobe por lucratividade aparente nem por HTTP 200.

**Critérios de aceite:**
- [x] ORB não é selecionável como estratégia principal de paper (Gate B `STRATEGY_NOT_PAPER`; N7).
- [x] Nenhum provedor Collective2 entra em paper-copy fora da lista nomeada; com lista vazia `approved_for_paper_copy` permanece falso (N50; painel não chama API Collective2).
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
- [x] Sinal válido vira ordem na conta demo sem ação manual — **US_EQUITY e CRYPTO (Alpaca paper)** (`tests/test_signal_paper_runner.py` `test_n30_us_equity_demo_on_paper_submitted`, `test_n30_crypto_risk_candidate_uses_signal_market`; `tests/test_paper_gateway_queue.py` `N30Feature7AlpacaPaperLoopTest.test_n30_gateway_crypto_risk_candidate_market_is_crypto`).
- [ ] Sinal válido vira ordem na conta demo **B3** (Clear simulada) — **G-MKT § abaixo; adapter ISS-010 / N29.5** (ADR-010: sem POST Alpaca).
- [ ] Sinal válido vira ordem na conta demo **FOREX** (OANDA Practice) — **G-MKT / ISS-010 / N29.5** (ADR-010: sem POST Alpaca).
- [x] Mercado sem conta demo nomeada fica barrado com `NO_DEMO_ACCOUNT_PATH` e **zero** POST Alpaca (`test_n30_crypto_without_named_path_blocked_no_post`; `test_n27_gateway_b3_equity_blocked_no_alpaca_post`; `test_n27_forex_runner_never_posts_alpaca_paper_host`).
- [x] Nenhuma ordem sai com qualquer âncora estourada — **laço paper lê `control_flags`** (`tests/test_signal_paper_runner.py` `PaperRunnerTests.test_n32_tight_defaults_qty1_aapl_paper_submitted`, `test_n32_lowered_capital_cents_blocks_capital_limit`, `test_n32_lowered_max_risk_per_trade_blocks_trade_risk_limit`, `test_n32_risk_check_tight_cap_not_parallel_10k_usd`, `test_n32_b3_equity_auto_blocked_no_alpaca_post`, `test_n32_forex_auto_blocked_no_alpaca_post`; complemento portfolio/Gate B em `tests/test_feature7_anchor_ceilings.py`, `test_n30_stale_v4_portfolio_snapshot_still_blocked`, `tests/test_ledger_loss_anchor.py`).
- [x] Perda do dia ou da semana no teto para a operação até o próximo período e registra o motivo (`tests/test_ledger_loss_anchor.py` `test_loss_ceiling_reject_daily_at_tight_default`, `test_loss_ceiling_reject_weekly_at_tight_default`, `test_gate_b_blocks_when_daily_loss_at_ceiling`; `tests/test_portfolio_risk_v4.py` `DAILY_LOSS_HALT`/`WEEKLY_LOSS_HALT`; rejeição persistida via `paper_gateway_queue.persist_risk_decision` no caminho `tv-worker`).
- [x] Host de destino é sempre o paper; existir uma chave live no ambiente não muda isso (`tests/test_paper_gateway_queue.py` `test_n27_5_live_looking_key_keeps_paper_alpaca_host`; hosts em `test_n30_us_equity_demo_on_paper_submitted`).
- [x] Reinício do serviço retoma a operação sem duplicar ordem com laço demo ligado (`tests/test_paper_restart_no_duplicate.py` `test_n30_demo_operation_on_restart_no_second_broker_post`).

**G-MKT — corretoras demo nomeadas (2026-11-13, operador):**

| Mercado | Conta demo escolhida | Observação | Feature 7 (N30.4) |
|---------|----------------------|------------|-------------------|
| B3 | Clear — Smart Trader API (ambiente **simulado**) | REST/WS; posição, ordem e status. Day trade Clear. **Não** Alpaca. | `[ ]` — **ISS-010**; barrado até adapter homologado |
| Cripto | Alpaca Paper (já ligada) | Mantém o caminho paper existente. | `[x]` — pytest N30.1 (env `DEMO_ACCOUNT_PATH_CRYPTO`) |
| Forex | OANDA fxTrade **Practice** (API v20) | REST practice; ordem + fill. **Não** Alpaca. | `[ ]` — **ISS-010**; barrado até adapter homologado |
| US ação | Alpaca Paper | Caminho existente N27/N30. | `[x]` — pytest N30.1 |

O identificador concreto da conta (login/account id) e as chaves ficam só no ambiente EasyPanel — nunca no Git. Enquanto a conta de um mercado não estiver criada/credenciada, esse mercado permanece visível e **barrado** com motivo (`NO_DEMO_ACCOUNT_PATH` ou equivalente). Conta real continua sem botão.

### Feature 8: Central de controle no painel

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have

**Fluxo principal:**
1. O operador entra no painel com login.
2. Vê e altera as âncoras de risco.
3. Liga ou desliga cada estratégia existente e aciona a parada geral.

**Critérios de aceite:**
- [x] Toda alteração vale a partir da próxima ordem e fica registrada com data e valor anterior (`tests/test_panel_triggers.py` `PanelTriggerHttpTests.test_patch_triggers_with_cookie_updates_audit` — `old_value`/`new_value`/`changed_at`; `PanelTriggerUnitTests.test_apply_trigger_patch_appends_audit`).
- [x] A plataforma nunca afrouxa uma âncora sozinha; só o operador altera (`tests/test_panel_triggers.py` `PanelTriggerHttpTests.test_loosening_anchor_without_operator_cookie_is_401_and_no_audit`; `PanelTriggerUnitTests.test_platform_never_loosens_anchors_when_db_unavailable` — falha de ledger usa `TIGHT_DEFAULTS`, sem PATCH autônomo).
- [x] Parada geral pelo painel impede ordem nova em até um ciclo (`tests/test_panel_ops.py` `PanelKillSwitchCycleTests.test_kill_switch_from_panel_blocks_next_eval`).
- [x] Nenhuma operação do dia a dia exige Exec no EasyPanel (`tests/test_panel_ops.py` `PanelOpsRunbookTest.test_daily_runbook_points_to_panel_not_exec`).
- [x] Acesso exige autenticação; o painel não abre sem login (`tests/test_panel_ops.py` `PanelOpsHttpTests.test_root_redirects_to_login_without_cookie`, `test_login_sets_cookie_and_opens_central`, `test_api_signals_requires_session`, `test_bearer_alone_still_401_on_patch`; `tests/test_panel_triggers.py` `PanelTriggerHttpTests.test_patch_triggers_bearer_only_is_401`).

### Feature 9: Sinais e Prodígio

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have
- **Objetivo da função (tela Sinais):** permitir ao operador **pesquisar e pré-aprovar cópia de terceiros** com auditoria — ver candidatos elegíveis, decidir Aprovar/Rejeitar, acompanhar o que entrou em operação e o inventário — **sem** tratar aprovação, refresh ou HTTP 200 como fill. LIVE permanece desligado.

**Fluxo principal (navegação mental):**
1. **Candidatos / pré-aprovação** — fila de provedores (Collective2, Prodígio, TradingView) com métricas de pesquisa rotuladas; botão **Atualizar candidatos** **varre plataformas homologadas** e aplica Feature 4 / Prodígio 15d já no código (não inventário em disco e não só reler arquivo estático). Collective2: listagem oficial no servidor + filtro 15d; **sem** allowlist para aparecer. TradingView: **sem varredura** até contrato de busca (ISS-025); origens já ingeridas continuam visíveis e **não** contam como varredura. Falha de uma fonte não apaga as outras.
2. **Decisão** — Aprovar ou Rejeitar grava no livro-razão (`signal_provider_approvals`); rejeição vence semente JSON/env; aprovação **não** envia ordem.
3. **Em operação** — sinais/ordens ligados a origem e destino (fila, barrado, ordem), com motivo de rejeição e gate quando barrado.
4. **Inventário** — resultado por sinal **só** com fill confirmado; valores brutos se custo incompleto (`gross_unverified_costs`).
5. **Critérios visíveis** — Feature 4 / Prodígio 15d (janela 15 dias, ≥5 operações em ≥3 dias, paper inicial R$ 20, fases; C2 lista nomeada; sem promoção automática) permanecem legíveis no painel; **sem fórmula nova**.

**Fluxo de exceção:**
- Fonte Collective2 indisponível ou sem chave → fail-closed, mensagem honesta; não inventar candidatos; **não** ocultar elegíveis de Prodígio nem de TradingView; preservar pesquisa anterior dessa fonte.
- Prodígio sem arquivos brutos / ranking vazio → aviso nomeia o que falta (arquivos brutos dos provedores); não inventar score; não apagar Collective2 nem TradingView.
- TradingView sem API de busca → **ISS-025**; N58 declara varredura TV **fora**. Origens já ingeridas (webhook) continuam visíveis; não inventar endpoint TV.
- Ledger sem migration `003` → pré-aprovação indisponível (503 / aviso); não fingir gravação.
- Atualizar candidatos **nunca** aprova, rejeita ou submete ordem.

**Critérios de aceite:**
- [x] Lista de sinais recebidos com origem, destino (ordem, barrado, fila) e motivo da rejeição (`tests/test_panel_ops.py` `PanelOpsDataTests.test_load_panel_signals_exposes_origin_destination_and_reject_reason`; `PanelOpsHttpTests.test_api_signals_json_origin_destination_reject_reason`).
- [x] Ranking Prodígio dos provedores e quais sinais ele copiou (`tests/test_panel_ops.py` `PanelOpsDataTests.test_snapshot_panel_ops_prodigy_ranking_and_copied_signals`; `test_build_panel_bundle_prodigy_copied_signals_structure`).
- [x] Sinal barrado mostra qual gate e qual âncora barrou (`tests/test_panel_ops.py` `PanelOpsDataTests.test_blocked_context_exposes_gate_and_anchor`).
- [x] Pré-aprovação Aprovar/Rejeitar no painel autenticado persiste no livro-razão; aprovação ≠ fill (N51; `signal_provider_approvals`).
- [x] Botão Atualizar candidatos + `GET /api/signals/reload` releitura honesta do bundle em disco com `mode: disk_reread` (N53/N54; `tests/test_panel_ops.py` `N54LiveCriteriaRefreshHttpTests.test_n54_get_reload_disk_reread_skips_prodigy_calculate`, `N53PanelShellRefreshTests.test_n53_reload_rereads_bundle_json`); não aprova nem envia ordem.
- [x] **Atualizar candidatos** aplica critérios Feature 4 / Prodígio 15d **nas fontes** Collective2 (server-side) e TradingView (escopo mínimo honesto) via `POST /api/signals/candidates/refresh` (`mode: live_criteria`; N54 / ISS-024; `tests/test_panel_ops.py` `N54LiveCriteriaRefreshHttpTests.test_n54_post_refresh_live_criteria_orders_sent_zero`, `test_n54_post_refresh_without_c2_key_partial_preserves_queue`).
- [x] Job/refresh POST tem cooldown/fail-closed; chave Collective2 só no servidor; painel não chama HTTP C2 do browser (N54; `N54LiveCriteriaRefreshHttpTests.test_n54_post_refresh_cooldown_ref_refresh_cooldown`, `test_n54_post_refresh_without_c2_key_partial_preserves_queue`; `N53PanelShellRefreshTests.test_n53_atualizar_candidatos_visible_on_sinais` — POST no JS, sem host C2).
- [x] Inventário e operação permanecem distintos da fila de pré-aprovação na navegação (decisão → operação → inventário) (`tests/test_panel_ops.py` `N53PanelShellRefreshTests.test_n53_atualizar_candidatos_visible_on_sinais`, `PanelSinaisN52Tests.test_n52_html_section_hierarchy_decision_first`).
- [x] Depois de **Atualizar candidatos**, a fila de pré-aprovação mostra **todos os candidatos elegíveis** de Collective2, Prodígio e TradingView (Feature 4 / Prodígio 15d já definidos; TradingView = origens já ingeridas), não só uma origem TradingView com métricas indisponíveis (N55 / ISS-024; `tests/test_panel_ops.py` `N55MultiPlatformLiveCriteriaTests.test_n55_refresh_queue_includes_collective2_prodigy_tradingview`).
- [x] Falha fail-closed de uma fonte (chave Collective2 ausente, Prodígio sem arquivos brutos, TradingView sem origens) emite aviso e **não** apaga linhas elegíveis das outras plataformas nem a pesquisa anterior (N55 / ISS-024; `N55MultiPlatformLiveCriteriaTests.test_n55_missing_c2_key_issues_keep_other_platforms_and_prior_research`, `test_n55_tradingview_refresh_failure_records_issue_without_wiping_queue`).
- [x] Prodígio raw/rank vazio: o aviso descreve os arquivos brutos necessários; **sem** inventar score e **sem** inventar API de busca TradingView (N55 / ISS-024; `N55MultiPlatformLiveCriteriaTests.test_n55_empty_prodigy_calculate_does_not_overwrite_prior_rank_json`, `test_n55_partial_warning_rendered_on_sinais_from_bundle`).
- [x] Job live-criteria lê arquivos brutos no volume canônico `{root}/providers/raw` (com `--root /app/reports` → `/app/reports/providers/raw`); pasta duplicada `{root}/reports/providers/raw` **não** é fonte; `UNSCORABLE` / `closed_trades_15d=0` ausente da fila Prodígio sem emitir `prodigy_raw_missing` (N56 / ISS-024 / F-019; `tests/test_panel_ops.py` `N56ProdigyCanonicalRawPathTests.test_n56_refresh_calculate_sees_canonical_raw_providers_gt_zero`, `test_n56_doubled_reports_raw_alone_does_not_feed_calculate`, `test_n56_unscorable_zero_15d_absent_from_queue_without_raw_missing`).
- [x] Com lista nomeada / env de cópia paper vazios, a fila de pré-aprovação lista Collective2 pendente a partir de `{root}/providers/raw/*_closed_trades.json` (`source: discovered`); allowlist/ledger permanece portão de cópia paper (`approved_for_paper_copy` false); refresh não grava aprovação; `UNSCORABLE` no mesmo ID não entra na fila Prodígio (N57 / ISS-024 / F-020; `tests/test_panel_ops.py` `N57Collective2RawQueueDiscoveryTests.test_n57_empty_allowlist_raw_files_pending_c2_after_disk_and_live_refresh`, `test_n57_allowlist_still_gates_paper_copy_not_raw_visibility`, `test_n57_refresh_no_ledger_upsert_live_false_prodigy_research_only`).
- [x] **Atualizar candidatos** varre a Collective2 no servidor (GET `/Strategies/SearchStrategies` disponível à chave, **sem** allowlist para aparecer) e só enfileira quem passa Feature 4 / Prodígio 15d já no código; identificador ausente do disco pode entrar se a varredura o trouxer e ele passar as regras; glob canônico permanece cache; cópia paper continua na lista nomeada/livro-razão (N58 / ISS-024 / F-021; `tests/test_panel_ops.py` `N58Collective2SearchStrategiesScanTests.test_n58_empty_allowlist_scan_eligible_pending_without_raw_on_disk`, `test_n58_fetch_must_not_use_leaderboard_or_historical_strategies_post`, `test_n58_missing_c2_api4_key_no_fake_scan`, `test_n58_refresh_no_auto_approve_live_false_orders_sent_zero`, `test_n58_next_cursor_surfaces_incomplete_scan_issue`, `test_n58_prodigy_rank_constants_unchanged`).
- [x] TradingView: varredura de marketplace **fora** desta sprint até existir contrato de busca (ISS-025); origens já recebidas (N55) **não** contam como varredura; refresh registra aviso honesto **sem** inventar HTTP de busca (N58; `tests/test_panel_ops.py` `N58Collective2SearchStrategiesScanTests.test_n58_tradingview_ingested_no_search_scan_out_iss025`).
- [x] Instantâneo de ordens ativas Collective2 **não** aborta varredura SearchStrategies + histórico fechado; falha do instantâneo é aviso isolado (`collective2_active_orders_snapshot_failed:*`), não critério de elegibilidade Feature 4 (N59 / ISS-024 / F-022; `tests/test_panel_ops.py` `N59Collective2SnapshotIsolationTests.test_n59_empty_allowlist_scan_ok_snapshot_skips_scan_page_ids`, `test_n59_snapshot_414_with_allowlist_does_not_abort_collective2_source`).
- [x] Falha na coleta de histórico fechado Collective2 **depois** de a listagem passar **não** marca a fonte como morta; o que já foi gravado segue no filtro de quinze dias; o aviso é de histórico parcial (não «fonte inteira falhou»); o botão **Atualizar candidatos** sai de «Atualizando…» se a espera estourar (N60 / ISS-024 / F-023; `tests/test_panel_ops.py` `N60PartialClosedTradesCollectTests.test_n60_search_ok_closed_trades_partial_keeps_collective2_source`, `test_n60_search_strategies_http_error_still_collective2_refresh_failed`, `test_n60_candidates_reload_script_has_abort_signal_and_honest_timeout_copy`).
- [x] Sinais e a checagem de vida mostram a versão do painel que está no ar (distinta do pin do vendor; desconhecida se o build não gravou). Falha da listagem Collective2 grava o número do erro e a hora desta tentativa; um aviso antigo de listagem sai quando a nova atualização começa. Falha temporária do servidor tenta a listagem mais uma vez; erro de acesso não. A hora e as fontes que responderam aparecem ao lado do aviso. O botão continua saindo de «Atualizando…» se a espera estourar. Constantes de quinze dias intactas. ISS-024 permanece aberto até homologação (N61 / ISS-024 / F-024; `tests/test_panel_ops.py` `N61Collective2RefreshHonestyTests.test_n61_healthz_and_status_expose_app_git_sha_when_set`, `test_n61_healthz_unknown_when_app_git_sha_unset`, `test_n61_search_strategies_403_codes_issue_single_call`, `test_n61_search_strategies_503_retries_twice_then_succeeds`, `test_n61_start_refresh_strips_stale_listagem_issue_before_search_raises`, `test_n61_banner_meta_without_issues_and_version_line`, `test_n61_abort_controller_and_prodigy_constants_unchanged`).

### Feature 10: Performance

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have

**Critérios de aceite:**
- [x] Resultado por estratégia e total, calculado só a partir de fill confirmado na corretora (`tests/test_panel_ops.py` `PanelOpsDataTests.test_performance_excludes_unfilled_orders` — `strategies[]` por `strategy_key`, ordem sem fill fora do total e do breakdown).
- [x] Ordem sem fill não entra no resultado (`tests/test_panel_ops.py` `PanelOpsDataTests.test_performance_excludes_unfilled_orders`).
- [x] Indicação de quais valores ainda são brutos (sem custo completo) (`tests/test_panel_ops.py` `PanelOpsDataTests.test_performance_excludes_unfilled_orders` — `pnl_label` = `PERFORMANCE_LABEL_GROSS`).

### Feature 11: Sugestões e ajuste supervisionado

- **Persona**: Operador do laboratório
- **Prioridade**: Should-have

**Fluxo principal:**
1. As estratégias encontram oportunidades; o painel mostra como sugestão, com a estratégia de origem.
2. A plataforma registra cada erro (perda, ordem barrada, sinal sem fill) ligado à estratégia.
3. A partir desses registros, o ciclo diário (ISS-012 / N31) produz **dicas rotuladas**; ajuste de parâmetro só na faixa original, via N28.2–4, suggestion-first se a nota for incerta. TimesFM, se disponível, entra só como contexto de pesquisa.

**Critérios de aceite:**
- [x] Sugestão aparece marcada como sugestão e nunca é tratada como ordem autorizada por si só (`tests/test_n28_suggestion_labels.py` `N28SuggestionSurfaceTests.test_command_panel_suggestion_surfaces_self_check`, `test_rank_row_without_ticket_blocks_before_paper_gateway`).
- [x] Ajuste automático só altera parâmetros que já existem na estratégia original, dentro da faixa que ela define (`tests/test_n28_supervised_adjustment.py` `N28SupervisedAdjustmentTests.test_n28_2_in_range_proposal_can_apply`, `test_n28_2_out_of_range_rejected`; catálogo `config/strategy_parameter_catalog.json`).
- [x] Todo ajuste fica registrado com antes, depois e motivo, e pode ser desfeito pelo painel (`tests/test_n28_supervised_adjustment.py` `N28SupervisedAdjustmentTests.test_n28_3_apply_undo_persist_before_after_reason`; API Central `POST /api/strategy-parameters/{propose,apply,undo}`).
- [x] Ajuste automático nunca altera as âncoras de risco (`tests/test_n28_supervised_adjustment.py` `N28SupervisedAdjustmentTests.test_n28_4_never_mutates_risk_anchors`).

---

## 5. Integrações

| Sistema | Tipo | Direção | Autenticação | Fallback |
|---|---|---|---|---|
| Dados públicos de ação e cripto (Yahoo e Binance citados no MVP) | API de leitura | Entrada | Nenhuma no MVP de pesquisa | Ciclo marcado como falho ou parcial. Sem ordem. |
| Alpaca Paper | API de corretora paper (cripto + ação US já ligada) | Bidirecional | Chave paper, fora do repositório | Sem chave, não há submit. Nunca usar chave live. B3 e forex **não** usam este host. |
| Clear Smart Trader (simulado) | API de corretora demo B3 | Bidirecional | API_KEY / SECRET / RSA no portal Clear, fora do repositório | Sem credencial simulada, mercado B3 fica barrado com motivo. Nunca apontar URL real com token simulado. |
| OANDA fxTrade Practice | API de corretora demo forex | Bidirecional | Personal access token practice, fora do repositório | Sem conta Practice, mercado forex fica barrado com motivo. Nunca usar host fxTrade live. |
| TradingView | Webhook (ingest); candidatos no painel via escopo mínimo honesto | Entrada | Segredo do webhook | Pedido sem segredo válido é rejeitado no Gate A. Sem API de busca TV no lab — refresh não inventa ranking TV. |
| Collective2 | Pesquisa e cópia paper por lista nomeada; refresh de candidatos **server-side** (ISS-024) | Entrada (poller/CLI/job; painel só dispara job autenticado) | Chave fora do repositório; browser **não** lê chave nem chama HTTP C2 | Lista nomeada padrão vazia; operador nomeia IDs / aprova no painel. Instantâneo de ordens ativas no disco não é ticket. Sem chave → fail-closed no refresh. |
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
- Copiar provedor Collective2 cujo ID numérico **não** esteja na lista nomeada aprovada pelo operador.
- Tratar ranking `eligible`, candidatos de pesquisa ou os dez observados em H10 como aprovados automaticamente para paper-copy.
- Tratar **Atualizar candidatos**, releitura de disco ou job de refresh como fill ou como aprovação de provedor.
- Inventar API/busca TradingView ou fórmula de score que não esteja no código recuperado / Feature 4.
- Sintetizar ticket Gate A / envio paper a partir de instantâneo de ordens ativas Collective2.
- Assinar em lote os dez candidatos históricos de H10 sem nomeação explícita na lista.
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
| 8 | Método do ajuste automático (Feature 11): o que conta como erro, com que frequência ajustar, quando desfazer | Alto | Respondida 2026-11-16 (ISS-012 + TimesFM research-only): erro = fill com perda **ou** ordem/sinal não executado; frequência = ciclo diário (`evolution-daily`); desfazer = N28.3; se scoring incerto → só sugerir. TimesFM é contexto de previsão rotulado (`research_tip`), fail-closed se indisponível, sem autorizar ordem e sem inventar limiar Tá Barato/momentum. Aplicação de parâmetro permanece N28.2–4. |
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
| H10 | Collective2, 10 candidatos, 0 elegíveis | Relato histórico daquele corte; copy fechada até IDs na lista nomeada; elegível no rank ≠ aprovação. |
| H11–H12 | Reconciliação `nf-`/`demo-` e atividades Alpaca reportadas | P&L com a corretora ainda não fechado. |

---

## Histórico de Revisões

| Data | Versão | Alteração | Autor |
|---|---|---|---|
| 2026-10-29 | 0.1 | Versão inicial a partir do adendo de 29/10/2026 e do snapshot importado | Analista de Requisitos (IA) |
| 2026-11-03 | 0.2 | Operação autônoma na conta demo; âncoras de risco confirmadas; central de controle no painel; Features 7–11; cadastro de estratégia nova adiado | Analista de Requisitos (IA) com o operador |
| 2026-11-13 | 0.4 | G-MKT: Clear Smart Trader simulado (B3), Alpaca Paper (cripto), OANDA Practice (forex); integrações e Feature 7 atualizados | Analista de Requisitos (IA) com o operador |
| 2026-11-16 | 0.4 | Dúvida #8 G-AJUSTE respondida (ISS-012): ciclo diário fills+não-fills + TimesFM research-only; Feature 11 critérios 2–4 seguem `[ ]` até N28.2–4 | Planejador N31 (IA) com o operador |
| 2026-11-16 | 0.4 | Feature 11 critérios 2–4 `[x]` após N28.2–4 (`tests/test_n28_supervised_adjustment.py`); closeout papel N33 — sem bump de versão de contrato | Sprint N33 docs |
| 2026-11-19 | 0.7.7 | Feature 9: rascunho de aceite N60 `[ ]` — histórico fechado parcial não derruba a Collective2; botão sai de «Atualizando…»; constantes de quinze dias intactas; ISS-024 permanece aberto | N60 PLAN |
| 2026-11-19 | 0.7.6 | Feature 9: aceite N58 `[x]` — Atualizar varre Collective2 via SearchStrategies + Feature 4/15d (disco = cache); TV varredura OUT ISS-025; F-021 corrigido (`N58Collective2SearchStrategiesScanTests`; ISS-024 aberto) | N58.3 docs |
| 2026-11-19 | 0.7.5 | Feature 9: rascunho de aceite N58 `[ ]` — Atualizar varre Collective2 nas regras 15d (não inventário em disco); TradingView varredura OUT até ISS-025; ISS-024 permanece aberto | N58 PLAN |
| 2026-11-19 | 0.7.4 | Feature 9: aceite N57 `[x]` — fila Collective2 a partir de arquivos brutos canônicos sem allowlist como pré-requisito de visibilidade; cópia paper continua na lista nomeada/ledger; F-020 corrigido (nodeids `N57Collective2RawQueueDiscoveryTests`; ISS-024 aberto) | N57.3 docs |
| 2026-11-19 | 0.7.3 | Feature 9: aceite N56 `[x]` — join canônico `providers/raw` no job live-criteria; fila Prodígio só elegíveis 15d; F-019 corrigido (nodeids `N56ProdigyCanonicalRawPathTests`; ISS-024 aberto) | N56.3 docs |
| 2026-11-18 | 0.7.2 | Feature 9: aceite N55 — fila com elegíveis de Collective2+Prodígio+TradingView; falha parcial não oculta outras fontes; Prodígio vazio documenta arquivos brutos (ISS-024 follow-up; N54 #73 em main) | N55 PLAN |
| 2026-11-18 | 0.7.1 | Feature 9: aceite N54 marcado `[x]` com nodeids `N54LiveCriteriaRefreshHttpTests` / `N53PanelShellRefreshTests` (frente EXECUTE; sem fechar ISS-024) | N54.4 docs |
| 2026-11-18 | 0.7 | Feature 9: objetivo/fluxo Sinais (candidatos→decisão→operação→inventário); aceite ISS-024 critérios ao vivo; Feature 4 + §5/§7 alinhados (refresh ≠ fill; TV escopo mínimo; C2 server-side) | Analista (Rock campanha Sinais) |
| 2026-11-17 | 0.6 | Feature 4: pré-aprovação no painel + `signal_provider_approvals`; JSON/env C2 = semente; métricas rank reutilizadas; aprovação ≠ fill | Sprint N51 ISS-021 |
| 2026-11-17 | 0.5 | Feature 4 Collective2: lista nomeada (padrão vazia); §5 painel sem API C2; §7 proíbe copy fora da lista e ticket a partir de snapshot; H10 permanece histórico | Sprint N50 ISS-020 |
