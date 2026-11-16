# Sprint diary — Trading Lab

## Índice

| Sprint | Módulos | Temas | Linhas |
|--------|---------|-------|--------|
| N33 | docs | Closeout ISS-011 Alpaca; carimbo N28/N30/N31; PR #43 main; PR #42/EasyPanel attested | 14–40 |
| N32 | paper-gateway, risk-gate-b | Feature 7 âncoras no laço paper; PR #42; ISS-011 lacuna | 38–63 |
| N24 | v4_web_dashboard, panel_ops | Onda 3 bundle N24–N26; PR #27; MVP-OP-1.3 | 40–69 |
| D1 | baseline, vendor | CI, submodule, EasyPanel 2 apps | 25–41 |
| D2 | ledger | migrations, ledger_store, CI Postgres | 15–21 |

---

## Sprint N33 — Closeout docs ISS-011 (laço americano no papel)

**Frente:** `n27-alpaca-loop`, branch `front/n27-alpaca-loop`. **Escopo:** docs/sessão apenas — zero diff em `src/`.

**Entregue (docs):** `docs/.briefs/N33-GIT-FIRST-REUSE.md` confirmado com SHAs/PRs verificados em `origin/main` + `gh pr view`; ROADMAP N28/N30/N31 → Status `concluida` com notas de closeout; ISS-011 honesto (aberto só **ISS-010** B3/FOREX + **N17.2** G-FORM); ISS-012 corpo `fechado`; REQUIREMENTS changelog linha N28.2–4 `[x]`; esta entrada + TEST-EVIDENCE.

**Prova citada:** PR **#42** merge `d30689b` (`2026-11-16T19:49:34Z`); PR **#39** `5178fff`; PR **#35** `622fbeb`; PR **#38** `681e8c5`. EasyPanel imagem **#42 no ar** — atestado operador 2026-11-16 (**não é fill**).

**Decisões:** N33 Status permanece `planejada` até sprint-finalizer/VERIFY; `LIVE_TRADING_ENABLED=false`; sem adapters Clear/OANDA.

**Finalizer (2026-11-16):** PR [**#43**](https://github.com/ig0rayres/trading_lab/pull/43) merge `fe80f161a314d215ece48b93b66f6e0d3e37593f` (`2026-11-16T20:34:39Z`); stamp local **APROVADA**; CI test / docker-smoke / docker-build SUCCESS. ROADMAP N33 → `concluida`; sessão `sprint_atual=null`, `checkpoint.phase=validated`, `sprint_delivery=finalized`.

**Aprendizados:** closeout em papel exige separar prova de código (PRs #35–#42) do PR de docs (#43); painel no ar ≠ fill.

**Próximo:** `/pmo plan` campanha **ISS-010** (B3/FOREX) e **N17.2** G-FORM (operador); LIVE false.

---

## Sprint N32 — Âncoras do painel no laço paper (Feature 7)

**Frente:** `n27-alpaca-loop`, branch `front/n27-alpaca-loop`.

**Gate:** validação local **APROVADA** (`validation_gate` + `qa_gate`); pytest `test_n32_*` e âncoras portfolio (25 testes na evidência do stamp); `LIVE_TRADING_ENABLED=false`. CI PR [#42](https://github.com/ig0rayres/trading_lab/pull/42): test, docker-smoke, docker-build **SUCCESS**; MERGEABLE (merge reservado ao operador).

**Entregue (código + docs):**

- `signal_paper_runner.risk_check` lê `fetch_control_flags` + `brl_from_cents` (fim do teto paralelo `Decimal('10000')` / 50 USD).
- Testes `tests/test_signal_paper_runner.py` (`test_n32_*`) + reforço âncoras em `test_feature7_anchor_ceilings.py`.
- Contrato: REQUIREMENTS Feature 7 âncora `[x]`; B3/FOREX permanecem `[ ]` (**ISS-010**).
- ROADMAP N32 e campanha **ISS-011** atualizados; blocos N17/N28/N29/N30/N31 não reescritos.

**Decisões:**

- Reuso N22 (`gate_b_risk`, `portfolio_risk_v4`) — sem segundo motor de risco.
- Épico **ISS-011** segue **aberto** (N17, Feature 11/N28, adapters Clear/OANDA).

**Aprendizados:**

- A lacuna de âncora só fechava no caminho paper; Gate B/carteira já liam `control_flags` desde N22.
- Verify green com stamp focal em `n32` evita regressão no ticket qty=1 AAPL conhecido.

**Próximo (operador):** merge PR #42; rebuild EasyPanel; campanha ISS-011 (N30 closeout, N17, adapters ISS-010).

---

## Sprint N24 — Onda 3 (N24 + N25 + N26)

**Bundle:** pacote único **Onda 3** (Features 8–10) — login + Central de controle, tela de sinais com motivo/gate/âncora, performance só de fill confirmado (bruto rotulado). Sprints N25 e N26 fechadas no mesmo merge; frente `n24-panel-ops`, branch `front/n24-panel-ops`.

**Gate:** validação local **APROVADA** — **455** testes pytest; `LIVE_TRADING_ENABLED=false`; vendor pin em `vendor/day-trader-skill`. CI PR [#27](https://github.com/ig0rayres/trading_lab/pull/27): test, docker-smoke, docker-build **SUCCESS**. Merge em `2026-11-11T21:23:04Z`, SHA `fb4a473134f8b6fd6af6cab9bc74c4c3be9701f9`.

**Entregue (código + docs):**

- Login na frente do painel (reuso sessão operador N19.2); Central com âncoras, mercados, estratégias e parada.
- `panel_ops_data` + rotas UI: sinais (origem/destino/motivo), ranking Prodígio, performance por fill + rótulo bruto (`PERFORMANCE_LABEL_GROSS`).
- Testes `tests/test_panel_ops.py` (redirect login, parada no ciclo, runbook sem Exec); integração ledger com `demo_operation_on` após fix CI.
- Runbook dia a dia aponta painel (`docs/DASHBOARD-OPERATIONS.md` / runbook N24.4).

**Falhas / correções:**

- CI pós-merge: `GateBLedgerIntegrationTest` exigia `demo_operation_on` explícito — commit `e545203` no PR.

**Decisões:**

- Um PR para N24+N25+N26 alinha **MVP-OP-1.3** (painel opera) com um único rebuild de imagem.
- HTTP 200, fila e `queued_intent` continuam **sem** contar como fill na performance.
- Plataforma não afrouxa âncora sozinha; kill switch pelo painel segura a próxima avaliação Gate B.

**Aprendizados:**

- Testes HTTP do painel com cookie de sessão localizam regressões de login/Central antes do EasyPanel.
- Bundling Onda 3 reduz drift entre telas que compartilham `build_snapshot` e `panel_ops_data`.

**Próximo:** Sprint **N27** (laço autônomo G-MKT / MVP-OP-1.4); homolog operador MVP-OP-1.3 após rebuild na imagem mergeada.

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
