# Sprint diary — Trading Lab

## Índice

| Sprint | Módulos | Temas | Linhas |
|--------|---------|-------|--------|
| D1 | baseline, vendor | CI, submodule, EasyPanel 2 apps | 25–41 |
| D2 | ledger | migrations, ledger_store, CI Postgres | 15–21 |

---

## Sprint D2 — Ledger Postgres

**Gate:** migration apply/rollback; 8 tabelas; testes CI com Postgres efêmero.

**Entregue (código):** `migrations/001_ledger_*.sql`, `ledger_migrate.py`, `ledger_store.py`, `.env.example`, CI Postgres service.

**Próximo:** Sprint D3 Gate A.

---

## Sprint D1 — Baseline verificável

**Gate:** CI verde + vendor pinado + pytest (Actions run [41041762290](https://github.com/ig0rayres/trading_lab/actions/runs/41041762290)).

**Entregue:**

- Submodule `vendor/day-trader-skill` @ `3d0f4ef…`
- Workflow CI (pytest + docker build)
- `vendor_verify` PASS offline
- Remote `ig0rayres/trading_lab`; branches `main` e `sprint/D1`

**Decisões:**

- EasyPanel: dois serviços, mesma imagem (pesquisa + webhook), sem consolidar em um container.
- Live trading permanece desligado.

**Próximo:** Sprint D2 (ledger Postgres).
