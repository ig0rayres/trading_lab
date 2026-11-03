# N16.8 — Homolog Command Panel remoto (operador)

> **Sprint N16** · **MVP-OP-1.0** gate · `LIVE_TRADING_ENABLED=false`  
> Complementa: `docs/COMMAND-PANEL.md`, `EASYPANEL.md`, `docs/HOMOLOGATION.md` item 6.

## Objetivo

Provar **HTTP remoto** com **Bearer** em `/api/status`, incluindo `command_panel.schema_version` = **`command-panel-v1`**, sem expor token no Git.

## Pré-requisitos

- Imagem pós **PR #14** (Command Panel) no **`trading-lab`** (rebuild se ainda pré-#14).
- `LEDGER_DATABASE_URL` no app que expõe o painel (mesmo DSN do ledger).
- **`/app/reports`** persistente (rank Prodígio, jsonl, evolution).

## Passo 1 — Env (EasyPanel → app `trading-lab` ou override aprovado)

| Variável | Valor |
|----------|--------|
| `LIVE_TRADING_ENABLED` | `false` |
| `DASHBOARD_ALLOW_REMOTE` | `true` |
| `DASHBOARD_BEARER_TOKEN` | string **≥ 32** caracteres (só painel; rotacionar se vazou) |
| `LEDGER_DATABASE_URL` | já configurado |

**Não** colar o token em chat, PR ou `TEST-EVIDENCE`.

## Passo 2 — Smoke sem HTTP (Exec container)

```bash
PYTHONPATH=/app/src python3 -c "
from v4_web_dashboard import build_snapshot
d = build_snapshot('/app/reports')
print('schema', d['command_panel']['schema_version'])
print('kill_switch', d.get('kill_switch_on'))
"
```

Esperado: `schema command-panel-v1`.

## Passo 3 — Subir dashboard (processo long-lived)

No **mesmo** container (não substituir CMD do scheduler no EasyPanel sem sprint ops):

```bash
/app/scripts/run.sh v4-dashboard --root /app/reports --host 0.0.0.0 --port 8765
```

Deixe rodando (terminal, `tmux`, ou job operador). **Dois apps** no EasyPanel — **não** criar terceiro serviço.

## Passo 4 — Publicar porta

No EasyPanel: mapear **8765** no domínio HTTPS do projeto (ou túnel SSH para teste). Rotas: `/`, `/api/status`, `/healthz`.

## Passo 5 — Teste remoto (sem curl no container)

Do **seu PC** (substitua URL; token só no header local):

```bash
curl -sS -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer SEU_TOKEN_AQUI" \
  "https://SEU-HOST/api/status"
```

Esperado: **`200`**.

Validar JSON (redigir na evidência):

- `command_panel.schema_version` = `command-panel-v1`
- `kill_switch_on` presente (boolean)
- `command_panel` contém seções read-only (estratégias, oportunidades se rank existir)

**Sem bearer** em remoto → **401** (comportamento esperado).

Loopback no container (opcional):

```bash
python3 << 'PY'
import os, urllib.request
req = urllib.request.Request("http://127.0.0.1:8765/api/status")
with urllib.request.urlopen(req, timeout=5) as r:
    print(r.status, r.read()[:200])
PY
```

(só funciona com dashboard rodando no passo 3)

## Passo 6 — Evidência

Preencher linha **N16.8** em `docs/TEST-EVIDENCE.md` (operador ou PR doc):

- Data UTC
- HTTPS sim/não
- Auth bearer exigida sim/não
- HTTP status `/api/status`
- `command-panel-v1` sim/não
- **Sem** token, URL com credenciais, ou DSN

## O que não conta

- Só smoke `build_snapshot` sem HTTP remoto (N16.8 exige bearer remoto).
- Painel sem PR #14 / schema antigo.
- Promover fase ou ordem pelo dashboard (read-only).

## Rollback

Parar processo `v4-dashboard`; remover exposição porta 8765; `DASHBOARD_ALLOW_REMOTE=false` se quiser desligar remoto.
