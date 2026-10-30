# Requisitos — Trading Lab

> Gerado em: 2026-10-29
> Status: Em Revisão
> Fonte: adendo técnico de 29/10/2026, que detalha o handoff da mesma data. O snapshot de código na raiz é o MVP de pesquisa mais novo que estava disponível (`ba36049`). Contagens de teste citadas em nomes de ZIP não foram reexecutadas aqui.

---

## 1. Visão Geral

**Descrição**: Sistema modular e multi-mercado (ações EUA, B3 e cripto) para identificar oportunidades de day trade e swing trade, LONG e SHORT quando o mercado permitir, classificar sinais, simular, reconciliar e medir resultado líquido.

**Problema que resolve**: Decisão apressada em cima de backtest isolado, de notícia lida no sentimento, ou de um HTTP 200 tratado como ordem executada. O operador precisa de uma trilha em que cada promoção de estado tenha evidência, e em que rejeição também fique registrada.

**Para quem**: O operador do laboratório, que pesquisa e, só depois, opera em paper.

**Objetivo de negócio**: Errar rápido e barato. A escada é Research, Shadow, Paper limitado, Paper validado. Live permanece desligado. Nenhuma promoção acontece só porque um número de teste subiu ou uma requisição retornou 200.

**Cenário**: LEGADO

---

## 2. Stakeholders

| Nome / Papel | Tipo | Prioridade | O que importa para ele |
|---|---|---|---|
| Operador do laboratório | Decisor, usuário final e patrocinador | Alta | Um pacote único, testado e implantável. Sem sequência de mini-ZIPs e deploys manuais. Sem dinheiro real antes da evidência. |

---

## 3. Usuários e Personas

| Persona | Contexto | Principal frustração (hoje) | Objetivo | Nível técnico |
|---|---|---|---|---|
| Operador do laboratório | Pessoa única que acompanha pesquisa, paper e o que está no EasyPanel | Sinais, filas e HTTP 200 aparecem como se o robô tivesse operado. Várias builds com contagens diferentes, sem uma base canônica comprovada. | Ver o estado real (pesquisa, sombra ou paper), o motivo de cada rejeição e o P&L reconciliado com a corretora, antes de sequer discutir live. | Semi-técnico |

---

## 4. Features (MVP)

O MVP de produto, para este documento, é o laboratório até paper reconciliado. O que o Git já contém é o ciclo de pesquisa. O restante entra como requisito, com o grau de evidência explícito. Não é lista do que já passou.

### Feature 1: Ciclo de pesquisa e shadow

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have
- **Evidência**: Reportado no snapshot importado. O scheduler não importa código de envio de ordem. Pytest desta máquina ainda não rodou.

**Fluxo principal:**
1. O ciclo lê o universo configurado (hoje: AAPL, MSFT, BBAS3, BBDC4, ITUB4, BTCBRL, ETHBRL).
2. Coleta dado público, gera decisão e preview de risco em modo Research/Shadow.
3. Grava relatórios e um manifesto cuja integridade o dashboard só exibe se os componentes conferem.
4. Nenhuma ordem sai.

**Fluxo alternativo:**
- Fonte externa indisponível: o estado fica `FAILED_OR_BLOCKED` ou `PARTIAL_OR_BLOCKED`, visível, sem ordem.

**Fluxo de exceção:**
- `LIVE_TRADING_ENABLED` diferente de false: o processo recusa e sai.
- Manifesto antigo não pode continuar parecendo sucesso depois de ciclo falho.

**Regras de negócio:**
- `OK_RESEARCH_ONLY` prova execução do radar naquela amostra, não prova paper.
- ORB e mean reversion permanecem em Research/Shadow. ORB não vira estratégia principal de paper.

**Critérios de aceite:**
- [x] `pytest` com evidência em CI (GitHub Actions run [41041762290](https://github.com/ig0rayres/trading_lab/actions/runs/41041762290), commit `f597f8b`, job **test** verde). Contagens 224–395 de ZIPs não substituem isso.
- [ ] Com live desligado, um ciclo termina sem ordem enviada.
- [ ] Ciclo falho não deixa manifesto de sucesso anterior visível como confiável.

### Feature 2: Gate A — autenticidade do sinal

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have
- **Evidência**: Decidido. Webhook TradingView retornou HTTP 200 e `PAPER_GATEWAY_QUEUE_ONLY` em relato: isso é fila, não ordem.

**Fluxo principal:**
1. Entra evento de mercado, notícia, TradingView ou sinal externo, com procedência.
2. O gate confere assinatura ou segredo, fonte, timestamp UTC, frescor, schema, símbolo, direção e idempotência.
3. Sinal autêntico segue. Sinal inválido para, com código de motivo, sem ordem.

**Fluxo de exceção:**
- Token ausente, inválido ou curto demais; payload malformado; replay; timestamp futuro; entrega duplicada; ticker não reconhecido.

**Regras de negócio:**
- Verdadeiro significa autêntico, fresco, coerente e permitido. Não significa que vai dar lucro.
- Segredos não entram em documentação nem em log. O requisito de tamanho citado no serviço foi token de webhook com pelo menos 32 caracteres e segredo de copy com pelo menos 24. Os valores não são registrados aqui.

**Critérios de aceite:**
- [ ] Sinal inválido é rejeitado e nenhuma ordem é criada.
- [ ] O mesmo evento entregue duas vezes não abre duas posições.
- [ ] A trilha guarda motivo, entrada sanitizada e timestamp.

### Feature 3: Gate B — risco e permissão de paper

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have
- **Evidência**: Decidido como política. Não é recomendação de operar no teto.

**Fluxo principal:**
1. Sinal que passou no Gate A entra na política da estratégia e no risco.
2. O gate só libera paper se mercado, calendário, dado, stop, spread, liquidez e limites globais estiverem aceitos, e se o kill switch estiver livre.
3. A fase da estratégia (research, shadow, paper limitado, paper validado) precisa permitir aquela ordem.

**Regras de negócio:**
- Capital paper de referência: R$ 5.000.
- Risco inicial: R$ 50 por operação (1%). Teto configurável: R$ 100 por operação.
- No máximo 3 posições simultâneas.
- Risco agregado até R$ 200.
- Perda diária R$ 200. Perda semanal R$ 500.
- Sem alavancagem.
- Prodigy experimental: teto inicial separado de R$ 20, só paper limitado, sem promoção automática.
- SHORT só se o mercado e a corretora permitirem.
- Calendário de NY e B3, feriado e horário de verão fazem parte do gate. O relato `NY weekdays, holidays not filtered` é bloqueio aberto, não detalhe cosmético.

**Critérios de aceite:**
- [ ] Ordem que estoura qualquer limite acima é recusada com motivo, sem ida à corretora.
- [ ] Kill switch acionado impede ordem nova.
- [ ] Fora da sessão ou em feriado não tratado, o sinal não vira ordem.

### Feature 4: Catálogo de estratégias e promoção de estado

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have
- **Evidência**: Decidido o contrato. Fórmulas numéricas de momentum, “Tá Barato Demais” e Prodigy não foram recuperadas. Não inventar limiar.

**Famílias:**
- News First: notícia é hipótese, com timestamp, veículo, tickers, categoria, frescor e confiança. Não é compra ou venda pelo tom do texto. Rejeitar notícia velha, ticker indefinido, rumor sem fonte, movimento já no preço, divergência com o preço e liquidez ruim.
- Momentum: força, rompimento e continuidade com barra fechada. Limiares numéricos finais não estão decididos até saírem do código.
- Tá Barato Demais: nome interno de desconto/distorção, por mercado (EUA, B3, cripto), com parâmetros próprios. Não é “caiu, compra”. Fórmula, percentis e gatilhos não foram recuperados.
- Signal copy: normalizar sinal de terceiro. Mérito econômico é um filtro depois da autenticidade. Collective2 observado: 10 candidatos, nenhum com histórico de seis meses verificado, nenhum aprovado para paper-copy, zero ordens.
- Prodigy 15 dias: candidatos fortes e recentes, janela móvel de 15 dias, mínimo de 5 operações em pelo menos 3 dias, retorno líquido positivo, drawdown e consistência. Fórmula de pontuação ainda pendente. Risco paper inicial R$ 20.
- ORB e mean reversion: shadow/research. ORB 1R e 2R reportados com média R e profit factor negativos. Sem edge intraday validado.

**Estados persistentes:** RESEARCH, SHADOW, PAPER_LIMITED, PAPER_VALIDATED. LIVE desabilitado. Um estado não sobe por lucratividade aparente nem por HTTP 200.

**Critérios de aceite:**
- [ ] ORB não é selecionável como estratégia principal de paper.
- [ ] Nenhum provedor Collective2 entra em copy enquanto `approved_for_paper_copy` for falso.
- [ ] Estratégia sem fórmula recuperada não ganha limiar inventado neste repositório.

### Feature 5: Paper ponta a ponta

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have para homologar. Não está comprovado no snapshot.
- **Evidência**: Módulos de gateway, webhook, ledger e atividades Alpaca existem no código. A ponte completa não foi homologada. Conta paper citada em captura não prova envio de ordem.

**Fluxo principal:**
1. Sinal autêntico passa nos dois gates.
2. A fila de paper envia à conta Alpaca Paper, nunca à conta live.
3. A corretora devolve aceite, rejeição, fill parcial ou fill cheio.
4. O reconciliador grava ids (incluindo prefixos `nf-` e `demo-` quando existirem), posição e P&L.
5. Reinício do processo não duplica ordem nem perde o ledger.

**Fluxo de exceção:**
- Timeout, rejeição da corretora, fill parcial, cancelamento, posição que já existia, API fora.

**Critérios de aceite:**
- [ ] Um sinal de fixture gera ordem paper, fill, ledger e posição coerente com a corretora.
- [ ] Um sinal inválido no mesmo ambiente não gera ordem.
- [ ] Duplicata não reabre posição.
- [ ] Depois de reinício, ledger e posição continuam consistentes.
- [ ] `PAPER_GATEWAY_QUEUE_ONLY` sozinho não conta como este critério cumprido.

### Feature 6: Observabilidade e parada

- **Persona**: Operador do laboratório
- **Prioridade**: Must-have

**Fluxo principal:**
1. O operador vê último ciclo, fila, sinais aceitos e rejeitados, ordens paper e P&L.
2. Log não contém segredo.
3. Existe parada de emergência que impede ordem nova.

**Critérios de aceite:**
- [ ] Dashboard, se publicado, exige autenticação. O MVP de pesquisa atual não publica porta.
- [ ] Kill switch é visível e testável sem dinheiro real.

---

## 5. Integrações

| Sistema | Tipo | Direção | Autenticação | Fallback |
|---|---|---|---|---|
| Dados públicos de ação e cripto (Yahoo e Binance citados no MVP) | API de leitura | Entrada | Nenhuma no MVP de pesquisa | Ciclo marcado como falho ou parcial. Sem ordem. |
| Alpaca Paper | API de corretora paper | Bidirecional | Chave paper, fora do repositório | Sem chave, não há submit. Nunca usar chave live. |
| TradingView | Webhook | Entrada | Segredo do webhook | Pedido sem segredo válido é rejeitado no Gate A. |
| Collective2 | Pesquisa e possível copy | Entrada | Acesso ainda não verificado | Nenhum provedor aprovado. Copy permanece fechado. |
| News | Feed de notícias | Entrada | Conforme a fonte, sem gravar segredo | Ausência de notícia não autoriza ordem. |
| day-trader-skill | Biblioteca de reuso | Entrada de código | Não se aplica | Sem o checkout pinado em `vendor/`, não afirmar paridade. Não reescrever entry, exit, budget, risk e scanner. |
| EasyPanel (`trading-lab` e `trading-lab-webhook`) | Deploy já existente | Operação | Fora deste repo | Não substituir esses dois serviços com este snapshot. App novo, se existir, é separado e sem volume compartilhado. |
| Postgres | Banco previsto | Persistência | DSN fora do repo | Estado atual das migrations não foi verificado nesta importação. |

**Autenticação do sistema**: um operador. Segredos de webhook e de paper ficam no ambiente, nunca no Git. Não há cadastro público.

---

## 6. Requisitos Não-Funcionais

| Categoria | Requisito | Meta |
|---|---|---|
| Segurança | Live desligado. Segredo fora de log, ZIP e markdown. | Falha fechada se a flag de live não for false. |
| Integridade | Idempotência de sinal e de ordem. Manifesto não mente após falha. | Duplicata não cria segunda posição. |
| Auditoria | Toda rejeição tem código, timestamp e entrada sanitizada. | Trilha recuperável depois do restart. |
| Calendário | Sessão EUA e B3, feriado e horário de verão. | Sinal fora da sessão não vira ordem. |
| Entrega | Um pacote consolidado, com teste e rollback. | Sem série de micro-deploys para o operador executar. |
| Performance | Tempo de resposta | A definir. Não há meta numérica no handoff. |
| Disponibilidade | Uptime | A definir. O requisito atual é ciclo observável e parada, não um percentual. |
| Escalabilidade | Usuários simultâneos | Um operador. |

---

## 7. Fora de Escopo

- Operação com dinheiro real (LIVE).
- Tratar ORB como edge validado ou como estratégia principal de paper.
- Assinar ou copiar provedor Collective2. Os dez candidatos observados estão reprovados para paper-copy.
- Inventar percentil, RSI, volume ou score de “Tá Barato Demais”, momentum ou Prodigy que não esteja no código recuperado.
- Substituir os serviços EasyPanel atuais por este ZIP.
- Publicar dashboard sem autenticação.
- Somar contagens de teste de ZIPs diferentes e apresentá-las como uma suíte única.

---

## 8. Premissas

- A base de código deste repositório é o snapshot de pesquisa v4 importado em 29/10/2026, não o container que porventura ainda roda no EasyPanel.
- A pasta `trading-lab-v4-mvp-implantavel` é anterior e não é a base.
- Paper de referência continua R$ 5.000, com os tetos da seção do Gate B.
- Reuso do `day-trader-skill` continua obrigatório onde aquelas funções já existirem. O vendor não veio no ZIP.
- “Reportado como implementado” não é o mesmo que homologado.

---

## 9. Dúvidas em Aberto

| # | Dúvida | Impacto | Status |
|---|---|---|---|
| 1 | Fórmula, percentis e gatilhos de “Tá Barato Demais” | Alto | Aberta. Não inventar. |
| 2 | Limiares numéricos finais de momentum | Alto | Aberta até leitura do código, sem promover a regra. |
| 3 | Fórmula de empate, drawdown e consistência do Prodigy 15d | Médio | Aberta. |
| 4 | Qual imagem está de fato no EasyPanel (`trading-lab` e webhook), com SHA | Alto | Aberta. Export não veio. |
| 5 | Commit pinado do `day-trader-skill` em `vendor/` | Alto | Aberta. |
| 6 | Prazo de calendário para a homologação paper | Médio | Aberta. Nenhum prazo foi decidido. |
| 7 | Postgres: há migration e dado, ou só intenção de infra | Médio | Aberta. |

---

## 10. Mapa do Legado

### Stack Atual

- **Frontend**: dashboard de leitura em Python, sem framework web de produto. Não publicar sem autenticação.
- **Backend**: Python 3.12 (`python:3.12-slim`), scripts em `src/`, entrada `scripts/run.sh`. Sem `requirements.txt` ou `pyproject.toml`.
- **Banco**: Postgres citado como infra prevista. Não verificado neste clone.
- **Testes**: `pytest.ini` + CI `.github/workflows/ci.yml`; suíte verde na Actions (2026-10-30, run 41041762290).
- **Git**: repositório local `master`, commit `ba36049`. Sem remote. O GitHub `Jakeschincariol/day-trader-skill` é dependência de reuso, não este repositório.

### Features Existentes

| Feature | Manter | Modificar | Remover | Observação |
|---|---|---|---|---|
| Scheduler de pesquisa, 15 min, universo de 7 símbolos | sim | | | Não envia ordem. |
| Pipeline, risco preview, shadow, manifesto com hash | sim | | | Pesquisa apenas. |
| Webhook, News First, copy, gateway paper, ledger | sim | sim | | Existem no código. Não estão ligados ao ciclo do MVP e não estão homologados. |
| ORB como candidato de pesquisa | sim | | | Fica em shadow. Resultado reportado é negativo. |
| Serviços EasyPanel atuais | sim | | | Não substituir com este pacote. |

### Migração de Dados

- **Volume**: relatórios sintéticos de smoke no repo. Volume real de `/app/reports` e banco do EasyPanel não foram copiados.
- **Estratégia**: coexistência. Este repo é a base Git. Os serviços já publicados continuam até uma release única, supervisionada.
- **Riscos**: operar em cima do ZIP errado; achar que fila é fill; promover ORB; perder o vendor upstream.

### Evidências numéricas que permanecem relato

Estas linhas não são aprovação. Servem para não perder o que já foi medido.

| ID | O que foi visto | Leitura |
|---|---|---|
| H01–H03 | 5.944 tickers, 897 com dado, 271 setups, 95 sinais ORB | Detecção, não execução. |
| H04–H06 | ORB 1R e 2R com média R e profit factor negativos; replay AMAT desfavorável | Sem edge intraday validado. |
| H08 | Webhook HTTP 200, `PAPER_GATEWAY_QUEUE_ONLY` | Fila, não ordem. |
| H09 | Radar `OK_RESEARCH_ONLY`, 12 candidatos, 0 ordens | Pesquisa naquela amostra. |
| H10 | Collective2, 10 candidatos, 0 elegíveis | Copy fechado. |
| H11–H12 | Reconciliação `nf-`/`demo-` e atividades Alpaca reportadas | P&L com a corretora ainda não fechado. |

---

## Histórico de Revisões

| Data | Versão | Alteração | Autor |
|---|---|---|---|
| 2026-10-29 | 0.1 | Versão inicial a partir do adendo de 29/10/2026 e do snapshot importado | Analista de Requisitos (IA) |
