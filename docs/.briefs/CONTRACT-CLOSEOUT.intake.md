# Intake — Contract closeout epic (2026-11-15)

> Source: operator `/pmo plan` 2026-11-15 23:18 — "validate everything missing from the contract, plan the sprints, deliver everything; only non-homologated third-party platforms (e.g. Clear B3) may stay out".
> Base: `origin/main` `376434e` (PR #33). Front: `front/contract-closeout`.
> Upstream: `Jakeschincariol/day-trader-skill` main = pin `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` (checked via `git ls-remote` 2026-11-15; no drift).

## Operator-accepted exclusions

| Item | Why out |
|------|---------|
| B3 via Clear Smart Trader (N29.5, N27.2 B3) | Third-party API not credentialed/homologated |
| Forex via OANDA Practice (N29.5, N27.2 FOREX) | Third-party account not credentialed/homologated |
| ORB / mean_reversion in paper | Contract forbids (REQUIREMENTS §4 Feature 1 rules, Feature 4, §7). They stay shadow and must keep running in shadow |
| LIVE | Contract §7 |
| Collective2 paper-copy approval | Contract Feature 4 / §7 (`approved_for_paper_copy` false) |

## Contract audit (REQUIREMENTS v0.4)

| Feature | Contract state | Code state | Gap |
|---------|----------------|------------|-----|
| 1–6 | `[x]` with evidence | merged | none |
| 7 Autonomous demo | 5 × `[ ]` | worker in `v4-ops` (N23), gates, demo flag, Alpaca CRYPTO gate (N27) | (a) `V4_RISK_SNAPSHOT_FILE` must be ≤120 s fresh (`signal_paper_runner.risk_check`) and nothing refreshes it in `v4-ops` → autonomous loop stalls; (b) only `signal_copy` produces queue signals — no autonomous producer for prodigy/momentum/ta_barato/news_first; (c) no-fill timeout cancel not proven; (d) N27.5 live key ⇒ host stays paper, N27.6 restart no duplicate not tested; (e) crypto signal path: `signal_copy.validate` accepts only `asset_class == 'us_equity'` |
| 8 Central | 5 × `[ ]` | N24 login + Central + PATCH triggers merged | criteria not verified/marked; `demo_operation_on` has no Central toggle (operator had to use SQL on 2026-11-15) |
| 9 Signals + Prodígio | 3 × `[ ]` | N25 merged | criteria not verified/marked |
| 10 Performance | 3 × `[ ]` | N26 merged | criteria not verified/marked |
| 11 Supervised tuning (Should) | 4 × `[ ]` | N28 not started | G-AJUSTE method open (REQUIREMENTS §9 #8) |

## Strategy families (Feature 4)

| Family | Default phase | Rule source | Gap |
|--------|---------------|-------------|-----|
| signal_copy | paper_limited | `src/signal_copy.py` | operational; crypto asset class missing |
| prodigy_15d | research | `src/prodigy_rank.py` (score already in repo) + `src/c2_signal_feed.py` (read-only C2 active orders) | no autonomous rank → signed signal producer; C2 feed needs key (env) |
| momentum | research | upstream `trader-scanner/scan.py` `find_setups`: `breakout_20d`, `bull_flag`, `reclaim_ma20`; entry/exit/budget via `src/original.py` | not wired (N17 never started). Mapping family ↔ upstream setup is an assumption for operator review |
| ta_barato | research | upstream `find_setups`: `oversold` (RSI14 Wilder < 30), `oversold_bounce` | same as momentum. Contract says "not 'caiu, compra'" — operator must confirm mapping before paper promotion |
| news_first | research | `src/news_first_sim.py`, `src/event_verifier.py`, upstream `trader-news` | candidates always `NO_TRADE`; needs price confirmation via upstream entry before becoming a signal |
| orb / mean_reversion | shadow | `src/multistrategy.py`, `shadow_journal.py` | must keep running in shadow; never paper |

Promotion rule (contract Feature 4): a phase never rises automatically. Code delivers producers end-to-end; phase moves to `paper_limited` only by the operator in the Central (existing `PATCH /api/strategies/{key}`).

## Operator pending list (no blocking)

1. Confirm mapping momentum ↔ `breakout_20d|bull_flag|reclaim_ma20` and ta_barato ↔ `oversold|oversold_bounce`, then promote phases in the Central.
2. G-AJUSTE method (what counts as error, frequency, undo).
3. EasyPanel rebuild after merge (agent cannot deploy).
4. C2 API key in env for Prodígio live feed (if not already set).
5. N20.2 image SHA for both services.
