# Contrato HTTP — rota Sinais (painel operador)

> Complemento de `docs/api-spec.yaml` · ISS-024 / N53–N54 · 2026-11-18  
> Implementação N54 ainda pendente para `POST /api/signals/candidates/refresh`.

## Autenticação

Todas as rotas abaixo exigem sessão de operador (`trading_lab_session`). Bearer sozinho **não** autoriza (padrão do painel).

## Endpoints

| Método | Caminho | Modo | Ordem? | Fill? |
|--------|---------|------|--------|-------|
| GET | `/api/signals` | leitura bundle | Não | Não |
| GET | `/api/signals/reload` | `disk_reread` (N53) | Não | Não |
| POST | `/api/signals/candidates/refresh` | `live_criteria` (N54) | Não | Não |
| POST | `/api/signals/providers` | decisão pré-aprovação | Não | Não |

## Persistência

- **Decisões:** tabela `signal_provider_approvals` (migration 003) — `platform`, `provider_id`, `status`, `source`, `decided_at`.
- **Plataformas válidas no POST:** `collective2`, `prodigy`, `tradingview`.
- **Refresh/job:** não cria tabela nova; regrava JSON de pesquisa em `REPORTS_DIR` e re-monta bundle.

## Campo `mode` (refresh)

| Valor | Significado |
|-------|-------------|
| `disk_reread` | Só `build_panel_bundle` — critérios ao vivo **não** executados |
| `live_criteria` | Job N54 aplicou critérios Feature 4 / Prodígio 15d server-side (C2 + TV mínimo) |

## Corpo `GET /api/signals`

- `signals[]` — auditoria Feature 9 (origem, destino, motivo).
- `copy` — objeto com pelo menos: `preapproval`, `operating`, `history`, `inventory`, `adoption`, `collective2`, `prodigy_pool`, `research_copies`.

## POST `/api/signals/providers`

Request: `{ "platform", "provider_id", "action": "approve" | "reject" }`.

Response 200 inclui `execution_authorized: false`, `orders_sent: 0`.

## Cooldown N54

Resposta **429** com `reject_code: REFRESH_COOLDOWN` e opcional `retry_after_seconds` — evita job concorrente (R4 no design).