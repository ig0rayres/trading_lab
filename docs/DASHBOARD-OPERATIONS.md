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
CMD → v4-ops → v4-scheduler (foreground) + v4-dashboard (supervisor com restart) + tv-worker --once (intervalo curto)
```

Serviços EasyPanel permanecem **somente** `trading-lab` e `trading-lab-webhook` — não há terceiro app para o worker (ADR-009).

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

## Dia a dia do operador (sem Exec)

| Ação | Onde |
|------|------|
| Entrar | `GET /login` → senha não vazia (protótipo) → cookie `trading_lab_session` (= `DASHBOARD_OPERATOR_SESSION` no env) |
| Ver âncoras, mercados, parada | `GET /` (Central) após login |
| Ligar parada geral | Botão na Central → `PATCH /api/triggers` (cookie obrigatório) |
| Ver sinais com motivo | `GET /sinais` ou `GET /api/signals` |
| Ver ranking Prodígio | `GET /prodigy` |
| Ver performance só de fill | `GET /performance` ou `GET /api/performance` |
| Monitoramento JSON | `GET /api/status` com Bearer (como antes) |

Rotina **não** exige shell no Exec do EasyPanel para parar, ajustar âncora ou ler sinais — só o painel HTTPS. Exec permanece para migrate, segredos e rebuild (operação rara).

Bearer sozinho **não** autoriza escrita (`PATCH` → **401**); cookie de operador obrigatório.

---

## Abrir o HTML no browser

1. **Com login operacional:** abra `https://…/login`, informe senha (qualquer valor não vazio no protótipo), navegue Central / Sinais / Prodígio / Performance.
2. **API/monitoramento:** `curl -H "Authorization: Bearer …" https://…/api/status` (token ≥ 32 se remoto).
3. Sem Bearer nem cookie → **401** ou redirecionamento para `/login` nas rotas operacionais.

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
