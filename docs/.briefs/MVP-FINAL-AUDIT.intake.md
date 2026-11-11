# Intake — auditoria contrato × entrega (plataforma operacional final)

> Gerado: 2026-11-11 · `/pmo plan` · operador pediu auditoria completa e plano em ondas até a plataforma ficar operacional conforme o contrato.
> Rascunho de entrada para o planner. Não altera ROADMAP.

## Contrato vigente

O contrato é a soma de:

- `docs/REQUIREMENTS.md` no `main` (v0.1): Features 1–6.
- Revisão v0.2/v0.3 de 2026-11-03, aprovada pelo operador, **só na branch local `front/n16-8-panel` (commit `3d26a13`, nunca enviado ao GitHub)**: Features 7–11 em `docs/REQUIREMENTS.md`; `docs/ARCHITECTURE.md` §12 com ADR-006, ADR-007, ADR-009, ADR-010 (ADR-008 revogada); `docs/DATABASE.md` §6; `docs/api-spec.yaml` 0.2.0; `docs/design/DESIGN.md`.
- Objetivo revisado (v0.3): a plataforma opera sozinha nas contas demo de **B3, cripto e forex**, com as estratégias já definidas, sem o operador disparar cada ordem. Âncoras de risco param a operação sozinhas. O operador acompanha e ajusta tudo num painel com login, sem Exec no EasyPanel. Conta real continua desligada.

Invariantes do contrato (não negociáveis neste plano): `LIVE_TRADING_ENABLED=false`; nenhum limiar inventado para Tá Barato, momentum ou Prodígio; ORB e mean reversion fora de paper; Collective2 fechado; dois serviços EasyPanel, sem terceiro; reuso do `day-trader-skill` via `src/original.py`.

## Matriz contrato × entregue

| Feature | Exigência | Entregue | Evidência | Lacuna |
|---------|-----------|----------|-----------|--------|
| F1 Pesquisa e shadow | ciclo sem ordem, manifesto honesto | sim | REQUIREMENTS F1 `[x]`, N11 | nenhuma |
| F2 Gate A | rejeição, idempotência, trilha | sim | F2 `[x]`, D3, N9 | nenhuma |
| F3 Gate B | tetos, kill switch, sessão | parcial | F3 `[x]` | calendário B3 e feriados; dois tetos divergentes (`gate_b_risk` R$ 5.000 vs `portfolio_risk_v4` R$ 10.000, ARCHITECTURE §12.1); `control_flags` de risco não lidas |
| F4 Catálogo | fases persistidas, sem limiar inventado | parcial | F4 `[x]`, N7/N8 | Tá Barato, momentum e score Prodígio sem fórmula recuperada (N17 planejada; dúvidas 1–3 abertas) |
| F5 Paper ponta a ponta | fill real + posição | parcial | submit `PAPER_SUBMITTED` MSFT 2026-11-02 e NVDA Prodígio 2026-11-03 | **fill `[ ]`** (P-001b); `paper_orders` não grava `broker_order_id`; sem acompanhamento até fill |
| F6 Observabilidade | painel, kill switch visível | sim (leitura) | N16.8, N18 (`v4-ops`, 200, `command-panel-v1`) | painel mostra; não opera |
| F7 Operação autônoma demo | sinal vira ordem sem operador; âncoras; restart sem duplicar | **não** | — | worker sem laço (não está em `v4_ops_main.sh`); `LOSS_DATA_NOT_VERIFIED` bloqueia por falta de P&L de fill; nenhuma conta demo para B3 e forex; forex fora do universo e do avaliador de carteira |
| F8 Central de controle | login, editar âncoras, ligar estratégia, parada | parcial, não publicado | N19.1 migração `002` e N19.2 PATCH de gatilho com sessão de operador — **só no commit local `3d26a13`** | login de verdade (hoje cookie `trading_lab_session` vindo do ambiente); tela; nada disso no `main` |
| F9 Sinais e Prodígio | lista com destino e motivo; ranking e cópias | parcial | ledger `signal_events`, `prodigy-rank` | tela de sinais com gate e âncora que barrou |
| F10 Performance | resultado só de fill confirmado | não | painel mostra P&L bruto de snapshots | depende de F5 fill e do laço da ordem |
| F11 Sugestões e ajuste | sugestão rotulada; ajuste dentro da faixa | não | tips research no painel | método do ajuste é dúvida aberta 8; ADR-007 manda esperar fill real |

## Itens abertos registrados

- ISS-005 parcial (fill), ISS-007 planejado (épico MVP-OP), ISS-009 aberto (laço demo, N19).
- F-003 orb-parity aberto e congelado.
- N12, N13, N15 aparecem "em execução" ou "planejada" no índice do ROADMAP, com tarefas de operador pendentes.
- Dúvidas abertas em REQUIREMENTS v0.3: 1–3 (fórmulas), 4 (SHA no EasyPanel), 7 (Postgres), 8 (método do ajuste), 9 (login), 10 (painel escreve).

## Decisões que só o operador pode tomar

1. Conta demo de cada mercado: B3, cripto, forex. ADR-010 proíbe inventar o nome. Sem conta que devolva posição, ordem e fill, o mercado fica barrado por contrato.
2. Origem das fórmulas de Tá Barato e momentum: se o upstream não as tiver, a família fica fora por contrato (não inventar limiar).
3. Método do ajuste automático (F11), depois de existir fill real.

## Pedido ao planner

Montar o plano em ondas (sprints N com `depends_on`, ondas topológicas) até fechar todas as lacunas da matriz, começando por publicar o contrato v0.3 e o código N19.1–N19.2 hoje presos no commit local. Cada sprint precisa de critério conferível pelo operador. Marcar explicitamente o que depende das decisões do operador acima.
