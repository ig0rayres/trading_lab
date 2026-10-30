# Issues — Trading Lab

## ISSUES-INDEX

| ID | Status | Sprint | Título |
|----|--------|--------|--------|
| ISS-001 | fechado | N6 | Imagem EasyPanel sem psycopg e sem vendor pinado |
| ISS-002 | fechado | N7 | Catálogo de estratégias sem persistência nem Gate B |
| ISS-003 | validado | N8 | `strategy_states` vazia após `ledger-migrate apply` |

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
| Status | validado |

**Impacto:** `migrations/001_ledger_up.sql` cria `strategy_states` sem seed. `ledger_migrate.apply()` só aplica DDL e retorna cedo em `already_applied`. `ensure_strategy_defaults()` existe em `src/strategy_catalog.py` mas só corre no caminho de leitura (Gate B / `fetch_strategy_phase`). EasyPanel ficou sem as 7 linhas até INSERT manual ou worker. Homologação não é reprodutível só com migrate.

**Critério de fechamento:** `ledger-migrate apply` (incluindo `already_applied`) chama `strategy_catalog.ensure_strategy_defaults()`; pytest de roundtrip com `LEDGER_DATABASE_URL` deixa 7 linhas em `strategy_states`; runbook em `docs/HOMOLOGATION.md` + nota EasyPanel em `docs/INFRASTRUCTURE.md` / `EASYPANEL.md`; seed insert-if-missing (não overwrite); sem migration `002`; sem reabrir Gate B nem Feature 4 scoring; `LIVE_TRADING_ENABLED` false.

**Fontes:** operador `/pmo plan` opção A 2026-10-30; ISS-002 fechado; evidência EasyPanel: tabela vazia até seed manual.
