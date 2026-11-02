# MVP Demo Runbook — pacotão único (`MVP-DEMO-1.0`)

> **Git anchor:** `main` após merge N14 (pacotão) · **`LIVE_TRADING_ENABLED=false` sempre**  
> Objetivo: **uma** imagem, **dois** apps EasyPanel, **um** smoke, **uma** política de deploy — parar rebuilds por doc-only.

---

## 1. O que é “MVP demo” neste repo

| Modo | Comando / app | Ordem na corretora? |
|------|----------------|---------------------|
| **Pesquisa** | `trading-lab` → `v4-scheduler` | **Não** (`orders_sent=0`) |
| **Ingestão** | `trading-lab-webhook` → `tv-webhook` | **Não** (Gate A → fila) |
| **Fila + Gate B** | `trading-lab` → `tv-worker` | **Não** até auto flags (`queued_intent`) |
| **Demo paper (fill)** | `signal-paper` ou worker + flags | **Sim** — só operador **N12.4** |

Homologação D5 itens 3–7: `docs/HOMOLOGATION.md`.  
Fill Feature 5: mesma doc § **Feature 5 — demo paper `signal_copy`**.

---

## 2. Pendências que **não** o pacotão fecha sozinho

Registrado em `docs/ISSUES.md` § **Pendências operacionais (MVP)**:

1. **N12.4 submit** — `PAPER_SUBMITTED` + ordem Alpaca (evidência `TEST-EVIDENCE` § N12). **Fill limit** — pendente P-001b.  
2. **N12.5** — `REQUIREMENTS` Feature 5 fill `[x]` + linhas N12 em `TEST-EVIDENCE.md`.  
3. **ISS-005** — Fecha só após 1–2.  
4. **F-003** — `parity.py` / orb-parity congelado até ISS-005 fechado.

**Deploy #10/#11 no ar ≠ Feature 5 fechada.**

---

## 3. EasyPanel — perfil mínimo (uma vez)

Template de nomes: `config/mvp-demo.env.example` (valores só no painel).

| App | CMD | Env crítico |
|-----|-----|-------------|
| `trading-lab` | `v4-scheduler` *ou* `tv-worker` conforme operação | `LIVE_TRADING_ENABLED=false`, `LEDGER_DATABASE_URL`, Alpaca paper read |
| `trading-lab-webhook` | `tv-webhook` | `LEDGER_DATABASE_URL`, `TV_WEBHOOK_TOKEN`, `SIGNAL_COPY_SECRET` |

**Migrate:** `scripts/run.sh ledger-migrate apply` uma vez por DSN (N8 seed 7 estratégias).

**Mesma imagem** nos dois serviços; anotar SHA Git = `git rev-parse origin/main`.

---

## 4. Smoke pós-deploy (sem ordem)

```bash
# No container (/app)
bash scripts/mvp-demo-smoke.sh
```

Local (dev):

```bash
cd /path/to/trading-lab
LIVE_TRADING_ENABLED=false PYTHONPATH=src bash scripts/mvp-demo-smoke.sh
```

Esperado: `OK: MVP demo smoke finished (no paper order placed)`.

---

## 5. Política de deploy (aderência)

| Mudança no Git | EasyPanel rebuild? |
|----------------|-------------------|
| Só `docs/`, `tests/`, ROADMAP | **Não** (merge sim, deploy não) |
| `src/`, `Dockerfile`, deps, migrate | **Sim** — **um** bump + smoke §4 |
| Operador completou N12.4 | Atualizar evidência no Git; **deploy só** se código/env mudou |

Antes de cada rebuild operador visível: anotar SHA anterior → SHA novo + resultado smoke.

---

## 6. Próximo marco único

1. Merge pacotão N14 → **um** deploy `main`.  
2. Executar smoke §4.  
3. Sessão operador **N12.4** (fill) — **sem** novo PR até ISS-005 fechado ou `/pmo plan` explícito.

---

## 7. Referências

- `docs/REQUIREMENTS.md` Feature 5–6  
- `docs/TEST-EVIDENCE.md` § N12, N13  
- `docs/INFRASTRUCTURE.md` § EasyPanel  
- Skill projeto: `.cursor/skills/paper-order-gate/SKILL.md`
