# Sprint diary — Trading Lab

## Índice

| Sprint | Módulos | Temas | Linhas |
|--------|---------|-------|--------|
| N54 | v4_web_dashboard, panel_ops_html, tests, docs | POST live_criteria; GET disk_reread; ISS-024; EXECUTE frente | 33–41 |
| N53 | panel_ops_html, v4_web_dashboard, docs | PanelShell v2 todas rotas; Atualizar candidatos + GET reload; ISS-023; N54=POST job | 42–50 |
| N52 | panel_ops_html, docs/design | Cockpit Sinais UX; métricas pesquisa completas; ISS-022; «finalizado» só pós-merge | 42–50 |
| N51 | panel_ops, ledger_migrate, docs | Pré-aprovação painel; migration 003; métricas pesquisa; ISS-021 aberto | 18–26 |
| N50 | panel_ops, docs | C2 lista nomeada; Sinais reordenado; provider_id Prodígio; ISS-020 aberto | 18–24 |
| N49 | panel_ops, docs | Proveniência ordem↔sinal; inventário fill-only; critérios Feature 4/9/10; pool Prodígio pesquisa; ISS-019 aberto | 26–34 |
| N48 | panel_ops, docs | Sinais = cópia de terceiros + auditoria; ISS-018; Collective2 fechado; família bruta | 28–36 |
| N44 | docs | Roteiro homologação US+cripto pelo menu; ISS-017 onda 4; evidência pendente operador | 40–46 |
| N43 | panel_ops, docs | Análise Google no menu; TimesFM research-only; ISS-017 onda 3; fail-closed | 26–34 |
| N42 | panel_ops, docs | Estratégias no menu; catálogo fases; ISS-017 onda 2; sem promoção na UI | 36–46 |
| N41 | panel_ops, docs | Ordens + Histórico no menu; ISS-017 onda 1; campanha CAMPAIGN-PLATFORM-DELIVERY | 48–58 |
| N40 | docs | Mapa OPERATOR-PANEL-MAP; duas superfícies 8765; ordens UI OUT; ISS-016 mapa existe | 34–44 |
| N39 | docs | Closeout papel N37/ISS-014; prova PR #52; rebuild/N29.5/N17.2 operador | 34–45 |
| N38 | panel_ops_html, platform_health | Faixa do freio (um CTA por estado) + bloco saúde na Central; kill_switch_on inalterado | 32–45 |
| N37 | platform_health, operational_defaults, observability | Saúde automática: probes, semáforo Central, defaults ON; PR #52 | 47–62 |
| N37-colisão | panel_ops_html, docs | *(colisão ID)* freio visual planeado aqui → N38 | 64–68 |
| N36 | panel_ops_html, docs | Copy freio na Central; kill_switch_on inalterado; sem botão Live | 40–51 |
| N35 | demo_account_gate, docs | env_presence_report + homolog roteiro; N29.5 ainda `[ ]` | 54–67 |
| N34 | signal_paper_runner | N27.2 wiring Clear/OANDA fail-closed; PR #45 main; N29.5 pendente | 68–89 |
| N33 | docs | Closeout ISS-011 Alpaca; carimbo N28/N30/N31; PR #43 main; PR #42/EasyPanel attested | 29–55 |
| N32 | paper-gateway, risk-gate-b | Feature 7 âncoras no laço paper; PR #42; ISS-011 lacuna | 38–63 |
| N24 | v4_web_dashboard, panel_ops | Onda 3 bundle N24–N26; PR #27; MVP-OP-1.3 | 40–69 |
| D1 | baseline, vendor | CI, submodule, EasyPanel 2 apps | 25–41 |
| D2 | ledger | migrations, ledger_store, CI Postgres | 15–21 |

---

## Sprint N54 — Critérios ao vivo em Sinais (ISS-024)

**Frente:** `sinais-live-criteria`, branch `front/sinais-live-criteria`. **Estado:** implementação em **EXECUTE** (código + testes na frente; merge pendente).

**Entregue na frente (N54.0–N54.3):** inventário Git First confirmado; `POST /api/signals/candidates/refresh` (`mode: live_criteria`, cooldown, fail-closed sem chave C2); CTA **Atualizar candidatos** no POST com hint Feature 4 / Prodígio 15d; `GET /api/signals/reload` declara `mode: disk_reread`; suíte `N54LiveCriteriaRefreshHttpTests` em `tests/test_panel_ops.py`.

**Entregue (N54.4 docs):** mapa operador §2, notas ISS-024/023, aceite Feature 9 com nodeids pytest, ROADMAP N54.0–N54.4 marcados na frente, este diário — sprint **ainda em EXECUTE** até merge e homologação operador.

**Honestidade:** atualizar **≠** aprovar **≠** fill; `orders_sent=0`; chave C2 só no servidor; LIVE false; **ISS-024** e **ISS-023** **permanecem abertos** até merge, CI e homologação operador — agente **não** declarou rebuild EasyPanel nem painel no ar.

---

## Sprint N53 — Plataforma visual ISS-023 + refresh honesto

**Frente:** `n27-alpaca-loop`, branch `front/n27-alpaca-loop`.

**Entregue (N53.1–N53.3):** tokens DESIGN.md v2 em `_PANEL_CSS`; PanelShell (topbar Paper, sidebar escura) em login + Central, Ordens, Histórico, Sinais, Estratégias, Prodígio, Performance, Análise Google; botão **Atualizar candidatos** na pré-aprovação; `GET /api/signals/reload` relê `build_panel_bundle` no disco — sem `prodigy_rank.calculate`, sem chave C2 no browser.

**Entregue (N53.4):** `tests/test_panel_ops.py` verde (81 OK no closeout); hierarquia N52 Sinais preservada; reload não autenticado → 401.

**Entregue (N53.5 docs):** mapa, `DASHBOARD-OPERATIONS`, `api-spec.yaml`, `docs/design/README.md`; **ISS-023** anotado — **permanece aberto** (job POST + critérios ao vivo = **N54** / **ISS-024**).

**Adiado:** POST/job refresh, cooldown R4, aplicação de critérios TradingView + Collective2 server-side (**N54**).

**Honestidade:** refresh GET **não** aprova, **não** envia ordem, **não** inventa score nem fill; métricas de pesquisa continuam do bundle em disco; **rebuild EasyPanel operador** — agente não declarou deploy no ar; **ISS-007** / **ISS-016** / **ISS-017** / **ISS-019–022** não fechados sem evidência operador; N45–N47 intactos; `LIVE_TRADING_ENABLED=false`.

**Closeout:** feat em `main` via PR **#71** (`bb103558`, 2026-11-18); `validation_gate` + QA **APROVADA**; `sprint-finalize` mecânico aplicado pelo orquestrador.

---

## Sprint N52 — Cockpit Sinais UX (ISS-022)

**Frente:** `n27-alpaca-loop`. Design em `docs/design/`. HTML: hierarquia decisão → operação → auditoria; bloco de métricas de pesquisa na pré-aprovação; tokens Lab Ops. Pytest `test_panel_ops` 75 OK. «Finalizado» só após merge em `main`.

---

## Sprint N51 — Pré-aprovação no painel (ISS-021)

**Frente:** `n27-alpaca-loop`, branch `front/n27-alpaca-loop`.

Fila autenticada em `/sinais` com métricas de pesquisa reutilizadas; `POST /api/signals/providers`; migration `003` `signal_provider_approvals`; semente N50 só sem linha no livro-razão; rejeição vence semente. ISS-021 aberto até operador aplicar migration e rebuild no ar.

---

## Sprint N50 — Collective2 lista nomeada + Sinais sem salada (ISS-020)

**Frente:** `n27-alpaca-loop`, branch `front/n27-alpaca-loop`.

**Entregue (N50.1–N50.4):** `REQUIREMENTS` v0.5; `config/c2_paper_copy_allowlist.json` (vazia); `copy.collective2` com lista nomeada + snapshot não-ticket; `/sinais` reordenado; `provider_id` no pool Prodígio; `tests/test_panel_ops.py` (**60 passed**).

**Entregue (N50.5 docs):** mapa §2, `DASHBOARD-OPERATIONS`, `ISSUES` (ISS-020 **aberto** até lista/rebuild operador), `DIARY`.

**Honestidade:** H10 dez candidatos **não** aprovados em lote; painel sem API/chave C2; LIVE false; ISS-007/017/019 abertos; rebuild EasyPanel operador.

---

## Sprint N49 — Proveniência, inventário e critérios na tela Sinais (ISS-019)

**Frente:** `n27-alpaca-loop`, branch `front/n27-alpaca-loop`.

**Entregue (N49.1–N49.4):** JOIN ledger `signal_events` + overlay `paper/signal-orders.jsonl`; `copy.inventory` / `adoption` / `prodigy_pool`; `/sinais` com Origem/Sinal, inventário, critérios Feature 4/9/10, pool Prodígio (`research_tip`); testes `tests/test_panel_ops.py` (55 passed).

**Entregue (N49.5 docs):** `docs/OPERATOR-PANEL-MAP.md` §2; `docs/DASHBOARD-OPERATIONS.md`; `docs/ISSUES.md` (**ISS-019** anotado; **permanece aberto** até rebuild + confirmação operador); `docs/DIARY.md`.

**Honestidade:** vínculo ausente → `origem desconhecida` / `sem vínculo com sinal`; performance por sinal só com fill confirmado; sem `prodigy_rank.calculate`; Collective2 fechado; **rebuild EasyPanel operador**; ISS-007/017/010/011 abertos; N45–N47 intactos; `LIVE_TRADING_ENABLED=false`.

---

## Sprint N48 — Sinais = cópia de terceiros + auditoria (ISS-018)

**Frente:** `n27-alpaca-loop`, branch `front/n27-alpaca-loop`.

**Entregue (N48.1–N48.3):** pacote `copy` em `build_panel_bundle`; mesma rota `GET /sinais` com seções **Cópia de terceiros** e **Auditoria de ingresso**; `GET /api/signals` estendido; testes `tests/test_panel_ops.py` (vazios e Collective2 fechado).

**Entregue (N48.4 docs):** `docs/OPERATOR-PANEL-MAP.md` §2 (duas seções, strings reais); `docs/DASHBOARD-OPERATIONS.md`; `docs/ISSUES.md` (**ISS-018** anotado; **permanece aberto** até confirmação do operador); `docs/ROADMAP.md` e sessão tickados.

**Honestidade:** totais **brutos** por família `signal_copy` — **sem** P&L por sinal/provedor; ingresso ≠ fill; painel **sem** POST de ordem; Collective2 fechado; **rebuild EasyPanel operador** — agente **não** declarou deploy no ar; **ISS-007** / **ISS-017** / **ISS-010** / **ISS-011** não fechados; N45–N47 stubs intactos; `LIVE_TRADING_ENABLED=false`.

---

## Sprint N44 — Roteiro homologação US + cripto pelo painel (ISS-017 onda 4)

**Frente:** `n27-alpaca-loop`, branch `front/n27-alpaca-loop`.

**Entregue (docs):** roteiro em `docs/HOMOLOGATION.md` § Sprint N44; folha com linhas **pendentes** em `docs/TEST-EVIDENCE.md` § Sprint N44; `docs/.briefs/N44-GIT-FIRST-REUSE.md` (pin re-chequeado, sem bump); ponteiros em `docs/DASHBOARD-OPERATIONS.md` e `docs/OPERATOR-PANEL-MAP.md`; `docs/ISSUES.md` (ISS-017 anotado; **permanece aberto**).

**Honestidade:** sprint **somente documentação** — **zero** `src/`; **passeio operador não feito** pelo agente; rebuild EasyPanel e observação na corretora paper continuam **operador**; pytest / HTTP 200 / fila / fill AAPL 2026-10-29 **não** fecham onda 4 nem campanha; **ISS-007** / **ISS-010** / **ISS-011** não fechados; `LIVE_TRADING_ENABLED=false`. PR **#64** foi closeout **N43**, não evidência de passeio N44.

---

## Sprint N43 — Análise Google no menu (ISS-017 onda 3)

**Frente:** `n27-alpaca-loop`, branch `front/n27-alpaca-loop`.

**Entregue:** bloco `timesfm` em `build_panel_bundle`; menu com **Análise Google** (`GET /analise-google`); API `GET /api/analise-google`; testes `tests/test_panel_ops.py`; mapa (`docs/OPERATOR-PANEL-MAP.md` área 9), `docs/DASHBOARD-OPERATIONS.md`, `docs/ISSUES.md` (ISS-017 anotado; **permanece aberto**).

**Honestidade:** painel só leitura — **sem** POST de ordem; dica de pesquisa **não** autoriza ordem; vazio `Análise Google indisponível: modelo ou dependência ausente.` quando o modelo ou dependência falta; melhoria contínua continua no Command Panel v1; B3/Clear/OANDA fora; rebuild EasyPanel operador; **ISS-007** / **ISS-010** / **ISS-011** / **ISS-016** não fechados; `LIVE_TRADING_ENABLED=false`.


**Closeout:** feat em main via PR **#63** (`8bbb6ad`); sessão finalized; rebuild EasyPanel ainda na mão do operador.
---

## Sprint N42 — Estratégias e fases no menu (ISS-017 onda 2)

**Frente:** `n27-alpaca-loop`, branch `front/n27-alpaca-loop`.

**Entregue:** `strategy_catalog` em `build_panel_bundle`; menu com **Estratégias** (`GET /estrategias`); API `GET /api/estrategias`; testes `tests/test_panel_ops.py`; mapa (`docs/OPERATOR-PANEL-MAP.md` área 3), `docs/DASHBOARD-OPERATIONS.md`, `docs/ISSUES.md` (ISS-017 anotado; **permanece aberto**).

**Honestidade:** painel só leitura — **sem** POST de ordem; **sem** promoção de fase na tela nova; vazio `Catálogo indisponível (ledger)` quando o ledger falta; melhoria contínua continua só no Command Panel v1; B3/Clear/OANDA fora; rebuild EasyPanel operador; **ISS-007** / **ISS-010** / **ISS-011** / **ISS-016** não fechados; `LIVE_TRADING_ENABLED=false`.

**Closeout:** feat em main via PR **#61** (`70cf0f2`); sessão `verify_green` → `finalized`; rebuild EasyPanel ainda na mão do operador.

---

## Sprint N41 — Ordens e Histórico no menu (ISS-017 onda 1)

**Frente:** `n27-alpaca-loop`, branch `front/n27-alpaca-loop`.

**Entregue:** listas `open_orders` e `order_history` em `build_panel_bundle`; menu com **Ordens** (`GET /ordens`) e **Histórico** (`GET /historico`); APIs `GET /api/orders` e `GET /api/history`; testes `tests/test_panel_ops.py`; mapa (`docs/OPERATOR-PANEL-MAP.md` áreas 5–6), `docs/DASHBOARD-OPERATIONS.md`, `docs/ISSUES.md` (ISS-017 anotado; **permanece aberto**). Folha da campanha: `docs/.briefs/CAMPAIGN-PLATFORM-DELIVERY.brief.md`.

**Honestidade:** painel só leitura — **sem** POST de ordem; fila / HTTP 200 ≠ fill; histórico = fills confirmados; B3/Clear/OANDA fora; rebuild EasyPanel operador; **ISS-007** / **ISS-010** / **ISS-011** / **ISS-016** não fechados; `LIVE_TRADING_ENABLED=false`.

---

## Sprint N40 — Mapa honesto «onde está cada coisa» (ISS-016)

**Frente:** `n27-alpaca-loop`, branch `front/n27-alpaca-loop`.

**Entregue:** `docs/OPERATOR-PANEL-MAP.md` (nove áreas, selos VISÍVEL / VAZIO-COMUM / NÃO-EXISTE-AINDA / SÓ-API-OU-JSONL); confirmação Git First em `docs/.briefs/N40-GIT-FIRST-REUSE.md` (pin `3d0f4ef`, sem bump); ligação em `docs/DASHBOARD-OPERATIONS.md`; **ISS-016** anotado com caminho do mapa (**permanece aberto**); sessão e ROADMAP tickados. Zero `src/`.

**Honestidade:** menu pós-login ≠ Command Panel v1 em `/` quando `DASHBOARD_OPERATOR_SESSION` está ligado; ordens abertas e histórico **sem** tela dedicada; **ISS-007** / **ISS-011** / **ISS-010** / **ISS-013** não fechados; rebuild EasyPanel, N29.5 e N17.2 continuam operador; `LIVE_TRADING_ENABLED=false`.

---

## Sprint N39 — Closeout docs saúde automática (ISS-014)

**Frente:** `n27-alpaca-loop`, branch `front/n27-alpaca-loop`.

**Entregue:** apenas documentos e sessão — ROADMAP N37 `concluida` com prova PR **#52**; **ISS-014** fechado; `docs/TEST-EVIDENCE.md` com nodeids N37; inventário `docs/.briefs/N39-GIT-FIRST-REUSE.md` (N39.0). Zero alteração em `src/`.

**Honestidade:** código N37 já estava em `origin/main` antes desta sprint; carimbo no papel **não** substitui rebuild EasyPanel `trading-lab`; credenciais demo (**N29.5**) e homologação Tá Barato (**N17.2** / G-FORM) continuam operador; semáforo no ar ≠ ordem executada; `LIVE_TRADING_ENABLED=false`.

**Prova citada:** mesma de N37 — PR [**#52**](https://github.com/ig0rayres/trading_lab/pull/52) MERGED `2026-11-17T13:14:04Z`; feat `76f76b3`; follow-up `ae916c6`.

---

## Sprint N38 — Faixa do freio na Central (estado visual)

**Frente:** `n27-alpaca-loop`, branch `front/n27-alpaca-loop`.

**Contexto:** colisão de ID — `main` já tinha **N37/ISS-014** (saúde da plataforma); o freio visual foi renumerado para **N38/ISS-015** no merge. Integrou `_platform_health_block` (origem N37 main) com a faixa do freio em `render_central_page`.

**Entregue:** faixa-luz `brake-strip--active` / `brake-strip--released`; um único CTA por estado (nunca os dois botões iguais); linha muted `Conta demo · Live desligado`; testes em `tests/test_panel_ops.py` e `tests/test_platform_health.py`; folha `docs/DASHBOARD-OPERATIONS.md`.

**Honestidade:** só apresentação — `kill_switch_on=true` ainda bloqueia ordens demo novas; `kill_switch_on=false` só limpa o gatilho do freio (não liga `demo_operation_on`); Liberar oculto quando já liberado (no-op por desenho); semântica kill switch inalterada; sem botão Live; N29.5 operador; `LIVE_TRADING_ENABLED=false`.

**Decisões:** não fechar **ISS-013** (copy N36) neste closeout — permanece histórico/aberto no índice; **ISS-015** fecha aqui.

**Prova:** PR [**#54**](https://github.com/ig0rayres/trading_lab/pull/54) **MERGED**; CI test / docker-smoke / docker-build verde; local `tests.test_panel_ops` + `tests.test_platform_health` **24 OK**; stamp **APROVADA** / verify_green.

---

## Sprint N37 — Saúde automática da plataforma (ISS-014)

**Frente:** código mergeado na linha principal (`front/n20-platform-health` → PR **#52**); closeout de papel em N39.

**Entregue:** probes em `src/platform_health.py` (`run_probes`, snapshot JSON sem segredos); loop no supervisor `v4_ops_main.sh`; bloco semáforo na Central (`_platform_health_block`); `platform_health` em `/api/status`; defaults operacionais ON no migrate (`operational_defaults`) sem sobrescrever OFF gravado pelo operador.

**Honestidade:** rotina diária pode usar a Central em vez de checklist EasyPanel; rebuild do painel em produção ainda é passo operador; fila antiga / worker parado aparecem como degraded/down nos testes — não são fill; B3/FOREX continuam `NO_DEMO_ACCOUNT_PATH` sem credenciais (**ISS-010**); `LIVE_TRADING_ENABLED=false`.

**Prova:** PR [**#52**](https://github.com/ig0rayres/trading_lab/pull/52) MERGED `2026-11-17T13:14:04Z`; commits `76f76b3`, `ae916c6`; mergeCommit `3bebe1c7d3236690c67533ef916cbc5be3206d92`; pytest `tests.test_platform_health`, `tests/test_operational_defaults.py` (ver `docs/TEST-EVIDENCE.md`).

---

## Sprint N37 — Colisão de ID (freio → N38)

**Nota:** o plano original nomeava esta sprint para a faixa do freio; antes do merge, `origin/main` assumiu **N37** para saúde (**ISS-014**). A entrega visual do freio foi renumerada para **N38** (ver seção acima).

---

## Sprint N36 — Copy do freio na Central

**Frente:** `n27-alpaca-loop`, branch `front/n27-alpaca-loop`.

**Entregue:** rótulos «freio de emergência» na Central (`render_central_page`); botões **Ativar freio** / **Liberar freio**; PATCH `{kill_switch_on}` inalterado; testes de string em `tests/test_panel_ops.py`; folha `docs/DASHBOARD-OPERATIONS.md`.

**Honestidade:** só copy — `kill_switch_on=true` ainda bloqueia ordens demo novas; `kill_switch_on=false` só limpa o gatilho do freio (não liga `demo_operation_on`); sem botão Live; N29.5 operador; ROADMAP N36 Status **planejada** até PR; `LIVE_TRADING_ENABLED=false`.

**Prova:** `tests.test_panel_ops.RenderCentralPageFreioCopyTests` + login HTTP assert «Ativar freio».

---

## Sprint N35 — Presença das chaves demo (sem valores)

**Frente:** `n27-alpaca-loop`, branch `front/n27-alpaca-loop`.

**Entregue:** `env_presence_report()` em `src/demo_account_gate.py` (nomes `present`/`absent`, mercados `READY`/`NO_DEMO_ACCOUNT_PATH`, sem valores/HTTP); roteiro `docs/HOMOLOGATION.md` § G-MKT; ponte `EASYPANEL.md`; nomes vazios em `.env.example`.

**Honestidade:** N29 Status **planejada**; N29.5 **não** marcada; ISS-010 **aberto**; EasyPanel **#46 no ar** ≠ creds ok ≠ fill; `LIVE_TRADING_ENABLED=false`.

**Prova:** nodeids `tests.test_demo_broker_adapters.EnvPresenceReportTests.test_n35_*` (ver `docs/TEST-EVIDENCE.md`).

**Próximo:** operador cola chaves no painel → presença `READY` → homolog ordem demo (roteiro N35) → chat «creds ok» para N29.5.

---

## Sprint N34 — Ligar B3/FOREX no laço paper (N27.2)

**Frente:** `n27-alpaca-loop`, branch `front/n27-alpaca-loop`.

**Entregue:** `signal_paper_runner.run()` despacha B3→Clear simulado e FOREX→OANDA Practice quando path pinado + credenciais; caso contrário `NO_DEMO_ACCOUNT_PATH`; zero POST Alpaca para esses mercados; ACK Alpaca só para US/CRYPTO. Testes mock em `tests/test_signal_paper_runner.py` (`test_n34_*`).

**Honestidade:** ISS-010 permanece **aberto** (homologação ao vivo N29.5); N29 Status **planejada**; adapter submit qty-only sem bracket; preencher EasyPanel sozinho não homologa conta real.

**Decisões:** `LIVE_TRADING_ENABLED=false`; vendor pin inalterado; sem HTTP Clear/OANDA real no CI.

**Prova citada:** PR [**#45**](https://github.com/ig0rayres/trading_lab/pull/45) merge `3aefd4474a99bb96c14125b493bcaf12f0f0abb7` (`2026-11-16T22:45:44Z`); `origin/main` tip `7627b45` (feat `4fc0644`, fix `bbe97b8`, restamp validação). CI test / docker-smoke / docker-build **SUCCESS** (não é fill).

**Finalizer (2026-11-16):** stamp local **APROVADA** (`validation_gate` focal `test_signal_paper_runner` + copy + demo adapters); ROADMAP N34 → `concluida`; N27.2 `[x]` com nodeids `test_n34_*`; N29 **planejada**; homologação ao vivo **N29.5** ainda `[ ]` — **não** alegar Clear/OANDA live.

**Aprendizados:** mock no laço fecha wiring fail-closed sem credencial operador; pytest ≠ homologação em conta demo real; pin path evita cross-market Alpaca.

**Próximo:** `/pmo plan` — lacuna honesta **ISS-011**: homolog Clear/OANDA (**N29.5** / credenciais EasyPanel) *vs* shadow→paper Tá Barato (**N17.2** / G-FORM); `LIVE_TRADING_ENABLED=false`.

**EasyPanel (2026-11-16):** operador atestou **#46 no ar** (tip `d99b332`, inclui N34/#45). **Não é fill**; N29.5 (creds Clear/OANDA) continua pendente.

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
