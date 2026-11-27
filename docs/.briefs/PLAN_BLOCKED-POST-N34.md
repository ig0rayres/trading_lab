---
planner_subagent_id: plan-only
auditor_subagent_id: plan-only
audited_at: 2026-11-16T19:49:00-03:00
findings_count: 0
severity_summary:
  CRITICAL: 0
  HIGH: 0
  MEDIUM: 0
  LOW: 0
audit_evidence_path: ""
sprint_id: null
planner: planejador-melhorias
status: PLAN_BLOCKED
plan_only: true
decision: N29.5
titulo_humano: Homologação ao vivo das contas demo, sem sprint de código inventada
---

# PLAN_BLOCKED após N34 — sem N35 de código

> Gerado: `/pmo plan` 2026-11-16 · pós-N34 concluída · PR **#45** merged · worktree `front/n27-alpaca-loop`  
> `auditor_subagent_id: plan-only` — revisão Fable / plan-verifier do parent. Não inventar UUID de auditor.

## Classificação

Categoria **N** (ROADMAP existe, `fase_atual` 10, demanda é continuação da campanha Features 7–11, não regressão). Subtipo **feature-sem-dominio** se houvesse código honesto. Confiança alta. `needs_diagnosis`: false.

Sinal que decidiu N (não F): ISS-011 restante é homologação humana + fórmula não recuperada, não um defeito.

**Veredito:** `PLAN_BLOCKED`. Não criar sprint N35. `sprint_atual` permanece vazio. `plan_only: true`.

### Em uma frase

O laço paper da bolsa brasileira e do câmbio já está no código; o que falta é você credenciar as contas demo e reconstruir a imagem — Tá Barato continua parado até a fórmula original aparecer.

### O que muda para você

- Não há sprint de código nova: inventar limiar ou atestar homologação no CI seria mentira
- O próximo passo é seu, no painel de deploy: reconstruir os dois apps e colar as chaves demo só lá
- Sem essas chaves, bolsa brasileira e câmbio continuam visíveis e barrados com motivo
- Tá Barato em paper espera a fórmula recuperada; não inventamos percentil

| nº | Entrega | Como você confere |
|----|---------|-------------------|
| 1 | Decisão única: homologar contas demo Clear e OANDA (não Tá Barato, não espera vazia) | Depois do rebuild com a imagem do pedido 45, o painel deixa de barrar bolsa brasileira e câmbio só por falta de chave |

## Por que não há N35 de código

Restante ISS-011 (pós-N33/N34):

| Caminho | Tipo | Por que não vira sprint de código agora |
|---------|------|-----------------------------------------|
| **N29.5** | operador | Credenciais Clear simulado + OANDA Practice só no EasyPanel; homologação ao vivo. Mock/CI da N34 **não** fecha ISS-010. |
| **N29.6** | docs | Depende de N29.5. N27.2 já está `[x]` na N34; carimbar N29 `concluida` agora seria mentira. |
| **N17.2** | operador + G-FORM | Homolog shadow→paper Tá Barato. Fórmula/percentis **não recuperados** (dúvida 1 aberta). Inventar limiar é proibido. Código N17.1/N17.5 já entregue. |
| **N17.4 / F-003** | opcional | Paridade ORB; catálogo **nunca paper**. Não é o próximo da campanha. |

Nada disso é produto executável sem inventar scoring, HTTP real no CI, ou atestado de fill. Adaptadores já enviam só símbolo/lado/quantidade — ampliar stop/alvo seria especificação nova, não recuperação.

## Decisão (uma)

**N29.5** — operador credencia Clear (B3) + OANDA Practice (câmbio) e homologa ao vivo.

Não N17.2: G-FORM continua bloqueado no pin; paper de Tá Barato sem fórmula é invenção.  
Não hold vazio: a N34 acabou de ligar o laço. **Atualização:** operador atestou EasyPanel **#46 no ar** (`d99b332`, 2026-11-16) — cobre wiring N34; **ainda falta** colar credenciais (passo 3).

N17.2 volta só se a fórmula aparecer no vendor pinado (ou o operador declarar por escrito que não existe).

## Próximo passo do operador

1. ~~Rebuild EasyPanel~~ — **#46 no ar** (tip `d99b332`, atestado operador 2026-11-16; inclui N34/#45). **Não é fill.**
2. Manter `LIVE_TRADING_ENABLED=false`.
3. Colar **só no EasyPanel** (nunca no Git nem no chat):

| Nome | Valor esperado |
|------|----------------|
| `DEMO_ACCOUNT_PATH_B3_EQUITY` | `clear_smart_trader_simulated` |
| `DEMO_ACCOUNT_PATH_FOREX` | `oanda_fxtrade_practice` |
| `CLEAR_SIM_BASE_URL` | URL do simulador Clear |
| `CLEAR_SIM_API_KEY` | chave simulada |
| `CLEAR_SIM_API_SECRET` | segredo simulado |
| `OANDA_PRACTICE_API_TOKEN` | token Practice |
| `OANDA_PRACTICE_ACCOUNT_ID` | id da conta Practice |

4. Confirmar homologação ao vivo (posição/ordem/fill demo) **sem** colar segredo. Aí sim N29.6 / Feature 7 B3+câmbio.
5. Dinheiro real continua desligado. HTTP 200 ou fila paper **não** é fill.

### Leituras

| Artefato | Trecho / linhas |
|----------|-----------------|
| `docs/ROADMAP.md` | Sprint N34 Status `concluida`; N29 Status `planejada`; N29.5/N29.6 `[ ]`; N17.2 `[ ]`; G-FORM blocked @ pin |
| `docs/ISSUES.md` | ISS-010 aberto (homolog N29.5); ISS-011 restante N29.5 + N17.2 |
| `docs/REQUIREMENTS.md` | Feature 7 B3/FOREX `[ ]`; §9 dúvida 1 Tá Barato aberta; G-MKT |
| `EASYPANEL.md` | § G-MKT demo paths (names only) |
| `.cursorsession` | `sprint_atual` null; `previous_sprint` N34; `checkpoint.phase` validated |

### Contratos afetados

N/A — nenhum contrato de API/dados muda neste bloqueio.

### Assumido

- EasyPanel ainda está na imagem do pedido 42 até o operador reconstruir na 45.
- Contas Clear simulada e OANDA Practice existem ou o operador as abre; ids não entram no Git.
- Fórmula Tá Barato/momentum continua ausente no pin do vendor.
- Parent não inicia sprint (`sprint_atual` vazio) até N29.5 ter evidência humana ou G-FORM ser respondido.
