# Trading Lab v4 — MVP implantavel de pesquisa (29/10/2026)

## O que funciona neste MVP
- Pesquisa periodica (a cada 15 min) de AAPL, MSFT, BBAS3, BBDC4, ITUB4, BTCBRL e ETHBRL via adaptadores publicos.
- Scanner e consolidacao de decisoes em modo Research/Shadow, avaliacao de risco sem autorizacao de ordens.
- Persistencia de relatórios no volume `/app/reports/v4`.
- Testes locais: 391 passed, 11 subtests passed (`PYTHONPATH=src python -m pytest -q`).

## DEPLOY NO EASYPANEL (MVP)
1. **Crie um terceiro app Docker chamado `trading-lab-mvp`**. Nao substitua `trading-lab` ou `trading-lab-webhook` e nao compartilhe volumes.
2. Faca upload deste ZIP **extraido como raiz do contexto de build**. Use o `Dockerfile` incluso.
3. Nao altere o comando de inicializacao: o Dockerfile ja executa `v4-scheduler` com o universo configurado.
4. Monte um volume **exclusivo** e persistente em `/app/reports`.
5. Defina `LIVE_TRADING_ENABLED=false`, `PAPER_EXECUTION_ENABLED=false`, `PAPER_SIGNAL_AUTO_ENABLED=false`.
6. **Nao configure chaves da Alpaca ou de corretoras**; nenhuma e necessaria para a pesquisa.
7. Nao publique dominio ou porta neste app. Confira logs do container e o relatorio `/app/reports/v4/v4_scheduler.json`.
8. Em ciclos com disponibilidade de fontes externas, confira `v4_market.json`, `v4_decisions.json`, `v4_risk.json` e `v4_manifest.json` no mesmo diretorio. Se faltar fonte, o estado indicara `FAILED_OR_BLOCKED` ou `PARTIAL_OR_BLOCKED`: isso nao envia ordens.

## Limites e criterios de aceite
- **Nao e um executor automatico de operacoes**. O scheduler nao importa nem chama codigo de envio de ordens.
- Os dados publicos de Yahoo e Binance nao foram homologados contra execucao real nesta sessao. API indisponivel/limitada e um bloqueio visivel; nao e motivo para habilitar ordens.
- Webhook/News First/Prodigios e motores de Paper existem na base, mas nao estao automaticamente ligados ao ciclo deste MVP.
- O dashboard web existe no codigo mas nao deve ser exposto sem autenticacao ou proxy; este deploy e privado/sem porta publica.
- Operacoes Alpaca Paper anteriores ficam intocadas nos apps atuais.

## Evolucao
Depois de observar coleta real de dados nos tres mercados, o proximo marco e habilitar o monitor/dashboard com acesso autenticado e executar homologacao de integracoes Paper em ambiente isolado. Nenhum caminho deste MVP autoriza ordens.
