# Prodígio — paper homolog `prodigy_15d` (Sprint N16, MVP-OP-1.0)

> **`prodigy-rank` = research only** (`PRODIGY_RANK_RESEARCH_ONLY`, `execution_authorized: false`).  
> **`queued_intent` / submit ≠ fill homologado** sem evidência operador.  
> **`LIVE_TRADING_ENABLED=false`**. Sem limiar de scoring inventado.  
> Git First: `docs/.briefs/N16-GIT-FIRST-REUSE.md`.

## Pré-requisitos

- N15 submit path documentado (`signal_copy` / `docs/TEST-EVIDENCE.md` § N12).
- Postgres: `ledger-migrate apply` + 7 linhas em `strategy_states`.
- Credenciais Alpaca **Paper** e `SIGNAL_COPY_SECRET` só no EasyPanel.
- Raw providers: `/app/reports/providers/raw` (mesmo input de `prodigy-rank`).
- **Promoção de fase (operador):** `prodigy_15d` deve estar em `paper_limited` (ou `paper_validated`) antes de Gate B permitir fila/submit — seed default é `research` (**bloqueia paper**).

```sql
-- Operador: só após decisão consciente; nunca automatizar por rank/PnL
SELECT strategy_key, phase FROM strategy_states WHERE strategy_key = 'prodigy_15d';
-- UPDATE manual fora do dashboard (read-only): phase = 'paper_limited'
```

- **`PRODIGY_PROVIDERS`:** lista CSV de `provider` slugs no JSON assinado que recebem teto R$20/trade em `signal_paper_runner` (ex.: slug escolhido no rank). Deve bater com o campo `provider` do sinal.

## Passo 1 — Rank (research)

| Passo | Ação |
|-------|------|
| 1 | `/app/scripts/run.sh prodigy-rank` |
| 2 | Verificar stdout: `mode` = `PRODIGY_RANK_RESEARCH_ONLY`, `orders_sent=0` |
| 3 | Arquivo | `/app/reports/intelligence/prodigy-top10-latest.json` |
| 4 | Painel | Command Panel → oportunidades (read-only) |

Escolher **uma** entrada com `status` = `PRODIGY_CANDIDATE_RESEARCH` (ou `OBSERVATION` se operador aceitar risco de homolog explícito). Anotar **`provider`** (slug) — não inventar score mínimo além do que o rank já calculou.

## Passo 2 — Sinal assinado

Campos `signal_copy.ALLOWED` + **`strategy_key`: `prodigy_15d`**. Assinatura HMAC com `SIGNAL_COPY_SECRET`.

| Campo | Nota |
|-------|------|
| `provider` | Slug do rank; deve estar em `PRODIGY_PROVIDERS` se teto Prodígio R$20 |
| `ttl_seconds` | **1–60** (não usar 300 — `EXPIRED_OR_FUTURE_SIGNAL`) |
| `sent_at_utc` | UTC agora; regenerar imediatamente antes do submit |
| `symbol` / preços | US equity long; mesmas regras de risco que Feature 5 |

Gerar JSON (container):

```bash
python3 << 'PY'
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, "/app/src")
from signal_copy import sign
rank = json.loads(Path("/app/reports/intelligence/prodigy-top10-latest.json").read_text())
pick = rank["top_10_research"][0]  # operador escolhe índice consciente
secret = os.environ["SIGNAL_COPY_SECRET"]
signal = {
    "provider": pick["provider"],
    "signal_id": "n16-prodigy-001",
    "symbol": "AAPL",  # operador: ticker real do setup Prodígio
    "side": "buy",
    "asset_class": "us_equity",
    "sent_at_utc": datetime.now(timezone.utc).isoformat(),
    "entry": 100.0, "stop": 99.0, "target": 102.0,
    "quantity": 1, "ttl_seconds": 60,
    "strategy_key": "prodigy_15d",
}
signal["provider_signature"] = sign(signal, secret)
Path("/app/data/received-signal-prodigy.json").write_text(json.dumps(signal, indent=2))
print("OK", pick["provider"], signal["signal_id"])
PY
```

(Ajustar `symbol`/preços; não commitar JSON com segredo.)

## Passo 3 — Risk snapshot

Mesmo fluxo que **`docs/HOMOLOGATION.md` § Feature 5** (`V4_RISK_SNAPSHOT_FILE`, `at_utc` ≤120s, contagens Alpaca alinhadas). Ver scripts de geração usados em N12.4 (operador).

## Passo 4 — Caminho A — one-shot `signal-paper` (recomendado pós-N12)

| Passo | Ação |
|-------|------|
| 1 | Preview: sem flags auto → `PREVIEW_ONLY` |
| 2 | Submit: `PAPER_SIGNAL_AUTO_ENABLED=true`, `PAPER_EXECUTION_ENABLED=true`, `PAPER_SIGNAL_ACCOUNT_ACK=I_AUTHORIZE_ALPACA_PAPER_ONLY`, `PAPER_DAILY_RISK_CONFIRMED=true`, `V4_RISK_SNAPSHOT_FILE=...` |
| 3 | `/app/scripts/run.sh signal-paper --signal /app/data/received-signal-prodigy.json` |
| 4 | Esperado | `PAPER_SUBMITTED`, `orders_sent=1` (redigir `broker_id` na evidência) |
| 5 | Alpaca paper | ordem/posição coerente |
| 6 | Reconcile | `v4-alpaca-reconcile` + nota `ledger_apply` (one-shot jsonl pode manter `linked:0`) |

## Passo 5 — Caminho B — webhook/worker (opcional)

1. POST TradingView/webhook com payload assinado incluindo `strategy_key=prodigy_15d`.
2. Gate A → worker → Gate B (fase `paper_limited` + limites).
3. Com flags auto no worker, `process_after_gate_b` delega a `signal_paper_runner` — distinto de `queued_intent` sem submit.

## Evidência (N16.4 / TEST-EVIDENCE)

Registrar em `docs/TEST-EVIDENCE.md` § Sprint N16 (quando operador executar):

- Rank file timestamp + provider escolhido (redigido)
- Fase `prodigy_15d` antes/depois promoção
- Preview + submit stdout
- Alpaca UI
- Reconcile `ledger_apply`

## O que não conta

- Rank file sozinho ou painel “oportunidades”
- `prodigy_15d` ainda em `research` com ordem na fila
- Rank top-N sem `strategy_key` / assinatura inválida
- **`PRODIGY_PROVIDERS` vazio** quando operador espera teto R$20 (cai no teto default USD 50/trade no runner — documentar, não reinterpretar como bug)

## N16.2 — gap de código

**Decisão pós-inventory:** homolog one-shot **não exige** alteração em `src/` se operador promove fase + `PRODIGY_PROVIDERS` + sinal assinado. Adaptação ingest/worker só se Caminho B falhar com gap documentado (issue separada).

**Promoção de fase + evolution:** `docs/HOMOLOGATION-EVOLUTION-N16.md` (N16.3).
