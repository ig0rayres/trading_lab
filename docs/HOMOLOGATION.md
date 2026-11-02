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
| Fluxo | Worker consome fila interna pós–Gate A; liga `signal_events` pelo **nome do arquivo** na fila (stem = chave Gate A). **Rejeição** grava **`risk_decisions`**; **aceite** grava **`paper_orders`** com **`status = queued_intent`**. |
| Não conta como homologado | **`PAPER_GATEWAY_QUEUE_ONLY`**, fila sem linha no ledger, **`orders_sent = 0`** no JSON do worker — intenção na fila **não** é fill Alpaca. |
| Verificar rejeição (opcional) | Forçar sinal fora de sessão ou estratégia não-paper (ex. `orb` em shadow): `SELECT decision, reason FROM risk_decisions ORDER BY created_at DESC LIMIT 3;` |
| Verificar aceite (opcional) | Sinal `signal_copy` em fase paper com gates OK: `SELECT status, symbol FROM paper_orders ORDER BY created_at DESC LIMIT 3;` — esperar **`queued_intent`**. |
| Smoke pós-deploy (N10) | **`sent_at_utc` deve estar dentro de `ttl_seconds` do relógio real** quando o worker roda (`signal_copy.validate`). Fim de semana: POST HTTP → `OUTSIDE_SESSION`; `ingest(..., now=)` em **dia útil NY** enfileira, mas worker ainda rejeita se `sent_at` estiver no passado → **`EXPIRED_OR_FUTURE_SIGNAL`**. Evidência **4b** válida com: (a) pregão + `sent_at=now` + worker, ou (b) `python3 -m unittest tests.test_paper_gateway_queue.GateBLedgerIntegrationTest.test_persist_uses_queue_stem_when_signal_id_hashed` no container com `LEDGER_DATABASE_URL`. |
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

## Feature 5 — demo paper `signal_copy` (Sprint N12, gate ISS-005)

> **`queued_intent` / `PAPER_GATEWAY_QUEUE_ONLY` ≠ fill.** Este runbook fecha o critério aberto de Feature 5 só com evidência operador redigida em `docs/TEST-EVIDENCE.md` (N12.4). `LIVE_TRADING_ENABLED=false` obrigatório.

### Pré-requisitos

- Itens N9.3–N9.7 já ok (gates, reconcile read-only, kill switch).
- `strategy_states`: `signal_copy` em fase que permite paper (`paper_limited` após seed N8).
- Credenciais **Alpaca Paper** só no EasyPanel (nunca no Git).
- Snapshot de risco consolidado: arquivo JSON apontado por **`V4_RISK_SNAPSHOT_FILE`** (ver `signal_paper_runner.risk_check` — stale >120s bloqueia).

### Caminho A — one-shot (`signal-paper`)

| Passo | Ação |
|-------|------|
| 1 | Montar JSON de sinal assinado (`signal_copy.validate` / `provider_signature` com `SIGNAL_COPY_SECRET`). |
| 2 | Env **preview** (default): sem `PAPER_SIGNAL_AUTO_ENABLED` → stdout `PREVIEW_ONLY`, `orders_sent=0`. |
| 3 | Env **submit** (operador consciente): `PAPER_SIGNAL_AUTO_ENABLED=true`, `PAPER_EXECUTION_ENABLED=true`, `PAPER_SIGNAL_ACCOUNT_ACK=I_AUTHORIZE_ALPACA_PAPER_ONLY`, `PAPER_DAILY_RISK_CONFIRMED=true`, `V4_RISK_SNAPSHOT_FILE=/app/data/risk-snapshot.json` (path real no container). |
| 4 | Comando | `/app/scripts/run.sh signal-paper --signal /app/data/received-signal.json` |
| 5 | Verificar stdout | `PAPER_SUBMITTED`, `orders_sent=1`, `broker_id` redigido na folha de evidência (não colar segredo). |
| 6 | Corretora | Confirmar ordem/posição na UI Alpaca **paper** (contagem/símbolo redigidos). |
| 7 | Reconcile | `PAPER_RECONCILE_LEDGER_APPLY=true` + `/app/scripts/run.sh v4-alpaca-reconcile --output /app/reports/paper/reconcile-post-fill.json` — anotar `ledger_apply` e que **`broker_reconciled` false** continua válido até política de reconcile completo. **One-shot `signal-paper`:** trilha principal em `/app/reports/paper/signal-orders.jsonl`; `ledger_apply.linked=0` é esperado se não houver linha `paper_orders` Postgres para o símbolo. |

### Caminho B — worker pós–Gate B (opcional)

Mesmas flags de submit no env do **`tv-worker`**. Após Gate B aceitar, `paper_gateway_queue.process_after_gate_b` delega a `signal_paper_runner.run` quando `broker_auto_allowed(env)` é true. Journal do worker deve mostrar `orders_sent=1` no caminho submit — distinto de `QUEUED` / `orders_sent=0`.

### O que não conta como Feature 5 fechada

- Só linha `paper_orders.status = queued_intent`.
- HTTP 202 webhook ou journal `QUEUED` sem submit Alpaca.
- Conta paper existente sem trilha documentada nesta folha.
- **Deploy #10 / imagem nova** sem fill documentado na folha N12.

---

## Homolog por família — Feature 4 (Sprint N13)

> Fases vêm de `strategy_catalog.DEFAULT_PHASE_BY_KEY` (seed insert-if-missing). **Não** promover fase por PnL, HTTP 200 ou fila.

| Família | Fase default | O que homologar (operador) | Ordem paper? |
|---------|--------------|----------------------------|--------------|
| `news_first` | research | Scheduler `--once` / manifesto; Gate A audit (`news_first` report) | **Não** |
| `momentum` | research | Confirmar Gate B recusa paper (`STRATEGY_PHASE_BLOCKED`) com `strategy_key=momentum` | **Não** (blocked upstream) |
| `ta_barato` | research | Idem momentum | **Não** (blocked upstream) |
| `prodigy_15d` | research | Idem research; teto R$20 só após regra recuperada | **Não** (blocked upstream) |
| `signal_copy` | paper_limited | N12 § Feature 5 demo; Collective2 permanece reprovado | **Sim** (paper limitado; fill N12.4 pendente) |
| `orb` | shadow | Shadow journal / research; Gate B `STRATEGY_NOT_PAPER` | **Não** (nunca principal) |
| `mean_reversion` | shadow | Idem ORB (shadow) | **Não** |

Evidência redigida: coluna **Status homolog** em `docs/TEST-EVIDENCE.md` § Sprint N13.

---

- HTTP 200 / `PAPER_GATEWAY_QUEUE_ONLY` / fila sem fill real observado.
- Conta paper existente sem trilha ledger + reconcile aplicado.
- ORB ou copy Collective2 como estratégia principal (Feature 4 aberta).

## Critérios parciais cobertos em CI

- Sinal inválido / duplicata / gates A+B: `tests/test_tradingview_webhook*.py`, `tests/test_gate_b_*.py`, `tests/test_paper_gateway_queue.py`.
- Ledger reconcile: `tests/test_ledger_reconcile.py` (com `LEDGER_DATABASE_URL` no job CI).

Fill real na corretora com P&L verificado continua **passo operador** com chaves paper reais.
