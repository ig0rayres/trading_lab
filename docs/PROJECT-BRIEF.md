# PROJECT-BRIEF — trading-lab

> Criado em: 2026-10-29 via `/pmo project`
> Cenário: LEGADO | Perfil: null (Python 3.12 de scripts; não é Laravel nem Nest)
> Arquétipo inferido: laboratório de pesquisa com execução paper isolada [inferred]

## Visão (1 parágrafo)

Robô de laboratório para identificar, estudar, filtrar e, só depois de evidência, operar oportunidades de day trade e swing trade, LONG e SHORT, em mais de um mercado. A regra é errar rápido e barato: pesquisa e replay primeiro, paper antes de dinheiro real. Capital de paper adotado: R$ 5.000, risco R$ 50 por operação (1%), no máximo 3 posições. `LIVE_TRADING` fica desligado até execução, conciliação, segurança, monitoramento e edge líquido de custos estarem demonstrados. O código importado em 2026-10-29 é o MVP v4 de pesquisa (scheduler a cada 15 minutos, universo AAPL, MSFT, BBAS3, BBDC4, ITUB4, BTCBRL, ETHBRL). Ele não é executor automático. Webhook, News First e motores de paper existem no repositório e não entram nesse ciclo. A pasta `trading-lab-v4-mvp-implantavel` é o mesmo MVP, anterior, e ficou de fora do git. [from-artifact]

## Plano de Montagem

| ID | VEM PRONTO | VAI SER ADAPTADO | NOVO DESTE PROJETO |
|----|------------|------------------|---------------------|
| BOM-1 | Snapshot v4 de pesquisa já no repo: `src/`, `tests/`, `Dockerfile`, `scripts/run.sh`, universo de 7 símbolos. Scheduler não importa código de ordem. [from-artifact] | Fixar esta árvore como raiz do projeto e manter `LIVE_TRADING_ENABLED=false`. | — |
| BOM-2 | Funções `trader-entry`, `trader-exit`, `trader-budget`, `trader-risk` e `trader-scanner` do `day-trader-skill`, carregadas por `src/original.py`. [from-artifact] | Pin do checkout em `vendor/` com teste de paridade. O ZIP não trouxe esse vendor. [needs-confirm] | Só o que o inventário de reuso mostrar que o upstream não cobre. |
| BOM-3 | Módulos já presentes de gateway paper, webhook TradingView, News First, shadow, ledger e dashboard somente leitura. [from-artifact] | — | Homologação ponta a ponta (sinal → risco → ordem paper → fill → ledger) ainda não existe e não começa nesta fase. |
| BOM-4 | Regras de capital e bloqueio: R$ 5.000 / R$ 50 / 3 posições; sem copy de provedor Collective2 aprovado. [from-artifact] | — | Evidência de edge (custos, walk-forward, calendário NY). ORB intraday reportado segue negativo. |

> Contagens de teste escritas nos markdowns (224, 355, 358, 391, 394, 395) são relato do pacote. Esta importação não reexecutou o pytest.

## Próximo passo

`/analista planejar` — nova conversa.
