# N16.3 — Promoção de fase + melhoria contínua (operador)

> **`LIVE_TRADING_ENABLED=false`**. Promoção **nunca** via dashboard (`v4_web_dashboard` é read-only).  
> Rank Prodígio, PnL, HTTP 200 ou fila **não** promovem fase.  
> Complementa: `docs/HOMOLOGATION-PRODIGY.md`, `EVOLUTION_ENGINE_V38.md`.

## 1. Promoção de fase (`strategy_states`)

### Regras

| Regra | Detalhe |
|-------|---------|
| Quem | **Só operador** (SQL ou ferramenta admin), fora do painel |
| O quê | Coluna `phase` em `strategy_states` (`research` → `shadow` → `paper_limited` → `paper_validated`) |
| O que não fazer | Promover `orb` / `mean_reversion` para paper; promover por fill isolado sem checklist |

### Checklist antes de `paper_limited` (`prodigy_15d` ou `signal_copy`)

- [ ] Runbook da família lido (`HOMOLOGATION-PRODIGY` ou Feature 5 § N12).
- [ ] Gates A+B homologados em CI; sessão operador preview ok.
- [ ] `PRODIGY_PROVIDERS` definido se Prodígio e teto R$20 aplicável.
- [ ] Evidência redigida em `docs/TEST-EVIDENCE.md` (submit antes de fill opcional).
- [ ] Kill switch testado (`TRADING_LAB_KILL_SWITCH` / `/api/status`).

### SQL (exemplo — executar no Postgres do ledger)

```sql
-- Antes
SELECT strategy_key, phase, updated_at FROM strategy_states
WHERE strategy_key IN ('prodigy_15d', 'signal_copy') AND deleted_at IS NULL;

-- Promoção consciente (ex.: Prodígio após checklist)
-- UPDATE strategy_states SET phase = 'paper_limited', updated_at = NOW()
-- WHERE strategy_key = 'prodigy_15d' AND deleted_at IS NULL;

-- Rollback (emergência)
-- UPDATE strategy_states SET phase = 'research', updated_at = NOW()
-- WHERE strategy_key = 'prodigy_15d' AND deleted_at IS NULL;
```

Registrar data + motivo em nota operador (não commitar segredos).

## 2. `evolution-daily` (evidência read-only)

### Comandos

```bash
# Relatório diário (UTC date)
/app/scripts/run.sh evolution-daily --date $(date -u +%Y-%m-%d)

# Saída: /app/reports/evolution/daily/YYYY-MM-DD.json

# Registrar decisão manual (append decisions.jsonl)
/app/scripts/run.sh evolution-daily --record-decision /app/data/decision-event.json
```

Exemplo `decision-event.json` (sem credenciais):

```json
{
  "at": "2026-11-02T15:30:00+00:00",
  "signal_id": "n16-prodigy-001",
  "strategy_id": "prodigy_15d",
  "symbol": "MSFT",
  "decision": "OBSERVED",
  "reason": "rank_top10_research_only",
  "policy_version": "mvp-op-1.0"
}
```

### O que o engine **não** faz

- Não altera `strategy_states`.
- Não autoriza ordens.
- Não calcula P&L hipotético de rejeitados sem dados externos.

## 3. Checklist semanal operador (melhoria contínua)

| # | Ação | Onde ver |
|---|------|----------|
| 1 | Rodar `evolution-daily` para os últimos 5 dias úteis | `reports/evolution/daily/*.json` |
| 2 | Revisar `decisions.jsonl` (últimas entradas) | Command Panel § Melhoria contínua ou arquivo |
| 3 | Revisar webhook `journal.jsonl` status/reasons | Relatório daily `worker_statuses` |
| 4 | Confirmar nenhuma promoção automática ocorreu | `SELECT strategy_key, phase FROM strategy_states` |
| 5 | Atualizar nota em `TEST-EVIDENCE` § N16 se houve submit/fill Prodígio | Git docs PR |

Agendar no EasyPanel (cron/job) **só** após volume `/app/reports` persistente compartilhado entre serviços.

## 4. Painel (ISS-007)

`/api/status` → `command_panel.continuous_improvement` espelha `decisions.jsonl` (read-only). Tips permanecem **research**; não confundir com ordem.
