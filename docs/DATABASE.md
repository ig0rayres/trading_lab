# Database — Trading Lab

> Gerado em: 2026-10-29
> Revisado em: 2026-11-03 (v0.2, gatilhos e mercados B3, cripto e forex)
> Fase: 4 — Arquitetura de Dados
> Baseado em: docs/REQUIREMENTS.md v0.3 + docs/ARCHITECTURE.md v0.3

Pesquisa continua em arquivo JSON no volume de reports. Este documento é só o ledger de paper, na instância PostgreSQL que o operador já tem. Não há servidor novo, réplica, cache nem banco analítico. Nenhuma credencial entra aqui.

---

## 1. Decisoes

| Decisao | Escolha | Alternativa descartada | Motivo |
|---------|---------|----------------------|--------|
| BD principal | PostgreSQL da instância existente | SQLite; MariaDB | ACID para fill e restart. A instância já existe. Não há evidência de MySQL. |
| Tier de infra | Tier 1, um nó, sem máquina nova | Tier 2 (réplica, ~US$ 300/mês); Tier 3 (sharding) | Um operador. Ledger pequeno. Réplica não impede ordem falsa. |
| Composicao | Nível 1: Postgres + JSON de pesquisa | Nível 2 (Valkey ou ClickHouse); Nível 3 | Candles e relatórios de pesquisa já são arquivo. Cache não entra. |

---

## 2. Schema Inicial

O schema guarda decisão e ordem. Não guarda candle. Preço de pesquisa permanece no JSON.

### Entidades

| Entidade | Descricao | Relacoes principais |
|----------|-----------|---------------------|
| strategy_states | Fase atual de cada família (research, shadow, paper limitado, paper validado) | Nenhuma FK. Lida pelo risk-gate-b |
| signal_events | Evento que entrou no Gate A, com idempotência | 1:N risk_decisions |
| risk_decisions | Resultado do Gate B, com motivo | N:1 signal_events; 1:0..1 paper_orders |
| paper_orders | Ordem enviada só se o gate permitiu | N:1 risk_decisions; 1:N paper_fills; N:1 positions |
| paper_fills | Fill parcial ou cheio vindo da corretora | N:1 paper_orders |
| positions | Posição paper aberta por símbolo | 1:N paper_orders |
| ledger_entries | Movimento de P&L realizado, append-only | N:1 paper_fills |
| control_flags | Kill switch e tetos vigentes | Nenhuma FK |

### Diagrama ER (ASCII)

```
strategy_states          control_flags
(fase da familia)        (kill switch, tetos)

signal_events
    |
    | 1:N
    v
risk_decisions
    |
    | 1:0..1  (so se paper permitido)
    v
paper_orders ------ N:1 ---- positions
    |
    | 1:N
    v
paper_fills
    |
    | 1:N
    v
ledger_entries
```

### Colunas que importam

Não é DDL. A migration futura materializa isto.

- `signal_events`: `idempotency_key` único, `source`, `symbol`, `side`, `status` (received, rejected, accepted), `reject_code`, `received_at`. Payload guardado sanitizado, sem segredo.
- `risk_decisions`: `signal_event_id`, `strategy_key`, `decision` (rejected, paper_allowed), `reject_code`, `risk_amount`.
- `paper_orders`: `risk_decision_id`, `broker_order_id` único quando a corretora devolver, `client_order_id` único, `symbol`, `side`, `status`, `qty`.
- `paper_fills`: `paper_order_id`, `broker_fill_id` único, `qty`, `price`.
- `positions`: `symbol` único entre posições não encerradas, `qty`, `side`.
- `ledger_entries`: `paper_fill_id`, `amount`, `kind` (fill, fee, adjustment).
- `strategy_states`: `strategy_key` único, `phase`.
- `control_flags`: uma linha lógica. `kill_switch_on`, tetos numéricos já decididos no requisito.

Prefixos `nf-` e `demo-` cabem em `client_order_id`. Não são tabelas separadas.

### Convencoes aplicadas

Conforme `database-conventions`, no formato SQL (o projeto é Python, não Laravel nem Prisma):

- UUID como chave primária. Sem autoincremento.
- `created_at` e `updated_at` em toda tabela.
- `deleted_at` existe em toda tabela por convenção.
- Tabela em plural snake_case. Coluna em singular snake_case. FK `{entidade}_id`.
- Índice em toda FK, em `signal_events.idempotency_key` (único), em `paper_orders.broker_order_id` (único), em `paper_orders.client_order_id` (único), em `paper_fills.broker_fill_id` (único), em `paper_orders.status`, em `positions.symbol`.
- Apagar pai com filho ativo é bloqueado. Sem cascade.
- Uso de `deleted_at` em `paper_orders`, `paper_fills` e `ledger_entries`: a aplicação não apaga fill para corrigir erro. Correção é uma nova `ledger_entries` de ajuste. A coluna existe para a convenção. Esconder fill com soft delete quebra a reconciliação.

### O que não vira tabela

- Barra, candle e relatório de pesquisa.
- Segredo de webhook, chave Alpaca, DSN.
- Provedor Collective2 aprovado. Não há linha de copy autorizada.

---

## 3. Infraestrutura de Dados

### Topologia (Tier 1)

```
processo paper-gateway
        |
        | driver Python, pool pequeno
        v
PostgreSQL existente (um nó, failover manual)
        |
        backup já configurado nessa instância

processo de pesquisa
        |
        v
arquivos JSON em /app/reports
(nao escreve no Postgres)
```

### Connection Pooling

- Ferramenta: pool do driver Python.
- Modo: um processo de paper. Sem PgBouncer.
- Pool size: pequeno (até 5 conexões). Um operador não justifica pooler.

### Read/Write Splitting

Não se aplica. Tier 1 não tem réplica.

### Cache Strategy

Não há. Nível 1 não adiciona Valkey nem Redis.

---

## 4. Seguranca

| Item | Config |
|------|--------|
| Usuario BD | Usuário dedicado, por exemplo `trading_lab`. Só INSERT, SELECT e UPDATE nas tabelas deste schema. Sem superusuário |
| Senha | No ambiente. 32 caracteres ou mais se for gerada agora. Rotação quando o operador trocar. O valor não é escrito aqui |
| TLS app-BD | Obrigatório se o Postgres não estiver no mesmo host. Socket local é aceitável no mesmo host |
| Encryption at rest | A que a instância já tiver. Não desligar |
| Backup | O backup já existente dessa instância. Se não houver nenhum, confirmar um dump diário antes de gravar ordem |
| PITR | Não verificado. Não afirmar que existe |
| Teste de restore | Ainda não feito. Entra antes de chamar o paper de homologado |

O processo `v4-scheduler` não recebe DSN. Só o paper-gateway recebe.

---

## 5. Migration Inicial

`migrations/001_ledger_up.sql` já cria as oito tabelas. Esta fase não aplica SQL e não cria a próxima migration. A sprint que for autorizada a tocar o banco escreve `002` em cima da `001`, com teste de rollback. Sem ordem real no arquivo. Sem credencial.

---

## 6. Revisão 2026-11-03 — gatilho e mercado

O motor continua o PostgreSQL da instância que já existe. Tier 1 e Nível 1 não mudam. Um operador e um ledger pequeno não justificam réplica, Valkey nem banco analítico.

### 6.1 O que a 001 não guarda

- Mercado da ordem. `paper_orders` e `positions` têm símbolo sem dizer se é B3, cripto ou forex.
- As seis âncoras. `control_flags` só tem kill switch, risco por operação e risco do Prodígio.
- O controle de operação demo. Hoje ele é variável de ambiente.
- Quem mudou o gatilho, quando, e qual era o valor anterior.
- Preço de fill fora do real. `paper_fills.price_cents` serve para duas casas de BRL. Não serve para forex nem para cripto com mais casas.

### 6.2 Mercado

Valor fechado, em três literais:

| Valor | Mercado |
|-------|---------|
| `B3_EQUITY` | B3 |
| `CRYPTO` | Cripto |
| `FOREX` | Forex |

`signal_events`, `paper_orders` e `positions` ganham `market`. Posição aberta é única por `(market, symbol)`, não por símbolo sozinho.

Ação americana que já existe no código não ganha linha nova de mercado nesta revisão. O laço decidido é B3, cripto e forex.

### 6.3 Gatilho vigente

`control_flags` continua uma linha lógica. Colunas novas, com o valor de partida. Se a linha já existir, a migration preenche só o que estiver vazio. Não sobrescreve parada nem teto que o operador já tiver gravado.

| Coluna | Partida | Significado |
|--------|---------|-------------|
| `demo_operation_on` | false | Operação demo ligada no painel |
| `capital_cents` | 500000 | R$ 5.000 |
| `max_risk_per_trade_cents` | 5000 | R$ 50. A coluna já existe |
| `max_open_positions` | 3 | Posições simultâneas |
| `max_aggregate_risk_cents` | 20000 | R$ 200 |
| `max_daily_loss_cents` | 20000 | R$ 200 |
| `max_weekly_loss_cents` | 50000 | R$ 500 |

`kill_switch_on` e `prodigy_risk_cents` permanecem. O Prodígio em R$ 20 já está no código. Não é teto novo.

Tabela nova `market_controls`, uma linha por mercado, as três nascendo desligadas:

| Coluna | Regra |
|--------|--------|
| `market` | Único. Um dos três literais |
| `operation_on` | false até o operador ligar no painel |

Painel desligado em `demo_operation_on` ou em `market_controls` barra a ordem daquele mercado. Isso é dado, não variável de ambiente.

### 6.4 Histórico do gatilho

Tabela nova `trigger_changes`. Append-only. A aplicação não atualiza nem apaga linha daqui.

| Coluna | Regra |
|--------|--------|
| `target_table` | `control_flags`, `market_controls` ou `strategy_states` |
| `target_id` | Id da linha alterada |
| `field_name` | Coluna alterada |
| `old_value` | Texto do valor anterior. Nulo na primeira gravação |
| `new_value` | Texto do valor novo |
| `changed_at` | Momento da mudança |

Não há tabela de usuário. O operador é um só. A linha não guarda segredo.

### 6.5 Dinheiro

Âncora e P&L realizado em real continuam em centavos (`bigint`). Perda do dia e da semana é soma de `ledger_entries.amount_cents` no período, não uma coluna acumulada que possa divergir do fill.

`paper_fills` ganha `quote_currency` e `price_quote numeric(24, 8)`. Fill em BRL continua podendo usar `price_cents`. Fill em outra moeda grava `price_quote` e deixa `price_cents` nulo. A migration afrouxa o `NOT NULL` dessa coluna só para esse caso.

`ledger_entries.amount_cents` só entra na âncora de perda quando o valor está em BRL. Fill cujo resultado ainda não tem conversão verificada para real fica de fora da soma e o Gate B não abre ordem nova. Não se inventa câmbio para fechar a conta.

### 6.6 O que não entra

- Nome da corretora demo de cada mercado. Ainda não foi escolhido.
- Chave, segredo e DSN.
- Candle e relatório de pesquisa.
- Tabela de ajuste automático de estratégia. Espera fill real.

### 6.7 Próxima migration

A `002` adiciona colunas e as duas tabelas novas. Não reescreve a `001`. Não apaga fill. Não roda nesta fase.

---

## Historico de Revisoes

| Data | Versao | Alteracao | Autor |
|------|--------|-----------|-------|
| 2026-10-29 | 0.1 | Postgres existente, Tier 1, Nível 1, schema do ledger | Arquiteto de Dados (IA) |
| 2026-11-03 | 0.2 | Gatilhos, mercado B3/cripto/forex, histórico e preço fora do real | Arquiteto de Dados (IA) |
