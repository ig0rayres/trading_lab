# Mockup: Análise Google (TimesFM / pesquisa)

**Rota:** `/analise-google`  
**API:** `GET /api/analise-google`  
**Autenticação:** sessão operador

## Layout

```text
+-----------------------------------------------------------------------------+
| h1 Análise Google                                                           |
| Dica de pesquisa — não autoriza ordem. Live desligado.                      |
+-----------------------------------------------------------------------------+
| ResearchBanner tracejada (obrigatória):                                     |
| Dica de pesquisa — não autoriza ordem.                                      |
+-----------------------------------------------------------------------------+
| [COM DADO] Tabela de dicas                                                  |
| colunas conforme relatório timesfm — cada linha badge `dica de pesquisa`    |
+-----------------------------------------------------------------------------+
| Rodapé: Esta análise é só pesquisa. Não autoriza ordem.                     |
+-----------------------------------------------------------------------------+
```

## Vazio / indisponível

| Caso | UI |
|------|-----|
| Modelo ausente | `Análise Google indisponível: modelo ou dependência ausente.` + linha `Motivo: …` |
| Relatório sem linhas | `Nenhuma dica de pesquisa neste relatório.` |

## Componentes

| Elemento | Regra |
|----------|-------|
| Tabela | Sem botão “Aplicar” ou “Enviar ordem” |
| JSON `execution_authorized` | Nunca mostrar como true no UI |

## Links

Opcional ghost: “Ver critérios em Sinais” → `/sinais` (adoção), sem cruzar para ordens.