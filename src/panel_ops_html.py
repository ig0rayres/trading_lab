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
    '/', '/central', '/sinais', '/prodigy', '/performance', '/ordens', '/historico', '/login',
})

_PANEL_CSS = '''
body{font:16px "IBM Plex Sans",system-ui,sans-serif;margin:0;background:var(--bg,#f3f5f8);color:var(--fg,#1c2430)}
.layout{display:flex;min-height:100vh}.side{width:240px;background:#1a2332;color:#e8eef6;padding:20px}
.side a{color:#e8eef6;text-decoration:none;display:block;padding:10px 0}.main{flex:1;padding:24px}
.card{background:#fff;border:1px solid #d5dee8;border-radius:8px;padding:16px;margin:8px 0}
.muted{color:#5c6b7c}.btn{display:inline-block;padding:10px 16px;border-radius:8px;border:none;cursor:pointer}
.btn-primary{background:#2c4a6e;color:#f7fafc}.btn-danger{background:#8f2d2d;color:#fff}
table{width:100%;border-collapse:collapse}td,th{border:1px solid #d5dee8;padding:8px;text-align:left}
.warn{background:#fff3cd;border:1px solid #e6c48a;padding:12px;border-radius:8px}
.brake-strip{padding:12px 16px;border-radius:8px;margin:8px 0;display:flex;flex-wrap:wrap;
align-items:center;gap:12px;justify-content:space-between;transition:background .2s,color .2s}
.brake-strip--active{background:#7A1218;color:#FFF7F5}
.brake-strip--released{background:#1C4A52;color:#E6F4F4}
.brake-strip__body{flex:1;min-width:200px}
.brake-strip__title{font-size:22px;font-weight:700;margin:0}
.brake-strip__help{font-size:14px;margin:4px 0 0}
.brake-strip__cta{padding:10px 16px;border-radius:8px;cursor:pointer;font:inherit;font-weight:600}
.brake-strip--active .brake-strip__cta{background:#FFF7F5;color:#7A1218;border:none}
.brake-strip--released .brake-strip__cta{background:transparent;color:#FFF7F5;border:2px solid #E6B6B6}
.brake-strip__cta:focus-visible{outline:3px solid #F0C14B;outline-offset:3px}
@media (prefers-reduced-motion:reduce){.brake-strip{transition:none}}
.mono{font-family:"IBM Plex Mono",monospace}
'''


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def render_login_page(*, error: str | None = None) -> str:
    err = f'<p role="alert" class="warn">Informe a senha do protótipo.</p>' if error else ''
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Entrar — Trading Lab</title>
<style>{_PANEL_CSS}</style></head><body><main class="main" style="max-width:420px;margin:40px auto">
<h1>Trading Lab</h1><p class="muted">Central de controle. Conta demo.</p>{err}
<form method="post" action="/api/login"><label>E-mail<input name="email" type="email" placeholder="operador@demo"></label>
<label>Senha<input name="password" type="password" required></label>
<button class="btn btn-primary" type="submit">Entrar</button></form></main></body></html>'''


def _nav(active: str) -> str:
    links = (
        ('central', '/', 'Central'),
        ('sinais', '/sinais', 'Sinais'),
        ('ordens', '/ordens', 'Ordens'),
        ('historico', '/historico', 'Histórico'),
        ('prodigy', '/prodigy', 'Prodígio'),
        ('performance', '/performance', 'Performance'),
    )
    parts = ['<nav class="side"><strong>Trading Lab</strong>']
    for key, href, label in links:
        prefix = '→ ' if key == active else ''
        parts.append(f'<a href="{href}">{prefix}{esc(label)}</a>')
    parts.append('</nav>')
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
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Central</title>
<style>{_PANEL_CSS}</style></head><body><div class="layout">{_nav("central")}<main class="main">
<h1>Central</h1><p class="muted">Conta demo · Live desligado (sem botão)</p>
{brake}
{_platform_health_block(data.get("platform_health"))}
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px">{cards}</div>
<h2>Mercados</h2><table><tbody>{market_rows}</tbody></table>
<h2>Sinais recentes</h2><table><tbody>{sig_rows}</tbody></table>
<p><a href="/sinais">Ver todos os sinais</a></p></main></div>
<script>{_KILL_PATCH_SCRIPT}</script></body></html>'''


def render_orders_page(bundle: dict[str, Any]) -> str:
    rows = ''.join(
        f'<tr><td class="mono">{esc(o.get("client_order_id") or "—")}</td>'
        f'<td>{esc(o.get("symbol"))}</td><td>{esc(o.get("side"))}</td>'
        f'<td>{esc(o.get("status"))}</td><td>{esc(o.get("broker_status") or o.get("paper_status") or "—")}</td>'
        f'<td class="mono">{esc(o.get("remaining_qty") or o.get("entry_qty") or "—")}</td>'
        f'<td>{esc(o.get("strategy_key") or "—")}</td></tr>'
        for o in bundle.get('open_orders') or []
    ) or '<tr><td colspan="7">Nenhuma ordem aberta no paper.</td></tr>'
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Ordens</title>
<style>{_PANEL_CSS}</style></head><body><div class="layout">{_nav("ordens")}<main class="main">
<h1>Ordens abertas</h1><p class="muted">Somente leitura — paper demo. Live desligado.</p>
<table><thead><tr><th>ID cliente</th><th>Ativo</th><th>Lado</th><th>Status</th><th>Corretora</th><th>Qtd rest.</th><th>Estratégia</th></tr></thead>
<tbody>{rows}</tbody></table></main></div></body></html>'''


def render_history_page(bundle: dict[str, Any]) -> str:
    label = esc(PERFORMANCE_LABEL_GROSS)
    rows = ''.join(
        f'<tr><td class="mono">{esc(h.get("client_order_id") or "—")}</td>'
        f'<td>{esc(h.get("symbol"))}</td><td>{esc(h.get("side"))}</td>'
        f'<td class="mono">{esc(h.get("realized_gross_pnl_usd") or "—")}</td>'
        f'<td>{label}</td><td>{esc(h.get("strategy_key") or "—")}</td></tr>'
        for h in bundle.get('order_history') or []
    ) or '<tr><td colspan="6">Nenhum fill confirmado no histórico.</td></tr>'
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Histórico</title>
<style>{_PANEL_CSS}</style></head><body><div class="layout">{_nav("historico")}<main class="main">
<h1>Histórico de fills</h1><p class="muted">Apenas fills confirmados — fila e HTTP 200 não entram.</p>
<table><thead><tr><th>ID cliente</th><th>Ativo</th><th>Lado</th><th>Resultado</th><th>Rótulo</th><th>Estratégia</th></tr></thead>
<tbody>{rows}</tbody></table></main></div></body></html>'''


def render_signals_page(bundle: dict[str, Any]) -> str:
    rows = ''.join(
        f'<tr><td class="mono">{esc(s.get("received_at") or "—")}</td>'
        f'<td>{esc(s.get("origin"))}</td><td>{esc(s.get("symbol"))}</td>'
        f'<td>{esc(s.get("market"))}</td><td>{esc(s.get("destination"))}</td>'
        f'<td>{esc(s.get("reject_reason") or "—")}</td></tr>'
        for s in bundle.get('signals') or []
    ) or '<tr><td colspan="6">Nenhum sinal neste destino.</td></tr>'
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Sinais</title>
<style>{_PANEL_CSS}</style></head><body><div class="layout">{_nav("sinais")}<main class="main">
<h1>Sinais</h1><p class="muted">Não é fill — auditoria de destino e motivo.</p>
<table><thead><tr><th>Hora</th><th>Origem</th><th>Ativo</th><th>Mercado</th><th>Destino</th><th>Motivo</th></tr></thead>
<tbody>{rows}</tbody></table></main></div></body></html>'''


def render_prodigy_page(bundle: dict[str, Any], opportunities: dict[str, Any]) -> str:
    items = (opportunities or {}).get('items') or []
    disclaimer = esc((opportunities or {}).get('disclaimer') or 'Sugestão de pesquisa — não autoriza ordem.')
    rank_rows = ''.join(
        f'<tr><td>{esc(o.get("provider"))}</td><td>{esc(o.get("status"))}</td>'
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
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Prodígio</title>
<style>{_PANEL_CSS}</style></head><body><div class="layout">{_nav("prodigy")}<main class="main">
<h1>Prodígio</h1><p class="warn">Ranking e cópias são pesquisa — não autorizam ordem.</p>
<p class="muted">{disclaimer}</p>
<h2>Ranking (rótulo <code>research_tip</code>)</h2><table><tbody>{rank_rows}</tbody></table>
<h2>Sinais copiados</h2><table><tbody>{copy_rows}</tbody></table></main></div></body></html>'''


def render_performance_page(perf: dict[str, Any]) -> str:
    label = esc(perf.get('pnl_label') or PERFORMANCE_LABEL_GROSS)
    total = perf.get('total_gross_usd') or perf.get('total_gross_brl_cents') or 'Indisponível'
    strat_rows = ''.join(
        f'<tr><td>{esc(s.get("strategy_key"))}</td><td class="mono">{esc(s.get("gross_usd") or s.get("gross_brl_cents"))}</td>'
        f'<td>{label}</td></tr>'
        for s in perf.get('strategies') or []
    ) or '<tr><td colspan="3">Sem fills confirmados</td></tr>'
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Performance</title>
<style>{_PANEL_CSS}</style></head><body><div class="layout">{_nav("performance")}<main class="main">
<h1>Performance</h1><p class="warn">Valores rotulados <b>{label}</b> — ordens sem fill não entram.</p>
<p>Total: <span class="mono">{esc(total)}</span> ({label})</p>
<table><thead><tr><th>Estratégia</th><th>Resultado</th><th>Rótulo</th></tr></thead><tbody>{strat_rows}</tbody></table>
</main></div></body></html>'''
