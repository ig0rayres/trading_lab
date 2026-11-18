# Mockup: Estratégias (catálogo)

**Rota:** `/estrategias`  
**API:** `GET /api/estrategias`  
**Autenticação:** sessão operador

## Layout

```text
+-----------------------------------------------------------------------------+
| h1 Estratégias                                                              |
| Catálogo de fases — somente leitura neste menu.                               |
+-----------------------------------------------------------------------------+
| TABELA strategy_catalog                                                     |
| Chave | Fase | Paper permitido (sim/não)                                    |
+-----------------------------------------------------------------------------+
| Rodapé fixo: Promoção de fase: somente operador (fora deste menu).          |
+-----------------------------------------------------------------------------+
```

## Badges de fase

| Fase | Badge |
|------|-------|
| research | muted / cinza |
| shadow | warning |
| paper / paper_limited | success-outline |

## Empty

Tabela inteira substituída por: `Catálogo indisponível (ledger)` (string do mapa).

## Proibido no visual

- Botão “Promover fase” ou PATCH exposto  
- Qualquer CTA que sugira ordem automática