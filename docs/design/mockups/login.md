# Mockup: Login operador

**Rota:** `/login`  
**Tipo:** página isolada (sem sidebar)  
**Autenticação:** pública → cookie após sucesso

## Layout

```text
+------------------------------------------+
|           fundo --color-canvas            |
|    +--------------------------------+    |
|    | CARD central (--radius-lg)     |    |
|    | Trading Lab — Painel operador    |    |
|    | Paper · Live desligado (badge)   |    |
|    |                                  |    |
|    | Senha do operador [__________]   |    |
|    | (protótipo: qualquer não vazio)  |    |
|    |                                  |    |
|    | [ Entrar ]  primary full-width   |    |
|    |                                  |    |
|    | Rodapé: pesquisa não autoriza    |    |
|    | ordem no painel.                 |    |
|    +--------------------------------+    |
+------------------------------------------+
```

## Componentes

| Componente | Dados | Interação |
|------------|-------|-----------|
| Badge ambiente | Texto fixo Live desligado | Somente leitura |
| Campo senha | `type=password`, `autocomplete=current-password` | Label visível |
| Botão Entrar | primary | Submit → `POST` conforme implementação atual |

## Estados

| Estado | UI |
|--------|-----|
| Vazio | Botão desabilitado ou erro “Informe a senha.” |
| Erro auth | InlineAlert destructive — sem revelar detalhes de servidor |
| Sucesso | Redirect `/` (Central) |

## Acessibilidade

- `label for` explícito; erro ligado com `aria-describedby`.
- Foco inicial no campo senha; Enter submete.