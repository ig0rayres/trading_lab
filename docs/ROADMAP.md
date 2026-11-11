# Roadmap Técnico — Trading Lab

> Gerado em: 2026-10-30  
> Fase: 8 — Planejamento técnico (`/pmo plan`, categoria **D**)  
> Baseado em: `docs/PROJECT-BRIEF.md`, `docs/REQUIREMENTS.md`, `docs/ARCHITECTURE.md`, `docs/DATABASE.md`, `docs/LEGACY-ANALYSIS.md`  
> Status: **Em execução** (D3 Gate A + D4 Gate B — nada marcado concluído sem critério fechado)
> Gerado via: `/pmo plan` — Rock handoff 2026-10-30

---

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de sprints (fase construção) | 5 |
| Tarefas estimadas | 28 (12 P, 16 M) |
| Caminho crítico | D1 → D2 → D4 → D5 (ledger + gates antes de homologação paper) |
| Live trading | Fora de escopo até evidência explícita; `LIVE_TRADING_ENABLED=false` |

**BOM:** D1 cobre BOM-1/BOM-2; D2–D5 cobrem BOM-3/BOM-4 (paper homologado, sem substituir EasyPanel).

---

## Índice de Sprints

| Sprint | Categoria | Gate (resumo) | Status | Tasks | Módulos | Resumo | Linhas |
|--------|-----------|---------------|--------|-------|---------|--------|--------|
| D1 | D | CI verde + vendor pinado + pytest com nodeids | concluida | 6 | baseline, vendor | Evidência reprodutível | 80–115 |
| D2 | D | Tabelas ledger no Postgres + rollback testado | concluida* | 5 | ledger | Persistência paper | 117–145 |
| D3 | D | Gate A rejeita sinal inválido sem broker | concluida | 6 | signal-gate-a | Ingestão autêntica | 147–178 |
| D4 | D | Gate B + fila paper sem fill | concluida | 6 | risk-gate-b, paper-gateway | Limites antes da fila | 179–210 |
| D5 | D | Paper reconciliado read-only; nenhum live | concluida* | 5 | paper-gateway, observability | Homologação ponta a ponta | 214–242 |
| N6 | N | Imagem com psycopg + vendor pinado; CI smoke | concluida | 5 | vendor, observability | Deploy reprodutível EasyPanel | *(abaixo)* |
| N7 | N | Fases persistidas; shadow/research sem paper_allowed; ORB fora | concluida | 6 | strategy-catalog, risk-gate-b | Catálogo MVP + Gate B | *(abaixo)* |
| N8 | N | migrate apply deixa 7 strategy_states; runbook EasyPanel | concluida | 4 | strategy-catalog, ledger | Homologação + seed on migrate | *(abaixo)* |
| N9 | N | Itens 3–7 com evidência operador; F-013 persist | concluida | 6 | signal-gate-a, risk-gate-b, paper-gateway, observability | Homologação D5 EasyPanel | *(abaixo)* |
| N10 | N | Closeout N9 no ROADMAP + notas smoke homolog | concluida | 5 | docs | Alinhamento pós-N9 | *(abaixo)* |
| N11 | N | Feature 1 REQUIREMENTS fechada; pytest traceability | concluida | 4 | research-cycle | Ciclo research sem ordem + manifesto | *(abaixo)* |
| N12 | N | Feature 5 fill `signal_copy` evidenciado; LIVE false | planejada | 5 | paper-gateway, signal_copy | Demo Alpaca paper (P0 pivot) | *(abaixo)* |
| N13 | N | Homolog por família; sem scoring inventado | em execucao | 4 | strategy-catalog | Estratégias P1 pós-demo | *(abaixo)* |
| N14 | N | Pacotão MVP-DEMO-1.0 runbook + smoke + deploy policy | concluida | 4 | docs, observability | Release único MVP demo | *(abaixo)* |
| N15 | N | MVP-OP-0.9 — submit copy paper homologado | em execucao | 2 | operador, docs | Submit `signal_copy` | *(abaixo)* |
| N16 | N | MVP-OP-1.0 — Prodígio paper + Command Panel v1 | concluida | 9 | prodigy, v4_web_dashboard | Plataforma operacional v1 | *(abaixo)* |
| N17 | N | MVP-OP-1.1 — Tá Barato upstream + painel família | planejada | 5 | vendor, strategy-catalog | Multi-estratégia | *(abaixo)* |
| N18 | N | Command Panel always-on (`v4-ops`) + runbook ops | em execucao | 4 | observability, docs | Painel 8765 sem nohup | *(abaixo)* |
| N19 | N | Laço demo: gatilho no painel e ciclo da ordem no ledger | em execucao | 4 | observability, paper-gateway | Operar B3, cripto e forex | *(abaixo)* |
| N20 | N | Contrato v0.3 + N19.1–N19.2 publicados; fill P-001b; SHA imagem; 0 rebuild | em execucao | 5 | docs, ledger, observability | Onda 0 — resgate | *(abaixo)* |
| N21 | N | Ordem até fill/cancel/expira; P&L só de fill; restart sem duplicar | planejada | 3 | paper-gateway, ledger | Onda 1 — ciclo da ordem | *(abaixo)* |
| N22 | N | Risco lê `control_flags`; capital único R$ 5.000; sessão B3 + feriado | concluida | 3 | risk-gate-b | Onda 2 — âncoras honestas | *(abaixo)* |
| N23 | N | Trabalhador da fila dentro do `v4-ops`; dois apps EasyPanel | concluida | 3 | observability, paper-gateway | Onda 2 — worker (ADR-009) | *(abaixo)* |
| N24 | N | Login + Central de controle; dia a dia sem Exec | planejada | 4 | v4_web_dashboard | Onda 3 — Feature 8 | *(abaixo)* |
| N25 | N | Tela de sinais com destino, gate e âncora; ranking Prodígio | planejada | 3 | v4_web_dashboard | Onda 3 — Feature 9 | *(abaixo)* |
| N26 | N | Performance só de fill confirmado; bruto rotulado | planejada | 3 | v4_web_dashboard, ledger | Onda 3 — Feature 10 | *(abaixo)* |
| N27 | N | Laço autônomo só no mercado com conta demo nomeada (G-MKT) | planejada | 6 | paper-gateway, risk-gate-b | Onda 4 — Feature 7 | *(abaixo)* |
| N28 | N | Ajuste supervisionado reversível, sem tocar âncora (G-AJUSTE) | planejada | 4 | strategy-catalog | Onda 6 — Feature 11 | *(abaixo)* |

\* D5: código + CI + `docs/HOMOLOGATION.md`; fill real Alpaca permanece passo operador (Feature 5 `[ ]` único critério).

\* D2: migration/CI ok; `.env.example` alinhado (F-004 fechado).

---

## Estratégia de Auditoria

> Modo: Pipeline (lab)

| Sprint | Review | Motivo |
|--------|--------|--------|
| D1 | skip | CI + pytest |
| D2 | senior+qa | DDL e integridade financeira |
| D3 | senior+qa | Superfície webhook |
| D4 | senior+qa | Gates de risco |
| D5 | comprehensive | Última sprint D — paper |
| N6 | senior+qa | Deploy EasyPanel |
| N7 | senior+qa | Catálogo + Gate B produto |
| N8 | senior+qa | Seed no CLI migrate + runbook homologação |
| N9 | senior+qa | Runbook itens 3–7 + evidência; F-013 persist |
| N10 | skip | Docs closeout only |
| N11 | senior+qa | Scheduler/run-once tests + REQUIREMENTS Feature 1 |
| N12 | senior+qa | Paper submit path + homolog operador Feature 5 |
| N13 | senior+qa | Matriz homolog estratégias; F-003 congelado até N12 |
| N15 | skip | Operador + docs; 0 rebuild |
| N16 | senior+qa | Prodígio paper + dashboard v1 (`v4_web_dashboard`) |
| N17 | senior+qa | Tá Barato upstream + extensão painel |
| N19 | senior+qa | Escrita de gatilho + rastro da ordem |
| N20 | senior+qa | Resgate de contrato e código N19.1–N19.2 |
| N21 | senior+qa | Ciclo da ordem e P&L de fill |
| N22 | senior+qa | Gates de risco e calendário |
| N23 | senior+qa | Supervisor `v4-ops` |
| N24 | senior+qa | Autenticação do painel |
| N25 | senior+qa | Tela de sinais |
| N26 | senior+qa | Performance financeira |
| N27 | comprehensive | Envio autônomo na conta demo |
| N28 | senior+qa | Ajuste automático de parâmetro |

---

## Grafo de Dependências

```
[D1 CI + vendor pin] ──► [D2 Postgres ledger]
                              │
[D3 Gate A] ──────────────────┼──► [D4 Gate B + gateway queue]
                              │              │
                              └──────────────┴──► [D5 reconcile + dashboard auth]
                                                              │
[N6 EasyPanel image] ──► [N7 strategy-catalog + Gate B phase] ──► [N8 seed on migrate]
```

D3 pode iniciar em paralelo com D2 após D1, mas D5 depende de D2–D4. N7 depende de D2 (tabela) + D4 (Gate B) + N6 (deploy estável). N8 depende de N7 (`ensure_strategy_defaults`) + D2 (`ledger_migrate`); não reabre Gate B.

---

## Sprint D1 — Baseline verificável
> Categoria: D  
> titulo_humano: CI verde, upstream pinado e pytest com evidência real  
> Gate: `gh`/local: pytest passa com inventário; `docs/VENDOR-PIN.md` registra SHA; workflow CI verde em PR  
> bom_ref: BOM-1, BOM-2  
> review: skip

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | Adicionar `vendor/day-trader-skill` (submodule ou cópia) e `docs/VENDOR-PIN.md` | `/git` + documentação | — |
| [x] | P | Garantir CI (`.github/workflows/ci.yml`) e `requirements-dev.txt` | `/devops planejar` | — |
| [~] | P | Configurar remote Git + branch `front/d1-baseline` | `/git` | — *(origin + `main`; CI #3 Success)* |
| [x] | M | Rodar `vendor_verify` offline contra pin | skill refs | vendor |
| [ ] | M | Rodar `parity.py` quando artefatos orb existirem | `/qa validar` | vendor |
| [x] | P | Reexecutar pytest local; arquivar saída (nodeids) em `docs/` ou artefato CI | `/qa testes` | CI |
| [x] | P | Atualizar `docs/REQUIREMENTS.md` critério pytest quando verde | `/pmo` | pytest |

---

## Sprint D2 — Ledger Postgres
> Categoria: D  
> titulo_humano: Banco pronto para ordens paper com trilha append-only  
> Gate: migration aplica e reverte; oito tabelas do DBML existem; teste de integração sem credencial real  
> bom_ref: BOM-3  
> review: senior+qa

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | Alembic/SQL migration alinhada a `docs/db-schema.dbml` | `/arquiteto dados` | D1 |
| [x] | P | Teste rollback da migration | `/qa testes` | migration |
| [x] | M | Adapter de persistência (append-only; sem `deleted_at` como borracha) | `/dev` | migration |
| [x] | P | `.env.example` alinhado aos nomes reais do código | `/devops` | — |
| [x] | P | Documentar runbook de apply na instância existente | `docs/INFRASTRUCTURE.md` | migration |

---

## Sprint D3 — Gate A (sinal)
> Categoria: D  
> titulo_humano: Webhook e ingestão recusam sinal falso antes de qualquer fila  
> Gate: testes cobrem rejeição (segredo, schema, idempotência); nenhuma chamada Alpaca no caminho A  
> bom_ref: BOM-3  
> review: senior+qa

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | Contrato Gate A = `api-spec.yaml` + skill (header + legacy EasyPanel) | `/dev` | D1 |
| [x] | P | Testes: sinal inválido → código de motivo, zero ordem | `/qa testes` | Gate A |
| [x] | M | Integrar News First / copy apenas como **entrada** auditada (sem broker) | `/dev` | Gate A |
| [x] | P | Calendário/sessão: recusar fora de horário (upstream `session`) | `/dev` | vendor |
| [x] | P | Atualizar `docs/REQUIREMENTS.md` Feature 2 critérios | `/pmo` | testes |
| [x] | P | Registrar achados abertos em `docs/FINDINGS.md` | `/pmo triar` | — |
| [x] | P | Testes HTTP handler webhook | `/qa testes` | Gate A |

---

## Sprint D4 — Gate B e fila paper
> Categoria: D  
> titulo_humano: Limites de capital e risco antes da fila Alpaca paper  
> Gate: ordem bloqueada excede R$50/posição/3 slots; `PAPER_GATEWAY_QUEUE_ONLY` continua não sendo fill  
> bom_ref: BOM-3, BOM-4  
> review: senior+qa

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | Gate B: reuso `trader-risk` + políticas REQUIREMENTS (capital paper) | skill `paper-order-gate` | D2, D3 |
| [x] | M | Paper gateway: fila após B; stub de broker em testes | `/dev` | Gate B |
| [x] | P | Testes + REQUIREMENTS Feature 3 fechados | `/qa testes` | gateway |
| [x] | M | Gravar intenção de ordem no ledger (pré-envio) | `/dev` | D2 |
| [x] | P | Kill switch documentado (`INFRASTRUCTURE`) | `docs/INFRASTRUCTURE.md` | — |
| [x] | P | 3 posições + rejeição persistida + critérios Feature 3 | `/dev` | Gate B |

---

## Sprint D5 — Homologação paper (read-only reconcile)
> Categoria: D  
> titulo_humano: Paper reconciliado sem live e sem trocar EasyPanel  
> Gate: fluxo sinal→A→B→fila→fill simulado/real paper read-only; dashboard exige auth se público  
> bom_ref: BOM-3, BOM-4  
> review: comprehensive

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | `v4_alpaca_reconcile` integrado ao ledger (READ_ONLY) | `/dev` | D4 |
| [x] | M | Trilha de evidência: shadow vs paper no dashboard | `/dev` | D4 |
| [x] | P | Checklist de homologação operador (sem live) | `docs/HOMOLOGATION.md` | — |
| [x] | P | Export comparativo EasyPanel vs snapshot (SHA imagem) | operador | `docs/INFRASTRUCTURE.md` §9 |
| [x] | M | Fechar critérios Features 2–3 e 6; Feature 5 parcial em REQUIREMENTS | `/pmo` | reconcile |

---

## Sprint N6 — Deploy reprodutível EasyPanel
> Categoria: N  
> Status: concluida  
> titulo_humano: Imagem EasyPanel sobe com Postgres e vendor pinado  
> resumo_humano: Redeploy deixa de depender de clone manual do vendor e de pip install de psycopg. Mesma imagem para trading-lab e trading-lab-webhook; live permanece desligado.  
> Gate: docker build ok; container importa psycopg; vendor @ SHA VENDOR-PIN; CI docker-build smoke; pytest inalterado + test_image_pin  
> bom_ref: BOM-2, BOM-3  
> review: senior+qa  

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | Pin runtime psycopg[binary] on requirements.txt | `/dev` | — |
| [x] | M | Bake vendor pin in Dockerfile (git clone SHA) | `/devops` | N6.1 |
| [x] | P | CI docker-build smoke | `/devops` | N6.2 |
| [x] | M | EasyPanel runbook: dois apps; sem overlay vazio /app/vendor | docs | N6.2 |
| [x] | P | Pin-drift test VENDOR-PIN vs Dockerfile | `/qa testes` | N6.2 |

---

## Sprint N7 — Catálogo de estratégias (MVP) + Gate B por fase
> Categoria: N  
> Status: concluida  
> titulo_humano: Fase persistida trava paper; ORB fora do principal  
> resumo_humano: Cada família passa a ter fase no Postgres (research, shadow, paper limitado, validado). O Gate B recusa paper se a fase for research ou shadow, e ORB não entra como estratégia principal. Sem inventar fórmula de momentum, Tá Barato ou Prodigy.  
> Gate: pytest — research/shadow nunca paper_allowed; ORB rejeitado mesmo com fase paper_* no banco; linha ausente fail-closed; risk_decisions.strategy_key vem do sinal (não literal signal_copy); LIVE_TRADING_ENABLED false; nenhum limiar novo de scoring momentum/Tá Barato/Prodigy  
> bom_ref: BOM-3, BOM-4  
> review: senior+qa  
> Generated via hub PMO (planning mode) on 2026-10-30. Source: Feature 4 REQUIREMENTS + ISS-002 + ARCHITECTURE strategy-catalog.  
> Brief: `docs/.briefs/N7.brief.md`

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | Catalog module + ledger helpers + insert-if-missing seed | `/dev` + `paper-order-gate` | — |
| [ ] | M | Signal carries strategy_key (HMAC ALLOWED + worker attach) | `/dev` | — |
| [ ] | M | Gate B reads strategy_states; shadow/research/ORB never paper_allowed | skill `paper-order-gate` | N7.1, N7.2 |
| [ ] | P | Persist risk_decisions.strategy_key from signal (drop hardcoded signal_copy) | `/dev` | N7.2 |
| [ ] | P | Ledger integration tests catalog + Gate B + queue (LEDGER_DATABASE_URL) | `/qa testes` | N7.1, N7.3, N7.4 |
| [ ] | P | REQUIREMENTS Feature 4 checkboxes N7 can close; no-invented-threshold regression | `/pmo` | N7.5 |

<details>
<summary>N7.1 executor_prompt</summary>

```yaml
id: N7.1
size: M
bom_ref: BOM-3
depends_on: []
files:
  - src/strategy_catalog.py
  - src/ledger_store.py
  - tests/test_strategy_catalog.py
reuse_targets:
  - component: src/ledger_store.py
    reuse_as: extend
    convergence_check: rg "strategy_states" src/ledger_store.py && rg "def get_strategy_phase|def ensure_strategy_defaults" src/strategy_catalog.py src/ledger_store.py
  - component: docs/db-schema.dbml
    reuse_as: mirror_shape
    convergence_check: rg "research|shadow|paper_limited|paper_validated" src/strategy_catalog.py && rg "news_first|momentum|ta_barato|signal_copy|prodigy_15d|orb|mean_reversion" src/strategy_catalog.py
  - component: migrations/001_ledger_up.sql
    reuse_as: call
    convergence_check: rg "CREATE TABLE strategy_states" migrations/001_ledger_up.sql && rg "strategy_states" src/ledger_store.py
guardrail_contract:
  - class: secrets
    id: n7-1-no-secrets
    target: src/strategy_catalog.py
    check: python3 -c "from pathlib import Path; t=Path('src/strategy_catalog.py').read_text() if Path('src/strategy_catalog.py').exists() else ''; assert 'ALPACA_API' not in t and 'sk_live' not in t"
    pass_condition: no broker credentials in catalog module
  - class: subagent-safety
    id: n7-1-live-lock
    target: src/original.py
    check: rg "LIVE_TRADING_ENABLED must be false" src/original.py
    pass_condition: LAB_LOCK remains
executor_prompt: |
  ### Quality Brief (Sprint N7)
  sprint: N7
  Maintain: load_original().risk.check for the capital bracket — do not reimplement trader-risk/check.py.
  Maintain: ledger_store.insert_row / connect / LEDGER_TABLES — extend helpers; no second persistence module.
  Maintain: LIVE_TRADING_ENABLED=false and original.py LAB_LOCK.
  Avoid: inventing RSI/percentile/score thresholds for momentum, Tá Barato, or Prodigy.
  Avoid: promoting strategy_states.phase from PnL, HTTP 200, or PAPER_GATEWAY_QUEUE_ONLY; seed is insert-if-missing only.
  [ABORDAGEM] Attach strategy_key on the in-memory signal in the worker after HMAC validate; Gate B never infers the key.
  [RISCO] Catalog check must fail-closed when DB/override is missing.
  [OPORTUNIDADE] Copy kill_switch_active SQL read pattern for strategy_states.phase.
  EXPIRES at end of Sprint N7.

  Melhoria: persistent strategy_states read/seed without a new migration.
  Contexto: migrations/001_ledger_up.sql and db-schema.dbml already define strategy_states (strategy_key unique, phase research|shadow|paper_limited|paper_validated). src/ledger_store.py lists the table in LEDGER_TABLES but has only insert_row — no get/seed. Gate B cannot consult phases today.
  Objetivo: add src/strategy_catalog.py plus helpers on ledger_store (get_strategy_phase, ensure_strategy_defaults). Known keys from DBML only. Seed insert-if-missing: news_first/momentum/ta_barato/prodigy_15d=research; signal_copy=paper_limited; orb/mean_reversion=shadow. Never overwrite an existing row. Never invent scoring numbers. LIVE_TRADING stays false.
  Arquivos: src/strategy_catalog.py, src/ledger_store.py, tests/test_strategy_catalog.py.
  Critério de pronto: unit tests for known keys/phases; ledger integration (skipUnless LEDGER_DATABASE_URL, apply migration like tests/test_paper_gateway_queue.py GateBLedgerIntegrationTest) proves insert-if-missing and that a second seed does not clobber a hand-updated phase; rg shows no CREATE TABLE strategy_states outside 001.
  Cenários de teste:
    1. Caso normal: empty table + ensure_strategy_defaults → seven rows with recommended phases.
    2. Edge case: existing orb=paper_validated is left unchanged by seed (overwrite forbidden).
    3. Edge case: unknown strategy_key → lookup error/None, never default paper_limited.
    4. Regressão: LEDGER_TABLES still includes all eight ledger tables; insert_row still rejects unknown table.
```
</details>

<details>
<summary>N7.2 executor_prompt</summary>

```yaml
id: N7.2
size: M
bom_ref: BOM-3
depends_on: []
files:
  - src/signal_copy.py
  - src/tradingview_worker.py
  - tests/test_signal_copy.py
reuse_targets:
  - component: src/signal_copy.py
    reuse_as: extend
    convergence_check: rg "strategy_key" src/signal_copy.py && rg "ALLOWED" src/signal_copy.py
  - component: src/tradingview_worker.py
    reuse_as: extend
    convergence_check: rg "strategy_key" src/tradingview_worker.py
  - component: tests/test_signal_copy.py
    reuse_as: copy_pattern
    convergence_check: rg "strategy_key" tests/test_signal_copy.py
guardrail_contract:
  - class: secrets
    id: n7-2-hmac-no-leak
    target: src/signal_copy.py
    check: rg "provider_signature" src/signal_copy.py && ! rg -n "print\(.*SECRET" src/signal_copy.py src/tradingview_worker.py
    pass_condition: signature stays HMAC compare; no secret print
  - class: subagent-safety
    id: n7-2-live-lock
    target: src/original.py
    check: rg "LIVE_TRADING_ENABLED=false" Dockerfile
    pass_condition: image live lock unchanged
executor_prompt: |
  ### Quality Brief (Sprint N7)
  sprint: N7
  Maintain: load_original().risk.check — do not reimplement trader-risk.
  Maintain: ledger_store helpers — no second store.
  Maintain: LIVE_TRADING_ENABLED=false.
  Avoid: invented scoring thresholds.
  Avoid: silent strategy_key inference inside Gate B.
  [ABORDAGEM] Worker attaches strategy_key after HMAC validate; add field to signal_copy.ALLOWED.
  [RISCO] Extra JSON key today is INVALID_SCHEMA — ALLOWED must include strategy_key or TV payloads with the field never reach Gate B.
  [OPORTUNIDADE] Keep signal_events schema unchanged (no strategy_key column).
  EXPIRES at end of Sprint N7.

  Melhoria: the signed signal carries strategy_key to Gate B.
  Contexto: signal_copy.ALLOWED omits strategy_key (unrecognized field → INVALID_SCHEMA). paper_gateway_queue hardcodes strategy_key 'signal_copy'. Gate A signal_events has no strategy_key column — do not add one.
  Objetivo: CONTRACT (documented in docs/.briefs/N7.brief.md): worker is the attachment point, not Gate A persist. Add optional strategy_key to ALLOWED. After validate succeeds, if missing and provider==tradingview, set signal_copy. Other providers without key stay missing (Gate B will reject). Do not default orb or momentum.
  Arquivos: src/signal_copy.py, src/tradingview_worker.py, tests/test_signal_copy.py (worker test in same file or tests/test_tradingview_worker.py only if already present — do not create a parallel package).
  Critério de pronto: valid HMAC without strategy_key still previews; with strategy_key='signal_copy' still previews; unknown extra field still INVALID_SCHEMA; worker-attached key is visible on the dict passed toward evaluate_signed_signal.
  Cenários de teste:
    1. Caso normal: signed payload with strategy_key=signal_copy → no INVALID_SCHEMA.
    2. Edge case: payload without strategy_key still validates (legacy HMAC).
    3. Edge case: unrecognized field (news_first=True) still INVALID_SCHEMA (test_unrecognized_field regression).
    4. Regressão: orders_sent remains 0 on preflight; LIVE_TRADING_ENABLED false.
```
</details>

<details>
<summary>N7.3 executor_prompt</summary>

```yaml
id: N7.3
size: M
bom_ref: BOM-3, BOM-4
depends_on: ["N7.1", "N7.2"]
files:
  - src/gate_b_risk.py
  - tests/test_gate_b_risk.py
reuse_targets:
  - component: vendor/day-trader-skill/trader-risk/check.py
    reuse_as: call
    convergence_check: rg "load_original\(\)\.risk" src/gate_b_risk.py && ! rg "def check\(" src/gate_b_risk.py src/strategy_catalog.py
  - component: src/strategy_catalog.py
    reuse_as: call
    convergence_check: rg "get_strategy_phase|STRATEGY_PHASE|STRATEGY_ORB" src/gate_b_risk.py
  - component: src/gate_b_risk.py
    reuse_as: extend
    convergence_check: rg "evaluate_signed_signal" src/gate_b_risk.py && rg "kill_switch_active" src/gate_b_risk.py
guardrail_contract:
  - class: secrets
    id: n7-3-no-live-host
    target: src/gate_b_risk.py
    check: rg "No broker calls" src/gate_b_risk.py && rg "LIVE_TRADING_ENABLED=false" Dockerfile
    pass_condition: Gate B stays broker-free; live flag false
  - class: subagent-safety
    id: n7-3-no-reimplement-risk
    target: vendor/day-trader-skill/trader-risk/check.py
    check: rg "load_original" src/gate_b_risk.py && rg "risk.check" src/gate_b_risk.py
    pass_condition: upstream check still called
executor_prompt: |
  ### Quality Brief (Sprint N7)
  sprint: N7
  Maintain: load_original().risk.check for the capital bracket — do not reimplement trader-risk/check.py.
  Maintain: existing kill switch, session, and max-positions checks.
  Maintain: LIVE_TRADING_ENABLED=false.
  Avoid: invented scoring thresholds; do not call trader-scanner orb_hit to authorize paper.
  Avoid: paper_allowed for research/shadow or for orb even if DB phase is paper_*.
  [ABORDAGEM] Phase check after kill/session/cap and before risk.check.
  [RISCO] Unit tests currently paper_allowed without DB — add strategy_phase= override for those cases; production path fail-closed without DB.
  [OPORTUNIDADE] Mirror kill_switch_active SELECT WHERE deleted_at IS NULL.
  EXPIRES at end of Sprint N7.

  Melhoria: Gate B enforces strategy_states phase.
  Contexto: evaluate_signed_signal applies kill switch, NYSE session, position cap, then trader-risk.check. It does not read strategy_states. Architecture: strategy in shadow never gets paper_allowed. Feature 4: ORB is not selectable as main paper strategy.
  Objetivo: require signal['strategy_key']. Resolve phase via strategy_phase= test override, else catalog/ledger (fail-closed if neither). Reject codes: STRATEGY_KEY_REQUIRED, STRATEGY_UNKNOWN, STRATEGY_PHASE_UNKNOWN, STRATEGY_PHASE_NOT_PAPER (research|shadow), STRATEGY_ORB_NOT_SELECTABLE (orb always; mean_reversion same non-selectable rule). Only paper_limited|paper_validated proceed to existing risk.check. Do not reimplement check(). Do not add momentum/Tá Barato/Prodigy numeric gates.
  Arquivos: src/gate_b_risk.py, tests/test_gate_b_risk.py.
  Critério de pronto: pytest GateBRiskTest still PASSes a within-risk signal when strategy_phase=paper_limited and strategy_key=signal_copy; shadow/research/missing/orb never paper_allowed; risk.check still invoked on the happy path.
  Cenários de teste:
    1. Caso normal: signal_copy + paper_limited + within-risk → paper_allowed (existing qty=1 case).
    2. Edge case: orb + paper_validated override still rejected STRATEGY_ORB_NOT_SELECTABLE.
    3. Edge case: momentum + research → STRATEGY_PHASE_NOT_PAPER, orders path not reached.
    4. Edge case: missing row / no DB and no override → STRATEGY_PHASE_UNKNOWN.
    5. Regressão: qty=100 still blocked by upstream risk; kill switch and OUTSIDE_SESSION unchanged.
```
</details>

---

## Sprint N8 — Homologação + seed on migrate
> Categoria: N  
> Status: concluida  
> titulo_humano: Migrate apply popula as 7 fases sem INSERT manual  
> resumo_humano: Depois de aplicar o ledger, o Postgres já nasce com as sete famílias do catálogo. Reaplicar a migrate em base já migrada também preenche linhas que faltam, sem sobrescrever fase gravada à mão. O runbook de homologação/EasyPanel diz como conferir; sem rebuild de imagem nesta sprint.  
> Gate: pytest — `ledger-migrate apply` (roundtrip ou `already_applied`) deixa 7 linhas em `strategy_states` quando `LEDGER_DATABASE_URL` está definido; seed insert-if-missing; rollback não semeia; `LIVE_TRADING_ENABLED` false; sem migration 002; sem reabrir Gate B nem limiar de scoring  
> bom_ref: BOM-3  
> review: senior+qa  
> Generated via hub PMO (planning mode) on 2026-10-30. Source: ISS-003 + operador opção A pós-N7.  
> Brief: `docs/.briefs/N8.brief.md`

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N8.1 Hook `ensure_strategy_defaults` into `ledger-migrate apply` (including `already_applied`) | `/dev` | — |
| [x] | P | N8.2 Unit + optional ledger integration: apply roundtrip leaves 7 `strategy_states` rows | `/qa testes` | N8.1 |
| [x] | P | N8.3 Homologation runbook: verify 7 rows after migrate | docs | N8.2 |
| [x] | P | N8.4 EasyPanel/INFRASTRUCTURE note: re-apply seeds insert-if-missing | docs | N8.1 |

P notes (no executor_prompt): **N8.2** extend `tests/test_ledger_migration.py` — unit without DSN: `apply()` still calls `ensure_strategy_defaults` on `already_applied` (mock status/connect as needed). Integration (`skipUnless LEDGER_DATABASE_URL`): after the existing apply/rollback/apply roundtrip, `strategy_states` has 7 rows whose keys match `DEFAULT_PHASE_BY_KEY`; a second apply does not clobber a hand-updated phase; optional subprocess `python3 src/ledger_migrate.py apply`. Do not add Gate B tests. **N8.3** add a checklist step after migrate: `SELECT strategy_key, phase FROM strategy_states WHERE deleted_at IS NULL` → 7 keys; INSERT manual deixa de ser o caminho feliz. **N8.4** EasyPanel § apply: re-run `ledger-migrate apply` is safe (insert-if-missing); no new service, no image rebuild.

### Task N8.1 — Hook catalog seed into ledger-migrate apply

**Estado atual**: `apply()` aplica `001_ledger_up.sql` ou retorna `already_applied` sem tocar `strategy_states`. Seed só corre em `fetch_strategy_phase` / testes N7. EasyPanel ficou vazio até INSERT manual.
**Estado desejado**: todo `apply()` bem-sucedido (primeiro e `already_applied`) chama `ensure_strategy_defaults()` e falha de forma visível se as 7 chaves N7 não existirem; rollback não semeia; insert-if-missing.
**Fonte(s)**: ISS-003
**Módulo(s) afetado(s)**: `src/ledger_migrate.py`
**Risco**: MEDIUM — CLI de migrate no Postgres de homologação; seed silencioso hoje é o bug.
**Task size**: M (1 file; decisão: semear em `already_applied` e falhar se faltar chave)

- **Arquivo(s)**: `src/ledger_migrate.py`

**executor_prompt**:

```yaml
id: N8.1
size: M
bom_ref: BOM-3
depends_on: []
files:
  - src/ledger_migrate.py
reuse_targets:
  - component: src/strategy_catalog.py
    reuse_as: call
    convergence_check: rg "ensure_strategy_defaults" src/ledger_migrate.py && ! rg "def ensure_strategy_defaults" src/ledger_migrate.py
  - component: src/ledger_migrate.py
    reuse_as: extend
    convergence_check: rg "def apply" src/ledger_migrate.py && rg "already_applied" src/ledger_migrate.py
guardrail_contract:
  - class: secrets
    id: n8-1-no-dsn-print
    target: src/ledger_migrate.py
    check: rg "LEDGER_DATABASE_URL" src/ledger_migrate.py && ! rg -n "print\\(.*PASSWORD" src/ledger_migrate.py
    pass_condition: DSN stays in env; no password print
  - class: subagent-safety
    id: n8-1-live-lock
    target: Dockerfile
    check: rg "LIVE_TRADING_ENABLED=false" Dockerfile
    pass_condition: image live lock unchanged
  - class: caller-level
    id: n8-1-cli-apply-seed
    target: src/ledger_migrate.py
    check: pytest -q tests/test_ledger_migration.py -k apply
    convergence_check: pytest -q tests/test_ledger_migration.py -k apply
    pass_condition: apply path seeds catalog when LEDGER_DATABASE_URL is set
executor_prompt: |
  ### Quality Brief (Sprint N8)
  sprint: N8
  Maintain: strategy_catalog.ensure_strategy_defaults() insert-if-missing for the seven N7 keys — call it; do not reimplement INSERT.
  Maintain: ledger_migrate.apply / rollback / status CLI wired by scripts/run.sh ledger-migrate.
  Maintain: LIVE_TRADING_ENABLED=false and original.py LAB_LOCK.
  Avoid: migration 002, DDL edits, and a second persistence module.
  Avoid: Gate B / scoring changes; do not promote strategy_states.phase from PnL, HTTP 200, or PAPER_GATEWAY_QUEUE_ONLY.
  [ABORDAGEM] Call ensure_strategy_defaults() at the end of apply() on both first apply and already_applied; then SELECT the seven known keys and raise if any are missing (ops-visible). Do not seed on rollback.
  [RISCO] ensure_strategy_defaults() swallows exceptions and no-ops without LEDGER_DATABASE_URL. A silent no-op after migrate is the EasyPanel empty-table failure mode — migrate must not treat that as success.
  [OPORTUNIDADE] Extend LedgerMigrationIntegrationTest.test_apply_rollback_roundtrip (skipUnless LEDGER_DATABASE_URL) to assert seven strategy_states rows after the final apply.
  EXPIRES at end of Sprint N8.

  Melhoria: ledger-migrate apply seeds strategy_states.
  Contexto: apply() runs 001_ledger_up.sql or returns already_applied without calling ensure_strategy_defaults(). EasyPanel had an empty strategy_states table until a manual INSERT or a worker fetch. ISS-002/N7 already defined the seven keys and insert-if-missing; do not reopen Gate B or invent scoring thresholds.
  Objetivo: after a successful apply — including the already_applied early return — call strategy_catalog.ensure_strategy_defaults(). Then verify the seven KNOWN_STRATEGY_KEYS / DEFAULT_PHASE_BY_KEY rows exist (SELECT); raise a RuntimeError (or equivalent) if any key is missing so operators see the failure. Do not overwrite an existing phase. Do not seed inside rollback(). Do not add migrations/002_*.sql. Do not edit gate_b_risk.py. LIVE_TRADING stays false. scripts/run.sh ledger-migrate wiring stays as-is.
  Arquivos: src/ledger_migrate.py.
  Critério de pronto: rg shows ensure_strategy_defaults imported/called from ledger_migrate.py and not redefined there; apply() no longer returns already_applied without attempting seed; unit coverage exists or is added in N8.2; no DSN/password printed.
  Cenários de teste (implemented in N8.2; this task must remain compatible):
    1. Caso normal: empty DB + apply → seven strategy_states rows with N7 default phases.
    2. Edge case: already_applied + empty table → seed still runs; seven rows appear.
    3. Edge case: existing orb=paper_validated is left unchanged (overwrite forbidden).
    4. Regressão: rollback still drops tables; apply after rollback still works; LIVE_TRADING_ENABLED false; no Gate B file edits.
```

---

## Sprint N9 — Homologação D5 no EasyPanel (itens 3–7)

> Categoria: N  
> Status: concluida  
> titulo_humano: Checklist EasyPanel 3–7 com evidência, sem ordem live  
> resumo_humano: O laboratório já grava sinal, risco e intenção de ordem paper. Esta sprint deixa o operador conferir isso no EasyPanel (webhook, worker, reconcile só leitura, dashboard e kill switch) e anotar a evidência sem segredo. Fila e HTTP 200 continuam sem ser fill; dinheiro real permanece desligado.  
> Gate: `docs/HOMOLOGATION.md` itens 3–7 nomeiam comando `scripts/run.sh`, SQL ou campo JSON, e o que não conta como fill; `docs/TEST-EVIDENCE.md` tem linhas pendentes para o operador (sem segredo); nenhum diff em `src/`; `LIVE_TRADING_ENABLED` false; Feature 5 fill permanece `[ ]`; ISS-004 não aberto  
> bom_ref: BOM-3  
> review: senior+qa  
> Gerado via: /pmo plan (planejador-melhorias)  
> Brief: `docs/.briefs/N9.brief.md`  
> plan_only: true (não define `sprint_atual`)

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N9.1 Runbook Gate A: webhook → `signal_events` | docs | — |
| [x] | P | N9.2 Runbook Gate B: worker → `risk_decisions` + `paper_orders` `queued_intent` | docs | N9.1 |
| [x] | P | N9.3 Runbook reconcile read-only (`ledger_apply`, não `broker_reconciled`) | docs | N9.2 |
| [x] | P | N9.4 Runbook dashboard auth + kill switch | docs | N9.3 |
| [x] | M | N9.5 Evidence sheet + optional Feature 5 operator note (no fill task) | docs | N9.4 |
| [x] | P | N9.6 Operador: executar itens 3–7 no EasyPanel e preencher evidência redigida | operador | N9.5 |

P notes (no executor_prompt): **N9.1** expand item 3 in `docs/HOMOLOGATION.md`: `scripts/run.sh tv-webhook`, header `X-Webhook-Token` or legacy `/webhook/{token}`, then `SELECT` on `signal_events` (count / status). HTTP 202 `QUEUED` is not a fill. **N9.2** expand item 4: `scripts/run.sh tv-worker` after Gate A; rejection row in `risk_decisions`; accept row in `paper_orders.status = queued_intent`. Cite `PAPER_GATEWAY_QUEUE_ONLY` and `orders_sent = 0` as non-fills. Do not change `gate_b_risk.py` or catalog phases. **N9.3** expand item 5: `PAPER_RECONCILE_LEDGER_APPLY=true` and `scripts/run.sh v4-alpaca-reconcile --output /app/reports/paper/reconcile.json`; record `ledger_apply`; do not treat `broker_reconciled` as true. **N9.4** expand items 6–7: loopback or `DASHBOARD_ALLOW_REMOTE=true` plus `DASHBOARD_BEARER_TOKEN` length ≥32 via `scripts/run.sh v4-dashboard`; `/api/status` fields `kill_switch_on` and `shadow_vs_paper`; kill via `TRADING_LAB_KILL_SWITCH=true` or a new `control_flags` row (see `docs/INFRASTRUCTURE.md` § Kill switch). Confirm the worker blocks (`orders_sent` 0, no new `queued_intent`). **N9.6** is operator-only on the existing EasyPanel apps. The agent does not SSH, does not read secrets, and does not invent row counts. Paste redacted counts into the N9.5 table. `bom_ref: BOM-3`.

### Task N9.5 — Evidence sheet for homologation items 3–7

**Estado atual**: `docs/HOMOLOGATION.md` lista os itens 3–7 em uma linha cada. `docs/TEST-EVIDENCE.md` para em N6. CI cobre testes; o EasyPanel ainda não tem evidência colada para sinal, risco, fila, reconcile, dashboard e kill switch. Feature 5 fill real segue `[ ]`.
**Estado desejado**: uma seção N9 em `docs/TEST-EVIDENCE.md` com uma linha por item 3–7, status `pendente`, comando e campo esperado, sem segredo e sem contagem inventada. `docs/HOMOLOGATION.md` aponta para essa seção. Um bloco separado, "Passo operador opcional — Feature 5", descreve fill real como passo só do operador e não entra no gate da N9. Nenhum arquivo em `src/`.
**Fonte(s)**: operador trilha A 2026-10-30; `docs/HOMOLOGATION.md` checklist; `docs/REQUIREMENTS.md` Feature 5–6; `docs/ROADMAP.md` Sprint D5. ISS-004 não aberto (fiação já existe).
**Módulo(s) afetado(s)**: `docs/TEST-EVIDENCE.md`, `docs/HOMOLOGATION.md`
**Risco**: MEDIUM — marcar fila ou HTTP 200 como fill fecharia homologação sem evidência.
**Task size**: M (2 files; decisão: o que prova cada item e o que fica fora)

- **Arquivo(s)**: `docs/TEST-EVIDENCE.md`, `docs/HOMOLOGATION.md`

**executor_prompt**:

```yaml
id: N9.5
size: M
bom_ref: BOM-3
depends_on: [N9.4]
files:
  - docs/TEST-EVIDENCE.md
  - docs/HOMOLOGATION.md
reuse_targets:
  - component: docs/HOMOLOGATION.md
    reuse_as: extend
    convergence_check: rg "tv-webhook" docs/HOMOLOGATION.md && rg "tv-worker" docs/HOMOLOGATION.md && rg "queued_intent" docs/HOMOLOGATION.md && rg "v4-alpaca-reconcile" docs/HOMOLOGATION.md && rg "v4-dashboard" docs/HOMOLOGATION.md && rg "Passo operador opcional" docs/HOMOLOGATION.md
  - component: docs/TEST-EVIDENCE.md
    reuse_as: extend
    convergence_check: rg "Homologação D5 itens 3–7" docs/TEST-EVIDENCE.md && rg "pendente" docs/TEST-EVIDENCE.md
guardrail_contract:
  - class: secrets
    id: n9-5-no-live-secrets
    target: docs/TEST-EVIDENCE.md
    check: rg "TV_WEBHOOK_TOKEN" docs/HOMOLOGATION.md && ! rg -n "APCA-API|BEGIN PRIVATE" docs/HOMOLOGATION.md docs/TEST-EVIDENCE.md
    pass_condition: env names only; no broker key or private key pasted
  - class: subagent-safety
    id: n9-5-live-lock
    target: Dockerfile
    check: rg "LIVE_TRADING_ENABLED=false" Dockerfile
    pass_condition: image live lock unchanged; no src/ edits in this task
  - class: secrets
    id: n9-5-feature5-open
    target: docs/REQUIREMENTS.md
    check: rg "Fill real Alpaca" docs/REQUIREMENTS.md
    pass_condition: Feature 5 real-fill checkbox stays open
executor_prompt: |
  ### Quality Brief (Sprint N9)
  sprint: N9
  Maintain: LIVE_TRADING_ENABLED=false and src/original.py LAB_LOCK; no live broker host or order path.
  Maintain: Gate A, Gate B, paper queue, reconcile, and dashboard stay as implemented; this task only documents them.
  Maintain: HTTP 200, PAPER_GATEWAY_QUEUE_ONLY, and queued_intent are not fills; reconcile keeps broker_reconciled false.
  Avoid: strategy threshold inventions and edits to gate_b_risk.py, strategy_catalog.py, or vendor/.
  Avoid: checking Feature 5 real fill or PnL as done; that step stays a separate unchecked operator note.
  [ABORDAGEM] Add a pending evidence table (redacted counts only) and point HOMOLOGATION items 3–7 at it. The operator runs EasyPanel; the agent does not.
  [RISCO] persist_risk_decision returns without a row when LEDGER_DATABASE_URL is unset or signal_events has no matching id. HTTP 200 is not evidence.
  [OPORTUNIDADE] CI already covers webhook, Gate B, and queue tests. Do not add src/ or tests: scripts/run.sh already exposes tv-webhook, tv-worker, v4-alpaca-reconcile, and v4-dashboard.
  EXPIRES at end of Sprint N9.

  Melhoria: record homologation evidence slots for checklist items 3–7.
  Contexto: D5 and N8 left the checklist and the 7 strategy_states seed. Wiring already persists signal_events (gate_a_signal.maybe_persist), risk_decisions and paper_orders queued_intent (paper_gateway_queue.persist_risk_decision via tradingview_worker), reconcile ledger_apply (v4_alpaca_reconcile + ledger_reconcile.apply_from_report), dashboard bearer (v4_web_dashboard.main), and kill switch (gate_b_risk.kill_switch_active). Do not reopen Gate B or the strategy catalog. Do not invent scoring thresholds. Upstream trader-* stays behind src/original.py; do not call it from docs work and do not bump the vendor pin.
  Objetivo: append a section headed "Homologação D5 itens 3–7" to docs/TEST-EVIDENCE.md with one pending row per item 3, 4, 5, 6, and 7 (command, expected table or JSON field, status pendente, result empty). In docs/HOMOLOGATION.md, after the checklist, add "Passo operador opcional — Feature 5" stating real Alpaca fill and PnL is operator-only, out of the N9 gate, and still the unchecked Feature 5 criterion. Do not place an order. Do not edit src/, tests/, Dockerfile, or .cursorsession. Do not paste tokens.
  Arquivos: docs/TEST-EVIDENCE.md, docs/HOMOLOGATION.md.
  Critério de pronto: both convergence_check commands exit 0; Dockerfile still has LIVE_TRADING_ENABLED=false; docs/REQUIREMENTS.md still contains the open Fill real Alpaca line; git diff shows no src/ file.
  Cenários de teste:
    1. Caso normal: each of items 3–7 has a pending evidence row naming signal_events, risk_decisions or queued_intent, ledger_apply, dashboard auth, or kill_switch_on.
    2. Edge case: evidence cells are empty or "pendente"; no API key, DSN, or bearer value appears.
    3. Regressão: Feature 5 fill checkbox in REQUIREMENTS stays open; LIVE_TRADING_ENABLED=false remains in the Dockerfile; Gate B source files are untouched.
    4. Edge case: the optional Feature 5 section is present and labeled operator-only, and it is not a sprint task that submits an order.
    5. Regressão: PAPER_GATEWAY_QUEUE_ONLY and broker_reconciled are still described as not a completed fill.
```

---

## Sprint N10 — Closeout N9 (ROADMAP + homolog notes)

> Categoria: N  
> Status: concluida  
> titulo_humano: Fechar N9 no roadmap e documentar smoke pós-deploy  
> resumo_humano: N9 já entregue em main e no EasyPanel. Esta sprint só alinha ROADMAP, evidência e runbook (smoke pregão vs unittest integração), sem mudar código de gates ou live.  
> Gate: N9 marcada concluida no indice e tasks [x]; sem diff em `src/`; `LIVE_TRADING_ENABLED` false; Feature 5 fill `[ ]`; `docs/TEST-EVIDENCE.md` nota smoke TTL/sessão  
> review: skip  
> Gerado via: /pmo plan + /pmo sprint N10  
> Brief: `docs/.briefs/N10.brief.md`

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N10.1 ROADMAP: N9 concluida + indice + proximo passo | docs | — |
| [x] | P | N10.2 TEST-EVIDENCE + HOMOLOGATION notas smoke item 4 | docs | N10.1 |
| [x] | P | N10.3 FINDINGS/TEST-EVIDENCE referencia main 0509732 | docs | N10.1 |
| [x] | P | N10.4 `.cursorsession` sprint N10 + previous N9 | session | N10.1 |
| [ ] | P | N10.5 Operador: `/git front finish` frentes após merge | operador | N10.2 |

---

## Sprint N11 — Feature 1 ciclo research (evidência + testes)

> Categoria: N  
> Status: concluida  
> titulo_humano: Fechar Feature 1 — ciclo research sem ordem e manifesto honesto  
> resumo_humano: Amarra os critérios abertos da Feature 1 a testes pytest e à folha de evidência. Reforça que scheduler e run-once não enviam ordem e que falha de ciclo não deixa manifesto antigo como sucesso. Sem corretora, sem live, sem EasyPanel.  
> Gate: pytest CI verde; `docs/REQUIREMENTS.md` Feature 1 critérios `[x]`; matriz nodeid em `TEST-EVIDENCE`; `rg` sem novo submit broker em `v4_scheduler`/`v4_run_once`; `LIVE_TRADING_ENABLED` false  
> bom_ref: BOM-1  
> review: senior+qa  
> Gerado via: `/pmo plan` N11 Feature 1 2026-11-01  
> Brief: `docs/.briefs/N11.brief.md`

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N11.1 Matriz Feature 1 → pytest nodeids em TEST-EVIDENCE | docs | — |
| [x] | M | N11.2 Teste integração scheduler `--once` falha + manifesto stale | `/qa testes` | N11.1 |
| [x] | P | N11.3 REQUIREMENTS Feature 1 checkboxes `[x]` com links | `/pmo` | N11.1 |
| [x] | P | N11.4 Sessão sprint N11 + módulo research-cycle | session | N11.1 |

<details>
<summary>N11.2 executor_prompt</summary>

```yaml
id: N11.2
size: M
bom_ref: BOM-1
depends_on: [N11.1]
files:
  - tests/test_v4_scheduler.py
  - src/v4_scheduler.py
reuse_targets:
  - component: src/v4_scheduler.py
    reuse_as: extend
    convergence_check: rg "def run_cycle|def invalidate_stale_manifest|def main" src/v4_scheduler.py && rg "paper-gateway|alpaca" src/v4_scheduler.py && test $? -ne 0
  - component: tests/test_v4_scheduler.py
    reuse_as: extend
    convergence_check: rg "test_failed_cycle_invalidates_previous_manifest|test_readonly_success" tests/test_v4_scheduler.py
guardrail_contract:
  - class: subagent-safety
    id: n11-2-no-broker
    target: src/v4_scheduler.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_scheduler.py').read_text(); assert 'paper-gateway' not in t and 'submit_order' not in t"
    pass_condition: scheduler stays research-only imports
  - class: subagent-safety
    id: n11-2-live-lock
    target: Dockerfile
    check: rg "LIVE_TRADING_ENABLED=false" Dockerfile
    pass_condition: live flag remains false in image
executor_prompt: |
  ### Quality Brief (Sprint N11)
  sprint: N11
  Maintain: v4_scheduler never imports broker or paper-gateway; run_cycle always reports orders_sent=0.
  Maintain: invalidate_stale_manifest deletes file manifest on failed/timeout cycles only; symlink guard stays.
  Avoid: adding Alpaca, tv-worker, or gate paths to scheduler tests.
  Avoid: weakening manifest deletion on FAILED_OR_BLOCKED to make tests pass.
  EXPIRES at end of Sprint N11.

  Melhoria: close the gap between unit tests and main() wiring for stale manifest on failed --once cycle.
  Contexto: ISS-004; REQUIREMENTS Feature 1 open criteria; existing unit tests cover invalidate_stale_manifest and run_cycle separately but not main(--once) after simulated failure with pre-existing v4_manifest.json.
  Objetivo: extend tests/test_v4_scheduler.py with an integration-style test invoking main(['--once', ...]) with mocked runner returning non-zero; assert manifest removed and status JSON orders_sent=0 and execution_authorized=false. Only touch scheduler test file unless a minimal bugfix in v4_scheduler.py is required (document in commit).
  Arquivos: tests/test_v4_scheduler.py (primary), src/v4_scheduler.py (only if wiring bug found).
  Critério de pronto: pytest nodeid passes; full pytest -q green locally/CI; no new dependencies.
  Cenários de teste:
    1. Caso normal: failed run_cycle path via main --once removes stale v4_manifest.json.
    2. Regressão: FINISHED_RESEARCH keeps manifest when exit_code 0.
    3. Edge case: symlink manifest still raises UNSafe path without deleting target.
    4. Regressão: LIVE_TRADING_ENABLED=true still BLOCKED before cycle.
```
</details>

---

## Sprint N12 — Demo Alpaca paper (`signal_copy`, P0 pivot)
> Categoria: N  
> Status: planejada  
> titulo_humano: Operar demo paper com fill comprovado na trilha signal_copy  
> resumo_humano: Fecha o único critério aberto de Feature 5 usando código já existente (runner + fila pós–Gate B), runbook e evidência operador — sem live e sem tratar fila como fill.  
> Gate: pytest verde incluindo caminho `PAPER_SUBMITTED` mockado; `docs/TEST-EVIDENCE.md` matriz Feature 5; operador preenche linha fill redigida; `REQUIREMENTS` fill `[x]` só após N12.5; `LIVE_TRADING_ENABLED` false; F-003 permanece congelado  
> bom_ref: BOM-3, BOM-4  
> review: senior+qa  
> Gerado via: `/pmo plan pivot-demo` 2026-11-02  
> Brief: `docs/.briefs/N12.brief.md`

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N12.1 Matriz Feature 5 → pytest nodeids + checklist operador | docs | — |
| [x] | P | N12.2 Runbook Feature 5 em HOMOLOGATION (`signal-paper` / worker auto flags) | docs | N12.1 |
| [x] | M | N12.3 Testes: `PAPER_SUBMITTED` + `process_after_gate_b` com broker mock | `/qa testes` | N12.1 |
| [ ] | P | N12.4 Operador: fill Alpaca paper + reconcile redigido (EasyPanel) | operador | N12.2, N12.3 |
| [ ] | P | N12.5 REQUIREMENTS Feature 5 fill `[x]` + TEST-EVIDENCE operador | docs | N12.4 |

P notes: **N12.2** document env chain from `signal_paper_runner.py` (`PAPER_SIGNAL_AUTO_ENABLED`, `PAPER_EXECUTION_ENABLED`, `PAPER_SIGNAL_ACCOUNT_ACK`, `PAPER_DAILY_RISK_CONFIRMED`, `V4_RISK_SNAPSHOT_FILE`) and contrast with N9 `queued_intent`. Cite `scripts/run.sh signal-paper`. **N12.4** operator only — no secrets in Git; `orders_sent=1` / broker id redacted. **N12.5** do not check fill before operator row exists.

<details>
<summary>N12.3 executor_prompt</summary>

```yaml
id: N12.3
size: M
bom_ref: BOM-3
depends_on: [N12.1]
files:
  - tests/test_signal_paper_runner.py
  - tests/test_paper_gateway_queue.py
  - src/signal_paper_runner.py
  - src/paper_gateway_queue.py
reuse_targets:
  - component: src/signal_paper_runner.py
    reuse_as: extend
    convergence_check: rg "def run\\(|PAPER_SUBMITTED" src/signal_paper_runner.py
  - component: src/paper_gateway_queue.py
    reuse_as: extend
    convergence_check: rg "process_after_gate_b|broker_auto_allowed" src/paper_gateway_queue.py
guardrail_contract:
  - class: subagent-safety
    id: n12-3-live-lock
    target: Dockerfile
    check: rg "LIVE_TRADING_ENABLED=false" Dockerfile
    pass_condition: live flag remains false in image
  - class: subagent-safety
    id: n12-3-paper-host
    target: src/signal_paper_runner.py
    check: rg "paper-api.alpaca.markets|PAPER_URL" src/paper_audit.py src/signal_paper_runner.py
    pass_condition: submit stays on paper URL module
executor_prompt: |
  ### Quality Brief (Sprint N12)
  sprint: N12
  Maintain: LIVE_TRADING_ENABLED=false; no live host; reuse signal_paper_runner.run and paper_gateway_queue.process_after_gate_b — no second broker client.
  Maintain: PREVIEW_ONLY and QUEUED paths unchanged when auto flags off.
  Avoid: loosening risk caps or bypassing V4_RISK_SNAPSHOT_FILE / SIGNAL_COPY_SECRET validation.
  Avoid: treating HTTP 200 or queued_intent as fill in assertions.
  EXPIRES at end of Sprint N12.

  Contexto: ISS-005; Feature 5 fill criterion open; existing tests cover preview/blocks but not successful PAPER_SUBMITTED with mocked POST, nor process_after_gate_b when broker_auto_allowed is true.
  Objetivo: add pytest coverage for (1) run() returning PAPER_SUBMITTED orders_sent=1 with mocked broker_get/post and valid snapshot env; (2) process_after_gate_b delegating to paper_run when auto env set (mock paper_run). Minimal production changes only if test reveals a wiring bug.
  Critério de pronto: new nodeids documented in TEST-EVIDENCE Feature 5 matrix (N12.1); pytest -q green in CI.
  Cenários de teste:
    1. Happy path mock: PAPER_SUBMITTED, orders_sent=1, ledger jsonl ATTEMPTED→SUBMITTED.
    2. Regressão: auto flags off → PREVIEW_ONLY / QUEUED orders_sent=0.
    3. Regressão: bad signature still BLOCKED.
    4. Regressão: LIVE_TRADING_ENABLED=true still fail-closed.
```
</details>

---

## Sprint N13 — Homolog estratégias por família (P1)
> Categoria: N  
> Status: planejada  
> titulo_humano: Checklist de homolog por estratégia sem inventar scoring  
> resumo_humano: Depois do demo paper, documenta como testar e homologar cada família do catálogo (fase research/shadow/paper_limited) com evidência pytest e operador — sem promover ORB/C2 nem limiares novos.  
> Gate: matriz por `strategy_key` em TEST-EVIDENCE; fases N7 intactas; momentum/ta_barato/prodigy sem checkbox fechado sem regra upstream recuperada; F-003 ainda congelado; CI verde; LIVE false  
> bom_ref: BOM-1  
> review: senior+qa  
> Gerado via: `/pmo plan pivot-demo` 2026-11-02  
> Status: em execucao  
> Brief: `docs/.briefs/N13.brief.md`

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N13.1 Matriz Feature 4 → família / fase / pytest ou “blocked upstream” | docs | — |
| [x] | P | N13.2 Folha homolog operador por família (sem ordem onde fase ≠ paper) | docs | N13.1 |
| [x] | P | N13.3 ROADMAP backlog: ordem P1 e freeze F-003 até N12 gate | docs | N13.1 |
| [x] | M | N13.4 Testes/traceability só para famílias com regra existente no repo | `/qa testes` | N13.1 |

P notes: **N13** repo entregue com **N12.4 ainda pendente** (ISS-005 aberto). F-003 congelado até Feature 5 fill evidenciado.

---

## Sprint N14 — Pacotão MVP-DEMO-1.0
> Categoria: N  
> Status: planejada  
> titulo_humano: Um runbook, um smoke e regra de deploy para parar rebuild infinito  
> resumo_humano: Consolida MVP demo em artefatos únicos; pendências Feature 5 (P-001–P-003) ficam explícitas em ISSUES; não substitui fill operador N12.4.  
> Gate: `docs/MVP-DEMO-RUNBOOK.md` + `scripts/mvp-demo-smoke.sh` OK local/CI; `config/mvp-demo.env.example`; ISS-006 critérios repo; ISS-005 permanece aberto  
> review: skip  
> Gerado via: operador pacotão 2026-11-02 · ISS-006

> Status: concluida  

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N14.1 `MVP-DEMO-RUNBOOK.md` + política deploy | docs | — |
| [x] | P | N14.2 `config/mvp-demo.env.example` | docs | N14.1 |
| [x] | P | N14.3 `scripts/mvp-demo-smoke.sh` | `/devops` | N14.1 |
| [x] | P | N14.4 ISSUES pendências P-001–P-005 + ISS-006 | docs | N14.1 |

P notes: **Um deploy EasyPanel** após merge N14; depois **freeze** rebuild até `src/`/`Dockerfile` ou N12.4 evidenciado.

---

## Release train MVP-OP (épico único — ISS-007)

> Plano mergeado (PR #13). Ampliado: **Command Panel v1** dentro de **1.0**, não sprint/epic separado.  
> Brief: `docs/.briefs/MVP-OP-RELEASE-TRAIN.brief.md`

```text
MVP-OP-0.9 (N15) ──► MVP-OP-1.0 (N16) ──► MVP-OP-1.1 (N17)
     │                      │                      │
  fill signal_copy      Prodígio + painel v1     Tá Barato + painel
  Feature 5 [x]         rank→fill + ledger UI   (Git First upstream)
  0 rebuild             1 rebuild              1 rebuild max
```

---

## Sprint N15 — Release MVP-OP-0.9 (fechar copy paper)
> Categoria: N  
> Status: planejada  
> titulo_humano: Submit paper homologado na copy (fill limit pendente)  
> Gate: submit operador evidenciado; Feature 5 fill `[ ]` com nota; TEST-EVIDENCE N12; **sem** rebuild EasyPanel  
> review: skip  
> Release tag: `MVP-OP-0.9`

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N15.1 Operador N12.4 submit + reconcile redigido (fill limit pendente) | operador | — |
| [x] | P | N15.2 TEST-EVIDENCE + ISS-005 parcial (sem fill `[x]`) | docs | N15.1 |

---

## Sprint N16 — Release MVP-OP-1.0 (Prodígio + Command Panel v1)
> Categoria: N  
> Status: concluida  
> titulo_humano: Plataforma operacional v1 — Prodígio paper + painel único (Feature 6 estendida)  
> Gate: Git First reuse inventory; **submit** `prodigy_15d` evidenciado; painel bearer **ok** operador 2026-11-03; fill limit opcional P-001b; CI verde; LIVE false  
> review: senior+qa  
> Release tag: `MVP-OP-1.0`  
> Deploy: **1 rebuild** após merge

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N16.0 Git First: vendor SHA + reuse inventory Prodígio/signal | `/git` | N15 gate |
| [x] | P | N16.1 Runbook Prodígio: rank → sinal assinado → Gate A/B (`strategy_key=prodigy_15d`) | docs | N16.0 |
| [x] | M | N16.2 Adaptação mínima ingestão (**waived** — one-shot ok; ver N16-GIT-FIRST) | — | N16.1 |
| [x] | P | N16.4 Operador: submit paper Prodígio + evidência TEST-EVIDENCE (fill limit pendente) | operador | N16.2 |
| [x] | M | N16.6 Command Panel: escopo v1 + mapa ISS-007 (histórico, performance, ordens, oportunidades, saúde, fases, evolution, tips research) | docs | PR #14 |
| [x] | M | N16.7 Implementação mínima em `v4_web_dashboard` + dados ledger/Alpaca read-only (reuse `trading_dashboard_data`) | `/dev` | N16.6 |
| [x] | P | N16.8 Homolog operador: painel remoto com bearer + smoke alinhado a MVP-DEMO | operador | N16.7 · **`docs/HOMOLOGATION-N16.8-PANEL.md`** |
| [x] | P | N16.5 Release notes `MVP-OP-1.0` + MVP-DEMO-RUNBOOK (N16.8 painel remoto pendente) | docs | N16.4 |

**Pré-requisito duro:** N15 submit evidenciado (0.9). Fill Feature 5 opcional para painel performance credível. **PRODIGY_PROVIDERS** e fase `paper_limited` só via operador.

---

## Sprint N17 — Release MVP-OP-1.1 (Tá Barato + momentum upstream)
> Categoria: N  
> Status: planejada  
> titulo_humano: Tá Barato com regras upstream homologadas em shadow/paper  
> Gate: fórmulas/limites de `ta_barato` (e momentum se escopo) recuperadas em vendor — **senão** sprint permanece blocked e documenta gap; homolog pytest; LIVE false  
> review: senior+qa  
> Release tag: `MVP-OP-1.1`

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | P | N17.0 Git First: upstream paths ta_barato/momentum | `/git` | N16 gate |
| [ ] | M | N17.1 Integração/adaptação Gate B ou research (reuse only) | `/dev` | N17.0 |
| [ ] | P | N17.2 Homolog operador shadow → paper limitado (evidência) | operador | N17.1 |
| [ ] | P | N17.3 REQUIREMENTS/TEST-EVIDENCE matriz ta_barato | docs | N17.2 |
| [ ] | P | N17.4 Repriorizar F-003 orb-parity (opcional pós-1.1) | `/pmo` | N17.2 |
| [ ] | M | N17.5 Painel: seção Tá Barato / família upstream (read-only homolog) | `/dev` | N17.2 |

---

## Sprint N18 — Command Panel always-on (`v4-ops`)
> Categoria: N  
> Status: em execucao  
> resumo_humano: O painel operacional deixa de depender de nohup no Exec: a imagem sobe pesquisa e dashboard juntos, com restart automático do HTTP e runbook de segurança Bearer/HTTPS.  
> titulo_humano: Painel operacional sempre ligado no trading-lab  
> Gate: CI verde; CMD **`v4-ops`** na imagem; operador redeploy **trading-lab** com log `listening on …:8765` **sem** nohup; `/api/status` Bearer **200**; `LIVE_TRADING_ENABLED=false`  
> review: senior+qa  
> Issue: **ISS-008**

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N18.1 Layout **`v4-ops`**: `v4_ops_main.sh`, `run.sh`, Dockerfile CMD, `tests/test_v4_ops_layout.py` | `/dev` | — |
| [x] | P | N18.2 Runbook **`docs/DASHBOARD-OPERATIONS.md`** + alinhar EASYPANEL, COMMAND-PANEL, HOMOLOGATION-N16.8 | docs | N18.1 |
| [x] | P | N18.3 Operador: rebuild EasyPanel `trading-lab` + linha TEST-EVIDENCE N18 (sem token no Git) | operador | N18.2 |
| [x] | P | N18.4 Closeout ROADMAP: **N16 → concluida**; MVP-DEMO-RUNBOOK menciona `v4-ops` | docs | N18.3 |

**N18.1 — executor_prompt (resumo):** Reuse `scripts/run.sh` pattern; add `v4-ops` → `v4_ops_main.sh` spawning supervised `v4-dashboard` + foreground `v4-scheduler`; default Dockerfile CMD `v4-ops` with same scheduler args; env `DASHBOARD_AUTOSTART` default true; no broker submit code in dashboard path; regression `tests/test_v4_web_dashboard.py` + new layout test; `guardrail_contract`: LIVE false, read-only HTTP only, no third EasyPanel service.

**Fora de escopo N18:** login HTML no browser; Tá Barato (N17); Feature 5 fill (P-001b operador).

---

## Sprint N19 — Laço demo com gatilho no painel

> Categoria: N
> Status: em execucao
> resumo_humano: O painel passa a alterar parada, âncoras e mercado, e a ordem paper deixa rastro no ledger até o fill. B3, cripto e forex só operam quando a conta demo daquele mercado devolver o estado. Conta real continua sem botão.
> titulo_humano: Gatilhos no painel e ordem com rastro no ledger
> Gate: pytest verde; `LIVE_TRADING_ENABLED=false`; PATCH de gatilho não insere `paper_orders`; resultado do simulador local não é fill; nenhuma ordem sai com `demo_operation_on` false
> review: senior+qa
> Issue: **ISS-009**

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N19.1 Migration `002`: mercado, âncoras, `market_controls`, `trigger_changes`, preço fora do real. Sem apagar fill | `/dev` | — |
| [x] | M | N19.2 PATCH de gatilho em `v4_web_dashboard` conforme `docs/api-spec.yaml` 0.2.0. Bearer sozinho recebe 401 na escrita | `/dev` | N19.1 |
| [x] | M | N19.3 Persistir `broker_order_id` e estado a partir de resposta mockada. Simulador local permanece sem fill | `/dev` | N19.1 |
| [x] | P | N19.4 Teste: mercado sem conta demo que devolva posição fica barrado, com motivo, e não chama a Alpaca | `/qa testes` | N19.2, N19.3 |

**Fora de escopo N19:** escolher a corretora demo de B3 ou forex; ligar `demo_operation_on` em produção; conta real; cadastrar estratégia nova; ajuste automático de parâmetro.

**N19.1 — executor_prompt (resumo):** Add `migrations/002_triggers_up.sql` and down. Columns and tables from `docs/DATABASE.md` section 6 and `docs/db-schema.dbml`. Do not rewrite `001`. Do not drop fills. Test rollback. `guardrail_contract`: no secrets in SQL, no live host, no seed order.

**N19.2 — executor_prompt (resumo):** Extend `src/v4_web_dashboard.py` only. Routes `PATCH /api/triggers`, `PATCH /api/markets/{market}`, `PATCH /api/strategies/{strategy_key}`. Insert `trigger_changes`. Do not import a broker client. Unknown strategy key is 404. `orb` and `mean_reversion` cannot move to a paper phase. `guardrail_contract`: write requires operator session; bearer alone is 401; response field names match the DBML.

**N19.3 — executor_prompt (resumo):** When a mocked paper submit returns an id, store it on `paper_orders` and do not leave the row at `queued_intent`. `src/v4_shadow_broker.py` stays a request log. Do not send `B3_EQUITY` or `FOREX` to `https://paper-api.alpaca.markets`. `guardrail_contract`: `orders_sent` stays 0 unless the mock is an explicit paper submit; `LIVE_TRADING_ENABLED` false.

---

## Programa MVP-FINAL — plataforma operacional pelo contrato v0.3

> Aprovado pelo operador em 2026-11-11 (`/pmo plan`).  
> Auditoria: `docs/.briefs/MVP-FINAL-AUDIT.intake.md` · Plano detalhado com rastreio critério → sprint: `docs/.briefs/MVP-FINAL-WAVES.plan.md`  
> Definição de pronto: todos os critérios das Features 1–10 conferíveis pelo operador no painel e na conta demo; Feature 11 é Should-have. Tempo de resposta e uptime ficam fora porque o contrato diz "a definir".  
> Invariantes: `LIVE_TRADING_ENABLED=false`; só `trading-lab` e `trading-lab-webhook`; nenhum limiar inventado; ORB e mean reversion fora de paper; simulador local não é fill; HTTP 200 ou fila não é ordem executada.

```text
Onda 0  N20                resgate do contrato v0.3 + N19.1–N19.2; fill P-001b; SHA      0 rebuild
Onda 1  N19.3–N19.4 + N21  ordem com id da corretora até fill; P&L só de fill (ADR-007)  MVP-OP-1.2 (1)
Onda 2  N22 + N23          âncoras lidas, capital único, sessão B3; worker no v4-ops     ┐
Onda 3  N24 + N25 + N26    login, Central, sinais com motivo, performance de fill        ┘ MVP-OP-1.3 (1)
Onda 4  N27                laço autônomo no mercado com conta demo nomeada (G-MKT)       MVP-OP-1.4 (0–1)
Onda 5  N17 (existente)    Tá Barato / momentum só com fórmula upstream (G-FORM)         MVP-OP-1.1 (0–1)
Onda 6  N28                ajuste supervisionado (G-AJUSTE + fill real)                  0–1
```

Caminho crítico Must-have: **0 → 1 → 2 → 3 → 4**. Envio autônomo permanece desligado até a Onda 4.

### Gates do operador

| ID | Decisão | Destrava | Sem resposta |
|----|---------|----------|--------------|
| G-MKT | Nome da conta demo de B3, de cripto e de forex (ou "fica barrado") | N27.2, N27.4 | Mercado barrado com motivo visível; nome nunca inventado (ADR-010) |
| G-FORM | Onde está a fórmula de Tá Barato e de momentum no upstream (ou "não existe") | N17.1+ | Família fica fora de paper |
| G-AJUSTE | Método do ajuste (erro, frequência, desfazer) | N28.2 | Feature 11 fica `[ ]` |

Nenhum gate trava as Ondas 0–3.

---

## Sprint N20 — Publicar o contrato e o painel que já altera gatilho
> Categoria: N  
> Status: em execucao  
> titulo_humano: Contrato v0.3 e gatilhos do painel num pedido de revisão  
> Gate: PR em frente própria (não `n18-closeout`); Features 7–11 no contrato; escrita de gatilho exige sessão de operador (Bearer sozinho = 401); suíte verde contra vendor pinado; `LIVE_TRADING_ENABLED=false`; **0 rebuild**  
> Issue: ISS-009 + P-001b + dúvidas 4 e 7  
> review: senior+qa  
> Gerado via: `/pmo plan` — 2026-11-11 (planner, aprovado pelo operador)

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N20.1 Resgatar contrato v0.3 e código N19.1–N19.2 do checkpoint local `3d26a13` (sem arquivos de sessão) | `/git` + `/dev` | — |
| [ ] | P | N20.2 Operador: anotar o SHA da imagem de `trading-lab` e `trading-lab-webhook` no EasyPanel (parcial: digest Docker trading-lab; falta webhook + SHA Git) | operador | — |
| [x] | P | N20.3 Operador: fill AAPL 2026-10-29 @349.85 + posição qty 1 (MSFT/NVDA sem fill; `n20-fill-001` → DUPLICATE_SYMBOL) | operador | — |
| [x] | P | N20.4 Marcar o fill da Feature 5 em REQUIREMENTS só com a linha de evidência | docs | N20.3 |
| [x] | P | N20.5 Operador: confirmar que o Postgres do EasyPanel tem o ledger (`001` applied; `triggers_applied` false até Onda 1) | operador | — |

**N20.1 — executor_prompt (resumo):** Apply only product paths from `3d26a13` onto a front cut from `main`: REQUIREMENTS v0.3, ARCHITECTURE §12, DATABASE §6, api-spec 0.2.0, DESIGN.md, db-schema.dbml, ISS-009, ROADMAP N19 block, N19 brief, `migrations/002_*`, ledger patches, PATCH trigger routes, `tests/test_ledger_migration.py`, `tests/test_panel_triggers.py`, panel-triggers rule/skill. Exclude `.cursorsession*`, `.beesy/`, `.cursor` caches. Do not implement N19.3–N19.4. `guardrail_contract`: LIVE false; no rebuild; full suite green with `UPSTREAM_DIR` at the pinned vendor SHA.

---

## Sprint N21 — Acompanhar até o fill e P&L verdadeiro
> Categoria: N  
> Status: planejada  
> titulo_humano: Fill, cancelamento ou expiração no ledger, com perda honesta  
> Gate: estado final gravado; perda do dia/semana só de fill em real; restart sem duplicar; LIVE false; sem envio autônomo  
> review: senior+qa  
> Depende de: N19.3 · Release: **MVP-OP-1.2** (1 rebuild, junto com N19.3–N19.4)

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N21.1 Acompanhar a ordem até fill, cancelamento ou expiração (reuso `paper_reconcile` / `ledger_reconcile`) | `/dev` | N19.3 |
| [x] | M | N21.2 Calcular perda do dia e da semana só com fill confirmado em real; sem câmbio inventado | `/dev` | N21.1 |
| [x] | P | N21.3 Provar que reinício não duplica ordem | `/qa testes` | N21.1 |

---

## Sprint N22 — Âncoras únicas e calendário B3
> Categoria: N  
> Status: concluida  
> titulo_humano: Um teto de risco e sessão B3 de verdade  
> Gate: Gate B e carteira leem `control_flags`; capital de partida R$ 5.000 nos dois caminhos; fora de sessão B3/NY e feriado ⇒ recusa com motivo; LIVE false  
> review: senior+qa  
> Depende de: N21 · Release: **MVP-OP-1.3**

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N22.1 Fazer `gate_b_risk` e `portfolio_risk_v4` lerem as âncoras gravadas pelo painel (banco fora: teto mais apertado) | `/dev` | — |
| [x] | M | N22.2 Unificar o capital de referência em R$ 5.000 (ARCHITECTURE §12.1) | `/dev` | N22.1 |
| [x] | M | N22.3 Recusar sinal fora da sessão B3/NY, feriado e horário de verão (calendário do upstream primeiro) | `/dev` | — |

---

## Sprint N23 — Trabalhador da fila dentro do v4-ops
> Categoria: N  
> Status: concluida  
> titulo_humano: A fila anda no mesmo serviço do painel, sem app novo  
> Gate: supervisor roda pesquisa, painel e worker; queda do worker não derruba a pesquisa; `demo_operation_on` false ⇒ worker recusa envio com motivo; dois apps EasyPanel  
> review: senior+qa  
> Depende de: N21, N22.1 · Release: **MVP-OP-1.3**

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N23.1 Estender `scripts/v4_ops_main.sh` com o worker da fila em intervalo curto (ADR-009) | `/dev` | — |
| [x] | P | N23.2 Teste: saída forçada do worker não derruba a pesquisa | `/qa testes` | N23.1 |
| [x] | P | N23.3 Runbook da release: só dois serviços EasyPanel | docs | N23.1 |

---

## Sprint N24 — Login e central de controle
> Categoria: N  
> Status: planejada  
> titulo_humano: Entrar no painel e mandar na operação sem o Exec  
> Gate: painel não abre sem login; alteração registrada com valor anterior; plataforma não afrouxa âncora sozinha; parada pelo painel segura a próxima ordem em até um ciclo; um operador; LIVE false  
> review: senior+qa  
> Depende de: N19.2, N23.1 · Release: **MVP-OP-1.3**

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | N24.1 Tela de entrar na frente do painel (reuso da sessão de operador da N19.2) | `/dev` | — |
| [ ] | M | N24.2 Central ligada às âncoras, mercados, estratégias e parada (DESIGN.md) | `/dev` | N24.1 |
| [ ] | P | N24.3 Teste: parada pelo painel segura a próxima ordem no ciclo | `/qa testes` | N24.2 |
| [ ] | P | N24.4 Runbook do dia a dia aponta o painel, não o Exec | docs | N24.2, N23.1 |

---

## Sprint N25 — Sinais e Prodígio com motivo visível
> Categoria: N  
> Status: planejada  
> titulo_humano: Cada sinal mostra para onde foi e o que o barrou  
> Gate: lista com origem, destino e motivo; ranking Prodígio e cópias; barrado mostra gate e âncora  
> review: senior+qa  
> Release: **MVP-OP-1.3**

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | N25.1 Tela de sinais com mercado, origem, destino e motivo | `/dev` | — |
| [ ] | M | N25.2 Ranking Prodígio e sinais copiados (pesquisa, não autorização) | `/dev` | — |
| [ ] | P | N25.3 Teste: sinal barrado aponta gate e âncora com o valor da hora | `/qa testes` | N25.1 |

---

## Sprint N26 — Performance só de fill confirmado
> Categoria: N  
> Status: planejada  
> titulo_humano: O número de resultado só conta fill da corretora  
> Gate: total e por estratégia só de fill; ordem sem fill fora; bruto rotulado  
> review: senior+qa  
> Depende de: N21 · Release: **MVP-OP-1.3**

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | N26.1 Resultado por estratégia e total só com fill confirmado | `/dev` | — |
| [ ] | P | N26.2 Teste: ordem `new`/`accepted`/fila fora do resultado | `/qa testes` | N26.1 |
| [ ] | P | N26.3 Rotular valor bruto onde não há custo completo | `/dev` | N26.1 |

---

## Sprint N27 — Contas demo no laço, sem inventar o nome
> Categoria: N  
> Status: planejada  
> titulo_humano: Operar só o mercado cuja conta demo o operador nomeou  
> Gate: G-MKT por mercado; Feature 7 conferível só nos mercados respondidos; destino sempre paper; restart sem duplicar; dois apps; LIVE false  
> review: comprehensive  
> Depende de: Ondas 1–3 · Release: **MVP-OP-1.4** (ou dentro da 1.3 se G-MKT chegar a tempo)

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | N27.1 Forex no universo e no avaliador de carteira, barrado sem conta | `/dev` | — |
| [ ] | M | N27.2 Adaptador da conta demo nomeada pelo operador (B3 e forex nunca pela Alpaca) | `/dev` | G-MKT |
| [ ] | P | N27.3 Teste: mercado sem conta continua visível e barrado com motivo | `/qa testes` | N27.1, N19.4 |
| [ ] | P | N27.4 Operador: sinal válido vira ordem demo sem ação manual | operador | N27.2, N23.1, N24.2 |
| [ ] | P | N27.5 Teste: chave live no ambiente não muda o destino paper | `/qa testes` | N27.2 |
| [ ] | P | N27.6 Teste: restart com laço ligado não duplica | `/qa testes` | N27.4 |

---

## Sprint N28 — Ajuste supervisionado depois do método
> Categoria: N  
> Status: planejada  
> titulo_humano: Ajuste registrado e reversível, sem mexer no risco  
> Gate: G-AJUSTE e fill real; só parâmetro existente na faixa original; histórico com desfazer; âncoras intocadas; LIVE false  
> review: senior+qa  
> Depende de: N20.3, N21

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | P | N28.1 Sugestão continua rotulada como sugestão | `/dev` | — |
| [ ] | M | N28.2 Ajustar só parâmetro existente, dentro da faixa original | `/dev` | G-AJUSTE |
| [ ] | M | N28.3 Registrar antes, depois e motivo, com desfazer na Central | `/dev` | N28.2 |
| [ ] | P | N28.4 Teste: ajuste nunca altera âncora de risco | `/qa testes` | N28.2 |

---

## Fora do roadmap D (backlog N)

| Tema | Origem | Notas |
|------|--------|-------|
| Estratégias Ta Barato / Prodigy / momentum (fórmulas) | LEGACY-ANALYSIS | N7 cobre fases; **não** inventar limiares de scoring |
| Walk-forward / Lean | RESEARCH_ROADMAP | Motor separado |
| Collective2 paper-copy | Feature 4 | Fora de N7; `approved_for_paper_copy` permanece falso |
| CI deploy EasyPanel | Operador | N6 feito; bump de imagem só com sprint própria (fora de N8) |
| Submodule pin vs clone raso | D1 | Preferir pin revisado, não `main` cego |
| F-003 orb-parity (`parity.py`) | D1 / FINDINGS | **Congelado até N12.4/ISS-005** (fill Feature 5); N13 repo não descongela |

---

## Próximo passo operador

1. N16 concluída neste closeout. Evidência N18.3 em `docs/TEST-EVIDENCE.md` (2026-11-10): log `8765` e `/api/status` bearer **200**. PR **#20** com verificação automática verde.  
2. Sprint N18 segue em execução até este commit de docs entrar num pedido de revisão com checks verdes.  
3. **P-001b** (ISS-005 fill) continua sessão operador.  
4. **`/pmo sprint N17`** só após Git First upstream.  
5. N19 (gatilho no painel) fica fora deste commit.  
6. **`LIVE_TRADING_ENABLED=false`** — invariável.
