# N33.0 Git First — closeout docs ISS-011 (Alpaca)

> Rock PLAN N33 · 2026-11-16 · frente `front/n27-alpaca-loop` · **no vendor bump** · **no `src/`**

## Pin verification (day-trader-skill)

| Source | SHA |
|--------|-----|
| `docs/VENDOR-PIN.md` / Docker `UPSTREAM_COMMIT` | `3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd` |
| Local `vendor/day-trader-skill` | **not a git checkout** on this worktree — treat pin above as the only SHA |
| GitHub `Jakeschincariol/day-trader-skill` `main` | **not re-checked** (fail-closed: do not claim current main) |

No vendor upgrade in N33. Do not copy upstream scoring. Do not invent Tá Barato / momentum / Prodígio thresholds. Do not enable live.

## Reuse inventory (briefs already on disk)

| Capability | Path / function | Decision | Rationale | Tests / evidence |
|------------|-----------------|----------|-----------|------------------|
| N30 Alpaca US+CRYPTO loop | `docs/.briefs/N30.brief.md`, `docs/.briefs/N30-GIT-FIRST-REUSE.md` | **Reuse / cite** | Feature 7 US/CRYPTO already `[x]` | `test_n30_us_equity_demo_on_paper_submitted`; PR **#35** `622fbeb` |
| N31 G-AJUSTE + TimesFM | `docs/.briefs/N31.brief.md`, `docs/.briefs/N31-GIT-FIRST-REUSE.md` | **Reuse / cite** | Method defined; ISS-012 body still stale | `tests/test_n31_g_ajuste_guardrails.py`; PR **#38** `681e8c5` |
| N28 Feature 11 apply/undo | ROADMAP N28 notes + `src/supervised_adjustment.py` (do not edit) | **Cite only** | Criteria 2–4 already `[x]` in REQUIREMENTS | `tests/test_n28_supervised_adjustment.py`; feat `71caca1`; stamp `c465724`; PR **#39** `5178fff` |
| N32 panel âncoras | `docs/.briefs/N32.brief.md`, `docs/.briefs/N32-GIT-FIRST-REUSE.md` | **Reuse / cite** | N32 already `concluida` | `test_n32_*`; PR **#42** merge `d30689bfeb4b009b6297d4bdea8fead233486474` |
| trader-entry/exit/budget/risk/scanner | `src/original.py` | **Do not touch** | MIT loader | `tests/test_vendor_verify.py` |
| Clear / OANDA | `src/demo_broker_adapters.py` | **Do not touch** | ISS-010 / N29.5 | existing gate tests |
| Tá Barato | vendor + sprint **N17** | **Defer** | G-FORM; N17.2 remains operador | `docs/TEST-EVIDENCE.md` Sprint N17 |

## Evidence to stamp (N33.1 — do not invent)

| Sprint | Index/Status today | Stamp `concluida`? | Cite |
|--------|--------------------|--------------------|------|
| N28 | index `planejada`; tasks `[x]` | **Yes** | `71caca1` `feat(sprint-N28)`; `c465724` stamp; PR **#39**; nodeids `test_n28_2_in_range_proposal_can_apply`, `test_n28_2_out_of_range_rejected`, `test_n28_3_apply_undo_persist_before_after_reason`, `test_n28_4_never_mutates_risk_anchors` |
| N30 | index `em closeout`; tasks `[x]` | **Yes** | `322318b` `feat(N30)`; PR **#35** `622fbeb`; TEST-EVIDENCE N30.1 / N30.3b nodeids |
| N31 | index `em execução`; tasks `[x]` | **Yes** | `d1d139a` `feat(sprint-N31)`; `84791eb` stamp; PR **#38** `681e8c5`; `N31GAjusteGuardrails.test_review_never_imports_paper_gateway`, `test_timesfm_missing_no_numeric_forecast_in_report` |
| N32 | already `concluida` | **Leave** | PR **#42** **MERGED** `d30689b` at `2026-11-16T19:49:34Z`; tip `9367cdd` |
| N17 | `planejada`; N17.2 `[ ]` | **No** | Optional one-liner: N17.2 remains operador / G-FORM |

## Gap (this sprint only)

| Gap | New code? | Notes |
|-----|-----------|-------|
| ROADMAP Status vs delivered code | **Docs** | Stamp N28/N30/N31 `concluida` with citations |
| ISS-011 body still says PR #42 pendente | **Docs** | Keep **aberto** for B3/FOREX (ISS-010) + N17.2 / G-FORM |
| ISS-012 index fechado / body aberto | **Docs** | Sync body to fechado |
| REQUIREMENTS changelog line 414 | **Docs** | Stale “critérios 2–4 `[ ]` até N28.2–4” while lines 283–286 are `[x]` |
| TEST-EVIDENCE EasyPanel #42 | **Docs one-liner** | Operator-attested 2026-11-16; **not** a fill |
| Clear / OANDA / scoring / LIVE | **No** | Forbidden |

## Security / invariants

- `LIVE_TRADING_ENABLED=false`.
- B3_EQUITY / FOREX stay `NO_DEMO_ACCOUNT_PATH` (zero Alpaca POST).
- HTTP 200 / `PAPER_GATEWAY_QUEUE_ONLY` / `OK_RESEARCH_ONLY` are not fills.
- EasyPanel “no ar” is operator attestation, not a broker fill.

## Deferred (out of N33)

- **N17.2** — operator shadow→paper; G-FORM blocked upstream.
- **N29.5 / ISS-010** — Clear B3 + OANDA Practice.
- **N17 task table** — do not rewrite checkboxes.
- Vendor pin bump.
- Any `src/` change.
