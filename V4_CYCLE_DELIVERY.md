# Trading Lab v4.0 — Orquestrador seguro de pesquisa

## Reuso antes do desenvolvimento
- Noticias: `src/news_cycle.py` existente, orquestra `news_audit`, `news_catalog`, `event_verifier`, `news_first_sim` (GET/sem ordens).
- Oportunidades: `src/market_opportunities.py` existente para EUA/B3/crypto, dados OHLCV fornecidos e validacao de timestamps.
- Performance: `src/trading_dashboard_data.py` existente agrega snapshots do broker e eventos.
- Execucao: `src/paper_gateway.py` e `src/signal_paper_runner.py` preservados, NAO acionados por esse ciclo.
- Upstream: `Jakeschincariol/day-trader-skill` consultado no GitHub; leitura do README confirmada. Codigo vendorizado/deploy SHA e paridade contra ultimo main ainda nao verificados; nao alterado.

## Novo comando
`/app/scripts/run.sh v4-cycle --reports /app/reports [--opportunity-input /app/input/verified-bars.json] [--news]`

`--news` so roda quando solicitado e requer credenciais de feed e retorno confiavel. Sem flags, gera snapshot do dashboard. Resultados no `reports/research/v4-cycle-latest.json`.

## Seguranca
- Sempre RESEARCH_ONLY; pedidos de ordem e automatic trading nao estao neste orquestrador.
- Bloqueia `LIVE_TRADING_ENABLED` diferente de false.
- Falha de qualquer modulo: `PARTIAL_OR_BLOCKED`, exit code 2.
- Nao promove estrategias Shadow e nao altera limites de risco.

## Estado da release
- Suite offline: `PYTHONPATH=src python3 -m unittest discover -s tests -q`: 197 testes OK na maquina de build.
- Nao testado em ambiente EasyPanel nem com feeds reais; entrega de desenvolvimento parcial, NAO release final autônoma.
- B3 Paper, Crypto executor com protecao persistente, risco unico multi-mercado, integracao assíncrona e dashboard web seguem pendentes.
- Nao substituir ambos os servicos do EasyPanel sem staging, backup e smoke tests de conectores.
