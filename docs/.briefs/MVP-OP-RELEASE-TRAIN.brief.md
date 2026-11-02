# MVP-OP release train — plan brief

> `/pmo plan MVP-OP-1.0` · operador opção B · 2026-11-02 · **plan-only PR**

## Objetivo

Uma linha de releases (**0.9 → 1.0 → 1.1**) até operador ter copy + Prodígio + catálogo + melhoria contínua **homologados**, sem deploy por doc.

### Leituras

| Artefato | Trecho |
|----------|--------|
| `docs/REQUIREMENTS.md` | § MVP, Feature 4–5, stakeholder pacote único |
| `docs/ISSUES.md` | § Release train MVP-OP |
| `docs/MVP-DEMO-RUNBOOK.md` | § Política de deploy |
| `docs/TEST-EVIDENCE.md` | § N12, N13 |
| `PRODIGY_RANK_V34.md` | research-only rank |
| `src/prodigy_rank.py` | no execution authorization |

### Contratos afetados (N16+)

- Ingestão webhook/worker + `strategy_key`
- `PRODIGY_PROVIDERS`, `strategy_states.phase`
- Alpaca paper API (host paper only)

### Assumido

- Operador aprova merge deste plano antes de `/pmo sprint N16`.
- Tá Barato **1.1** blocked se upstream não entregar fórmulas — documentar gap, não inventar.
- Collective2 copy permanece reprovado salvo `approved_for_paper_copy` explícito.

### N/A

Guardrail tasks M — preencher no `/pmo sprint N16` via G0.
