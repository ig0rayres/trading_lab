"""HTML shells for operational panel (login, central, signals, prodigy, performance)."""
from __future__ import annotations

import html
import json
from typing import Any

try:
    from .panel_ops_data import PERFORMANCE_LABEL_GROSS
except ImportError:
    from panel_ops_data import PERFORMANCE_LABEL_GROSS

OPERATOR_PANEL_PATHS = frozenset({
    '/', '/central', '/sinais', '/estrategias', '/analise-google', '/prodigy', '/performance',
    '/ordens', '/historico', '/login',
})

_TIP_LABEL_PT = {
    'research_tip': 'dica de pesquisa',
    'suggestion': 'sugestão',
}

_N43_UNAVAILABLE_MAIN = 'Análise Google indisponível: modelo ou dependência ausente.'
_N43_SUBTITLE = 'Dica de pesquisa — não autoriza ordem. Live desligado.'
_N43_FOOTER = 'Esta análise é só pesquisa. Não autoriza ordem.'
_N43_EMPTY_TIPS = 'Nenhuma dica de pesquisa neste relatório.'

_N48_COPY_SECTION = 'Cópia de terceiros'
_N48_AUDIT_SECTION = 'Auditoria de ingresso'
_N50_OPERATING_SECTION = 'Em operação / assinados'
_N50_C2_SECTION = 'Collective2'
_N50_C2_EMPTY = 'Collective2: cópia paper fechada — nenhum provedor na lista nomeada.'
_N50_C2_ALLOWLIST = 'Collective2: cópia paper só para os provedores nomeados.'
_N50_C2_SUBTITLE = 'Marketplace Collective2 — lista nomeada; elegível no ranking não é aprovação.'
_N50_C2_SNAPSHOT_LABEL = 'Instantâneo de ordens ativas no disco — não é ticket. execution_authorized: false.'
_N48_COPY_EMPTY = 'Nenhuma cópia de terceiro em operação.'
_N48_COPY_PERF_EMPTY = 'Sem fills confirmados nesta cópia.'
_N48_COLLECTIVE2 = 'Collective2: cópia fechada — nenhum provedor aprovado.'
_N48_AUDIT_EMPTY = 'Nenhum sinal neste destino.'
_N48_AUDIT_SUBTITLE = 'Auditoria de ingresso — origem, destino e motivo. Não é fill.'
_N48_COPY_SUBTITLE = 'Cópia de terceiros (TradingView / provedores). Não é fill.'
_N48_FOOTER = (
    'O painel não envia ordem. Live desligado. Valores brutos se o custo não estiver completo.'
)
_N48_RESEARCH_NOTE = 'Cópias de pesquisa (Prodígio) — não são operação.'
_N49_INVENTORY_SECTION = 'Inventário de sinais'
_N49_ADOPTION_SECTION = 'Critérios de adoção'
_N49_POOL_SECTION = 'Candidatos ao pool (Prodígio)'
_N50_POOL_SECTION = 'Candidatos Prodígio (pesquisa)'
_N49_INVENTORY_EMPTY = 'Nenhum sinal neste inventário.'
_N49_POOL_EMPTY = 'Nenhum candidato de pesquisa no pool.'
_N49_POOL_SUBTITLE = 'Pesquisa — não autoriza ordem / não promove.'
_N51_PREAPPROVAL_SECTION = 'Pré-aprovação de provedores'
_N51_PREAPPROVAL_SUBTITLE = (
    'Pesquisa — não autoriza ordem. Aprovar não é fill. Métricas rotuladas pesquisa.'
)
_N51_PREAPPROVAL_EMPTY = (
    'Nenhum provedor aguardando análise no momento. Novos candidatos aparecerão aqui.'
)
_N48_COPY_EMPTY_HINT = 'Aprove um provedor acima para iniciar.'
_PREAPPROVAL_METRIC_LABELS: dict[str, str] = {
    'win_rate_pct': 'Percentual de acertos (pesquisa)',
    'shrunk_win_rate_pct': 'Acertos encolhidos % (pesquisa)',
    'profit_factor_reported': 'Fator de lucro (pesquisa)',
    'reported_pnl_sum': 'Resultado reportado (pesquisa)',
    'net_return_pct': 'Retorno líquido % (pesquisa)',
    'max_drawdown_pct': 'Drawdown máximo % (pesquisa)',
    'prodigy_score': 'Score Prodígio (pesquisa)',
    'score': 'Score (pesquisa)',
    'status': 'Status (pesquisa)',
}
_PREAPPROVAL_DISPLAY_METRIC_KEYS = tuple(_PREAPPROVAL_METRIC_LABELS.keys())

_STRATEGY_PHASE_LABELS = {
    'research': 'pesquisa',
    'shadow': 'sombra',
    'paper_limited': 'paper limitado',
    'paper_validated': 'paper validado',
}

_PANEL_CSS = '''
:root{
--color-canvas:#F1F5F9;--color-surface:#FFFFFF;--color-sidebar:#0F172A;
--color-sidebar-muted:#94A3B8;--color-sidebar-active:#E2E8F0;--color-sidebar-active-bg:#1E293B;
--color-foreground:#0F172A;--color-muted:#64748B;--color-border:#CBD5E1;--color-ring:#0284C7;
--color-primary:#0369A1;--color-primary-fg:#FFFFFF;--color-destructive:#B91C1C;
--color-success-bg:#ECFDF5;--color-success-fg:#065F46;
--color-warning-bg:#FFFBEB;--color-warning-fg:#92400E;
--color-danger-bg:#FEF2F2;--color-danger-fg:#991B1B;
--color-research-bg:#F8FAFC;--color-research-border:#94A3B8;
--radius-sm:4px;--radius-md:8px;--radius-lg:12px;
--text-xs:12px;--text-sm:14px;--text-base:16px;--text-lg:18px;--text-xl:20px;
--space-4:16px;--space-6:24px;
--bg-canvas:var(--color-canvas);--bg-card:var(--color-surface);--text-primary:var(--color-foreground);
--text-muted:var(--color-muted);--border-subtle:var(--color-border);
--action-primary:var(--color-primary);--action-danger:var(--color-destructive);
--status-research-bg:var(--color-research-bg);--status-research-text:var(--color-muted);
--status-active-bg:var(--color-success-bg);--status-active-text:var(--color-success-fg);
--status-warning-bg:var(--color-warning-bg);--status-warning-text:var(--color-warning-fg);
}
body{font:var(--text-base) Inter,system-ui,sans-serif;margin:0;
background:var(--color-canvas);color:var(--color-foreground)}
.panel-shell{min-height:100vh;display:flex;flex-direction:column}
.panel-topbar{height:48px;display:flex;align-items:center;justify-content:space-between;
padding:0 var(--space-4);background:var(--color-surface);border-bottom:1px solid var(--color-border)}
.env-badge{font-size:var(--text-sm);font-weight:600}.env-dot{color:var(--color-success-fg)}
.layout{display:flex;flex:1;min-height:0}
.side{width:240px;background:var(--color-sidebar);color:var(--color-sidebar-active);
padding:var(--space-4);display:flex;flex-direction:column;gap:2px}
.side-brand{margin-bottom:var(--space-4);font-weight:700}
.badge-ops{font-size:var(--text-xs);background:var(--color-sidebar-active-bg);
padding:2px 6px;border-radius:var(--radius-sm);margin-left:6px;font-weight:500}
.nav-link{color:var(--color-sidebar-muted);text-decoration:none;display:block;
padding:10px 12px;border-radius:var(--radius-md);border-left:3px solid transparent}
.nav-link:focus-visible{outline:3px solid var(--color-ring);outline-offset:2px}
.nav-link--active{color:var(--color-sidebar-active);background:var(--color-sidebar-active-bg);
border-left-color:var(--color-primary)}
.side-version{margin-top:auto;font-size:var(--text-xs);color:var(--color-sidebar-muted)}
.main{flex:1;padding:var(--space-6);background:var(--color-canvas)}
.page-header{margin-bottom:var(--space-6)}
.page-header__row{display:flex;flex-wrap:wrap;align-items:flex-start;justify-content:space-between;gap:12px}
.page-header h1{margin:0 0 4px;font-size:var(--text-xl);font-weight:600}
.research-banner{padding:12px var(--space-4);margin-bottom:var(--space-4);
background:var(--color-research-bg);border:1px dashed var(--color-research-border);
border-radius:var(--radius-md);font-size:var(--text-sm)}
.section-header{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px;margin:8px 0}
.login-wrap{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:var(--space-4)}
.login-card{max-width:420px;width:100%;padding:var(--space-6);background:var(--color-surface);
border:1px solid var(--color-border);border-radius:var(--radius-lg)}
.login-badge{display:inline-block;padding:4px 10px;border-radius:var(--radius-sm);
background:var(--color-success-bg);color:var(--color-success-fg);font-size:var(--text-xs);font-weight:600;margin:8px 0}
.login-card label{display:block;margin:12px 0;font-size:var(--text-sm)}
.login-card input{width:100%;padding:10px;margin-top:4px;border:1px solid var(--color-border);
border-radius:var(--radius-md);font:inherit}
.login-footer{margin-top:var(--space-4);font-size:var(--text-sm);color:var(--color-muted)}
.card{background:var(--bg-card);border:1px solid var(--border-subtle);border-radius:var(--radius-md);
padding:var(--space-4);margin:8px 0}
.muted{color:var(--text-muted)}
.btn{display:inline-block;padding:10px 16px;border-radius:var(--radius-md);border:none;cursor:pointer;
font-weight:600;font-size:var(--text-sm);min-height:44px;text-decoration:none;text-align:center}
.btn-primary{background:var(--action-primary);color:var(--color-primary-fg)}
.btn-danger-outline{background:transparent;color:var(--action-danger);
border:1px solid var(--action-danger)}
.btn-outline{background:transparent;color:var(--color-primary);border:1px solid var(--color-primary)}
.btn-ghost{background:transparent;color:var(--color-muted);border:1px solid var(--color-border)}
.btn-ghost:hover{color:var(--color-foreground)}
.inline-alert{padding:10px 12px;border-radius:var(--radius-md);margin:8px 0;font-size:var(--text-sm)}
.inline-alert--loading{background:var(--color-research-bg);color:var(--color-muted)}
.inline-alert--ok{background:var(--color-success-bg);color:var(--color-success-fg)}
.inline-alert--err{background:var(--color-danger-bg);color:var(--color-danger-fg)}
.inline-alert--warn{background:var(--color-warning-bg);color:var(--color-warning-fg)}
.metrics-block{display:flex;flex-direction:column;gap:4px;font-size:var(--text-sm)}
.metrics-block .metric{display:block;color:var(--text-primary)}
.empty-state{padding:16px;border-radius:var(--radius-md);background:var(--status-research-bg);
color:var(--status-research-text);border:1px solid var(--border-subtle)}
.badge-status{display:inline-block;padding:4px 8px;border-radius:var(--radius-sm);
font-size:var(--text-xs);font-weight:500}
.badge-status--pending{background:var(--status-research-bg);color:var(--status-research-text)}
.badge-status--approved{background:var(--status-active-bg);color:var(--status-active-text)}
.badge-status--rejected{background:var(--status-warning-bg);color:var(--status-warning-text)}
table{width:100%;border-collapse:collapse}td,th{border:1px solid var(--border-subtle);padding:12px 16px;
text-align:left;font-size:var(--text-sm);font-variant-numeric:tabular-nums}
.warn{background:var(--status-warning-bg);border:1px solid #e6c48a;padding:12px;border-radius:var(--radius-md);
color:var(--status-warning-text)}
.brake-strip{padding:12px 16px;border-radius:8px;margin:8px 0;display:flex;flex-wrap:wrap;
align-items:center;gap:12px;justify-content:space-between;transition:background .2s,color .2s}
.brake-strip--active{background:#7A1218;color:#FFF7F5}
.brake-strip--released{background:#1C4A52;color:#E6F4F4}
.brake-strip__body{flex:1;min-width:200px}
.brake-strip__title{font-size:22px;font-weight:700;margin:0}
.brake-strip__help{font-size:14px;margin:4px 0 0}
.brake-strip__cta{padding:10px 16px;border-radius:8px;cursor:pointer;font:inherit;font-weight:600;min-height:44px}
.brake-strip--active .brake-strip__cta{background:#FFF7F5;color:#7A1218;border:none}
.brake-strip--released .brake-strip__cta{background:transparent;color:#FFF7F5;border:2px solid #E6B6B6}
.brake-strip__cta:focus-visible{outline:3px solid #F0C14B;outline-offset:3px}
@media (prefers-reduced-motion:reduce){.brake-strip{transition:none}}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
'''


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_login_page(*, error: str | None = None) -> str:
    err = f'<p role="alert" class="warn">Informe a senha do protótipo.</p>' if error else ''
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Entrar — Trading Lab</title>
<style>{_PANEL_CSS}</style></head><body><div class="login-wrap">
<main class="login-card"><h1>Trading Lab — Painel operador</h1>
<span class="login-badge">Paper · Live desligado</span>
<p class="muted">Protótipo: informe qualquer senha não vazia.</p>{err}
<form method="post" action="/api/login"><label>E-mail<input name="email" type="email"
placeholder="operador@demo" autocomplete="username"></label>
<label>Senha<input name="password" type="password" required autocomplete="current-password"></label>
<button class="btn btn-primary" type="submit" style="width:100%">Entrar</button></form>
<p class="login-footer">Pesquisa não autoriza ordem no painel.</p></main></div></body></html>'''


def _topbar_html() -> str:
    return (
        '<header class="panel-topbar" role="banner">'
        '<span class="env-badge"><span class="env-dot" aria-hidden="true">●</span> '
        'Paper · Live desligado</span>'
        '<a class="btn btn-ghost" href="/login">Sair</a>'
        '</header>'
    )


def _page_header(title: str, subtitle: str, actions: str = '') -> str:
    actions_html = f'<div class="page-header__actions">{actions}</div>' if actions else ''
    return (
        f'<header class="page-header"><div class="page-header__row">'
        f'<div><h1>{esc(title)}</h1><p class="muted">{esc(subtitle)}</p></div>'
        f'{actions_html}</div></header>'
    )


def _wrap_panel_page(
    *,
    title: str,
    active: str,
    page_title: str,
    subtitle: str,
    body: str,
    research_banner: str = '',
    scripts: str = '',
) -> str:
    header = _page_header(page_title, subtitle)
    banner = research_banner
    script_tag = f'<script>{scripts}</script>' if scripts else ''
    return (
        f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        f'<title>{esc(title)}</title><style>{_PANEL_CSS}</style></head><body>'
        f'<div class="panel-shell">{_topbar_html()}'
        f'<div class="layout">{_nav(active)}<main class="main">{header}{banner}{body}</main></div>'
        f'</div><!-- PanelShell v2 ISS-023 -->{script_tag}</body></html>'
    )


def _nav(active: str) -> str:
    links = (
        ('central', '/', 'Central'),
        ('ordens', '/ordens', 'Ordens'),
        ('historico', '/historico', 'Histórico'),
        ('sinais', '/sinais', 'Sinais'),
        ('estrategias', '/estrategias', 'Estratégias'),
        ('prodigy', '/prodigy', 'Prodígio'),
        ('performance', '/performance', 'Performance'),
        ('analise_google', '/analise-google', 'Análise Google'),
    )
    parts = [
        '<nav class="side panel-sidebar" aria-label="Menu principal">',
        '<div class="side-brand">Trading Lab<span class="badge-ops">Ops</span></div>',
    ]
    for key, href, label in links:
        cls = 'nav-link nav-link--active' if key == active else 'nav-link'
        aria = ' aria-current="page"' if key == active else ''
        parts.append(f'<a class="{cls}" href="{href}"{aria}>{esc(label)}</a>')
    parts.append('<span class="side-version">ISS-023</span></nav>')
    return ''.join(parts)


def _brake_strip_html(kill_active: bool) -> str:
    if kill_active:
        mod = 'brake-strip--active'
        title = 'Freio de emergência ativo'
        help_txt = 'Ordens demo novas bloqueadas.'
        cta = '<button type="button" class="brake-strip__cta" id="kill-off">Liberar freio</button>'
    else:
        mod = 'brake-strip--released'
        title = 'Freio liberado'
        help_txt = 'Outros limites ainda valem.'
        cta = '<button type="button" class="brake-strip__cta" id="kill-on">Ativar freio</button>'
    return (
        f'<div class="brake-strip {mod}" role="status">'
        f'<div class="brake-strip__body"><p class="brake-strip__title">{esc(title)}</p>'
        f'<p class="brake-strip__help">{esc(help_txt)}</p></div>{cta}</div>'
    )


_KILL_PATCH_SCRIPT = '''
async function patchKill(on){await fetch('/api/triggers',{method:'PATCH',headers:{'Content-Type':'application/json'},
credentials:'same-origin',body:JSON.stringify({kill_switch_on:on})});location.reload();}
const killOn=document.getElementById('kill-on');
if(killOn)killOn.onclick=()=>patchKill(true);
const killOff=document.getElementById('kill-off');
if(killOff)killOff.onclick=()=>patchKill(false);
'''

_PROVIDER_APPROVAL_SCRIPT = '''
async function setProviderApproval(platform,providerId,action){
  const res=await fetch('/api/signals/providers',{
    method:'POST',headers:{'Content-Type':'application/json'},credentials:'same-origin',
    body:JSON.stringify({platform,provider_id:providerId,action})});
  if(res.status===401){location.href='/login';return;}
  if(!res.ok){alert('Não foi possível registrar a decisão.');return;}
  location.reload();
}
document.querySelectorAll('[data-provider-action]').forEach(btn=>{
  btn.onclick=()=>setProviderApproval(
    btn.dataset.platform,btn.dataset.providerId,btn.dataset.providerAction);
});
'''

_CANDIDATES_RELOAD_HINT = (
    'Aplica critérios Feature 4 / Prodígio 15d no servidor '
    '(C2 server-side; TV = origens já ingeridas). Não aprova nem envia ordem.'
)

_CANDIDATES_RELOAD_SCRIPT = '''
(async function(){
  const btn=document.getElementById('reload-candidates');
  const box=document.getElementById('reload-feedback');
  if(!btn||!box)return;
  const failClosed='Não foi possível atualizar. A fila anterior foi mantida.';
  const waitEnded='A espera terminou antes da resposta do servidor. A fila anterior foi mantida.';
  const clientWaitMs=45000;
  const fmtClock=(iso)=>{
    if(!iso)return'';
    try{
      const d=new Date(iso);
      if(Number.isNaN(d.getTime()))return'';
      return d.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});
    }catch(_e){return'';}
  };
  btn.onclick=async()=>{
    btn.disabled=true;
    btn.setAttribute('aria-busy','true');
    box.hidden=false;
    box.className='inline-alert inline-alert--loading';
    box.textContent='Atualizando candidatos…';
    let timer=null;
    try{
      const controller=new AbortController();
      timer=setTimeout(()=>controller.abort(),clientWaitMs);
      const res=await fetch('/api/signals/candidates/refresh',{
        method:'POST',headers:{'Content-Type':'application/json'},
        credentials:'same-origin',body:JSON.stringify({}),
        signal:controller.signal});
      clearTimeout(timer);
      if(res.status===401){clearTimeout(timer);location.href='/login';return;}
      const data=await res.json().catch(()=>({}));
      if(res.status===429){
        box.className='inline-alert inline-alert--err';
        box.textContent='Aguarde antes de atualizar de novo.';
        return;
      }
      if(!res.ok){
        box.className='inline-alert inline-alert--err';
        box.textContent=data.message||failClosed;
        return;
      }
      const clock=fmtClock(data.refreshed_at);
      box.className='inline-alert inline-alert--ok';
      box.textContent=clock
        ?'Candidatos atualizados às '+clock+'.'
        :(data.message||'Critérios ao vivo aplicados no servidor.');
      setTimeout(()=>location.reload(),500);
    }catch(err){
      box.className='inline-alert inline-alert--err';
      const aborted=err&&(err.name==='AbortError'||err.name==='TimeoutError');
      box.textContent=aborted?waitEnded:failClosed;
    }finally{
      try{clearTimeout(timer);}catch(_t){}
      btn.disabled=false;
      btn.removeAttribute('aria-busy');
    }
  };
})();
'''


def _platform_health_block(ph: dict[str, Any] | None) -> str:
    ph = ph or {}
    overall = ph.get('overall') or 'unknown'
    comp_rows = ''.join(
        f'<tr><td>{esc(c.get("id", ""))}</td>'
        f'<td>{esc(c.get("status", ""))}</td>'
        f'<td>{esc(c.get("detail", ""))}</td></tr>'
        for c in (ph.get('components') or [])
    ) or '<tr><td colspan="3">Aguardando primeira checagem automática (v4-ops)</td></tr>'
    return (
        f'<h2>Plataforma — semáforo</h2>'
        f'<p class="muted">Agregado: <strong>{esc(overall)}</strong> · '
        f'atualizado em {esc(ph.get("generated_at", "—"))}</p>'
        f'<table><thead><tr><th>Componente</th><th>Status</th><th>Detalhe</th></tr></thead>'
        f'<tbody>{comp_rows}</tbody></table>'
    )


def render_central_page(data: dict[str, Any], triggers: dict[str, Any] | None) -> str:
    flags = (triggers or {}).get('control_flags') or {}
    markets = (triggers or {}).get('market_controls') or []
    kill_active = flags.get('kill_switch_on') is True
    brake = _brake_strip_html(kill_active)
    cards = ''.join(
        f'<div class="card"><small class="muted">{esc(label)}</small>'
        f'<div class="mono"><strong>{esc(flags.get(key, "—"))}</strong></div></div>'
        for label, key in (
            ('Capital (centavos)', 'capital_cents'),
            ('Risco por operação', 'max_risk_per_trade_cents'),
            ('Posições abertas máx.', 'max_open_positions'),
            ('Risco agregado', 'max_aggregate_risk_cents'),
            ('Perda diária', 'max_daily_loss_cents'),
            ('Perda semanal', 'max_weekly_loss_cents'),
        )
    )
    market_rows = ''.join(
        f'<tr><td>{esc(m.get("market"))}</td><td>{"sim" if m.get("operation_on") else "não"}</td></tr>'
        for m in markets
    )
    recent = (data.get('signals') or [])[:5]
    sig_rows = ''.join(
        f'<tr><td>{esc(s.get("origin"))}</td><td>{esc(s.get("symbol"))}</td>'
        f'<td>{esc(s.get("destination"))}</td><td>{esc(s.get("reject_reason") or "—")}</td></tr>'
        for s in recent
    ) or '<tr><td colspan="4">Sem sinais recentes</td></tr>'
    body = (
        f'{brake}'
        f'{_platform_health_block(data.get("platform_health"))}'
        f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px">{cards}</div>'
        f'<h2>Mercados</h2><table><tbody>{market_rows}</tbody></table>'
        f'<h2>Sinais recentes</h2><table><tbody>{sig_rows}</tbody></table>'
        f'<p><a href="/sinais">Ver todos os sinais</a></p>'
    )
    return _wrap_panel_page(
        title='Central',
        active='central',
        page_title='Central',
        subtitle='Conta demo · Live desligado (sem botão)',
        body=body,
        scripts=_KILL_PATCH_SCRIPT,
    )


def render_orders_page(bundle: dict[str, Any]) -> str:
    rows = ''.join(
        f'<tr><td class="mono">{esc(o.get("client_order_id") or "—")}</td>'
        f'<td>{esc(o.get("symbol"))}</td><td>{esc(o.get("side"))}</td>'
        f'<td>{esc(o.get("status"))}</td><td>{esc(o.get("broker_status") or o.get("paper_status") or "—")}</td>'
        f'<td class="mono">{esc(o.get("remaining_qty") or o.get("entry_qty") or "—")}</td>'
        f'<td>{esc(o.get("strategy_key") or "—")}</td></tr>'
        for o in bundle.get('open_orders') or []
    ) or '<tr><td colspan="7">Nenhuma ordem aberta no paper.</td></tr>'
    body = (
        '<table><thead><tr><th>ID cliente</th><th>Ativo</th><th>Lado</th><th>Status</th>'
        '<th>Corretora</th><th>Qtd rest.</th><th>Estratégia</th></tr></thead>'
        f'<tbody>{rows}</tbody></table>'
    )
    return _wrap_panel_page(
        title='Ordens',
        active='ordens',
        page_title='Ordens abertas',
        subtitle='Somente leitura — paper demo. Live desligado.',
        body=body,
    )


def render_history_page(bundle: dict[str, Any]) -> str:
    label = esc(PERFORMANCE_LABEL_GROSS)
    rows = ''.join(
        f'<tr><td class="mono">{esc(h.get("client_order_id") or "—")}</td>'
        f'<td>{esc(h.get("symbol"))}</td><td>{esc(h.get("side"))}</td>'
        f'<td class="mono">{esc(h.get("realized_gross_pnl_usd") or "—")}</td>'
        f'<td>{label}</td><td>{esc(h.get("strategy_key") or "—")}</td></tr>'
        for h in bundle.get('order_history') or []
    ) or '<tr><td colspan="6">Nenhum fill confirmado no histórico.</td></tr>'
    body = (
        '<table><thead><tr><th>ID cliente</th><th>Ativo</th><th>Lado</th><th>Resultado</th>'
        f'<th>Rótulo</th><th>Estratégia</th></tr></thead><tbody>{rows}</tbody></table>'
    )
    return _wrap_panel_page(
        title='Histórico',
        active='historico',
        page_title='Histórico de fills',
        subtitle='Apenas fills confirmados — fila e HTTP 200 não entram.',
        body=body,
    )


def _strategy_phase_label(phase: Any) -> str:
    raw = str(phase or '')
    return _STRATEGY_PHASE_LABELS.get(raw, raw)


def _tip_label_pt(label: Any) -> str:
    raw = str(label or '')
    return _TIP_LABEL_PT.get(raw, raw)


def _analise_google_body(block: dict[str, Any]) -> str:
    status = str(block.get('timesfm_status') or 'UNAVAILABLE')
    if status != 'OK':
        reason = block.get('operator_reason') or 'modelo ou dependência ausente.'
        return (
            f'<p class="warn">{esc(_N43_UNAVAILABLE_MAIN)}</p>'
            f'<p class="muted">Motivo: {esc(reason)}</p>'
        )
    tips = block.get('tips') or []
    if not tips:
        return f'<p class="muted">{esc(_N43_EMPTY_TIPS)}</p>'
    rows = ''.join(
        f'<tr><td>{esc(_tip_label_pt(t.get("label")))}</td>'
        f'<td>{esc(t.get("summary") or "—")}</td></tr>'
        for t in tips
    )
    return (
        '<table><thead><tr><th>Rótulo</th><th>Resumo</th></tr></thead>'
        f'<tbody>{rows}</tbody></table>'
    )


def render_analise_google_page(bundle: dict[str, Any]) -> str:
    block = bundle.get('timesfm') if isinstance(bundle.get('timesfm'), dict) else {}
    body = _analise_google_body(block)
    page_body = f'{body}<p class="muted">{esc(_N43_FOOTER)}</p>'
    return _wrap_panel_page(
        title='Análise Google',
        active='analise_google',
        page_title='Análise Google',
        subtitle=_N43_SUBTITLE,
        research_banner=(
            f'<aside class="research-banner">{esc(_N43_SUBTITLE)}</aside>'
        ),
        body=page_body,
    )


def render_strategies_page(bundle: dict[str, Any]) -> str:
    catalog = bundle.get('strategy_catalog') or {}
    strategies = catalog.get('strategies') or []
    if catalog.get('status') == 'LEDGER_UNAVAILABLE' or not strategies:
        rows = (
            '<tr><td colspan="3">Catálogo indisponível (ledger)</td></tr>'
        )
    else:
        rows = ''.join(
            f'<tr><td class="mono">{esc(s.get("strategy_key") or "—")}</td>'
            f'<td>{esc(_strategy_phase_label(s.get("phase")))}</td>'
            f'<td>{"sim" if s.get("paper_allowed") else "não"}</td></tr>'
            for s in strategies
        )
    disclaimer = 'Promoção de fase: somente operador (fora deste menu).'
    page_body = (
        '<table><thead><tr><th>Chave</th><th>Fase</th><th>Paper permitido</th></tr></thead>'
        f'<tbody>{rows}</tbody></table><p class="muted">{esc(disclaimer)}</p>'
    )
    return _wrap_panel_page(
        title='Estratégias',
        active='estrategias',
        page_title='Estratégias',
        subtitle='Catálogo de fases — somente leitura. Live desligado.',
        body=page_body,
    )


def _order_signal_cell(row: dict[str, Any]) -> str:
    if row.get('signal_id'):
        return f'<code>{esc(row.get("signal_id"))}</code>'
    return esc(row.get('signal_link_notice') or 'sem vínculo com sinal')


def _signals_copy_operating_html(operating: list[dict[str, Any]]) -> str:
    if not operating:
        return (
            f'<div class="empty-state">{esc(_N48_COPY_EMPTY)} '
            f'{esc(_N48_COPY_EMPTY_HINT)}</div>'
        )
    rows = ''.join(
        f'<tr><td class="mono">{esc(o.get("client_order_id") or "—")}</td>'
        f'<td>{esc(o.get("symbol"))}</td><td>{esc(o.get("side"))}</td>'
        f'<td>{esc(o.get("origin") or "origem desconhecida")}</td>'
        f'<td>{_order_signal_cell(o)}</td>'
        f'<td>{esc(o.get("broker_status") or o.get("paper_status") or "—")}</td>'
        f'<td class="mono">{esc(o.get("remaining_qty") or o.get("entry_qty") or "—")}</td></tr>'
        for o in operating
    )
    head = (
        '<table><thead><tr><th>ID cliente</th><th>Ativo</th><th>Lado</th>'
        '<th>Origem</th><th>Sinal</th><th>Status</th><th>Qtd rest.</th></tr></thead><tbody>'
    )
    return f'{head}{rows}</tbody></table>'


def _signals_copy_perf_html(perf: dict[str, Any]) -> str:
    label = esc(perf.get('pnl_label') or PERFORMANCE_LABEL_GROSS)
    strategies = perf.get('strategies') or []
    if not strategies:
        return f'<p class="muted">{esc(_N48_COPY_PERF_EMPTY)}</p>'
    rows = ''.join(
        f'<tr><td>{esc(s.get("strategy_key"))}</td>'
        f'<td class="mono">{esc(s.get("gross_usd") or "—")}</td><td>{label}</td></tr>'
        for s in strategies
    )
    return (
        '<h3>Resultado (família de cópia)</h3>'
        f'<p class="warn">Valores rotulados <b>{label}</b> — fila e HTTP 200 não são fill.</p>'
        '<table><thead><tr><th>Família</th><th>Resultado</th><th>Rótulo</th></tr></thead>'
        f'<tbody>{rows}</tbody></table>'
    )


def _signals_copy_research_html(research: list[dict[str, Any]]) -> str:
    if not research:
        return ''
    rows = ''.join(
        f'<tr><td>{esc(c.get("provider"))}</td><td>{esc(c.get("symbol"))}</td>'
        f'<td><code>{esc(c.get("label") or "research_copy_not_order_auth")}</code></td></tr>'
        for c in research
    )
    return (
        f'<h3>Pesquisa (Prodígio)</h3><p class="muted">{esc(_N48_RESEARCH_NOTE)}</p>'
        f'<table><tbody>{rows}</tbody></table>'
    )


def _signals_inventory_html(inventory: dict[str, Any]) -> str:
    items = inventory.get('items') or []
    if not items:
        empty = inventory.get('empty_label') or _N49_INVENTORY_EMPTY
        return (
            f'<h2>{esc(_N49_INVENTORY_SECTION)}</h2>'
            f'<p class="muted">{esc(empty)}</p>'
        )
    label = esc(inventory.get('pnl_label') or PERFORMANCE_LABEL_GROSS)
    rows = ''.join(
        f'<tr><td>{esc(it.get("origin"))}</td>'
        f'<td><code>{esc(it.get("signal_id") or it.get("signal_event_id") or "—")}</code></td>'
        f'<td class="mono">{esc(it.get("operating"))}</td>'
        f'<td class="mono">{esc(it.get("fills_confirmed"))}</td>'
        f'<td class="mono">{esc(it.get("gross_usd_total") or "—")}</td>'
        f'<td>{label}</td></tr>'
        for it in items
    )
    unknown = inventory.get('unknown_unlinked_count') or 0
    extra = ''
    if unknown:
        extra = (
            f'<p class="muted">Vínculo desconhecido em {esc(unknown)} linha(s) — '
            'sem resultado por sinal inventado.</p>'
        )
    return (
        f'<h2>{esc(_N49_INVENTORY_SECTION)}</h2>'
        '<p class="muted">Resultado por sinal só com fill confirmado; valores brutos se o custo faltar.</p>'
        '<table><thead><tr><th>Origem</th><th>Sinal</th><th>Em operação</th>'
        f'<th>Fills</th><th>Resultado</th><th>Rótulo</th></tr></thead><tbody>{rows}</tbody></table>'
        f'{extra}'
    )


def _signals_adoption_html(adoption: dict[str, Any]) -> str:
    criteria = adoption.get('criteria_pt') or []
    bullets = ''.join(f'<li>{esc(line)}</li>' for line in criteria)
    phases = adoption.get('catalog_phases') or []
    phase_rows = ''.join(
        f'<tr><td class="mono">{esc(p.get("strategy_key"))}</td>'
        f'<td>{esc(_strategy_phase_label(p.get("phase")))}</td>'
        f'<td>{"sim" if p.get("paper_allowed") else "não"}</td></tr>'
        for p in phases
    )
    phase_table = ''
    if phase_rows:
        phase_table = (
            '<h3>Fases no catálogo</h3>'
            '<table><thead><tr><th>Chave</th><th>Fase</th><th>Paper permitido</th></tr></thead>'
            f'<tbody>{phase_rows}</tbody></table>'
        )
    return (
        f'<h2>{esc(_N49_ADOPTION_SECTION)}</h2>'
        f'<ul>{bullets}</ul>'
        f'{phase_table}'
    )


def _provider_cell(it: dict[str, Any]) -> str:
    return esc(it.get('provider') or it.get('provider_id') or '—')


def _signals_prodigy_pool_html(pool: dict[str, Any]) -> str:
    items = pool.get('items') or []
    if not items:
        return (
            f'<h2>{esc(_N50_POOL_SECTION)}</h2>'
            f'<p class="muted">{esc(_N49_POOL_SUBTITLE)}</p>'
            f'<p class="muted">{esc(_N49_POOL_EMPTY)}</p>'
        )
    rows = ''.join(
        f'<tr><td>{_provider_cell(it)}</td>'
        f'<td>{esc(it.get("status"))}</td>'
        f'<td class="mono">{esc(it.get("prodigy_score"))}</td>'
        f'<td><code>{esc(it.get("label") or "research_tip")}</code></td></tr>'
        for it in items
    )
    disclaimer = esc(pool.get('disclaimer') or 'Research rank only; does not authorize orders.')
    return (
        f'<h2>{esc(_N50_POOL_SECTION)}</h2>'
        f'<p class="muted">{esc(_N49_POOL_SUBTITLE)}</p>'
        f'<p class="muted">{disclaimer}</p>'
        f'<table><thead><tr><th>Provedor</th><th>Status</th><th>Score</th>'
        f'<th>Rótulo</th></tr></thead><tbody>{rows}</tbody></table>'
    )


def _signals_operating_section_html(copy: dict[str, Any]) -> str:
    operating = copy.get('operating') or []
    history = copy.get('history') or []
    perf = copy.get('performance') if isinstance(copy.get('performance'), dict) else {}
    research = copy.get('research_copies') or []
    collective2 = copy.get('collective2') if isinstance(copy.get('collective2'), dict) else {}
    subscribed = collective2.get('subscribed') or []
    c2_operating = copy.get('collective2_operating') or []
    label = esc(perf.get('pnl_label') or PERFORMANCE_LABEL_GROSS)
    hist_rows = ''.join(
        f'<tr><td class="mono">{esc(h.get("client_order_id") or "—")}</td>'
        f'<td>{esc(h.get("symbol"))}</td>'
        f'<td class="mono">{esc(h.get("realized_gross_pnl_usd") or "—")}</td>'
        f'<td>{label}</td></tr>'
        for h in history
    )
    hist_block = ''
    if hist_rows:
        hist_block = (
            '<h3>Fills confirmados (família de cópia)</h3>'
            '<table><thead><tr><th>ID cliente</th><th>Ativo</th><th>Resultado</th>'
            f'<th>Rótulo</th></tr></thead><tbody>{hist_rows}</tbody></table>'
        )
    subscribed_block = ''
    if subscribed:
        sub_rows = ''.join(
            f'<tr><td class="mono">{esc(s.get("provider_id"))}</td>'
            f'<td>{esc(s.get("status"))}</td>'
            f'<td><code>{esc(s.get("label") or "named_allowlist")}</code></td></tr>'
            for s in subscribed
        )
        subscribed_block = (
            '<h3>Assinados Collective2 (lista nomeada)</h3>'
            '<p class="muted">Identificadores nomeados — não é fill nem promove sozinho.</p>'
            '<table><thead><tr><th>ID provedor</th><th>Status</th><th>Rótulo</th></tr></thead>'
            f'<tbody>{sub_rows}</tbody></table>'
        )
    elif collective2.get('approved_ids'):
        subscribed_block = (
            '<h3>Assinados Collective2 (lista nomeada)</h3>'
            '<p class="muted">Nenhuma ordem paper Collective2 neste recorte; IDs nomeados aguardam operação.</p>'
        )
    c2_ops_block = ''
    if c2_operating:
        c2_ops_block = (
            '<h3>Ordens paper Collective2</h3>'
            f'{_signals_copy_operating_html(c2_operating)}'
        )
    return (
        f'<h2>{esc(_N50_OPERATING_SECTION)}</h2>'
        f'<p class="muted">{esc(_N48_COPY_SUBTITLE)}</p>'
        '<h3>Em operação (paper)</h3>'
        f'{_signals_copy_operating_html(operating)}'
        f'{c2_ops_block}'
        f'{subscribed_block}'
        f'{hist_block}'
        f'{_signals_copy_perf_html(perf)}'
        f'{_signals_copy_research_html(research)}'
    )


def _signals_collective2_section_html(collective2: dict[str, Any]) -> str:
    c2 = collective2 if isinstance(collective2, dict) else {}
    approved = c2.get('approved_ids') or []
    banner = _N50_C2_ALLOWLIST if approved else _N50_C2_EMPTY
    candidates = c2.get('candidates') or []
    cand_rows = ''.join(
        f'<tr><td class="mono">{esc(c.get("provider_id"))}</td>'
        f'<td>{esc(c.get("name"))}</td>'
        f'<td><code>{esc(c.get("label") or "research_only")}</code></td></tr>'
        for c in candidates
    )
    cand_block = (
        f'<table><thead><tr><th>ID</th><th>Nome</th><th>Rótulo</th></tr></thead>'
        f'<tbody>{cand_rows}</tbody></table>'
        if cand_rows
        else '<p class="muted">Nenhum candidato de pesquisa gravado no disco.</p>'
    )
    snapshot = c2.get('active_orders_snapshot')
    snap_block = ''
    if isinstance(snapshot, dict):
        snap_block = (
            '<h3>Instantâneo de ordens ativas (somente leitura)</h3>'
            f'<p class="warn">{esc(_N50_C2_SNAPSHOT_LABEL)}</p>'
            f'<p class="muted">Registros: {esc(snapshot.get("active_orders_count", 0))}; '
            f'as_of: {esc(snapshot.get("as_of") or "—")}</p>'
        )
    id_list = ', '.join(str(x) for x in approved) if approved else '—'
    return (
        f'<h2>{esc(_N50_C2_SECTION)}</h2>'
        f'<p class="muted">{esc(_N50_C2_SUBTITLE)}</p>'
        f'<p class="warn">{esc(banner)}</p>'
        f'<p><strong>Lista nomeada:</strong> <span class="mono">{esc(id_list)}</span></p>'
        '<h3>Candidatos de pesquisa (não aprovados automaticamente)</h3>'
        f'{cand_block}'
        f'{snap_block}'
    )


def _format_research_metric(metrics: dict[str, Any] | None, key: str) -> str:
    block = metrics if isinstance(metrics, dict) else {}
    if key not in block:
        return 'indisponível'
    return esc(block[key])


def _preapproval_metrics_block_html(metrics: dict[str, Any] | None) -> str:
    block = metrics if isinstance(metrics, dict) else {}
    spans = []
    for key in _PREAPPROVAL_DISPLAY_METRIC_KEYS:
        label = _PREAPPROVAL_METRIC_LABELS[key]
        value = _format_research_metric(block, key)
        spans.append(
            f'<span class="metric"><strong>{esc(label)}:</strong> {value}</span>'
        )
    return f'<div class="metrics-block">{"".join(spans)}</div>'


def _candidates_refresh_meta_html(refresh: dict[str, Any] | None) -> str:
    block = refresh if isinstance(refresh, dict) else {}
    refreshed_at = str(block.get('refreshed_at') or '').strip()
    sources = block.get('sources_ok')
    if isinstance(sources, list) and sources:
        sources_label = ', '.join(str(s) for s in sources)
    else:
        sources_label = 'nenhuma'
    chunks: list[str] = []
    if refreshed_at:
        chunks.append(f'Última tentativa: <code>{esc(refreshed_at)}</code>')
    chunks.append(f'Fontes OK: <code>{esc(sources_label)}</code>')
    if not chunks:
        return ''
    return (
        f'<p class="muted candidates-refresh-meta" role="status">'
        f'{" · ".join(chunks)}</p>'
    )


def _candidates_refresh_warning_html(copy: dict[str, Any]) -> str:
    block = copy if isinstance(copy, dict) else {}
    refresh = block.get('candidates_refresh')
    issues: list[str] = []
    status: str | None = None
    refresh_record: dict[str, Any] | None = None
    if isinstance(refresh, dict):
        refresh_record = refresh
        raw_issues = refresh.get('issues')
        if isinstance(raw_issues, list):
            issues = [str(item) for item in raw_issues if str(item).strip()]
        status_val = refresh.get('status')
        status = str(status_val) if status_val is not None else None
    if not issues:
        pre = block.get('preapproval') or {}
        if isinstance(pre, dict):
            raw_issues = pre.get('refresh_issues')
            if isinstance(raw_issues, list):
                issues = [str(item) for item in raw_issues if str(item).strip()]
            status_val = pre.get('refresh_status')
            status = str(status_val) if status_val is not None else status
    meta = _candidates_refresh_meta_html(refresh_record)
    if not issues:
        return meta
    if status and status not in ('partial', 'ok'):
        return meta
    items = ''.join(f'<li><code>{esc(issue)}</code></li>' for issue in issues)
    banner = (
        '<div class="inline-alert inline-alert--warn partial-refresh-banner" '
        'role="status" aria-live="polite">'
        '<p><strong>Atualização parcial.</strong> Algumas fontes falharam; '
        'a fila abaixo mantém as plataformas que responderam.</p>'
        f'<ul class="partial-issues-list">{items}</ul></div>'
    )
    return f'{meta}{banner}'


def _preapproval_status_badge(status: Any) -> str:
    raw = str(status or 'pending').lower()
    if raw == 'approved':
        css = 'badge-status badge-status--approved'
    elif raw == 'rejected':
        css = 'badge-status badge-status--rejected'
    else:
        css = 'badge-status badge-status--pending'
    return f'<span class="{css}">{esc(status or "pending")}</span>'


def _signals_preapproval_section_html(
    preapproval: dict[str, Any],
    *,
    copy: dict[str, Any] | None = None,
) -> str:
    block = preapproval if isinstance(preapproval, dict) else {}
    partial_banner = _candidates_refresh_warning_html(copy or {})
    queue = block.get('queue') or []
    if not queue:
        body = f'<div class="empty-state">{esc(_N51_PREAPPROVAL_EMPTY)}</div>'
    else:
        rows = []
        for item in queue:
            metrics = item.get('metrics') if isinstance(item.get('metrics'), dict) else {}
            metrics_block = _preapproval_metrics_block_html(metrics)
            plat_raw = str(item.get('platform') or '—')
            pid_raw = str(item.get('provider_id') or '—')
            plat = esc(plat_raw)
            pid = esc(pid_raw)
            plat_attr = html.escape(plat_raw, quote=True)
            pid_attr = html.escape(pid_raw, quote=True)
            status_badge = _preapproval_status_badge(item.get('status'))
            approve = (
                f'<button type="button" class="btn btn-primary" data-provider-action="approve" '
                f'data-platform="{plat_attr}" data-provider-id="{pid_attr}">Aprovar</button>'
            )
            reject = (
                f'<button type="button" class="btn btn-danger-outline" data-provider-action="reject" '
                f'data-platform="{plat_attr}" data-provider-id="{pid_attr}">Rejeitar</button>'
            )
            rows.append(
                f'<tr><td>{plat}</td><td class="mono">{pid}</td>'
                f'<td>{metrics_block}</td><td>{status_badge}</td>'
                f'<td>{approve} {reject}</td></tr>'
            )
        body = (
            '<table><thead><tr><th>Plataforma</th><th>Identificador</th>'
            '<th>Métricas vitais (pesquisa)</th><th>Status</th><th>Ações</th>'
            f'</tr></thead><tbody>{"".join(rows)}</tbody></table>'
        )
    refresh_controls = (
        '<div class="section-header">'
        f'<p class="muted" style="margin:0">{esc(_N51_PREAPPROVAL_SUBTITLE)}</p>'
        '<button type="button" class="btn btn-outline" id="reload-candidates">'
        '<span aria-hidden="true">↻</span> Atualizar candidatos</button>'
        '</div>'
        f'<p class="muted panel-hint">{esc(_CANDIDATES_RELOAD_HINT)}</p>'
        '<div id="reload-feedback" class="inline-alert" aria-live="polite" role="status" hidden></div>'
    )
    return (
        f'<h2>{esc(_N51_PREAPPROVAL_SECTION)}</h2>'
        f'{partial_banner}'
        f'{refresh_controls}'
        f'{body}'
    )


def _signals_audit_section_html(signals: list[dict[str, Any]]) -> str:
    rows = ''.join(
        f'<tr><td class="mono">{esc(s.get("received_at") or "—")}</td>'
        f'<td>{esc(s.get("origin"))}</td><td>{esc(s.get("symbol"))}</td>'
        f'<td>{esc(s.get("market"))}</td><td>{esc(s.get("destination"))}</td>'
        f'<td>{esc(s.get("reject_reason") or "—")}</td></tr>'
        for s in signals
    ) or f'<tr><td colspan="6">{esc(_N48_AUDIT_EMPTY)}</td></tr>'
    return (
        f'<h2>{esc(_N48_AUDIT_SECTION)}</h2>'
        f'<p class="muted">{esc(_N48_AUDIT_SUBTITLE)}</p>'
        '<table><thead><tr><th>Hora</th><th>Origem</th><th>Ativo</th><th>Mercado</th>'
        f'<th>Destino</th><th>Motivo</th></tr></thead><tbody>{rows}</tbody></table>'
    )


def render_signals_page(bundle: dict[str, Any]) -> str:
    import os

    copy = bundle.get('copy') if isinstance(bundle.get('copy'), dict) else {}
    signals = bundle.get('signals') or []
    app_version = os.environ.get('APP_GIT_SHA', '').strip() or 'unknown'
    version_line = (
        f'<p class="muted panel-version">Versão do painel: '
        f'<code>{esc(app_version)}</code></p>'
    )
    operating_body = _signals_operating_section_html(copy)
    preapproval_body = _signals_preapproval_section_html(
        copy.get('preapproval') or {},
        copy=copy,
    )
    inventory_body = _signals_inventory_html(copy.get('inventory') or {})
    c2_body = _signals_collective2_section_html(copy.get('collective2') or {})
    pool_body = _signals_prodigy_pool_html(copy.get('prodigy_pool') or {})
    adoption_body = _signals_adoption_html(copy.get('adoption') or {})
    audit_body = _signals_audit_section_html(signals)
    footer = f'<p class="muted">{esc(_N48_FOOTER)}</p>'
    body = (
        f'{version_line}'
        f'{preapproval_body}'
        f'{operating_body}'
        f'{inventory_body}'
        f'{c2_body}'
        f'{pool_body}'
        f'{adoption_body}'
        f'{audit_body}'
        f'{footer}'
    )
    research = (
        '<aside class="research-banner">'
        'Cópia de terceiros — pesquisa. Aprovar não é fill. Live desligado.</aside>'
    )
    scripts = _PROVIDER_APPROVAL_SCRIPT + _CANDIDATES_RELOAD_SCRIPT
    return _wrap_panel_page(
        title='Sinais',
        active='sinais',
        page_title='Sinais',
        subtitle='Cockpit de decisão — cópia de terceiros (pesquisa). Live desligado.',
        research_banner=research,
        body=body,
        scripts=scripts,
    )


def render_prodigy_page(bundle: dict[str, Any], opportunities: dict[str, Any]) -> str:
    items = (opportunities or {}).get('items') or []
    disclaimer = esc((opportunities or {}).get('disclaimer') or 'Sugestão de pesquisa — não autoriza ordem.')
    rank_rows = ''.join(
        f'<tr><td>{_provider_cell(o)}</td><td>{esc(o.get("status"))}</td>'
        f'<td class="mono">{esc(o.get("prodigy_score"))}</td>'
        f'<td><code>{esc(o.get("label", "research_tip"))}</code></td></tr>'
        for o in items
    ) or '<tr><td colspan="4">Execute prodigy-rank (research)</td></tr>'
    copied = bundle.get('prodigy', {}).get('copied_signals') or []
    copy_rows = ''.join(
        f'<tr><td>{esc(c.get("provider"))}</td><td>{esc(c.get("symbol"))}</td>'
        f'<td>{esc(c.get("signal_id"))}</td></tr>'
        for c in copied
    ) or '<tr><td colspan="3">Nenhuma cópia registrada</td></tr>'
    body = (
        f'<p class="warn">Ranking e cópias são pesquisa — não autorizam ordem.</p>'
        f'<p class="muted">{disclaimer}</p>'
        f'<h2>Ranking (rótulo <code>research_tip</code>)</h2><table><tbody>{rank_rows}</tbody></table>'
        f'<h2>Sinais copiados</h2><table><tbody>{copy_rows}</tbody></table>'
    )
    return _wrap_panel_page(
        title='Prodígio',
        active='prodigy',
        page_title='Prodígio',
        subtitle='Ranking e cópias — somente pesquisa.',
        research_banner=(
            '<aside class="research-banner">Prodígio — pesquisa; não autoriza ordem.</aside>'
        ),
        body=body,
    )


def render_performance_page(perf: dict[str, Any]) -> str:
    label = esc(perf.get('pnl_label') or PERFORMANCE_LABEL_GROSS)
    total = perf.get('total_gross_usd') or perf.get('total_gross_brl_cents') or 'Indisponível'
    strat_rows = ''.join(
        f'<tr><td>{esc(s.get("strategy_key"))}</td><td class="mono">{esc(s.get("gross_usd") or s.get("gross_brl_cents"))}</td>'
        f'<td>{label}</td></tr>'
        for s in perf.get('strategies') or []
    ) or '<tr><td colspan="3">Sem fills confirmados</td></tr>'
    body = (
        f'<p class="warn">Valores rotulados <b>{label}</b> — ordens sem fill não entram.</p>'
        f'<p>Total: <span class="mono">{esc(total)}</span> ({label})</p>'
        '<table><thead><tr><th>Estratégia</th><th>Resultado</th><th>Rótulo</th></tr></thead>'
        f'<tbody>{strat_rows}</tbody></table>'
    )
    return _wrap_panel_page(
        title='Performance',
        active='performance',
        page_title='Performance',
        subtitle='Somente fills confirmados. Live desligado.',
        body=body,
    )
