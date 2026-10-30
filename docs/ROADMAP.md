# Roadmap Técnico — Trading Lab

> Gerado em: 2026-10-30  
> Fase: 8 — Planejamento técnico (`/pmo plan`, categoria **D**)  
> Baseado em: `docs/PROJECT-BRIEF.md`, `docs/REQUIREMENTS.md`, `docs/ARCHITECTURE.md`, `docs/DATABASE.md`, `docs/LEGACY-ANALYSIS.md`  
> Status: **Em execução** (Sprint D2 próxima)  
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
| D2 | D | Tabelas ledger no Postgres + rollback testado | pendente | 5 | ledger | Persistência paper | 117–145 |
| D3 | D | Gate A rejeita sinal inválido sem broker | pendente | 6 | signal-gate-a | Ingestão autêntica | 147–178 |
| D4 | D | Gate B bloqueia ordem fora de limites | pendente | 6 | risk-gate-b, paper-gateway | Risco antes de fila | 180–212 |
| D5 | D | Paper reconciliado read-only; nenhum live | pendente | 5 | paper-gateway, observability | Homologação ponta a ponta | 214–242 |

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

---

## Grafo de Dependências

```
[D1 CI + vendor pin] ──► [D2 Postgres ledger]
                              │
[D3 Gate A] ──────────────────┼──► [D4 Gate B + gateway queue]
                              │              │
                              └──────────────┴──► [D5 reconcile + dashboard auth]
```

D3 pode iniciar em paralelo com D2 após D1, mas D5 depende de D2–D4.

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
| [x] | M | Rodar `vendor_verify` / `parity` offline contra pin | skill `paper-order-gate` refs | vendor |
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
| [ ] | M | Alembic/SQL migration alinhada a `docs/db-schema.dbml` | `/arquiteto dados` | D1 |
| [ ] | P | Teste rollback da migration | `/qa testes` | migration |
| [ ] | M | Adapter de persistência (append-only; sem `deleted_at` como borracha) | `/dev` | migration |
| [ ] | P | `.env.example` só com **nomes** de variáveis (DSN) | `/devops` | — |
| [ ] | P | Documentar runbook de apply na instância existente | `docs/INFRASTRUCTURE.md` | migration |

---

## Sprint D3 — Gate A (sinal)
> Categoria: D  
> titulo_humano: Webhook e ingestão recusam sinal falso antes de qualquer fila  
> Gate: testes cobrem rejeição (segredo, schema, idempotência); nenhuma chamada Alpaca no caminho A  
> bom_ref: BOM-3  
> review: senior+qa

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | Extrair/contratar Gate A conforme `docs/api-spec.yaml` + skill `signal-ingest` | `/dev` | D1 |
| [ ] | P | Testes: sinal inválido → código de motivo, zero ordem | `/qa testes` | Gate A |
| [ ] | M | Integrar News First / copy apenas como **entrada** auditada (sem broker) | `/dev` | Gate A |
| [ ] | P | Calendário/sessão: recusar fora de horário (upstream `session`) | `/dev` | vendor |
| [ ] | P | Atualizar `docs/REQUIREMENTS.md` Feature 2 critérios | `/pmo` | testes |
| [ ] | P | Registrar achados abertos em `docs/FINDINGS.md` se gap | `/pmo triar` | — |

---

## Sprint D4 — Gate B e fila paper
> Categoria: D  
> titulo_humano: Limites de capital e risco antes da fila Alpaca paper  
> Gate: ordem bloqueada excede R$50/posição/3 slots; `PAPER_GATEWAY_QUEUE_ONLY` continua não sendo fill  
> bom_ref: BOM-3, BOM-4  
> review: senior+qa

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | Gate B: reuso `trader-risk` + políticas REQUIREMENTS (capital paper) | skill `paper-order-gate` | D2, D3 |
| [ ] | M | Paper gateway: só após A+B; stub de broker em testes | `/dev` | Gate B |
| [ ] | P | Testes: HTTP 200 / queue ≠ fill documentados | `/qa testes` | gateway |
| [ ] | M | Gravar intenção de ordem no ledger (pré-envio) | `/dev` | D2 |
| [ ] | P | Kill switch operacional documentado | `docs/INFRASTRUCTURE.md` | — |
| [ ] | P | Paridade de limites com `ENGINEERING_RULES.md` | `/qa validar` | Gate B |

---

## Sprint D5 — Homologação paper (read-only reconcile)
> Categoria: D  
> titulo_humano: Paper reconciliado sem live e sem trocar EasyPanel  
> Gate: fluxo sinal→A→B→fila→fill simulado/real paper read-only; dashboard exige auth se público  
> bom_ref: BOM-3, BOM-4  
> review: comprehensive

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | `v4_alpaca_reconcile` integrado ao ledger (READ_ONLY) | `/dev` | D4 |
| [ ] | M | Trilha de evidência: shadow vs paper no dashboard | `/dev` | D4 |
| [ ] | P | Checklist de homologação operador (sem live) | `docs/REQUIREMENTS.md` | — |
| [ ] | P | Export comparativo EasyPanel vs snapshot (SHA imagem) | operador | — |
| [ ] | M | Fechar critérios de aceite Features 2–4 em REQUIREMENTS | `/pmo` | reconcile |

---

## Fora do roadmap D (backlog N)

| Tema | Origem | Notas |
|------|--------|-------|
| Estratégias Ta Barato / Prodigy / momentum | LEGACY-ANALYSIS | Não inventar limiares |
| Walk-forward / Lean | RESEARCH_ROADMAP | Motor separado |
| CI deploy EasyPanel | Operador | Exige `/devops infra` + L2 |
| Submodule pin vs clone raso | D1 | Preferir pin revisado, não `main` cego |

---

## Próximo passo operador

1. Revisar este roadmap (ajustar ordem ou escopo).  
2. **`/pmo sprint`** — iniciar **Sprint D1** (worktree: `/git front create d1-baseline` se paralelo).  
3. Não promover para paper principal enquanto ORB intraday seguir negativo em evidência (REQUIREMENTS).
