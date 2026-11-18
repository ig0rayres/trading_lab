# Issues — Trading Lab

## ISSUES-INDEX

| ID | Status | Sprint | Título |
|----|--------|--------|--------|
| ISS-001 | fechado | N6 | Imagem EasyPanel sem psycopg e sem vendor pinado |
| ISS-002 | fechado | N7 | Catálogo de estratégias sem persistência nem Gate B |
| ISS-003 | fechado | N8 | `strategy_states` vazia após `ledger-migrate apply` |
| ISS-004 | fechado | N11 | Feature 1 — critérios de ciclo research ainda `[ ]` em REQUIREMENTS |
| ISS-005 | fechado | N12 / N20 | Feature 5 — fill AAPL 2026-10-29 + posição; P-001b fechado 2026-11-11 |
| ISS-006 | fechado | N14 | Pacotão MVP-DEMO-1.0 — runbook único + smoke + política deploy |
| ISS-007 | aprovado | N15–N17 | Épico único **MVP-OP** (0.9 → 1.0 → 1.1) + **Command Panel v1** (`v4_web_dashboard`) |
| ISS-008 | fechado | N18 | Command Panel always-on (`v4-ops`) — fim do nohup manual |
| ISS-009 | aberto | N19 | Laço demo em B3, cripto e forex, com gatilhos no painel |
| ISS-010 | aberto | N29 | Adapters demo G-MKT: Clear (B3), Alpaca (cripto), OANDA (forex) |
| ISS-011 | aberto | ISS-010 B3/FOREX + N17.2 G-FORM (pós-N33) | Épico contrato Features 7–11 (Alpaca-only; sem Clear/OANDA) |
| ISS-012 | fechado (N31 merged PR #38; N28.2–4 entregues nesta frente) | N31/N28 | G-AJUSTE: melhoria contínua diária + TimesFM research-only + ajuste supervisionado Feature 11 |
| ISS-013 | aberto | N36 | Copy do freio na Central: Ligar/Desligar parada parece ligar o sistema |
| ISS-014 | fechado | N37 (closeout papel **N39**) | Saúde automática da plataforma + defaults operacionais ON |
| ISS-015 | fechado | N38 | Estado visual do freio na Central: dois botões iguais e faixa sempre amarela |
| ISS-016 | aberto | N40 | Orientação no painel: mapa «onde está cada coisa» (docs; não é tela de ordens) |
| ISS-017 | aberto | N41+ / N42 / N43 / N44 | Épico: entrega do painel operacional completo (campanha pós-N40) |
| ISS-018 | fechado | N48 | Alinhar a tela Sinais ao conceito de cópia de terceiros |
| ISS-019 | aberto | N49 | Sinais: proveniência ordem↔sinal, inventário/assinaturas, critérios + pool Prodígio |
| ISS-020 | aberto | N50 | Habilitar Collective2 + reorganizar tela Sinais; Prodígio provider None |
| ISS-021 | aberto | N51 | Pré-aprovação manual no painel + métricas de decisão (qualquer fonte) |
| ISS-022 | aberto | N52 | Redesign UX Sinais + planejamento visual do painel operacional |
| ISS-023 | aberto | N53/N54 | Botão refresh candidatos + redesign visual completo do painel |
| ISS-024 | aberto | N55 (#74 em main) | Critérios ao vivo: código mergeado; homologação operador pendente |

## Release train MVP-OP (visão alvo operacional)

> Plano **`/pmo plan MVP-OP-1.0`** 2026-11-02 · merge PR #13 · **Sem código N16+** até **MVP-OP-0.9** (N15) fechado.  
> **`LIVE_TRADING_ENABLED=false`** em todas as releases. Sem limiar inventado. Sem C2 copy sem `approved_for_paper_copy`.

| Release | Objetivo (operador vê funcionando) | Deploy EasyPanel | Issue / sprint |
|---------|-----------------------------------|------------------|----------------|
| **MVP-OP-0.9** | Cópia sinais **paper submit homologado** (`signal_copy` → Alpaca `PAPER_SUBMITTED`); Feature 5 fill `[ ]` até execução limit; ISS-005 parcial | **Não** (sessão operador) | N15 · P-001b |
| **MVP-OP-1.0** | **Prodígio** paper homologado + **painel único** (histórico, performance paper, ordens abertas, oportunidades rank, saúde/limites, fases catálogo, melhoria contínua, tips rotuladas research) | **1 rebuild** / release tag | N16 · ISS-007 |
| **MVP-OP-1.1** | **Tá Barato** (+ momentum se upstream): shadow/paper homolog; **painel** estende família `ta_barato` | **1 rebuild** se `src/` | N17 |

### Command Panel v1 — mapa de áreas (épico ISS-007, entrega **1.0**)

| Área do painel | Fonte (reuse) | Release |
|----------------|---------------|---------|
| Histórico / ledger read-only | Postgres ledger + reconcile | 1.0 |
| Performance (PnL paper) | `paper_fills` + Alpaca read-only | 1.0 (credível após 0.9 fill) |
| Ordens abertas / fila | `paper_gateway` + Alpaca paper API | 1.0 |
| Oportunidades | `prodigy-rank` / research (sem autorizar ordem) | 1.0 |
| Saúde financeira | Gate B, capital, kill switch | 1.0 |
| Estratégias adotadas / fase | `strategy_states` + catálogo | 1.0 |
| Melhoria contínua | `evolution-daily`, `decisions.jsonl` | 1.0 |
| Tips / sugestões | Rotuladas **research**; nunca ordem automática | 1.0 |
| Tá Barato no painel | Mesma UI, família upstream | **1.1** |

> **N40 (2026-11-17):** este quadro é a **promessa** MVP-OP-1.0, não o clique do dia a dia. O menu após login (Central / Sinais / Prodígio / Performance) é outra superfície HTML. Mapa honesto → sprint **N40** / **ISS-016**. Não fecha este épico. Não é a tela de ordens.

> **N41 / ISS-017 (2026-11-17):** campanha «operar pelo painel» (`docs/.briefs/CAMPAIGN-PLATFORM-DELIVERY.brief.md`). **N41 entregue:** menu **Ordens** (`/ordens`) e **Histórico** (`/historico`) com listas ou vazio honesto; painel **sem** submit de ordem. **ISS-017 permanece aberto** (campanha). Catálogo de fases, TimesFM visível, Tá Barato, Clear e OANDA ficam nas ondas seguintes — **não** fecha ISS-007 / ISS-010 / ISS-011 nesta onda.

> **N42 / ISS-017 (2026-11-17):** onda 2 **entregue** — menu **Estratégias** (`/estrategias`) só leitura (chave / fase / paper permitido); vazio `Catálogo indisponível (ledger)`; **sem** promoção de fase na tela nova. **ISS-017 permanece aberto** (campanha). TimesFM, Tá Barato, Clear e OANDA ficam nas ondas seguintes — **não** fecha ISS-007 / ISS-010 / ISS-011 nesta onda.

> **N43 / ISS-017 (2026-11-17):** onda 3 **entregue** — menu **Análise Google** (`/analise-google`) só pesquisa; fail-closed `Análise Google indisponível: modelo ou dependência ausente.` quando o modelo falta; **não** autoriza ordem; **sem** POST de ordem. **ISS-017 permanece aberto** (campanha). Tá Barato, Clear e OANDA ficam nas ondas seguintes — **não** fecha ISS-007 / ISS-010 / ISS-011 nesta onda.

> **N44 / ISS-017 (2026-11-17):** onda 4 runbook **publicado** — `docs/HOMOLOGATION.md` § passeio menu US+cripto; evidência **pendente** em `docs/TEST-EVIDENCE.md` § Sprint N44. **Passeio operador não feito** nesta entrega. Pytest / fill AAPL 2026-10-29 **não** fecham onda 4. **ISS-017 permanece aberto** até critério de fechamento do épico. **Não** fecha ISS-007 / ISS-010 / ISS-011.

> **Sem N18 separado:** dashboard não é épico paralelo; estende `src/v4_web_dashboard.py` + dados existentes (Feature 6), bearer remoto invariável.

### Critérios “pronto” por tema (MVP-OP-1.0+)

| Tema | Pronto quando |
|------|----------------|
| Cópia de sinais | 0.9: submit `signal-paper` evidenciado (2026-11-02); fill limit na corretora **pendente** (`REQUIREMENTS` fill `[ ]`) |
| Sinais Prodígio (rodízio) | Top-N do `prodigy-rank` mapeado → ingestão com `strategy_key=prodigy_15d`; ≥1 fill paper evidenciado; fase `paper_limited` **só** operador |
| Tá Barato | 1.1 — fórmulas upstream em vendor; homolog; **não** em 1.0 |
| Estratégias adotadas | Runbook promoção + dashboard fase; sem promoção por PnL/HTTP 200 |
| Melhoria contínua | `evolution-daily` + `decisions.jsonl` + checklist semanal operador |
| Ordens não realizadas | Matriz clara: research/shadow=0; paper=só fill ou rejeição broker registrada |

---

## Pendências operacionais (MVP demo)

> Atualizado: operador N12.4 submit 2026-11-02 · Feature 5 fill `[ ]` mantido (ordem MSFT limit **new**, filled qty 0).

| ID | Item | Responsável | Bloqueia MVP “operacional”? |
|----|------|-------------|----------------------------|
| P-001a | **N12.4 submit** — `PAPER_SUBMITTED`, `orders_sent=1`, jsonl `SUBMITTED`, ordem Alpaca paper visível | Operador | **Não** (trilha demo submit) |
| P-001b | **Feature 5 fill** — AAPL buy @349.85 filled 2026-10-29 + posição qty 1 (evidência 2026-11-11) | Operador | **Fechado** (`REQUIREMENTS` fill `[x]`) |
| P-002 | **N12.5 docs** — `TEST-EVIDENCE` § N12 operador (sem marcar fill `[x]` até P-001b) | Docs | Parcial (este PR) |
| P-003 | **Reconcile** — `v4-alpaca-reconcile` + `ledger_apply` (one-shot não grava `paper_orders` Postgres) | Operador | Parcial (`linked:0` esperado no caminho jsonl) |
| P-004 | **F-003** orb-parity | Backlog | Não (demo `signal_copy`) |
| P-005 | **Momentum / Tá Barato / Prodigy** — homolog paper | Backlog upstream | Sim para “multi-estratégia”; **não** para demo única |

**Não conta como P-001a fechado:** deploy EasyPanel, `queued_intent`, HTTP 202, CI verde, pytest mock `PAPER_SUBMITTED` **sem** sessão operador redigida.

**Não conta como P-001b fechado:** ordem **`new`** / **`accepted`** sem fill; reconcile com atividade FILL de outro símbolo/data.

---

## ISS-001 — Imagem EasyPanel sem psycopg e sem vendor pinado

| Campo | Valor |
|-------|--------|
| Categoria | improvement |
| Sprint | N6 |
| Status | fechado |

**Impacto:** Redeploy perde clone manual em `/app/vendor`; `ledger-migrate` e `load_original()` falham sem `pip install` ad hoc.

**Critério de fechamento:** `docker build` inclui `psycopg[binary]` e vendor @ SHA em `docs/VENDOR-PIN.md`; CI docker-build smoke verde; docs EasyPanel descrevem rebuild dos dois apps sem overlay vazio em `/app/vendor`.

**Fontes:** operador homologação 2026-10-30; `docs/ROADMAP.md` backlog N; `/pmo plan` + Rock PLAN.

---

## ISS-002 — Catálogo de estratégias sem persistência nem Gate B

| Campo | Valor |
|-------|--------|
| Categoria | enhancement |
| Sprint | N7 |
| Status | fechado |

**Impacto:** `strategy_states` existe no DDL e no DBML, mas o ledger não lê fase e o Gate B autoriza paper sem consultar o catálogo. `paper_gateway_queue` grava `strategy_key='signal_copy'` para qualquer sinal. ORB poderia ser tratado como paper principal. Feature 4 permanece com critérios em aberto.

**Critério de fechamento:** fases persistidas (research/shadow/paper_limited/paper_validated) com seed insert-if-missing; Gate B recusa research/shadow e ORB não selecionável; `strategy_key` no sinal (worker + HMAC ALLOWED); `risk_decisions.strategy_key` deixa de ser literal hardcoded; pytest unitário + integração ledger; nenhum limiar inventado de momentum/Tá Barato/Prodigy; `LIVE_TRADING_ENABLED` false.

**Fontes:** operador `/pmo plan N7` 2026-10-30; `docs/REQUIREMENTS.md` Feature 4; `docs/ARCHITECTURE.md` strategy-catalog / risk-gate-b; `docs/ROADMAP.md` próximo passo N7.

---

## ISS-003 — `strategy_states` vazia após `ledger-migrate apply`

| Campo | Valor |
|-------|--------|
| Categoria | improvement |
| Sprint | N8 |
| Status | fechado |

**Impacto:** `migrations/001_ledger_up.sql` cria `strategy_states` sem seed. `ledger_migrate.apply()` só aplica DDL e retorna cedo em `already_applied`. `ensure_strategy_defaults()` existe em `src/strategy_catalog.py` mas só corre no caminho de leitura (Gate B / `fetch_strategy_phase`). EasyPanel ficou sem as 7 linhas até INSERT manual ou worker. Homologação não é reprodutível só com migrate.

**Critério de fechamento:** `ledger-migrate apply` (incluindo `already_applied`) chama `strategy_catalog.ensure_strategy_defaults()`; pytest de roundtrip com `LEDGER_DATABASE_URL` deixa 7 linhas em `strategy_states`; runbook em `docs/HOMOLOGATION.md` + nota EasyPanel em `docs/INFRASTRUCTURE.md` / `EASYPANEL.md`; seed insert-if-missing (não overwrite); sem migration `002`; sem reabrir Gate B nem Feature 4 scoring; `LIVE_TRADING_ENABLED` false.

**Fontes:** operador `/pmo plan` opção A 2026-10-30; ISS-002 fechado; evidência EasyPanel: tabela vazia até seed manual.

**Fechamento:** PR #4 merge `81e6e88` em `main`; CI verde; homolog EasyPanel 2026-10-30 — `SELECT strategy_key, phase FROM strategy_states WHERE deleted_at IS NULL` com 7 linhas (fases N7: `signal_copy=paper_limited`, `orb`/`mean_reversion=shadow`, demais `research`).

---

## ISS-004 — Feature 1 critérios abertos (ciclo research / manifesto)

| Campo | Valor |
|-------|--------|
| Categoria | improvement |
| Sprint | N11 |
| Status | fechado |

**Impacto:** `docs/REQUIREMENTS.md` Feature 1 mantém `[ ]` em “ciclo sem ordem com live desligado” e “ciclo falho não deixa manifesto anterior como sucesso confiável”, apesar de cobertura parcial em `tests/test_v4_scheduler.py`, `test_v4_run_once.py` e `test_v4_report_integrity.py`. Operador não consegue fechar MVP research só pela folha de requisitos.

**Critério de fechamento:** matriz de evidência em `docs/TEST-EVIDENCE.md`; teste de integração scheduler `--once` + falha remove `v4_manifest.json` quando aplicável; ambos checkboxes Feature 1 `[x]` com referência a nodeids pytest; CI verde; sem novo caminho de ordem; `LIVE_TRADING_ENABLED` false.

**Fontes:** operador `/pmo plan` N11 Feature 1 2026-11-01; `docs/REQUIREMENTS.md` § Feature 1; `docs/PROJECT-BRIEF.md` BOM-1.

**Fechamento:** Sprint N11 — matriz em `TEST-EVIDENCE.md`; `test_main_once_failure_clears_stale_manifest`; REQUIREMENTS Feature 1 critérios `[x]` (2026-11-01).

---

## ISS-005 — Feature 5 demo Alpaca paper (`signal_copy`, pivot P0)

| Campo | Valor |
|-------|--------|
| Categoria | improvement |
| Sprint | N12 / N20 |
| Status | fechado |

**Impacto:** D1–N11 entregaram gates, ledger e homologação D5 (itens 3–7). **Submit paper** `signal_copy` homologado em 2026-11-02. **Fill + posição:** AAPL 2026-10-29 filled qty 1 + posição aberta — Feature 5 fill `[x]` (N20.3/N20.4, 2026-11-11). MSFT/NVDA sem fill não contam.

**Critério de fechamento:** trilha **`signal_copy`** via módulos existentes (`signal_paper_runner.py`, `paper_gateway_queue.process_after_gate_b`, `scripts/run.sh signal-paper`); runbook Feature 5 em `docs/HOMOLOGATION.md`; matriz pytest + linha operador redigida em `docs/TEST-EVIDENCE.md`; operador registra fill paper Alpaca + reconcile coerente (sem segredos no Git); checkbox Feature 5 fill `[x]` **somente** após evidência operador; `LIVE_TRADING_ENABLED` false; Collective2 permanece reprovado; **não** promover ORB/mean a paper principal.

**Evidência operador 2026-11-02 (redigida):** preview `PREVIEW_ONLY`; submit `PAPER_SUBMITTED` `orders_sent=1`; `client_order_id` `nf-54c50327…`; broker id `8dcfa34f…`; Alpaca paper ordem MSFT buy limit @420 qty 1 status **new** (filled 0); jsonl `/app/reports/paper/signal-orders.jsonl` estados `ATTEMPTED_UNKNOWN`→`SUBMITTED`; reconcile `ledger_apply` `linked:0` `skipped:1` (FILL histórico AAPL no bundle; one-shot não popula `paper_orders` Postgres).

**Fontes:** operador `/pmo plan pivot-demo` 2026-11-02; `docs/REQUIREMENTS.md` § Feature 5; `docs/HOMOLOGATION.md` passo opcional Feature 5; ISS-005 aprovado no plano PMO.

**Evidência operador 2026-11-11:** UI Alpaca — AAPL buy limit @349.85 filled 2026-10-29 qty 1; posição AAPL qty 1 avg 349.85; Exec `AAPL qty 1`. P-001b fechado. Tentativa nova AAPL `n20-fill-001` → `DUPLICATE_SYMBOL` (correto).

**Pendências detalhadas:** P-001b fechado; P-003 parcial permanece.

---

## ISS-006 — Pacotão MVP-DEMO-1.0 (runbook + smoke + deploy policy)

| Campo | Valor |
|-------|--------|
| Categoria | improvement |
| Sprint | N14 |
| Status | fechado |

**Impacto:** Dezenas de builds CI/deploy sem percepção de plataforma operacional; falta artefato único de release e regra “doc-only não rebuild”.

**Critério de fechamento:** `docs/MVP-DEMO-RUNBOOK.md`; `config/mvp-demo.env.example`; `scripts/mvp-demo-smoke.sh` executável; ROADMAP N14; pendências P-001–P-003 registradas; política deploy §5 runbook; CI verde; **ISS-006 fechado no repo** — ISS-005 permanece aberto até P-001–P-002.

**Fechamento:** merge #12 `9aaac77`; operador smoke OK 2026-11-02.

**Fontes:** operador 2026-11-02 — levantamento master + pacotão único.

---

## ISS-007 — Release train MVP-OP (0.9 → 1.0 → 1.1)

| Campo | Valor |
|-------|--------|
| Categoria | enhancement |
| Sprint | N15–N17 (planejado) |
| Status | planejado |

**Impacto:** Operador precisa de **uma versão** onde copy, Prodígio, catálogo, melhoria contínua e ordens paper façam sentido juntos — sem sequência infinita de deploys por doc.

**Critério de fechamento (epic):** releases **MVP-OP-0.9**, **1.0**, **1.1** conforme § Release train MVP-OP; cada release com gate mensurável em `docs/ROADMAP.md`; no máximo **1 rebuild EasyPanel** por release minor (1.0, 1.1); Git First antes de N16/N17 (`vendor/` + reuse inventory); `LIVE_TRADING_ENABLED` false.

**Fontes:** operador **`/pmo plan MVP-OP-1.0`** opção B 2026-11-02.

**Aprovação:** operador confirma plano no Git (merge PR plano) antes de `/pmo sprint N16`.

---

## ISS-008 — Command Panel always-on (`v4-ops`)

| Campo | Valor |
|-------|--------|
| Categoria | improvement |
| Sprint | N18 |
| Status | fechado |

**Impacto:** Operador perde painel após restart/deploy porque `v4-dashboard` era processo manual; impede “dashboard operacional” contínuo no hashia.

**Critério de fechamento:** imagem com CMD **`v4-ops`**; supervisor reinicia dashboard; docs `docs/DASHBOARD-OPERATIONS.md` + EASYPANEL alinhados; pytest `test_v4_ops_layout`; operador registra redeploy **sem nohup** + `/api/status` Bearer **200** + log `listening on …:8765`; `LIVE_TRADING_ENABLED=false`.

**Fontes:** operador 2026-11-03 (`/pmo plan`, pacote N18 ops); implementação local `front/n16-8-panel`.

**Evidência 2026-11-10:** log `listening on 0.0.0.0:8765` via `v4-ops`; console `GET /api/status` com bearer **200** e schema `command-panel-v1`; verificação automática do PR #20 verde. Sem token no Git. HTTPS público não reconsultado.

---

## ISS-009 — Laço demo em B3, cripto e forex, com gatilhos no painel

| Campo | Valor |
|-------|--------|
| Categoria | feature-com-dominio |
| Sprint | N19 |
| Status | aberto |

**Impacto:** A plataforma não manda ordem sozinha. O retrato de risco nunca fica verificado e o painel não altera gatilho. Sem isso a conta demo não opera e o operador continua no terminal.

**Critério de fechamento:** ordem só na conta demo do mercado, com fill no ledger; mudança de gatilho pelo painel gravada em `trigger_changes`; conta real sem botão; simulador local não conta como fill; `LIVE_TRADING_ENABLED` false.

**Fontes:** operador 2026-11-03; `docs/REQUIREMENTS.md` v0.3; `docs/ARCHITECTURE.md` seção 12 e ADR-010; `docs/DATABASE.md` seção 6; `docs/api-spec.yaml` 0.2.0.

**Nota 2026-11-13:** G-MKT nomeou corretoras em REQUIREMENTS v0.4; adapters ficam em **ISS-010 / N29**. ISS-009 permanece aberto até Feature 7 por mercado homologada.

---

## ISS-010 — Adapters demo G-MKT: Clear (B3), Alpaca (cripto), OANDA (forex)

| Campo | Valor |
|-------|--------|
| Categoria | feature-com-dominio |
| Sprint | N29 |
| Status | aberto |

**Impacto:** Sem adapters das contas demo escolhidas, N27.2/N27.4 e o laço autônomo (Feature 7) ficam só no papel. B3 e forex não podem ir pela Alpaca (ADR-010).

**Critério de fechamento:** Clear Smart Trader **simulado** (B3) e OANDA fxTrade **Practice** (forex) expõem posição, ordem aberta e fill ao laço; cripto reusa Alpaca paper; mercado sem credencial no env fica visível e barrado com motivo; `LIVE_TRADING_ENABLED=false`; account ids e chaves só no EasyPanel (nunca Git).

**Estado N34 (2026-11-16):** Adaptadores mock existiam desde PR **#32**; sprint **N34** passou a chamar `build_demo_adapter` em `signal_paper_runner.run()` fail-closed (pin B3→`clear_smart_trader_simulated`, FOREX→`oanda_fxtrade_practice`; zero POST Alpaca). Merge produção PR **#45** `3aefd447` / main `7627b45`. `submit_order` nos adaptadores é **symbol/side/qty only** (sem bracket stop/target no envio demo). Pytest mock **não** fecha esta issue — homologação ao vivo permanece **N29.5** (operador).

**Estado N35 (2026-11-16):** Sprint **N35** adiciona `env_presence_report` (nomes `present`/`absent` sem valores) + roteiro em `docs/HOMOLOGATION.md` § G-MKT. **Não** fecha ISS-010; live homolog / «creds ok» permanece **N29.5**. EasyPanel **#46 no ar** ≠ creds preenchidas ≠ fill.

**Fontes:** operador `/analista planejar` + `/pmo plan` 2026-11-13; `docs/REQUIREMENTS.md` v0.4 § Feature 7 G-MKT e § Integrações; ADR-010; ISS-009; N27.2.

---

## ISS-011 — Entregar Features 7–11 do contrato (exceto Clear/OANDA)

| Campo | Valor |
|-------|--------|
| Categoria | enhancement / epic |
| Sprint | N33 closeout Alpaca; restante **ISS-010** / **N17.2** |
| Status | aberto — trilha Alpaca Features 7–11 entregue (N30/N31/N28/N32); **N34** wiring B3/FOREX fail-closed (PR **#45**); EasyPanel tip **#46 no ar** (`d99b332`, atestado operador 2026-11-16, **não é fill**, **não** fecha N29.5). **Restante:** credenciar + homologar Clear/OANDA (**ISS-010** / **N29.5**); homologação shadow→paper Tá Barato (**N17.2** / G-FORM) |

**Impacto:** Feature 7 **US_EQUITY + CRYPTO** conferível em repo (N30.1); **âncoras no laço paper** (N32.1–N32.3) via `control_flags`; B3/FOREX barrados sem adapter **ISS-010**; Prodígio rank→ingest (N30.2) sem promoção automática de fase; Features 8–10 parcialmente `[x]` no contrato (N30.3); Feature 11 código N28/N31 nesta frente; Clear/OANDA permanecem fora.

**Critério de fechamento:** Feature 7 conferível em US/CRYPTO (Alpaca paper) sem ação manual; Prodígio e Tá Barato com caminho paper homologado quando upstream permitir; Features 8–10 critérios fecháveis no painel; Feature 11 (N28) entregue ou blocked com gap documentado; Clear/OANDA **fora** (pendência operador ISS-010/N29.5).

**Campanha (2026-11-16 `/pmo plan`; atualizado N30.4):**

| Ordem | Sprint | Entrega | Estado |
|-------|--------|---------|--------|
| 1 | **N30** | Feature 7 Alpaca US+CRYPTO; Prodígio rank→ingestão sem promover fase; Features 8–10 só com evidência de teste | **concluída** — feat `322318b`; PR **#35** merge `622fbeb` (`2026-11-16T12:47:20Z`); TEST-EVIDENCE N30.1/N30.3b |
| 1c | **N32** | Feature 7: `signal_paper_runner.risk_check` lê `control_flags` (fecha lacuna 10k/50 USD) | **concluída** — PR **#42** merge `d30689b` (`2026-11-16T19:49:34Z`); `test_n32_*` |
| 1b | **N31** | G-AJUSTE método: ciclo diário fills+não-fills + TimesFM research-only (ISS-012) | **concluída** — feat `d1d139a`; PR **#38** merge `681e8c5` (`2026-11-16T17:12:28Z`) |
| 2 | **N17** | Tá Barato shadow homolog + G-FORM blocked; painel `ta_barato_shadow` | **código done** (paper blocked upstream; **N17.2 operador pendente**) |
| 3 | **N28** | Feature 11 ajuste supervisionado | **concluída** — feat `71caca1`; PR **#39** merge `5178fff` (`2026-11-16T17:20:14Z`); bloco histórico não reescrito |
| fora | N29.5 / **ISS-010** | Clear B3 + OANDA Practice | pendência operador |
| fora | N27.4 | Smoke sinal válido → ordem demo | **done** (smoke MSFT paper 2026-11-16; não substituído por pytest) |

**Estratégias (N30.4 — sem promoção nesta sprint):**

| `strategy_key` | Fase | Paper |
|----------------|------|-------|
| `news_first` | research | Não exigido pelo contrato; manifesto/Gate A apenas (`tests/test_news_first_report_audited`) |
| `orb` | shadow | **NEVER_PAPER** — `NEVER_PAPER_KEYS` + Gate B (`tests/test_strategy_catalog`, `tests/test_gate_b_risk`) |
| `mean_reversion` | shadow | **NEVER_PAPER** — idem catálogo |
| `prodigy_15d` | research (default) | Rank→ingest N30.2; ordem só após promoção explícita do operador |

**Pendências operador (somente humano / EasyPanel):**

1. Credenciais e account ids **Clear (B3)** e **OANDA Practice (FOREX)** — EasyPanel; **ISS-010** / sprint N29.5 (fora de N30).
2. ~~Smoke **N27.4**~~ — **concluído** (MSFT `PAPER_SUBMITTED` na sessão real, 2026-11-16 pós-merge #35).
3. Retrato de risco consolidado **≤120s** antes de submit em produção (`V4_PORTFOLIO_SNAPSHOT_STALE` se velho).
4. ~~**Rebuild** EasyPanel~~ — tip **#46 no ar** (`d99b332`, atestado operador 2026-11-16; **não é fill**; cobre N34/#45). Credenciais Clear/OANDA ainda item 1.
5. ~~Definir método **G-AJUSTE** (Feature 11)~~ — **respondido** ISS-012 / N31 (ciclo diário fills+não-fills; TimesFM research-only). N28.2–4 executam o ajuste depois do gate N31; bloco N28 não é reescrito.
6. Promover `prodigy_15d` a paper no banco **somente** com evidência; default continua research.

**Pendências operador (push/CI):**

7. ~~**PR #35**~~ — **merged** (2026-11-16). Closeout Features 8–9: `tests/test_panel_ops.py` + `tests/test_panel_triggers.py` (N30.3b).

**Fora de escopo agora:** adapters Clear B3 e OANDA Practice; `LIVE_TRADING_ENABLED=true`; promover `orb` / `mean_reversion` a paper; inventar scoring; reescrever blocos N17/N28/N29/N30/N31.

**Fontes:** REQUIREMENTS v0.4 Features 7–11 (critério âncora `[x]` N32.3); ROADMAP N22/N30/N32; `docs/TEST-EVIDENCE.md` (N30.1/N30.3, N32.3); pedido operador 2026-11-16 `/pmo plan` + `/rock` sem pausa.

**Nota N33 (2026-11-16, closeout docs):** N28/N30/N31 carimbadas `concluida` no ROADMAP com SHA/PR citados; sprint N33 `concluida` via PR **#43** merge `fe80f161` (`2026-11-16T20:34:39Z`). **ISS-011 permanece aberto** somente para B3/FOREX (**ISS-010**) e **N17.2** (G-FORM / homologação Tá Barato paper). PR **#42** na linha principal; EasyPanel **#42 no ar** = atestado operador, não fill.

**Nota N39 (2026-11-17):** closeout de **ISS-014** / N37 (saúde automática, PR **#52**) é só papel + pytest — **não** fecha o restante do épico; pendências **ISS-010** / **N29.5** e **N17.2** inalteradas.

**Nota headless:** operador ausente; EasyPanel/rebuild e credenciais 3os → `Pendências operador` sem interromper a campanha de código/testes. Brief N30: `docs/.briefs/N30.brief.md`.

---

## ISS-012 — G-AJUSTE: melhoria contínua diária (Feature 11)

| Campo | Valor |
|-------|--------|
| Categoria | feature-sem-dominio / enhancement |
| Sprint | N31 (campanha Feature 11 / N28) |
| Status | fechado — feat `d1d139a`, stamp `84791eb`; PR **#38** merge `681e8c546ab7d6388f8627813e0606a9a347bfee` (`2026-11-16T17:12:28Z`); N28.2–4 entregues `71caca1` / PR **#39** `5178fff` |

**Decisão operador (2026-11-16):** serviço de melhoria contínua que analisa com frequência ordens **executadas e não executadas**; a plataforma se **auto-analisa diariamente** para aprimorar as melhores estratégias (aprendizado a partir do rastro real). Fecha dúvida REQUIREMENTS §9 item **#8** (método do ajuste).

**Adendo operador (2026-11-16):** incluir **TimesFM** (Google — foundation model de séries temporais) no planejamento do ciclo de melhoria contínua, como apoio de previsão/contexto — **não** como autorização de ordem nem limiar inventado de Tá Barato/momentum.

**Guardrails (já no contrato):** sugestão ≠ ordem; não inventar parâmetro/limiar; não afrouxar âncora de risco; antes/depois/motivo + desfazer (ou só sugerir até o operador aplicar); saída TimesFM rotulada research/suggestion.

**Reuse:** `src/evolution_engine.py`, `evolution/decisions.jsonl`, painel `continuous_improvement` (N28.1 labels); TimesFM via pacote/API oficial Google (Git First no plano) — sem reimplementar o modelo.

**Aceite:** job/ciclo diário produz relatório + sugestões rotuladas a partir de fills e não-fills (+ forecast TimesFM quando disponível); nenhum caminho aplica ordem paper só por tip/forecast; N28.2–4 avançam sem inventar scoring; LIVE false; fail-closed se TimesFM indisponível.

**Fontes:** operador `/pmo plan` 2026-11-16 (+ TimesFM); REQUIREMENTS Feature 11 + dúvida #8 (Respondida); ROADMAP N31 (bloco N28 intocado); ISS-011.

**Nota headless:** TimesFM entra na task dedicada **N31.2** (adapter opcional, fail-closed, rótulo `research_tip`). N31.1 = job diário fills+não-fills. N31.3 = desbloqueia caminho N28.2–4 suggestion-first, sem inventar scoring. Brief: `docs/.briefs/N31.brief.md`.

---

## ISS-013 — Copy do freio na Central (Ligar/Desligar parada)

| Campo | Valor |
|-------|--------|
| Categoria | feature-sem-dominio / enhancement |
| Sprint | N36 |
| Status | aberto |
| Impacto | Na Central, «Ligar parada» / «Desligar parada» e «Parada geral ligada» parecem ligar ou desligar o laboratório. O campo já bloqueia ordem demo nova quando verdadeiro; o texto é que confunde. |

**Critério de aceite:** status «Freio de emergência ativo» / «Freio liberado (outros limites ainda valem)»; botões «Ativar freio» (`kill_switch_on=true`) e «Liberar freio» (`kill_switch_on=false`); testes afirmam as frases novas e a ausência das antigas (sem «operação demo permitida» nem «Liberar operação demo»); sem botão Live; `kill_switch_on` e Gate B inalterados; `demo_operation_on` fora desta sprint; `LIVE_TRADING_ENABLED=false`.

**Fontes:** operador `/pmo plan` 2026-11-17 (demanda aprovada); `src/panel_ops_html.py` `render_central_page`; `docs/DASHBOARD-OPERATIONS.md`.

**Nota autopilot:** Passo 3 sem AskQuestion; registro automático. Brief: `docs/.briefs/N36.brief.md`.

## ISS-014 — Saúde automática da plataforma + defaults operacionais ON

| Campo | Valor |
|-------|--------|
| Categoria | feature-com-dominio |
| Sprint | N37 |
| Status | fechado |
| resolved_by | Sprint N37 (PR **#52**); closeout docs N39 |

**Impacto:** Operador depende de checklist manual (EasyPanel, Exec, curl) para saber se painel, worker, webhook e gatilhos estão vivos. A Central mostra “Operando” só pela parada geral, não pela stack.

**Critério de fechamento:** Central e `/api/status` expõem `platform_health`; probes no `v4-ops`; defaults ON no migrate sem apagar OFF do operador; pytest verde; `LIVE_TRADING_ENABLED=false`.

**Evidência:** PR #52; deploy EasyPanel 2026-11-17; Central **Plataforma — semáforo** agregado ok (operador).

**Fontes:** operador 2026-11-17; frente `front/n20-platform-health` → PR #52 (PR #50 fechado).

**correcao:** `src/platform_health.py` (`run_probes`, snapshot em reports); semáforo na Central (`_platform_health_block`) e campo `platform_health` em `build_snapshot` / `GET /api/status`; probes no supervisor `scripts/v4_ops_main.sh`; defaults operacionais ON em `operational_defaults` / migrate sem sobrescrever OFF do operador.

**validacao:** PR [**#52**](https://github.com/ig0rayres/trading_lab/pull/52) MERGED `2026-11-17T13:14:04Z`; feat `76f76b3` `feat(observability): platform health probes and operational defaults (N37)`; follow-up `ae916c6` `test: isolate demo-off gate checks from N37 migrate defaults`; mergeCommit `3bebe1c7d3236690c67533ef916cbc5be3206d92`. Pytest: `tests.test_platform_health.PlatformHealthTests.test_run_probes_writes_snapshot`, `test_webhook_skipped_without_url`, `test_worker_stamp_enables_ok_worker`, `test_stale_queue_degraded`, `test_aggregate_overall_down_beats_degraded`; `BuildSnapshotHealthTest.test_build_snapshot_includes_platform_health`; `tests/test_operational_defaults.py`. Sprint **N39** alinhou ROADMAP/DIARY/TEST-EVIDENCE (docs-only; **não** reutilizar o ID N37).

**Nota N39 (2026-11-17, EXECUTE):** fechar no papel **não** atesta rebuild EasyPanel nem semáforo em produção; pytest verde ≠ fill. Rebuild EasyPanel, **N29.5** e **N17.2** continuam operador. `LIVE_TRADING_ENABLED=false`.

---

## ISS-015 — Estado visual do freio na Central (faixa e um só botão)

| Campo | Valor |
|-------|--------|
| Categoria | feature-sem-dominio / enhancement |
| Sprint | N38 |
| Status | fechado |
| resolved_by | Sprint N38 |
| Impacto | Depois da copy N36, os dois botões ainda parecem iguais, a faixa fica amarela nos dois estados, o status some na linha fraca, e clicar Liberar com o freio já solto parece não fazer nada. |

**Critério de aceite:** faixa `brake-strip--active` (vermelha) com só Liberar freio; faixa `brake-strip--released` (calma) com só Ativar freio; um único `brake-strip__cta` por estado; textos N36 onde ainda forem certos; testes afirmam classe, copy e ausência dos dois botões iguais; sem botão Live; `kill_switch_on` e Gate B inalterados; `demo_operation_on` fora desta sprint; `LIVE_TRADING_ENABLED=false`.

**Fontes:** operador `/pmo plan` 2026-11-17 (demanda aprovada + frontend-design); `src/panel_ops_html.py` `render_central_page`; ISS-013 (copy N36). Colisão de ID: main tomou N37/ISS-014 para saúde; freio renumerado para N38/ISS-015.

**Nota autopilot:** Passo 3 sem AskQuestion; registro automático. Brief: `docs/.briefs/N38.brief.md`.

**correcao:** `render_central_page` — faixa `brake-strip--active` / `brake-strip--released`, um CTA por estado, integração com `_platform_health_block`; testes `tests/test_panel_ops.py` e `tests/test_platform_health.py`.

**validacao:** PR [**#54**](https://github.com/ig0rayres/trading_lab/pull/54) merge; CI test / docker-smoke / docker-build verde; stamp **APROVADA** (24 testes locais panel_ops + platform_health); kill-switch semantics inalteradas; `LIVE_TRADING_ENABLED=false`.

**Histórico:** **ISS-013** (copy N36) não foi fechado neste sprint — entrega de texto N36 permanece referência; estado visual era **ISS-015**.

---

## ISS-016 — Orientação no painel: mapa «onde está cada coisa»

| Campo | Valor |
|-------|--------|
| Categoria | feature-sem-dominio / enhancement / docs |
| Sprint | N40 |
| Status | aberto |
| Impacto | Depois das sprints de freio e saúde, o operador não consegue cruzar o menu do dia a dia com o que o painel único prometeu (ordens abertas, histórico, Tá Barato, melhoria contínua). Parece que «sumiu»; na prática há duas superfícies HTML e várias áreas só em JSON. |

**Mapa (N40 EXECUTE):** [`docs/OPERATOR-PANEL-MAP.md`](OPERATOR-PANEL-MAP.md) — nove áreas, quatro selos, duas superfícies (porta **8765**, serviço `trading-lab` / `v4-ops`). O chamado **permanece aberto** como registro de orientação; **não fecha ISS-007**. A tela de ordens/histórico que este chamado adiou entra na campanha **ISS-017** / sprint **N41** — este ISS-016 continua orientação, não a implementação.

**Critério de aceite:** mapa operador com as nove áreas pedidas; cada linha com onde clicar, fonte, vazio versus com dado, e selo VISÍVEL / VAZIO-COMUM / NÃO-EXISTE-AINDA / SÓ-API-OU-JSONL; as duas superfícies nomeadas (menu após login versus página única); porta 8765 do serviço publicado citada sem hostname inventado; zero `src/`; sem tela de ordens; `LIVE_TRADING_ENABLED=false`.

**Fontes:** operador `/pmo plan` 2026-11-17 opção **2**; `docs/ISSUES.md` mapa ISS-007; `src/panel_ops_html.py` `_nav`; `src/v4_web_dashboard.py` `render_page`; `docs/DASHBOARD-OPERATIONS.md`; ROADMAP N16/N17/N25/N30.

**Nota autopilot:** Passo 3 sem AskQuestion; registro automático. Brief: `docs/.briefs/N40.brief.md`. Não fecha ISS-007 / ISS-011 / ISS-010.

**Nota N41 (2026-11-17):** `docs/OPERATOR-PANEL-MAP.md` atualizado nas áreas **5–6** (Ordens/Histórico **VISÍVEL** no menu); mapa antigo que dizia NÃO-EXISTE-AINDA para essas telas foi corrigido. Implementação da tela foi **ISS-017** / N41 — **ISS-016** continua chamado de orientação, não fecha com N41.

---

## ISS-017 — Entrega do painel operacional completo (campanha pós-N40)

| Campo | Valor |
|-------|--------|
| Categoria | feature-com-dominio / epic |
| Sprint | N41+ (onda 1 **N41** concluída; onda 2 **N42** concluída; onda 3 **N43** concluída; onda 4 **N44** runbook entregue — **passeio operador pendente**; N45–N47 stubs) |
| Status | aberto |

**Impacto:** Depois de muitas sprints o contrato Features 1–11 está quase todo `[x]` em teste, e o operador ainda não opera pelo menu do dia a dia. Faltam listas de ordens abertas e histórico; estratégias/fases e TimesFM não estão nesse menu; B3 e forex esperam credencial. Sem um épico de campanha, cada rodada vira cosmética (mapa, copy, closeout) e a plataforma não fecha.

**Critério de fechamento (epic):** o operador entra no painel (login, sem Exec) e vê estratégias, sinais, ordens abertas, histórico/fills, performance e Prodígio; o caminho de demonstração US+cripto Alpaca paper é acompanhável até fill ou recusa; TimesFM só como pesquisa rotulada (nunca autorização de ordem); B3/Clear e OANDA **não** fecham este épico sem N29.5; `LIVE_TRADING_ENABLED=false`. Folha: `docs/.briefs/CAMPAIGN-PLATFORM-DELIVERY.brief.md`.

**Ondas (não executar todas nesta rodada):**

| Onda | Sprint | Entrega |
|------|--------|---------|
| 1 | **N41** | Ordens abertas + histórico no menu |
| 2 | N42 | Estratégias/fases no menu |
| 3 | N43 | TimesFM / dicas visíveis e rotuladas |
| 4 | N44 | Homologar operar US+cripto pelo painel |
| 5 | N45 | Tá Barato no menu — bloqueado em N17.2 |
| 6 | N46 | B3 Clear — bloqueado em N29.5 |
| 7 | N47 | OANDA Practice — bloqueado em N29.5 |

**Não fecha:** ISS-007 (épico histórico 0.9/1.0/1.1; N41 cobre só duas áreas 1.0), ISS-010, ISS-011, ISS-016, ISS-013. Não inventar limiar. Não live.

**Fontes:** operador 2026-11-17 (plano-mestre da plataforma por contrato); `docs/REQUIREMENTS.md` Features 1–11; ISS-007 / ISS-009 / ISS-010 / ISS-011 / ISS-016; `docs/OPERATOR-PANEL-MAP.md`.

**Nota autopilot:** Passo 3 sem AskQuestion; registro automático. Brief da campanha + `docs/.briefs/N41.brief.md`.

**Nota N41 EXECUTE (2026-11-17):** onda **1** entregue — rotas `/ordens` e `/historico` no menu após login; mapa e `docs/DASHBOARD-OPERATIONS.md` atualizados em N41.4. **Épico permanece aberto** até ondas N42–N47 e critério de fechamento acima. Não fecha ISS-007, ISS-010, ISS-011.

**Nota N42 EXECUTE (2026-11-17):** onda **2** entregue — rotas `/estrategias` e `GET /api/estrategias` no menu após login; mapa área **3** e `docs/DASHBOARD-OPERATIONS.md` atualizados em N42.4. Vazio `Catálogo indisponível (ledger)`; página **sem** controles de promoção de fase; **sem** POST de ordem. **Épico permanece aberto** até ondas N43–N47 e critério de fechamento acima. Não fecha ISS-007, ISS-010, ISS-011.

**Nota N43 EXECUTE (2026-11-17):** onda **3** entregue — rotas `/analise-google` e `GET /api/analise-google` no menu após login; mapa área **9** (`docs/OPERATOR-PANEL-MAP.md`) e `docs/DASHBOARD-OPERATIONS.md` atualizados em N43.4. Vazio `Análise Google indisponível: modelo ou dependência ausente.`; página **sem** envio de ordem; pesquisa **não** autoriza ordem; `LIVE_TRADING_ENABLED=false`. **Épico permanece aberto** até ondas N44–N47 e critério de fechamento acima. Não fecha ISS-007, ISS-010, ISS-011.

**Nota N44 EXECUTE (2026-11-17):** onda **4** runbook **publicado** — `docs/HOMOLOGATION.md` § passeio menu US+cripto; folha pendente `docs/TEST-EVIDENCE.md` § Sprint N44; ponteiros em `docs/DASHBOARD-OPERATIONS.md` e `docs/OPERATOR-PANEL-MAP.md`; **zero** `src/`. Rebuild EasyPanel e **passeio** (sinal → ordem aberta → fill ou recusa → performance) continuam **operador** — **não** declarar campanha fechada nem onda 4 concluída no critério de fechamento sem evidência redigida. Pytest e fill AAPL 2026-10-29 **não** fecham cripto nem substituem o menu. Código só se o passeio provar listas N41 cegas — então STOP/replan, fora desta sprint. **ISS-017 permanece aberto** até critério de fechamento do épico. **Não** fecha ISS-007 / ISS-010 / ISS-011.

**Nota N48 PLAN (2026-11-17):** correção de conceito da tela **Sinais** (ingresso ≠ cópia/operação) registrada em **ISS-018** / sprint **N48**. **Não** é onda 5–7 da campanha (N45–N47 permanecem stubs). **ISS-017 permanece aberto.** **Não** fecha ISS-007 / ISS-010 / ISS-011.

---

## ISS-018 — Alinhar a tela Sinais ao conceito de cópia de terceiros

| Campo | Valor |
|-------|--------|
| Categoria | feature-com-dominio / enhancement |
| Sprint | N48 |
| Status | fechado |
| Impacto | No produto, Sinais = ordens/cópia de terceiros (TradingView / família de cópia / provedores). A tela atual só mostra auditoria de ingresso (origem, destino fila/bloqueado, motivo). O operador não vê o que está sendo copiado, o que opera, nem resultado/ordens/custos por sinal ou provedor — e pode confundir ingresso com fill. |

**Critério de aceite:** `GET /sinais` (mesma rota) com seção de cópia de terceiros e seção de auditoria de ingresso claramente distintas; vazio honesto em português quando não houver cópia em operação; resultado só de fill confirmado, rotulado bruto se o custo não estiver completo; total honesto por família de cópia (ordens paper hoje não têm provedor/`signal_id` — não inventar P&L por sinal/provedor); Collective2 visível como cópia fechada (`approved_for_paper_copy` falso); painel sem POST de ordem; Feature 9 (origem/destino/motivo) permanece; `LIVE_TRADING_ENABLED=false`. Sem superfície paralela. Sem fill inventado.

**Não fecha:** ISS-007, ISS-017, ISS-010, ISS-011, ISS-016. Não arranca N45–N47.

**Fontes:** operador 2026-11-17 (correção: Sinais = copy de terceiros); `docs/REQUIREMENTS.md` Features 4, 9 e 10; `docs/OPERATOR-PANEL-MAP.md` §2; N25/N26/N41.

**Nota autopilot:** Passo 3 sem AskQuestion; registro automático. Brief: `docs/.briefs/N48.brief.md`.

**Nota N48 EXECUTE (2026-11-17):** sprint **N48** entregue em N48.1–N48.3 (tela `/sinais` com seções **Cópia de terceiros** e **Auditoria de ingresso**; `GET /api/signals` estendido; testes `tests/test_panel_ops.py`) e **N48.4** (mapa §2, folha do dia a dia, esta nota, `docs/DIARY.md`, `docs/ROADMAP.md`). Vazios reais: `Nenhuma cópia de terceiro em operação.` · `Sem fills confirmados nesta cópia.` · `Nenhum sinal neste destino.` · Collective2 `Collective2: cópia fechada — nenhum provedor aprovado.`; totais **brutos** por família `signal_copy` (`gross_unverified_costs`) — **sem** P&L inventado por sinal/provedor. **ISS-018 permanece aberto** até o operador confirmar no deploy (rebuild EasyPanel) que a tela no ar bate com o conceito. **Não** fecha **ISS-007** / **ISS-017** / **ISS-010** / **ISS-011**. Rebuild EasyPanel **operador**. N45–N47 não arrancados. `LIVE_TRADING_ENABLED=false`.

**Fechamento (2026-11-17):** operador confirmou EasyPanel no ar + screenshot `/sinais` (cópia AAPL paper + auditoria TradingView). Conceito N48 ok. Lacuna restante (ordem↔`signal_id`, inventário/assinaturas, critérios visíveis, pool Prodígio) → **ISS-019** — **não** reabre ISS-018.

---

## ISS-019 — Sinais: proveniência ordem↔sinal, inventário e critérios (reuso Feature 4/9)

| Campo | Valor |
|-------|--------|
| Categoria | feature-com-dominio / enhancement |
| Sprint | N49 |
| Status | aberto |
| Impacto | Sem vínculo claro ordem paper → sinal de origem, performance por sinal é impossível. Sinais no produto = inventário do que está assinado/em operação + performance + origem + lista; Prodígio deve monitorar candidatos ao pool. Critérios de adoção **já** estão em REQUIREMENTS Feature 4/9 — falta superfície e ligação honesta no painel/ledger. |

**Diretrizes do operador (2026-11-17) — mandatório:**
1. Ordem aberta (paper) deve mostrar **qual sinal** a abriu (`signal_id` / origem) — sem isso não há performance por origem.
2. `/sinais` = inventário: sinais assinados, performance de cada um, origem, lista acessível; Prodígio monitora novos/bons candidatos ao pool (reuso `prodigy-rank` / Feature 9 — sem inventar score).
3. Critérios de adoção **visíveis na feature** — reusar texto já definido (Feature 4: signal copy + Prodigy 15d + fases; Feature 9; C2 fechado; promoção só operador).

**Reuso obrigatório (não reinventar):**
- `docs/REQUIREMENTS.md` Feature 4 (signal copy, Prodigy 15d: janela 15d, ≥5 ops / ≥3 dias, retorno líquido +, drawdown/consistência; fase research default; R$ 20; sem promoção automática; C2 sem `approved_for_paper_copy`).
- Feature 9 (lista origem/destino/motivo; ranking + cópias Prodígio).
- Feature 10 (P&L só de fill confirmado; bruto rotulado).
- Ledger: `risk_decisions.signal_event_id` ↔ `paper_orders`; N48 `copy` bundle; `prodigy_rank` / `prodigy_copied_signals`.
- Sem limiar inventado; `LIVE_TRADING_ENABLED=false`; painel sem POST de ordem.

**Critério de aceite (esboço para o planejador):** painel/API mostram proveniência ordem→sinal; inventário de assinados/em pool com performance só de fill (ou vazio honesto); critérios de adoção Feature 4/9 visíveis; candidatos Prodígio research distintos de paper; Collective2 fechado; testes de regressão painel; sem fill inventado.

**Não fecha:** ISS-007, ISS-017, ISS-010, ISS-011. Não arranca N45–N47.

**Fontes:** operador 2026-11-17 (3 diretrizes); REQUIREMENTS Features 4, 9, 10; ISS-018/N48 (família ok, sem per-signal); OPERATOR-PANEL-MAP §2; `paper_gateway_queue` / `signal_events`.

**Nota autopilot:** Passo 2 fases — requisitos já em Feature 4/9; skip AskQuestion. Passo 3 — registro automático ISS-019.

**Nota N49 PLAN (2026-11-17):** sprint **N49** planejada (`docs/.briefs/N49.brief.md`). Critérios **reusados** de REQUIREMENTS Feature 4, 9 e 10 — não inventados. **Não** fecha ISS-007 / ISS-017 / ISS-010 / ISS-011. Não arranca N45–N47. `LIVE_TRADING_ENABLED=false`.

**Nota N49 EXECUTE (2026-11-17):** frente `front/n27-alpaca-loop` — JOIN ledger `signal_events` + overlay `paper/signal-orders.jsonl`; `/sinais` com colunas Origem/Sinal, inventário fill-only, bloco critérios Feature 4/9/10, pool `_load_prodigy_opportunities` (`research_tip`); `tests/test_panel_ops.py` 55 passed. **Chamado permanece aberto** até rebuild EasyPanel + confirmação visual do operador (mesma política de ISS-018).

**Nota operador (2026-11-17 pós-deploy #67):** N49 no ar; lacunas de UX/C2 → **ISS-020** (não reabre escopo N49 além do bug `provider` vs `provider_id` no pool).

---

## ISS-020 — Habilitar Collective2 + reorganizar Sinais (salada + Prodígio None)

| Campo | Valor |
|-------|--------|
| Categoria | feature-com-dominio / enhancement (+ bug mapeamento Prodígio) |
| Sprint | N50 (não roubar N45–N47) |
| Status | aberto |
| Impacto | Operador quer sinais C2 operando; tela `/sinais` confusa (cópia + audit + inventário + critérios + pool misturados); pool Prodígio mostra Provedor `None`/`NONE` — rank usa `provider_id`, loader lê `provider`. |

**Diretrizes do operador (2026-11-17):**
1. **Habilitar Collective2** (outro marketplace de sinais) — hoje fechado por H10/Feature 4 (`approved_for_paper_copy` falso; 10 candidatos, 0 elegíveis). Plano deve definir processo de aprovação honesto (não flip cego) + superfície no painel; LIVE false.
2. **Reorganizar `/sinais`** — deixar claro o que está **ativo/assinado/operando** vs audit vs candidatos; acabar com a “salada”.
3. **Corrigir Prodígio pool** — `provider` None: bug de campo (`provider_id` → exibir como provedor).

**Ativos hoje (honesto):** canal paper ativo = TradingView / família `signal_copy`; C2 = fechado; Prodígio pool = research-only (e IDs quebrados na UI).

**Reuso:** `src/c2_signal_feed.py`, `c2_history_collect.py`, REQUIREMENTS Feature 4 H10, N49 panel_ops, `prodigy_rank` (`provider_id`), `_load_prodigy_opportunities`. Sem limiar inventado; sem fill inventado.

**Não fecha:** ISS-007, ISS-017, ISS-010, ISS-011. Não arranca N45–N47.

**Fontes:** operador 2026-11-17; REQUIREMENTS Feature 4/H10; `trading_dashboard_data._load_prodigy_opportunities` L180; ISS-019/N49.

**Nota autopilot:** registro automático ISS-020; Passo 2 — requisitos C2 já em Feature 4 (revisar política H10 com plano, não inventar score).

**Nota PLAN N50 (2026-11-17):** sprint **N50** planejada (`docs/.briefs/N50.brief.md`). Política = lista nomeada (padrão vazia). Tela `/sinais` reorganizada em operação vs auditoria vs candidatos. Bug Provedor `None` = `provider_id`. **Não** fecha ISS-007 / ISS-017 / ISS-010 / ISS-011 / ISS-019. N45–N47 intactos. `LIVE_TRADING_ENABLED=false`.

**Nota N50 EXECUTE (2026-11-17):** frente `front/n27-alpaca-loop` — allowlist `config/c2_paper_copy_allowlist.json`; `REQUIREMENTS` v0.5; `/sinais` reordenado (operação → inventário → Collective2 → Prodígio → critérios → auditoria); `provider_id` no pool; `tests/test_panel_ops.py` **60 passed**. **Chamado permanece aberto** até operador preencher lista (se desejar C2), rebuild EasyPanel e confirmação visual.

**Nota operador (2026-11-17):** JSON/env inadequado — lacuna de UX/política → **ISS-021** (pré-aprovação no painel + métricas).

---

## ISS-021 — Pré-aprovação manual no painel + métricas de decisão (todas as fontes)

| Campo | Valor |
|-------|--------|
| Categoria | feature-com-dominio / enhancement |
| Sprint | N51 (não roubar N45–N47) |
| Status | aberto |
| Impacto | Allowlist via JSON/env (N50) é inviável no dia a dia. Operador exige fila de **pré-aprovação** e **aprovar/rejeitar no painel**. Precisa de métricas (assertividade, % ganho, etc.) que **pesem** na decisão — mesmas regras para Collective2, Prodígio, TradingView ou qualquer fonte. |

**Diretrizes do operador (2026-11-17):**
1. Todo **novo candidato** entra em **pré-aprovação**; aprovação **manual no painel** — sem env, arquivo de texto ou rebuild só para nomear ID.
2. Mostrar **índice de assertividade / % ganho / métricas** úteis à decisão (reusar campos do rank/pesquisa quando existirem; não inventar fórmula se não recuperada — rotular research; documentar gap).
3. Regras iguais para **qualquer plataforma de sinais**.

**Reuso:** N50 allowlist (evoluir para persistência + ação autenticada); JSON research C2/Prodígio; Feature 4/9; sessão do painel. LIVE false; aprovação ≠ fill; painel não posta ordem de mercado.

**Não fecha:** ISS-007, ISS-017, ISS-010, ISS-011, ISS-019, ISS-020. Não arranca N45–N47.

**Fontes:** operador 2026-11-17; N50 allowlist; REQUIREMENTS v0.5 Feature 4.

**Nota autopilot:** registro automático ISS-021.

**Nota planejamento (2026-11-17):** sprint **N51** planejada (`docs/.briefs/N51.brief.md`). EXECUTE ainda não rodou.

**Nota N51 EXECUTE (2026-11-17):** frente `front/n27-alpaca-loop` — fila `copy.preapproval` em `/sinais` e `GET /api/signals`; `POST /api/signals/providers` autenticado; migration `003_signal_provider_approvals`; métricas reutilizadas do rank; pytest painel verde. **Chamado permanece aberto** até operador aplicar `003` no Postgres da instância, rebuild EasyPanel e confirmar decisões no ar.

**Nota operador (2026-11-17):** N51 no ar mas UX insuficiente — métricas vitais ausentes na listagem; tela confusa. Redesign + planejamento visual → **ISS-022** (`/designer`).

---

## ISS-022 — Redesign UX Sinais + planejamento visual do painel

| Campo | Valor |
|-------|--------|
| Categoria | feature-com-dominio / design |
| Sprint | N52 (não roubar N45–N47) |
| Status | aberto |
| Impacto | Painel do dia a dia (esp. `/sinais`) não atende tomada de decisão: salada de seções, feia, pouco intuitiva; pré-aprovação sem colunas vitais (acertos, PF, drawdown, score, status). Operador pede **reformulação visual** da tela Sinais e **planejamento visual de toda a plataforma** (menu operacional). |

**Diretrizes do operador (2026-11-17):**
1. Mostrar na avaliação do sinal as métricas já recuperáveis (`win_rate_pct`, `shrunk_win_rate_pct`, `profit_factor_reported`, `reported_pnl_sum`, `net_return_pct`, `max_drawdown_pct`, `prodigy_score`/`score`, `status`) — ausente = indisponível; sem fórmula inventada.
2. Visão clara: o que aprovar, o que opera, o que é só pesquisa/auditoria — hierarquia de decisão, não tabela-salada.
3. Chamar design/UI: reformular `/sinais` e produzir planejamento visual do painel (Central, Sinais, Ordens, Histórico, Estratégias, Prodígio, Performance, …) alinhado a `docs/OPERATOR-PANEL-MAP.md` + Features 8–10.
4. LIVE false; aprovação ≠ fill; sem POST de ordem de mercado.

**Fase pré-código:** `/designer planejar` (ou retrofit) → `docs/design/` (DESIGN.md + mockups). Só depois Sprint N de implementação.

**Não fecha:** ISS-007, ISS-016, ISS-017, ISS-019–021. Não arranca N45–N47.

**Fontes:** operador 2026-11-17 (screenshots pré-aprovação); ISS-021; OPERATOR-PANEL-MAP; REQUIREMENTS Features 8–10.

**Nota autopilot:** registro ISS-022; Passo 2 design **obrigatório** antes de N de UI.

**Nota planejamento (2026-11-17):** Design DONE (`docs/design/DESIGN.md`, `mockups/sinais.md`, `mockups/panel-overview.md`). Sprint **N52** planejada (`docs/.briefs/N52.brief.md`). EXECUTE ainda não rodou. Entrega «finalizado» só após merge no ramo principal.

**Nota N52 EXECUTE (2026-11-17):** `panel_ops_html` cockpit + métricas completas na pré-aprovação; testes painel 75 OK. **Chamado aberto** até merge `main` + rebuild EasyPanel + confirmação visual. «Finalizado» só pós-merge.

**Nota operador (2026-11-18):** #70 no ar; visual ainda **sofrível**; falta botão de refresh de candidatos. Escopo ampliado → **ISS-023** (especialista design + refresh). ISS-022 permanece aberto (N52 parcial).

---

## ISS-023 — Botão refresh de candidatos + redesign visual completo do painel

| Campo | Valor |
|-------|--------|
| Categoria | feature-com-dominio / design |
| Sprint | **N53** (UI PanelShell v2 + `GET /api/signals/reload`) em `front/n27-alpaca-loop` · **N54** (job POST) seguinte |
| Status | aberto — N53 (UI + `GET /api/signals/reload`) merge **#71** em `main` @ `bb103558` (2026-11-18); **N54** job POST (`live_criteria`) **implementado no código** na frente `front/sinais-live-criteria` (2026-11-18) — chamado **permanece aberto** até merge em `main`, rebuild EasyPanel e homologação operador no ar |
| Impacto | Operador precisa **atualizar sugestões de sinais no painel** (hoje só lê JSON estático; sem botão). Visual do menu operacional continua inadequado após N52 — exige **nova estrutura visual** de toda a plataforma (Central, Sinais, Ordens, Histórico, Estratégias, Prodígio, Performance, Análise Google), não só métricas na fila. |

**Diretrizes do operador (2026-11-18):**
1. **Botão** na área de candidatos/pré-aprovação para refrescar sugestões (ação explícita no painel; sem depender de editar disco/cron invisível).
2. **Especialista design** redesenha toda a plataforma — nova estrutura visual (IA + tokens + mockups por rota).
3. LIVE false; refresh **não** autoriza ordem; painel não inventa score; se refresh dispara job, fail-closed e sem chave C2 no browser.

**Fase pré-código:** `/designer planejar` (plataforma inteira) → atualizar `docs/design/`. Depois `/pmo plan` N53+ (UI + refresh).

**Não fecha:** ISS-007, ISS-016, ISS-017, ISS-019–022. Não arranca N45–N47.

**Fontes:** operador 2026-11-18; ISS-022/N52; OPERATOR-PANEL-MAP; `prodigy_rank` / provider-research JSON.

**Nota autopilot:** registro ISS-023; design obrigatório antes de N.

**Nota operador (2026-11-18):** `ledger-migrate apply` no EasyPanel devolveu só `001_ledger` — imagem **sem** código N51/N53 (sem 003). Rebuild necessário para aprovar. Critérios ao vivo TV+C2 (não JSON estático) → **ISS-024**.

**Nota closeout N53 (2026-11-18):** PanelShell v2 em todas as rotas do menu e botão **Atualizar candidatos** com releitura honesta via `GET /api/signals/reload` entregues em `main` (PR **#71**). Chamado **permanece aberto** até job POST (**N54**), homologação operador e rebuild no ar.

**Nota N54 EXECUTE (2026-11-18):** `POST /api/signals/candidates/refresh`, CTA em `/sinais` e `GET /api/signals/reload` com `mode: disk_reread` entregues **no código da frente** `sinais-live-criteria` (pytest `N54LiveCriteriaRefreshHttpTests`). **ISS-023 continua aberto** — merge + painel no ar + confirmação operador ainda pendentes.

---

## ISS-024 — Critérios de candidatos ao vivo (TradingView + Collective2)

| Campo | Valor |
|-------|--------|
| Categoria | feature-com-dominio |
| Sprint | **N55** (`front/sinais-live-criteria`; N54 merge **#73** em `main`; não rouba N45–N47) |
| Status | aberto — N54 job POST (#73) e fila multiplataforma N55 (#74) em `main`; **permanece aberto** até rebuild EasyPanel + homologação operador (fila C2+Prodígio+TV no painel no ar) |
| Impacto | Operador rejeita modelo “ler JSON no disco”. Botão **Atualizar candidatos** deve **aplicar critérios de seleção** nas plataformas e trazer **todos os candidatos elegíveis** (Collective2, Prodígio e TradingView); não basta reler `prodigy-top10` / `provider-research` estáticos nem mostrar só uma origem TradingView sem métricas. |

**Diretrizes do operador (2026-11-18):**
1. Aprovar entrada de sinais no painel exige ledger **003** no ar (rebuild + migrate com código atual).
2. Refresh/candidatos = critérios aplicados **direto nas plataformas** (TV + C2), não “nada que ficar lendo disco” como fonte da verdade.
3. Reusar critérios Feature 4 / Prodígio 15d já definidos; sem fórmula inventada; LIVE false; refresh ≠ ordem; chave C2 só server-side.

**Nota operador 2026-11-18 (follow-up N55, após N54 #73):** depois de **Atualizar candidatos**, a fila de pré-aprovação deve mostrar **todos os candidatos de todas as plataformas** (Collective2, Prodígio, TradingView) que **já atendem** Feature 4 / Prodígio 15d. Não apenas uma origem TradingView com métricas indisponíveis. Falha honesta e fechada quando uma fonte não roda (ex.: chave Collective2 ausente): o aviso descreve o problema, mas **não** oculta as linhas elegíveis das outras plataformas. Preservar a pesquisa anterior se uma fonte falhar (intenção N54). Se Prodígio raw/rank estiver vazio, documentar o que falta (arquivos brutos dos provedores) — **não** inventar score nem API de busca TradingView. LIVE false; aprovar ≠ fill; atualizar ≠ ordem; chave Collective2 só no servidor.

**Não fecha:** ISS-007, ISS-017, ISS-019–023. Não arranca N45–N47.

**Fontes:** operador 2026-11-18; ISS-023 N53 GET reload; REQUIREMENTS Feature 4; `prodigy_rank` / `c2_signal_feed`.

**Nota autopilot:** registro ISS-024.

**Nota planejamento N54 (2026-11-18):** bloco `## Sprint N54` em `docs/ROADMAP.md`; brief `docs/.briefs/N54.brief.md`. Chamado permanece **aberto** até job POST + testes + merge + rebuild operador.

**Nota N54 EXECUTE (2026-11-18):** job POST critérios ao vivo, botão Sinais e contrato dual GET/POST codificados na frente `sinais-live-criteria`; `tests/test_panel_ops.py` cobre sessão, cooldown, `live_criteria` vs `disk_reread`, `orders_sent=0`. Merge **#73** em `main` (2026-11-18). **Não** fecha o chamado: a fila no painel ainda não prova elegíveis das três plataformas.

**Nota planejamento N55 (2026-11-18):** follow-up ISS-024; bloco `## Sprint N55` em `docs/ROADMAP.md`; brief `docs/.briefs/N55.brief.md`. Chamado permanece **aberto** até fila multiplataforma + testes + merge + rebuild operador.

**Nota N55 EXECUTE (2026-11-18):** frente `sinais-live-criteria` — fila união Collective2+Prodígio+TradingView após refresh; `partial` persiste em `copy.candidates_refresh` (`intelligence/candidates-refresh-latest.json`); banner em `/sinais`; Prodígio vazio não sobrescreve JSON; `provider-research` C2 não recebe dump Prodígio; F-018 corrigido. Suíte `N55MultiPlatformLiveCriteriaTests` (7) verde; `tests/test_panel_ops.py` verde na frente.

**Nota closeout N55 (2026-11-18):** PR **#74** MERGED → `main` @ `d8870c281a5b87e1e22871632a50e23868ba0c7b`; CI test + docker-smoke + docker-build SUCCESS; sprint N55 Status `concluida` no ROADMAP. Chamado **permanece aberto**: operador deve rebuild EasyPanel (`trading-lab` / `v4-ops`), conferir migration **003** no ledger, montar volume **`reports/providers/raw/`** para Prodígio e definir **`C2_API4_KEY`** no servidor — depois clicar **Atualizar candidatos** em `/sinais` e confirmar fila das três plataformas + avisos parciais honestos. `LIVE_TRADING_ENABLED=false`.

---