# Prodígio paper homolog (N16 — draft)

> **Research rank ≠ ordem.** `prodigy-rank` never sets `execution_authorized`. Paper only with `strategy_key=prodigy_15d` and operator phase promotion. `LIVE_TRADING_ENABLED=false`.

## Pré-requisitos

- MVP-OP submit path ok (`signal_copy` / N15).
- `strategy_states`: `prodigy_15d` remains **research** until operator sets `paper_limited`.
- Raw provider data under `/app/reports/providers/raw` (same as `scripts/run.sh prodigy-rank`).

## Passos (operador)

| # | Ação |
|---|------|
| 1 | `/app/scripts/run.sh prodigy-rank` → `reports/intelligence/prodigy-top10-latest.json` |
| 2 | Pick top entry **research only**; map to signed signal JSON (`strategy_key=prodigy_15d`) — reuse `signal_copy` signing; **no invented thresholds** |
| 3 | Gate A/B via webhook/worker **or** one-shot `signal-paper` with same env chain as Feature 5 (`docs/HOMOLOGATION.md` § Feature 5) |
| 4 | Evidência redigida in `docs/TEST-EVIDENCE.md` (new § N16 when sprint closes) |
| 5 | Command Panel: opportunities table reads rank file; still read-only |

Git First reuse: `docs/.briefs/N16-GIT-FIRST-REUSE.md`.
