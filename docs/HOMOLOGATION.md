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

**Evidência colada pelo operador (Sprint N9):** preencher a tabela em [`docs/TEST-EVIDENCE.md` § Homologação D5 itens 3–7](TEST-EVIDENCE.md) — só contagens redigidas, sem tokens nem chaves.

---

## Runbook detalhado — itens 3–7 (EasyPanel)

Pré-requisitos nos dois apps: `LIVE_TRADING_ENABLED=false`, `LEDGER_DATABASE_URL` no serviço webhook/worker, migrate apply feito (item 2). Comandos abaixo assumem shell no container (`/app/scripts/run.sh …`).

### 3. Gate A — webhook → `signal_events`

| Passo | Ação |
|-------|------|
| Subir | No app **`trading-lab-webhook`**: comando `tv-webhook` (via `run.sh`). Variável **`TV_WEBHOOK_TOKEN`** já configurada no painel (não colar no repo). |
| Enviar sinal | `POST` HTTPS para o domínio do webhook. Caminho: **`/webhooks/tradingview`** com header **`X-Webhook-Token: <TV_WEBHOOK_TOKEN>`**, ou legacy **`POST /webhook/<TV_WEBHOOK_TOKEN>`**. Corpo JSON mínimo válido (ver `tests/test_tradingview_webhook_http.py`: ticker, side, etc.). |
| Não conta como homologado | HTTP **202** / corpo **`QUEUED`** / ausência de linha em Postgres — resposta HTTP sozinha não prova persistência. |
| Verificar | No Postgres do ledger: `SELECT id, status, created_at FROM signal_events ORDER BY created_at DESC LIMIT 5;` — esperar **≥1 linha** após POST válido. Anotar na folha de evidência: contagem de linhas e `status` (redigido). |

### 4. Gate B — worker → `risk_decisions` + `paper_orders`

| Passo | Ação |
|-------|------|
| Subir | Mesmo container (ou processo dedicado) com **`/app/scripts/run.sh tv-worker`**, credenciais Alpaca **paper** read-only, `LEDGER_DATABASE_URL` setado. |
| Fluxo | Worker consome fila interna pós–Gate A; **rejeição** deve gravar **`risk_decisions`**; **aceite** grava **`paper_orders`** com **`status = queued_intent`**. |
| Não conta como homologado | **`PAPER_GATEWAY_QUEUE_ONLY`**, fila sem linha no ledger, **`orders_sent = 0`** no JSON do worker — intenção na fila **não** é fill Alpaca. |
| Verificar rejeição (opcional) | Forçar sinal fora de sessão ou estratégia não-paper (ex. `orb` em shadow): `SELECT decision, reason FROM risk_decisions ORDER BY created_at DESC LIMIT 3;` |
| Verificar aceite (opcional) | Sinal `signal_copy` em fase paper com gates OK: `SELECT status, symbol FROM paper_orders ORDER BY created_at DESC LIMIT 3;` — esperar **`queued_intent`**. |
| Evidência | Contagens redigidas na folha N9 (itens 4a rejeição / 4b aceite — pode ser “n/a” se só um caminho testado). |

### 5. Reconcile read-only — `ledger_apply`

| Passo | Ação |
|-------|------|
| Env | **`PAPER_RECONCILE_LEDGER_APPLY=true`**, credenciais Alpaca paper no container, migrate já aplicado. |
| Comando | `/app/scripts/run.sh v4-alpaca-reconcile --output /app/reports/paper/reconcile.json` |
| Verificar JSON | Campo **`ledger_apply`** presente (objeto/lista conforme implementação). **`broker_reconciled`** deve permanecer **`false`** — reconcile read-only **não** fecha homologação de fill. |
| Evidência | Anotar na folha: “`ledger_apply` presente: sim/não”; **`broker_reconciled`**: false. |

### 6. Dashboard — auth e `/api/status`

| Passo | Ação |
|-------|------|
| Subir | `/app/scripts/run.sh v4-dashboard` — bind **`127.0.0.1`** no container, ou remoto só com **`DASHBOARD_ALLOW_REMOTE=true`** e **`DASHBOARD_BEARER_TOKEN`** (≥32 caracteres; valor só no EasyPanel). |
| Verificar | `GET /api/status` com header **`Authorization: Bearer <token>`** (quando exigido). JSON deve expor **`kill_switch_on`** e **`shadow_vs_paper`**. |
| Evidência | Anotar: auth exigida sim/não; campos presentes sim/não (sem colar bearer). |

### 7. Kill switch — bloqueio no worker

| Passo | Ação |
|-------|------|
| Ligar | **`TRADING_LAB_KILL_SWITCH=true`** no env do **worker** **ou** SQL append-only em **`control_flags`** (`kill_switch_on = true`) — ver `docs/INFRASTRUCTURE.md` § Kill switch. |
| Testar | Enviar sinal que passaria Gate B com switch desligado; com switch **ligado**, worker **não** deve criar nova **`queued_intent`** / **`orders_sent`** permanece 0. |
| Desligar | `TRADING_LAB_KILL_SWITCH=false` ou nova linha `control_flags` com `kill_switch_on = false`. |
| Evidência | Anotar: bloqueio observado sim/não; sem ordem enviada. |

---

## Passo operador opcional — Feature 5 (fora do gate N9)

Fill real na Alpaca Paper (aceite, fill parcial/cheio, P&L reconciliado) **não** faz parte do gate desta sprint. Permanece critério aberto em `docs/REQUIREMENTS.md` (Feature 5). Se o operador quiser tentar depois da N9: usar credenciais paper no ambiente controlado, trilha documentada em Feature 5, e **nunca** tratar `queued_intent` ou HTTP 200 como fill comprovado.

---

- HTTP 200 / `PAPER_GATEWAY_QUEUE_ONLY` / fila sem fill real observado.
- Conta paper existente sem trilha ledger + reconcile aplicado.
- ORB ou copy Collective2 como estratégia principal (Feature 4 aberta).

## Critérios parciais cobertos em CI

- Sinal inválido / duplicata / gates A+B: `tests/test_tradingview_webhook*.py`, `tests/test_gate_b_*.py`, `tests/test_paper_gateway_queue.py`.
- Ledger reconcile: `tests/test_ledger_reconcile.py` (com `LEDGER_DATABASE_URL` no job CI).

Fill real na corretora com P&L verificado continua **passo operador** com chaves paper reais.
