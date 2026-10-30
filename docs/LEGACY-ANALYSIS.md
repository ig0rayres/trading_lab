# Analise do legado — Trading Lab

> Gerado em: 2026-10-29
> Cenario: LEGADO
> Base: snapshot importado em `master` (`ba36049`) e os contratos de `docs/ARCHITECTURE.md` e `docs/DATABASE.md`

Este arquivo nao e uma auditoria linha a linha. E o mapa do que o codigo atual e, do que os contratos passam a exigir, e do que nao foi comprovado.

---

## 1. O que o codigo ja separa

- `src/v4_scheduler.py` nao importa cliente de corretora. O ciclo de pesquisa dispara `v4_run_once.py`.
- Varios modulos v4 recusam `LIVE_TRADING_ENABLED` diferente de false.
- `src/v4_alpaca_reconcile.py` se declara `READ_ONLY`.
- O webhook vive em `src/tradingview_webhook.py`, comando separado no `scripts/run.sh`.

## 2. Divida

| Item | Classe | Por que |
|------|--------|---------|
| Nao existe migration nem DSN de ledger. As tabelas do DBML ainda nao estao no Postgres. | Alta | O contrato de paper nao tem onde persistir de verdade. |
| Webhook, News First, copy e gateway existem e nao entram no ciclo do scheduler. | Alta | Presenca de modulo parece integracao. Nao e. |
| `src/v4_readiness.py` trata existencia de arquivo em `/app/src` como binding. | Media | Arquivo no disco nao e homologacao. |
| Pytest nao foi reexecutado nesta maquina. Contagens dos ZIPs continuam relato. | Alta | Sem nodeid, nao ha suite comprovada. |
| `vendor/day-trader-skill` ausente. | Alta | A regra do projeto manda reusar esse codigo. |
| Dashboard pode ser ligado por comando `v4-dashboard` sem a auth que o contrato agora exige na porta publica. | Media | O MVP de pesquisa manda nao publicar porta. O contrato cobre o caso em que alguem publicar. |
| Formulas de Ta Barato Demais, momentum e Prodigy nao recuperadas. | Alta | Inventar limiar violaria o requisito. |
| Calendario de feriado citado como incompleto. | Alta | Sinal fora de sessao nao pode virar ordem. |

Nada aqui foi classificado como critico de seguranca exploravel sem reler o webhook com o segredo real. O risco conhecido e operacional: confundir fila com fill, e ligar live. Os dois ja estao bloqueados por politica, nao por uma prova ponta a ponta.

## 3. Riscos de levar este codigo ao contrato novo

- Gravar ordem no Postgres antes do Gate A e do Gate B existirem como funcao que o gateway e obrigado a chamar.
- Apontar o paper-gateway para a conta errada. So paper. A chave fica no ambiente.
- Substituir os servicos EasyPanel atuais com este snapshot. O requisito manda nao fazer isso.
- Tratar `deleted_at` como borracha de fill. O DBML deixa a coluna e proibe esse uso.

## 4. O que esta fora deste mapa

- Imagem que esta rodando no EasyPanel. Nao houve export.
- Se o Postgres existente ja tem backup ou PITR.
- Conteudo do `.env` de exemplo. Nao foi lido.
