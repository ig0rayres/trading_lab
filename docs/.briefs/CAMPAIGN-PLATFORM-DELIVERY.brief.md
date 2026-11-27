---
planner_subagent_id: plan-only
auditor_subagent_id: plan-only
audited_at: 2026-11-17T11:20:00-03:00
findings_count: 0
severity_summary:
  CRITICAL: 0
  HIGH: 0
  MEDIUM: 0
  LOW: 0
audit_evidence_path: ""
sprint_id: N41
campaign_id: PLATFORM-DELIVERY
planner: planejador-melhorias
status: plan_only
plan_only: true
titulo_humano: Plano-mestre para operar pelo painel, não mais uma sprint cosmética
---

# Campanha — entrega da plataforma operacional

> `/pmo plan` 2026-11-17 · operador: frustração «menos de 20% pronto» · **não é infra** · **não é uma sprint de texto** · worktree `front/n27-alpaca-loop`  
> Primeira sprint executável: **N41** (ordens abertas + histórico). O resto desta folha é a fila.  
> `LIVE_TRADING_ENABLED=false` em todas as ondas. TimesFM = pesquisa, nunca autorização de ordem. Clear e OANDA não fingem entrega.

### Em uma frase

O laboratório deixa de acumular sprints de teste e passa a ter um plano até você operar pelo menu do dia a dia — vendo estratégias, sinais, ordens abertas, histórico, resultado, Prodígio e os mercados que o contrato já permite.

### O que muda para você

- O contrato marcado com testes deixa de ser confundido com «já dá para operar no painel»
- A primeira entrega útil é a lista de ordens abertas e o histórico de fills, no mesmo menu em que você já entra
- Ação americana e cripto na Alpaca paper são o caminho de demonstração que pode fechar primeiro
- Bolsa brasileira (Clear) e câmbio (OANDA) continuam visíveis e barrados até você credenciar — o código não inventa conta
- Análise Google (TimesFM) permanece dica de pesquisa; dinheiro real permanece desligado

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Matriz honesta dos nove pilares | Nesta folha: feito, parcial, bloqueado ou faltando, com o critério do contrato citado |
| 2 | Fila de ondas até «operar pelo painel» | Tabelas Onda 0…N abaixo, com o que fica na sua mão |
| 3 | Primeira sprint da fila | Abrir o plano **N41**: menu ganha Ordens e Histórico, sem enviar ordem pelo painel |

---

## Por que parece pouco pronto

O contrato (`docs/REQUIREMENTS.md` Features 1–11) tem a maior parte dos critérios **marcados** porque existem testes e, em alguns casos, uma tela. Operar é outra barra: depois do login no painel publicado, o menu do dia a dia hoje é só **Central, Sinais, Prodígio, Performance**. Ordens abertas e histórico **não existem** como tela (`docs/OPERATOR-PANEL-MAP.md`). O épico do painel único (ISS-007) prometeu essas áreas na versão 1.0; a N40 só mapeou a lacuna (ISS-016).

Checkboxes do contrato **não** são fill. Semáforo no ar **não** é fill. Fila HTTP **não** é fill.

---

## O que «pronto para operar» significa nesta campanha

Você entra no painel (login), **sem Exec**, e consegue:

1. Ver quais estratégias existem e em que fase estão (pesquisa, sombra, paper limitado).
2. Ver sinais com origem, destino e motivo de recusa.
3. Ver **ordens paper ainda abertas** (símbolo, quantidade, estado) — não só um número.
4. Ver **histórico / fills confirmados** (e o que é fila, não fill).
5. Ver resultado **só de fill**, rotulado como bruto quando o custo não está completo.
6. Ver Prodígio como ranking de pesquisa (não como ordem autorizada).
7. Nos mercados **já permitidos pelo contrato** (ação US e cripto na Alpaca paper), acompanhar o laço até fill ou recusa.

Fora dessa barra, de propósito:

- Bolsa brasileira e câmbio: prontos só depois das suas credenciais (N29.5 / ISS-010).
- Tá Barato em paper: só depois da fórmula recuperada e da homologação que já é sua (N17.2).
- TimesFM: contexto de previsão rotulado; se faltar a dependência, some com motivo; **nunca** autoriza ordem.
- Dinheiro real: desligado. Sem botão Live.

---

## Matriz de maturidade (nove pilares)

Legenda: **FEITO** = tela ou laço no menu/caminho combinado, com evidência citada. **PARCIAL** = código/teste existe, mas a superfície do dia a dia está vazia, na página errada, ou falta homologação. **BLOQUEADO** = falta você (credencial, promoção de fase, EasyPanel). **FALTA** = não há rota nem lista no menu.

| Pilar | Maturidade | O que o contrato já marca | O que você vê hoje | Bloqueio |
|-------|------------|---------------------------|--------------------|----------|
| Estratégias | **PARCIAL** | Feature 4: ORB fora de paper, Collective2 fechado, sem limiar inventado — os três critérios `[x]` | Fases na página única antiga; o menu do dia a dia **não** lista o catálogo; a Central altera âncoras, não mostra a tabela de fases | Fórmulas Tá Barato / momentum / empate Prodígio **abertas** (dúvidas 1–3). N17.2 é seu |
| Sinais | **FEITO** | Feature 9 critério 1 e 3 `[x]` | Menu **Sinais** (`/sinais`) | Sem dado = «Nenhum sinal neste destino.» (vazio comum, não sumiço) |
| Ordens em aberto | **FALTA** | Feature 6 pede ver ordens paper; ISS-007 área 1.0 | **Sem** item de menu, **sem** `/ordens`; no máximo contadores na página única antiga | Esta é a **Onda 1 / N41** |
| Performance | **PARCIAL** | Feature 10 os três critérios `[x]` | Menu **Performance**; só fill; rótulo bruto | Vazio até fill confirmado. Um fill AAPL histórico (Feature 5 `[x]`, 2026-10-29) não enche a tela sozinho |
| Google TM (TimesFM) | **PARCIAL** | Feature 11: TimesFM só pesquisa (dúvida 8 respondida) | **Nenhuma** secção HTML; relatório diário / JSON | Fail-closed se indisponível. **Nunca** ordem. Onda de visibilidade rotulada (N43), não de execução |
| Prodígio | **PARCIAL** | Feature 9 critério 2 `[x]`; N30 rank→sinal sem promover fase | Menu **Prodígio**; ranking vazio até `prodigy-rank` | Fase padrão **pesquisa**. Paper só se **você** promover. Ranking ≠ ordem |
| B3 | **BLOQUEADO** | Feature 7 critério B3 **`[ ]`** | Mercado visível; envio barrado com motivo; adaptador mock no laço (N34) | Conta Clear **simulada** e ids só no EasyPanel (**N29.5**, ISS-010). Sem credencial não há fill B3 |
| Cripto | **PARCIAL** | Feature 7 cripto `[x]` (pytest N30) | Laço Alpaca paper no código; **sem** lista de ordens no menu | Completa o caminho de demonstração **depois da N41** + rebuild. Não é Clear |
| Alpaca (ação US paper) | **PARCIAL** | Feature 5 fill `[x]`; Feature 7 US `[x]`; live recusado | Laço paper no código; fill AAPL citado; **sem** tela de abertas/histórico no menu | Mesmo que o laço envie, você não opera pelo painel até a N41. Host sempre paper; chave com cara de live não muda destino (Feature 7 `[x]`) |

Leitura curta: **quatro áreas já têm menu** (Central implícita, Sinais, Prodígio, Performance). **Duas faltam de verdade** (ordens abertas, histórico). **Uma está na página errada** (estratégias). **Uma é só pesquisa** (TimesFM). **Duas corretoras terceiras esperam você** (B3, forex/OANDA — forex não estava na lista de nove pilares, mas o contrato Feature 7 critério forex também está `[ ]`).

---

## Contrato (Features 1–11) — o que já é evidência vs o que ainda é operação

| Feature | Critérios no papel | Serve para «operar pelo painel»? |
|---------|--------------------|----------------------------------|
| 1 Pesquisa/shadow | `[x]` ciclo sem ordem, manifesto honesto, pytest CI | Sim para radar. Não é paper |
| 2 Gate A | `[x]` rejeita inválido, duplicata, ledger | Infra de sinal; você já vê destino em **Sinais** |
| 3 Gate B | `[x]` tetos, kill switch, sessão | Âncoras na **Central**; o laço paper já lê as flags (N32) |
| 4 Catálogo | `[x]` ORB never-paper, C2 fechado, sem score inventado | Fases **não** estão no menu do dia a dia |
| 5 Paper ponta a ponta | `[x]` fill AAPL 2026-10-29 + testes | Homologação pontual ≠ tela de ordens |
| 6 Observabilidade | `[x]` dashboard auth + kill switch visível | «Ver ordens paper» ainda é contador, não lista |
| 7 Autônomo demo | US+cripto `[x]`; **B3 `[ ]`**; **FOREX `[ ]`**; âncoras `[x]` | Laço US/cripto sem a lista no menu |
| 8 Central | `[x]` login, âncoras, parada, sem Exec no dia a dia | Feito como controle; não lista ordens |
| 9 Sinais e Prodígio | `[x]` | Telas existem; Prodígio continua pesquisa até você promover |
| 10 Performance | `[x]` | Tela existe; vazia sem fill |
| 11 Sugestões | `[x]` N28.2–4 + TimesFM research-only | Dicas no JSON/página única; TimesFM sem HTML |

Issues abertas que esta campanha atravessa: **ISS-007** (épico painel 1.0), **ISS-009** (laço B3/cripto/forex — cripto código feito, B3/forex não), **ISS-010** (Clear/OANDA), **ISS-011** (restante B3/FOREX + N17.2), **ISS-016** (mapa; permanece como orientação), **ISS-017** (épico desta campanha). ISS-013 (texto do freio) **não** entra nesta campanha.

---

## Ondas (Onda 0 … N)

| Onda | Sprint | O que você ganha | «Pronto» desta onda | Quem |
|------|--------|------------------|---------------------|------|
| **0** | este plano | Matriz + fila + ISS-017 | Você lê e discorda ou manda executar a N41 | Planejamento |
| **1** | **N41** | Menu **Ordens** e **Histórico** (listas, não contadores) | Depois do login você clica e vê linhas ou o vazio honesto; o painel **não** envia ordem | Código + teste |
| **2** | **N42** | Estratégias e fases no menu do dia a dia | Você vê pesquisa / sombra / paper no mesmo menu, sem promoção automática | Código + teste |
| **3** | **N43** | TimesFM / dicas de pesquisa visíveis e rotuladas | Bloco «pesquisa — não autoriza ordem»; se o modelo faltar, some com motivo | Código fail-closed |
| **4** | **N44** | Homologar **operar** US+cripto pelo painel | Um passeio: sinal → ordem aberta → fill ou recusa → performance; rebuild EasyPanel é seu | Operador + docs; código só se a lista N41 estiver cega |
| **5** | **N45** | Tá Barato no menu (sombra) | Só se N17.2 / fórmula upstream existir; senão a onda **não arranca** | Bloqueado em você / upstream |
| **6** | **N46** | B3 no painel via Clear simulada | Só depois de **N29.5** (ids no EasyPanel). Sem credencial = continua barrado | Bloqueado em você |
| **7** | **N47** | Forex no painel via OANDA Practice | Idem N29.5. Host practice, nunca live | Bloqueado em você |

A campanha **termina** quando as ondas 1–4 estão no ar e você opera US+cripto pelo menu. Ondas 5–7 são o contrato completo; **não** são fingidas como feitas na onda 4.

### O que permanece na sua mão (não é sprint de código)

| Item | Por quê |
|------|---------|
| Credenciais Clear simulada e OANDA Practice (N29.5) | Segredo fora do Git; Feature 7 B3/FOREX `[ ]` até homologar |
| Rebuild EasyPanel `trading-lab` depois de `src/` | Imagem antiga não mostra menu novo |
| Promover `prodigy_15d` a paper no banco | Default continua pesquisa |
| Homologação Tá Barato shadow→paper (N17.2) | Fórmula não recuperada; não inventar limiar |
| Fill novo na corretora | pytest e mapa **não** são fill |
| Ligar dinheiro real | Fora de escopo permanente desta campanha |

---

## Primeira sprint executável = N41

Mais alavancagem para «começar a operar»: hoje o laço Alpaca paper **já pode enviar** (Feature 7 US+cripto `[x]`), e você **não vê** a ordem no menu. Sem lista, o painel continua um quadro de sinais e um número de resultado.

N41 **não** liga B3, **não** liga OANDA, **não** promove Prodígio, **não** usa TimesFM para autorizar ordem, **não** inventa score.

Detalhe: `docs/.briefs/N41.brief.md` e bloco `## Sprint N41` no roadmap.

---

### Leituras

| Artefato | Trecho / linhas |
|----------|-----------------|
| `docs/REQUIREMENTS.md` | `### Feature 1` … `### Feature 11` (critérios `[x]` / `[ ]`) |
| `docs/REQUIREMENTS.md` | `**G-MKT — corretoras demo nomeadas` |
| `docs/ISSUES.md` | `### Command Panel v1 — mapa de áreas` |
| `docs/ISSUES.md` | `## ISS-007` · `## ISS-009` · `## ISS-010` · `## ISS-011` · `## ISS-016` |
| `docs/OPERATOR-PANEL-MAP.md` | `## 5. Ordens abertas Alpaca paper` · `## 6. Histórico / fills` |
| `docs/ROADMAP.md` | `## Índice de Sprints` · `## Sprint N16` · `## Sprint N25` · `## Sprint N26` · `## Sprint N40` |
| `docs/COMMAND-PANEL.md` | `## Surfaces` |
| `docs/VENDOR-PIN.md` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |

### Contratos afetados

N/A nesta folha de campanha (só documentos). A sprint **N41** passa a expor rotas novas no painel — ver brief N41.

### Assumido

- O painel publicado com sessão de operador continua servindo o menu (Central), não a página única antiga, no endereço raiz.
- Rebuild EasyPanel, chaves Clear/OANDA e promoção de fase Prodígio continuam seus.
- Revisão Fable / verificador de plano do parent ainda não passou neste texto; EXECUTE da N41 só depois.

## Review

`review: skip` para **esta folha de campanha**. A sprint **N41** pede `review: senior+qa` (rotas HTML novas). Sem auditor fabricado.

## Tech debt budget

O índice do roadmap é quase só feature. A regra «1 em 4 sprints de dívida» **não** aparece. Esta campanha também não abre sprint de dívida: fecha lacuna de operação. F-003 orb-parity permanece congelado. Aviso apenas.
