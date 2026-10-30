# Homologação paper (operador) — sem live

> Sprint D5. `LIVE_TRADING_ENABLED=false` permanece obrigatório.

## Checklist (ordem sugerida)

1. **CI verde** em `main` (pytest + Postgres efêmero + `docker-smoke.yml`: psycopg import, vendor `entry.py`, `LIVE_TRADING_ENABLED=false`). Local: `docker build -t trading-lab:ci . && bash scripts/ci-docker-smoke.sh`. Pin drift: `tests/test_image_pin.py`. Evidência em `docs/TEST-EVIDENCE.md`.
2. **Postgres:** `scripts/run.sh ledger-migrate apply` no serviço com `LEDGER_DATABASE_URL`. O apply semeia **7** linhas em `strategy_states` (insert-if-missing; re-apply seguro). Verificar:
   ```sql
   SELECT strategy_key, phase FROM strategy_states ORDER BY strategy_key;
   ```
   Esperado: `news_first`, `momentum`, `ta_barato`, `prodigy_15d` → `research`; `signal_copy` → `paper_limited`; `orb`, `mean_reversion` → `shadow`.
3. **Gate A:** webhook com `TV_WEBHOOK_TOKEN` (header `X-Webhook-Token` ou legacy `/webhook/{token}`); confirmar linhas em `signal_events`.
4. **Gate B:** worker com Alpaca paper read-only; rejeição grava `risk_decisions`; aceite grava `paper_orders` (`queued_intent`).
5. **Reconcile read-only:** `PAPER_RECONCILE_LEDGER_APPLY=true` + credenciais paper; `scripts/run.sh v4-alpaca-reconcile --output /app/reports/paper/reconcile.json`. Ver `ledger_apply` no JSON — **não** implica `broker_reconciled=true`.
6. **Dashboard:** bind `127.0.0.1` ou remoto só com `DASHBOARD_ALLOW_REMOTE=true` + `DASHBOARD_BEARER_TOKEN` (≥32). `/api/status` expõe `kill_switch_on` e `shadow_vs_paper`.
7. **Kill switch:** testar `TRADING_LAB_KILL_SWITCH=true` ou linha em `control_flags`; confirmar bloqueio no worker (sem ordem).
8. **EasyPanel comparativo (manual):** anotar SHA da imagem em execução vs `git rev-parse HEAD` deste repo; **não** substituir serviços sem release supervisionada (`docs/INFRASTRUCTURE.md`).

## O que **não** conta como homologado

- HTTP 200 / `PAPER_GATEWAY_QUEUE_ONLY` / fila sem fill real observado.
- Conta paper existente sem trilha ledger + reconcile aplicado.
- ORB ou copy Collective2 como estratégia principal (Feature 4 aberta).

## Critérios parciais cobertos em CI

- Sinal inválido / duplicata / gates A+B: `tests/test_tradingview_webhook*.py`, `tests/test_gate_b_*.py`, `tests/test_paper_gateway_queue.py`.
- Ledger reconcile: `tests/test_ledger_reconcile.py` (com `LEDGER_DATABASE_URL` no job CI).

Fill real na corretora com P&L verificado continua **passo operador** com chaves paper reais.
