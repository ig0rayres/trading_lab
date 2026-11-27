# Mockup: Prodígio

**Rota:** `/prodigy`  
**Autenticação:** sessão operador

## Layout

```text
+-----------------------------------------------------------------------------+
| h1 Prodígio                                                                 |
| Ranking e cópias de pesquisa. Não promove fase automaticamente.             |
+-----------------------------------------------------------------------------+
| ResearchBanner: Execute prodigy-rank (research) no runbook — não no browser.|
+-----------------------------------------------------------------------------+
| [A] RANKING / OPORTUNIDADES (tabela ordenável por colunas existentes)       |
| Provedor | campos presentes no JSON — sem score inventado                    |
+-----------------------------------------------------------------------------+
| [B] CÓPIAS REGISTRADAS                                                       |
| tabela prodigy_copied_signals / ledger conforme bundle                       |
+-----------------------------------------------------------------------------+
```

## Empty

| Bloco | Texto mapa |
|-------|------------|
| Rank | `Execute prodigy-rank (research)` |
| Cópias | `Nenhuma cópia registrada` |

## Visual

- Coluna numérica: tabular-nums; ranks sem gráfico de barras colorido (acessibilidade).
- Badge fixo em [A]: `Pesquisa — não autoriza ordem`.

## Sem CTA de ordem

Nenhum botão “Copiar sinal” ou “Operar” nesta rota no escopo ISS-023.