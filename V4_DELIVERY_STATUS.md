# Trading Lab v4 - consolidated development package (NOT production-approved)

## Verified locally on 2026-10-29
- 224 pytest tests passed with `PYTHONPATH=.:src python -m pytest -q`.
- Python source compiled successfully.
- Existing US Alpaca paper modules retained, subject to their own explicit gates.
- B3/crypto local Paper intent recorder (`src/v4_shadow_broker.py`) added and tested.
- New recorder is **not a fill engine or live broker integration**. It does not claim execution or profits.
- Duplicate signal intents are rejected even before a portfolio-risk approval.
- Full, reconciled portfolio snapshot is mandatory for any local Paper intent.

## Not yet production-approved / known gaps
- Verified real-time B3 and crypto data ingestion and fill/reconciliation missing.
- No B3 broker API trading integration; local intents never submit to broker.
- Unified risk snapshot producer, with real B3/crypto broker reconciliation, not implemented.
- Fully autonomous multi-strategy selection and live data integration unfinished.
- Web dashboard and end-to-end EasyPanel deployment validation unfinished.
- Never enable live trading; preserve existing deployments until complete acceptance.

## Safe local usage
`PYTHONPATH=src python src/v4_shadow_broker.py --ticket TICKET.json --verified-snapshot RECONCILED_SNAPSHOT.json --ledger /app/reports/paper/v4-local-intents.jsonl`
This command creates a *pending intent* only when supplied with a trustworthy, externally reconciled snapshot. A `complete=true` JSON field is not independent proof of correctness; provenance must be verified upstream.
