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
| Fill real Alpaca + posição coerente | Operador 2026-11-11: Alpaca paper AAPL buy limit @349.85 (2026-10-29) **filled** qty 1 + posição AAPL qty 1 avg 349.85. MSFT/NVDA canceled/expired filled 0 — não contam. | ok | N20.3 / P-001b |
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
| Promoção fase + evolution | `docs/HOMOLOGATION-EVOLUTION-N16.md` | ok | N16.3 |
| `prodigy-rank` → JSON | `tests.test_prodigy_rank` | ok | CI |
| Rank → sinal → preview | Operador (`HOMOLOGATION-PRODIGY` § 1–3) | ok | N16.4 preview + rank 0 candidates |
| Submit paper Prodígio | Operador EasyPanel 2026-11-03 · NVDA · provider **132169961** · `PAPER_SUBMITTED` · `orders_sent=1` · bracket **new**/held Alpaca | ok | N16.4 submit |
| Fill limit Prodígio | Alpaca paper (limit `new` / filled 0) | pendente | P-001b / ISS-005 parcial |
| Painel oportunidades | Command Panel + rank file | ok | PR #14 |
| Painel remoto bearer (N16.8) | EasyPanel `trading-lab` 2026-11-03: `ALLOW_REMOTE=true`, token ≥32, `0.0.0.0:8765`, `/api/status` Bearer **200**, `command-panel-v1` | ok | operador |

```bash
LIVE_TRADING_ENABLED=false PYTHONPATH=src python3 -m unittest tests.test_prodigy_rank -q
```

## Sprint N18 — Command Panel always-on (`v4-ops`)

> Gate: merge **`feat(ops): v4-ops`** · rebuild **`trading-lab`** · log `listening on …:8765` **sem** `nohup` · Bearer `/api/status` **200** · `LIVE_TRADING_ENABLED=false`  
> Runbook: `docs/DASHBOARD-OPERATIONS.md` · Issue **ISS-008**

| Critério / check | Evidência | Status | Resultado |
|------------------|-----------|--------|-----------|
| Layout `v4-ops` + pytest | `tests/test_v4_ops_layout.py`, `tests/test_v4_web_dashboard.py` | ok | N18.1 repo |
| Runbook ops + MVP-DEMO | `docs/DASHBOARD-OPERATIONS.md`, `EASYPANEL.md`, `MVP-DEMO-RUNBOOK.md` | ok | N18.2 repo |
| Deploy imagem CMD `v4-ops` | 2026-11-10 EasyPanel `trading-lab`: histórico de implantação com sucesso, "Deploy service: Merge pull request #20 from ig0rayres/front/n16-8-panel", 40s, cerca de 52 min antes de 10:23 -03. Log `v4-ops: starting read-only dashboard on 0.0.0.0:8765` e `Read-only dashboard listening on 0.0.0.0:8765`; trecho sem `nohup`; ciclos `RESEARCH_ONLY` com `orders_sent` 0 | ok | N18.3 operador |
| `/api/status` com bearer | 2026-11-10 console do container, `GET http://127.0.0.1:8765/api/status` com bearer do ambiente: **200**, schema `command-panel-v1`. Sem token no Git. HTTPS público não foi reconsultado neste registro | ok | N18.3 operador |
| Closeout N16 no ROADMAP | 2026-11-10: N16 `concluida` no índice e na seção; ISS-008 `fechado`. PR #20 já mergeado com checks verdes. Este commit de docs ainda local | ok | N18.4 |

```bash
LIVE_TRADING_ENABLED=false PYTHONPATH=src python3 -m unittest tests.test_v4_ops_layout tests.test_v4_web_dashboard -q
```

## Sprint N20 — Onda 0 (evidência operador + Feature 5 fill)

> Gate: PR **#22** no `main` · `LIVE_TRADING_ENABLED=false` · fill Feature 5 só com qty preenchida ≠ 0

| Critério / check | Evidência | Status | Resultado |
|------------------|-----------|--------|-----------|
| N20.1 Resgate contrato v0.3 + N19.1–N19.2 | PR [#22](https://github.com/ig0rayres/trading_lab/pull/22) merged | ok | N20.1 |
| N20.2 SHA imagem EasyPanel | Digest Docker `trading-lab` `sha256:d3b5528dddc39a930fe1ca35bc2b10521115d4c142dfcb37e7c2c6714bcc81c1` (não é SHA Git); webhook não anotado | parcial | N20.2 |
| N20.5 Postgres ledger | Exec: `ledger-migrate status` → `001_ledger` `applied: True`, `triggers_applied: False` | ok | N20.5 |
| N20.3 Fill paper | AAPL 2026-10-29 buy @349.85 **filled** + posição qty 1. MSFT/NVDA sem fill. Tentativa `n20-fill-001` AAPL → `DUPLICATE_SYMBOL` (esperado) | ok | P-001b |
| N20.4 Feature 5 fill `[x]` | REQUIREMENTS atualizado com evidência AAPL | ok | N20.4 |

## Sprint N13 — Feature 4 homolog por família

> Sprint N13 · `docs/REQUIREMENTS.md` Feature 4 · seed N7/N8 · **sem** limiar inventado · `LIVE_TRADING_ENABLED=false`  
> **ISS-005:** fill Feature 5 `[x]` via AAPL (N20); submits MSFT/NVDA sem fill permanecem só como histórico.

| `strategy_key` | Fase seed (N7) | Homolog repo (pytest / gate) | Homolog operador | Status homolog |
|----------------|----------------|------------------------------|------------------|----------------|
| `news_first` | research | `tests.test_strategy_catalog` + Gate B phase block; `test_news_first_report_audited` (Gate A audit, sem broker) | Research: ciclo/manifesto via scheduler; **sem ordem paper** | repo ok / operador pendente |
| `momentum` | research | `tests.test_gate_b_risk` + `test_seed_and_strategy_key_on_risk_row` (fase research → rejeição paper) | Bloqueado paper até regra upstream recuperada | **blocked upstream** |
| `ta_barato` | research | Idem momentum (fase research) | Bloqueado paper | **blocked upstream** |
| `prodigy_15d` | research | `tests.test_prodigy_rank`, Gate B phase; runbook N16 | Paper submit 2026-11-03 (NVDA) sem fill; fill Feature 5 fechado via AAPL `signal_copy` | submit ok / fill via AAPL |
| `signal_copy` | paper_limited | `tests.test_signal_copy`, `tests.test_signal_paper_runner`, `tests.test_paper_gateway_queue` | Paper: AAPL fill 2026-10-29 + posição; MSFT submit sem fill | **fill ok** |
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

## Sprint N30.3 — Features 8–10 (painel; pytest `test_panel_*` only)

> Sprint N30 · `docs/REQUIREMENTS.md` Features 8–10 · `LIVE_TRADING_ENABLED=false`  
> Gate N30.3: marcar `[x]` no REQUIREMENTS **somente** com nodeid em `tests/test_panel_ops.py` ou `tests/test_panel_triggers.py`. Feature 7 inalterada nesta task.

**Feature 10 (lacuna N30.3):** `performance_from_snapshots` e `performance_from_ledger` (`panel_ops_data`) já retornam `strategies[]` só com fills confirmados; `test_performance_excludes_unfilled_orders` passa a assertar breakdown por `strategy_key` (fills `signal_copy` + `momentum`, ordem open excluída).

| Feature | Critério REQUIREMENTS | Evidência pytest (nodeid) | REQUIREMENTS |
|---------|------------------------|---------------------------|--------------|
| 8 | Parada geral impede ordem nova | `tests.test_panel_ops.PanelKillSwitchCycleTests.test_kill_switch_from_panel_blocks_next_eval` | `[x]` |
| 8 | Dia a dia sem Exec | `tests.test_panel_ops.PanelOpsRunbookTest.test_daily_runbook_points_to_panel_not_exec` | `[x]` |
| 8 | Acesso exige autenticação | `tests.test_panel_ops.PanelOpsHttpTests.test_root_redirects_to_login_without_cookie`, `test_login_sets_cookie_and_opens_central`, `test_api_signals_requires_session`, `test_bearer_alone_still_401_on_patch`; `tests.test_panel_triggers.PanelTriggerHttpTests.test_patch_triggers_bearer_only_is_401` | `[x]` |
| 8 | Alteração registrada com valor anterior + data | `tests.test_panel_triggers.PanelTriggerHttpTests.test_patch_triggers_with_cookie_updates_audit`; `PanelTriggerUnitTests.test_apply_trigger_patch_appends_audit` (`old_value`, `new_value`, `changed_at`) | `[x]` |
| 8 | Plataforma nunca afrouxa âncora sozinha | `tests.test_panel_triggers.PanelTriggerHttpTests.test_loosening_anchor_without_operator_cookie_is_401_and_no_audit`; `PanelTriggerUnitTests.test_platform_never_loosens_anchors_when_db_unavailable` | `[x]` |
| 9 | Lista sinais origem/destino/motivo | `tests.test_panel_ops.PanelOpsDataTests.test_load_panel_signals_exposes_origin_destination_and_reject_reason`; `PanelOpsHttpTests.test_api_signals_json_origin_destination_reject_reason` | `[x]` |
| 9 | Ranking Prodígio + copiados | `tests.test_panel_ops.PanelOpsDataTests.test_snapshot_panel_ops_prodigy_ranking_and_copied_signals`; `test_build_panel_bundle_prodigy_copied_signals_structure` | `[x]` |
| 9 | Barrado com gate e âncora | `tests.test_panel_ops.PanelOpsDataTests.test_blocked_context_exposes_gate_and_anchor` | `[x]` |
| 10 | Resultado por estratégia + total (fill confirmado) | `tests.test_panel_ops.PanelOpsDataTests.test_performance_excludes_unfilled_orders` (`strategies[]` por `strategy_key`; unfilled PnL 99 excluído) | `[x]` |
| 10 | Ordem sem fill fora do resultado | `tests.test_panel_ops.PanelOpsDataTests.test_performance_excludes_unfilled_orders` | `[x]` |
| 10 | Valores brutos rotulados | idem — `pnl_label` gross | `[x]` |

Comando local (escopo N30.3):

```bash
LIVE_TRADING_ENABLED=false PYTHONPATH=src python3 -m unittest tests.test_panel_ops tests.test_panel_triggers -q
```

Git First (N30.0): `docs/.briefs/N30-GIT-FIRST-REUSE.md` · vendor pin/local SHA `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd`.

## Sprint N30.1 — Feature 7 Alpaca US_EQUITY + CRYPTO (pytest only)

> Sprint N30 · `docs/REQUIREMENTS.md` Feature 7 · `LIVE_TRADING_ENABLED=false`  
> Gate N30.4: marcar `[x]` no REQUIREMENTS **somente** com nodeid abaixo ou equivalente N27 no mesmo gate. B3/FOREX permanecem `[ ]` (**ISS-010**).

| Critério / mercado | Evidência pytest (nodeid) | REQUIREMENTS |
|--------------------|---------------------------|--------------|
| US_EQUITY → ordem Alpaca paper | `tests.test_signal_paper_runner.PaperRunnerTests.test_n30_us_equity_demo_on_paper_submitted` | `[x]` |
| CRYPTO candidato de risco honesto + submit | `tests.test_signal_paper_runner.PaperRunnerTests.test_n30_crypto_risk_candidate_uses_signal_market` | `[x]` |
| CRYPTO gateway auto submit | `tests.test_paper_gateway_queue.N30Feature7AlpacaPaperLoopTest.test_n30_gateway_crypto_risk_candidate_market_is_crypto` | `[x]` |
| CRYPTO sem path nomeado barrado | `tests.test_signal_paper_runner.PaperRunnerTests.test_n30_crypto_without_named_path_blocked_no_post` | `[x]` barrado |
| Snapshot risco >120s | `tests.test_signal_paper_runner.PaperRunnerTests.test_n30_stale_v4_portfolio_snapshot_still_blocked` | `[x]` Feature 7 stale |
| Refresh snapshot ops | `tests.test_risk_snapshot_refresh` | `scripts/run.sh risk-snapshot-refresh` |
| Âncoras control_flags (portfolio) | `tests.test_feature7_anchor_ceilings.Feature7PortfolioAnchorTests` | `[x]` + N32 runner abaixo |
| Chave live-looking → host paper | `tests.test_paper_gateway_queue.N27AlpacaOnlyGateBWiringTest.test_n27_5_live_looking_key_keeps_paper_alpaca_host` | `[x]` |
| Reinício laço demo sem 2º POST | `tests.test_paper_restart_no_duplicate.PaperRestartNoDuplicateTest.test_n30_demo_operation_on_restart_no_second_broker_post` | `[x]` |
| B3/FOREX zero POST Alpaca | `tests.test_paper_gateway_queue.N27AlpacaOnlyGateBWiringTest.test_n27_gateway_b3_equity_blocked_no_alpaca_post`; `tests.test_paper_gateway_queue.N27AlpacaOnlyPaperRunnerMarketTest.test_n27_forex_runner_never_posts_alpaca_paper_host` | B3/FOREX `[ ]` ISS-010 |

Comando local (escopo N30.1):

```bash
LIVE_TRADING_ENABLED=false PYTHONPATH=src python3 -m pytest -q \
  tests/test_signal_paper_runner.py tests/test_paper_gateway_queue.py tests/test_paper_restart_no_duplicate.py -k 'n30 or n27_5 or n27_gateway_b3 or n27_forex_runner'
```

**Sprint N32.3 — Feature 7 âncora no `signal_paper_runner` (pytest):** `tests.test_signal_paper_runner.PaperRunnerTests.test_n32_tight_defaults_qty1_aapl_paper_submitted`, `test_n32_lowered_capital_cents_blocks_capital_limit`, `test_n32_lowered_max_risk_per_trade_blocks_trade_risk_limit`, `test_n32_risk_check_tight_cap_not_parallel_10k_usd`, `test_n32_b3_equity_auto_blocked_no_alpaca_post`, `test_n32_forex_auto_blocked_no_alpaca_post` → `docs/REQUIREMENTS.md` Feature 7 âncora `[x]`; B3/FOREX ordem demo permanecem `[ ]` (**ISS-010**).

**Sprint N33 (docs closeout):** PR **#42** na linha principal — merge `d30689bfeb4b009b6297d4bdea8fead233486474` (`2026-11-16T19:49:34Z`); EasyPanel imagem do pedido **#42 no ar** (atestado operador chat 2026-11-16). **Não é fill** — painel no ar ≠ ordem executada na corretora.

**EasyPanel #46 no ar (2026-11-16, atestado operador):** tip `main` `d99b332` (closeout N34 / PR **#46** merge `e83994b3cbd57f211e455e13b614802a0b3a9d93`); inclui wiring N34 (PR **#45**). **Não é fill** e **não** fecha N29.5 — falta credenciar Clear/OANDA no painel.

## Sprint N17 — MVP-OP-1.1 Tá Barato (G-FORM blocked; shadow homolog)

> Sprint N17 · `LIVE_TRADING_ENABLED=false` · vendor pin `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd`  
> **G-FORM:** no `ta_barato` / `momentum` module in `day-trader-skill` at pin — paper integration **blocked**; local `market_opportunities.py` is shadow-only, not upstream formula.

| Task | Entrega | Status |
|------|---------|--------|
| N17.0 Git First | `docs/.briefs/N17-GIT-FIRST-REUSE.md` | ok |
| N17.1 Gate B / research | `UPSTREAM_FORMULA_BLOCKED_KEYS`; reuse `gate_b_strategy_reject` | ok (blocked upstream) |
| N17.2 Operador shadow→paper | — | operador pendente |
| N17.3 Docs matriz | Esta seção + REQUIREMENTS sem limiar novo | ok |
| N17.4 F-003 orb-parity | — | skip |
| N17.5 Painel read-only | `command_panel.ta_barato_shadow` + HTML Command Panel v1 | ok |

| `strategy_key` | G-FORM | Fase | Homolog pytest | Paper |
|----------------|--------|------|----------------|-------|
| `ta_barato` | **BLOCKED** (0 vendor paths) | research | `tests.test_n17_ta_barato` + `tests.test_v4_capabilities` shadow | **não** |
| `momentum` | **BLOCKED** (0 vendor paths) | research | `tests.test_gate_b_risk` phase block | **não** |

```bash
LIVE_TRADING_ENABLED=false PYTHONPATH=src python3 -m unittest \
  tests.test_n17_ta_barato tests.test_strategy_homolog_traceability tests.test_v4_capabilities -q
```

## Sprint N28.1 — Sugestões rotuladas (Feature 11 critério 1)

> `LIVE_TRADING_ENABLED=false` · painel read-only · rank/tips **não** disparam paper sozinhos

| Verificação | Teste / artefato | Status |
|-------------|------------------|--------|
| Superfícies `opportunities` / `ta_barato_shadow` / `continuous_improvement` com `surface_kind=suggestion` | `tests.test_n28_suggestion_labels.N28SuggestionSurfaceTests.test_command_panel_suggestion_surfaces_self_check` | ok |
| Rank sem ticket bloqueia antes de `process_after_gate_b` | `tests.test_n28_suggestion_labels.N28SuggestionSurfaceTests.test_rank_row_without_ticket_blocks_before_paper_gateway` | ok |
| HTML painel expõe rótulo `research_tip` | `tests.test_n28_suggestion_labels.N28SuggestionSurfaceTests.test_dashboard_html_exposes_suggestion_labels` | ok |

```bash
LIVE_TRADING_ENABLED=false PYTHONPATH=src python3 -m unittest tests.test_n28_suggestion_labels -q
```

## Sprint N30.3b — Features 8–9 lacunas (ISS-011 onda 2)

> `LIVE_TRADING_ENABLED=false` · escopo `test_panel_ops` + `test_panel_triggers` · 6 casos novos · **29** testes no par (2026-11-16)

| Lacuna Feature 8–9 | Nodeid |
|--------------------|--------|
| Audit `old_value` + timestamp | `PanelTriggerHttpTests.test_patch_triggers_with_cookie_updates_audit`; `PanelTriggerUnitTests.test_apply_trigger_patch_appends_audit` |
| Sem afrouxar âncora sozinha | `PanelTriggerHttpTests.test_loosening_anchor_without_operator_cookie_is_401_and_no_audit`; `PanelTriggerUnitTests.test_platform_never_loosens_anchors_when_db_unavailable` |
| `/api/signals` origem/destino/motivo | `PanelOpsDataTests.test_load_panel_signals_exposes_origin_destination_and_reject_reason`; `PanelOpsHttpTests.test_api_signals_json_origin_destination_reject_reason` |
| Ranking Prodígio + `copied_signals` | `PanelOpsDataTests.test_snapshot_panel_ops_prodigy_ranking_and_copied_signals`; `test_build_panel_bundle_prodigy_copied_signals_structure` |

Operador: **PR #35 merged**; smoke **MSFT** `PAPER_SUBMITTED` ok; **N27.4** fechado como done (smoke real, fora de pytest).

## Sprint N30.4 — Campanha ISS-011 e pendências operador

> Docs-only · campanha **N30 → N17 → N28 (blocked)** · `news_first` research · `orb`/`mean_reversion` NEVER_PAPER · sem live

| Artefato | Entrega |
|----------|---------|
| `docs/ISSUES.md` `## ISS-011` | Fila de campanha, tabela de estratégias, lista numerada de pendências operador |
| `docs/REQUIREMENTS.md` Feature 7 + G-MKT | `[x]` só US/CRYPTO; B3/FOREX `[ ]` + **ISS-010** |
| `docs/REQUIREMENTS.md` Feature 1 + 4 | `news_first` research; NEVER_PAPER explícito |
| `docs/ROADMAP.md` Sprint N30 | Status **em closeout** (não `concluída` até verifier) |

## Sprint N34 — Clear/OANDA no laço paper (N27.2)

> `LIVE_TRADING_ENABLED=false` · HTTP mock apenas · credenciais operador (N29.5) · **não é fill**

| Closeout | Prova |
|----------|-------|
| Merge produção | PR [**#45**](https://github.com/ig0rayres/trading_lab/pull/45) `3aefd447` (`2026-11-16T22:45:44Z`); `origin/main` tip `7627b45` |
| CI | test / docker-smoke / docker-build **SUCCESS** (merge #45) |
| Stamp sprint | `validation_gate` **APROVADA** — `unittest tests.test_signal_paper_runner tests.test_signal_copy tests.test_demo_broker_adapters -q` (33 testes) |

| Cenário | Nodeid |
|---------|--------|
| B3 sem cred → bloqueio | `tests.test_signal_paper_runner.PaperRunnerTests.test_n32_b3_equity_auto_blocked_no_alpaca_post` |
| FOREX sem cred → bloqueio | `tests.test_signal_paper_runner.PaperRunnerTests.test_n32_forex_auto_blocked_no_alpaca_post` |
| B3 Clear mock submit | `tests.test_signal_paper_runner.PaperRunnerTests.test_n34_b3_clear_mock_submit_no_alpaca_post` |
| FOREX OANDA mock submit | `tests.test_signal_paper_runner.PaperRunnerTests.test_n34_forex_oanda_mock_submit_no_alpaca_post` |
| CLEAR_* faltando | `tests.test_signal_paper_runner.PaperRunnerTests.test_n34_b3_missing_clear_secret_blocks` |
| OANDA token vazio | `tests.test_signal_paper_runner.PaperRunnerTests.test_n34_forex_empty_oanda_token_blocks` |
| Pin abuse B3/FOREX path | `tests.test_signal_paper_runner.PaperRunnerTests.test_n34_pin_b3_alpaca_paper_path_blocked`; `test_n34_pin_forex_clear_path_cross_blocked` |
| LIVE true | `tests.test_signal_paper_runner.PaperRunnerTests.test_n34_live_trading_enabled_blocks_demo_submit` |
| Regressão AAPL Alpaca | `tests.test_signal_paper_runner.PaperRunnerTests.test_n32_tight_defaults_qty1_aapl_paper_submitted` |

```bash
LIVE_TRADING_ENABLED=false PYTHONPATH=src python3 -m unittest tests.test_signal_paper_runner -q
```

## Sprint N35 — Presença das chaves demo (sem valores)

> `LIVE_TRADING_ENABLED=false` · **não** imprime valores · **não** HTTP · **não** fecha N29.5 · EasyPanel **#46 no ar** ≠ creds ok ≠ fill

| Cenário | Nodeid |
|---------|--------|
| Env vazio → chaves ausentes, mercados barrados | `tests.test_demo_broker_adapters.EnvPresenceReportTests.test_n35_empty_env_all_keys_absent_markets_blocked_live_false` |
| Mock completo → present + READY | `tests.test_demo_broker_adapters.EnvPresenceReportTests.test_n35_full_mock_creds_keys_present_markets_ready` |
| Um CLEAR_* faltando | `tests.test_demo_broker_adapters.EnvPresenceReportTests.test_n35_missing_one_clear_key_that_name_absent_b3_blocked` |
| repr/json sem segredos de fixture | `tests.test_demo_broker_adapters.EnvPresenceReportTests.test_n35_report_repr_and_json_contain_no_fixture_secrets` |
| urlopen não chamado | `tests.test_demo_broker_adapters.EnvPresenceReportTests.test_n35_urlopen_raise_report_still_returns_no_http` |
| LIVE=true → flag live_trading_enabled_false | `tests.test_demo_broker_adapters.EnvPresenceReportTests.test_n35_live_trading_true_live_trading_enabled_false_is_false` |

Roteiro operador: `docs/HOMOLOGATION.md` § **G-MKT Clear simulated + OANDA Practice homolog (N35)**.

```bash
LIVE_TRADING_ENABLED=false PYTHONPATH=src python3 -m unittest tests.test_demo_broker_adapters.EnvPresenceReportTests -q
```

## Sprint N37 — platform_health (ISS-014)

> `LIVE_TRADING_ENABLED=false` · merge produção PR **#52** · **pytest verde ≠ rebuild EasyPanel ≠ fill** · sem segredos neste arquivo

| Closeout | Prova |
|----------|-------|
| Merge produção | PR [**#52**](https://github.com/ig0rayres/trading_lab/pull/52) MERGED `2026-11-17T13:14:04Z` |
| Commits | feat `76f76b3` `feat(observability): platform health probes and operational defaults (N37)`; follow-up `ae916c6` `test: isolate demo-off gate checks from N37 migrate defaults` |
| mergeCommit | `3bebe1c7d3236690c67533ef916cbc5be3206d92` |
| Papel ISS-014 | Sprint **N39** closeout docs (ROADMAP/DIARY/ISSUES); não roubar ID N37 |

| Cenário | Nodeid |
|---------|--------|
| Probes gravam snapshot | `tests.test_platform_health.PlatformHealthTests.test_run_probes_writes_snapshot` |
| Webhook sem URL → skipped | `tests.test_platform_health.PlatformHealthTests.test_webhook_skipped_without_url` |
| Stamp worker habilita ok | `tests.test_platform_health.PlatformHealthTests.test_worker_stamp_enables_ok_worker` |
| Fila antiga → degraded | `tests.test_platform_health.PlatformHealthTests.test_stale_queue_degraded` |
| down vence degraded no agregado | `tests.test_platform_health.PlatformHealthTests.test_aggregate_overall_down_beats_degraded` |
| Snapshot API inclui health | `tests.test_platform_health.BuildSnapshotHealthTest.test_build_snapshot_includes_platform_health` |
| Defaults ON migrate (isolamento demo-off) | `tests/test_operational_defaults.py` (cobertura N37.4; ver suite no CI do PR #52) |

```bash
LIVE_TRADING_ENABLED=false PYTHONPATH=src python3 -m unittest tests.test_platform_health tests.test_operational_defaults -q
```

**Operador:** rebuild EasyPanel `trading-lab` necessário para ver o semáforo em produção — fora desta evidência pytest.

## Sprint N44 — Passeio painel US + cripto (ISS-017 onda 4)

> `LIVE_TRADING_ENABLED=false` · **roteiro** `docs/HOMOLOGATION.md` § **Homologar operar US + cripto pelo menu do painel** · **pytest ≠ passeio** · **não** colar tokens, chaves Alpaca nem ids completos  
> O agente **não** preenche estas linhas — só o operador, após rebuild EasyPanel e caminhada real no menu.

| Critério / mercado | Evidência (operador redige) | Status | Resultado |
|--------------------|-----------------------------|--------|-----------|
| N44 passeio **US equity** — Sinais → Ordens → confirmação corretora → Histórico → Performance | *(pendente)* | pendente | — |
| N44 passeio **cripto** — mesmos cinco passos com ativo cripto paper | *(pendente)* | pendente | — |

**Não usar como evidência N44:** fill AAPL 2026-10-29 (§ Sprint N20) sozinho; Feature 7 pytest; HTTP 200; fila sem fill; rebuild sem observação no painel publicado.
