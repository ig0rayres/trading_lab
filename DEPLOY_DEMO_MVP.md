# Trading Lab v4 — MVP de pesquisa em ambiente demo isolado

**Este MVP NAO envia ordens para Alpaca nem para qualquer corretora.** E a primeira fase da homologacao pratica com dados publicos de mercado e ambiente Shadow. Nao representa a validacao de sinais/news ou de operacao Paper automatica.

## EasyPanel: CRIAR um terceiro servico temporario `trading-lab-demo`

1. Nao substituir `trading-lab` nem `trading-lab-webhook`; nao copiar chaves de API nem secrets de producao.
2. Enviar o ZIP e usar o diretorio `trading-lab-v4/` como contexto do Docker build, ou extrair seu conteudo como raiz do contexto.
3. Selecionar o Dockerfile **`Dockerfile.demo`** (nao o Dockerfile padrao).
4. Variaveis: `LIVE_TRADING_ENABLED=false`, `PAPER_EXECUTION_ENABLED=false`, `PAPER_SIGNAL_AUTO_ENABLED=false`, `ALPACA_PAPER_TRADE=true`. Sem `ALPACA_API_KEY`/`ALPACA_SECRET_KEY` nesta primeira fase.
5. Volume persistente exclusivo para demo em `/app/reports`; nao montar volumes compartilhados com os dois servicos existentes.
6. Sem porta publica e sem dominio nesta fase. O processo padrao `v4-scheduler` coleta pesquisa de 15 em 15 min. Se uma API falhar, o log e `v4_scheduler.json` assinalam `FAILED_OR_BLOCKED`; nenhuma ordem e enviada.
7. Conferir logs e os arquivos `/app/reports/v4/v4_scheduler.json`, `v4_manifest.json`, `v4_market.json`, `v4_decisions.json`, `v4_risk.json` (os nomes tem prefixo v4_ no codigo). Acesso ao relatorio via os recursos do EasyPanel; a interface web nao sera publicada sem autenticacao.
8. Para testes manuais da interface em acesso restrito: `./scripts/run.sh v4-dashboard --root /app/reports --host 127.0.0.1 --port 8765` (somente leitura, loopback). Nao expor publicamente sem proxy autenticado.

## Criterios objetivos de observacao

- Dados atuais de pelo menos um ticker de cada mercado (EUA, B3, crypto) com moeda, horario e proveniencia; estados de falha visiveis.
- Scanner em Shadow e relatorios produzidos mesmo se nao houver sinais; sem qualquer ordem.
- `orders_sent=0` em todos os manifests; chaves reais ausentes; flag live false.
- Repetir por varias sessoes e conferir gaps, cobertura e custos antes de habilitar a fase **Alpaca Paper**.

## Fase 2 (separada): conta Alpaca Paper

A ordem AAPL do teste anterior comprovou a conectividade Paper, mas nao validou o fluxo automatico v4. A fase 2 requer integracao do risco, verificador de preco, deduplicacao e reconciliacao de ordens no fluxo completo, seguida de teste com uma unica ordem controlada e protecao de stop; nao habilitar com este ZIP.
