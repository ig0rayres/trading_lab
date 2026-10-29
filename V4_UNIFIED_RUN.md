# Trading Lab v4 — Unificado (pesquisa, não homologação final)

O comando `v4-run-once` coleta dados públicos dos mercados configurados, passa pelo scanner,
consolida notícias/sinais opcionais, executa a prévia de risco e grava quatro relatórios JSON.
Nunca envia ordens. Um erro de upstream torna o ciclo parcial/bloqueado, sem fabricar sucesso.

## Exemplo

`python src/v4_run_once.py --universe config/universe.json --output-dir reports/v4`

No EasyPanel: `/app/scripts/run.sh v4-run-once --universe /app/config/universe.json --output-dir /app/reports/v4`.
O arquivo de universo é personalizável; os feeds Yahoo/Binance são somente para pesquisa.

## Critérios ainda pendentes para uma versão FINAL de operação automática

- Disponibilidade/limites/autenticidade e licenças dos feeds e notícias em rede validada.
- Integração autorizada de sinais à execução, com recibos reais Alpaca Paper.
- Risco único persistente/atômico, idempotência global e ordens pendentes reconciliadas.
- Execução simulada e validação de posições em B3 e crypto, incluindo saídas e custos.
- P&L confirmado com histórico e comissões completo; testes de recuperação após reinício.
- Dashboard web e autenticação testados em implantação real; teste de operações E2E.

Não substituir os serviços em produção com este ZIP. Nunca definir LIVE_TRADING_ENABLED=true.
