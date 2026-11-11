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
    '/', '/central', '/sinais', '/prodigy', '/performance', '/login',
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
        ('prodigy', '/prodigy', 'Prodígio'),
        ('performance', '/performance', 'Performance'),
    )
    parts = ['<nav class="side"><strong>Trading Lab</strong>']
    for key, href, label in links:
        prefix = '→ ' if key == active else ''
        parts.append(f'<a href="{href}">{prefix}{esc(label)}</a>')
    parts.append('</nav>')
    return ''.join(parts)


def render_central_page(data: dict[str, Any], triggers: dict[str, Any] | None) -> str:
    flags = (triggers or {}).get('control_flags') or {}
    markets = (triggers or {}).get('market_controls') or []
    kill = flags.get('kill_switch_on')
    status = 'Parada geral ligada' if kill else 'Operando'
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
<h1>Central</h1><p class="muted">Conta demo · {esc(status)} · Live desligado (sem botão)</p>
<div class="warn"><b>Parada geral</b> — alterações gravam histórico append-only.
<button class="btn btn-danger" id="kill-on">Ligar parada</button>
<button class="btn" id="kill-off">Desligar parada</button></div>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px">{cards}</div>
<h2>Mercados</h2><table><tbody>{market_rows}</tbody></table>
<h2>Sinais recentes</h2><table><tbody>{sig_rows}</tbody></table>
<p><a href="/sinais">Ver todos os sinais</a></p></main></div>
<script>
async function patchKill(on){{await fetch('/api/triggers',{{method:'PATCH',headers:{{'Content-Type':'application/json'}},
credentials:'same-origin',body:JSON.stringify({{kill_switch_on:on}})}});location.reload();}}
document.getElementById('kill-on').onclick=()=>patchKill(true);
document.getElementById('kill-off').onclick=()=>patchKill(false);
</script></body></html>'''


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
    rank_rows = ''.join(
        f'<tr><td>{esc(o.get("provider"))}</td><td>{esc(o.get("status"))}</td>'
        f'<td class="mono">{esc(o.get("prodigy_score"))}</td></tr>'
        for o in items
    ) or '<tr><td colspan="3">Execute prodigy-rank (research)</td></tr>'
    copied = bundle.get('prodigy', {}).get('copied_signals') or []
    copy_rows = ''.join(
        f'<tr><td>{esc(c.get("provider"))}</td><td>{esc(c.get("symbol"))}</td>'
        f'<td>{esc(c.get("signal_id"))}</td></tr>'
        for c in copied
    ) or '<tr><td colspan="3">Nenhuma cópia registrada</td></tr>'
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Prodígio</title>
<style>{_PANEL_CSS}</style></head><body><div class="layout">{_nav("prodigy")}<main class="main">
<h1>Prodígio</h1><p class="warn">Ranking e cópias são pesquisa — não autorizam ordem.</p>
<h2>Ranking</h2><table><tbody>{rank_rows}</tbody></table>
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
