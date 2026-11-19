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
| F-012 | N6 | M | Gate N6: diff não commitado; pytest/docker smoke/CI não reexecutados nesta rodada | fechado |
| F-013 | N9 | P | Worker `persist_risk_decision` não liga `signal_events` quando `signal_id` na fila está hasheado (journal `QUEUED` sem `paper_orders` / `risk_decisions`) | fechado |
| F-014 | N54 | M | Prodígio `calculate` sem persistir JSON quando `C2_API4_KEY` ausente (`v4_web_dashboard._live_refresh_prodigy`) | corrigido |
| F-015 | N54 | M | Monkey-patch global de `c2_history_collect.fetch` na importação do dashboard | corrigido |
| F-016 | N54 | M | Cooldown live-criteria sem lock em servidor threaded | corrigido |
| F-017 | N54 | P | POST refresh só exige cookie se `DASHBOARD_OPERATOR_SESSION` definido | corrigido |
| F-018 | N55 | P | Falha silenciosa no ramo TradingView do job live-criteria | corrigido — `N55MultiPlatformLiveCriteriaTests.test_n55_tradingview_refresh_failure_records_issue_without_wiping_queue` |
| F-019 | N56 | M | Job live-criteria junta `reports/` em `--root /app/reports` → pasta vazia `/app/reports/reports/providers/raw` | corrigido — `N56ProdigyCanonicalRawPathTests` |
| F-020 | N57 | M | Fila Collective2 só nasce da allowlist/JSON de pesquisa; arquivos brutos canônicos não entram como candidatos pendentes | corrigido — `N57Collective2RawQueueDiscoveryTests` |
| CQ-003 | N55 | L | `_unique_tradingview_origins` não filtra por `source` quando o campo existe | deferido |
| CQ-004 | N55 | M | Redesign lock/cooldown live-criteria (threading + persistência) | deferido |

## Notas

- **D3** fechada no ROADMAP após F-001, F-005, F-006 (CI pytest obrigatório).
- **D4** fechada após F-007–F-010 e CI pytest.
- **D5** fechada no escopo código/CI; fill Alpaca real continua checklist operador (Feature 5).
- **N6** fechada: PR #1 merge `6813fb5`; CI test + docker-smoke verdes; operador EasyPanel hashia (2026-10-30).
- **N9** homolog itens 3–7 operador (2026-10-30 / 2026-11-01): evidência em `TEST-EVIDENCE.md`. **F-013** fechado em **`main` `0509732`**: worker passa `queue_idempotency_key` (stem da fila); unittest integração OK no EasyPanel (2026-11-01).
- **N10** closeout: ROADMAP N9 concluída; runbook §4 documenta armadilhas de smoke (TTL/sessão).
- **N56 / F-019 (2026-11-19):** join duplicado em `_live_refresh_prodigy` / `_live_refresh_collective2` corrigido para `{root}/providers/raw` e `{root}/providers/signals` (`_providers_raw_dir`); pytest `N56ProdigyCanonicalRawPathTests` (3 nodeids). Fila Prodígio continua só `PRODIGY_CANDIDATE_RESEARCH`; `UNSCORABLE` + `closed_trades_15d=0` ausentes — comportamento esperado, não segundo defeito.
- **N57 / F-020 (2026-11-19):** após #76, allowlist vazia + fila sem linhas C2 apesar de arquivos brutos canônicos — `_merged_c2_strategy_ids` / `build_preapproval_queue` passam a unir glob `{root}/providers/raw/*_closed_trades.json` + JSON de pesquisa C2; fila pendente com `source: discovered` **sem** exigir allowlist/env. Allowlist / livro-razão permanece portão de **cópia paper** (`approved_for_paper_copy` false com lista vazia). Pytest `N57Collective2RawQueueDiscoveryTests` (3 nodeids). **ISS-024 permanece aberto** até merge + rebuild operador.
