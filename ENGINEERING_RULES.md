# Engineering rule 1 — REUSE FIRST

1. Search the **already installed code** and trusted open-source libraries before proposing new implementation.
2. Audit license, API contract, maintenance, security exposure and existing tests.
3. Import, adapt, compose and test upstream functionality **rather than duplicating algorithms**.
4. Add explicit interface/parity tests; fail closed on incompatible upstream changes.
5. Build only truly missing orchestration and research functionality; document why it is new.
6. Pin upstream revisions for reproducible runs and preserve original license attribution.
7. Keep research and live execution separate. No broker, real orders or secrets in Trading Lab research image.

In particular, `trader-entry`, `trader-exit`, `trader-budget`, `trader-risk`, and `trader-scanner` must be integrated from `/app/vendor/day-trader-skill`, not rewritten in the Trading Lab.

# Research rule 2 — EVIDENCE BEFORE PROMOTION

- A repo with working trade tools is not a profitable trading strategy.
- Do not claim published research, a high in-sample PF, or Monte Carlo trajectories prove an edge.
- Reproduce exact third-party reference implementation before adapting it.
- Treat zero/very small observations as unassessed, not as winners.
- Keep an untouched holdout and capital-constrained portfolio checks as mandatory future gates.
- Preserve research-only image: never bundle live order execution or broker secrets.

# Engineering rule 3 — MANDATORY GIT FIRST CHECKLIST

Before implementation, compare (a) the current upstream `main` of
`Jakeschincariol/day-trader-skill`, (b) its pinned local vendor checkout,
(c) Trading Lab's own implementation. Inspect source and tests, record SHAs,
produce a reuse inventory and explain each gap requiring new code. Reuse
before writing; do not automatically upgrade from `main` without reviewing
license/security/API changes and running parity/regression tests. If current
GitHub access fails, state that the inspection is incomplete.
