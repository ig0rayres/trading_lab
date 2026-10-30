"""Read-only dashboard for persisted research and Paper observations.

This service NEVER imports broker order submission code. Bind to loopback by default;
use an authenticated reverse proxy before exposing it publicly.
"""
import argparse
import hmac
import hashlib
import html
import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

try:
    from .trading_dashboard_data import summary
except ImportError:
    from trading_dashboard_data import summary

MODULES = ('market', 'news', 'signals', 'risk', 'paper', 'reconciliation')


def research_overview(root):
    """Summarize only persisted research, never infer trades or verified P&L."""
    root = Path(root)
    folder = root / 'v4' if (root / 'v4').is_dir() else root
    reports = {}
    for name in ('manifest', 'market', 'decisions', 'risk'):
        path = folder / ('v4_' + name + '.json')
        if path.is_symlink() or not path.is_file():
            return {'status': 'INCOMPLETE', 'counts': None}
        try:
            if path.stat().st_size > 5_000_000:
                return {'status': 'UNREADABLE', 'counts': None}
            reports[name] = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, ValueError, TypeError):
            return {'status': 'UNREADABLE', 'counts': None}
    m, market, decisions, risk = (reports[k] for k in ('manifest', 'market', 'decisions', 'risk'))
    # A manifest produced by the current publisher must cryptographically match
    # every component. Older manifests (prior to this feature) remain viewable.
    hashes = m.get('component_sha256') if isinstance(m, dict) else None
    if hashes is not None:
        if not isinstance(hashes, dict) or set(hashes) != {'market', 'decisions', 'risk'}:
            return {'status': 'UNTRUSTED', 'counts': None}
        for name in ('market', 'decisions', 'risk'):
            expected = hashes.get(name)
            if not isinstance(expected, str) or len(expected) != 64:
                return {'status': 'UNTRUSTED', 'counts': None}
            try:
                current = hashlib.sha256((folder / ('v4_' + name + '.json')).read_bytes()).hexdigest()
            except OSError:
                return {'status': 'UNREADABLE', 'counts': None}
            if not hmac.compare_digest(expected, current):
                return {'status': 'INCONSISTENT_CYCLE', 'counts': None}
    if (not isinstance(m, dict) or m.get('schema_version') != 'v4-once-1'
            or m.get('orders_sent') != 0 or m.get('execution_authorized') is not False
            or m.get('automatic_order_submission') is not False
            or not isinstance(market, dict) or not isinstance(market.get('results'), dict)
            or not isinstance(market.get('errors'), dict)
            or not isinstance(decisions, dict) or not isinstance(decisions.get('decisions'), list)
            or decisions.get('orders_sent') != 0 or decisions.get('automatic_order_submission') is not False
            or not isinstance(risk, dict) or not isinstance(risk.get('results'), list)
            or risk.get('orders_sent') != 0 or risk.get('automatic_order_submission') is not False):
        return {'status': 'UNTRUSTED', 'counts': None}
    rows = decisions['decisions']
    if any(not isinstance(row, dict) or row.get('decision') != 'RESEARCH_ONLY'
           or row.get('paper_approved') is not False or row.get('orders_sent') != 0 for row in rows):
        return {'status': 'UNTRUSTED', 'counts': None}
    counts = {'assets_with_data': len(market['results']), 'feed_errors': len(market['errors']),
              'research_signals': len(rows), 'market_candidates': sum(row.get('kind') == 'MARKET_SHADOW' and row.get('candidate') is True for row in rows),
              'news_reviews': sum(row.get('kind') == 'NEWS_REVIEW' for row in rows),
              'external_signals': sum(row.get('kind') == 'EXTERNAL_SIGNAL' for row in rows),
              'risk_previews': len(risk['results'])}
    return {'status': m.get('status', 'UNKNOWN'), 'counts': counts, 'orders_sent': 0,
            'explanation': 'Observações de pesquisa, sem autorização de execução.'}


def build_snapshot(root):
    root = Path(root)
    data = summary(root)
    data['generated_at'] = datetime.now(timezone.utc).isoformat()
    data['execution_state'] = 'READ_ONLY_NO_ORDER_SUBMISSION'
    data['operational_acceptance'] = False
    try:
        from gate_b_risk import kill_switch_active

        data['kill_switch_on'] = kill_switch_active()
    except Exception:
        data['kill_switch_on'] = os.getenv('TRADING_LAB_KILL_SWITCH', '').lower() in ('1', 'true', 'yes', 'on')
    data['modules'] = {name: 'NOT_VERIFIED' for name in MODULES}
    data['research_overview'] = research_overview(root)
    # Never expose a raw manifest status as a trusted cycle. The overview
    # checks every component's integrity and research-only safety invariants.
    # A corrupt/missing component must not appear as a successful run.
    overview = data['research_overview']
    if overview.get('counts') is None:
        data['research_cycle'] = {'status': overview['status'], 'trusted': False}
    else:
        data['research_cycle'] = {
            'status': overview['status'], 'trusted': True,
            'orders_sent': 0,
        }
    # No inference of P&L from research candidates or incomplete brokerage records.
    return data


def render_page(data):
    def esc(value):
        return html.escape(str(value), quote=True)
    cards = [
        ('Ordens monitoradas', data['paper_orders_monitored']),
        ('Posições ainda abertas', data['positions_not_fully_closed']),
        ('Ordens encerradas com resultado bruto', data['closed_orders_with_pnl']),
        ('P&L bruto observado (USD)', data['realized_gross_pnl_usd'] if data['realized_gross_pnl_usd'] is not None else 'Indisponível'),
        ('Eventos webhook', data['journal_events']),
        ('Decisões registradas', data['decision_events']),
    ]
    items = ''.join(f'<article><small>{esc(label)}</small><strong>{esc(value)}</strong></article>' for label, value in cards)
    research = data.get('research_overview', {})
    counts = research.get('counts')
    if counts is not None:
        items += ''.join(f'<article><small>{esc(label)}</small><strong>{esc(counts[key])}</strong></article>' for label, key in (("Ativos com dados (pesquisa)", "assets_with_data"), ("Candidatos Shadow", "market_candidates"), ("Notícias em revisão", "news_reviews"), ("Sinais externos observados", "external_signals"), ("Erros de coleta", "feed_errors")))
    cycle = data.get('research_cycle', {}).get('status', 'NOT_AVAILABLE')
    caveats = ''.join(f'<li>{esc(text)}</li>' for text in data['limitations'])
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Trading Lab — Observação</title><style>
    :root{{color-scheme:dark}}body{{font:16px system-ui;background:#0c1322;color:#eef3fa;max-width:1040px;margin:auto;padding:40px 20px}}h1{{font-size:32px}}.muted,small{{color:#a6b4c5}}.warning{{background:#30251a;border:1px solid #765124;border-radius:12px;padding:14px;margin:20px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}article{{background:#182337;border:1px solid #2c3c56;border-radius:12px;padding:20px;display:flex;flex-direction:column;gap:14px}}strong{{font-size:24px}}footer{{margin-top:32px;color:#a6b4c5}}a{{color:#9bc5fa}}
    </style></head><body><h1>Trading Lab <span class="muted">/ Observação</span></h1><p class="muted">Atualizado em {esc(data['generated_at'])} UTC · Somente leitura</p><div class="warning"><b>Não homologado para execução autônoma.</b> Dados parciais, valores brutos sem custos completos e nenhum envio de ordens.</div><div class="grid">{items}</div><p class="muted">Último ciclo de pesquisa: {esc(cycle)}</p><h2>Limitações</h2><ul>{caveats}</ul><footer>API local: <a href="/api/status">/api/status</a> · Esta interface não contém controles de negociação.</footer></body></html>'''


def make_handler(root, token=None):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if token is not None:
                provided = self.headers.get('Authorization', '')
                expected = 'Bearer ' + token
                if not hmac.compare_digest(provided, expected):
                    self.send_response(401)
                    self.send_header('WWW-Authenticate', 'Bearer')
                    self.send_header('Cache-Control', 'no-store')
                    self.send_header('Content-Length', '0')
                    self.end_headers()
                    return
            path = urlsplit(self.path).path
            if path not in ('/', '/api/status', '/healthz'):
                self.send_error(404)
                return
            if path == '/healthz':
                body = b'{"status":"alive","orders_enabled":false}'
                mime = 'application/json; charset=utf-8'
            else:
                try:
                    data = build_snapshot(root)
                    body = (json.dumps(data, ensure_ascii=False, allow_nan=False) if path == '/api/status' else render_page(data)).encode('utf-8')
                except (OSError, ValueError, TypeError, KeyError):
                    self.send_error(503, 'Snapshot unavailable')
                    return
                mime = 'application/json; charset=utf-8' if path == '/api/status' else 'text/html; charset=utf-8'
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'")
            self.send_header('X-Frame-Options', 'DENY')
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            self.send_error(405, 'Read only')
    return Handler


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--root', default='/app/reports')
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, default=8765)
    args = p.parse_args(argv)
    if os.getenv('LIVE_TRADING_ENABLED', 'false').lower() != 'false':
        raise SystemExit('LIVE_TRADING_ENABLED must be false')
    remote = args.host not in ('127.0.0.1', 'localhost', '::1')
    token = os.getenv('DASHBOARD_BEARER_TOKEN')
    if remote and (os.getenv('DASHBOARD_ALLOW_REMOTE', 'false').lower() != 'true' or not token or len(token) < 32):
        raise SystemExit('Remote binding requires explicit enablement and a bearer token of at least 32 characters')
    server = ThreadingHTTPServer((args.host, args.port), make_handler(Path(args.root), token))
    print(f'Read-only dashboard listening on {args.host}:{args.port}', flush=True)
    server.serve_forever()

if __name__ == '__main__':
    main()
