"""Read-only dashboard for persisted research and Paper observations.

This service NEVER imports broker order submission code. Bind to loopback by default;
use an authenticated reverse proxy before exposing it publicly.
"""
import argparse
import cgi
import hmac
import hashlib
import html
import json
import os
import re
import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from urllib.parse import parse_qs, urlsplit, unquote

try:
    from .strategy_catalog import NEVER_PAPER_KEYS, PAPER_PHASES
    from .trading_dashboard_data import summary
except ImportError:
    from strategy_catalog import NEVER_PAPER_KEYS, PAPER_PHASES
    from trading_dashboard_data import summary

try:
    from . import ledger_store as _ledger_store
except ImportError:
    import ledger_store as _ledger_store

try:
    from . import panel_ops_data as _panel_ops
    from . import panel_ops_html as _panel_html
except ImportError:
    import panel_ops_data as _panel_ops
    import panel_ops_html as _panel_html

MODULES = ('market', 'news', 'signals', 'risk', 'paper', 'reconciliation')

VALID_MARKETS = frozenset({'B3_EQUITY', 'CRYPTO', 'FOREX'})
VALID_PHASES = frozenset({'research', 'shadow', 'paper_limited', 'paper_validated'})
TRIGGER_PATCH_FIELDS = frozenset({
    'kill_switch_on', 'demo_operation_on', 'capital_cents', 'max_risk_per_trade_cents',
    'max_open_positions', 'max_aggregate_risk_cents', 'max_daily_loss_cents',
    'max_weekly_loss_cents', 'prodigy_risk_cents',
})
INTEGER_PATCH_FIELDS = frozenset({
    'capital_cents', 'max_risk_per_trade_cents', 'max_open_positions',
    'max_aggregate_risk_cents', 'max_daily_loss_cents', 'max_weekly_loss_cents',
    'prodigy_risk_cents',
})
CONTROL_FLAG_RESPONSE_FIELDS = tuple(TRIGGER_PATCH_FIELDS)
_LIVE_FIELD_RE = re.compile(r'live[_ ]?trading', re.I)


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
    panel = data.get('command_panel') or {}
    health = panel.get('financial_health') or {}
    fills = int(health.get('paper_fills_recorded') or 0)
    closed_pnl_rows = int(data.get('closed_orders_with_pnl') or 0)
    # Ledger fills alone are not homologation (CI DB may contain rows unrelated to this snapshot root).
    data['operational_acceptance'] = fills > 0 and closed_pnl_rows > 0
    if not data['operational_acceptance']:
        data['operational_acceptance_reason'] = 'NO_OPERATOR_HOMOLOGATION_EVIDENCE'
    else:
        data['operational_acceptance_reason'] = 'LEDGER_FILLS_AND_CLOSED_SNAPSHOTS_PRESENT'
    data['command_panel'] = panel
    try:
        conn_factory = default_connect if os.environ.get('LEDGER_DATABASE_URL', '').strip() else None
        bundle = _panel_ops.build_panel_bundle(root, conn_factory)
        data['panel_ops'] = bundle
        data['performance_panel'] = bundle.get('performance')
        if isinstance(panel.get('opportunities'), dict) and isinstance(bundle.get('prodigy'), dict):
            bundle['prodigy']['ranking'] = panel['opportunities']
    except Exception:
        data['panel_ops'] = {'status': 'PANEL_OPS_UNAVAILABLE'}
        data['performance_panel'] = None
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
    panel = data.get('command_panel') or {}
    strategies = panel.get('strategy_catalog', {}).get('strategies') or []
    strat_rows = ''.join(
        f'<tr><td>{esc(s.get("strategy_key",""))}</td><td>{esc(s.get("phase",""))}</td>'
        f'<td>{"sim" if s.get("paper_allowed") else "não"}</td></tr>'
        for s in strategies
    ) or '<tr><td colspan="3">Catálogo indisponível (ledger)</td></tr>'
    opps = panel.get('opportunities', {}).get('items') or []
    opp_rows = ''.join(
        f'<tr><td>{esc(o.get("provider",""))}</td><td>{esc(o.get("status",""))}</td>'
        f'<td>{esc(o.get("prodigy_score",""))}</td></tr>'
        for o in opps
    ) or '<tr><td colspan="3">Execute prodigy-rank ou aguarde relatório</td></tr>'
    evo = panel.get('continuous_improvement', {}).get('recent') or []
    evo_items = ''.join(
        f'<li><span class="muted">{esc(e.get("at",""))}</span> — {esc(e.get("summary") or e.get("kind") or "—")}</li>'
        for e in evo
    ) or '<li>Nenhum evento em evolution/decisions.jsonl</li>'
    health = panel.get('financial_health') or {}
    health_line = (
        f'Ledger: {"conectado" if health.get("ledger_connected") else "indisponível"} · '
        f'Fills registrados: {esc(health.get("paper_fills_recorded", 0))} · '
        f'Fila queued_intent: {esc(health.get("paper_queued_intent", 0))}'
    )
    if health.get('queued_is_not_fill'):
        health_line += ' · <b>queued ≠ fill</b>'
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Trading Lab — Command Panel</title><style>
    :root{{color-scheme:dark}}body{{font:16px system-ui;background:#0c1322;color:#eef3fa;max-width:1040px;margin:auto;padding:40px 20px}}h1{{font-size:32px}}h2{{margin-top:28px;font-size:20px}}.muted,small{{color:#a6b4c5}}.warning{{background:#30251a;border:1px solid #765124;border-radius:12px;padding:14px;margin:20px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}article{{background:#182337;border:1px solid #2c3c56;border-radius:12px;padding:20px;display:flex;flex-direction:column;gap:14px}}strong{{font-size:24px}}footer{{margin-top:32px;color:#a6b4c5}}a{{color:#9bc5fa}}table{{width:100%;border-collapse:collapse;margin-top:10px}}td,th{{border:1px solid #2c3c56;padding:8px;text-align:left}}th{{color:#a6b4c5;font-weight:600}}
    </style></head><body><h1>Trading Lab <span class="muted">/ Command Panel v1</span></h1><p class="muted">Atualizado em {esc(data['generated_at'])} UTC · Somente leitura · MVP-OP ISS-007</p><div class="warning"><b>Não homologado para execução autônoma.</b> Dados parciais, valores brutos sem custos completos e nenhum envio de ordens pelo painel.</div><p>{health_line}</p><div class="grid">{items}</div><p class="muted">Último ciclo de pesquisa: {esc(cycle)} · Aceitação operacional: {esc(data.get("operational_acceptance_reason","NO"))}</p><h2>Estratégias (catálogo)</h2><table><thead><tr><th>Chave</th><th>Fase</th><th>Paper permitido</th></tr></thead><tbody>{strat_rows}</tbody></table><p class="muted">Promoção de fase: somente operador (fora do painel).</p><h2>Oportunidades Prodígio (research)</h2><table><thead><tr><th>Provedor</th><th>Status</th><th>Score</th></tr></thead><tbody>{opp_rows}</tbody></table><h2>Melhoria contínua</h2><ul>{evo_items}</ul><h2>Limitações</h2><ul>{caveats}</ul><footer>API: <a href="/api/status">/api/status</a> (inclui command_panel) · Sem controles de negociação.</footer></body></html>'''


def default_connect():
    return _ledger_store.connect()


def cookie_value(cookie_header, name):
    if not cookie_header:
        return None
    prefix = name + '='
    for part in cookie_header.split(';'):
        piece = part.strip()
        if piece.startswith(prefix):
            return piece[len(prefix):]
    return None


def operator_session_authorized(headers, operator_session):
    if not operator_session:
        return False
    raw = cookie_value(headers.get('Cookie'), 'trading_lab_session')
    if raw is None:
        return False
    return hmac.compare_digest(raw, operator_session)


def bearer_authorized(headers, token):
    if token is None:
        return True
    provided = headers.get('Authorization', '')
    expected = 'Bearer ' + token
    return hmac.compare_digest(provided, expected)


def audit_value(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return 'true' if value else 'false'
    return str(value)


def insert_trigger_change(conn, *, target_table, target_id, field_name, old_value, new_value):
    now = datetime.now(timezone.utc)
    _ledger_store.insert_row(conn, 'trigger_changes', {
        'id': str(uuid.uuid4()),
        'target_table': target_table,
        'target_id': str(target_id),
        'field_name': field_name,
        'old_value': audit_value(old_value),
        'new_value': audit_value(new_value),
        'changed_at': now,
        'created_at': now,
        'updated_at': now,
    })


def row_to_control_flags(row):
    return {name: row[name] for name in CONTROL_FLAG_RESPONSE_FIELDS}


def fetch_control_flags_row(conn):
    with conn.cursor() as cur:
        cur.execute(
            'SELECT id, ' + ', '.join(CONTROL_FLAG_RESPONSE_FIELDS)
            + ' FROM control_flags WHERE deleted_at IS NULL ORDER BY created_at DESC LIMIT 1'
        )
        row = cur.fetchone()
    if not row:
        return None
    names = ('id',) + CONTROL_FLAG_RESPONSE_FIELDS
    return dict(zip(names, row))


def fetch_market_control_rows(conn):
    with conn.cursor() as cur:
        cur.execute(
            'SELECT id, market, operation_on FROM market_controls '
            'WHERE deleted_at IS NULL AND market = ANY(%s) ORDER BY market',
            (list(VALID_MARKETS),),
        )
        rows = cur.fetchall()
    return [
        {'id': r[0], 'market': r[1], 'operation_on': r[2]}
        for r in rows
    ]


def load_trigger_snapshot(conn):
    flags = fetch_control_flags_row(conn)
    if flags is None:
        raise LookupError('NO_CONTROL_FLAGS')
    markets = fetch_market_control_rows(conn)
    public_flags = row_to_control_flags(flags)
    public_markets = [{'market': m['market'], 'operation_on': m['operation_on']} for m in markets]
    return {'control_flags': public_flags, 'market_controls': public_markets}


def reject_live_field_names(body):
    if not isinstance(body, dict):
        return False
    for key in body:
        if _LIVE_FIELD_RE.search(key.replace('_', ' ')):
            return True
    return False


def known_trigger_patch_keys(body):
    if not isinstance(body, dict):
        return []
    return [key for key in body if key in TRIGGER_PATCH_FIELDS]


def validate_trigger_patch(body):
    if not isinstance(body, dict):
        return 'INVALID_BODY'
    if reject_live_field_names(body):
        return 'LIVE_TRADING_FIELD_FORBIDDEN'
    keys = known_trigger_patch_keys(body)
    if not keys:
        return 'EMPTY_PATCH'
    for key in keys:
        value = body[key]
        if key in INTEGER_PATCH_FIELDS:
            if not isinstance(value, int) or isinstance(value, bool):
                return 'INVALID_FIELD'
            if value < 1:
                return 'BELOW_MINIMUM'
        elif key in ('kill_switch_on', 'demo_operation_on'):
            if not isinstance(value, bool):
                return 'INVALID_FIELD'
    return None


def apply_trigger_patch(conn, body):
    err = validate_trigger_patch(body)
    if err:
        return None, err
    row = fetch_control_flags_row(conn)
    if row is None:
        raise LookupError('NO_CONTROL_FLAGS')
    now = datetime.now(timezone.utc)
    row_id = row['id']
    for key in known_trigger_patch_keys(body):
        new_value = body[key]
        old_value = row[key]
        if old_value == new_value:
            continue
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE control_flags SET %s = %%s, updated_at = %%s WHERE id = %%s' % key,
                (new_value, now, row_id),
            )
        insert_trigger_change(
            conn, target_table='control_flags', target_id=row_id,
            field_name=key, old_value=old_value, new_value=new_value,
        )
        row[key] = new_value
    return row_to_control_flags(row), None


def validate_market_patch(market, body):
    if market not in VALID_MARKETS:
        return 'INVALID_MARKET'
    if not isinstance(body, dict) or 'operation_on' not in body:
        return 'INVALID_BODY'
    if not isinstance(body['operation_on'], bool):
        return 'INVALID_FIELD'
    return None


def apply_market_patch(conn, market, body):
    err = validate_market_patch(market, body)
    if err:
        return None, err
    with conn.cursor() as cur:
        cur.execute(
            'SELECT id, operation_on FROM market_controls '
            'WHERE market = %s AND deleted_at IS NULL',
            (market,),
        )
        row = cur.fetchone()
    if not row:
        raise LookupError('NO_MARKET_ROW')
    row_id, old_on = row[0], row[1]
    new_on = body['operation_on']
    if old_on == new_on:
        return {'market': market, 'operation_on': new_on}, None
    now = datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute(
            'UPDATE market_controls SET operation_on = %s, updated_at = %s WHERE id = %s',
            (new_on, now, row_id),
        )
    insert_trigger_change(
        conn, target_table='market_controls', target_id=row_id,
        field_name='operation_on', old_value=old_on, new_value=new_on,
    )
    return {'market': market, 'operation_on': new_on}, None


def validate_strategy_patch(strategy_key, body):
    if not isinstance(body, dict) or 'phase' not in body:
        return 'INVALID_BODY'
    phase = body['phase']
    if phase not in VALID_PHASES:
        return 'INVALID_PHASE'
    if strategy_key in NEVER_PAPER_KEYS and phase in PAPER_PHASES:
        return 'STRATEGY_PAPER_FORBIDDEN'
    return None


def apply_strategy_patch(conn, strategy_key, body):
    err = validate_strategy_patch(strategy_key, body)
    if err:
        return None, err, None
    with conn.cursor() as cur:
        cur.execute(
            'SELECT id, phase FROM strategy_states '
            'WHERE strategy_key = %s AND deleted_at IS NULL',
            (strategy_key,),
        )
        row = cur.fetchone()
    if not row:
        return None, None, 'NOT_FOUND'
    row_id, old_phase = row[0], row[1]
    new_phase = body['phase']
    if old_phase == new_phase:
        return {'strategy_key': strategy_key, 'phase': new_phase}, None, None
    now = datetime.now(timezone.utc)
    with conn.cursor() as cur:
        cur.execute(
            'UPDATE strategy_states SET phase = %s, updated_at = %s WHERE id = %s',
            (new_phase, now, row_id),
        )
    insert_trigger_change(
        conn, target_table='strategy_states', target_id=row_id,
        field_name='phase', old_value=old_phase, new_value=new_phase,
    )
    return {'strategy_key': strategy_key, 'phase': new_phase}, None, None


def run_with_ledger(connect_factory, operation):
    try:
        with connect_factory() as conn:
            result = operation(conn)
            conn.commit()
            return result
    except RuntimeError:
        return 'LEDGER_UNAVAILABLE'
    except LookupError:
        return 'LEDGER_INCOMPLETE'
    except Exception:
        return 'LEDGER_ERROR'


def mutation_outcome(op, connect_factory):
    outcome = run_with_ledger(connect_factory, op)
    if isinstance(outcome, str):
        return 'error', outcome, None
    if outcome[0] == 'missing':
        return 'missing', None, None
    if outcome[0] == 'reject':
        return 'reject', outcome[1], None
    return 'ok', None, outcome[1]


def patch_triggers_op(body):
    def op(conn):
        updated, code = apply_trigger_patch(conn, body)
        if code:
            return ('reject', code)
        return ('ok', updated)
    return op


def patch_market_op(market, body):
    def op(conn):
        updated, code = apply_market_patch(conn, market, body)
        if code:
            return ('reject', code)
        return ('ok', updated)
    return op


def patch_strategy_op(strategy_key, body):
    def op(conn):
        updated, code, missing = apply_strategy_patch(conn, strategy_key, body)
        if missing:
            return ('missing', None)
        if code:
            return ('reject', code)
        return ('ok', updated)
    return op


def send_no_store_headers(handler, status, content_type=None, length=0):
    handler.send_response(status)
    if content_type:
        handler.send_header('Content-Type', content_type)
    handler.send_header('Content-Length', str(length))
    handler.send_header('Cache-Control', 'no-store')
    handler.end_headers()


def send_json_response(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode('utf-8')
    send_no_store_headers(handler, status, 'application/json; charset=utf-8', len(body))
    handler.wfile.write(body)


def send_empty_response(handler, status):
    send_no_store_headers(handler, status, length=0)


def read_json_body(handler):
    length = int(handler.headers.get('Content-Length') or 0)
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    return json.loads(raw.decode('utf-8'))


def respond_mutation(handler, kind, code, payload):
    if kind == 'missing':
        send_empty_response(handler, 404)
        return
    if kind == 'error':
        send_json_response(handler, 500, {'reject_code': code})
        return
    if kind == 'reject':
        send_json_response(handler, 422, {'reject_code': code})
        return
    send_json_response(handler, 200, payload)


def dispatch_patch(path, body, connect_factory):
    if path == '/api/triggers':
        return mutation_outcome(patch_triggers_op(body), connect_factory)
    if path.startswith('/api/markets/'):
        market = unquote(path[len('/api/markets/'):])
        return mutation_outcome(patch_market_op(market, body), connect_factory)
    if path.startswith('/api/strategies/'):
        strategy_key = unquote(path[len('/api/strategies/'):])
        return mutation_outcome(patch_strategy_op(strategy_key, body), connect_factory)
    return 'not_found', None, None


def write_public_security_headers(handler):
    handler.send_header('X-Content-Type-Options', 'nosniff')
    handler.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'")
    handler.send_header('X-Frame-Options', 'DENY')


def write_panel_security_headers(handler):
    handler.send_header('X-Content-Type-Options', 'nosniff')
    handler.send_header(
        'Content-Security-Policy',
        "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'",
    )
    handler.send_header('X-Frame-Options', 'DENY')


def operator_panel_route(path: str) -> bool:
    return path in _panel_html.OPERATOR_PANEL_PATHS


def send_redirect(handler, location: str, *, status: int = HTTPStatus.FOUND):
    body = b''
    handler.send_response(status)
    handler.send_header('Location', location)
    handler.send_header('Content-Length', str(len(body)))
    handler.send_header('Cache-Control', 'no-store')
    write_public_security_headers(handler)
    handler.end_headers()
    handler.wfile.write(body)


def send_html_page(handler, page: str, *, status: int = HTTPStatus.OK):
    body = page.encode('utf-8')
    handler.send_response(status)
    handler.send_header('Content-Type', 'text/html; charset=utf-8')
    handler.send_header('Content-Length', str(len(body)))
    handler.send_header('Cache-Control', 'no-store')
    write_panel_security_headers(handler)
    handler.end_headers()
    handler.wfile.write(body)


def set_operator_session_cookie(handler, operator_session: str):
    handler.send_header(
        'Set-Cookie',
        'trading_lab_session=' + operator_session + '; Path=/; HttpOnly; SameSite=Lax',
    )


def parse_login_payload(handler) -> dict:
    length = int(handler.headers.get('Content-Length') or 0)
    raw = handler.rfile.read(length) if length > 0 else b''
    ctype = (handler.headers.get('Content-Type') or '').split(';')[0].strip().lower()
    if ctype == 'application/json':
        return json.loads(raw.decode('utf-8'))
    if ctype == 'application/x-www-form-urlencoded':
        return {k: v[0] for k, v in parse_qs(raw.decode('utf-8')).items()}
    environ = {'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': ctype, 'CONTENT_LENGTH': str(len(raw))}
    form = cgi.FieldStorage(fp=BytesIO(raw), environ=environ, keep_blank_values=True)
    return {key: form.getvalue(key) for key in form.keys()}


def serve_login_page(handler, *, error: bool = False):
    send_html_page(handler, _panel_html.render_login_page(error='empty' if error else None))


def handle_login_post(handler, operator_session: str | None):
    if not operator_session:
        send_empty_response(handler, 503)
        return
    try:
        payload = parse_login_payload(handler)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError, TypeError):
        send_html_page(handler, _panel_html.render_login_page(error='empty'), status=HTTPStatus.BAD_REQUEST)
        return
    password = str(payload.get('password') or '').strip()
    if not password:
        send_html_page(handler, _panel_html.render_login_page(error='empty'), status=HTTPStatus.BAD_REQUEST)
        return
    handler.send_response(HTTPStatus.SEE_OTHER)
    handler.send_header('Location', '/')
    set_operator_session_cookie(handler, operator_session)
    handler.send_header('Cache-Control', 'no-store')
    write_public_security_headers(handler)
    handler.end_headers()


def load_triggers_for_page(connect_factory):
    outcome = run_with_ledger(connect_factory, load_trigger_snapshot)
    if isinstance(outcome, str):
        return None
    return outcome


def serve_operator_panel(handler, root: Path, path: str, connect_factory):
    data = build_snapshot(root)
    bundle = data.get('panel_ops') or {}
    triggers = load_triggers_for_page(connect_factory)
    if path in ('/', '/central'):
        page = _panel_html.render_central_page(bundle, triggers)
    elif path == '/sinais':
        page = _panel_html.render_signals_page(bundle)
    elif path == '/prodigy':
        cp = data.get('command_panel') or {}
        page = _panel_html.render_prodigy_page(bundle, cp.get('opportunities') or {})
    elif path == '/performance':
        page = _panel_html.render_performance_page(bundle.get('performance') or {})
    else:
        handler.send_error(404)
        return
    send_html_page(handler, page)


def serve_panel_json(handler, root: Path, path: str):
    data = build_snapshot(root)
    if path == '/api/signals':
        payload = {'signals': (data.get('panel_ops') or {}).get('signals') or []}
    elif path == '/api/performance':
        payload = data.get('performance_panel') or {}
    else:
        handler.send_error(404)
        return
    send_json_response(handler, 200, payload)


def serve_public_get(handler, root, token, path):
    if token is not None and not bearer_authorized(handler.headers, token):
        handler.send_response(401)
        handler.send_header('WWW-Authenticate', 'Bearer')
        handler.send_header('Cache-Control', 'no-store')
        handler.send_header('Content-Length', '0')
        handler.end_headers()
        return
    if path not in ('/', '/api/status', '/healthz'):
        handler.send_error(404)
        return
    if path == '/healthz':
        body = b'{"status":"alive","orders_enabled":false}'
        mime = 'application/json; charset=utf-8'
    else:
        try:
            data = build_snapshot(root)
            encoded = json.dumps(data, ensure_ascii=False, allow_nan=False) if path == '/api/status' else render_page(data)
            body = encoded.encode('utf-8')
        except (OSError, ValueError, TypeError, KeyError):
            handler.send_error(503, 'Snapshot unavailable')
            return
        mime = 'application/json; charset=utf-8' if path == '/api/status' else 'text/html; charset=utf-8'
    handler.send_response(200)
    handler.send_header('Content-Type', mime)
    handler.send_header('Content-Length', str(len(body)))
    handler.send_header('Cache-Control', 'no-store')
    write_public_security_headers(handler)
    handler.end_headers()
    handler.wfile.write(body)


def make_handler(root, token=None, operator_session=None, connect_factory=None):
    db_connect = connect_factory or default_connect

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlsplit(self.path).path
            if path == '/login':
                serve_login_page(self)
                return
            if path in ('/api/signals', '/api/performance'):
                if operator_session and not operator_session_authorized(self.headers, operator_session):
                    send_empty_response(self, 401)
                    return
                serve_panel_json(self, root, path)
                return
            if path == '/api/triggers':
                if not operator_session_authorized(self.headers, operator_session):
                    send_empty_response(self, 401)
                    return
                outcome = run_with_ledger(db_connect, load_trigger_snapshot)
                if isinstance(outcome, str):
                    send_json_response(self, 500, {'reject_code': outcome})
                    return
                send_json_response(self, 200, outcome)
                return
            if operator_session and operator_panel_route(path):
                if not operator_session_authorized(self.headers, operator_session):
                    send_redirect(self, '/login')
                    return
                serve_operator_panel(self, root, path, db_connect)
                return
            serve_public_get(self, root, token, path)

        def do_PATCH(self):
            if not operator_session_authorized(self.headers, operator_session):
                send_empty_response(self, 401)
                return
            path = urlsplit(self.path).path
            try:
                body = read_json_body(self)
            except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
                send_json_response(self, 422, {'reject_code': 'INVALID_BODY'})
                return
            kind, code, payload = dispatch_patch(path, body, db_connect)
            if kind == 'not_found':
                self.send_error(404)
                return
            respond_mutation(self, kind, code, payload)

        def do_POST(self):
            path = urlsplit(self.path).path
            if path in ('/api/login', '/login'):
                handle_login_post(self, operator_session)
                return
            self.send_error(405, 'Read only')
    return Handler


def operator_session_from_env(env=None):
    env = env or os.environ
    raw = env.get('DASHBOARD_OPERATOR_SESSION', '')
    if raw is None:
        return None
    value = str(raw).strip()
    return value if value else None


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
    operator_session = operator_session_from_env()
    server = ThreadingHTTPServer(
        (args.host, args.port),
        make_handler(Path(args.root), token, operator_session),
    )
    print(f'Read-only dashboard listening on {args.host}:{args.port}', flush=True)
    server.serve_forever()

if __name__ == '__main__':
    main()
