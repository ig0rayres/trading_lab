# N34.0 Git First — wire Clear/OANDA adapters into the paper signal loop

> Rock PLAN N34 rewrite · 2026-11-16 · frente `front/n27-alpaca-loop` · **no vendor bump** · **CI/mock HTTP only**

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| Local `vendor/day-trader-skill` | **empty / absent** on this worktree — not a git checkout; treat pin above as the only SHA |
| GitHub `Jakeschincariol/day-trader-skill` `main` | **not re-checked** (fail-closed: do not claim current main) |

No vendor upgrade in N34. Do not copy upstream scoring. Do not invent Tá Barato / momentum / Prodígio thresholds. Do not enable live. Do not call real Clear/OANDA HTTP from CI.

## Honesty gap (why the prior N34 plan was false)

| Claim in prior N34 | Fact on disk |
|--------------------|--------------|
| Adapter code path ready; only operator attestation left | `build_demo_adapter` has **no production callers**. Callers are `tests/test_demo_broker_adapters.py` only. |
| Gate already selects Clear/OANDA in the paper loop | `demo_account_gate.named_demo_account_configured` already calls `credentials_block_for_adapter` for B3/FOREX. `paper_gateway_queue.process_after_gate_b` already calls `demo_market_block_reason`. The **runner still short-circuits**. |
| B3/FOREX blocked only when env missing | `signal_paper_runner._market_blocks_alpaca_paper` returns `NO_DEMO_ACCOUNT_PATH` for every `B3_EQUITY`/`FOREX` signal, even when `DEMO_ACCOUNT_PATH_*` + `CLEAR_*` / `OANDA_PRACTICE_*` are set. |
| N29.6 must unlock N27.2 after N29.5 | N27.2 is still `[ ]`. Wiring can proceed **fail-closed without live credentials**. N29.5 remains operator homolog. |

## Reuse inventory (MUST)

| Capability | Path / function | Decision | Rationale | Tests / evidence |
|------------|-----------------|----------|-----------|------------------|
| Clear simulated + OANDA Practice HTTP | `src/demo_broker_adapters.py` `build_demo_adapter`, `_ClearSimulatedAdapter`, `_OandaPracticeAdapter`, `credentials_block_for_adapter`, `adapter_path_for_market` | **Call — do not reimplement HTTP** | N29.1–N29.4 `[x]`; mock REST already exists | `tests/test_demo_broker_adapters.py` `test_clear_simulated_mock_http_exposes_position_open_order_and_fill_status`, `test_oanda_practice_uses_practice_host_only_order_and_fill`, `test_clear_simulated_without_credentials_blocks_no_demo_account_path`, `test_oanda_practice_empty_token_blocks_with_reason`, `test_regression_b3_forex_adapter_http_never_posts_alpaca_paper` |
| Named path + credential gate | `src/demo_account_gate.py` `demo_market_block_reason`, `named_demo_account_configured` | **Call from runner** (same as CRYPTO) | Gate already fail-closed; runner ignores it for B3/FOREX | `test_named_path_env_selects_g_mkt_adapter_per_market`; gateway `test_n27_gateway_b3_equity_blocked_no_alpaca_post` (no-cred) |
| Paper signal loop | `src/signal_paper_runner.py` `_market_blocks_alpaca_paper`, `run`, `submit` | **Adapt** — stop always-block; dispatch adapter; keep Alpaca CRYPTO/US happy path | This is N27.2 core | Today: `test_n32_b3_equity_auto_blocked_no_alpaca_post`, `test_n32_forex_auto_blocked_no_alpaca_post` always expect block even without env. N34.2 must keep no-cred block **and** add mock submit when path+creds present. |
| Queue thin gate | `src/paper_gateway_queue.py` `process_after_gate_b` → `demo_market_block_reason` then `paper_run` | **Reuse** — no second HTTP client; runner change is enough once auto path calls `run` | With creds, queue already would call `paper_run`; runner currently still blocks | `tests/test_paper_gateway_queue.py` |
| trader-entry/exit/budget/risk/scanner | `src/original.py` | **Do not touch** | MIT loader | `tests/test_vendor_verify.py` |
| Tá Barato | vendor + sprint **N17** | **Defer** | G-FORM; N17.2 remains operador | `docs/TEST-EVIDENCE.md` Sprint N17 |
| Alpaca CRYPTO/US | `signal_paper_runner.submit` + `PAPER_URL` | **Keep** | Out of scope except not to break | `test_n32_tight_defaults_qty1_aapl_paper_submitted`, N30 CRYPTO tests |

## Evidence already merged (adapters only — not the loop)

| Item | Cite | Wired into `run()`? |
|------|------|---------------------|
| Adapter feat | `27c1dd9294c0cc2f9f53ce0954e356358aa81ca2` | **No** |
| PR **#32** MERGED | `88aae40e549647165c51f52276fce9bbcd09be3f` (`2026-11-13T10:05:16Z`) | **No** — mock HTTP in pytest of adapters |
| N29.1–N29.4 | ROADMAP `[x]` | Code of adapters + gate names; **not** N27.2 |
| N29.5 / N29.6 | still `[ ]` | Operator attestation / docs unlock — **out of N34 live HTTP** |
| N27.2 | still `[ ]` | **This sprint delivers the wiring** (fail-closed, mock-tested) |

## Gap (this sprint)

| Gap | New code? | Notes |
|-----|-----------|-------|
| Runner always returns `NO_DEMO_ACCOUNT_PATH` for B3/FOREX | **Yes** — `signal_paper_runner.py` | Use `demo_market_block_reason`; then `build_demo_adapter` |
| `build_demo_adapter` unused in production | **Yes** — call it from `run` | Do not copy `_http_json` |
| Tests only cover always-block | **Yes** — urlopen mock | submit/position/fill-or-block; prove zero Alpaca POST |
| ISS-010/011 still readable as “adapters not started” or “code ready, only attestation” | **Docs** | Honest: adapters existed in mock; **now** loop-wired fail-closed; live homolog still N29.5 |
| N27.2 still `[ ]` | **ROADMAP after tests** | Check N27.2 when N34.2 nodeids exist; do **not** stamp N29 `concluida` |
| Live Clear/OANDA HTTP / LIVE / scoring | **No** | Forbidden |

## Security / invariants

- `LIVE_TRADING_ENABLED=false`.
- Credentials are **operator-owned**; names only in Git; values only in EasyPanel.
- Until N29.5, CI uses mock `urlopen` only. Filling EasyPanel **alone did not** place B3/FOREX orders **before this wiring**.
- Missing path or credential → `NO_DEMO_ACCOUNT_PATH` with reason; B3/FOREX never POST `paper-api.alpaca.markets`.
- HTTP 200 / `PAPER_GATEWAY_QUEUE_ONLY` / `OK_RESEARCH_ONLY` / pytest mock are not fills.

## Deferred (out of N34)

- **N29.5** — operator opens/credentials Clear simulated + OANDA Practice in EasyPanel (live homolog).
- **N29.6** — docs unlock after N29.5; do not mark N29 `concluida`.
- **N17.2** — Tá Barato shadow→paper; G-FORM; do not invent thresholds.
- Vendor pin bump.
- Real Clear/OANDA HTTP in CI.
