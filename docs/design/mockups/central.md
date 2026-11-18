# Mockup: Central

**Rota:** `/` (`/central` alias se existir)  
**Autenticação:** sessão operador

## Layout

```text
+-----------------------------------------------------------------------------+
| h1 Central                                                                  |
| Freio, saúde da plataforma e visão rápida.                                  |
+-----------------------------------------------------------------------------+
| [A] FREIO / KILL SWITCH                                    card destaque    |
|     Estado atual · [ Ativar freio ] / [ Liberar ] (destructive isolado)     |
+-----------------------------------------------------------------------------+
| [B] SEMÁFORO PLATAFORMA        | [C] SAÚDE (platform_health)               |
| texto + ícone (não só cor)     | lista chaves legíveis                      |
| vazio: Aguardando primeira…    |                                             |
+-----------------------------------------------------------------------------+
| [D] MERCADOS / ÂNCORAS (tabela)                                              |
+-----------------------------------------------------------------------------+
| [E] SINAIS RECENTES (trecho)     vazio: Sem sinais recentes                 |
| link secundário → /sinais                                                    |
+-----------------------------------------------------------------------------+
```

## Componentes

| Bloco | Dados (mapa) | Visual |
|-------|--------------|--------|
| Freio | `control_flags` / APIs painel | Botão destrutivo único, confirmação dupla |
| Semáforo | health check v4-ops | Badge success/warning + label PT |
| Mercados | âncoras bundle | Tabela compacta |
| Sinais recentes | subset sinais | Máx. 5 linhas + “Ver todos” |

## Estados

| Estado | UI |
|--------|-----|
| Semáforo vazio | Copy exata: `Aguardando primeira checagem automática (v4-ops)` |
| Sem sinais | `Sem sinais recentes` |

## Acessibilidade

- Kill switch: `aria-describedby` com aviso de impacto paper (não live).