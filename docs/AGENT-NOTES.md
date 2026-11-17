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

### 2026-11-17 — «Finalizado» só depois do merge em `main`

**Source:** operator correction in chat (N51 / EasyPanel deploy).

- **Never** tell the operator a sprint/feature is **finalizado** / pronto para deploy while the PR is still open on `front/*`.
- Closeout language («finalizado», «no ar no código», «pode rebuild») requires **`MERGED` into `main`** (`gh pr view` → `state=MERGED`) first.
- After CI green, **merge immediately** — do not stop at «PR aberto / CI verde» and wait for the operator to ask «sobe pra main».
- EasyPanel rebuild still operator-only, but the agent must leave `main` ready before saying the delivery is done.

## 2026-11-17 N38 closeout — pendências operador

- Rebuild EasyPanel serviço `trading-lab` para ver faixa do freio (N38) + semáforo (N37).
- N29.5: credenciais demo só no EasyPanel (não no agente).
- N17.2 G-FORM: aguarda formulário/aprovação do operador.
- Colisão de ID: freio renumerado N37→N38/ISS-015 porque main tomou N37 para platform_health.
