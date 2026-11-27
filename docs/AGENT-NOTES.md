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

### 2026-11-19 — Sempre subir no closeout (N60)

**Source:** operator correction in chat after N60 PR #80 left open while panel still showed the old failure.

- Closing a build = **push front + open PR + CI green + `gh pr merge` into `main` in the same closeout**. Do not report «pronto» / «finalizei» / «pode Atualizar» while the PR is still `OPEN`.
- Do **not** ask the operator to merge trading-lab PRs — agent merges when CI is green (note 2026-11-11).
- Screenshot of the old panel while PR is open is evidence the agent failed this duty, not that the operator forgot to merge.
- EasyPanel rebuild remains operator-only (no deploy API in agent context); after merge, say only: rebuild `trading-lab` then Atualizar — never imply the panel already has the commit.

### 2026-11-25 — Push pelo agente em frente worktree (GFX.2b / F257)

**Source:** N61 closeout bloqueado no Shell do agente com chat ancorado em outro worktree (`n18-closeout`).

**Binding for all trading-lab `front/*` worktrees:**

1. **Git root:** every `git` / `gh` that touches a frente must use  
   `git -C /home/igor/cursor/trading-lab.fronts/<slug>`  
   (or read `front.worktree` from **that** frente’s `.cursorsession`).  
   `cd … && git push` no chat ancorado na mãe/outra frente falha: `PROJECT_ROOT` e `.cursorsession` errados → `patch_id` / `sprint_delivery` (F257).

2. **Sprint binding before stamp:** committed `sprint_atual` must equal the `--sprint` passed to `validation-stamp.py` and must match `checkpoint.sprint_delivery_sprint` after stamp (FW-526).  
   If the sprint mudou, commit **`chore: activate sprint NX`** (only `.cursorsession`) **before** stamp/QA — não gravar N61 no stamp com `sprint_atual` ainda N60.

3. **Stamp → push:** run `validation-stamp.py`, commit `.cursorsession` (**new commit**, avoid amend loops), then `git fetch origin main`, then push.  
   If push says `last_validated_sha` stale, re-stamp at current `HEAD` and commit session again (docs-only delta is OK).

4. **No hook bypass:** `BEESY_VALIDATION_OVERRIDE` is emergency-only with signed override; prefer (1)–(3).

**Proven path (N61):** `git -C …/sinais-raw-path push` after delivery bound to `sprint_atual` N60 + stamp sync commit; merge #81.

## 2026-11-17 N38 closeout — pendências operador

- Rebuild EasyPanel serviço `trading-lab` para ver faixa do freio (N38) + semáforo (N37).
- N29.5: credenciais demo só no EasyPanel (não no agente).
- N17.2 G-FORM: aguarda formulário/aprovação do operador.
- Colisão de ID: freio renumerado N37→N38/ISS-015 porque main tomou N37 para platform_health.
