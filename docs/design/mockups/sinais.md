# Mockup: Sinais (cockpit cópia de terceiros — IA v0.7 / ISS-024)

**Rota:** `/sinais`  
**API:** `GET /api/signals` · `POST /api/signals/providers` · refresh: `GET /api/signals/reload` (N53) · job critérios (N54+)  
**Autenticação:** sessão operador · **`LIVE_TRADING_ENABLED=false`** (selo na topbar N53)

## Arquitetura de informação (5 marcos)

Ordem vertical fixa — cada marco = `section` + `h2` + `id` (skip link opcional no shell):

| Ordem | `h2` | `id` |
|-------|------|------|
| 1 | Pré-aprovação | `sinais-preaprovacao` |
| 2 | Em operação / assinados | `sinais-operacao` |
| 3 | Inventário | `sinais-inventario` |
| 4 | Critérios de adoção | `sinais-criterios` |
| 5 | Auditoria de ingresso | `sinais-auditoria` |

**Sub-blocos (h3, não quebram a IA):** Collective2 e Candidatos Prodígio ficam **dentro ou imediatamente após** Operação/Inventário, com `ResearchBanner` onde for pesquisa.

## Layout (wireframe)

```text
+-----------------------------------------------------------------------------+
| [PanelShell topbar]  selo: Paper · Live desligado  (tokens N53, WCAG AA)    |
+-----------------------------------------------------------------------------+
| h1 Sinais                                                                   |
| Cópia de terceiros (TradingView / provedores). Decisão antes da fila.       |
+-----------------------------------------------------------------------------+
| ## 1. Pré-aprovação de provedores          [badge: Decisão]                 |
| Candidatos na fila. Aprovar libera roteamento paper — não é fill.           |
|                                                      [ Atualizar candidatos ]|
| Linha status refresh: idle | running | …  (ver tabela estados)                |
| Fonte última run: disco (N53) OU critérios-ao-vivo (N54) — texto honesto    |
| +-------------------------------------------------------------------------+ |
| | Plataforma | Nome (ID) | Métricas (pesquisa) | Status | Ações          | |
| | collective2| Easy Val. | Assert: 65,4% (pesq) | pending| [Aprovar][Rej.] | |
| +-------------------------------------------------------------------------+ |
| Callout se vazio: use Atualizar candidatos — sem prometer score inventado |
|                                                                               |
| ## 2. Em operação / assinados                                               |
| ResearchBanner: Cópia de terceiros … **Não é fill.**                          |
| Tabela: Origem · Sinal · fills · bruto (gross_unverified_costs)               |
|                                                                               |
| h3 Collective2 (cópia nomeada)     h3 Candidatos Prodígio (pesquisa)        |
| [approved ids / fechado]           [pool research_tip · não promove]         |
|                                                                               |
| Callout: Provedor aprovado ≠ linha de inventário (ver § distinção)          |
|                                                                               |
| ## 3. Inventário                                                            |
| Por sinal / evento — performance só com fill confirmado                     |
|                                                                               |
| ## 4. Critérios de adoção (somente leitura)                                 |
| copy.adoption.criteria_pt — Feature 4 / Prodígio 15d / C2 / LIVE off       |
|                                                                               |
| ## 5. Auditoria de ingresso (última)                                        |
| Sub: origem, destino e motivo. **Não é fill.**                               |
| Tabela Feature 9: hora, origem, destino, motivo                               |
+-----------------------------------------------------------------------------+
```

## Distinção: fila × aprovado × inventário

Use **badges + coluna de tipo** — nunca só cor.

| Entidade | Rótulo UI | Seção | Operador entende |
|----------|-----------|-------|------------------|
| Provedor na fila | `Candidato · decisão pendente` | 1 | Ainda não decidi Aprovar/Rejeitar |
| Provedor aprovado (ledger) | `Aprovado para paper` (paper badge) | 2 / bloco C2 | Posso copiar — **não** significa que já houve fill |
| Sinal no inventário | `Inventário · sinal <id curto>` | 3 | Rastro de um sinal com P&L quando fill existir |
| Candidato pool Prodígio | `Pesquisa — não autoriza ordem` | h3 sob 2 | Olhar ranking; aprovação vai para fila §1 |
| Evento webhook/journal | `Ingresso auditado` | 5 | O que chegou e para onde foi (fila/barrado/ordem) |

**Anti-confusão (copy fixa acima do inventário):**

> Aprovar um **provedor** não cria linha de **inventário** sozinho. Inventário enche quando há sinal rastreado com fill confirmado.

## Botão «Atualizar candidatos»

**Posição:** cabeçalho da seção **1 — Pré-aprovação** (alinha à direita do `h2`).  
**Variante:** `Button` outline (`--color-border`); **não** primário (primário = Aprovar).  
**Alvo:** mín. 44×44px · foco `3px solid var(--color-ring)`.

### Dois modos — comunicação honesta

| Modo | Backend | Hint permanente (texto `sm` muted) |
|------|---------|-------------------------------------|
| **Releitura disco** (N53 hoje) | `GET /api/signals/reload` | `Recarrega o bundle gravado no servidor. Não consulta Collective2 no browser. Critérios ao vivo: pendente N54.` |
| **Critérios ao vivo** (N54 / ISS-024) | `POST` job + cooldown | `Aplica critérios Feature 4 / Prodígio 15d no servidor (C2 server-side; TV = origens já ingeridas). Não aprova nem envia ordem.` |

**Linha de status** (sempre abaixo do botão, `aria-live="polite"`):

```text
Última atualização: — | Fonte: —
```

Após sucesso, preencher com hora + `disco` ou `critérios-ao-vivo`.

### Estados canônicos (refresh)

| ID | Estado | Aparência | Comportamento | Copy UI |
|----|--------|-----------|---------------|---------|
| S0 | **idle** | Outline + ícone ↻ | Clicável | `Atualizar candidatos` |
| S1 | **running** | Outline disabled + spinner | `aria-busy="true"`; bloqueia clique | `Atualizando candidatos…` |
| S2 | **success** | Volta S0 + toast success (3s) | Re-render fila §1; atualiza linha status | Toast: `Candidatos atualizados às HH:MM.` |
| S3 | **fail-closed** | S0 + `InlineAlert` danger | **Fila anterior intacta**; sem limpar tabela | `Não foi possível atualizar. A fila anterior foi mantida.` |
| S3a | *(sub)* sem migration 003 | danger inline | 503 pré-aprovação | `Pré-aprovação indisponível: migration do livro-razão ausente.` |
| S3b | *(sub)* C2/chave/job | danger inline | 503 fail-closed | `Atualização indisponível: serviço de pesquisa ou credencial ausente no servidor.` |
| S4 | **cooldown** (N54) | Outline disabled | Opcional 30s entre jobs | `Aguarde antes de atualizar de novo.` |
| S5 | **sem sessão** | botão oculto | 401 | redirect `/login` |

**Distinções coladas ao CTA (S0/S2):**

- Atualizar **≠** Aprovar  
- Atualizar **≠** ordem / fill  
- Métricas permanecem **(pesquisa)** após qualquer refresh  

## Métricas vit ais (seção 1)

Agrupar em `MetricCluster` por linha da fila (não 10 colunas soltas):

```text
Assertividade (pesquisa): 65,4%  |  Encolhida: indisponível
Fator de lucro (pesquisa): 1,82  |  Retorno líq.: indisponível
Drawdown máx. (pesquisa): -12,4% |  Score: indisponível
```

Ausente no JSON → **`indisponível`** (nunca `0` silencioso).

## Ações Aprovar / Rejeitar

| Controle | Estilo | Colocação | Acessibilidade |
|----------|--------|-----------|----------------|
| **Aprovar** | `primary` | Última coluna da tabela, ordem: Aprovar à esquerda de Rejeitar | `aria-label="Aprovar provedor {nome}"` |
| **Rejeitar** | outline `destructive` | ≥8px do Aprovar | Confirmação **não** modal bloqueante — opcional `aria-describedby` com hint rejeição vence semente |

**503 sem ledger:** ocultar botões; mostrar S3a na seção 1.

## Empty states (strings do mapa — não inventar)

| Seção | Texto |
|-------|-------|
| Pré-aprovação vazia | `Nenhum candidato na fila de pré-aprovação.` + hint: `Use Atualizar candidatos após novo JSON, job ou runbook — sem garantir elegibilidade.` |
| Em operação | `Nenhuma cópia de terceiro em operação.` |
| Performance nesta cópia | `Sem fills confirmados nesta cópia.` |
| Inventário | `Nenhum sinal neste inventário.` |
| Pool Prodígio | `Nenhum candidato de pesquisa no pool.` + badge pesquisa |
| C2 | `Collective2: cópia paper fechada — nenhum provedor na lista nomeada.` |
| Critérios indisponível | Mostrar bloco com texto estático Feature 4 se API falhar — ou `Critérios indisponíveis no bundle.` |
| Auditoria | `Nenhum sinal neste destino.` |

## Error states (página)

| Cenário | Tratamento |
|---------|------------|
| 401 | redirect login |
| Bundle vazio / ledger parcial | seções com empty honesto; sem tabela fake |
| Refresh fail-closed S3 | alert + manter dados anteriores |
| Aprovar/Rejeitar falha | toast danger por linha; não remover linha |

## Acessibilidade (WCAG 2.1 AA)

- Contraste tokens N53 (`DESIGN.md` §2.1); sem dependência só de cor nos badges.
- `th scope="col"` em todas as tabelas; cabeçalho sticky em §1 e §5 se lista longa.
- Região refresh: `role="status"` + `aria-live="polite"`.
- Skip link opcional no shell: «Ir para pré-aprovação» → `#sinais-preaprovacao`.

## Fluxo do operador (resumo)

1. **Atualizar candidatos** → servidor (disco hoje / critérios N54) → fila §1 atualiza → S2 ou S3.  
2. **Aprovar / Rejeitar** → `POST /api/signals/providers` → linha sai ou muda badge — **≠ fill**.  
3. Ler **operação** e **inventário** sem confundir com fila.  
4. **Critérios** como referência; **auditoria** por último para rastreio de ingresso.

## Handoff implementação

- **N53:** shell + 5 `h2` + GET reload + copy modo disco honesto.  
- **N54+:** wire mesmo CTA para job POST; cooldown S4; trocar hint para modo critérios-ao-vivo.  
- Paridade de strings com `docs/OPERATOR-PANEL-MAP.md` §2.