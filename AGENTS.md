# Development agent directions

**Mandatory:** Read `ENGINEERING_RULES.md` before implementing anything. REUSE FIRST; do not reimplement upstream `day-trader-skill` logic. Original module APIs are loaded by `src/original.py`. Treat changes as hypotheses and build parity tests before merging. No broker connection or live-trading feature without a separate explicit authorization and comprehensive validation. Keep deployments consolidated and validate the entire release offline + against the actual upstream checkout. Document incompleteness; never present simulated metrics as actual performance.

## GIT FIRST — mandatory pre-development gate

Before proposing, changing, or implementing ANY feature (including news, earnings,
backtests, data collection, scoring, risk controls, and integration), the agent MUST:

1. Inspect the latest accessible `main` of `Jakeschincariol/day-trader-skill` and
   the project's local `/app/vendor/day-trader-skill` checkout. Record the
   exact commit SHA of each; do not assume the deployed checkout is current.
2. Search existing modules, source code, documentation, and tests for the
   capability. Inspect the actual implementation, not only the README.
3. Check present Trading Lab code and integrations for existing support.
4. Produce a brief **reuse inventory** before writing code, listing:
   capability; upstream path/function; reuse/adaptation/new work decision;
   rationale; compatibility/license/security limitations; tests required.
5. Reuse or adapt existing functionality first. New code is permitted only
   for a documented gap; never silently duplicate upstream logic.
6. Preserve read-only research mode and `NO_TRADE` by default. Never enable
   Alpaca Paper or live orders as part of an implementation.
7. Run regression and parity tests and report what was actually tested,
   including any source/version or access limitation.

If GitHub is unavailable, stop the claim of Git First verification, report
that limitation, and do not represent the code as checked against current main.
The latest main is not automatically safe: inspect changes, pin a reviewed
commit, and require tests before upgrading vendored code.
