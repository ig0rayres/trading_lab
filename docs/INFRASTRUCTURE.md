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

PostgreSQL da instância existente do operador (ver `docs/DATABASE.md`). Migrations em `migrations/001_ledger_*.sql`; CLI `scripts/run.sh ledger-migrate`.

### Kill switch (Gate B)

Ordens paper não passam do Gate B quando:

1. **`TRADING_LAB_KILL_SWITCH=true`** no ambiente do worker/gateway (fail-closed imediato), ou
2. A linha mais recente em **`control_flags.kill_switch_on = true`** no Postgres (`LEDGER_DATABASE_URL`).

O scheduler de pesquisa (`v4-scheduler`) não consulta o kill switch; só caminhos pós-Gate A (`tradingview_worker`, fila paper). Para ligar via SQL (operador):

```sql
INSERT INTO control_flags (kill_switch_on, max_risk_per_trade_cents, prodigy_risk_cents)
VALUES (true, 5000, 2000);
```

Desligar: inserir nova linha com `kill_switch_on = false` (histórico append-only por linhas novas).

---

## 6. Secrets (nomes apenas)

Nunca commitar valores. Referência de nomes: webhook secret, chaves Alpaca **paper**, DSN Postgres — conforme `.env.example` quando criado na Sprint D1/D2.

---

## 7. Hooks Cursor (Beesy)

Hooks de automação Beesy (`safety-guard`, `pmo-update`) **não** foram instalados neste passo: o repo não está ancorado na suíte Beesy com `scripts/` do framework. Podem ser adicionados quando o operador ligar o projeto a um anchor com hooks compartilhados.

---

## 8. EasyPanel (dois apps, uma imagem)

Decisão do operador (2026-10-30): manter **`trading-lab`** + **`trading-lab-webhook`**, alinhado a `docs/ARCHITECTURE.md` ADR-002.

| Serviço | Comando | Porta / domínio |
|---------|---------|-----------------|
| `trading-lab` | `v4-scheduler` (CMD padrão do Dockerfile) | Sem publicação se só pesquisa |
| `trading-lab-webhook` | `tv-webhook` via entrypoint `run.sh` | HTTPS só neste app, após Gate A |

Mesma build de imagem; volumes `/app/reports` e `/app/vendor` persistentes; **não** substituir deploy EasyPanel atual sem release supervisionada.

### Apply ledger migration (operador)

1. Criar usuário `trading_lab` no Postgres existente (INSERT/SELECT/UPDATE nas tabelas do ledger; sem superuser).
2. Definir `LEDGER_DATABASE_URL` **somente** no serviço paper-gateway (não no scheduler).
3. No shell do container: `/app/scripts/run.sh ledger-migrate apply`
4. Verificar: `/app/scripts/run.sh ledger-migrate status`
5. Rollback de emergência (somente em homologação): `/app/scripts/run.sh ledger-migrate rollback`

Arquivos SQL: `migrations/001_ledger_up.sql` / `001_ledger_down.sql`. CI executa roundtrip apply/rollback com Postgres efêmero.

---

## 9. Próximos passos

1. **Sprint D2** — migrations ledger Postgres (`docs/ROADMAP.md`).
2. Opcional: `/devops infra` — topologia alinhada ao Postgres e volumes de reports.
3. Deploy GitHub → EasyPanel quando houver sprint de infra aprovada.
