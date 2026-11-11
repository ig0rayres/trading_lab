# Agent notes — Trading Lab

## Operator corrections (binding)

### 2026-11-11 — Agent may merge GitHub PRs

**Source:** operator instruction in chat (N20 / MVP-FINAL).

The agent working on **trading-lab** (`ig0rayres/trading_lab`) is **authorized and responsible** for merging pull requests into `main` when:

1. The PR is for this product (trading-lab), not another project.
2. CI checks on the PR are green (`test`, `docker-build` / `docker-smoke` as applicable).
3. The change was produced on a `front/*` branch with a reviewable PR (no direct push to `main`).
4. Live trading remains off (`LIVE_TRADING_ENABLED=false`); merge does not by itself authorize EasyPanel rebuild or paper/live orders.

**Duty:** after CI green, the agent merges with a normal merge commit (`gh pr merge --merge`), resolves conflicts on the front if needed, and reports the merge URL. Do not wait for a second human click on Merge when these conditions hold.

**Still operator-only:** EasyPanel rebuild/deploy, pasting secrets, naming demo broker accounts (G-MKT), and paper fill evidence from the broker UI.

**Out of scope:** hellopaco / GEARNOC / other repos. This note applies only to trading-lab.
