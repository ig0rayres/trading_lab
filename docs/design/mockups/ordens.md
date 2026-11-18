# Mockup: Ordens abertas (paper)

**Rota:** `/ordens`  
**API:** `GET /api/orders`  
**Autenticação:** sessão operador

## Layout

```text
+-----------------------------------------------------------------------------+
| h1 Ordens abertas                                                           |
| O que está no paper agora. Fila e HTTP 200 não são fill.                    |
+-----------------------------------------------------------------------------+
| ResearchBanner leve: Sem envio de ordem por esta tela.                      |
+-----------------------------------------------------------------------------+
| TABELA open_orders (sticky header)                                          |
| ID cliente | Ativo | Lado | Status | Corretora | Qtd rest. | Estratégia    |
+-----------------------------------------------------------------------------+
| Rodapé legal: snapshots + ledger; sem poll Alpaca HTTP pelo painel.         |
+-----------------------------------------------------------------------------+
```

## Badges de status

| Status | Badge |
|--------|-------|
| new / accepted / pending | warning-bg |
| partial | warning-bg |
| canceled / rejected | danger-bg textual |
| filled (se aparecer em abertas) | success-bg |

## Empty

`Nenhuma ordem aberta no paper.` — `EmptyState` central, sem tabela fantasma.

## Densidade

Modo compacto `--text-sm`; IDs em monospace; lado Buy/Sell com rótulo PT + cor secundária.