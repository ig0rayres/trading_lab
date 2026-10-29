# V4 — Reconciliação parcial Alpaca Paper (read-only)

O comando `v4-broker-snapshot --output /app/reports/v4/alpaca-partial.json` consulta apenas GET `/v2/account`, `/v2/positions` e `/v2/orders?status=open&limit=500` da Alpaca Paper. Requer as credenciais Paper e `USD_BRL_REFERENCE` configurada explicitamente. Não executa ordens, não cancela ordens e não consulta corretora real.

O relatório contém caixa, posições, valores de mercado e ordens abertas observadas na Alpaca. Campos `complete`, `broker_reconciled`, `daily_pnl_verified`, `weekly_pnl_verified` e `execution_authorized` permanecem `false`: é **somente uma reconciliação parcial**. É proibido convertê-los em `true` sem verificar independentemente todos os mercados, stops, P&L, FX e ordens pendentes. Valor de mercado não revela distância até stop; referência cambial não é cotação ao vivo.

A API externa **não foi testada em rede nesta rodada**; foram usados fixtures/mocks. Para o ciclo de decisão, passar `--risk-snapshot` com este relatório resulta em bloqueio fail-closed. Os serviços EasyPanel atuais não foram alterados.

Próximo marco: integrar livros de posição B3 e crypto, event logs duráveis, cálculos verificáveis de P&L e stop risk, e controle único de ordem em tempo real com reserva atômica/idempotência.
