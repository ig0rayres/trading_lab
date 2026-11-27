# N31.0 Git First — evolution-daily + official TimesFM (research-only)

> Rock N31.0 · 2026-11-16 · frente `front/n27-alpaca-loop` · **no vendor bump**

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| Host checkout `/home/igor/cursor/trading-lab/vendor/day-trader-skill` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` (matches pin) |

GitHub `Jakeschincariol/day-trader-skill` main: not re-checked in this headless run (fail-closed: reuse pin above only).

## Reuse inventory

| Capability | Path | Decision | Rationale | Tests |
|------------|------|----------|-----------|-------|
| Daily read-only review | `src/evolution_engine.py` `review` / `add_decision` | **Extend** | ISS-012 fills + non-fills → labeled tips; `orders_sent=0` | `tests/test_evolution_engine.py` |
| Decision ledger | `evolution/decisions.jsonl` | **Reuse** | append-only via `add_decision` | existing |
| CLI hook | `scripts/run.sh` `evolution-daily` | **Call** | no third EasyPanel app | `rg evolution-daily` |
| Fill vs queue/blocked | `src/panel_ops_data.signal_destination` | **Call** | same taxonomy as panel PnL exclusions | `tests/test_panel_ops.py` |
| Suggestion surfaces | `src/trading_dashboard_data.py` N28.1 | **Extend** | merge daily tips into `continuous_improvement` | `tests/test_n28_suggestion_labels.py` |
| TimesFM (Google) | PyPI `timesfm` · repo `google-research/timesfm` | **Reuse official API** via `src/timesfm_context.py` | Context7 `/google-research/timesfm`; **no** model reimplementation | `tests/test_timesfm_context.py` |
| trader-* | `vendor/…` via `src/original.py` | **Reuse / no rewrite** | MIT loader | `tests/test_vendor_verify.py` |
| N28.2–4 parameter apply | ROADMAP `## Sprint N28` | **Defer** | method only in N31; do not edit N28 task rows | — |

## TimesFM package (official)

| Item | Record |
|------|--------|
| PyPI package | `timesfm` (optional extras `timesfm[torch]` or `timesfm[mlx]`) |
| Import paths | `timesfm` (2.x torch) · `timesfm3.mlx.TimesFM3Forecaster` (3.x MLX) per upstream README |
| Context7 library ID | `/google-research/timesfm` |
| Default image | **Not** a required `requirements.txt` dependency — adapter fail-closed (`timesfm_status=UNAVAILABLE`) |
| Enable in lab | `TIMESFM_ENABLED=1` **and** `TIMESFM_CHECKPOINT` (e.g. `google/timesfm-2.5-200m-pytorch`) — operator-only |
| License note | TimesFM **code** Apache-2.0; some **3.0 checkpoints** may carry non-commercial weight terms — treat 2.5 PyTorch checkpoint as conservative default when enabling |
| Fail-closed | `ImportError`, missing checkpoint, or disabled env → no numeric forecast; daily tips from fills/non-fills still emitted |

## Security / invariants

- `LIVE_TRADING_ENABLED=false` unchanged.
- Tips and TimesFM blocks never call `process_after_gate_b` or paper submit.
- No Tá Barato / momentum / Prodigy thresholds derived from forecast.