# Release `MVP-OP-1.1` — Tá Barato (blocked upstream; shadow homolog)

> **Tag:** `MVP-OP-1.1` (documental; Git tag opcional operador)  
> **`LIVE_TRADING_ENABLED=false`** · **G-FORM blocked** at vendor pin `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd`

## Entregue nesta sprint (código)

| Área | Evidência |
|------|-----------|
| Git First G-FORM | `docs/.briefs/N17-GIT-FIRST-REUSE.md` |
| Gate B / catálogo | `UPSTREAM_FORMULA_BLOCKED_KEYS`; fases `research` inalteradas |
| Painel read-only | `command_panel.ta_barato_shadow` + seção HTML Command Panel v1 |
| Shadow screen (lab) | `src/market_opportunities.py` — **not** upstream formula |
| Pytest | `docs/TEST-EVIDENCE.md` § Sprint N17 |

## Não entregue (honesto)

| Gap | Motivo |
|-----|--------|
| Paper homolog `ta_barato` / `momentum` | No scoring module in `day-trader-skill` at pin |
| MVP-OP-1.1 operador rebuild | Opcional até merge; campanha pode continuar em N28 |

## Operador — pendências

1. Homolog shadow→paper limitado (N17.2) **somente** se upstream publicar fórmula ou aceitar explicitamente que shadow local não é G-FORM.
2. Rebuild EasyPanel após merge desta frente (1 rebuild minor).

## Próximo na campanha

- **N28** — Feature 11 ajuste supervisionado (**blocked** G-AJUSTE).