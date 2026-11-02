# Test evidence — Sprint D1

> Generated: 2026-10-30  
> Sprint: D1 — Baseline verificável  
> `LIVE_TRADING_ENABLED=false`

## Upstream pin

| Item | Value |
|------|--------|
| Submodule | `vendor/day-trader-skill` |
| SHA (documented) | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| Reference | `docs/VENDOR-PIN.md` |

## vendor_verify (offline, real upstream modules)

Command:

```bash
UPSTREAM_DIR="$PWD/vendor/day-trader-skill" LIVE_TRADING_ENABLED=false PYTHONPATH=src \
  python3 src/vendor_verify.py
```

Result (2026-10-30):

- **status:** PASS  
- **source:** ACTUAL_ORIGINAL_MODULES  
- **checks:** first closed-bar entry; scanner/entry parity; 1R/2R target; sizing and risk PASS; invalid plan rejection  
- **live_orders_enabled:** false  

Note: `upstream_commit` in JSON may show `UNVERSIONED_UPSTREAM` on this host if `git -C vendor/...` is blocked by safe-directory; the pin above is authoritative.

## orb-parity (`parity.py`)

Not run in D1: requires v0.5 report artifacts (`watchlist-*.json`, trades CSV, cache under `/app/reports/orb`). Run when those paths exist:

```bash
UPSTREAM_DIR="$PWD/vendor/day-trader-skill" PYTHONPATH=src python3 src/parity.py --date YYYY-MM-DD ...
```

## Pytest full suite

| Run | Status | Notes |
|-----|--------|-------|
| Local (Cursor agent, 2026-10-30) | **Not executed** | Environment policy blocked `pip install` / venv (#385 ask mode). |
| CI (GitHub Actions) | **Success** | [Run 41041762290](https://github.com/ig0rayres/trading_lab/actions/runs/41041762290) — workflow **CI #3** on `main` @ `f597f8b` (2026-10-30, ~41s): jobs **test** (~21s, `pytest -q`) and **docker-build** (~15s) green. |

Commit under test: [`f597f8b`](https://github.com/ig0rayres/trading_lab/commit/f597f8b5bc8437615f68403eea067b20146d34c6) · default branch tree: [`main`](https://github.com/ig0rayres/trading_lab/tree/main)

Expected local command once deps are available:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
UPSTREAM_DIR="$PWD/vendor/day-trader-skill" LIVE_TRADING_ENABLED=false PYTHONPATH=src \
  .venv/bin/python -m pytest -q --tb=line 2>&1 | tee docs/pytest-D1.log
```

Gate D1 pytest/docker: **closed** via CI run above. Re-run locally optional (`docs/pytest-D1.log`).

## Sprint D2 — CI evidence

| Run | Branch | Result |
|-----|--------|--------|
| [41043938920](https://github.com/ig0rayres/trading_lab/actions/runs/41043938920) | `sprint/D2` @ `d68a845` | **Success** (pytest + migration roundtrip + docker-build) |

Merged to `main` after verify (2026-10-30).

## Sprint D3 — Gate A (em progresso)

| Run | Branch | Result |
|-----|--------|--------|
| [41044496969](https://github.com/ig0rayres/trading_lab/actions/runs/41044496969) | `main` @ `146ba5a` | **Success** (D2 merge + Gate A persist) |
| [41052645066](https://github.com/ig0rayres/trading_lab/actions/runs/41052645066) | `sprint/D5` @ `4667086` | **Success** (ledger reconcile + homologation docs) |

## Sprint D1–D5 construction gate

Coverage (no Alpaca on path A): `tests/test_tradingview_webhook.py`, `tests/test_gate_a_signal.py` (ledger rows when `LEDGER_DATABASE_URL` set in CI).

| [41049439799](https://github.com/ig0rayres/trading_lab/actions/runs/41049439799) | `sprint/D3` @ `9431250` | **Success** (Gate A close: HTTP + News First audit) |

## Sprint D4 — Gate B + paper queue

| Run | Branch | Result |
|-----|--------|--------|
| [41046350535](https://github.com/ig0rayres/trading_lab/actions/runs/41046350535) | `sprint/D4` @ `a8d94cb` | **Success** (`gate_b_risk`, `paper_gateway_queue`, full pytest) |

## Sprint D1.3 (Git remote)

| Item | Value |
|------|--------|
| Remote | `https://github.com/ig0rayres/trading_lab.git` |
| Branch pushed | `sprint/D1`, `main` @ `f597f8b` |
| CI run (pytest + docker) | https://github.com/ig0rayres/trading_lab/actions/runs/41041762290 |

## Sprint N6 — Deploy reprodutível (local / CI)

| Check | Command / artifact |
|-------|---------------------|
| Pin drift | `tests/test_image_pin.py::test_dockerfile_pin_matches_vendor_pin_doc` |
| Image smoke | `docker build -t trading-lab:ci . && bash scripts/ci-docker-smoke.sh` |
| CI workflow | `.github/workflows/docker-smoke.yml` (paralelo ao job `docker-build` em `ci.yml`) |

**Nota:** validação local bloqueada neste agente (`local-runtime` ask); evidência pós-push na Action `Docker image smoke`.

| Evidência | Valor |
|-----------|--------|
| PR | https://github.com/ig0rayres/trading_lab/pull/1 (merged 2026-10-30) |
| `main` merge | `6813fb5` (N6); homolog N9 + F-013 → **`0509732`** (2026-11-01) |
| Operador | EasyPanel hashia — N6 no ar (dois apps) |

## Homologação D5 itens 3–7 (Sprint N9 — operador EasyPanel)

> Preencher após executar o runbook em `docs/HOMOLOGATION.md` § Runbook detalhado. **Sem** tokens, DSN, bearer ou chaves Alpaca. Só contagens redigidas e sim/não.

| Item | Checklist | Comando / verificação | Evidência esperada | Status | Resultado (operador) |
|------|-----------|------------------------|-------------------|--------|----------------------|
| 3 | Gate A | `run.sh tv-webhook` + POST válido | ≥1 linha em `signal_events` | ok | 1 linha `accepted` AAPL; `idempotency_key` = digest do sinal (~2026-10-30T19:28Z). HTTP 202 `QUEUED` ≠ fill. |
| 4a | Gate B rejeição | `run.sh tv-worker` | linha em `risk_decisions` (opcional) | ok | Journal `BLOCKED`; worker persiste rejeição via stem da fila (F-013). |
| 4b | Gate B aceite | `run.sh tv-worker` | `paper_orders.status = queued_intent` | ok | Journal `QUEUED`; F-013 em **`main` `0509732`**. Persistência 4b confirmada no EasyPanel via unittest integração (`test_persist_uses_queue_stem_when_signal_id_hashed` OK). Smoke manual com `sent_at` antigo → worker `EXPIRED_OR_FUTURE_SIGNAL` (esperado). |
| 5 | Reconcile | `v4-alpaca-reconcile` + `PAPER_RECONCILE_LEDGER_APPLY=true` | JSON com `ledger_apply`; `broker_reconciled` false | ok | `reconcile.json`: `ledger_apply` presente; `broker_reconciled` false; stdout `BLOCKED_INCOMPLETE`, `orders_sent` 0. |
| 6 | Dashboard | `run.sh v4-dashboard` + `/api/status` | `kill_switch_on`, `shadow_vs_paper`; auth se remoto | ok | Loopback 127.0.0.1:8765; Bearer auth; HTTP 200; campos `kill_switch_on`, `shadow_vs_paper` presentes (~2026-11-01). |
| 7 | Kill switch | `TRADING_LAB_KILL_SWITCH` ou `control_flags` | worker bloqueia; sem nova ordem | ok | Switch `true` → fila + `tv-worker` → journal `BLOCKED` / `KILL_SWITCH`; `orders_sent` 0. Fim de semana: enfileirar via `ingest(..., now=)` em sessão NY (POST HTTP 422 `OUTSIDE_SESSION`). Switch reposto `false`. |

**N9.6 operador:** colar resultados redigidos na coluna “Resultado” e mudar **Status** para `ok` quando conferido. Agente/repo não executa SSH nem lê secrets.

## Sprint N9 — repo (runbook docs)

| Task | Artefato | Notas |
|------|----------|--------|
| N9.1–N9.4 | `docs/HOMOLOGATION.md` runbook § itens 3–7 | Sem diff em `src/` |
| N9.5 | esta seção + bloco Feature 5 opcional em HOMOLOGATION | Feature 5 fill permanece `[ ]` em REQUIREMENTS |

## Sprint N10 — closeout N9 (docs)

| Task | Evidência |
|------|-----------|
| N10 | ROADMAP N9 `concluida`; notas smoke §4 HOMOLOGATION; `main` `0509732` nesta folha |

## Sprint N11 — Feature 1 ciclo research (pytest traceability)

> Sprint N11 · ISS-004 · `docs/REQUIREMENTS.md` Feature 1 · `LIVE_TRADING_ENABLED=false`

| Critério REQUIREMENTS | Evidência pytest (nodeid) | Notas |
|------------------------|---------------------------|--------|
| Live desligado: ciclo termina **sem ordem** | `tests.test_v4_scheduler.SchedulerTests.test_readonly_success` | `run_cycle` → `orders_sent` 0, sem `paper-gateway` no comando |
| Live desligado: ciclo termina **sem ordem** | `tests.test_v4_scheduler.SchedulerTests.test_live_guard` | `BLOCKED_LIVE_FLAG`, exit 2 |
| Live desligado: ciclo termina **sem ordem** | `tests.test_v4_run_once.TestOnce.test_full_readonly_path` | manifest `orders_sent` 0, `execution_authorized` false |
| Ciclo falho não deixa manifesto antigo confiável | `tests.test_v4_scheduler.SchedulerTests.test_failed_cycle_invalidates_previous_manifest` | `invalidate_stale_manifest` remove arquivo |
| Ciclo falho não deixa manifesto antigo confiável | `tests.test_v4_scheduler.SchedulerTests.test_main_once_failure_clears_stale_manifest` | `main --once` wiring + status JSON |
| Dashboard não promove manifesto adulterado | `tests.test_v4_report_integrity.test_dashboard_never_promotes_tampered_manifest_to_visible_success` | integridade manifesto |
| Status scheduler não autoriza execução | `tests.test_v4_scheduler.SchedulerTests.test_lock_and_status` | `execution_authorized` false |

Comando local (com deps):

```bash
LIVE_TRADING_ENABLED=false PYTHONPATH=src python3 -m pytest tests/test_v4_scheduler.py tests/test_v4_run_once.py tests/test_v4_report_integrity.py -q
```

## Sprint N12 — Feature 5 demo paper (`signal_copy`)

> Sprint N12 · ISS-005 **parcial** · operador submit **2026-11-02** · fill limit **pendente** · `LIVE_TRADING_ENABLED=false`

| Critério / check | Evidência pytest (nodeid) ou operador | Status | Resultado |
|------------------|----------------------------------------|--------|-----------|
| Preview não chama broker | `tests.test_signal_paper_runner.PaperRunnerTests.test_preview_does_not_call_broker` | ok | CI |
| Assinatura inválida bloqueia | `tests.test_signal_paper_runner.PaperRunnerTests.test_bad_signature_blocked` | ok | CI |
| Auto exige ack explícito | `tests.test_signal_paper_runner.PaperRunnerTests.test_auto_mode_requires_attestation` | ok | CI |
| Submit mock → `PAPER_SUBMITTED`, `orders_sent=1` | `tests.test_signal_paper_runner.PaperRunnerTests.test_auto_submit_success_orders_sent_one` | ok | CI |
| Fila sem auto → `QUEUED`, `orders_sent=0` | `tests.test_paper_gateway_queue.PaperGatewayQueueTest.test_queue_never_calls_broker` | ok | CI |
| Auto flags → delega a `paper_run` | `tests.test_paper_gateway_queue.PaperGatewayQueueTest.test_auto_allowed_delegates_to_paper_run` | ok | CI |
| Submit real Alpaca (`signal-paper`) | Operador EasyPanel 2026-11-02: `PAPER_SUBMITTED`, `orders_sent=1`, jsonl `SUBMITTED`, ordem MSFT limit **new** | ok | EasyPanel |
| Fill real Alpaca + posição coerente | Operador — ordem aberta limit @420, filled qty 0 (2026-11-02) | pendente | P-001b |
| Reconcile pós-submit | `v4-alpaca-reconcile`; `ledger_apply` linked 0 (one-shot jsonl; FILL AAPL histórico no bundle) | ok | parcial |

Comando local (repo tasks N12.1–N12.3):

```bash
LIVE_TRADING_ENABLED=false PYTHONPATH=src python3 -m pytest \
  tests/test_signal_paper_runner.py \
  tests/test_paper_gateway_queue.py -q
```

**N12.5:** marcar Feature 5 fill `[x]` em REQUIREMENTS **somente** após linha **Fill real** ok (P-001b). Submit operador registrado acima (opção A MVP-OP-0.9).

## Sprint N16 — Prodígio paper (`prodigy_15d`, MVP-OP-1.0)

> Sprint N16 · `docs/HOMOLOGATION-PRODIGY.md` · rank research-only · `LIVE_TRADING_ENABLED=false`

| Critério / check | Evidência | Status | Resultado |
|------------------|-----------|--------|-----------|
| Git First inventory | `docs/.briefs/N16-GIT-FIRST-REUSE.md` | ok | N16.0 |
| Runbook operador | `docs/HOMOLOGATION-PRODIGY.md` | ok | N16.1 |
| `prodigy-rank` → JSON | `tests.test_prodigy_rank` | ok | CI |
| Rank → sinal → preview | Operador (`HOMOLOGATION-PRODIGY` § 1–3) | pendente | N16.4 |
| Submit / fill paper Prodígio | Operador + Alpaca paper | pendente | N16.4 |
| Painel oportunidades | Command Panel + rank file | ok | PR #14 |

```bash
LIVE_TRADING_ENABLED=false PYTHONPATH=src python3 -m unittest tests.test_prodigy_rank -q
```

## Sprint N13 — Feature 4 homolog por família

> Sprint N13 · `docs/REQUIREMENTS.md` Feature 4 · seed N7/N8 · **sem** limiar inventado · `LIVE_TRADING_ENABLED=false`  
> **ISS-005 parcial:** submit paper ok; fill Feature 5 ainda `[ ]`.

| `strategy_key` | Fase seed (N7) | Homolog repo (pytest / gate) | Homolog operador | Status homolog |
|----------------|----------------|------------------------------|------------------|----------------|
| `news_first` | research | `tests.test_strategy_catalog` + Gate B phase block; `test_news_first_report_audited` (Gate A audit, sem broker) | Research: ciclo/manifesto via scheduler; **sem ordem paper** | repo ok / operador pendente |
| `momentum` | research | `tests.test_gate_b_risk` + `test_seed_and_strategy_key_on_risk_row` (fase research → rejeição paper) | Bloqueado paper até regra upstream recuperada | **blocked upstream** |
| `ta_barato` | research | Idem momentum (fase research) | Bloqueado paper | **blocked upstream** |
| `prodigy_15d` | research | `tests.test_prodigy_rank`, Gate B phase; runbook N16 | Paper: **`HOMOLOGATION-PRODIGY.md`** após promoção fase | runbook ok / operador pendente |
| `signal_copy` | paper_limited | `tests.test_signal_copy`, `tests.test_signal_paper_runner`, `tests.test_paper_gateway_queue` | Paper: submit homologado 2026-11-02; fill limit **pendente** | submit ok / fill pendente |
| `orb` | shadow | `tests.test_strategy_catalog.test_orb_never_paper_even_if_phase_paper`; `tests.test_gate_b_risk.test_orb_not_paper` | Shadow only — **nunca** paper principal | repo ok |
| `mean_reversion` | shadow | `NEVER_PAPER_KEYS` + fase shadow (catálogo) | Shadow only | repo ok |

Comando traceability (N13.4):

```bash
LIVE_TRADING_ENABLED=false PYTHONPATH=src python3 -m unittest tests.test_strategy_homolog_traceability -v
```

Comando Gate B / catálogo (regressão):

```bash
LIVE_TRADING_ENABLED=false PYTHONPATH=src python3 -m unittest \
  tests.test_strategy_catalog tests.test_gate_b_risk -v
```
