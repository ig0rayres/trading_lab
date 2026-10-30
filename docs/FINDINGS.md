# Findings — Trading Lab

> Índice de gaps abertos (não inventar critérios; fechar sprint só com evidência).

## FINDINGS-INDEX

| ID | Sprint | Severidade | Resumo | Status |
|----|--------|------------|--------|--------|
| F-001 | D3 | M | News First / copy → `signal_events` auditado (sem broker) | fechado |
| F-002 | D3 | P | `docs/FINDINGS.md` criado; gaps D1–D4 registrados | fechado (este doc) |
| F-003 | D1 | P | `parity.py` / orb-parity não executado (faltam artefatos v0.5) | aberto |
| F-004 | D2 | P | `.env.example` alinhado ao código | fechado |
| F-005 | D3 | M | Gate A: header `X-Webhook-Token` + legacy `/webhook/{token}` | fechado |
| F-006 | D3 | P | Testes HTTP handler webhook | fechado |
| F-007 | D4 | M | `docs/REQUIREMENTS.md` Feature 3 critérios ainda `[ ]` (kill switch, limites, sessão no Gate B) | aberto |
| F-008 | D4 | M | Gate B: `max_trades_per_day` upstream ≠ teto de **3 posições abertas** do REQUIREMENTS (worker não lê posições Alpaca antes da fila) | aberto |
| F-009 | D4 | P | Rejeição Gate B não persiste linha em `risk_decisions` (só aceite + `paper_orders` intent) | aberto |
| F-010 | D4 | P | Marcar “paridade ENGINEERING_RULES” foi documental; limites estão em REQUIREMENTS/paper modules, não em ENGINEERING_RULES | aberto |
| F-011 | D5 | M | Homologação ponta a ponta (fill + reconcile + dashboard auth) — backlog explícito | aberto |

## Notas

- **D4 não está pronta para “concluída”** enquanto F-007–F-009 (e dependência D3 estável) permanecerem abertos.
- **D2** migration/CI ok; F-004 impede fechar operador runbook sem confusão de nomes.
- **D1** CI + vendor_verify ok; F-003 é aceite consciente até existirem artefatos orb.
