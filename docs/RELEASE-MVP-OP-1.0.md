# Release `MVP-OP-1.0` — Prodígio paper + Command Panel v1

> **Tag:** `MVP-OP-1.0` (documental; Git tag opcional operador)  
> **`LIVE_TRADING_ENABLED=false`** · Alpaca **paper** only · **submit ≠ fill**

## Entregue neste release

| Área | Evidência |
|------|-----------|
| Git First Prodígio | `docs/.briefs/N16-GIT-FIRST-REUSE.md` |
| Runbooks operador | `docs/HOMOLOGATION-PRODIGY.md`, `docs/HOMOLOGATION-EVOLUTION-N16.md` |
| Command Panel v1 | PR #14 · `/api/status` → `command_panel` |
| Rank research | `prodigy-rank` → `prodigy-top10-latest.json` |
| Paper submit Prodígio | Operador 2026-11-03 · `TEST-EVIDENCE` § N16 |
| Paper submit copy (0.9) | Operador 2026-11-02 · `TEST-EVIDENCE` § N12 |

## Operador — critérios deste tag

| Critério | Status |
|----------|--------|
| `prodigy_15d` fase `paper_limited` (SQL operador) | ok 2026-11-02 |
| `PAPER_SUBMITTED` Prodígio (`strategy_key=prodigy_15d`) | ok 2026-11-03 (NVDA bracket) |
| Painel remoto bearer (N16.8) | **pendente** |
| Fill limit Feature 5 / Prodígio (P-001b) | **pendente** (ordem `new`/`held` ok para demo) |

## Deploy

- **1 rebuild** EasyPanel recomendado após merge `main` com N16.7 (#14) se ainda não aplicado no `trading-lab`.
- Doc-only merges **não** exigem rebuild (`docs/MVP-DEMO-RUNBOOK.md` §5).

## Fora de escopo

- Live trading, scoring inventado, promoção automática de fase por rank/PnL.
- MVP-OP-1.1 (N17): Tá Barato upstream — sprint planejada.

## Smoke pós-deploy

```bash
bash /app/scripts/mvp-demo-smoke.sh
```
