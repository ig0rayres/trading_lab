# N35.0 Git First — env-presence smoke + homolog checklist (no live fill)

> Rock PLAN N35 · 2026-11-16 · frente `front/n27-alpaca-loop` · **no vendor bump** · **no real Clear/OANDA HTTP**

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| Local `vendor/day-trader-skill` | **empty / absent** on this worktree — not a git checkout; treat pin above as the only SHA |
| GitHub `Jakeschincariol/day-trader-skill` `main` | **not re-checked** (fail-closed: do not claim current main) |

No vendor upgrade. Do not copy upstream scoring. Do not invent Tá Barato / momentum / Prodígio thresholds. Do not enable live. Do not call real Clear/OANDA HTTP from CI.

## Why N35 is not fake (post-N34, post-#46)

| Already on disk | Still missing | N35 does |
|-----------------|---------------|----------|
| N34 wired `build_demo_adapter` into `signal_paper_runner.run()` fail-closed (PR **#45**); N27.2 `[x]` with `test_n34_*` | Per-**key** present/absent map (operator can only see market-level `block_reason` or a boolean `credentials_block_for_adapter`) | Add `env_presence_report`: names + `present`/`absent` + market `READY`/`NO_DEMO_ACCOUNT_PATH`; never values; never HTTP |
| `EASYPANEL.md` G-MKT names-only table | How to confirm a **demo order** without pasting secrets (HOMOLOGATION is Alpaca-centric) | Operator checklist in HOMOLOGATION + pointer from EASYPANEL |
| EasyPanel **#46 no ar** (`d99b332`, operator 2026-11-16) | Operator did **not** say «creds ok»; CLEAR_*/OANDA_* not attested | Do **not** check N29.5; do **not** stamp N29 `concluida` |
| N34 mock tests already cover missing/present creds with fake HTTP | `.env.example` still has no empty CLEAR_*/OANDA_*/DEMO_ACCOUNT_PATH_* names (N34 optional, not done) | Empty names only (F-004); never values |
| Dashboard `load_trigger_snapshot` already attaches `block_reason` | That is market-level, not which named key is missing | Report lists each known key present/absent |

**Not N35:** live homolog, inventing secrets, real broker HTTP in CI, closing ISS-010, checking N29.5, treating #46 or pytest mock as a fill.

## Reuse inventory (MUST)

| Capability | Path / function | Decision | Rationale | Tests / evidence |
|------------|-----------------|----------|-----------|------------------|
| Named path + credential gate | `src/demo_account_gate.py` `named_demo_account_configured`, `demo_market_block_reason`, `NO_DEMO_ACCOUNT_PATH` | **Call / extend** — add `env_presence_report` in this module | Market READY vs blocked already exists; per-key map does not | `tests/test_demo_broker_adapters.py` `test_clear_simulated_without_credentials_blocks_no_demo_account_path`, `test_named_path_env_selects_g_mkt_adapter_per_market` |
| Credential names | `src/demo_broker_adapters.py` `credentials_block_for_adapter` (CLEAR_SIM_* / OANDA_PRACTICE_*) | **Call — do not reimplement HTTP or adapters** | Key names already canonical | same file `test_oanda_practice_empty_token_blocks_with_reason` |
| Path constants | `G_MKT_ADAPTER_PATH_CLEAR_SIMULATED`, `G_MKT_ADAPTER_PATH_OANDA_PRACTICE`, `DEMO_ACCOUNT_PATH_ENV_BY_MARKET` | **Reuse literals** | Pin already fail-closed in N34 | `test_n34_*` in `tests/test_signal_paper_runner.py` |
| Paper loop / adapters HTTP | `signal_paper_runner.run`, `build_demo_adapter` | **Do not touch** | N34 already wired; N35 is presence + docs | N34 closeout PR **#45** |
| Dashboard block_reason | `src/v4_web_dashboard.py` `load_trigger_snapshot` | **Do not add a second UI** | Checklist may point at existing `block_reason`; presence report is a names-only helper | panel trigger tests |
| trader-entry/exit/budget/risk/scanner | `src/original.py` | **Do not touch** | MIT loader | `tests/test_vendor_verify.py` |
| Tá Barato | vendor + **N17.2** | **Defer** | G-FORM; do not invent thresholds | `docs/TEST-EVIDENCE.md` Sprint N17 |

## Security / invariants

- `LIVE_TRADING_ENABLED=false`.
- Credentials are **operator-owned**; names only in Git; values only in EasyPanel.
- Presence report and tests **must not** print, log, or embed secret values (assert fixture secrets absent from `repr`/`json`).
- No `urlopen` / real Clear/OANDA in N35 code or CI.
- `#46 no ar` ≠ creds filled ≠ fill. HTTP 200 / queue / mock / panel-on-air are not fills.
- N29.5 stays `[ ]` until operator attests in chat «creds ok» **and** demo order evidence without secrets.
- N29.6 stays `[ ]`; N27.2 already `[x]` from N34 — do **not** stamp N29 `concluida` until N29.5.
- ISS-010 / ISS-011 stay **aberto**. Feature 7 B3/FOREX boxes stay `[ ]`.

## Deferred (out of N35)

- **N29.5** — operator pastes Clear simulated + OANDA Practice values in EasyPanel and homologates live.
- **N29 `concluida`** — only after N29.5.
- **N17.2** — Tá Barato shadow→paper; G-FORM.
- Vendor pin bump. Live trading. New adapter methods (stop/target bracket).
