# Sprint diary — Trading Lab

## Índice

| Sprint | Módulos | Temas | Linhas |
|--------|---------|-------|--------|
| D1 | baseline, vendor | CI, submodule, EasyPanel 2 apps | 12–28 |

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
