# Mockup: Histórico (fills confirmados)

**Rota:** `/historico`  
**API:** `GET /api/history`  
**Autenticação:** sessão operador

## Layout

```text
+-----------------------------------------------------------------------------+
| h1 Histórico                                                                |
| Passado imutável — só fills confirmados.                                    |
+-----------------------------------------------------------------------------+
| Banner: queued_intent e fila **não** entram nesta tabela.                   |
+-----------------------------------------------------------------------------+
| TABELA order_history                                                        |
| ID cliente | Ativo | Lado | Resultado bruto (rotulado) | Estratégia       |
+-----------------------------------------------------------------------------+
| Rodapé (mapa): fila e HTTP 200 não entram como fill.                        |
+-----------------------------------------------------------------------------+
```

## Coluna resultado bruto

- Sempre com sufixo visual `bruto · custos não verificados` (alinhado a `PERFORMANCE_LABEL_GROSS` no código).
- Sem sparkline ou P&L agregado inventado nesta rota.

## Empty

`Nenhum fill confirmado no histórico.`

## Relação com Performance

Link ghost: “Ver totais em Performance” → `/performance` (não duplicar KPI gigante aqui).