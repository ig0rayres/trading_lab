# Mockup: Performance (paper)

**Rota:** `/performance`  
**API:** `GET /api/performance`  
**Autenticação:** sessão operador

## Layout

```text
+-----------------------------------------------------------------------------+
| h1 Performance                                                              |
| Totais paper — somente fills confirmados.                                   |
+-----------------------------------------------------------------------------+
| [KPI único] Total bruto                                                     |
| valor ou Indisponível (string mapa)                                         |
| legenda: custos não verificados — não apresentar como lucro líquido         |
+-----------------------------------------------------------------------------+
| TABELA linhas por operação / snapshot                                       |
+-----------------------------------------------------------------------------+
| Sem gráfico de equity inventado se não houver série no bundle.              |
+-----------------------------------------------------------------------------+
```

## Empty / indisponível

| Caso | Copy |
|------|------|
| Total ausente | `Indisponível` |
| Sem linhas | `Sem fills confirmados` |

## Proibido

- Sharpe, win rate agregado ou metas se não existirem em `panel_ops_data`  
- Comparativo “vs ontem” sem dado histórico real