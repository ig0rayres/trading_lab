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
| N17 | N | MVP-OP-1.1 — Tá Barato upstream + painel família | substituida (N31) | 5 | vendor, strategy-catalog | Multi-estratégia | *(abaixo)* |
| N18 | N | Command Panel always-on (`v4-ops`) + runbook ops | em execucao | 4 | observability, docs | Painel 8765 sem nohup | *(abaixo)* |
| N19 | N | Laço demo: gatilho no painel e ciclo da ordem no ledger | em execucao | 4 | observability, paper-gateway | Operar B3, cripto e forex | *(abaixo)* |
| N20 | N | Contrato v0.3 + N19.1–N19.2 publicados; fill P-001b; SHA imagem; 0 rebuild | em execucao | 5 | docs, ledger, observability | Onda 0 — resgate | *(abaixo)* |
| N21 | N | Ordem até fill/cancel/expira; P&L só de fill; restart sem duplicar | planejada | 3 | paper-gateway, ledger | Onda 1 — ciclo da ordem | *(abaixo)* |
| N22 | N | Risco lê `control_flags`; capital único R$ 5.000; sessão B3 + feriado | concluida | 3 | risk-gate-b | Onda 2 — âncoras honestas | *(abaixo)* |
| N23 | N | Trabalhador da fila dentro do `v4-ops`; dois apps EasyPanel | concluida | 3 | observability, paper-gateway | Onda 2 — worker (ADR-009) | *(abaixo)* |
| N24 | N | Login + Central de controle; dia a dia sem Exec | concluida | 4 | v4_web_dashboard | Onda 3 — Feature 8 | *(abaixo)* |
| N25 | N | Tela de sinais com destino, gate e âncora; ranking Prodígio | concluida | 3 | v4_web_dashboard | Onda 3 — Feature 9 | *(abaixo)* |
| N26 | N | Performance só de fill confirmado; bruto rotulado | concluida | 3 | v4_web_dashboard, ledger | Onda 3 — Feature 10 | *(abaixo)* |
| N27 | N | Laço autônomo só no mercado com conta demo nomeada (G-MKT) | planejada* | 6 | paper-gateway, risk-gate-b | Onda 4 — Feature 7 | *(abaixo)* |
| N29 | N | Adapters Clear (B3) + OANDA Practice (forex); Alpaca cripto (ISS-010) | planejada* | 6 | paper-gateway | Onda 4b — G-MKT adapters | *(abaixo)* |
| N28 | N | Ajuste supervisionado reversível, sem tocar âncora (G-AJUSTE) | substituida (N34) | 4 | strategy-catalog | Onda 6 — Feature 11 | *(abaixo)* |
| N30 | N | Snapshot de risco fresco, cripto no mesmo laço, cancelamento sem fill, parada por perda | planejada | 5 | paper-gateway, observability | CONTRACT-CLOSEOUT onda 1 | *(abaixo)* |
| N31 | N | Produtores internos momentum e Tá Barato via scanner upstream | planejada | 5 | vendor, strategy-catalog | CONTRACT-CLOSEOUT onda 2 | *(abaixo)* |
| N32 | N | Produtores Prodígio e News First + sombra ORB visível | planejada | 4 | prodigy, news-first | CONTRACT-CLOSEOUT onda 3 | *(abaixo)* |
| N33 | N | Interruptor demo na Central e conferência Features 7–10 | planejada | 4 | v4_web_dashboard, docs | CONTRACT-CLOSEOUT onda 4 | *(abaixo)* |
| N34 | N | Ajuste supervisionado reversível (Feature 11) | planejada | 5 | strategy-catalog, v4_web_dashboard | CONTRACT-CLOSEOUT onda 5 | *(abaixo)* |

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
| N17 | senior+qa | Tá Barato upstream + extensão painel (substituída por N31) |
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
| N28 | senior+qa | Ajuste automático de parâmetro (substituída por N34) |
| N30 | comprehensive | Laço demo fail-closed (snapshot, cripto, cancel, perda) |
| N31 | senior+qa | Produtores internos via scanner upstream |
| N32 | senior+qa | Prodígio, News First, sombra visível |
| N33 | senior+qa | Central demo + evidência Features 7–10 |
| N34 | senior+qa | Ajuste supervisionado (Feature 11) |

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
> Status: substituida (N31) — 2026-11-15 CONTRACT-CLOSEOUT  
> titulo_humano: Tá Barato com regras upstream homologadas em shadow/paper  
> Gate: fórmulas/limites de `ta_barato` (e momentum se escopo) recuperadas em vendor — **senão** sprint permanece blocked e documenta gap; homolog pytest; LIVE false  
> review: senior+qa  
> Release tag: `MVP-OP-1.1`  
> **Não executar.** O escopo aberto (scanner upstream `find_setups`, produtores internos, fases research até o operador promover) passou para **N31**. Tasks abaixo ficam históricas.

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
Onda 4b N29                adapters Clear simulado + OANDA Practice (+ Alpaca cripto)     MVP-OP-1.4 (0–1)
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
| [ ] | M | N27.2 Adaptador da conta demo nomeada pelo operador (B3 e forex nunca pela Alpaca) | `/dev` | G-MKT, N29 — **B3/FOREX excluded — third-party not homologated (operator 2026-11-15)**; cripto Alpaca já coberto em N27.1/N27.3 |
| [x] | P | N27.3 Teste: mercado sem conta continua visível e barrado com motivo | `/qa testes` | N27.1, N19.4 |
| [ ] | P | N27.4 Operador: sinal válido vira ordem demo sem ação manual | operador | N27.2, N23.1, N24.2 — **B3/FOREX excluded — third-party not homologated (operator 2026-11-15)**; US/cripto absorvido por N30/N33 |
| [ ] | P | N27.5 Teste: chave live no ambiente não muda o destino paper | `/qa testes` | N27.2 — **absorvido por N30.5** (há teste parcial `test_n27_5_live_looking_key_keeps_paper_alpaca_host`) |
| [ ] | P | N27.6 Teste: restart com laço ligado não duplica | `/qa testes` | N27.4 — **absorvido por N30.5** (N21.3 existe; falta laço `demo_operation_on`) |

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
| [ ] | P | N29.5 Operador: abrir/credenciar Clear + OANDA; ids só no EasyPanel | operador | N29.3 — **excluded — third-party not homologated (operator 2026-11-15)** |
| [ ] | P | N29.6 Desbloquear N27.2 no ROADMAP após adapters verdes + nota de release | docs | N29.4, N29.5 — **excluded — third-party not homologated (operator 2026-11-15)** |

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
> Status: substituida (N34) — 2026-11-15 CONTRACT-CLOSEOUT  
> titulo_humano: Ajuste registrado e reversível, sem mexer no risco  
> Gate: G-AJUSTE e fill real; só parâmetro existente na faixa original; histórico com desfazer; âncoras intocadas; LIVE false  
> review: senior+qa  
> Depende de: N20.3, N21  
> **Não executar.** Feature 11 (Should) passou para **N34**: rótulo de sugestão, histórico com desfazer, âncoras intocadas, e ajuste automático conservador **desligado** até o operador ligar. G-AJUSTE permanece aberto para revisão do operador.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | P | N28.1 Sugestão continua rotulada como sugestão | `/dev` | — |
| [ ] | M | N28.2 Ajustar só parâmetro existente, dentro da faixa original | `/dev` | G-AJUSTE |
| [ ] | M | N28.3 Registrar antes, depois e motivo, com desfazer na Central | `/dev` | N28.2 |
| [ ] | P | N28.4 Teste: ajuste nunca altera âncora de risco | `/qa testes` | N28.2 |

---

## Programa CONTRACT-CLOSEOUT

> Planejado em 2026-11-15 via `/pmo plan` (Rock PLAN, `plan_only`).  
> Auditoria: `docs/.briefs/CONTRACT-CLOSEOUT.intake.md` (lista de gaps soberana). Contrato: `docs/REQUIREMENTS.md` v0.4.  
> Base: `origin/main` `376434e`. Frente: `front/contract-closeout`. Upstream pin: `3d0f4ef` (= main do `day-trader-skill` em 2026-11-15).  
> Invariantes: `LIVE_TRADING_ENABLED=false`; só paper/demo; um único caminho de ordem (Gate A → fila → Gate B → `paper_gateway_queue` → `signal_paper_runner`); sem limiar inventado; ORB e mean reversion só em sombra; Collective2 copy permanece fechado; B3/Clear e forex/OANDA **barrados** (terceiro não homologado).

```text
Onda 1  N30   laço operacional: snapshot ≤120s, cripto, cancel sem fill, parada por perda, N27.5/N27.6
Onda 2  N31   produtores internos + momentum + ta_barato via find_setups (substitui N17)
Onda 3  N32   Prodígio (C2 leitura) + news_first com confirmação de preço + sombra visível
Onda 4  N33   interruptor demo na Central + conferência Features 7–10 (TEST-EVIDENCE)
Onda 5  N34   Feature 11 infra supervisionada (substitui N28)
```

Caminho crítico Must-have: **N30 → N31 → N32 → N33**. Feature 11 (Should) é N34 e não trava 7–10.

### Exclusões aceitas pelo operador (2026-11-15)

| Item | Tratamento |
|------|------------|
| B3 via Clear Smart Trader | Continua visível e **barrado** com motivo. N27.2/N27.4 (parte B3), N29.5, N29.6 fora. |
| Forex via OANDA Practice | Idem. Sem credencial, sem adapter no laço. |
| ORB / mean reversion em paper | Proibido. Sombra deve continuar e aparecer no painel (N32.3). |
| LIVE | Fora. |
| Collective2 paper-copy | `approved_for_paper_copy` permanece falso. Prodígio usa o feed C2 só como pesquisa → sinal interno da família `prodigy_15d`. |

### Pendências do operador (não bloqueiam o plano)

1. Confirmar o mapeamento momentum ↔ `breakout_20d|bull_flag|reclaim_ma20` e ta_barato ↔ `oversold|oversold_bounce`, depois promover fases na Central.
2. Método G-AJUSTE (o que conta como erro, frequência, desfazer) — N34 entrega infra conservadora **desligada**.
3. Rebuild EasyPanel depois do merge (agente não publica).
4. Chave C2 no ambiente para o feed ao vivo do Prodígio (se ainda não estiver).
5. N20.2 SHA da imagem dos dois serviços.

---

## Sprint N30 — Laço demo fail-closed (snapshot, cripto, cancel, perda)

> Categoria: N  
> Status: planejada  
> titulo_humano: O laço demo para sozinho se o risco estiver velho, estourado ou sem fill  
> resumo_humano: O serviço operacional passa a renovar sozinho a fotografia de risco com dados reais da corretora paper e do ledger. Sem fotografia fresca ou P&L conferido, nenhuma ordem nova sai. Cripto usa o mesmo caminho da ação americana. Ordem sem fill no prazo é cancelada e não volta sozinha. Perda do dia ou da semana para até o período seguinte.  
> Gate: fotografia de risco com idade ≤120s no worker; P&L não verificado ⇒ recusa; cripto assinado aceito sem afrouxar autenticidade; TTL cancela e `may_auto_resubmit` falso; `DAILY_LOSS_HALT`/`WEEKLY_LOSS_HALT` até o próximo período; chave live não muda o host paper; restart com laço ligado não duplica; LIVE false  
> review: comprehensive  
> Depende de: N23, N27.1, N27.3  
> Gerado via: `/pmo plan` — CONTRACT-CLOSEOUT 2026-11-15  
> Brief: `docs/.briefs/N30.brief.md`

### Em uma frase

O laço demo só envia ordem paper quando a fotografia de risco está fresca e verdadeira; cripto entra no mesmo caminho, e ordem sem fill ou perda no teto param sozinhas.

### O que muda para você

- Você não precisa renovar a fotografia de risco no Exec: o serviço operacional faz isso sozinho
- Sem P&L conferido, o laço recusa ordem nova em vez de inventar “verificado”
- Cripto paper (Alpaca) usa o mesmo caminho da ação americana, ainda com assinatura e prazo
- Ordem que não preenche no prazo some da corretora paper e não é reenviada
- Estouro de perda do dia ou da semana segura até o dia ou a semana seguinte, com motivo visível

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Fotografia de risco renovada sozinha | No painel, ordem nova só passa com fotografia recente; fotografia velha ou P&L não conferido barra com motivo |
| 2 | Sinal cripto no mesmo laço | Um sinal cripto assinado segue o mesmo caminho da ação; sessão 24h; autenticação continua obrigatória |
| 3 | Cancelamento sem fill | Ordem paper aberta além do prazo some na corretora e não volta sozinha |
| 4 | Parada por perda do período | Com perda do dia/semana no teto, ordem nova recusa até o período seguinte |
| 5 | Chave live e restart | Chave com cara de live continua no host paper; reinício com laço ligado não abre ordem duplicada |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | N30.1 Renovar a fotografia de risco no serviço operacional | `/dev` | — |
| [ ] | M | N30.2 Aceitar sinal cripto Alpaca no mesmo caminho autenticado | `/dev` | N30.1 |
| [ ] | M | N30.3 Cancelar ordem paper sem fill no prazo, sem reenvio | `/dev` | N30.1 |
| [ ] | M | N30.4 Parar por perda do dia/semana até o próximo período | `/dev` | N30.1 |
| [ ] | P | N30.5 Provar host paper com chave live e restart sem duplicata | `/qa testes` | N30.2, N30.3 |

### Task N30.1 — Renovar a fotografia de risco no serviço operacional

**Entrega:** O serviço operacional grava sozinho uma fotografia de risco com idade máxima de dois minutos, feita com P&L do ledger e contagens reais da corretora paper.
**Como conferir:** Com a fotografia velha ou P&L não conferido, a ordem paper é recusada com motivo; com fotografia fresca e P&L conferido, o laço deixa de travar só por arquivo ausente.
**Por quê:** Hoje o envio paper exige esse arquivo fresco e nada no serviço operacional o atualiza — o laço autônomo fica parado.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: signal_paper_runner.risk_check exige V4_RISK_SNAPSHOT_FILE com at_utc ≤120s, alpaca_positions_count e alpaca_open_orders_count iguais ao GET Alpaca; ledger_loss_anchor.portfolio_risk_snapshot não traz esses campos; v4_broker_snapshot nunca marca complete/verified; v4_ops_main.sh só supervisiona dashboard + tv-worker; risk_check ainda recusa com DAILY_RISK_NOT_CONFIRMED se PAPER_DAILY_RISK_CONFIRMED≠true (contradiz o comentário de não inferir P&L de boolean de env).
desejado: loop no v4-ops (intervalo ≤60s) grava V4_RISK_SNAPSHOT_FILE mesclando portfolio_risk_snapshot + GET Alpaca (contagens e posições); at_utc UTC; sem verified=true hardcoded — complete/daily_pnl_verified/weekly_pnl_verified/broker_reconciled só quando o ledger realmente conferiu; risk_check deixa de usar o boolean de env e passa a ler os flags da fotografia; B3/FOREX fora da fotografia (mercados excluídos).
guardrail: LIVE false; host só paper-api.alpaca.markets; GET allowlist existente; não inventar P&L; não POST de ordem neste módulo.
testes: fotografia ausente/stale/mismatch ⇒ V4_PORTFOLIO_SNAPSHOT_*; P&L não verificado ⇒ LOSS_DATA_NOT_VERIFIED; idade ≤120s + counts iguais ⇒ não há STALE; loop v4-ops presente no script (espelhar test_v4_ops_layout).
files:
  - src/risk_snapshot_refresh.py
  - scripts/v4_ops_main.sh
  - src/signal_paper_runner.py
  - tests/test_risk_snapshot_refresh.py
  - tests/test_signal_paper_runner.py
reuse_targets:
  - component: src/ledger_loss_anchor.py portfolio_risk_snapshot
    reuse_as: call
    convergence_check: rg "portfolio_risk_snapshot" src/risk_snapshot_refresh.py
  - component: src/v4_broker_snapshot.py collect/get_json
    reuse_as: call
    convergence_check: rg "alpaca_positions_count|alpaca_open_orders_count" src/risk_snapshot_refresh.py
guardrail_contract:
  - class: secrets
    check: rg -n "ALPACA_|C2_|SIGNAL_COPY" src/risk_snapshot_refresh.py scripts/v4_ops_main.sh | rg -v "environ|env.get|os.environ"
    pass_condition: no hardcoded credentials
  - class: caller-level
    convergence_check: pytest -q tests/test_risk_snapshot_refresh.py tests/test_v4_ops_layout.py
depends_on: []
```

### Task N30.2 — Aceitar sinal cripto Alpaca no mesmo caminho autenticado

**Entrega:** Sinal cripto da Alpaca paper (símbolo no formato da corretora, sessão contínua) passa no mesmo caminho autenticado da ação americana.
**Como conferir:** Sinal cripto sem assinatura, atrasado ou com schema errado continua recusado; sinal válido não cai mais na recusa “só ação americana”.
**Por quê:** A conta paper já cobre cripto, mas a validação do sinal só aceita ação americana e símbolos de até cinco letras — `BTCUSD` nem entra.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: signal_copy.validate exige asset_class==us_equity e symbol [A-Z]{1,5} (BTCUSD tem 6; BTC/USD tem barra); risk_check exige qty int; make_order usa time_in_force day; tradingview_webhook espelha us_equity; gate_b_session já trata CRYPTO como 24/7; paper_gateway_queue já roteia CRYPTO pela Alpaca paper quando DEMO_ACCOUNT_PATH_CRYPTO está setado.
desejado: asset_class crypto permitido com símbolo Alpaca (BTCUSD ou BTC/USD) sem afrouxar HMAC, ttl 1–60s, schema, lado buy, frescor; qty fracionária só CRYPTO; TIF gtc só CRYPTO; US equity permanece [A-Z]{1,5} + tif day + qty int. Não aceitar B3/FOREX neste caminho.
guardrail: não relaxar AUTH_FAILED / ttl / schema; LIVE false; Gate A checks intactos.
testes: crypto válido assinado aceito; crypto sem assinatura AUTH_FAILED; AAPL continua us_equity; símbolo de 6 letras em us_equity continua INVALID_SYMBOL; sessão crypto fora do NYSE não dá OUTSIDE_SESSION.
files:
  - src/signal_copy.py
  - src/signal_paper_runner.py
  - src/tradingview_webhook.py
  - tests/test_signal_copy.py
  - tests/test_signal_paper_runner.py
depends_on: [N30.1]
```

### Task N30.3 — Cancelar ordem paper sem fill no prazo, sem reenvio

**Entrega:** Ordem paper que não preenche no prazo é cancelada na corretora, registrada, e o mesmo sinal não é reenviado sozinho.
**Como conferir:** No teste, a corretora paper recebe o cancelamento, o ledger mostra cancelado por prazo, e uma segunda passagem do worker não abre ordem nova.
**Por quê:** O contrato Feature 7 exige isso; a função de acompanhamento já sabe cancelar se receber o gancho, mas o laço nunca passa o gancho nem guarda o prazo na ordem.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: paper_fill_cycle.track_once cancela só se cancel_fn e broker_id existirem; process_after_gate_b chama track_once no resume sem cancel_fn; _load_paper_order não lê ttl_seconds/submitted_at_utc; paper_audit é GET-only (sem cancel); may_auto_resubmit já retorna False; v4-ops não tem loop de acompanhamento.
desejado: cancel DELETE/POST só no host paper, injetado como cancel_fn; persistir ttl e submitted_at no paper_orders (coluna existente ou campo já no JSON — sem inventar prazo novo além do ttl do sinal); loop curto no v4-ops chama track_once nas abertas; sem auto-resend.
guardrail: LIVE false; cancel nunca no host live; may_auto_resubmit permanece False; não segundo cliente broker.
testes: TTL expirado ⇒ cancel_fn chamado + TRACKED_CANCELLED_TTL + orders_sent 0; may_auto_resubmit False; resume após restart não re-POST.
files:
  - src/paper_fill_cycle.py
  - src/paper_gateway_queue.py
  - src/signal_paper_runner.py
  - scripts/v4_ops_main.sh
  - tests/test_paper_fill_cycle.py
depends_on: [N30.1]
```

### Task N30.4 — Parar por perda do dia/semana até o próximo período

**Entrega:** Quando a perda do dia ou da semana atinge o teto, nenhuma ordem nova sai até o próximo dia ou semana UTC, e o motivo aparece para o operador.
**Como conferir:** Depois do teto, uma ordem nova no mesmo período é recusada com o motivo de perda; no período seguinte a recusa dessa parada some (outras âncoras continuam valendo).
**Por quê:** O avaliador de carteira já calcula a perda, mas a parada não fica presa ao período e o painel não mapeia o código de recusa à âncora.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: portfolio_risk_v4 emite DAILY_LOSS_HALT/WEEKLY_LOSS_HALT por avaliação pontual (P&L pode “destravar” no mesmo dia); gate_b_loss_reject só barra fill sem conversão BRL; panel_ops_data.ANCHOR_FIELD_BY_REJECT não inclui DAILY_LOSS_HALT/WEEKLY_LOSS_HALT.
desejado: ao atingir o teto, persistir halt até o início do próximo dia/semana UTC (não coluna de âncora editável pelo operador); Gate B e risk_check honram o halt; mapear os códigos no painel para max_daily_loss_cents / max_weekly_loss_cents.
guardrail: não afrouxar âncoras; não inventar FX; LIVE false.
testes: teto diário ⇒ halt no mesmo dia; avanço de relógio para o dia seguinte ⇒ halt diário some; sem P&L verificado continua fail-closed (não halt falso).
files:
  - src/ledger_loss_anchor.py
  - src/portfolio_risk_v4.py
  - src/gate_b_risk.py
  - src/panel_ops_data.py
  - tests/test_ledger_loss_anchor.py
depends_on: [N30.1]
```

### Task N30.5 — Provar host paper com chave live e restart sem duplicata

**Entrega:** Testes mostram que chave com cara de live não muda o destino paper e que reinício com o laço ligado não duplica ordem.
**Como conferir:** A suíte falha se algum POST for para o host live, ou se o segundo ciclo do worker enviar de novo a mesma ordem.
**Por quê:** Feature 7 ainda está em aberto nesses dois critérios; já existe teste parcial da chave e teste de restart da N21 sem o laço demo ligado.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: test_n27_5_live_looking_key_keeps_paper_alpaca_host existe; paper_audit.validate_env já exige ALPACA_BASE_URL==paper; test_paper_restart_no_duplicate cobre N21.3 sem demo_operation_on / worker loop.
desejado: caso BASE_URL live ⇒ fail-closed zero POST live; restart com demo_operation_on true + auto flags não chama broker_run de novo se broker_order_id já existe.
guardrail: LIVE false; não enfraquecer validate_env.
testes: estender os dois arquivos citados; nodeids estáveis para N33/TEST-EVIDENCE.
files:
  - tests/test_paper_gateway_queue.py
  - tests/test_paper_restart_no_duplicate.py
depends_on: [N30.2, N30.3]
```

---

## Sprint N31 — Produtores internos momentum e Tá Barato

> Categoria: N  
> Status: planejada  
> titulo_humano: Momentum e Tá Barato passam a emitir sinal interno pelas regras originais  
> resumo_humano: As famílias internas passam a gerar sinal assinado no mesmo caminho do copy, usando só os setups do scanner original. Elas nascem em pesquisa: virar paper é só você ligar a família na Central. Nenhum número novo de estratégia é inventado aqui.  
> Gate: original.py exige find_setups (+ rsi); produtores emitem sinal com strategy_key e provider dedicado, assinados; fase default research ⇒ Gate B STRATEGY_PHASE_BLOCKED até PATCH do operador; zero POST broker no produtor; LIVE false; N17 marcada substituída  
> review: senior+qa  
> Depende de: N30, N7  
> Gerado via: `/pmo plan` — CONTRACT-CLOSEOUT 2026-11-15  
> Brief: `docs/.briefs/N31.brief.md`

### Em uma frase

Momentum e Tá Barato passam a gerar sinais internos com as regras do scanner original, ainda em pesquisa até você promover no painel.

### O que muda para você

- As duas famílias deixam de ser só nome no catálogo: elas produzem sinal de verdade
- A promoção para paper continua só na Central — o código não sobe a fase sozinho
- Você ainda precisa confirmar se os setups originais são mesmo essas duas famílias

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Scanner original exposto | A carga do vendor recusa se faltar a função de setups do scanner |
| 2 | Sinal interno assinado | Cada família grava um sinal com origem própria no mesmo caminho do copy |
| 3 | Momentum pelos setups de força | Setup de rompimento/bandeira/média 20 vira sinal da família momentum |
| 4 | Tá Barato pelos setups de oversold | Setup oversold / oversold bounce vira sinal da família ta_barato |
| 5 | Pesquisa não envia paper | Com a fase ainda em pesquisa, o gate de risco barra paper com motivo de fase |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | P | N31.1 Expor find_setups (e rsi) no carregador original | `/dev` | — |
| [ ] | M | N31.2 Criar o emissor de sinal interno assinado | `/dev` | N31.1 |
| [ ] | M | N31.3 Emitir momentum só com setups de força do scanner | `/dev` | N31.2 |
| [ ] | M | N31.4 Emitir Tá Barato só com setups oversold do scanner | `/dev` | N31.3 |
| [ ] | P | N31.5 Ligar os produtores no serviço operacional em pesquisa | `/dev` | N31.3, N31.4 |

### Task N31.1 — Expor find_setups no carregador original

**Entrega:** O carregador do vendor passa a exigir as funções de setup do scanner original, sem copiar a fórmula.
**Como conferir:** Se o scanner original perder `find_setups`, a carga falha; o teste de vendor confirma o contrato.
**Por quê:** Sem esse contrato, o próximo passo copiaria a lógica em vez de reutilizar.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: original.SCRIPTS scanner required=('orb_hit',); find_setups e rsi existem em trader-scanner/scan.py e já são chamados por multistrategy via orig.scanner.find_setups, mas não estão no contrato de API.
desejado: required += find_setups e rsi; sem copiar o corpo de find_setups.
guardrail: não editar vendor/; LIVE false.
testes: load_original falha se find_setups ausente (monkeypatch); vendor_verify ou teste novo lista o atributo.
files:
  - src/original.py
  - tests/test_original_scanner_api.py
depends_on: []
```

### Task N31.2 — Criar o emissor de sinal interno assinado

**Entrega:** Um único emissor grava sinal interno assinado na mesma fila do copy, com origem própria e família preenchida.
**Como conferir:** Sinal sem família, sem assinatura ou com segredo curto não entra na fila; sinal válido aparece como evento autenticado, sem ordem na corretora neste passo.
**Por quê:** Feature 4 exige um só caminho de ordem; sem isso cada família inventaria um segundo cliente.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: só signal_copy/TradingView escrevem a fila TV_QUEUE_DIR; tradingview_worker chama signal_copy.validate e process_after_gate_b; strategy_key obrigatório no Gate B.
desejado: módulo que monta payload ALLOWED, preenche strategy_key + provider dedicado (lab_momentum, lab_ta_barato, lab_prodigy, lab_news_first), assina com SIGNAL_COPY_SECRET (env, ≥24), persiste Gate A (maybe_persist) e escreve o mesmo pending dir; sem importar cliente broker.
guardrail: LIVE false; HMAC obrigatório; sem segundo broker; fases não sobem sozinhas.
testes: falta strategy_key ⇒ não enfileira; assinatura ruim ⇒ AUTH_FAILED no worker; provider dedicado ≠ tradingview.
files:
  - src/internal_signal_producer.py
  - src/tradingview_worker.py
  - src/gate_a_signal.py
  - tests/test_internal_signal_producer.py
depends_on: [N31.1]
```

### Task N31.3 — Emitir momentum só com setups de força do scanner

**Entrega:** A família momentum só emite sinal quando o scanner original marca rompimento de 20 dias, bandeira de alta ou retomada da média 20.
**Como conferir:** Fixture com esses setups gera sinal momentum; fixture só oversold não gera momentum; nenhum limiar numérico novo aparece no código da família.
**Por quê:** O contrato proíbe inventar regra de momentum; o scanner original já tem essas três marcas.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: N17 nunca começou; catálogo tem momentum em research; find_setups tags breakout_20d, bull_flag, reclaim_ma20.
desejado: produtor chama load_original().scanner.find_setups(closes) — mapping MOMENTUM_SETUPS = {breakout_20d, bull_flag, reclaim_ma20} rotulado ASSUMPTION_OPERATOR_REVIEW; stop/target via original.entry/exit/budget, não números inventados; emite via N31.2; fase permanece research.
guardrail: não copiar find_setups; não PATCH de fase; LIVE false.
testes: tags momentum ⇒ um sinal strategy_key=momentum; tag só oversold ⇒ zero momentum; orders_sent 0 no produtor.
files:
  - src/scanner_family_producer.py
  - src/internal_signal_producer.py
  - tests/test_scanner_family_producer.py
depends_on: [N31.2]
```

### Task N31.4 — Emitir Tá Barato só com setups oversold do scanner

**Entrega:** A família Tá Barato só emite sinal quando o scanner original marca oversold ou oversold bounce — não “caiu, compra”.
**Como conferir:** Fixture oversold gera sinal ta_barato; fixture só de rompimento não gera; o contrato de “não inventar percentil” continua visível no teste.
**Por quê:** A fórmula recuperada no vendor é RSI Wilder 14 < 30 e o bounce; qualquer outro gatilho seria invenção.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: ta_barato no catálogo em research, sem produtor.
desejado: no mesmo scanner_family_producer, TA_BARATO_SETUPS = {oversold, oversold_bounce} rotulado ASSUMPTION_OPERATOR_REVIEW; reusa find_setups; não implementar RSI local.
guardrail: não “caiu, compra”; não limiar novo; LIVE false.
testes: oversold ⇒ strategy_key=ta_barato; breakout_20d sozinho ⇒ zero ta_barato.
files:
  - src/scanner_family_producer.py
  - tests/test_scanner_family_producer.py
depends_on: [N31.3]
```

### Task N31.5 — Ligar os produtores no serviço operacional em pesquisa

**Entrega:** O serviço operacional dispara os produtores internos em intervalo, ainda em pesquisa, sem envio paper até você promover.
**Como conferir:** Com fase research, o worker da fila recusa paper com motivo de fase; o scheduler de pesquisa continua sem importar corretora.
**Por quê:** O contrato pede produtores ponta a ponta para a promoção na Central ser o único passo que falta.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: v4_ops_main.sh = dashboard + tv-worker + exec v4-scheduler.
desejado: supervisor opcional INTERNAL_PRODUCER_AUTOSTART (default true) chama o produtor de famílias em intervalo; v4_scheduler permanece sem broker.
guardrail: LIVE false; research cycle orders_sent 0; STRATEGY_PHASE_BLOCKED até PATCH.
testes: layout script contém o produtor; fase research ⇒ paper_allowed falso.
files:
  - scripts/v4_ops_main.sh
  - tests/test_v4_ops_layout.py
depends_on: [N31.3, N31.4]
```

---

## Sprint N32 — Prodígio, News First e sombra visível

> Categoria: N  
> Status: planejada  
> titulo_humano: Prodígio e notícia viram sinal interno; sombra de ORB continua visível  
> resumo_humano: O ranking Prodígio que já existe passa a emitir sinal interno a partir do feed somente leitura da Collective2, com teto de risco menor e sem promoção automática. Notícia só vira sinal se a evidência passar e a entrada original confirmar o preço; senão permanece sem negócio. ORB e retorno à média continuam só em sombra, agora visíveis no painel.  
> Gate: prodigy_rank.calculate intacto; C2 key só env; teto Prodígio R$20; news_first só com verifier pass AND entry.evaluate status triggered; ORB/mean_reversion nunca paper_allowed; sombra visível; LIVE false  
> review: senior+qa  
> Depende de: N31  
> Gerado via: `/pmo plan` — CONTRACT-CLOSEOUT 2026-11-15  
> Brief: `docs/.briefs/N32.brief.md`

### Em uma frase

Prodígio e notícia só viram sinal interno com as regras já existentes; ORB permanece sombra visível, nunca paper.

### O que muda para você

- Prodígio deixa de ser só ranking na tela: pode gerar sinal da família prodigy, ainda em pesquisa
- Notícia continua “não é compra pelo tom”; só vira sinal com evidência e confirmação de preço
- Você vê ORB e retorno à média rodando em sombra, sem botão de paper

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Sinal Prodígio a partir do feed C2 | Ranking inalterado; sem chave C2 não há sinal; teto de risco menor na família |
| 2 | News First só com preço confirmado | Sem evidência ou sem gatilho da entrada original, a decisão permanece sem negócio |
| 3 | Sombra visível | Painel mostra ORB/retorno à média em sombra e recusa promoção a paper |
| 4 | Produtores no serviço operacional | Os dois produtores rodam no mesmo serviço, sem segundo caminho de corretora |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | N32.1 Emitir sinal Prodígio a partir do feed C2 e do ranking existente | `/dev` | — |
| [ ] | M | N32.2 Emitir News First só com evidência e confirmação de preço | `/dev` | — |
| [ ] | P | N32.3 Manter ORB e retorno à média visíveis só em sombra | `/dev` | — |
| [ ] | P | N32.4 Ligar Prodígio e News First no serviço operacional | `/dev` | N32.1, N32.2 |

### Task N32.1 — Emitir sinal Prodígio a partir do feed C2 e do ranking existente

**Entrega:** A família Prodígio emite sinal interno usando a pontuação que já existe e o feed somente leitura da Collective2, com teto de risco menor e sem subir de fase sozinha.
**Como conferir:** Sem chave no ambiente, zero sinal e zero ordem; o arquivo de pontuação não muda a fórmula; provedor não aprovado para copy continua fora do copy.
**Por quê:** Feature 4 pede Prodígio 15d com risco inicial menor, sem promoção automática e sem inventar score.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: prodigy_rank.calculate já implementa a heurística 15d; c2_signal_feed é read-only (não sintetiza ticket); approved_for_paper_copy permanece false; portfolio_risk_v4 já tem prodigy_risk_cents e motivo DEFAULT_TRADE_RISK; signal_paper_runner usa PRODIGY_PROVIDERS para teto 20.
desejado: produtor lê snapshot C2 + calculate() as-is; só PRODIGY_CANDIDATE_RESEARCH pode virar sinal interno strategy_key=prodigy_15d provider=lab_prodigy; C2 key só env; sem PATCH de fase; copy C2 continua fechado.
guardrail: não editar a fórmula de calculate; não paper-copy C2; LIVE false; chave ausente ⇒ NO_TRADE / skip, não crash com ordem.
testes: score function unchanged (hash/snapshot do calculate); sem key ⇒ 0 sinais; candidato research ⇒ sinal assinado + fase research bloqueia paper; planned risk > 20 ⇒ DEFAULT_TRADE_RISK.
files:
  - src/prodigy_signal_producer.py
  - src/internal_signal_producer.py
  - src/c2_signal_feed.py
  - tests/test_prodigy_signal_producer.py
depends_on: []
```

### Task N32.2 — Emitir News First só com evidência e confirmação de preço

**Entrega:** Candidato de notícia só vira sinal interno se a evidência passar e a função de entrada original disparar no preço; caso contrário permanece sem negócio.
**Como conferir:** Sem atestados de evidência, zero sinal de paper; com evidência e status triggered da entrada original, nasce um sinal news_first ainda em pesquisa.
**Por quê:** O simulador hoje marca todos como sem negócio; o avaliador de evento nunca passa — e não podemos virar isso para verdadeiro à força.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: news_first_sim sempre decision=NO_TRADE; event_verifier.assess hardcode event_status UNVERIFIED, strategy_eligible False, verified counters 0; original.entry.evaluate já exposto (status triggered).
desejado: função fail-closed passes(event, evidence) verdadeira só se todos verification_requirements estiverem atestados no payload de evidência (não flipar assess); E evaluate(chart, now, setup='level', ...) status=='triggered' (nível = último close completo já no chart, sem limiar inventado); senão permanece NO_TRADE; sinal interno strategy_key=news_first provider=lab_news_first.
guardrail: não inventar tom→lado; não marcar verified=true sem evidência; LIVE false.
testes: sem evidence ⇒ NO_TRADE; evidence completa + evaluate waiting ⇒ NO_TRADE; evidence + triggered ⇒ sinal assinado orders_sent 0.
files:
  - src/news_first_sim.py
  - src/event_verifier.py
  - tests/test_news_first_sim.py
  - tests/test_event_verifier.py
depends_on: []
```

### Task N32.3 — Manter ORB e retorno à média visíveis só em sombra

**Entrega:** ORB e retorno à média continuam rodando em sombra e aparecem no painel, sem caminho paper.
**Como conferir:** No painel as duas famílias mostram fase sombra e recusa de promoção a paper; o diário de sombra recebe linha nova no ciclo de pesquisa.
**Por quê:** O contrato manda sombra viva e visível, nunca paper.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: NEVER_PAPER_KEYS já barra paper; Central (panel_ops_html) não lista famílias; shadow_journal existe mas o ciclo v4_run_once não o destaca no panel_ops.
desejado: Central/sinais mostram orb e mean_reversion como sombra (não selecionáveis para paper); ciclo de pesquisa continua a gravar sombra (reuso shadow_journal / multistrategy, sem novo motor).
guardrail: NEVER_PAPER_KEYS intacto; LIVE false.
testes: PATCH paper_limited em orb ⇒ recusa; página Central contém as duas chaves em sombra.
files:
  - src/panel_ops_html.py
  - src/panel_ops_data.py
  - tests/test_panel_ops.py
depends_on: []
```

### Task N32.4 — Ligar Prodígio e News First no serviço operacional

**Entrega:** Os dois produtores novos rodam no mesmo serviço operacional, no mesmo caminho de fila.
**Como conferir:** O script de layout cita os dois produtores; o scheduler de pesquisa segue sem cliente de corretora.
**Por quê:** Sem o laço, os produtores existem só no pytest.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: v4-ops após N31 tem produtor de scanner.
desejado: mesmo supervisor dispara prodigy + news_first (flags AUTOSTART, default true, skip se C2 key ausente).
guardrail: LIVE false; sem segundo broker.
testes: test_v4_ops_layout contém os nomes dos produtores.
files:
  - scripts/v4_ops_main.sh
  - tests/test_v4_ops_layout.py
depends_on: [N32.1, N32.2]
```

---

## Sprint N33 — Central demo e conferência do contrato 7–10

> Categoria: N  
> Status: planejada  
> titulo_humano: Ligar o demo pelo painel e marcar o contrato só com prova  
> resumo_humano: A Central ganha o interruptor de operação demo que hoje só existe na API (e que você teve de mudar no banco). Cada família aparece para ligar ou desligar. Os critérios das Features 7 a 10 só são marcados no contrato quando houver linha de teste ou evidência sua; o que depender de produção fica em aberto com nota.  
> Gate: toggle demo_operation_on na Central; famílias visíveis com PATCH existente; TEST-EVIDENCE com nodeids; REQUIREMENTS 7–10 [x] só com evidência; critérios de operador permanecem [ ] + 'pending operator evidence'; LIVE false  
> review: senior+qa  
> Depende de: N30, N32, N24  
> Gerado via: `/pmo plan` — CONTRACT-CLOSEOUT 2026-11-15  
> Brief: `docs/.briefs/N33.brief.md`

### Em uma frase

Você liga ou desliga o demo e cada família na Central, e o contrato 7–10 só fecha critério com prova.

### O que muda para você

- O interruptor de operação demo deixa de exigir SQL ou Exec
- Cada estratégia existente aparece na Central para ligar ou desligar (ORB continua sem paper)
- Features 7–10 só recebem visto quando o teste ou a sua evidência existir

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Interruptor demo na Central | Na Central, ligar/desligar operação demo grava histórico e a próxima ordem obedece |
| 2 | Famílias ligáveis na Central | Cada família mostra fase; ORB/retorno à média recusam paper |
| 3 | Caderno de evidência 7–10 | Cada critério tem linha de teste ou nota de evidência pendente sua |
| 4 | Contrato atualizado com honestidade | Só critério com prova vira feito; o resto fica aberto com a nota combinada |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | N33.1 Colocar o interruptor de operação demo na Central | `/dev` | — |
| [ ] | M | N33.2 Mostrar e ligar/desligar cada família na Central | `/dev` | N33.1 |
| [ ] | P | N33.3 Registrar evidência de teste das Features 7–10 | docs | N33.1, N33.2 |
| [ ] | P | N33.4 Marcar Features 7–10 no contrato só com prova | docs | N33.3 |

### Task N33.1 — Colocar o interruptor de operação demo na Central

**Entrega:** A Central mostra e altera o interruptor de operação demo, com o mesmo histórico das outras âncoras.
**Como conferir:** Um clique grava o valor anterior e o novo; com o interruptor desligado a próxima ordem não sai.
**Por quê:** A API já aceita o campo; a tela da Central não tem o botão — em 2026-11-15 foi preciso SQL.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: TRIGGER_PATCH_FIELDS inclui demo_operation_on; test_panel_triggers PATCH funciona; render_central_page só tem kill switch + âncoras de centavos + mercados, sem demo_operation_on.
desejado: toggle na Central (PATCH /api/triggers) com valor anterior em trigger_changes; LIVE sem botão.
guardrail: sessão de operador obrigatória; bearer sozinho 401; LIVE false.
testes: HTML contém o controle; PATCH demo_operation_on True/False roundtrip; demo off ⇒ DEMO_OPERATION_OFF.
files:
  - src/panel_ops_html.py
  - src/v4_web_dashboard.py
  - tests/test_panel_ops.py
  - tests/test_panel_triggers.py
depends_on: []
```

### Task N33.2 — Mostrar e ligar/desligar cada família na Central

**Entrega:** A Central lista cada família existente e permite mudar a fase (ligar/desligar paper) pelo PATCH que já existe.
**Como conferir:** Momentum/Tá Barato/Prodígio/News First aparecem; ORB recusa ir para paper; a mudança grava valor anterior.
**Por quê:** Feature 8 pede ligar ou desligar cada estratégia no painel, sem cadastrar família nova.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: PATCH /api/strategies/{key} existe; load_trigger_snapshot não inclui strategy_states; Central não lista famílias (só o HTML legado do Command Panel v1).
desejado: Central mostra strategy_key, fase, paper_allowed; controles chamam o PATCH existente; NEVER_PAPER_KEYS sem controle paper.
guardrail: sem cadastro de família nova; sem auto-promoção; LIVE false.
testes: GET Central contém as chaves do catálogo; PATCH orb paper_limited ⇒ 4xx; PATCH momentum paper_limited (quando operador) grava trigger_changes.
files:
  - src/panel_ops_html.py
  - src/v4_web_dashboard.py
  - tests/test_panel_ops.py
  - tests/test_panel_triggers.py
depends_on: [N33.1]
```

### Task N33.3 — Registrar evidência de teste das Features 7–10

**Entrega:** O caderno de evidência ganha uma linha por critério das Features 7–10, com teste ou nota de evidência pendente sua.
**Como conferir:** Cada critério aponta nodeid de pytest ou a frase combinada de evidência pendente do operador.
**Por quê:** Código das ondas 3–4 existe; os checkboxes do contrato ainda estão vazios.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: REQUIREMENTS Features 7–10 todos [ ]; N24–N26 merged; N30–N32 planejadas.
desejado: seção CONTRACT-CLOSEOUT em TEST-EVIDENCE.md; Feature 8/9/10 critérios cobertos por testes de painel já existentes + N33.1/N33.2; Feature 7: snapshot/cancel/halt/crypto/N27.5/N27.6 via N30; “sinal válido vira ordem sem ação manual” e fill em produção = pending operator evidence se não houver pytest ponta a ponta com broker real.
guardrail: não marcar [x] nesta task (só evidência); não inventar fill.
files:
  - docs/TEST-EVIDENCE.md
depends_on: [N33.1, N33.2]
```

### Task N33.4 — Marcar Features 7–10 no contrato só com prova

**Entrega:** Os critérios 7–10 no contrato só viram feitos com a linha de evidência correspondente; o restante fica aberto com a nota combinada.
**Como conferir:** Abrir o contrato: visto apenas onde TEST-EVIDENCE cita teste; os outros têm “pending operator evidence”.
**Por quê:** O contrato v0.4 exige honestidade de evidência, não HTTP 200.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: Features 7–10 5+5+3+3 checkboxes [ ].
desejado: [x] somente com citação TEST-EVIDENCE; demais [ ] + nota 'pending operator evidence'. EasyPanel rebuild e fill demo real do operador não são [x] de pytest.
guardrail: não marcar Feature 11 aqui; LIVE false.
files:
  - docs/REQUIREMENTS.md
  - docs/TEST-EVIDENCE.md
depends_on: [N33.3]
```

---

## Sprint N34 — Ajuste supervisionado (Feature 11)

> Categoria: N  
> Status: planejada  
> titulo_humano: Sugestão rotulada, ajuste reversível, risco intocado  
> resumo_humano: Sugestões aparecem como sugestão, nunca como ordem. Ajuste automático nasce desligado e só mexe em parâmetro que já existe na estratégia original, na faixa original. Cada mudança tem antes, depois e motivo, e você desfaz na Central. Âncoras de risco não entram nesse caminho. O método fino (o que é erro, de quanto em quanto) continua aberto para você.  
> Gate: rótulo sugestão; auto-tune default OFF; só flags/setups já no vendor (ex. --min-volume, seleção de setup); trigger_changes-like undo; âncoras intocadas; G-AJUSTE flagado; N28 substituída; LIVE false  
> review: senior+qa  
> Depende de: N33, N21  
> Gerado via: `/pmo plan` — CONTRACT-CLOSEOUT 2026-11-15  
> Brief: `docs/.briefs/N34.brief.md`

### Em uma frase

Sugestão não é ordem; qualquer ajuste automático nasce desligado, é reversível e não mexe nas âncoras de risco.

### O que muda para você

- O que for sugestão vem com o rótulo de sugestão
- Você vê antes/depois/motivo e pode desfazer na Central
- O ajuste automático só liga se você ligar; o método fino continua à sua escolha

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Rótulo de sugestão | Item de sugestão não abre ordem só por existir |
| 2 | Histórico com desfazer | Cada ajuste mostra antes, depois e motivo; desfazer volta o valor |
| 3 | Auto-ajuste conservador desligado | Default off; só parâmetros originais na faixa original |
| 4 | Âncoras intocadas | Teste prova que capital/perda/posições não mudam por esse caminho |
| 5 | Método em aberto | A dúvida do contrato sobre o método permanece visível para você |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | P | N34.1 Rotular sugestão como sugestão, nunca como ordem | `/dev` | — |
| [ ] | M | N34.2 Registrar antes, depois e motivo com desfazer na Central | `/dev` | N34.1 |
| [ ] | M | N34.3 Ajuste automático conservador, desligado por padrão | `/dev` | N34.2 |
| [ ] | P | N34.4 Provar que ajuste nunca altera âncora de risco | `/qa testes` | N34.3 |
| [ ] | P | N34.5 Deixar o método de ajuste visível para o operador | docs | N34.3 |

### Task N34.1 — Rotular sugestão como sugestão, nunca como ordem

**Entrega:** Toda sugestão de estratégia aparece marcada como sugestão e não autoriza ordem por si só.
**Como conferir:** No painel o item diz que é sugestão; o caminho de ordem exige sinal assinado como nas outras famílias.
**Por quê:** Feature 11 critério 1; o ranking Prodígio já tem aviso semelhante.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: Prodígio page já avisa research; opportunities não rotulam “sugestão” de forma genérica para Feature 11.
desejado: campo suggestion=true / label visível; produtor de sugestão não chama paper_gateway_queue.
guardrail: LIVE false; sugestão ≠ paper_allowed.
testes: HTML contém rótulo de sugestão; clique/API de sugestão não insere paper_orders.
files:
  - src/panel_ops_html.py
  - tests/test_panel_ops.py
depends_on: []
```

### Task N34.2 — Registrar antes, depois e motivo com desfazer na Central

**Entrega:** Cada ajuste de parâmetro de estratégia grava antes, depois e motivo, e a Central oferece desfazer.
**Como conferir:** Depois de um ajuste, o histórico mostra os três campos; desfazer restaura o valor anterior sem tocar âncora de risco.
**Por quê:** Feature 11 critério 3; N28.3 absorvido aqui.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: DATABASE.md §6.6 adia tabela de ajuste automático; trigger_changes cobre control_flags/market_controls/strategy_states (fase), não parâmetros de estratégia.
desejado: migration append-only strategy_parameter_changes (strategy_key, param_name, old_value, new_value, reason, changed_at) + PATCH undo na Central; sem soft-delete de histórico.
guardrail: LIVE false; não escrever control_flags por esse PATCH.
testes: insert + undo restaura; trigger/parameter log append-only.
files:
  - migrations/003_strategy_parameter_changes_up.sql
  - src/supervised_tune.py
  - src/v4_web_dashboard.py
  - src/panel_ops_html.py
  - tests/test_supervised_tune.py
depends_on: [N34.1]
```

### Task N34.3 — Ajuste automático conservador, desligado por padrão

**Entrega:** Um ajuste automático opcional, desligado por padrão, só altera parâmetro que já existe na estratégia original e só dentro da faixa original (por exemplo volume mínimo ou escolha de setup do scanner).
**Como conferir:** Com a flag desligada, zero mudança; ligada, tenta só `--min-volume` / seleção de setup já documentados no scanner original, nunca um limiar novo.
**Por quê:** G-AJUSTE está em aberto; o contrato permite auto-ajuste só na faixa original. Método marcado para a sua revisão.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: G-AJUSTE aberto (REQUIREMENTS §9 #8); trader-scanner CLI já tem --min-volume e seleção de setup; não há motor de tune.
desejado: flag supervised_tune_on default false (control_flags ou env, default off); quando on, candidato a ajuste SOMENTE min-volume (faixa do argparse original) ou subset dos setups já em find_setups; nunca RSI/percentil/score novos; nunca âncoras; rotular DEFAULT_CONSERVATIVE_AWAITING_G_AJUSTE.
guardrail: off by default; não inventar parâmetro; LIVE false.
testes: default off ⇒ zero writes; on + min-volume dentro da faixa ⇒ log before/after; valor fora da faixa ⇒ reject.
files:
  - src/supervised_tune.py
  - src/risk_control_flags.py
  - tests/test_supervised_tune.py
depends_on: [N34.2]
```

### Task N34.4 — Provar que ajuste nunca altera âncora de risco

**Entrega:** Teste prova que o caminho de ajuste não altera capital, perda, posições nem as outras âncoras.
**Como conferir:** O teste falha se qualquer âncora de `control_flags` mudar depois do ajuste.
**Por quê:** Feature 11 critério 4 / N28.4.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: sem teste de isolamento âncora vs tune.
desejado: fixture aplica undo/auto-tune; control_flags âncoras idênticas.
guardrail: LIVE false.
testes: pytest nodeid estável para N33/N34 evidência.
files:
  - tests/test_supervised_tune.py
  - src/supervised_tune.py
depends_on: [N34.3]
```

### Task N34.5 — Deixar o método de ajuste visível para o operador

**Entrega:** A dúvida do contrato sobre o método de ajuste permanece aberta, agora apontando o default conservador desligado que a plataforma passou a oferecer.
**Como conferir:** No contrato, a linha do método cita o default (volume mínimo / setups originais, desligado) e pede a sua confirmação.
**Por quê:** Planejar infra sem fingir que G-AJUSTE foi decidido.

**Detalhe técnico**

**executor_prompt**:
```
estado_atual: REQUIREMENTS §9 #8 Status Aberta.
desejado: atualizar a linha com o default conservador OFF e pedido de revisão; Feature 11 critérios [x] só os cobertos por N34.1–N34.4 testes; auto-ajuste fino permanece [ ] se G-AJUSTE não respondido.
guardrail: não inventar método; não marcar tudo [x].
files:
  - docs/REQUIREMENTS.md
  - docs/TEST-EVIDENCE.md
depends_on: [N34.3]
```

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
