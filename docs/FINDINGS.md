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
| F-007 | D4 | M | Feature 3 critérios em REQUIREMENTS + testes | fechado |
| F-008 | D4 | M | Teto 3 posições abertas (`open_positions` / Alpaca GET) | fechado |
| F-009 | D4 | P | Rejeição Gate B persiste `risk_decisions` | fechado |
| F-010 | D4 | P | Limites paper em `gate_b_risk.py` + REQUIREMENTS Feature 3 | fechado |
| F-011 | D5 | M | Reconcile→ledger + dashboard + homologação doc (fill real = operador) | fechado |

## Notas

- **D3** fechada no ROADMAP após F-001, F-005, F-006 (CI pytest obrigatório).
- **D4** fechada após F-007–F-010 e CI pytest.
- **D5** fechada no escopo código/CI; fill Alpaca real continua checklist operador (Feature 5).
- **D1** CI + vendor_verify ok; **F-003** (orb parity) permanece aberto.
