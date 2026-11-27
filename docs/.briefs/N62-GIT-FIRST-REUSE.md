# N62 — Git First / reuse inventory

> Sprint N62 · Inbox pérola · `plan_only` · LIVE false

## Upstream / vendor

- Pin: `docs/VENDOR-PIN.md` — `3d0f4ef` (read-only; no bump in N62).
- No new trader-* logic; Feature 4 thresholds stay in `prodigy_rank`.

## Reuse inventory

| Capability | Path | Decision |
|------------|------|----------|
| 15d rank | `src/prodigy_rank.py` `calculate` | **Adapt** — add P/L>0 gate, sort by `reported_pnl_sum` |
| Preapproval queue | `src/panel_ops_data.py` `build_preapproval_queue` | **Adapt** — top 10 pearl only |
| Refresh job | `src/v4_web_dashboard.py` `_live_criteria_job` | **Reuse** — no change to C2 collect |
| Sinais UI | `src/panel_ops_html.py` | **Adapt** — inbox copy + reload script fix |
| Tests pattern | `tests/test_panel_ops.py` N54–N61 | **Extend** — N62InboxPearlTests |
| REQUIREMENTS Feature 4 | `docs/REQUIREMENTS.md` | **Docs** — align checkbox wording |

## Gaps (new work)

- Explicit `reported_pnl_sum > 0` before candidate status (contract vs code).
- Remove TV/pending from primary pearl queue (product).
- Reload button stuck after long POST (UX bug).

## Tests required

- `test_prodigy_rank.py` — negative P/L not candidate; sort order.
- `test_panel_ops.py` — pearl queue ≤10, no TV, metrics present.

## Security / LIVE

- `LIVE_TRADING_ENABLED=false`; refresh `orders_sent=0`; approve ≠ fill.