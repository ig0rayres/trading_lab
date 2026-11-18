# Mockup: Shell do painel (menu do dia a dia)

**Rota:** todas após `GET /login`  
**Tipo:** layout persistente (`panel_ops_html`)  
**Autenticação:** cookie `trading_lab_session` / `DASHBOARD_OPERATOR_SESSION`

## Layout

```text
+--------------------------------------------------------------------------------+
| TOPBAR (altura 48px, fundo --color-surface, borda inferior)                    |
| [●] Paper · Live desligado          Última leitura: — (bundle)    Sair          |
+--------+-----------------------------------------------------------------------+
| SIDEBAR| PAGE HEADER                                                         |
| 240px  | h1 + subtítulo + [slot ações — ex. Refresh em /sinais]              |
|        +---------------------------------------------------------------------+
| Central| [ResearchBanner opcional — faixa tracejada research]                  |
| Ordens | +-------------------------------------------------------------------+
| Histórico | CARD / SECTION primary                                              |
| Sinais | | conteúdo da rota                                                  |
| Estrat.  | +-------------------------------------------------------------------+
| Prodígio | SECTION secondary (auditoria, critérios, rodapé legal)              |
| Perf.    |                                                                       |
| Análise  |                                                                       |
| G.       |                                                                       |
|        |                                                                       |
| v2.0   |                                                                       |
+--------+-----------------------------------------------------------------------+
```

## Sidebar

| Elemento | Comportamento |
|----------|----------------|
| Logo / marca | Texto “Trading Lab” + badge `Ops` |
| Itens | Ordem do `DESIGN.md` §4.2; ícone 20px + rótulo |
| Ativo | `--color-sidebar-active-bg` + borda esquerda 3px `--color-primary` |
| Rodapé | Versão design `ISS-023` (comentário HTML) — não confundir com deploy |

## Topbar

| Elemento | Dados |
|----------|-------|
| Selo ambiente | Sempre: `Paper · Live desligado` (não ocultar após N52) |
| Sair | Link `GET /logout` ou equivalente existente — ghost button |
| Sem Bearer | Não mostrar token |

## Componentes

| Componente | Tipo | Interação |
|------------|------|-----------|
| NavItem | link | `aria-current="page"` no ativo |
| PageHeader | header | Um `h1`; ações alinhadas à direita |
| ResearchBanner | aside | Leitura só; sem botão de ordem |

## Responsivo

| Breakpoint | Mudança |
|------------|---------|
| ≥1024px | Sidebar fixa 240px |
| &lt;1024px | Sidebar colapsa em drawer; hamburger na topbar; foco trap no drawer |

## Estados globais

| Estado | Comportamento |
|--------|---------------|
| Não autenticado | Redireciona `/login` — shell não renderiza |
| 401 API | InlineAlert na página: sessão expirada + link login |