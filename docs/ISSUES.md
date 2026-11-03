# Issues — Trading Lab

## ISSUES-INDEX

| ID | Status | Sprint | Título |
|----|--------|--------|--------|
| ISS-001 | fechado | N6 | Imagem EasyPanel sem psycopg e sem vendor pinado |
| ISS-002 | fechado | N7 | Catálogo de estratégias sem persistência nem Gate B |
| ISS-003 | fechado | N8 | `strategy_states` vazia após `ledger-migrate apply` |
| ISS-004 | fechado | N11 | Feature 1 — critérios de ciclo research ainda `[ ]` em REQUIREMENTS |
| ISS-005 | parcial | N12 | Feature 5 — submit paper ok; fill limit pendente (P-001b) |
| ISS-006 | fechado | N14 | Pacotão MVP-DEMO-1.0 — runbook único + smoke + política deploy |
| ISS-007 | aprovado | N15–N17 | Épico único **MVP-OP** (0.9 → 1.0 → 1.1) + **Command Panel v1** (`v4_web_dashboard`) |
| ISS-008 | aberto | N18 | Command Panel always-on (`v4-ops`) — fim do nohup manual |

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
| P-001b | **Feature 5 fill** — execução limit + posição coerente (ou cancel + novo sinal marketable) | Operador | **Sim** (`REQUIREMENTS` fill `[ ]`) |
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
| Sprint | N12 |
| Status | parcial |

**Impacto:** D1–N11 entregaram gates, ledger e homologação D5 (itens 3–7). **Submit paper** `signal_copy` homologado em 2026-11-02 (`PAPER_SUBMITTED`, ordem Alpaca MSFT limit **new**). Critério **fill + posição** em `docs/REQUIREMENTS.md` permanece `[ ]`.

**Critério de fechamento:** trilha **`signal_copy`** via módulos existentes (`signal_paper_runner.py`, `paper_gateway_queue.process_after_gate_b`, `scripts/run.sh signal-paper`); runbook Feature 5 em `docs/HOMOLOGATION.md`; matriz pytest + linha operador redigida em `docs/TEST-EVIDENCE.md`; operador registra fill paper Alpaca + reconcile coerente (sem segredos no Git); checkbox Feature 5 fill `[x]` **somente** após evidência operador; `LIVE_TRADING_ENABLED` false; Collective2 permanece reprovado; **não** promover ORB/mean a paper principal.

**Evidência operador 2026-11-02 (redigida):** preview `PREVIEW_ONLY`; submit `PAPER_SUBMITTED` `orders_sent=1`; `client_order_id` `nf-54c50327…`; broker id `8dcfa34f…`; Alpaca paper ordem MSFT buy limit @420 qty 1 status **new** (filled 0); jsonl `/app/reports/paper/signal-orders.jsonl` estados `ATTEMPTED_UNKNOWN`→`SUBMITTED`; reconcile `ledger_apply` `linked:0` `skipped:1` (FILL histórico AAPL no bundle; one-shot não popula `paper_orders` Postgres).

**Fontes:** operador `/pmo plan pivot-demo` 2026-11-02; `docs/REQUIREMENTS.md` § Feature 5; `docs/HOMOLOGATION.md` passo opcional Feature 5; ISS-005 aprovado no plano PMO.

**Pendências detalhadas:** § Pendências operacionais (MVP) — P-001b, P-003 parcial.

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
| Status | aberto |

**Impacto:** Operador perde painel após restart/deploy porque `v4-dashboard` era processo manual; impede “dashboard operacional” contínuo no hashia.

**Critério de fechamento:** imagem com CMD **`v4-ops`**; supervisor reinicia dashboard; docs `docs/DASHBOARD-OPERATIONS.md` + EASYPANEL alinhados; pytest `test_v4_ops_layout`; operador registra redeploy **sem nohup** + `/api/status` Bearer **200** + log `listening on …:8765`; `LIVE_TRADING_ENABLED=false`.

**Fontes:** operador 2026-11-03 (`/pmo plan`, pacote N18 ops); implementação local `front/n16-8-panel`.

---