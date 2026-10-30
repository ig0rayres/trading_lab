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

## Fora do roadmap D (backlog N)

| Tema | Origem | Notas |
|------|--------|-------|
| Estratégias Ta Barato / Prodigy / momentum (fórmulas) | LEGACY-ANALYSIS | N7 cobre fases; **não** inventar limiares de scoring |
| Walk-forward / Lean | RESEARCH_ROADMAP | Motor separado |
| Collective2 paper-copy | Feature 4 | Fora de N7; `approved_for_paper_copy` permanece falso |
| CI deploy EasyPanel | Operador | N6 feito; bump de imagem só com sprint própria (fora de N8) |
| Submodule pin vs clone raso | D1 | Preferir pin revisado, não `main` cego |

---

## Próximo passo operador

1. N8 **concluída** (PR #4 → `main` `81e6e88`; homolog: 7 linhas `strategy_states` no EasyPanel).  
2. **`/git front finish n8-homolog-seed`** (ou `gc --apply --safe`) e reconciliar na mãe.  
3. **`/pmo`** — escolher próximo item (backlog N ou Feature 5 fill real); sem inventar limiar de scoring.
