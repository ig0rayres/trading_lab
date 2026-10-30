# Arquitetura — Trading Lab

> Gerado em: 2026-10-29
> Fase: 3 — Arquitetura de Solucao
> Status: Aprovada
> Baseado em: docs/REQUIREMENTS.md
> Design: `docs/design/DESIGN.md` nao existe. O operador escolheu seguir a arquitetura sem a fase de design. Tokens visuais do dashboard ficam para `/designer planejar`.

---

## 1. Visao Geral

**Tipo**: Monolito modular em um codigo, com dois processos.

**Justificativa**: Um operador, um repositorio e uma imagem. O ciclo de pesquisa e o webhook ja sao comandos diferentes do mesmo `scripts/run.sh`. Separar mercados em microservicos aumentaria deploy sem reduzir o risco principal, que e tratar fila ou HTTP 200 como ordem. A escada Research, Shadow, Paper limitado e Paper validado vive num estado persistente dentro deste monolito. Live permanece desligado.

Os servicos EasyPanel `trading-lab` e `trading-lab-webhook` que ja existem nao sao substituidos por este snapshot. Um processo novo, se for criado, usa volume proprio.

---

## 2. Stack Tecnologica

| Camada | Tecnologia | Versao | Justificativa |
|--------|-----------|--------|---------------|
| Frontend | Dashboard de leitura em Python | o que ja esta em `src/v4_web_dashboard.py` | Nao ha produto web publico. Sem Next.js neste corte. |
| Backend | Python | 3.12-slim, como no Dockerfile | O laboratorio inteiro ja esta nesta stack. Reescrever em NestJS ou Laravel jogaria fora o snapshot importado. |
| Banco de dados | Arquivos JSON no volume de reports agora. PostgreSQL quando o ledger de paper for persistido | versao a cargo de `/arquiteto dados` | Pesquisa ja grava JSON. Postgres foi a infra prevista no handoff para o que precisa sobreviver a restart de ordem. |
| ORM | Nenhum neste corte | — | Schema fica na fase de dados. |
| Cache | Nenhum | — | Um operador, ciclo de 15 minutos. |
| Fila | Fila de paper dentro do processo | — | Nao introduz Redis antes de o Gate B existir. `PAPER_GATEWAY_QUEUE_ONLY` continua sendo fila, nao fill. |
| Storage | Volume `/app/reports` | — | Relatorios de pesquisa. Nao compartilhar com os servicos EasyPanel atuais. |
| Auth | Segredo de webhook e chave paper no ambiente | tamanho minimo ja decidido: webhook >= 32, copy >= 24 | Nao ha cadastro de usuarios. |
| Deploy | Docker, comando do `Dockerfile` atual | imagem `python:3.12-slim` | CI e topologia nova ficam em `/devops planejar` e `/devops infra`. |
| CI/CD | GitHub Actions | `.github/workflows/ci.yml` | CI-only (pytest + docker build). CD EasyPanel fora deste corte. |
| Monitoring | Relatorio de ciclo e kill switch | — | Sem ferramenta externa escolhida. |

Perfil Beesy `nestjs` / `laravel` nao se aplica. O codigo e Python de scripts, sem `pyproject.toml`.

---

## 3. Estrutura de Pastas

O codigo permanece onde ja esta. Nao ha geracao de arvore nova nesta fase.

```
src/                          # modulos Python atuais
scripts/run.sh                # um entrypoint, varios comandos
config/universe.json          # universo do ciclo de pesquisa
tests/                        # pytest
docs/REQUIREMENTS.md
docs/ARCHITECTURE.md
```

Dois processos, mesma imagem:

- Pesquisa: `v4-scheduler` (comando padrao do Dockerfile).
- Webhook: `tv-webhook`, so quando o Gate A estiver fechado e o segredo existir no ambiente.

Contrato entre modulos, neste monolito, e arquivo e funcao publica, nao REST CRUD. Um modulo nao importa o cliente da corretora de outro modulo para "atalhar" o gate.

---

## 4. Diagrama de Modulos

```
Fontes (mercado, noticia, TradingView, copy)
        |
        v
[market-data] ----> relatorio de mercado
        |
        v
[research-cycle] --> manifesto de pesquisa (sem ordem)
        |
        +---- [strategy-catalog] politica e fase da estrategia
        |
        v
[signal-gate-a] autenticidade
        |
        v
[risk-gate-b] limites e calendario
        |
        v
[paper-gateway] --> Alpaca Paper --> fill / reject
        |
        v
[observability] dashboard, ledger visivel, kill switch
```

`LIVE` nao aparece no diagrama. Nao ha ramo de ordem real.

### 4.1 Assessment de Modulos

| Modulo | Complexidade | Risco | Flag | Depende de | Desbloqueia | Ordem |
|--------|-------------|-------|------|------------|-------------|-------|
| market-data | 2 — feeds e saneamento | 2 — APIs externas | foundation | — | research-cycle, strategy-catalog | 1 |
| research-cycle | 2 — ciclo, manifesto, bloqueio de live | 1 — interno | foundation | market-data | observability, gates | 2 |
| strategy-catalog | 3 — familias e promocao de estado | 2 — regra de negocio | complexo | market-data | risk-gate-b | 3 |
| signal-gate-a | 3 — autenticidade e idempotencia | 3 — webhook e segredo | complexo | — | risk-gate-b, paper-gateway | 4 |
| risk-gate-b | 3 — limites, sessao, kill switch | 2 — decisao de capital | complexo | signal-gate-a, strategy-catalog | paper-gateway | 5 |
| paper-gateway | 3 — ordem, fill, reconciliacao | 3 — corretora e custodia | complexo | signal-gate-a, risk-gate-b | observability | 6 |
| observability | 2 — leitura e parada | 2 — pode expor estado se publicado | — | research-cycle, paper-gateway | — | 7 |

**Legenda flags:**

- `complexo` = Complexidade 3 ou Risco 3. Mini design doc obrigatorio quando entrar em sprint.
- `foundation` = dependido por 3 ou mais modulos.

**Sequencia recomendada**: risk-first, aprovada em 29/10/2026. Fundacao que ja existe (dados e ciclo) primeiro, para nao reescrever. Em seguida o catalogo so com a politica de fase, sem inventar formula. Gate A e Gate B antes de qualquer submit. Paper por ultimo entre os modulos de execucao. Dashboard depois, porque uma tela cedo nao reduz o risco de ordem falsa.

### Modulo: market-data

- **Responsabilidade**: ler preco publico de acao EUA, B3 e cripto e recusar dado atrasado, vazio ou fora de ordem.
- **API publica**: comandos `v4-equity-feed`, `v4-crypto-feed`, `v4-import-prices`. Saida: documento de mercado com erros explicitos.
- **Depende de**: nenhum | **Desbloqueia**: research-cycle, strategy-catalog
- **Origem**: ADAPTAR (`src/v4_equity_feed.py`, `src/v4_crypto_feed.py`, `src/v4_market_data_import.py`)
- **Complexidade**: 2 — saneamento de serie, nao CRUD
- **Risco**: 2 — fonte externa
- **Flag**: foundation

### Modulo: research-cycle

- **Responsabilidade**: orquestrar pesquisa e shadow, gravar manifesto integro, recusar live.
- **API publica**: `v4-scheduler`, `v4-run-once`. Saida: JSON de ciclo com `orders_sent = 0`.
- **Depende de**: market-data | **Desbloqueia**: observability e a leitura dos gates
- **Origem**: ADAPTAR (`src/v4_scheduler.py`, `src/v4_run_once.py`)
- **Complexidade**: 2
- **Risco**: 1
- **Flag**: foundation

### Modulo: strategy-catalog

- **Responsabilidade**: manter a fase de cada familia (Research, Shadow, Paper limitado, Paper validado) e a regra do que cada uma pode fazer. News First, momentum, Ta Barato Demais, copy, Prodigy 15d, ORB e mean reversion.
- **API publica**: consulta interna `fase(estrategia) -> permissao`. ORB e mean reversion nao retornam permissao de paper principal.
- **Depende de**: market-data | **Desbloqueia**: risk-gate-b
- **Origem**: ADAPTAR o que ja existe; formula ausente nao e criada aqui
- **Complexidade**: 3
- **Risco**: 2
- **Flag**: complexo

### Modulo: signal-gate-a

- **Responsabilidade**: decidir se o evento e autentico, fresco e unico.
- **API publica**: entrada com procedencia; saida aceite ou rejeicao com codigo. Nao envia ordem.
- **Depende de**: nenhum modulo de negocio | **Desbloqueia**: risk-gate-b, paper-gateway
- **Origem**: ADAPTAR (`src/tradingview_webhook.py` e equivalentes)
- **Complexidade**: 3
- **Risco**: 3
- **Flag**: complexo

### Modulo: risk-gate-b

- **Responsabilidade**: aplicar capital, tetos, calendario, short e kill switch.
- **API publica**: decisao `paper permitido` ou rejeicao com motivo. Limites: R$ 5.000 de referencia, R$ 50 por operacao, teto R$ 100, 3 posicoes, agregado R$ 200, perda diaria R$ 200, semanal R$ 500, Prodigy R$ 20, sem alavancagem.
- **Depende de**: signal-gate-a, strategy-catalog | **Desbloqueia**: paper-gateway
- **Origem**: ADAPTAR (`src/v4_decision_risk.py`, `src/portfolio_risk_v4.py`)
- **Complexidade**: 3
- **Risco**: 2
- **Flag**: complexo

### Modulo: paper-gateway

- **Responsabilidade**: unica porta que fala com a Alpaca Paper. Grava ack, fill, cancelamento e reconciliacao (`nf-`, `demo-`).
- **API publica**: so aceita pacote que ja passou nos dois gates. Saida: estado da ordem e do ledger.
- **Depende de**: signal-gate-a, risk-gate-b | **Desbloqueia**: observability
- **Origem**: ADAPTAR (`src/paper_gateway.py`, `src/v4_alpaca_reconcile.py`, `src/v4_realized_ledger.py`)
- **Complexidade**: 3
- **Risco**: 3
- **Flag**: complexo

### Modulo: observability

- **Responsabilidade**: mostrar ciclo, rejeicoes, ordens paper e P&L. Parada de emergencia.
- **API publica**: `v4-dashboard`, somente com autenticacao se houver porta publicada.
- **Depende de**: research-cycle, paper-gateway | **Desbloqueia**: nenhum
- **Origem**: ADAPTAR (`src/v4_web_dashboard.py`)
- **Complexidade**: 2
- **Risco**: 2
- **Flag**: —

---

## 5. Decisoes Tecnicas (ADRs)

### ADR-001: Permanecer em Python 3.12

- **Status**: Aprovada
- **Contexto**: O snapshot importado, os testes e o Dockerfile ja sao Python. O handoff manda nao reiniciar.
- **Decisao**: O monolito continua em Python 3.12. Nao ha backend NestJS nem Laravel ao lado.
- **Alternativas consideradas**:
  1. Reescrever em NestJS — descartada porque apaga o laboratorio ja testado no pacote e nao existe equipe TypeScript neste corte.
  2. Extrair um FastAPI so para servir HTTP — descartada porque o entrypoint atual e script e o webhook ja tem processo proprio. FastAPI entra na reversao, nao agora.
  3. Status quo sem documentar a fronteira dos modulos — descartada porque os modulos de paper existem soltos e podem ser chamados fora do gate.
- **Trade-offs aceitos**: as skills Beesy de Nest e Laravel nao cobrem este codigo. Contratos entre modulos nao sao OpenAPI de CRUD.
- **Condicao de reversao**: se surgir um segundo produto com varios usuarios e API publica, revisar FastAPI na borda, sem jogar fora o nucleo de pesquisa.
- **Consequencias**: implementacao segue `src/` e `scripts/run.sh`.

### ADR-002: Dois processos, uma imagem

- **Status**: Aprovada
- **Contexto**: O EasyPanel ja mostrou um servico de radar e outro de webhook. O MVP de pesquisa manda nao substituir nenhum dos dois.
- **Decisao**: Mesma arvore de codigo. Processo de pesquisa no scheduler. Processo de webhook separado, sem volume compartilhado com o que ja esta no ar, ate uma release unica.
- **Alternativas consideradas**:
  1. Um processo so, webhook dentro do scheduler — descartada porque um ciclo de 15 minutos nao deve segurar ingestao, e o handoff ja separou os servicos.
  2. Um repositorio por servico — descartada porque duplica gate e risco.
  3. Trocar os servicos atuais por este ZIP — descartada no requisito.
- **Trade-offs aceitos**: dois entrypoints exigem disciplina para nao configurar chave paper no processo de pesquisa.
- **Condicao de reversao**: se o webhook passar a ser so fila interna do scheduler, o segundo processo pode ser desligado.
- **Consequencias**: `LIVE_TRADING_ENABLED=false` nos dois. Pesquisa nao recebe chave de corretora.

### ADR-003: JSON agora, Postgres so no ledger de paper

- **Status**: Aprovada no nivel de escolha. Schema nao.
- **Contexto**: Relatorios de pesquisa ja sao arquivo. O handoff cita Postgres para o que precisa de reconciliacao duravel. O detalhe de tier e tabela e da fase de dados.
- **Decisao**: Pesquisa continua em JSON no volume de reports. PostgreSQL e o banco do ledger de paper, quando essa fase comecar. Sem cache e sem fila externa.
- **Alternativas consideradas**:
  1. Postgres para todo evento de pesquisa agora — descartada porque aumenta operacao antes do paper estar homologado.
  2. SQLite unico para tudo — descartada para o ledger que precisa conviver com a infra ja citada, mas pode ser reaberta na fase de dados se o operador nao tiver Postgres.
  3. Nao persistir ordem — descartada porque restart tem de manter ledger.
- **Trade-offs aceitos**: dois meios de persistencia. A fase `/arquiteto dados` precisa dizer como o JSON e o Postgres se encontram.
- **Condicao de reversao**: se o paper for adiado por muito tempo, Postgres nao sobe.
- **Consequencias**: esta arquitetura nao define tabela, tier nem backup.

### ADR-004: Risk-first e formula nao inventada

- **Status**: Aprovada
- **Contexto**: ORB reportado sem edge. Formulas de Ta Barato Demais, momentum e Prodigy nao foram recuperadas. HTTP 200 ja foi confundido com execucao.
- **Decisao**: Implementar e fechar Gate A e Gate B antes de submit paper. Estrategia sem formula recuperada nao ganha limiar novo. ORB permanece em shadow.
- **Alternativas consideradas**:
  1. Experience-first, dashboard antes dos gates — descartada pelo operador em 29/10/2026.
  2. Preencher limiares ausentes com valores plausiveis — descartada pelo requisito.
  3. Ligar paper no codigo que ja existe, porque o modulo esta no repositorio — descartada porque presenca de modulo nao e homologacao.
- **Trade-offs aceitos**: o catalogo fica incompleto de proposito ate achar a formula no codigo ou num ZIP posterior.
- **Condicao de reversao**: se o codigo atual ja tiver a formula, ela entra por leitura, nao por invencao.
- **Consequencias**: sprint futura de paper depende dos gates, nao do visual.

### ADR-005: Reuso do day-trader-skill

- **Status**: Aprovada, checkout ainda ausente
- **Contexto**: `ENGINEERING_RULES.md` manda reusar entry, exit, budget, risk e scanner. O ZIP nao trouxe `vendor/`.
- **Decisao**: Nao reimplementar essas funcoes. O pin do commit upstream e pre-requisito antes de mudar scanner.
- **Alternativas consideradas**:
  1. Copiar a logica para `src/` — descartada pela regra do projeto.
  2. Ignorar o upstream — descartada.
- **Trade-offs aceitos**: parte do radar fica bloqueada ate o vendor existir.
- **Condicao de reversao**: nenhuma enquanto a licenca e o contrato do upstream servirem.
- **Consequencias**: `src/original.py` continua sendo a porta. Sem SHA pinado, nao ha paridade declarada.

---

## 6. Integracoes

| Servico | Proposito | Abordagem | Fallback |
|---------|-----------|-----------|----------|
| Yahoo / Binance publicos | Preco de pesquisa | Leitura no market-data | Ciclo `FAILED_OR_BLOCKED` ou `PARTIAL_OR_BLOCKED`. Sem ordem. |
| Alpaca Paper | Unica corretora deste corte | So o paper-gateway, conta paper | Sem chave, nao ha submit. Chave live e recusa. |
| TradingView | Entrada de sinal | Webhook no signal-gate-a | Segredo invalido: rejeicao, sem ordem. |
| Collective2 | Pesquisa de provedor | Fora do caminho de ordem | Nenhum provedor aprovado. Copy fechado. |
| News | Hipotese, nao gatilho de compra | strategy-catalog / News First | Sem feed, nao autoriza ordem. |
| day-trader-skill | Funcoes de scanner e risco ja existentes | Vendor pinado | Sem checkout, nao reescrever. |
| EasyPanel atual | Continua no ar, intocado | Nao faz parte do deploy deste snapshot | Release unica, supervisionada, no futuro. |

---

## 7. Seguranca

### 7.1 Classificacao de Dados

| Dado | Sensibilidade | Modulo responsavel | Protecao |
|------|--------------|-------------------|----------|
| Chave Alpaca Paper | Alta | paper-gateway | Ambiente, nunca no Git, ZIP ou log |
| Segredo de webhook e de copy | Alta | signal-gate-a | Ambiente. Tamanho minimo ja decidido. Valor nao documentado |
| Sinal e payload | Media | signal-gate-a | Persistir versao sanitizada |
| Relatorio de pesquisa | Baixa | research-cycle | Volume de reports, sem segredo |
| Ledger e P&L paper | Alta | paper-gateway | Persistencia duravel. Sem conta live |

### 7.2 Fronteiras de Confianca

| Origem | Destino | Protocolo | Auth | Validacao | Rate Limit |
|--------|---------|-----------|------|-----------|------------|
| TradingView | signal-gate-a | HTTPS webhook | Segredo | Schema, frescor, idempotencia | A definir na implementacao do gate |
| paper-gateway | Alpaca Paper | HTTPS | Chave paper | Resposta de ack e fill | Retry idempotente |
| market-data | Fonte publica | HTTPS | Nenhuma | Barra fechada, vazio, ordem temporal | Falha visivel, sem ordem |
| Operador | observability | HTTP local ou autenticado | Auth se houver porta | So leitura, mais kill switch | Nao publicar sem auth |
| Processo | Volume de reports | Arquivo | Permissao do container | Manifesto com hash | Nao se aplica |

Nao ha fronteira com conta live.

### 7.3 Top 3 Vetores de Ataque

1. **Webhook sem segredo ou com replay** → Impacto: ordem paper indevida → Mitigacao: signal-gate-a rejeita e o paper-gateway nem e chamado.
2. **Flag de live ou chave live no ambiente** → Impacto: dinheiro real → Mitigacao: `run.sh` e o scheduler recusam live true. Paper-gateway so aceita endpoint paper.
3. **Dashboard aberto** → Impacto: vazamento de posicao e P&L → Mitigacao: sem porta publica no MVP de pesquisa. Porta futura exige autenticacao.

### 7.4 Requisitos de Seguranca por Modulo

| Modulo | Auth requerido? | Rate limit? | Input validation critico? | Dados sensiveis? |
|--------|----------------|-------------|--------------------------|------------------|
| market-data | Nao | Falha fechada na fonte | Sim | Nao |
| research-cycle | Nao | Nao | Sim, universo e paths | Nao |
| strategy-catalog | Nao | Nao | Sim, fase da estrategia | Nao |
| signal-gate-a | Sim, segredo | Sim | Sim | Sim |
| risk-gate-b | Herda o gate A | Nao | Sim, limites | Sim, tamanhos de risco |
| paper-gateway | Sim, chave paper | Retry idempotente | Sim | Sim |
| observability | Sim, se publicado | Nao | Sim, nao ler manifesto cru | Sim, se mostrar P&L |

---

## 8. Banco de Dados e Infraestrutura de Dados

> Gerado pelo Arquiteto de Dados (Fase 4). Detalhe em `docs/DATABASE.md`.

### 8.1 BD Principal

- **Escolhido**: PostgreSQL da instância que o operador já tem. Versão não foi fixada neste corte. Pesquisa continua em arquivo JSON.
- **Justificativa**: um operador, ledger pequeno, ACID para fill e restart. O handoff já previa Postgres. MariaDB não tem evidência na infra. SQLite foi descartado para não criar um terceiro arquivo de ordem ao lado de uma instância que já existe.

### 8.2 Tier de Infraestrutura

- **Tier**: 1 — Single Node, na instância existente. Nenhum servidor novo.
- **Justificativa**: um operador, sem meta de alta disponibilidade, ledger de ordens e não de candles. Réplica e sharding não reduzem o risco de ordem falsa.
- **Componentes**:

| Componente | Tecnologia | Config |
|------------|-----------|--------|
| BD Primary | PostgreSQL já existente | Um nó. Sem réplica neste corte |
| BD Replica | — | Fora do Tier 1 |
| Connection Pool | Pool do driver Python | Pequeno, um processo. Sem PgBouncer |
| Cache | — | Nível 1 não adiciona cache |
| Failover | Manual | O da instância que já existe |

### 8.3 Composicao

- **Nivel**: 1 — o Postgres do ledger e os arquivos JSON da pesquisa. Sem banco complementar.
- **Bancos complementares**: nenhum.
- **Justificativa**: Valkey e ClickHouse não mudam o ledger. Nível 3 fica fora para um operador só.

### 8.4 Seguranca de Dados

- **Conexao app-BD**: TLS quando o host não for local. Socket local no mesmo host é aceitável. Credencial fora do Git.
- **Credenciais**: usuário dedicado, só DML nas tabelas do ledger. Senha no ambiente, não neste documento.
- **Encryption at rest**: a da instância já existente. Não desligar.
- **Backups**: o backup que essa instância já tiver. Se não houver, o mínimo a confirmar é um dump diário. PITR não foi verificado.

---

## 9. Observabilidade

- **Logs**: texto do processo, sem segredo e sem payload cru de webhook.
- **Metricas**: ultimo ciclo, sinais aceitos e rejeitados, ordens paper, motivo de rejeicao, kill switch.
- **Tracing**: nao ha ferramenta distribuida neste corte.
- **Error tracking**: nao ha Sentry decidido. Falha de ciclo aparece no JSON de status.

---

## 10. Decisoes Tecnicas por Modulo

### market-data

**Anti-patterns a evitar:**
- Tratar barra incompleta como barra fechada.
- Inventar preco quando a fonte falha.

**Decisoes de implementacao:**
- Erro de fonte vira estado visivel do ciclo.
- Calendario de NY e B3, feriado e horario de verao entram antes de qualquer sinal intraday ser elegivel. O relato de feriado nao filtrado continua aberto.

**Edge cases conhecidos:**
- Ticker sem dado, candle fora de ordem, preco zero.
- Universo fixo tem vies de sobrevivencia. Pesquisa registra isso. Nao vira ordem.

**Integracoes criticas:**
- Entrega documento para research-cycle e strategy-catalog. Nao chama paper-gateway.

### research-cycle

**Anti-patterns a evitar:**
- Importar modulo de envio de ordem.
- Deixar manifesto de sucesso antigo visivel depois de falha.

**Decisoes de implementacao:**
- `LIVE_TRADING_ENABLED` diferente de false encerra o processo.
- `orders_sent` deste ciclo permanece 0.

**Edge cases conhecidos:**
- Timeout de ciclo. Symlink no caminho do manifesto e recusado.

**Integracoes criticas:**
- Chama market-data e a avaliacao de risco em modo pesquisa. Nao chama paper-gateway.

### strategy-catalog

**Anti-patterns a evitar:**
- Promover estrategia porque o backtest isolado ficou bonito.
- Criar percentil ou RSI que nao esteja no codigo recuperado.
- Colocar ORB como estrategia principal de paper.

**Decisoes de implementacao:**
- Cada familia tem fase persistente.
- Copy Collective2 permanece fechado enquanto nenhum provedor estiver aprovado.
- Prodigy, se um dia entrar, nasce em paper limitado com teto de R$ 20.

**Edge cases conhecidos:**
- Conflito de dois sinais no mesmo simbolo.
- Noticia duplicada ou ja refletida no preco.

**Integracoes criticas:**
- Responde ao risk-gate-b com a permissao da fase. Nao envia ordem.

### signal-gate-a

**Anti-patterns a evitar:**
- Aceitar HTTP 200 como prova de ordem.
- Gravar o segredo no log.

**Decisoes de implementacao:**
- Rejeicao tem codigo, timestamp e entrada sanitizada.
- Reentrega do mesmo evento nao cria segundo registro ativo.

**Edge cases conhecidos:**
- Token curto, ausente ou trocado. Timestamp futuro. Payload sem simbolo.

**Integracoes criticas:**
- So o resultado aceite segue para risk-gate-b.

### risk-gate-b

**Anti-patterns a evitar:**
- Operar no teto como se o teto fosse meta.
- Ignorar kill switch, feriado ou short indisponivel.

**Decisoes de implementacao:**
- Limites do requisito sao politica, aplicados antes do gateway.
- Estrategia em shadow nunca recebe `paper permitido`.

**Edge cases conhecidos:**
- Terceira posicao ja aberta. Perda diaria estourada. Stop ausente.

**Integracoes criticas:**
- Unica saida positiva vai para paper-gateway.

### paper-gateway

**Anti-patterns a evitar:**
- Enviar ordem que nao passou pelos dois gates.
- Usar host ou chave de conta live.
- Tratar fila como fill.

**Decisoes de implementacao:**
- Idempotencia por id de evento, inclusive prefixos `nf-` e `demo-`.
- Restart relê o ledger antes de aceitar trabalho novo.

**Edge cases conhecidos:**
- Fill parcial, reject, timeout, posicao que ja existia.

**Integracoes criticas:**
- Unico modulo com cliente Alpaca Paper.

### observability

**Anti-patterns a evitar:**
- Ler status do manifesto sem checar o hash dos componentes.
- Publicar porta sem autenticacao.

**Decisoes de implementacao:**
- Kill switch e uma acao explicita, testavel sem dinheiro real.
- P&L mostrado so com a mesma fonte do ledger, nao com numero de pesquisa.

**Edge cases conhecidos:**
- Ciclo parcial. Ledger ainda vazio.

**Integracoes criticas:**
- Le research-cycle e paper-gateway. Nao escreve ordem.

---

## Candidatos a Reuso

Nenhum modulo deste laboratorio entra na biblioteca Beesy agora. O reuso externo obrigatorio e o `day-trader-skill`, no sentido inverso: este repo consome, nao publica template.

---

## 11. Artefatos Gerados

- [x] `docs/ARCHITECTURE.md` (este arquivo — `/arquiteto planejar`)
- [x] Secao "Decisoes Tecnicas por Modulo"
- [x] Secao 8 detalhada + `docs/DATABASE.md` (`/arquiteto dados`)
- [ ] `.cursor/rules/*.mdc` (`/arquiteto padroes`)
- [ ] `.cursor/skills/` do projeto (`/arquiteto padroes`)
- [ ] CI, hooks e Docker alem do Dockerfile ja importado (`/devops planejar`)
- [ ] `docs/INFRASTRUCTURE.md` (`/devops infra`)
- [ ] `docs/design/DESIGN.md` nao foi feito. Dashboard visual continua em aberto.

---

## Mapa de Dependencias

### Ordem de implementacao

1. market-data
2. research-cycle
3. strategy-catalog, lendo `strategy_states`
4. signal-gate-a, gravando `signal_events`
5. risk-gate-b, gravando `risk_decisions` e lendo `control_flags`
6. paper-gateway, gravando `paper_orders`, `paper_fills`, `positions`, `ledger_entries`
7. observability, so leitura

### Matriz de impacto

| Modulo alterado | Impacta |
|----------------|---------|
| market-data | research-cycle, strategy-catalog |
| research-cycle | observability |
| strategy-catalog | risk-gate-b |
| signal-gate-a | risk-gate-b, paper-gateway, observability |
| risk-gate-b | paper-gateway |
| paper-gateway | observability |
| control_flags / kill switch | risk-gate-b, paper-gateway |

O webhook HTTP nao cria `paper_orders`. Quem cria e o paper-gateway, e so com `decision = paper_allowed`.

---

## Historico de Revisoes

| Data | Versao | Alteracao | Autor |
|------|--------|-----------|-------|
| 2026-10-29 | 0.1 | Arquitetura aprovada: Python, dois processos, risk-first | Arquiteto de Solucoes (IA) |
