# Mockup: Sinais (cockpit cópia de terceiros)

**Rota:** `/sinais`  
**API:** `GET /api/signals` · `POST /api/signals/providers`  
**Autenticação:** sessão operador

## Layout

```text
+-----------------------------------------------------------------------------+
| h1 Sinais                                                                   |
| Cópia de terceiros (TradingView / provedores). Decisão antes da fila.     |
|                                                      [ Atualizar candidatos ]|
+-----------------------------------------------------------------------------+
| [1] PRÉ-APROVAÇÃO DE PROVEDORES                              badge: decisão |
| Sub: Candidatos na fila. Aprovar libera roteamento paper — não é fill.      |
| Status refresh: (ver tabela de estados abaixo)                               |
| +-------------------------------------------------------------------------+ |
| | Plataforma | Nome (ID) | Métricas (pesquisa) | Status | Ações          | |
| |------------|-----------|---------------------|--------|----------------| |
| | collective2| Easy Val. | Assert: 65,4% (pesq)| pending| Aprovar Rejeitar| |
| |            | (132169)  | PF: 1,82 …          |        |                | |
| +-------------------------------------------------------------------------+ |
|                                                                               |
| [2] EM OPERAÇÃO / ASSINADOS                                                |
| Banner: Cópia de terceiros … **Não é fill.**                                 |
| Tabela origem · sinal · fills · bruto (gross_unverified_costs)               |
|                                                                               |
| [3] INVENTÁRIO · [4] COLLECTIVE2 · [5] POOL PRODÍGIO (research)              |
| [6] CRITÉRIOS ADOÇÃO (Feature 4/9/10)                                        |
| [7] AUDITORIA DE INGRESSO (última) — Não é fill.                             |
+-----------------------------------------------------------------------------+
```

## Botão «Atualizar candidatos» (ISS-023)

**Posição:** `PageHeader` à direita, alinhado ao título da página **ou** cabeçalho da seção [1] pré-aprovação (preferência: **cabeçalho da seção [1]** para contexto claro).

**Rótulo:** `Atualizar candidatos`  
**Tooltip / hint permanente (texto menor abaixo do botão):**  
`Recarrega JSON de pesquisa no servidor. Não aprova nem envia ordem.`

**Variante visual:** `Button` outline (`--color-border`); **não** usar cor primária (reservada a Aprovar).

### Estados do CTA

| ID | Estado | Aparência | Comportamento | Copy UI |
|----|--------|-----------|---------------|---------|
| R0 | **idle** | Outline, ícone ↻ | Clicável | `Atualizar candidatos` |
| R1 | **loading** | Outline disabled + spinner | `aria-busy=true`; ignora cliques | `Atualizando…` |
| R2 | **success** | Volta idle + toast success (3s) | Re-render tabela pré-aprovação com bundle novo | Toast: `Candidatos atualizados às HH:MM.` + `aria-live` |
| R3 | **error** | Idle + toast/InlineAlert danger | **Fail-closed:** fila anterior permanece | `Não foi possível atualizar. Tente de novo ou use o runbook.` |
| R4 | **cooldown** | Outline disabled | Opcional implementação: 30s entre cliques | `Aguarde antes de atualizar de novo.` |
| R5 | **sem sessão** | Oculto ou disabled | 401 se API chamada | N/A — redirect login |
| R6 | **job indisponível** | Outline + aviso inline | 503 migration/ledger | `Atualização indisponível: serviço de pesquisa ou migration ausente.` |

**Distinções obrigatórias (copy próxima ao botão em R0/R2):**

- Refresh **≠** Aprovar  
- Refresh **≠** ordem / fill  
- Dados ainda rotulados **(pesquisa)** após refresh  

**Implementação futura (nota para N53/N54):** `POST` ou `GET` dedicado server-side que reexecuta leitura de arquivos / job allowlisted — **sem** expor chaves C2/Alpaca no browser; não chamar `prodigy_rank.calculate` do painel (mapa).

## Seção [1] — Métricas vitais

Agrupamento em `MetricCluster` (não 10 colunas):

```text
Assertividade (pesquisa): 65,4%  |  Encolhida: indisponível
Fator de lucro (pesquisa): 1,82  |  Retorno líq.: indisponível
Drawdown máx. (pesquisa): -12,4% |  Score: indisponível
```

Ausente no JSON → **indisponível** (nunca `0` ou `N/D` silencioso sem rótulo pesquisa).

## Ações por linha

| Botão | Estilo | Nota |
|-------|--------|------|
| Aprovar | primary | Confirmação opcional leve (não modal bloqueante) |
| Rejeitar | outline destructive | Espaçamento ≥8px do Aprovar |

## Empty states (strings do mapa)

| Seção | Texto |
|-------|-------|
| Pré-aprovação vazia | Orientação: fila vazia honesta + hint “use Atualizar candidatos após novo JSON/runbook” **sem** prometer score |
| Em operação | `Nenhuma cópia de terceiro em operação.` |
| Inventário | `Nenhum sinal neste inventário.` |
| Pool Prodígio | `Nenhum candidato de pesquisa no pool.` + badge `Pesquisa — não autoriza ordem` |
| C2 | `Collective2: cópia paper fechada — nenhum provedor na lista nomeada.` |
| Auditoria | `Nenhum sinal neste destino.` |

## Ações do usuário

1. **Atualizar candidatos** → servidor recarrega fontes research → tabela [1] atualiza → toast R2 ou erro R3.  
2. **Aprovar** → `POST` providers approve → linha sai da fila / badge aprovado — **não** implica fill.  
3. **Rejeitar** → excluded mesmo na semente JSON/env (mapa).