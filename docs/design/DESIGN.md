# Design System — Trading Lab

> Fase 2 (Design) | Modo: RETROFIT (redesign) | Engine: Beesy nativo | Biblioteca: Tailwind puro | Dark mode: Sim, troca manual

Operador aprovou a direção 1 (sóbrio, menu escuro, conteúdo claro) em 2026-11-03, com ícone mais texto nos estados e tema claro e escuro. Protótipos em `docs/design/canvas/` (login, central, sinais). Números daquelas telas são exemplo.

---

## 1. Identidade Visual

**Estilo**: operacional, sóbrio
**Tom**: Uma pessoa olha o painel por sessão longa. A tela mostra se a conta demo pode abrir ordem, o que barrou um sinal e onde estão as âncoras. Sem gráfico de candle e sem cara de campanha.
**Público-alvo**: Operador único, semi-técnico. Densidade de mesa, leitura em português.

### Referencias visuais

| Referencia | O que inspirou | Link |
|-----------|---------------|------|
| Direção 1, sóbrio | Menu escuro, seis âncoras, faixa de operação, parada geral | `docs/design/moodboards/moodboard-sobrio.jpg` |
| Direção 3, neutro | Estado com ícone e texto, não só cor | `docs/design/moodboards/moodboard-neutro.jpg` |

---

## 2. Design Tokens

Extraídos dos protótipos aprovados. Contraste texto/fundo conferido em 2026-11-03: os pares abaixo passam 4.5:1.

### 2.1 Cores

#### Light mode

| Token | Valor | Uso |
|-------|-------|-----|
| `--color-background` | `#f3f5f8` | Fundo da página |
| `--color-foreground` | `#1c2430` | Texto |
| `--color-primary` / `-foreground` | `#2c4a6e` / `#f7fafc` | Item ativo, botão Entrar |
| `--color-muted` / `-foreground` | `#e7edf3` / `#5c6b7c` | Faixas, texto auxiliar |
| `--color-destructive` | `#8f2d2d` | Parada geral, erro |
| `--color-success` | `#1d6b45` | Operando, abaixo do limite |
| `--color-warning` | `#8a5a12` | Parada ligada, atenção |
| `--color-border` | `#d5dee8` | Bordas |
| `--color-card` / `-foreground` | `#ffffff` / `#1c2430` | Cartões |
| `--color-sidebar` / `-foreground` | `#1a2332` / `#e8eef6` | Menu |

#### Dark mode

| Token | Valor Light | Valor Dark |
|-------|------------|------------|
| `--color-background` | `#f3f5f8` | `#121820` |
| `--color-foreground` | `#1c2430` | `#e7eef6` |
| `--color-card` | `#ffffff` | `#1b2531` |
| `--color-primary` | `#2c4a6e` | `#9ec0e6` |
| `--color-primary-foreground` | `#f7fafc` | `#121820` |
| `--color-muted` | `#e7edf3` | `#243041` |
| `--color-muted-foreground` | `#5c6b7c` | `#b7c3d1` |
| `--color-border` | `#d5dee8` | `#314255` |
| `--color-destructive` | `#8f2d2d` | `#f0b4b4` |
| `--color-success` | `#1d6b45` | `#8dccb0` |
| `--color-warning` | `#8a5a12` | `#e6c48a` |
| `--color-sidebar` | `#1a2332` | `#0e141c` |

Troca pela classe `dark` no `html`. A preferência fica em `localStorage` (`trading-lab-theme`).

### 2.2 Tipografia

| Propriedade | Valor |
|-------------|-------|
| **Font family** | IBM Plex Sans |
| **Números, hora, ativo** | IBM Plex Mono |
| **Font fallback** | sans-serif / monospace |
| **Base size** | 16px |

### 2.3 Espacamento

Escala Tailwind. Cartão com padding 16px. Alvo de toque mínimo 44px.

### 2.4 Border Radius

| Contexto | Token | Valor |
|----------|-------|-------|
| Botões e inputs | `--radius-lg` | `0.5rem` |
| Cartões | `--radius-lg` | `0.5rem` |
| Monograma | `--radius-lg` | `0.5rem` |

### 2.5 Shadows

| Contexto | Token |
|----------|-------|
| Menu mobile | `shadow-xl` |
| Cartões | borda, sem sombra forte |

---

## 3. Biblioteca de Componentes

**Escolha**: Tailwind puro
**Justificativa**: O painel de hoje é HTML gerado em Python, sem React. O protótipo não puxa biblioteca de componentes. A implementação futura reaproveita estes tokens.

### Componentes utilizados

| Componente | Uso no projeto | Customizacao necessaria |
|-----------|---------------|----------------------|
| Button | Entrar, Parada geral, filtros, tema | Primary, outline destructive, ghost |
| Input | Login | Label visível, erro com ícone e texto |
| Card | Âncoras | Número em mono, texto auxiliar com ícone |
| Table | Sinais | Linha clicável, filtro por destino |
| Status | Operando, parada, barrado, fila | Ícone mais texto |

**Componentes custom**: faixa de parada geral com confirmação na própria página, sem alerta do navegador.

---

## 4. Layout e Navegacao

### Estrutura geral

```
+------------------+----------------------------------+
| TL  Trading Lab  | Título          Conta demo  Tema |
| Central          | Banner: protótipo / exemplo      |
| Estratégias      | Conteúdo                         |
| Sinais           |                                  |
| Prodígio         |                                  |
| Performance      |                                  |
| Sugestões        |                                  |
+------------------+----------------------------------+
```

Menu com 240px. No celular, o menu abre por botão.

### Navegacao

| Plataforma | Tipo | Detalhes |
|-----------|------|---------|
| Web desktop | sidebar | Seis áreas dos requisitos. Central e Sinais existem no protótipo. |
| Web mobile | menu sobreposto | Mesmos destinos |

### Responsividade

| Breakpoint | Mudancas |
|-----------|---------|
| Mobile (< 1024px) | Menu some e abre por botão. Cartões empilham. |
| Desktop (>= 1024px) | Menu fixo e cartões em grade. |

---

## 5. Mockups

### Entrar

**Rota**: `/login`
**Tipo**: pagina
**Autenticacao**: publica

#### Layout

```
+----------------------------------+
|                         [Tema]   |
|            TL                    |
|        Trading Lab               |
|   Central de controle. Conta demo|
|   [e-mail]                       |
|   [senha]                        |
|   [Entrar]                       |
+----------------------------------+
```

#### Componentes

| Componente | Tipo | Dados | Interacao |
|-----------|------|-------|-----------|
| Tema | Button | Claro ou escuro | Alterna e grava a preferência |
| E-mail | Input | Placeholder | Sem envio real |
| Senha | Input | Vazio ou preenchida | Vazio bloqueia e mostra erro |
| Entrar | Link primary | — | Com senha, segue para a Central |

#### Estados

| Estado | Comportamento |
|--------|--------------|
| Error | Senha vazia: ícone mais "Informe a senha do protótipo." |
| Success | Qualquer senha não vazia abre a Central |

#### Acoes do usuario

1. Alternar tema → as duas cores da seção 2.1.
2. Entrar sem senha → permanece na tela com erro.
3. Entrar com senha → Central.

### Central

**Rota**: `/`
**Tipo**: pagina
**Autenticacao**: autenticada

#### Layout

```
+--------+------------------------------------------+
| Central| Central          Conta demo        Tema  |
|        | Capital  Risco/op  Posições  ...         |
|        | [ícone] Operando          [Parada geral] |
|        | Sinais recentes                          |
+--------+------------------------------------------+
```

#### Componentes

| Componente | Tipo | Dados | Interacao |
|-----------|------|-------|-----------|
| Âncoras | Card | Capital, risco por operação, posições, risco aberto, perda do dia, perda da semana | Leitura neste corte |
| Status | Status | Operando ou parada ligada | Ícone mais texto |
| Parada geral | Button destructive | — | Abre confirmação na página |
| Sinais recentes | Table | Origem, ativo, destino, motivo | Link para Sinais |

#### Estados

| Estado | Comportamento |
|--------|--------------|
| Success | Operando, com a frase de que a conta demo pode abrir ordem nova |
| Warning | Depois de confirmar a parada: "Parada geral ligada" e o botão desabilitado |

#### Acoes do usuario

1. Parada geral → confirmação → estado de parada. O protótipo não envia comando.
2. Ver todos os sinais → tela Sinais.

### Sinais

**Rota**: `/sinais`
**Tipo**: pagina
**Autenticacao**: autenticada

#### Layout

```
+--------+------------------------------------------+
| Sinais | Sinais            Conta demo        Tema |
|        | [Todos] [Ordem] [Barrado] [Fila]         |
|        | Tabela                                   |
|        | Detalhe: gate, âncora, "não é um fill"   |
+--------+------------------------------------------+
```

#### Componentes

| Componente | Tipo | Dados | Interacao |
|-----------|------|-------|-----------|
| Filtros | Button | Todos, Ordem, Barrado, Fila | Esconde as outras linhas |
| Tabela | DataTable | Hora, origem, ativo, destino, motivo | Clique abre o detalhe |
| Detalhe | Painel | Gate e âncora | Fechar |

#### Estados

| Estado | Comportamento |
|--------|--------------|
| Empty | Filtro sem linha: ícone mais "Nenhum sinal neste destino." e "Limpar filtro" |
| Success | Linhas de exemplo com destinos distintos |

#### Acoes do usuario

1. Filtrar → a tabela muda.
2. Clicar a linha → leitura do gate. O texto diz que não é um fill.

---

## 5b. Canvas Prototypes

| Tela | Canvas File | Status | Exportado para Figma |
|------|-------------|--------|----------------------|
| Entrar | `docs/design/canvas/login.html` | Aprovado em conversa, 2026-11-03 | Nao |
| Central | `docs/design/canvas/central.html` | Aprovado em conversa, 2026-11-03 | Nao |
| Sinais | `docs/design/canvas/sinais.html` | Aprovado em conversa, 2026-11-03 | Nao |

**Engine**: HTML no repositório
**Boost**: Nivel 1 (Tailwind puro)
**Export**: N/A

Telas ainda sem protótipo: Estratégias, Prodígio, Performance, Sugestões, edição das âncoras. Ficam para o corte em que a operação na conta demo existir.

---

## 6. Acessibilidade

| Requisito | Implementacao |
|-----------|--------------|
| Contraste WCAG AA | Pares da seção 2.1 medidos em 2026-11-03, todos >= 4.5:1 |
| Touch targets | Minimo 44px nos botões e inputs do protótipo |
| Focus visible | Anel no foco por teclado |
| Keyboard nav | Botões e links reais, sem div clicável |
| Screen reader | `aria-label` no tema e no menu; erro de senha em `role="alert"` |
| Reduced motion | Menu mobile usa transição curta; respeitar `prefers-reduced-motion` na implementação |
| Color not sole | Operando, parada, barrado e fila levam ícone e texto |

---

## 7. Decisoes de Design (ADRs)

### ADR-D001: Redesign sóbrio com dois temas
- **Contexto**: O painel atual é uma página escura só de leitura. Os requisitos pedem navegação e ações.
- **Decisao**: Direção 1, com ícone mais texto vindo da direção 3. Tema claro e escuro, troca manual.
- **Alternativas**: Formalizar o visual antigo. Ficar só no escuro.
- **Consequencias**: A implementação nova não copia o CSS inline de `src/v4_web_dashboard.py`.

### ADR-D002: Três telas neste corte
- **Contexto**: O operador pediu para seguir a operação, não desenhar o painel inteiro.
- **Decisao**: Entrar, Central e Sinais. O resto do menu fica visível e sem destino.
- **Alternativas**: Prototipar as seis áreas antes de qualquer ordem.
- **Consequencias**: Estratégias, Prodígio, Performance e Sugestões não têm layout aprovado.

---

## CSS de Implementacao (copiar para o projeto)

```css
@import "tailwindcss";

@theme {
  --color-background: #f3f5f8;
  --color-foreground: #1c2430;
  --color-primary: #2c4a6e;
  --color-primary-foreground: #f7fafc;
  --color-muted: #e7edf3;
  --color-muted-foreground: #5c6b7c;
  --color-destructive: #8f2d2d;
  --color-success: #1d6b45;
  --color-warning: #8a5a12;
  --color-border: #d5dee8;
  --color-card: #ffffff;
  --color-card-foreground: #1c2430;
  --color-sidebar: #1a2332;
  --color-sidebar-foreground: #e8eef6;
  --radius-lg: 0.5rem;
  --font-sans: "IBM Plex Sans", sans-serif;
  --font-mono: "IBM Plex Mono", monospace;
}
```

O tema escuro troca os valores da tabela da seção 2.1 pela classe `dark`. Não há segundo nome de token.

## Implementacao pendente

Não aplicar este CSS no painel em produção neste passo. A operação na conta demo vem antes do resto das telas. Quando houver sprint de interface, os arquivos candidatos são o gerador HTML em `src/v4_web_dashboard.py` e a folha que substituir o CSS inline. Preservar rotas, autenticação e os campos já lidos pelo painel.
