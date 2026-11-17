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

Antes de achar que uma área “sumiu” do painel, leia o [**mapa de onde está cada coisa**](OPERATOR-PANEL-MAP.md) (N40 mapa · **N41** Ordens/Histórico · **N42** Estratégias): o login diário mostra **Central / Sinais / Estratégias / Ordens / Histórico / Prodígio / Performance**. Tá Barato e melhoria contínua ainda ficam na **Command Panel v1** (página única) ou só em **`GET /api/status`**. O painel **não** envia nem cancela ordem (POST continua **405**); a tela **Estratégias** não promove fase.

| Ação | Onde |
|------|------|
| Entrar | `GET /login` → senha não vazia (protótipo) → cookie `trading_lab_session` (= `DASHBOARD_OPERATOR_SESSION` no env) |
| Ver âncoras, mercados, freio | `GET /` (Central) após login |
| Ativar freio | Com o freio liberado, só aparece **Ativar freio** na faixa da Central → `PATCH /api/triggers` com `kill_switch_on: true` (cookie obrigatório). |
| Liberar freio | Com o freio ativo, só aparece **Liberar freio** na faixa → `PATCH /api/triggers` com `kill_switch_on: false` (cookie obrigatório). Liberar o freio não liga a operação demo (`demo_operation_on` permanece separado). |
| Ver sinais com motivo | `GET /sinais` ou `GET /api/signals` |
| Ver catálogo de fases (somente leitura) | `GET /estrategias` ou `GET /api/estrategias` |
| Ver ranking Prodígio | `GET /prodigy` |
| Ver performance só de fill | `GET /performance` ou `GET /api/performance` |
| Ver ordens paper ainda abertas (lista) | `GET /ordens` ou `GET /api/orders` |
| Ver histórico só de fill confirmado | `GET /historico` ou `GET /api/history` |
| Monitoramento JSON | `GET /api/status` com Bearer (como antes) |

Rotina **não** exige shell no Exec do EasyPanel para parar, ajustar âncora ou ler sinais — só o painel HTTPS. Exec permanece para migrate, segredos e rebuild (operação rara).

Bearer sozinho **não** autoriza escrita (`PATCH` → **401**); cookie de operador obrigatório.

---

## Abrir o HTML no browser

1. **Com login operacional:** abra `https://…/login`, informe senha (qualquer valor não vazio no protótipo), navegue Central / Sinais / Estratégias / Ordens / Histórico / Prodígio / Performance.
2. **API/monitoramento:** `curl -H "Authorization: Bearer …" https://…/api/status` (token ≥ 32 se remoto).
3. Sem Bearer nem cookie → **401** ou redirecionamento para `/login` nas rotas operacionais.

---

## Rotina diária (sem Exec)

| Passo | Onde |
|-------|------|
| Saúde da stack | Painel HTML: seção **Plataforma — semáforo** ou `GET /api/status` → `platform_health` |
| Gatilhos | Central / `GET /api/triggers` (sessão operador) |
| Incidente | EasyPanel só se semáforo vermelho persistente |

Probes automáticos: `v4-ops` com `PLATFORM_HEALTH_AUTOSTART=true` (default); worker com `TV_WORKER_AUTOSTART=true`.

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
