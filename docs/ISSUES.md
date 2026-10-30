# Issues — Trading Lab

## ISS-001 — Imagem EasyPanel sem psycopg e sem vendor pinado

| Campo | Valor |
|-------|--------|
| Categoria | improvement |
| Sprint | N6 |
| Status | em_validacao |

**Impacto:** Redeploy perde clone manual em `/app/vendor`; `ledger-migrate` e `load_original()` falham sem `pip install` ad hoc.

**Critério de fechamento:** `docker build` inclui `psycopg[binary]` e vendor @ SHA em `docs/VENDOR-PIN.md`; CI docker-build smoke verde; docs EasyPanel descrevem rebuild dos dois apps sem overlay vazio em `/app/vendor`.

**Fontes:** operador homologação 2026-10-30; `docs/ROADMAP.md` backlog N; `/pmo plan` + Rock PLAN.
