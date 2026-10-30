# Test evidence — Sprint D1

> Generated: 2026-10-30  
> Sprint: D1 — Baseline verificável  
> `LIVE_TRADING_ENABLED=false`

## Upstream pin

| Item | Value |
|------|--------|
| Submodule | `vendor/day-trader-skill` |
| SHA (documented) | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| Reference | `docs/VENDOR-PIN.md` |

## vendor_verify (offline, real upstream modules)

Command:

```bash
UPSTREAM_DIR="$PWD/vendor/day-trader-skill" LIVE_TRADING_ENABLED=false PYTHONPATH=src \
  python3 src/vendor_verify.py
```

Result (2026-10-30):

- **status:** PASS  
- **source:** ACTUAL_ORIGINAL_MODULES  
- **checks:** first closed-bar entry; scanner/entry parity; 1R/2R target; sizing and risk PASS; invalid plan rejection  
- **live_orders_enabled:** false  

Note: `upstream_commit` in JSON may show `UNVERSIONED_UPSTREAM` on this host if `git -C vendor/...` is blocked by safe-directory; the pin above is authoritative.

## orb-parity (`parity.py`)

Not run in D1: requires v0.5 report artifacts (`watchlist-*.json`, trades CSV, cache under `/app/reports/orb`). Run when those paths exist:

```bash
UPSTREAM_DIR="$PWD/vendor/day-trader-skill" PYTHONPATH=src python3 src/parity.py --date YYYY-MM-DD ...
```

## Pytest full suite

| Run | Status | Notes |
|-----|--------|-------|
| Local (Cursor agent, 2026-10-30) | **Not executed** | Environment policy blocked `pip install` / venv (#385 ask mode). |
| CI (GitHub Actions) | **Success** | [Run 41041762290](https://github.com/ig0rayres/trading_lab/actions/runs/41041762290) — workflow **CI #3** on `main` @ `f597f8b` (2026-10-30, ~41s): jobs **test** (~21s, `pytest -q`) and **docker-build** (~15s) green. |

Commit under test: [`f597f8b`](https://github.com/ig0rayres/trading_lab/commit/f597f8b5bc8437615f68403eea067b20146d34c6) · default branch tree: [`main`](https://github.com/ig0rayres/trading_lab/tree/main)

Expected local command once deps are available:

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
UPSTREAM_DIR="$PWD/vendor/day-trader-skill" LIVE_TRADING_ENABLED=false PYTHONPATH=src \
  .venv/bin/python -m pytest -q --tb=line 2>&1 | tee docs/pytest-D1.log
```

Gate D1 pytest/docker: **closed** via CI run above. Re-run locally optional (`docs/pytest-D1.log`).

## Sprint D2 — CI evidence

| Run | Branch | Result |
|-----|--------|--------|
| [41043938920](https://github.com/ig0rayres/trading_lab/actions/runs/41043938920) | `sprint/D2` @ `d68a845` | **Success** (pytest + migration roundtrip + docker-build) |

Merged to `main` after verify (2026-10-30).

## Sprint D3 — Gate A (em progresso)

| Run | Branch | Result |
|-----|--------|--------|
| [41044496969](https://github.com/ig0rayres/trading_lab/actions/runs/41044496969) | `main` @ `146ba5a` | **Success** (D2 merge + Gate A persist) |
| [41044732897](https://github.com/ig0rayres/trading_lab/actions/runs/41044732897) | `sprint/D3` @ `1579f0d` | **Success** (session gate + rejection tests) |

Coverage (no Alpaca on path A): `tests/test_tradingview_webhook.py`, `tests/test_gate_a_signal.py` (ledger rows when `LEDGER_DATABASE_URL` set in CI).

## Sprint D1.3 (Git remote)

| Item | Value |
|------|--------|
| Remote | `https://github.com/ig0rayres/trading_lab.git` |
| Branch pushed | `sprint/D1`, `main` @ `f597f8b` |
| CI run (pytest + docker) | https://github.com/ig0rayres/trading_lab/actions/runs/41041762290 |
