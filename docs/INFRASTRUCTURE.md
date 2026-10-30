# Infraestrutura — Trading Lab

> Gerado em: 2026-10-30
> Fase: 7 — `/devops planejar`
> Estratégia: **CI-only** (sem CD para EasyPanel neste corte)
> Baseado em: `docs/ARCHITECTURE.md`, `docs/REQUIREMENTS.md`

---

## 1. Ambientes

| Ambiente | Onde roda | Observação |
|----------|-----------|------------|
| Desenvolvimento | Workspace local ou container `docker build` | `LIVE_TRADING_ENABLED=false` obrigatório |
| CI | GitHub Actions (`.github/workflows/ci.yml`) | Clona `day-trader-skill` em `vendor/` a cada job |
| Paper (futuro) | Instância separada; **não** substituir serviços EasyPanel `trading-lab` / `trading-lab-webhook` | Chaves só via secrets do host |

Não há staging/prod gerenciados por pipeline neste repositório até `/devops infra` e decisão explícita de deploy.

---

## 2. CI (GitHub Actions)

Ordem dos jobs:

1. **test** — Python 3.12, `pip install -r requirements-dev.txt`, clone raso de [day-trader-skill](https://github.com/Jakeschincariol/day-trader-skill), `UPSTREAM_DIR=vendor/day-trader-skill`, `pytest -q`.
2. **docker-build** — `docker build` da imagem de pesquisa (`Dockerfile` existente).

Variáveis fixas no workflow:

- `LIVE_TRADING_ENABLED=false`
- `PYTHONPATH=src`

Pin reprodutível em produção: definir `UPSTREAM_COMMIT` no ambiente do serviço e documentar SHA em `docs/VENDOR-PIN.md` (Sprint D1).

---

## 3. Docker

- **Imagem**: `python:3.12-slim`, entrypoint `scripts/run.sh`.
- **Comando padrão**: `v4-scheduler` (pesquisa; sem ordem).
- **Segundo processo** (quando homologado): `tv-webhook` via compose ou segundo serviço EasyPanel — fora deste CI.

Artefatos: `Dockerfile`, `.dockerignore`.

---

## 4. Upstream vendor

| Item | Valor |
|------|--------|
| Repositório | `Jakeschincariol/day-trader-skill` |
| Montagem em runtime | `/app/vendor/day-trader-skill` ou `UPSTREAM_DIR` |
| Loader | `src/original.py` |
| Testes de paridade | `vendor_verify`, `parity` (CLI via `run.sh`) — Sprint D1 |

O ZIP importado **não** incluiu `vendor/`; CI e Sprint D1 tratam de pin + evidência.

---

## 5. Banco de dados (ledger paper)

PostgreSQL da instância existente do operador (ver `docs/DATABASE.md`). Migrations **não** existem ainda — Sprint D2.

---

## 6. Secrets (nomes apenas)

Nunca commitar valores. Referência de nomes: webhook secret, chaves Alpaca **paper**, DSN Postgres — conforme `.env.example` quando criado na Sprint D1/D2.

---

## 7. Hooks Cursor (Beesy)

Hooks de automação Beesy (`safety-guard`, `pmo-update`) **não** foram instalados neste passo: o repo não está ancorado na suíte Beesy com `scripts/` do framework. Podem ser adicionados quando o operador ligar o projeto a um anchor com hooks compartilhados.

---

## 8. Próximos passos

1. `/pmo sprint` — ativar **Sprint D1** a partir de `docs/ROADMAP.md`.
2. Opcional: `/devops infra` — topologia alinhada ao Postgres e volumes de reports.
3. Configurar **remote Git** e abrir PRs em `front/*` conforme regra do operador.
