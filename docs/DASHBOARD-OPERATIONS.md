# Dashboard operacional — política e deploy

> **Command Panel v1** · read-only · `LIVE_TRADING_ENABLED=false` sempre  
> Detalhe técnico em inglês: [`V4_DASHBOARD_SECURITY.md`](../V4_DASHBOARD_SECURITY.md), [`docs/COMMAND-PANEL.md`](COMMAND-PANEL.md)

## O que é o “dashboard operacional”

| Superfície | URL | Uso |
|------------|-----|-----|
| **Painel HTML** | `GET /` | Visão do operador: saúde, catálogo, Prodígio, melhoria contínua, limitações |
| **API JSON** | `GET /api/status` | Integrações, scripts, monitoramento (`command_panel`, kill switch, shadow vs paper) |
| **Liveness** | `GET /healthz` | Probe (mesmas regras de auth que as outras rotas) |

Não envia ordens. Não promove fase de estratégia. POST → **405**.

---

## Sempre ligado (sem `nohup` manual)

A partir desta entrega, a imagem padrão do app **`trading-lab`** usa:

```text
CMD → v4-ops → v4-scheduler (foreground) + v4-dashboard (supervisor com restart)
```

| Variável | Default | Efeito |
|----------|---------|--------|
| `DASHBOARD_AUTOSTART` | `true` | `false` desliga só o HTTP; scheduler continua |
| `DASHBOARD_HOST` | vazio → `0.0.0.0` se `DASHBOARD_ALLOW_REMOTE=true`, senão `127.0.0.1` | Bind do painel |
| `DASHBOARD_PORT` | `8765` | Porta interna |
| `DASHBOARD_ROOT` | `/app/reports` | Raiz de snapshots/jsonl |

Se o processo HTTP cair, **`v4-ops` reinicia em ~3s** (supervisor em shell).

**Webhook** (`trading-lab-webhook`) continua com CMD próprio (`tv-webhook`); **não** sobe dashboard.

Após **rebuild + redeploy** do `trading-lab`, mapear porta **8765** no EasyPanel (HTTPS na frente).

---

## Política de acesso e segurança

### Fail-closed

| Regra | Comportamento |
|-------|----------------|
| Live | `LIVE_TRADING_ENABLED` ≠ `false` → container recusa subir |
| Bind remoto | `--host` ≠ loopback exige `DASHBOARD_ALLOW_REMOTE=true` **e** `DASHBOARD_BEARER_TOKEN` **≥ 32** caracteres |
| Token definido | **Todas** as rotas GET (`/`, `/api/status`, `/healthz`) exigem `Authorization: Bearer <token>` — **inclusive** de dentro do container |
| Sem token no env | Loopback pode acessar sem Bearer; **não** publique porta assim |

### Camadas recomendadas (produção demo)

1. **HTTPS** no EasyPanel / reverse proxy (Bearer **não** substitui TLS).
2. **`DASHBOARD_BEARER_TOKEN`** só no painel de env (nunca Git/chat).
3. Opcional: segundo fator no proxy (IP allowlist, Basic no edge) — fora do código Python.

### O que o painel **não** garante

- Fila / `queued_intent` **≠** fill.
- PnL **bruto** (sem taxas completas).
- `operational_acceptance` só fica true com fills + snapshots fechados homologados (Feature 5 parcial).
- Rank Prodígio / evolution = **research tips**, não ordem automática.

---

## Abrir o HTML no browser (com Bearer)

O servidor **não** tem tela de login. Com token ativo:

- **Postman / Insomnia / curl** com header Bearer → `/api/status` ou `/`.
- **Browser:** extensão que injeta `Authorization`, ou proxy que adiciona o header, ou túnel + ferramenta que você já usou na homolog N16.8.

Sem Bearer → **401** (esperado).

---

## Checklist operador (hashia / `trading-lab`)

- [ ] `LIVE_TRADING_ENABLED=false`
- [ ] `LEDGER_DATABASE_URL` no main
- [ ] `DASHBOARD_ALLOW_REMOTE=true` + token ≥ 32
- [ ] Volume `/app/reports` persistente
- [ ] Rebuild imagem + redeploy (CMD `v4-ops` na imagem)
- [ ] Porta **8765** publicada com HTTPS
- [ ] `curl -H "Authorization: Bearer …" https://…/api/status` → **200**, `command-panel-v1`
- [ ] (Opcional) `prodigy-rank` para popular oportunidades

Rollback dashboard: `DASHBOARD_AUTOSTART=false` + redeploy (scheduler-only) ou CMD explícito `v4-scheduler …` no EasyPanel.
