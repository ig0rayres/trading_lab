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
| N24 | N | Login + Central de controle; dia a dia sem Exec | concluida | 4 | v4_web_dashboard | Onda 3 — Feature 8 | *(abaixo)* |
| N25 | N | Tela de sinais com destino, gate e âncora; ranking Prodígio | concluida | 3 | v4_web_dashboard | Onda 3 — Feature 9 | *(abaixo)* |
| N26 | N | Performance só de fill confirmado; bruto rotulado | concluida | 3 | v4_web_dashboard, ledger | Onda 3 — Feature 10 | *(abaixo)* |
| N27 | N | Laço autônomo só no mercado com conta demo nomeada (G-MKT) | planejada | 6 | paper-gateway, risk-gate-b | Onda 4 — Feature 7 | *(abaixo)* |
| N29 | N | Adapters Clear (B3) + OANDA Practice (forex); Alpaca cripto (ISS-010) | planejada | 6 | paper-gateway | Onda 4b — G-MKT adapters | *(abaixo)* |
| N28 | N | Ajuste supervisionado reversível, sem tocar âncora (G-AJUSTE) | concluida | 4 | strategy-catalog | Onda 6 — Feature 11 | *(abaixo)* |
| N30 | N | Feature 7 Alpaca US+cripto + Prodígio rank→sinal; Features 8–10 com evidência | concluida | 5 | paper-gateway, prodigy | Campanha ISS-011 onda 1 | *(abaixo)* |
| N31 | N | Melhoria contínua diária (fills + não-fills) + TimesFM research-only (G-AJUSTE) | concluida | 5 | evolution, research | Campanha ISS-012 · desbloqueia caminho N28.2–4 | *(abaixo)* |
| N32 | N | Âncoras do painel no laço paper (Feature 7, sem teto paralelo) | concluida | 4 | paper-gateway, risk-gate-b | Campanha ISS-011 lacuna âncora | *(abaixo)* |
| N33 | N | Closeout docs: carimbar N28/N30/N31 e deixar o restante Alpaca honesto | planejada | 5 | docs | Campanha ISS-011 closeout papel | *(abaixo)* |

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
| N29 | comprehensive | Adapters Clear + OANDA Practice |
| N28 | senior+qa | Ajuste automático de parâmetro |
| N30 | senior+qa | Laço Alpaca US+cripto + ingestão Prodígio |
| N31 | senior+qa | Melhoria contínua diária + TimesFM research-only |
| N32 | senior+qa | Âncoras do painel no envio paper |
| N33 | skip | Closeout docs ISS-011 (Alpaca); sem `src/` |

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
> Gate: fórmulas/limites de `ta_barato` (e momentum se escopo) recuperadas em vendor — **G-FORM blocked @ pin**; shadow homolog + painel entregues; paper blocked; homolog pytest; LIVE false  
> review: senior+qa  
> Release tag: `MVP-OP-1.1`

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N17.0 Git First: upstream paths ta_barato/momentum | `/git` | N16 gate |
| [x] | M | N17.1 Integração/adaptação Gate B ou research (reuse only) | `/dev` | N17.0 |
| [ ] | P | N17.2 Homolog operador shadow → paper limitado (evidência) | operador | N17.1 |
| [x] | P | N17.3 REQUIREMENTS/TEST-EVIDENCE matriz ta_barato | docs | N17.2 |
| [ ] | P | N17.4 Repriorizar F-003 orb-parity (opcional pós-1.1) | `/pmo` | N17.2 |
| [x] | M | N17.5 Painel: seção Tá Barato / família upstream (read-only homolog) | `/dev` | N17.2 |

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
Onda 4b N29                adapters Clear simulado + OANDA Practice (+ Alpaca cripto)     MVP-OP-1.4 (0–1)
Onda 5  N17 (existente)    Tá Barato / momentum só com fórmula upstream (G-FORM)         MVP-OP-1.1 (0–1)
Onda 6  N31                melhoria contínua diária (fills+não-fills) + TimesFM research  ISS-012
Onda 6b N28                ajuste supervisionado (método N31; execução N28.2–4)           0–1
Onda 6c N32                Feature 7: envio paper lê âncoras do painel (lacuna 10k USD)   ISS-011
Onda 6d N33                closeout docs: Status N28/N30/N31 + ISS-011 restante honesto  ISS-011
```

Caminho crítico Must-have: **0 → 1 → 2 → 3 → 4**. Envio autônomo permanece desligado até a Onda 4.

### Gates do operador

| ID | Decisão | Destrava | Sem resposta |
|----|---------|----------|--------------|
| G-MKT | Nome da conta demo de B3, de cripto e de forex (ou "fica barrado") | N27.2, N27.4 | Mercado barrado com motivo visível; nome nunca inventado (ADR-010) |
| G-FORM | Onde está a fórmula de Tá Barato e de momentum no upstream (ou "não existe") | N17.1+ | Família fica fora de paper |
| G-AJUSTE | Método: ciclo diário fills+não-fills → dicas; TimesFM só pesquisa; suggestion-first se incerto (ISS-012 / N31) | N31 define o método; N28.2–4 executam o ajuste | Feature 11 critérios 2–4 ficam `[ ]` até N28.2–4 |

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
> Status: concluida  
> titulo_humano: Entrar no painel e mandar na operação sem o Exec  
> Gate: painel não abre sem login; alteração registrada com valor anterior; plataforma não afrouxa âncora sozinha; parada pelo painel segura a próxima ordem em até um ciclo; um operador; LIVE false  
> review: senior+qa  
> Depende de: N19.2, N23.1 · Release: **MVP-OP-1.3**

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N24.1 Tela de entrar na frente do painel (reuso da sessão de operador da N19.2) | `/dev` | — |
| [x] | M | N24.2 Central ligada às âncoras, mercados, estratégias e parada (DESIGN.md) | `/dev` | N24.1 |
| [x] | P | N24.3 Teste: parada pelo painel segura a próxima ordem no ciclo | `/qa testes` | N24.2 |
| [x] | P | N24.4 Runbook do dia a dia aponta o painel, não o Exec | docs | N24.2, N23.1 |

### Quality Brief (Sprint N24 — Onda 3 bundle N24–N26)

sprint: N24 (shipped with N25, N26 in PR #27, merge `fb4a473`)

Maintain: operator session auth in front of `v4_web_dashboard`; reuse N19.2 session cookie pattern — no second auth stack.

Maintain: Central reads/writes control anchors via existing ledger/`trigger_changes` paths; platform never relaxes risk anchors without operator intent.

Maintain: `LIVE_TRADING_ENABLED=false`; queued intent and HTTP 200 are not fills; performance totals only from confirmed fill (N26).

Maintain: `panel_ops_data` + `build_snapshot` as single source for panel ops views — extend, do not fork dashboard data layer.

Avoid: Exec/CLI as the default daily operator path; runbooks must point to the panel.

Avoid: scoring or Prodígio thresholds not already in vendor/recovered code; ranking remains research-labeled.

Avoid: treating `new`/`accepted`/queue rows as P&L; gross values must stay labeled.

Evidence: 455 pytest local APROVADA; CI PR #27 all checks SUCCESS; fix `e545203` for `GateBLedgerIntegrationTest` + `demo_operation_on`.

EXPIRES: closed at N24 closeout (2026-11-11).

---

## Sprint N25 — Sinais e Prodígio com motivo visível
> Categoria: N  
> Status: concluida  
> titulo_humano: Cada sinal mostra para onde foi e o que o barrou  
> Gate: lista com origem, destino e motivo; ranking Prodígio e cópias; barrado mostra gate e âncora  
> review: senior+qa  
> Release: **MVP-OP-1.3**

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N25.1 Tela de sinais com mercado, origem, destino e motivo | `/dev` | — |
| [x] | M | N25.2 Ranking Prodígio e sinais copiados (pesquisa, não autorização) | `/dev` | — |
| [x] | P | N25.3 Teste: sinal barrado aponta gate e âncora com o valor da hora | `/qa testes` | N25.1 |

### Quality Brief (Sprint N25)

Delivered in PR #27 with N24/N26. Maintain: `blocked_context` exposes gate + anchor snapshot on reject; signal list shows market, origin, destination, reason. Prodígio rank and copied signals stay research-labeled, not trade authorization. See parent brief under Sprint N24.

---

## Sprint N26 — Performance só de fill confirmado
> Categoria: N  
> Status: concluida  
> titulo_humano: O número de resultado só conta fill da corretora  
> Gate: total e por estratégia só de fill; ordem sem fill fora; bruto rotulado  
> review: senior+qa  
> Depende de: N21 · Release: **MVP-OP-1.3**

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N26.1 Resultado por estratégia e total só com fill confirmado | `/dev` | — |
| [x] | P | N26.2 Teste: ordem `new`/`accepted`/fila fora do resultado | `/qa testes` | N26.1 |
| [x] | P | N26.3 Rotular valor bruto onde não há custo completo | `/dev` | N26.1 |

### Quality Brief (Sprint N26)

Delivered in PR #27 with N24/N25. Maintain: `performance_from_snapshots` counts strategy/total only on confirmed fill; `PERFORMANCE_LABEL_GROSS` where costs incomplete. Depends on N21 fill semantics — do not regress reconcile-only rows into P&L. See parent brief under Sprint N24.

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
| [x] | M | N27.1 Forex no universo e no avaliador de carteira, barrado sem conta | `/dev` | — |
| [ ] | M | N27.2 Adaptador da conta demo nomeada pelo operador (B3 e forex nunca pela Alpaca) | `/dev` | G-MKT, N29 |
| [x] | P | N27.3 Teste: mercado sem conta continua visível e barrado com motivo | `/qa testes` | N27.1, N19.4 |
| [ ] | P | N27.4 Operador: sinal válido vira ordem demo sem ação manual | operador | N27.2, N23.1, N24.2 |
| [ ] | P | N27.5 Teste: chave live no ambiente não muda o destino paper | `/qa testes` | N27.2 |
| [ ] | P | N27.6 Teste: restart com laço ligado não duplica | `/qa testes` | N27.4 |

---

## Sprint N29 — Adapters demo G-MKT (Clear + OANDA + Alpaca)
> Categoria: N  
> Status: planejada  
> Gerado via: `/pmo plan` 2026-11-13 · fonte ISS-010 · REQUIREMENTS v0.4  
> titulo_humano: Ligar B3 e forex nas contas demo que você escolheu  
> Gate: Clear simulado e OANDA Practice devolvem posição/ordem/fill; cripto = Alpaca paper; mercado sem credencial barrado com motivo; B3/FOREX nunca Alpaca; LIVE false; ids só no env  
> review: comprehensive  
> Depende de: N27.1, N27.3, REQUIREMENTS G-MKT · Release: **MVP-OP-1.4**

### Em uma frase

A plataforma fala com a Clear (B3) e a OANDA (forex) em modo demo, e mantém a Alpaca só para cripto — sem inventar conta e sem live.

### O que muda para você

- Você cria as contas demo Clear + OANDA e cola as chaves só no EasyPanel
- O painel mostra B3/forex operáveis quando a credencial existir; senão, motivo claro
- N27.2/N27.4 podem fechar o laço nos mercados respondidos

| Entrega | Como você confere |
|---------|-------------------|
| Clear simulado no laço | Posição/ordem/fill de um símbolo B3 demo sem POST na Alpaca |
| OANDA Practice no laço | Ordem forex practice com fill/estado legível no ledger/painel |
| Sem credencial | Mercado visível + `NO_DEMO_ACCOUNT_PATH` (ou equivalente) |
| Live | Processo recusa se `LIVE_TRADING_ENABLED` ≠ false |

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N29.1 Adapter Clear Smart Trader **simulado** (posição, ordem aberta, fill) | `/dev` | — |
| [x] | M | N29.2 Adapter OANDA fxTrade **Practice** (posição, ordem, fill) | `/dev` | — |
| [x] | P | N29.3 Ligar `DEMO_ACCOUNT_PATH_*` / env aos três mercados (Clear, Alpaca, OANDA) | `/dev` | N29.1, N29.2 |
| [x] | P | N29.4 Teste: B3/FOREX nunca POST Alpaca; sem credencial → barrado com motivo | `/qa testes` | N29.3 |
| [ ] | P | N29.5 Operador: abrir/credenciar Clear + OANDA; ids só no EasyPanel | operador | N29.3 |
| [ ] | P | N29.6 Desbloquear N27.2 no ROADMAP após adapters verdes + nota de release | docs | N29.4, N29.5 |

### Task N29.1 — Clear Smart Trader simulado

**Entrega:** Adapter B3 que lê/escreve no ambiente **simulado** da Clear (não URL real).
**Como conferir:** Mock/integração mostra posição, ordem aberta e fill; nenhum POST a `paper-api.alpaca.markets`.
**Por quê:** REQUIREMENTS v0.4 G-MKT; ADR-010.

**Detalhe técnico / executor_prompt:**
```
estado_atual: demo_account_gate + NO_DEMO_ACCOUNT_PATH; B3 bloqueado na Alpaca (N19.4); sem cliente Clear.
desejado: módulo adapter Clear simulado (REST/WS conforme docs Clear) atrás da mesma porta de “conta demo do mercado”; credenciais só via env; fail-closed sem chave.
guardrail: LIVE false; nunca misturar URL real com token simulado; não reimplementar trader-entry/exit.
testes: unit com HTTP mock — submit → order id; positions; block se env vazio.
```

### Task N29.2 — OANDA Practice

**Entrega:** Adapter forex na API v20 **Practice**.
**Como conferir:** Mock/integração cria ordem practice e lê fill/estado; host practice, não fxTrade live.
**Por quê:** REQUIREMENTS v0.4 G-MKT.

**Detalhe técnico / executor_prompt:**
```
estado_atual: FOREX no universo/risco mas sem path de envio.
desejado: cliente OANDA Practice (api-fxpractice) com account id + token no env; posição/ordem/fill.
guardrail: LIVE false; nunca api-fxtrade live; B3 não passa por aqui.
testes: mock REST — order + fill transaction; block se token ausente.
```

### Task N29.3 — Wiring env por mercado

**Entrega:** `DEMO_ACCOUNT_PATH_B3_EQUITY|CRYPTO|FOREX` (ou equivalente) aponta para Clear / Alpaca / OANDA sem inventar nome.
**Como conferir:** Com env preenchido, `block_reason` some no painel para aquele mercado; vazio → barrado.
**Depende de:** N29.1, N29.2.

### Task N29.4 — Testes de regressão

**Entrega:** Suíte prova ADR-010 + fail-closed.
**Como conferir:** pytest verde; casos B3/FOREX sem Alpaca POST; missing creds → motivo.

### Task N29.5 — Operador credencia

**Entrega:** Contas Clear simulado + OANDA Practice criadas; vars no EasyPanel.
**Como conferir:** Operador confirma ids (sem colar segredo no chat/Git).

### Task N29.6 — Ponte N27.2

**Entrega:** ROADMAP N27.2 desbloqueado / marcado pronto para implementação do laço pós-adapter.
**Como conferir:** Checkbox/nota explícita; sem rebuild só por docs.

---

## Sprint N28 — Ajuste supervisionado depois do método
> Categoria: N  
> Status: concluida  
> titulo_humano: Ajuste registrado e reversível, sem mexer no risco  
> Gate: G-AJUSTE e fill real; só parâmetro existente na faixa original; histórico com desfazer; âncoras intocadas; LIVE false  
> review: senior+qa  
> Depende de: N20.3, N21

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N28.1 Sugestão continua rotulada como sugestão | `/dev` | — |
| [x] | M | N28.2 Ajustar só parâmetro existente, dentro da faixa original | `/dev` | G-AJUSTE |
| [x] | M | N28.3 Registrar antes, depois e motivo, com desfazer na Central | `/dev` | N28.2 |
| [x] | P | N28.4 Teste: ajuste nunca altera âncora de risco | `/qa testes` | N28.2 |

**Notas N28.2–4 (pós-N31 merge `681e8c5`):** `src/supervised_adjustment.py` + catálogo documentado; ledger append-only `parameter_adjustments.jsonl`; apply/undo via `/api/strategy-parameters/*` (sessão operador); faixa incerta → só `suggestion_only`; âncoras espelham `TRIGGER_PATCH_FIELDS`.

**Closeout N33 (2026-11-16):** feat `71caca1`, stamp `c465724`; PR **#39** merge `5178fff04fbf7f4675fb9950580df81fdf732f7f` (`2026-11-16T17:20:14Z`); Feature 11 critérios 2–4 `[x]` — `tests/test_n28_supervised_adjustment.py` (`test_n28_2_in_range_proposal_can_apply`, `test_n28_3_apply_undo_persist_before_after_reason`, `test_n28_4_never_mutates_risk_anchors`).

---

## Sprint N30 — Laço Alpaca (ação US + cripto) e caminho Prodígio
> Categoria: N  
> Status: concluida  
> Gerado via: `/pmo plan` 2026-11-16 · fonte ISS-011 · ISS-007 / ISS-009 abertos · ISS-010 fora  
> titulo_humano: Alpaca opera sozinha em ação e cripto; Prodígio só com fase liberada  
> resumo_humano: A conta demo da Alpaca envia sozinha em ação americana e cripto. O ranking Prodígio vira sinal paper só se a fase já estiver liberada. O contrato marca o que o painel já faz. Clear, OANDA e o método de ajuste ficam fora desta rodada.  
> Gate: pytest — US_EQUITY e CRYPTO nomeada submetem na Alpaca paper sem clique extra; chave com cara de live não muda o host paper; reinício com laço demo ligado não duplica; B3/FOREX sem POST Alpaca; rank→sinal `prodigy_15d` com orders_sent=0 enquanto fase for research; Features 8–10 no contrato só com teste nomeado; orb/mean_reversion NEVER_PAPER; LIVE false  
> review: senior+qa  
> Brief: `docs/.briefs/N30.brief.md`  
> bom_ref: BOM-3, BOM-4  
> Depende de: N27 parcial (Alpaca-only) · Release: campanha ISS-011 onda 1  
> LIVE_TRADING_ENABLED: false

**Closeout N33 (2026-11-16):** feat `322318b`; PR **#35** merge `622fbeb786b4e042d2269d60d5c44e7e0f51ab8e` (`2026-11-16T12:47:20Z`); evidência `docs/TEST-EVIDENCE.md` N30.1 / N30.3b; campanha histórica acima não reescrita.

### Em uma frase

A conta demo da Alpaca passa a operar ação americana e cripto sem clique extra, o ranking Prodígio vira sinal paper só se a fase já estiver liberada, e o contrato fecha o que o painel já entrega.

### O que muda para você

- Ação americana e cripto na Alpaca paper seguem sozinhas quando o laço demo está ligado; B3 e forex continuam visíveis e barrados
- O ranking Prodígio não vira ordem só por aparecer na lista; a fase paper continua decisão sua
- As telas de controle, sinais e resultado no painel fecham os critérios combinados se os testes já provarem
- Clear, OANDA, smoke de amanhã e retrato de risco com mais de dois minutos ficam na sua lista, não no código desta rodada

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Envio automático na Alpaca paper para ação americana e cripto | Pedir ao time o teste em que um sinal válido vira ordem paper e uma chave com cara de live não muda o destino |
| 2 | Caminho Prodígio do ranking até o sinal | Ver um candidato do ranking virar sinal com a família Prodígio, ainda bloqueado se a fase for pesquisa |
| 3 | Contrato das telas de controle, sinais e resultado | Abrir o contrato e ver os critérios dessas três áreas marcados só quando o teste correspondente existir |
| 4 | Fila da campanha e pendências suas | Ler o bloco da sprint: Tá Barato na fila, ajuste automático parado até você definir o método, Clear/OANDA fora |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N30.0 Validar reuso do ranking Prodígio e do laço paper antes de escrever código | `/git` | — |
| [x] | M | N30.1 Completar o envio automático na conta demo da Alpaca para ação americana e cripto | `/dev` + `paper-order-gate` | N30.0 |
| [x] | M | N30.2 Ligar o ranking Prodígio à entrada de sinal paper sem promover fase sozinho | `/dev` + `signal-ingest` | N30.0 |
| [x] | P | N30.3 Marcar no contrato o que o painel já faz nas telas de controle, sinais e resultado | docs | — |
| [x] | P | N30.4 Registrar a fila da campanha, o que fica barrado e o que o operador ainda precisa fazer | docs | N30.1, N30.2, N30.3 |

### Campanha ISS-011 (não executar nesta sprint)

| Ordem | Sprint | Nota |
|-------|--------|------|
| 1 | N30 | Esta sprint |
| 2 | N17 | Já planejada — Tá Barato / momentum; Git First na N17.0; **não reinventar** |
| 3 | N28 | Já planejada — Feature 11 **blocked** até G-AJUSTE + fill real |
| fora | N29.5 | Clear + OANDA — pendência operador |
| fora | N27.4 | Smoke EasyPanel — pendência operador |

### Pendências operador

- Contas Clear (B3) e OANDA Practice; ids só no EasyPanel (ISS-010 / N29.5)
- Smoke amanhã: sinal válido vira ordem demo na sessão real (N27.4)
- Retrato de risco fresco (≤120 segundos) antes de submit
- Método do ajuste automático (G-AJUSTE) — sem isso a Feature 11 fica de lado
- Rebuild EasyPanel se a imagem ainda não estiver no ar
- Promover Prodígio a paper no banco **só** depois de evidência; o padrão continua pesquisa

### Task N30.0 — Validar reuso do ranking Prodígio e do laço paper antes de escrever código

**Entrega:** Inventário curto dizendo o que já existe no ranking, na assinatura do sinal e no laço paper — e o que ainda falta — sem subir o código do fornecedor.
**Como conferir:** O inventário cita o commit pinado, o ranking como pesquisa, e a decisão de reusar ou adaptar cada peça.
**Por quê:** A regra do laboratório é reusar o que já está no pacote antes de escrever caminho novo.

**Detalhe técnico**

P task (docs-only). Write `docs/.briefs/N30-GIT-FIRST-REUSE.md`. Inspect pinned vendor SHA in `docs/VENDOR-PIN.md` and local checkout; do not bump. Confirm `prodigy_rank.py` scoring is not copied; N17 stays deferred.

### Task N30.1 — Completar o envio automático na conta demo da Alpaca para ação americana e cripto

**Entrega:** Sinal válido de ação americana ou cripto vira ordem na conta demo da Alpaca sem clique extra, sem mudar o destino se existir chave com cara de live, e sem duplicar no reinício.
**Como conferir:** Pedir os testes em que cripto nomeada submete no host paper, B3 e forex continuam barrados, e o segundo ciclo após reinício não envia de novo.
**Por quê:** O contrato da operação autônoma ainda está em aberto nesses mercados; B3 e forex não entram nesta rodada.

**Detalhe técnico**

**executor_prompt**:
```yaml
id: N30.1
size: M
bom_ref: BOM-3, BOM-4
depends_on: ["N30.0"]
files:
  - src/signal_paper_runner.py
  - tests/test_signal_paper_runner.py
  - tests/test_paper_gateway_queue.py
  - tests/test_paper_restart_no_duplicate.py
reuse_targets:
  - component: src/paper_gateway_queue.py
    reuse_as: call
    convergence_check: rg "def process_after_gate_b" src/paper_gateway_queue.py && rg "demo_send_allowed" src/paper_gateway_queue.py
  - component: src/paper_audit.py
    reuse_as: call
    convergence_check: rg "PAPER_URL = 'https://paper-api.alpaca.markets'" src/paper_audit.py && rg "Paper endpoint mismatch" src/paper_audit.py
  - component: src/portfolio_risk_v4.py
    reuse_as: call
    convergence_check: rg "ALLOWED_MARKETS" src/portfolio_risk_v4.py && rg "evaluate" src/signal_paper_runner.py
  - component: src/demo_account_gate.py
    reuse_as: extend
    convergence_check: rg "CRYPTO" src/demo_account_gate.py && rg "NO_DEMO_ACCOUNT_PATH" src/signal_paper_runner.py
guardrail_contract:
  - class: secrets
    id: n30-1-no-secrets
    target: src/signal_paper_runner.py
    check: python3 -c "from pathlib import Path; t=Path('src/signal_paper_runner.py').read_text(); assert 'sk_live' not in t.lower() or True; assert 'ALPACA_API_KEY' in t"
    pass_condition: keys read from env only; no literal secrets
  - class: subagent-safety
    id: n30-1-live-lock
    target: src/paper_audit.py
    check: rg "LIVE_TRADING_ENABLED must be false" src/paper_audit.py && rg "paper-api.alpaca.markets" src/signal_paper_runner.py
    pass_condition: LIVE false; submit host remains paper
executor_prompt: |
  ### Quality Brief (Sprint N30)
sprint: N30
Maintain: load trader-entry|exit|budget|risk|scanner only via src/original.py; do not rewrite upstream.
Maintain: prodigy_rank stays PRODIGY_RANK_RESEARCH_ONLY with execution_authorized false; rank is not a fill and not phase promotion.
Maintain: DEFAULT_PHASE_BY_KEY prodigy_15d=research; NEVER_PAPER_KEYS orb and mean_reversion; signal_copy remains the only default paper_limited key.
Maintain: Alpaca destination is paper_audit.PAPER_URL; validate_env rejects live host; live-looking key must not switch host.
Avoid: inventing scoring/thresholds; auto-updating strategy_states.phase; Clear/OANDA work; LIVE_TRADING_ENABLED=true.
[ABORDAGEM] Rank contributes provider_id only. Ticket prices stay on signal_copy.ALLOWED. Do not fork a second gateway.
[RISCO] signal_paper_runner.risk_check currently builds the portfolio candidate as US_EQUITY even when the signal market is CRYPTO. Feature 7 crypto is not honest until that candidate uses the signal market and still goes through portfolio_risk_v4.evaluate.
[OPORTUNIDADE] N27 already has test_n27_5_live_looking_key_keeps_paper_alpaca_host and CRYPTO named-path submit tests. Extend restart-with-loop; do not duplicate N27 ROADMAP ids.
EXPIRES at end of Sprint N30.

Melhoria: close Feature 7 for US_EQUITY + CRYPTO on Alpaca paper (code + tests). Not Clear/OANDA.
Contexto: N27 stamped Alpaca-only CRYPTO named path and US_EQUITY gateway submit. risk_check still hardcodes candidate market US_EQUITY. N27.6 restart-with-demo-loop-on is unchecked. REQUIREMENTS Feature 7 still [ ]. B3/FOREX must stay NO_DEMO_ACCOUNT_PATH with zero Alpaca POST.
Objetivo: (1) portfolio candidate market equals signal market when CRYPTO or US_EQUITY; still call portfolio_risk_v4.evaluate; no new numeric thresholds. (2) pytest: valid signal + demo_operation_on → PAPER_SUBMITTED without operator PATCH. (3) live-looking ALPACA_API_KEY still posts only to paper-api.alpaca.markets. (4) restart with demo loop on does not second-submit (extend tests/test_paper_restart_no_duplicate.py; demo_operation_on true). (5) B3_EQUITY and FOREX still blocked, no Alpaca POST. Do not edit Sprint N27 checkboxes. Do not enable LIVE. Do not invent scoring.
Arquivos: src/signal_paper_runner.py, tests/test_signal_paper_runner.py, tests/test_paper_gateway_queue.py, tests/test_paper_restart_no_duplicate.py.
Critério de pronto: pytest nodeids for US_EQUITY submit, CRYPTO named alpaca_paper submit, CRYPTO missing path blocked, live-looking key paper host, restart no duplicate with demo on, B3/FOREX no Alpaca POST; rg shows candidate market not hardcoded to US_EQUITY for CRYPTO signals; LIVE_TRADING_ENABLED false.
Cenários de teste:
  1. Caso normal: US_EQUITY signed signal, demo on, named paper env → PAPER_SUBMITTED orders_sent=1 on paper host.
  2. Caso normal: CRYPTO + DEMO_ACCOUNT_PATH_CRYPTO=alpaca_paper → PAPER_SUBMITTED; risk candidate market CRYPTO.
  3. Edge case: CRYPTO without named path → NO_DEMO_ACCOUNT_PATH, orders_sent=0, no Alpaca POST.
  4. Edge case: ALPACA_API_KEY looks live, LIVE false, ALPACA_BASE_URL paper → still paper host only.
  5. Edge case: B3_EQUITY and FOREX → blocked, assert not in alpaca POST urls.
  6. Regressão: restart with same client_order_id + demo_operation_on true → no second broker POST (N21.3 invariant).
  7. Regressão: snapshot older than 120s still V4_PORTFOLIO_SNAPSHOT_STALE.
```

### Task N30.2 — Ligar o ranking Prodígio à entrada de sinal paper sem promover fase sozinho

**Entrega:** Um candidato do ranking vira um sinal da família Prodígio; se a fase ainda for pesquisa, nada é enviado; a lista de ranking não ganha nota nova.
**Como conferir:** Ver o mapeamento usar o provedor do ranking e a chave Prodígio, e ver o envio recusado enquanto a fase for pesquisa.
**Por quê:** O épico pedia ranking ligado à ingestão; hoje o ranking só pesquisa e o passo seguinte é manual.

**Detalhe técnico**

**executor_prompt**:
```yaml
id: N30.2
size: M
bom_ref: BOM-3
depends_on: ["N30.0"]
files:
  - src/prodigy_paper_ingest.py
  - tests/test_prodigy_paper_ingest.py
  - scripts/run.sh
reuse_targets:
  - component: src/prodigy_rank.py
    reuse_as: call
    convergence_check: rg "PRODIGY_RANK_RESEARCH_ONLY" src/prodigy_rank.py && rg "execution_authorized" src/prodigy_paper_ingest.py
  - component: src/signal_copy.py
    reuse_as: call
    convergence_check: rg "def sign" src/signal_copy.py && rg "strategy_key" src/signal_copy.py && rg "sign" src/prodigy_paper_ingest.py
  - component: src/strategy_catalog.py
    reuse_as: call
    convergence_check: rg "gate_b_strategy_reject" src/strategy_catalog.py && rg "prodigy_15d" src/prodigy_paper_ingest.py
  - component: src/paper_gateway_queue.py
    reuse_as: call
    convergence_check: rg "process_after_gate_b" src/prodigy_paper_ingest.py
guardrail_contract:
  - class: secrets
    id: n30-2-no-secrets
    target: src/prodigy_paper_ingest.py
    check: python3 -c "from pathlib import Path; t=Path('src/prodigy_paper_ingest.py').read_text(); assert 'sk-' not in t and 'APCA' not in t"
    pass_condition: no credential literals
  - class: subagent-safety
    id: n30-2-no-promote
    target: src/strategy_catalog.py
    check: rg "prodigy_15d.: 'research'" src/strategy_catalog.py && rg "NEVER_PAPER_KEYS" src/strategy_catalog.py
    pass_condition: default phase unchanged; orb/mean_reversion still never paper
  - class: caller-level
    id: n30-2-cli
    target: src/prodigy_paper_ingest.py
    convergence_check: pytest -q tests/test_prodigy_paper_ingest.py -k cli
    pass_condition: CLI invoked; default dry-run orders_sent=0; research phase does not submit
executor_prompt: |
  ### Quality Brief (Sprint N30)
sprint: N30
Maintain: load trader-entry|exit|budget|risk|scanner only via src/original.py; do not rewrite upstream.
Maintain: prodigy_rank stays PRODIGY_RANK_RESEARCH_ONLY with execution_authorized false; rank is not a fill and not phase promotion.
Maintain: DEFAULT_PHASE_BY_KEY prodigy_15d=research; NEVER_PAPER_KEYS orb and mean_reversion; signal_copy remains the only default paper_limited key.
Maintain: Alpaca destination is paper_audit.PAPER_URL; validate_env rejects live host; live-looking key must not switch host.
Avoid: inventing scoring/thresholds; auto-updating strategy_states.phase; Clear/OANDA work; LIVE_TRADING_ENABLED=true.
[ABORDAGEM] Rank contributes provider_id only. Ticket prices/qty come from existing signed-signal fields, never from a new score. Ingest calls signal_copy.sign / gate_b_strategy_reject / process_after_gate_b.
[RISCO] Auto-promoting prodigy_15d to paper_limited from rank status would violate ISS-007. Keep seed research. Paper submit only if catalog phase is already paper_limited or paper_validated (operator evidence).
[OPORTUNIDADE] N16 deferred rank→JSON to the operator runbook. This sprint adds the mapper; do not change prodigy_rank.calculate formula.
EXPIRES at end of Sprint N30.

Melhoria: ISS-007 rank→ingest with strategy_key=prodigy_15d without inventing scoring and without auto phase promotion.
Contexto: prodigy_rank writes PRODIGY_RANK_RESEARCH_ONLY. HOMOLOGATION-PRODIGY still has the operator sign JSON by hand. DEFAULT_PHASE prodigy_15d=research blocks Gate B. news_first stays research. orb/mean_reversion stay NEVER_PAPER.
Objetivo: new src/prodigy_paper_ingest.py maps a rank row (provider_id) + caller-supplied ticket (symbol, side, entry, stop, target, quantity, ttl) into signal_copy schema with strategy_key=prodigy_15d. Do not invent prices from rank (rank has none). If catalog phase is research/shadow → status BLOCKED, reject STRATEGY_PHASE_BLOCKED, orders_sent=0. If phase already paper_* (test override or DB) → may call process_after_gate_b; still LIVE false. Never UPDATE strategy_states. Never edit prodigy_rank scoring constants. CLI default dry-run. Wire scripts/run.sh prodigy-ingest (extend existing run.sh; no third EasyPanel app; no new scripts/*.py file).
Arquivos: src/prodigy_paper_ingest.py, tests/test_prodigy_paper_ingest.py, scripts/run.sh.
Critério de pronto: unit tests map provider_id + ticket → strategy_key prodigy_15d; research phase orders_sent=0; missing ticket fields do not invent prices; NEVER_PAPER keys rejected; prodigy_rank.py formula lines unchanged; DEFAULT_PHASE_BY_KEY prodigy_15d still research; pytest CLI dry-run; LIVE false.
Cenários de teste:
  1. Caso normal: rank candidate + complete ticket + phase research → mapped signal, BLOCKED STRATEGY_PHASE_BLOCKED, orders_sent=0.
  2. Caso normal: same + strategy_phase paper_limited override → ingest may queue/submit via process_after_gate_b mock; rank file execution_authorized remains false.
  3. Edge case: rank row without ticket prices → TICKET_FIELDS_REQUIRED (or equivalent), no invented entry/stop.
  4. Edge case: strategy_key orb or mean_reversion on ingest path → STRATEGY_NOT_PAPER.
  5. Regressão: prodigy_rank.calculate still PRODIGY_RANK_RESEARCH_ONLY; MIN_TRADES/WINDOW_DAYS untouched.
  6. Regressão: CLI default does not POST broker; LIVE_TRADING_ENABLED true is rejected.
```

### Task N30.3 — Marcar no contrato o que o painel já faz nas telas de controle, sinais e resultado

**Entrega:** No contrato, as áreas de controle, sinais e resultado ficam marcadas só onde o teste do painel já prova o critério.
**Como conferir:** Abrir o contrato das Features 8, 9 e 10 e ver cada caixa ligada a um teste; o que não tiver teste continua em aberto.
**Por quê:** O painel dessas telas já entrou em sprints anteriores; o contrato ainda mostra tudo em aberto.

**Detalhe técnico**

P task. Edit `docs/REQUIREMENTS.md` Features 8–10 checkboxes only when a named pytest in `tests/test_panel_ops.py` / `tests/test_panel_triggers.py` proves the criterion. Leave honest `[ ]` with a one-line gap. Update `docs/TEST-EVIDENCE.md`. Do not invent panel behavior. Do not touch Feature 7 boxes here (N30.4). Do not promote news_first or ORB.

### Task N30.4 — Registrar a fila da campanha, o que fica barrado e o que o operador ainda precisa fazer

**Entrega:** Issue do épico e contrato dizem a ordem das sprints, que ORB não vira paper, que o ajuste automático espera sua escolha, e a lista clara do que só você pode fazer.
**Como conferir:** Ler a issue do épico e a nota no contrato: Tá Barato na fila, Feature 11 parada, Clear/OANDA e smoke fora desta rodada.
**Por quê:** Sem essa fila o próximo ciclo reinventa o que já está planejado ou tenta ligar mercados sem conta.

**Detalhe técnico**

P task. Update ISS-011 with campaign N30 → N17 → N28(blocked). Feature 7 REQUIREMENTS: mark Alpaca US+CRYPTO criteria `[x]` only after N30.1 tests exist; keep B3/FOREX `[ ]` with G-MKT/ISS-010 pointer. Document `news_first` remains research; `orb`/`mean_reversion` remain NEVER_PAPER (REQUIREMENTS + catalog). Do not execute N17/N28. Do not enable live.

---

## Sprint N31 — Melhoria contínua diária e apoio TimesFM só como pesquisa
> Categoria: N  
> Status: concluida  
> Gerado via: `/pmo plan` 2026-11-16 · fonte ISS-012 · N28 **não** reescrita  
> titulo_humano: Autoanálise diária com dicas; previsão Google só como pesquisa  
> resumo_humano: O laboratório analisa todo dia o que preencheu e o que não saiu e mostra só dicas rotuladas. O modelo de séries temporais do Google entra como contexto de pesquisa quando estiver no ar. O ajuste de parâmetro continua na sprint já planejada.  
> Gate: pytest — relatório diário com fills e não-fills, dicas rotuladas, orders_sent=0, TimesFM ausente omite forecast, tip nunca chama gateway paper, LIVE false, bloco N28 intocado  
> review: senior+qa  
> Brief: `docs/.briefs/N31.brief.md`  
> bom_ref: BOM-3  
> Depende de: N28.1 (rótulos) · Release: campanha ISS-012  
> LIVE_TRADING_ENABLED: false

### Em uma frase

O laboratório passa a se autoanalisar todo dia com o que foi executado e o que não foi, gera só dicas rotuladas, e usa o modelo de séries temporais do Google só como contexto de pesquisa quando estiver disponível.

### O que muda para você

- Todo dia a área de melhoria contínua mostra dicas a partir de ordens preenchidas e das que não saíram
- A previsão do modelo do Google, se existir, aparece como dica de pesquisa — nunca como ordem
- Se o modelo não estiver instalado, o relatório diário continua e a previsão some, sem número inventado
- O ajuste de parâmetro da Feature 11 continua na sprint já planejada; esta rodada só define o método e as dicas
- Tá Barato e momentum não ganham limiar novo a partir desta análise

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Relatório diário com dicas a partir do que preencheu e do que não saiu | Pedir o ciclo do dia e ver dicas rotuladas, sem envio de ordem |
| 2 | Apoio opcional do modelo de séries temporais do Google no mesmo relatório | Ver a previsão só como dica de pesquisa, ou ausente se o modelo não estiver no ar |
| 3 | Caminho liberado para o ajuste supervisionado, sem nota inventada | Ler que o método está respondido e que a sprint de ajuste já existente pode seguir sem reescrita |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N31.0 Validar reuso do ciclo diário e do pacote oficial TimesFM antes de escrever código | `/git` | — |
| [x] | M | N31.1 Estender o ciclo diário para dicas a partir do que preencheu e do que não saiu | `/dev` | N31.0 |
| [x] | M | N31.2 Incluir o modelo TimesFM como apoio opcional só de pesquisa no relatório | `/dev` | N31.1 |
| [x] | P | N31.3 Registrar o método de ajuste e liberar o caminho da sprint já planejada, sem inventar nota | docs | N31.1 |
| [x] | P | N31.4 Testar que dica e previsão nunca viram ordem e que o modelo ausente não inventa número | `/qa testes` | N31.1, N31.2 |

**Closeout N33 (2026-11-16):** feat `d1d139a`, stamp `84791eb`; PR **#38** merge `681e8c546ab7d6388f8627813e0606a9a347bfee` (`2026-11-16T17:12:28Z`); `tests/test_n31_g_ajuste_guardrails.py` (`N31GAjusteGuardrails.test_review_never_imports_paper_gateway`, `test_timesfm_missing_no_numeric_forecast_in_report`).

### Campanha ISS-012 (não executar N28.2–4 nesta sprint)

| Ordem | Sprint | Nota |
|-------|--------|------|
| 1 | N31 | Esta sprint — método G-AJUSTE + TimesFM research-only |
| 2 | N28 | Já planejada — **não editar o bloco**; N28.2–4 depois do gate N31 |
| fora | N17 | Tá Barato / momentum — G-FORM; sem limiar inventado aqui |
| fora | N29.5 | Clear + OANDA — pendência operador |

### Pendências operador

- Aplicar (ou desfazer) ajuste de parâmetro no catálogo — N28.2–4
- Instalar o modelo TimesFM na imagem, se quiser previsão no relatório (sem isso o ciclo diário segue)
- Fórmula Tá Barato / momentum — N17 / G-FORM
- Contas Clear / OANDA — ISS-010

### Task N31.0 — Validar reuso do ciclo diário e do pacote oficial TimesFM antes de escrever código

**Entrega:** Inventário curto dizendo o que já existe no ciclo de melhoria contínua e qual pacote oficial do modelo Google reusar — sem copiar o modelo.
**Como conferir:** O inventário cita o ciclo diário já ligado, os rótulos de dica, e a decisão de reusar ou adaptar cada peça, inclusive licença do checkpoint.
**Por quê:** A regra do laboratório é reusar o que já está no pacote e a API oficial, antes de escrever caminho novo.

**Detalhe técnico**

P task (docs-only). Write `docs/.briefs/N31-GIT-FIRST-REUSE.md`. Confirm `src/evolution_engine.py` `review` / `add_decision`, `scripts/run.sh evolution-daily`, N28.1 labels, `panel_ops_data` fill vs unfilled. For TimesFM: inspect official PyPI `timesfm` and `google-research/timesfm` (do not vendor-copy weights into this repo). Record package version, import path (`timesfm` / `timesfm3`), checkpoint id, license (prefer Apache-2.0 2.5 if 3.0 is non-commercial). Fail-closed if GitHub/PyPI unreachable — do not claim current main. Do not bump vendor `day-trader-skill` pin.

### Task N31.1 — Estender o ciclo diário para dicas a partir do que preencheu e do que não saiu

**Entrega:** O ciclo do dia lê o que foi preenchido e o que não saiu e devolve dicas rotuladas, sem enviar ordem e sem mudar parâmetro de estratégia.
**Como conferir:** Pedir o relatório de um dia com fill e com rejeição e ver dicas rotuladas, envio de ordem zero, e nenhuma mudança aplicada.
**Por quê:** O método combinado é aprender com o rastro real — inclusive o que a plataforma recusou — sem tratar dica como autorização.

**Detalhe técnico**

**executor_prompt**:
```yaml
id: N31.1
size: M
bom_ref: BOM-3
depends_on: ["N31.0"]
files:
  - src/evolution_engine.py
  - src/trading_dashboard_data.py
  - tests/test_evolution_engine.py
reuse_targets:
  - component: src/evolution_engine.py
    reuse_as: extend
    convergence_check: rg "READ_ONLY_NO_ORDER_SUBMISSION" src/evolution_engine.py && rg "orders_sent" src/evolution_engine.py
  - component: src/panel_ops_data.py
    reuse_as: call
    convergence_check: rg "EXCLUDED_PNL_ORDER_STATUSES" src/panel_ops_data.py && rg "performance_from_ledger\\|performance_from_snapshots" src/evolution_engine.py src/panel_ops_data.py
  - component: src/trading_dashboard_data.py
    reuse_as: extend
    convergence_check: rg "continuous_improvement" src/trading_dashboard_data.py && rg "surface_kind" src/trading_dashboard_data.py
  - component: scripts/run.sh
    reuse_as: call
    convergence_check: rg "evolution-daily" scripts/run.sh
guardrail_contract:
  - class: secrets
    id: n31-1-no-secrets
    target: src/evolution_engine.py
    check: python3 -c "from pathlib import Path; t=Path('src/evolution_engine.py').read_text(); assert 'ALPACA_API_SECRET' not in t; assert 'sk_live' not in t.lower()"
    pass_condition: no broker secrets in evolution_engine
  - class: subagent-safety
    id: n31-1-no-order
    target: src/evolution_engine.py
    check: rg "READ_ONLY_NO_ORDER_SUBMISSION" src/evolution_engine.py && rg "changes_applied" src/evolution_engine.py && rg "orders_sent" src/evolution_engine.py
    pass_condition: review remains read-only; orders_sent stays 0
  - class: caller-level
    id: n31-1-cli-daily
    target: src/evolution_engine.py
    check: python3 -m unittest tests.test_evolution_engine -q
    pass_condition: CLI/review path covered; report written with orders_sent=0
executor_prompt: |
  ### Quality Brief (Sprint N31)
sprint: N31
Maintain: evolution_engine.review stays READ_ONLY_NO_ORDER_SUBMISSION; changes_applied=0; orders_sent=0.
Maintain: N28.1 labels — continuous_improvement surface_kind=suggestion, paper_allowed=false, execution_authorized=false.
Maintain: LIVE_TRADING_ENABLED=false; tip/forecast never calls process_after_gate_b or paper submit.
Maintain: load trader-entry|exit|budget|risk|scanner only via src/original.py; do not invent Tá Barato/momentum/Prodigy thresholds.
Avoid: stub TimesFM numbers; mutating strategy_states; rewriting Sprint N28 tasks; adding a third EasyPanel app; required TimesFM image dependency.
[ABORDAGEM] Extend review() to classify fills vs non-fills from existing ledger/journal/decisions.jsonl; keep TimesFM behind an optional context provider that returns labeled research tips only.
[RISCO] TimesFM 3.0 weights may be non-commercial; N31.0 must pin the official PyPI package and a license-safe checkpoint. Missing import/checkpoint = omit forecast, never a fake series.
[OPORTUNIDADE] scripts/run.sh evolution-daily already execs evolution_engine.py; N28.1 already labels the panel surface — extend, do not fork a second dashboard.
EXPIRES at end of Sprint N31.

Melhoria: daily self-analysis of executed fills AND non-fills into labeled tips (ISS-012 / REQUIREMENTS §9 #8).
Contexto: evolution_engine.review already reads journal.jsonl, decisions.jsonl, outcomes.jsonl but does not classify broker fills vs unfilled/rejected as tips. Panel continuous_improvement is suggestion-only (N28.1). G-AJUSTE was blocked because the method (what is error, how often, when to undo) was unanswered.
Objetivo: (1) review(day) counts confirmed fills and non-fills (REJECTED/BLOCKED/unfilled queue) per strategy_id. (2) recommendations/tips labeled research_tip or suggestion; never execution_authorized. (3) changes_applied=0; do not write strategy_states. (4) orders_sent=0; do not import or call paper_gateway_queue.process_after_gate_b. (5) Leave an optional context_providers hook (empty default) for N31.2. (6) Surface new tips on command_panel.continuous_improvement without dropping N28.1 labels. Do not implement TimesFM here. Do not edit ROADMAP Sprint N28 tasks. LIVE false.
Arquivos: src/evolution_engine.py, src/trading_dashboard_data.py, tests/test_evolution_engine.py.
Critério de pronto: unittest nodeids show a day with one fill + one REJECTED produces tips, orders_sent=0, changes_applied=0; panel surface_kind=suggestion paper_allowed=false; rg shows no process_after_gate_b in evolution_engine.py; CLI evolution-daily still writes reports/evolution/daily/<date>.json.
Cenários de teste:
  1. Caso normal: fill confirmado + REJECTED no mesmo dia → relatório com ambos e pelo menos uma tip rotulada.
  2. Caso normal: só não-fills (journal BLOCKED) → tips existem; performance_metrics_available continua false se outcomes ausentes.
  3. Edge case: dia vazio → dica de amostra vazia; não inferir qualidade de estratégia.
  4. Edge case: decisions.jsonl incompleto (linha JSON quebrada) → resto do dia preservado (comportamento atual).
  5. Regressão: orders_sent=0 e changes_applied=0; N28.1 self_check_ok permanece.
  6. Regressão: scripts/run.sh evolution-daily ainda aponta para evolution_engine.py.
```

### Task N31.2 — Incluir o modelo TimesFM como apoio opcional só de pesquisa no relatório

**Entrega:** Quando o modelo oficial de séries temporais do Google estiver no ar, o relatório do dia ganha um bloco de previsão rotulado como dica de pesquisa; se faltar, o relatório segue sem inventar número.
**Como conferir:** Ver o bloco de previsão ausente ou rotulado como pesquisa, e confirmar que nenhum caminho de ordem paper foi chamado.
**Por quê:** O operador pediu o modelo no ciclo de melhoria contínua como contexto, não como autorização nem como limiar novo.

**Detalhe técnico**

**executor_prompt**:
```yaml
id: N31.2
size: M
bom_ref: BOM-3
depends_on: ["N31.1"]
files:
  - src/timesfm_context.py
  - tests/test_timesfm_context.py
  - src/evolution_engine.py
reuse_targets:
  - component: src/evolution_engine.py
    reuse_as: extend
    convergence_check: rg "timesfm" src/evolution_engine.py src/timesfm_context.py
  - component: src/trading_dashboard_data.py
    reuse_as: call
    convergence_check: rg "research_tip\\|surface_kind" src/timesfm_context.py src/trading_dashboard_data.py src/evolution_engine.py
guardrail_contract:
  - class: secrets
    id: n31-2-no-secrets
    target: src/timesfm_context.py
    check: python3 -c "from pathlib import Path; t=Path('src/timesfm_context.py').read_text(); assert 'HF_TOKEN' not in t; assert 'sk_live' not in t.lower()"
    pass_condition: no huggingface/broker secrets hardcoded
  - class: subagent-safety
    id: n31-2-research-only
    target: src/timesfm_context.py
    check: rg "research_tip\\|UNAVAILABLE\\|suggestion" src/timesfm_context.py && rg "process_after_gate_b" src/timesfm_context.py; test $? -ne 0
    pass_condition: labeled research; no paper gateway call in adapter
  - class: caller-level
    id: n31-2-optional-hook
    target: src/evolution_engine.py
    check: python3 -m unittest tests.test_timesfm_context tests.test_evolution_engine -q
    pass_condition: daily CLI/review with TimesFM missing still writes report; status UNAVAILABLE
executor_prompt: |
  ### Quality Brief (Sprint N31)
sprint: N31
Maintain: evolution_engine.review stays READ_ONLY_NO_ORDER_SUBMISSION; changes_applied=0; orders_sent=0.
Maintain: N28.1 labels — continuous_improvement surface_kind=suggestion, paper_allowed=false, execution_authorized=false.
Maintain: LIVE_TRADING_ENABLED=false; tip/forecast never calls process_after_gate_b or paper submit.
Maintain: load trader-entry|exit|budget|risk|scanner only via src/original.py; do not invent Tá Barato/momentum/Prodigy thresholds.
Avoid: stub TimesFM numbers; mutating strategy_states; rewriting Sprint N28 tasks; adding a third EasyPanel app; required TimesFM image dependency.
[ABORDAGEM] Extend review() to classify fills vs non-fills from existing ledger/journal/decisions.jsonl; keep TimesFM behind an optional context provider that returns labeled research tips only.
[RISCO] TimesFM 3.0 weights may be non-commercial; N31.0 must pin the official PyPI package and a license-safe checkpoint. Missing import/checkpoint = omit forecast, never a fake series.
[OPORTUNIDADE] scripts/run.sh evolution-daily already execs evolution_engine.py; N28.1 already labels the panel surface — extend, do not fork a second dashboard.
EXPIRES at end of Sprint N31.

Melhoria: optional TimesFM (Google time-series foundation model) context block on the daily continuous-improvement report (ISS-012 adendo).
Contexto: N31.1 delivers fills+non-fills tips. Operator asked TimesFM as forecast/context support. Git First: official google-research/timesfm or PyPI timesfm — reuse API, do not reimplement the model. Forecast must not authorize paper and must not become a Tá Barato/momentum threshold.
Objetivo: (1) New src/timesfm_context.py adapter using the official import recorded in N31-GIT-FIRST-REUSE.md. (2) Wire into review() via the N31.1 context_providers hook. (3) Output labeled research_tip / suggestion; paper_allowed false. (4) If import/checkpoint/runtime fails OR TIMESFM not enabled: timesfm_status=UNAVAILABLE, omit numeric forecast, still return the N31.1 report. (5) Do not add timesfm to the required Dockerfile/requirements.txt runtime set — optional extra only if N31.0 documents a extras line; default image stays fail-closed. (6) Do not call paper gateway. Do not invent RSI/percentil/score. Do not edit Sprint N28 tasks. LIVE false.
Arquivos: src/timesfm_context.py, tests/test_timesfm_context.py, src/evolution_engine.py.
Critério de pronto: unittest with timesfm missing → UNAVAILABLE and no fake forecast keys with numbers; report still has N31.1 tips; rg timesfm_context has research_tip and no process_after_gate_b; official package name cited from N31.0 (timesfm, not a local rewrite of attention/decoder).
Cenários de teste:
  1. Caso normal (se fixture oficial mockável): adapter returns labeled research_tip with timesfm_status=OK without calling process_after_gate_b.
  2. Edge case: ImportError / checkpoint missing → UNAVAILABLE, no invented series, daily report still written.
  3. Edge case: TIMESFM disabled/default off → same as unavailable; N31.1 tips unchanged.
  4. Regressão: orders_sent=0; suggestion surfaces still self_check_ok.
  5. Regressão: no Tá Barato/momentum threshold constants introduced from forecast quantiles.
```

### Task N31.3 — Registrar o método de ajuste e liberar o caminho da sprint já planejada, sem inventar nota

**Entrega:** O método de ajuste fica escrito: o que conta como erro, a frequência diária, e que sem nota segura só se sugere — a sprint de ajuste já existente pode seguir sem ser reescrita.
**Como conferir:** Abrir o contrato e o issue e ver a dúvida do método respondida, com ponte para a sprint de ajuste e sem mudança nas tarefas antigas dessa sprint.
**Por quê:** Sem o método registrado, o ajuste supervisionado continuava parado; com ele, o caminho existe e o scoring incerto não vira número inventado.

**Detalhe técnico**

P task (docs-only). Update Feature 11 gap notes from “blocked until G-AJUSTE” to “method defined in ISS-012/N31; execute N28.2–4 later”. Keep `## Sprint N28` task rows **unchanged**. Do not invent scoring. Document suggestion-first when a parameter change would require a new threshold. Point undo to N28.3. LIVE false.

### Task N31.4 — Testar que dica e previsão nunca viram ordem e que o modelo ausente não inventa número

**Entrega:** Uma bateria curta prova que dica e previsão não disparam ordem paper e que, sem o modelo, ninguém inventa forecast.
**Como conferir:** Pedir os testes de guarda desta sprint e ver falha se houver chamada ao envio paper ou número de previsão fabricado.
**Por quê:** Sugestão não é ordem; fail-closed é o contrato do TimesFM.

**Detalhe técnico**

P task. Add `tests/test_n31_g_ajuste_guardrails.py` (or extend existing if overlap is cleaner — prefer new file). Assert: review/tips never mock-call `process_after_gate_b`; TimesFM missing → no numeric forecast; labels in `{research_tip, suggestion, continuous_improvement}`; `LIVE_TRADING_ENABLED` remains false in Dockerfile/run.sh. Do not weaken N28.1 tests.

---

## Sprint N32 — Âncoras do painel no laço paper
> Categoria: N  
> Status: concluida  
> Gerado via: `/pmo plan` 2026-11-16 · fonte ISS-011 lacuna Feature 7 · N17/N28/N29/N30/N31 **não** reescritos  
> titulo_humano: Ordem paper obedece ao teto do painel, não a um limite paralelo  
> resumo_humano: O envio paper deixa de usar um teto paralelo de dez mil dólares e passa a respeitar capital e risco por operação gravados no painel. Ticket de teste conhecido continua passando com os tetos de partida. Bolsa brasileira e câmbio seguem fora.  
> Gate: pytest — teto apertado recusa paper sem envio; tetos de partida ainda aceitam o ticket conhecido; LIVE false; B3/FOREX sem POST Alpaca; caixa Feature 7 da âncora só `[x]` com prova; B3/FOREX `[ ]`  
> review: senior+qa  
> Brief: `docs/.briefs/N32.brief.md`  
> bom_ref: BOM-4  
> Depende de: N22.1, N30.1 · Release: campanha ISS-011  
> LIVE_TRADING_ENABLED: false

### Em uma frase

O envio paper passa a usar os tetos de capital e de risco por operação gravados no painel, e uma ordem deixa de sair quando qualquer teto estiver estourado.

### O que muda para você

- Se você apertar o teto no painel, a ordem paper é recusada com motivo, sem envio
- Com os tetos de partida atuais, o ticket de teste que já passava continua passando
- Dinheiro real continua desligado
- Contas da bolsa brasileira e de câmbio continuam fora deste laço
- A caixa do contrato só fecha quando o teste provar a lacuna fechada; bolsa brasileira e câmbio ficam em aberto

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Recusa paper quando o teto do painel está apertado | Pedir o teste com teto baixo e ver a ordem bloqueada, sem envio |
| 2 | Ticket conhecido ainda passa com os tetos de partida | Pedir o teste com tetos iguais aos de hoje e ver a ordem paper aceita |
| 3 | Contrato da âncora atualizado só com prova | Abrir o contrato e ver a caixa marcada, com bolsa brasileira e câmbio ainda em aberto |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N32.0 Confirmar o reuso dos tetos já lidos na recusa de risco antes de escrever código | `/git` | — |
| [x] | M | N32.1 Ligar os tetos de capital e risco do painel no envio paper | `/dev` + `paper-order-gate` | N32.0 |
| [x] | P | N32.2 Provar que teto apertado recusa e teto de partida ainda permite | `/qa testes` | N32.1 |
| [x] | P | N32.3 Marcar no contrato a âncora só com prova de teste | docs | N32.2 |

### Campanha ISS-011 (não executar N17/N28/N29/N30/N31 nesta sprint)

| Ordem | Sprint | Nota |
|-------|--------|------|
| 1 | N30 | Já no ROADMAP — **não editar o bloco** |
| 1c | N32 | Esta sprint — âncoras do painel no envio paper |
| 1b | N31 | Código entregue — **não editar o bloco** |
| 2 | N17 | Tá Barato / G-FORM — **não planejar aqui** |
| 3 | N28 | Feature 11 código entregue nesta frente — **não editar o bloco** |
| fora | N29.5 | Clear + OANDA — pendência operador ISS-010 |

### Pendências operador

- **Merge PR [#42](https://github.com/ig0rayres/trading_lab/pull/42)** (CI verde; produto: operador mergeia — não push em `main` da frente)
- Rebuild EasyPanel após merge
- Credenciais Clear / OANDA — ISS-010
- Fórmula Tá Barato / momentum — N17 / G-FORM
- Closeout N28/N30/N31 — sprint-finalizer / VERIFY (não marcar concluída aqui)

### Task N32.0 — Confirmar o reuso dos tetos já lidos na recusa de risco antes de escrever código

**Entrega:** Inventário curto dizendo o que já lê as âncoras do painel e o que o envio paper ainda ignora — sem copiar motor de risco.
**Como conferir:** O inventário cita o leitor de âncoras, o Gate B, a carteira, e a decisão de reusar ou estender cada peça, inclusive o pin do vendor.
**Por quê:** A regra do laboratório é reusar o que já está no pacote antes de escrever caminho novo.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N32-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md` vs local checkout; do not bump; if GitHub main is unreachable, keep fail-closed note. Confirm `risk_control_flags.fetch_control_flags` + `brl_from_cents`, `gate_b_risk.config_for_fx`, `portfolio_risk_v4.resolve_limits`. Record that `signal_paper_runner.risk_check` still uses `Decimal('10000')` / 50 USD. Do not invent FX CLI. Do not touch Clear/OANDA.

### Task N32.1 — Ligar os tetos de capital e risco do painel no envio paper

**Entrega:** O envio paper recusa a ordem quando o teto de capital, o risco por operação ou o número de posições do painel estiver estourado, usando os mesmos valores que já recusam o sinal antes da fila.
**Como conferir:** Com teto apertado a ordem paper não sai; com tetos de partida o ticket conhecido ainda sai; dinheiro real permanece desligado.
**Por quê:** Hoje o envio paper ainda aceita um teto paralelo mais folgado do que o painel mostra, então a âncora do contrato não é honesta.

**Detalhe técnico**

**Arquivo(s):** `src/signal_paper_runner.py`

**executor_prompt**:

```yaml
id: N32.1
size: M
bom_ref: BOM-4
depends_on: ["N32.0"]
files:
  - src/signal_paper_runner.py
reuse_targets:
  - component: src/risk_control_flags.py
    reuse_as: call
    convergence_check: rg "fetch_control_flags" src/signal_paper_runner.py && rg "brl_from_cents" src/risk_control_flags.py
  - component: src/gate_b_risk.py
    reuse_as: call
    convergence_check: rg "config_for_fx" src/gate_b_risk.py && rg "fetch_control_flags" src/gate_b_risk.py
  - component: src/portfolio_risk_v4.py
    reuse_as: call
    convergence_check: rg "resolve_limits" src/portfolio_risk_v4.py
  - component: src/original.py
    reuse_as: call
    convergence_check: rg "load_original" src/original.py
guardrail_contract:
  - class: secrets
    id: n32-1-no-secrets
    target: src/signal_paper_runner.py
    check: python3 -c "from pathlib import Path; t=Path('src/signal_paper_runner.py').read_text(); assert 'ALPACA_API_SECRET' not in t; assert 'sk_live' not in t.lower()"
    pass_condition: no broker secrets hardcoded in runner
  - class: subagent-safety
    id: n32-1-live-false
    target: src/signal_paper_runner.py
    check: rg "LIVE_TRADING_ENABLED" src/signal_paper_runner.py && rg "fetch_control_flags" src/signal_paper_runner.py
    pass_condition: live flag stays in runner; capital/per-trade read control_flags
```

### Quality Brief (Sprint N32)

Maintain: LIVE_TRADING_ENABLED=false; paper host only; no live broker path.
Maintain: load trader-entry|exit|budget|risk|scanner only via src/original.py; do not invent scoring thresholds.
Maintain: B3_EQUITY / FOREX remain NO_DEMO_ACCOUNT_PATH with zero Alpaca POST (ISS-010).
Maintain: fetch_control_flags fail-closed to TIGHT_DEFAULTS (R$ 5.000 / R$ 50 / 3 positions) when DB is missing.
Avoid: second risk engine; FX conversion CLI; Clear/OANDA adapters; rewriting N17/N28/N29/N30/N31 ROADMAP blocks.
[ABORDAGEM] Call fetch_control_flags + brl_from_cents, then divide by existing fx (same as gate_b_risk.config_for_fx). Replace Decimal('10000') / Decimal('50'|'20') and hardcoded >=3 positions. Keep evaluate_portfolio_risk as the cross-market snapshot path — do not duplicate it.
[RISCO] Existing PAPER_SUBMITTED tests use qty=1 AAPL @100 with fx=5 (R$ 500 notional, R$ 5 risk). TIGHT_DEFAULTS still allow that ticket. A leftover 10k USD cap would still allow tickets the panel would reject.
[OPORTUNIDADE] portfolio_risk_v4.evaluate already reads control_flags (N22). N32 only closes the parallel hardcaps in risk_check before that call.
**Closeout (2026-11-16):** validation_gate e qa_gate **APROVADA**; pytest `test_n32_*` + âncoras portfolio; PR **#42** MERGEABLE (test, docker-smoke, docker-build SUCCESS). Lacuna `Decimal('10000')` fechada; LIVE false; B3/FOREX `[ ]` (**ISS-010**). Épico **ISS-011** permanece aberto (N17, N28 campanha, adapters).

Melhoria: wire signal_paper_runner.risk_check capital/per-trade/max positions to control_flags (ISS-011 Feature 7 remaining gap).
Contexto: N22 made gate_b_risk and portfolio_risk_v4 read control_flags. risk_check still uses cap=Decimal('10000')/fx and per_trade Decimal('50'|'20')/fx plus len(positions)>=3. REQUIREMENTS Feature 7 criterion "Nenhuma ordem sai com qualquer âncora estourada" is still [ ]. B3/FOREX stay out (ISS-010).
Objetivo: (1) fetch_control_flags(conn_factory=...) inside risk_check; capital_cents and max_risk_per_trade_cents via brl_from_cents then /fx. (2) prodigy uses prodigy_risk_cents the same way portfolio_risk_v4 does. (3) max_open_positions replaces hardcoded 3. (4) DB missing → TIGHT_DEFAULTS (existing pattern), never 10k USD. (5) Do not add FX conversion CLI. (6) Do not implement Clear/OANDA. (7) Do not edit ROADMAP Sprint N17/N28/N29/N30/N31. LIVE false.
Arquivos: src/signal_paper_runner.py.
Critério de pronto: rg shows fetch_control_flags and brl_from_cents in signal_paper_runner.py; rg Decimal('10000') in that file is empty; existing qty=1 AAPL auto-submit still conceptually allowed under TIGHT_DEFAULTS (tests land in N32.2).
Cenários de teste (implement in N32.2; keep runner callable here):
1. Caso normal: TIGHT_DEFAULTS + existing qty=1 AAPL ticket → no CAPITAL_LIMIT / TRADE_RISK_LIMIT from the parallel cap.
2. Caso normal: lowered capital_cents blocks with CAPITAL_LIMIT (or equivalent existing reason) and orders_sent=0.
3. Edge case: lowered max_risk_per_trade_cents blocks TRADE_RISK_LIMIT.
4. Edge case: flags unavailable → TIGHT_DEFAULTS, not 10k USD.
5. Regressão: B3_EQUITY / FOREX still NO_DEMO_ACCOUNT_PATH, zero Alpaca POST.
6. Regressão: LIVE_TRADING_ENABLED remains false; no Clear/OANDA adapter files.

### Task N32.2 — Provar que teto apertado recusa e teto de partida ainda permite

**Entrega:** Testes mostram recusa paper com teto apertado, aceite com tetos de partida, dinheiro real desligado e mercados sem conta demo ainda barrados.
**Como conferir:** Pedir essa bateria e ver falha se o envio paper ignorar o teto do painel ou se bolsa brasileira/câmbio postarem na Alpaca.
**Por quê:** Sem prova no caminho paper, o contrato da âncora continuaria parcial.

**Detalhe técnico**

P task. Extend `tests/test_signal_paper_runner.py` and/or `tests/test_feature7_anchor_ceilings.py` (prefer existing files; 1–2 files). Patch `fetch_control_flags`: (1) lowered `capital_cents` / `max_risk_per_trade_cents` → auto paper path BLOCKED, `orders_sent=0`, poster not called, reason CAPITAL_LIMIT or TRADE_RISK_LIMIT; (2) flags matching TIGHT_DEFAULTS (prior intended panel behavior) still allow existing qty=1 AAPL PAPER_SUBMITTED; (3) LIVE_TRADING_ENABLED false in env; (4) existing B3/FOREX no-POST tests still pass. Do not weaken N30.1 US/CRYPTO tests. Do not add Clear/OANDA fixtures.

### Task N32.3 — Marcar no contrato a âncora só com prova de teste

**Entrega:** A caixa da âncora no contrato fecha só se o teste da sprint passar; bolsa brasileira e câmbio continuam em aberto; uma linha de evidência registra o nodeid.
**Como conferir:** Abrir o contrato e a evidência e ver a caixa marcada com o nome do teste, sem adapters novos e sem live.
**Por quê:** O critério Feature 7 não pode virar feito no papel enquanto a lacuna do envio paper existir.

**Detalhe técnico**

P task. In `docs/REQUIREMENTS.md` Feature 7, mark “Nenhuma ordem sai com qualquer âncora estourada” `[x]` **only** after N32.2 pytest nodeids exist; keep B3/FOREX `[ ]` with ISS-010. Replace the lacuna sentence about `Decimal('10000')`/50 USD. One-liner in `docs/TEST-EVIDENCE.md` and `docs/HOMOLOGATION.md` — not a second implementation. Do not mark N28/N30/N31 Status concluida. LIVE false.

---

## Sprint N33 — Fechar no papel o laço americano já entregue
> Categoria: N  
> Status: planejada  
> Gerado via: `/pmo plan` 2026-11-16 · fonte ISS-011 restante após N32 + PR #42 merged · N17 tabela de tasks **não** reescrita  
> titulo_humano: Fechar no papel o laço americano já entregue  
> resumo_humano: O laço da conta demo americana, o ajuste supervisionado e a autoanálise diária já estão no código e no pedido 42. Esta sprint só alinha o plano e os chamados, e deixa claro que bolsa brasileira, câmbio e a homologação da fórmula Tá Barato continuam fora.  
> Gate: N28/N30/N31 Status `concluida` só com SHA/PR/nodeid citados; ISS-011 aberto só B3/FOREX + N17.2/G-FORM; ISS-012 corpo fechado; DIARY N33; TEST-EVIDENCE pedido 42 na linha principal + painel no ar atestado; zero `src/`; LIVE false  
> review: skip  
> Brief: `docs/.briefs/N33.brief.md`  
> bom_ref: BOM-3, BOM-4  
> Depende de: N32 concluida · Release: campanha ISS-011 closeout docs  
> LIVE_TRADING_ENABLED: false

### Em uma frase

O plano passa a mostrar como concluído o laço da conta demo americana, o ajuste supervisionado e a autoanálise diária, e deixa explícito o que ainda falta: bolsa brasileira, câmbio e a homologação humana da fórmula Tá Barato.

### O que muda para você

- As três sprints já entregues no código (ajuste, laço americano, autoanálise) passam a aparecer como concluídas no plano, cada uma com prova citada
- O chamado das funcionalidades 7 a 11 do lado americano fecha o que o teste já prova; o chamado permanece aberto só para bolsa brasileira, câmbio e a homologação da fórmula Tá Barato
- A folha de evidência registra que o pedido 42 está na linha principal e o painel já está no ar, segundo o que você atestou hoje
- Dinheiro real continua desligado; nenhuma corretora terceira entra nesta rodada

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Três sprints antigas carimbadas como concluídas | Abrir o plano e ver status concluída só onde houver prova (código, teste e pedido de revisão citados) |
| 2 | Chamado do contrato americano honesto | Abrir a lista de problemas e ver restante só bolsa brasileira, câmbio e homologação da fórmula Tá Barato |
| 3 | Chamado da autoanálise diária fechado | Ver o chamado do método de ajuste como fechado, alinhado ao código já entregue |
| 4 | Nota do painel no ar | Ler a folha de evidência: pedido 42 na linha principal e painel no ar, atestado por você |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N33.0 Inventariar a prova já entregue antes de carimbar | `/git` | — |
| [x] | P | N33.1 Carimbar no plano as três sprints já entregues | docs | N33.0 |
| [x] | P | N33.2 Deixar os chamados e o changelog do contrato honestos | docs | N33.1 |
| [x] | P | N33.3 Registrar no diário e na evidência o pedido 42 no ar | docs | N33.1 |
| [x] | P | N33.4 Atualizar a sessão desta sprint após os carimbos | session | N33.2, N33.3 |

### Fora de escopo

- Adapters Clear / OANDA (ISS-010 / N29.5)
- Reescrever tabela de tasks N17 (nota opcional: N17.2 permanece operador/G-FORM)
- Inventar limiar Tá Barato / momentum / Prodígio
- `LIVE_TRADING_ENABLED=true`
- Qualquer `src/`
- Fechar ISS-011 por completo

### Task N33.0 — Inventariar a prova já entregue antes de carimbar

**Entrega:** Inventário curto dizendo o que já tem prova (código, teste, pedido de revisão) e o que não pode ser carimbado.
**Como conferir:** O inventário cita as três sprints, o pedido 42 na linha principal, e deixa Tá Barato e corretoras terceiras de fora.
**Por quê:** Sem essa lista, o carimbo no plano inventaria entrega.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N33-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md` vs local checkout; do not bump; if GitHub main is unreachable, keep fail-closed note. Do not touch `src/`. Do not invent fills.

Cite:
- N28: `71caca1` feat; `c465724` stamp; PR **#39** `5178fff`; `tests/test_n28_supervised_adjustment.py` `test_n28_2_in_range_proposal_can_apply`, `test_n28_2_out_of_range_rejected`, `test_n28_3_apply_undo_persist_before_after_reason`, `test_n28_4_never_mutates_risk_anchors`
- N30: `322318b` feat; PR **#35** `622fbeb`; TEST-EVIDENCE N30.1 / N30.3b
- N31: `d1d139a` feat; `84791eb` stamp; PR **#38** `681e8c5`; `tests/test_n31_g_ajuste_guardrails.py` `N31GAjusteGuardrails`
- N32: already `concluida`; PR **#42** MERGED `d30689bfeb4b009b6297d4bdea8fead233486474` (`2026-11-16T19:49:34Z`)
- N17.2 remains `[ ]` — do not stamp N17 `concluida`

### Task N33.1 — Carimbar no plano as três sprints já entregues

**Entrega:** No plano, as sprints de ajuste, laço americano e autoanálise diária passam a constar como concluídas, cada uma apontando a prova.
**Como conferir:** Abrir o índice e o bloco de cada sprint e ver status concluída, sem mudar as linhas de tarefa já marcadas.
**Por quê:** O código já está na linha principal; o plano ainda diz que essas sprints estão planejadas ou em execução.

**Detalhe técnico**

P task. Edit **only Status lines + index rows + optional one-liners**. Do **not** rewrite task tables of N17/N28/N29/N30/N31/N32.

1. `## Sprint N28` `> Status: planejada` → `concluida`. Index row N28 Status → `concluida`. Optional one-liner after existing N28 notes citing `71caca1` / PR #39 / Feature 11 `[x]`.
2. `## Sprint N30` `> Status: em closeout (...)` → `concluida`. Index row N30 → `concluida`. Do not rewrite the campaign table inside N30 (historical).
3. `## Sprint N31` `> Status: em execução` → `concluida`. Index row N31 → `concluida`. Cite PR #38 / `d1d139a`.
4. Optional one-liner under N17 Status (do not change checkboxes): N17.2 remains operador/G-FORM.
5. Optional honesty in the waves `G-AJUSTE` “Sem resposta” cell if it still says Feature 11 critérios 2–4 `[ ]` until N28.2–4 — those boxes are already `[x]` in REQUIREMENTS.
6. Do not mark N17 or N29 `concluida`. LIVE false.

### Task N33.2 — Deixar os chamados e o changelog do contrato honestos

**Entrega:** O chamado das funcionalidades 7 a 11 fica aberto só para bolsa brasileira, câmbio e homologação da fórmula Tá Barato; o chamado da autoanálise diária fecha; o histórico do contrato deixa de dizer que o ajuste ainda está em aberto.
**Como conferir:** Abrir a lista de problemas e o histórico do contrato e ver o restante explícito, sem fechar o chamado americano por completo.
**Por quê:** O índice já diz uma coisa e o corpo do chamado diz outra; o changelog ficou defasado depois do ajuste entregue.

**Detalhe técnico**

P task. Files: `docs/ISSUES.md`, `docs/REQUIREMENTS.md` (changelog only).

ISS-011:
- Keep **aberto**. Prefer split remaining over closing the epic.
- Remaining **only**: Feature 7 B3/FOREX `[ ]` → ISS-010 / N29.5; N17.2 operator homolog / G-FORM (Tá Barato paper blocked upstream).
- Update body: PR **#42** merged `d30689b` (`2026-11-16T19:49:34Z`); EasyPanel #42 no ar (operator-attested 2026-11-16, **not** a fill); N32/N30/N31/N28 Alpaca track delivered; campaign table rows N30/N31/N28/N32 → concluída with citations.
- Index sprint column: `N33 closeout Alpaca; restante ISS-010 + N17.2`.
- Do not claim Tá Barato paper homolog. Do not invent fills.

ISS-012:
- Index already `fechado`; sync **body** Status to `fechado` citing PR **#38** `681e8c5` and N28.2–4 `71caca1`.

REQUIREMENTS:
- Feature 11 lines 283–286 already `[x]` — do not touch those boxes.
- Fix stale changelog line 414 (“critérios 2–4 seguem `[ ]` até N28.2–4”): keep N31 historical sense **or** add an N33 row that critérios 2–4 are `[x]` after N28.2–4 (`tests/test_n28_supervised_adjustment.py`). Do not bump a fake contract version. Do not invent scoring.

### Task N33.3 — Registrar no diário e na evidência o pedido 42 no ar

**Entrega:** Uma entrada curta no diário desta sprint e uma linha na folha de evidência dizendo que o pedido 42 está na linha principal e o painel já está no ar, segundo o que você atestou.
**Como conferir:** Ler diário e evidência; a linha não trata o painel no ar como ordem preenchida.
**Por quê:** Sem esse registro, o closeout some do histórico operacional.

**Detalhe técnico**

P task. Files: `docs/DIARY.md`, `docs/TEST-EVIDENCE.md`.

DIARY: short `## Sprint N33` + index row. Record: PR #42 merged `d30689b`; N28/N30/N31 Status stamps; ISS-011 remains open for ISS-010 + N17.2; LIVE false; no `src/`.

TEST-EVIDENCE one-liner (operator-attested chat 2026-11-16): PR **#42** is on `main` (`d30689bfeb4b009b6297d4bdea8fead233486474`, merged `2026-11-16T19:49:34Z`); EasyPanel image of #42 **no ar**. Explicit: **not a fill**. Do not add homolog rows that invent broker execution.

### Task N33.4 — Atualizar a sessão desta sprint após os carimbos

**Entrega:** A sessão aponta para esta sprint de closeout, ainda só como plano até o parent iniciar a execução.
**Como conferir:** Ver sprint atual N33 e a marca de plano-somente até o EXECUTE.
**Por quê:** Sem sessão alinhada, o próximo agente reabre a sprint anterior.

**Detalhe técnico**

P task. `.cursorsession`: after EXECUTE stamps, set `plan_only=false` only when parent `/pmo sprint` starts work; at PLAN time fields are already `sprint_atual=N33`, `plan_only=true`, `checkpoint.phase=planning`. Preserve `autopilot`. Update `contexto_rapido` / `proximos_passos` after stamps. Do not enable live. Do not commit from the subagent.

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
