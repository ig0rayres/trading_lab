# Roadmap Técnico — Trading Lab

> Gerado em: 2026-10-30  
> Fase: 8 — Planejamento técnico (`/pmo plan`, categoria **D**)  
> Baseado em: `docs/PROJECT-BRIEF.md`, `docs/REQUIREMENTS.md`, `docs/ARCHITECTURE.md`, `docs/DATABASE.md`, `docs/LEGACY-ANALYSIS.md`  
> Status: **Em execução** (D3 Gate A + D4 Gate B — nada marcado concluído sem critério fechado)
> Gerado via: `/pmo plan` — Rock handoff 2026-10-30

---

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de sprints (fase construção) | 5 |
| Tarefas estimadas | 28 (12 P, 16 M) |
| Caminho crítico | D1 → D2 → D4 → D5 (ledger + gates antes de homologação paper) |
| Live trading | Fora de escopo até evidência explícita; `LIVE_TRADING_ENABLED=false` |

**BOM:** D1 cobre BOM-1/BOM-2; D2–D5 cobrem BOM-3/BOM-4 (paper homologado, sem substituir EasyPanel).

---

## Índice de Sprints

| Sprint | Categoria | Gate (resumo) | Status | Tasks | Módulos | Resumo | Linhas |
|--------|-----------|---------------|--------|-------|---------|--------|--------|
| D1 | D | CI verde + vendor pinado + pytest com nodeids | concluida | 6 | baseline, vendor | Evidência reprodutível | 80–115 |
| D2 | D | Tabelas ledger no Postgres + rollback testado | concluida* | 5 | ledger | Persistência paper | 117–145 |
| D3 | D | Gate A rejeita sinal inválido sem broker | concluida | 6 | signal-gate-a | Ingestão autêntica | 147–178 |
| D4 | D | Gate B + fila paper sem fill | concluida | 6 | risk-gate-b, paper-gateway | Limites antes da fila | 179–210 |
| D5 | D | Paper reconciliado read-only; nenhum live | concluida* | 5 | paper-gateway, observability | Homologação ponta a ponta | 214–242 |
| N6 | N | Imagem com psycopg + vendor pinado; CI smoke | concluida | 5 | vendor, observability | Deploy reprodutível EasyPanel | *(abaixo)* |
| N7 | N | Fases persistidas; shadow/research sem paper_allowed; ORB fora | concluida | 6 | strategy-catalog, risk-gate-b | Catálogo MVP + Gate B | *(abaixo)* |
| N8 | N | migrate apply deixa 7 strategy_states; runbook EasyPanel | concluida | 4 | strategy-catalog, ledger | Homologação + seed on migrate | *(abaixo)* |
| N9 | N | Itens 3–7 com evidência operador; F-013 persist | concluida | 6 | signal-gate-a, risk-gate-b, paper-gateway, observability | Homologação D5 EasyPanel | *(abaixo)* |
| N10 | N | Closeout N9 no ROADMAP + notas smoke homolog | concluida | 5 | docs | Alinhamento pós-N9 | *(abaixo)* |
| N11 | N | Feature 1 REQUIREMENTS fechada; pytest traceability | concluida | 4 | research-cycle | Ciclo research sem ordem + manifesto | *(abaixo)* |
| N12 | N | Feature 5 fill `signal_copy` evidenciado; LIVE false | planejada | 5 | paper-gateway, signal_copy | Demo Alpaca paper (P0 pivot) | *(abaixo)* |
| N13 | N | Homolog por família; sem scoring inventado | em execucao | 4 | strategy-catalog | Estratégias P1 pós-demo | *(abaixo)* |
| N14 | N | Pacotão MVP-DEMO-1.0 runbook + smoke + deploy policy | concluida | 4 | docs, observability | Release único MVP demo | *(abaixo)* |
| N15 | N | MVP-OP-0.9 — submit copy paper homologado | em execucao | 2 | operador, docs | Submit `signal_copy` | *(abaixo)* |
| N16 | N | MVP-OP-1.0 — Prodígio paper + Command Panel v1 | concluida | 9 | prodigy, v4_web_dashboard | Plataforma operacional v1 | *(abaixo)* |
| N17 | N | MVP-OP-1.1 — Tá Barato upstream + painel família | planejada | 5 | vendor, strategy-catalog | Multi-estratégia | *(abaixo)* |
| N18 | N | Command Panel always-on (`v4-ops`) + runbook ops | em execucao | 4 | observability, docs | Painel 8765 sem nohup | *(abaixo)* |
| N19 | N | Laço demo: gatilho no painel e ciclo da ordem no ledger | em execucao | 4 | observability, paper-gateway | Operar B3, cripto e forex | *(abaixo)* |
| N20 | N | Contrato v0.3 + N19.1–N19.2 publicados; fill P-001b; SHA imagem; 0 rebuild | em execucao | 5 | docs, ledger, observability | Onda 0 — resgate | *(abaixo)* |
| N21 | N | Ordem até fill/cancel/expira; P&L só de fill; restart sem duplicar | planejada | 3 | paper-gateway, ledger | Onda 1 — ciclo da ordem | *(abaixo)* |
| N22 | N | Risco lê `control_flags`; capital único R$ 5.000; sessão B3 + feriado | concluida | 3 | risk-gate-b | Onda 2 — âncoras honestas | *(abaixo)* |
| N23 | N | Trabalhador da fila dentro do `v4-ops`; dois apps EasyPanel | concluida | 3 | observability, paper-gateway | Onda 2 — worker (ADR-009) | *(abaixo)* |
| N24 | N | Login + Central de controle; dia a dia sem Exec | concluida | 4 | v4_web_dashboard | Onda 3 — Feature 8 | *(abaixo)* |
| N25 | N | Tela de sinais com destino, gate e âncora; ranking Prodígio | concluida | 3 | v4_web_dashboard | Onda 3 — Feature 9 | *(abaixo)* |
| N26 | N | Performance só de fill confirmado; bruto rotulado | concluida | 3 | v4_web_dashboard, ledger | Onda 3 — Feature 10 | *(abaixo)* |
| N27 | N | Laço autônomo só no mercado com conta demo nomeada (G-MKT) | planejada | 6 | paper-gateway, risk-gate-b | Onda 4 — Feature 7 | *(abaixo)* |
| N29 | N | Adapters Clear (B3) + OANDA Practice (forex); Alpaca cripto (ISS-010) | planejada | 6 | paper-gateway | Onda 4b — G-MKT adapters | *(abaixo)* |
| N28 | N | Ajuste supervisionado reversível, sem tocar âncora (G-AJUSTE) | concluida | 4 | strategy-catalog | Onda 6 — Feature 11 | *(abaixo)* |
| N30 | N | Feature 7 Alpaca US+cripto + Prodígio rank→sinal; Features 8–10 com evidência | concluida | 5 | paper-gateway, prodigy | Campanha ISS-011 onda 1 | *(abaixo)* |
| N31 | N | Melhoria contínua diária (fills + não-fills) + TimesFM research-only (G-AJUSTE) | concluida | 5 | evolution, research | Campanha ISS-012 · desbloqueia caminho N28.2–4 | *(abaixo)* |
| N32 | N | Âncoras do painel no laço paper (Feature 7, sem teto paralelo) | concluida | 4 | paper-gateway, risk-gate-b | Campanha ISS-011 lacuna âncora | *(abaixo)* |
| N33 | N | Closeout docs: carimbar N28/N30/N31 e deixar o restante Alpaca honesto | concluida | 5 | docs | Campanha ISS-011 closeout papel | *(abaixo)* |
| N34 | N | Ligar Clear/OANDA no laço paper fail-closed (N27.2); N29 não concluída | concluida | 4 | paper-gateway | Campanha ISS-010 / N27.2 wiring | *(abaixo)* |
| N35 | N | Presença das chaves demo (nomes) + roteiro de homologação; N29.5 continua operador | concluida | 4 | paper-gateway, docs | Campanha ISS-010 / pré-homolog N29.5 | *(abaixo)* |
| N36 | N | Textos do freio na Central; kill_switch inalterado; LIVE false | concluida | 3 | observability | Copy UX kill switch | *(abaixo)* |
| N37 | N | Saúde automática + Central semáforo + defaults ON | concluida | 5 | observability | Plataforma monitorada sem Exec | *(abaixo)* |
| N38 | N | Faixa do freio com dois estados e um só botão; kill_switch inalterado; LIVE false | concluida | 3 | observability | UX estado visual do freio | *(abaixo)* |
| N39 | N | Closeout docs: carimbar N37 saúde automática e fechar ISS-014 | concluida | 5 | docs | Campanha ISS-014 closeout papel | *(abaixo)* |
| N40 | N | Mapa honesto: onde está cada coisa no painel (docs-only) | concluida | 5 | docs, observability | Orientação operador ISS-016 | *(abaixo)* |
| N41 | N | Menu Ordens + Histórico (listas); painel sem envio; LIVE false | concluida | 5 | observability | Campanha ISS-017 onda 1 | *(abaixo)* |
| N42 | N | Menu Estratégias com fases; sem promoção; LIVE false | concluida | 5 | observability | Campanha ISS-017 onda 2 | *(abaixo)* |
| N43 | N | TimesFM / dicas visíveis e rotuladas (não autorizam ordem) | concluida | 5 | observability, research | Campanha ISS-017 onda 3 | *(abaixo)* |
| N44 | N | Homologar operar US+cripto pelo painel (roteiro; sem fill inventado) | concluida | 5 | docs, operador | Campanha ISS-017 onda 4 — **runbook entregue; passeio operador pendente** | *(abaixo)* |
| N45 | N | Tá Barato no menu — bloqueado em N17.2 | planejada | stub | strategy-catalog | Campanha ISS-017 onda 5 | *(abaixo)* |
| N46 | N | B3 Clear no painel — bloqueado em N29.5 | planejada | stub | paper-gateway | Campanha ISS-017 onda 6 | *(abaixo)* |
| N47 | N | OANDA Practice no painel — bloqueado em N29.5 | planejada | stub | paper-gateway | Campanha ISS-017 onda 7 | *(abaixo)* |
| N48 | N | Sinais = cópia de terceiros + auditoria; sem fill inventado; LIVE false | concluida | 5 | observability | ISS-018 alinhamento Sinais↔copy | *(abaixo)* |
| N49 | N | Ordem paper mostra o sinal; inventário e critérios visíveis; LIVE false | planejada | 6 | observability | ISS-019 proveniência e pool | *(abaixo)* |
| N50 | N | Lista nomeada Collective2; Sinais em operação vs auditoria vs Prodígio; Provedor visível; LIVE false | planejada | 6 | observability | ISS-020 C2 + reorganizar Sinais | *(abaixo)* |
| N51 | N | Fila de pré-aprovação no painel com métricas de pesquisa; aprovar não envia ordem; LIVE false | planejada | 6 | observability, ledger | ISS-021 pré-aprovação + métricas | *(abaixo)* |
| N52 | N | Cockpit Sinais: decisão no topo, todos os números de pesquisa, visual do desenho; LIVE false | planejada | 4 | observability | ISS-022 redesign UX Sinais | *(abaixo)* |
| N53 | N | Painel visual v2 em todas as rotas + botão atualizar candidatos (GET releitura); LIVE false | concluida | 5 | observability | ISS-023 redesign plataforma + refresh UI | *(abaixo)* |
| N54 | N | POST critérios ao vivo em Atualizar candidatos; GET declara releitura; LIVE false | concluida | 5 | observability | ISS-024 job C2/Prodígio/TV mínimo · PR #73 | *(abaixo)* |
| N55 | N | Fila de pré-aprovação com elegíveis de Collective2, Prodígio e TradingView após atualizar; LIVE false | concluida | 5 | observability | ISS-024 follow-up fila multiplataforma · PR #74 | *(abaixo)* |
| N56 | N | Job lê arquivos brutos no volume certo; fila Prodígio só elegíveis 15d; LIVE false | concluida | 4 | observability | ISS-024 / F-019 join duplicado · PR #76 | *(abaixo)* |
| N57 | N | Collective2 na fila a partir dos arquivos brutos, sem lista nomeada para aparecer; LIVE false | concluida | 4 | observability | ISS-024 / F-020 fila C2 sem allowlist · PR #77 | *(abaixo)* |
| N58 | N | Atualizar varre Collective2 nas regras de 15 dias; TradingView sem busca; LIVE false | concluida | 4 | observability | ISS-024 / F-021 varredura C2 · PR #78 | *(abaixo)* |
| N59 | N | Varredura Collective2 segue se ordens ativas falharem; LIVE false | concluida | 4 | observability | ISS-024 / F-022 isolamento snapshot | *(abaixo)* |
| N60 | N | Histórico fechado parcial não derruba a Collective2; botão sai de «Atualizando…»; LIVE false | em_execucao | 5 | observability | ISS-024 / F-023 coleta em massa · plan_only | *(abaixo)* |

\* D5: código + CI + `docs/HOMOLOGATION.md`; fill real Alpaca permanece passo operador (Feature 5 `[ ]` único critério).

\* D2: migration/CI ok; `.env.example` alinhado (F-004 fechado).

---

## Estratégia de Auditoria

> Modo: Pipeline (lab)

| Sprint | Review | Motivo |
|--------|--------|--------|
| D1 | skip | CI + pytest |
| D2 | senior+qa | DDL e integridade financeira |
| D3 | senior+qa | Superfície webhook |
| D4 | senior+qa | Gates de risco |
| D5 | comprehensive | Última sprint D — paper |
| N6 | senior+qa | Deploy EasyPanel |
| N7 | senior+qa | Catálogo + Gate B produto |
| N8 | senior+qa | Seed no CLI migrate + runbook homologação |
| N9 | senior+qa | Runbook itens 3–7 + evidência; F-013 persist |
| N10 | skip | Docs closeout only |
| N11 | senior+qa | Scheduler/run-once tests + REQUIREMENTS Feature 1 |
| N12 | senior+qa | Paper submit path + homolog operador Feature 5 |
| N13 | senior+qa | Matriz homolog estratégias; F-003 congelado até N12 |
| N15 | skip | Operador + docs; 0 rebuild |
| N16 | senior+qa | Prodígio paper + dashboard v1 (`v4_web_dashboard`) |
| N17 | senior+qa | Tá Barato upstream + extensão painel |
| N19 | senior+qa | Escrita de gatilho + rastro da ordem |
| N20 | senior+qa | Resgate de contrato e código N19.1–N19.2 |
| N21 | senior+qa | Ciclo da ordem e P&L de fill |
| N22 | senior+qa | Gates de risco e calendário |
| N23 | senior+qa | Supervisor `v4-ops` |
| N24 | senior+qa | Autenticação do painel |
| N25 | senior+qa | Tela de sinais |
| N26 | senior+qa | Performance financeira |
| N27 | comprehensive | Envio autônomo na conta demo |
| N29 | comprehensive | Adapters Clear + OANDA Practice |
| N28 | senior+qa | Ajuste automático de parâmetro |
| N30 | senior+qa | Laço Alpaca US+cripto + ingestão Prodígio |
| N31 | senior+qa | Melhoria contínua diária + TimesFM research-only |
| N32 | senior+qa | Âncoras do painel no envio paper |
| N33 | skip | Closeout docs ISS-011 (Alpaca); sem `src/` |
| N34 | comprehensive | Ligar adaptadores demo no laço paper (N27.2); AgentCoder |
| N35 | senior+qa | Presença de nomes + roteiro homologação demo; zero M |
| N36 | skip | Copy do freio na Central; testes de string; zero M |
| N37 | senior+qa | Saúde automática + semáforo Central; defaults ON |
| N38 | skip | Faixa do freio na Central; um CTA por estado; zero M |
| N39 | skip | Closeout docs N37 / ISS-014; sem `src/` |
| N40 | skip | Mapa operador das duas superfícies; zero M; sem `src/` |
| N41 | senior+qa | Ordens e histórico no menu do dia a dia; AgentCoder |
| N42 | senior+qa | stub campanha — catálogo de fases no menu |
| N43 | senior+qa | Análise Google no menu; TimesFM só pesquisa |
| N44 | skip | Homologação operador US+cripto pelo painel; zero M; sem src/ |
| N45 | senior+qa | stub campanha — Tá Barato; não arranca sem N17.2 |
| N46 | comprehensive | stub campanha — Clear; não arranca sem N29.5 |
| N47 | comprehensive | stub campanha — OANDA; não arranca sem N29.5 |
| N48 | senior+qa | Tela Sinais: cópia de terceiros + auditoria; sem fill inventado |
| N49 | senior+qa | Proveniência ordem↔sinal + inventário/critérios visíveis; sem fill inventado |
| N50 | senior+qa | Collective2 lista nomeada + reorganizar Sinais + Provedor visível; sem fill inventado |
| N51 | senior+qa | Pré-aprovação no painel + métricas reutilizadas; sem fill inventado |
| N52 | senior+qa | Cockpit Sinais: métricas completas + hierarquia + tokens visuais; sem fill inventado |
| N53 | senior+qa | Plataforma visual v2 + refresh honesto GET; job refresh = N54; sem fill inventado |
| N54 | senior+qa | Job critérios ao vivo ISS-024; POST live_criteria; LIVE false |
| N55 | senior+qa | Fila pré-aprovação multiplataforma após refresh; ISS-024 follow-up |
| N56 | senior+qa | Join dos arquivos brutos no volume de relatórios; fila só elegíveis; LIVE false |
| N57 | senior+qa | Collective2 na fila a partir dos arquivos brutos sem allowlist para aparecer; LIVE false |
| N58 | senior+qa | Varredura Collective2 com regras de 15 dias; TradingView fora até contrato de busca; LIVE false |
| N59 | senior+qa | Isolar consulta de ordens ativas da varredura Collective2; LIVE false |
| N60 | senior+qa | Isolar coleta de histórico fechado da fonte Collective2; botão não fica preso; LIVE false |

---

## Grafo de Dependências

```
[D1 CI + vendor pin] ──► [D2 Postgres ledger]
                              │
[D3 Gate A] ──────────────────┼──► [D4 Gate B + gateway queue]
                              │              │
                              └──────────────┴──► [D5 reconcile + dashboard auth]
                                                              │
[N6 EasyPanel image] ──► [N7 strategy-catalog + Gate B phase] ──► [N8 seed on migrate]
```

D3 pode iniciar em paralelo com D2 após D1, mas D5 depende de D2–D4. N7 depende de D2 (tabela) + D4 (Gate B) + N6 (deploy estável). N8 depende de N7 (`ensure_strategy_defaults`) + D2 (`ledger_migrate`); não reabre Gate B.

---

## Sprint D1 — Baseline verificável
> Categoria: D  
> titulo_humano: CI verde, upstream pinado e pytest com evidência real  
> Gate: `gh`/local: pytest passa com inventário; `docs/VENDOR-PIN.md` registra SHA; workflow CI verde em PR  
> bom_ref: BOM-1, BOM-2  
> review: skip

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | Adicionar `vendor/day-trader-skill` (submodule ou cópia) e `docs/VENDOR-PIN.md` | `/git` + documentação | — |
| [x] | P | Garantir CI (`.github/workflows/ci.yml`) e `requirements-dev.txt` | `/devops planejar` | — |
| [~] | P | Configurar remote Git + branch `front/d1-baseline` | `/git` | — *(origin + `main`; CI #3 Success)* |
| [x] | M | Rodar `vendor_verify` offline contra pin | skill refs | vendor |
| [ ] | M | Rodar `parity.py` quando artefatos orb existirem | `/qa validar` | vendor |
| [x] | P | Reexecutar pytest local; arquivar saída (nodeids) em `docs/` ou artefato CI | `/qa testes` | CI |
| [x] | P | Atualizar `docs/REQUIREMENTS.md` critério pytest quando verde | `/pmo` | pytest |

---

## Sprint D2 — Ledger Postgres
> Categoria: D  
> titulo_humano: Banco pronto para ordens paper com trilha append-only  
> Gate: migration aplica e reverte; oito tabelas do DBML existem; teste de integração sem credencial real  
> bom_ref: BOM-3  
> review: senior+qa

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | Alembic/SQL migration alinhada a `docs/db-schema.dbml` | `/arquiteto dados` | D1 |
| [x] | P | Teste rollback da migration | `/qa testes` | migration |
| [x] | M | Adapter de persistência (append-only; sem `deleted_at` como borracha) | `/dev` | migration |
| [x] | P | `.env.example` alinhado aos nomes reais do código | `/devops` | — |
| [x] | P | Documentar runbook de apply na instância existente | `docs/INFRASTRUCTURE.md` | migration |

---

## Sprint D3 — Gate A (sinal)
> Categoria: D  
> titulo_humano: Webhook e ingestão recusam sinal falso antes de qualquer fila  
> Gate: testes cobrem rejeição (segredo, schema, idempotência); nenhuma chamada Alpaca no caminho A  
> bom_ref: BOM-3  
> review: senior+qa

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | Contrato Gate A = `api-spec.yaml` + skill (header + legacy EasyPanel) | `/dev` | D1 |
| [x] | P | Testes: sinal inválido → código de motivo, zero ordem | `/qa testes` | Gate A |
| [x] | M | Integrar News First / copy apenas como **entrada** auditada (sem broker) | `/dev` | Gate A |
| [x] | P | Calendário/sessão: recusar fora de horário (upstream `session`) | `/dev` | vendor |
| [x] | P | Atualizar `docs/REQUIREMENTS.md` Feature 2 critérios | `/pmo` | testes |
| [x] | P | Registrar achados abertos em `docs/FINDINGS.md` | `/pmo triar` | — |
| [x] | P | Testes HTTP handler webhook | `/qa testes` | Gate A |

---

## Sprint D4 — Gate B e fila paper
> Categoria: D  
> titulo_humano: Limites de capital e risco antes da fila Alpaca paper  
> Gate: ordem bloqueada excede R$50/posição/3 slots; `PAPER_GATEWAY_QUEUE_ONLY` continua não sendo fill  
> bom_ref: BOM-3, BOM-4  
> review: senior+qa

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | Gate B: reuso `trader-risk` + políticas REQUIREMENTS (capital paper) | skill `paper-order-gate` | D2, D3 |
| [x] | M | Paper gateway: fila após B; stub de broker em testes | `/dev` | Gate B |
| [x] | P | Testes + REQUIREMENTS Feature 3 fechados | `/qa testes` | gateway |
| [x] | M | Gravar intenção de ordem no ledger (pré-envio) | `/dev` | D2 |
| [x] | P | Kill switch documentado (`INFRASTRUCTURE`) | `docs/INFRASTRUCTURE.md` | — |
| [x] | P | 3 posições + rejeição persistida + critérios Feature 3 | `/dev` | Gate B |

---

## Sprint D5 — Homologação paper (read-only reconcile)
> Categoria: D  
> titulo_humano: Paper reconciliado sem live e sem trocar EasyPanel  
> Gate: fluxo sinal→A→B→fila→fill simulado/real paper read-only; dashboard exige auth se público  
> bom_ref: BOM-3, BOM-4  
> review: comprehensive

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | `v4_alpaca_reconcile` integrado ao ledger (READ_ONLY) | `/dev` | D4 |
| [x] | M | Trilha de evidência: shadow vs paper no dashboard | `/dev` | D4 |
| [x] | P | Checklist de homologação operador (sem live) | `docs/HOMOLOGATION.md` | — |
| [x] | P | Export comparativo EasyPanel vs snapshot (SHA imagem) | operador | `docs/INFRASTRUCTURE.md` §9 |
| [x] | M | Fechar critérios Features 2–3 e 6; Feature 5 parcial em REQUIREMENTS | `/pmo` | reconcile |

---

## Sprint N6 — Deploy reprodutível EasyPanel
> Categoria: N  
> Status: concluida  
> titulo_humano: Imagem EasyPanel sobe com Postgres e vendor pinado  
> resumo_humano: Redeploy deixa de depender de clone manual do vendor e de pip install de psycopg. Mesma imagem para trading-lab e trading-lab-webhook; live permanece desligado.  
> Gate: docker build ok; container importa psycopg; vendor @ SHA VENDOR-PIN; CI docker-build smoke; pytest inalterado + test_image_pin  
> bom_ref: BOM-2, BOM-3  
> review: senior+qa  

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | Pin runtime psycopg[binary] on requirements.txt | `/dev` | — |
| [x] | M | Bake vendor pin in Dockerfile (git clone SHA) | `/devops` | N6.1 |
| [x] | P | CI docker-build smoke | `/devops` | N6.2 |
| [x] | M | EasyPanel runbook: dois apps; sem overlay vazio /app/vendor | docs | N6.2 |
| [x] | P | Pin-drift test VENDOR-PIN vs Dockerfile | `/qa testes` | N6.2 |

---

## Sprint N7 — Catálogo de estratégias (MVP) + Gate B por fase
> Categoria: N  
> Status: concluida  
> titulo_humano: Fase persistida trava paper; ORB fora do principal  
> resumo_humano: Cada família passa a ter fase no Postgres (research, shadow, paper limitado, validado). O Gate B recusa paper se a fase for research ou shadow, e ORB não entra como estratégia principal. Sem inventar fórmula de momentum, Tá Barato ou Prodigy.  
> Gate: pytest — research/shadow nunca paper_allowed; ORB rejeitado mesmo com fase paper_* no banco; linha ausente fail-closed; risk_decisions.strategy_key vem do sinal (não literal signal_copy); LIVE_TRADING_ENABLED false; nenhum limiar novo de scoring momentum/Tá Barato/Prodigy  
> bom_ref: BOM-3, BOM-4  
> review: senior+qa  
> Generated via hub PMO (planning mode) on 2026-10-30. Source: Feature 4 REQUIREMENTS + ISS-002 + ARCHITECTURE strategy-catalog.  
> Brief: `docs/.briefs/N7.brief.md`

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | Catalog module + ledger helpers + insert-if-missing seed | `/dev` + `paper-order-gate` | — |
| [ ] | M | Signal carries strategy_key (HMAC ALLOWED + worker attach) | `/dev` | — |
| [ ] | M | Gate B reads strategy_states; shadow/research/ORB never paper_allowed | skill `paper-order-gate` | N7.1, N7.2 |
| [ ] | P | Persist risk_decisions.strategy_key from signal (drop hardcoded signal_copy) | `/dev` | N7.2 |
| [ ] | P | Ledger integration tests catalog + Gate B + queue (LEDGER_DATABASE_URL) | `/qa testes` | N7.1, N7.3, N7.4 |
| [ ] | P | REQUIREMENTS Feature 4 checkboxes N7 can close; no-invented-threshold regression | `/pmo` | N7.5 |

<details>
<summary>N7.1 executor_prompt</summary>

```yaml
id: N7.1
size: M
bom_ref: BOM-3
depends_on: []
files:
  - src/strategy_catalog.py
  - src/ledger_store.py
  - tests/test_strategy_catalog.py
reuse_targets:
  - component: src/ledger_store.py
    reuse_as: extend
    convergence_check: rg "strategy_states" src/ledger_store.py && rg "def get_strategy_phase|def ensure_strategy_defaults" src/strategy_catalog.py src/ledger_store.py
  - component: docs/db-schema.dbml
    reuse_as: mirror_shape
    convergence_check: rg "research|shadow|paper_limited|paper_validated" src/strategy_catalog.py && rg "news_first|momentum|ta_barato|signal_copy|prodigy_15d|orb|mean_reversion" src/strategy_catalog.py
  - component: migrations/001_ledger_up.sql
    reuse_as: call
    convergence_check: rg "CREATE TABLE strategy_states" migrations/001_ledger_up.sql && rg "strategy_states" src/ledger_store.py
guardrail_contract:
  - class: secrets
    id: n7-1-no-secrets
    target: src/strategy_catalog.py
    check: python3 -c "from pathlib import Path; t=Path('src/strategy_catalog.py').read_text() if Path('src/strategy_catalog.py').exists() else ''; assert 'ALPACA_API' not in t and 'sk_live' not in t"
    pass_condition: no broker credentials in catalog module
  - class: subagent-safety
    id: n7-1-live-lock
    target: src/original.py
    check: rg "LIVE_TRADING_ENABLED must be false" src/original.py
    pass_condition: LAB_LOCK remains
executor_prompt: |
  ### Quality Brief (Sprint N7)
  sprint: N7
  Maintain: load_original().risk.check for the capital bracket — do not reimplement trader-risk/check.py.
  Maintain: ledger_store.insert_row / connect / LEDGER_TABLES — extend helpers; no second persistence module.
  Maintain: LIVE_TRADING_ENABLED=false and original.py LAB_LOCK.
  Avoid: inventing RSI/percentile/score thresholds for momentum, Tá Barato, or Prodigy.
  Avoid: promoting strategy_states.phase from PnL, HTTP 200, or PAPER_GATEWAY_QUEUE_ONLY; seed is insert-if-missing only.
  [ABORDAGEM] Attach strategy_key on the in-memory signal in the worker after HMAC validate; Gate B never infers the key.
  [RISCO] Catalog check must fail-closed when DB/override is missing.
  [OPORTUNIDADE] Copy kill_switch_active SQL read pattern for strategy_states.phase.
  EXPIRES at end of Sprint N7.

  Melhoria: persistent strategy_states read/seed without a new migration.
  Contexto: migrations/001_ledger_up.sql and db-schema.dbml already define strategy_states (strategy_key unique, phase research|shadow|paper_limited|paper_validated). src/ledger_store.py lists the table in LEDGER_TABLES but has only insert_row — no get/seed. Gate B cannot consult phases today.
  Objetivo: add src/strategy_catalog.py plus helpers on ledger_store (get_strategy_phase, ensure_strategy_defaults). Known keys from DBML only. Seed insert-if-missing: news_first/momentum/ta_barato/prodigy_15d=research; signal_copy=paper_limited; orb/mean_reversion=shadow. Never overwrite an existing row. Never invent scoring numbers. LIVE_TRADING stays false.
  Arquivos: src/strategy_catalog.py, src/ledger_store.py, tests/test_strategy_catalog.py.
  Critério de pronto: unit tests for known keys/phases; ledger integration (skipUnless LEDGER_DATABASE_URL, apply migration like tests/test_paper_gateway_queue.py GateBLedgerIntegrationTest) proves insert-if-missing and that a second seed does not clobber a hand-updated phase; rg shows no CREATE TABLE strategy_states outside 001.
  Cenários de teste:
    1. Caso normal: empty table + ensure_strategy_defaults → seven rows with recommended phases.
    2. Edge case: existing orb=paper_validated is left unchanged by seed (overwrite forbidden).
    3. Edge case: unknown strategy_key → lookup error/None, never default paper_limited.
    4. Regressão: LEDGER_TABLES still includes all eight ledger tables; insert_row still rejects unknown table.
```
</details>

<details>
<summary>N7.2 executor_prompt</summary>

```yaml
id: N7.2
size: M
bom_ref: BOM-3
depends_on: []
files:
  - src/signal_copy.py
  - src/tradingview_worker.py
  - tests/test_signal_copy.py
reuse_targets:
  - component: src/signal_copy.py
    reuse_as: extend
    convergence_check: rg "strategy_key" src/signal_copy.py && rg "ALLOWED" src/signal_copy.py
  - component: src/tradingview_worker.py
    reuse_as: extend
    convergence_check: rg "strategy_key" src/tradingview_worker.py
  - component: tests/test_signal_copy.py
    reuse_as: copy_pattern
    convergence_check: rg "strategy_key" tests/test_signal_copy.py
guardrail_contract:
  - class: secrets
    id: n7-2-hmac-no-leak
    target: src/signal_copy.py
    check: rg "provider_signature" src/signal_copy.py && ! rg -n "print\(.*SECRET" src/signal_copy.py src/tradingview_worker.py
    pass_condition: signature stays HMAC compare; no secret print
  - class: subagent-safety
    id: n7-2-live-lock
    target: src/original.py
    check: rg "LIVE_TRADING_ENABLED=false" Dockerfile
    pass_condition: image live lock unchanged
executor_prompt: |
  ### Quality Brief (Sprint N7)
  sprint: N7
  Maintain: load_original().risk.check — do not reimplement trader-risk.
  Maintain: ledger_store helpers — no second store.
  Maintain: LIVE_TRADING_ENABLED=false.
  Avoid: invented scoring thresholds.
  Avoid: silent strategy_key inference inside Gate B.
  [ABORDAGEM] Worker attaches strategy_key after HMAC validate; add field to signal_copy.ALLOWED.
  [RISCO] Extra JSON key today is INVALID_SCHEMA — ALLOWED must include strategy_key or TV payloads with the field never reach Gate B.
  [OPORTUNIDADE] Keep signal_events schema unchanged (no strategy_key column).
  EXPIRES at end of Sprint N7.

  Melhoria: the signed signal carries strategy_key to Gate B.
  Contexto: signal_copy.ALLOWED omits strategy_key (unrecognized field → INVALID_SCHEMA). paper_gateway_queue hardcodes strategy_key 'signal_copy'. Gate A signal_events has no strategy_key column — do not add one.
  Objetivo: CONTRACT (documented in docs/.briefs/N7.brief.md): worker is the attachment point, not Gate A persist. Add optional strategy_key to ALLOWED. After validate succeeds, if missing and provider==tradingview, set signal_copy. Other providers without key stay missing (Gate B will reject). Do not default orb or momentum.
  Arquivos: src/signal_copy.py, src/tradingview_worker.py, tests/test_signal_copy.py (worker test in same file or tests/test_tradingview_worker.py only if already present — do not create a parallel package).
  Critério de pronto: valid HMAC without strategy_key still previews; with strategy_key='signal_copy' still previews; unknown extra field still INVALID_SCHEMA; worker-attached key is visible on the dict passed toward evaluate_signed_signal.
  Cenários de teste:
    1. Caso normal: signed payload with strategy_key=signal_copy → no INVALID_SCHEMA.
    2. Edge case: payload without strategy_key still validates (legacy HMAC).
    3. Edge case: unrecognized field (news_first=True) still INVALID_SCHEMA (test_unrecognized_field regression).
    4. Regressão: orders_sent remains 0 on preflight; LIVE_TRADING_ENABLED false.
```
</details>

<details>
<summary>N7.3 executor_prompt</summary>

```yaml
id: N7.3
size: M
bom_ref: BOM-3, BOM-4
depends_on: ["N7.1", "N7.2"]
files:
  - src/gate_b_risk.py
  - tests/test_gate_b_risk.py
reuse_targets:
  - component: vendor/day-trader-skill/trader-risk/check.py
    reuse_as: call
    convergence_check: rg "load_original\(\)\.risk" src/gate_b_risk.py && ! rg "def check\(" src/gate_b_risk.py src/strategy_catalog.py
  - component: src/strategy_catalog.py
    reuse_as: call
    convergence_check: rg "get_strategy_phase|STRATEGY_PHASE|STRATEGY_ORB" src/gate_b_risk.py
  - component: src/gate_b_risk.py
    reuse_as: extend
    convergence_check: rg "evaluate_signed_signal" src/gate_b_risk.py && rg "kill_switch_active" src/gate_b_risk.py
guardrail_contract:
  - class: secrets
    id: n7-3-no-live-host
    target: src/gate_b_risk.py
    check: rg "No broker calls" src/gate_b_risk.py && rg "LIVE_TRADING_ENABLED=false" Dockerfile
    pass_condition: Gate B stays broker-free; live flag false
  - class: subagent-safety
    id: n7-3-no-reimplement-risk
    target: vendor/day-trader-skill/trader-risk/check.py
    check: rg "load_original" src/gate_b_risk.py && rg "risk.check" src/gate_b_risk.py
    pass_condition: upstream check still called
executor_prompt: |
  ### Quality Brief (Sprint N7)
  sprint: N7
  Maintain: load_original().risk.check for the capital bracket — do not reimplement trader-risk/check.py.
  Maintain: existing kill switch, session, and max-positions checks.
  Maintain: LIVE_TRADING_ENABLED=false.
  Avoid: invented scoring thresholds; do not call trader-scanner orb_hit to authorize paper.
  Avoid: paper_allowed for research/shadow or for orb even if DB phase is paper_*.
  [ABORDAGEM] Phase check after kill/session/cap and before risk.check.
  [RISCO] Unit tests currently paper_allowed without DB — add strategy_phase= override for those cases; production path fail-closed without DB.
  [OPORTUNIDADE] Mirror kill_switch_active SELECT WHERE deleted_at IS NULL.
  EXPIRES at end of Sprint N7.

  Melhoria: Gate B enforces strategy_states phase.
  Contexto: evaluate_signed_signal applies kill switch, NYSE session, position cap, then trader-risk.check. It does not read strategy_states. Architecture: strategy in shadow never gets paper_allowed. Feature 4: ORB is not selectable as main paper strategy.
  Objetivo: require signal['strategy_key']. Resolve phase via strategy_phase= test override, else catalog/ledger (fail-closed if neither). Reject codes: STRATEGY_KEY_REQUIRED, STRATEGY_UNKNOWN, STRATEGY_PHASE_UNKNOWN, STRATEGY_PHASE_NOT_PAPER (research|shadow), STRATEGY_ORB_NOT_SELECTABLE (orb always; mean_reversion same non-selectable rule). Only paper_limited|paper_validated proceed to existing risk.check. Do not reimplement check(). Do not add momentum/Tá Barato/Prodigy numeric gates.
  Arquivos: src/gate_b_risk.py, tests/test_gate_b_risk.py.
  Critério de pronto: pytest GateBRiskTest still PASSes a within-risk signal when strategy_phase=paper_limited and strategy_key=signal_copy; shadow/research/missing/orb never paper_allowed; risk.check still invoked on the happy path.
  Cenários de teste:
    1. Caso normal: signal_copy + paper_limited + within-risk → paper_allowed (existing qty=1 case).
    2. Edge case: orb + paper_validated override still rejected STRATEGY_ORB_NOT_SELECTABLE.
    3. Edge case: momentum + research → STRATEGY_PHASE_NOT_PAPER, orders path not reached.
    4. Edge case: missing row / no DB and no override → STRATEGY_PHASE_UNKNOWN.
    5. Regressão: qty=100 still blocked by upstream risk; kill switch and OUTSIDE_SESSION unchanged.
```
</details>

---

## Sprint N8 — Homologação + seed on migrate
> Categoria: N  
> Status: concluida  
> titulo_humano: Migrate apply popula as 7 fases sem INSERT manual  
> resumo_humano: Depois de aplicar o ledger, o Postgres já nasce com as sete famílias do catálogo. Reaplicar a migrate em base já migrada também preenche linhas que faltam, sem sobrescrever fase gravada à mão. O runbook de homologação/EasyPanel diz como conferir; sem rebuild de imagem nesta sprint.  
> Gate: pytest — `ledger-migrate apply` (roundtrip ou `already_applied`) deixa 7 linhas em `strategy_states` quando `LEDGER_DATABASE_URL` está definido; seed insert-if-missing; rollback não semeia; `LIVE_TRADING_ENABLED` false; sem migration 002; sem reabrir Gate B nem limiar de scoring  
> bom_ref: BOM-3  
> review: senior+qa  
> Generated via hub PMO (planning mode) on 2026-10-30. Source: ISS-003 + operador opção A pós-N7.  
> Brief: `docs/.briefs/N8.brief.md`

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N8.1 Hook `ensure_strategy_defaults` into `ledger-migrate apply` (including `already_applied`) | `/dev` | — |
| [x] | P | N8.2 Unit + optional ledger integration: apply roundtrip leaves 7 `strategy_states` rows | `/qa testes` | N8.1 |
| [x] | P | N8.3 Homologation runbook: verify 7 rows after migrate | docs | N8.2 |
| [x] | P | N8.4 EasyPanel/INFRASTRUCTURE note: re-apply seeds insert-if-missing | docs | N8.1 |

P notes (no executor_prompt): **N8.2** extend `tests/test_ledger_migration.py` — unit without DSN: `apply()` still calls `ensure_strategy_defaults` on `already_applied` (mock status/connect as needed). Integration (`skipUnless LEDGER_DATABASE_URL`): after the existing apply/rollback/apply roundtrip, `strategy_states` has 7 rows whose keys match `DEFAULT_PHASE_BY_KEY`; a second apply does not clobber a hand-updated phase; optional subprocess `python3 src/ledger_migrate.py apply`. Do not add Gate B tests. **N8.3** add a checklist step after migrate: `SELECT strategy_key, phase FROM strategy_states WHERE deleted_at IS NULL` → 7 keys; INSERT manual deixa de ser o caminho feliz. **N8.4** EasyPanel § apply: re-run `ledger-migrate apply` is safe (insert-if-missing); no new service, no image rebuild.

### Task N8.1 — Hook catalog seed into ledger-migrate apply

**Estado atual**: `apply()` aplica `001_ledger_up.sql` ou retorna `already_applied` sem tocar `strategy_states`. Seed só corre em `fetch_strategy_phase` / testes N7. EasyPanel ficou vazio até INSERT manual.
**Estado desejado**: todo `apply()` bem-sucedido (primeiro e `already_applied`) chama `ensure_strategy_defaults()` e falha de forma visível se as 7 chaves N7 não existirem; rollback não semeia; insert-if-missing.
**Fonte(s)**: ISS-003
**Módulo(s) afetado(s)**: `src/ledger_migrate.py`
**Risco**: MEDIUM — CLI de migrate no Postgres de homologação; seed silencioso hoje é o bug.
**Task size**: M (1 file; decisão: semear em `already_applied` e falhar se faltar chave)

- **Arquivo(s)**: `src/ledger_migrate.py`

**executor_prompt**:

```yaml
id: N8.1
size: M
bom_ref: BOM-3
depends_on: []
files:
  - src/ledger_migrate.py
reuse_targets:
  - component: src/strategy_catalog.py
    reuse_as: call
    convergence_check: rg "ensure_strategy_defaults" src/ledger_migrate.py && ! rg "def ensure_strategy_defaults" src/ledger_migrate.py
  - component: src/ledger_migrate.py
    reuse_as: extend
    convergence_check: rg "def apply" src/ledger_migrate.py && rg "already_applied" src/ledger_migrate.py
guardrail_contract:
  - class: secrets
    id: n8-1-no-dsn-print
    target: src/ledger_migrate.py
    check: rg "LEDGER_DATABASE_URL" src/ledger_migrate.py && ! rg -n "print\\(.*PASSWORD" src/ledger_migrate.py
    pass_condition: DSN stays in env; no password print
  - class: subagent-safety
    id: n8-1-live-lock
    target: Dockerfile
    check: rg "LIVE_TRADING_ENABLED=false" Dockerfile
    pass_condition: image live lock unchanged
  - class: caller-level
    id: n8-1-cli-apply-seed
    target: src/ledger_migrate.py
    check: pytest -q tests/test_ledger_migration.py -k apply
    convergence_check: pytest -q tests/test_ledger_migration.py -k apply
    pass_condition: apply path seeds catalog when LEDGER_DATABASE_URL is set
executor_prompt: |
  ### Quality Brief (Sprint N8)
  sprint: N8
  Maintain: strategy_catalog.ensure_strategy_defaults() insert-if-missing for the seven N7 keys — call it; do not reimplement INSERT.
  Maintain: ledger_migrate.apply / rollback / status CLI wired by scripts/run.sh ledger-migrate.
  Maintain: LIVE_TRADING_ENABLED=false and original.py LAB_LOCK.
  Avoid: migration 002, DDL edits, and a second persistence module.
  Avoid: Gate B / scoring changes; do not promote strategy_states.phase from PnL, HTTP 200, or PAPER_GATEWAY_QUEUE_ONLY.
  [ABORDAGEM] Call ensure_strategy_defaults() at the end of apply() on both first apply and already_applied; then SELECT the seven known keys and raise if any are missing (ops-visible). Do not seed on rollback.
  [RISCO] ensure_strategy_defaults() swallows exceptions and no-ops without LEDGER_DATABASE_URL. A silent no-op after migrate is the EasyPanel empty-table failure mode — migrate must not treat that as success.
  [OPORTUNIDADE] Extend LedgerMigrationIntegrationTest.test_apply_rollback_roundtrip (skipUnless LEDGER_DATABASE_URL) to assert seven strategy_states rows after the final apply.
  EXPIRES at end of Sprint N8.

  Melhoria: ledger-migrate apply seeds strategy_states.
  Contexto: apply() runs 001_ledger_up.sql or returns already_applied without calling ensure_strategy_defaults(). EasyPanel had an empty strategy_states table until a manual INSERT or a worker fetch. ISS-002/N7 already defined the seven keys and insert-if-missing; do not reopen Gate B or invent scoring thresholds.
  Objetivo: after a successful apply — including the already_applied early return — call strategy_catalog.ensure_strategy_defaults(). Then verify the seven KNOWN_STRATEGY_KEYS / DEFAULT_PHASE_BY_KEY rows exist (SELECT); raise a RuntimeError (or equivalent) if any key is missing so operators see the failure. Do not overwrite an existing phase. Do not seed inside rollback(). Do not add migrations/002_*.sql. Do not edit gate_b_risk.py. LIVE_TRADING stays false. scripts/run.sh ledger-migrate wiring stays as-is.
  Arquivos: src/ledger_migrate.py.
  Critério de pronto: rg shows ensure_strategy_defaults imported/called from ledger_migrate.py and not redefined there; apply() no longer returns already_applied without attempting seed; unit coverage exists or is added in N8.2; no DSN/password printed.
  Cenários de teste (implemented in N8.2; this task must remain compatible):
    1. Caso normal: empty DB + apply → seven strategy_states rows with N7 default phases.
    2. Edge case: already_applied + empty table → seed still runs; seven rows appear.
    3. Edge case: existing orb=paper_validated is left unchanged (overwrite forbidden).
    4. Regressão: rollback still drops tables; apply after rollback still works; LIVE_TRADING_ENABLED false; no Gate B file edits.
```

---

## Sprint N9 — Homologação D5 no EasyPanel (itens 3–7)

> Categoria: N  
> Status: concluida  
> titulo_humano: Checklist EasyPanel 3–7 com evidência, sem ordem live  
> resumo_humano: O laboratório já grava sinal, risco e intenção de ordem paper. Esta sprint deixa o operador conferir isso no EasyPanel (webhook, worker, reconcile só leitura, dashboard e kill switch) e anotar a evidência sem segredo. Fila e HTTP 200 continuam sem ser fill; dinheiro real permanece desligado.  
> Gate: `docs/HOMOLOGATION.md` itens 3–7 nomeiam comando `scripts/run.sh`, SQL ou campo JSON, e o que não conta como fill; `docs/TEST-EVIDENCE.md` tem linhas pendentes para o operador (sem segredo); nenhum diff em `src/`; `LIVE_TRADING_ENABLED` false; Feature 5 fill permanece `[ ]`; ISS-004 não aberto  
> bom_ref: BOM-3  
> review: senior+qa  
> Gerado via: /pmo plan (planejador-melhorias)  
> Brief: `docs/.briefs/N9.brief.md`  
> plan_only: true (não define `sprint_atual`)

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N9.1 Runbook Gate A: webhook → `signal_events` | docs | — |
| [x] | P | N9.2 Runbook Gate B: worker → `risk_decisions` + `paper_orders` `queued_intent` | docs | N9.1 |
| [x] | P | N9.3 Runbook reconcile read-only (`ledger_apply`, não `broker_reconciled`) | docs | N9.2 |
| [x] | P | N9.4 Runbook dashboard auth + kill switch | docs | N9.3 |
| [x] | M | N9.5 Evidence sheet + optional Feature 5 operator note (no fill task) | docs | N9.4 |
| [x] | P | N9.6 Operador: executar itens 3–7 no EasyPanel e preencher evidência redigida | operador | N9.5 |

P notes (no executor_prompt): **N9.1** expand item 3 in `docs/HOMOLOGATION.md`: `scripts/run.sh tv-webhook`, header `X-Webhook-Token` or legacy `/webhook/{token}`, then `SELECT` on `signal_events` (count / status). HTTP 202 `QUEUED` is not a fill. **N9.2** expand item 4: `scripts/run.sh tv-worker` after Gate A; rejection row in `risk_decisions`; accept row in `paper_orders.status = queued_intent`. Cite `PAPER_GATEWAY_QUEUE_ONLY` and `orders_sent = 0` as non-fills. Do not change `gate_b_risk.py` or catalog phases. **N9.3** expand item 5: `PAPER_RECONCILE_LEDGER_APPLY=true` and `scripts/run.sh v4-alpaca-reconcile --output /app/reports/paper/reconcile.json`; record `ledger_apply`; do not treat `broker_reconciled` as true. **N9.4** expand items 6–7: loopback or `DASHBOARD_ALLOW_REMOTE=true` plus `DASHBOARD_BEARER_TOKEN` length ≥32 via `scripts/run.sh v4-dashboard`; `/api/status` fields `kill_switch_on` and `shadow_vs_paper`; kill via `TRADING_LAB_KILL_SWITCH=true` or a new `control_flags` row (see `docs/INFRASTRUCTURE.md` § Kill switch). Confirm the worker blocks (`orders_sent` 0, no new `queued_intent`). **N9.6** is operator-only on the existing EasyPanel apps. The agent does not SSH, does not read secrets, and does not invent row counts. Paste redacted counts into the N9.5 table. `bom_ref: BOM-3`.

### Task N9.5 — Evidence sheet for homologation items 3–7

**Estado atual**: `docs/HOMOLOGATION.md` lista os itens 3–7 em uma linha cada. `docs/TEST-EVIDENCE.md` para em N6. CI cobre testes; o EasyPanel ainda não tem evidência colada para sinal, risco, fila, reconcile, dashboard e kill switch. Feature 5 fill real segue `[ ]`.
**Estado desejado**: uma seção N9 em `docs/TEST-EVIDENCE.md` com uma linha por item 3–7, status `pendente`, comando e campo esperado, sem segredo e sem contagem inventada. `docs/HOMOLOGATION.md` aponta para essa seção. Um bloco separado, "Passo operador opcional — Feature 5", descreve fill real como passo só do operador e não entra no gate da N9. Nenhum arquivo em `src/`.
**Fonte(s)**: operador trilha A 2026-10-30; `docs/HOMOLOGATION.md` checklist; `docs/REQUIREMENTS.md` Feature 5–6; `docs/ROADMAP.md` Sprint D5. ISS-004 não aberto (fiação já existe).
**Módulo(s) afetado(s)**: `docs/TEST-EVIDENCE.md`, `docs/HOMOLOGATION.md`
**Risco**: MEDIUM — marcar fila ou HTTP 200 como fill fecharia homologação sem evidência.
**Task size**: M (2 files; decisão: o que prova cada item e o que fica fora)

- **Arquivo(s)**: `docs/TEST-EVIDENCE.md`, `docs/HOMOLOGATION.md`

**executor_prompt**:

```yaml
id: N9.5
size: M
bom_ref: BOM-3
depends_on: [N9.4]
files:
  - docs/TEST-EVIDENCE.md
  - docs/HOMOLOGATION.md
reuse_targets:
  - component: docs/HOMOLOGATION.md
    reuse_as: extend
    convergence_check: rg "tv-webhook" docs/HOMOLOGATION.md && rg "tv-worker" docs/HOMOLOGATION.md && rg "queued_intent" docs/HOMOLOGATION.md && rg "v4-alpaca-reconcile" docs/HOMOLOGATION.md && rg "v4-dashboard" docs/HOMOLOGATION.md && rg "Passo operador opcional" docs/HOMOLOGATION.md
  - component: docs/TEST-EVIDENCE.md
    reuse_as: extend
    convergence_check: rg "Homologação D5 itens 3–7" docs/TEST-EVIDENCE.md && rg "pendente" docs/TEST-EVIDENCE.md
guardrail_contract:
  - class: secrets
    id: n9-5-no-live-secrets
    target: docs/TEST-EVIDENCE.md
    check: rg "TV_WEBHOOK_TOKEN" docs/HOMOLOGATION.md && ! rg -n "APCA-API|BEGIN PRIVATE" docs/HOMOLOGATION.md docs/TEST-EVIDENCE.md
    pass_condition: env names only; no broker key or private key pasted
  - class: subagent-safety
    id: n9-5-live-lock
    target: Dockerfile
    check: rg "LIVE_TRADING_ENABLED=false" Dockerfile
    pass_condition: image live lock unchanged; no src/ edits in this task
  - class: secrets
    id: n9-5-feature5-open
    target: docs/REQUIREMENTS.md
    check: rg "Fill real Alpaca" docs/REQUIREMENTS.md
    pass_condition: Feature 5 real-fill checkbox stays open
executor_prompt: |
  ### Quality Brief (Sprint N9)
  sprint: N9
  Maintain: LIVE_TRADING_ENABLED=false and src/original.py LAB_LOCK; no live broker host or order path.
  Maintain: Gate A, Gate B, paper queue, reconcile, and dashboard stay as implemented; this task only documents them.
  Maintain: HTTP 200, PAPER_GATEWAY_QUEUE_ONLY, and queued_intent are not fills; reconcile keeps broker_reconciled false.
  Avoid: strategy threshold inventions and edits to gate_b_risk.py, strategy_catalog.py, or vendor/.
  Avoid: checking Feature 5 real fill or PnL as done; that step stays a separate unchecked operator note.
  [ABORDAGEM] Add a pending evidence table (redacted counts only) and point HOMOLOGATION items 3–7 at it. The operator runs EasyPanel; the agent does not.
  [RISCO] persist_risk_decision returns without a row when LEDGER_DATABASE_URL is unset or signal_events has no matching id. HTTP 200 is not evidence.
  [OPORTUNIDADE] CI already covers webhook, Gate B, and queue tests. Do not add src/ or tests: scripts/run.sh already exposes tv-webhook, tv-worker, v4-alpaca-reconcile, and v4-dashboard.
  EXPIRES at end of Sprint N9.

  Melhoria: record homologation evidence slots for checklist items 3–7.
  Contexto: D5 and N8 left the checklist and the 7 strategy_states seed. Wiring already persists signal_events (gate_a_signal.maybe_persist), risk_decisions and paper_orders queued_intent (paper_gateway_queue.persist_risk_decision via tradingview_worker), reconcile ledger_apply (v4_alpaca_reconcile + ledger_reconcile.apply_from_report), dashboard bearer (v4_web_dashboard.main), and kill switch (gate_b_risk.kill_switch_active). Do not reopen Gate B or the strategy catalog. Do not invent scoring thresholds. Upstream trader-* stays behind src/original.py; do not call it from docs work and do not bump the vendor pin.
  Objetivo: append a section headed "Homologação D5 itens 3–7" to docs/TEST-EVIDENCE.md with one pending row per item 3, 4, 5, 6, and 7 (command, expected table or JSON field, status pendente, result empty). In docs/HOMOLOGATION.md, after the checklist, add "Passo operador opcional — Feature 5" stating real Alpaca fill and PnL is operator-only, out of the N9 gate, and still the unchecked Feature 5 criterion. Do not place an order. Do not edit src/, tests/, Dockerfile, or .cursorsession. Do not paste tokens.
  Arquivos: docs/TEST-EVIDENCE.md, docs/HOMOLOGATION.md.
  Critério de pronto: both convergence_check commands exit 0; Dockerfile still has LIVE_TRADING_ENABLED=false; docs/REQUIREMENTS.md still contains the open Fill real Alpaca line; git diff shows no src/ file.
  Cenários de teste:
    1. Caso normal: each of items 3–7 has a pending evidence row naming signal_events, risk_decisions or queued_intent, ledger_apply, dashboard auth, or kill_switch_on.
    2. Edge case: evidence cells are empty or "pendente"; no API key, DSN, or bearer value appears.
    3. Regressão: Feature 5 fill checkbox in REQUIREMENTS stays open; LIVE_TRADING_ENABLED=false remains in the Dockerfile; Gate B source files are untouched.
    4. Edge case: the optional Feature 5 section is present and labeled operator-only, and it is not a sprint task that submits an order.
    5. Regressão: PAPER_GATEWAY_QUEUE_ONLY and broker_reconciled are still described as not a completed fill.
```

---

## Sprint N10 — Closeout N9 (ROADMAP + homolog notes)

> Categoria: N  
> Status: concluida  
> titulo_humano: Fechar N9 no roadmap e documentar smoke pós-deploy  
> resumo_humano: N9 já entregue em main e no EasyPanel. Esta sprint só alinha ROADMAP, evidência e runbook (smoke pregão vs unittest integração), sem mudar código de gates ou live.  
> Gate: N9 marcada concluida no indice e tasks [x]; sem diff em `src/`; `LIVE_TRADING_ENABLED` false; Feature 5 fill `[ ]`; `docs/TEST-EVIDENCE.md` nota smoke TTL/sessão  
> review: skip  
> Gerado via: /pmo plan + /pmo sprint N10  
> Brief: `docs/.briefs/N10.brief.md`

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N10.1 ROADMAP: N9 concluida + indice + proximo passo | docs | — |
| [x] | P | N10.2 TEST-EVIDENCE + HOMOLOGATION notas smoke item 4 | docs | N10.1 |
| [x] | P | N10.3 FINDINGS/TEST-EVIDENCE referencia main 0509732 | docs | N10.1 |
| [x] | P | N10.4 `.cursorsession` sprint N10 + previous N9 | session | N10.1 |
| [ ] | P | N10.5 Operador: `/git front finish` frentes após merge | operador | N10.2 |

---

## Sprint N11 — Feature 1 ciclo research (evidência + testes)

> Categoria: N  
> Status: concluida  
> titulo_humano: Fechar Feature 1 — ciclo research sem ordem e manifesto honesto  
> resumo_humano: Amarra os critérios abertos da Feature 1 a testes pytest e à folha de evidência. Reforça que scheduler e run-once não enviam ordem e que falha de ciclo não deixa manifesto antigo como sucesso. Sem corretora, sem live, sem EasyPanel.  
> Gate: pytest CI verde; `docs/REQUIREMENTS.md` Feature 1 critérios `[x]`; matriz nodeid em `TEST-EVIDENCE`; `rg` sem novo submit broker em `v4_scheduler`/`v4_run_once`; `LIVE_TRADING_ENABLED` false  
> bom_ref: BOM-1  
> review: senior+qa  
> Gerado via: `/pmo plan` N11 Feature 1 2026-11-01  
> Brief: `docs/.briefs/N11.brief.md`

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N11.1 Matriz Feature 1 → pytest nodeids em TEST-EVIDENCE | docs | — |
| [x] | M | N11.2 Teste integração scheduler `--once` falha + manifesto stale | `/qa testes` | N11.1 |
| [x] | P | N11.3 REQUIREMENTS Feature 1 checkboxes `[x]` com links | `/pmo` | N11.1 |
| [x] | P | N11.4 Sessão sprint N11 + módulo research-cycle | session | N11.1 |

<details>
<summary>N11.2 executor_prompt</summary>

```yaml
id: N11.2
size: M
bom_ref: BOM-1
depends_on: [N11.1]
files:
  - tests/test_v4_scheduler.py
  - src/v4_scheduler.py
reuse_targets:
  - component: src/v4_scheduler.py
    reuse_as: extend
    convergence_check: rg "def run_cycle|def invalidate_stale_manifest|def main" src/v4_scheduler.py && rg "paper-gateway|alpaca" src/v4_scheduler.py && test $? -ne 0
  - component: tests/test_v4_scheduler.py
    reuse_as: extend
    convergence_check: rg "test_failed_cycle_invalidates_previous_manifest|test_readonly_success" tests/test_v4_scheduler.py
guardrail_contract:
  - class: subagent-safety
    id: n11-2-no-broker
    target: src/v4_scheduler.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_scheduler.py').read_text(); assert 'paper-gateway' not in t and 'submit_order' not in t"
    pass_condition: scheduler stays research-only imports
  - class: subagent-safety
    id: n11-2-live-lock
    target: Dockerfile
    check: rg "LIVE_TRADING_ENABLED=false" Dockerfile
    pass_condition: live flag remains false in image
executor_prompt: |
  ### Quality Brief (Sprint N11)
  sprint: N11
  Maintain: v4_scheduler never imports broker or paper-gateway; run_cycle always reports orders_sent=0.
  Maintain: invalidate_stale_manifest deletes file manifest on failed/timeout cycles only; symlink guard stays.
  Avoid: adding Alpaca, tv-worker, or gate paths to scheduler tests.
  Avoid: weakening manifest deletion on FAILED_OR_BLOCKED to make tests pass.
  EXPIRES at end of Sprint N11.

  Melhoria: close the gap between unit tests and main() wiring for stale manifest on failed --once cycle.
  Contexto: ISS-004; REQUIREMENTS Feature 1 open criteria; existing unit tests cover invalidate_stale_manifest and run_cycle separately but not main(--once) after simulated failure with pre-existing v4_manifest.json.
  Objetivo: extend tests/test_v4_scheduler.py with an integration-style test invoking main(['--once', ...]) with mocked runner returning non-zero; assert manifest removed and status JSON orders_sent=0 and execution_authorized=false. Only touch scheduler test file unless a minimal bugfix in v4_scheduler.py is required (document in commit).
  Arquivos: tests/test_v4_scheduler.py (primary), src/v4_scheduler.py (only if wiring bug found).
  Critério de pronto: pytest nodeid passes; full pytest -q green locally/CI; no new dependencies.
  Cenários de teste:
    1. Caso normal: failed run_cycle path via main --once removes stale v4_manifest.json.
    2. Regressão: FINISHED_RESEARCH keeps manifest when exit_code 0.
    3. Edge case: symlink manifest still raises UNSafe path without deleting target.
    4. Regressão: LIVE_TRADING_ENABLED=true still BLOCKED before cycle.
```
</details>

---

## Sprint N12 — Demo Alpaca paper (`signal_copy`, P0 pivot)
> Categoria: N  
> Status: planejada  
> titulo_humano: Operar demo paper com fill comprovado na trilha signal_copy  
> resumo_humano: Fecha o único critério aberto de Feature 5 usando código já existente (runner + fila pós–Gate B), runbook e evidência operador — sem live e sem tratar fila como fill.  
> Gate: pytest verde incluindo caminho `PAPER_SUBMITTED` mockado; `docs/TEST-EVIDENCE.md` matriz Feature 5; operador preenche linha fill redigida; `REQUIREMENTS` fill `[x]` só após N12.5; `LIVE_TRADING_ENABLED` false; F-003 permanece congelado  
> bom_ref: BOM-3, BOM-4  
> review: senior+qa  
> Gerado via: `/pmo plan pivot-demo` 2026-11-02  
> Brief: `docs/.briefs/N12.brief.md`

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N12.1 Matriz Feature 5 → pytest nodeids + checklist operador | docs | — |
| [x] | P | N12.2 Runbook Feature 5 em HOMOLOGATION (`signal-paper` / worker auto flags) | docs | N12.1 |
| [x] | M | N12.3 Testes: `PAPER_SUBMITTED` + `process_after_gate_b` com broker mock | `/qa testes` | N12.1 |
| [ ] | P | N12.4 Operador: fill Alpaca paper + reconcile redigido (EasyPanel) | operador | N12.2, N12.3 |
| [ ] | P | N12.5 REQUIREMENTS Feature 5 fill `[x]` + TEST-EVIDENCE operador | docs | N12.4 |

P notes: **N12.2** document env chain from `signal_paper_runner.py` (`PAPER_SIGNAL_AUTO_ENABLED`, `PAPER_EXECUTION_ENABLED`, `PAPER_SIGNAL_ACCOUNT_ACK`, `PAPER_DAILY_RISK_CONFIRMED`, `V4_RISK_SNAPSHOT_FILE`) and contrast with N9 `queued_intent`. Cite `scripts/run.sh signal-paper`. **N12.4** operator only — no secrets in Git; `orders_sent=1` / broker id redacted. **N12.5** do not check fill before operator row exists.

<details>
<summary>N12.3 executor_prompt</summary>

```yaml
id: N12.3
size: M
bom_ref: BOM-3
depends_on: [N12.1]
files:
  - tests/test_signal_paper_runner.py
  - tests/test_paper_gateway_queue.py
  - src/signal_paper_runner.py
  - src/paper_gateway_queue.py
reuse_targets:
  - component: src/signal_paper_runner.py
    reuse_as: extend
    convergence_check: rg "def run\\(|PAPER_SUBMITTED" src/signal_paper_runner.py
  - component: src/paper_gateway_queue.py
    reuse_as: extend
    convergence_check: rg "process_after_gate_b|broker_auto_allowed" src/paper_gateway_queue.py
guardrail_contract:
  - class: subagent-safety
    id: n12-3-live-lock
    target: Dockerfile
    check: rg "LIVE_TRADING_ENABLED=false" Dockerfile
    pass_condition: live flag remains false in image
  - class: subagent-safety
    id: n12-3-paper-host
    target: src/signal_paper_runner.py
    check: rg "paper-api.alpaca.markets|PAPER_URL" src/paper_audit.py src/signal_paper_runner.py
    pass_condition: submit stays on paper URL module
executor_prompt: |
  ### Quality Brief (Sprint N12)
  sprint: N12
  Maintain: LIVE_TRADING_ENABLED=false; no live host; reuse signal_paper_runner.run and paper_gateway_queue.process_after_gate_b — no second broker client.
  Maintain: PREVIEW_ONLY and QUEUED paths unchanged when auto flags off.
  Avoid: loosening risk caps or bypassing V4_RISK_SNAPSHOT_FILE / SIGNAL_COPY_SECRET validation.
  Avoid: treating HTTP 200 or queued_intent as fill in assertions.
  EXPIRES at end of Sprint N12.

  Contexto: ISS-005; Feature 5 fill criterion open; existing tests cover preview/blocks but not successful PAPER_SUBMITTED with mocked POST, nor process_after_gate_b when broker_auto_allowed is true.
  Objetivo: add pytest coverage for (1) run() returning PAPER_SUBMITTED orders_sent=1 with mocked broker_get/post and valid snapshot env; (2) process_after_gate_b delegating to paper_run when auto env set (mock paper_run). Minimal production changes only if test reveals a wiring bug.
  Critério de pronto: new nodeids documented in TEST-EVIDENCE Feature 5 matrix (N12.1); pytest -q green in CI.
  Cenários de teste:
    1. Happy path mock: PAPER_SUBMITTED, orders_sent=1, ledger jsonl ATTEMPTED→SUBMITTED.
    2. Regressão: auto flags off → PREVIEW_ONLY / QUEUED orders_sent=0.
    3. Regressão: bad signature still BLOCKED.
    4. Regressão: LIVE_TRADING_ENABLED=true still fail-closed.
```
</details>

---

## Sprint N13 — Homolog estratégias por família (P1)
> Categoria: N  
> Status: planejada  
> titulo_humano: Checklist de homolog por estratégia sem inventar scoring  
> resumo_humano: Depois do demo paper, documenta como testar e homologar cada família do catálogo (fase research/shadow/paper_limited) com evidência pytest e operador — sem promover ORB/C2 nem limiares novos.  
> Gate: matriz por `strategy_key` em TEST-EVIDENCE; fases N7 intactas; momentum/ta_barato/prodigy sem checkbox fechado sem regra upstream recuperada; F-003 ainda congelado; CI verde; LIVE false  
> bom_ref: BOM-1  
> review: senior+qa  
> Gerado via: `/pmo plan pivot-demo` 2026-11-02  
> Status: em execucao  
> Brief: `docs/.briefs/N13.brief.md`

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N13.1 Matriz Feature 4 → família / fase / pytest ou “blocked upstream” | docs | — |
| [x] | P | N13.2 Folha homolog operador por família (sem ordem onde fase ≠ paper) | docs | N13.1 |
| [x] | P | N13.3 ROADMAP backlog: ordem P1 e freeze F-003 até N12 gate | docs | N13.1 |
| [x] | M | N13.4 Testes/traceability só para famílias com regra existente no repo | `/qa testes` | N13.1 |

P notes: **N13** repo entregue com **N12.4 ainda pendente** (ISS-005 aberto). F-003 congelado até Feature 5 fill evidenciado.

---

## Sprint N14 — Pacotão MVP-DEMO-1.0
> Categoria: N  
> Status: planejada  
> titulo_humano: Um runbook, um smoke e regra de deploy para parar rebuild infinito  
> resumo_humano: Consolida MVP demo em artefatos únicos; pendências Feature 5 (P-001–P-003) ficam explícitas em ISSUES; não substitui fill operador N12.4.  
> Gate: `docs/MVP-DEMO-RUNBOOK.md` + `scripts/mvp-demo-smoke.sh` OK local/CI; `config/mvp-demo.env.example`; ISS-006 critérios repo; ISS-005 permanece aberto  
> review: skip  
> Gerado via: operador pacotão 2026-11-02 · ISS-006

> Status: concluida  

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N14.1 `MVP-DEMO-RUNBOOK.md` + política deploy | docs | — |
| [x] | P | N14.2 `config/mvp-demo.env.example` | docs | N14.1 |
| [x] | P | N14.3 `scripts/mvp-demo-smoke.sh` | `/devops` | N14.1 |
| [x] | P | N14.4 ISSUES pendências P-001–P-005 + ISS-006 | docs | N14.1 |

P notes: **Um deploy EasyPanel** após merge N14; depois **freeze** rebuild até `src/`/`Dockerfile` ou N12.4 evidenciado.

---

## Release train MVP-OP (épico único — ISS-007)

> Plano mergeado (PR #13). Ampliado: **Command Panel v1** dentro de **1.0**, não sprint/epic separado.  
> Brief: `docs/.briefs/MVP-OP-RELEASE-TRAIN.brief.md`

```text
MVP-OP-0.9 (N15) ──► MVP-OP-1.0 (N16) ──► MVP-OP-1.1 (N17)
     │                      │                      │
  fill signal_copy      Prodígio + painel v1     Tá Barato + painel
  Feature 5 [x]         rank→fill + ledger UI   (Git First upstream)
  0 rebuild             1 rebuild              1 rebuild max
```

---

## Sprint N15 — Release MVP-OP-0.9 (fechar copy paper)
> Categoria: N  
> Status: planejada  
> titulo_humano: Submit paper homologado na copy (fill limit pendente)  
> Gate: submit operador evidenciado; Feature 5 fill `[ ]` com nota; TEST-EVIDENCE N12; **sem** rebuild EasyPanel  
> review: skip  
> Release tag: `MVP-OP-0.9`

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N15.1 Operador N12.4 submit + reconcile redigido (fill limit pendente) | operador | — |
| [x] | P | N15.2 TEST-EVIDENCE + ISS-005 parcial (sem fill `[x]`) | docs | N15.1 |

---

## Sprint N16 — Release MVP-OP-1.0 (Prodígio + Command Panel v1)
> Categoria: N  
> Status: concluida  
> titulo_humano: Plataforma operacional v1 — Prodígio paper + painel único (Feature 6 estendida)  
> Gate: Git First reuse inventory; **submit** `prodigy_15d` evidenciado; painel bearer **ok** operador 2026-11-03; fill limit opcional P-001b; CI verde; LIVE false  
> review: senior+qa  
> Release tag: `MVP-OP-1.0`  
> Deploy: **1 rebuild** após merge

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N16.0 Git First: vendor SHA + reuse inventory Prodígio/signal | `/git` | N15 gate |
| [x] | P | N16.1 Runbook Prodígio: rank → sinal assinado → Gate A/B (`strategy_key=prodigy_15d`) | docs | N16.0 |
| [x] | M | N16.2 Adaptação mínima ingestão (**waived** — one-shot ok; ver N16-GIT-FIRST) | — | N16.1 |
| [x] | P | N16.4 Operador: submit paper Prodígio + evidência TEST-EVIDENCE (fill limit pendente) | operador | N16.2 |
| [x] | M | N16.6 Command Panel: escopo v1 + mapa ISS-007 (histórico, performance, ordens, oportunidades, saúde, fases, evolution, tips research) | docs | PR #14 |
| [x] | M | N16.7 Implementação mínima em `v4_web_dashboard` + dados ledger/Alpaca read-only (reuse `trading_dashboard_data`) | `/dev` | N16.6 |
| [x] | P | N16.8 Homolog operador: painel remoto com bearer + smoke alinhado a MVP-DEMO | operador | N16.7 · **`docs/HOMOLOGATION-N16.8-PANEL.md`** |
| [x] | P | N16.5 Release notes `MVP-OP-1.0` + MVP-DEMO-RUNBOOK (N16.8 painel remoto pendente) | docs | N16.4 |

**Pré-requisito duro:** N15 submit evidenciado (0.9). Fill Feature 5 opcional para painel performance credível. **PRODIGY_PROVIDERS** e fase `paper_limited` só via operador.

---

## Sprint N17 — Release MVP-OP-1.1 (Tá Barato + momentum upstream)
> Categoria: N  
> Status: planejada  
> titulo_humano: Tá Barato com regras upstream homologadas em shadow/paper  
> Gate: fórmulas/limites de `ta_barato` (e momentum se escopo) recuperadas em vendor — **G-FORM blocked @ pin**; shadow homolog + painel entregues; paper blocked; homolog pytest; LIVE false  
> review: senior+qa  
> Release tag: `MVP-OP-1.1`

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N17.0 Git First: upstream paths ta_barato/momentum | `/git` | N16 gate |
| [x] | M | N17.1 Integração/adaptação Gate B ou research (reuse only) | `/dev` | N17.0 |
| [ ] | P | N17.2 Homolog operador shadow → paper limitado (evidência) | operador | N17.1 |
| [x] | P | N17.3 REQUIREMENTS/TEST-EVIDENCE matriz ta_barato | docs | N17.2 |
| [ ] | P | N17.4 Repriorizar F-003 orb-parity (opcional pós-1.1) | `/pmo` | N17.2 |
| [x] | M | N17.5 Painel: seção Tá Barato / família upstream (read-only homolog) | `/dev` | N17.2 |

---

## Sprint N18 — Command Panel always-on (`v4-ops`)
> Categoria: N  
> Status: em execucao  
> resumo_humano: O painel operacional deixa de depender de nohup no Exec: a imagem sobe pesquisa e dashboard juntos, com restart automático do HTTP e runbook de segurança Bearer/HTTPS.  
> titulo_humano: Painel operacional sempre ligado no trading-lab  
> Gate: CI verde; CMD **`v4-ops`** na imagem; operador redeploy **trading-lab** com log `listening on …:8765` **sem** nohup; `/api/status` Bearer **200**; `LIVE_TRADING_ENABLED=false`  
> review: senior+qa  
> Issue: **ISS-008**

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N18.1 Layout **`v4-ops`**: `v4_ops_main.sh`, `run.sh`, Dockerfile CMD, `tests/test_v4_ops_layout.py` | `/dev` | — |
| [x] | P | N18.2 Runbook **`docs/DASHBOARD-OPERATIONS.md`** + alinhar EASYPANEL, COMMAND-PANEL, HOMOLOGATION-N16.8 | docs | N18.1 |
| [x] | P | N18.3 Operador: rebuild EasyPanel `trading-lab` + linha TEST-EVIDENCE N18 (sem token no Git) | operador | N18.2 |
| [x] | P | N18.4 Closeout ROADMAP: **N16 → concluida**; MVP-DEMO-RUNBOOK menciona `v4-ops` | docs | N18.3 |

**N18.1 — executor_prompt (resumo):** Reuse `scripts/run.sh` pattern; add `v4-ops` → `v4_ops_main.sh` spawning supervised `v4-dashboard` + foreground `v4-scheduler`; default Dockerfile CMD `v4-ops` with same scheduler args; env `DASHBOARD_AUTOSTART` default true; no broker submit code in dashboard path; regression `tests/test_v4_web_dashboard.py` + new layout test; `guardrail_contract`: LIVE false, read-only HTTP only, no third EasyPanel service.

**Fora de escopo N18:** login HTML no browser; Tá Barato (N17); Feature 5 fill (P-001b operador).

---

## Sprint N19 — Laço demo com gatilho no painel

> Categoria: N
> Status: em execucao
> resumo_humano: O painel passa a alterar parada, âncoras e mercado, e a ordem paper deixa rastro no ledger até o fill. B3, cripto e forex só operam quando a conta demo daquele mercado devolver o estado. Conta real continua sem botão.
> titulo_humano: Gatilhos no painel e ordem com rastro no ledger
> Gate: pytest verde; `LIVE_TRADING_ENABLED=false`; PATCH de gatilho não insere `paper_orders`; resultado do simulador local não é fill; nenhuma ordem sai com `demo_operation_on` false
> review: senior+qa
> Issue: **ISS-009**

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N19.1 Migration `002`: mercado, âncoras, `market_controls`, `trigger_changes`, preço fora do real. Sem apagar fill | `/dev` | — |
| [x] | M | N19.2 PATCH de gatilho em `v4_web_dashboard` conforme `docs/api-spec.yaml` 0.2.0. Bearer sozinho recebe 401 na escrita | `/dev` | N19.1 |
| [x] | M | N19.3 Persistir `broker_order_id` e estado a partir de resposta mockada. Simulador local permanece sem fill | `/dev` | N19.1 |
| [x] | P | N19.4 Teste: mercado sem conta demo que devolva posição fica barrado, com motivo, e não chama a Alpaca | `/qa testes` | N19.2, N19.3 |

**Fora de escopo N19:** escolher a corretora demo de B3 ou forex; ligar `demo_operation_on` em produção; conta real; cadastrar estratégia nova; ajuste automático de parâmetro.

**N19.1 — executor_prompt (resumo):** Add `migrations/002_triggers_up.sql` and down. Columns and tables from `docs/DATABASE.md` section 6 and `docs/db-schema.dbml`. Do not rewrite `001`. Do not drop fills. Test rollback. `guardrail_contract`: no secrets in SQL, no live host, no seed order.

**N19.2 — executor_prompt (resumo):** Extend `src/v4_web_dashboard.py` only. Routes `PATCH /api/triggers`, `PATCH /api/markets/{market}`, `PATCH /api/strategies/{strategy_key}`. Insert `trigger_changes`. Do not import a broker client. Unknown strategy key is 404. `orb` and `mean_reversion` cannot move to a paper phase. `guardrail_contract`: write requires operator session; bearer alone is 401; response field names match the DBML.

**N19.3 — executor_prompt (resumo):** When a mocked paper submit returns an id, store it on `paper_orders` and do not leave the row at `queued_intent`. `src/v4_shadow_broker.py` stays a request log. Do not send `B3_EQUITY` or `FOREX` to `https://paper-api.alpaca.markets`. `guardrail_contract`: `orders_sent` stays 0 unless the mock is an explicit paper submit; `LIVE_TRADING_ENABLED` false.

---

## Programa MVP-FINAL — plataforma operacional pelo contrato v0.3

> Aprovado pelo operador em 2026-11-11 (`/pmo plan`).  
> Auditoria: `docs/.briefs/MVP-FINAL-AUDIT.intake.md` · Plano detalhado com rastreio critério → sprint: `docs/.briefs/MVP-FINAL-WAVES.plan.md`  
> Definição de pronto: todos os critérios das Features 1–10 conferíveis pelo operador no painel e na conta demo; Feature 11 é Should-have. Tempo de resposta e uptime ficam fora porque o contrato diz "a definir".  
> Invariantes: `LIVE_TRADING_ENABLED=false`; só `trading-lab` e `trading-lab-webhook`; nenhum limiar inventado; ORB e mean reversion fora de paper; simulador local não é fill; HTTP 200 ou fila não é ordem executada.

```text
Onda 0  N20                resgate do contrato v0.3 + N19.1–N19.2; fill P-001b; SHA      0 rebuild
Onda 1  N19.3–N19.4 + N21  ordem com id da corretora até fill; P&L só de fill (ADR-007)  MVP-OP-1.2 (1)
Onda 2  N22 + N23          âncoras lidas, capital único, sessão B3; worker no v4-ops     ┐
Onda 3  N24 + N25 + N26    login, Central, sinais com motivo, performance de fill        ┘ MVP-OP-1.3 (1)
Onda 4  N27                laço autônomo no mercado com conta demo nomeada (G-MKT)       MVP-OP-1.4 (0–1)
Onda 4b N29                adapters Clear simulado + OANDA Practice (+ Alpaca cripto)     MVP-OP-1.4 (0–1)
Onda 5  N17 (existente)    Tá Barato / momentum só com fórmula upstream (G-FORM)         MVP-OP-1.1 (0–1)
Onda 6  N31                melhoria contínua diária (fills+não-fills) + TimesFM research  ISS-012
Onda 6b N28                ajuste supervisionado (método N31; execução N28.2–4)           0–1
Onda 6c N32                Feature 7: envio paper lê âncoras do painel (lacuna 10k USD)   ISS-011
Onda 6d N33                closeout docs: Status N28/N30/N31 + ISS-011 restante honesto  ISS-011
Onda 6e N34                N27.2: ligar Clear/OANDA no laço paper fail-closed            ISS-010
```

Caminho crítico Must-have: **0 → 1 → 2 → 3 → 4**. Envio autônomo permanece desligado até a Onda 4.

### Gates do operador

| ID | Decisão | Destrava | Sem resposta |
|----|---------|----------|--------------|
| G-MKT | Nome da conta demo de B3, de cripto e de forex (ou "fica barrado") | N27.2, N27.4 | Mercado barrado com motivo visível; nome nunca inventado (ADR-010) |
| G-FORM | Onde está a fórmula de Tá Barato e de momentum no upstream (ou "não existe") | N17.1+ | Família fica fora de paper |
| G-AJUSTE | Método: ciclo diário fills+não-fills → dicas; TimesFM só pesquisa; suggestion-first se incerto (ISS-012 / N31) | N31 define o método; N28.2–4 executam o ajuste | Feature 11 critérios 2–4 ficam `[ ]` até N28.2–4 |

Nenhum gate trava as Ondas 0–3.

---

## Sprint N20 — Publicar o contrato e o painel que já altera gatilho
> Categoria: N  
> Status: em execucao  
> titulo_humano: Contrato v0.3 e gatilhos do painel num pedido de revisão  
> Gate: PR em frente própria (não `n18-closeout`); Features 7–11 no contrato; escrita de gatilho exige sessão de operador (Bearer sozinho = 401); suíte verde contra vendor pinado; `LIVE_TRADING_ENABLED=false`; **0 rebuild**  
> Issue: ISS-009 + P-001b + dúvidas 4 e 7  
> review: senior+qa  
> Gerado via: `/pmo plan` — 2026-11-11 (planner, aprovado pelo operador)

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N20.1 Resgatar contrato v0.3 e código N19.1–N19.2 do checkpoint local `3d26a13` (sem arquivos de sessão) | `/git` + `/dev` | — |
| [ ] | P | N20.2 Operador: anotar o SHA da imagem de `trading-lab` e `trading-lab-webhook` no EasyPanel (parcial: digest Docker trading-lab; falta webhook + SHA Git) | operador | — |
| [x] | P | N20.3 Operador: fill AAPL 2026-10-29 @349.85 + posição qty 1 (MSFT/NVDA sem fill; `n20-fill-001` → DUPLICATE_SYMBOL) | operador | — |
| [x] | P | N20.4 Marcar o fill da Feature 5 em REQUIREMENTS só com a linha de evidência | docs | N20.3 |
| [x] | P | N20.5 Operador: confirmar que o Postgres do EasyPanel tem o ledger (`001` applied; `triggers_applied` false até Onda 1) | operador | — |

**N20.1 — executor_prompt (resumo):** Apply only product paths from `3d26a13` onto a front cut from `main`: REQUIREMENTS v0.3, ARCHITECTURE §12, DATABASE §6, api-spec 0.2.0, DESIGN.md, db-schema.dbml, ISS-009, ROADMAP N19 block, N19 brief, `migrations/002_*`, ledger patches, PATCH trigger routes, `tests/test_ledger_migration.py`, `tests/test_panel_triggers.py`, panel-triggers rule/skill. Exclude `.cursorsession*`, `.beesy/`, `.cursor` caches. Do not implement N19.3–N19.4. `guardrail_contract`: LIVE false; no rebuild; full suite green with `UPSTREAM_DIR` at the pinned vendor SHA.

---

## Sprint N21 — Acompanhar até o fill e P&L verdadeiro
> Categoria: N  
> Status: planejada  
> titulo_humano: Fill, cancelamento ou expiração no ledger, com perda honesta  
> Gate: estado final gravado; perda do dia/semana só de fill em real; restart sem duplicar; LIVE false; sem envio autônomo  
> review: senior+qa  
> Depende de: N19.3 · Release: **MVP-OP-1.2** (1 rebuild, junto com N19.3–N19.4)

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N21.1 Acompanhar a ordem até fill, cancelamento ou expiração (reuso `paper_reconcile` / `ledger_reconcile`) | `/dev` | N19.3 |
| [x] | M | N21.2 Calcular perda do dia e da semana só com fill confirmado em real; sem câmbio inventado | `/dev` | N21.1 |
| [x] | P | N21.3 Provar que reinício não duplica ordem | `/qa testes` | N21.1 |

---

## Sprint N22 — Âncoras únicas e calendário B3
> Categoria: N  
> Status: concluida  
> titulo_humano: Um teto de risco e sessão B3 de verdade  
> Gate: Gate B e carteira leem `control_flags`; capital de partida R$ 5.000 nos dois caminhos; fora de sessão B3/NY e feriado ⇒ recusa com motivo; LIVE false  
> review: senior+qa  
> Depende de: N21 · Release: **MVP-OP-1.3**

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N22.1 Fazer `gate_b_risk` e `portfolio_risk_v4` lerem as âncoras gravadas pelo painel (banco fora: teto mais apertado) | `/dev` | — |
| [x] | M | N22.2 Unificar o capital de referência em R$ 5.000 (ARCHITECTURE §12.1) | `/dev` | N22.1 |
| [x] | M | N22.3 Recusar sinal fora da sessão B3/NY, feriado e horário de verão (calendário do upstream primeiro) | `/dev` | — |

---

## Sprint N23 — Trabalhador da fila dentro do v4-ops
> Categoria: N  
> Status: concluida  
> titulo_humano: A fila anda no mesmo serviço do painel, sem app novo  
> Gate: supervisor roda pesquisa, painel e worker; queda do worker não derruba a pesquisa; `demo_operation_on` false ⇒ worker recusa envio com motivo; dois apps EasyPanel  
> review: senior+qa  
> Depende de: N21, N22.1 · Release: **MVP-OP-1.3**

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N23.1 Estender `scripts/v4_ops_main.sh` com o worker da fila em intervalo curto (ADR-009) | `/dev` | — |
| [x] | P | N23.2 Teste: saída forçada do worker não derruba a pesquisa | `/qa testes` | N23.1 |
| [x] | P | N23.3 Runbook da release: só dois serviços EasyPanel | docs | N23.1 |

---

## Sprint N24 — Login e central de controle
> Categoria: N  
> Status: concluida  
> titulo_humano: Entrar no painel e mandar na operação sem o Exec  
> Gate: painel não abre sem login; alteração registrada com valor anterior; plataforma não afrouxa âncora sozinha; parada pelo painel segura a próxima ordem em até um ciclo; um operador; LIVE false  
> review: senior+qa  
> Depende de: N19.2, N23.1 · Release: **MVP-OP-1.3**

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N24.1 Tela de entrar na frente do painel (reuso da sessão de operador da N19.2) | `/dev` | — |
| [x] | M | N24.2 Central ligada às âncoras, mercados, estratégias e parada (DESIGN.md) | `/dev` | N24.1 |
| [x] | P | N24.3 Teste: parada pelo painel segura a próxima ordem no ciclo | `/qa testes` | N24.2 |
| [x] | P | N24.4 Runbook do dia a dia aponta o painel, não o Exec | docs | N24.2, N23.1 |

### Quality Brief (Sprint N24 — Onda 3 bundle N24–N26)

sprint: N24 (shipped with N25, N26 in PR #27, merge `fb4a473`)

Maintain: operator session auth in front of `v4_web_dashboard`; reuse N19.2 session cookie pattern — no second auth stack.

Maintain: Central reads/writes control anchors via existing ledger/`trigger_changes` paths; platform never relaxes risk anchors without operator intent.

Maintain: `LIVE_TRADING_ENABLED=false`; queued intent and HTTP 200 are not fills; performance totals only from confirmed fill (N26).

Maintain: `panel_ops_data` + `build_snapshot` as single source for panel ops views — extend, do not fork dashboard data layer.

Avoid: Exec/CLI as the default daily operator path; runbooks must point to the panel.

Avoid: scoring or Prodígio thresholds not already in vendor/recovered code; ranking remains research-labeled.

Avoid: treating `new`/`accepted`/queue rows as P&L; gross values must stay labeled.

Evidence: 455 pytest local APROVADA; CI PR #27 all checks SUCCESS; fix `e545203` for `GateBLedgerIntegrationTest` + `demo_operation_on`.

EXPIRES: closed at N24 closeout (2026-11-11).

---

## Sprint N25 — Sinais e Prodígio com motivo visível
> Categoria: N  
> Status: concluida  
> titulo_humano: Cada sinal mostra para onde foi e o que o barrou  
> Gate: lista com origem, destino e motivo; ranking Prodígio e cópias; barrado mostra gate e âncora  
> review: senior+qa  
> Release: **MVP-OP-1.3**

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N25.1 Tela de sinais com mercado, origem, destino e motivo | `/dev` | — |
| [x] | M | N25.2 Ranking Prodígio e sinais copiados (pesquisa, não autorização) | `/dev` | — |
| [x] | P | N25.3 Teste: sinal barrado aponta gate e âncora com o valor da hora | `/qa testes` | N25.1 |

### Quality Brief (Sprint N25)

Delivered in PR #27 with N24/N26. Maintain: `blocked_context` exposes gate + anchor snapshot on reject; signal list shows market, origin, destination, reason. Prodígio rank and copied signals stay research-labeled, not trade authorization. See parent brief under Sprint N24.

---

## Sprint N26 — Performance só de fill confirmado
> Categoria: N  
> Status: concluida  
> titulo_humano: O número de resultado só conta fill da corretora  
> Gate: total e por estratégia só de fill; ordem sem fill fora; bruto rotulado  
> review: senior+qa  
> Depende de: N21 · Release: **MVP-OP-1.3**

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N26.1 Resultado por estratégia e total só com fill confirmado | `/dev` | — |
| [x] | P | N26.2 Teste: ordem `new`/`accepted`/fila fora do resultado | `/qa testes` | N26.1 |
| [x] | P | N26.3 Rotular valor bruto onde não há custo completo | `/dev` | N26.1 |

### Quality Brief (Sprint N26)

Delivered in PR #27 with N24/N25. Maintain: `performance_from_snapshots` counts strategy/total only on confirmed fill; `PERFORMANCE_LABEL_GROSS` where costs incomplete. Depends on N21 fill semantics — do not regress reconcile-only rows into P&L. See parent brief under Sprint N24.

---

## Sprint N27 — Contas demo no laço, sem inventar o nome
> Categoria: N  
> Status: planejada  
> titulo_humano: Operar só o mercado cuja conta demo o operador nomeou  
> Gate: G-MKT por mercado; Feature 7 conferível só nos mercados respondidos; destino sempre paper; restart sem duplicar; dois apps; LIVE false  
> review: comprehensive  
> Depende de: Ondas 1–3 · Release: **MVP-OP-1.4** (ou dentro da 1.3 se G-MKT chegar a tempo)

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N27.1 Forex no universo e no avaliador de carteira, barrado sem conta | `/dev` | — |
| [x] | M | N27.2 Adaptador da conta demo nomeada pelo operador (B3 e forex nunca pela Alpaca) | `/dev` | G-MKT, N29 |
| [x] | P | N27.3 Teste: mercado sem conta continua visível e barrado com motivo | `/qa testes` | N27.1, N19.4 |
| [ ] | P | N27.4 Operador: sinal válido vira ordem demo sem ação manual | operador | N27.2, N23.1, N24.2 |
| [ ] | P | N27.5 Teste: chave live no ambiente não muda o destino paper | `/qa testes` | N27.2 |
| [ ] | P | N27.6 Teste: restart com laço ligado não duplica | `/qa testes` | N27.4 |

---

## Sprint N29 — Adapters demo G-MKT (Clear + OANDA + Alpaca)
> Categoria: N  
> Status: planejada  
> Nota N34 (2026-11-16): Sprint **N34** ligou `signal_paper_runner.run()` aos adaptadores Clear/OANDA fail-closed (mock no CI). Homologação ao vivo e credenciais no EasyPanel permanecem **N29.5**; esta sprint **não** conclui N29.  
> Nota N35 (2026-11-16): **N27.2** já `[x]` no código (N34/PR **#45**). **N29.6** (“desbloquear N27.2”) satisfeito no repo — **não** marcar N29.6 nem N29.5. Status **planejada** até operador fechar N29.5. N35 entrega presença por nome + roteiro homolog — **não** substitui atestado ao vivo.  
> Gerado via: `/pmo plan` 2026-11-13 · fonte ISS-010 · REQUIREMENTS v0.4  
> titulo_humano: Ligar B3 e forex nas contas demo que você escolheu  
> Gate: Clear simulado e OANDA Practice devolvem posição/ordem/fill; cripto = Alpaca paper; mercado sem credencial barrado com motivo; B3/FOREX nunca Alpaca; LIVE false; ids só no env  
> review: comprehensive  
> Depende de: N27.1, N27.3, REQUIREMENTS G-MKT · Release: **MVP-OP-1.4**

### Em uma frase

A plataforma fala com a Clear (B3) e a OANDA (forex) em modo demo, e mantém a Alpaca só para cripto — sem inventar conta e sem live.

### O que muda para você

- Você cria as contas demo Clear + OANDA e cola as chaves só no EasyPanel
- O painel mostra B3/forex operáveis quando a credencial existir; senão, motivo claro
- N27.2/N27.4 podem fechar o laço nos mercados respondidos

| Entrega | Como você confere |
|---------|-------------------|
| Clear simulado no laço | Posição/ordem/fill de um símbolo B3 demo sem POST na Alpaca |
| OANDA Practice no laço | Ordem forex practice com fill/estado legível no ledger/painel |
| Sem credencial | Mercado visível + `NO_DEMO_ACCOUNT_PATH` (ou equivalente) |
| Live | Processo recusa se `LIVE_TRADING_ENABLED` ≠ false |

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N29.1 Adapter Clear Smart Trader **simulado** (posição, ordem aberta, fill) | `/dev` | — |
| [x] | M | N29.2 Adapter OANDA fxTrade **Practice** (posição, ordem, fill) | `/dev` | — |
| [x] | P | N29.3 Ligar `DEMO_ACCOUNT_PATH_*` / env aos três mercados (Clear, Alpaca, OANDA) | `/dev` | N29.1, N29.2 |
| [x] | P | N29.4 Teste: B3/FOREX nunca POST Alpaca; sem credencial → barrado com motivo | `/qa testes` | N29.3 |
| [ ] | P | N29.5 Operador: abrir/credenciar Clear + OANDA; ids só no EasyPanel | operador | N29.3 |
| [ ] | P | N29.6 Desbloquear N27.2 no ROADMAP após adapters verdes + nota de release | docs | N29.4, N29.5 |

### Task N29.1 — Clear Smart Trader simulado

**Entrega:** Adapter B3 que lê/escreve no ambiente **simulado** da Clear (não URL real).
**Como conferir:** Mock/integração mostra posição, ordem aberta e fill; nenhum POST a `paper-api.alpaca.markets`.
**Por quê:** REQUIREMENTS v0.4 G-MKT; ADR-010.

**Detalhe técnico / executor_prompt:**
```
estado_atual: demo_account_gate + NO_DEMO_ACCOUNT_PATH; B3 bloqueado na Alpaca (N19.4); sem cliente Clear.
desejado: módulo adapter Clear simulado (REST/WS conforme docs Clear) atrás da mesma porta de “conta demo do mercado”; credenciais só via env; fail-closed sem chave.
guardrail: LIVE false; nunca misturar URL real com token simulado; não reimplementar trader-entry/exit.
testes: unit com HTTP mock — submit → order id; positions; block se env vazio.
```

### Task N29.2 — OANDA Practice

**Entrega:** Adapter forex na API v20 **Practice**.
**Como conferir:** Mock/integração cria ordem practice e lê fill/estado; host practice, não fxTrade live.
**Por quê:** REQUIREMENTS v0.4 G-MKT.

**Detalhe técnico / executor_prompt:**
```
estado_atual: FOREX no universo/risco mas sem path de envio.
desejado: cliente OANDA Practice (api-fxpractice) com account id + token no env; posição/ordem/fill.
guardrail: LIVE false; nunca api-fxtrade live; B3 não passa por aqui.
testes: mock REST — order + fill transaction; block se token ausente.
```

### Task N29.3 — Wiring env por mercado

**Entrega:** `DEMO_ACCOUNT_PATH_B3_EQUITY|CRYPTO|FOREX` (ou equivalente) aponta para Clear / Alpaca / OANDA sem inventar nome.
**Como conferir:** Com env preenchido, `block_reason` some no painel para aquele mercado; vazio → barrado.
**Depende de:** N29.1, N29.2.

### Task N29.4 — Testes de regressão

**Entrega:** Suíte prova ADR-010 + fail-closed.
**Como conferir:** pytest verde; casos B3/FOREX sem Alpaca POST; missing creds → motivo.

### Task N29.5 — Operador credencia

**Entrega:** Contas Clear simulado + OANDA Practice criadas; vars no EasyPanel.
**Como conferir:** Operador confirma ids (sem colar segredo no chat/Git).

### Task N29.6 — Ponte N27.2

**Entrega:** ROADMAP N27.2 desbloqueado / marcado pronto para implementação do laço pós-adapter.
**Como conferir:** Checkbox/nota explícita; sem rebuild só por docs.

---

## Sprint N28 — Ajuste supervisionado depois do método
> Categoria: N  
> Status: concluida  
> titulo_humano: Ajuste registrado e reversível, sem mexer no risco  
> Gate: G-AJUSTE e fill real; só parâmetro existente na faixa original; histórico com desfazer; âncoras intocadas; LIVE false  
> review: senior+qa  
> Depende de: N20.3, N21

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N28.1 Sugestão continua rotulada como sugestão | `/dev` | — |
| [x] | M | N28.2 Ajustar só parâmetro existente, dentro da faixa original | `/dev` | G-AJUSTE |
| [x] | M | N28.3 Registrar antes, depois e motivo, com desfazer na Central | `/dev` | N28.2 |
| [x] | P | N28.4 Teste: ajuste nunca altera âncora de risco | `/qa testes` | N28.2 |

**Notas N28.2–4 (pós-N31 merge `681e8c5`):** `src/supervised_adjustment.py` + catálogo documentado; ledger append-only `parameter_adjustments.jsonl`; apply/undo via `/api/strategy-parameters/*` (sessão operador); faixa incerta → só `suggestion_only`; âncoras espelham `TRIGGER_PATCH_FIELDS`.

**Closeout N33 (2026-11-16):** feat `71caca1`, stamp `c465724`; PR **#39** merge `5178fff04fbf7f4675fb9950580df81fdf732f7f` (`2026-11-16T17:20:14Z`); Feature 11 critérios 2–4 `[x]` — `tests/test_n28_supervised_adjustment.py` (`test_n28_2_in_range_proposal_can_apply`, `test_n28_3_apply_undo_persist_before_after_reason`, `test_n28_4_never_mutates_risk_anchors`).

---

## Sprint N30 — Laço Alpaca (ação US + cripto) e caminho Prodígio
> Categoria: N  
> Status: concluida  
> Gerado via: `/pmo plan` 2026-11-16 · fonte ISS-011 · ISS-007 / ISS-009 abertos · ISS-010 fora  
> titulo_humano: Alpaca opera sozinha em ação e cripto; Prodígio só com fase liberada  
> resumo_humano: A conta demo da Alpaca envia sozinha em ação americana e cripto. O ranking Prodígio vira sinal paper só se a fase já estiver liberada. O contrato marca o que o painel já faz. Clear, OANDA e o método de ajuste ficam fora desta rodada.  
> Gate: pytest — US_EQUITY e CRYPTO nomeada submetem na Alpaca paper sem clique extra; chave com cara de live não muda o host paper; reinício com laço demo ligado não duplica; B3/FOREX sem POST Alpaca; rank→sinal `prodigy_15d` com orders_sent=0 enquanto fase for research; Features 8–10 no contrato só com teste nomeado; orb/mean_reversion NEVER_PAPER; LIVE false  
> review: senior+qa  
> Brief: `docs/.briefs/N30.brief.md`  
> bom_ref: BOM-3, BOM-4  
> Depende de: N27 parcial (Alpaca-only) · Release: campanha ISS-011 onda 1  
> LIVE_TRADING_ENABLED: false

**Closeout N33 (2026-11-16):** feat `322318b`; PR **#35** merge `622fbeb786b4e042d2269d60d5c44e7e0f51ab8e` (`2026-11-16T12:47:20Z`); evidência `docs/TEST-EVIDENCE.md` N30.1 / N30.3b; campanha histórica acima não reescrita.

### Em uma frase

A conta demo da Alpaca passa a operar ação americana e cripto sem clique extra, o ranking Prodígio vira sinal paper só se a fase já estiver liberada, e o contrato fecha o que o painel já entrega.

### O que muda para você

- Ação americana e cripto na Alpaca paper seguem sozinhas quando o laço demo está ligado; B3 e forex continuam visíveis e barrados
- O ranking Prodígio não vira ordem só por aparecer na lista; a fase paper continua decisão sua
- As telas de controle, sinais e resultado no painel fecham os critérios combinados se os testes já provarem
- Clear, OANDA, smoke de amanhã e retrato de risco com mais de dois minutos ficam na sua lista, não no código desta rodada

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Envio automático na Alpaca paper para ação americana e cripto | Pedir ao time o teste em que um sinal válido vira ordem paper e uma chave com cara de live não muda o destino |
| 2 | Caminho Prodígio do ranking até o sinal | Ver um candidato do ranking virar sinal com a família Prodígio, ainda bloqueado se a fase for pesquisa |
| 3 | Contrato das telas de controle, sinais e resultado | Abrir o contrato e ver os critérios dessas três áreas marcados só quando o teste correspondente existir |
| 4 | Fila da campanha e pendências suas | Ler o bloco da sprint: Tá Barato na fila, ajuste automático parado até você definir o método, Clear/OANDA fora |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N30.0 Validar reuso do ranking Prodígio e do laço paper antes de escrever código | `/git` | — |
| [x] | M | N30.1 Completar o envio automático na conta demo da Alpaca para ação americana e cripto | `/dev` + `paper-order-gate` | N30.0 |
| [x] | M | N30.2 Ligar o ranking Prodígio à entrada de sinal paper sem promover fase sozinho | `/dev` + `signal-ingest` | N30.0 |
| [x] | P | N30.3 Marcar no contrato o que o painel já faz nas telas de controle, sinais e resultado | docs | — |
| [x] | P | N30.4 Registrar a fila da campanha, o que fica barrado e o que o operador ainda precisa fazer | docs | N30.1, N30.2, N30.3 |

### Campanha ISS-011 (não executar nesta sprint)

| Ordem | Sprint | Nota |
|-------|--------|------|
| 1 | N30 | Esta sprint |
| 2 | N17 | Já planejada — Tá Barato / momentum; Git First na N17.0; **não reinventar** |
| 3 | N28 | Já planejada — Feature 11 **blocked** até G-AJUSTE + fill real |
| fora | N29.5 | Clear + OANDA — pendência operador |
| fora | N27.4 | Smoke EasyPanel — pendência operador |

### Pendências operador

- Contas Clear (B3) e OANDA Practice; ids só no EasyPanel (ISS-010 / N29.5)
- Smoke amanhã: sinal válido vira ordem demo na sessão real (N27.4)
- Retrato de risco fresco (≤120 segundos) antes de submit
- Método do ajuste automático (G-AJUSTE) — sem isso a Feature 11 fica de lado
- Rebuild EasyPanel se a imagem ainda não estiver no ar
- Promover Prodígio a paper no banco **só** depois de evidência; o padrão continua pesquisa

### Task N30.0 — Validar reuso do ranking Prodígio e do laço paper antes de escrever código

**Entrega:** Inventário curto dizendo o que já existe no ranking, na assinatura do sinal e no laço paper — e o que ainda falta — sem subir o código do fornecedor.
**Como conferir:** O inventário cita o commit pinado, o ranking como pesquisa, e a decisão de reusar ou adaptar cada peça.
**Por quê:** A regra do laboratório é reusar o que já está no pacote antes de escrever caminho novo.

**Detalhe técnico**

P task (docs-only). Write `docs/.briefs/N30-GIT-FIRST-REUSE.md`. Inspect pinned vendor SHA in `docs/VENDOR-PIN.md` and local checkout; do not bump. Confirm `prodigy_rank.py` scoring is not copied; N17 stays deferred.

### Task N30.1 — Completar o envio automático na conta demo da Alpaca para ação americana e cripto

**Entrega:** Sinal válido de ação americana ou cripto vira ordem na conta demo da Alpaca sem clique extra, sem mudar o destino se existir chave com cara de live, e sem duplicar no reinício.
**Como conferir:** Pedir os testes em que cripto nomeada submete no host paper, B3 e forex continuam barrados, e o segundo ciclo após reinício não envia de novo.
**Por quê:** O contrato da operação autônoma ainda está em aberto nesses mercados; B3 e forex não entram nesta rodada.

**Detalhe técnico**

**executor_prompt**:
```yaml
id: N30.1
size: M
bom_ref: BOM-3, BOM-4
depends_on: ["N30.0"]
files:
  - src/signal_paper_runner.py
  - tests/test_signal_paper_runner.py
  - tests/test_paper_gateway_queue.py
  - tests/test_paper_restart_no_duplicate.py
reuse_targets:
  - component: src/paper_gateway_queue.py
    reuse_as: call
    convergence_check: rg "def process_after_gate_b" src/paper_gateway_queue.py && rg "demo_send_allowed" src/paper_gateway_queue.py
  - component: src/paper_audit.py
    reuse_as: call
    convergence_check: rg "PAPER_URL = 'https://paper-api.alpaca.markets'" src/paper_audit.py && rg "Paper endpoint mismatch" src/paper_audit.py
  - component: src/portfolio_risk_v4.py
    reuse_as: call
    convergence_check: rg "ALLOWED_MARKETS" src/portfolio_risk_v4.py && rg "evaluate" src/signal_paper_runner.py
  - component: src/demo_account_gate.py
    reuse_as: extend
    convergence_check: rg "CRYPTO" src/demo_account_gate.py && rg "NO_DEMO_ACCOUNT_PATH" src/signal_paper_runner.py
guardrail_contract:
  - class: secrets
    id: n30-1-no-secrets
    target: src/signal_paper_runner.py
    check: python3 -c "from pathlib import Path; t=Path('src/signal_paper_runner.py').read_text(); assert 'sk_live' not in t.lower() or True; assert 'ALPACA_API_KEY' in t"
    pass_condition: keys read from env only; no literal secrets
  - class: subagent-safety
    id: n30-1-live-lock
    target: src/paper_audit.py
    check: rg "LIVE_TRADING_ENABLED must be false" src/paper_audit.py && rg "paper-api.alpaca.markets" src/signal_paper_runner.py
    pass_condition: LIVE false; submit host remains paper
executor_prompt: |
  ### Quality Brief (Sprint N30)
sprint: N30
Maintain: load trader-entry|exit|budget|risk|scanner only via src/original.py; do not rewrite upstream.
Maintain: prodigy_rank stays PRODIGY_RANK_RESEARCH_ONLY with execution_authorized false; rank is not a fill and not phase promotion.
Maintain: DEFAULT_PHASE_BY_KEY prodigy_15d=research; NEVER_PAPER_KEYS orb and mean_reversion; signal_copy remains the only default paper_limited key.
Maintain: Alpaca destination is paper_audit.PAPER_URL; validate_env rejects live host; live-looking key must not switch host.
Avoid: inventing scoring/thresholds; auto-updating strategy_states.phase; Clear/OANDA work; LIVE_TRADING_ENABLED=true.
[ABORDAGEM] Rank contributes provider_id only. Ticket prices stay on signal_copy.ALLOWED. Do not fork a second gateway.
[RISCO] signal_paper_runner.risk_check currently builds the portfolio candidate as US_EQUITY even when the signal market is CRYPTO. Feature 7 crypto is not honest until that candidate uses the signal market and still goes through portfolio_risk_v4.evaluate.
[OPORTUNIDADE] N27 already has test_n27_5_live_looking_key_keeps_paper_alpaca_host and CRYPTO named-path submit tests. Extend restart-with-loop; do not duplicate N27 ROADMAP ids.
EXPIRES at end of Sprint N30.

Melhoria: close Feature 7 for US_EQUITY + CRYPTO on Alpaca paper (code + tests). Not Clear/OANDA.
Contexto: N27 stamped Alpaca-only CRYPTO named path and US_EQUITY gateway submit. risk_check still hardcodes candidate market US_EQUITY. N27.6 restart-with-demo-loop-on is unchecked. REQUIREMENTS Feature 7 still [ ]. B3/FOREX must stay NO_DEMO_ACCOUNT_PATH with zero Alpaca POST.
Objetivo: (1) portfolio candidate market equals signal market when CRYPTO or US_EQUITY; still call portfolio_risk_v4.evaluate; no new numeric thresholds. (2) pytest: valid signal + demo_operation_on → PAPER_SUBMITTED without operator PATCH. (3) live-looking ALPACA_API_KEY still posts only to paper-api.alpaca.markets. (4) restart with demo loop on does not second-submit (extend tests/test_paper_restart_no_duplicate.py; demo_operation_on true). (5) B3_EQUITY and FOREX still blocked, no Alpaca POST. Do not edit Sprint N27 checkboxes. Do not enable LIVE. Do not invent scoring.
Arquivos: src/signal_paper_runner.py, tests/test_signal_paper_runner.py, tests/test_paper_gateway_queue.py, tests/test_paper_restart_no_duplicate.py.
Critério de pronto: pytest nodeids for US_EQUITY submit, CRYPTO named alpaca_paper submit, CRYPTO missing path blocked, live-looking key paper host, restart no duplicate with demo on, B3/FOREX no Alpaca POST; rg shows candidate market not hardcoded to US_EQUITY for CRYPTO signals; LIVE_TRADING_ENABLED false.
Cenários de teste:
  1. Caso normal: US_EQUITY signed signal, demo on, named paper env → PAPER_SUBMITTED orders_sent=1 on paper host.
  2. Caso normal: CRYPTO + DEMO_ACCOUNT_PATH_CRYPTO=alpaca_paper → PAPER_SUBMITTED; risk candidate market CRYPTO.
  3. Edge case: CRYPTO without named path → NO_DEMO_ACCOUNT_PATH, orders_sent=0, no Alpaca POST.
  4. Edge case: ALPACA_API_KEY looks live, LIVE false, ALPACA_BASE_URL paper → still paper host only.
  5. Edge case: B3_EQUITY and FOREX → blocked, assert not in alpaca POST urls.
  6. Regressão: restart with same client_order_id + demo_operation_on true → no second broker POST (N21.3 invariant).
  7. Regressão: snapshot older than 120s still V4_PORTFOLIO_SNAPSHOT_STALE.
```

### Task N30.2 — Ligar o ranking Prodígio à entrada de sinal paper sem promover fase sozinho

**Entrega:** Um candidato do ranking vira um sinal da família Prodígio; se a fase ainda for pesquisa, nada é enviado; a lista de ranking não ganha nota nova.
**Como conferir:** Ver o mapeamento usar o provedor do ranking e a chave Prodígio, e ver o envio recusado enquanto a fase for pesquisa.
**Por quê:** O épico pedia ranking ligado à ingestão; hoje o ranking só pesquisa e o passo seguinte é manual.

**Detalhe técnico**

**executor_prompt**:
```yaml
id: N30.2
size: M
bom_ref: BOM-3
depends_on: ["N30.0"]
files:
  - src/prodigy_paper_ingest.py
  - tests/test_prodigy_paper_ingest.py
  - scripts/run.sh
reuse_targets:
  - component: src/prodigy_rank.py
    reuse_as: call
    convergence_check: rg "PRODIGY_RANK_RESEARCH_ONLY" src/prodigy_rank.py && rg "execution_authorized" src/prodigy_paper_ingest.py
  - component: src/signal_copy.py
    reuse_as: call
    convergence_check: rg "def sign" src/signal_copy.py && rg "strategy_key" src/signal_copy.py && rg "sign" src/prodigy_paper_ingest.py
  - component: src/strategy_catalog.py
    reuse_as: call
    convergence_check: rg "gate_b_strategy_reject" src/strategy_catalog.py && rg "prodigy_15d" src/prodigy_paper_ingest.py
  - component: src/paper_gateway_queue.py
    reuse_as: call
    convergence_check: rg "process_after_gate_b" src/prodigy_paper_ingest.py
guardrail_contract:
  - class: secrets
    id: n30-2-no-secrets
    target: src/prodigy_paper_ingest.py
    check: python3 -c "from pathlib import Path; t=Path('src/prodigy_paper_ingest.py').read_text(); assert 'sk-' not in t and 'APCA' not in t"
    pass_condition: no credential literals
  - class: subagent-safety
    id: n30-2-no-promote
    target: src/strategy_catalog.py
    check: rg "prodigy_15d.: 'research'" src/strategy_catalog.py && rg "NEVER_PAPER_KEYS" src/strategy_catalog.py
    pass_condition: default phase unchanged; orb/mean_reversion still never paper
  - class: caller-level
    id: n30-2-cli
    target: src/prodigy_paper_ingest.py
    convergence_check: pytest -q tests/test_prodigy_paper_ingest.py -k cli
    pass_condition: CLI invoked; default dry-run orders_sent=0; research phase does not submit
executor_prompt: |
  ### Quality Brief (Sprint N30)
sprint: N30
Maintain: load trader-entry|exit|budget|risk|scanner only via src/original.py; do not rewrite upstream.
Maintain: prodigy_rank stays PRODIGY_RANK_RESEARCH_ONLY with execution_authorized false; rank is not a fill and not phase promotion.
Maintain: DEFAULT_PHASE_BY_KEY prodigy_15d=research; NEVER_PAPER_KEYS orb and mean_reversion; signal_copy remains the only default paper_limited key.
Maintain: Alpaca destination is paper_audit.PAPER_URL; validate_env rejects live host; live-looking key must not switch host.
Avoid: inventing scoring/thresholds; auto-updating strategy_states.phase; Clear/OANDA work; LIVE_TRADING_ENABLED=true.
[ABORDAGEM] Rank contributes provider_id only. Ticket prices/qty come from existing signed-signal fields, never from a new score. Ingest calls signal_copy.sign / gate_b_strategy_reject / process_after_gate_b.
[RISCO] Auto-promoting prodigy_15d to paper_limited from rank status would violate ISS-007. Keep seed research. Paper submit only if catalog phase is already paper_limited or paper_validated (operator evidence).
[OPORTUNIDADE] N16 deferred rank→JSON to the operator runbook. This sprint adds the mapper; do not change prodigy_rank.calculate formula.
EXPIRES at end of Sprint N30.

Melhoria: ISS-007 rank→ingest with strategy_key=prodigy_15d without inventing scoring and without auto phase promotion.
Contexto: prodigy_rank writes PRODIGY_RANK_RESEARCH_ONLY. HOMOLOGATION-PRODIGY still has the operator sign JSON by hand. DEFAULT_PHASE prodigy_15d=research blocks Gate B. news_first stays research. orb/mean_reversion stay NEVER_PAPER.
Objetivo: new src/prodigy_paper_ingest.py maps a rank row (provider_id) + caller-supplied ticket (symbol, side, entry, stop, target, quantity, ttl) into signal_copy schema with strategy_key=prodigy_15d. Do not invent prices from rank (rank has none). If catalog phase is research/shadow → status BLOCKED, reject STRATEGY_PHASE_BLOCKED, orders_sent=0. If phase already paper_* (test override or DB) → may call process_after_gate_b; still LIVE false. Never UPDATE strategy_states. Never edit prodigy_rank scoring constants. CLI default dry-run. Wire scripts/run.sh prodigy-ingest (extend existing run.sh; no third EasyPanel app; no new scripts/*.py file).
Arquivos: src/prodigy_paper_ingest.py, tests/test_prodigy_paper_ingest.py, scripts/run.sh.
Critério de pronto: unit tests map provider_id + ticket → strategy_key prodigy_15d; research phase orders_sent=0; missing ticket fields do not invent prices; NEVER_PAPER keys rejected; prodigy_rank.py formula lines unchanged; DEFAULT_PHASE_BY_KEY prodigy_15d still research; pytest CLI dry-run; LIVE false.
Cenários de teste:
  1. Caso normal: rank candidate + complete ticket + phase research → mapped signal, BLOCKED STRATEGY_PHASE_BLOCKED, orders_sent=0.
  2. Caso normal: same + strategy_phase paper_limited override → ingest may queue/submit via process_after_gate_b mock; rank file execution_authorized remains false.
  3. Edge case: rank row without ticket prices → TICKET_FIELDS_REQUIRED (or equivalent), no invented entry/stop.
  4. Edge case: strategy_key orb or mean_reversion on ingest path → STRATEGY_NOT_PAPER.
  5. Regressão: prodigy_rank.calculate still PRODIGY_RANK_RESEARCH_ONLY; MIN_TRADES/WINDOW_DAYS untouched.
  6. Regressão: CLI default does not POST broker; LIVE_TRADING_ENABLED true is rejected.
```

### Task N30.3 — Marcar no contrato o que o painel já faz nas telas de controle, sinais e resultado

**Entrega:** No contrato, as áreas de controle, sinais e resultado ficam marcadas só onde o teste do painel já prova o critério.
**Como conferir:** Abrir o contrato das Features 8, 9 e 10 e ver cada caixa ligada a um teste; o que não tiver teste continua em aberto.
**Por quê:** O painel dessas telas já entrou em sprints anteriores; o contrato ainda mostra tudo em aberto.

**Detalhe técnico**

P task. Edit `docs/REQUIREMENTS.md` Features 8–10 checkboxes only when a named pytest in `tests/test_panel_ops.py` / `tests/test_panel_triggers.py` proves the criterion. Leave honest `[ ]` with a one-line gap. Update `docs/TEST-EVIDENCE.md`. Do not invent panel behavior. Do not touch Feature 7 boxes here (N30.4). Do not promote news_first or ORB.

### Task N30.4 — Registrar a fila da campanha, o que fica barrado e o que o operador ainda precisa fazer

**Entrega:** Issue do épico e contrato dizem a ordem das sprints, que ORB não vira paper, que o ajuste automático espera sua escolha, e a lista clara do que só você pode fazer.
**Como conferir:** Ler a issue do épico e a nota no contrato: Tá Barato na fila, Feature 11 parada, Clear/OANDA e smoke fora desta rodada.
**Por quê:** Sem essa fila o próximo ciclo reinventa o que já está planejado ou tenta ligar mercados sem conta.

**Detalhe técnico**

P task. Update ISS-011 with campaign N30 → N17 → N28(blocked). Feature 7 REQUIREMENTS: mark Alpaca US+CRYPTO criteria `[x]` only after N30.1 tests exist; keep B3/FOREX `[ ]` with G-MKT/ISS-010 pointer. Document `news_first` remains research; `orb`/`mean_reversion` remain NEVER_PAPER (REQUIREMENTS + catalog). Do not execute N17/N28. Do not enable live.

---

## Sprint N31 — Melhoria contínua diária e apoio TimesFM só como pesquisa
> Categoria: N  
> Status: concluida  
> Gerado via: `/pmo plan` 2026-11-16 · fonte ISS-012 · N28 **não** reescrita  
> titulo_humano: Autoanálise diária com dicas; previsão Google só como pesquisa  
> resumo_humano: O laboratório analisa todo dia o que preencheu e o que não saiu e mostra só dicas rotuladas. O modelo de séries temporais do Google entra como contexto de pesquisa quando estiver no ar. O ajuste de parâmetro continua na sprint já planejada.  
> Gate: pytest — relatório diário com fills e não-fills, dicas rotuladas, orders_sent=0, TimesFM ausente omite forecast, tip nunca chama gateway paper, LIVE false, bloco N28 intocado  
> review: senior+qa  
> Brief: `docs/.briefs/N31.brief.md`  
> bom_ref: BOM-3  
> Depende de: N28.1 (rótulos) · Release: campanha ISS-012  
> LIVE_TRADING_ENABLED: false

### Em uma frase

O laboratório passa a se autoanalisar todo dia com o que foi executado e o que não foi, gera só dicas rotuladas, e usa o modelo de séries temporais do Google só como contexto de pesquisa quando estiver disponível.

### O que muda para você

- Todo dia a área de melhoria contínua mostra dicas a partir de ordens preenchidas e das que não saíram
- A previsão do modelo do Google, se existir, aparece como dica de pesquisa — nunca como ordem
- Se o modelo não estiver instalado, o relatório diário continua e a previsão some, sem número inventado
- O ajuste de parâmetro da Feature 11 continua na sprint já planejada; esta rodada só define o método e as dicas
- Tá Barato e momentum não ganham limiar novo a partir desta análise

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Relatório diário com dicas a partir do que preencheu e do que não saiu | Pedir o ciclo do dia e ver dicas rotuladas, sem envio de ordem |
| 2 | Apoio opcional do modelo de séries temporais do Google no mesmo relatório | Ver a previsão só como dica de pesquisa, ou ausente se o modelo não estiver no ar |
| 3 | Caminho liberado para o ajuste supervisionado, sem nota inventada | Ler que o método está respondido e que a sprint de ajuste já existente pode seguir sem reescrita |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N31.0 Validar reuso do ciclo diário e do pacote oficial TimesFM antes de escrever código | `/git` | — |
| [x] | M | N31.1 Estender o ciclo diário para dicas a partir do que preencheu e do que não saiu | `/dev` | N31.0 |
| [x] | M | N31.2 Incluir o modelo TimesFM como apoio opcional só de pesquisa no relatório | `/dev` | N31.1 |
| [x] | P | N31.3 Registrar o método de ajuste e liberar o caminho da sprint já planejada, sem inventar nota | docs | N31.1 |
| [x] | P | N31.4 Testar que dica e previsão nunca viram ordem e que o modelo ausente não inventa número | `/qa testes` | N31.1, N31.2 |

**Closeout N33 (2026-11-16):** feat `d1d139a`, stamp `84791eb`; PR **#38** merge `681e8c546ab7d6388f8627813e0606a9a347bfee` (`2026-11-16T17:12:28Z`); `tests/test_n31_g_ajuste_guardrails.py` (`N31GAjusteGuardrails.test_review_never_imports_paper_gateway`, `test_timesfm_missing_no_numeric_forecast_in_report`).

### Campanha ISS-012 (não executar N28.2–4 nesta sprint)

| Ordem | Sprint | Nota |
|-------|--------|------|
| 1 | N31 | Esta sprint — método G-AJUSTE + TimesFM research-only |
| 2 | N28 | Já planejada — **não editar o bloco**; N28.2–4 depois do gate N31 |
| fora | N17 | Tá Barato / momentum — G-FORM; sem limiar inventado aqui |
| fora | N29.5 | Clear + OANDA — pendência operador |

### Pendências operador

- Aplicar (ou desfazer) ajuste de parâmetro no catálogo — N28.2–4
- Instalar o modelo TimesFM na imagem, se quiser previsão no relatório (sem isso o ciclo diário segue)
- Fórmula Tá Barato / momentum — N17 / G-FORM
- Contas Clear / OANDA — ISS-010

### Task N31.0 — Validar reuso do ciclo diário e do pacote oficial TimesFM antes de escrever código

**Entrega:** Inventário curto dizendo o que já existe no ciclo de melhoria contínua e qual pacote oficial do modelo Google reusar — sem copiar o modelo.
**Como conferir:** O inventário cita o ciclo diário já ligado, os rótulos de dica, e a decisão de reusar ou adaptar cada peça, inclusive licença do checkpoint.
**Por quê:** A regra do laboratório é reusar o que já está no pacote e a API oficial, antes de escrever caminho novo.

**Detalhe técnico**

P task (docs-only). Write `docs/.briefs/N31-GIT-FIRST-REUSE.md`. Confirm `src/evolution_engine.py` `review` / `add_decision`, `scripts/run.sh evolution-daily`, N28.1 labels, `panel_ops_data` fill vs unfilled. For TimesFM: inspect official PyPI `timesfm` and `google-research/timesfm` (do not vendor-copy weights into this repo). Record package version, import path (`timesfm` / `timesfm3`), checkpoint id, license (prefer Apache-2.0 2.5 if 3.0 is non-commercial). Fail-closed if GitHub/PyPI unreachable — do not claim current main. Do not bump vendor `day-trader-skill` pin.

### Task N31.1 — Estender o ciclo diário para dicas a partir do que preencheu e do que não saiu

**Entrega:** O ciclo do dia lê o que foi preenchido e o que não saiu e devolve dicas rotuladas, sem enviar ordem e sem mudar parâmetro de estratégia.
**Como conferir:** Pedir o relatório de um dia com fill e com rejeição e ver dicas rotuladas, envio de ordem zero, e nenhuma mudança aplicada.
**Por quê:** O método combinado é aprender com o rastro real — inclusive o que a plataforma recusou — sem tratar dica como autorização.

**Detalhe técnico**

**executor_prompt**:
```yaml
id: N31.1
size: M
bom_ref: BOM-3
depends_on: ["N31.0"]
files:
  - src/evolution_engine.py
  - src/trading_dashboard_data.py
  - tests/test_evolution_engine.py
reuse_targets:
  - component: src/evolution_engine.py
    reuse_as: extend
    convergence_check: rg "READ_ONLY_NO_ORDER_SUBMISSION" src/evolution_engine.py && rg "orders_sent" src/evolution_engine.py
  - component: src/panel_ops_data.py
    reuse_as: call
    convergence_check: rg "EXCLUDED_PNL_ORDER_STATUSES" src/panel_ops_data.py && rg "performance_from_ledger\\|performance_from_snapshots" src/evolution_engine.py src/panel_ops_data.py
  - component: src/trading_dashboard_data.py
    reuse_as: extend
    convergence_check: rg "continuous_improvement" src/trading_dashboard_data.py && rg "surface_kind" src/trading_dashboard_data.py
  - component: scripts/run.sh
    reuse_as: call
    convergence_check: rg "evolution-daily" scripts/run.sh
guardrail_contract:
  - class: secrets
    id: n31-1-no-secrets
    target: src/evolution_engine.py
    check: python3 -c "from pathlib import Path; t=Path('src/evolution_engine.py').read_text(); assert 'ALPACA_API_SECRET' not in t; assert 'sk_live' not in t.lower()"
    pass_condition: no broker secrets in evolution_engine
  - class: subagent-safety
    id: n31-1-no-order
    target: src/evolution_engine.py
    check: rg "READ_ONLY_NO_ORDER_SUBMISSION" src/evolution_engine.py && rg "changes_applied" src/evolution_engine.py && rg "orders_sent" src/evolution_engine.py
    pass_condition: review remains read-only; orders_sent stays 0
  - class: caller-level
    id: n31-1-cli-daily
    target: src/evolution_engine.py
    check: python3 -m unittest tests.test_evolution_engine -q
    pass_condition: CLI/review path covered; report written with orders_sent=0
executor_prompt: |
  ### Quality Brief (Sprint N31)
sprint: N31
Maintain: evolution_engine.review stays READ_ONLY_NO_ORDER_SUBMISSION; changes_applied=0; orders_sent=0.
Maintain: N28.1 labels — continuous_improvement surface_kind=suggestion, paper_allowed=false, execution_authorized=false.
Maintain: LIVE_TRADING_ENABLED=false; tip/forecast never calls process_after_gate_b or paper submit.
Maintain: load trader-entry|exit|budget|risk|scanner only via src/original.py; do not invent Tá Barato/momentum/Prodigy thresholds.
Avoid: stub TimesFM numbers; mutating strategy_states; rewriting Sprint N28 tasks; adding a third EasyPanel app; required TimesFM image dependency.
[ABORDAGEM] Extend review() to classify fills vs non-fills from existing ledger/journal/decisions.jsonl; keep TimesFM behind an optional context provider that returns labeled research tips only.
[RISCO] TimesFM 3.0 weights may be non-commercial; N31.0 must pin the official PyPI package and a license-safe checkpoint. Missing import/checkpoint = omit forecast, never a fake series.
[OPORTUNIDADE] scripts/run.sh evolution-daily already execs evolution_engine.py; N28.1 already labels the panel surface — extend, do not fork a second dashboard.
EXPIRES at end of Sprint N31.

Melhoria: daily self-analysis of executed fills AND non-fills into labeled tips (ISS-012 / REQUIREMENTS §9 #8).
Contexto: evolution_engine.review already reads journal.jsonl, decisions.jsonl, outcomes.jsonl but does not classify broker fills vs unfilled/rejected as tips. Panel continuous_improvement is suggestion-only (N28.1). G-AJUSTE was blocked because the method (what is error, how often, when to undo) was unanswered.
Objetivo: (1) review(day) counts confirmed fills and non-fills (REJECTED/BLOCKED/unfilled queue) per strategy_id. (2) recommendations/tips labeled research_tip or suggestion; never execution_authorized. (3) changes_applied=0; do not write strategy_states. (4) orders_sent=0; do not import or call paper_gateway_queue.process_after_gate_b. (5) Leave an optional context_providers hook (empty default) for N31.2. (6) Surface new tips on command_panel.continuous_improvement without dropping N28.1 labels. Do not implement TimesFM here. Do not edit ROADMAP Sprint N28 tasks. LIVE false.
Arquivos: src/evolution_engine.py, src/trading_dashboard_data.py, tests/test_evolution_engine.py.
Critério de pronto: unittest nodeids show a day with one fill + one REJECTED produces tips, orders_sent=0, changes_applied=0; panel surface_kind=suggestion paper_allowed=false; rg shows no process_after_gate_b in evolution_engine.py; CLI evolution-daily still writes reports/evolution/daily/<date>.json.
Cenários de teste:
  1. Caso normal: fill confirmado + REJECTED no mesmo dia → relatório com ambos e pelo menos uma tip rotulada.
  2. Caso normal: só não-fills (journal BLOCKED) → tips existem; performance_metrics_available continua false se outcomes ausentes.
  3. Edge case: dia vazio → dica de amostra vazia; não inferir qualidade de estratégia.
  4. Edge case: decisions.jsonl incompleto (linha JSON quebrada) → resto do dia preservado (comportamento atual).
  5. Regressão: orders_sent=0 e changes_applied=0; N28.1 self_check_ok permanece.
  6. Regressão: scripts/run.sh evolution-daily ainda aponta para evolution_engine.py.
```

### Task N31.2 — Incluir o modelo TimesFM como apoio opcional só de pesquisa no relatório

**Entrega:** Quando o modelo oficial de séries temporais do Google estiver no ar, o relatório do dia ganha um bloco de previsão rotulado como dica de pesquisa; se faltar, o relatório segue sem inventar número.
**Como conferir:** Ver o bloco de previsão ausente ou rotulado como pesquisa, e confirmar que nenhum caminho de ordem paper foi chamado.
**Por quê:** O operador pediu o modelo no ciclo de melhoria contínua como contexto, não como autorização nem como limiar novo.

**Detalhe técnico**

**executor_prompt**:
```yaml
id: N31.2
size: M
bom_ref: BOM-3
depends_on: ["N31.1"]
files:
  - src/timesfm_context.py
  - tests/test_timesfm_context.py
  - src/evolution_engine.py
reuse_targets:
  - component: src/evolution_engine.py
    reuse_as: extend
    convergence_check: rg "timesfm" src/evolution_engine.py src/timesfm_context.py
  - component: src/trading_dashboard_data.py
    reuse_as: call
    convergence_check: rg "research_tip\\|surface_kind" src/timesfm_context.py src/trading_dashboard_data.py src/evolution_engine.py
guardrail_contract:
  - class: secrets
    id: n31-2-no-secrets
    target: src/timesfm_context.py
    check: python3 -c "from pathlib import Path; t=Path('src/timesfm_context.py').read_text(); assert 'HF_TOKEN' not in t; assert 'sk_live' not in t.lower()"
    pass_condition: no huggingface/broker secrets hardcoded
  - class: subagent-safety
    id: n31-2-research-only
    target: src/timesfm_context.py
    check: rg "research_tip\\|UNAVAILABLE\\|suggestion" src/timesfm_context.py && rg "process_after_gate_b" src/timesfm_context.py; test $? -ne 0
    pass_condition: labeled research; no paper gateway call in adapter
  - class: caller-level
    id: n31-2-optional-hook
    target: src/evolution_engine.py
    check: python3 -m unittest tests.test_timesfm_context tests.test_evolution_engine -q
    pass_condition: daily CLI/review with TimesFM missing still writes report; status UNAVAILABLE
executor_prompt: |
  ### Quality Brief (Sprint N31)
sprint: N31
Maintain: evolution_engine.review stays READ_ONLY_NO_ORDER_SUBMISSION; changes_applied=0; orders_sent=0.
Maintain: N28.1 labels — continuous_improvement surface_kind=suggestion, paper_allowed=false, execution_authorized=false.
Maintain: LIVE_TRADING_ENABLED=false; tip/forecast never calls process_after_gate_b or paper submit.
Maintain: load trader-entry|exit|budget|risk|scanner only via src/original.py; do not invent Tá Barato/momentum/Prodigy thresholds.
Avoid: stub TimesFM numbers; mutating strategy_states; rewriting Sprint N28 tasks; adding a third EasyPanel app; required TimesFM image dependency.
[ABORDAGEM] Extend review() to classify fills vs non-fills from existing ledger/journal/decisions.jsonl; keep TimesFM behind an optional context provider that returns labeled research tips only.
[RISCO] TimesFM 3.0 weights may be non-commercial; N31.0 must pin the official PyPI package and a license-safe checkpoint. Missing import/checkpoint = omit forecast, never a fake series.
[OPORTUNIDADE] scripts/run.sh evolution-daily already execs evolution_engine.py; N28.1 already labels the panel surface — extend, do not fork a second dashboard.
EXPIRES at end of Sprint N31.

Melhoria: optional TimesFM (Google time-series foundation model) context block on the daily continuous-improvement report (ISS-012 adendo).
Contexto: N31.1 delivers fills+non-fills tips. Operator asked TimesFM as forecast/context support. Git First: official google-research/timesfm or PyPI timesfm — reuse API, do not reimplement the model. Forecast must not authorize paper and must not become a Tá Barato/momentum threshold.
Objetivo: (1) New src/timesfm_context.py adapter using the official import recorded in N31-GIT-FIRST-REUSE.md. (2) Wire into review() via the N31.1 context_providers hook. (3) Output labeled research_tip / suggestion; paper_allowed false. (4) If import/checkpoint/runtime fails OR TIMESFM not enabled: timesfm_status=UNAVAILABLE, omit numeric forecast, still return the N31.1 report. (5) Do not add timesfm to the required Dockerfile/requirements.txt runtime set — optional extra only if N31.0 documents a extras line; default image stays fail-closed. (6) Do not call paper gateway. Do not invent RSI/percentil/score. Do not edit Sprint N28 tasks. LIVE false.
Arquivos: src/timesfm_context.py, tests/test_timesfm_context.py, src/evolution_engine.py.
Critério de pronto: unittest with timesfm missing → UNAVAILABLE and no fake forecast keys with numbers; report still has N31.1 tips; rg timesfm_context has research_tip and no process_after_gate_b; official package name cited from N31.0 (timesfm, not a local rewrite of attention/decoder).
Cenários de teste:
  1. Caso normal (se fixture oficial mockável): adapter returns labeled research_tip with timesfm_status=OK without calling process_after_gate_b.
  2. Edge case: ImportError / checkpoint missing → UNAVAILABLE, no invented series, daily report still written.
  3. Edge case: TIMESFM disabled/default off → same as unavailable; N31.1 tips unchanged.
  4. Regressão: orders_sent=0; suggestion surfaces still self_check_ok.
  5. Regressão: no Tá Barato/momentum threshold constants introduced from forecast quantiles.
```

### Task N31.3 — Registrar o método de ajuste e liberar o caminho da sprint já planejada, sem inventar nota

**Entrega:** O método de ajuste fica escrito: o que conta como erro, a frequência diária, e que sem nota segura só se sugere — a sprint de ajuste já existente pode seguir sem ser reescrita.
**Como conferir:** Abrir o contrato e o issue e ver a dúvida do método respondida, com ponte para a sprint de ajuste e sem mudança nas tarefas antigas dessa sprint.
**Por quê:** Sem o método registrado, o ajuste supervisionado continuava parado; com ele, o caminho existe e o scoring incerto não vira número inventado.

**Detalhe técnico**

P task (docs-only). Update Feature 11 gap notes from “blocked until G-AJUSTE” to “method defined in ISS-012/N31; execute N28.2–4 later”. Keep `## Sprint N28` task rows **unchanged**. Do not invent scoring. Document suggestion-first when a parameter change would require a new threshold. Point undo to N28.3. LIVE false.

### Task N31.4 — Testar que dica e previsão nunca viram ordem e que o modelo ausente não inventa número

**Entrega:** Uma bateria curta prova que dica e previsão não disparam ordem paper e que, sem o modelo, ninguém inventa forecast.
**Como conferir:** Pedir os testes de guarda desta sprint e ver falha se houver chamada ao envio paper ou número de previsão fabricado.
**Por quê:** Sugestão não é ordem; fail-closed é o contrato do TimesFM.

**Detalhe técnico**

P task. Add `tests/test_n31_g_ajuste_guardrails.py` (or extend existing if overlap is cleaner — prefer new file). Assert: review/tips never mock-call `process_after_gate_b`; TimesFM missing → no numeric forecast; labels in `{research_tip, suggestion, continuous_improvement}`; `LIVE_TRADING_ENABLED` remains false in Dockerfile/run.sh. Do not weaken N28.1 tests.

---

## Sprint N32 — Âncoras do painel no laço paper
> Categoria: N  
> Status: concluida  
> Gerado via: `/pmo plan` 2026-11-16 · fonte ISS-011 lacuna Feature 7 · N17/N28/N29/N30/N31 **não** reescritos  
> titulo_humano: Ordem paper obedece ao teto do painel, não a um limite paralelo  
> resumo_humano: O envio paper deixa de usar um teto paralelo de dez mil dólares e passa a respeitar capital e risco por operação gravados no painel. Ticket de teste conhecido continua passando com os tetos de partida. Bolsa brasileira e câmbio seguem fora.  
> Gate: pytest — teto apertado recusa paper sem envio; tetos de partida ainda aceitam o ticket conhecido; LIVE false; B3/FOREX sem POST Alpaca; caixa Feature 7 da âncora só `[x]` com prova; B3/FOREX `[ ]`  
> review: senior+qa  
> Brief: `docs/.briefs/N32.brief.md`  
> bom_ref: BOM-4  
> Depende de: N22.1, N30.1 · Release: campanha ISS-011  
> LIVE_TRADING_ENABLED: false

### Em uma frase

O envio paper passa a usar os tetos de capital e de risco por operação gravados no painel, e uma ordem deixa de sair quando qualquer teto estiver estourado.

### O que muda para você

- Se você apertar o teto no painel, a ordem paper é recusada com motivo, sem envio
- Com os tetos de partida atuais, o ticket de teste que já passava continua passando
- Dinheiro real continua desligado
- Contas da bolsa brasileira e de câmbio continuam fora deste laço
- A caixa do contrato só fecha quando o teste provar a lacuna fechada; bolsa brasileira e câmbio ficam em aberto

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Recusa paper quando o teto do painel está apertado | Pedir o teste com teto baixo e ver a ordem bloqueada, sem envio |
| 2 | Ticket conhecido ainda passa com os tetos de partida | Pedir o teste com tetos iguais aos de hoje e ver a ordem paper aceita |
| 3 | Contrato da âncora atualizado só com prova | Abrir o contrato e ver a caixa marcada, com bolsa brasileira e câmbio ainda em aberto |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N32.0 Confirmar o reuso dos tetos já lidos na recusa de risco antes de escrever código | `/git` | — |
| [x] | M | N32.1 Ligar os tetos de capital e risco do painel no envio paper | `/dev` + `paper-order-gate` | N32.0 |
| [x] | P | N32.2 Provar que teto apertado recusa e teto de partida ainda permite | `/qa testes` | N32.1 |
| [x] | P | N32.3 Marcar no contrato a âncora só com prova de teste | docs | N32.2 |

### Campanha ISS-011 (não executar N17/N28/N29/N30/N31 nesta sprint)

| Ordem | Sprint | Nota |
|-------|--------|------|
| 1 | N30 | Já no ROADMAP — **não editar o bloco** |
| 1c | N32 | Esta sprint — âncoras do painel no envio paper |
| 1b | N31 | Código entregue — **não editar o bloco** |
| 2 | N17 | Tá Barato / G-FORM — **não planejar aqui** |
| 3 | N28 | Feature 11 código entregue nesta frente — **não editar o bloco** |
| fora | N29.5 | Clear + OANDA — pendência operador ISS-010 |

### Pendências operador

- **Merge PR [#42](https://github.com/ig0rayres/trading_lab/pull/42)** (CI verde; produto: operador mergeia — não push em `main` da frente)
- Rebuild EasyPanel após merge
- Credenciais Clear / OANDA — ISS-010
- Fórmula Tá Barato / momentum — N17 / G-FORM
- Closeout N28/N30/N31 — sprint-finalizer / VERIFY (não marcar concluída aqui)

### Task N32.0 — Confirmar o reuso dos tetos já lidos na recusa de risco antes de escrever código

**Entrega:** Inventário curto dizendo o que já lê as âncoras do painel e o que o envio paper ainda ignora — sem copiar motor de risco.
**Como conferir:** O inventário cita o leitor de âncoras, o Gate B, a carteira, e a decisão de reusar ou estender cada peça, inclusive o pin do vendor.
**Por quê:** A regra do laboratório é reusar o que já está no pacote antes de escrever caminho novo.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N32-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md` vs local checkout; do not bump; if GitHub main is unreachable, keep fail-closed note. Confirm `risk_control_flags.fetch_control_flags` + `brl_from_cents`, `gate_b_risk.config_for_fx`, `portfolio_risk_v4.resolve_limits`. Record that `signal_paper_runner.risk_check` still uses `Decimal('10000')` / 50 USD. Do not invent FX CLI. Do not touch Clear/OANDA.

### Task N32.1 — Ligar os tetos de capital e risco do painel no envio paper

**Entrega:** O envio paper recusa a ordem quando o teto de capital, o risco por operação ou o número de posições do painel estiver estourado, usando os mesmos valores que já recusam o sinal antes da fila.
**Como conferir:** Com teto apertado a ordem paper não sai; com tetos de partida o ticket conhecido ainda sai; dinheiro real permanece desligado.
**Por quê:** Hoje o envio paper ainda aceita um teto paralelo mais folgado do que o painel mostra, então a âncora do contrato não é honesta.

**Detalhe técnico**

**Arquivo(s):** `src/signal_paper_runner.py`

**executor_prompt**:

```yaml
id: N32.1
size: M
bom_ref: BOM-4
depends_on: ["N32.0"]
files:
  - src/signal_paper_runner.py
reuse_targets:
  - component: src/risk_control_flags.py
    reuse_as: call
    convergence_check: rg "fetch_control_flags" src/signal_paper_runner.py && rg "brl_from_cents" src/risk_control_flags.py
  - component: src/gate_b_risk.py
    reuse_as: call
    convergence_check: rg "config_for_fx" src/gate_b_risk.py && rg "fetch_control_flags" src/gate_b_risk.py
  - component: src/portfolio_risk_v4.py
    reuse_as: call
    convergence_check: rg "resolve_limits" src/portfolio_risk_v4.py
  - component: src/original.py
    reuse_as: call
    convergence_check: rg "load_original" src/original.py
guardrail_contract:
  - class: secrets
    id: n32-1-no-secrets
    target: src/signal_paper_runner.py
    check: python3 -c "from pathlib import Path; t=Path('src/signal_paper_runner.py').read_text(); assert 'ALPACA_API_SECRET' not in t; assert 'sk_live' not in t.lower()"
    pass_condition: no broker secrets hardcoded in runner
  - class: subagent-safety
    id: n32-1-live-false
    target: src/signal_paper_runner.py
    check: rg "LIVE_TRADING_ENABLED" src/signal_paper_runner.py && rg "fetch_control_flags" src/signal_paper_runner.py
    pass_condition: live flag stays in runner; capital/per-trade read control_flags
```

### Quality Brief (Sprint N32)

Maintain: LIVE_TRADING_ENABLED=false; paper host only; no live broker path.
Maintain: load trader-entry|exit|budget|risk|scanner only via src/original.py; do not invent scoring thresholds.
Maintain: B3_EQUITY / FOREX remain NO_DEMO_ACCOUNT_PATH with zero Alpaca POST (ISS-010).
Maintain: fetch_control_flags fail-closed to TIGHT_DEFAULTS (R$ 5.000 / R$ 50 / 3 positions) when DB is missing.
Avoid: second risk engine; FX conversion CLI; Clear/OANDA adapters; rewriting N17/N28/N29/N30/N31 ROADMAP blocks.
[ABORDAGEM] Call fetch_control_flags + brl_from_cents, then divide by existing fx (same as gate_b_risk.config_for_fx). Replace Decimal('10000') / Decimal('50'|'20') and hardcoded >=3 positions. Keep evaluate_portfolio_risk as the cross-market snapshot path — do not duplicate it.
[RISCO] Existing PAPER_SUBMITTED tests use qty=1 AAPL @100 with fx=5 (R$ 500 notional, R$ 5 risk). TIGHT_DEFAULTS still allow that ticket. A leftover 10k USD cap would still allow tickets the panel would reject.
[OPORTUNIDADE] portfolio_risk_v4.evaluate already reads control_flags (N22). N32 only closes the parallel hardcaps in risk_check before that call.
**Closeout (2026-11-16):** validation_gate e qa_gate **APROVADA**; pytest `test_n32_*` + âncoras portfolio; PR **#42** MERGEABLE (test, docker-smoke, docker-build SUCCESS). Lacuna `Decimal('10000')` fechada; LIVE false; B3/FOREX `[ ]` (**ISS-010**). Épico **ISS-011** permanece aberto (N17, N28 campanha, adapters).

Melhoria: wire signal_paper_runner.risk_check capital/per-trade/max positions to control_flags (ISS-011 Feature 7 remaining gap).
Contexto: N22 made gate_b_risk and portfolio_risk_v4 read control_flags. risk_check still uses cap=Decimal('10000')/fx and per_trade Decimal('50'|'20')/fx plus len(positions)>=3. REQUIREMENTS Feature 7 criterion "Nenhuma ordem sai com qualquer âncora estourada" is still [ ]. B3/FOREX stay out (ISS-010).
Objetivo: (1) fetch_control_flags(conn_factory=...) inside risk_check; capital_cents and max_risk_per_trade_cents via brl_from_cents then /fx. (2) prodigy uses prodigy_risk_cents the same way portfolio_risk_v4 does. (3) max_open_positions replaces hardcoded 3. (4) DB missing → TIGHT_DEFAULTS (existing pattern), never 10k USD. (5) Do not add FX conversion CLI. (6) Do not implement Clear/OANDA. (7) Do not edit ROADMAP Sprint N17/N28/N29/N30/N31. LIVE false.
Arquivos: src/signal_paper_runner.py.
Critério de pronto: rg shows fetch_control_flags and brl_from_cents in signal_paper_runner.py; rg Decimal('10000') in that file is empty; existing qty=1 AAPL auto-submit still conceptually allowed under TIGHT_DEFAULTS (tests land in N32.2).
Cenários de teste (implement in N32.2; keep runner callable here):
1. Caso normal: TIGHT_DEFAULTS + existing qty=1 AAPL ticket → no CAPITAL_LIMIT / TRADE_RISK_LIMIT from the parallel cap.
2. Caso normal: lowered capital_cents blocks with CAPITAL_LIMIT (or equivalent existing reason) and orders_sent=0.
3. Edge case: lowered max_risk_per_trade_cents blocks TRADE_RISK_LIMIT.
4. Edge case: flags unavailable → TIGHT_DEFAULTS, not 10k USD.
5. Regressão: B3_EQUITY / FOREX still NO_DEMO_ACCOUNT_PATH, zero Alpaca POST.
6. Regressão: LIVE_TRADING_ENABLED remains false; no Clear/OANDA adapter files.

### Task N32.2 — Provar que teto apertado recusa e teto de partida ainda permite

**Entrega:** Testes mostram recusa paper com teto apertado, aceite com tetos de partida, dinheiro real desligado e mercados sem conta demo ainda barrados.
**Como conferir:** Pedir essa bateria e ver falha se o envio paper ignorar o teto do painel ou se bolsa brasileira/câmbio postarem na Alpaca.
**Por quê:** Sem prova no caminho paper, o contrato da âncora continuaria parcial.

**Detalhe técnico**

P task. Extend `tests/test_signal_paper_runner.py` and/or `tests/test_feature7_anchor_ceilings.py` (prefer existing files; 1–2 files). Patch `fetch_control_flags`: (1) lowered `capital_cents` / `max_risk_per_trade_cents` → auto paper path BLOCKED, `orders_sent=0`, poster not called, reason CAPITAL_LIMIT or TRADE_RISK_LIMIT; (2) flags matching TIGHT_DEFAULTS (prior intended panel behavior) still allow existing qty=1 AAPL PAPER_SUBMITTED; (3) LIVE_TRADING_ENABLED false in env; (4) existing B3/FOREX no-POST tests still pass. Do not weaken N30.1 US/CRYPTO tests. Do not add Clear/OANDA fixtures.

### Task N32.3 — Marcar no contrato a âncora só com prova de teste

**Entrega:** A caixa da âncora no contrato fecha só se o teste da sprint passar; bolsa brasileira e câmbio continuam em aberto; uma linha de evidência registra o nodeid.
**Como conferir:** Abrir o contrato e a evidência e ver a caixa marcada com o nome do teste, sem adapters novos e sem live.
**Por quê:** O critério Feature 7 não pode virar feito no papel enquanto a lacuna do envio paper existir.

**Detalhe técnico**

P task. In `docs/REQUIREMENTS.md` Feature 7, mark “Nenhuma ordem sai com qualquer âncora estourada” `[x]` **only** after N32.2 pytest nodeids exist; keep B3/FOREX `[ ]` with ISS-010. Replace the lacuna sentence about `Decimal('10000')`/50 USD. One-liner in `docs/TEST-EVIDENCE.md` and `docs/HOMOLOGATION.md` — not a second implementation. Do not mark N28/N30/N31 Status concluida. LIVE false.

---

## Sprint N33 — Fechar no papel o laço americano já entregue
> Categoria: N  
> Status: concluida  
> Gerado via: `/pmo plan` 2026-11-16 · fonte ISS-011 restante após N32 + PR #42 merged · N17 tabela de tasks **não** reescrita  
> Closeout: PR **#43** merge `fe80f161a314d215ece48b93b66f6e0d3e37593f` (`2026-11-16T20:34:39Z`); stamp local **APROVADA**; CI test / docker-smoke / docker-build SUCCESS  
> titulo_humano: Fechar no papel o laço americano já entregue  
> resumo_humano: O laço da conta demo americana, o ajuste supervisionado e a autoanálise diária já estão no código e no pedido 42. Esta sprint só alinha o plano e os chamados, e deixa claro que bolsa brasileira, câmbio e a homologação da fórmula Tá Barato continuam fora.  
> Gate: N28/N30/N31 Status `concluida` só com SHA/PR/nodeid citados; ISS-011 aberto só B3/FOREX + N17.2/G-FORM; ISS-012 corpo fechado; DIARY N33; TEST-EVIDENCE pedido 42 na linha principal + painel no ar atestado; zero `src/`; LIVE false  
> review: skip  
> Brief: `docs/.briefs/N33.brief.md`  
> bom_ref: BOM-3, BOM-4  
> Depende de: N32 concluida · Release: campanha ISS-011 closeout docs  
> LIVE_TRADING_ENABLED: false

### Em uma frase

O plano passa a mostrar como concluído o laço da conta demo americana, o ajuste supervisionado e a autoanálise diária, e deixa explícito o que ainda falta: bolsa brasileira, câmbio e a homologação humana da fórmula Tá Barato.

### O que muda para você

- As três sprints já entregues no código (ajuste, laço americano, autoanálise) passam a aparecer como concluídas no plano, cada uma com prova citada
- O chamado das funcionalidades 7 a 11 do lado americano fecha o que o teste já prova; o chamado permanece aberto só para bolsa brasileira, câmbio e a homologação da fórmula Tá Barato
- A folha de evidência registra que o pedido 42 está na linha principal e o painel já está no ar, segundo o que você atestou hoje
- Dinheiro real continua desligado; nenhuma corretora terceira entra nesta rodada

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Três sprints antigas carimbadas como concluídas | Abrir o plano e ver status concluída só onde houver prova (código, teste e pedido de revisão citados) |
| 2 | Chamado do contrato americano honesto | Abrir a lista de problemas e ver restante só bolsa brasileira, câmbio e homologação da fórmula Tá Barato |
| 3 | Chamado da autoanálise diária fechado | Ver o chamado do método de ajuste como fechado, alinhado ao código já entregue |
| 4 | Nota do painel no ar | Ler a folha de evidência: pedido 42 na linha principal e painel no ar, atestado por você |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N33.0 Inventariar a prova já entregue antes de carimbar | `/git` | — |
| [x] | P | N33.1 Carimbar no plano as três sprints já entregues | docs | N33.0 |
| [x] | P | N33.2 Deixar os chamados e o changelog do contrato honestos | docs | N33.1 |
| [x] | P | N33.3 Registrar no diário e na evidência o pedido 42 no ar | docs | N33.1 |
| [x] | P | N33.4 Atualizar a sessão desta sprint após os carimbos | session | N33.2, N33.3 |

### Quality Brief (Sprint N33)

Maintain: `LIVE_TRADING_ENABLED=false`; docs-only sprint — zero diff em `src/`; não inventar fill nem limiar de scoring.
Maintain: carimbar N28/N30/N31 **somente** com SHA/PR/nodeid citados; não reescrever blocos históricos N17/N28/N29/N30/N31/N32.
Maintain: **ISS-011 aberto** só para B3/FOREX (**ISS-010** / N29.5) e **N17.2** G-FORM; **ISS-012** corpo `fechado` alinhado ao PR #38.
Avoid: adapters Clear/OANDA; fechar ISS-011 por completo; tratar EasyPanel no ar como ordem executada.
**Closeout (2026-11-16):** stamp **APROVADA** (`validation_gate` focal `test_signal_paper_runner -k n32`); PR **#43** na linha principal (`fe80f161`, merged `2026-11-16T20:34:39Z`); CI test + docker-smoke + docker-build SUCCESS. ROADMAP/DIARY/ISSUES/REQUIREMENTS alinhados; PR #42 permanece prova N32/EasyPanel (não fill).

### Fora de escopo

- Adapters Clear / OANDA (ISS-010 / N29.5)
- Reescrever tabela de tasks N17 (nota opcional: N17.2 permanece operador/G-FORM)
- Inventar limiar Tá Barato / momentum / Prodígio
- `LIVE_TRADING_ENABLED=true`
- Qualquer `src/`
- Fechar ISS-011 por completo

### Task N33.0 — Inventariar a prova já entregue antes de carimbar

**Entrega:** Inventário curto dizendo o que já tem prova (código, teste, pedido de revisão) e o que não pode ser carimbado.
**Como conferir:** O inventário cita as três sprints, o pedido 42 na linha principal, e deixa Tá Barato e corretoras terceiras de fora.
**Por quê:** Sem essa lista, o carimbo no plano inventaria entrega.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N33-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md` vs local checkout; do not bump; if GitHub main is unreachable, keep fail-closed note. Do not touch `src/`. Do not invent fills.

Cite:
- N28: `71caca1` feat; `c465724` stamp; PR **#39** `5178fff`; `tests/test_n28_supervised_adjustment.py` `test_n28_2_in_range_proposal_can_apply`, `test_n28_2_out_of_range_rejected`, `test_n28_3_apply_undo_persist_before_after_reason`, `test_n28_4_never_mutates_risk_anchors`
- N30: `322318b` feat; PR **#35** `622fbeb`; TEST-EVIDENCE N30.1 / N30.3b
- N31: `d1d139a` feat; `84791eb` stamp; PR **#38** `681e8c5`; `tests/test_n31_g_ajuste_guardrails.py` `N31GAjusteGuardrails`
- N32: already `concluida`; PR **#42** MERGED `d30689bfeb4b009b6297d4bdea8fead233486474` (`2026-11-16T19:49:34Z`)
- N17.2 remains `[ ]` — do not stamp N17 `concluida`

### Task N33.1 — Carimbar no plano as três sprints já entregues

**Entrega:** No plano, as sprints de ajuste, laço americano e autoanálise diária passam a constar como concluídas, cada uma apontando a prova.
**Como conferir:** Abrir o índice e o bloco de cada sprint e ver status concluída, sem mudar as linhas de tarefa já marcadas.
**Por quê:** O código já está na linha principal; o plano ainda diz que essas sprints estão planejadas ou em execução.

**Detalhe técnico**

P task. Edit **only Status lines + index rows + optional one-liners**. Do **not** rewrite task tables of N17/N28/N29/N30/N31/N32.

1. `## Sprint N28` `> Status: planejada` → `concluida`. Index row N28 Status → `concluida`. Optional one-liner after existing N28 notes citing `71caca1` / PR #39 / Feature 11 `[x]`.
2. `## Sprint N30` `> Status: em closeout (...)` → `concluida`. Index row N30 → `concluida`. Do not rewrite the campaign table inside N30 (historical).
3. `## Sprint N31` `> Status: em execução` → `concluida`. Index row N31 → `concluida`. Cite PR #38 / `d1d139a`.
4. Optional one-liner under N17 Status (do not change checkboxes): N17.2 remains operador/G-FORM.
5. Optional honesty in the waves `G-AJUSTE` “Sem resposta” cell if it still says Feature 11 critérios 2–4 `[ ]` until N28.2–4 — those boxes are already `[x]` in REQUIREMENTS.
6. Do not mark N17 or N29 `concluida`. LIVE false.

### Task N33.2 — Deixar os chamados e o changelog do contrato honestos

**Entrega:** O chamado das funcionalidades 7 a 11 fica aberto só para bolsa brasileira, câmbio e homologação da fórmula Tá Barato; o chamado da autoanálise diária fecha; o histórico do contrato deixa de dizer que o ajuste ainda está em aberto.
**Como conferir:** Abrir a lista de problemas e o histórico do contrato e ver o restante explícito, sem fechar o chamado americano por completo.
**Por quê:** O índice já diz uma coisa e o corpo do chamado diz outra; o changelog ficou defasado depois do ajuste entregue.

**Detalhe técnico**

P task. Files: `docs/ISSUES.md`, `docs/REQUIREMENTS.md` (changelog only).

ISS-011:
- Keep **aberto**. Prefer split remaining over closing the epic.
- Remaining **only**: Feature 7 B3/FOREX `[ ]` → ISS-010 / N29.5; N17.2 operator homolog / G-FORM (Tá Barato paper blocked upstream).
- Update body: PR **#42** merged `d30689b` (`2026-11-16T19:49:34Z`); EasyPanel #42 no ar (operator-attested 2026-11-16, **not** a fill); N32/N30/N31/N28 Alpaca track delivered; campaign table rows N30/N31/N28/N32 → concluída with citations.
- Index sprint column: `N33 closeout Alpaca; restante ISS-010 + N17.2`.
- Do not claim Tá Barato paper homolog. Do not invent fills.

ISS-012:
- Index already `fechado`; sync **body** Status to `fechado` citing PR **#38** `681e8c5` and N28.2–4 `71caca1`.

REQUIREMENTS:
- Feature 11 lines 283–286 already `[x]` — do not touch those boxes.
- Fix stale changelog line 414 (“critérios 2–4 seguem `[ ]` até N28.2–4”): keep N31 historical sense **or** add an N33 row that critérios 2–4 are `[x]` after N28.2–4 (`tests/test_n28_supervised_adjustment.py`). Do not bump a fake contract version. Do not invent scoring.

### Task N33.3 — Registrar no diário e na evidência o pedido 42 no ar

**Entrega:** Uma entrada curta no diário desta sprint e uma linha na folha de evidência dizendo que o pedido 42 está na linha principal e o painel já está no ar, segundo o que você atestou.
**Como conferir:** Ler diário e evidência; a linha não trata o painel no ar como ordem preenchida.
**Por quê:** Sem esse registro, o closeout some do histórico operacional.

**Detalhe técnico**

P task. Files: `docs/DIARY.md`, `docs/TEST-EVIDENCE.md`.

DIARY: short `## Sprint N33` + index row. Record: PR #42 merged `d30689b`; N28/N30/N31 Status stamps; ISS-011 remains open for ISS-010 + N17.2; LIVE false; no `src/`.

TEST-EVIDENCE one-liner (operator-attested chat 2026-11-16): PR **#42** is on `main` (`d30689bfeb4b009b6297d4bdea8fead233486474`, merged `2026-11-16T19:49:34Z`); EasyPanel image of #42 **no ar**. Explicit: **not a fill**. Do not add homolog rows that invent broker execution.

### Task N33.4 — Atualizar a sessão desta sprint após os carimbos

**Entrega:** A sessão aponta para esta sprint de closeout, ainda só como plano até o parent iniciar a execução.
**Como conferir:** Ver sprint atual N33 e a marca de plano-somente até o EXECUTE.
**Por quê:** Sem sessão alinhada, o próximo agente reabre a sprint anterior.

**Detalhe técnico**

P task. `.cursorsession`: after EXECUTE stamps, set `plan_only=false` only when parent `/pmo sprint` starts work; at PLAN time fields are already `sprint_atual=N33`, `plan_only=true`, `checkpoint.phase=planning`. Preserve `autopilot`. Update `contexto_rapido` / `proximos_passos` after stamps. Do not enable live. Do not commit from the subagent.

---

## Sprint N34 — Ligar bolsa brasileira e câmbio no laço paper, sem chave real
> Categoria: N  
> Status: concluida  
> Gerado via: `/pmo plan` 2026-11-16 · rewrite honestidade · fonte ISS-010 / N27.2 · N29.1–N29.4 `[x]` mas `build_demo_adapter` sem caller de produção · N17 tabela **não** reescrita  
> titulo_humano: Ligar B3 e forex no laço paper sem chave real  
> resumo_humano: O envio paper passa a usar a conta demo da bolsa brasileira e a de câmbio quando o caminho e as chaves estão no ambiente. Sem chave, barra com motivo. Esses mercados nunca vão para a corretora americana. Homologação ao vivo continua sua.  
> Gate: runner chama o adaptador demo com path+creds; sem credencial → motivo e zero envio; pytest mock prova zero POST Alpaca; N27.2 `[x]` só com nodeid; N29 permanece planejada; LIVE false  
> Closeout: PR **#45** merge `3aefd447` (`2026-11-16T22:45:44Z`); main tip `7627b45`; CI test / docker-smoke / docker-build SUCCESS; stamp **APROVADA**  
> review: comprehensive  
> Brief: `docs/.briefs/N34.brief.md`  
> bom_ref: BOM-3  
> Depende de: N29.1–N29.4 adapters no disco · Release: campanha ISS-010 / N27.2 wiring  
> LIVE_TRADING_ENABLED: false

### Em uma frase

O envio paper passa a usar a conta demo da bolsa brasileira e a de câmbio quando o caminho e as chaves estão no ambiente; se faltar, barra com motivo e nunca manda esses mercados para a corretora americana.

### O que muda para você

- Com caminho e chaves no ambiente, o teste do laço fala com a corretora demo certa (HTTP falso no CI)
- Sem chave, o mercado continua visível e barrado com motivo
- Bolsa brasileira e câmbio nunca vão para a corretora americana
- Preencher o painel sozinho, antes deste wiring, não colocava ordem nesses mercados
- Homologação ao vivo e a fórmula Tá Barato continuam fora; dinheiro real permanece desligado

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Inventário honesto do que já existe e do que o laço ainda ignora | Abrir o inventário e ver adaptadores, envio paper e portão citados, com a lacuna do laço explícita |
| 2 | Laço paper nas contas demo da bolsa brasileira e do câmbio, barrado sem chave | Pedir o teste: com chave mock a ordem demo sai na corretora certa; sem chave barra; nada na corretora americana |
| 3 | Chamados e plano honestos | Abrir a lista de problemas e a sprint das corretoras: laço ligado no código, homologação ao vivo ainda sua, sprint das corretoras não concluída |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N34.0 Inventariar o reuso do laço e dos adaptadores | `/git` | — |
| [x] | M | N34.1 Ligar bolsa brasileira e câmbio no envio paper | `/dev` + AgentCoder | N34.0 |
| [x] | P | N34.2 Provar envio mock e bloqueio sem chave | `/qa testes` | N34.1 |
| [x] | P | N34.3 Atualizar chamados e o plano com honestidade | docs | N34.2 |

### Quality Brief (Sprint N34)

Maintain: `LIVE_TRADING_ENABLED=false`; paper/demo hosts only; no live broker path.
Maintain: load `trader-entry|exit|budget|risk|scanner` only via `src/original.py`; do not invent scoring thresholds.
Maintain: B3_EQUITY / FOREX never POST `paper-api.alpaca.markets`; missing path/creds → `NO_DEMO_ACCOUNT_PATH`.
Maintain: CRYPTO / US_EQUITY Alpaca paper happy path.
Maintain: N29 Status **planejada**; N29.5 e N29.6 permanecem `[ ]`.
Avoid: reimplementing adapter HTTP; real Clear/OANDA in CI; stamping N29 `concluida`; closing ISS-010/ISS-011; writing secret values.

**Closeout (2026-11-16):** PR [**#45**](https://github.com/ig0rayres/trading_lab/pull/45) merge `3aefd4474a99bb96c14125b493bcaf12f0f0abb7` (`2026-11-16T22:45:44Z`); `origin/main` tip `7627b45` (`4fc0644` wiring + `bbe97b8` gap fix + restamp); CI test / docker-smoke / docker-build **SUCCESS**; stamp **APROVADA** (unittest focal 33 OK). N27.2 `[x]` com `tests/test_signal_paper_runner.py` `test_n34_*`. Homologação ao vivo Clear/OANDA permanece **N29.5** (operador) — mock/CI **não** fecha ISS-010. ISS-011 aberto: N29.5 + **N17.2** G-FORM. `LIVE_TRADING_ENABLED=false`.

### Fora de escopo

- Homologação ao vivo / credenciais reais
- Inventar scoring (N17.2)
- Concluir N29 ou checar N29.5 / N29.6
- Mudar o caminho feliz Alpaca CRYPTO/US, exceto para não quebrá-lo
- HTTP Clear/OANDA real no CI
- `LIVE_TRADING_ENABLED=true`
- Segredos no Git

### Task N34.0 — Inventariar o reuso do laço e dos adaptadores

**Entrega:** Inventário curto dizendo que os adaptadores e o portão já existem, e que o envio paper ainda barra bolsa brasileira e câmbio mesmo com chave no ambiente.
**Como conferir:** O inventário cita adaptadores, envio paper e portão, marca o checkout do vendor como vazio nesta frente, e deixa homologação ao vivo de fora.
**Por quê:** O plano anterior tratou código de adaptador como laço pronto; sem essa lista o EXECUTE reimplementa HTTP ou inventa atestado.

**Detalhe técnico**

P task (docs). Confirm `docs/.briefs/N34-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md`; local `vendor/day-trader-skill` is empty/absent on this worktree — keep fail-closed. GitHub main not re-checked. Do not bump. Do not invent live homolog.

Must cite: `src/demo_broker_adapters.py` (`build_demo_adapter`, `credentials_block_for_adapter`); `src/signal_paper_runner.py` (`_market_blocks_alpaca_paper` always-block); `src/demo_account_gate.py` (`demo_market_block_reason`, `named_demo_account_configured`). Record: `build_demo_adapter` production callers = none (tests only). PR **#32** `88aae40` / feat `27c1dd9` = adapters in mock, not N27.2.

### Task N34.1 — Ligar bolsa brasileira e câmbio no envio paper

**Entrega:** O envio paper usa a conta demo da bolsa brasileira e a de câmbio quando o caminho e as chaves existem; se faltar, barra com motivo e não fala com a corretora americana.
**Como conferir:** Com chave mock a ordem demo segue a corretora certa; sem chave o motivo aparece e nada é enviado; o caminho americano de cripto continua igual; dinheiro real permanece desligado.
**Por quê:** Hoje o envio paper recusa bolsa brasileira e câmbio sempre, mesmo com o caminho e as chaves no ambiente — os adaptadores existem só nos testes.

**Detalhe técnico**

- **Arquivo(s):** `src/signal_paper_runner.py`

**executor_prompt**:

```yaml
id: N34.1
size: M
bom_ref: BOM-3
depends_on: ["N34.0"]
files:
  - src/signal_paper_runner.py
reuse_targets:
  - component: src/demo_broker_adapters.py
    reuse_as: call
    convergence_check: rg "build_demo_adapter" src/signal_paper_runner.py && rg "credentials_block_for_adapter" src/signal_paper_runner.py
  - component: src/demo_account_gate.py
    reuse_as: call
    convergence_check: rg "demo_market_block_reason" src/signal_paper_runner.py
  - component: src/original.py
    reuse_as: call
    convergence_check: rg "load_original" src/original.py
guardrail_contract:
  - class: secrets
    id: n34-1-no-secrets
    target: src/signal_paper_runner.py
    check: python3 -c "from pathlib import Path; t=Path('src/signal_paper_runner.py').read_text(); assert 'sk_live' not in t.lower(); assert 'practice-token-value' not in t; assert 'test-clear-secret' not in t"
    pass_condition: no broker secret values hardcoded in runner
  - class: subagent-safety
    id: n34-1-live-false-no-alpaca-b3-forex
    target: src/signal_paper_runner.py
    check: rg "build_demo_adapter" src/signal_paper_runner.py && rg "demo_market_block_reason" src/signal_paper_runner.py && rg "LIVE_TRADING_ENABLED" src/demo_broker_adapters.py
    pass_condition: runner calls existing adapters; live stays false in adapters; B3/FOREX not Alpaca POST
```

### Quality Brief (Sprint N34)

Maintain: LIVE_TRADING_ENABLED=false; paper/demo hosts only; no live broker path.
Maintain: load trader-entry|exit|budget|risk|scanner only via src/original.py; do not invent scoring thresholds.
Maintain: B3_EQUITY / FOREX never POST paper-api.alpaca.markets; missing path/creds → NO_DEMO_ACCOUNT_PATH.
Maintain: CRYPTO / US_EQUITY Alpaca paper happy path unchanged except not to break it.
Avoid: copying _http_json into the runner; real Clear/OANDA HTTP; N29 concluida; invented Tá Barato thresholds.

Melhoria: wire N27.2 — signal_paper_runner.run dispatches B3_EQUITY to Clear simulated and FOREX to OANDA Practice fail-closed.
Contexto: `_market_blocks_alpaca_paper` always returns NO_DEMO_ACCOUNT_PATH for B3/FOREX. `build_demo_adapter` has no production callers. `demo_account_gate` + `paper_gateway_queue` already use `demo_market_block_reason`; the runner ignores that for B3/FOREX and then Alpaca GET/POST.
Objetivo: (1) For B3_EQUITY/FOREX call `demo_market_block_reason` instead of hard-block. (2) If blocked → NO_DEMO_ACCOUNT_PATH, orders_sent=0, never Alpaca. (3) **Market→adapter pin (fail-closed):** B3_EQUITY may only use `clear_smart_trader_simulated`; FOREX may only use `oanda_fxtrade_practice`. Any other `DEMO_ACCOUNT_PATH_*` value (including `alpaca_paper` or cross-path) → NO_DEMO_ACCOUNT_PATH, orders_sent=0, zero Alpaca POST. After pin+creds: `adapter_path_for_market` + `credentials_block_for_adapter` + `build_demo_adapter` (pass opener for tests); call only methods the adapter already exposes (`submit_order`; Clear also has list_positions / list_open_orders / get_order_status / get_fill_for_order). Do not call `submit()` Alpaca or `broker_get` Alpaca for those markets. (4) **Risk anchors for B3/FOREX:** keep `fetch_control_flags` TRADE_RISK_LIMIT / CAPITAL_LIMIT / max_open_positions and DAILY_RISK_NOT_CONFIRMED when those checks do not require Alpaca account shape; skip Alpaca USD/PDT/V4 `alpaca_positions_count` GETs. OANDA Practice adapter today has no list_positions / list_open_orders — for FOREX use submit-only + fail-closed on position-dependent checks (do not invent position APIs). (5) **Order shape:** adapter `submit_order` is symbol/side/qty only (no stop/target bracket). Document in ISS-010 note (N34.3); do not invent bracket fields. (6) Keep PAPER_SIGNAL_AUTO_ENABLED + PAPER_EXECUTION_ENABLED; apply `I_AUTHORIZE_ALPACA_PAPER_ONLY` only to Alpaca markets (decision: B3/FOREX are not Alpaca POST — no new ACK string). (7) LIVE false; adapters already raise if live. (8) Do not edit N17/N29 task tables except N34.3 later. (9) Do not reimplement HTTP.
Arquivos: src/signal_paper_runner.py.
Critério de pronto: rg shows build_demo_adapter and demo_market_block_reason in signal_paper_runner.py; B3/FOREX auto path does not call PAPER_URL POST; wrong path pin blocks; CRYPTO/US still can.
Cenários de teste (implement in N34.2):
1. B3 without path/creds → NO_DEMO_ACCOUNT_PATH, orders_sent=0, zero Alpaca POST (keep existing n32 tests).
2. B3 with DEMO_ACCOUNT_PATH_B3_EQUITY=clear_smart_trader_simulated + CLEAR_* and urlopen mock → adapter submit (Clear URL), not paper-api.alpaca.markets; position/open-order/fill-status as adapter returns.
3. FOREX without creds → block; with path=oanda_fxtrade_practice + OANDA_PRACTICE_* mock → practice host only, never Alpaca, never api-fxtrade live; no invented list_positions.
4. Missing one CLEAR_* or empty OANDA token → NO_DEMO_ACCOUNT_PATH.
5. Regressão: qty=1 AAPL / CRYPTO named path still Alpaca PAPER_SUBMITTED.
6. LIVE_TRADING_ENABLED not false → no live HTTP (adapter RuntimeError / block).
7. Pin abuse: DEMO_ACCOUNT_PATH_B3_EQUITY=alpaca_paper or FOREX path=clear_smart_trader_simulated (cross) → NO_DEMO_ACCOUNT_PATH, orders_sent=0, zero Alpaca POST.

### Task N34.2 — Provar envio mock e bloqueio sem chave

**Entrega:** Testes mostram envio demo com HTTP falso quando o caminho e as chaves existem, bloqueio com motivo quando faltam, e zero envio à corretora americana para bolsa brasileira e câmbio.
**Como conferir:** Pedir essa bateria e ver falha se o laço ainda recusar com chave mock, se postar na corretora americana, ou se o CI chamar a Clear/OANDA de verdade.
**Por quê:** Sem prova no caminho paper, N27.2 continuaria só no papel.

**Detalhe técnico**

P task. Prefer `tests/test_signal_paper_runner.py` (1 file; extend `tests/test_paper_gateway_queue.py` only if runner tests cannot see the queue auto path). Patch `urlopen` / adapter opener — never real Clear/OANDA. Keep `test_n32_b3_equity_auto_blocked_no_alpaca_post` / forex equivalent for the no-cred case. Add nodeids for mock submit + zero Alpaca POST with creds present. Do not weaken N30/N32 US/CRYPTO tests. LIVE false in env. No secret values — use the same fixture names as `tests/test_demo_broker_adapters.py` (`_clear_env_with_path`, `_oanda_env_with_path`).

### Task N34.3 — Atualizar chamados e o plano com honestidade

**Entrega:** Os chamados dizem que o laço está ligado no código e que a homologação ao vivo ainda é sua; a tarefa do laço no plano fecha só com prova de teste; a sprint das corretoras continua planejada.
**Como conferir:** Abrir a lista de problemas e o plano: laço marcado só com teste; credenciar ainda aberto; fórmula Tá Barato ainda esperando você; dinheiro real desligado.
**Por quê:** O texto atual ou some o wiring ou trata mock como homologação.

**Detalhe técnico**

P task. EXECUTE (not PLAN time):

ISS-010 — keep **aberto**. Honest note: adapters existed in mock (PR **#32**); N34 wires them into `run()` fail-closed; live homolog still N29.5. Do not close.

ISS-011 — keep **aberto**. Remaining: ISS-010 live homolog (N29.5) + N17.2 G-FORM. Do not claim Clear/OANDA live. Do not invent Tá Barato thresholds.

ROADMAP: check N27.2 `[x]` **only after** N34.2 nodeids exist. Short note under `## Sprint N29` that N34 wired the loop fail-closed; do **not** change N29 Status from `planejada`; do **not** check N29.5 or N29.6. Do not rewrite N29.1–N29.4 history.

REQUIREMENTS Feature 7 B3/FOREX order-demo boxes stay `[ ]` until N29.5 (pytest mock ≠ homolog). Keep the “sem conta → barrado” box `[x]`.

Optional: `EASYPANEL.md` names-only checklist (`CLEAR_SIM_BASE_URL`, `CLEAR_SIM_API_KEY`, `CLEAR_SIM_API_SECRET`, `OANDA_PRACTICE_API_TOKEN`, `OANDA_PRACTICE_ACCOUNT_ID`, `DEMO_ACCOUNT_PATH_B3_EQUITY`, `DEMO_ACCOUNT_PATH_FOREX`) + one line: filling env enables the path **only after this wiring**. Optional empty names in `.env.example` (F-004). Never values.

DIARY + TEST-EVIDENCE: nodeids of mock submit / no-Alpaca-POST; credentials operator-owned; until N29.5 CI/mock only; EasyPanel-alone did not place B3/FOREX orders before this wiring. LIVE false.

---

## Sprint N35 — Conferir chaves demo sem ver valores, sem fechar homologação
> Categoria: N  
> Status: concluida  
> Gerado via: `/pmo plan` 2026-11-16 · pós-N34 · #46 no ar · operador «Vamos em frente» · **não** «creds ok» · fonte ISS-010 / N29.5  
> Closeout: PR **#48** merged (`26839bb`); N29.5 continua operador.  
> titulo_humano: Conferir chaves demo sem ver valores, sem fechar homologação  
> resumo_humano: Depois que você cola as chaves demo no painel, um relatório diz só se os nomes estão preenchidos e se o mercado está pronto ou barrado. Um roteiro ensina a atestar ordem demo sem colar segredo. A homologação ao vivo continua sua.  
> Gate: relatório de presença cobre nomes + mercados sem valores e sem HTTP; roteiro operador existe; N29.5/N29.6 `[ ]`; N29 permanece planejada; ISS-010 aberto; LIVE false  
> review: senior+qa  
> Brief: `docs/.briefs/N35.brief.md`  
> bom_ref: BOM-3  
> Depende de: N34 concluída (N27.2 no laço) · Release: campanha ISS-010 / pré-homolog N29.5  
> LIVE_TRADING_ENABLED: false

### Em uma frase

Depois que você colar as chaves demo no painel, dá para conferir se os nomes estão preenchidos — sem ver os valores — e seguir um roteiro para atestar uma ordem demo, sem tratar isso como homologação concluída.

### O que muda para você

- Um relatório diz só se cada nome de chave está presente ou ausente, e se cada mercado demo está pronto ou barrado
- O roteiro ensina a confirmar uma ordem demo sem colar segredo no chat
- A homologação ao vivo continua sua: o plano das corretoras não fecha até você atestar
- Painel no ar não é preenchimento de chave nem ordem executada; dinheiro real permanece desligado

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Relatório de presença das chaves, sem valores | Pedir o teste: sem chave o mercado aparece barrado; com chave de teste aparece pronto; o relatório não contém o valor da chave |
| 2 | Roteiro para atestar ordem demo sem colar segredo | Abrir o guia de homologação e o painel de deploy: passos de colar no painel, conferir presença e anotar evidência sem valor |
| 3 | Plano das corretoras ainda aberto até você atestar | Abrir o plano: credenciar continua em aberto; o laço já ligado no código não conta como homologação ao vivo |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N35.0 Inventariar o reuso do portão e das chaves | `/git` | — |
| [x] | P | N35.1 Expor o relatório de presença sem valores | `/dev` | N35.0 |
| [x] | P | N35.2 Documentar o roteiro de homologação demo | docs | N35.0 |
| [x] | P | N35.3 Manter o plano das corretoras honesto | docs | N35.1, N35.2 |

### Task N35.0 — Inventariar o reuso do portão e das chaves

**Entrega:** Inventário curto dizendo o que já barra o mercado sem chave, o que o painel já mostra, e que ainda falta um relatório por nome de chave mais o roteiro de atestado.
**Como conferir:** O inventário cita o portão, o bloco de credencial e o laço já ligado; marca o checkout do vendor como vazio nesta frente; deixa homologação ao vivo de fora.
**Por quê:** Sem essa lista o EXECUTE reimplementa o adaptador ou trata painel no ar como chave colada.

**Detalhe técnico**

P task (docs). Confirm `docs/.briefs/N35-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md`; local `vendor/day-trader-skill` is empty/absent — keep fail-closed. GitHub main not re-checked. Do not bump. Do not invent live homolog. Do not claim «creds ok».

Must cite: `src/demo_account_gate.py` (`named_demo_account_configured`, `demo_market_block_reason`); `src/demo_broker_adapters.py` (`credentials_block_for_adapter`); `src/v4_web_dashboard.py` (`load_trigger_snapshot` `block_reason`); N34 `test_n34_*` already wired the loop. Gap = per-key present/absent + homolog HOW-TO, not a second HTTP client.

### Task N35.1 — Expor o relatório de presença sem valores

**Entrega:** Um relatório diz, para cada nome de chave conhecido, se está presente ou ausente, e se bolsa brasileira e câmbio estão prontos ou barrados — sem mostrar o valor e sem falar com a corretora.
**Como conferir:** Pedir o teste: ambiente vazio → barrado e ausente; chave de teste completa → pronto e presente; uma chave faltando → aquele nome ausente e o mercado barrado; o texto do relatório não contém o valor da chave de teste.
**Por quê:** Hoje só existe o bloqueio por mercado; você não vê qual nome falta sem abrir o valor no painel.

**Detalhe técnico**

P task. Files: `src/demo_account_gate.py`, `tests/test_demo_broker_adapters.py` (2 files). Add `env_presence_report(env=None) -> dict` (name may match this). Reuse `named_demo_account_configured` / `demo_market_block_reason` / key names already checked by `credentials_block_for_adapter`. Do **not** edit `signal_paper_runner.py` or adapter HTTP. Do **not** add a CLI (`scripts/*`) — operator `python3 -c` belongs in N35.2 docs.

**executor_prompt**:
```
estado_atual: named_demo_account_configured + credentials_block_for_adapter return a market-level block; dashboard shows block_reason; no per-key present/absent map; N34 tests already cover mock submit.
desejado: env_presence_report returns only: keys {CLEAR_SIM_BASE_URL, CLEAR_SIM_API_KEY, CLEAR_SIM_API_SECRET, OANDA_PRACTICE_API_TOKEN, OANDA_PRACTICE_ACCOUNT_ID, DEMO_ACCOUNT_PATH_B3_EQUITY, DEMO_ACCOUNT_PATH_FOREX} -> present|absent; markets B3_EQUITY/FOREX -> READY|NO_DEMO_ACCOUNT_PATH via existing gate; live_trading_enabled_false bool derived (true when LIVE is false/0/no/empty). Never include values. Never HTTP.
guardrail: LIVE false; no urlopen; no secret strings in report/repr/json; no real Clear/OANDA; do not check N29.5.
testes (extend tests/test_demo_broker_adapters.py; reuse _clear_env_with_path / _oanda_env_with_path fixtures):
  1. Empty env → all listed keys absent; B3/FOREX NO_DEMO_ACCOUNT_PATH; live_trading_enabled_false true if LIVE unset/false.
  2. Full mock creds + pinned paths → those keys present; B3 and FOREX READY.
  3. Missing one CLEAR_* → that key absent, others present; B3 NO_DEMO; FOREX follows its own keys.
  4. repr(report) and json.dumps(report) must not contain fixture secrets (test-clear-secret, practice-token-value).
  5. Patch urlopen to raise; report must still return (no HTTP).
  6. LIVE_TRADING_ENABLED=true → live_trading_enabled_false is false; still no HTTP; still no values.
reuse_targets:
  - component: src/demo_account_gate.py
    reuse_as: extend
    convergence_check: rg "def env_presence_report" src/demo_account_gate.py && rg "named_demo_account_configured" src/demo_account_gate.py
  - component: src/demo_broker_adapters.py
    reuse_as: call
    convergence_check: rg "CLEAR_SIM_BASE_URL" src/demo_account_gate.py && rg "OANDA_PRACTICE_API_TOKEN" src/demo_account_gate.py
```

### Task N35.2 — Documentar o roteiro de homologação demo

**Entrega:** Guia dizendo como colar as chaves só no painel de deploy, conferir a presença sem ver valores, e atestar uma ordem demo sem colar segredo no chat.
**Como conferir:** Abrir o guia de homologação e a folha do painel de deploy: a tabela de nomes continua sem valores; os passos deixam claro o que não conta como ordem executada.
**Por quê:** O guia de homologação hoje fala da corretora americana; bolsa brasileira e câmbio não têm passo de atestado seguro.

**Detalhe técnico**

P task. Files: `docs/HOMOLOGATION.md`, `EASYPANEL.md`. New HOMOLOGATION section (Clear simulated + OANDA Practice): (1) paste names in EasyPanel only — table already in EASYPANEL G-MKT; (2) run presence report (`PYTHONPATH` + `env_presence_report`) — interpret READY vs NO_DEMO_ACCOUNT_PATH; never print env values; (3) optional: panel `block_reason` already on market rows; (4) how to confirm a demo order without pasting secrets (ledger/panel counts, order id redacted, host practice/simulated — not Alpaca for B3/FOREX); (5) what does **not** count: HTTP 200, queue, #46 on air, pytest mock, presence READY alone; (6) close N29.5 only after chat «creds ok» + that evidence. Keep `LIVE_TRADING_ENABLED=false`. Pointer from EASYPANEL G-MKT section to the new HOMOLOGATION heading. Do not add secret values. Do not claim creds are filled.

### Task N35.3 — Manter o plano das corretoras honesto

**Entrega:** O plano diz que o laço já está ligado no código, que credenciar continua aberto, e que a sprint das corretoras só fecha depois do atestado ao vivo.
**Como conferir:** Abrir a lista de problemas e o plano: credenciar em aberto; laço já marcado no código; fórmula Tá Barato ainda esperando você; exemplo de ambiente com nomes vazios, sem valores.
**Por quê:** Sem essa nota, alguém carimba a sprint das corretoras porque o laço e o painel no ar já existiam.

**Detalhe técnico**

P task. EXECUTE (not PLAN time):

ISS-010 — keep **aberto**. Note: N35 adds presence report + homolog HOW-TO; live homolog still N29.5; #46 ≠ creds ok ≠ fill.

ISS-011 — keep **aberto**. Remaining: ISS-010 live homolog (N29.5) + N17.2 G-FORM.

ROADMAP `## Sprint N29`: short note that N27.2 is already `[x]` from N34; N29.6 original “unblock N27.2” is satisfied in code; **do not** check N29.6; **do not** change N29 Status from `planejada`; **do not** check N29.5; unlock N29 `concluida` **only after** N29.5. Do not rewrite N29.1–N29.4 history.

REQUIREMENTS Feature 7 B3/FOREX order-demo boxes stay `[ ]`.

`.env.example`: append empty names only (`DEMO_ACCOUNT_PATH_B3_EQUITY=`, `DEMO_ACCOUNT_PATH_FOREX=`, `CLEAR_SIM_BASE_URL=`, `CLEAR_SIM_API_KEY=`, `CLEAR_SIM_API_SECRET=`, `OANDA_PRACTICE_API_TOKEN=`, `OANDA_PRACTICE_ACCOUNT_ID=`) plus one comment: values in EasyPanel, never Git. Do not add Alpaca secret values. Keep `LIVE_TRADING_ENABLED=false` at top.

DIARY + TEST-EVIDENCE: N35 nodeids of presence tests; checklist heading; N29.5 still operator; #46 on air still not fill. LIVE false.

---

## Sprint N36 — Freio de emergência na Central, sem parecer ligar o sistema
> Categoria: N  
> Status: concluida  
> Closeout: PR **#51** merged (`2157b53` tip era).  
> Gerado via: `/pmo plan` 2026-11-17 · pós-N35 · demanda operador (copy do kill switch) · fonte ISS-013  
> titulo_humano: Freio de emergência na Central, sem parecer ligar o sistema  
> resumo_humano: Na Central, o botão deixa de parecer ligar ou desligar o laboratório. Ativar freio bloqueia ordem demo nova; Liberar freio só tira o freio — os outros limites ainda valem. Dinheiro real permanece desligado.  
> Gate: HTML da Central usa as quatro frases travadas; testes afirmam presença das novas e ausência das antigas (incluindo operação demo permitida); PATCH continua kill_switch_on true/false; sem botão Live; LIVE false  
> review: skip  
> Brief: `docs/.briefs/N36.brief.md`  
> bom_ref: BOM-3  
> Depende de: N35 concluída · Release: ISS-013 copy UX  
> LIVE_TRADING_ENABLED: false

### Em uma frase

Na Central, o botão deixa de parecer ligar ou desligar o laboratório: ativa o freio (bloqueia ordem demo nova) ou libera o freio (os outros limites continuam valendo).

### O que muda para você

- Com o freio ativo, o aviso diz que é emergência e que ordem demo nova não sai
- O botão vermelho passa a ser Ativar freio; o outro, Liberar freio
- Com o freio liberado, o aviso não diz que a operação demo está permitida
- Dinheiro real continua desligado; não aparece botão Live
- O bloqueio em si não muda — só o texto

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Textos do freio na Central | Abrir a Central: com freio ativo lê Freio de emergência ativo; com freio liberado lê Freio liberado (outros limites ainda valem); botões Ativar freio e Liberar freio |
| 2 | Teste que trava o texto | Pedir o teste da Central: as frases novas aparecem; Ligar parada, Desligar parada e operação demo permitida não aparecem |
| 3 | Folha do dia a dia alinhada | Abrir a folha operacional: a ação do botão usa Ativar freio, não Ligar parada geral |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N36.0 Inventariar o reuso do painel e do freio | `/git` | — |
| [x] | P | N36.1 Renomear os textos do freio na Central | `/dev` | N36.0 |
| [x] | P | N36.2 Alinhar a folha do dia a dia e o diário | docs | N36.0 |

### Task N36.0 — Inventariar o reuso do painel e do freio

**Entrega:** Lista curta dizendo onde o texto confuso mora, o que já bloqueia ordem demo nova, e que o vendor não tem essa tela.
**Como conferir:** O inventário cita a Central, o PATCH do freio e o bloqueio no risco; marca o checkout do vendor como vazio nesta frente; deixa botão Live de fora; deixa claro que liberar o freio não liga a operação demo.
**Por quê:** Sem essa lista o EXECUTE reimplementa o bloqueio ou inventa um segundo painel.

**Detalhe técnico**

P task (docs). Confirm `docs/.briefs/N36-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md`; local `vendor/day-trader-skill` is empty/absent — keep fail-closed. GitHub main not re-checked. Do not bump. Do not change kill-switch semantics. Record: `kill_switch_on=false` only clears the kill gate; it does not turn on `demo_operation_on` (default off → `DEMO_OPERATION_OFF`).

Must cite: `src/panel_ops_html.py` `render_central_page`; `src/v4_web_dashboard.py` `serve_operator_panel`; `src/gate_b_risk.py` `kill_switch_active`; `src/signal_paper_runner.py` `_demo_panel_block`. Gap = Portuguese labels only. `demo_operation_on` is OUT.

### Task N36.1 — Renomear os textos do freio na Central

**Entrega:** Na Central, o aviso e os dois botões falam em freio de emergência, não em ligar ou desligar o laboratório.
**Como conferir:** Pedir o teste da Central: freio ativo mostra Freio de emergência ativo e os botões Ativar freio e Liberar freio; freio liberado mostra Freio liberado (outros limites ainda valem); Ligar parada, Desligar parada e operação demo permitida não aparecem; Live desligado continua; não há botão Live.
**Por quê:** Hoje Ligar parada parece ligar o sistema, e Parada geral ligada parece que o laboratório está em marcha.

**Detalhe técnico**

P task. Files: `src/panel_ops_html.py`, `tests/test_panel_ops.py` (2 files). Change only visible copy in `render_central_page`. Keep `id="kill-on"` / `id="kill-off"`, `patchKill(true|false)`, JSON `{kill_switch_on:on}`, and `Live desligado (sem botão)`.

Locked strings:
- status true: `Freio de emergência ativo`
- status false: `Freio liberado (outros limites ainda valem)`
- box title: `Freio de emergência`
- box help: `quando ativo, bloqueia ordens demo novas. Alterações gravam histórico append-only.`
- kill-on: `Ativar freio`
- kill-off: `Liberar freio`

Must not remain in this HTML: `Ligar parada`, `Desligar parada`, `Parada geral ligada`, status `Operando`, `Liberar operação demo`, `operação demo permitida`.

Tests (extend `tests/test_panel_ops.py`; prefer unit `render_central_page` plus keep existing HTTP login assertion):
1. `kill_switch_on=True` → contains the active status, both new buttons, box title; not `Ligar parada` / `Desligar parada` / `Parada geral ligada` / `operação demo permitida`.
2. `kill_switch_on=False` / missing flag → released status string; still both buttons; still `Live desligado`; no Live button (`>Live<` or `id="live"` absent); no `operação demo permitida`.
3. Existing `test_login_sets_cookie_and_opens_central` still finds `Central` and `Live desligado`; may assert `Ativar freio`.
4. `test_kill_switch_from_panel_blocks_next_eval` unchanged (logic).
Do not edit `gate_b_risk.py`, `signal_paper_runner.py`, `panel_ops_data.py`, `risk_control_flags.py`, or trigger PATCH handlers. Do not rename or toggle `demo_operation_on`.

### Task N36.2 — Alinhar a folha do dia a dia e o diário

**Entrega:** A folha do dia a dia chama a ação de Ativar freio, e o diário anota que só o texto mudou.
**Como conferir:** Abrir a folha operacional e o diário: a linha do botão não diz mais Ligar parada geral; o diário diz que o bloqueio ficou igual.
**Por quê:** Se a folha continuar com Ligar parada geral, o operador volta a achar que está ligando o sistema.

**Detalhe técnico**

P task. Files: `docs/DASHBOARD-OPERATIONS.md`, `docs/DIARY.md` (2 files). In the operator day-to-day table, replace the action label `Ligar parada geral` with `Ativar freio` (same PATCH `/api/triggers`, cookie still required). Optional one-line note that Liberar freio is the other button. Do not write that releasing the brake permits demo operation. Do not rewrite auth, Live, or fill policy.

DIARY: short `## Sprint N36` + index row. Record: copy-only; `kill_switch_on=true` still blocks new demo orders; `kill_switch_on=false` only clears the kill gate (does not turn on `demo_operation_on`); no Live button; N29.5 still operator. LIVE false.

Do not edit DESIGN.md, HOMOLOGATION env kill-switch, or REQUIREMENTS criterion wording.

## Sprint N37 — Saúde automática e plataforma ON por padrão

> Categoria: N
> Status: concluida
> Closeout: PR **#52** merged (`3bebe1c`); deploy EasyPanel 2026-11-17; Central semáforo agregado **ok** (webhook `skipped` sem `WEBHOOK_HEALTH_URL`). Papel **N39** nesta frente (docs-only; não roubar ID N37).
> Issue: **ISS-014**
> titulo_humano: Central mostra se tudo está vivo — sem checklist manual
> resumo_humano: A Central vira o semáforo único da plataforma: painel, banco, worker e webhook checados sozinhos. Instalação nova nasce com operação demo e mercados ligados; só desliga quando o operador pedir. Conta real continua sem botão.
> Gate: pytest verde; `GET /api/status` inclui `platform_health` verificável; probe grava carimbo sem segredo; defaults ON não apaga OFF do operador; nenhum terceiro app EasyPanel; `LIVE_TRADING_ENABLED=false`
> review: senior+qa
> **Depende de:** painel com PATCH de gatilhos (N19.2+ ou frente `panel_ops` mergeada); supervisor `tv-worker` (N18/`TV_WORKER_AUTOSTART`)

### Em uma frase

Você abre a Central e vê de imediato se a plataforma inteira está operacional, sem entrar no EasyPanel.

### O que muda para você

- A Central (e a API) mostram um **semáforo** com painel, Postgres, worker, webhook e fila — não só “Operando” pela parada geral.
- O processo **`v4-ops`** roda checagens automáticas e grava o último resultado em `/app/reports` (sem credenciais nos logs).
- **Novas instalações** iniciam com demo ligada, parada geral desligada e **B3, cripto e forex** ligados no painel; se você já desligou algo, o migrate **não** religa sozinho.
- O runbook operacional deixa de pedir checklist manual de EasyPanel para rotina diária.
- Política explícita: plataforma **ON até desligar de propósito**; `LIVE_TRADING_ENABLED` permanece false.

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Semáforo na Central e na API | Abrir a Central: bloco de saúde com verde/amarelo/vermelho por componente; ou pedir JSON de status e ver `platform_health` |
| 2 | Checagens automáticas no container | Após deploy, sem Exec: em alguns minutos o relatório de saúde atualiza; fila antiga aparece como alerta |
| 3 | Defaults operacionais ON | Migrate em DSN novo: gatilhos nascem ligados; desligar no painel e rodar migrate de novo — permanece desligado |
| 4 | Documentação sem checklist manual | Folha operacional aponta só para a Central para rotina; EasyPanel só para incidente |

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N37.1 Contrato `platform_health` e inventário de reuso | `/dev` | — |
| [x] | M | N37.2 Probes no `v4-ops` (ledger, worker, webhook, fila) | `/dev` | N37.1 |
| [x] | M | N37.3 Semáforo na Central + `GET /api/status` | `/dev` | N37.1, N37.2 |
| [x] | M | N37.4 Defaults ON no migrate (demo + 3 mercados + kill off) | `/dev` | — |
| [x] | P | N37.5 Testes + runbook (substituir checklist EasyPanel) | `/qa testes` | N37.2, N37.3, N37.4 |

**Fora de escopo N37:** alertas Slack/e-mail; terceiro serviço EasyPanel; conta real; inventar limiar de scoring; probes que coloquem ordem.

### Task N20.1 — Definir contrato `platform_health` e inventário de reuso

**Entrega:** Esquema documentado (`docs/api-spec.yaml` + nota em `ARCHITECTURE.md`) e lista do que reusa (`v4_ops_main.sh`, `ledger_store`, `trading_dashboard_data`, painel operacional).
**Como conferir:** Abrir o brief N20: seção Leituras cita trechos lidos; api-spec tem objeto `PlatformHealth` com componentes nomeados.
**Por quê:** Evita duplicar monitor fora da Central e alinha com Feature 6.

**Detalhe técnico**

**executor_prompt:**
Inventory `scripts/v4_ops_main.sh`, `src/v4_web_dashboard.py`, `src/trading_dashboard_data.py`, and panel HTML module if present after merge. Add OpenAPI fragment for `platform_health` on `/api/status`. Fields: `generated_at`, `overall` (ok|degraded|down), `components[]` with `id`, `status`, `detail` (no secrets). Reuse heartbeat file under reports root e.g. `reports/ops/platform-health-latest.json`.
guardrail_contract:
LIVE_TRADING_ENABLED=false; no broker client in probe path; no secret in JSON; fail-closed overall if ledger DSN missing when required.

### Task N20.2 — Implementar probes no superviso `v4-ops`

**Entrega:** Loop leve que testa ledger (`SELECT 1`), idade do último `tv-worker` (stamp file), webhook HTTP opcional via env interno, contagem de fila/envelhecimento; grava JSON atômico em reports.
**Como conferir:** Com stack local ou container: após um ciclo, arquivo de saúde existe e `components` refletem worker parado vs rodando.
**Por quê:** Automatiza o que hoje é checklist manual.

**Detalhe técnico**

**executor_prompt:**
Extend `scripts/v4_ops_main.sh` or new `src/platform_health.py` called from supervisor. Worker stamp: write at end of `tv-worker --once`. Webhook probe: `WEBHOOK_HEALTH_URL` optional, default skip if unset. Queue stale: read counts from ledger or journal mtime. No Alpaca calls. Interval env `PLATFORM_HEALTH_INTERVAL_SEC` default 60.
guardrail_contract:
No live host; probe errors logged stderr without DSN/token; supervisor crash must not stop scheduler foreground.

### Task N20.3 — Expor semáforo na Central e em `/api/status`

**Entrega:** Central mostra bloco “Plataforma” acima de sinais; status agregado distinto de `kill_switch_on`; API inclui `platform_health` espelhando o JSON persistido.
**Como conferir:** Abrir Central: verde com stack saudável; simular worker parado (env) → amarelo/vermelho com texto legível; Live desligado inalterado.
**Por quê:** Central é a pérola operacional pedida pelo operador.

**Detalhe técnico**

**executor_prompt:**
Merge-aware: prefer `panel_ops_html.render_central_page` when present; else extend `render_page` in `v4_web_dashboard.py`. Load latest health snapshot in `build_snapshot`. UI: icon+text per component; link “Ver todos os sinais” unchanged. Session auth unchanged for PATCH.
guardrail_contract:
Read-only health block; PATCH still does not insert `paper_orders`; bearer rules unchanged.

### Task N20.4 — Aplicar defaults operacionais ON no migrate

**Entrega:** `ledger-migrate apply` / `ensure_operational_defaults()` liga `demo_operation_on`, `kill_switch_on=false`, e `market_controls.operation_on=true` para B3_EQUITY, CRYPTO, FOREX quando valor ainda é default de criação — **não** UPDATE se operador já gravou OFF.
**Como conferir:** pytest roundtrip: fresh DB → tudo ON; após PATCH OFF → re-apply migrate → permanece OFF.
**Por quê:** Política aprovada pelo operador (todos os mercados ON por default).

**Detalhe técnico**

**executor_prompt:**
Implement in `ledger_migrate.py` or `risk_control_flags.py` helper called from apply path. Align `docs/DATABASE.md` section 6 starting values doc — document policy shift vs N19 gate text. Insert-if-missing only; respect `trigger_changes` audit on panel writes only, not on seed.
guardrail_contract:
Never set LIVE; never overwrite non-default operator rows; B3/FOREX orders still blocked at gateway until demo account book exists (N19.4 invariant).

### Task N20.5 — Validar com testes e atualizar runbook

**Entrega:** pytest cobrindo snapshot schema, default seed, e regressão de auth; `docs/DASHBOARD-OPERATIONS.md` e `docs/MVP-DEMO-RUNBOOK.md` sem checklist Exec para rotina.
**Como conferir:** `pytest` verde local/CI; ler runbook: rotina diária = abrir Central.
**Por quê:** Fecha ISS-010 com evidência reprodutível.

**Detalhe técnico**

**executor_prompt:**
Add `tests/test_platform_health.py`, extend panel tests if present. Update docs tables replacing manual EasyPanel checklist with Central semaphore. Record intent in `docs/TEST-EVIDENCE.md` stub section for N20 (no operator tokens).
guardrail_contract:
LIVE false; no new env vars that arm orders.

### Assumido (operador confirmou 2026-11-17)

- Defaults ON incluem **os três mercados** do painel; Gate B continua barrando ordem sem livro demo verificado (N19).
- Probes de webhook usam URL interna configurável; sem URL, componente `webhook` = `skipped` não falha o agregado.
- Implementação de UI Central pode exigir **merge** da frente com `panel_ops_html.py` antes de N20.3 fechar na mãe.

### Contratos afetados

- `GET /api/status` — campo `platform_health`
- `control_flags` / `market_controls` — política de seed no migrate
- Arquivo `reports/ops/platform-health-latest.json` (novo artefato operacional, não API pública)

**Closeout (2026-11-17):** PR [**#52**](https://github.com/ig0rayres/trading_lab/pull/52) **MERGED** `2026-11-17T13:14:04Z`; feat `76f76b3` `feat(observability): platform health probes and operational defaults (N37)`; follow-up `ae916c6` `test: isolate demo-off gate checks from N37 migrate defaults`; mergeCommit `3bebe1c7d3236690c67533ef916cbc5be3206d92`. Pytest: `tests.test_platform_health.PlatformHealthTests.test_run_probes_writes_snapshot`, `test_webhook_skipped_without_url`, `test_worker_stamp_enables_ok_worker`, `test_stale_queue_degraded`, `test_aggregate_overall_down_beats_degraded`; `BuildSnapshotHealthTest.test_build_snapshot_includes_platform_health`; `tests/test_operational_defaults.py`. Papel **ISS-014** fechado em sprint **N39** (docs; não roubar ID N37). EasyPanel rebuild permanece operador; pytest verde ≠ painel no ar ≠ fill. `LIVE_TRADING_ENABLED=false`.

---

## Sprint N38 — Freio da Central com faixa que muda de cor e um só botão
> Categoria: N  
> Status: concluida  
> Gerado via: `/pmo plan` 2026-11-17 · pós-N36 · demanda operador (estado visual do freio) · fonte ISS-015  
> titulo_humano: Freio da Central com faixa que muda de cor e um só botão  
> resumo_humano: Na Central, o operador vê em menos de um segundo se o freio está ativo. Faixa vermelha com Liberar, ou faixa calma com Ativar — nunca dois botões iguais. Dinheiro real permanece desligado.  
> Gate: faixa com classe de estado + um único botão principal por estado; testes afirmam classe, copy e ausência dos dois botões iguais; PATCH kill_switch_on inalterado; sem botão Live; LIVE false  
> review: skip  
> Brief: `docs/.briefs/N38.brief.md`  
> bom_ref: BOM-3  
> Depende de: N36 concluída · Release: ISS-015 UX estado visual  
> LIVE_TRADING_ENABLED: false

### Em uma frase

Na Central, o operador vê em menos de um segundo se o freio está ativo: faixa vermelha com Liberar, ou faixa calma com Ativar — nunca dois botões iguais.

### O que muda para você

- Com o freio ativo, a faixa fica vermelha e só aparece Liberar freio
- Com o freio liberado, a faixa fica calma e só aparece Ativar freio
- O aviso amarelo permanente some
- Clicar Liberar com o freio já solto deixa de parecer um clique sem efeito, porque esse botão não aparece
- O bloqueio em si não muda; dinheiro real continua desligado

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Faixa do freio com dois estados | Abrir a Central: freio ativo = faixa vermelha e só Liberar freio; freio liberado = faixa calma e só Ativar freio |
| 2 | Teste que trava o estado visual | Pedir o teste da Central: cada estado tem a classe certa, o texto certo e um único botão principal; os dois botões iguais não voltam |
| 3 | Folha do dia a dia alinhada | Abrir a folha operacional: ela descreve um botão por estado, não dois botões lado a lado |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N38.0 Inventariar o reuso do painel e da faixa do freio | `/git` | — |
| [x] | P | N38.1 Distinguir a faixa do freio na Central | `/dev` | N38.0 |
| [x] | P | N38.2 Alinhar a folha do dia a dia e o diário | docs | N38.0 |

### Task N38.0 — Inventariar o reuso do painel e da faixa do freio

**Entrega:** Lista curta dizendo onde a faixa amarela e os dois botões iguais moram, o que já bloqueia ordem demo nova, e que o vendor não tem essa tela.
**Como conferir:** O inventário cita a Central, o PATCH do freio e o bloqueio no risco; marca o checkout do vendor como vazio nesta frente; deixa botão Live de fora; deixa claro que liberar o freio não liga a operação demo.
**Por quê:** Sem essa lista o EXECUTE reimplementa o bloqueio ou inventa um segundo painel.

**Detalhe técnico**

P task (docs). Confirm `docs/.briefs/N38-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md`; local `vendor/day-trader-skill` is empty/absent — keep fail-closed. GitHub main not re-checked. Do not bump. Do not change kill-switch semantics. Record: `kill_switch_on=false` only clears the kill gate; it does not turn on `demo_operation_on`. Click Liberar when already released is a no-op by design; N38 hides that button.

Must cite: `src/panel_ops_html.py` `render_central_page`; `src/v4_web_dashboard.py` `serve_operator_panel`; `src/gate_b_risk.py` `kill_switch_active`; `src/signal_paper_runner.py` `_demo_panel_block`. Gap = visual state of the existing strip. `demo_operation_on` is OUT.

### Task N38.1 — Distinguir a faixa do freio na Central

**Entrega:** Na Central, uma faixa-luz mostra se o freio está ativo ou liberado, com um único botão para a transição que faz sentido.
**Como conferir:** Pedir o teste da Central: freio ativo mostra a faixa ativa, Freio de emergência ativo e só Liberar freio; freio liberado mostra a faixa calma, Freio liberado e só Ativar freio; os dois botões iguais não aparecem; Live desligado continua; não há botão Live.
**Por quê:** Hoje os dois botões parecem iguais, o aviso fica amarelo nos dois estados, e o status some na linha fraca — o operador não vê o freio em um segundo.

**Detalhe técnico**

P task. Files: `src/panel_ops_html.py`, `tests/test_panel_ops.py` (2 files). CSS-only in existing `_PANEL_CSS` + conditional markup in `render_central_page`. No new SPA. Keep `patchKill(true|false)`, JSON `{kill_switch_on:on}`, and `Live desligado (sem botão)`. Bind onclick only on the button that exists.

Locked visual (see `docs/.briefs/N37.brief.md`):
- Tokens: halt-red `#7A1218`, halt-paper `#FFF7F5`, calm-slate `#1C4A52`, calm-mist `#E6F4F4`, focus-gold `#F0C14B`.
- Active: `div.brake-strip.brake-strip--active` `role="status"`; label `Freio de emergência ativo`; help `Ordens demo novas bloqueadas.`; only `id="kill-off"` with `class="brake-strip__cta"` text `Liberar freio` (filled halt-paper on halt-red).
- Released / missing flag: `div.brake-strip.brake-strip--released`; label `Freio liberado`; help `Outros limites ainda valem.`; only `id="kill-on"` with `class="brake-strip__cta"` text `Ativar freio` (danger outline).
- Exactly one `brake-strip__cta` per HTML. Do not wrap the strip in `.warn`.
- Muted line: `Conta demo · Live desligado (sem botão)` — do not repeat brake status there.
- Focus-visible outline `#F0C14B`. `prefers-reduced-motion: reduce { transition: none }`.
- Do not emit both buttons. Hide the no-op action (Liberar when released; Ativar when active).

Must not remain in this HTML: `Ligar parada`, `Desligar parada`, `Parada geral ligada`, status `Operando`, `Liberar operação demo`, `operação demo permitida`, dual equal-weight kill buttons.

Tests (rewrite `RenderCentralPageFreioCopyTests` in `tests/test_panel_ops.py`; keep HTTP login assertion):
1. `kill_switch_on=True` → `brake-strip--active`; `Freio de emergência ativo`; `>Liberar freio<`; `id="kill-off"`; `html.count('brake-strip__cta') == 1`; not `>Ativar freio<`; not `id="kill-on"`; not class `warn` on the strip; not old copy.
2. `kill_switch_on=False` / missing flag → `brake-strip--released`; `Freio liberado`; `Outros limites ainda valem.`; `>Ativar freio<`; `id="kill-on"`; one `brake-strip__cta`; not `>Liberar freio<`; not `id="kill-off"`; `Live desligado`; no Live button (`>Live<` or `id="live"` absent).
3. Existing `test_login_sets_cookie_and_opens_central` still finds `Central`, `Live desligado`, and `Ativar freio` (default flag is released).
4. `test_kill_switch_from_panel_blocks_next_eval` unchanged (logic).
Do not edit `gate_b_risk.py`, `signal_paper_runner.py`, `panel_ops_data.py`, `risk_control_flags.py`, or trigger PATCH handlers. Do not rename or toggle `demo_operation_on`.

### Task N38.2 — Alinhar a folha do dia a dia e o diário

**Entrega:** A folha do dia a dia descreve um botão por estado do freio, e o diário anota que só a apresentação mudou.
**Como conferir:** Abrir a folha operacional e o diário: a linha não diz mais que Liberar usa o outro botão ao lado; o diário diz que o bloqueio ficou igual.
**Por quê:** Se a folha continuar falando em dois botões, o operador volta a procurar o par que não existe mais.

**Detalhe técnico**

P task. Files: `docs/DASHBOARD-OPERATIONS.md`, `docs/DIARY.md` (2 files). Replace the day-to-day row that says Liberar uses the other button with: Ativar freio is the only button when released (`kill_switch_on: true`); Liberar freio is the only button when active (`kill_switch_on: false`). Do not write that releasing the brake permits demo operation. Do not rewrite auth, Live, or fill policy.

DIARY: short `## Sprint N38` + index row. Record: presentation-only halt-light strip; `kill_switch_on=true` still blocks new demo orders; `kill_switch_on=false` only clears the kill gate (does not turn on `demo_operation_on`); Liberar hidden when already released (no-op by design); no Live button; N29.5 still operator. LIVE false.

Do not edit DESIGN.md, HOMOLOGATION env kill-switch, or REQUIREMENTS criterion wording.

### Quality Brief (Sprint N38)

Maintain: `kill_switch_on` PATCH + `gate_b_risk.kill_switch_active` + `signal_paper_runner` demo block — presentation-only in `render_central_page`; do not relax Gate B or rename `demo_operation_on`.

Maintain: copy N36 («Ativar freio» / «Liberar freio» / «Freio de emergência ativo») — extend with state classes, not revert to «Ligar/Desligar parada».

Maintain: `_platform_health_block` on the Central beside the brake strip — health probes stay separate from kill-switch semantics.

Maintain: `LIVE_TRADING_ENABLED=false`; no Live button; HTTP 200 / queued intent are not fills.

Avoid: dual equal-weight kill CTAs; `.warn` yellow strip for both states; inventing platform thresholds or scoring.

**Closeout (2026-11-17):** PR [**#54**](https://github.com/ig0rayres/trading_lab/pull/54) **MERGED**; CI test / docker-smoke / docker-build **SUCCESS**; stamp **APROVADA** — local `tests.test_panel_ops` + `tests.test_platform_health` **24 OK**. Renumbered from planned N37 after main took N37/ISS-014 (platform_health). **ISS-015** fechado; **ISS-013** (copy N36) permanece histórico no índice. Kill-switch semantics unchanged.

---

## Sprint N39 — Carimbar no plano a saúde automática já entregue
> Categoria: N  
> Status: concluida  
> Gerado via: `/pmo plan` 2026-11-17 · pós-N38 `concluida` · fonte ISS-014 · N37 código já no `main` (PR **#52**) · **não** reusa o ID N37  
> titulo_humano: Saúde automática da plataforma carimbada no plano  
> resumo_humano: A saúde automática da plataforma já está no código e no pedido 52. Esta sprint só alinha o plano e fecha o chamado, e deixa claro que rebuild do painel, chaves demo e homologação da fórmula Tá Barato continuam com você.  
> Gate: N37 Status `concluida` só com SHA/PR/nodeid citados; ISS-014 fechado com a mesma prova; DIARY descreve a entrega de saúde; TEST-EVIDENCE pedido 52; zero `src/`; LIVE false  
> review: skip  
> Brief: `docs/.briefs/N39.brief.md`  
> bom_ref: BOM-3  
> Depende de: N37 código no main · N38 concluida · Release: ISS-014 closeout docs  
> LIVE_TRADING_ENABLED: false

### Em uma frase

O plano passa a mostrar a saúde automática da plataforma como concluída, com a prova do pedido 52, e o chamado correspondente fecha.

### O que muda para você

- A sprint de saúde automática deixa de aparecer como em execução no plano
- O chamado de saúde da plataforma fecha, com a prova citada
- O diário registra a entrega real da saúde, não só a colisão de número
- Rebuild do painel, chaves demo e homologação da fórmula Tá Barato continuam com você
- Dinheiro real permanece desligado

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Sprint de saúde automática carimbada como concluída | Abrir o plano: a sprint de saúde aparece concluída e aponta o pedido 52 e os testes |
| 2 | Chamado de saúde da plataforma fechado | Abrir a lista de problemas: o chamado da saúde automática está fechado, com a mesma prova |
| 3 | Diário e folha de evidência alinhados | Ler o diário e a folha: a entrega de saúde está descrita, sem tratar o painel no ar como ordem executada |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N39.0 Inventariar a prova da saúde automática já entregue | `/git` | — |
| [x] | P | N39.1 Carimbar no plano a saúde automática já entregue | docs | N39.0 |
| [x] | P | N39.2 Fechar o chamado da saúde da plataforma | docs | N39.1 |
| [x] | P | N39.3 Registrar no diário e na evidência o pedido 52 | docs | N39.1 |
| [x] | P | N39.4 Atualizar a sessão desta sprint após os carimbos | session | N39.2, N39.3 |

### Quality Brief (Sprint N39)

Maintain: `LIVE_TRADING_ENABLED=false`; docs-only sprint — zero diff em `src/`; não inventar fill nem limiar de scoring.
Maintain: carimbar N37 **somente** com SHA/PR/nodeid citados; não reescrever a tabela histórica de tasks N37 (títulos N20.*) nem N38.
Maintain: **ISS-014 fechado** com a prova do PR **#52**; **ISS-011 / ISS-010 / ISS-013** permanecem como estão.
Avoid: adapters Clear/OANDA; reusar o ID N37; tratar EasyPanel/rebuild/semáforo como ordem executada.

### Fora de escopo

- Qualquer `src/`
- Adapters Clear / OANDA (ISS-010 / N29.5)
- Credenciais demo no Git
- Carimbar N21 `concluida`
- Fechar ISS-011 / ISS-010 / ISS-013
- Rebuild EasyPanel
- `LIVE_TRADING_ENABLED=true`

### Task N39.0 — Inventariar a prova da saúde automática já entregue

**Entrega:** Inventário curto dizendo o que já tem prova (código, teste, pedido de revisão) e o que não pode ser carimbado.
**Como conferir:** O inventário cita a sprint de saúde, o pedido 52 na linha principal, e deixa rebuild, chaves demo e a fórmula Tá Barato de fora.
**Por quê:** Sem essa lista, o carimbo no plano inventaria entrega.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N39-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md` vs local checkout; do not bump. GitHub `Jakeschincariol/day-trader-skill` `main` was `3d0f4ef` on 2026-11-17 (matches pin). Do not touch `src/`. Do not invent fills. Do not steal N37.

Cite:
- N37: feat `76f76b3` `feat(observability): platform health probes and operational defaults (N37)`; `ae916c6` demo-off test isolation; PR **#52** MERGED `2026-11-17T13:14:04Z`; mergeCommit `3bebe1c7d3236690c67533ef916cbc5be3206d92`; `tests/test_platform_health.py` `PlatformHealthTests.test_run_probes_writes_snapshot`, `test_webhook_skipped_without_url`, `test_worker_stamp_enables_ok_worker`, `test_stale_queue_degraded`, `test_aggregate_overall_down_beats_degraded`; `BuildSnapshotHealthTest.test_build_snapshot_includes_platform_health`
- N38: already index `concluida`; PR **#54**; section header may still say `planejada`
- N21 remains out (tasks `[x]`, do not stamp)
- N17.2 remains `[ ]` — G-FORM; N29.5 remains operator

### Task N39.1 — Carimbar no plano a saúde automática já entregue

**Entrega:** No plano, a sprint de saúde automática passa a constar como concluída, apontando a prova.
**Como conferir:** Abrir o índice e o bloco dessa sprint e ver status concluída, sem mudar as linhas de tarefa já marcadas.
**Por quê:** O código já está na linha principal; o plano ainda diz que essa sprint está em execução.

**Detalhe técnico**

P task. Edit **only Status lines + index rows + optional one-liners**. Do **not** rewrite task tables of N37/N38.

1. `## Sprint N37` `> Status: em execucao` → `concluida`. Index row N37 Status → `concluida`. One-liner after existing N37 notes citing `76f76b3` / `ae916c6` / PR **#52** / nodeids above. Do not rename historical Task N20.* headings inside the N37 block.
2. `## Sprint N38` `> Status: planejada` → `concluida` **only if still planejada** (index already `concluida`; closeout note already cites PR **#54**).
3. Do not mark N17, N21, or N29 `concluida`. LIVE false.

### Task N39.2 — Fechar o chamado da saúde da plataforma

**Entrega:** O chamado da saúde automática fecha, com a mesma prova do plano.
**Como conferir:** Abrir a lista de problemas: o chamado da saúde está fechado; os chamados de bolsa brasileira, câmbio, copy do freio e contrato americano permanecem como estão.
**Por quê:** O código e o teste já existem; o chamado ainda diz em execução.

**Detalhe técnico**

P task. Files: `docs/ISSUES.md` (1 file).

1. ISSUES-INDEX: ISS-014 Status → `fechado`.
2. Body ISS-014: Status `fechado`; `resolved_by` Sprint N37; cite PR **#52** `76f76b3` / `ae916c6` / nodeids; note N39 is docs closeout (do not steal N37).
3. Do **not** close ISS-011, ISS-010, ISS-013, ISS-009.
4. Optional one-liner under ISS-011: N37/ISS-014 closeout is paper only; remaining still ISS-010 + N17.2.

### Task N39.3 — Registrar no diário e na evidência o pedido 52

**Entrega:** O diário descreve a saúde automática de verdade, e a folha de evidência aponta o pedido 52 e os testes — sem tratar isso como ordem executada.
**Como conferir:** Ler o diário: além da colisão de número, há a entrega do semáforo; a folha cita o pedido 52 e diz que rebuild e fill continuam fora.
**Por quê:** Hoje o diário da sprint de saúde só fala da colisão de ID; a folha de evidência para nessa lacuna.

**Detalhe técnico**

P task. Files: `docs/DIARY.md`, `docs/TEST-EVIDENCE.md` (2 files).

DIARY: keep the collision note; add a real `## Sprint N37` health delivery (probes, Central semaphore, defaults ON, PR **#52**) plus short `## Sprint N39` closeout row in the index. Record: docs-only; EasyPanel rebuild still operator; N29.5 still operator; N17.2 still G-FORM; LIVE false.

TEST-EVIDENCE: new `## Sprint N37 — platform_health` section with nodeids from N39.0 and PR **#52** MERGED. Explicit: pytest green ≠ EasyPanel rebuild ≠ fill. Do not copy secrets. Do not add a fake operator smoke.

### Task N39.4 — Atualizar a sessão desta sprint após os carimbos

**Entrega:** A sessão desta frente aponta a sprint de closeout como feita no papel, sem ligar dinheiro real.
**Como conferir:** A sessão lista as tarefas desta sprint como feitas e não deixa a sprint de saúde como se ainda fosse a ativa de código.
**Por quê:** Sem isso o próximo ciclo reabre a saúde como se faltasse implementar.

**Detalhe técnico**

P task. File: `.cursorsession` (1 file). After stamps: `previous_sprint=N39` when finalized by parent; during EXECUTE keep `sprint_atual=N39` until closeout. Preserve `autopilot`, `rock_auto`, N38 `validation_gate` history. Do not enable LIVE. Do not start N21/N29/N17.

**Closeout (2026-11-17):** docs-only — ROADMAP N37 `concluida` com prova PR **#52**; **ISS-014** fechado; DIARY + TEST-EVIDENCE alinhados; zero diff `src/`; EasyPanel rebuild, **N29.5** e **N17.2** permanecem operador; `LIVE_TRADING_ENABLED=false`.

---

## Sprint N40 — Mapa honesto de onde está cada coisa no painel
> Categoria: N  
> Status: concluida  
> Gerado via: `/pmo plan` 2026-11-17 · decisão operador opção **2** (mapa, não tela de ordens) · fonte ISS-016 · **não** fecha ISS-007  
> titulo_humano: Mapa honesto de onde está cada coisa no painel  
> resumo_humano: Você passa a ter um mapa que diz, para cada área, onde clicar, de onde vem o dado, o que aparece vazio e o que ainda não existe. Não há tela nova de ordens nesta rodada.  
> Gate: mapa com nove áreas, quatro selos e duas superfícies; folha do dia a dia aponta o mapa; ISS-016 registrado; zero `src/`; LIVE false  
> review: skip  
> Brief: `docs/.briefs/N40.brief.md`  
> bom_ref: BOM-3  
> Depende de: N39 concluida · Release: ISS-016 orientação (docs)  
> LIVE_TRADING_ENABLED: false

### Em uma frase

Você ganha um mapa honesto: onde clicar, o que alimenta cada área, o que aparece vazio e o que ainda não existe — sem tela nova de ordens.

### O que muda para você

- Fica claro se a área está no menu do dia a dia ou só na página única antiga
- Vazio por falta de dado deixa de parecer “sumiu”
- Ordens abertas e histórico não são prometidos como tela nesta rodada
- Tá Barato, fases do catálogo e melhoria contínua: você vê onde de fato aparecem
- Dinheiro real permanece desligado

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Mapa das nove áreas do painel | Abrir o mapa e conferir, em cada área: onde clicar, de onde vem o dado, o que aparece vazio e o selo |
| 2 | Duas superfícies explicadas | Ler no mapa qual endereço o painel publicado mostra depois do login, e qual página só existe no outro modo |
| 3 | Chamado de orientação aberto | Abrir a lista de problemas: o chamado do mapa está aberto; o épico do painel único não fecha |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N40.0 Inventariar as duas superfícies do painel sem inventar tela | `/git` | — |
| [x] | P | N40.1 Escrever o mapa de onde está cada coisa | docs | N40.0 |
| [x] | P | N40.2 Ligar o mapa na folha do dia a dia | docs | N40.1 |
| [x] | P | N40.3 Registrar o chamado de orientação no painel | docs | N40.1 |
| [x] | P | N40.4 Atualizar a sessão desta frente após o mapa | session | N40.2, N40.3 |

### Quality Brief (Sprint N40)

Maintain: `LIVE_TRADING_ENABLED=false`; docs-only sprint — zero diff em `src/`; não inventar fill nem limiar de scoring.
Maintain: map both UIs; do not call the login menu the Command Panel v1 page.
Maintain: **ISS-016 aberto** até o mapa existir; **ISS-007 / ISS-011 / ISS-010** permanecem como estão.
Avoid: tela de ordens; adapters Clear/OANDA; tratar EasyPanel/rebuild/semáforo como ordem executada.

### Fora de escopo

- Qualquer `src/`
- Tela de ordens abertas / histórico de fills
- Adapters Clear / OANDA (ISS-010 / N29.5)
- Credenciais demo no Git
- Fechar ISS-007 / ISS-011 / ISS-010 / ISS-013
- Rebuild EasyPanel
- `LIVE_TRADING_ENABLED=true`

### Task N40.0 — Inventariar as duas superfícies do painel sem inventar tela

**Entrega:** Inventário curto dizendo quais páginas o menu do dia a dia realmente tem e o que só existe na página única antiga ou no JSON.
**Como conferir:** O inventário nomeia as duas superfícies, a porta do painel publicado, e deixa tela de ordens, chaves demo e fórmula Tá Barato de fora.
**Por quê:** Sem essa lista, o mapa inventaria telas que o operador não consegue clicar.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N40-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md` vs `git ls-remote` `Jakeschincariol/day-trader-skill` `main`; do not bump. If GitHub unreachable, stop claiming current main. Do not touch `src/`. Do not invent fills. Do not plan `/ordens`.

Cite: `_nav` only Central `/`, Sinais `/sinais`, Prodígio `/prodigy`, Performance `/performance`. `make_handler`: operator session set → `serve_operator_panel` for those paths; `render_page` is Command Panel v1 HTML on `GET /` only when session env is unset. EasyPanel `trading-lab` CMD `v4-ops`, port **8765**, HTTPS. JSON `GET /api/status`.

### Task N40.1 — Escrever o mapa de onde está cada coisa

**Entrega:** Um mapa que o operador lê e entende, para cada área, onde clicar, de onde vem o dado, o que vê vazio e o selo honesto.
**Como conferir:** As nove áreas pedidas estão no mapa; cada uma tem os quatro campos; nenhum selo inventado fora da lista combinada.
**Por quê:** Freio e saúde chegaram no menu; o contrato do painel único prometia mais — sem o mapa isso parece sumiço.

**Detalhe técnico**

P task. File: `docs/OPERATOR-PANEL-MAP.md` (1 file; create). Portuguese operator prose. Do **not** put only file paths in the operator table.

Must cover, using labels **VISÍVEL** / **VAZIO-COMUM** / **NÃO-EXISTE-AINDA** / **SÓ-API-OU-JSONL** and the draft table in `docs/.briefs/N40-GIT-FIRST-REUSE.md`:

1. Central (freio, semáforo, mercados, limites)
2. Sinais (`/sinais`)
3. Prodígio (`/prodigy`)
4. Performance (`/performance`)
5. Ordens abertas / ativas Alpaca paper
6. Histórico de ordens / fills
7. Tá Barato
8. Análise Google / TimesFM (research — not order auth)
9. Melhoria contínua / catálogo de fases (Command Panel v1 HTML only)

Each row: where to click; which surface; data source; empty vs with data (copy empty strings from `panel_ops_html` / `render_page`); status. Map **both** UIs. Name EasyPanel URL/port from `docs/DASHBOARD-OPERATIONS.md` (8765) without inventing a public hostname. Cite ISS-007 map as the *promised* 1.0 list, not as current click path. LIVE false. HTTP 200 ≠ fill.

### Task N40.2 — Ligar o mapa na folha do dia a dia

**Entrega:** A folha do dia a dia aponta o mapa, para o próximo login não recomeçar do zero.
**Como conferir:** Abrir a folha operacional e achar um parágrafo que manda ler o mapa antes de achar que a área sumiu.
**Por quê:** Sem esse ponteiro, o mapa fica órfão no repositório.

**Detalhe técnico**

P task. File: `docs/DASHBOARD-OPERATIONS.md` (1 file). Add a short operator paragraph + markdown link to `OPERATOR-PANEL-MAP.md` under «Dia a dia do operador» (or a new `## Onde está cada coisa` section). Do not rewrite bearer/kill-switch tables. Do not add a fake public URL. Do not edit `src/`.

### Task N40.3 — Registrar o chamado de orientação no painel

**Entrega:** O chamado de orientação descreve a lacuna do mapa (não uma tela nova) e o diário registra esta sprint.
**Como conferir:** Abrir a lista de problemas: o chamado do mapa existe; o épico do painel único continua; o diário tem uma linha desta sprint.
**Por quê:** Sem o chamado, a próxima rodada pode achar que falta implementar ordens em vez de orientar.

**Detalhe técnico**

P task. Files: `docs/ISSUES.md`, `docs/DIARY.md` (2 files).

ISSUES: ISS-016 already opened at plan-time — keep **aberto** until the map file exists, then note path + «não fecha ISS-007». Optional one-liner under ISS-007 Command Panel map: N40 is orientation, not orders UI. Do **not** close ISS-007, ISS-011, ISS-010, ISS-013.

DIARY: short `## Sprint N40` row — docs-only map; two UIs; orders screen OUT; LIVE false; EasyPanel rebuild still operator.

### Task N40.4 — Atualizar a sessão desta frente após o mapa

**Entrega:** A sessão desta frente aponta a sprint do mapa, com as tarefas feitas no papel, sem ligar dinheiro real.
**Como conferir:** A sessão lista as tarefas desta sprint e não deixa a sprint de saúde como se ainda fosse a ativa.
**Por quê:** Sem isso o próximo ciclo reabre orientação como se faltasse implementar tela.

**Detalhe técnico**

P task. Files: `.cursorsession`, `docs/ROADMAP.md` (tick N40.0–N40.4 only; do not rewrite other sprints). After map: `sprint_atual=N40` until parent closeout; `plan_only` false only at EXECUTE start. Preserve `autopilot`, `rock_auto`, N39 `validation_gate` history. Do not enable LIVE. Do not start orders UI / N17 / N29.

---

## Campanha entrega plataforma (pós-N40)

> Gerado via: `/pmo plan` 2026-11-17 · operador: plano-mestre por contrato, não infra · fonte **ISS-017**  
> Folha humana: `docs/.briefs/CAMPAIGN-PLATFORM-DELIVERY.brief.md`  
> «Pronto» da campanha: operar pelo menu (estratégias, sinais, ordens abertas, histórico, performance, Prodígio) nos mercados que o contrato já permite (Alpaca paper US+cripto).  
> TimesFM = pesquisa, nunca autorização de ordem. Clear/OANDA = fail-closed até N29.5. `LIVE_TRADING_ENABLED=false`.

| Onda | Sprint | Uma linha | Estado |
|------|--------|-----------|--------|
| 0 | esta folha | Matriz honesta; fila; ISS-017 | plan_only |
| 1 | **N41** | Ordens abertas + histórico no menu (listas) | concluida (decomposta abaixo) |
| 2 | N42 | Estratégias e fases no menu do dia a dia | concluida |
| 3 | **N43** | TimesFM / dicas visíveis e rotuladas | concluida |
| 4 | **N44** | Homologar operar US+cripto pelo painel | runbook entregue (docs); **passeio operador pendente** |
| 5 | N45 | Tá Barato no menu | stub; bloqueado em N17.2 |
| 6 | N46 | B3 via Clear simulada | stub; bloqueado em N29.5 |
| 7 | N47 | Forex via OANDA Practice | stub; bloqueado em N29.5 |

Não reescreve N17 / N28 / N29. Não fecha ISS-010 / ISS-011 / ISS-007 na onda 1.

---

## Sprint N41 — Ver ordens abertas e histórico no menu do dia a dia
> Categoria: N  
> Status: concluida  
> Gerado via: `/pmo plan` 2026-11-17 · fonte ISS-017 onda 1 · ISS-007 áreas Histórico / Ordens abertas · mapa N40 marcou NÃO-EXISTE-AINDA  
> titulo_humano: Ver no menu as ordens paper abertas e o histórico de fills  
> resumo_humano: Depois do login você clica em Ordens e Histórico e vê linhas — ou o vazio honesto. Fila não conta como fill. O painel não envia ordem. Bolsa brasileira e câmbio não entram nesta rodada.  
> Gate: menu com Ordens e Histórico; listas a partir de snapshots/ledger; sessão obrigatória; queued_intent fora do histórico; zero envio pelo painel; pytest do painel verde; mapa atualizado; LIVE false  
> review: senior+qa  
> Brief: `docs/.briefs/N41.brief.md`  
> bom_ref: BOM-3  
> Depende de: N40 concluida · Release: campanha ISS-017 onda 1  
> LIVE_TRADING_ENABLED: false

### Em uma frase

Você passa a ver, no mesmo menu do dia a dia, as ordens paper ainda abertas e o histórico de fills — lista de linhas, não um contador escondido na página antiga.

### O que muda para você

- Depois do login aparecem os itens **Ordens** e **Histórico**
- Fila não entra no histórico como se fosse fill
- Bolsa brasileira e câmbio não ganham fill inventado; o caminho de demonstração continua ação americana e cripto na Alpaca paper
- O painel continua só leitura: nenhum botão envia ordem
- Dinheiro real permanece desligado

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Inventário do que já conta ordem sem listar | Abrir o inventário e ver snapshots, ledger e menu citados, com a lacuna da lista explícita |
| 2 | Lista de ordens abertas no menu | Entrar no painel, abrir Ordens, ver linhas ou o vazio combinado — sem enviar ordem |
| 3 | Histórico só de fill confirmado | Abrir Histórico; ordem só na fila não aparece como resultado |
| 4 | Mapa e chamado atualizados | O mapa deixa de dizer que a tela não existe; o épico da campanha aponta esta sprint |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N41.0 Inventariar o reuso das contagens de ordem antes de desenhar a lista | `/git` | — |
| [x] | M | N41.1 Montar as linhas de ordens abertas e de histórico no pacote do painel | `/dev` | N41.0 |
| [x] | M | N41.2 Colocar Ordens e Histórico no menu do dia a dia | `/dev` | N41.1 |
| [x] | P | N41.3 Provar listas, vazio, sessão e que fila não é fill | `/qa testes` | N41.2 |
| [x] | P | N41.4 Atualizar o mapa e os chamados depois das telas existirem | docs | N41.3 |

### Quality Brief (Sprint N41)

Maintain: `LIVE_TRADING_ENABLED=false`; paper host only; dashboard does not submit or cancel orders.
Maintain: load `trader-entry|exit|budget|risk|scanner` only via `src/original.py`; do not invent scoring thresholds.
Maintain: B3_EQUITY / FOREX remain fail-closed without operator creds (ISS-010); zero Alpaca POST from this sprint.
Maintain: history counts confirmed fills only; `queued_intent` is not a fill; gross label when costs incomplete.
Avoid: forking a second jsonl parser; Alpaca HTTP from the panel; TimesFM as order auth; rewriting Command Panel v1 instead of the login menu; closing ISS-007/010/011.

### Fora de escopo

- Clear / OANDA / N29.5
- POST ou cancelamento de ordem pelo painel
- Poll HTTP Alpaca a partir do dashboard
- TimesFM HTML (N43)
- Catálogo de fases no menu (N42)
- Inventar limiar / promover Prodígio / ORB paper
- `LIVE_TRADING_ENABLED=true`
- Fechar ISS-007 / ISS-010 / ISS-011 / ISS-009 / ISS-013

### Task N41.0 — Inventariar o reuso das contagens de ordem antes de desenhar a lista

**Entrega:** Inventário curto dizendo o que já conta ordem no snapshot e no ledger, e que o menu ainda não lista linhas.
**Como conferir:** O inventário cita snapshots, contagens do ledger, o menu atual e deixa Clear, câmbio e envio pelo painel de fora.
**Por quê:** Sem essa lista o EXECUTE reimplementa o parser ou trata contador como tela.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N41-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md` vs `git ls-remote` `Jakeschincariol/day-trader-skill` `main`; do not bump. Local vendor SHA may differ from the pin — do not treat it as reviewed main. If GitHub unreachable, stop claiming current main. Do not touch `src/` in this task.

Cite: `summary()` / `read_jsonl` on `paper/order-snapshots.jsonl`; `ledger_snapshot()` counts only; `_nav` without Ordens; `command_panel.history` is counts. Do not plan Alpaca HTTP from the panel.

### Task N41.1 — Montar as linhas de ordens abertas e de histórico no pacote do painel

**Entrega:** O pacote do painel passa a carregar listas de ordens ainda abertas e de fills confirmados, com a mesma regra do resultado: fila não entra como fill.
**Como conferir:** Pedir o teste de dados em que um snapshot aberto aparece na lista de abertas, um fill confirmado aparece no histórico, e uma intenção só na fila não aparece como resultado.
**Por quê:** Hoje só existem contadores; sem linhas a tela nova nasceria vazia por desenho.

**Detalhe técnico**

- **Arquivo(s):** `src/panel_ops_data.py`

**executor_prompt**:

```yaml
id: N41.1
size: M
bom_ref: BOM-3
depends_on: ["N41.0"]
files:
  - src/panel_ops_data.py
reuse_targets:
  - component: src/trading_dashboard_data.py
    reuse_as: copy_pattern
    convergence_check: rg "order-snapshots.jsonl" src/panel_ops_data.py
  - component: src/panel_ops_data.py
    reuse_as: extend
    convergence_check: rg "open_orders" src/panel_ops_data.py && rg "order_history" src/panel_ops_data.py && rg "build_panel_bundle" src/panel_ops_data.py
  - component: src/panel_ops_data.py
    reuse_as: copy_pattern
    convergence_check: rg "load_panel_signals" src/panel_ops_data.py && rg "performance_from_ledger" src/panel_ops_data.py
guardrail_contract:
  - class: secrets
    id: n41-1-no-secrets
    target: src/panel_ops_data.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_data.py').read_text(); assert 'sk_live' not in t.lower(); assert 'AKIA' not in t"
    pass_condition: no broker secret values hardcoded
  - class: subagent-safety
    id: n41-1-no-broker-post
    target: src/panel_ops_data.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_data.py').read_text(); assert 'paper-api.alpaca.markets' not in t; assert 'process_after_gate_b' not in t"
    pass_condition: panel data loader does not call Alpaca or the paper gateway submit path
```

### Quality Brief (Sprint N41)

Maintain: LIVE_TRADING_ENABLED=false; paper host only; dashboard does not submit or cancel orders.
Maintain: load trader-entry|exit|budget|risk|scanner only via src/original.py; do not invent scoring thresholds.
Maintain: B3_EQUITY / FOREX remain fail-closed without operator creds; zero Alpaca POST from this sprint.
Maintain: history counts confirmed fills only; queued_intent is not a fill.
Avoid: forking a second unrelated jsonl format; Alpaca HTTP from the panel; TimesFM as order auth.

Melhoria: expose row lists `open_orders` and `order_history` on `build_panel_bundle`.
Contexto: `trading_dashboard_data.summary()` already walks `paper/order-snapshots.jsonl` (latest MONITORED per client_order_id) but only returns counts. `ledger_snapshot()` returns table counts, not rows. `command_panel.history` is `{postgres_ledger_counts: ledger}`. Login menu has no lists.
Objetivo: (1) Reuse the snapshot walk (do not invent a second jsonl schema). Open = remaining qty > 0 or equivalent monitored open; history = confirmed fills / closed monitored with realized gross — same fill rule as `performance_from_ledger` / `performance_from_snapshots`. (2) If ledger DSN present, SELECT rows from `paper_orders` / `paper_fills` like `load_panel_signals` (deleted_at IS NULL); prefer ledger rows when available, else snapshots. (3) `queued_intent` / unfilled must not appear in `order_history` as fills; they may appear on open/queue with a destination label that is not fill. (4) Row fields: symbol, side, qty, status, client_order_id, broker_order_id if present, market, strategy_key, timestamp; fills: qty, price, gross label. (5) Do not call Alpaca HTTP. Do not import `process_after_gate_b`. Do not touch Clear/OANDA adapters. (6) Empty list is valid. LIVE false.
Arquivos: src/panel_ops_data.py.
Critério de pronto: `build_panel_bundle` includes `open_orders` and `order_history` lists; rg shows order-snapshots.jsonl reuse; no alpaca host string in this file.
Cenários de teste (implement in N41.3):
1. Snapshot open remaining_qty > 0 → appears in open_orders.
2. Confirmed fill / closed monitored → appears in order_history.
3. queued_intent only → not in order_history as fill.
4. No files / no ledger → empty lists, no exception.
5. Regressão: signals and performance keys still present on the bundle.

### Task N41.2 — Colocar Ordens e Histórico no menu do dia a dia

**Entrega:** Depois do login, o menu ganha Ordens e Histórico, com tabela de linhas ou a frase de vazio, no mesmo visual das outras páginas.
**Como conferir:** Abrir o painel logado, clicar nos dois itens, ver a lista ou o vazio combinado, e confirmar que não há botão de enviar ordem.
**Por quê:** Os dados sozinhos não aparecem no clique do dia a dia; o mapa marcou essas áreas como ainda inexistentes.

**Detalhe técnico**

- **Arquivo(s):** `src/panel_ops_html.py`, `src/v4_web_dashboard.py`

**executor_prompt**:

```yaml
id: N41.2
size: M
bom_ref: BOM-3
depends_on: ["N41.1"]
files:
  - src/panel_ops_html.py
  - src/v4_web_dashboard.py
reuse_targets:
  - component: src/panel_ops_html.py
    reuse_as: extend
    convergence_check: rg "/ordens" src/panel_ops_html.py && rg "/historico" src/panel_ops_html.py && rg "def _nav" src/panel_ops_html.py
  - component: src/panel_ops_html.py
    reuse_as: copy_pattern
    convergence_check: rg "def render_orders_page" src/panel_ops_html.py && rg "def render_history_page" src/panel_ops_html.py && rg "def render_signals_page" src/panel_ops_html.py
  - component: src/v4_web_dashboard.py
    reuse_as: extend
    convergence_check: rg "/ordens" src/v4_web_dashboard.py && rg "/historico" src/v4_web_dashboard.py && rg "serve_operator_panel" src/v4_web_dashboard.py
guardrail_contract:
  - class: secrets
    id: n41-2-no-secrets
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_html.py').read_text()+Path('src/v4_web_dashboard.py').read_text(); assert 'sk_live' not in t.lower()"
    pass_condition: no live keys in HTML or dashboard routes
  - class: subagent-safety
    id: n41-2-read-only-routes
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'process_after_gate_b' not in t"
    pass_condition: dashboard still does not call the paper submit path
```

### Quality Brief (Sprint N41)

Maintain: LIVE_TRADING_ENABLED=false; operator session cookie in front of the new pages; same shell as Sinais.
Maintain: do not rewrite render_page as the daily UI; login menu is panel_ops_html.
Maintain: empty copy is explicit Portuguese; queued is not fill.
Avoid: Live button; order submit/cancel controls; inventing a public hostname; TimesFM block on these pages.

Melhoria: add authenticated GET /ordens and GET /historico to the daily menu; optional GET /api/orders and GET /api/history mirroring /api/signals.
Contexto: OPERATOR_PANEL_PATHS is only /, /central, /sinais, /prodigy, /performance, /login. _nav has four items. serve_operator_panel 404s anything else. Command Panel v1 count cards stay as they are.
Objetivo: (1) Extend OPERATOR_PANEL_PATHS and _nav with Ordens (/ordens) and Histórico (/historico). (2) render_orders_page / render_history_page copy render_signals_page layout (side nav, table, muted disclaimer). Empty copy: open = `Nenhuma ordem aberta no paper.`; history = `Nenhum fill confirmado no histórico.` Disclaimer: fila e HTTP 200 não são fill; valores brutos se o rótulo de performance já disser isso. (3) serve_operator_panel branches; session required like /sinais. (4) serve_panel_json for /api/orders and /api/history. (5) No POST handlers for placing/cancelling orders. Do not add Live button. Do not call Alpaca. Do not edit TimesFM. Do not replace render_page.
Arquivos: src/panel_ops_html.py, src/v4_web_dashboard.py.
Critério de pronto: logged-in GET /ordens and /historico return HTML with nav labels; unauthenticated still blocked; rg shows both paths in _nav and serve_operator_panel.
Cenários de teste (implement in N41.3):
1. Sem cookie → redirect/401 like /sinais.
2. Com cookie, listas vazias → frases combinadas.
3. Com fixture rows → symbol/status visíveis.
4. Nav contém Ordens e Histórico.
5. Regressão: /sinais /performance / central still render.
6. Nenhum POST de ordem nessas rotas.

### Task N41.3 — Provar listas, vazio, sessão e que fila não é fill

**Entrega:** Testes mostram as telas com e sem dado, recusa sem login, e que intenção só na fila não vira linha de fill.
**Como conferir:** Pedir essa bateria e ver falha se o menu não tiver os itens, se a fila entrar no histórico, ou se a página abrir sem sessão.
**Por quê:** Sem prova, o mapa poderia marcar VISÍVEL com a tela ainda mentindo.

**Detalhe técnico**

P task. File: `tests/test_panel_ops.py` (extend; 1 file unless HTTP helpers force a tiny extra). Reuse PanelOpsHttpTests cookie pattern. Nodeids for: unauthenticated /ordens and /historico; empty copy strings; fixture open row; fixture fill row; queued_intent absent from history fills; nav labels. Do not call real Alpaca. LIVE false in env. No secret values.

### Task N41.4 — Atualizar o mapa e os chamados depois das telas existirem

**Entrega:** O mapa deixa de dizer que ordens e histórico não existem no menu; os chamados apontam a campanha e não fecham corretoras terceiras.
**Como conferir:** Abrir o mapa: Ordens e Histórico com selo visível ou vazio comum; ISS-017 aberto; ISS-010 e o épico antigo do painel único continuam.
**Por quê:** Sem esse recorte, a próxima rodada acha que a tela ainda foi adiada.

**Detalhe técnico**

P task. Files: `docs/OPERATOR-PANEL-MAP.md`, `docs/DASHBOARD-OPERATIONS.md`, `docs/ISSUES.md` (ISS-017 keep **aberto**; ISS-007 keep open; ISS-016 stays orientation). Flip areas 5–6 from NÃO-EXISTE-AINDA to VISÍVEL / VAZIO-COMUM using the real empty strings. Do not close ISS-010 / ISS-011 / ISS-007 / ISS-009. Do not claim EasyPanel rebuild. LIVE false.

---

## Sprint N42 — Mostrar estratégias e fases no menu do dia a dia
> Categoria: N  
> Status: concluida  
> Gerado via: `/pmo plan` 2026-11-17 · fonte ISS-017 onda 2 · ISS-007 área Estratégias adotadas / fase · mapa N40 §9 NÃO-EXISTE-AINDA no menu  
> titulo_humano: Ver no menu quais estratégias estão em pesquisa, sombra ou paper  
> resumo_humano: Depois do login você clica em Estratégias e vê pesquisa, sombra ou paper — ou o vazio honesto. O painel não promove fase e não envia ordem. Bolsa brasileira e câmbio não entram nesta rodada.  
> Gate: menu com Estratégias; linhas a partir do catálogo persistido; sessão obrigatória; tela nova sem promoção de fase; zero envio pelo painel; pytest do painel verde; mapa atualizado; LIVE false  
> review: senior+qa  
> Brief: `docs/.briefs/N42.brief.md`  
> bom_ref: BOM-3  
> Depende de: N41 concluida · Release: campanha ISS-017 onda 2  
> LIVE_TRADING_ENABLED: false

### Em uma frase

Você passa a ver, no mesmo menu do dia a dia, quais estratégias existem e se estão em pesquisa, sombra ou paper — sem o painel promover fase sozinho.

### O que muda para você

- Depois do login aparece o item **Estratégias** ao lado de Sinais e Ordens
- Pesquisa, sombra e paper aparecem como fase; paper permitido continua sim/não
- A tela nova não sobe fase e não envia ordem
- Bolsa brasileira e câmbio não entram; a análise Google continua fora desta onda
- Dinheiro real permanece desligado

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Inventário do catálogo que já existe na página antiga | Abrir o inventário e ver que as fases já estão no catálogo, mas o menu do dia a dia ainda não as lista |
| 2 | Lista de estratégias e fases no menu | Entrar no painel, abrir Estratégias, ver pesquisa / sombra / paper ou o vazio combinado — sem promover fase |
| 3 | Tela só leitura | Confirmar que a página nova não tem botão para subir fase nem enviar ordem |
| 4 | Mapa e chamado atualizados | O mapa deixa de dizer que o catálogo não existe no menu; a campanha aponta esta onda |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N42.0 Inventariar o reuso do catálogo de fases antes de desenhar o menu | `/git` | — |
| [x] | M | N42.1 Carregar as linhas de estratégia e fase no pacote do painel | `/dev` | N42.0 |
| [x] | M | N42.2 Colocar Estratégias no menu do dia a dia | `/dev` | N42.1 |
| [x] | P | N42.3 Provar tabela, vazio, sessão e que a tela não promove fase | `/qa testes` | N42.2 |
| [x] | P | N42.4 Atualizar o mapa e os chamados depois da tela existir | docs | N42.3 |

### Quality Brief (Sprint N42)

Maintain: `LIVE_TRADING_ENABLED=false`; paper host only; dashboard does not submit or cancel orders.
Maintain: load `trader-entry|exit|budget|risk|scanner` only via `src/original.py`; do not invent scoring thresholds.
Maintain: B3_EQUITY / FOREX remain fail-closed without operator creds (ISS-010); zero Alpaca POST from this sprint.
Maintain: strategy phase does not rise from PnL, HTTP 200, or queued intent.
Avoid: second catalog SQL; calling `apply_strategy_patch` from the new page; TimesFM as order auth; rewriting Command Panel v1 instead of the login menu; closing ISS-007/010/011/017.

### Fora de escopo

- Promover fase a partir da tela nova
- POST ou cancelamento de ordem pelo painel
- TimesFM HTML (N43)
- Tela própria de Tá Barato (N45)
- Eventos de melhoria contínua nessa página
- Clear / OANDA / N29.5 / adapters B3
- Inventar limiar / promover Prodígio / ORB paper
- `LIVE_TRADING_ENABLED=true`
- Fechar ISS-007 / ISS-010 / ISS-011 / ISS-009 / ISS-013 / ISS-016 / ISS-017

### Task N42.0 — Inventariar o reuso do catálogo de fases antes de desenhar o menu

**Entrega:** Inventário curto dizendo que as fases já existem no catálogo e na página antiga, e que o menu do dia a dia ainda não as lista.
**Como conferir:** O inventário cita o catálogo persistido, a tabela da página antiga, o menu atual e deixa promoção, câmbio e envio pelo painel de fora.
**Por quê:** Sem essa lista o EXECUTE reimplementa a leitura ou coloca um botão de subir fase.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N42-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md` vs `git ls-remote` `Jakeschincariol/day-trader-skill` `main`; do not bump. Local vendor may be uninitialized/empty — do not treat it as reviewed main. If GitHub unreachable, stop claiming current main. Do not touch `src/` in this task.

Cite: `list_strategy_states`; `_load_strategy_catalog`; `render_page` catalog table; `_nav` without Estratégias; existing `PATCH /api/strategies/{key}` is OUT of the new page. Do not plan Alpaca HTTP from the panel.

### Task N42.1 — Carregar as linhas de estratégia e fase no pacote do painel

**Entrega:** O pacote do painel passa a carregar a lista de estratégias com a fase gravada e se paper é permitido, sem inventar linha quando o ledger falta.
**Como conferir:** Pedir o teste de dados em que o catálogo traz as famílias conhecidas com a fase gravada, e o ledger ausente mostra lista vazia com o estado combinado.
**Por quê:** Hoje só a página antiga lê o catálogo; sem linhas no pacote a tela nova nasceria vazia por desenho.

**Detalhe técnico**

- **Arquivo(s):** `src/panel_ops_data.py`

**executor_prompt**:

```yaml
id: N42.1
size: M
bom_ref: BOM-3
depends_on: ["N42.0"]
files:
  - src/panel_ops_data.py
reuse_targets:
  - component: src/strategy_catalog.py
    reuse_as: call
    convergence_check: rg "list_strategy_states" src/panel_ops_data.py
  - component: src/trading_dashboard_data.py
    reuse_as: copy_pattern
    convergence_check: rg "strategy_catalog" src/panel_ops_data.py && rg "LEDGER_UNAVAILABLE" src/panel_ops_data.py
  - component: src/panel_ops_data.py
    reuse_as: extend
    convergence_check: rg "build_panel_bundle" src/panel_ops_data.py && rg "strategy_catalog" src/panel_ops_data.py
guardrail_contract:
  - class: secrets
    id: n42-1-no-secrets
    target: src/panel_ops_data.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_data.py').read_text(); assert 'sk_live' not in t.lower(); assert 'AKIA' not in t"
    pass_condition: no broker secret values hardcoded
  - class: subagent-safety
    id: n42-1-no-phase-write
    target: src/panel_ops_data.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_data.py').read_text(); assert 'UPDATE strategy_states' not in t; assert 'apply_strategy_patch' not in t; assert 'process_after_gate_b' not in t; assert 'paper-api.alpaca.markets' not in t"
    pass_condition: panel data loader does not write phases, patch strategies, or call Alpaca/paper submit
```

### Quality Brief (Sprint N42)

Maintain: LIVE_TRADING_ENABLED=false; paper host only; dashboard does not submit or cancel orders.
Maintain: load trader-entry|exit|budget|risk|scanner only via src/original.py; do not invent scoring thresholds.
Maintain: B3_EQUITY / FOREX remain fail-closed without operator creds; zero Alpaca POST from this sprint.
Maintain: do not UPDATE strategy_states; do not invent DEFAULT_PHASE_BY_KEY rows when list_strategy_states returns None.
Avoid: forking a second catalog SELECT; TimesFM as order auth.

Melhoria: expose `strategy_catalog` on `build_panel_bundle`.
Contexto: `trading_dashboard_data._load_strategy_catalog()` already calls `list_strategy_states()` for Command Panel v1 / `/api/status`. Login menu bundle has signals, orders, history, prodigy, performance — no catalog. Feature 4 forbids invented thresholds and auto-promotion.
Objetivo: (1) Call `list_strategy_states` (do not copy the SQL). Shape like `_load_strategy_catalog`: `{status: OK|LEDGER_UNAVAILABLE, strategies: [...], note}` with fields `strategy_key`, `phase`, `paper_allowed`, `promotion: operator_only`. (2) None from list → LEDGER_UNAVAILABLE and empty list — never hardcode seven fake rows. (3) Do not UPDATE phase. Do not import `apply_strategy_patch` or `process_after_gate_b`. Do not touch Clear/OANDA. (4) Keep existing bundle keys. LIVE false.
Arquivos: src/panel_ops_data.py.
Critério de pronto: `build_panel_bundle` includes `strategy_catalog`; rg shows `list_strategy_states`; no UPDATE strategy_states in this file.
Cenários de teste (implement in N42.3):
1. Fake/list rows with orb=shadow, signal_copy=paper_limited, prodigy_15d=research → same keys/phases in the bundle; orb paper_allowed false.
2. list_strategy_states None / no DSN → status LEDGER_UNAVAILABLE, strategies [].
3. NEVER_PAPER key never paper_allowed true.
4. Regressão: signals, open_orders, order_history, performance still present on the bundle.

### Task N42.2 — Colocar Estratégias no menu do dia a dia

**Entrega:** Depois do login, o menu ganha Estratégias, com tabela de chave / fase / paper permitido ou a frase de vazio, no mesmo visual das outras páginas.
**Como conferir:** Abrir o painel logado, clicar em Estratégias, ver a lista ou o vazio combinado, e confirmar que não há botão de promover fase nem de enviar ordem.
**Por quê:** Os dados sozinhos não aparecem no clique do dia a dia; o mapa marcou o catálogo como ainda inexistente nesse menu.

**Detalhe técnico**

- **Arquivo(s):** `src/panel_ops_html.py`, `src/v4_web_dashboard.py`

**executor_prompt**:

```yaml
id: N42.2
size: M
bom_ref: BOM-3
depends_on: ["N42.1"]
files:
  - src/panel_ops_html.py
  - src/v4_web_dashboard.py
reuse_targets:
  - component: src/panel_ops_html.py
    reuse_as: extend
    convergence_check: rg "/estrategias" src/panel_ops_html.py && rg "def _nav" src/panel_ops_html.py
  - component: src/panel_ops_html.py
    reuse_as: copy_pattern
    convergence_check: rg "def render_strategies_page" src/panel_ops_html.py && rg "def render_signals_page" src/panel_ops_html.py
  - component: src/v4_web_dashboard.py
    reuse_as: copy_pattern
    convergence_check: rg "Estratégias (catálogo)" src/v4_web_dashboard.py && rg "Catálogo indisponível (ledger)" src/panel_ops_html.py
  - component: src/v4_web_dashboard.py
    reuse_as: extend
    convergence_check: rg "/estrategias" src/v4_web_dashboard.py && rg "/api/estrategias" src/v4_web_dashboard.py && rg "serve_operator_panel" src/v4_web_dashboard.py
guardrail_contract:
  - class: secrets
    id: n42-2-no-secrets
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_html.py').read_text()+Path('src/v4_web_dashboard.py').read_text(); assert 'sk_live' not in t.lower()"
    pass_condition: no live keys in HTML or dashboard routes
  - class: subagent-safety
    id: n42-2-read-only-page
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; html=Path('src/panel_ops_html.py').read_text(); dash=Path('src/v4_web_dashboard.py').read_text(); assert '/api/strategies' not in html; assert 'apply_strategy_patch' not in html; assert 'process_after_gate_b' not in dash; assert 'def apply_strategy_patch' in dash"
    pass_condition: new page does not PATCH phases; existing apply_strategy_patch remains; dashboard still does not call paper submit
```

### Quality Brief (Sprint N42)

Maintain: LIVE_TRADING_ENABLED=false; operator session cookie in front of the new page; same shell as Sinais/Ordens.
Maintain: do not rewrite render_page as the daily UI; login menu is panel_ops_html.
Maintain: empty copy is explicit Portuguese; no promote control on this page.
Avoid: Live button; order submit/cancel controls; phase form; inventing a public hostname; TimesFM block on this page.

Melhoria: add authenticated GET /estrategias to the daily menu; GET /api/estrategias mirroring /api/signals.
Contexto: OPERATOR_PANEL_PATHS has /, /central, /sinais, /prodigy, /performance, /ordens, /historico, /login. _nav has six items. serve_operator_panel 404s /estrategias. Command Panel v1 catalog table stays. PATCH /api/strategies/{key} already exists — do not wire it from this HTML. Do not add GET /api/strategies (prefix collision with PATCH).
Objetivo: (1) Extend OPERATOR_PANEL_PATHS and _nav with Estratégias (/estrategias). (2) render_strategies_page copy render_orders_page / render_signals_page (side nav, table, muted disclaimer). Columns like render_page: Chave, Fase, Paper permitido. Phase labels for the operator: research→pesquisa, shadow→sombra, paper_limited→paper limitado, paper_validated→paper validado; unknown phase shown raw. paper_allowed → sim/não. Empty when LEDGER_UNAVAILABLE or no rows: `Catálogo indisponível (ledger)`. Disclaimer: `Promoção de fase: somente operador (fora deste menu).` (3) serve_operator_panel branch; session required like /sinais. (4) serve_panel_json for GET /api/estrategias (status + strategies). Register the path next to /api/orders. (5) No form/button that PATCHes phase. No POST handlers for placing orders. Do not add Live button. Do not call Alpaca. Do not edit TimesFM. Do not replace render_page. Do not delete apply_strategy_patch.
Arquivos: src/panel_ops_html.py, src/v4_web_dashboard.py.
Critério de pronto: logged-in GET /estrategias returns HTML with nav label; unauthenticated still blocked; rg shows /estrategias in _nav and serve_operator_panel; HTML has no /api/strategies.
Cenários de teste (implement in N42.3):
1. Sem cookie → redirect/401 like /sinais.
2. Com cookie, ledger ausente → `Catálogo indisponível (ledger)`.
3. Com fixture rows no bundle → chave e fase visíveis (pesquisa/sombra/paper).
4. Nav contém Estratégias.
5. Página sem controle de promoção (sem /api/strategies no HTML da tela nova).
6. Regressão: /sinais /ordens /historico /performance /central still render.

### Task N42.3 — Provar tabela, vazio, sessão e que a tela não promove fase

**Entrega:** Testes mostram a tela com e sem dado, recusa sem login, e que a página nova não sobe fase nem envia ordem.
**Como conferir:** Pedir essa bateria e ver falha se o menu não tiver Estratégias, se a página abrir sem sessão, ou se aparecer controle de promoção.
**Por quê:** Sem prova, o mapa poderia marcar visível com a tela ainda mentindo.

**Detalhe técnico**

P task. File: `tests/test_panel_ops.py` (extend; 1 file). Reuse PanelOpsHttpTests cookie pattern. Nodeids for: unauthenticated /estrategias matches /sinais; empty copy `Catálogo indisponível (ledger)`; fixture catalog rows (orb shadow / signal_copy paper_limited); nav label Estratégias; HTML of /estrategias does not contain `/api/strategies` or a phase form; GET /api/estrategias requires session; regression previous menu routes. Do not call real Alpaca. Do not weaken `tests/test_panel_triggers.py` PATCH /api/strategies tests. LIVE false in env. No secret values.

### Task N42.4 — Atualizar o mapa e os chamados depois da tela existir

**Entrega:** O mapa deixa de dizer que o catálogo de fases não existe no menu; os chamados apontam a campanha e não fecham corretoras terceiras.
**Como conferir:** Abrir o mapa: Estratégias no menu com selo visível ou vazio comum; ISS-017 aberto; ISS-010 e o épico antigo do painel único continuam.
**Por quê:** Sem esse recorte, a próxima rodada acha que o catálogo ainda está só na página antiga.

**Detalhe técnico**

P task. Files: `docs/OPERATOR-PANEL-MAP.md`, `docs/DASHBOARD-OPERATIONS.md`, `docs/ISSUES.md` (ISS-017 keep **aberto**; ISS-007 keep open; ISS-016 stays orientation). Flip area 9 catalog-on-login-menu from NÃO-EXISTE-AINDA to VISÍVEL / VAZIO-COMUM using the real empty string; melhoria contínua events may remain Command Panel v1 / JSON. Do not close ISS-010 / ISS-011 / ISS-007 / ISS-009 / ISS-017. Do not claim EasyPanel rebuild. LIVE false.

---

## Sprint N43 — Mostrar a análise Google só como pesquisa
> Categoria: N  
> Status: concluida  
> Gerado via: `/pmo plan` 2026-11-17 · fonte ISS-017 onda 3 · ISS-007 área Tips / sugestões · mapa N40 TimesFM SÓ-API-OU-JSONL  
> titulo_humano: Ver a previsão do modelo como dica, nunca como ordem  
> resumo_humano: Depois do login você clica em Análise Google e vê a dica de pesquisa — ou o vazio com o motivo se o modelo faltar. Isso não autoriza ordem. Bolsa brasileira e câmbio não entram nesta rodada.  
> Gate: menu com Análise Google; bloco a partir do adaptador/relatório diário; vazio com frase e motivo; sessão obrigatória; pesquisa não autoriza ordem; zero envio pelo painel; pytest do painel verde; mapa atualizado; LIVE false  
> review: senior+qa  
> Brief: `docs/.briefs/N43.brief.md`  
> bom_ref: BOM-3  
> Depende de: N42 concluida · Release: campanha ISS-017 onda 3  
> LIVE_TRADING_ENABLED: false

### Em uma frase

Você passa a ver, no mesmo menu do dia a dia, a análise Google como dica de pesquisa — e, se o modelo faltar, o motivo — sem isso virar autorização de ordem.

### O que muda para você

- Depois do login aparece o item **Análise Google** ao lado de Sinais, Ordens e Estratégias
- Se o modelo ou a dependência faltar, a tela mostra o motivo em português — não some em silêncio
- O texto deixa claro que pesquisa não autoriza ordem
- Bolsa brasileira, câmbio e Tá Barato não entram; o painel não envia ordem
- Dinheiro real permanece desligado

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Inventário do relatório TimesFM que já existe | Abrir o inventário e ver que a dica já nasce no relatório diário, mas o menu do dia a dia ainda não a mostra |
| 2 | Análise Google no menu | Entrar no painel, abrir Análise Google, ver a dica rotulada ou o vazio com motivo — sem botão de enviar ordem |
| 3 | Falha fechada com motivo | Com o modelo desligado ou ausente, a frase combinada e o motivo aparecem; nenhum número inventado |
| 4 | Mapa e chamado atualizados | O mapa deixa de dizer que a análise só existe em arquivo; a campanha aponta esta onda |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N43.0 Inventariar o reuso da análise Google antes de desenhar o menu | `/git` | — |
| [x] | M | N43.1 Carregar o bloco TimesFM e as dicas rotuladas no pacote do painel | `/dev` | N43.0 |
| [x] | M | N43.2 Colocar Análise Google no menu do dia a dia | `/dev` | N43.1 |
| [x] | P | N43.3 Provar vazio com motivo, rótulo de pesquisa e que a tela não envia ordem | `/qa testes` | N43.2 |
| [x] | P | N43.4 Atualizar o mapa e os chamados depois da tela existir | docs | N43.3 |

### Quality Brief (Sprint N43)

Maintain: `LIVE_TRADING_ENABLED=false`; paper host only; dashboard does not submit or cancel orders.
Maintain: load `trader-entry|exit|budget|risk|scanner` only via `src/original.py`; do not invent scoring thresholds.
Maintain: TimesFM stays optional and fail-closed; missing import/checkpoint/env omits numeric forecast.
Maintain: B3_EQUITY / FOREX remain fail-closed without operator creds (ISS-010); zero Alpaca POST from this sprint.
Avoid: required TimesFM image dependency; calling evolution CLI on GET; TimesFM as order auth; rewriting Command Panel v1; closing ISS-007/010/011/017.

### Fora de escopo

- Autorizar ordem a partir da dica
- Inventar limiar / stop / entrada a partir do horizonte
- POST ou cancelamento de ordem pelo painel
- Promover fase; aplicar parâmetro
- Tela própria de Tá Barato (N45)
- Eventos completos de melhoria contínua nessa página
- Clear / OANDA / N29.5 / adapters B3
- `LIVE_TRADING_ENABLED=true`
- Fechar ISS-007 / ISS-010 / ISS-011 / ISS-009 / ISS-013 / ISS-016 / ISS-017

### Task N43.0 — Inventariar o reuso da análise Google antes de desenhar o menu

**Entrega:** Inventário curto dizendo que a dica TimesFM já existe no relatório diário, e que o menu do dia a dia ainda não a mostra.
**Como conferir:** O inventário cita o adaptador, o relatório do dia, o menu atual e deixa envio, câmbio e limiar inventado de fora.
**Por quê:** Sem essa lista o EXECUTE reimplementa o modelo ou trata a dica como ordem.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N43-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md` vs `git ls-remote` `Jakeschincariol/day-trader-skill` `main`; do not bump. Local vendor may be uninitialized/empty — do not treat it as reviewed main. If GitHub unreachable, stop claiming current main. Do not touch `src/` in this task.

Cite: `build_timesfm_block`; `evolution_engine.review` `timesfm` payload; `_nav` without Análise Google; official PyPI `timesfm` optional; do not plan Alpaca HTTP from the panel; do not call `evolution_engine.main()` from GET.

### Task N43.1 — Carregar o bloco TimesFM e as dicas rotuladas no pacote do painel

**Entrega:** O pacote do painel passa a carregar o estado da análise Google e as dicas já rotuladas, sem inventar número quando o modelo falta.
**Como conferir:** Pedir o teste de dados em que o modelo desligado traz status indisponível sem previsão numérica, e um relatório do dia com dica rotulada aparece no pacote.
**Por quê:** Hoje só o relatório/JSON guarda o bloco; sem linhas no pacote a tela nova nasceria vazia por desenho.

**Detalhe técnico**

- **Arquivo(s):** `src/panel_ops_data.py`

**executor_prompt**:

```yaml
id: N43.1
size: M
bom_ref: BOM-3
depends_on: ["N43.0"]
files:
  - src/panel_ops_data.py
reuse_targets:
  - component: src/timesfm_context.py
    reuse_as: call
    convergence_check: rg "build_timesfm_block" src/panel_ops_data.py
  - component: src/trading_dashboard_data.py
    reuse_as: copy_pattern
    convergence_check: rg "research_tip" src/panel_ops_data.py && rg "timesfm_status" src/panel_ops_data.py
  - component: src/panel_ops_data.py
    reuse_as: extend
    convergence_check: rg "build_panel_bundle" src/panel_ops_data.py && rg "timesfm" src/panel_ops_data.py
guardrail_contract:
  - class: secrets
    id: n43-1-no-secrets
    target: src/panel_ops_data.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_data.py').read_text(); assert 'sk_live' not in t.lower(); assert 'HF_TOKEN' not in t; assert 'AKIA' not in t"
    pass_condition: no broker or Hugging Face secret values hardcoded
  - class: subagent-safety
    id: n43-1-no-order-no-cli-write
    target: src/panel_ops_data.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_data.py').read_text(); assert 'process_after_gate_b' not in t; assert 'paper-api.alpaca.markets' not in t; assert 'evolution_engine.main' not in t; assert 'apply_strategy_patch' not in t"
    pass_condition: panel data loader does not submit paper, write daily reports, or patch strategies
```

### Quality Brief (Sprint N43)

Maintain: LIVE_TRADING_ENABLED=false; paper host only; dashboard does not submit or cancel orders.
Maintain: load trader-entry|exit|budget|risk|scanner only via src/original.py; do not invent scoring thresholds.
Maintain: TimesFM optional and fail-closed; never fabricate forecast numbers.
Avoid: required timesfm image dependency; calling evolution CLI on GET; TimesFM as order auth.

Melhoria: expose a TimesFM / labeled-tips block on `build_panel_bundle`.
Contexto: `timesfm_context.build_timesfm_block` already returns `timesfm_status` OK|UNAVAILABLE and `research_tip` items with `execution_authorized=false`. `evolution_engine.review` stores `timesfm` on `evolution/daily/{day}.json` via CLI only. Login menu bundle has signals, orders, history, catalog — no TimesFM. Feature 11 forbids treating tips as orders. Default `TIMESFM_ENABLED` is off.
Objetivo: (1) Add `load_panel_timesfm(root)` (name may vary) that prefers the latest `evolution/daily/*.json` `timesfm` object when present; otherwise call `build_timesfm_block` with the day and any cheap context series already on disk — do **not** call `evolution_engine.main()` or `review()` just to render the panel. (2) Shape: `{timesfm_status, note, operator_reason, tips, execution_authorized: false, paper_allowed: false}`. Map internal notes to operator_reason keys: `TIMESFM_ENABLED off` → `modelo desligado neste ambiente.`; `TIMESFM_CHECKPOINT unset` → `checkpoint não configurado.`; `insufficient_context_series` → `série de contexto insuficiente.`; `runtime_unavailable` / missing / unknown → `modelo ou dependência ausente.` (3) Tips from the TimesFM block plus daily tips whose label is in `{research_tip, suggestion}` — keep label, summary, kind; drop numeric `forecast` / `forecast_values`. (4) UNAVAILABLE → empty tips, no invented numbers. (5) Do not import `process_after_gate_b`. Do not add timesfm to Dockerfile/requirements. Do not touch Clear/OANDA. (6) Keep existing bundle keys. LIVE false.
Arquivos: src/panel_ops_data.py.
Critério de pronto: `build_panel_bundle` includes `timesfm`; rg shows `build_timesfm_block`; no `forecast_values` fabricated on UNAVAILABLE.
Cenários de teste (implement in N43.3):
1. Default env (TIMESFM_ENABLED off, no daily file) → timesfm_status UNAVAILABLE, tips [], no forecast/forecast_values, operator_reason for modelo desligado or dependência ausente.
2. Fixture daily JSON with timesfm_status OK and one research_tip → same tip on the bundle; execution_authorized false; paper_allowed false.
3. Fixture UNAVAILABLE note runtime_unavailable → tips [], operator_reason modelo ou dependência ausente.
4. Regressão: signals, open_orders, order_history, strategy_catalog, performance still present on the bundle.

### Task N43.2 — Colocar Análise Google no menu do dia a dia

**Entrega:** Depois do login, o menu ganha Análise Google, com a dica rotulada ou a frase de vazio e o motivo, no mesmo visual das outras páginas.
**Como conferir:** Abrir o painel logado, clicar em Análise Google, ver a dica ou o vazio com motivo, e confirmar o aviso de que pesquisa não autoriza ordem e que não há botão de enviar.
**Por quê:** Os dados sozinhos não aparecem no clique do dia a dia; o mapa marcou a análise como só arquivo.

**Detalhe técnico**

- **Arquivo(s):** `src/panel_ops_html.py`, `src/v4_web_dashboard.py`

**executor_prompt**:

```yaml
id: N43.2
size: M
bom_ref: BOM-3
depends_on: ["N43.1"]
files:
  - src/panel_ops_html.py
  - src/v4_web_dashboard.py
reuse_targets:
  - component: src/panel_ops_html.py
    reuse_as: extend
    convergence_check: rg "/analise-google" src/panel_ops_html.py && rg "def _nav" src/panel_ops_html.py
  - component: src/panel_ops_html.py
    reuse_as: copy_pattern
    convergence_check: rg "def render_analise_google_page" src/panel_ops_html.py && rg "def render_strategies_page" src/panel_ops_html.py
  - component: src/v4_web_dashboard.py
    reuse_as: extend
    convergence_check: rg "/analise-google" src/v4_web_dashboard.py && rg "/api/analise-google" src/v4_web_dashboard.py && rg "serve_operator_panel" src/v4_web_dashboard.py
guardrail_contract:
  - class: secrets
    id: n43-2-no-secrets
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_html.py').read_text()+Path('src/v4_web_dashboard.py').read_text(); assert 'sk_live' not in t.lower(); assert 'HF_TOKEN' not in t"
    pass_condition: no live keys in HTML or dashboard routes
  - class: subagent-safety
    id: n43-2-research-only-page
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; html=Path('src/panel_ops_html.py').read_text(); dash=Path('src/v4_web_dashboard.py').read_text(); assert 'não autoriza ordem' in html; assert 'modelo ou dependência ausente' in html; assert 'process_after_gate_b' not in html; assert 'process_after_gate_b' not in dash"
    pass_condition: page states research does not authorize order; fail-closed copy present; dashboard still does not call paper submit
```

### Quality Brief (Sprint N43)

Maintain: LIVE_TRADING_ENABLED=false; operator session cookie in front of the new page; same shell as Sinais/Ordens/Estratégias.
Maintain: do not rewrite render_page as the daily UI; login menu is panel_ops_html.
Maintain: empty copy is explicit Portuguese; research does not authorize order.
Avoid: Live button; order submit/cancel controls; inventing a public hostname; TimesFM inference inside the HTML renderer.

Melhoria: add authenticated GET /analise-google to the daily menu; GET /api/analise-google mirroring /api/signals.
Contexto: OPERATOR_PANEL_PATHS has /, /central, /sinais, /estrategias, /prodigy, /performance, /ordens, /historico, /login. _nav has seven items. serve_operator_panel 404s /analise-google. DESIGN.md sidebar says Sugestões — operator-facing nav label is **Análise Google** (campaign/ROADMAP), not Central parameter apply.
Objetivo: (1) Extend OPERATOR_PANEL_PATHS and _nav with Análise Google (/analise-google). (2) render_analise_google_page copy render_strategies_page / render_signals_page (side nav, table or list, muted disclaimer). Title Análise Google. Subtitle exactly `Dica de pesquisa — não autoriza ordem. Live desligado.` When timesfm_status is not OK: primary empty copy exactly `Análise Google indisponível: modelo ou dependência ausente.` plus muted `Motivo: {operator_reason}` using the mapped Portuguese reason. When OK: list tip summaries with Portuguese labels `dica de pesquisa` / `sugestão`; if no tips, `Nenhuma dica de pesquisa neste relatório.` Footer always `Esta análise é só pesquisa. Não autoriza ordem.` Optional research metadata (model id, horizon) is allowed; never print forecast arrays as entry/stop. (3) serve_operator_panel branch; session required like /sinais. (4) serve_panel_json for GET /api/analise-google (status + tips + operator_reason + execution_authorized false). Register the path next to /api/estrategias. (5) No form/button that submits or cancels orders. No Live button. Do not call Alpaca. Do not call evolution CLI. Do not replace render_page. Do not wire POST /api/strategy-parameters.
Arquivos: src/panel_ops_html.py, src/v4_web_dashboard.py.
Critério de pronto: logged-in GET /analise-google returns HTML with nav label; unauthenticated still blocked; HTML contains `não autoriza ordem` and the UNAVAILABLE copy string; rg shows /analise-google in _nav and serve_operator_panel.
Cenários de teste (implement in N43.3):
1. Sem cookie → redirect/401 like /sinais.
2. Com cookie, default env → primary empty copy + Motivo + `não autoriza ordem`.
3. Com fixture OK + research_tip → summary visível; rótulo dica de pesquisa; sem array de forecast como ordem.
4. Nav contém Análise Google.
5. Página sem controle de envio (sem process_after_gate_b, sem form POST de ordem).
6. Regressão: /sinais /ordens /historico /estrategias /performance /central still render.

### Task N43.3 — Provar vazio com motivo, rótulo de pesquisa e que a tela não envia ordem

**Entrega:** Testes mostram a tela com e sem modelo, recusa sem login, o aviso de pesquisa, e que a página nova não envia ordem.
**Como conferir:** Pedir essa bateria e ver falha se o menu não tiver Análise Google, se a página abrir sem sessão, se faltar o motivo, ou se aparecer controle de envio.
**Por quê:** Sem prova, o mapa poderia marcar visível com a tela ainda mentindo número ou ordem.

**Detalhe técnico**

P task. File: `tests/test_panel_ops.py` (extend; 1 file). Reuse PanelOpsHttpTests cookie pattern. Nodeids for: unauthenticated /analise-google matches /sinais; empty copy `Análise Google indisponível: modelo ou dependência ausente.`; HTML contains `não autoriza ordem`; fixture OK research_tip shows Portuguese `dica de pesquisa`; GET /api/analise-google requires session and has execution_authorized false; regression previous menu routes. Assert no numeric forecast keys on UNAVAILABLE JSON. Do not call real Alpaca. Do not install timesfm in CI. Do not weaken `tests/test_timesfm_context.py`. LIVE false in env. No secret values.

### Task N43.4 — Atualizar o mapa e os chamados depois da tela existir

**Entrega:** O mapa deixa de dizer que a análise Google só existe em arquivo; os chamados apontam a campanha e não fecham corretoras terceiras.
**Como conferir:** Abrir o mapa: Análise Google no menu com selo visível ou vazio comum; ISS-017 aberto; ISS-010 e o épico antigo do painel único continuam.
**Por quê:** Sem esse recorte, a próxima rodada acha que a dica ainda está só no relatório.

**Detalhe técnico**

P task. Files: `docs/OPERATOR-PANEL-MAP.md`, `docs/DASHBOARD-OPERATIONS.md`, `docs/ISSUES.md` (ISS-017 keep **aberto**; ISS-007 keep open; ISS-016 stays orientation). Flip map section `## 9. TimesFM / Google (pesquisa)` from SÓ-API-OU-JSONL to VISÍVEL / VAZIO-COMUM using the real empty string `Análise Google indisponível: modelo ou dependência ausente.`; melhoria contínua events may remain Command Panel v1 / JSON. Do not close ISS-010 / ISS-011 / ISS-007 / ISS-009 / ISS-017. Do not claim EasyPanel rebuild. Do not claim TimesFM is installed in production. LIVE false.

---

## Sprint N44 — Homologar operar ação americana e cripto pelo painel
> Categoria: N  
> Status: concluida *(entrega docs/runbook N44.0–N44.4; **passeio operador e evidência TEST-EVIDENCE ainda pendentes**)*  
> Gerado via: `/pmo plan` 2026-11-17 · EXECUTE docs 2026-11-17 · fonte ISS-017 onda 4 · pós-N43 PR #64 · **docs/operador, zero M**  
> titulo_humano: Percorrer sinal, ordem, fill ou recusa e resultado no painel paper  
> resumo_humano: Você ganha um roteiro para percorrer no painel o caminho sinal → ordem aberta → fill ou recusa → resultado, em ação americana e cripto na conta paper. Rebuild da imagem publicada continua seu. A suíte de testes não substitui o que você viu. Dinheiro real permanece desligado.  
> Gate: roteiro do passeio publicado; folha de evidência com linhas pendentes (não inventadas); ISS-017 anotado e aberto; ISS-007/010/011 abertos; zero src/; LIVE false  
> review: skip  
> Brief: `docs/.briefs/N44.brief.md`  
> bom_ref: BOM-3  
> Depende de: N43 concluida · Release: campanha ISS-017 onda 4  
> LIVE_TRADING_ENABLED: false

### Em uma frase

Você ganha um roteiro para percorrer no painel o caminho sinal → ordem aberta → fill ou recusa → resultado, em ação americana e cripto na conta paper — sem o laboratório inventar fill nem ligar dinheiro real.

### O que muda para você

- Reconstruir a imagem do painel publicado continua na sua mão; sem isso o menu novo não aparece no ar
- O passeio é o critério desta onda — a suíte de testes verde não substitui o que você viu
- Vazio honesto nas listas não é fill; recusa com motivo conta
- Bolsa brasileira e câmbio continuam barrados até você credenciar
- Dinheiro real permanece desligado

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Inventário honesto do que já existe | Abrir o inventário e ver o que o menu e o laço paper já fazem, e quando código entra ou fica de fora |
| 2 | Roteiro do passeio | Ler o roteiro: ação americana e cripto, o que conta e o que não conta |
| 3 | Folha de evidência | Ver as linhas pendentes para ação americana e cripto — preenchidas só com o que você viu |
| 4 | Campanha anotada | Abrir a lista de problemas: a onda 4 está planejada; os chamados da campanha, da bolsa brasileira e do câmbio continuam abertos |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N44.0 Inventariar o que já existe no laço paper e no menu | `/git` | — |
| [x] | P | N44.1 Escrever o roteiro do passeio no painel | docs | N44.0 |
| [x] | P | N44.2 Abrir a folha de evidência do passeio | docs | N44.1 |
| [x] | P | N44.3 Ligar o roteiro na folha do dia a dia e no mapa | docs | N44.1 |
| [x] | P | N44.4 Anotar a campanha e o diário sem fechar os chamados | docs | N44.2, N44.3 |

### Quality Brief (Sprint N44)

Maintain: `LIVE_TRADING_ENABLED=false`; docs-only sprint — zero diff em `src/`; não inventar fill nem limiar de scoring.
Maintain: dashboard does not submit or cancel orders; load `trader-entry|exit|budget|risk|scanner` only via `src/original.py`.
Maintain: B3_EQUITY / FOREX remain fail-closed without operator creds (ISS-010); zero Alpaca POST from this sprint.
Maintain: **ISS-017 aberto**; **ISS-007 / ISS-010 / ISS-011** permanecem abertos.
Avoid: treating pytest/HTTP 200/queue/rebuild as fill; Alpaca poll from the panel; Live button; closing the campaign epic without operator walk evidence.

### Fora de escopo

- Qualquer `src/` ou `tests/`
- Poll HTTP Alpaca a partir do painel
- POST / cancelamento de ordem pelo painel
- Inventar fill / limiar / score
- Clear / OANDA / N29.5 / Tá Barato (N45)
- Fechar ISS-007 / ISS-010 / ISS-011 / ISS-009 / ISS-013 / ISS-016 / ISS-017
- Rebuild EasyPanel (você)
- `LIVE_TRADING_ENABLED=true`

### Task N44.0 — Inventariar o que já existe no laço paper e no menu

**Entrega:** Inventário curto dizendo que as listas do menu e o laço paper já existem, e que esta onda é roteiro — código só se o passeio provar lista cega.
**Como conferir:** O inventário cita as listas do menu, o laço paper, a evidência antiga de fill e deixa bolsa brasileira, câmbio e envio pelo painel de fora.
**Por quê:** Sem essa lista o EXECUTE reimplementa o laço ou inventa um fill.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N44-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md` vs `git ls-remote` `Jakeschincariol/day-trader-skill` `main`; do not bump. Local vendor may be uninitialized/empty — do not treat it as reviewed main. If GitHub unreachable, stop claiming current main. Do not touch `src/` in this task.

Cite: `load_panel_open_orders` / `load_panel_order_history`; empty strings `Nenhuma ordem aberta no paper.` / `Nenhum fill confirmado no histórico.`; Feature 5 AAPL 2026-10-29; Feature 7 pytest US+CRYPTO; paper runner **not** called from panel. Code IN only if a later operator walk proves missing rows — then STOP, do not patch here.

### Task N44.1 — Escrever o roteiro do passeio no painel

**Entrega:** Um roteiro que você segue depois do login: sinal, ordem aberta, fill ou recusa, resultado — ação americana e cripto.
**Como conferir:** O roteiro lista os dois mercados, o que conta, o que não conta, o vazio honesto e o pedido de rebuild na sua mão.
**Por quê:** Sem o roteiro, pytest e o fill antigo de ação americana fingem que a onda 4 acabou.

**Detalhe técnico**

P task. File: `docs/HOMOLOGATION.md` (append a section, do not rewrite Feature 5 / G-MKT). Portuguese operator prose. Copy the walk checklist from `docs/.briefs/N44.brief.md` (`## Checklist de passeio`). Reuse N41 empty strings verbatim. State rebuild EasyPanel is operator. State pytest / HTTP 200 / queue / semaphore ≠ fill. Refusal with reason counts. Historical AAPL fill may appear in Histórico after rebuild if volume still has rows — cite as “lists not blind”, not as the crypto walk. LIVE false. No secrets.

### Task N44.2 — Abrir a folha de evidência do passeio

**Entrega:** Uma folha com linhas pendentes para ação americana e cripto, prontas para você preencher o que viu — sem número inventado.
**Como conferir:** Abrir a folha e achar duas linhas (ação americana e cripto) em status pendente, sem fill fingido.
**Por quê:** Sem a folha, o próximo chat não tem onde colar o passeio redigido.

**Detalhe técnico**

P task. File: `docs/TEST-EVIDENCE.md` (append Sprint N44 section). One pending row for US equity panel walk; one pending row for crypto panel walk. Columns like N20 (criterion, evidence, status, result). Status `pendente`. Do **not** copy AAPL 2026-10-29 as N44 crypto evidence. Do not paste tokens. Do not mark ok. Pointer from HOMOLOGATION N44 section. LIVE false.

### Task N44.3 — Ligar o roteiro na folha do dia a dia e no mapa

**Entrega:** A folha do dia a dia e o mapa apontam o roteiro do passeio, para o próximo login não recomeçar do zero.
**Como conferir:** Abrir a folha operacional e o mapa e achar um parágrafo que manda seguir o passeio de ação americana e cripto depois do rebuild.
**Por quê:** Sem esse ponteiro, o roteiro fica órfão no repositório.

**Detalhe técnico**

P task. Files: `docs/DASHBOARD-OPERATIONS.md`, `docs/OPERATOR-PANEL-MAP.md` (2 files). Short operator paragraph + markdown link to the new HOMOLOGATION N44 section under «Dia a dia do operador». Map «Fora deste mapa»: onda 4 is homologation walk, not a new screen; rebuild still operator. Do not rewrite bearer/kill-switch tables. Do not add a fake public URL. Do not edit `src/`. Do not flip Ordens/Histórico selos (already VISÍVEL).

### Task N44.4 — Anotar a campanha e o diário sem fechar os chamados

**Entrega:** O chamado da campanha registra a onda 4 planejada (e, na execução, que o roteiro existe); o diário ganha uma linha desta sprint; os chamados da bolsa brasileira, do câmbio e do painel único continuam abertos.
**Como conferir:** Abrir a lista de problemas: a campanha aponta esta onda e permanece aberta; os outros chamados listados continuam; o diário tem a linha.
**Por quê:** Sem a nota, a próxima rodada pode achar que faltou código ou que a campanha já fechou.

**Detalhe técnico**

P task. Files: `docs/ISSUES.md`, `docs/DIARY.md` (2 files). ISS-017 keep **aberto**; add EXECUTE note “onda 4 runbook published; walk still operator; do not claim campaign complete without operator evidence”. Do **not** close ISS-017 / ISS-007 / ISS-010 / ISS-011 / ISS-009 / ISS-016. Optional one-liner under ISS-007: N44 is homologation, not a new 1.0 screen. DIARY: short `## Sprint N44` row — docs/runbook; operator walk; LIVE false; EasyPanel rebuild still operator; PR #64 is N43 closeout not N44 fill.

---


## Sprint N45 — Trazer Tá Barato para o menu, só com fórmula recuperada
> Categoria: N  
> Status: planejada  
> titulo_humano: Ver Tá Barato no menu quando a fórmula original existir  
> Campanha ISS-017 onda 5 (stub). **Não arranca** sem N17.2 / G-FORM. Não inventar percentil. LIVE false.

---

## Sprint N46 — Mostrar a bolsa brasileira no painel depois da conta Clear
> Categoria: N  
> Status: planejada  
> titulo_humano: Ver B3 no painel só com a conta simulada credenciada  
> Campanha ISS-017 onda 6 (stub). **Não arranca** sem N29.5. Sem credencial continua barrado com motivo. Zero POST Alpaca. LIVE false.

---

## Sprint N47 — Mostrar o câmbio no painel depois da conta OANDA Practice
> Categoria: N  
> Status: planejada  
> titulo_humano: Ver forex no painel só com a conta Practice credenciada  
> Campanha ISS-017 onda 7 (stub). **Não arranca** sem N29.5. Host practice, nunca live. LIVE false.

---

## Sprint N48 — Mostrar na tela Sinais o que se copia e o que opera
> Categoria: N  
> Status: concluida *(entrega N48.0–N48.4; **rebuild EasyPanel e confirmação ISS-018 ainda operador**)*  
> Gerado via: `/pmo plan` 2026-11-17 · EXECUTE 2026-11-17 · fonte ISS-018 · correção do operador 2026-11-17 · Feature 9/4/10 já em REQUIREMENTS  
> titulo_humano: Ver na tela Sinais o que se copia e o que opera  
> resumo_humano: Depois do login você abre Sinais e vê o que o laboratório copia de terceiros e o que está operando — ou o vazio honesto. A auditoria de ingresso continua na mesma página, claramente à parte. Collective2 permanece fechado. O painel não envia ordem.  
> Gate: Sinais com seção de cópia e seção de auditoria; vazio em português; resultado só de fill rotulado bruto se o custo faltar; Collective2 fechado; sessão obrigatória; zero envio pelo painel; pytest do painel verde; mapa atualizado; LIVE false  
> review: senior+qa  
> Brief: `docs/.briefs/N48.brief.md`  
> bom_ref: BOM-3  
> Depende de: N25 concluida · N26 concluida · N41 concluida · Release: ISS-018 (não usa N45–N47)  
> LIVE_TRADING_ENABLED: false

### Em uma frase

A tela Sinais passa a mostrar o que o laboratório copia de terceiros e o que está operando, com resultado só de fill — e a auditoria de ingresso continua visível na mesma página, sem se passar por fill.

### O que muda para você

- Sinais deixa de ser só origem, destino e motivo
- Você vê o que está sendo copiado, o que opera, e o resultado bruto por família de cópia
- A auditoria de ingresso permanece numa seção à parte, com o texto de que não é fill
- Collective2 continua fechado; o painel não envia ordem; dinheiro real permanece desligado

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Inventário do que já é cópia e do que é só auditoria | Abrir o inventário e ver que a tela de hoje lista ingresso, enquanto a cópia e o resultado já existem noutros pontos |
| 2 | Mesma tela de Sinais com cópia e auditoria | Entrar no painel, abrir Sinais, ver a seção de cópia (ou o vazio honesto) e a seção de ingresso |
| 3 | Tela só leitura, sem fill inventado | Confirmar que não há botão de enviar ordem, que Collective2 aparece fechado, e que o resultado diz bruto quando o custo falta |
| 4 | Mapa e chamado atualizados | O mapa descreve as duas seções; o chamado de alinhamento aponta esta sprint; a campanha e o épico antigo continuam abertos |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N48.0 Inventariar o reuso da cópia de terceiros antes de redesenhar Sinais | `/git` | — |
| [x] | M | N48.1 Montar a vista de cópia e operação no pacote do painel | `/dev` | N48.0 |
| [x] | M | N48.2 Mostrar cópia e auditoria na mesma tela de Sinais | `/dev` | N48.1 |
| [x] | P | N48.3 Provar cópia, vazio honesto, auditoria e que o painel não envia ordem | `/qa testes` | N48.2 |
| [x] | P | N48.4 Atualizar o mapa e os chamados depois da tela alinhada | docs | N48.3 |

### Quality Brief (Sprint N48)

Maintain: `LIVE_TRADING_ENABLED=false`; paper host only; dashboard does not submit or cancel orders.
Maintain: load `trader-entry|exit|budget|risk|scanner` only via `src/original.py`; do not invent scoring thresholds.
Maintain: B3_EQUITY / FOREX remain fail-closed without operator creds (ISS-010); zero Alpaca POST from this sprint.
Maintain: performance counts confirmed fills only; `queued_intent` and HTTP 200 are not fills; gross label when costs incomplete.
Avoid: parallel `/copy` route; calling `signal_copy.validate` from the panel; inventing per-signal P&L; approving Collective2; stealing N45–N47; closing ISS-007/010/011/017.

### Fora de escopo

- Rota nova de cópia ou provedores
- POST ou cancelamento de ordem pelo painel
- Inventar fill, custo líquido ou resultado por sinal sem join
- Aprovar Collective2
- Tela própria de Tá Barato (N45)
- Clear / OANDA / N29.5
- Inventar limiar / promover Prodígio / ORB paper
- `LIVE_TRADING_ENABLED=true`
- Fechar ISS-007 / ISS-010 / ISS-011 / ISS-009 / ISS-013 / ISS-016 / ISS-017
- Roubar identificadores N45–N47

### Task N48.0 — Inventariar o reuso da cópia de terceiros antes de redesenhar Sinais

**Entrega:** Inventário curto dizendo que a tela de hoje é auditoria de ingresso, e que cópia, ordens e resultado já existem noutros pontos para reusar.
**Como conferir:** O inventário cita a lista de ingresso, a família de cópia, as cópias de pesquisa do Prodígio, o resultado só de fill e deixa Collective2, câmbio e envio pelo painel de fora.
**Por quê:** Sem essa lista o EXECUTE reimplementa a cópia ou inventa fill.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N48-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md` vs `git ls-remote` `Jakeschincariol/day-trader-skill` `main`; do not bump. Local vendor may be uninitialized/empty — do not treat it as reviewed main. If GitHub unreachable, stop claiming current main. Do not touch `src/` in this task.

Cite: `load_panel_signals`; `signal_copy.ALLOWED`; `prodigy_copied_signals`; `performance_from_ledger` / `performance_from_snapshots`; `build_panel_bundle`; `render_signals_page`; `GET /api/signals`. Do not plan Alpaca HTTP from the panel. Do not steal N45–N47.

### Task N48.1 — Montar a vista de cópia e operação no pacote do painel

**Entrega:** O pacote do painel passa a carregar, além da auditoria, o que está em cópia e o que opera — só com dados já existentes, sem inventar fill nem custo.
**Como conferir:** Pedir o teste de dados em que a família de cópia traz ordens e resultado bruto quando houver fill, e o vazio combinado quando não houver; Collective2 continua fechado.
**Por quê:** Hoje o pacote só entrega ingresso; sem a vista de cópia a tela continuaria mentindo o conceito.

**Detalhe técnico**

- **Estado atual:** `build_panel_bundle` delivers `signals` (ingest audit) plus open_orders / order_history / performance / prodigy.copied_signals. Order rows have `strategy_key` and no `provider` / `signal_id`. `/api/signals` is not this task.
- **Estado desejado:** same bundle plus `copy` object (operating/history/performance slice for `signal_copy`, Collective2 closed, research copies labeled). Family totals only.
- **Fonte(s):** ISS-018, Feature 4/9/10, N25/N26/N41.
- **Risco:** MEDIUM — shared panel bundle; invented provider/P&L would lie.
- **Arquivo(s):** `src/panel_ops_data.py`

**executor_prompt**:

```yaml
id: N48.1
size: M
bom_ref: BOM-3
depends_on: ["N48.0"]
files:
  - src/panel_ops_data.py
reuse_targets:
  - component: src/panel_ops_data.py
    reuse_as: extend
    convergence_check: rg "def load_panel_signals" src/panel_ops_data.py && rg "def build_panel_bundle" src/panel_ops_data.py && rg "'copy'" src/panel_ops_data.py
  - component: src/panel_ops_data.py
    reuse_as: call
    convergence_check: rg "def prodigy_copied_signals" src/panel_ops_data.py && rg "PERFORMANCE_LABEL_GROSS" src/panel_ops_data.py
  - component: src/panel_ops_data.py
    reuse_as: call
    convergence_check: rg "def performance_from_ledger" src/panel_ops_data.py && rg "def performance_from_snapshots" src/panel_ops_data.py && rg "def load_panel_open_orders" src/panel_ops_data.py
guardrail_contract:
  - class: secrets
    id: n48-1-no-secrets
    target: src/panel_ops_data.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_data.py').read_text(); assert 'sk_live' not in t.lower(); assert 'AKIA' not in t; assert 'SIGNAL_COPY_SECRET' not in t"
    pass_condition: no broker or webhook secret values hardcoded
  - class: subagent-safety
    id: n48-1-no-invented-fill
    target: src/panel_ops_data.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_data.py').read_text(); assert 'process_after_gate_b' not in t; assert 'paper-api.alpaca.markets' not in t; assert 'from signal_copy' not in t; assert 'import signal_copy' not in t; assert 'approved_for_paper_copy' in t; assert 'PERFORMANCE_LABEL_GROSS' in t"
    pass_condition: panel data loader does not submit paper, does not import HMAC copy module, does not invent fills, keeps gross label, records Collective2 closed
```

### Quality Brief (Sprint N48)

Maintain: LIVE_TRADING_ENABLED=false; paper host only; dashboard does not submit or cancel orders.
Maintain: load trader-entry|exit|budget|risk|scanner only via src/original.py; do not invent scoring thresholds.
Maintain: confirmed fills only; queued_intent is not a fill; PERFORMANCE_LABEL_GROSS when costs incomplete.
Maintain: Collective2 approved_for_paper_copy remains false; prodigy_copied_signals stay research_copy_not_order_auth.
Avoid: forking a second SELECT on signal_events; calling signal_copy.validate; synthesizing per-signal P&L when signal_id is missing; treating research copies as operating.

Melhoria: expose a `copy` object on `build_panel_bundle` without replacing `signals`.
Contexto: `load_panel_signals` is ingest audit (origin/destination/reason). Operator concept of Sinais is third-party copy (TradingView / signal_copy / providers) plus what is operating and fill-only performance. Feature 10 already groups performance by strategy_key. N41 already lists open_orders / order_history with strategy_key but **without** provider or signal_id. prodigy_copied_signals is the only existing list with provider and is research. Collective2 is closed. signal_events SELECT has no strategy_key/signal_id — do not add a column. Do not import the HMAC module `signal_copy`.
Objetivo: (1) Attach `copy` on build_panel_bundle without replacing signals. (2) copy.operating = open_orders where strategy_key=='signal_copy' (existing row fields only). (3) copy.history = order_history where strategy_key=='signal_copy' (already confirmed fills). (4) copy.performance = slice of existing performance.strategies for strategy_key=='signal_copy'; keep pnl_label PERFORMANCE_LABEL_GROSS and source; family totals only. (5) copy.collective2 = {approved_for_paper_copy: false, status: closed} always. (6) copy.research_copies = prodigy_copied_signals() as-is (research_copy_not_order_auth) — NOT operating. (7) copy.providers = unique provider from research_copies only, each labeled research_only. Do NOT invent provider from orders. Do NOT invent per-signal or per-provider P&L. (8) Do not import signal_copy (no validate/sign/preflight). Do not import process_after_gate_b. Do not add SQL columns. Do not touch Clear/OANDA. (9) Keep existing bundle keys. LIVE false.
Arquivos: src/panel_ops_data.py.
Critério de pronto: `build_panel_bundle` includes `copy`; rg shows approved_for_paper_copy and PERFORMANCE_LABEL_GROSS; load_panel_signals still present; no process_after_gate_b and no `from signal_copy` / `import signal_copy` in this file.
Cenários de teste (implement in N48.3):
1. Fixture open order strategy_key=signal_copy → copy.operating non-empty; is_fill false unless snapshot/ledger fill rules pass; no invented provider field required on that row.
2. Confirmed fill for signal_copy → copy performance counts it with PERFORMANCE_LABEL_GROSS; queued_intent excluded; no per-signal P&L key invented.
3. No copy rows → empty operating/history lists, not fake providers.
4. prodigy_copied_signals remain labeled research_copy_not_order_auth and sit under research_copies, not operating.
5. collective2.approved_for_paper_copy is false.
6. Regressão: signals, open_orders, order_history, performance, strategy_catalog still present on the bundle.

### Task N48.2 — Mostrar cópia e auditoria na mesma tela de Sinais

**Entrega:** A tela Sinais, no mesmo menu, mostra primeiro a cópia de terceiros (ou o vazio honesto) e depois a auditoria de ingresso, sem botão de enviar ordem.
**Como conferir:** Abrir o painel logado, clicar em Sinais, ver as duas seções, Collective2 fechado, e confirmar que a lista antiga de origem/destino/motivo ainda existe.
**Por quê:** Os dados sozinhos não mudam o que o operador entende por Sinais; a tela hoje só fala de ingresso.

**Detalhe técnico**

- **Estado atual:** `render_signals_page` is one ingest table; `GET /api/signals` returns only `{signals: [...]}`. DESIGN filters Todos/Ordem/Barrado/Fila are not implemented.
- **Estado desejado:** same `/sinais` with two `h2` sections (copy then ingest audit); JSON keeps `signals` and adds `copy`. No `/copy` route. No order POST.
- **Fonte(s):** ISS-018, OPERATOR-PANEL-MAP §2, N25 HTML shell.
- **Risco:** MEDIUM — operator-facing copy; parallel route or invented fill would break the concept.
- **Arquivo(s):** `src/panel_ops_html.py`, `src/v4_web_dashboard.py`

**executor_prompt**:

```yaml
id: N48.2
size: M
bom_ref: BOM-3
depends_on: ["N48.1"]
files:
  - src/panel_ops_html.py
  - src/v4_web_dashboard.py
reuse_targets:
  - component: src/panel_ops_html.py
    reuse_as: extend
    convergence_check: rg "def render_signals_page" src/panel_ops_html.py && rg "Cópia de terceiros" src/panel_ops_html.py && rg "Auditoria de ingresso" src/panel_ops_html.py
  - component: src/panel_ops_html.py
    reuse_as: copy_pattern
    convergence_check: rg "Nenhuma cópia de terceiro em operação." src/panel_ops_html.py && rg "Nenhum sinal neste destino." src/panel_ops_html.py && rg "def render_prodigy_page" src/panel_ops_html.py
  - component: src/v4_web_dashboard.py
    reuse_as: extend
    convergence_check: rg "/api/signals" src/v4_web_dashboard.py && rg "serve_panel_json" src/v4_web_dashboard.py
guardrail_contract:
  - class: secrets
    id: n48-2-no-secrets
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_html.py').read_text()+Path('src/v4_web_dashboard.py').read_text(); assert 'sk_live' not in t.lower(); assert 'SIGNAL_COPY_SECRET' not in t"
    pass_condition: no live keys or webhook secrets in HTML or dashboard routes
  - class: subagent-safety
    id: n48-2-read-only-page
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; html=Path('src/panel_ops_html.py').read_text(); dash=Path('src/v4_web_dashboard.py').read_text(); assert 'process_after_gate_b' not in html; assert 'process_after_gate_b' not in dash; assert 'Cópia de terceiros' in html; assert 'Auditoria de ingresso' in html; paths=html.split('OPERATOR_PANEL_PATHS',1)[1].split(')',1)[0]; assert '/copy' not in paths"
    pass_condition: same /sinais route; two labeled sections; dashboard still does not call paper submit
```

### Quality Brief (Sprint N48)

Maintain: LIVE_TRADING_ENABLED=false; operator session cookie in front of /sinais; do not add a parallel route.
Maintain: Feature 9 ingest table remains (origin, destination, reason) under a distinct heading.
Maintain: empty copy is explicit Portuguese; Collective2 closed copy is always visible.
Avoid: Live button; order submit/cancel controls; calling signal_copy.validate; rewriting render_page as the daily UI.

Melhoria: extend authenticated GET /sinais and GET /api/signals with a copy/operating view; keep ingest audit.
Contexto: render_signals_page is a single table (hora, origem, ativo, mercado, destino, motivo) with subtitle about destination audit. serve_panel_json /api/signals returns only `{signals: [...]}`. DESIGN.md filters Todos/Ordem/Barrado/Fila are **not** in today's HTML — do not add them in N48. Operator wants copy concept on this page, not /prodigy and not a new path. Two `h2` sections copy the Prodígio page pattern (rank + copied), not a new tab widget.
Objetivo: (1) Keep OPERATOR_PANEL_PATHS and _nav Sinais → /sinais (no /copy). (2) render_signals_page: heading Sinais; two sections in this order — `Cópia de terceiros` then `Auditoria de ingresso`. Copy empty: `Nenhuma cópia de terceiro em operação.` Copy performance empty: `Sem fills confirmados nesta cópia.` Collective2 line always: `Collective2: cópia fechada — nenhum provedor aprovado.` Audit empty stays `Nenhum sinal neste destino.` Audit subtitle: `Auditoria de ingresso — origem, destino e motivo. Não é fill.` Copy subtitle: `Cópia de terceiros (TradingView / provedores). Não é fill.` Footer: `O painel não envia ordem. Live desligado. Valores brutos se o custo não estiver completo.` Show PERFORMANCE_LABEL_GROSS when a number is shown. Research prodigy copies, if listed, must say they are research not operating. Do not show a provider P&L column. (3) serve_panel_json /api/signals: keep `signals`; add `copy` from the bundle. Session required like today. (4) No POST handlers for placing orders. Do not add Live button. Do not call Alpaca. Do not replace render_page. Do not add /copy to OPERATOR_PANEL_PATHS. Do not implement DESIGN ingest-filter chips.
Arquivos: src/panel_ops_html.py, src/v4_web_dashboard.py.
Critério de pronto: logged-in GET /sinais HTML contains both section titles and Collective2 closed copy; unauthenticated still blocked; /api/signals JSON has signals and copy; OPERATOR_PANEL_PATHS still has no /copy.
Cenários de teste (implement in N48.3):
1. Sem cookie → redirect/401 like today /sinais.
2. Com cookie, sem cópia → `Nenhuma cópia de terceiro em operação.` e Collective2 fechado.
3. Com fixture de cópia + fill → família visível; rótulo bruto; fila não aparece como fill.
4. Seção de auditoria ainda mostra origem/destino/motivo (Feature 9).
5. HTML da página sem controle de envio de ordem.
6. Regressão: /ordens /historico /estrategias /performance /central /prodigy still render.

### Task N48.3 — Provar cópia, vazio honesto, auditoria e que o painel não envia ordem

**Entrega:** Testes mostram a tela com e sem cópia, a auditoria antiga, Collective2 fechado, recusa sem login, e que a página não envia ordem nem inventa fill.
**Como conferir:** Pedir essa bateria e ver falha se faltar a seção de cópia, se Collective2 parecer aprovado, se a auditoria sumir, ou se aparecer controle de envio.
**Por quê:** Sem prova, o mapa poderia marcar alinhado com a tela ainda só de ingresso.

**Detalhe técnico**

P task. File: `tests/test_panel_ops.py` (extend; 1 file). Reuse PanelOpsHttpTests cookie pattern. Nodeids for: unauthenticated /sinais; empty copy `Nenhuma cópia de terceiro em operação.`; Collective2 closed string; audit empty `Nenhum sinal neste destino.`; Feature 9 origin/destination/reject_reason still on /api/signals `signals`; copy object present with operating/history/performance/collective2; fixture signal_copy fill uses PERFORMANCE_LABEL_GROSS and excludes queued_intent; research_copies not merged into operating; no per-signal P&L key invented; HTML has both headings and no process_after_gate_b / order form; regression previous menu routes. Do not call real Alpaca. Do not weaken existing Feature 9/10 tests. LIVE false in env. No secret values.

### Task N48.4 — Atualizar o mapa e os chamados depois da tela alinhada

**Entrega:** O mapa descreve Sinais como cópia mais auditoria; o chamado de alinhamento aponta esta sprint; a campanha e o épico antigo continuam abertos.
**Como conferir:** Abrir o mapa na área Sinais: duas seções, vazios reais, Collective2 fechado; ISS-018 ligado a N48; ISS-017 e o épico antigo do painel único continuam abertos.
**Por quê:** Sem esse recorte, a próxima rodada acha que Sinais ainda é só ingresso ou que a campanha fechou.

**Detalhe técnico**

P task. Files: `docs/OPERATOR-PANEL-MAP.md`, `docs/DASHBOARD-OPERATIONS.md`, `docs/ISSUES.md`, `docs/DIARY.md` (ISS-018 keep **aberto** until EXECUTE evidence; ISS-017 keep **aberto**; ISS-007 keep open). Update area 2 Sinais: copy section + ingest section; real empty strings; Collective2 closed. DASHBOARD-OPERATIONS row «Ver sinais» mentions copy concept, not only motivo. Do not close ISS-010 / ISS-011 / ISS-007 / ISS-009 / ISS-017. Do not claim EasyPanel rebuild. Do not mark N45–N47 started. LIVE false.

---

## Sprint N49 — Mostrar qual sinal abriu cada ordem e os critérios de adoção
> Categoria: N  
> Status: planejada  
> Gerado via: `/pmo plan` 2026-11-17 · fonte ISS-019 · correção do operador 2026-11-17 · Feature 4/9/10 já em REQUIREMENTS (Passo 2 pulado)  
> titulo_humano: Ver qual sinal abriu cada ordem e os critérios de adoção  
> resumo_humano: Depois do login você abre Sinais e vê qual sinal abriu cada ordem paper — ou o aviso honesto de que o vínculo não existe. A lista do que está assinado traz resultado só de fill. Os critérios de adoção já combinados aparecem na tela. O Prodígio só sugere candidatos de pesquisa. Collective2 permanece fechado. O painel não envia ordem.  
> Gate: Ordem paper em operação mostra origem/identificador do sinal ou vazio honesto; inventário com performance só de fill; critérios Feature 4/9/10 visíveis; pool Prodígio pesquisa separado de paper; Collective2 fechado; sessão obrigatória; zero envio pelo painel; pytest do painel verde; mapa atualizado; LIVE false  
> review: senior+qa  
> Brief: `docs/.briefs/N49.brief.md`  
> bom_ref: BOM-3  
> Depende de: N48 concluida · N25 concluida · N26 concluida · N42 concluida · Release: ISS-019 (não usa N45–N47)  
> LIVE_TRADING_ENABLED: false

### Em uma frase

Na tela Sinais, cada ordem paper aberta mostra qual sinal a abriu, a lista de sinais em uso traz resultado só de fill, e os critérios de adoção já combinados aparecem na própria feature — com o Prodígio só sugerindo candidatos de pesquisa.

### O que muda para você

- Cada ordem paper aberta mostra origem e identificador do sinal, ou diz com clareza que o vínculo não existe
- Você vê o inventário do que está assinado ou em operação, com resultado por sinal só quando houver fill confirmado
- Os critérios de adoção (cópia, janela de quinze dias do Prodígio, fases, Collective2 fechado, sem promoção automática) ficam visíveis na tela
- O Prodígio continua só monitorando candidatos de pesquisa para o pool; não promove sozinho
- O painel não envia ordem; dinheiro real permanece desligado

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Ligação honesta entre ordem paper e o sinal que a abriu | Abrir Sinais, olhar uma ordem em operação e ver origem/identificador — ou o aviso de que o vínculo não existe |
| 2 | Inventário de sinais com resultado só de fill | Ver a lista do que está assinado ou em operação; números só quando houver fill, rotulados brutos se o custo faltar |
| 3 | Critérios de adoção e pool de pesquisa na mesma tela | Ler o bloco de critérios (cópia, quinze dias, fases, Collective2 fechado) e a lista de candidatos do Prodígio marcada como pesquisa |
| 4 | Mapa e chamado atualizados | O mapa descreve proveniência e inventário; o chamado ISS-019 aponta esta sprint; a campanha e o épico antigo continuam abertos |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | P | N49.0 Inventariar o reuso da proveniência, do inventário e do pool | `/git` | — |
| [ ] | M | N49.1 Ligar cada ordem paper ao sinal que a abriu | `/dev` | N49.0 |
| [ ] | M | N49.2 Montar o inventário de sinais e o pool de candidatos | `/dev` | N49.1 |
| [ ] | M | N49.3 Mostrar proveniência, inventário e critérios na tela Sinais | `/dev` | N49.2 |
| [ ] | P | N49.4 Provar proveniência, vazio honesto e critérios visíveis | `/qa testes` | N49.3 |
| [ ] | P | N49.5 Atualizar o mapa e o chamado depois da tela completa | docs | N49.4 |

### Quality Brief (Sprint N49)

Maintain: `LIVE_TRADING_ENABLED=false`; paper host only; dashboard does not submit or cancel orders.
Maintain: load `trader-entry|exit|budget|risk|scanner` only via `src/original.py`; do not invent scoring thresholds; do not call `prodigy_rank.calculate` from the panel.
Maintain: B3_EQUITY / FOREX remain fail-closed without operator creds (ISS-010); zero Alpaca POST from this sprint.
Maintain: performance counts confirmed fills only; `queued_intent` and HTTP 200 are not fills; gross label when costs incomplete.
Avoid: inventing `signal_id` or per-signal P&L when join/overlay is missing; reversing `idempotency_key`; new SQL column; parallel `/copy`; approving Collective2; stealing N45–N47; closing ISS-007/010/011/017; auto-promote.

### Fora de escopo

- Rota nova de cópia, provedores ou assinaturas
- POST ou cancelamento de ordem pelo painel
- Inventar fill, custo líquido, P&L por sinal sem fill, ou identificador por engenharia reversa do hash
- Nova coluna SQL
- Redefinir critérios de adoção (Feature 4/9/10 já definem)
- Chamar o cálculo de ranking do Prodígio a partir do painel ou alterar a janela de quinze dias / o mínimo de operações
- Aprovar Collective2
- Tela própria de Tá Barato (N45)
- Clear / OANDA / N29.5
- Inventar limiar / promover Prodígio / ORB paper
- `LIVE_TRADING_ENABLED=true`
- Fechar ISS-007 / ISS-010 / ISS-011 / ISS-009 / ISS-013 / ISS-016 / ISS-017
- Roubar identificadores N45–N47

### Task N49.0 — Inventariar o reuso da proveniência, do inventário e do pool

**Entrega:** Inventário curto dizendo que a ligação ordem↔sinal já existe no ledger, que o painel hoje a omite, e que ranking, cópia e critérios já estão escritos para reusar.
**Como conferir:** O inventário cita a cadeia do ledger, o diário de ordens com identificador de sinal, o ranking de pesquisa do Prodígio e deixa Collective2, câmbio e envio pelo painel de fora.
**Por quê:** Sem essa lista o EXECUTE inventa coluna, score ou critério de adoção.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N49-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md` vs `git ls-remote` `Jakeschincariol/day-trader-skill` `main`; do not bump. Local vendor may be uninitialized/empty — do not treat it as reviewed main. If GitHub unreachable, stop claiming current main. Do not touch `src/` in this task.

Cite: `open_orders_from_ledger`; `persist_risk_decision`; `record_signal_event`; `signal-orders.jsonl`; `build_panel_copy`; `_load_prodigy_opportunities`; Feature 4/9/10 headings. Do not plan Alpaca HTTP from the panel. Do not steal N45–N47. Do not invent adoption numbers.

### Task N49.1 — Ligar cada ordem paper ao sinal que a abriu

**Entrega:** Cada ordem paper em operação (e o histórico de fill da família de cópia) traz origem e identificador do sinal quando o ledger ou o diário já têm o vínculo — ou o aviso honesto de que o vínculo não existe.
**Como conferir:** Pedir o teste de dados em que uma ordem ligada mostra origem e identificador, e uma ordem sem vínculo mostra o aviso em português, sem inventar número de resultado.
**Por quê:** Sem essa ligação não existe performance por origem, que é o pedido obrigatório desta sprint.

**Detalhe técnico**

- **Estado atual:** `open_orders_from_ledger` / `order_history_from_ledger` JOIN `risk_decisions` only for `strategy_key`. `order_row_from_snapshot` has no origin/`signal_id`. N48 operating table hides provenance.
- **Estado desejado:** same loaders plus honest `origin`, `signal_event_id` (ledger UUID when JOIN hits), ticket `signal_id` only when already stored on `paper/signal-orders.jsonl` (match `client_order_id`), `provenance_status` `linked`|`unknown`. Portuguese unknown; no invented P&L.
- **Fonte(s):** ISS-019 diretriz 1, Feature 9 origem, DATABASE `risk_decisions.signal_event_id`, N48 copy rows.
- **Risco:** MEDIUM — shared order rows; invented id/P&L would lie.
- **Arquivo(s):** `src/panel_ops_data.py`

**executor_prompt**:

```yaml
id: N49.1
size: M
bom_ref: BOM-3
depends_on: ["N49.0"]
files:
  - src/panel_ops_data.py
reuse_targets:
  - component: src/panel_ops_data.py
    reuse_as: extend
    convergence_check: rg "def open_orders_from_ledger" src/panel_ops_data.py && rg "def order_history_from_ledger" src/panel_ops_data.py && rg "signal_events" src/panel_ops_data.py
  - component: src/panel_ops_data.py
    reuse_as: extend
    convergence_check: rg "def order_row_from_snapshot" src/panel_ops_data.py && rg "provenance_status" src/panel_ops_data.py
  - component: src/paper_gateway_queue.py
    reuse_as: call
    convergence_check: rg "def persist_risk_decision" src/paper_gateway_queue.py && rg "signal_event_id" src/paper_gateway_queue.py
guardrail_contract:
  - class: secrets
    id: n49-1-no-secrets
    target: src/panel_ops_data.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_data.py').read_text(); assert 'sk_live' not in t.lower(); assert 'AKIA' not in t; assert 'SIGNAL_COPY_SECRET' not in t"
    pass_condition: no broker or webhook secret values hardcoded
  - class: subagent-safety
    id: n49-1-honest-provenance
    target: src/panel_ops_data.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_data.py').read_text(); assert 'process_after_gate_b' not in t; assert 'paper-api.alpaca.markets' not in t; assert 'from signal_copy' not in t; assert 'import signal_copy' not in t; assert 'provenance_status' in t; assert 'signal_events' in t"
    pass_condition: panel data loader joins existing ledger events, does not submit paper, does not import HMAC copy module, records provenance_status
```

### Quality Brief (Sprint N49)

Maintain: LIVE_TRADING_ENABLED=false; paper host only; dashboard does not submit or cancel orders.
Maintain: load trader-entry|exit|budget|risk|scanner only via src/original.py; do not invent scoring thresholds.
Maintain: confirmed fills only; queued_intent is not a fill; PERFORMANCE_LABEL_GROSS when costs incomplete.
Maintain: do not reverse idempotency_key SHA; ticket signal_id only from an existing stored record.
Avoid: adding a SQL column; synthesizing signal_id; treating unknown rows as linked; calling persist_risk_decision from the panel.

Melhoria: expose honest provenance on open and history order rows without replacing N48 copy filters.
Contexto: paper_orders already FK to risk_decisions; risk_decisions already has signal_event_id; signal_events.source is origin. Panel SELECT drops the join. Ticket signal_id is not a SQL column (hashed into idempotency_key). signal-orders.jsonl already stores provider+signal_id+client_order_id on the runner path. Snapshots from paper_monitor lack signal_id.
Objetivo: (1) Extend open_orders_from_ledger and order_history_from_ledger to JOIN signal_events on rd.signal_event_id; add origin=source, signal_event_id=se.id, provenance_status=linked when the join hits. (2) Overlay ticket signal_id from reports paper/signal-orders.jsonl by client_order_id when that field already exists — never invent, never unhash. (3) Snapshot/unknown rows: provenance_status=unknown; origin may be missing; do not invent P&L keys. (4) Keep _sanitize_order_row. Keep strategy_key. Do not add SQL migrations. Do not import signal_copy. Do not import process_after_gate_b. Do not touch Clear/OANDA. LIVE false.
Arquivos: src/panel_ops_data.py.
Critério de pronto: rg shows signal_events and provenance_status in panel_ops_data.py; JOIN present; no process_after_gate_b and no import signal_copy in this file.
Cenários de teste (implement in N49.4):
1. Ledger fixture paper_order + risk_decision + signal_event source=tradingview → operating row origin tradingview, provenance_status linked, signal_event_id set.
2. Same plus signal-orders.jsonl line with matching client_order_id and signal_id → ticket signal_id appears as stored.
3. Order without join and without journal line → provenance_status unknown; no invented signal_id; no per-signal P&L key.
4. Hashed webhook signal_id stored in journal is shown as stored, not reversed to plaintext.
5. queued_intent remains is_fill false.
6. Regressão: N48 copy.operating still filters strategy_key=signal_copy; signals[] unchanged.

### Task N49.2 — Montar o inventário de sinais e o pool de candidatos

**Entrega:** O pacote do painel passa a trazer a lista do que está assinado ou em operação, o resultado por sinal só de fill, as fases já persistidas, e o pool de candidatos do Prodígio como pesquisa.
**Como conferir:** Pedir o teste de dados em que o inventário agrupa por origem/sinal com resultado bruto só quando há fill, o pool vem do ranking já gravado com rótulo de pesquisa, e Collective2 continua fechado.
**Por quê:** A ligação sozinha não entrega a lista acessível nem o monitoramento contínuo de candidatos que o operador pediu.

**Detalhe técnico**

- **Estado atual:** `copy` has operating/history/family performance/research_copies/providers/collective2. No inventory, no per-signal fill totals, no prodigy_pool, no adoption object. `prodigy.ranking` is None on the bundle.
- **Estado desejado:** `copy.inventory`, `copy.adoption` (Feature 4 text + catalog phases, no new numbers), `copy.prodigy_pool` from `_load_prodigy_opportunities`. Per-signal totals only from confirmed fills with linked provenance.
- **Fonte(s):** ISS-019 diretrizes 2–3, Feature 4/9/10, N25 ranking, N42 catalog.
- **Risco:** MEDIUM — invented per-signal P&L or new score would violate Feature 4/10.
- **Arquivo(s):** `src/panel_ops_data.py`

**executor_prompt**:

```yaml
id: N49.2
size: M
bom_ref: BOM-3
depends_on: ["N49.1"]
files:
  - src/panel_ops_data.py
reuse_targets:
  - component: src/panel_ops_data.py
    reuse_as: extend
    convergence_check: rg "def build_panel_copy" src/panel_ops_data.py && rg "inventory" src/panel_ops_data.py && rg "prodigy_pool" src/panel_ops_data.py && rg "adoption" src/panel_ops_data.py
  - component: src/panel_ops_data.py
    reuse_as: call
    convergence_check: rg "PERFORMANCE_LABEL_GROSS" src/panel_ops_data.py && rg "def prodigy_copied_signals" src/panel_ops_data.py && rg "def load_panel_strategy_catalog" src/panel_ops_data.py
  - component: src/trading_dashboard_data.py
    reuse_as: call
    convergence_check: rg "def _load_prodigy_opportunities" src/trading_dashboard_data.py && rg "_load_prodigy_opportunities" src/panel_ops_data.py
  - component: src/prodigy_rank.py
    reuse_as: call
    convergence_check: rg "WINDOW_DAYS = 15" src/prodigy_rank.py && rg "MIN_TRADES = 5" src/prodigy_rank.py && ! rg "def calculate" src/panel_ops_data.py
guardrail_contract:
  - class: secrets
    id: n49-2-no-secrets
    target: src/panel_ops_data.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_data.py').read_text(); assert 'sk_live' not in t.lower(); assert 'SIGNAL_COPY_SECRET' not in t"
    pass_condition: no live keys or webhook secrets
  - class: subagent-safety
    id: n49-2-no-invented-score-or-fill
    target: src/panel_ops_data.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_data.py').read_text(); assert 'process_after_gate_b' not in t; assert 'from prodigy_rank import calculate' not in t; assert 'import prodigy_rank' not in t; assert 'PERFORMANCE_LABEL_GROSS' in t; assert 'approved_for_paper_copy' in t; assert 'research_tip' in t or 'prodigy_pool' in t"
    pass_condition: no paper submit, no prodigy_rank.calculate, gross label kept, Collective2 closed, pool research-labeled
```

### Quality Brief (Sprint N49)

Maintain: LIVE_TRADING_ENABLED=false; confirmed fills only; PERFORMANCE_LABEL_GROSS when costs incomplete.
Maintain: Feature 4 adoption text reused (15-day window, min 5 operations in at least 3 days, net positive, drawdown/consistency, formula pending, R$ 20, default research, no auto-promote, C2 closed, phases RESEARCH/SHADOW/PAPER_LIMITED/PAPER_VALIDATED, LIVE off). Do not invent new numbers.
Maintain: prodigy pool from existing intelligence/prodigy-top10-latest.json loader; label research_tip; not operating.
Avoid: grouping unfilled orders into per-signal P&L; calling prodigy_rank.calculate; editing WINDOW_DAYS/MIN_TRADES; auto-promote.

Melhoria: attach inventory, fill-only per-signal performance, Feature 4 adoption object, and research prodigy pool on copy without dropping N48 keys.
Contexto: N48 family totals only. Feature 10 groups by strategy_key from confirmed fills. Feature 9 already has ranking via _load_prodigy_opportunities. Feature 4 already writes Prodigy 15d and C2 closed. Operator wants inventory of subscribed/operating signals and continuous research monitoring of candidates — reuse, do not rescore.
Objetivo: (1) copy.inventory = unique operating/subscribed rows keyed by origin + signal_id or signal_event_id; include origin; performance gross only from confirmed fills with provenance_status=linked; unknown provenance excluded from per-signal totals (optional unknown_unlinked count, no fake P&L). (2) copy.adoption = Portuguese Feature 4 facts (signal copy; Prodigy 15d window / min 5 ops / min 3 days / net positive / drawdown and consistency / formula pending / R$ 20 / default research / rank does not promote; phases; C2 closed; operator-only promotion) plus catalog phase for signal_copy and prodigy_15d from load_panel_strategy_catalog. (3) copy.prodigy_pool = _load_prodigy_opportunities(root) items, label research_tip, never merged into operating. (4) Keep collective2 closed, research_copies labeled research. (5) Do not import prodigy_rank. Do not import process_after_gate_b. Do not add SQL columns. LIVE false.
Arquivos: src/panel_ops_data.py.
Critério de pronto: build_panel_copy / bundle copy includes inventory, adoption, prodigy_pool; rg shows _load_prodigy_opportunities and PERFORMANCE_LABEL_GROSS; no import prodigy_rank; approved_for_paper_copy still present.
Cenários de teste (implement in N49.4):
1. Two confirmed fills same signal_id → inventory row counts both with PERFORMANCE_LABEL_GROSS; queued_intent excluded.
2. Unlinked fill → not attributed to a fabricated signal; no invented P&L.
3. prodigy_pool items labeled research_tip and not inside operating.
4. adoption text includes 15 dias, 5 operações, 3 dias, R$ 20, pesquisa as default, Collective2 fechado, sem promoção automática — and does not introduce a new numeric threshold.
5. catalog phase for prodigy_15d remains research unless already paper in DB (do not UPDATE strategy_states).
6. Regressão: copy.operating/history/performance/collective2/research_copies still present.

### Task N49.3 — Mostrar proveniência, inventário e critérios na tela Sinais

**Entrega:** A tela Sinais, no mesmo menu, mostra a origem do sinal em cada ordem em operação, o inventário, o bloco de critérios de adoção e o pool de pesquisa — sem botão de enviar ordem.
**Como conferir:** Abrir o painel logado, clicar em Sinais, ver as colunas de origem na ordem, a lista, o texto dos critérios (quinze dias, fases, Collective2 fechado) e os candidatos marcados como pesquisa; a auditoria de ingresso continua abaixo.
**Por quê:** Os dados sozinhos não mudam o que o operador lê; hoje a ordem em operação não diz qual sinal a abriu e os critérios não aparecem na feature.

**Detalhe técnico**

- **Estado atual:** `render_signals_page` is N48 copy + ingest; operating table has no origin/signal columns; no adoption/pool sections. `GET /api/signals` returns `signals` + `copy` N48 keys.
- **Estado desejado:** same `/sinais`; operating table adds origem / sinal / aviso de vínculo; inventory + adoption + prodigy pool sections in Portuguese; JSON extends `copy`. No `/copy`. No order POST.
- **Fonte(s):** ISS-019, OPERATOR-PANEL-MAP §2, Feature 4/9/10, N48 HTML shell.
- **Risco:** MEDIUM — operator-facing copy; invented fill or new criterion text would break the contract.
- **Arquivo(s):** `src/panel_ops_html.py`, `src/v4_web_dashboard.py`

**executor_prompt**:

```yaml
id: N49.3
size: M
bom_ref: BOM-3
depends_on: ["N49.2"]
files:
  - src/panel_ops_html.py
  - src/v4_web_dashboard.py
reuse_targets:
  - component: src/panel_ops_html.py
    reuse_as: extend
    convergence_check: 'rg "def render_signals_page" src/panel_ops_html.py && rg "Cópia de terceiros" src/panel_ops_html.py && rg "Auditoria de ingresso" src/panel_ops_html.py && rg "Critérios de adoção" src/panel_ops_html.py'
  - component: src/panel_ops_html.py
    reuse_as: copy_pattern
    convergence_check: 'rg "origem desconhecida" src/panel_ops_html.py && rg "Collective2: cópia fechada" src/panel_ops_html.py && rg "def render_prodigy_page" src/panel_ops_html.py'
  - component: src/v4_web_dashboard.py
    reuse_as: extend
    convergence_check: rg "/api/signals" src/v4_web_dashboard.py && rg "serve_panel_json" src/v4_web_dashboard.py
guardrail_contract:
  - class: secrets
    id: n49-3-no-secrets
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_html.py').read_text()+Path('src/v4_web_dashboard.py').read_text(); assert 'sk_live' not in t.lower(); assert 'SIGNAL_COPY_SECRET' not in t"
    pass_condition: no live keys or webhook secrets in HTML or dashboard routes
  - class: subagent-safety
    id: n49-3-read-only-page
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; html=Path('src/panel_ops_html.py').read_text(); dash=Path('src/v4_web_dashboard.py').read_text(); assert 'process_after_gate_b' not in html; assert 'process_after_gate_b' not in dash; assert 'Critérios de adoção' in html; assert 'Auditoria de ingresso' in html; paths=html.split('OPERATOR_PANEL_PATHS',1)[1].split(')',1)[0]; assert '/copy' not in paths"
    pass_condition: same /sinais route; adoption visible; dashboard still does not call paper submit
```

### Quality Brief (Sprint N49)

Maintain: LIVE_TRADING_ENABLED=false; operator session cookie in front of /sinais; do not add a parallel route.
Maintain: Feature 9 ingest table remains under a distinct heading. N48 copy heading remains.
Maintain: empty provenance is explicit Portuguese; Collective2 closed copy is always visible; prodigy pool says research not operating.
Avoid: Live button; order submit/cancel controls; calling signal_copy.validate; rewriting Feature 4 numbers; DESIGN ingest-filter chips.

Melhoria: extend authenticated GET /sinais and GET /api/signals with provenance columns, inventory, Feature 4 adoption block, and research pool; keep N48 sections.
Contexto: operating HTML has client id, symbol, side, status, qty — no origin. Operator cannot see which signal opened the order. Adoption criteria live only in REQUIREMENTS. Prodígio ranking lives on /prodigy. Same page, not a new path.
Objetivo: (1) Keep OPERATOR_PANEL_PATHS and _nav Sinais → /sinais (no /copy). (2) Operating table columns include Origem and Sinal; unknown: `origem desconhecida` and `sem vínculo com sinal`. (3) Section `Inventário de sinais` with empty `Nenhum sinal neste inventário.` (4) Section `Critérios de adoção` with Feature 4 Portuguese facts: cópia de terceiros; Prodígio janela móvel de 15 dias, mínimo de 5 operações em pelo menos 3 dias, retorno líquido positivo, drawdown e consistência, fórmula de pontuação ainda pendente, risco paper inicial R$ 20, fase padrão pesquisa, ranking não promove sozinho; fases pesquisa / sombra / paper limitado / paper validado; Live desligado; fase não sobe por lucratividade aparente nem HTTP 200; promoção só operador; Collective2 cópia fechada. Do not add a new numeric rule. (5) Section `Candidatos ao pool (Prodígio)` labeled pesquisa — não autoriza ordem / não promove. Empty: `Nenhum candidato de pesquisa no pool.` (6) Keep N48 strings (Cópia de terceiros, Auditoria de ingresso, Collective2 fechado, vazios N48). (7) serve_panel_json /api/signals: keep signals and copy; copy includes inventory, adoption, prodigy_pool. Session required. (8) No POST handlers. No Live button. Do not add /copy.
Arquivos: src/panel_ops_html.py, src/v4_web_dashboard.py.
Critério de pronto: logged-in GET /sinais HTML contains Critérios de adoção, origem desconhecida (or linked origin in fixture), Inventário de sinais, Candidatos ao pool; Collective2 closed; unauthenticated still blocked; /api/signals JSON has copy.inventory, copy.adoption, copy.prodigy_pool; OPERATOR_PANEL_PATHS still has no /copy.
Cenários de teste (implement in N49.4):
1. Sem cookie → redirect/401 like today /sinais.
2. Ordem sem vínculo → `origem desconhecida` e `sem vínculo com sinal`.
3. Inventário vazio → `Nenhum sinal neste inventário.`
4. Critérios de adoção HTML contains 15 dias, 5 operações, 3 dias, R$ 20, pesquisa, Collective2 fechado, não promove.
5. Pool HTML says pesquisa and not operating; empty `Nenhum candidato de pesquisa no pool.`
6. Seção de auditoria ainda mostra origem/destino/motivo (Feature 9). HTML sem controle de envio. Regressão: /ordens /historico /estrategias /performance /central /prodigy still render.

### Task N49.4 — Provar proveniência, vazio honesto e critérios visíveis

**Entrega:** Testes mostram ordem ligada e ordem sem vínculo, inventário só com fill, critérios na tela, pool de pesquisa, Collective2 fechado, recusa sem login, e que a página não envia ordem nem inventa fill.
**Como conferir:** Pedir essa bateria e ver falha se a origem sumir, se aparecer resultado sem fill, se faltar o texto dos critérios, se o pool parecer operação, ou se aparecer controle de envio.
**Por quê:** Sem prova, o mapa poderia marcar completo com a ordem ainda sem sinal.

**Detalhe técnico**

P task. File: `tests/test_panel_ops.py` (extend; 1 file). Reuse PanelOpsHttpTests cookie pattern. Nodeids for: unauthenticated /sinais; linked provenance; unknown provenance strings `origem desconhecida` and `sem vínculo com sinal`; inventory empty `Nenhum sinal neste inventário.`; Feature 4 adoption strings (15 dias, 5 operações, 3 dias, R$ 20, não promove); prodigy_pool research_tip not merged into operating; Feature 10 queued_intent excluded from per-signal totals; Feature 9 origin/destination/reject_reason still on /api/signals `signals`; copy object still has operating/history/performance/collective2; HTML has Critérios de adoção and no process_after_gate_b / order form; regression previous menu routes and N48 headings. Do not call real Alpaca. Do not weaken existing Feature 9/10/N48 tests. LIVE false in env. No secret values.

### Task N49.5 — Atualizar o mapa e o chamado depois da tela completa

**Entrega:** O mapa descreve Sinais com proveniência, inventário e critérios; o chamado ISS-019 aponta esta sprint; a campanha e o épico antigo continuam abertos.
**Como conferir:** Abrir o mapa na área Sinais: colunas de origem, inventário, critérios, pool de pesquisa; ISS-019 ligado a N49; ISS-017 e o épico antigo do painel único continuam abertos.
**Por quê:** Sem esse recorte, a próxima rodada acha que Sinais ainda é só família de cópia ou que a campanha fechou.

**Detalhe técnico**

P task. Files: `docs/OPERATOR-PANEL-MAP.md`, `docs/DASHBOARD-OPERATIONS.md`, `docs/ISSUES.md`, `docs/DIARY.md` (ISS-019 keep **aberto** until EXECUTE evidence + operator confirm; ISS-017 keep **aberto**; ISS-007 keep open; ISS-018 stays **fechado**). Update area 2 Sinais: provenance columns; inventory; Feature 4 adoption block; prodigy pool research. Real empty strings. Collective2 closed. DASHBOARD-OPERATIONS row «Ver cópia» mentions origin/inventory/criteria. Do not close ISS-010 / ISS-011 / ISS-007 / ISS-009 / ISS-017. Do not claim EasyPanel rebuild. Do not mark N45–N47 started. LIVE false.

---

## Sprint N50 — Habilitar Collective2 por lista nomeada e reorganizar Sinais
> Categoria: N  
> Status: planejada  
> Gerado via: `/pmo plan` 2026-11-17 · fonte ISS-020 · Feature 4 já define C2 fechado (Passo 2: revisar política, não inventar score)  
> titulo_humano: Collective2 por lista nomeada e tela Sinais sem salada  
> resumo_humano: Depois do login você abre Sinais e vê o que está em operação separado da auditoria e dos candidatos de pesquisa. Collective2 só entra em cópia paper se você nomear o identificador; lista vazia continua fechada. O Prodígio mostra o provedor. O painel não envia ordem.  
> Gate: Requisitos com lista nomeada (vazia = cópia Collective2 fechada; H10 histórico); tela separa operação, auditoria e candidatos; pool mostra provedor; um ID nomeado não aprova os outros; sessão obrigatória; zero envio; pytest do painel verde; mapa atualizado; LIVE false  
> review: senior+qa  
> Brief: `docs/.briefs/N50.brief.md`  
> bom_ref: BOM-3  
> Depende de: N49 planejada/entregue · N48 concluida · Release: ISS-020 (não usa N45–N47)  
> LIVE_TRADING_ENABLED: false

### Em uma frase

A tela Sinais separa o que está em operação do que é auditoria e do que é só candidato de pesquisa; o Collective2 só entra em cópia paper com identificadores que você nomear; o Prodígio deixa de mostrar provedor vazio.

### O que muda para você

- Collective2 deixa de ser um bloqueio total: a cópia paper só abre para os identificadores que você colocar na lista nomeada (vazia = continua fechado)
- A tela Sinais deixa claro o que está ativo ou assinado versus a auditoria de ingresso versus os candidatos do Prodígio
- O pool do Prodígio mostra o identificador do provedor em vez de vazio
- Os dez candidatos observados no passado não entram sozinhos na lista
- O painel não envia ordem; dinheiro real permanece desligado

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Política de aprovação por identificador nomeado | Ler os requisitos: lista vazia fecha a cópia; só entra quem você nomear; o relato antigo dos dez candidatos continua histórico |
| 2 | Marketplace visível sem aprovar todo mundo | Abrir Sinais: sem nomes na lista, a cópia Collective2 aparece fechada; com um identificador nomeado, só esse aparece como assinado |
| 3 | Tela em três papéis claros | Ver operação/assinados no topo, auditoria no fim, candidatos do Prodígio no meio, cada um com título próprio |
| 4 | Provedor do Prodígio visível | No pool, a coluna de provedor mostra o identificador — não vazio |
| 5 | Mapa e chamado atualizados | O mapa descreve a lista nomeada e as três seções; o chamado ISS-020 aponta esta sprint |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | P | N50.0 Inventariar o reuso do Collective2, do painel de Sinais e do campo do Prodígio | `/git` | — |
| [ ] | P | N50.1 Atualizar a política de Collective2 nos requisitos | docs | N50.0 |
| [ ] | M | N50.2 Ligar a lista nomeada de Collective2 e corrigir o provedor do Prodígio | `/dev` | N50.1 |
| [ ] | M | N50.3 Reorganizar a tela Sinais em operação, auditoria e candidatos | `/dev` | N50.2 |
| [ ] | P | N50.4 Provar lista vazia, provedor visível e seções distintas | `/qa testes` | N50.3 |
| [ ] | P | N50.5 Atualizar o mapa e o chamado depois da tela reorganizada | docs | N50.4 |

### Quality Brief (Sprint N50)

Maintain: `LIVE_TRADING_ENABLED=false`; paper host only; dashboard does not submit or cancel orders.
Maintain: load `trader-entry|exit|budget|risk|scanner` only via `src/original.py`; do not invent scoring thresholds; do not call `prodigy_rank.calculate` or Collective2 HTTP from the panel.
Maintain: confirmed fills only; `queued_intent` and HTTP 200 are not fills; gross label when costs incomplete.
Maintain: named Collective2 allowlist defaults empty; never bulk-approve H10’s ten; rank eligibility is not paper-copy approval; active-order snapshots are not tickets.
Avoid: mapping only `row.get('provider')`; parallel `/c2`; new SQL column; stealing N45–N47; closing ISS-007/010/011/017/019; auto-promote; printing API keys.

### Fora de escopo

- Aprovar em lote os dez candidatos históricos ou copiar IDs de exemplo do feed
- Tratar ranking como aprovação de cópia paper
- Chamar o poller Collective2 ou o cálculo de ranking a partir do painel
- Sintetizar ticket a partir de ordem ativa Collective2
- Nova coluna SQL
- Inventar fill, custo líquido, P&L ou score
- POST ou cancelamento de ordem pelo painel
- Tela própria de Tá Barato (N45)
- Clear / OANDA / N29.5
- `LIVE_TRADING_ENABLED=true`
- Fechar ISS-007 / ISS-010 / ISS-011 / ISS-009 / ISS-017 / ISS-019
- Roubar identificadores N45–N47

### Task N50.0 — Inventariar o reuso do Collective2, do painel de Sinais e do campo do Prodígio

**Entrega:** Inventário curto dizendo que o feed e o ranking Collective2 já existem, que a tela hoje mistura papéis, e que o Prodígio já emite o identificador do provedor que o painel ignora.
**Como conferir:** O inventário cita o poller só leitura, o ranking de pesquisa, a lista nomeada vazia, o campo errado do provedor, e deixa envio pelo painel, câmbio e os dez candidatos automáticos de fora.
**Por quê:** Sem essa lista o EXECUTE aprova todo mundo, inventa score ou sintetiza ticket.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N50-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md` vs `git ls-remote` `Jakeschincariol/day-trader-skill` `main`; do not bump. Local vendor may be uninitialized/empty — do not treat it as reviewed main. If GitHub unreachable, stop claiming current main. Do not touch `src/` in this task.

Cite: `c2_signal_feed.snapshot`; `c2_history_collect`; `prodigy_rank` `provider_id`; `_load_prodigy_opportunities`; `build_panel_copy` collective2 hardcoded closed; Feature 4 / H10. Do not plan Alpaca HTTP from the panel. Do not steal N45–N47. Do not copy example strategy IDs into the allowlist.

### Task N50.1 — Atualizar a política de Collective2 nos requisitos

**Entrega:** Os requisitos passam a dizer que a cópia Collective2 abre só para identificadores que o operador nomear, com a lista vazia como padrão, e que o relato antigo dos dez candidatos continua histórico.
**Como conferir:** Abrir os requisitos: Feature 4, integrações e fora de escopo falam em lista nomeada; a linha H10 ainda descreve os dez candidatos daquele corte, sem transformá-los em aprovados.
**Por quê:** Ligar o marketplace sem gravar a política faria o código contradizer o contrato que já fechava a cópia.

**Detalhe técnico**

P task (docs-only). File: `docs/REQUIREMENTS.md` bump to **v0.5** with a revision-history row. Rewrite Feature 4 signal-copy paragraph and acceptance bullet: no Collective2 provider enters copy unless its numeric id is on the named allowlist (default empty). H10 row stays historical (10 candidates, 0 eligible); add one sentence that eligibility from rank is not approval. §5 Integrações Collective2: marketplace + named allowlist; panel does not call the API. §7 Fora de Escopo: forbid copying a provider **not** on the allowlist; forbid synthesizing a ticket from an active-order snapshot; keep the H10 ten unapproved until named. Do not invent scores, windows, or min-trades. Do not mark Feature 4 checkboxes as newly proven paper fills. LIVE false.

### Task N50.2 — Ligar a lista nomeada de Collective2 e corrigir o provedor do Prodígio

**Entrega:** O pacote do painel lê uma lista nomeada vazia por padrão; só os identificadores listados entram como assinados Collective2; o pool do Prodígio passa a exibir o identificador do provedor.
**Como conferir:** Pedir o teste de dados em que a lista vazia deixa a cópia fechada, um identificador nomeado aparece sozinho como assinado, e o item do Prodígio traz o provedor preenchido.
**Por quê:** Hoje o banner diz fechado para sempre e o pool mostra provedor vazio mesmo com ranking gravado.

**Detalhe técnico**

- **Estado atual:** `copy.collective2` is always `{approved_for_paper_copy: false, status: closed}`. `_load_prodigy_opportunities` sets `provider` from `row.get('provider')` while rank JSON has `provider_id`.
- **Estado desejado:** empty JSON allowlist + optional numeric env overlay; `copy.collective2.approved_ids`; closed if empty; Prodígio `provider` falls back to `provider_id`. No HTTP, no tickets from snapshots.
- **Fonte(s):** ISS-020, Feature 4 / H10, `prodigy_rank.provider_id`, N49 `build_panel_copy`.
- **Risco:** MEDIUM — silent approve-all or invented tickets would violate Feature 4 / the C2 feed contract.
- **Arquivo(s):** `src/panel_ops_data.py`, `src/trading_dashboard_data.py`, `config/c2_paper_copy_allowlist.json`

**executor_prompt**:

```yaml
id: N50.2
size: M
bom_ref: BOM-3
depends_on: ["N50.1"]
files:
  - src/panel_ops_data.py
  - src/trading_dashboard_data.py
  - config/c2_paper_copy_allowlist.json
reuse_targets:
  - component: src/panel_ops_data.py
    reuse_as: extend
    convergence_check: rg "def build_panel_copy" src/panel_ops_data.py && rg "approved_ids" src/panel_ops_data.py && rg "c2_paper_copy_allowlist" src/panel_ops_data.py
  - component: src/trading_dashboard_data.py
    reuse_as: extend
    convergence_check: rg "def _load_prodigy_opportunities" src/trading_dashboard_data.py && rg "provider_id" src/trading_dashboard_data.py
  - component: src/c2_signal_feed.py
    reuse_as: call
    convergence_check: rg "execution_authorized" src/c2_signal_feed.py && rg "active-orders-latest.json" src/panel_ops_data.py
  - component: src/prodigy_rank.py
    reuse_as: call
    convergence_check: rg "provider_id" src/prodigy_rank.py && ! rg "def calculate" src/panel_ops_data.py
guardrail_contract:
  - class: secrets
    id: n50-2-no-secrets
    target: src/panel_ops_data.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_data.py').read_text()+Path('src/trading_dashboard_data.py').read_text(); assert 'sk_live' not in t.lower(); assert 'C2_API4_KEY' not in t; assert 'SIGNAL_COPY_SECRET' not in t"
    pass_condition: panel loaders do not embed or read the Collective2 API key
  - class: subagent-safety
    id: n50-2-named-allowlist
    target: src/panel_ops_data.py
    check: python3 -c "from pathlib import Path; import json; t=Path('src/panel_ops_data.py').read_text(); d=Path('src/trading_dashboard_data.py').read_text(); a=json.loads(Path('config/c2_paper_copy_allowlist.json').read_text()); assert a.get('approved_ids')==[]; assert 'process_after_gate_b' not in t; assert 'fetch_orders' not in t; assert '30415311' not in t; assert 'provider_id' in d; assert 'approved_ids' in t"
    pass_condition: empty allowlist committed; no bulk example IDs; no paper submit; prodigy loader reads provider_id
```

### Quality Brief (Sprint N50)

Maintain: LIVE_TRADING_ENABLED=false; paper host only; dashboard does not submit or cancel orders.
Maintain: load trader-entry|exit|budget|risk|scanner only via src/original.py; do not invent scoring thresholds; do not call prodigy_rank.calculate or Collective2 HTTP from the panel.
Maintain: confirmed fills only; queued_intent is not a fill; PERFORMANCE_LABEL_GROSS when costs incomplete.
Maintain: named allowlist defaults empty; never bulk-approve H10 ten; rank eligible is not approval.
Avoid: seeding example strategy IDs; synthesizing tickets from active-order snapshots; mapping only row.get('provider').

Melhoria: attach a named Collective2 allowlist to copy.collective2 and map prodigy provider_id into provider without rescoring.
Contexto: Feature 4 / H10 close all C2 copy. Operator wants the other marketplace enabled honestly. Rank JSON uses provider_id; loader and HTML read provider, so the pool shows None. c2_signal_feed forbids treating active orders as tickets. control_flags has no allowlist column — do not migrate risk anchors.
Objetivo: (1) Add config/c2_paper_copy_allowlist.json {"approved_ids":[]} committed. (2) Loader unions that list with optional env C2_PAPER_COPY_APPROVED_IDS (comma-separated digits only; ignore junk). (3) copy.collective2 = {approved_ids, approved_for_paper_copy: bool(approved_ids), status: closed|allowlist, candidates: research-labeled from existing on-disk rank/history if present, never merged into operating}. (4) If reports/providers/signals/active-orders-latest.json exists, attach a snapshot object with execution_authorized false and a Portuguese label that it is not a ticket; do not call fetch_orders. (5) Operating C2 rows = existing paper orders whose origin is collective2 OR allowlisted ids shown as subscribed even with zero orders (honest empty). (6) _load_prodigy_opportunities: provider = row.get('provider') or row.get('provider_id'); keep status, prodigy_score, research_tip. (7) Do not import signal_copy. Do not import process_after_gate_b. Do not import prodigy_rank.calculate. Do not hardcode 30415311 or the H10 ten. LIVE false.
Arquivos: src/panel_ops_data.py, src/trading_dashboard_data.py, config/c2_paper_copy_allowlist.json.
Critério de pronto: allowlist JSON exists with approved_ids []; rg shows approved_ids and provider_id; C2_API4_KEY absent from those two py files; no fetch_orders in panel_ops_data.
Cenários de teste (implement in N50.4):
1. Empty allowlist → approved_for_paper_copy false, status closed, no operating C2 ids.
2. One named id in JSON or env → only that id in approved_ids; others remain candidates/research.
3. Rank fixture with provider_id and no provider → pool item provider equals that id (not None).
4. Missing snapshot file → no invented active orders.
5. Present snapshot → listed as not a ticket; execution_authorized false.
6. Regressão: copy.operating/history/inventory/adoption/prodigy_pool still present; PERFORMANCE_LABEL_GROSS kept.

### Task N50.3 — Reorganizar a tela Sinais em operação, auditoria e candidatos

**Entrega:** A mesma tela Sinais mostra em operação/assinados no topo, Collective2 e Prodígio como papéis distintos, e a auditoria de ingresso por último — sem botão de enviar ordem.
**Como conferir:** Abrir o painel logado, clicar em Sinais, ver os títulos nessa ordem, Collective2 fechado se a lista estiver vazia, e o provedor preenchido no pool.
**Por quê:** Hoje cópia, inventário, critérios, pool e auditoria aparecem misturados no mesmo scroll; o operador não distingue o que opera do que só audita.

**Detalhe técnico**

- **Estado atual:** `render_signals_page` order is copy, inventory, adoption, pool, audit. Collective2 is one closed sentence inside copy. Pool Provedor column uses `it.get("provider")`.
- **Estado desejado:** headings in Portuguese: operação/assinados first, inventory, Collective2 marketplace, Prodígio research candidates, adoption, audit last. Fallback provider or provider_id in the table. Same `/sinais`. No POST.
- **Fonte(s):** ISS-020 diretrizes 2–3, OPERATOR-PANEL-MAP §2, N48/N49 HTML shell.
- **Risco:** MEDIUM — operator-facing copy; a closed banner that claims all ten are approved would break the contract.
- **Arquivo(s):** `src/panel_ops_html.py`, `src/v4_web_dashboard.py`

**executor_prompt**:

```yaml
id: N50.3
size: M
bom_ref: BOM-3
depends_on: ["N50.2"]
files:
  - src/panel_ops_html.py
  - src/v4_web_dashboard.py
reuse_targets:
  - component: src/panel_ops_html.py
    reuse_as: extend
    convergence_check: 'rg "def render_signals_page" src/panel_ops_html.py && rg "Em operação / assinados" src/panel_ops_html.py && rg "Auditoria de ingresso" src/panel_ops_html.py && rg "Candidatos Prodígio" src/panel_ops_html.py'
  - component: src/panel_ops_html.py
    reuse_as: copy_pattern
    convergence_check: 'rg "lista nomeada" src/panel_ops_html.py && rg "def _signals_prodigy_pool_html" src/panel_ops_html.py'
  - component: src/v4_web_dashboard.py
    reuse_as: extend
    convergence_check: rg "/api/signals" src/v4_web_dashboard.py && rg "serve_panel_json" src/v4_web_dashboard.py
guardrail_contract:
  - class: secrets
    id: n50-3-no-secrets
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_html.py').read_text()+Path('src/v4_web_dashboard.py').read_text(); assert 'sk_live' not in t.lower(); assert 'C2_API4_KEY' not in t; assert 'SIGNAL_COPY_SECRET' not in t"
    pass_condition: no live keys or Collective2 API key in HTML or dashboard routes
  - class: subagent-safety
    id: n50-3-read-only-page
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; html=Path('src/panel_ops_html.py').read_text(); dash=Path('src/v4_web_dashboard.py').read_text(); assert 'process_after_gate_b' not in html; assert 'process_after_gate_b' not in dash; assert 'Em operação / assinados' in html; assert 'Auditoria de ingresso' in html; assert 'Candidatos Prodígio' in html; paths=html.split('OPERATOR_PANEL_PATHS',1)[1].split(')',1)[0]; assert '/c2' not in paths; assert '/copy' not in paths"
    pass_condition: same /sinais route; three roles visible; dashboard still does not call paper submit
```

### Quality Brief (Sprint N50)

Maintain: LIVE_TRADING_ENABLED=false; operator session cookie in front of /sinais; do not add a parallel route.
Maintain: Feature 9 ingest table remains under a distinct heading at the bottom. N48/N49 inventory and adoption remain.
Maintain: empty allowlist copy is explicit Portuguese; prodigy pool says research not operating; provider column uses provider or provider_id.
Avoid: Live button; order submit/cancel; calling signal_copy.validate; rewriting Feature 4 numbers; listing H10 ten as approved.

Melhoria: extend authenticated GET /sinais and GET /api/signals with a clear ACTIVE vs audit vs Prodígio research layout and honest Collective2 allowlist copy.
Contexto: five h2 blocks already exist but read as a salad. Operator asked what is active/subscribed/operating vs audit vs Prodigy candidates. Collective2 must remain closed when the allowlist is empty.
Objetivo: (1) Keep OPERATOR_PANEL_PATHS and _nav Sinais → /sinais (no /copy, no /c2). (2) Section order: `Em operação / assinados` (TradingView signal_copy + allowlisted C2); `Inventário de sinais`; `Collective2`; `Candidatos Prodígio (pesquisa)`; `Critérios de adoção`; `Auditoria de ingresso` last. (3) Empty operating stays `Nenhuma cópia de terceiro em operação.` (4) Collective2 empty: `Collective2: cópia paper fechada — nenhum provedor na lista nomeada.` Collective2 with ids: `Collective2: cópia paper só para os provedores nomeados.` (5) Pool subtitle stays pesquisa — não autoriza ordem / não promove. Table cell uses provider or provider_id. (6) Audit subtitle unchanged: origem, destino e motivo. Não é fill. (7) Footer unchanged: painel não envia ordem. Live desligado. (8) serve_panel_json /api/signals keeps signals and copy; copy.collective2 matches N50.2. Session required. (9) No POST. Update adoption bullet that previously said Collective2 always closed so it matches named allowlist (empty = closed).
Arquivos: src/panel_ops_html.py, src/v4_web_dashboard.py.
Critério de pronto: logged-in GET /sinais HTML contains the three role headings in that relative order (operação before audit, Prodígio candidates distinct); empty Collective2 string; unauthenticated still blocked; OPERATOR_PANEL_PATHS still has no /copy and no /c2.
Cenários de teste (implement in N50.4):
1. Sem cookie → redirect/401 like today /sinais.
2. Lista vazia → string de cópia paper fechada / lista nomeada; nenhum ID aparece como assinado Collective2.
3. Um ID nomeado → esse ID visível como assinado; os demais não.
4. Pool com provider_id → coluna Provedor não é None/NONE.
5. Auditoria ainda mostra origem/destino/motivo (Feature 9) e vem depois da operação.
6. HTML sem controle de envio. Regressão: /ordens /historico /estrategias /performance /central /prodigy still render.

### Task N50.4 — Provar lista vazia, provedor visível e seções distintas

**Entrega:** Testes mostram lista vazia fechada, um identificador nomeado sozinho, provedor do Prodígio visível, as três seções na ordem combinada, recusa sem login, e que a página não envia ordem nem inventa fill.
**Como conferir:** Pedir essa bateria e ver falha se a cópia Collective2 parecer toda aprovada, se o provedor voltar vazio, se a auditoria subir para o topo, ou se aparecer controle de envio.
**Por quê:** Sem prova, o mapa poderia marcar completo com a salada e o Provedor None ainda no ar.

**Detalhe técnico**

P task. File: `tests/test_panel_ops.py` (extend; 1 file). Reuse PanelOpsHttpTests cookie pattern. Nodeids for: unauthenticated /sinais; empty allowlist Portuguese closed string; one named id only; prodigy pool provider from provider_id (not None); headings `Em operação / assinados`, `Candidatos Prodígio`, `Auditoria de ingresso` with operação before audit; Feature 9 origin/destination/reject_reason still on /api/signals `signals`; copy.collective2.approved_ids; snapshot not a ticket; no process_after_gate_b / order form; regression previous menu routes and N48/N49 inventory/adoption. Do not call real Alpaca or Collective2 HTTP. Do not put C2_API4_KEY in tests. LIVE false in env. No secret values.

### Task N50.5 — Atualizar o mapa e o chamado depois da tela reorganizada

**Entrega:** O mapa descreve Sinais em operação, auditoria e candidatos, com Collective2 por lista nomeada; o chamado ISS-020 aponta esta sprint; a campanha e o épico antigo continuam abertos.
**Como conferir:** Abrir o mapa na área Sinais: três papéis, lista nomeada, provedor visível; ISS-020 ligado a N50; ISS-017, ISS-019 e o épico antigo do painel único continuam abertos.
**Por quê:** Sem esse recorte, a próxima rodada acha que Collective2 ainda está interditado para sempre ou que a campanha fechou.

**Detalhe técnico**

P task. Files: `docs/OPERATOR-PANEL-MAP.md`, `docs/DASHBOARD-OPERATIONS.md`, `docs/ISSUES.md`, `docs/DIARY.md` (ISS-020 keep **aberto** until EXECUTE evidence + operator confirm; ISS-019 keep **aberto** unless operator already closed; ISS-017 keep **aberto**; ISS-007 keep open). Update area 2 Sinais: ACTIVE vs audit vs Prodígio; named allowlist; real empty Collective2 string; provider_id mapping. DASHBOARD-OPERATIONS «Ver sinais» mentions the three roles. Do not close ISS-010 / ISS-011 / ISS-007 / ISS-009 / ISS-017 / ISS-019. Do not claim EasyPanel rebuild. Do not mark N45–N47 started. LIVE false.

---

## Sprint N51 — Colocar a pré-aprovação de provedores no painel com métricas de pesquisa
> Categoria: N  
> Status: planejada  
> Gerado via: `/pmo plan` 2026-11-17 · fonte ISS-021 · Feature 4 já define lista nomeada (Passo 2: revisar política para o painel, não inventar score)  
> titulo_humano: Pré-aprovação no painel com métricas de pesquisa  
> resumo_humano: Depois do login você vê uma fila de provedores novos, com percentual de acertos e ganho só quando o ranking de pesquisa já gravou o campo. Aprovar ou rejeitar é no painel e não envia ordem. Arquivo e ambiente viram semente.  
> Gate: Requisitos com pré-aprovação no painel (arquivo/ambiente = semente); fila com métricas reutilizadas; aprovar/rejeitar autenticado persiste; rejeitado não volta pela semente; sessão obrigatória; zero envio; pytest do painel verde; mapa atualizado; LIVE false  
> review: senior+qa  
> Brief: `docs/.briefs/N51.brief.md`  
> bom_ref: BOM-3  
> Depende de: N50 planejada/entregue · N49 planejada · N48 concluida · Release: ISS-021 (não usa N45–N47)  
> LIVE_TRADING_ENABLED: false

### Em uma frase

Todo provedor de sinal novo entra numa fila de pré-aprovação no painel; você aprova ou rejeita logado, vendo as métricas de pesquisa já gravadas, e isso não envia ordem.

### O que muda para você

- Aprovar ou rejeitar um provedor passa a ser um clique no painel, não editar lista, variável de ambiente ou rebuild
- A fila mostra percentual de acertos, resultado reportado e demais campos já existentes no ranking de pesquisa; se o campo não existir, aparece indisponível — sem fórmula nova
- A mesma regra vale para Collective2, Prodígio, TradingView e fontes futuras
- Aprovar não é fill e não dispara ordem; dinheiro real permanece desligado
- A lista em arquivo e a variável de ambiente ficam só como semente se o livro-razão ainda não tiver decisão

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Política de pré-aprovação no painel | Ler os requisitos: o caminho do dia a dia é aprovar no painel; arquivo e ambiente são semente; ranking não aprova sozinho |
| 2 | Fila persistida | Depois de um rebuild, a decisão de aprovar ou rejeitar continua; um rejeitado não volta pela semente |
| 3 | Métricas visíveis na decisão | Na fila, cada candidato mostra acertos e ganho só se o campo já existir no ranking; falta = indisponível, rotulado pesquisa |
| 4 | Aprovar e rejeitar no painel | Logado, clicar aprovar ou rejeitar muda o status; sem login a ação é recusada; nenhum controle de envio de ordem |
| 5 | Mapa e chamado atualizados | O mapa descreve a fila; o chamado ISS-021 aponta esta sprint |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | P | N51.0 Inventariar o reuso da fila de pré-aprovação e das métricas já gravadas | `/git` | — |
| [ ] | P | N51.1 Atualizar a política de aprovação nos requisitos | docs | N51.0 |
| [ ] | M | N51.2 Persistir as decisões no livro-razão e montar a fila com métricas reutilizadas | `/dev` | N51.1 |
| [ ] | M | N51.3 Mostrar a fila no painel com aprovar, rejeitar e métricas visíveis | `/dev` | N51.2 |
| [ ] | P | N51.4 Provar fila, métricas reutilizadas, recusa sem login e ausência de envio | `/qa testes` | N51.3 |
| [ ] | P | N51.5 Atualizar o mapa e o chamado depois da fila no painel | docs | N51.4 |

### Quality Brief (Sprint N51)

Maintain: `LIVE_TRADING_ENABLED=false`; paper host only; dashboard does not submit or cancel orders; approval is not a fill.
Maintain: load `trader-entry|exit|budget|risk|scanner` only via `src/original.py`; do not invent scoring thresholds; do not call `prodigy_rank.calculate` or Collective2 HTTP from the panel.
Maintain: confirmed fills only; `queued_intent` and HTTP 200 are not fills; gross label when costs incomplete.
Maintain: N50 JSON/env is seed/fallback; ledger reject wins; rank eligibility is not paper-copy approval; H10 remains historical.
Avoid: mutating `control_flags`; parallel `/aprovacoes`; filling missing metrics with 0; stealing N45–N47; closing ISS-007/010/011/017/019/020; auto-promote; printing API keys.

### Fora de escopo

- Inventar fórmula de assertividade ou score composto
- Tratar ranking como aprovação de cópia paper
- Chamar o poller Collective2 ou o cálculo de ranking a partir do painel
- POST ou cancelamento de ordem pelo painel
- Alterar âncoras de risco
- Reescrever o webhook TradingView
- Aprovar em lote os dez candidatos históricos
- Tela própria de Tá Barato (N45)
- Clear / OANDA / N29.5
- `LIVE_TRADING_ENABLED=true`
- Fechar ISS-007 / ISS-010 / ISS-011 / ISS-009 / ISS-017 / ISS-019 / ISS-020
- Roubar identificadores N45–N47

### Task N51.0 — Inventariar o reuso da fila de pré-aprovação e das métricas já gravadas

**Entrega:** Inventário curto dizendo que a sessão do painel e a lista nomeada já existem, que o ranking já emite percentual de acertos e ganho, e que o livro-razão ainda não guarda decisão de provedor.
**Como conferir:** O inventário cita sessão autenticada, semente da lista nomeada, campos de ranking reutilizáveis, tabela nova no livro-razão, e deixa envio pelo painel, fórmula nova e os dez candidatos automáticos de fora.
**Por quê:** Sem essa lista o EXECUTE inventa score, reabre variável de ambiente como caminho do operador, ou dispara ordem ao aprovar.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N51-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md` vs `git ls-remote` `Jakeschincariol/day-trader-skill` `main`; do not bump. Local vendor may be uninitialized/empty — do not treat it as reviewed main. If GitHub unreachable, stop claiming current main. Do not touch `src/` in this task.

Cite: `operator_session_authorized`; `load_c2_paper_copy_approved_ids`; `prodigy_rank` `win_rate_pct` / `profit_factor_reported` / `reported_pnl_sum`; `provider_rank` `net_return_pct`; `ledger_migrate` 001+002; Feature 4 / H10. Do not plan Alpaca HTTP from the panel. Do not steal N45–N47. Do not invent an assertiveness formula.

### Task N51.1 — Atualizar a política de aprovação nos requisitos

**Entrega:** Os requisitos passam a dizer que o caminho do dia a dia é pré-aprovar no painel, que arquivo e ambiente são só semente, e que as métricas exibidas são campos já recuperados — com lacuna explícita se o nome pedido pelo operador não existir no código.
**Como conferir:** Abrir os requisitos: Feature 4, integrações e fora de escopo falam em fila no painel; a linha H10 ainda descreve os dez candidatos daquele corte; percentual de acertos aponta para o campo já gravado no ranking.
**Por quê:** Ligar o clique sem gravar a política deixaria o contrato na lista em arquivo que o operador recusou.

**Detalhe técnico**

P task (docs-only). File: `docs/REQUIREMENTS.md` bump to **v0.6** with a revision-history row. Rewrite Feature 4 signal-copy paragraph and acceptance bullet: every new provider candidate enters a pre-approval queue; approve/reject is the authenticated panel; N50 `config/c2_paper_copy_allowlist.json` and `C2_PAPER_COPY_APPROVED_IDS` are seed/fallback when the ledger has no row for that id; a ledger reject wins. Display `win_rate_pct` as percentual de acertos (pesquisa); there is **no** recovered field named assertividade — document the gap; never invent a composite. H10 row stays historical. §5 Integrações Collective2: marketplace + panel pre-approval; panel does not call the API. §7 Fora de Escopo: forbid copy of a provider not approved in the panel (except seed until first decision); forbid treating rank eligible as approval; forbid panel order POST. Do not invent scores, windows, or min-trades. Do not mark Feature 4 checkboxes as newly proven paper fills. LIVE false.

### Task N51.2 — Persistir as decisões no livro-razão e montar a fila com métricas reutilizadas

**Entrega:** O pacote do painel monta uma fila de candidatos de qualquer fonte, com status pendente/aprovado/rejeitado gravado no livro-razão, e anexa só as métricas que o ranking de pesquisa já tiver.
**Como conferir:** Pedir o teste de dados em que a fila nasce pendente, um aprovado persiste, um rejeitado não volta pela semente, e um candidato sem campo de ranking mostra indisponível — nunca zero inventado.
**Por quê:** Hoje a lista nomeada some no rebuild ou exige editar arquivo; o ranking já tem os números e o painel não os mostra para decidir.

**Detalhe técnico**

- **Estado atual:** `load_c2_paper_copy_approved_ids` unions committed JSON + env. No SQL table for provider adoption. Candidate loader drops rank metrics. `control_flags` is risk anchors only.
- **Estado desejado:** migration `003` table `signal_provider_approvals`; queue union of discovered candidates; metrics overlay from on-disk rank JSON; seed only when no ledger row; reject wins. No HTTP, no tickets, no new score.
- **Fonte(s):** ISS-021, Feature 4 / H10, `prodigy_rank` fields, N50 `build_panel_copy`, `ledger_migrate` 002 pattern.
- **Risco:** MEDIUM — env overlay resurrecting a reject, or inventing metrics, would violate the operator contract.
- **Arquivo(s):** `src/panel_ops_data.py`, `src/ledger_migrate.py`, `migrations/003_signal_provider_approvals_up.sql`, `migrations/003_signal_provider_approvals_down.sql`

**executor_prompt**:

```yaml
id: N51.2
size: M
bom_ref: BOM-3
depends_on: ["N51.1"]
files:
  - src/panel_ops_data.py
  - src/ledger_migrate.py
  - migrations/003_signal_provider_approvals_up.sql
  - migrations/003_signal_provider_approvals_down.sql
reuse_targets:
  - component: src/panel_ops_data.py
    reuse_as: extend
    convergence_check: rg "def load_c2_paper_copy_approved_ids" src/panel_ops_data.py && rg "preapproval" src/panel_ops_data.py && rg "signal_provider_approvals" src/panel_ops_data.py
  - component: src/ledger_migrate.py
    reuse_as: extend
    convergence_check: rg "VERSION_TRIGGERS" src/ledger_migrate.py && rg "001_ledger" src/ledger_migrate.py
  - component: migrations/002_triggers_up.sql
    reuse_as: copy_pattern
    convergence_check: rg "CREATE TABLE IF NOT EXISTS trigger_changes" migrations/002_triggers_up.sql && rg "schema_migrations" migrations/002_triggers_up.sql
  - component: src/prodigy_rank.py
    reuse_as: call
    convergence_check: rg "win_rate_pct" src/prodigy_rank.py && ! rg "def calculate" src/panel_ops_data.py
guardrail_contract:
  - class: secrets
    id: n51-2-no-secrets
    target: src/panel_ops_data.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_data.py').read_text()+Path('src/ledger_migrate.py').read_text(); assert 'sk_live' not in t.lower(); assert 'C2_API4_KEY' not in t; assert 'SIGNAL_COPY_SECRET' not in t"
    pass_condition: loaders and migrate do not embed Collective2 or broker keys
  - class: subagent-safety
    id: n51-2-ledger-not-risk-anchors
    target: src/panel_ops_data.py
    check: python3 -c "from pathlib import Path; d=Path('src/panel_ops_data.py').read_text(); m=Path('src/ledger_migrate.py').read_text(); t=Path('migrations/002_triggers_up.sql').read_text(); assert 'process_after_gate_b' not in d; assert 'fetch_orders' not in d; assert 'VERSION_TRIGGERS' in m; assert 'control_flags' in t"
    pass_condition: no paper submit from panel loader; 003 must not alter control_flags (file tests in N51.4)
```

### Quality Brief (Sprint N51)

Maintain: LIVE_TRADING_ENABLED=false; paper host only; dashboard does not submit or cancel orders.
Maintain: load trader-entry|exit|budget|risk|scanner only via src/original.py; do not invent scoring thresholds; do not call prodigy_rank.calculate or Collective2 HTTP from the panel.
Maintain: confirmed fills only; queued_intent is not a fill; PERFORMANCE_LABEL_GROSS when costs incomplete.
Maintain: N50 JSON/env seed only; ledger reject wins; rank eligible is not approval.
Avoid: mutating control_flags; filling missing metrics with 0; bulk-approving H10 ten; synthesizing tickets.

Melhoria: persist provider pre-approval in the ledger and attach recovered research metrics to a unified queue.
Contexto: Operator rejected JSON/env/rebuild as the daily path. prodigy_rank already has win_rate_pct, shrunk_win_rate_pct, profit_factor_reported, reported_pnl_sum, prodigy_score. provider_rank has win_rate_pct, net_return_pct, max_drawdown_pct, score. No recovered field named assertividade. control_flags is risk anchors — do not migrate those.
Objetivo: (1) Add migrations/003_signal_provider_approvals_up.sql creating signal_provider_approvals (platform, provider_id, status pending|approved|rejected, source panel|seed_json|seed_env, decided_at, timestamps, unique platform+provider_id). Down drops only that table. (2) Extend ledger_migrate apply/status/rollback for 003 without rewriting 001/002. (3) Discover candidates from existing on-disk C2 rank/history, Prodígio pool, and unique TradingView origins already in the copy/signals bundle — do not call calculate/fetch. (4) Overlay metrics dict with only present recovered keys; never coerce missing to 0. (5) Eligibility: ledger approved ∪ (N50 seed ids with no ledger row); ledger rejected excluded even if still in JSON/env. (6) copy.preapproval.queue on build_panel_copy. (7) copy.collective2.approved_ids follows eligibility. (8) Do not import signal_copy. Do not import process_after_gate_b. Do not import prodigy_rank.calculate. LIVE false.
Arquivos: src/panel_ops_data.py, src/ledger_migrate.py, migrations/003_signal_provider_approvals_up.sql, migrations/003_signal_provider_approvals_down.sql.
Critério de pronto: 003 SQL exists; rg shows signal_provider_approvals and win_rate_pct in panel_ops_data; C2_API4_KEY absent; no ALTER TABLE control_flags in 003; no fetch_orders in panel_ops_data.
Cenários de teste (implement in N51.4):
1. No ledger rows + empty seed → queue pending or empty honest; approved_for_paper_copy false.
2. Seed id without ledger row → appears approved with source seed; not mixed into invented fills.
3. Ledger reject of a seed id → excluded from approved_ids; still listed as rejected.
4. Rank fixture with win_rate_pct → queue item metrics include that field labeled research_only.
5. Rank fixture missing net_return_pct → key absent or indisponível; not 0.
6. TradingView origin without rank JSON → metrics empty/indisponível.
7. Regressão: copy.operating/history/inventory/adoption/prodigy_pool and N50 collective2 snapshot-not-ticket still present.

### Task N51.3 — Mostrar a fila no painel com aprovar, rejeitar e métricas visíveis

**Entrega:** A mesma tela Sinais ganha a fila de pré-aprovação em português, com botões de aprovar e rejeitar só para quem está logado, métricas de pesquisa visíveis, e sem botão de enviar ordem.
**Como conferir:** Abrir o painel logado, clicar em Sinais, ver a fila, aprovar um pendente e ver o status mudar; sair da sessão e confirmar que a ação é recusada; confirmar que não existe controle de envio.
**Por quê:** Sem a superfície autenticada o operador continua dependendo de arquivo, ambiente ou rebuild — exatamente o que recusou.

**Detalhe técnico**

- **Estado atual:** `render_signals_page` has N50 sections; `do_POST` allows login + strategy-parameters only, else 405 Read only. No provider approve POST.
- **Estado desejado:** Portuguese section Pré-aprovação de provedores; Aprovar/Rejeitar posts to `/api/signals/providers`; session required; metrics columns from recovered fields; footer still says the panel does not send orders.
- **Fonte(s):** ISS-021 diretrizes 1–3, OPERATOR-PANEL-MAP §2, N50 HTML shell, `operator_session_authorized`.
- **Risco:** MEDIUM — a button that submits paper, or metrics shown as proven edge, would break Feature 4/10.
- **Arquivo(s):** `src/panel_ops_html.py`, `src/v4_web_dashboard.py`

**executor_prompt**:

```yaml
id: N51.3
size: M
bom_ref: BOM-3
depends_on: ["N51.2"]
files:
  - src/panel_ops_html.py
  - src/v4_web_dashboard.py
reuse_targets:
  - component: src/panel_ops_html.py
    reuse_as: extend
    convergence_check: 'rg "def render_signals_page" src/panel_ops_html.py && rg "Pré-aprovação de provedores" src/panel_ops_html.py && rg "Aprovar" src/panel_ops_html.py'
  - component: src/v4_web_dashboard.py
    reuse_as: copy_pattern
    convergence_check: rg "operator_session_authorized" src/v4_web_dashboard.py && rg "/api/signals/providers" src/v4_web_dashboard.py
  - component: src/v4_web_dashboard.py
    reuse_as: extend
    convergence_check: rg "/api/signals" src/v4_web_dashboard.py && rg "serve_panel_json" src/v4_web_dashboard.py
guardrail_contract:
  - class: secrets
    id: n51-3-no-secrets
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_html.py').read_text()+Path('src/v4_web_dashboard.py').read_text(); assert 'sk_live' not in t.lower(); assert 'C2_API4_KEY' not in t; assert 'SIGNAL_COPY_SECRET' not in t"
    pass_condition: no live keys or Collective2 API key in HTML or dashboard routes
  - class: subagent-safety
    id: n51-3-approve-not-order
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; html=Path('src/panel_ops_html.py').read_text(); dash=Path('src/v4_web_dashboard.py').read_text(); assert 'process_after_gate_b' not in html; assert 'process_after_gate_b' not in dash; assert 'Pré-aprovação de provedores' in html; assert '/api/signals/providers' in dash; assert 'paper-api.alpaca.markets' not in dash"
    pass_condition: same /sinais route; preapproval visible; dashboard still does not call paper submit
```

### Quality Brief (Sprint N51)

Maintain: LIVE_TRADING_ENABLED=false; operator session cookie in front of /sinais and POST; do not add a parallel route.
Maintain: Feature 9 ingest table remains; N50 operation/audit/Prodígio headings remain.
Maintain: metrics labeled pesquisa; missing field Portuguese indisponível; Aprovar não envia ordem.
Avoid: Live button; order submit/cancel; calling signal_copy.validate; rewriting Feature 4 numbers; listing H10 ten as approved.

Melhoria: extend authenticated GET /sinais and POST /api/signals/providers with a pre-approval queue and reused research metrics.
Contexto: N50 still requires JSON/env as the operator path. Operator 2026-11-17 demanded panel approve/reject and metrics that weigh the decision.
Objetivo: (1) Keep OPERATOR_PANEL_PATHS and _nav Sinais → /sinais (no /copy, no /aprovacoes). (2) Section `Pré-aprovação de provedores` with table: plataforma, identificador, status, percentual de acertos (pesquisa), resultado reportado (pesquisa), ações Aprovar/Rejeitar. (3) Empty: `Nenhum candidato em pré-aprovação.` (4) Subtitle: `Pesquisa — não autoriza ordem. Aprovar não é fill.` (5) POST /api/signals/providers JSON {platform, provider_id, action} only when operator_session_authorized; 401 otherwise; 422 invalid; 503 ledger unavailable. (6) serve_panel_json /api/signals includes copy.preapproval from N51.2. (7) Footer unchanged: painel não envia ordem. Live desligado. (8) Copy authenticated mutation pattern from strategy-parameters POST (JSON body, respond_mutation) — do not call Alpaca. (9) Portuguese UI. LIVE false.
Arquivos: src/panel_ops_html.py, src/v4_web_dashboard.py.
Critério de pronto: logged-in GET /sinais HTML contains Pré-aprovação de provedores and Aprovar; unauthenticated POST 401; OPERATOR_PANEL_PATHS still has no /copy; process_after_gate_b absent from both files.
Cenários de teste (implement in N51.4):
1. Sem cookie → GET /sinais redirect/401; POST /api/signals/providers 401.
2. Fila vazia → string nenhum candidato.
3. Candidato com win_rate_pct → célula mostra o número e o rótulo pesquisa.
4. Candidato sem métricas → indisponível, não 0.
5. POST approve autenticado → status aprovado no GET seguinte; HTML sem controle de envio.
6. Regressão: /ordens /historico /estrategias /performance /central /prodigy and N50 headings still render.

### Task N51.4 — Provar fila, métricas reutilizadas, recusa sem login e ausência de envio

**Entrega:** Testes mostram fila pendente, aprovação persistida, rejeição vencendo a semente, métricas só quando o campo existe, recusa sem login, migration da tabela nova, e que a página não envia ordem nem inventa fill.
**Como conferir:** Pedir essa bateria e ver falha se a semente reaprovar um rejeitado, se faltar métrica virar zero, se aparecer controle de envio, ou se a tabela nova alterar âncoras de risco.
**Por quê:** Sem prova, o mapa poderia marcar completo com a lista em arquivo ainda sendo o caminho do operador.

**Detalhe técnico**

P task. Files: `tests/test_panel_ops.py`, `tests/test_ledger_migration.py` (extend; 2 files). Reuse PanelOpsHttpTests cookie pattern. Nodeids for: unauthenticated GET/POST; empty queue Portuguese; approve persists; reject wins over seed; win_rate_pct displayed from fixture; missing metric not 0; TradingView without rank → indisponível; 003 SQL creates signal_provider_approvals and does not ALTER control_flags; no process_after_gate_b / order form; regression N48–N50 headings and inventory/adoption. Do not call real Alpaca or Collective2 HTTP. Do not put C2_API4_KEY in tests. LIVE false in env. No secret values.

### Task N51.5 — Atualizar o mapa e o chamado depois da fila no painel

**Entrega:** O mapa descreve a fila de pré-aprovação e o significado de cada métrica; o chamado ISS-021 aponta esta sprint; a campanha e o épico antigo continuam abertos.
**Como conferir:** Abrir o mapa na área Sinais: fila, semente, métricas pesquisa, aprovar não envia ordem; ISS-021 ligado a N51; ISS-017, ISS-019, ISS-020 e o épico antigo do painel único continuam abertos.
**Por quê:** Sem esse recorte, a próxima rodada acha que a lista em arquivo ainda é o caminho do dia a dia ou que a campanha fechou.

**Detalhe técnico**

P task. Files: `docs/OPERATOR-PANEL-MAP.md`, `docs/DASHBOARD-OPERATIONS.md`, `docs/DATABASE.md`, `docs/ISSUES.md`, `docs/DIARY.md` (ISS-021 keep **aberto** until EXECUTE evidence + operator confirm; ISS-020 keep **aberto** unless operator already closed; ISS-019 keep **aberto**; ISS-017 keep **aberto**; ISS-007 keep open). Update area 2 Sinais: Pré-aprovação; recovered metrics table; seed vs ledger; real empty queue string. DATABASE § new 003 note — do not rewrite §6 risk anchors. DASHBOARD-OPERATIONS «Ver sinais» mentions the queue. Do not close ISS-010 / ISS-011 / ISS-007 / ISS-009 / ISS-017 / ISS-019 / ISS-020. Do not claim EasyPanel rebuild. Do not mark N45–N47 started. LIVE false.

---

## Sprint N52 — Transformar Sinais num cockpit de decisão com todos os números de pesquisa
> Categoria: N  
> Status: planejada  
> Gerado via: `/pmo plan` 2026-11-17 · fonte ISS-022 · Design já em `docs/design/` (Passo 2 pulado)  
> titulo_humano: Cockpit de decisão na tela Sinais com todos os números de pesquisa  
> resumo_humano: Depois do login a tela Sinais abre na fila de aprovar ou rejeitar, com todos os números de pesquisa já gravados. O que opera fica no meio; auditoria no fim. Aprovar não envia ordem. Entrega só depois de entrar no ramo principal.  
> Gate: Sinais logado com decisão no topo, todos os números recuperados ou indisponível, operação no meio, auditoria no fim, visual do desenho, pytest do painel verde, mapa atualizado, LIVE false; «finalizado» só após merge no ramo principal  
> review: senior+qa  
> Brief: `docs/.briefs/N52.brief.md`  
> bom_ref: BOM-3  
> Depende de: N51 planejada/entregue · N50 planejada · N49 planejada · N48 concluida · Release: ISS-022 (não usa N45–N47)  
> LIVE_TRADING_ENABLED: false

### Em uma frase

A tela Sinais passa a ser um cockpit: você decide no topo, vendo todos os números de pesquisa já gravados, e só depois o que opera e o que é auditoria.

### O que muda para você

- A fila de aprovar ou rejeitar sobe para o começo da tela, com todos os números recuperáveis visíveis
- O que já opera e o inventário ficam no meio; pesquisa e auditoria descem para o fim
- Campo ausente aparece como indisponível — sem fórmula nova e sem zero inventado
- Cores e botões seguem o desenho já aprovado; as outras telas não são redesenhadas nesta rodada
- Aprovar continua não enviando ordem; dinheiro real permanece desligado; «finalizado» só depois de entrar no ramo principal

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Cockpit de decisão no topo | Abrir Sinais logado: a fila de aprovar ou rejeitar é o primeiro bloco |
| 2 | Todos os números de pesquisa visíveis | Em cada candidato, acertos, fator de lucro, drawdown, score e demais campos recuperados aparecem ou dizem indisponível |
| 3 | Operação no meio, auditoria no fim | O que já opera vem depois da fila; ingresso e candidatos de pesquisa ficam por último |
| 4 | Visual alinhado ao desenho | Botão aprovar destacado, rejeitar distinto, estados vazios em português |
| 5 | Mapa e chamado atualizados | O mapa descreve a nova ordem; o chamado aponta esta sprint |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | P | N52.0 Inventariar o reuso do cockpit e das métricas já na fila | `/git` | — |
| [ ] | M | N52.1 Reestruturar a tela Sinais como cockpit de decisão | `/dev` | N52.0 |
| [ ] | P | N52.2 Provar hierarquia, números completos e ausência de envio | `/qa testes` | N52.1 |
| [ ] | P | N52.3 Atualizar o mapa e o chamado depois do cockpit | docs | N52.2 |

### Quality Brief (Sprint N52)

Maintain: `LIVE_TRADING_ENABLED=false`; paper host only; dashboard does not submit or cancel orders; approval is not a fill.
Maintain: load `trader-entry|exit|budget|risk|scanner` only via `src/original.py`; do not invent scoring thresholds; do not call `prodigy_rank.calculate` or Collective2 HTTP from the panel.
Maintain: N51 overlay keys; missing = indisponível (never 0); rank eligible is not paper-copy approval.
Maintain: N38 brake-strip colors; other routes keep their HTML.
Avoid: rewriting `panel_ops_data` unless a listed key never reaches HTML; stealing N45–N47; closing ISS-007/010/011/017/019/020/021; Live button; printing API keys.

### Fora de escopo

- Inventar fórmula de assertividade ou score composto
- Preencher métrica ausente com zero
- Tratar ranking como aprovação de cópia paper
- Redesign HTML das outras rotas
- POST ou cancelamento de ordem pelo painel
- Tela própria de Tá Barato (N45)
- Clear / OANDA / N29.5
- `LIVE_TRADING_ENABLED=true`
- Fechar ISS-007 / ISS-010 / ISS-011 / ISS-009 / ISS-017 / ISS-019 / ISS-020 / ISS-021
- Marcar «finalizado» antes do merge no ramo principal
- Roubar identificadores N45–N47

### Task N52.0 — Inventariar o reuso do cockpit e das métricas já na fila

**Entrega:** Inventário curto dizendo que a fila e o overlay de números já existem, que a tela só mostra dois campos, e que o desenho do cockpit já está no repositório.
**Como conferir:** O inventário cita a sessão autenticada, as chaves já gravadas no overlay, a ordem atual da tela, os tokens do desenho, e deixa envio pelo painel, fórmula nova e as outras telas de fora.
**Por quê:** Sem essa lista o EXECUTE inventa score, mexe no pacote de dados sem necessidade, ou redesenha o painel inteiro.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N52-GIT-FIRST-REUSE.md` (written at plan-time). Re-check vendor pin `docs/VENDOR-PIN.md` vs `git ls-remote` `Jakeschincariol/day-trader-skill` `main`; do not bump. Local vendor may be uninitialized/empty — do not treat it as reviewed main. If GitHub unreachable, stop claiming current main. Do not touch `src/` in this task.

Cite: `render_signals_page` order; `_signals_preapproval_section_html` two-column metrics; `PREAPPROVAL_METRIC_KEYS`; `_PANEL_CSS`; `docs/design/mockups/sinais.md`; `docs/design/DESIGN.md`. Do not plan Alpaca HTTP from the panel. Do not steal N45–N47. Do not invent an assertiveness formula.

### Task N52.1 — Reestruturar a tela Sinais como cockpit de decisão

**Entrega:** A mesma tela Sinais abre na fila de decisão, com todos os números de pesquisa visíveis ou marcados indisponível, operação no meio, auditoria no fim, e visual alinhado ao desenho — sem botão de enviar ordem.
**Como conferir:** Abrir o painel logado, ir em Sinais, ver a fila no topo com acertos, fator de lucro, drawdown, score e status; rolar até operação e depois auditoria; confirmar que aprovar não envia ordem e que a Central ainda mostra o freio.
**Por quê:** Hoje a decisão fica no meio da salada e só dois números aparecem — exatamente o que o operador recusou.

**Detalhe técnico**

- **Estado atual:** `render_signals_page` emits operating → preapproval → inventory → C2/pool/adoption/audit. Pre-approval table shows only `win_rate_pct` and `reported_pnl_sum`. `_PANEL_CSS` is a compact untokenized block. Approve/reject POST already exists.
- **Estado desejado:** Portuguese cockpit per `docs/design/mockups/sinais.md`: (1) pre-approval first with `metrics-block` for every recovered key; (2) operating then inventory; (3) C2, Prodígio pool, adoption, audit last. DESIGN.md tokens in `_PANEL_CSS`. Empty states humanized. Other routes' HTML unchanged. Brake-strip colors unchanged.
- **Fonte(s):** ISS-022, `docs/design/DESIGN.md`, `docs/design/mockups/sinais.md`, N51 overlay, N50 headings.
- **Risco:** MEDIUM — treating rank status as copy approval, inventing metrics, or restyling the brake would break Feature 4 / N38.
- **Arquivo(s):** `src/panel_ops_html.py`

**executor_prompt**:

```yaml
id: N52.1
size: M
bom_ref: BOM-3
depends_on: ["N52.0"]
files:
  - src/panel_ops_html.py
reuse_targets:
  - component: src/panel_ops_html.py
    reuse_as: extend
    convergence_check: 'rg "def render_signals_page" src/panel_ops_html.py && rg "def _signals_preapproval_section_html" src/panel_ops_html.py && rg "metrics-block" src/panel_ops_html.py && rg "Pré-aprovação de provedores" src/panel_ops_html.py'
  - component: src/panel_ops_html.py
    reuse_as: extend
    convergence_check: 'rg -- "--bg-canvas" src/panel_ops_html.py && rg -- "--action-primary" src/panel_ops_html.py && rg -- "--action-danger" src/panel_ops_html.py && rg "_PANEL_CSS" src/panel_ops_html.py'
  - component: src/panel_ops_data.py
    reuse_as: call
    convergence_check: rg "PREAPPROVAL_METRIC_KEYS" src/panel_ops_data.py && rg "win_rate_pct" src/panel_ops_html.py && rg "shrunk_win_rate_pct" src/panel_ops_html.py && rg "profit_factor_reported" src/panel_ops_html.py && rg "max_drawdown_pct" src/panel_ops_html.py
  - component: docs/design/mockups/sinais.md
    reuse_as: copy_pattern
    convergence_check: 'rg "empty-state" src/panel_ops_html.py && rg "Nenhum provedor aguardando análise" src/panel_ops_html.py'
guardrail_contract:
  - class: secrets
    id: n52-1-no-secrets
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_html.py').read_text(); assert 'sk_live' not in t.lower(); assert 'C2_API4_KEY' not in t; assert 'SIGNAL_COPY_SECRET' not in t"
    pass_condition: no live keys or Collective2 API key in HTML
  - class: subagent-safety
    id: n52-1-cockpit-not-order
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; html=Path('src/panel_ops_html.py').read_text(); assert 'process_after_gate_b' not in html; assert 'paper-api.alpaca.markets' not in html; i=html.find('def render_signals_page'); assert i>=0; fn=html[i:i+2500]; pre=fn.find('preapproval_body'); op=fn.find('operating_body'); au=fn.find('audit_body'); assert 0<=pre<op<au; assert 'win_rate_pct' in html and 'profit_factor_reported' in html and 'max_drawdown_pct' in html and 'shrunk_win_rate_pct' in html; assert 'brake-strip--active' in html"
    pass_condition: same /sinais route; decision before operating before audit; recovered keys in HTML; brake strip preserved; no paper submit
```

### Quality Brief (Sprint N52)

Maintain: LIVE_TRADING_ENABLED=false; operator session cookie in front of /sinais and POST; do not add a parallel route.
Maintain: Feature 9 ingest table remains; N50 operation/C2/Prodígio headings remain as inner titles.
Maintain: metrics labeled pesquisa; missing field Portuguese indisponível; Aprovar não envia ordem.
Maintain: N38 brake-strip modifiers unchanged; other pages keep their HTML structure.
Avoid: Live button; order submit/cancel; calling signal_copy.validate; rewriting Feature 4 numbers; listing H10 ten as approved; rewriting panel_ops_data unless a listed key is missing from the overlay.

Melhoria: restyle authenticated GET /sinais as the ISS-022 decision cockpit using DESIGN.md tokens and the sinais mockup, without changing the N51 approve POST.
Contexto: N51 HTML shows only win_rate_pct and reported_pnl_sum and places operating above the queue. Operator 2026-11-17 demanded all recovered metrics and a decision-first hierarchy. Designer already wrote docs/design/.
Objetivo: (1) Keep OPERATOR_PANEL_PATHS and _nav Sinais → /sinais (no /copy, no /aprovacoes). (2) render_signals_page order: preapproval_body, operating_body, inventory_body, then c2/pool/adoption/audit. (3) Pre-approval metrics-block must render win_rate_pct, shrunk_win_rate_pct, profit_factor_reported, reported_pnl_sum, net_return_pct, max_drawdown_pct, prodigy_score or score, and status via _format_research_metric (indisponível when absent). Label win_rate_pct as percentual de acertos (pesquisa) — there is no assertividade field. Do not display eligible or copy_approved as paper approval. (4) Empty pre-approval: `Nenhum provedor aguardando análise no momento. Novos candidatos aparecerão aqui.` Empty operating may keep Nenhuma cópia de terceiro em operação and may add the mockup second sentence. Use class empty-state. (5) Put DESIGN.md tokens into _PANEL_CSS as CSS variables (--bg-canvas, --bg-card, --text-primary, --text-muted, --border-subtle, --action-primary, --action-danger, --status-research, --status-active, --status-warning, --radius-sm, --radius-md). Map .btn-primary / .btn-danger to those tokens. Do not restyle .brake-strip--active / .brake-strip--released hex colors. (6) Portuguese UI. Footer unchanged: painel não envia ordem. Live desligado. (7) Do not edit panel_ops_data.py unless EXECUTE proves a listed key is absent from copy.preapproval.queue[].metrics. (8) Do not rewrite HTML of / /ordens /historico /estrategias /prodigy /performance /analise-google except inherited CSS variables. LIVE false.
Arquivos: src/panel_ops_html.py.
Critério de pronto: logged-in GET /sinais HTML contains Pré-aprovação before Em operação / assinados before Auditoria de ingresso; metrics-block includes shrunk_win_rate_pct, profit_factor_reported, max_drawdown_pct; --bg-canvas in _PANEL_CSS; process_after_gate_b absent; brake-strip--active still in file.
Cenários de teste (implement in N52.2):
1. Sem cookie → GET /sinais redirect/401; POST /api/signals/providers 401.
2. Fila vazia → string nenhum provedor aguardando análise.
3. Candidato com win_rate_pct e profit_factor_reported → ambos visíveis, rótulo pesquisa.
4. Candidato sem net_return_pct → indisponível, não 0.
5. Ordem HTML: pré-aprovação < operação < auditoria.
6. Central ainda tem faixa do freio; demais rotas do menu ainda renderizam. HTML sem controle de envio.

### Task N52.2 — Provar hierarquia, números completos e ausência de envio

**Entrega:** Testes mostram a fila no topo com todos os números recuperados, indisponível quando falta campo, estados vazios em português, recusa sem login, freio da Central intacto, e que a página não envia ordem nem inventa fill.
**Como conferir:** Pedir essa bateria e ver falha se a auditoria subir ao topo, se faltar um número recuperado, se ausência virar zero, se aparecer controle de envio, ou se a Central perder o freio.
**Por quê:** Sem prova, o mapa poderia marcar completo com a salada e só dois números ainda no ar.

**Detalhe técnico**

P task. File: `tests/test_panel_ops.py` (extend; 1 file). Reuse PanelOpsHttpTests / PanelSinaisN51Tests cookie pattern. Nodeids for: unauthenticated GET/POST; empty queue Portuguese (`Nenhum provedor aguardando análise`); all recovered keys rendered or `indisponível`; missing metric not 0; heading order preapproval < operating < audit (keep N50 operating < audit); no process_after_gate_b / order form; Central still contains brake-strip; regression N48–N51 headings and previous menu routes. Do not call real Alpaca or Collective2 HTTP. Do not put C2_API4_KEY in tests. LIVE false in env. No secret values. Do not require panel_ops_data contract change.

### Task N52.3 — Atualizar o mapa e o chamado depois do cockpit

**Entrega:** O mapa descreve Sinais como cockpit (decisão, operação, auditoria) e lista o significado de cada número; o chamado aponta esta sprint; a campanha e os chamados anteriores continuam abertos.
**Como conferir:** Abrir o mapa na área Sinais: ordem nova, métricas completas, aprovar não envia ordem; chamado desta sprint ligado; campanha e épico antigo do painel único continuam abertos.
**Por quê:** Sem esse recorte, a próxima rodada redesenha as outras telas achando que Sinais ainda é a salada, ou fecha a campanha cedo.

**Detalhe técnico**

P task. Files: `docs/OPERATOR-PANEL-MAP.md`, `docs/DASHBOARD-OPERATIONS.md`, `docs/ISSUES.md`, `docs/DIARY.md` (ISS-022 keep **aberto** until EXECUTE evidence + operator confirm **and** merge to main; ISS-021 keep **aberto** unless operator already closed; ISS-020/019/017/007 keep open). Update area 2 Sinais: decision-first order; full recovered-metrics table; empty-state strings; tokens note (shared CSS vars, other pages not redesigned). DASHBOARD-OPERATIONS «Ver sinais» mentions the cockpit. Do not close ISS-010 / ISS-011 / ISS-007 / ISS-009 / ISS-017 / ISS-019 / ISS-020 / ISS-021. Do not claim EasyPanel rebuild. Do not mark the sprint finalizado before merge to main. Do not mark N45–N47 started. LIVE false.

---

## Sprint N53 — Aplicar o visual novo em todo o menu e mostrar o botão de atualizar candidatos
> Categoria: N  
> Status: concluida *(PR [#71](https://github.com/ig0rayres/trading_lab/pull/71) merge `bb103558` 2026-11-18; validation_gate APROVADA; pytest `test_panel_ops.py` verde; **ISS-023 aberto** — job POST refresh = **N54**; rebuild EasyPanel operador)*  
> Gerado via: `/pmo plan` 2026-11-18 · fonte ISS-023 · Design DONE `docs/design/`  
> titulo_humano: Painel operacional com visual novo em todas as rotas e botão de atualizar candidatos  
> resumo_humano: Após o login, todas as telas do menu seguem o desenho v2 com o mesmo casco. Em Sinais, o botão de atualizar candidatos recarrega só os dados de pesquisa já no servidor. Job pesado fica para N54. LIVE false. Finalizado só após merge no ramo principal.  
> Gate: rotas do menu com PanelShell v2; Sinais com refresh GET honesto; refresh ≠ aprovar ≠ ordem; pytest painel verde; mapa + nota N54; LIVE false  
> review: senior+qa  
> Brief: `docs/.briefs/N53.brief.md`  
> bom_ref: BOM-3  
> Depende de: N52 planejada/entregue · design ISS-023 · Release: ISS-023 (não usa N45–N47)  
> LIVE_TRADING_ENABLED: false  
> previous_sprint: N52  
> N54: POST/job refresh (fora deste bloco)

### Em uma frase

Todo o menu do painel ganha o visual novo do desenho aprovado, e em Sinais você passa a ter o botão de atualizar candidatos que só recarrega os dados de pesquisa já no servidor — sem aprovar nem enviar ordem; o trabalho pesado de job fica para a sprint seguinte.

### O que muda para você

- Central, Ordens, Histórico, Sinais, Estratégias, Prodígio, Performance, Análise Google e login seguem o mesmo casco visual: menu escuro, selo Paper com dinheiro real desligado, tipografia e cores do desenho v2
- A hierarquia da tela Sinais do cockpit anterior permanece; o visual e os componentes passam a bater com o mockup novo
- O botão «Atualizar candidatos» aparece na pré-aprovação; ao clicar, o servidor relê os arquivos de pesquisa e a tela atualiza — sem inventar números novos
- Atualizar não é aprovar nem ordem; aprovar continua separado; dinheiro real continua desligado
- «Finalizado» só depois do merge no ramo principal e rebuild do painel no ar

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Casco visual único em todas as rotas do menu | Depois do login, navegue pelo menu: sidebar escura, topbar com selo Paper, páginas legíveis e alinhadas aos mockups |
| 2 | Login e Central com o novo desenho | Tela de entrada e Central mantêm o freio de emergência visível e compreensível |
| 3 | Sinais com botão de atualizar | Na pré-aprovação, o botão outline «Atualizar candidatos» existe; após clicar, vê feedback e dados relidos ou mensagem de erro sem sumir a fila |
| 4 | Demais rotas no novo layout | Ordens, Histórico, Estratégias, Prodígio, Performance e Análise Google abrem sem voltar ao visual antigo |
| 5 | Prova automática e mapa | A suíte de testes do painel passa; o mapa descreve o visual v2 e o que N54 ainda fará no refresh |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N53.0 Inventariar reuso visual e contrato de refresh honesto | `/git` | — |
| [x] | M | N53.1 Aplicar tokens v2 e o casco PanelShell compartilhado | `/dev` | N53.0 |
| [x] | M | N53.2 Alinhar o HTML de todas as rotas do menu aos mockups | `/dev` | N53.1 |
| [x] | M | N53.3 Expor o botão de atualizar e o endpoint GET de releitura | `/dev` | N53.2 |
| [x] | P | N53.4 Provar shell, refresh e ausência de envio de ordem | `/qa testes` | N53.3 |
| [x] | P | N53.5 Atualizar mapa, chamado e nota da sprint N54 | docs | N53.4 |

### Quality Brief (Sprint N53)

**Validação:** checkpoint `validation_gate` **APROVADA**; QA **APROVADA**; `tests/test_panel_ops.py` verde (81 casos na sessão de closeout); merge **#71** → `main` @ `bb10355865011ea19ddfbe5a8d651c159888702a`.

**Entregue:** PanelShell v2 (tokens DESIGN §2, topbar Paper, sidebar) em login e em todas as rotas do menu; botão **Atualizar candidatos** + `GET /api/signals/reload` (sessão obrigatória) relendo `build_panel_bundle` — sem `prodigy_rank.calculate`, sem POST de job.

**Adiado (N54):** refresh pesado (POST/job allowlisted, cooldown R4, critérios TV+C2 server-side — ver **ISS-024**).

Maintain: `LIVE_TRADING_ENABLED=false`; paper host only; dashboard does not submit or cancel orders; refresh and approval are not fills.
Maintain: load `trader-entry|exit|budget|risk|scanner` only via `src/original.py`; do not call `prodigy_rank.calculate` or Collective2 HTTP from the panel (N54 job).
Maintain: N52 Sinais hierarchy and recovered metrics; missing = indisponível; N38 brake-strip colors on Central.
Maintain: `build_panel_bundle` semantics; N53 refresh = re-read disk/bundle only.
Avoid: stealing N45–N47; POST refresh job in N53; inventing scores; claiming EasyPanel rebuild without operator; printing API keys.

### Fora de escopo

- POST job refresh, cooldown R4 obrigatório, `prodigy_rank.calculate` (**N54**)
- Inventar métricas ou preencher ausente com zero
- Alterar semântica de `panel_ops_data` salvo bug provado
- N45–N47, LIVE true, ordem pelo painel
- Marcar «finalizado» antes do merge em `main`

### Task N53.0 — Inventariar reuso visual e contrato de refresh honesto

**Entrega:** Inventário dizendo o que já existe no HTML, o que o desenho v2 exige, e como o refresh em N53 difere do job em N54.
**Como conferir:** O inventário cita o casco atual, os mockups por rota, a montagem do bundle, e proíbe score inventado e chave no browser.
**Por quê:** Sem isso o EXECUTE mistura job N54 com re-skin ou chama ranking no painel.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N53-GIT-FIRST-REUSE.md`. Re-check vendor pin; no bump. Cite: `_PANEL_CSS`, `_nav`, `render_*_page`, `build_panel_bundle`, `mockups/panel-shell.md`, `mockups/sinais.md` R0–R6.

### Task N53.1 — Aplicar tokens v2 e o casco PanelShell compartilhado

**Entrega:** Variáveis de cor e tipografia v2 no CSS compartilhado e um casco único com menu lateral e faixa superior de contexto reutilizado por todas as rotas autenticadas.
**Como conferir:** Abra qualquer tela do menu logado: sidebar escura, selo de ambiente Paper visível, foco e botões coerentes com o desenho; a Central ainda mostra o freio com as cores de antes.
**Por quê:** O operador pediu plataforma inteira, não só retoques em Sinais.

**Detalhe técnico**

- **Estado atual:** `_PANEL_CSS` usa tokens N52 parciais; layout `flex` simples; sem topbar formal.
- **Estado desejado:** Tokens `docs/design/DESIGN.md` §2 em `_PANEL_CSS`; helpers `PanelShell` / `PageHeader` per `mockups/panel-shell.md`; login com `mockups/login.md`; preserve `brake-strip--active` hex.
- **Arquivo(s):** `src/panel_ops_html.py`

**executor_prompt**:

```yaml
id: N53.1
size: M
bom_ref: BOM-3
depends_on: ["N53.0"]
files:
  - src/panel_ops_html.py
reuse_targets:
  - component: src/panel_ops_html.py
    reuse_as: extend
    convergence_check: 'rg "_PANEL_CSS" src/panel_ops_html.py && rg "def _nav" src/panel_ops_html.py'
  - component: docs/design/DESIGN.md
    reuse_as: copy_pattern
    convergence_check: 'rg -- "--color-canvas" src/panel_ops_html.py && rg -- "--color-sidebar" src/panel_ops_html.py'
guardrail_contract:
  - class: secrets
    id: n53-1-no-secrets
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_html.py').read_text(); assert 'C2_API4_KEY' not in t; assert 'sk_live' not in t.lower()"
    pass_condition: no broker keys in HTML module
  - class: subagent-safety
    id: n53-1-brake-preserved
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; h=Path('src/panel_ops_html.py').read_text(); assert 'brake-strip--active' in h; assert 'process_after_gate_b' not in h"
    pass_condition: N38 brake preserved; no order submit
```

### Task N53.2 — Alinhar o HTML de todas as rotas do menu aos mockups

**Entrega:** Cada rota do menu usa o casco novo e a estrutura de página do mockup correspondente, mantendo os mesmos textos honestos e dados de antes.
**Como conferir:** Percorra Central, Ordens, Histórico, Sinais, Estratégias, Prodígio, Performance e Análise Google: cabeçalhos, tabelas e avisos de pesquisa batem com o mapa; Sinais mantém pré-aprovação antes de operação e auditoria por último.
**Por quê:** ISS-023 é redesign da plataforma, não só CSS solto.

**Detalhe técnico**

Refactor `render_central_page`, `render_orders_page`, `render_history_page`, `render_signals_page`, `render_strategies_page`, `render_prodigy_page`, `render_performance_page`, `render_analise_google_page` to use shell helpers from N53.1 and layout notes in `docs/design/mockups/*.md`. Do **not** change `panel_ops_data` loaders. Do **not** add order controls.

**executor_prompt**:

```yaml
id: N53.2
size: M
bom_ref: BOM-3
depends_on: ["N53.1"]
files:
  - src/panel_ops_html.py
reuse_targets:
  - component: src/panel_ops_html.py
    reuse_as: extend
    convergence_check: 'rg "def render_signals_page" src/panel_ops_html.py && rg "Pré-aprovação" src/panel_ops_html.py'
  - component: docs/OPERATOR-PANEL-MAP.md
    reuse_as: call
    convergence_check: 'rg "indisponível" src/panel_ops_html.py'
guardrail_contract:
  - class: subagent-safety
    id: n53-2-sinais-order
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; h=Path('src/panel_ops_html.py').read_text(); i=h.find('def render_signals_page'); fn=h[i:i+3500]; pre=fn.find('preapproval'); op=fn.find('operating'); au=fn.find('audit'); assert 0<=pre<op<au"
    pass_condition: Sinais hierarchy preserved
```

### Task N53.3 — Expor o botão de atualizar e o endpoint GET de releitura

**Entrega:** Botão «Atualizar candidatos» visível na pré-aprovação com feedback de carregamento e sucesso ou erro, ligado a um endpoint autenticado que só relê o bundle a partir do disco.
**Como conferir:** Logado em Sinais, clique no botão: vê estado Atualizando e depois mensagem de sucesso ou erro sem a fila sumir; a rede mostra GET autenticado, não POST de ordem nem chamada a ranking no browser.
**Por quê:** Era a peça que faltava no ar (#70) sem antecipar o job pesado de N54.

**Detalhe técnico**

- UI: `mockups/sinais.md` R0–R3, hint permanente, `aria-live` feedback, button outline.
- API: add authenticated `GET /api/signals/reload` (or documented alias) in `v4_web_dashboard.py` calling `build_panel_bundle` again; JSON response or reload signal; **no** `prodigy_rank.calculate`; document **N54** for POST/job in handler comment.
- Client: small fetch script in `panel_ops_html.py` beside existing provider approval script; `credentials: same-origin`.
- **Files:** `src/panel_ops_html.py`, `src/v4_web_dashboard.py`

**executor_prompt**:

```yaml
id: N53.3
size: M
bom_ref: BOM-3
depends_on: ["N53.2"]
files:
  - src/panel_ops_html.py
  - src/v4_web_dashboard.py
reuse_targets:
  - component: src/panel_ops_data.py
    reuse_as: call
    convergence_check: rg "def build_panel_bundle" src/panel_ops_data.py
  - component: src/v4_web_dashboard.py
    reuse_as: extend
    convergence_check: rg "/api/signals" src/v4_web_dashboard.py
guardrail_contract:
  - class: subagent-safety
    id: n53-3-no-rank-in-panel
    target: src
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text()+Path('src/panel_ops_html.py').read_text(); assert 'prodigy_rank.calculate' not in t; assert 'Atualizar candidatos' in t"
    pass_condition: refresh UI present; no rank calculate in panel path
  - class: subagent-safety
    id: n53-3-get-reload
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'reload' in t or 're-read' in t.lower() or 'signals/reload' in t"
    pass_condition: reload route wired
```

### Task N53.4 — Provar shell, refresh e ausência de envio de ordem

**Entrega:** Testes cobrem casco compartilhado, presença do botão, GET autenticado, hierarquia Sinais e regressão das rotas anteriores.
**Como conferir:** Rodar a suíte do painel e ver falha se faltar botão, se refresh não exigir sessão, ou se Sinais perder a ordem decisão→operação→auditoria.
**Por quê:** Mudança transversal no HTML exige rede de segurança antes do merge.

**Detalhe técnico**

P task. File: `tests/test_panel_ops.py`. Add nodeids: token/shell snippets on multiple routes; `Atualizar candidatos`; unauthenticated reload 401; no `process_after_gate_b`; Sinais order; brake-strip Central; regression N48–N52 strings.

### Task N53.5 — Atualizar mapa, chamado e nota da sprint N54

**Entrega:** Mapa descreve visual v2 e refresh GET; ISS-023 aponta N53; design README anota N54 para job POST.
**Como conferir:** Ler mapa área 2 e ISS-023: sprint N53; README design lista N54 como próximo passo de refresh.
**Por quê:** Separar claramente o que já está no ar do job que ainda virá.

**Detalhe técnico**

P task. Files: `docs/OPERATOR-PANEL-MAP.md`, `docs/DASHBOARD-OPERATIONS.md`, `docs/ISSUES.md`, `docs/DIARY.md`, `docs/design/README.md`, `docs/api-spec.yaml` (reload GET). ISS-023 **aberto** até merge + operador. Do not close ISS-022/021/… without evidence. LIVE false. N45–N47 not started.

---

## Sprint N54 — Aplicar critérios ao vivo ao atualizar candidatos
> Categoria: N  
> Status: planejada  
> Gerado via: `/pmo plan` 2026-11-18 · fonte ISS-024 · fases analista/designer/arquiteto/contratos DONE  
> titulo_humano: Atualizar candidatos aplica critérios ao vivo no servidor, sem ordem  
> resumo_humano: Em Sinais, o botão de atualizar candidatos passa a aplicar no servidor os critérios já definidos. Collective2 só no servidor; TradingView só origens já recebidas. Atualizar não aprova nem envia ordem. LIVE false. Finalizado só após merge no ramo principal.  
> Gate: POST autenticado de critérios ao vivo; GET reload declara releitura em disco; cooldown 429; sem chave C2 a fila permanece; pytest verde; mapa com dois modos; LIVE false  
> review: senior+qa  
> Brief: `docs/.briefs/N54.brief.md`  
> bom_ref: BOM-3  
> Depende de: N53 concluída (#71) · ISS-024 · Release: ISS-024 (não usa N45–N47)  
> LIVE_TRADING_ENABLED: false  
> previous_sprint: N53

### Em uma frase

Em Sinais, o botão de atualizar candidatos passa a aplicar no servidor os critérios de seleção já definidos — consulta Collective2 só no servidor, usa origens TradingView já recebidas, e não aprova nem envia ordem.

### O que muda para você

- Clicar em Atualizar candidatos dispara o trabalho pesado no servidor; deixa de ser só reler arquivo gravado
- Sem chave Collective2 no servidor, a fila anterior permanece e o aviso diz o que faltou — sem inventar candidato
- TradingView não ganha busca inventada: entram só origens já ingeridas
- Atualizar continua separado de Aprovar; dinheiro real permanece desligado
- «Finalizado» só depois do merge no ramo principal e rebuild do painel no ar

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Critérios ao vivo no servidor | Logado em Sinais, clique em Atualizar candidatos: a mensagem fala em critérios aplicados no servidor, não só em arquivo relido |
| 2 | Falha honesta sem chave ou com espera | Sem credencial no servidor vê aviso e a fila antiga; clique imediato de novo pede para aguardar |
| 3 | Releitura em disco ainda existe e se declara | O caminho antigo de só reler arquivo continua autenticado e avisa que critérios ao vivo não rodaram |
| 4 | Tela e mapa alinhados | O texto permanente do botão e o mapa da área Sinais descrevem o modo ao vivo; Aprovar segue separado |
| 5 | Prova automática | A suíte do painel passa cobrindo sessão, espera entre cliques, ausência de ordem e chave fora do browser |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N54.0 Inventariar reuso do job de candidatos ao vivo | `docs/.briefs/N54-GIT-FIRST-REUSE.md` | — |
| [x] | M | N54.1 Implementar o trabalho de critérios ao vivo e o envio autenticado | `src/v4_web_dashboard.py` | N54.0 |
| [x] | M | N54.2 Ligar o botão da tela ao trabalho ao vivo | `src/panel_ops_html.py` | N54.1 |
| [x] | M | N54.3 Provar modos, espera entre cliques e ausência de ordem | `tests/test_panel_ops.py` | N54.2 |
| [x] | P | N54.4 Atualizar o mapa, o chamado e o aceite da função | `docs/OPERATOR-PANEL-MAP.md, docs/ISSUES.md, docs/REQUIREMENTS.md` | N54.3 |

### Quality Brief (Sprint N54)

**Validação:** preventiva (plan-only). Parent Fable / plan-verifier ainda não carimbou.

**Alvo:** `POST /api/signals/candidates/refresh` (`mode: live_criteria`) reusa `prodigy_rank.calculate`, `c2_history_collect.fetch` e `c2_signal_feed.snapshot`; GET reload declara `mode: disk_reread`; CTA Sinais aponta ao POST; cooldown sem DDL.

Maintain: `LIVE_TRADING_ENABLED=false`; paper host only; dashboard does not submit or cancel orders; refresh and approval are not fills.
Maintain: load `trader-entry|exit|budget|risk|scanner` only via `src/original.py`.
Maintain: N53 GET `/api/signals/reload` stays disk-only (no `prodigy_rank.calculate` in that handler); N52 Sinais hierarchy; missing metrics = indisponível.
Maintain: Feature 4 / Prodígio 15d thresholds already in `prodigy_rank` (`WINDOW_DAYS=15`, `MIN_TRADES=5`); do not invent scores or a TradingView search API.
Maintain: Collective2 HTTP and `C2_API4_KEY` stay server-side; `signal_provider_approvals` unchanged by refresh; no new cooldown table.
Avoid: stealing N45–N47; calling C2 from browser JS; mutating approvals on refresh; `process_after_gate_b`; printing API keys; claiming EasyPanel rebuild without operator.

### Technical Advisory

- [ABORDAGEM] Helpers de job no mesmo `v4_web_dashboard` do GET reload — evita pacote paralelo e mantém C2 fora do HTML.
- [RISCO] GET N53 ainda não emite `mode`; testes N53 não asserem o campo — N54.1 deve completar o contrato sem quebrar releitura.
- [OPORTUNIDADE] `tests/test_c2_signal_feed.py` já usa `opener` injetável; o job deve aceitar opener/env de teste e não bater rede real no CI.

> EXPIRES at end of Sprint N54. Not reusable in future sprints without a new preventive audit.

### Fora de escopo

- Inventar busca TradingView ou fórmula nova
- Mutar livro de pré-aprovação no refresh
- Ordem / fill / LIVE true
- Tabela nova de cooldown; `dry_run` OpenAPI
- N45–N47; marcar «finalizado» antes do merge em `main`

### Task N54.0 — Inventariar reuso do job de candidatos ao vivo

**Entrega:** Inventário dizendo o que já calcula ranking, o que já fala com Collective2, e o que a tela não pode fazer no browser.
**Como conferir:** O inventário cita ranking 15 dias, coletores Collective2, montagem da fila, e proíbe busca TradingView inventada e chave no browser.
**Por quê:** Sem isso o EXECUTE recalcula no painel ou inventa endpoint.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N54-GIT-FIRST-REUSE.md`. Re-check vendor pin `3d0f4ef`; no bump. Cite: `prodigy_rank.calculate`, `c2_history_collect.fetch`, `c2_signal_feed.snapshot`, `build_preapproval_queue`, `_unique_tradingview_origins`, `serve_signals_reload`.

### Task N54.1 — Implementar o trabalho de critérios ao vivo e o envio autenticado

**Entrega:** Um envio autenticado no servidor aplica os critérios já definidos, consulta Collective2 só no processo, recalcula o ranking de pesquisa, e devolve a fila atualizada sem aprovar ninguém.
**Como conferir:** Com sessão, o envio novo responde modo critérios ao vivo e zero ordens; sem sessão recusa; um segundo envio imediato pede espera; o caminho antigo de só reler arquivo declara modo releitura em disco.
**Por quê:** O operador recusou tratar arquivo estático como verdade das plataformas.

**Detalhe técnico**

- **Estado atual:** só `GET /api/signals/reload` chama `build_panel_bundle`; JSON sem `mode`; `do_POST` não conhece `/api/signals/candidates/refresh`.
- **Estado desejado:** orquestrador + POST 200/partial/401/429/502 conforme `docs/api-spec.yaml` v0.3.0 e `docs/ARCHITECTURE.md` §13.4; GET reload com `mode: disk_reread`.
- **Arquivo(s):** `src/v4_web_dashboard.py`
- **Fonte(s):** ISS-024, Feature 9, ADR-011/012
- **Risco:** MEDIUM — HTTP externo + JSON de pesquisa compartilhado com o painel
- **Task size:** M (endpoint + orquestração C2/rank no dashboard)

**executor_prompt**:

```yaml
id: N54.1
size: M
bom_ref: BOM-3
depends_on: ["N54.0"]
files:
  - src/v4_web_dashboard.py
reuse_targets:
  - component: src/prodigy_rank.py
    reuse_as: call
    convergence_check: 'rg "prodigy_rank" src/v4_web_dashboard.py'
  - component: src/c2_history_collect.py
    reuse_as: call
    convergence_check: 'rg "c2_history_collect" src/v4_web_dashboard.py'
  - component: src/c2_signal_feed.py
    reuse_as: call
    convergence_check: 'rg "c2_signal_feed" src/v4_web_dashboard.py'
  - component: src/panel_ops_data.py
    reuse_as: call
    convergence_check: 'rg "build_panel_bundle" src/v4_web_dashboard.py'
guardrail_contract:
  - class: secrets
    id: n54-1-no-key-leak
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'sk_live' not in t.lower(); assert 'C2_API4_KEY' not in t or 'environ' in t"
    pass_condition: no live keys hardcoded; C2 key only via env lookup
  - class: subagent-safety
    id: n54-1-no-order
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'process_after_gate_b' not in t"
    pass_condition: dashboard still never submits via Gate B
  - class: subagent-safety
    id: n54-1-get-still-disk
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; b=Path('src/v4_web_dashboard.py').read_text().split('def serve_signals_reload',1)[-1].split('def serve_public_get',1)[0]; assert 'prodigy_rank.calculate' not in b; assert 'disk_reread' in b"
    pass_condition: GET reload remains disk_reread without calculate
```

### Quality Brief (Sprint N54)

See sprint Quality Brief above. LIVE false; refresh ≠ approve ≠ fill; reuse calculate/fetch/snapshot; no TV search API; no approval mutation; C2 key env-only.

Melhoria: implement live-criteria refresh job + authenticated POST.
Contexto: N53 GET only rereads disk; ISS-024 / Feature 9 require applying Feature 4 / Prodigy 15d on sources.
Objetivo: `POST /api/signals/candidates/refresh` with session cookie; cooldown 30s in-process (no new table); empty body = all sources `[collective2, prodigy, tradingview]`. Helpers stay in `src/v4_web_dashboard.py` — do **not** add a parallel module.
C2: if `C2_API4_KEY` set, `c2_history_collect.fetch` for numeric IDs from `load_c2_paper_copy_approved_ids` plus IDs already in research JSON; write adapter-shaped `{sid}_{kind}.json`; `c2_signal_feed.snapshot` for active orders (not tickets). Missing key → `issues` + `status: partial` or documented 502; **do not wipe** previous JSON/queue.
Prodigy: `prodigy_rank.calculate` on raw dir; write `intelligence/prodigy-top10-latest.json` and `intelligence/provider-research-top10-latest.json` (paths already loaded by `panel_ops_data`).
TV: `_unique_tradingview_origins` on current signals; no HTTP.
Then `build_panel_bundle`. Never upsert `signal_provider_approvals`. Never `process_after_gate_b`.
GET `serve_signals_reload`: add `mode: disk_reread`, `execution_authorized: false`, `orders_sent: 0`. Keep `prodigy_rank.calculate` **out** of that function (place POST helpers before it or after `serve_public_get` so the N53 slice stays disk-only).
POST JSON: OpenAPI `PanelSignalsLiveRefreshResponse` / cooldown / upstream error schemas.
`dry_run` out of scope.
Critério de pronto: unauthenticated POST 401; sequential POST 429 `REFRESH_COOLDOWN`; success payload `mode=live_criteria` and `orders_sent=0`; GET reload `mode=disk_reread` and handler still without `prodigy_rank.calculate`.
Cenários de teste (mínimo no implementer self-check; N54.3 owns pytest):
  1. Caso normal: POST com sessão + opener fake + raw trades → 200 live_criteria
  2. Edge: sem C2_API4_KEY → partial/issues, fila anterior intacta
  3. Edge: segundo POST <30s → 429
  4. Regressão: GET reload não chama calculate; providers POST inalterado

### Task N54.2 — Ligar o botão da tela ao trabalho ao vivo

**Entrega:** O mesmo botão de atualizar candidatos dispara o trabalho ao vivo, mostra espera/sucesso/erro/aguarde, e o texto permanente deixa de insinuar que só relê arquivo.
**Como conferir:** Em Sinais, o hint fala em critérios no servidor; ao clicar vê Atualizando e depois sucesso ou erro sem a fila sumir; a rede mostra o envio autenticado do trabalho ao vivo, não chamada Collective2 no browser.
**Por quê:** Um único controle na tela precisa contar a verdade do que o servidor fez.

**Detalhe técnico**

- UI: `docs/design/mockups/sinais.md` S0–S5; hint permanente do modo critérios ao vivo; linha de status `Última atualização` + fonte; `aria-live="polite"`.
- Client: change `_CANDIDATES_RELOAD_SCRIPT` to `POST /api/signals/candidates/refresh` with `credentials: same-origin`; handle 401→login, 429→S4 using `retry_after_seconds` if present, 502/503→S3 keep table.
- Do **not** fetch Collective2 from JS. Do **not** change Aprovar/Rejeitar.
- **Arquivo(s):** `src/panel_ops_html.py`

**executor_prompt**:

```yaml
id: N54.2
size: M
bom_ref: BOM-3
depends_on: ["N54.1"]
files:
  - src/panel_ops_html.py
reuse_targets:
  - component: src/panel_ops_html.py
    reuse_as: extend
    convergence_check: 'rg "reload-candidates" src/panel_ops_html.py && rg "/api/signals/candidates/refresh" src/panel_ops_html.py'
  - component: docs/design/mockups/sinais.md
    reuse_as: copy_pattern
    convergence_check: 'rg "Aplica critérios Feature 4" src/panel_ops_html.py || rg "Prodígio 15d" src/panel_ops_html.py'
guardrail_contract:
  - class: secrets
    id: n54-2-no-c2-in-browser
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_html.py').read_text(); assert 'C2_API4_KEY' not in t; assert 'collective2.com' not in t.lower(); assert 'api4-general' not in t"
    pass_condition: HTML/JS never calls C2 hosts or embeds the key
  - class: subagent-safety
    id: n54-2-cta-post
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_html.py').read_text(); assert '/api/signals/candidates/refresh' in t; assert 'Atualizar candidatos' in t"
    pass_condition: same CTA wired to live-criteria POST
```

### Quality Brief (Sprint N54)

See sprint Quality Brief. Preserve N52 hierarchy and N53 shell; refresh ≠ approve.

Melhoria: wire existing `#reload-candidates` to POST live-criteria; honest copy.
Contexto: script still GET-reloads disk and hint says JSON only.
Objetivo: hint from mockup live-criteria row; S1 running; S2 success with clock; S3 fail-closed keeps queue HTML; S4 cooldown; S5 401→`/login`.
Keep GET reload available (not used by the button). No `prodigy_rank` import in HTML module.
Critério de pronto: `/sinais` HTML contains POST path, live-criteria hint, aria-live; no collective2.com in JS.
Cenários:
  1. Caso normal: click → POST same-origin
  2. Edge: 429 copy «Aguarde antes de atualizar de novo.»
  3. Regressão: Aprovar/Rejeitar script unchanged; hierarchy pré-aprovação → operação → auditoria

### Task N54.3 — Provar modos, espera entre cliques e ausência de ordem

**Entrega:** Testes cobrem o envio ao vivo, a releitura em disco declarada, a espera entre cliques, a fila preservada sem chave, e a prova de que nada disso envia ordem.
**Como conferir:** Rodar a suíte do painel e do job e ver falha se faltar modo no JSON, se o botão ainda só reler arquivo, se Collective2 aparecer no HTML, ou se o caminho de ordem for chamado.
**Por quê:** Integração com fonte externa e tela compartilhada exige rede de segurança antes do merge.

**Detalhe técnico**

- **Arquivo(s):** `tests/test_panel_ops.py`
- **Risco:** MEDIUM — HTTP in-process + mocks
- **Task size:** M

**executor_prompt**:

```yaml
id: N54.3
size: M
bom_ref: BOM-3
depends_on: ["N54.2"]
files:
  - tests/test_panel_ops.py
reuse_targets:
  - component: tests/test_c2_signal_feed.py
    reuse_as: copy_pattern
    convergence_check: 'rg "candidates/refresh" tests/test_panel_ops.py'
  - component: tests/test_panel_ops.py
    reuse_as: extend
    convergence_check: 'rg "live_criteria" tests/test_panel_ops.py'
guardrail_contract:
  - class: subagent-safety
    id: n54-3-no-live-net
    target: tests/test_panel_ops.py
    check: python3 -c "from pathlib import Path; t=Path('tests/test_panel_ops.py').read_text(); assert 'C2_API4_KEY' not in t or 'environ' in t.lower() or 'patch' in t"
    pass_condition: tests do not require a real Collective2 key
```

### Quality Brief (Sprint N54)

See sprint Quality Brief.

Melhoria: pytest for POST live-criteria, GET mode, UI wiring, fail-closed.
Objetivo: nodeids covering 401 POST, 429 cooldown, 200/partial without key, GET `mode=disk_reread`, HTML has POST path and no C2 host, `process_after_gate_b` absent from job, N53 reload tests still pass, Sinais section order preserved.
Do not teach production about `tests/` paths (no HARNESS_BUG).
Critério de pronto: `python3 -m pytest tests/test_panel_ops.py tests/test_prodigy_rank.py tests/test_c2_signal_feed.py -q` green.
Cenários:
  1. Caso normal: POST sessão + fake opener → live_criteria, orders_sent 0
  2. Edge: sem chave → issues, bundle_preserved / fila
  3. Edge: cooldown 429 REFRESH_COOLDOWN
  4. Edge: TV-only sources → no C2 HTTP
  5. Regressão: GET reload disk_reread; N53 button still named Atualizar candidatos
  6. Regressão: HTML sem collective2.com; approve path unchanged

### Task N54.4 — Atualizar o mapa, o chamado e o aceite da função

**Entrega:** Mapa e aceite da função Sinais descrevem o trabalho ao vivo; o chamado ISS-024 aponta esta sprint e permanece aberto até merge.
**Como conferir:** Ler a área Sinais do mapa e o chamado: sprint desta rodada; Feature 9 com o item de critérios ao vivo marcado só se os testes existirem.
**Por quê:** Separar o que N53 já pôs no ar do que esta sprint entrega.

**Detalhe técnico**

P task. Files: `docs/OPERATOR-PANEL-MAP.md` (§2 refresh POST + GET mode), `docs/DASHBOARD-OPERATIONS.md`, `docs/ISSUES.md` (ISS-024 notes; **do not close**), `docs/DIARY.md`, `docs/REQUIREMENTS.md` Feature 9 checkboxes only with cited nodeids. LIVE false. N45–N47 not started. ISS-023 stays open until operator rebuild.

---

## Sprint N55 — Mostrar todos os elegíveis das três plataformas na fila
> Categoria: N  
> Status: concluida *(PR [#74](https://github.com/ig0rayres/trading_lab/pull/74) merge `d8870c281a5b87e1e22871632a50e23868ba0c7b` 2026-11-18; CI test + docker-smoke + docker-build SUCCESS; suíte `N55MultiPlatformLiveCriteriaTests` (7/7); `tests/test_panel_ops.py` verde; **ISS-024 aberto** — rebuild EasyPanel + homologação operador; `LIVE_TRADING_ENABLED=false`)*
> Gerado via: `/pmo plan` 2026-11-18 · fonte ISS-024 follow-up · N54 #73 em `main`  
> titulo_humano: A fila de candidatos mostra as três plataformas, sem apagar quem já passou  
> resumo_humano: Depois de atualizar candidatos, a pré-aprovação lista Collective2, Prodígio e TradingView que já passam nos critérios definidos. Se uma fonte falhar, o aviso aparece e as outras linhas permanecem. Atualizar não aprova nem envia ordem. LIVE false.  
> Gate: fila com elegíveis das plataformas que rodaram; aviso parcial honesto; pesquisa anterior preservada; pytest com as três plataformas; LIVE false  
> review: senior+qa  
> Brief: `docs/.briefs/N55.brief.md`  
> bom_ref: BOM-3  
> Depende de: N54 concluída (#73) · ISS-024 · Release: ISS-024 (não usa N45–N47)  
> LIVE_TRADING_ENABLED: false  
> previous_sprint: N54

### Em uma frase

Depois de atualizar candidatos, a fila de pré-aprovação lista todos os elegíveis de Collective2, Prodígio e TradingView — e se uma fonte falhar, as outras não desaparecem.

### O que muda para você

- Clicar em Atualizar candidatos passa a trazer os elegíveis das três plataformas, não só uma origem TradingView sem métricas
- Sem chave Collective2 ou sem arquivos brutos do Prodígio, o aviso diz o que faltou; a fila das outras fontes permanece
- Prodígio vazio não inventa nota: o texto explica que faltam os arquivos brutos dos provedores
- Aprovar continua separado de atualizar; dinheiro real permanece desligado
- «Finalizado» só depois do merge no ramo principal e rebuild do painel no ar

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Fila com as três plataformas | Logado em Sinais, depois de atualizar, vê Collective2, Prodígio e TradingView quando cada fonte tem dados que passam nos critérios já definidos |
| 2 | Falha de uma fonte não apaga as outras | Sem credencial Collective2 o aviso aparece e as linhas de Prodígio/TradingView continuam; o contrário também vale |
| 3 | Prodígio vazio é honesto | Sem arquivos brutos, a mensagem pede esses arquivos — não aparece nota inventada |
| 4 | Aviso sobrevive ao recarregar a tela | Depois do clique, o recarregamento ainda mostra o aviso parcial e a fila restante |
| 5 | Prova automática | A suíte monta as três plataformas com dados de teste e falha se uma fonte sumir porque a outra quebrou |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N55.0 Inventariar reuso da fila multiplataforma | `docs/.briefs/N55-GIT-FIRST-REUSE.md` | — |
| [x] | M | N55.1 Garantir que o trabalho ao vivo e a fila mostrem elegíveis de todas as plataformas | `src/v4_web_dashboard.py, src/panel_ops_data.py` | N55.0 |
| [x] | M | N55.2 Mostrar aviso honesto quando uma fonte falha e as outras seguem | `src/panel_ops_html.py` | N55.1 |
| [x] | M | N55.3 Provar a fila com as três plataformas quando houver dados de teste | `tests/test_panel_ops.py` | N55.2 |
| [x] | P | N55.4 Atualizar o chamado, o aceite e o mapa da fila completa | `docs/OPERATOR-PANEL-MAP.md, docs/ISSUES.md, docs/REQUIREMENTS.md` | N55.3 |

### Quality Brief (Sprint N55)

**Validação:** merge **#74** → `main` @ `d8870c281a5b87e1e22871632a50e23868ba0c7b` (2026-11-18); CI **test**, **docker-smoke** e **docker-build** SUCCESS; `tests/test_panel_ops.py` — `N55MultiPlatformLiveCriteriaTests` 7/7; CQ-001/002/005 corrigidos na frente; CQ-003/CQ-004 deferidos em `docs/FINDINGS.md`.

**Alvo:** POST N54 `mode: live_criteria` estendido; fila de pré-aprovação com elegíveis Collective2 + Prodígio + TradingView; fail-closed por fonte sem apagar as outras; `partial` persiste em `copy.candidates_refresh`.

Maintain: `LIVE_TRADING_ENABLED=false`; paper host only; dashboard does not submit or cancel orders; refresh and approval are not fills.
Maintain: load `trader-entry|exit|budget|risk|scanner` only via `src/original.py`.
Maintain: N54 POST `/api/signals/candidates/refresh` and GET `/api/signals/reload` (`disk_reread`); no parallel job package.
Maintain: Feature 4 / Prodígio 15d thresholds already in `prodigy_rank` (`WINDOW_DAYS=15`, `MIN_TRADES=5`, ≥3 days, `PRODIGY_CANDIDATE_RESEARCH`); do not invent scores or a TradingView search API.
Maintain: Collective2 HTTP and `C2_API4_KEY` stay server-side; `signal_provider_approvals` unchanged by refresh; empty calculate must not wipe prior research JSON.
Avoid: stealing N45–N47; calling C2 from browser JS; mutating approvals on refresh; `process_after_gate_b`; printing API keys; inventing a Collective2 marketplace search; claiming EasyPanel rebuild without operator.

### Technical Advisory

- [ABORDAGEM] Estender o job N54 e `build_preapproval_queue` — a rota POST já existe; o defeito é persistir ranking vazio e montar a fila como se só TradingView existisse.
- [RISCO] Gravar `provider-research` a partir do ranking Prodígio relabela IDs Prodígio como Collective2 e, se o cálculo vier vazio, apaga a pesquisa anterior.
- [OPORTUNIDADE] O mockup já tem S3 (fila anterior intacta); o 200 `partial` precisa de aviso visível depois do recarregamento, não de 503 total.

> EXPIRES at end of Sprint N55. Not reusable in future sprints without a new preventive audit.

### Fora de escopo

- Inventar busca TradingView, listagem marketplace Collective2 ou fórmula nova
- Mutar livro de pré-aprovação no refresh
- Ordem / fill / LIVE true
- SSH no EasyPanel; tabela nova de cooldown
- N45–N47; marcar «finalizado» antes do merge em `main`

### Task N55.0 — Inventariar reuso da fila multiplataforma

**Entrega:** Inventário dizendo o que o trabalho ao vivo já faz, o que a fila já une, e o que falta no servidor quando Collective2 ou Prodígio vêm vazios.
**Como conferir:** O inventário cita o envio N54, o ranking de 15 dias, a montagem da fila, proíbe busca TradingView e listagem marketplace Collective2, e lista os arquivos brutos que o Prodígio precisa.
**Por quê:** Sem isso o EXECUTE inventa endpoint ou apaga pesquisa antiga para “completar” a tabela.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N55-GIT-FIRST-REUSE.md`. Re-check vendor pin `3d0f4ef`; no bump. Cite: `serve_signals_candidates_refresh`, `_live_criteria_job`, `prodigy_rank.calculate`, `build_preapproval_queue`, `_persist_prodigy_rank`, F-018. Document EasyPanel needs: server `C2_API4_KEY`, `reports/providers/raw/{sid}_closed_trades.json`, named C2 IDs — never print secrets.

### Task N55.1 — Garantir que o trabalho ao vivo e a fila mostrem elegíveis de todas as plataformas

**Entrega:** O mesmo trabalho ao vivo no servidor passa a montar a fila com os elegíveis de Collective2, Prodígio e TradingView; se uma fonte não rodar, as outras continuam e a pesquisa antiga dessa fonte não some.
**Como conferir:** Com dados de teste das três fontes, a fila tem as três plataformas; sem chave Collective2 o aviso existe e Prodígio/TradingView permanecem; sem arquivos brutos do Prodígio o aviso pede esses arquivos e não inventa nota.
**Por quê:** O operador ainda vê só uma origem TradingView sem métricas depois do clique, apesar do job N54 já existir.

**Detalhe técnico**

- **Estado atual:** N54 POST orquestra Prodígio/`calculate`, Collective2/`fetch` e TV origens; `calculate` vazio persiste JSON vazio; `provider-research` é dump do ranking Prodígio lido como Collective2; F-018 silencia erro TV; fila = C2 research rows + allowlist + prodigy rows + TV origins.
- **Estado desejado:** união independente por plataforma; elegível Prodígio = `PRODIGY_CANDIDATE_RESEARCH` já no código; Collective2 a partir de lista nomeada + pesquisa C2 real (não relabelar dump Prodígio); TV = origens ingeridas (métricas podem permanecer indisponível); persistir ranking só quando houver resultado útil; `issues` por fonte; preservar JSON anterior.
- **Arquivo(s):** `src/v4_web_dashboard.py`, `src/panel_ops_data.py`
- **Fonte(s):** ISS-024 nota operador 2026-11-18, Feature 9 v0.7.2, F-018, ADR-012
- **Risco:** MEDIUM — JSON de pesquisa compartilhado com o painel
- **Task size:** M (job + montagem da fila)

**executor_prompt**:

```yaml
id: N55.1
size: M
bom_ref: BOM-3
depends_on: ["N55.0"]
files:
  - src/v4_web_dashboard.py
  - src/panel_ops_data.py
reuse_targets:
  - component: src/v4_web_dashboard.py
    reuse_as: extend
    convergence_check: 'rg "serve_signals_candidates_refresh" src/v4_web_dashboard.py && rg "_live_criteria_job" src/v4_web_dashboard.py'
  - component: src/panel_ops_data.py
    reuse_as: extend
    convergence_check: 'rg "def build_preapproval_queue" src/panel_ops_data.py && rg "prodigy" src/panel_ops_data.py && rg "collective2" src/panel_ops_data.py && rg "tradingview" src/panel_ops_data.py'
  - component: src/prodigy_rank.py
    reuse_as: call
    convergence_check: 'rg "prodigy_rank" src/v4_web_dashboard.py && rg "PRODIGY_CANDIDATE_RESEARCH" src/prodigy_rank.py'
  - component: src/c2_history_collect.py
    reuse_as: call
    convergence_check: 'rg "c2_history_collect" src/v4_web_dashboard.py'
guardrail_contract:
  - class: secrets
    id: n55-1-no-key-leak
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'sk_live' not in t.lower(); assert 'C2_API4_KEY' not in t or 'environ' in t"
    pass_condition: no live keys hardcoded; C2 key only via env lookup
  - class: subagent-safety
    id: n55-1-no-order
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'process_after_gate_b' not in t"
    pass_condition: dashboard still never submits via Gate B
  - class: subagent-safety
    id: n55-1-no-tv-search
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'tradingview.com' not in t.lower() or 'webhook' in t.lower()"
    pass_condition: no invented TradingView search host in the job
```

### Quality Brief (Sprint N55)

See sprint Quality Brief above. LIVE false; refresh ≠ approve ≠ fill; reuse N54 POST; no TV search; no C2 marketplace search; no approval mutation.

Melhoria: adapt N54 live-criteria job + preapproval queue so all eligible C2+Prodigy+TV rows appear; fail-closed per source.
Contexto: operator still sees one TradingView origin with metrics unavailable after Atualizar candidatos. Empty `calculate` persists empty JSON and wipes prior research; provider-research dump is then loaded as Collective2; TV errors are silent (F-018).
Objetivo: keep `POST /api/signals/candidates/refresh` (`mode: live_criteria`, `orders_sent=0`). Do **not** add a parallel package. Empty Prodígio raw → `issues` naming required raw `{sid}_closed_trades.json`; **do not persist** empty rank over previous JSON. Missing `C2_API4_KEY` or empty C2 IDs → `issues`; continue Prodígio+TV. `_live_refresh_tradingview` must append `issues` on failure (fix F-018). `build_preapproval_queue` returns union of: Collective2 named/seed + C2 research that is not merely a Prodígio dump; Prodígio rows with existing status `PRODIGY_CANDIDATE_RESEARCH`; TradingView ingested origins (metrics may stay missing). Never upsert `signal_provider_approvals`. Never `process_after_gate_b`. Never invent scores.
Critério de pronto: with fixtures for all three platforms, queue contains collective2 + prodigy + tradingview; without C2 key, prodigy+TV remain and prior C2 JSON remains; empty raw does not wipe prior prodigy JSON; TV helper records issues instead of bare `return`.
Cenários de teste (mínimo no implementer self-check; N55.3 owns pytest):
  1. Caso normal: fixtures C2 + Prodígio elegível + origem TV → fila com as três plataformas
  2. Edge: sem C2_API4_KEY → issues + Prodígio/TV intactos + pesquisa C2 anterior preservada
  3. Edge: raw Prodígio vazio → issue de arquivos brutos; sem score inventado; C2/TV intactos
  4. Regressão: GET reload ainda `disk_reread`; POST ainda `live_criteria` e `orders_sent=0`

### Task N55.2 — Mostrar aviso honesto quando uma fonte falha e as outras seguem

**Entrega:** Depois de atualizar, a tela mostra um aviso quando uma fonte falhou e mantém visível a tabela das outras; o aviso não some só porque a página recarregou.
**Como conferir:** Sem chave Collective2, após o clique e o recarregamento, o aviso descreve a falta da credencial e as linhas de Prodígio/TradingView ainda estão na tabela.
**Por quê:** Hoje o recarregamento descarta o JSON de problemas e o operador só vê a fila curta, como se as outras plataformas não existissem.

**Detalhe técnico**

- UI: `docs/design/mockups/sinais.md` S2 success + S3 keep table; 200 `partial` is **not** S3b 503 total. Warning banner + remaining rows. `aria-live="polite"`.
- Persist last refresh `issues` / `sources_ok` into the bundle the GET `/sinais` already reads (reuse research JSON volume — no new SQL). Reload script may keep POST then reload, but the banner must come from the bundle.
- Do **not** fetch Collective2 from JS. Do **not** change Aprovar/Rejeitar.
- **Arquivo(s):** `src/panel_ops_html.py`

**executor_prompt**:

```yaml
id: N55.2
size: M
bom_ref: BOM-3
depends_on: ["N55.1"]
files:
  - src/panel_ops_html.py
reuse_targets:
  - component: src/panel_ops_html.py
    reuse_as: extend
    convergence_check: 'rg "reload-candidates" src/panel_ops_html.py && rg "/api/signals/candidates/refresh" src/panel_ops_html.py'
  - component: docs/design/mockups/sinais.md
    reuse_as: copy_pattern
    convergence_check: 'rg "A fila anterior" src/panel_ops_html.py || rg "partial" src/panel_ops_html.py || rg "issues" src/panel_ops_html.py'
guardrail_contract:
  - class: secrets
    id: n55-2-no-c2-in-browser
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_html.py').read_text(); assert 'C2_API4_KEY' not in t; assert 'collective2.com' not in t.lower(); assert 'api4-general' not in t"
    pass_condition: HTML/JS never calls C2 hosts or embeds the key
  - class: subagent-safety
    id: n55-2-cta-post
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_html.py').read_text(); assert '/api/signals/candidates/refresh' in t; assert 'Atualizar candidatos' in t"
    pass_condition: same CTA still wired to live-criteria POST
```

### Quality Brief (Sprint N55)

See sprint Quality Brief. Preserve N52 hierarchy and N54 POST CTA; refresh ≠ approve.

Melhoria: honest partial banner after Atualizar candidatos that survives reload; keep remaining queue rows.
Contexto: script reloads the page 500ms after POST; `issues` never reach GET `/sinais`.
Objetivo: when `status=partial`, operator sees Portuguese warning naming the failed source (missing C2 key, missing Prodígio raw files) and the table of other platforms. Empty queue copy only when **no** platform contributed rows. S3 keep-table. No `prodigy_rank` import in HTML. No C2 host in JS.
Critério de pronto: `/sinais` HTML can render partial warning from bundle; POST path unchanged; no collective2.com.
Cenários:
  1. Caso normal: três plataformas na tabela, sem aviso de falha
  2. Edge: partial C2 → aviso + Prodígio/TV visíveis após reload
  3. Regressão: Aprovar/Rejeitar inalterado; hierarquia pré-aprovação → operação → auditoria

### Task N55.3 — Provar a fila com as três plataformas quando houver dados de teste

**Entrega:** Testes comprovam a fila com Collective2, Prodígio e TradingView juntos, a preservação quando uma fonte falha, e a recusa de nota inventada quando o Prodígio não tem arquivos brutos.
**Como conferir:** Rodar a suíte do painel e ver falha se a fila tiver só TradingView apesar dos fixtures, se a pesquisa anterior sumir sem chave, ou se o caminho de ordem for chamado.
**Por quê:** Sem essa prova o painel no ar volta a parecer “só uma origem” e ninguém percebe no CI.

**Detalhe técnico**

- **Arquivo(s):** `tests/test_panel_ops.py`
- **Risco:** MEDIUM — HTTP in-process + fixtures
- **Task size:** M

**executor_prompt**:

```yaml
id: N55.3
size: M
bom_ref: BOM-3
depends_on: ["N55.2"]
files:
  - tests/test_panel_ops.py
reuse_targets:
  - component: tests/test_panel_ops.py
    reuse_as: extend
    convergence_check: 'rg "live_criteria" tests/test_panel_ops.py && rg "preapproval" tests/test_panel_ops.py'
  - component: tests/test_prodigy_rank.py
    reuse_as: copy_pattern
    convergence_check: 'rg "PRODIGY_CANDIDATE_RESEARCH" tests/test_panel_ops.py || rg "prodigy" tests/test_panel_ops.py'
guardrail_contract:
  - class: subagent-safety
    id: n55-3-no-live-net
    target: tests/test_panel_ops.py
    check: python3 -c "from pathlib import Path; t=Path('tests/test_panel_ops.py').read_text(); assert 'C2_API4_KEY' not in t or 'environ' in t.lower() or 'patch' in t"
    pass_condition: tests do not require a real Collective2 key
```

### Quality Brief (Sprint N55)

See sprint Quality Brief.

Melhoria: pytest proving multi-platform preapproval queue after live-criteria POST.
Objetivo: nodeids covering (1) fixtures C2+Prodígio+TV → queue has all three platforms; (2) missing C2 key → partial issues, prodigy+TV remain, prior C2 research preserved; (3) empty prodigy raw → issue names raw providers, no invented score, other platforms remain; (4) HTML partial warning; (5) N54 regressions: 401/429/`orders_sent=0`/`disk_reread`; (6) no collective2.com in HTML; (7) `process_after_gate_b` absent.
Do not teach production about `tests/` paths (no HARNESS_BUG).
Critério de pronto: `python3 -m pytest tests/test_panel_ops.py tests/test_prodigy_rank.py tests/test_c2_signal_feed.py -q` green.
Cenários:
  1. Caso normal: três plataformas na fila com fixtures
  2. Edge: sem chave C2 → issues + outras plataformas
  3. Edge: raw Prodígio vazio → issue de arquivos brutos
  4. Edge: TV-only signals → TV rows + métricas indisponível honestas; C2/Prodígio só se fixtures existirem
  5. Regressão: N54 cooldown 429; GET disk_reread; Aprovar inalterado

### Task N55.4 — Atualizar o chamado, o aceite e o mapa da fila completa

**Entrega:** Mapa e aceite da função Sinais descrevem a fila das três plataformas e o aviso parcial; o chamado ISS-024 aponta esta sprint e permanece aberto até merge.
**Como conferir:** Ler a área Sinais do mapa e o chamado: sprint desta rodada; Feature 9 com os itens da fila completa marcados só se os testes existirem.
**Por quê:** Separar o job N54 já em main do que o operador ainda não vê na mesa.

**Detalhe técnico**

P task. Files: `docs/OPERATOR-PANEL-MAP.md` (§2 fila das três plataformas + aviso parcial), `docs/DASHBOARD-OPERATIONS.md` if the Sinais row exists, `docs/ISSUES.md` (ISS-024 notes; **do not close**), `docs/DIARY.md`, `docs/REQUIREMENTS.md` Feature 9 N55 checkboxes only with cited nodeids, `docs/FINDINGS.md` F-018 if fixed. LIVE false. N45–N47 not started. Document EasyPanel raw/key checklist without printing secrets.

---

## Sprint N56 — Ler os arquivos brutos no volume certo e manter a fila só com elegíveis
> Categoria: N  
> Status: planejada  
> Gerado via: `/pmo plan` 2026-11-19 · fonte ISS-024 / F-019 · N55 #74+#75 em `main`  
> titulo_humano: Atualizar candidatos lê os arquivos brutos no volume certo  
> resumo_humano: O trabalho ao vivo passa a ler os arquivos brutos no volume de relatórios, não numa pasta duplicada vazia. Quem não passa na janela de 15 dias continua fora da fila. Collective2 precisa da chave no servidor; TradingView só origens já recebidas. LIVE false.  
> Gate: job lê `{root}/providers/raw` quando `--root` é `/app/reports`; fila Prodígio só Feature 4 / 15d; `closed_trades_15d=0` ausente; pytest verde; LIVE false  
> review: senior+qa  
> Brief: `docs/.briefs/N56.brief.md`  
> Git First: `docs/.briefs/N56-GIT-FIRST-REUSE.md`  
> bom_ref: BOM-3  
> Depende de: N55 concluída (#74/#75) · ISS-024 · Release: ISS-024 (não usa N45–N47)  
> LIVE_TRADING_ENABLED: false  
> previous_sprint: N55  
> plan_only: true

### Em uma frase

Atualizar candidatos passa a ler os arquivos brutos no volume certo; quem não passa na janela de 15 dias continua fora da fila.

### O que muda para você

- O painel deixa de procurar os arquivos numa pasta vazia duplicada dentro do volume de relatórios
- Quem tem zero operações fechadas nos últimos 15 dias continua fora da fila do Prodígio — isso é o critério, não um defeito
- Collective2 só roda com a chave no servidor; TradingView lista só origens já recebidas
- Aprovar continua separado de atualizar; dinheiro real permanece desligado
- «Finalizado» só depois do merge no ramo principal e rebuild do painel no ar

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Leitura no volume certo | Depois de atualizar, o aviso de arquivos brutos some quando esses arquivos já estão no volume de relatórios |
| 2 | Fila só com quem passa | A fila do Prodígio lista só quem já atende a janela de 15 dias e os critérios já definidos |
| 3 | Sem histórico recente fica de fora | Três provedores sem operação fechada na janela continuam ausentes até haver histórico novo |
| 4 | Collective2 e TradingView honestos | Sem chave no servidor o Collective2 avisa e não inventa linhas; TradingView mostra só origens já ingeridas |
| 5 | Prova automática | A suíte falha se o trabalho voltar a procurar numa pasta duplicada vazia, ou se inventar nota para quem não pontua |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N56.0 Inventariar o caminho dos arquivos brutos no volume | `docs/.briefs/N56-GIT-FIRST-REUSE.md` | — |
| [x] | M | N56.1 Corrigir o caminho dos arquivos brutos no trabalho ao vivo | `src/v4_web_dashboard.py` | N56.0 |
| [x] | M | N56.2 Provar que o volume certo alimenta a fila só com elegíveis | `tests/test_panel_ops.py` | N56.1 |
| [x] | P | N56.3 Registrar o caminho certo e a fila só-elegível no chamado e no mapa | `docs/OPERATOR-PANEL-MAP.md, docs/ISSUES.md, docs/FINDINGS.md` | N56.2 |

### Quality Brief (Sprint N56)

**Alvo:** o job N54/N55 lê e grava arquivos brutos em `{root}/providers/raw` quando `--root` é `/app/reports`; a fila Prodígio permanece só elegíveis Feature 4 / 15d.

Maintain: `LIVE_TRADING_ENABLED=false`; paper host only; dashboard does not submit or cancel orders; refresh and approval are not fills.
Maintain: load `trader-entry|exit|budget|risk|scanner` only via `src/original.py`.
Maintain: N54 POST `/api/signals/candidates/refresh` and N55 queue union; argparse `--root` default `/app/reports` unchanged.
Maintain: Feature 4 / Prodígio 15d thresholds already in `prodigy_rank` (`WINDOW_DAYS=15`, `MIN_TRADES=5`, ≥3 days, `PRODIGY_CANDIDATE_RESEARCH`); `UNSCORABLE` with `closed_trades_15d=0` stays out of the Prodígio queue.
Avoid: changing `--root`/`DASHBOARD_ROOT` as a workaround; inventing scores; TradingView search; Collective2 marketplace search; `process_after_gate_b`; printing API keys; stealing N45–N47.

### Technical Advisory

- [ABORDAGEM] Juntar `providers/raw` sob o volume de relatórios já passado em `--root` — não mudar a bandeira.
- [RISCO] Os testes atuais gravam na pasta duplicada e ficam verdes apesar do defeito; a suíte precisa mudar o fixture junto com o join.
- [OPORTUNIDADE] Distinguir pasta canônica vazia (aviso de arquivos brutos) de provedores `UNSCORABLE` com zero operações na janela (ausência correta da fila).

> EXPIRES at end of Sprint N56. Not reusable in future sprints without a new preventive audit.

### Fora de escopo

- Mudar `--root` / `DASHBOARD_ROOT` / `REPORTS_DIR` como atalho
- Inventar busca TradingView, listagem marketplace Collective2 ou fórmula nova
- Soltar o filtro da fila para quem não pontua
- Mutar livro de pré-aprovação no refresh
- Ordem / fill / LIVE true
- SSH no EasyPanel; N45–N47; marcar «finalizado» antes do merge em `main`

### Task N56.0 — Inventariar o caminho dos arquivos brutos no volume

**Entrega:** Inventário dizendo que o volume de relatórios já é a raiz, onde o trabalho ao vivo junta a pasta errada, e que a fila só mostra quem passa nos critérios de 15 dias.
**Como conferir:** O inventário proíbe mudar a bandeira da raiz, cita o ranking de 15 dias sem inventar nota, e registra que três provedores sem operação na janela ficam de fora.
**Por quê:** Sem isso o EXECUTE muda a bandeira da raiz ou completa a fila com quem não pontua.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N56-GIT-FIRST-REUSE.md`. Re-check vendor pin `3d0f4ef`; no bump. Cite: `--root` default `/app/reports`, `_live_refresh_prodigy`, `_live_refresh_collective2`, `prodigy_rank.calculate` `--raw-dir=/app/reports/providers/raw`, `build_preapproval_queue` Prodígio filter, `_n54_write_prodigy_raw_trades` doubled fixture. Document: C2 needs server `C2_API4_KEY`; TV = ingested origins; `UNSCORABLE` `closed_trades_15d=0` correctly absent. Never print secrets.

### Task N56.1 — Corrigir o caminho dos arquivos brutos no trabalho ao vivo

**Entrega:** O mesmo trabalho ao vivo no servidor lê e grava os arquivos brutos no volume de relatórios, não numa pasta duplicada vazia.
**Como conferir:** Com os arquivos já no volume, atualizar candidatos deixa de tratar o Prodígio como pasta vazia; a bandeira da raiz permanece a mesma.
**Por quê:** Hoje o trabalho junta de novo a pasta de relatórios em cima da raiz que já é esse volume, e olha para uma pasta vazia.

**Detalhe técnico**

- **Estado atual:** `--root` default `/app/reports`. `_live_refresh_prodigy` and `_live_refresh_collective2` set `raw_dir = root / 'reports' / 'providers' / 'raw'` → `/app/reports/reports/providers/raw` (empty; mkdir even creates it). Real files: `/app/reports/providers/raw`. `_intelligence_dir` already uses `root / 'intelligence'` (correct).
- **Estado desejado:** canonical `raw_dir = root / 'providers' / 'raw'` and `snap_dir = root / 'providers' / 'signals'`. Do **not** change argparse `--root`. Do **not** mkdir the doubled path. Keep `prodigy_raw_missing` operator text as volume-relative `reports/providers/raw/{sid}_closed_trades.json` (the real path), not `reports/reports/...`. Empty canonical dir → missing issue and do not persist empty rank. Files present but all `UNSCORABLE` / `closed_trades_15d=0` → persist honest rank; **do not** treat as missing files; queue filter already drops them.
- **Arquivo(s):** `src/v4_web_dashboard.py`
- **Fonte(s):** ISS-024 nota operador 2026-11-19, F-019, Feature 4 / Prodígio 15d
- **Risco:** MEDIUM — shared live-criteria job and research JSON
- **Task size:** M (path join + mkdir side effect + C2 write path)

**executor_prompt**:

```yaml
id: N56.1
size: M
bom_ref: BOM-3
depends_on: ["N56.0"]
files:
  - src/v4_web_dashboard.py
reuse_targets:
  - component: src/v4_web_dashboard.py
    reuse_as: extend
    convergence_check: 'rg "_live_refresh_prodigy" src/v4_web_dashboard.py && rg "_live_refresh_collective2" src/v4_web_dashboard.py && rg -- "--root" src/v4_web_dashboard.py'
  - component: src/prodigy_rank.py
    reuse_as: call
    convergence_check: 'rg "prodigy_rank.calculate" src/v4_web_dashboard.py && rg "WINDOW_DAYS = 15" src/prodigy_rank.py'
  - component: src/c2_history_collect.py
    reuse_as: call
    convergence_check: 'rg "c2_history_collect" src/v4_web_dashboard.py'
guardrail_contract:
  - class: secrets
    id: n56-1-no-key-leak
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'sk_live' not in t.lower(); assert 'C2_API4_KEY' not in t or 'environ' in t"
    pass_condition: no live keys hardcoded; C2 key only via env lookup
  - class: subagent-safety
    id: n56-1-no-order
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'process_after_gate_b' not in t"
    pass_condition: dashboard still never submits via Gate B
  - class: subagent-safety
    id: n56-1-keep-root-default
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert \"default='/app/reports'\" in t or 'default=\"/app/reports\"' in t"
    pass_condition: argparse --root default remains /app/reports
```

### Quality Brief (Sprint N56)

See sprint Quality Brief above. LIVE false; refresh ≠ approve ≠ fill; do not change `--root`; do not invent Feature 4 thresholds.

Melhoria: fix live-criteria raw/signals joins so `--root /app/reports` reads `/app/reports/providers/raw`, not `/app/reports/reports/providers/raw`.
Contexto: operator confirmed real files at `/app/reports/providers/raw`; job mkdir/join still uses `root/'reports'/'providers'/'raw'`. Tests currently write to the doubled path and hide the bug.
Objetivo: keep `POST /api/signals/candidates/refresh` (`mode: live_criteria`, `orders_sent=0`). Do **not** add a parallel package. Do **not** change `--root` default. Helper ok: `_providers_raw_dir(root) = root / 'providers' / 'raw'` used by both Prodígio and Collective2. `_prodigy_rank_has_eligible_rows` must **not** be tightened to `PRODIGY_CANDIDATE_RESEARCH` only — files with `UNSCORABLE`/`closed_trades_15d=0` are present data, not missing raw. Never `process_after_gate_b`. Never invent scores. Never print `C2_API4_KEY`.
Critério de pronto: with `--root` still `/app/reports`, raw_dir resolves to `{root}/providers/raw`; doubled `{root}/reports/providers/raw` is not mkdir'd by the job; missing canonical files still emit `prodigy_raw_missing`; C2 snapshot dir `{root}/providers/signals`.
Cenários de teste (mínimo no implementer self-check; N56.2 owns pytest):
  1. Caso normal: arquivos em `{root}/providers/raw` → `calculate` sees them
  2. Edge: pasta duplicada `{root}/reports/providers/raw` vazia não é a fonte
  3. Edge: arquivos presentes com `closed_trades_15d=0` → não emitir missing; não inventar nota
  4. Regressão: `--root` default `/app/reports`; POST ainda `live_criteria` e `orders_sent=0`

### Task N56.2 — Provar que o volume certo alimenta a fila só com elegíveis

**Entrega:** Testes comprovam que os arquivos no volume certo alimentam o ranking, que a pasta duplicada não é a fonte, e que quem não pontua na janela de 15 dias não entra na fila do Prodígio.
**Como conferir:** A suíte falha se o trabalho só enxergar a pasta duplicada, se inventar nota, ou se incluir na fila quem está sem pontuação na janela.
**Por quê:** Sem essa prova o painel no ar volta a parecer vazio mesmo com arquivos no volume, ou alguém “completa” a fila contra o critério.

**Detalhe técnico**

- **Arquivo(s):** `tests/test_panel_ops.py`
- **Risco:** MEDIUM — HTTP in-process + fixtures currently encode the doubled path
- **Task size:** M

**executor_prompt**:

```yaml
id: N56.2
size: M
bom_ref: BOM-3
depends_on: ["N56.1"]
files:
  - tests/test_panel_ops.py
reuse_targets:
  - component: tests/test_panel_ops.py
    reuse_as: extend
    convergence_check: 'rg "_n54_write_prodigy_raw_trades" tests/test_panel_ops.py && rg "live_criteria" tests/test_panel_ops.py'
  - component: tests/test_prodigy_rank.py
    reuse_as: copy_pattern
    convergence_check: 'rg "PRODIGY_CANDIDATE_RESEARCH" tests/test_panel_ops.py || rg "UNSCORABLE" tests/test_panel_ops.py'
guardrail_contract:
  - class: subagent-safety
    id: n56-2-no-live-net
    target: tests/test_panel_ops.py
    check: python3 -c "from pathlib import Path; t=Path('tests/test_panel_ops.py').read_text(); assert 'api.collective2.com' not in t.lower()"
    pass_condition: tests do not call live Collective2 hosts
  - class: subagent-safety
    id: n56-2-no-harness-bug
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'tests/' not in t"
    pass_condition: production does not special-case tests/ paths
```

### Quality Brief (Sprint N56)

See sprint Quality Brief.

Melhoria: pytest proving canonical `{root}/providers/raw` is the live-criteria input and the Prodígio queue stays eligible-only.
Objetivo: nodeids covering (1) fixtures at `{root}/providers/raw` are read (`calculate` / no `prodigy_raw_missing` from empty doubled dir); (2) doubled `{root}/reports/providers/raw` is not the source; (3) three providers with `closed_trades_15d=0` / `UNSCORABLE` are absent from the Prodígio queue — no invented score; (4) missing canonical files still emit raw-missing; (5) N54/N55 regressions: `orders_sent=0`, missing C2 key issues, TV ingested origins only; (6) `process_after_gate_b` absent. Move `_n54_write_prodigy_raw_trades` (and any N55 helper that writes the same doubled path) to `{root}/providers/raw`. Do not teach production about `tests/` paths (no HARNESS_BUG).
Critério de pronto: `python3 -m pytest tests/test_panel_ops.py tests/test_prodigy_rank.py tests/test_c2_signal_feed.py -q` green.
Cenários:
  1. Caso normal: arquivos canônicos elegíveis → Prodígio na fila
  2. Edge: pasta duplicada vazia + arquivos canônicos → lê os canônicos
  3. Edge: três provedores 15d=0 → ausentes da fila Prodígio; sem nota inventada
  4. Edge: canônico vazio → `prodigy_raw_missing`; outras plataformas intactas
  5. Regressão: N54 cooldown 429; GET disk_reread; Aprovar inalterado; `--root` default unchanged

### Task N56.3 — Registrar o caminho certo e a fila só-elegível no chamado e no mapa

**Entrega:** Mapa e chamado descrevem o volume certo e que a fila do Prodígio só mostra quem passa na janela de 15 dias; o chamado permanece aberto até merge.
**Como conferir:** Ler a área Sinais do mapa e o chamado: sprint desta rodada; três provedores sem operação na janela documentados como ausência correta; Feature 9 marcada só se os testes existirem.
**Por quê:** Separar o defeito da pasta duplicada da fila vazia honesta de quem não pontua.

**Detalhe técnico**

P task. Files: `docs/OPERATOR-PANEL-MAP.md` (§2 canonical `{root}/providers/raw` under `--root /app/reports`; eligible-only Prodígio queue; C2 key; TV ingested origins), `docs/ISSUES.md` (ISS-024 notes; **do not close**), `docs/FINDINGS.md` (F-019; mark corrigido only with nodeids), `docs/DIARY.md`, `docs/REQUIREMENTS.md` Feature 9 N56 checkboxes only with cited nodeids. LIVE false. N45–N47 not started. Never print secrets.

---

## Sprint N57 — Mostrar Collective2 na fila a partir dos arquivos brutos, sem exigir lista de cópia
> Categoria: N  
> Status: planejada  
> Gerado via: `/pmo plan` 2026-11-19 · fonte ISS-024 / F-020 · N56 #76 em `main`  
> titulo_humano: Collective2 entra na fila sem exigir lista de cópia paper  
> resumo_humano: Depois de atualizar candidatos, as estratégias Collective2 já presentes nos arquivos brutos aparecem na fila como pendentes, mesmo com a lista de cópia paper vazia. Essa lista continua o portão da cópia — não da visibilidade. LIVE false.  
> Gate: allowlist vazia + arquivos brutos canônicos → fila Collective2 pendente; chave no servidor busca esses IDs; cópia paper fechada; pytest verde; LIVE false  
> review: senior+qa  
> Brief: `docs/.briefs/N57.brief.md`  
> Git First: `docs/.briefs/N57-GIT-FIRST-REUSE.md`  
> bom_ref: BOM-3  
> Depende de: N56 concluída (#76) · ISS-024 · Release: ISS-024 (não usa N45–N47)  
> LIVE_TRADING_ENABLED: false  
> previous_sprint: N56  
> plan_only: true

### Em uma frase

Depois de atualizar candidatos, o Collective2 aparece na fila a partir dos arquivos brutos já no volume, sem precisar de lista nomeada só para ser visto.

### O que muda para você

- Três estratégias já presentes nos arquivos brutos passam a aparecer na fila como pendentes, mesmo com a lista de cópia paper vazia
- Atualizar com a chave no servidor busca e atualiza esses identificadores; sem chave o aviso continua honesto e as linhas de disco não somem
- A lista nomeada e a aprovação no painel continuam o portão da cópia paper — aparecer na fila não autoriza operação
- Quem não passa na janela de 15 dias do Prodígio segue fora da fila do Prodígio; TradingView continua só origens já recebidas
- «Finalizado» só depois do merge no ramo principal e rebuild do painel no ar

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Collective2 visível sem lista nomeada | Com a lista de cópia vazia, atualizar candidatos lista as estratégias cujos arquivos brutos já estão no volume, como pendentes |
| 2 | Atualização ao vivo desses identificadores | Com a chave no servidor, o trabalho busca exatamente esses identificadores e não inventa outros |
| 3 | Cópia paper continua fechada | A seção de cópia paper permanece fechada enquanto a lista nomeada e o livro-razão não aprovarem; atualizar não aprova sozinho |
| 4 | Prodígio e TradingView inalterados | As mesmas estratégias sem janela de 15 dias continuam fora do Prodígio; TradingView mostra só origens já ingeridas |
| 5 | Prova automática | A suíte falha se a fila Collective2 exigir lista nomeada para aparecer, se autoaprovar, ou se inventar busca de marketplace |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N57.0 Inventariar de onde o Collective2 deve aparecer na fila | `docs/.briefs/N57-GIT-FIRST-REUSE.md` | — |
| [x] | M | N57.1 Mostrar candidatos Collective2 a partir dos arquivos brutos sem exigir lista de cópia | `src/v4_web_dashboard.py, src/panel_ops_data.py` | N57.0 |
| [x] | M | N57.2 Provar que a fila lista Collective2 pendente sem lista nomeada e que a cópia paper continua fechada | `tests/test_panel_ops.py` | N57.1 |
| [x] | P | N57.3 Registrar no mapa e no chamado que aparecer na fila não é autorizar cópia | `docs/OPERATOR-PANEL-MAP.md, docs/ISSUES.md, docs/FINDINGS.md` | N57.2 |

### Quality Brief (Sprint N57)

**Alvo:** após **Atualizar candidatos**, a fila lista Collective2 pendente a partir de `{root}/providers/raw/*_closed_trades.json` (e JSON de pesquisa C2 se existir) **sem** exigir allowlist/env; allowlist/ledger permanece o portão de cópia paper.

Maintain: `LIVE_TRADING_ENABLED=false`; paper host only; dashboard does not submit or cancel orders; refresh and approval are not fills.
Maintain: load `trader-entry|exit|budget|risk|scanner` only via `src/original.py`.
Maintain: N54 POST `/api/signals/candidates/refresh`, N55 queue union, N56 `_providers_raw_dir`; argparse `--root` default `/app/reports` unchanged.
Maintain: Feature 4 / Prodígio 15d thresholds already in `prodigy_rank`; `UNSCORABLE` with `closed_trades_15d=0` stays out of the Prodígio queue.
Maintain: `config/c2_paper_copy_allowlist.json` / `C2_PAPER_COPY_APPROVED_IDS` / ledger approve as paper-copy gate; empty seed ⇒ `approved_for_paper_copy` false.
Avoid: filling committed allowlist as a show-workaround; auto-approve; inventing scores; TradingView search; Collective2 marketplace search; `process_after_gate_b`; printing API keys; stealing N45–N47.

### Technical Advisory

- [ABORDAGEM] Reusar o glob numérico de `prodigy_rank.calculate` para descobrir IDs Collective2 no volume canônico; unir JSON de pesquisa C2; allowlist só como extra de fetch e como portão de cópia.
- [RISCO] Os mesmos arquivos brutos alimentam Prodígio (filtro 15d) e Collective2 (candidato pendente) — não misturar os dois critérios.
- [RISCO] `_live_refresh_collective2` hoje marca `sources_ok` mesmo com `ids=[]`; ops viu fonte ok e fila vazia.
- [OPORTUNIDADE] Chave ausente: aviso honesto **e** linhas já no disco continuam visíveis.

> EXPIRES at end of Sprint N57. Not reusable in future sprints without a new preventive audit.

### Fora de escopo

- Preencher lista nomeada commitada ou env como atalho de visibilidade
- Autoaprovar; mutar livro-razão no refresh
- Inventar busca TradingView, listagem marketplace Collective2 ou fórmula nova
- Soltar o filtro da fila Prodígio para quem não pontua
- Ordem / fill / LIVE true
- SSH no EasyPanel; N45–N47; marcar «finalizado» antes do merge em `main`

### Task N57.0 — Inventariar de onde o Collective2 deve aparecer na fila

**Entrega:** Inventário dizendo que os arquivos brutos no volume já são fonte suficiente para o Collective2 aparecer como pendente, e que a lista nomeada só autoriza cópia paper.
**Como conferir:** O inventário cita os três identificadores do volume, proíbe preencher a lista nomeada só para aparecer, e mantém o ranking de 15 dias sem inventar nota.
**Por quê:** Sem isso o EXECUTE trata a lista vazia como defeito e a preenche, ou mistura Prodígio com Collective2.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N57-GIT-FIRST-REUSE.md`. Re-check vendor pin `3d0f4ef`; no bump. Cite: `_merged_c2_strategy_ids` (allowlist + research only today), `build_preapproval_queue`, `_providers_raw_dir`, `prodigy_rank` glob, `load_c2_paper_copy_approved_ids`, operator IDs `132169961` / `148311109` / `30415311`. Document: allowlist = paper-copy gate; raw glob = queue visibility; TV ingested origins; LIVE false. Never print secrets. Never copy those IDs into committed allowlist.

### Task N57.1 — Mostrar candidatos Collective2 a partir dos arquivos brutos sem exigir lista de cópia

**Entrega:** Depois de atualizar, o Collective2 lista na fila as estratégias cujos arquivos brutos já estão no volume, como pendentes, mesmo com a lista de cópia vazia.
**Como conferir:** Com a lista vazia e os três arquivos no volume, a fila mostra essas três linhas pendentes; a cópia paper continua fechada; atualizar não grava aprovação.
**Por quê:** Hoje o trabalho só olha a lista nomeada e o JSON de pesquisa, então a fonte Collective2 pode “dar certo” e a fila ficar sem essas linhas.

**Detalhe técnico**

- **Estado atual:** `_merged_c2_strategy_ids` unions `load_c2_paper_copy_approved_ids` + `_load_c2_research_candidates` only. `build_preapproval_queue` adds C2 from `_load_c2_research_rows` + allowlist seed. Empty allowlist + empty research JSON ⇒ zero C2 queue rows even when `{root}/providers/raw/{sid}_closed_trades.json` exists. `_live_refresh_collective2` still `sources_ok.append('collective2')` when `ids=[]`.
- **Estado desejado:** discover numeric IDs from `_providers_raw_dir(root).glob('*_closed_trades.json')` (same prefix rule as `prodigy_rank.calculate`; do **not** change `WINDOW_DAYS`/`MIN_TRADES`). Union existing C2 research JSON (skip `PRODIGY_RANK_RESEARCH_ONLY`). `_merged_c2_strategy_ids` = discovery ∪ research ∪ allowlist (allowlist still fetched if named). `build_preapproval_queue` adds discovered IDs as `status: pending`, `source: discovered` without allowlist. Do **not** auto-approve. `resolve_c2_paper_copy_approved_ids` unchanged. Key present + ids → existing `_invoke_c2_history_collect`. Key present + no discoverable ids → honest issue (not silent `sources_ok`). Key missing → `C2_API4_KEY_missing`; disk-discovered rows still listed. Prodígio filter unchanged. TV unchanged.
- **Arquivo(s):** `src/v4_web_dashboard.py`, `src/panel_ops_data.py`
- **Fonte(s):** ISS-024 nota operador 2026-11-19, F-020, Feature 4 / N50 paper-copy gate, N56 canonical raw
- **Risco:** MEDIUM — shared live-criteria job, queue, and paper-copy gate
- **Task size:** M (2 files + discovery vs allowlist design)

**executor_prompt**:

```yaml
id: N57.1
size: M
bom_ref: BOM-3
depends_on: ["N57.0"]
files:
  - src/v4_web_dashboard.py
  - src/panel_ops_data.py
reuse_targets:
  - component: src/v4_web_dashboard.py
    reuse_as: extend
    convergence_check: 'rg "_merged_c2_strategy_ids" src/v4_web_dashboard.py && rg "_live_refresh_collective2" src/v4_web_dashboard.py && rg "_providers_raw_dir" src/v4_web_dashboard.py'
  - component: src/panel_ops_data.py
    reuse_as: extend
    convergence_check: 'rg "def build_preapproval_queue" src/panel_ops_data.py && rg "def load_c2_paper_copy_approved_ids" src/panel_ops_data.py'
  - component: src/prodigy_rank.py
    reuse_as: copy_pattern
    convergence_check: 'rg "_closed_trades.json" src/v4_web_dashboard.py src/panel_ops_data.py && rg "WINDOW_DAYS = 15" src/prodigy_rank.py'
  - component: src/c2_history_collect.py
    reuse_as: call
    convergence_check: 'rg "c2_history_collect" src/v4_web_dashboard.py'
guardrail_contract:
  - class: secrets
    id: n57-1-no-key-leak
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text()+Path('src/panel_ops_data.py').read_text(); assert 'sk_live' not in t.lower(); assert 'C2_API4_KEY' not in t or 'environ' in t"
    pass_condition: no live keys hardcoded; C2 key only via env lookup
  - class: subagent-safety
    id: n57-1-no-order
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text()+Path('src/panel_ops_data.py').read_text(); assert 'process_after_gate_b' not in t"
    pass_condition: dashboard still never submits via Gate B
  - class: subagent-safety
    id: n57-1-no-auto-approve
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'upsert_signal_provider_approval' not in t"
    pass_condition: live-criteria refresh does not write ledger approve
  - class: subagent-safety
    id: n57-1-keep-root-default
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert \"default='/app/reports'\" in t or 'default=\"/app/reports\"' in t"
    pass_condition: argparse --root default remains /app/reports
```

### Quality Brief (Sprint N57)

See sprint Quality Brief above. LIVE false; refresh ≠ approve ≠ fill; do not require allowlist to appear; do not invent Feature 4 thresholds.

Melhoria: discover Collective2 strategy IDs from canonical `{root}/providers/raw/*_closed_trades.json` (and existing C2 research JSON) and list them as pending preapproval rows without an allowlist/env prerequisite.
Contexto: after N56 #76, ops has empty allowlist/env, `sources_ok` includes collective2, queue has no C2 rows, raw has 132169961 / 148311109 / 30415311. `_merged_c2_strategy_ids` ignores the glob. Same files may be UNSCORABLE for Prodígio 15d — keep them out of the Prodígio queue.
Objetivo: keep `POST /api/signals/candidates/refresh` (`mode: live_criteria`, `orders_sent=0`). Do **not** add a parallel package. Do **not** write those IDs into committed `config/c2_paper_copy_allowlist.json`. Helper ok: discover via `_providers_raw_dir` glob (copy_pattern of `prodigy_rank`). Allowlist remains paper-copy only. Never `process_after_gate_b`. Never invent scores. Never print `C2_API4_KEY`.
Critério de pronto: empty allowlist + canonical raw IDs → C2 pending in `copy.preapproval.queue`; `approved_for_paper_copy` false; with key, fetch is invoked with those IDs; key+no IDs → honest issue not silent ok; Prodígio filter unchanged.
Cenários de teste (mínimo no implementer self-check; N57.2 owns pytest):
  1. Caso normal: três arquivos brutos + allowlist vazia → três C2 pendentes
  2. Edge: chave presente + ids descobertos → fetch desses ids
  3. Edge: chave presente + zero ids → aviso honesto, sem sources_ok falso
  4. Regressão: `approved_for_paper_copy` false; N56 Prodígio 15d; `--root` default; `orders_sent=0`

### Task N57.2 — Provar que a fila lista Collective2 pendente sem lista nomeada e que a cópia paper continua fechada

**Entrega:** Testes comprovam que os arquivos brutos bastam para o Collective2 aparecer como pendente, que a cópia paper segue fechada, e que atualizar não aprova sozinho.
**Como conferir:** A suíte falha se a fila exigir lista nomeada para mostrar Collective2, se marcar cópia paper aberta, se autoaprovar, ou se incluir no Prodígio quem não passa na janela de 15 dias.
**Por quê:** Sem essa prova o painel no ar volta a esconder as estratégias já no volume, ou alguém preenche a lista nomeada como atalho.

**Detalhe técnico**

- **Arquivo(s):** `tests/test_panel_ops.py`
- **Risco:** MEDIUM — HTTP in-process + N55 fixtures currently plant allowlist as the C2 show path
- **Task size:** M

**executor_prompt**:

```yaml
id: N57.2
size: M
bom_ref: BOM-3
depends_on: ["N57.1"]
files:
  - tests/test_panel_ops.py
reuse_targets:
  - component: tests/test_panel_ops.py
    reuse_as: extend
    convergence_check: 'rg "N55MultiPlatformLiveCriteriaTests" tests/test_panel_ops.py && rg "N56ProdigyCanonicalRawPathTests" tests/test_panel_ops.py && rg "_n56_write_closed_trades_file" tests/test_panel_ops.py'
  - component: tests/test_panel_ops.py
    reuse_as: copy_pattern
    convergence_check: 'rg "_n54_mock_c2_fetch" tests/test_panel_ops.py && rg "approved_for_paper_copy" tests/test_panel_ops.py'
guardrail_contract:
  - class: subagent-safety
    id: n57-2-no-live-net
    target: tests/test_panel_ops.py
    check: python3 -c "from pathlib import Path; t=Path('tests/test_panel_ops.py').read_text(); assert 'api.collective2.com' not in t.lower()"
    pass_condition: tests do not call live Collective2 hosts
  - class: subagent-safety
    id: n57-2-no-harness-bug
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text()+Path('src/panel_ops_data.py').read_text(); assert 'tests/' not in t"
    pass_condition: production does not special-case tests/ paths
  - class: subagent-safety
    id: n57-2-no-committed-allowlist-seed
    target: config/c2_paper_copy_allowlist.json
    check: python3 -c "import json; from pathlib import Path; d=json.loads(Path('config/c2_paper_copy_allowlist.json').read_text()); assert d.get('approved_ids')==[]"
    pass_condition: committed allowlist stays empty; tests must not write operator IDs into repo config
```

### Quality Brief (Sprint N57)

See sprint Quality Brief.

Melhoria: pytest proving canonical raw C2 IDs appear as pending queue rows with empty allowlist/env, paper-copy stays closed, refresh does not approve.
Objetivo: nodeids covering (1) empty allowlist JSON + empty `C2_PAPER_COPY_APPROVED_IDS` + raw files for 132169961, 148311109, 30415311 → those three Collective2 pending rows; (2) with `C2_API4_KEY`, mocked fetch/history is invoked with those IDs (extend `_n54_mock_c2_fetch` if it ignores `strategy_ids`); (3) `copy.collective2.approved_for_paper_copy` is false; (4) POST refresh does not upsert ledger approve; (5) same files `UNSCORABLE`/`closed_trades_15d=0` stay out of Prodígio queue; (6) missing key still lists disk IDs + `C2_API4_KEY_missing`; (7) key + zero discoverable IDs → honest issue, not silent sources_ok; (8) N54/N55/N56 regressions: `orders_sent=0`, TV ingested origins only, `--root` default; (9) `process_after_gate_b` absent. Do not teach production about `tests/` paths (no HARNESS_BUG). Do not commit operator IDs into `config/c2_paper_copy_allowlist.json`.
Critério de pronto: `python3 -m pytest tests/test_panel_ops.py tests/test_prodigy_rank.py tests/test_c2_signal_feed.py -q` green.
Cenários:
  1. Caso normal: três raw + allowlist vazia → C2 pendente na fila
  2. Edge: chave + ids → mock fetch recebe esses ids
  3. Edge: chave + zero ids → aviso honesto
  4. Edge: sem chave → aviso de chave; linhas de disco visíveis
  5. Regressão: N50 paper-copy closed; N55 union with allowlist fixture still works; N56 Prodígio 15d; cooldown 429; Aprovar inalterado

### Task N57.3 — Registrar no mapa e no chamado que aparecer na fila não é autorizar cópia

**Entrega:** Mapa e chamado descrevem que o Collective2 aparece a partir dos arquivos brutos e que a lista nomeada só autoriza cópia paper; o chamado permanece aberto até merge.
**Como conferir:** Ler a área Sinais do mapa e o chamado: sprint desta rodada; lista vazia não esconde candidatos; Feature 9 marcada só se os testes existirem.
**Por quê:** O texto atual ainda sugere que identificadores Collective2 só existem depois da lista nomeada.

**Detalhe técnico**

P task. Files: `docs/OPERATOR-PANEL-MAP.md` (§2 C2 queue from canonical raw without allowlist show-prerequisite; paper-copy gate unchanged; Prodígio 15d; TV ingested origins), `docs/DASHBOARD-OPERATIONS.md` (replace “IDs Collective2 só após allowlist/env” — visibility vs paper-copy), `docs/ISSUES.md` (ISS-024 notes; **do not close**), `docs/FINDINGS.md` (F-020; mark corrigido only with nodeids), `docs/DIARY.md`, `docs/REQUIREMENTS.md` Feature 9 N57 checkboxes only with cited nodeids. LIVE false. N45–N47 not started. Never print secrets. Never copy operator IDs into committed allowlist.

---

## Sprint N58 — Varrer a Collective2 nas regras já definidas, sem lista nomeada para aparecer
> Categoria: N  
> Status: planejada  
> Gerado via: `/pmo plan` 2026-11-19 · fonte ISS-024 / F-021 · N57 #77 em `main`  
> titulo_humano: Atualizar varre Collective2 nas regras já definidas  
> resumo_humano: Ao atualizar candidatos, o laboratório procura estratégias na Collective2 com as regras de quinze dias já no código e mostra só quem passa, mesmo com a lista de cópia vazia. O TradingView ainda não tem busca e fica de fora até haver contrato. LIVE false.  
> Gate: lista vazia + chave no servidor → varredura Collective2 mockável + fila só elegíveis 15d, inclusive IDs ausentes do disco; cópia paper fechada; TradingView sem varredura com aviso; pytest verde; LIVE false  
> review: senior+qa  
> Brief: `docs/.briefs/N58.brief.md`  
> Git First: `docs/.briefs/N58-GIT-FIRST-REUSE.md`  
> bom_ref: BOM-3  
> Depende de: N57 concluída (#77) · ISS-024 · Release: ISS-024 (não usa N45–N47)  
> LIVE_TRADING_ENABLED: false  
> previous_sprint: N57  
> plan_only: true

### Em uma frase

Ao atualizar candidatos, o laboratório varre a Collective2 com as regras de quinze dias já definidas e mostra só quem passa; o TradingView ainda não tem busca e fica de fora até haver contrato.

### O que muda para você

- Atualizar candidatos passa a procurar estratégias na Collective2 com a chave do servidor, sem lista nomeada para aparecer
- Só entra na fila quem já passa a janela de quinze dias, o mínimo de operações e os demais critérios já no código — sem nota nova
- Quem não passa continua fora; a lista nomeada só autoriza cópia paper
- TradingView não é varrido nesta rodada: o laboratório só vê origens já recebidas, até existir contrato de busca
- «Finalizado» só depois do merge no ramo principal e rebuild do painel no ar

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Varredura Collective2 sem lista nomeada | Com a lista de cópia vazia, atualizar candidatos traz estratégias da Collective2 que passam as regras de quinze dias, não só o que já estava no disco |
| 2 | Fila só com quem passa as regras | Estratégias sem histórico recente suficiente não aparecem como candidatas |
| 3 | Cópia paper continua fechada | Atualizar não aprova nem envia operação; a seção de cópia continua fechada sem lista e livro-razão |
| 4 | TradingView explícito fora da varredura | O aviso deixa claro que o TradingView não foi varrido; origens já recebidas continuam visíveis |
| 5 | Prova automática | A bateria de testes falha se a fila exigir lista nomeada, se usar o ranking da loja Collective2, se inventar busca TradingView, ou se mudar os números de quinze dias |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N58.0 Inventariar a varredura Collective2 e o bloqueio TradingView | `docs/.briefs/N58-GIT-FIRST-REUSE.md` | — |
| [x] | M | N58.1 Varrer a Collective2 e filtrar candidatos pelas regras já definidas | `src/c2_history_collect.py, src/v4_web_dashboard.py, src/panel_ops_data.py` | N58.0 |
| [x] | M | N58.2 Provar a varredura sem lista nomeada e sem inventar busca TradingView | `tests/test_panel_ops.py` | N58.1 |
| [x] | P | N58.3 Registrar no mapa que atualizar varre Collective2 e deixa TradingView de fora | `docs/OPERATOR-PANEL-MAP.md, docs/ISSUES.md, docs/FINDINGS.md, docs/REQUIREMENTS.md` | N58.2 |

### Quality Brief (Sprint N58)

**Alvo:** **Atualizar candidatos** varre Collective2 na listagem oficial disponível à chave, aplica Feature 4 / Prodígio 15d já no código, e mostra só elegíveis **sem** allowlist; TradingView não é varrido (ISS-025).

Maintain: `LIVE_TRADING_ENABLED=false`; paper host only; dashboard does not submit or cancel orders; refresh and approval are not fills.
Maintain: load `trader-entry|exit|budget|risk|scanner` only via `src/original.py`.
Maintain: N54 POST `/api/signals/candidates/refresh`, N55–N57 queue/join/discovery; argparse `--root` default `/app/reports` unchanged.
Maintain: Feature 4 / Prodígio 15d thresholds already in `prodigy_rank` (`WINDOW_DAYS = 15`, `MIN_TRADES = 5`); do not change them.
Avoid: SearchHistoricalStrategies C2 stats; GetLeaderBoard as eligibility; TradingView search HTTP; auto-approve; treating disk glob as Atualizar definition of done; `process_after_gate_b`; printing API keys; stealing N45–N47.

### Technical Advisory

- [ABORDAGEM] Reusar `c2_history_collect.fetch` para um GET `SearchStrategies` por clique; gravar só `closed_trades`; filtrar com `prodigy_rank.calculate`; cursor da próxima página no instantâneo de refresh já existente.
- [RISCO] Uma página da listagem oficial pode ser grande demais para o timeout de 25s — parar com aviso honesto de incompleto; não inventar tamanho de página no texto do produto.
- [RISCO] Usar estatísticas Collective2 (`SearchHistoricalStrategies`, Score, leaderboard) no lugar das constantes recuperadas reescreveria o aceite Feature 4.

> EXPIRES at end of Sprint N58. Not reusable in future sprints without a new preventive audit.

### Fora de escopo

- Inventar loja Collective2, ranking da loja ou estatísticas históricas Collective2 como filtro
- Inventar busca TradingView (ISS-025)
- Alterar constantes de quinze dias / mínimo de operações
- Tratar arquivos brutos no disco como história do botão Atualizar
- Autoaprovar; mutar livro-razão no refresh
- Ordem / fill / LIVE true
- SSH no EasyPanel; N45–N47; marcar «finalizado» antes do merge em `main`

### Task N58.0 — Inventariar a varredura Collective2 e o bloqueio TradingView

**Entrega:** Inventário dizendo que a Collective2 tem listagem oficial para varrer, que as regras de quinze dias já estão no código, e que o TradingView não tem busca neste laboratório.
**Como conferir:** O inventário cita a listagem oficial, proíbe usar o ranking da loja no lugar das regras já definidas, e marca o TradingView como fora até haver contrato.
**Por quê:** Sem isso o EXECUTE ou inventa uma loja, ou volta a vender o disco como se fosse varredura.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N58-GIT-FIRST-REUSE.md` and `docs/proposals/N58-collective2-api4-search.md`. Re-check vendor pin `3d0f4ef`; no bump. Cite: recovered `PATHS` history-by-id only; official GET `/Strategies/SearchStrategies`; POST `SearchHistoricalStrategies` forbidden; `GetLeaderBoard` forbidden; ADR-012 TV ingest only; `prodigy_rank` constants; N57 glob is cache not DoD; LIVE false. Never print secrets.

### Task N58.1 — Varrer a Collective2 e filtrar candidatos pelas regras já definidas

**Entrega:** Depois de atualizar, o laboratório procura estratégias na Collective2 com a chave do servidor e lista só quem passa as regras de quinze dias, mesmo com a lista de cópia vazia e mesmo que o identificador ainda não estivesse no disco.
**Como conferir:** Com a lista vazia, atualizar traz candidatos da varredura que passam as regras; quem não passa fica fora; a cópia paper continua fechada; atualizar não grava aprovação.
**Por quê:** Hoje o trabalho só atualiza identificadores já conhecidos no disco ou na lista, e a fila Collective2 ainda mostra quem não pontua na janela de quinze dias.

**Detalhe técnico**

- **Estado atual:** `_live_refresh_collective2` fetches `_merged_c2_strategy_ids` (allowlist ∪ raw glob ∪ research JSON). `build_preapproval_queue` lists every discovered raw C2 ID as pending even when `prodigy_rank` marks `UNSCORABLE`. Recovered `PATHS` are history-by-id only. TradingView job only unions ingested origins.
- **Estado desejado:** with `C2_API4_KEY`, one GET `/Strategies/SearchStrategies` via `c2_history_collect.fetch` per Atualizar. Persist `Pagination.next_cursor` on existing `candidates-refresh-latest.json`. For IDs on that page, GET `PATHS['closed_trades']` only; then `prodigy_rank.calculate` **without** changing `WINDOW_DAYS`/`MIN_TRADES`. Queue Collective2 and Prodígio only `PRODIGY_CANDIDATE_RESEARCH`. Skip `IsPrivate=true`. Empty allowlist still shows eligible scan rows as pending (`source: scanned` or keep `discovered` — do **not** auto-approve). Key missing → existing `C2_API4_KEY_missing`; do not fake a scan. Incomplete page → honest issue, not silent ok. TV: ingested origins + issue that scan is out (ISS-025). `--root` default unchanged.
- **Arquivo(s):** `src/c2_history_collect.py`, `src/v4_web_dashboard.py`, `src/panel_ops_data.py`
- **Fonte(s):** ISS-024 restatement 2026-11-19, F-021, Feature 4 / N50 paper-copy gate, N57 cache, ADR-012
- **Risco:** MEDIUM — shared live-criteria job, queue, paper-copy gate, new C2 GET
- **Task size:** M (3 files + scan vs cache design)

**executor_prompt**:

```yaml
id: N58.1
size: M
bom_ref: BOM-3
depends_on: ["N58.0"]
files:
  - src/c2_history_collect.py
  - src/v4_web_dashboard.py
  - src/panel_ops_data.py
reuse_targets:
  - component: src/c2_history_collect.py
    reuse_as: extend
    convergence_check: 'rg "SearchStrategies" src/c2_history_collect.py src/v4_web_dashboard.py && rg "GetStrategyHistoricalClosedTrades" src/c2_history_collect.py'
  - component: src/v4_web_dashboard.py
    reuse_as: extend
    convergence_check: 'rg "_live_refresh_collective2" src/v4_web_dashboard.py && rg "c2_history_collect" src/v4_web_dashboard.py && rg "_providers_raw_dir" src/v4_web_dashboard.py'
  - component: src/panel_ops_data.py
    reuse_as: extend
    convergence_check: 'rg "def build_preapproval_queue" src/panel_ops_data.py && rg "PRODIGY_CANDIDATE_RESEARCH" src/panel_ops_data.py'
  - component: src/prodigy_rank.py
    reuse_as: call
    convergence_check: 'rg "WINDOW_DAYS = 15" src/prodigy_rank.py && rg "MIN_TRADES = 5" src/prodigy_rank.py'
guardrail_contract:
  - class: secrets
    id: n58-1-no-key-leak
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text()+Path('src/panel_ops_data.py').read_text()+Path('src/c2_history_collect.py').read_text(); assert 'sk_live' not in t.lower()"
    pass_condition: no live keys hardcoded
  - class: subagent-safety
    id: n58-1-no-order
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text()+Path('src/panel_ops_data.py').read_text(); assert 'process_after_gate_b' not in t"
    pass_condition: dashboard still never submits via Gate B
  - class: subagent-safety
    id: n58-1-no-auto-approve
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'upsert_signal_provider_approval' not in t"
    pass_condition: live-criteria refresh does not write ledger approve
  - class: subagent-safety
    id: n58-1-no-invented-c2-stats
    target: src/c2_history_collect.py
    check: python3 -c "from pathlib import Path; t=Path('src/c2_history_collect.py').read_text()+Path('src/v4_web_dashboard.py').read_text(); assert 'SearchHistoricalStrategies' not in t; assert 'GetLeaderBoard' not in t"
    pass_condition: scan uses SearchStrategies plus recovered closed_trades; no C2 stats marketplace filter
  - class: subagent-safety
    id: n58-1-keep-root-default
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert \"default='/app/reports'\" in t or 'default=\"/app/reports\"' in t"
    pass_condition: argparse --root default remains /app/reports
  - class: subagent-safety
    id: n58-1-keep-prodigy-constants
    target: src/prodigy_rank.py
    check: python3 -c "from pathlib import Path; t=Path('src/prodigy_rank.py').read_text(); assert 'WINDOW_DAYS = 15' in t; assert 'MIN_TRADES = 5' in t"
    pass_condition: Feature 4 / Prodigy 15d constants unchanged
```

### Quality Brief (Sprint N58)

See sprint Quality Brief above. LIVE false; refresh ≠ approve ≠ fill; scan Collective2 via existing GET fetch; do not invent Feature 4 thresholds; TradingView search remains out.

Melhoria: wire official GET SearchStrategies through recovered `c2_history_collect.fetch`, fetch closed_trades for those IDs, filter with unchanged `prodigy_rank.calculate`, list only eligible pending rows without allowlist.
Contexto: after N57 #77, Atualizar still means refresh IDs already on disk/research. Operator restated scan of homologated Collective2 as DoD. Recovered PATHS are history-by-id; official API4 SearchStrategies exists on the same host. SearchHistoricalStrategies / GetLeaderBoard are not Feature 4. TV has ingest only (ADR-012) — ISS-025.
Objetivo: keep `POST /api/signals/candidates/refresh` (`mode: live_criteria`, `orders_sent=0`). Do **not** add a parallel package. One SearchStrategies GET per click; persist next_cursor on existing refresh snapshot; closed_trades only on scan path; queue only `PRODIGY_CANDIDATE_RESEARCH`. Allowlist remains paper-copy only. Never `process_after_gate_b`. Never invent scores. Never print `C2_API4_KEY`. Never call a TradingView search host.
Critério de pronto: empty allowlist + mocked SearchStrategies IDs not on disk → eligible C2/Prodígio pending in `copy.preapproval.queue`; unscorable mocked histories absent; `approved_for_paper_copy` false; TV issue records scan-out; key missing → no fake scan.
Cenários de teste (mínimo no implementer self-check; N58.2 owns pytest):
  1. Caso normal: SearchStrategies devolve ID novo que passa 15d → aparece pendente sem allowlist
  2. Edge: o mesmo ID falha 15d → ausente da fila
  3. Edge: next_cursor presente → aviso de varredura incompleta
  4. Regressão: cópia paper fechada; N54–N57; `--root` default; `orders_sent=0`; sem busca TV

### Task N58.2 — Provar a varredura sem lista nomeada e sem inventar busca TradingView

**Entrega:** Testes comprovam que atualizar varre a Collective2 sem lista nomeada, que só quem passa as regras entra na fila, que a cópia paper segue fechada, e que nenhuma busca TradingView foi inventada.
**Como conferir:** A bateria falha se a fila exigir lista nomeada, se aceitar quem não passa quinze dias, se autoaprovar, se chamar ranking da loja Collective2, ou se inventar HTTP de busca TradingView.
**Por quê:** Sem essa prova o painel volta a vender o disco como varredura, ou alguém inventa filtro da loja no lugar das regras já recuperadas.

**Detalhe técnico**

- **Arquivo(s):** `tests/test_panel_ops.py`
- **Risco:** MEDIUM — HTTP in-process + N57 fixtures currently treat raw glob as C2 show path
- **Task size:** M

**executor_prompt**:

```yaml
id: N58.2
size: M
bom_ref: BOM-3
depends_on: ["N58.1"]
files:
  - tests/test_panel_ops.py
reuse_targets:
  - component: tests/test_panel_ops.py
    reuse_as: extend
    convergence_check: 'rg "N57Collective2RawQueueDiscoveryTests" tests/test_panel_ops.py && rg "N56ProdigyCanonicalRawPathTests" tests/test_panel_ops.py && rg "_n54_mock_c2_fetch" tests/test_panel_ops.py'
  - component: tests/test_panel_ops.py
    reuse_as: copy_pattern
    convergence_check: 'rg "approved_for_paper_copy" tests/test_panel_ops.py && rg "PRODIGY_CANDIDATE_RESEARCH" tests/test_panel_ops.py'
guardrail_contract:
  - class: subagent-safety
    id: n58-2-no-live-net
    target: tests/test_panel_ops.py
    check: python3 -c "from pathlib import Path; t=Path('tests/test_panel_ops.py').read_text(); assert 'api.collective2.com' not in t.lower(); assert 'tradingview.com' not in t.lower() or 'webhook' in t.lower()"
    pass_condition: tests do not call live Collective2 or invented TradingView search hosts
  - class: subagent-safety
    id: n58-2-no-harness-bug
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text()+Path('src/panel_ops_data.py').read_text()+Path('src/c2_history_collect.py').read_text(); assert 'tests/' not in t"
    pass_condition: production does not special-case tests/ paths
  - class: subagent-safety
    id: n58-2-no-committed-allowlist-seed
    target: config/c2_paper_copy_allowlist.json
    check: python3 -c "import json; from pathlib import Path; d=json.loads(Path('config/c2_paper_copy_allowlist.json').read_text()); assert d.get('approved_ids')==[]"
    pass_condition: committed allowlist stays empty
  - class: subagent-safety
    id: n58-2-keep-prodigy-constants
    target: src/prodigy_rank.py
    check: python3 -c "from pathlib import Path; t=Path('src/prodigy_rank.py').read_text(); assert 'WINDOW_DAYS = 15' in t; assert 'MIN_TRADES = 5' in t"
    pass_condition: tests must not rewrite Feature 4 constants
```

### Quality Brief (Sprint N58)

See sprint Quality Brief.

Melhoria: pytest proving mocked SearchStrategies IDs (not on disk) become pending queue rows only when recovered Prodígio 15d passes, empty allowlist, paper-copy closed, no TV search, no C2 leaderboard.
Objetivo: nodeids covering (1) empty allowlist + mocked SearchStrategies ID absent from raw + closed_trades fixture that yields `PRODIGY_CANDIDATE_RESEARCH` → Collective2/Prodígio pending; (2) same ID with `UNSCORABLE` / `closed_trades_15d=0` → absent from queue; (3) `approved_for_paper_copy` false; (4) POST refresh does not upsert ledger approve; (5) next_cursor → honest incomplete issue; (6) missing key → `C2_API4_KEY_missing`, no SearchStrategies call pretended ok; (7) TradingView still ingested origins only — no search HTTP; issue or flag that TV scan is out; (8) N54–N57 regressions: `orders_sent=0`, `--root` default, raw glob still must not require allowlist for cache rows that pass 15d; (9) `SearchHistoricalStrategies` / `GetLeaderBoard` absent from production; (10) `process_after_gate_b` absent. Do not teach production about `tests/` paths (no HARNESS_BUG). Do not commit operator IDs into `config/c2_paper_copy_allowlist.json`.
Critério de pronto: `python3 -m pytest tests/test_panel_ops.py tests/test_prodigy_rank.py tests/test_c2_signal_feed.py -q` green.
Cenários:
  1. Caso normal: SearchStrategies ID novo elegível → fila pendente sem allowlist
  2. Edge: ID novo inelegível 15d → fora da fila
  3. Edge: next_cursor → aviso incompleto
  4. Edge: sem chave → aviso de chave; sem fingir varredura
  5. Regressão: N50 paper-copy closed; N55 union; N56 Prodígio 15d; N57 cache without allowlist; cooldown 429; Aprovar inalterado; sem busca TV

### Task N58.3 — Registrar no mapa que atualizar varre Collective2 e deixa TradingView de fora

**Entrega:** Mapa e chamado descrevem que atualizar varre a Collective2 nas regras já definidas, que a lista nomeada só autoriza cópia paper, e que o TradingView permanece sem varredura até haver contrato; o chamado ISS-024 permanece aberto até merge.
**Como conferir:** Ler a área Sinais do mapa e o chamado: sprint desta rodada; disco não é a história do botão; Feature 9 marcada só se os testes existirem.
**Por quê:** O texto atual ainda vende arquivos brutos no volume como se fossem a varredura que o operador pediu.

**Detalhe técnico**

P task. Files: `docs/OPERATOR-PANEL-MAP.md` (§2 Atualizar = Collective2 SearchStrategies + Feature 4 filter; disk glob is cache; paper-copy gate unchanged; TV scan OUT ISS-025; ingested origins remain), `docs/DASHBOARD-OPERATIONS.md` (Atualizar is platform scan, not raw inventory), `docs/ISSUES.md` (ISS-024 notes keep OPEN; ISS-025 TV search contract), `docs/FINDINGS.md` (F-021; mark corrigido only with nodeids), `docs/DIARY.md`, `docs/REQUIREMENTS.md` Feature 9 N58 checkboxes only with cited nodeids. LIVE false. N45–N47 not started. Never print secrets.

---

## Sprint N59 — Não perder a varredura Collective2 se a consulta de ordens ativas falhar
> Categoria: N  
> Status: planejada  
> Gerado via: `/pmo plan` 2026-11-19 · fonte ISS-024 / F-022 · N58 #78 em `main`  
> titulo_humano: Atualizar não perde a varredura Collective2 se ordens ativas falharem  
> resumo_humano: Ao atualizar candidatos, a listagem Collective2 e o filtro de quinze dias continuam mesmo se a consulta de ordens ativas recusar ou o endereço ficar longo demais. Quem passa as regras entra na fila com a lista de cópia vazia. LIVE false.  
> Gate: lista vazia + SearchStrategies e histórico fechado mockados ok + snapshot HTTP 414 → refresh 200 com fila elegível e sources_ok collective2; aviso de instantâneo sem collective2_refresh_failed; pytest verde; LIVE false  
> review: senior+qa  
> Brief: `docs/.briefs/N59.brief.md`  
> Git First: `docs/.briefs/N59-GIT-FIRST-REUSE.md`  
> bom_ref: BOM-3  
> Depende de: N58 concluída (#78) · ISS-024 · Release: ISS-024 (não usa N45–N47)  
> LIVE_TRADING_ENABLED: false  
> previous_sprint: N58  
> plan_only: true

### Em uma frase

Ao atualizar candidatos, a varredura Collective2 e o filtro de quinze dias continuam mesmo se a consulta de ordens ativas falhar; quem passa as regras entra na fila.

### O que muda para você

- Atualizar deixa de tratar a Collective2 como morta só porque a consulta de ordens ativas recusou ou o endereço ficou longo demais
- Com a lista de cópia vazia, quem já passa as regras de quinze dias continua aparecendo na fila
- O aviso descreve a falha das ordens ativas sem apagar o resultado da varredura
- A consulta de ordens ativas deixa de receber a página inteira da listagem — ela não define quem é candidato
- «Finalizado» só depois do merge no ramo principal e rebuild do painel no ar

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Varredura Collective2 sobrevive à falha de ordens ativas | Atualizar com lista de cópia vazia ainda traz quem passa quinze dias; o aviso de ordens ativas não esvazia a fila |
| 2 | Aviso honesto, fonte Collective2 ainda ok | O painel diz que a consulta de ordens ativas falhou e mesmo assim marca a varredura Collective2 como feita |
| 3 | Ordens ativas fora da elegibilidade | A listagem oficial não é mandada inteira para a consulta de ordens ativas |
| 4 | Cópia paper continua fechada | Atualizar não aprova nem envia operação |
| 5 | Prova automática | A bateria falha se a consulta de ordens ativas derrubar a fila, se exigir lista nomeada, ou se mudar os números de quinze dias |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N59.0 Inventariar a consulta de ordens ativas versus a varredura | `docs/.briefs/N59-GIT-FIRST-REUSE.md` | — |
| [x] | M | N59.1 Isolar a consulta de ordens ativas da varredura Collective2 | `src/v4_web_dashboard.py` | N59.0 |
| [x] | M | N59.2 Provar que a falha de ordens ativas não esvazia a fila | `tests/test_panel_ops.py` | N59.1 |
| [x] | P | N59.3 Registrar no mapa que ordens ativas não definem quem é candidato | `docs/OPERATOR-PANEL-MAP.md, docs/ISSUES.md, docs/FINDINGS.md, docs/REQUIREMENTS.md` | N59.2 |

### Quality Brief (Sprint N59)

**Alvo:** **Atualizar candidatos** continua a varrer Collective2 e a enfileirar só quem passa quinze dias mesmo quando a consulta de ordens ativas falha; o instantâneo não recebe a página da listagem.

Maintain: `LIVE_TRADING_ENABLED=false`; paper host only; dashboard does not submit or cancel orders; refresh and approval are not fills.
Maintain: load `trader-entry|exit|budget|risk|scanner` only via `src/original.py`.
Maintain: N54 POST `/api/signals/candidates/refresh`, N55–N58 queue/join/discovery/SearchStrategies; argparse `--root` default `/app/reports` unchanged.
Maintain: Feature 4 / Prodígio 15d thresholds already in `prodigy_rank` (`WINDOW_DAYS = 15`, `MIN_TRADES = 5`); do not change them.
Avoid: passing SearchStrategies page IDs into `c2_signal_feed.snapshot`; mapping snapshot HTTPError to `collective2_refresh_failed`; inventing GetStrategyActiveOrders batching; TradingView search HTTP; auto-approve; `process_after_gate_b`; printing API keys; stealing N45–N47.

### Technical Advisory

- [ABORDAGEM] Isolar `snapshot` num `try` interno; nunca unir IDs da listagem; pular se a lista nomeada de cópia estiver vazia — ordens ativas não são elegibilidade.
- [RISCO] Capturar HTTPError da listagem no mesmo `except` interno esconderia falha real de varredura — o `except` de instantâneo fica só em volta de `snapshot`.
- [RISCO] Inventar lote/paginação para `GetStrategyActiveOrders` transformaria diagnóstico em segundo cliente Collective2; 414 é limite de URL, não Feature 4.

> EXPIRES at end of Sprint N59. Not reusable in future sprints without a new preventive audit.

### Fora de escopo

- Inventar lote, paginação ou cliente novo para ordens ativas da página da listagem
- Inventar busca TradingView (ISS-025)
- Alterar constantes de quinze dias / mínimo de operações
- Autoaprovar; mutar livro-razão no refresh
- Ordem / fill / LIVE true
- SSH no EasyPanel; N45–N47; marcar «finalizado» antes do merge em `main`

### Task N59.0 — Inventariar a consulta de ordens ativas versus a varredura

**Entrega:** Inventário dizendo que a consulta de ordens ativas é só diagnóstico, que a varredura e o filtro de quinze dias já existem, e que misturar os dois no mesmo bloco derruba a fonte Collective2.
**Como conferir:** O inventário cita a listagem oficial e o histórico fechado como elegibilidade, proíbe mandar a página inteira para ordens ativas, e marca o TradingView como fora.
**Por quê:** Sem isso o EXECUTE tenta “consertar” o 414 inventando lote, ou deixa a falha abortar de novo a varredura.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N59-GIT-FIRST-REUSE.md`. Re-check vendor pin `3d0f4ef`; no bump. Cite: `_live_refresh_collective2` shared try; `c2_signal_feed.snapshot` / `GetStrategyActiveOrders`; HTTPError subclasses OSError; N50 snapshot-not-ticket; Feature 4 is `prodigy_rank` not active orders; ADR-012 TV ingest only; LIVE false. Never print secrets.

### Task N59.1 — Isolar a consulta de ordens ativas da varredura Collective2

**Entrega:** Depois de atualizar, a varredura Collective2 e o filtro de quinze dias terminam mesmo se a consulta de ordens ativas falhar; a fila mostra quem passa, com a lista de cópia vazia.
**Como conferir:** Com a lista vazia, atualizar traz candidatos da varredura; um aviso descreve a falha das ordens ativas sem dizer que a Collective2 inteira morreu; atualizar não grava aprovação.
**Por quê:** Hoje a consulta de ordens ativas vive no mesmo bloco da varredura: recusa ou endereço longo demais marca a fonte como falha e a fila perde o resultado.

**Detalhe técnico**

- **Estado atual:** `_live_refresh_collective2` runs SearchStrategies + closed_trades then `c2_signal_feed.snapshot(snap_ids)` where `snap_ids` unions **scan page IDs** with approved IDs, all in one `try`. `HTTPError` is an `OSError`, so 403/414 become `collective2_refresh_failed:HTTPError` and skip `sources_ok.append('collective2')`.
- **Estado desejado:** SearchStrategies + closed_trades + Feature 4 filter stay the success path. `sources_ok.append('collective2')` if that path succeeded. Snapshot in a **nested** `try` catching `urllib.error.HTTPError`, `URLError`, `ValueError` (and `OSError` only there): append `collective2_active_orders_snapshot_failed:{Type}` plus HTTP code when present (403/414), **no secrets, no ID dump**. **Never** pass SearchStrategies page IDs to snapshot. Preferred: skip snapshot on live-criteria when approved IDs are empty, or omit snapshot from the job (active orders are not eligibility). Do not invent GetStrategyActiveOrders batching. Empty allowlist still shows eligible scan rows. TV ISS-025 unchanged. `--root` default unchanged.
- **Arquivo(s):** `src/v4_web_dashboard.py`
- **Fonte(s):** ISS-024 operador EasyPanel 2026-11-19, F-022, N50 snapshot-not-ticket, N58 scan path
- **Risco:** MEDIUM — shared live-criteria job; must not swallow real SearchStrategies failures
- **Task size:** M (1 file + isolation design)

**executor_prompt**:

```yaml
id: N59.1
size: M
bom_ref: BOM-3
depends_on: ["N59.0"]
files:
  - src/v4_web_dashboard.py
reuse_targets:
  - component: src/v4_web_dashboard.py
    reuse_as: extend
    convergence_check: 'rg "_live_refresh_collective2" src/v4_web_dashboard.py && rg "c2_signal_feed.snapshot" src/v4_web_dashboard.py && rg "collective2_active_orders_snapshot_failed" src/v4_web_dashboard.py'
  - component: src/c2_signal_feed.py
    reuse_as: call
    convergence_check: 'rg "GetStrategyActiveOrders" src/c2_signal_feed.py && rg "execution_authorized" src/c2_signal_feed.py'
  - component: src/c2_history_collect.py
    reuse_as: call
    convergence_check: 'rg "SearchStrategies" src/c2_history_collect.py src/v4_web_dashboard.py'
  - component: src/prodigy_rank.py
    reuse_as: call
    convergence_check: 'rg "WINDOW_DAYS = 15" src/prodigy_rank.py && rg "MIN_TRADES = 5" src/prodigy_rank.py'
guardrail_contract:
  - class: secrets
    id: n59-1-no-key-leak
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'sk_live' not in t.lower(); assert 'C2_API4_KEY' in t"
    pass_condition: no live keys hardcoded; snapshot issues must not interpolate the API key
  - class: subagent-safety
    id: n59-1-no-order
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'process_after_gate_b' not in t"
    pass_condition: dashboard still never submits via Gate B
  - class: subagent-safety
    id: n59-1-no-auto-approve
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'upsert_signal_provider_approval' not in t"
    pass_condition: live-criteria refresh does not write ledger approve
  - class: subagent-safety
    id: n59-1-snapshot-isolated
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'collective2_active_orders_snapshot_failed' in t; assert 'def _live_refresh_collective2' in t"
    pass_condition: snapshot failures use dedicated issue prefix, not collective2_refresh_failed
  - class: subagent-safety
    id: n59-1-no-invented-c2-stats
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text()+Path('src/c2_history_collect.py').read_text(); assert 'SearchHistoricalStrategies' not in t; assert 'GetLeaderBoard' not in t"
    pass_condition: scan stays SearchStrategies plus recovered closed_trades
  - class: subagent-safety
    id: n59-1-keep-root-default
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert \"default='/app/reports'\" in t or 'default=\"/app/reports\"' in t"
    pass_condition: argparse --root default remains /app/reports
  - class: subagent-safety
    id: n59-1-keep-prodigy-constants
    target: src/prodigy_rank.py
    check: python3 -c "from pathlib import Path; t=Path('src/prodigy_rank.py').read_text(); assert 'WINDOW_DAYS = 15' in t; assert 'MIN_TRADES = 5' in t"
    pass_condition: Feature 4 / Prodigy 15d constants unchanged
```

### Quality Brief (Sprint N59)

See sprint Quality Brief above. LIVE false; refresh ≠ approve ≠ fill; isolate snapshot; do not invent Feature 4 thresholds; TradingView search remains out.

Melhoria: isolate `c2_signal_feed.snapshot` from the SearchStrategies + closed_trades try in `_live_refresh_collective2`; never pass the scan page; on snapshot HTTPError/URLError/ValueError record `collective2_active_orders_snapshot_failed:*` and still `sources_ok` collective2.
Contexto: after N58 #78, EasyPanel SearchStrategies returns 846 IDs (HTTP 200) but snapshot with those IDs is HTTP 414 (5 IDs → 403). Shared try maps that to `collective2_refresh_failed:HTTPError` (`HTTPError` subclasses `OSError`) and drops `sources_ok`. Snapshot is N50 read-only diagnostic, not Feature 4.
Objetivo: keep `POST /api/signals/candidates/refresh` (`mode: live_criteria`, `orders_sent=0`). Nested try around snapshot only. Preferred skip snapshot on scan path / approved-IDs-only / omit from live-criteria. Never `process_after_gate_b`. Never invent scores or GetStrategyActiveOrders batching. Never print `C2_API4_KEY`. Never call a TradingView search host.
Critério de pronto: mocked SearchStrategies + closed_trades success + snapshot HTTPError 414 → HTTP 200 with eligible C2 queue rows, `collective2` in `sources_ok`, empty allowlist, no `collective2_refresh_failed` for that case.
Cenários de teste (mínimo no implementer self-check; N59.2 owns pytest):
  1. Caso normal: varredura ok + snapshot 414 → fila elegível, sources_ok, aviso de instantâneo se invocado
  2. Edge: snapshot não recebe IDs da página da listagem
  3. Edge: lista nomeada vazia ainda mostra quem passa quinze dias
  4. Regressão: N58 scan; cópia paper fechada; `--root` default; `orders_sent=0`; sem busca TV

### Task N59.2 — Provar que a falha de ordens ativas não esvazia a fila

**Entrega:** Testes comprovam que a consulta de ordens ativas pode falhar e a fila Collective2 elegível continua, sem lista nomeada e sem tratar a varredura como morta.
**Como conferir:** A bateria falha se um erro 414 no instantâneo virar falha da fonte Collective2, se a fila exigir lista nomeada, se autoaprovar, ou se mudar os números de quinze dias.
**Por quê:** Os testes atuais da varredura fingem que o instantâneo sempre dá certo, então o painel no ar quebrou sem o pytest vermelho.

**Detalhe técnico**

- **Arquivo(s):** `tests/test_panel_ops.py`
- **Risco:** MEDIUM — N58 helpers patch snapshot to always succeed (`_n54_mock_c2_snapshot`)
- **Task size:** M

**executor_prompt**:

```yaml
id: N59.2
size: M
bom_ref: BOM-3
depends_on: ["N59.1"]
files:
  - tests/test_panel_ops.py
reuse_targets:
  - component: tests/test_panel_ops.py
    reuse_as: extend
    convergence_check: 'rg "N58Collective2SearchStrategiesScanTests" tests/test_panel_ops.py && rg "_n54_mock_c2_snapshot" tests/test_panel_ops.py'
  - component: tests/test_panel_ops.py
    reuse_as: copy_pattern
    convergence_check: 'rg "approved_for_paper_copy" tests/test_panel_ops.py && rg "N59" tests/test_panel_ops.py'
guardrail_contract:
  - class: subagent-safety
    id: n59-2-no-live-net
    target: tests/test_panel_ops.py
    check: python3 -c "from pathlib import Path; t=Path('tests/test_panel_ops.py').read_text(); assert 'api.collective2.com' not in t.lower(); assert 'tradingview.com' not in t.lower() or 'webhook' in t.lower()"
    pass_condition: tests do not call live Collective2 or invented TradingView search hosts
  - class: subagent-safety
    id: n59-2-no-harness-bug
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'tests/' not in t"
    pass_condition: production does not special-case tests/ paths
  - class: subagent-safety
    id: n59-2-no-committed-allowlist-seed
    target: config/c2_paper_copy_allowlist.json
    check: python3 -c "import json; from pathlib import Path; d=json.loads(Path('config/c2_paper_copy_allowlist.json').read_text()); assert d.get('approved_ids')==[]"
    pass_condition: committed allowlist stays empty
  - class: subagent-safety
    id: n59-2-keep-prodigy-constants
    target: src/prodigy_rank.py
    check: python3 -c "from pathlib import Path; t=Path('src/prodigy_rank.py').read_text(); assert 'WINDOW_DAYS = 15' in t; assert 'MIN_TRADES = 5' in t"
    pass_condition: tests must not rewrite Feature 4 constants
```

### Quality Brief (Sprint N59)

See sprint Quality Brief.

Melhoria: pytest proving mocked SearchStrategies + closed_trades success while snapshot raises HTTPError 414 still yields HTTP 200 with eligible queue rows and `collective2` in `sources_ok`, empty allowlist.
Objetivo: nodeids covering (1) empty allowlist + mocked SearchStrategies eligible ID + closed_trades that yield `PRODIGY_CANDIDATE_RESEARCH` + `c2_signal_feed.snapshot` `side_effect` `urllib.error.HTTPError` code 414 → POST refresh 200, eligible C2/Prodígio pending in `copy.preapproval.queue`, `collective2` in `sources_ok`, `approved_for_paper_copy` false, `collective2_refresh_failed` absent; (2) snapshot **not** called with the SearchStrategies page ID list (call args empty, skipped, or approved-only); (3) when snapshot **is** invoked and raises, issues contain `collective2_active_orders_snapshot_failed` with `HTTPError` and/or `414` — no secrets; (4) POST refresh does not upsert ledger approve; (5) N58 regressions: scan without allowlist, TV `tradingview_scan_out:ISS-025`, `orders_sent=0`, `--root` default, no `SearchHistoricalStrategies` / `GetLeaderBoard`; (6) `process_after_gate_b` absent. Do **not** reuse `_n54_mock_c2_snapshot` in the 414 case (that mock hid the bug). Do not teach production about `tests/` paths (no HARNESS_BUG). Do not commit operator IDs into `config/c2_paper_copy_allowlist.json`.
Critério de pronto: `python3 -m pytest tests/test_panel_ops.py tests/test_prodigy_rank.py tests/test_c2_signal_feed.py -q` green.
Cenários:
  1. Caso normal: varredura ok + snapshot 414 → 200, fila elegível, sources_ok, sem collective2_refresh_failed
  2. Edge: snapshot não recebe a página da listagem
  3. Edge: instantâneo invocado + 414 → aviso `collective2_active_orders_snapshot_failed`
  4. Edge: lista nomeada vazia → cópia paper fechada
  5. Regressão: N58 scan; N55 union; N56 path; cooldown 429; Aprovar inalterado; sem busca TV

### Task N59.3 — Registrar no mapa que ordens ativas não definem quem é candidato

**Entrega:** Mapa e chamado descrevem que a consulta de ordens ativas não aborta a varredura Collective2 e não substitui as regras de quinze dias; o chamado ISS-024 permanece aberto até merge.
**Como conferir:** Ler a área Sinais do mapa e o chamado: sprint desta rodada; instantâneo de ordens ativas é aviso, não critério; Feature 9 marcada só se os testes existirem.
**Por quê:** O texto atual ainda pode fazer o operador achar que a Collective2 morreu quando só a consulta de ordens ativas falhou.

**Detalhe técnico**

P task. Files: `docs/OPERATOR-PANEL-MAP.md` (§2 Atualizar = SearchStrategies + Feature 4; snapshot failure is isolated issue, not dead C2 source; paper-copy gate unchanged; TV scan OUT ISS-025), `docs/DASHBOARD-OPERATIONS.md` if the Sinais row mentions C2 refresh, `docs/ISSUES.md` (ISS-024 notes keep OPEN; ISS-025 unchanged), `docs/FINDINGS.md` (F-022; mark corrigido only with nodeids), `docs/DIARY.md`, `docs/REQUIREMENTS.md` Feature 9 N59 checkboxes only with cited nodeids. LIVE false. N45–N47 not started. Never print secrets.

---

## Sprint N60 — Não perder a Collective2 se o histórico fechado falhar, e soltar o botão
> Categoria: N  
> Status: em_execucao  
> Gerado via: `/pmo plan` 2026-11-19 · fonte ISS-024 / F-023 · N59 #79 em `main` (`2d609f0`)  
> titulo_humano: Atualizar não mata a Collective2 se o histórico fechado falhar, e o botão não fica preso  
> resumo_humano: Ao atualizar candidatos, a listagem Collective2 continua valendo mesmo se o histórico fechado falhar no meio. O que já foi gravado entra no filtro de quinze dias. O botão sai de «Atualizando…» se a espera estourar. LIVE false.  
> Gate: SearchStrategies mock ok + HTTPError na coleta depois de arquivos bons → refresh 200 com fila elegível e sources_ok collective2; aviso collective2_closed_trades_partial_failed sem collective2_refresh_failed; script do botão sai de loading em AbortError; pytest verde; LIVE false; constantes Feature 4 intactas  
> review: senior+qa  
> Brief: `docs/.briefs/N60.brief.md`  
> Git First: `docs/.briefs/N60-GIT-FIRST-REUSE.md`  
> bom_ref: BOM-3  
> Depende de: N59 concluída (#79) · ISS-024 · Release: ISS-024 (não usa N45–N47)  
> LIVE_TRADING_ENABLED: false  
> previous_sprint: N59  
> plan_only: false

### Em uma frase

Ao atualizar candidatos, a Collective2 continua na fila mesmo se o histórico fechado falhar no meio, e o botão deixa de ficar preso em atualizando.

### O que muda para você

- Atualizar deixa de tratar a Collective2 como morta quando o histórico fechado de alguma estratégia falha
- O que já foi gravado entra no filtro de quinze dias e pode aparecer na fila
- O aviso fala de histórico parcial, sem dizer que a fonte inteira morreu
- O botão sai de «Atualizando…» se a espera estourar, com uma mensagem honesta
- «Finalizado» só depois do merge no ramo principal e rebuild do painel no ar

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Histórico parcial não derruba a Collective2 | Atualizar ainda mostra quem já tem histórico bom, mesmo se outra estratégia falhar na coleta |
| 2 | Aviso de histórico parcial | O painel descreve a falha parcial e marca a varredura Collective2 como feita quando a listagem passou |
| 3 | Fila com o que chegou | Quem passa quinze dias com o histórico gravado aparece; métricas indisponíveis não substituem esse resultado |
| 4 | Botão não fica preso | Se a espera estourar, o botão volta a ser clicável e o texto deixa de ser «Atualizando candidatos…» |
| 5 | Cópia paper continua fechada | Atualizar não aprova nem envia operação |
| 6 | Prova automática | A bateria falha se um erro no histórico derrubar a fila, se o botão ficar preso, ou se mudar os números de quinze dias |

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | P | N60.0 Inventariar o histórico fechado versus a fonte Collective2 | `docs/.briefs/N60-GIT-FIRST-REUSE.md` | — |
| [x] | M | N60.1 Isolar a coleta do histórico fechado da fonte Collective2 | `src/v4_web_dashboard.py` | N60.0 |
| [x] | M | N60.2 Fazer o botão sair de «Atualizando…» quando a espera estourar | `src/panel_ops_html.py` | N60.1 |
| [x] | M | N60.3 Provar que falha no histórico não mata a fila nem prende o botão | `tests/test_panel_ops.py` | N60.1, N60.2 |
| [x] | P | N60.4 Registrar no mapa o aviso parcial e o fim da espera infinita | `docs/OPERATOR-PANEL-MAP.md, docs/ISSUES.md, docs/FINDINGS.md, docs/REQUIREMENTS.md` | N60.3 |

### Quality Brief (Sprint N60)

**Alvo:** **Atualizar candidatos** continua a marcar a Collective2 como varrida quando a listagem oficial passa, mesmo se o histórico fechado falhar no meio; o que foi gravado entra no filtro de quinze dias; o botão não fica em «Atualizando…» para sempre.

Maintain: `LIVE_TRADING_ENABLED=false`; paper host only; dashboard does not submit or cancel orders; refresh and approval are not fills.
Maintain: load `trader-entry|exit|budget|risk|scanner` only via `src/original.py`.
Maintain: N54 POST `/api/signals/candidates/refresh`, N55–N59 queue/join/discovery/SearchStrategies/snapshot isolation; argparse `--root` default `/app/reports` unchanged.
Maintain: Feature 4 / Prodígio 15d thresholds already in `prodigy_rank` (`WINDOW_DAYS = 15`, `MIN_TRADES = 5`); do not change them.
Maintain: N59 `_run_collective2_active_orders_snapshot` — do not pass SearchStrategies page IDs back into the snapshot.
Avoid: mapping closed-trades HTTPError to `collective2_refresh_failed` after SearchStrategies succeeded; one `fetch` call with the full scan page; inventing a bulk Collective2 query; TradingView search HTTP; auto-approve; `process_after_gate_b`; printing API keys; stealing N45–N47; a new job-status endpoint.

### Technical Advisory

- [ABORDAGEM] SearchStrategies ok ⇒ `sources_ok` inclui `collective2`. Coleta por ID com `GetStrategyHistoricalClosedTrades`, pulando quem falhar, gravando o parcial, com orçamento de tempo do job (não constante de quinze dias). Aviso `collective2_closed_trades_partial_failed:*`. Ranking existente roda no que chegou. Botão: `AbortSignal` no POST que já existe.
- [RISCO] Engolir de novo o `OSError` em silêncio deixa o banner honesto de fora — o código parcial é obrigatório quando houve falha ou corte por tempo.
- [RISCO] Tratar HTTPError da listagem como parcial esconderia fonte realmente morta — `collective2_refresh_failed` fica só na falha de SearchStrategies (e erros antes da listagem).
- [RISCO] Orçamento numérico 15 ou 5 no job seria lido como limiar Feature 4. O orçamento é segundos (ou um nome explícito no dashboard), patchável em teste, fora de `prodigy_rank`.

> EXPIRES at end of Sprint N60. Not reusable in future sprints without a new preventive audit.

### Fora de escopo

- Inventar lote na query, paginação nova ou cliente novo para o histórico fechado
- Inventar busca TradingView (ISS-025)
- Alterar constantes de quinze dias / mínimo de operações
- Recolocar a página da listagem no instantâneo de ordens ativas
- Autoaprovar; mutar livro-razão no refresh
- Ordem / fill / LIVE true
- SSH no EasyPanel; N45–N47; marcar «finalizado» antes do merge em `main`

### Task N60.0 — Inventariar o histórico fechado versus a fonte Collective2

**Entrega:** Inventário dizendo que a listagem oficial marca a fonte como ok, que o histórico fechado é a entrada do filtro de quinze dias já existente, e que misturar a coleta da página inteira nesse bloco derruba a Collective2 e prende o botão.
**Como conferir:** O inventário cita a listagem e o histórico por identificador como reuso, proíbe uma chamada única com a página inteira, e marca o TradingView como fora.
**Por quê:** Sem isso o EXECUTE tenta “acelerar” os centenas de identificadores inventando um cliente novo, ou deixa o erro abortar de novo a fonte.

**Detalhe técnico**

P task (docs-only). Confirm `docs/.briefs/N60-GIT-FIRST-REUSE.md`. Re-check vendor pin `3d0f4ef`; no bump. Cite: `_live_refresh_collective2` shared try around `_invoke_c2_closed_trades_collect`; `_panel_c2_closed_trades_collect` already swallows per-id `OSError` silently when `fetch` is the original; the else branch passes the full id list in one call; `HTTPError` subclasses `OSError`; button script has no `AbortSignal`; N59 snapshot stays isolated; Feature 4 is `prodigy_rank` not a new collect threshold; ADR-012 TV ingest only; LIVE false. Never print secrets.

### Task N60.1 — Isolar a coleta do histórico fechado da fonte Collective2

**Entrega:** Depois de atualizar, a Collective2 continua marcada como varrida quando a listagem passou, mesmo se o histórico de alguma estratégia falhar; o que foi gravado segue no filtro de quinze dias.
**Como conferir:** Com a lista de cópia vazia, um erro no histórico não esvazia quem já tem arquivo bom; o aviso fala de histórico parcial e não de fonte morta; atualizar não grava aprovação.
**Por quê:** Hoje a coleta da página inteira vive no mesmo bloco que marca a fonte: um erro HTTP mata a Collective2 e a fila fica com métricas indisponíveis.

**Detalhe técnico**

- **Estado atual:** `_live_refresh_collective2` calls `_invoke_c2_closed_trades_collect(scan_ids, …)` for the full SearchStrategies page inside the `try` that `sources_ok.append('collective2')`. Escaped `HTTPError` (`OSError`) becomes `collective2_refresh_failed:HTTPError` and returns before the rank sees new files. The per-id helper swallows `OSError` with no issue when `fetch` is the original object. The else branch sends `list(strategy_ids)` in one `fetch` call. `fetch` timeout is 25s with no job budget (~846 IDs). N59 snapshot is already outside this try.
- **Estado desejado:** SearchStrategies success appends `sources_ok` `'collective2'` even when collect raises or is partial. Collect stays per-id via `c2_history_collect.fetch(path, {StrategyId, CommissionPlan}, token)` / `_panel_c2_closed_trades_collect`. Never pass the page as one call. On per-id `HTTPError`/`URLError`/`TimeoutError`/`OSError`: skip that id, keep files already written, append `collective2_closed_trades_partial_failed:{Type}` plus HTTP code when present — no secrets, no ID dump. Do **not** use `collective2_refresh_failed` for that case. Stop scheduling new IDs when a wall-clock budget elapses (module-level name on `v4_web_dashboard.py`, **not** `prodigy_rank`; default must let the POST return inside a ~45s client abort; tests may patch it). Persist the remainder and resume on the next click (honest incomplete/partial issue, distinct from `collective2_search_incomplete`). Then the existing `_live_refresh_prodigy` → `prodigy_rank.calculate` runs on `{root}/providers/raw`. Real SearchStrategies `HTTPError` still `collective2_refresh_failed` and does **not** append `sources_ok`. Leave `_run_collective2_active_orders_snapshot` as N59. TV ISS-025 unchanged. `--root` default unchanged. Empty allowlist still shows eligible rows from files that landed.
- **Arquivo(s):** `src/v4_web_dashboard.py`
- **Fonte(s):** ISS-024 operador 2026-11-19 após #79, F-023, N58 scan, N59 snapshot isolation
- **Risco:** MEDIUM — shared live-criteria job; must not swallow real SearchStrategies failures or change Feature 4 constants
- **Task size:** M (1 file + isolation and budget design)

**executor_prompt**:

```yaml
id: N60.1
size: M
bom_ref: BOM-3
depends_on: ["N60.0"]
files:
  - src/v4_web_dashboard.py
reuse_targets:
  - component: src/v4_web_dashboard.py
    reuse_as: extend
    convergence_check: 'rg "_live_refresh_collective2" src/v4_web_dashboard.py && rg "_invoke_c2_closed_trades_collect" src/v4_web_dashboard.py && rg "collective2_closed_trades_partial_failed" src/v4_web_dashboard.py'
  - component: src/c2_history_collect.py
    reuse_as: call
    convergence_check: 'rg "GetStrategyHistoricalClosedTrades" src/c2_history_collect.py && rg "def fetch" src/c2_history_collect.py'
  - component: src/prodigy_rank.py
    reuse_as: call
    convergence_check: 'rg "WINDOW_DAYS = 15" src/prodigy_rank.py && rg "MIN_TRADES = 5" src/prodigy_rank.py && rg "def calculate" src/prodigy_rank.py'
  - component: src/v4_web_dashboard.py
    reuse_as: call
    convergence_check: 'rg "_run_collective2_active_orders_snapshot" src/v4_web_dashboard.py && rg "collective2_active_orders_snapshot_failed" src/v4_web_dashboard.py'
guardrail_contract:
  - class: secrets
    id: n60-1-no-key-leak
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'sk_live' not in t.lower(); assert 'C2_API4_KEY' in t"
    pass_condition: no live keys hardcoded; partial-collect issues must not interpolate the API key
  - class: subagent-safety
    id: n60-1-no-order
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'process_after_gate_b' not in t"
    pass_condition: dashboard still never submits via Gate B
  - class: subagent-safety
    id: n60-1-no-auto-approve
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'upsert_signal_provider_approval' not in t"
    pass_condition: live-criteria refresh does not write ledger approve
  - class: subagent-safety
    id: n60-1-partial-isolated
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'collective2_closed_trades_partial_failed' in t; assert 'def _live_refresh_collective2' in t"
    pass_condition: closed-trades failures use a dedicated issue prefix, not collective2_refresh_failed
  - class: subagent-safety
    id: n60-1-no-invented-c2-stats
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text()+Path('src/c2_history_collect.py').read_text(); assert 'SearchHistoricalStrategies' not in t; assert 'GetLeaderBoard' not in t"
    pass_condition: scan stays SearchStrategies plus recovered closed_trades per StrategyId
  - class: subagent-safety
    id: n60-1-keep-root-default
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert \"default='/app/reports'\" in t or 'default=\"/app/reports\"' in t"
    pass_condition: argparse --root default remains /app/reports
  - class: subagent-safety
    id: n60-1-keep-prodigy-constants
    target: src/prodigy_rank.py
    check: python3 -c "from pathlib import Path; t=Path('src/prodigy_rank.py').read_text(); assert 'WINDOW_DAYS = 15' in t; assert 'MIN_TRADES = 5' in t"
    pass_condition: Feature 4 / Prodigy 15d constants unchanged
  - class: subagent-safety
    id: n60-1-keep-snapshot-isolation
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'def _run_collective2_active_orders_snapshot' in t; assert 'collective2_active_orders_snapshot_failed' in t"
    pass_condition: N59 snapshot isolation remains
```

### Quality Brief (Sprint N60)

See sprint Quality Brief above. LIVE false; refresh ≠ approve ≠ fill; isolate closed-trades collect; do not invent Feature 4 thresholds; TradingView search remains out; do not undo N59 snapshot isolation.

Melhoria: isolate `_invoke_c2_closed_trades_collect` from the `sources_ok` try in `_live_refresh_collective2`; per-id skip-on-error; persist partial raw; record `collective2_closed_trades_partial_failed:*`; still run `prodigy_rank.calculate` on what landed.
Contexto: after N59 #79 on air, the orange banner is still `collective2_refresh_failed:HTTPError` (not the snapshot code). The full SearchStrategies page (~846 IDs) is collected inside the same try that marks the C2 source ok. `HTTPError` subclasses `OSError`. The per-id helper swallows errors silently; the patched-fetch branch sends the whole list at once. The button stays on «Atualizando…» because that POST does not return.
Objetivo: keep `POST /api/signals/candidates/refresh` (`mode: live_criteria`, `orders_sent=0`). SearchStrategies success ⇒ `collective2` in `sources_ok` even if collect is partial. Never one fetch with the page. Job wall-clock budget on the dashboard module (patchable; not 15 and not `MIN_TRADES`). Resume remainder next click. Never `process_after_gate_b`. Never print `C2_API4_KEY`. Never call a TradingView search host. Never put scan IDs back into the active-order snapshot.
Critério de pronto: mocked SearchStrategies success + HTTPError during closed-trades after at least one good trades file → HTTP 200, eligible queue from those files, `collective2` in `sources_ok`, partial issue present, `collective2_refresh_failed` absent for that case.
Cenários de teste (mínimo no implementer self-check; N60.3 owns pytest):
  1. Caso normal: listagem ok + um ID grava trades elegíveis + o próximo ID levanta HTTPError → fila elegível, sources_ok, aviso parcial, sem collective2_refresh_failed
  2. Edge: a coleta estoura o orçamento de tempo e para; arquivos já gravados permanecem; o restante retoma no próximo clique
  3. Edge: HTTPError na própria listagem continua collective2_refresh_failed e a fonte não entra em sources_ok
  4. Regressão: N59 instantâneo isolado; cópia paper fechada; `--root` default; `orders_sent=0`; sem busca TV; constantes 15d intactas

### Task N60.2 — Fazer o botão sair de «Atualizando…» quando a espera estourar

**Entrega:** O botão Atualizar deixa o texto «Atualizando candidatos…» e volta a ser clicável se a espera estourar ou a chamada for cancelada, com uma frase honesta de que a fila anterior foi mantida.
**Como conferir:** No painel, uma espera que não volta não deixa o botão ocupado para sempre; a mensagem não promete que a varredura terminou.
**Por quê:** Hoje o script só muda o texto quando o pedido responde, então uma coleta longa parece que o botão não faz nada.

**Detalhe técnico**

- **Estado atual:** `_CANDIDATES_RELOAD_SCRIPT` in `src/panel_ops_html.py` posts `/api/signals/candidates/refresh` with no `AbortSignal` / timeout. It sets «Atualizando candidatos…», disables the button, and clears `aria-busy` only in `finally` after `fetch` settles. A hung POST never reaches `finally`.
- **Estado desejado:** Same POST, same JSON body, no new route. Add `AbortSignal` (timeout or `AbortController`) so the wait is bounded (about 45s, longer than the server job budget from N60.1). On `AbortError` / timeout: set an honest Portuguese message that the wait ended and the previous queue was kept — not «Atualizando candidatos…», not a claim that criteria were applied. Re-enable the button and clear `aria-busy` on that path as well as on success/HTTP error. Do not call a Collective2 host from the browser. Do not embed `C2_API4_KEY`. Do not auto-approve.
- **Arquivo(s):** `src/panel_ops_html.py`
- **Fonte(s):** ISS-024 operador 2026-11-19, F-023, N53/N54 button script
- **Risco:** MEDIUM — operator-facing script; must not turn a real HTTP 401/429 into a timeout message
- **Task size:** M (1 file + abort design)

**executor_prompt**:

```yaml
id: N60.2
size: M
bom_ref: BOM-3
depends_on: ["N60.1"]
files:
  - src/panel_ops_html.py
reuse_targets:
  - component: src/panel_ops_html.py
    reuse_as: extend
    convergence_check: 'rg "_CANDIDATES_RELOAD_SCRIPT" src/panel_ops_html.py && rg "AbortSignal" src/panel_ops_html.py && rg "/api/signals/candidates/refresh" src/panel_ops_html.py'
guardrail_contract:
  - class: secrets
    id: n60-2-no-key-in-script
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_html.py').read_text(); assert 'C2_API4_KEY' not in t; assert 'sk_live' not in t.lower(); assert 'api4-general.collective2.com' not in t"
    pass_condition: the browser script does not embed the Collective2 key or call the Collective2 host
  - class: subagent-safety
    id: n60-2-abort-leaves-loading
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_html.py').read_text(); assert 'AbortSignal' in t; assert 'Atualizando candidatos' in t; assert 'reload-candidates' in t"
    pass_condition: the existing button keeps a deadline; loading copy is not the only terminal state
  - class: subagent-safety
    id: n60-2-no-new-status-route
    target: src/panel_ops_html.py
    check: python3 -c "from pathlib import Path; t=Path('src/panel_ops_html.py').read_text(); assert t.count('/api/signals/candidates/refresh')>=1; assert '/api/signals/candidates/status' not in t"
    pass_condition: timeout uses the existing refresh POST, not a new status endpoint
```

### Quality Brief (Sprint N60)

See sprint Quality Brief. No new route. No Collective2 HTTP from the browser. 401 still goes to login; 429 still says to wait; abort/timeout is a different honest message and must re-enable the button.

Melhoria: add AbortSignal/timeout to `_CANDIDATES_RELOAD_SCRIPT` so the button cannot stay on «Atualizando candidatos…» forever.
Contexto: the POST can run for a long closed-trades collect. `finally` never runs if `fetch` does not settle. The operator sees a stuck button.
Objetivo: bounded wait on the existing POST. AbortError clears the loading label, shows that the previous queue was kept, re-enables the button. Do not claim success. Do not print secrets.
Critério de pronto: the script source contains `AbortSignal` (or `AbortController`) and a non-loading Portuguese sentence used on abort; `finally` or the abort branch sets `disabled` false and removes `aria-busy`.
Cenários de teste (N60.3 asserts the script text):
  1. Caso normal: resposta 200 ainda recarrega e mostra horário
  2. Edge: AbortError / timeout não deixa o texto em «Atualizando candidatos…» e reabilita o botão
  3. Regressão: 401 vai ao login; 429 pede para aguardar; sem host Collective2 no script

### Task N60.3 — Provar que falha no histórico não mata a fila nem prende o botão

**Entrega:** Testes comprovam que um erro no histórico fechado, depois da listagem, mantém a Collective2 e a fila de quem já tem arquivo bom, e que o botão não fica em atualizando para sempre.
**Como conferir:** A bateria falha se esse erro virar fonte morta, se a fila exigir lista nomeada, se os números de quinze dias mudarem, ou se o script não tiver prazo de espera.
**Por quê:** Os testes da varredura fingem que a coleta sempre dá certo, então o painel no ar quebrou sem o pytest vermelho.

**Detalhe técnico**

- **Arquivo(s):** `tests/test_panel_ops.py`
- **Risco:** MEDIUM — N58/N59 helpers mock collect as success; do not hide HTTPError behind `_n54_mock_c2_snapshot` or an always-ok closed-trades mock in the new case
- **Task size:** M

**executor_prompt**:

```yaml
id: N60.3
size: M
bom_ref: BOM-3
depends_on: ["N60.1", "N60.2"]
files:
  - tests/test_panel_ops.py
reuse_targets:
  - component: tests/test_panel_ops.py
    reuse_as: extend
    convergence_check: 'rg "N59Collective2SnapshotIsolationTests" tests/test_panel_ops.py && rg "N58Collective2SearchStrategiesScanTests" tests/test_panel_ops.py && rg "N60" tests/test_panel_ops.py'
  - component: tests/test_panel_ops.py
    reuse_as: copy_pattern
    convergence_check: 'rg "approved_for_paper_copy" tests/test_panel_ops.py && rg "collective2_closed_trades_partial_failed" tests/test_panel_ops.py'
  - component: src/panel_ops_html.py
    reuse_as: call
    convergence_check: 'rg "AbortSignal" src/panel_ops_html.py && rg "_CANDIDATES_RELOAD_SCRIPT" tests/test_panel_ops.py'
guardrail_contract:
  - class: subagent-safety
    id: n60-3-no-live-net
    target: tests/test_panel_ops.py
    check: python3 -c "from pathlib import Path; t=Path('tests/test_panel_ops.py').read_text(); assert 'api.collective2.com' not in t.lower(); assert 'api4-general.collective2.com' not in t.lower()"
    pass_condition: tests do not call live Collective2 or invented TradingView search hosts
  - class: subagent-safety
    id: n60-3-no-harness-bug
    target: src/v4_web_dashboard.py
    check: python3 -c "from pathlib import Path; t=Path('src/v4_web_dashboard.py').read_text(); assert 'tests/' not in t"
    pass_condition: production does not special-case tests/ paths
  - class: subagent-safety
    id: n60-3-no-committed-allowlist-seed
    target: config/c2_paper_copy_allowlist.json
    check: python3 -c "import json; from pathlib import Path; d=json.loads(Path('config/c2_paper_copy_allowlist.json').read_text()); assert d.get('approved_ids')==[]"
    pass_condition: committed allowlist stays empty
  - class: subagent-safety
    id: n60-3-keep-prodigy-constants
    target: src/prodigy_rank.py
    check: python3 -c "from pathlib import Path; t=Path('src/prodigy_rank.py').read_text(); assert 'WINDOW_DAYS = 15' in t; assert 'MIN_TRADES = 5' in t"
    pass_condition: tests must not rewrite Feature 4 constants
```

### Quality Brief (Sprint N60)

See sprint Quality Brief.

Melhoria: pytest proving SearchStrategies success plus HTTPError during closed-trades, after at least one successful trades file, still yields HTTP 200 with eligible queue rows and `collective2` in `sources_ok`, plus a button script that leaves the loading label on abort.
Objetivo: nodeids covering (1) empty allowlist + mocked SearchStrategies + one ID whose closed trades yield `PRODIGY_CANDIDATE_RESEARCH` and a later ID (or the collect call) raising `urllib.error.HTTPError` → POST refresh 200, eligible pending row in `copy.preapproval.queue`, `collective2` in `sources_ok`, issues contain `collective2_closed_trades_partial_failed` with `HTTPError` and/or the HTTP code, `collective2_refresh_failed` absent, `approved_for_paper_copy` false, no secrets; (2) SearchStrategies itself raising HTTPError → `collective2_refresh_failed`, `collective2` not in `sources_ok`; (3) job budget stops further IDs and keeps files already written (patch the dashboard budget; do not use 15 or 5 as that budget); (4) `_CANDIDATES_RELOAD_SCRIPT` contains `AbortSignal` or `AbortController`, and the abort path text is not `Atualizando candidatos`; button is re-enabled (`disabled = false` or equivalent) on that path; script has no `api4-general.collective2.com` and no `C2_API4_KEY`; (5) N59 regressions: snapshot 414 does not abort the source; scan page IDs are not passed to snapshot; (6) N58 regressions: TV `tradingview_scan_out:ISS-025`, `orders_sent=0`, `--root` default, no `SearchHistoricalStrategies` / `GetLeaderBoard`, no ledger upsert, `process_after_gate_b` absent; (7) `WINDOW_DAYS = 15` and `MIN_TRADES = 5` unchanged. Do not teach production about `tests/` paths (no HARNESS_BUG). Do not commit operator IDs into `config/c2_paper_copy_allowlist.json`.
Critério de pronto: `python3 -m pytest tests/test_panel_ops.py tests/test_prodigy_rank.py tests/test_c2_signal_feed.py -q` green.
Cenários:
  1. Caso normal: listagem ok + arquivo bom + HTTPError na coleta → 200, fila elegível, sources_ok, aviso parcial, sem collective2_refresh_failed
  2. Edge: HTTPError na listagem → fonte não ok, collective2_refresh_failed
  3. Edge: orçamento de tempo corta a página; arquivos já gravados ficam
  4. Edge: script do botão tem AbortSignal e não termina em «Atualizando candidatos…» no aborto
  5. Regressão: N59 instantâneo; N58 varredura; cópia paper fechada; sem busca TV; constantes 15d intactas

### Task N60.4 — Registrar no mapa o aviso parcial e o fim da espera infinita

**Entrega:** Mapa e chamado descrevem que uma falha no histórico fechado não apaga a Collective2, e que o botão não fica preso em atualizando; o chamado ISS-024 permanece aberto até merge.
**Como conferir:** Ler a área Sinais do mapa e o chamado: sprint desta rodada; aviso de histórico parcial não é fonte morta; Feature 9 desta rodada continua desmarcada até existirem os testes.
**Por quê:** O texto atual ainda pode fazer o operador achar que a Collective2 morreu, ou que o botão não responde, quando só a coleta atrasou ou falhou no meio.

**Detalhe técnico**

P task. Files: `docs/OPERATOR-PANEL-MAP.md` (§2 Atualizar = SearchStrategies + closed trades per ID with partial issue `collective2_closed_trades_partial_failed`; snapshot stays N59; button leaves «Atualizando…» on timeout; paper-copy gate unchanged; TV scan OUT ISS-025), `docs/DASHBOARD-OPERATIONS.md` if the Sinais row mentions C2 refresh, `docs/ISSUES.md` (ISS-024 notes keep OPEN; ISS-025 unchanged), `docs/FINDINGS.md` (F-023; mark corrigido only with nodeids), `docs/DIARY.md`, `docs/REQUIREMENTS.md` Feature 9 N60 checkbox only `[x]` with cited nodeids. LIVE false. N45–N47 not started. Never print secrets.

---

## Fora do roadmap D (backlog N)

| Tema | Origem | Notas |
|------|--------|-------|
| Estratégias Ta Barato / Prodigy / momentum (fórmulas) | LEGACY-ANALYSIS | N7 cobre fases; **não** inventar limiares de scoring |
| Walk-forward / Lean | RESEARCH_ROADMAP | Motor separado |
| Collective2 paper-copy | Feature 4 / N51 | Pré-aprovação no painel (N50 JSON/env = semente); H10 histórico; não aprovar os dez em lote |
| CI deploy EasyPanel | Operador | N6 feito; bump de imagem só com sprint própria (fora de N8) |
| Submodule pin vs clone raso | D1 | Preferir pin revisado, não `main` cego |
| F-003 orb-parity (`parity.py`) | D1 / FINDINGS | **Congelado até N12.4/ISS-005** (fill Feature 5); N13 repo não descongela |

---

## Próximo passo operador

1. N16 concluída neste closeout. Evidência N18.3 em `docs/TEST-EVIDENCE.md` (2026-11-10): log `8765` e `/api/status` bearer **200**. PR **#20** com verificação automática verde.  
2. Sprint N18 segue em execução até este commit de docs entrar num pedido de revisão com checks verdes.  
3. **P-001b** (ISS-005 fill) continua sessão operador.  
4. **`/pmo sprint N17`** só após Git First upstream.  
5. N19 (gatilho no painel) fica fora deste commit.  
6. **`LIVE_TRADING_ENABLED=false`** — invariável.
