# Rascunho — ondas até a plataforma operacional (contrato v0.3)

> Status: **rascunho de planejamento** · `plan_only: true`  
> Gerado: 2026-11-11 · planner (Rock PLAN) · intake `docs/.briefs/MVP-FINAL-AUDIT.intake.md`  
> **Este arquivo não entra no roteiro.** Não altera `docs/ROADMAP.md`, `docs/ISSUES.md`, `docs/REQUIREMENTS.md` nem a sessão da frente. Sem commit.  
> Frente atual: `front/n18-closeout` (PR #21, só closeout N18). A Onda 0 abre **outra** frente.  
> Próximo ID livre: **N20**. **N19 já existe** (N19.1–N19.2 feitas no commit local `3d26a13`; N19.3–N19.4 abertas) — incorporada, não duplicada.  
> Revisão: aguarda Fable / verificador de plano no pai. Sem carimbo de auditoria neste rascunho.

---

### Em uma frase

A plataforma fica operacional quando todos os critérios de aceite do contrato (Features 1–11 e os requisitos não-funcionais que já têm meta) estiverem conferíveis por você no painel e na conta demo — sem inventar corretora, fórmula ou ordem real.

### O que muda para você

- Você passa a ter uma definição fechada de “pronto”: só o que o contrato já pediu, nada a mais.
- O trabalho preso (contrato v0.3 e o painel que já grava gatilho) sai desta frente de closeout e vai para um pedido de revisão próprio, sem misturar com o N18.
- Três decisões suas (contas demo, origem das fórmulas, método do ajuste) ficam **fora** das tarefas de código: sem resposta, o mercado ou a família ficam barrados com motivo visível — a plataforma não inventa.
- Rebuild da imagem só em release nomeada, no máximo um por pacote; documento sozinho não rebuilda.

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Definição de plataforma operacional só com o contrato | A seção 1 abaixo lista cada critério; nada além disso entra como exigência |
| 2 | Sete ondas com sprints N20+ e o resto do N19 | Cada onda tem título, frase, tarefas e o que fecha na matriz |
| 3 | Gates seus separados do código | Três decisões; cada uma diz o que destrava e o que acontece se você não responder |
| 4 | Tabela de rastreio critério → sprint | A seção 9 cobre todo `[ ]` e `[x]` do contrato |
| 5 | Contagem de rebuilds | A seção 8: documento = zero; no máximo um rebuild por release |

---

## 0. Como ler este rascunho

- **Categoria:** programa de Sprints N (melhoria + domínio já desenhado no contrato v0.3). Não é Sprint F: as lacunas já estão na matriz do intake e no §12 da arquitetura.
- **Ordem dura:** fechar o ciclo da ordem e o fill (ADR-007) **antes** de ligar envio autônomo; o trabalhador da fila mora no mesmo serviço do painel (ADR-009); dois serviços EasyPanel, nunca um terceiro.
- **Invariantes:** conta real desligada; nenhum limiar inventado; ORB e mean reversion fora de paper; Collective2 fechado; reuso do skill de day trade pelo módulo original, sem reescrever entrada/saída/orçamento/risco/scanner; simulador local não é fill; HTTP 200 ou fila não é ordem executada.

### Leituras

| Artefato | Trecho / linhas |
|----------|-----------------|
| `docs/.briefs/MVP-FINAL-AUDIT.intake.md` | Contrato vigente, matriz, decisões do operador |
| `docs/REQUIREMENTS.md` | Features 1–6, critérios `[x]`/`[ ]`, §6 não-funcionais (v0.1 neste worktree) |
| `docs/ROADMAP.md` | Índice D1–N18; N12.4/N12.5 abertas; N17 planejada; N18 em execução |
| `docs/ISSUES.md` | ISS-005 parcial, ISS-007, P-001b, P-003 |
| `docs/FINDINGS.md` | F-003 aberto/congelado |
| `docs/TEST-EVIDENCE.md` | Submit MSFT 2026-11-02 e NVDA 2026-11-03; fill pendente; N18.3 8765/200 |
| `docs/HOMOLOGATION.md` | Passo fill Feature 5; SHA da imagem vs HEAD |
| `docs/COMMAND-PANEL.md` | Painel v1 leitura; fila ≠ fill |
| `docs/DASHBOARD-OPERATIONS.md` | `v4-ops`; dois apps; Bearer/HTTPS |
| `docs/RELEASE-MVP-OP-1.0.md` | Política 1 rebuild / release |
| `scripts/v4_ops_main.sh` | Supervisor: painel + pesquisa; **sem** trabalhador da fila |
| Contrato v0.3 (git, só leitura, commit `3d26a13` / `front/n16-8-panel`) | `docs/REQUIREMENTS.md` Features 7–11; `docs/ARCHITECTURE.md` §12 ADR-006/007/009/010; `docs/DATABASE.md` §6; `docs/api-spec.yaml` 0.2.0; `docs/ROADMAP.md` Sprint N19; `docs/ISSUES.md` ISS-009; `docs/design/DESIGN.md` telas Entrar / Central / Sinais |

### Contratos afetados

- HTTP 0.2.0 (ainda não no `main`): leitura e alteração de gatilhos, mercado e fase; mais tarde login e tela de sinais.
- Ledger: colunas de mercado e âncoras, histórico de gatilho, identificador da corretora, fill e P&L só de fill.
- EasyPanel: continua só `trading-lab` e `trading-lab-webhook`. CMD do app principal permanece o layout `v4-ops`.
- Conta real: nenhum endpoint, botão ou host novo.

### Assumido

- Você **ainda não aprovou** gravar este plano no roteiro; até lá isto é só rascunho.
- Nomes das contas demo de B3, cripto e forex **não** foram ditos (ADR-010).
- Origem das fórmulas de Tá Barato e momentum no upstream **não** foi confirmada.
- Método do ajuste automático (Feature 11) **não** foi escolhido.
- O commit `3d26a13` mistura produto com lixo de sessão; o resgate leva só o contrato e o código N19.1–N19.2 (lista no detalhe técnico de N20.1).
- Dúvida 5 (pin do skill) já tem SHA no pin de vendor deste repo; a Onda 0 só pede conferência da imagem no EasyPanel (dúvida 4).

---

## 1. O que é “plataforma totalmente operacional”

Só o que o contrato já exige. **Não entra:** SLA de tempo de resposta, percentual de uptime, cadastro de estratégia nova, Collective2, ORB em paper, ordem com dinheiro real, limiar inventado, terceiro serviço.

### 1.1 Núcleo Must-have (Features 1–10)

A plataforma está operacional quando **você** consegue conferir, sem Exec no EasyPanel no dia a dia:

1. Pesquisa e sombra rodam sem ordem, com manifesto honesto (Feature 1 — já `[x]`).
2. Sinal falso ou repetido não vira posição (Feature 2 — já `[x]`).
3. Limite, parada geral e sessão recusam ordem com motivo (Feature 3 checkboxes já `[x]`; calendário B3/feriado e âncoras únicas ainda faltam — ver 1.3).
4. Família sem fórmula recuperada **não** ganha número inventado; ORB e Collective2 fora de paper (Feature 4 — já `[x]`).
5. Há **fill real** na conta demo + posição coerente; fila e HTTP 200 não contam (Feature 5 — único `[ ]` da v0.1).
6. Você vê ciclo, fila, sinais, ordens e parada (Feature 6 — já `[x]` na leitura).
7. Sinal válido vira ordem na conta **demo** sozinho; âncora estourada para; perda do dia/semana no teto para até o próximo período; destino sempre paper; reinício não duplica (Feature 7 — todos `[ ]`).
8. Você entra com login, altera âncoras, liga/desliga estratégia, aciona parada; cada mudança fica registrada; a plataforma não afrouxa âncora sozinha (Feature 8 — todos `[ ]`).
9. Lista de sinais com origem, destino e motivo; ranking Prodígio e o que copiou; barrado mostra gate e âncora (Feature 9 — todos `[ ]`).
10. Resultado por estratégia e total **só** de fill confirmado; ordem sem fill fora; valores brutos rotulados (Feature 10 — todos `[ ]`).

### 1.2 Should-have (Feature 11)

Sugestão rotulada como sugestão; ajuste só em parâmetro que já existe, na faixa original; histórico com antes/depois/motivo e desfazer; ajuste nunca mexe âncora. **Depende** de fill real e da sua escolha de método. Sem isso a plataforma **já pode** operar no núcleo 1.1; a Feature 11 permanece `[ ]` de propósito.

### 1.3 Não-funcionais com meta (contam)

| Categoria | Meta do contrato | Já está? |
|-----------|------------------|----------|
| Segurança | Live desligado; segredo fora de log | Sim (invariante) |
| Integridade | Duplicata não abre segunda posição | Sim (Feature 2) |
| Auditoria | Rejeição com código, data e trilha após restart | Parcial: trilha existe; a tela (Feature 9) falta |
| Calendário | Sessão EUA **e B3**, feriado e horário de verão; sinal fora não vira ordem | Não: hoje a sessão é NYSE em dia útil, feriado não filtrado |
| Entrega | Um pacote com teste e rollback; sem micro-deploy | Política de release deste plano |
| Disponibilidade | Ciclo observável e parada (não é percentual) | Sim (Feature 6) |
| Escalabilidade | Um operador | Sim |

**Não contam** (contrato diz “a definir”, logo não viram sprint): tempo de resposta numérico; percentual de uptime.

### 1.4 Ordem de construção da arquitetura (§12.3) — não é exigência nova, é o *como*

1. Gravar identificador e estado da corretora; acompanhar até fill, cancelamento ou expiração.
2. Perda do dia e da semana só desses fills — aí o retrato pode dizer verificado.
3. Laço em B3, cripto e forex **só** se a conta demo daquele mercado devolver posição, ordem e fill.
4. Risco lê as âncoras gravadas pelo painel.
5. Trabalhador da fila no mesmo supervisor do painel.
6. Login para quem altera gatilho.

Envio autônomo **depois** de 1–2. Sem conta nomeada por você, o mercado fica barrado com motivo visível (ADR-010).

---

## 2. Gates do operador (não são tarefas de código)

Tabela para o agente; você lê os três blocos abaixo.

| ID | Decisão | O que destrava | Se você não responder |
|----|---------|----------------|------------------------|
| G-MKT | Nome da conta **demo** de B3, de cripto e de forex (três respostas, pode ser “ainda não” por mercado) | Onda 4 (N27): ligar o laço naquele mercado | O mercado permanece **barrado**, com motivo visível no painel; **nenhuma** ordem sai por aquele mercado; o nome **não** será inventado |
| G-FORM | Onde está a fórmula de Tá Barato e a de momentum no upstream (ou “não existe”) | Continuação da N17 depois do Git First | A família fica **fora de paper**, em pesquisa/sombra; critério Feature 4 “não inventar limiar” permanece cumprido |
| G-AJUSTE | Método do ajuste automático (o que é erro, frequência, quando desfazer) | Onda 6 (N28) | Não nasce tabela de ajuste; sugestões continuam rotuladas como pesquisa; Feature 11 fica `[ ]` |

**O que estes gates não são:** o fill da ordem paper já enviada (P-001b) e o SHA da imagem no EasyPanel. Isso são **tarefas suas** na Onda 0, porque a conta Alpaca paper e o painel já existem.

**Quando responder:** pode ser agora, em paralelo com qualquer onda. G-MKT atrasado **não** impede Ondas 0–3. G-FORM atrasado **não** impede o núcleo Must-have. G-AJUSTE atrasado **não** impede Features 1–10.

**Pergunta objetiva para G-MKT (quando for responder):** para cada mercado (B3, cripto, forex), o nome da conta demo que devolve posição, ordem aberta e fill — ou a frase “este mercado fica barrado”. Cripto **pode** ser a Alpaca paper se você disser isso; o plano não assume.

---

## 3. Mapa das ondas

```
Onda 0  N20 resgate + suas tarefas (fill, SHA, banco)
   │
   ├─ G-MKT / G-FORM / G-AJUSTE (paralelo, não bloqueiam 0–3)
   │
Onda 1  N19.3–N19.4 + N21     ← ADR-007 (ciclo da ordem e fill no ledger)
   │
Onda 2  N22 + N23             ← âncoras honestas + trabalhador no v4-ops (ADR-009)
   │                            envio autônomo continua DESLIGADO
Onda 3  N24 + N25 + N26       ← login, sinais, performance só de fill (F8–F10)
   │
Onda 4  N27                   ← F7 nos mercados cuja conta você nomeou (G-MKT)
   │
Onda 5  N17                   ← Tá Barato/momentum só com G-FORM
   │
Onda 6  N28                   ← Feature 11 só com G-AJUSTE e fill real
```

Caminho crítico Must-have: **0 → 1 → 2 → 3 → 4**. Ondas 5 e 6 não travam o núcleo.

---

## Onda 0 — Resgate do trabalho preso e bloqueios seus

> titulo_humano: Contrato e gatilhos no Git; fill e SHA na sua mesa  
> Sprints: **N20** (nova). N19 **não** é refeita: só se publica o que já está `[x]`.  
> Rebuild: **zero** nesta onda. O código entra num pedido de revisão; a imagem espera a release da Onda 1.

### Em uma frase

O contrato que você aprovou em 3 de novembro e o painel que já grava gatilho saem do commit local e viram um pedido de revisão; você fecha o fill da ordem paper e anota qual imagem está no ar.

### O que muda para você

- O closeout N18 (PR #21) não mistura contrato v0.3 nem migration de gatilho.
- Você deixa de depender de um commit que nunca foi enviado.
- Sem o fill da ordem paper, performance e aprendizado continuam sem dado real — essa sessão é sua, nesta onda.

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Pedido de revisão só com contrato v0.3 e gatilhos N19.1–N19.2 | Abrir a frente nova e ver Features 7–11 + telas de gatilho, sem o resto do N19 |
| 2 | SHA da imagem que está no EasyPanel | Anotar no evidência o hash que o painel de deploy mostra, lado a lado com o commit |
| 3 | Fill da ordem paper + posição coerente | Na corretora paper: quantidade preenchida e posição; no laboratório: linha de evidência, sem tratar fila como fill |

---

## Sprint N20 — Publicar o contrato e o painel que já altera gatilho

> Categoria: N  
> Status: planejada  
> titulo_humano: Contrato v0.3 e gatilhos do painel num pedido de revisão  
> Gate: pedido de revisão aberto numa frente **nova**; Features 7–11 visíveis no contrato; escrita de gatilho exige sessão de operador (Bearer sozinho = recusado); `LIVE_TRADING_ENABLED=false`; **0 rebuild**  
> Issue: ISS-009 (corpo ainda só no commit `3d26a13`) + P-001b + dúvida 4  
> review: senior+qa  
> Depende de frente: **não** usar `n18-closeout`

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | N20.1 Resgatar contrato v0.3 e código N19.1–N19.2 numa frente própria | `/git` + `/dev` | — |
| [ ] | P | N20.2 Anotar o SHA da imagem no EasyPanel | operador | — |
| [ ] | P | N20.3 Fechar o fill da ordem paper já enviada | operador | — |
| [ ] | P | N20.4 Marcar o critério de fill no contrato só depois da evidência | docs | N20.3 |
| [ ] | P | N20.5 Confirmar que o Postgres do laboratório tem o ledger | operador | — |

### Task N20.1 — Resgatar o contrato e os gatilhos presos

**Entrega:** Um pedido de revisão, em frente nova, com o contrato v0.3 e o código que já deixa o painel gravar parada, âncoras e mercado — sem o acompanhamento da ordem (isso é Onda 1).
**Como conferir:** No pedido, Features 7–11 existem; a alteração de gatilho recusa Bearer sozinho; ORB não sobe para paper; conta real sem botão.
**Por quê:** Esse trabalho está num checkpoint local que nunca foi enviado; misturá-lo no closeout N18 esconde o que já foi feito.

**Detalhe técnico**

**executor_prompt**:
```yaml
id: N20.1
size: M
depends_on: []
files:
  - docs/REQUIREMENTS.md
  - docs/ARCHITECTURE.md
  - docs/DATABASE.md
  - docs/api-spec.yaml
  - docs/design/DESIGN.md
  - docs/db-schema.dbml
  - docs/ISSUES.md
  - docs/ROADMAP.md
  - docs/.briefs/N19.brief.md
  - migrations/002_triggers_up.sql
  - migrations/002_triggers_down.sql
  - src/ledger_migrate.py
  - src/ledger_store.py
  - src/v4_web_dashboard.py
  - tests/test_ledger_migration.py
  - tests/test_panel_triggers.py
reuse_targets:
  - component: commit 3d26a13 (N19.1–N19.2 only)
    reuse_as: reuse
    convergence_check: git show 3d26a13 --stat
guardrail_contract:
  - class: subagent-safety
    id: n20-1-no-n18-mix
    target: docs/ROADMAP.md
    check: this task runs on a new front, not front/n18-closeout
    pass_condition: n18-closeout worktree remains docs-only closeout
  - class: subagent-safety
    id: n20-1-live-lock
    target: Dockerfile
    check: LIVE_TRADING_ENABLED=false
    pass_condition: live flag remains false
executor_prompt: |
  Open a dedicated git front from current main (after or beside PR #21; do not commit on n18-closeout).
  Bring ONLY product slices from 3d26a13: REQUIREMENTS v0.3, ARCHITECTURE §12, DATABASE §6,
  api-spec 0.2.0, DESIGN.md, db-schema.dbml, ISS-009, ROADMAP N19 block, N19.brief.md,
  migrations/002_*, ledger_migrate/ledger_store patches, v4_web_dashboard PATCH triggers,
  tests/test_ledger_migration.py + test_panel_triggers.py, panel-triggers skill/rules if present.
  EXCLUDE: .cursorsession*, .beesy stamp logs, .cursor session caches, unrelated N18 closeout.
  Do not implement N19.3–N19.4 here. Do not enable demo_operation_on. Do not rebuild EasyPanel.
  N19.1 and N19.2 stay marked done; N19.3–N19.4 stay open on that front.
```

### Task N20.2 — Anotar o SHA da imagem no EasyPanel

**Entrega:** A dúvida “qual imagem está no ar” deixa de ser aberta: você registra o hash dos dois apps.
**Como conferir:** Uma linha na folha de evidência com o SHA de `trading-lab` e o de `trading-lab-webhook`, sem colar segredo.
**Por quê:** Sem isso, homologação compara o Git com um container desconhecido.

**Detalhe técnico:** operador no EasyPanel; cruzar com `git rev-parse` do `main` implantado; dúvida 4; 0 rebuild.

### Task N20.3 — Fechar o fill da ordem paper já enviada

**Entrega:** A ordem paper que já foi aceita (MSFT e/ou NVDA) chega a fill com posição coerente, ou é cancelada e substituída por um sinal que preencha.
**Como conferir:** Na corretora, quantidade preenchida ≠ 0 e posição visível; no laboratório, linha de evidência. Ordem `new`/`accepted` **não** conta.
**Por quê:** Feature 5 é o único critério aberto da v0.1 e o ADR-007 manda ter fill real antes de tratar o painel como suficiente para mandar ordem sozinha.

**Detalhe técnico:** P-001b / ISS-005 / N12.4; host paper only; sem segredo no Git; reconcile read-only; `broker_reconciled` false continua válido.

### Task N20.4 — Marcar o critério de fill no contrato só depois da evidência

**Entrega:** O quadradinho de fill da Feature 5 vira `[x]` somente com a linha de evidência da tarefa anterior.
**Como conferir:** Você abre o contrato e vê o fill marcado, com data da sessão, não um HTTP 200.
**Por quê:** Marcar antes é mentir o critério.

**Detalhe técnico:** N12.5; `docs/REQUIREMENTS.md` Feature 5; `docs/TEST-EVIDENCE.md`; depende de N20.3.

### Task N20.5 — Confirmar que o banco do laboratório tem o ledger

**Entrega:** A dúvida “Postgres é intenção ou fato” ganha resposta sua: o banco do EasyPanel tem as tabelas do ledger (e, depois do merge da Onda 1, receberá a migration 002).
**Como conferir:** Você confirma que migrate já rodou neste ambiente (N8) e anota. Sem essa confirmação, gatilho no painel não tem onde gravar.
**Por quê:** Dúvida 7 do contrato; o código assume o banco que você já tem.

**Detalhe técnico:** sem dump de dado real no Git; sem DSN.

**Lacunas que a Onda 0 fecha:** Feature 5 fill `[ ]` (se N20.3 ok); dúvida 4; dúvida 7; publicação de F7–F11 no Git (ainda `[ ]` de comportamento); ISS-009 visível no `main` após merge. **Não fecha** N19.3–N19.4.

---

## Onda 1 — Ciclo da ordem e fill no ledger (ADR-007)

> titulo_humano: A ordem deixa rastro até o fill, antes de operar sozinha  
> Sprints: **N19** (resto: N19.3–N19.4) + **N21**  
> Depende de: merge da N20 na frente de produto  
> Rebuild: **1** — release **MVP-OP-1.2** (ciclo da ordem). Primeiro rebuild desta linha.  
> Envio autônomo: **permanece desligado.**

### Em uma frase

Depois desta onda, cada ordem paper tem número da corretora, estado final (fill, cancelamento ou expiração) e P&L só de fill — ainda sem o robô mandar ordem sozinho.

### O que muda para você

- Fila eterna em “intenção” deixa de ser o fim da história.
- O retrato de perda do dia/semana pode dizer a verdade; até lá a trava de dado não verificado é a trava **correta**.
- Mercado sem conta demo aparece barrado, com motivo, e não é desviado para a Alpaca.

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Número da corretora gravado no ledger | Depois de um submit de teste (mock ou paper), a linha da ordem não fica só como intenção |
| 2 | Mercado sem conta demo barrado | Um sinal de B3 ou forex **não** chama a Alpaca e mostra o motivo |
| 3 | Acompanhamento até fill/cancelamento/expiração | Você vê o estado final no painel/ledger, não só o POST aceito |
| 4 | P&L do dia/semana a partir de fill | Perda só soma fill confirmado em real; fill sem conversão verificada não entra e não libera ordem nova |

---

## Sprint N19 — Laço demo com gatilho no painel *(resto)*

> Categoria: N  
> Status: em execucao (N19.1–N19.2 `[x]` no `3d26a13`; **não refazer**)  
> titulo_humano: Gatilhos no painel e ordem com rastro no ledger  
> Gate: pytest verde; live false; PATCH de gatilho não insere ordem; simulador local ≠ fill; `demo_operation_on` false ⇒ nenhuma ordem  
> Issue: ISS-009  
> Fora de escopo N19 (inalterado): escolher corretora de B3/forex; ligar operação demo em produção; conta real; estratégia nova; ajuste automático.

Tabela para o agente; o operador lê as tarefas abaixo.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [x] | M | N19.1 Migration 002 (mercado, âncoras, histórico, preço fora do real) | `/dev` | — |
| [x] | M | N19.2 PATCH de gatilho; Bearer sozinho = 401 na escrita | `/dev` | N19.1 |
| [ ] | M | N19.3 Persistir identificador e estado a partir de resposta mockada | `/dev` | N19.1 |
| [ ] | P | N19.4 Mercado sem conta demo que devolva posição fica barrado, com motivo, e não chama a Alpaca | `/qa testes` | N19.2, N19.3 |

### Task N19.3 — Gravar o número da ordem devolvido pela corretora

**Entrega:** Quando a corretora paper devolve um identificador, ele entra no ledger e a linha não permanece eterno em “intenção na fila”.
**Como conferir:** Num teste com resposta simulada da corretora, a ordem tem identificador e estado; o simulador local de B3/cripto continua sendo só log de pedido.
**Por quê:** Sem isso o retrato de carteira não pode ser honesto (ADR-007).

**Detalhe técnico**

**executor_prompt**:
```yaml
id: N19.3
size: M
depends_on: [N19.1]
reuse_targets:
  - component: src/signal_paper_runner.py
    reuse_as: extend
  - component: src/paper_gateway_queue.py
    reuse_as: extend
  - component: src/v4_shadow_broker.py
    reuse_as: reuse
guardrail_contract:
  - class: subagent-safety
    id: n19-3-no-alpaca-b3-forex
    target: src/
    check: B3_EQUITY and FOREX never POST to paper-api.alpaca.markets
    pass_condition: no cross-market submit
  - class: subagent-safety
    id: n19-3-shadow-not-fill
    target: src/v4_shadow_broker.py
    check: local simulator remains request log
    pass_condition: no paper_fills from shadow broker
```
Quando um submit paper mockado devolve id, gravar em `paper_orders` (`broker_order_id` + estado). Não deixar `queued_intent` após POST aceito. `orders_sent` só > 0 no submit paper explícito. Live false.

### Task N19.4 — Barrar mercado sem conta demo, com motivo visível

**Entrega:** B3 ou forex sem conta que devolva posição **não** vira chamada à Alpaca; o motivo aparece.
**Como conferir:** Você (ou o teste) manda um sinal desses mercados e vê recusa com código, sem ordem na Alpaca.
**Por quê:** ADR-010: sem leitura de posição/ordem/fill daquele mercado, o sinal fica barrado.

**Detalhe técnico:** depends_on `[N19.2, N19.3]`; reject_code estável e visível; 0 rebuild próprio (entra na release 1.2).

---

## Sprint N21 — Acompanhar até o fill e P&L verdadeiro

> Categoria: N  
> Status: planejada  
> titulo_humano: Fill, cancelamento ou expiração no ledger, com perda honesta  
> Gate: estado final gravado; P&L do dia/semana só de fill em real; live false; sem envio autônomo  
> review: senior+qa  
> Depende de: N19.3

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | N21.1 Acompanhar a ordem até fill, cancelamento ou expiração | `/dev` | — |
| [ ] | M | N21.2 Calcular perda do dia e da semana só com fill confirmado | `/dev` | N21.1 |
| [ ] | P | N21.3 Provar que reinício não duplica ordem | `/qa testes` | N21.1 |

### Task N21.1 — Acompanhar a ordem até o estado final

**Entrega:** Depois do envio, a plataforma consulta a corretora até fill, cancelamento ou expiração e grava o fill no ledger. Sem fill no prazo, cancela, registra e **não** reenvia o mesmo sinal sozinha.
**Como conferir:** Uma ordem de teste termina num estado final visível; ordem sem fill não aparece como executada.
**Por quê:** Feature 7 fluxo de erro + Feature 5 passo 3–4; reusa o reconciliador que hoje é manual.

**Detalhe técnico:** reuso `paper_reconcile` / `ledger_reconcile`; append-only fills; News First `paper_gateway` fora deste corte (ARCHITECTURE 12.3).

### Task N21.2 — Contar perda do dia e da semana só com fill

**Entrega:** O retrato deixa de marcar perda como “não verificada” por falta de ciclo: soma só fill confirmado em real. Fill em outra moeda sem conversão verificada **não** entra na âncora e o risco **não** abre ordem nova.
**Como conferir:** Sem fill, a âncora de perda não inventa número; com fill em real, o teto do dia/semana passa a ter base.
**Por quê:** DATABASE §6.5 e ADR-007 passo 2. A trava atual é correta; o ciclo que a satisfaz é este.

**Detalhe técnico:** não inventar câmbio; `ledger_entries.amount_cents` só na âncora quando BRL; não marcar verificado sem fill.

### Task N21.3 — Provar que reinício não duplica ordem

**Entrega:** Cair e subir o serviço retoma o acompanhamento sem mandar a mesma ordem de novo.
**Como conferir:** Teste de reinício com a mesma intenção: uma ordem, dois estados no ledger, não duas ordens na corretora.
**Por quê:** Feature 5 e Feature 7 critério de restart.

**Lacunas que a Onda 1 fecha:** Feature 5 trilha de identificador; Feature 7 (parcial: acompanhamento, restart, base de perda — **não** o envio autônomo); Feature 10 fica desbloqueada para a Onda 3; `LOSS_DATA_NOT_VERIFIED` deixa de ser beco sem saída.

---

## Onda 2 — Âncoras honestas e trabalhador no mesmo serviço

> titulo_humano: Risco lê o que você gravou; a fila anda sozinha, ainda sem mandar  
> Sprints: **N22** + **N23**  
> Depende de: Onda 1 (ADR-007). N22 também exige schema da N19.1 (já na N20).  
> Rebuild: **1** — release **MVP-OP-1.3** (painel opera), **junto com a Onda 3** se as duas fecharem no mesmo pacote; senão esta onda espera a 3 para um único rebuild.  
> Envio autônomo: ainda **desligado** (painel `demo_operation_on` default false; G-MKT pode estar vazio).

### Em uma frase

O teto de risco passa a ser um só, o calendário B3 passa a barrar fora de sessão, e a fila é processada no mesmo serviço do painel — sem criar app novo e sem mandar ordem sozinha ainda.

### O que muda para você

- Some a divergência “cinco mil num lugar, dez mil noutro”.
- Feriado e sessão B3 deixam de ser detalhe ignorado.
- Você não cola o trabalhador da fila no Exec: ele sobe com o painel.

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Âncoras do painel valem no risco | Mudar o teto no painel (Onda 3 liga a tela; o dado já vale aqui) muda a recusa da próxima ordem |
| 2 | Um capital de referência | Os dois avaliadores usam R$ 5.000 de partida, não R$ 10.000 |
| 3 | Fora da sessão B3/feriado | Sinal nesses horários é recusado com motivo, sem ordem |
| 4 | Fila no mesmo serviço | Log do app principal mostra pesquisa, painel **e** trabalhador; só dois apps no EasyPanel |

---

## Sprint N22 — Âncoras únicas e calendário B3

> Categoria: N  
> Status: planejada  
> titulo_humano: Um teto de risco e sessão B3 de verdade  
> Gate: Gate B e carteira leem `control_flags`; capital de partida R$ 5.000; fora de sessão B3/NY + feriado ⇒ recusa; live false  
> review: senior+qa

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | N22.1 Fazer o risco ler as âncoras gravadas pelo painel | `/dev` | — |
| [ ] | M | N22.2 Unificar o capital de referência no valor mais apertado | `/dev` | N22.1 |
| [ ] | M | N22.3 Recusar sinal fora da sessão B3, feriado e horário de verão | `/dev` | — |

### Task N22.1 — Fazer o risco ler as âncoras do painel

**Entrega:** Parada, capital, risco por operação, posições, risco aberto, perda do dia e da semana vêm do que está gravado — não de constante esquecida. Banco fora: vale o teto mais apertado já no código (R$ 5.000 e R$ 50).
**Como conferir:** Com parada ligada no dado, ordem nova é recusada com motivo de parada; com teto no máximo do dia, para até o próximo período.
**Por quê:** Feature 3 regras + Feature 7 âncoras + ARCHITECTURE 12.1 (“colunas de risco não são lidas”).

**Detalhe técnico:** `gate_b_risk` + `portfolio_risk_v4` leem `control_flags`; Prodígio R$ 20 inalterado; sem afrouxar sozinho.

### Task N22.2 — Unificar o capital de referência

**Entrega:** Some a divergência R$ 5.000 vs R$ 10.000. Partida do contrato: R$ 5.000.
**Como conferir:** Os dois caminhos de risco recusam no mesmo teto de capital.
**Por quê:** ARCHITECTURE 12.1; ADR-006 proíbe o código escolher o teto mais frouxo.

### Task N22.3 — Recusar fora da sessão B3, feriado e horário de verão

**Entrega:** Calendário EUA **e** B3, com feriado e horário de verão, faz parte do gate. Sinal fora não vira ordem.
**Como conferir:** Um horário de feriado B3 e um fora do pregão NY geram recusa com motivo de sessão; dia útil dentro do pregão não.
**Por quê:** Feature 3 regra de negócio + NFR Calendário; o relato “NY weekdays, holidays not filtered” é bloqueio aberto, não cosmética.

**Detalhe técnico:** reuso de calendário do vendor se existir (`trader-risk` / original); **não** inventar lista de feriados se o upstream já tiver; sessão por mercado (B3 ≠ NYSE).

---

## Sprint N23 — Trabalhador da fila dentro do v4-ops

> Categoria: N  
> Status: planejada  
> titulo_humano: A fila anda no mesmo serviço do painel, sem app novo  
> Gate: supervisor chama o trabalhador em intervalo curto; falha dele não derruba a pesquisa; dois apps EasyPanel; **não** trata controle do painel como autorização de envio (ADR-007 já fechado na Onda 1, mas `demo_operation_on` continua false)  
> review: senior+qa  
> Depende de: N21 (ciclo da ordem existe); N22.1 (âncoras lidas)

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | N23.1 Colocar o trabalhador da fila no mesmo supervisor do painel | `/dev` | — |
| [ ] | P | N23.2 Garantir que a queda do trabalhador não derruba a pesquisa | `/qa testes` | N23.1 |
| [ ] | P | N23.3 Confirmar que continuam só dois serviços no EasyPanel | docs | N23.1 |

### Task N23.1 — Colocar o trabalhador da fila no mesmo supervisor do painel

**Entrega:** O app principal passa a rodar pesquisa, painel **e** o ciclo da fila. Sinal não espera 15 minutos da pesquisa. Nenhum terceiro serviço.
**Como conferir:** No log do `trading-lab`, as três tarefas aparecem; o app de webhook continua só ingressão.
**Por quê:** ADR-009. Sem isso Feature 7 nunca vira ordem sozinha, mesmo com fill no ledger.

**Detalhe técnico:** estender `scripts/v4_ops_main.sh`; intervalo curto; chave de corretora **só** no caminho de ordem (pesquisa continua sem chave); `demo_operation_on` false ⇒ worker recusa envio e registra motivo; não importar cliente de corretora no painel.

### Task N23.2 — Isolar a queda do trabalhador

**Entrega:** Se o trabalhador cai, o supervisor reinicia só ele; a pesquisa segue.
**Como conferir:** Teste de layout: processo da pesquisa vivo após saída forçada do trabalhador.
**Por quê:** Trade-off aceito na ADR-009.

### Task N23.3 — Confirmar só dois serviços

**Entrega:** Runbook da release 1.3 diz explicitamente: não criar app novo.
**Como conferir:** Você abre o runbook e vê os mesmos dois nomes de sempre.
**Por quê:** Requisito de integração EasyPanel.

**Lacunas que a Onda 2 fecha:** F3 calendário e tetos divergentes; `control_flags` lidas; Feature 7 (parcial: âncoras e host paper no worker, **sem** “sinal vira ordem” até a Onda 4); ADR-009.

---

## Onda 3 — O painel passa a operar (login, sinais, performance)

> titulo_humano: Você entra, vê o motivo e o resultado verdadeiro, sem Exec  
> Sprints: **N24** + **N25** + **N26**  
> Depende de: Onda 1 (fill no ledger para performance); Onda 2 (âncoras e worker). Telas segundo o design já aprovado (Entrar, Central, Sinais).  
> Rebuild: o **mesmo 1** da release **MVP-OP-1.3** (com a Onda 2).  
> Feature 8 “nenhuma operação do dia a dia exige Exec”: conferida nesta onda, com worker da Onda 2.

### Em uma frase

Você entra com login, altera âncoras e estratégias no painel, vê por que cada sinal foi barrado, e o número de performance só conta fill confirmado.

### O que muda para você

- Cookie plantado no ambiente deixa de ser “login”.
- Bearer sozinho continua recusado na escrita (já N19.2); agora a tela de entrar existe.
- P&L bruto de snapshot deixa de se passar por resultado homologado.

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Tela de entrar | Sem login, o painel de operação não abre; com login, a Central aparece |
| 2 | Central de gatilhos | Mudar parada/âncora/fase grava histórico (valor anterior + data) e vale na próxima ordem |
| 3 | Tela de sinais | Cada linha tem origem, destino e motivo; barrado mostra gate e âncora |
| 4 | Performance honesta | Ordem `new` sem fill **não** entra no total |

---

## Sprint N24 — Login e central de controle

> Categoria: N  
> Status: planejada  
> titulo_humano: Entrar no painel e mandar na operação sem o Exec  
> Gate: painel não abre sem login; alteração registrada; plataforma não afrouxa âncora sozinha; parada geral impede ordem nova em até um ciclo; live false; um operador, sem cadastro público  
> review: senior+qa  
> Dúvida 9 e 10: esta sprint **responde no código** o que o contrato já decidiu (login + painel escreve). Segredo do operador continua no ambiente, nunca no Git.

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | N24.1 Colocar a tela de entrar na frente do painel | `/dev` | — |
| [ ] | M | N24.2 Ligar a Central às âncoras, fases e parada já graváveis | `/dev` | N24.1 |
| [ ] | P | N24.3 Conferir que a parada pelo painel segura a próxima ordem no ciclo | `/qa testes` | N24.2 |
| [ ] | P | N24.4 Tirar o Exec do roteiro do dia a dia | docs | N24.2, N23.1 |

### Task N24.1 — Colocar a tela de entrar na frente do painel

**Entrega:** Acesso exige autenticação. Sem login, o painel operacional não abre. Continua um operador só; sem tabela de usuários (o contrato de dados não tem cadastro).
**Como conferir:** Abrir o endereço sem sessão → tela de entrar ou recusa; com sessão válida → Central.
**Por quê:** Feature 8 último critério; o design já tem a tela Entrar; hoje a sessão é um cookie igual ao valor do ambiente.

**Detalhe técnico:** reuso da sessão de operador da N19.2 (escrita já exige cookie, Bearer = 401); não publicar sem auth (fora de escopo); HTTPS no EasyPanel permanece; não logar o segredo.

### Task N24.2 — Ligar a Central às âncoras, fases e parada

**Entrega:** Você vê e altera as seis âncoras, liga/desliga mercado e estratégia existente, aciona parada. Cada mudança grava data e valor anterior. ORB e mean reversion não sobem para paper. Conta real aparece desligada, sem botão.
**Como conferir:** Uma alteração na Central aparece no histórico; a próxima ordem usa o valor novo; tentar afrouxar sozinho (sem você) não existe no produto.
**Por quê:** Feature 8 + ADR-006. A API PATCH já está na N19.2; falta a tela.

**Detalhe técnico:** três telas do DESIGN (Central aqui, Sinais na N25); `trigger_changes` append-only; unknown strategy = 404.

### Task N24.3 — Conferir a parada em até um ciclo

**Entrega:** Parada geral pelo painel impede ordem nova em até um ciclo do trabalhador.
**Como conferir:** Ligar a parada na Central e ver a próxima intenção recusada com motivo de parada, sem ordem na corretora.
**Por quê:** Feature 8 critério 3.

### Task N24.4 — Tirar o Exec do roteiro do dia a dia

**Entrega:** O runbook do dia a dia (ver, parar, ajustar teto, ligar estratégia) aponta o painel, não o Exec.
**Como conferir:** Você segue o runbook sem abrir o terminal do EasyPanel. Segredo e rebuild continuam sendo operação rara, não dia a dia.
**Por quê:** Feature 8 critério 4.

---

## Sprint N25 — Sinais e Prodígio com motivo visível

> Categoria: N  
> Status: planejada  
> titulo_humano: Cada sinal mostra para onde foi e o que o barrou  
> Gate: lista com origem/destino/motivo; ranking Prodígio e cópias; barrado mostra gate e âncora  
> review: senior+qa

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | N25.1 Mostrar a lista de sinais com destino e motivo | `/dev` | — |
| [ ] | M | N25.2 Mostrar o ranking Prodígio e quais sinais ele copiou | `/dev` | — |
| [ ] | P | N25.3 Garantir que o barrado aponta gate e âncora | `/qa testes` | N25.1 |

### Task N25.1 — Mostrar a lista de sinais com destino e motivo

**Entrega:** Tela de sinais: origem, destino (ordem, barrado, fila) e motivo da rejeição. Mercado visível em cada linha.
**Como conferir:** Um sinal aceito, um barrado no Gate A e um barrado no Gate B aparecem distintos, sem parecer fill.
**Por quê:** Feature 9 critério 1; o ledger de eventos já existe.

### Task N25.2 — Mostrar o ranking Prodígio e o que foi copiado

**Entrega:** Ranking dos provedores e quais sinais o Prodígio copiou — pesquisa, não autorização de ordem.
**Como conferir:** A linha do ranking bate com o que o ciclo de ranking já produz; cópia aponta o sinal, não um lucro inventado.
**Por quê:** Feature 9 critério 2; o painel v1 já lista oportunidades em leitura.

### Task N25.3 — Mostrar gate e âncora no sinal barrado

**Entrega:** Sinal barrado diz **qual** gate e **qual** âncora, com o valor da hora.
**Como conferir:** Estourar de propósito o teto de posições (em teste) mostra a âncora, não só um código opaco.
**Por quê:** Feature 9 critério 3; ARCHITECTURE 12.2.

---

## Sprint N26 — Performance só de fill confirmado

> Categoria: N  
> Status: planejada  
> titulo_humano: O número de resultado só conta fill da corretora  
> Gate: total e por estratégia só de fill; ordem sem fill fora; bruto rotulado  
> review: senior+qa  
> Depende de: N21

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | N26.1 Calcular resultado só com fill confirmado | `/dev` | — |
| [ ] | P | N26.2 Tirar ordem sem fill do resultado | `/qa testes` | N26.1 |
| [ ] | P | N26.3 Rotular o que ainda é bruto | `/dev` | N26.1 |

### Task N26.1 — Calcular resultado só com fill confirmado

**Entrega:** Painel de performance por estratégia e total usa fill confirmado na corretora, não snapshot bruto.
**Como conferir:** Com submit sem fill, o total de resultado não sobe; com fill evidenciado (Onda 0), o número aparece.
**Por quê:** Feature 10 critério 1; ADR-007.

### Task N26.2 — Tirar ordem sem fill do resultado

**Entrega:** Ordem `new`/`accepted`/fila não entra no resultado.
**Como conferir:** A MSFT limit que ficou em filled 0 **não** vira lucro/prejuízo.
**Por quê:** Feature 10 critério 2.

### Task N26.3 — Rotular o que ainda é bruto

**Entrega:** Onde o custo completo não existe, o painel diz que o valor é bruto.
**Como conferir:** Você lê o rótulo; não há “lucro líquido” inventado.
**Por quê:** Feature 10 critério 3.

**Lacunas que a Onda 3 fecha:** Feature 6 “mostra mas não opera”; Feature 8; Feature 9; Feature 10; dúvidas 9 e 10.

---

## Onda 4 — Mercados demo (Feature 7 fecha)

> titulo_humano: B3, cripto e forex no laço, cada um na conta que você nomear  
> Sprints: **N27**  
> Depende de: Ondas 1–3 **e** G-MKT por mercado.  
> Rebuild: **0** se G-MKT chegar a tempo de entrar na release 1.3; senão **1** — release **MVP-OP-1.4**.  
> Sem G-MKT: esta onda **não implementa corretora**. Só mantém o barramento visível (já N19.4).

### Em uma frase

O sinal válido vira ordem na conta demo **daquele** mercado, sozinho, só depois que você disser o nome da conta; os outros mercados ficam visíveis e barrados.

### O que muda para você

- Alpaca paper **não** cobre B3 nem forex — o plano não desvia esses símbolos para ela.
- Simulador local continua sem fill.
- Você liga a operação no painel; o destino real continua sem botão.

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Forex existe no universo e no risco, ainda sem ordem se sem conta | Símbolo forex aparece e é barrado com motivo, não some nem vai para a Alpaca |
| 2 | Mercado com conta nomeada por você opera no laço | Um sinal válido desse mercado vira ordem **demo** sem você colar comando |
| 3 | Reinício e host paper | Cair o app não duplica; existir chave live no ambiente não muda o destino |

---

## Sprint N27 — Contas demo no laço, sem inventar o nome

> Categoria: N  
> Status: planejada  
> titulo_humano: Operar só o mercado cuja conta demo você nomeou  
> Gate: G-MKT por mercado; Feature 7 critérios conferíveis **apenas** nos mercados respondidos; live false; dois apps  
> review: comprehensive  
> Bloqueio: sem G-MKT, N27.2 e N27.4 não começam (N27.1 e N27.3 podem).

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | M | N27.1 Incluir forex no universo e no avaliador de carteira, sem ordem se sem conta | `/dev` | — |
| [ ] | M | N27.2 Ligar a conta demo do mercado que o operador nomeou | `/dev` | G-MKT |
| [ ] | P | N27.3 Manter mercado sem conta barrado com motivo visível | `/qa testes` | N27.1, N19.4 |
| [ ] | P | N27.4 Homologar sinal válido virando ordem demo sem ação manual | operador | N27.2, N23.1, N24.2 |
| [ ] | P | N27.5 Confirmar que o destino é sempre paper | `/qa testes` | N27.2 |
| [ ] | P | N27.6 Confirmar restart sem duplicar no laço ligado | `/qa testes` | N27.4 |

### Task N27.1 — Incluir forex no universo e no risco, ainda barrado

**Entrega:** Forex deixa de ser invisível. Sem conta demo, o sinal forex é barrado com motivo — não avaliado como ação americana.
**Como conferir:** Um símbolo forex aparece no painel como mercado sem conta, se G-MKT ainda não veio.
**Por quê:** ADR-010: o avaliador hoje não conhece forex; isso entra quando o contrato de dados existir (DATABASE §6.2 já tem o literal).

**Detalhe técnico:** literal `FOREX`; posição única por `(market, symbol)`; sem adapter inventado.

### Task N27.2 — Ligar a conta demo do mercado que você nomeou

**Entrega:** Só depois de G-MKT: um adaptador **daquela** conta, capaz de posição, ordem aberta e fill. Reuso primeiro; se a conta for a Alpaca paper para cripto e você disser, reusa o caminho paper já existente. B3 e forex **não** passam pela Alpaca.
**Como conferir:** A conta nomeada devolve os três estados; o painel mostra o mercado como operável.
**Por quê:** ADR-010. Sem nome, esta tarefa não existe.

**Detalhe técnico:** BLOCKED sem G-MKT; não usar `v4_shadow_broker` como fill; não reimplementar trader-entry/exit/budget/risk/scanner.

### Task N27.3 — Manter o barramento visível

**Entrega:** Mercado sem G-MKT continua na tela, desligado, com motivo.
**Como conferir:** Você vê “sem conta demo” (ou equivalente em português claro), não um erro mudo.
**Por quê:** Trade-off da ADR-010.

### Task N27.4 — Homologar o sinal virando ordem demo sozinho

**Entrega:** Com operação ligada no painel, âncoras ok, conta demo no ar: sinal válido vira ordem **sem** você disparar cada uma.
**Como conferir:** Você não cola comando; a ordem aparece na conta demo e no ledger com identificador (Onda 1).
**Por quê:** Feature 7 critério 1 — este é o fechamento Must-have.

### Task N27.5 — Destino sempre paper

**Entrega:** Existir chave live no ambiente não muda o host. Conta real sem botão.
**Como conferir:** Teste com flag live diferente de false: processo recusa; com chave live presente e live false: ainda paper.
**Por quê:** Feature 7 critério 4.

### Task N27.6 — Restart no laço ligado

**Entrega:** Reinício com operação ligada retoma sem duplicar.
**Como conferir:** Mesmo sinal/idempotência após restart: uma ordem.
**Por quê:** Feature 7 critério 5 no caminho autônomo.

**Lacunas que a Onda 4 fecha:** Feature 7 restante; ISS-009 critério de fechamento **por mercado respondido**. Mercados sem G-MKT ficam explicitamente fora, por contrato.

---

## Onda 5 — Catálogo só com fórmula recuperada (N17 já existe)

> titulo_humano: Tá Barato e momentum só se o upstream tiver a regra  
> Sprints: **N17** (já no roteiro — **não duplicar tarefas**)  
> Depende de: G-FORM. N17.0 (Git First) **pode** rodar em paralelo desde a Onda 0. N17.1+ só com fórmula encontrada.  
> Rebuild: **0** se G-FORM = “não existe” (só documenta o gap). **1** se integrar — release **MVP-OP-1.1** (nome já do épico ISS-007), no máximo um rebuild.

### Em uma frase

A família Tá Barato (e momentum, se o escopo achar regra) só entra em sombra/paper com a fórmula do código original; se não houver, fica fora e o critério “não inventar” continua cumprido.

### O que muda para você

- N17 **já está escrita** no roteiro; esta onda só a posiciona. Nada de segundo pacote paralelo.
- Feature 4 checkboxes já estão `[x]`; esta onda **não** é necessária para o núcleo Must-have 1.1.
- Prodígio já tem submit paper (N16); a dúvida 3 (empate/drawdown/consistência) só vira número novo se o upstream tiver a fórmula.

Tarefas **já existentes** (não reescrever): N17.0 Git First; N17.1 adaptação só com reuso; N17.2 homolog operador sombra → paper limitado; N17.3 evidência; N17.4 F-003 opcional; N17.5 seção no painel.

**Se G-FORM = não existe:** fechar N17.0 com o gap documentado; N17.1–N17.5 permanecem bloqueadas; **não** inventar percentil, RSI, volume ou score.

**Lacunas:** matriz F4 “sem fórmula” — ou fecha com homologação, ou fecha como gap explícito. Collective2 e ORB continuam fora.

---

## Onda 6 — Sugestões e ajuste supervisionado (Feature 11)

> titulo_humano: Ajuste automático só depois do método e do fill  
> Sprints: **N28**  
> Depende de: G-AJUSTE **e** fill real (Onda 0 N20.3 + Onda 1). DATABASE §6.6: tabela de ajuste espera fill.  
> Rebuild: **0** extra se couber na mesma release da Onda 5; senão **1**.  
> Should-have: o núcleo 1.1 pode estar operacional com esta onda ainda `[ ]`.

### Em uma frase

Sugestão continua sugestão; se você definir o método, a plataforma ajusta só parâmetro que já existe, registra antes e depois, deixa desfazer, e nunca mexe âncora.

### O que muda para você

- Tips de pesquisa que o painel v1 já mostra **não** são ordem.
- Sem G-AJUSTE, não nasce “inteligência” de parâmetro em cima de zero dado.

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Sugestão rotulada | A oportunidade diz que é sugestão, não ordem autorizada |
| 2 | Ajuste na faixa original | Nenhum número novo que a estratégia original não tenha |
| 3 | Histórico e desfazer | Antes, depois, motivo; você desfaz na Central |
| 4 | Âncoras intocadas | O ajuste não altera capital, perda do dia, parada |

---

## Sprint N28 — Ajuste supervisionado depois do método

> Categoria: N  
> Status: planejada  
> titulo_humano: Ajuste registrado e reversível, sem mexer no risco  
> Gate: G-AJUSTE; Feature 11 quatro critérios; live false  
> review: senior+qa

| Status | Tamanho | Tarefa | Skill/Command | Depende de |
|--------|---------|--------|---------------|------------|
| [ ] | P | N28.1 Manter sugestão rotulada como sugestão | `/dev` | — |
| [ ] | M | N28.2 Ajustar só parâmetro já existente, dentro da faixa original | `/dev` | G-AJUSTE |
| [ ] | M | N28.3 Registrar antes, depois e motivo, com desfazer no painel | `/dev` | N28.2 |
| [ ] | P | N28.4 Proibir ajuste de âncora de risco | `/qa testes` | N28.2 |

### Task N28.1 — Manter sugestão rotulada como sugestão

**Entrega:** Oportunidade no painel continua marcada como sugestão; nunca autoriza ordem por si só.
**Como conferir:** Você não consegue “aceitar a dica” como se fosse fill.
**Por quê:** Feature 11 critério 1 (já parcialmente no painel v1).

### Task N28.2 — Ajustar só o que a estratégia original já tem

**Entrega:** Frequência, definição de erro e desfazer = o que você disser em G-AJUSTE. Código só altera parâmetro existente na faixa.
**Como conferir:** Não aparece RSI/percentil/score novo. Família sem fórmula continua intocada (G-FORM).
**Por quê:** Feature 11 critério 2; fora de escopo “criar parâmetro inexistente”.

### Task N28.3 — Registrar e permitir desfazer

**Entrega:** Cada ajuste tem antes, depois, motivo; a Central desfaz.
**Como conferir:** Você ajusta, lê o histórico, desfaz, e o valor volta.
**Por quê:** Feature 11 critério 3.

### Task N28.4 — Proibir mexer âncora no ajuste

**Entrega:** Ajuste automático não altera as seis âncoras nem a parada.
**Como conferir:** Tentativa no teste é recusada; âncora só muda pela Central (você).
**Por quê:** Feature 11 critério 4 + ADR-006.

**Lacunas que a Onda 6 fecha:** Feature 11; dúvida 8.

---

## 8. Rebuilds EasyPanel previstos

Política: **documento sozinho = 0 rebuild**; **no máximo um rebuild por release**; NFR Entrega = sem série de micro-deploys. Só os dois apps de sempre. Webhook só rebuilda se a release tocar ingressão (nenhuma onda acima exige isso por padrão).

| Release | Ondas | O que sobe | Rebuild `trading-lab` | Rebuild webhook |
|---------|-------|------------|------------------------|-----------------|
| PR #21 N18 closeout (esta frente) | — | Só docs | **0** | **0** |
| Onda 0 N20 (pedido de revisão) | 0 | Contrato + código N19.1–N19.2 no Git | **0** (espera 1.2) | **0** |
| **MVP-OP-1.2** ciclo da ordem | 0+1 | Migration 002, gatilhos, identificador, acompanhamento, P&L de fill | **1** | 0 |
| **MVP-OP-1.3** painel opera | 2+3 (+ N27 se G-MKT no prazo) | Âncoras, calendário, worker, login, sinais, performance | **1** | 0 |
| **MVP-OP-1.4** mercados | 4 se G-MKT atrasar | Adapter da conta que você nomear | **0 ou 1** | 0 |
| **MVP-OP-1.1** Tá Barato (nome ISS-007) | 5 se G-FORM achar fórmula | Família upstream no painel | **0 ou 1** | 0 |
| Ajuste Feature 11 | 6 | Tabela/ajuste se G-AJUSTE | **0** se empacotar com 1.1; senão **1** | 0 |

**Contagem máxima se tudo destravar em pacotes separados:** 4 rebuilds de `trading-lab` (1.2 + 1.3 + 1.4 + 1.1) e 0 de webhook. **Contagem do núcleo Must-have (Features 1–10):** 2 rebuilds (1.2 + 1.3), 3 se G-MKT vier depois (1.4).

N20.2/N20.3/N20.5 são sessão sua: **0 rebuild**.

---

## 9. Rastreio — cada critério de aceite do contrato → sprint

Legenda: **já** = checkbox `[x]` hoje; **onda** = quem fecha o `[ ]` ou a regra ainda aberta.

### Feature 1 — Pesquisa e shadow

| Critério | Estado | Sprint |
|----------|--------|--------|
| Pytest com evidência em CI | já `[x]` | N11 |
| Ciclo com live desligado termina sem ordem | já `[x]` | N11 |
| Ciclo falho não deixa manifesto antigo confiável | já `[x]` | N11 |

### Feature 2 — Gate A

| Critério | Estado | Sprint |
|----------|--------|--------|
| Sinal inválido recusado, nenhuma ordem | já `[x]` | D3 |
| Mesmo evento duas vezes não abre duas posições | já `[x]` | D3 |
| Trilha com motivo, status e timestamp | já `[x]` | D3 |

### Feature 3 — Gate B (checkboxes + regras ainda abertas)

| Critério | Estado | Sprint |
|----------|--------|--------|
| Ordem que estoura limite recusada com motivo | já `[x]` | D4 |
| Parada geral impede ordem nova | já `[x]` (env/dado); painel na N24 | D4 + N24.3 |
| Fora da sessão NYSE ou 3+ posições | já `[x]` (NYSE) | D4 |
| Calendário B3, feriado, horário de verão (regra + NFR) | aberto | **N22.3** |
| Dois tetos de capital (5.000 vs 10.000) | aberto (§12.1) | **N22.2** |
| Colunas de risco do painel não lidas | aberto (§12.1) | **N22.1** |

### Feature 4 — Catálogo

| Critério | Estado | Sprint |
|----------|--------|--------|
| ORB não é paper principal | já `[x]` | N7 |
| Collective2 sem aprovação não entra | já `[x]` | N7 |
| Sem fórmula recuperada, sem limiar inventado | já `[x]` | N7; **N17** só se G-FORM achar fórmula |

### Feature 5 — Paper ponta a ponta

| Critério | Estado | Sprint |
|----------|--------|--------|
| Fill real + posição coerente | `[ ]` | **N20.3 + N20.4** (P-001b / N12.4–N12.5) |
| Sinal inválido não gera ordem | já `[x]` | D3/D4 |
| Duplicata não reabre posição | já `[x]` | D3 |
| Reinício não perde trilha | já `[x]` (ledger); laço autônomo em N21.3 / N27.6 | D2 + **N21.3** |
| Fila ≠ homologação completa | já `[x]` | N9 |
| Reconcile read-only → fills | já `[x]` | D5 |
| Identificador da corretora no ledger (fluxo 2–4) | lacuna | **N19.3 + N21.1** |

### Feature 6 — Observabilidade

| Critério | Estado | Sprint |
|----------|--------|--------|
| Dashboard local/remoto com regra de auth da v0.1 | já `[x]` | N16/N18 |
| Parada visível | já `[x]` | N9/N16 |
| Painel opera o dia a dia (extensão F8) | lacuna da matriz | **N24** |

### Feature 7 — Operação autônoma demo

| Critério | Estado | Sprint |
|----------|--------|--------|
| Sinal válido vira ordem demo sem ação manual | `[ ]` | **N27.4** (depois N23 + N24 + G-MKT) |
| Nenhuma ordem com âncora estourada | `[ ]` | **N22 + N23 + N24.3** |
| Perda do dia/semana no teto para e registra motivo | `[ ]` | **N21.2 + N22.1** |
| Destino sempre paper | `[ ]` | **N27.5** (e invariante em todas) |
| Reinício sem duplicar | `[ ]` | **N21.3 + N27.6** |

### Feature 8 — Central de controle

| Critério | Estado | Sprint |
|----------|--------|--------|
| Alteração vale na próxima ordem e registra anterior | `[ ]` | **N19.2** (API) + **N24.2** (tela) |
| Plataforma nunca afrouxa âncora sozinha | `[ ]` | **N24.2 + N28.4** |
| Parada pelo painel em até um ciclo | `[ ]` | **N24.3** |
| Dia a dia sem Exec | `[ ]` | **N23 + N24.4** |
| Painel não abre sem login | `[ ]` | **N24.1** |

### Feature 9 — Sinais e Prodígio

| Critério | Estado | Sprint |
|----------|--------|--------|
| Lista com origem, destino e motivo | `[ ]` | **N25.1** |
| Ranking Prodígio e sinais copiados | `[ ]` | **N25.2** |
| Barrado mostra gate e âncora | `[ ]` | **N25.3** |

### Feature 10 — Performance

| Critério | Estado | Sprint |
|----------|--------|--------|
| Resultado só de fill confirmado | `[ ]` | **N26.1** (dep. N21) |
| Ordem sem fill fora | `[ ]` | **N26.2** |
| Valores brutos rotulados | `[ ]` | **N26.3** |

### Feature 11 — Sugestões e ajuste (Should-have)

| Critério | Estado | Sprint |
|----------|--------|--------|
| Sugestão marcada como sugestão | `[ ]` | **N28.1** (parcial no painel v1) |
| Ajuste só parâmetro original na faixa | `[ ]` | **N28.2** (G-AJUSTE) |
| Histórico antes/depois/motivo e desfazer | `[ ]` | **N28.3** |
| Ajuste nunca altera âncoras | `[ ]` | **N28.4** |

### Não-funcionais

| Meta | Estado | Sprint |
|------|--------|--------|
| Live desligado; segredo fora de log | já | invariante |
| Idempotência | já | Feature 2 |
| Auditoria recuperável | parcial | D3 + **N25** (visível) |
| Calendário EUA e B3 + feriado | aberto | **N22.3** |
| Pacote consolidado, sem micro-deploy | política | §8 |
| Tempo de resposta numérico | “a definir” | **não mapeado** (não inventar meta) |
| Uptime percentual | “a definir” | **não mapeado** |
| Um operador | já | — |

### Dúvidas v0.3

| # | Destino |
|---|---------|
| 1–2 Tá Barato / momentum | G-FORM → N17 |
| 3 Prodígio empate/drawdown | G-FORM / N17 se o upstream tiver; senão não inventar (N16 já submete com regras que existem) |
| 4 SHA EasyPanel | **N20.2** |
| 5 Pin do skill | já pinado neste repo; conferir na imagem junto com N20.2 |
| 6 Prazo | respondida no v0.3 (sem data fixa) |
| 7 Postgres | **N20.5** |
| 8 Método do ajuste | G-AJUSTE → N28 |
| 9 Login | **N24.1** |
| 10 Painel escreve | **N19.2 + N24.2** |

---

## 10. O que não entra neste plano (de propósito)

- F-003 orb-parity: congelado; ORB permanece pesquisa/sombra. Não é critério `[ ]` de Feature 1–11.
- Walk-forward / Lean: motor separado, backlog.
- Cadastro de estratégia nova pelo painel: fora de escopo v0.3.
- Ação americana como quarto mercado do laço: ADR-008 revogada; submits US já feitos não são apagados e **não** substituem B3/cripto/forex.
- Terceiro serviço EasyPanel; host live; limiar inventado; simulador como fill.

---

## 11. Sprints existentes que este rascunho não reabre

| Sprint | Tratamento |
|--------|------------|
| N12 | Só as tarefas abertas N12.4/N12.5 viram N20.3/N20.4 |
| N13 | Tarefas `[x]`; índice “em execução” é poeira de status — não planejar de novo |
| N15–N16 | Entregues no que o índice marca; fill continua P-001b |
| N17 | Incorporada na Onda 5, tarefas originais |
| N18 | Closeout nesta frente (PR #21); fora das ondas de produto |
| N19.1–N19.2 | Publicar na N20; não reimplementar |

---

## 12. Próximo passo (quando você aprovar escrita no roteiro)

1. Responder ou adiar G-MKT / G-FORM / G-AJUSTE (adiar é válido e tem efeito descrito na §2).
2. `/pmo plan` de verdade: copiar as sprints N20–N28 (+ resto N19) para `docs/ROADMAP.md` **noutra frente**, não nesta.
3. Abrir frente da Onda 0 (`/git front create` com slug de contrato/gatilho) a partir do `main`, resgatar `3d26a13` conforme N20.1.
4. Sua sessão: P-001b + SHA + Postgres.
5. Só então `/pmo sprint` da N19 restante / N21. `sprint_atual` **não** é preenchido por este rascunho.

```
PLAN_SUMMARY: sprint=N20..N28+N19resto brief=docs/.briefs/MVP-FINAL-WAVES.plan.md plan_only=true
```
