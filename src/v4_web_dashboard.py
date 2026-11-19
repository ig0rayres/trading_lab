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
import threading
import time
import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError
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
    from .demo_account_gate import demo_market_block_reason
    from . import supervised_adjustment as _supervised
    from . import c2_history_collect
    from . import c2_signal_feed
    from . import prodigy_rank
except ImportError:
    import panel_ops_data as _panel_ops
    import panel_ops_html as _panel_html
    from demo_account_gate import demo_market_block_reason
    import supervised_adjustment as _supervised
    import c2_history_collect
    import c2_signal_feed
    import prodigy_rank

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
        from platform_health import load_health_snapshot

        data['platform_health'] = load_health_snapshot(root)
    except Exception:
        data['platform_health'] = None
    try:
        conn_factory = default_connect if os.environ.get('LEDGER_DATABASE_URL', '').strip() else None
        bundle = _panel_ops.build_panel_bundle(root, conn_factory)
        data['panel_ops'] = bundle
        data['performance_panel'] = bundle.get('performance')
        if isinstance(panel.get('opportunities'), dict) and isinstance(bundle.get('prodigy'), dict):
            bundle['prodigy']['ranking'] = panel['opportunities']
        if data.get('platform_health') is not None:
            bundle['platform_health'] = data['platform_health']
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
    prodigy_surface = panel.get('opportunities') or {}
    opps = prodigy_surface.get('items') or []
    prodigy_disclaimer = esc(prodigy_surface.get('disclaimer') or 'Sugestão de pesquisa — não autoriza ordem.')
    opp_rows = ''.join(
        f'<tr><td>{esc(o.get("provider",""))}</td><td>{esc(o.get("status",""))}</td>'
        f'<td>{esc(o.get("prodigy_score",""))}</td><td>{esc(o.get("label","research_tip"))}</td></tr>'
        for o in opps
    ) or '<tr><td colspan="4">Execute prodigy-rank ou aguarde relatório</td></tr>'
    tb = panel.get('ta_barato_shadow') or {}
    tb_rows = ''.join(
        f'<tr><td>{esc(o.get("market",""))}</td><td>{esc(o.get("symbol",""))}</td>'
        f'<td>{esc(o.get("drop_pct",""))}</td><td>{"sim" if o.get("radar_candidate") else "não"}</td>'
        f'<td>{esc(o.get("label","shadow_suggestion"))}</td></tr>'
        for o in (tb.get('items') or [])
    ) or '<tr><td colspan="5">Execute v4-cycle com --opportunity-input ou aguarde relatório</td></tr>'
    tb_upstream = esc(tb.get('upstream_formula', 'BLOCKED'))
    tb_note = esc(tb.get('local_shadow_note', ''))
    evo = panel.get('continuous_improvement', {}).get('recent') or []
    evo_items = ''.join(
        f'<li><span class="muted">{esc(e.get("at",""))}</span> '
        f'<code>{esc(e.get("label","continuous_improvement"))}</code> — '
        f'{esc(e.get("summary") or e.get("kind") or "—")}</li>'
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
    ph = data.get('platform_health') or {}
    overall = ph.get('overall') or 'unknown'
    comp_rows = ''
    for comp in ph.get('components') or []:
        comp_rows += (
            f'<tr><td>{esc(comp.get("id", ""))}</td>'
            f'<td>{esc(comp.get("status", ""))}</td>'
            f'<td>{esc(comp.get("detail", ""))}</td></tr>'
        )
    if not comp_rows:
        comp_rows = '<tr><td colspan="3">Aguardando primeira checagem automática (v4-ops)</td></tr>'
    platform_block = (
        f'<h2>Plataforma — semáforo</h2>'
        f'<p class="muted">Agregado: <strong>{esc(overall)}</strong> · atualizado em {esc(ph.get("generated_at", "—"))}</p>'
        f'<table><thead><tr><th>Componente</th><th>Status</th><th>Detalhe</th></tr></thead><tbody>{comp_rows}</tbody></table>'
    )
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Trading Lab — Command Panel</title><style>
    :root{{color-scheme:dark}}body{{font:16px system-ui;background:#0c1322;color:#eef3fa;max-width:1040px;margin:auto;padding:40px 20px}}h1{{font-size:32px}}h2{{margin-top:28px;font-size:20px}}.muted,small{{color:#a6b4c5}}.warning{{background:#30251a;border:1px solid #765124;border-radius:12px;padding:14px;margin:20px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}article{{background:#182337;border:1px solid #2c3c56;border-radius:12px;padding:20px;display:flex;flex-direction:column;gap:14px}}strong{{font-size:24px}}footer{{margin-top:32px;color:#a6b4c5}}a{{color:#9bc5fa}}table{{width:100%;border-collapse:collapse;margin-top:10px}}td,th{{border:1px solid #2c3c56;padding:8px;text-align:left}}th{{color:#a6b4c5;font-weight:600}}
    </style></head><body><h1>Trading Lab <span class="muted">/ Command Panel v1</span></h1><p class="muted">Atualizado em {esc(data['generated_at'])} UTC · Somente leitura · MVP-OP ISS-007</p><div class="warning"><b>Não homologado para execução autônoma.</b> Dados parciais, valores brutos sem custos completos e nenhum envio de ordens pelo painel.</div>{platform_block}<p>{health_line}</p><div class="grid">{items}</div><p class="muted">Último ciclo de pesquisa: {esc(cycle)} · Aceitação operacional: {esc(data.get("operational_acceptance_reason","NO"))}</p><h2>Estratégias (catálogo)</h2><table><thead><tr><th>Chave</th><th>Fase</th><th>Paper permitido</th></tr></thead><tbody>{strat_rows}</tbody></table><p class="muted">Promoção de fase: somente operador (fora do painel).</p><h2>Oportunidades Prodígio (sugestão / research)</h2><p class="muted">{prodigy_disclaimer}</p><table><thead><tr><th>Provedor</th><th>Status</th><th>Score</th><th>Rótulo</th></tr></thead><tbody>{opp_rows}</tbody></table><h2>Tá Barato (<code>ta_barato</code>) — sombra / homolog</h2><p class="muted">Upstream ({tb_upstream} @ pin vendor) · {tb_note}</p><table><thead><tr><th>Mercado</th><th>Símbolo</th><th>Queda % (5 barras)</th><th>Radar</th><th>Rótulo</th></tr></thead><tbody>{tb_rows}</tbody></table><p class="muted">Fase catálogo: research — Gate B bloqueia paper até fórmula upstream (G-FORM).</p><h2>Melhoria contínua (sugestão)</h2><ul>{evo_items}</ul><h2>Limitações</h2><ul>{caveats}</ul><footer>API: <a href="/api/status">/api/status</a> (inclui command_panel) · Sem controles de negociação.</footer></body></html>'''


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
    public_markets = []
    for m in markets:
        row = {'market': m['market'], 'operation_on': m['operation_on']}
        block = demo_market_block_reason(m['market'])
        if block:
            row['block_reason'] = block
        public_markets.append(row)
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


def fetch_strategy_state_row(conn, strategy_key):
    with conn.cursor() as cur:
        cur.execute(
            'SELECT id, phase FROM strategy_states '
            'WHERE strategy_key = %s AND deleted_at IS NULL',
            (strategy_key,),
        )
        row = cur.fetchone()
    if not row:
        return None
    return {'id': row[0], 'phase': row[1]}


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


def strategy_parameters_get_payload():
    root = Path(os.environ.get('REPORTS_DIR', '/app/reports'))
    evo = root / 'evolution'
    return {
        'catalog': _supervised.parameter_catalog_public_view(),
        'history': _supervised.list_adjustment_history(evo),
        'overrides': _supervised.load_overrides(evo).get('strategies') or {},
        'execution_authorized': False,
        'paper_allowed': False,
        'orders_sent': 0,
    }


def signals_providers_post(body: dict, connect_factory, root: Path):
    if not isinstance(body, dict):
        return 'reject', 'INVALID_BODY', None
    platform = str(body.get('platform') or '').strip().lower()
    provider_id = str(body.get('provider_id') or '').strip()
    action = str(body.get('action') or '').strip().lower()
    if not platform or not provider_id or action not in ('approve', 'reject'):
        return 'reject', 'INVALID_BODY', None
    if connect_factory is None:
        return 'reject', 'LEDGER_UNAVAILABLE', None
    try:
        result = _panel_ops.upsert_signal_provider_approval(
            connect_factory, platform, provider_id, action
        )
    except ValueError:
        return 'reject', 'INVALID_BODY', None
    except Exception as exc:
        err = str(exc).lower()
        if 'undefinedtable' in err or 'signal_provider_approvals' in err:
            return 'reject', 'LEDGER_UNAVAILABLE', None
        if 'not set' in err or 'ledger_database_url' in err:
            return 'reject', 'LEDGER_UNAVAILABLE', None
        raise
    _ = root
    return 'ok', None, {**result, 'execution_authorized': False, 'orders_sent': 0}


def strategy_parameters_post(path: str, body: dict, connect_factory):
    root = Path(os.environ.get('REPORTS_DIR', '/app/reports')) / 'evolution'
    audit_hooks = {
        'conn_factory': connect_factory,
        'insert_trigger_change': insert_trigger_change,
        'fetch_strategy_row': fetch_strategy_state_row,
    }
    if path == '/api/strategy-parameters/propose':
        required = ('strategy_key', 'parameter', 'proposed_value', 'reason')
        if not isinstance(body, dict) or any(k not in body for k in required):
            return 'reject', 'INVALID_BODY', None
        row = _supervised.propose_adjustment(
            strategy_key=body['strategy_key'],
            parameter=body['parameter'],
            proposed_value=body['proposed_value'],
            reason=str(body['reason']),
            root=root,
        )
        return 'ok', None, row
    if path == '/api/strategy-parameters/apply':
        pid = body.get('proposal_id') if isinstance(body, dict) else None
        if not pid:
            return 'reject', 'INVALID_BODY', None
        updated, code = _supervised.apply_proposal(str(pid), root=root, **audit_hooks)
        if code:
            return 'reject', code, None
        return 'ok', None, updated
    if path == '/api/strategy-parameters/undo':
        aid = body.get('applied_id') if isinstance(body, dict) else None
        if not aid:
            return 'reject', 'INVALID_BODY', None
        reason = str(body.get('reason') or 'operator_undo')
        updated, code = _supervised.undo_adjustment(str(aid), reason=reason, root=root, **audit_hooks)
        if code:
            return 'reject', code, None
        return 'ok', None, updated
    return 'not_found', None, None


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
        if data.get('platform_health') is not None:
            bundle = {**bundle, 'platform_health': data['platform_health']}
        page = _panel_html.render_central_page(bundle, triggers)
    elif path == '/sinais':
        page = _panel_html.render_signals_page(bundle)
    elif path == '/estrategias':
        page = _panel_html.render_strategies_page(bundle)
    elif path == '/analise-google':
        page = _panel_html.render_analise_google_page(bundle)
    elif path == '/prodigy':
        cp = data.get('command_panel') or {}
        page = _panel_html.render_prodigy_page(bundle, cp.get('opportunities') or {})
    elif path == '/performance':
        page = _panel_html.render_performance_page(bundle.get('performance') or {})
    elif path == '/ordens':
        page = _panel_html.render_orders_page(bundle)
    elif path == '/historico':
        page = _panel_html.render_history_page(bundle)
    else:
        handler.send_error(404)
        return
    send_html_page(handler, page)


def _panel_ops_bundle(snapshot: dict) -> dict:
    bundle = snapshot.get('panel_ops') if isinstance(snapshot, dict) else None
    if not isinstance(bundle, dict) or bundle.get('status') == 'PANEL_OPS_UNAVAILABLE':
        return {}
    return bundle


def serve_panel_json(handler, root: Path, path: str):
    try:
        data = build_snapshot(root)
    except Exception:
        data = {}
    bundle = _panel_ops_bundle(data)
    if path == '/api/signals':
        payload = {
            'signals': bundle.get('signals') or [],
            'copy': bundle.get('copy') if isinstance(bundle.get('copy'), dict) else {},
        }
    elif path == '/api/orders':
        payload = {'orders': bundle.get('open_orders') or []}
    elif path == '/api/history':
        payload = {'history': bundle.get('order_history') or []}
    elif path == '/api/estrategias':
        catalog = bundle.get('strategy_catalog') or {}
        payload = {'strategies': catalog.get('strategies') or []}
    elif path == '/api/analise-google':
        block = bundle.get('timesfm') if isinstance(bundle.get('timesfm'), dict) else {}
        payload = {
            'timesfm_status': block.get('timesfm_status', 'UNAVAILABLE'),
            'tips': block.get('tips') or [],
            'operator_reason': block.get('operator_reason'),
            'execution_authorized': False,
            'paper_allowed': False,
        }
        if block.get('note') is not None:
            payload['note'] = block.get('note')
    elif path == '/api/performance':
        payload = data.get('performance_panel') if isinstance(data, dict) else {}
        payload = payload or {}
    else:
        handler.send_error(404)
        return
    send_json_response(handler, 200, payload)


_LIVE_CRITERIA_SOURCES = ('collective2', 'prodigy', 'tradingview')
_LIVE_CRITERIA_COOLDOWN_SEC = 30
_LAST_LIVE_CRITERIA_REFRESH_MONO: float | None = None
_LIVE_CRITERIA_REFRESH_LOCK = threading.Lock()
_C2_API4_HTTP_FETCH = c2_history_collect.fetch
# Wall-clock cap for closed-trades collect within one POST (seconds; not Feature 4 thresholds).
_C2_CLOSED_TRADES_COLLECT_BUDGET_SEC = 35.0


def _live_criteria_cooldown_wait(now_mono: float) -> int:
    if _LAST_LIVE_CRITERIA_REFRESH_MONO is None:
        return 0
    elapsed = now_mono - _LAST_LIVE_CRITERIA_REFRESH_MONO
    if elapsed >= _LIVE_CRITERIA_COOLDOWN_SEC:
        return 0
    return max(1, int(_LIVE_CRITERIA_COOLDOWN_SEC - elapsed) + 1)


def _resolve_live_refresh_sources(body: dict) -> list[str]:
    if not isinstance(body, dict):
        return list(_LIVE_CRITERIA_SOURCES)
    raw = body.get('sources')
    if raw is None:
        return list(_LIVE_CRITERIA_SOURCES)
    if not isinstance(raw, list):
        return list(_LIVE_CRITERIA_SOURCES)
    picked = [s for s in raw if s in _LIVE_CRITERIA_SOURCES]
    return picked or list(_LIVE_CRITERIA_SOURCES)


def _merged_c2_strategy_ids(root: Path) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for pid in _panel_ops.load_c2_paper_copy_approved_ids(root):
        if pid not in seen:
            seen.add(pid)
            merged.append(pid)
    for pid in _panel_ops.discover_c2_strategy_ids_from_raw(root):
        if pid not in seen:
            seen.add(pid)
            merged.append(pid)
    for row in _panel_ops._load_c2_research_candidates(root):
        pid = str(row.get('provider_id') or '').strip()
        if pid and pid not in seen:
            seen.add(pid)
            merged.append(pid)
    return sorted(merged, key=int)


def _write_c2_history_dataset(out_dir: Path, sid: str, dataset: str, raw: dict) -> str:
    out_dir.mkdir(parents=True, exist_ok=True)
    name = f'{sid}_{dataset}.json'
    payload = {
        'strategy_id': sid,
        'dataset': dataset,
        'fetched_at_utc': datetime.now(timezone.utc).isoformat(),
        'raw': raw,
    }
    (out_dir / name).write_text(json.dumps(payload, indent=2), encoding='utf-8')
    return name


def _panel_c2_history_collect(strategy_ids, key, out_dir, opener=None, **kwargs):
    del opener, kwargs
    root = Path(out_dir)
    written: list[str] = []
    for sid in sorted({str(x) for x in strategy_ids}):
        sid_int = int(sid)
        for dataset, api_path in c2_history_collect.PATHS.items():
            try:
                raw = _C2_API4_HTTP_FETCH(api_path, {'StrategyId': sid_int, 'CommissionPlan': '0'}, key)
            except (OSError, ValueError, TypeError, KeyError):
                continue
            written.append(_write_c2_history_dataset(root, sid, dataset, raw))
    return {'status': 'ok', 'written': written}


def _collective2_closed_trades_partial_issue(exc: BaseException) -> str:
    label = type(exc).__name__
    code = getattr(exc, 'code', None)
    if code is not None:
        return f'collective2_closed_trades_partial_failed:{label}:{code}'
    return f'collective2_closed_trades_partial_failed:{label}'


def _c2_closed_trades_pending_from_refresh(root: Path) -> list[str]:
    record = _panel_ops.load_candidates_refresh(root)
    if not isinstance(record, dict):
        return []
    raw = record.get('c2_closed_trades_pending_ids') or []
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for item in raw:
        s = str(item).strip()
        if s.isdigit():
            out.append(s)
    return sorted(set(out), key=int)


def _panel_c2_closed_trades_collect(
    strategy_ids,
    key,
    out_dir,
    issues: list[str] | None = None,
    *,
    deadline: float | None = None,
    opener=None,
    **kwargs,
):
    del kwargs
    root = Path(out_dir)
    api_path = c2_history_collect.PATHS['closed_trades']
    written: list[str] = []
    pending: list[str] = []
    partial_labels: set[str] = set()
    if deadline is None and _C2_CLOSED_TRADES_COLLECT_BUDGET_SEC > 0:
        deadline = time.monotonic() + _C2_CLOSED_TRADES_COLLECT_BUDGET_SEC
    bound_fetch = c2_history_collect.fetch
    sorted_ids = sorted({str(x) for x in strategy_ids})
    budget_stopped = False
    for idx, sid in enumerate(sorted_ids):
        if deadline is not None and time.monotonic() >= deadline:
            budget_stopped = True
            pending.extend(sorted_ids[idx:])
            break
        try:
            if bound_fetch is _C2_API4_HTTP_FETCH:
                raw = _C2_API4_HTTP_FETCH(
                    api_path,
                    {'StrategyId': int(sid), 'CommissionPlan': '0'},
                    key,
                )
            else:
                panel = bound_fetch(
                    [sid],
                    key,
                    out_dir,
                    opener=opener,
                    path=api_path,
                )
                if isinstance(panel, dict) and panel.get('written'):
                    written.extend(str(x) for x in panel['written'])
                    continue
                raw = panel.get('raw') if isinstance(panel, dict) else panel
                if raw is None:
                    raise ValueError('closed_trades_fetch_empty')
        except (OSError, ValueError, TypeError, KeyError) as exc:
            if issues is not None:
                label = _collective2_closed_trades_partial_issue(exc)
                if label not in partial_labels:
                    partial_labels.add(label)
                    issues.append(label)
            continue
        written.append(_write_c2_history_dataset(root, sid, 'closed_trades', raw))
    if budget_stopped and issues is not None:
        budget_issue = 'collective2_closed_trades_partial_failed:time_budget'
        if budget_issue not in partial_labels:
            issues.append(budget_issue)
    if pending:
        pending = sorted(set(pending), key=int)
    return {'status': 'ok', 'written': written, 'pending_ids': pending}


def _invoke_c2_history_collect(strategy_ids, key, out_dir, opener=None, **kwargs):
    bound_fetch = c2_history_collect.fetch
    if bound_fetch is _C2_API4_HTTP_FETCH:
        return _panel_c2_history_collect(strategy_ids, key, out_dir, opener=opener, **kwargs)
    return bound_fetch(strategy_ids, key, out_dir, opener=opener, **kwargs)


def _invoke_c2_closed_trades_collect(
    strategy_ids,
    key,
    out_dir,
    issues: list[str] | None = None,
    opener=None,
    **kwargs,
):
    deadline = kwargs.pop('deadline', None)
    return _panel_c2_closed_trades_collect(
        strategy_ids,
        key,
        out_dir,
        issues,
        deadline=deadline,
        opener=opener,
        **kwargs,
    )


def _c2_search_cursor_from_refresh(root: Path) -> str:
    record = _panel_ops.load_candidates_refresh(root)
    if not isinstance(record, dict):
        return ''
    return str(record.get('c2_search_next_cursor') or '').strip()


def _persist_c2_search_snapshot(root: Path, raw_api: dict) -> None:
    intel = _intelligence_dir(root)
    payload = {
        'dataset': 'search_strategies',
        'fetched_at_utc': datetime.now(timezone.utc).isoformat(),
        'raw': raw_api,
    }
    (intel / 'c2_search_strategies_latest.json').write_text(
        json.dumps(payload, indent=2),
        encoding='utf-8',
    )


def _parse_c2_search_ids(raw_api: dict) -> tuple[list[str], str]:
    results = raw_api.get('Results') or []
    pagination = raw_api.get('Pagination') if isinstance(raw_api.get('Pagination'), dict) else {}
    next_cursor = str(pagination.get('next_cursor') or '').strip()
    ids: list[str] = []
    for row in results:
        if not isinstance(row, dict) or row.get('IsPrivate') is True:
            continue
        sid = row.get('StrategyId')
        if sid is None:
            continue
        try:
            ids.append(str(int(sid)))
        except (TypeError, ValueError):
            continue
    return sorted(set(ids), key=int), next_cursor


def _collective2_search_incomplete_issue(next_cursor: str) -> str:
    if not next_cursor:
        return ''
    return (
        'collective2_search_incomplete:pagination next_cursor present; '
        'click Atualizar again to continue scan'
    )


def _append_collective2_non_numeric_id_issues(root: Path, issues: list[str]) -> None:
    bad = False
    for pid in _panel_ops.load_c2_paper_copy_approved_ids(root):
        if pid and not str(pid).isdigit():
            bad = True
            break
    if not bad:
        for row in _panel_ops._load_c2_research_candidates(root):
            pid = str(row.get('provider_id') or row.get('provider') or '').strip()
            if pid and not pid.isdigit():
                bad = True
                break
    if bad:
        issues.append('collective2_refresh_failed:non_numeric_strategy_id')


def _invoke_c2_search_strategies(key: str, out_dir: Path, cursor: str, opener=None):
    search_path = c2_history_collect.SEARCH_STRATEGIES_PATH
    bound_fetch = c2_history_collect.fetch
    if bound_fetch is _C2_API4_HTTP_FETCH:
        params: dict[str, str] = {}
        if cursor:
            params['Cursor'] = cursor
        raw = bound_fetch(search_path, params, key)
        _persist_c2_search_snapshot(Path(out_dir).parent.parent, raw)
        return _parse_c2_search_ids(raw)
    panel = bound_fetch(
        search_path,
        key,
        out_dir,
        opener=opener,
        path=search_path,
        cursor=cursor,
    )
    if isinstance(panel, dict) and panel.get('strategy_ids') is not None:
        ids = [str(x) for x in panel.get('strategy_ids') or []]
        ncur = str(panel.get('next_cursor') or '').strip()
        return sorted(set(ids), key=int), ncur
    raw = panel.get('raw') if isinstance(panel, dict) else {}
    if isinstance(raw, dict):
        return _parse_c2_search_ids(raw)
    return [], ''


def _intelligence_dir(root: Path) -> Path:
    path = root / 'intelligence'
    path.mkdir(parents=True, exist_ok=True)
    return path


def _providers_raw_dir(root: Path) -> Path:
    return root / 'providers' / 'raw'


def _providers_signals_dir(root: Path) -> Path:
    return root / 'providers' / 'signals'


def _prodigy_rank_has_eligible_rows(rank: dict) -> bool:
    top = rank.get('top_10_research')
    if isinstance(top, list) and top:
        return True
    providers = rank.get('providers')
    return isinstance(providers, list) and bool(providers)


def _persist_prodigy_rank(root: Path, rank: dict) -> None:
    intel = _intelligence_dir(root)
    (intel / 'prodigy-top10-latest.json').write_text(json.dumps(rank, indent=2), encoding='utf-8')


def _ledger_conn_factory(conn_factory):
    return conn_factory if os.environ.get('LEDGER_DATABASE_URL', '').strip() else None


def _live_refresh_prodigy(root: Path, issues: list[str], sources_ok: list[str]) -> None:
    raw_dir = _providers_raw_dir(root)
    try:
        rank = prodigy_rank.calculate(raw_dir)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        issues.append(f'prodigy_rank_failed:{type(exc).__name__}')
        return
    if not _prodigy_rank_has_eligible_rows(rank):
        issues.append(
            'prodigy_raw_missing:reports/providers/raw/{sid}_closed_trades.json',
        )
        return
    _persist_prodigy_rank(root, rank)
    sources_ok.append('prodigy')


def _collective2_active_orders_snapshot_issue(exc: BaseException) -> str:
    label = type(exc).__name__
    code = getattr(exc, 'code', None)
    if code is not None:
        return f'collective2_active_orders_snapshot_failed:{label}:{code}'
    return f'collective2_active_orders_snapshot_failed:{label}'


def _run_collective2_active_orders_snapshot(
    root: Path,
    key: str,
    issues: list[str],
) -> None:
    snap_ids = sorted({int(x) for x in _panel_ops.load_c2_paper_copy_approved_ids(root)})
    if not snap_ids:
        return
    try:
        c2_signal_feed.snapshot(snap_ids, key, _providers_signals_dir(root))
    except (HTTPError, URLError, ValueError, OSError) as exc:
        issues.append(_collective2_active_orders_snapshot_issue(exc))


def _live_refresh_collective2(
    root: Path,
    issues: list[str],
    sources_ok: list[str],
) -> tuple[str, list[str]]:
    key = os.environ.get('C2_API4_KEY', '').strip()
    if not key:
        issues.append('C2_API4_KEY_missing')
        return '', []
    raw_dir = _providers_raw_dir(root)
    _append_collective2_non_numeric_id_issues(root, issues)
    next_cursor = ''
    try:
        cursor = _c2_search_cursor_from_refresh(root)
        scan_ids, next_cursor = _invoke_c2_search_strategies(key, raw_dir, cursor)
        incomplete = _collective2_search_incomplete_issue(next_cursor)
        if incomplete:
            issues.append(incomplete)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        issues.append(f'collective2_refresh_failed:{type(exc).__name__}')
        return '', []
    sources_ok.append('collective2')
    pending_prior = _c2_closed_trades_pending_from_refresh(root)
    collect_ids = sorted(set(pending_prior) | set(scan_ids or []), key=int)
    closed_pending: list[str] = []
    if collect_ids:
        collect_deadline = time.monotonic() + _C2_CLOSED_TRADES_COLLECT_BUDGET_SEC
        result = _invoke_c2_closed_trades_collect(
            collect_ids,
            key,
            raw_dir,
            issues,
            deadline=collect_deadline,
        )
        closed_pending = list(result.get('pending_ids') or [])
    _run_collective2_active_orders_snapshot(root, key, issues)
    return next_cursor, closed_pending


def _live_refresh_tradingview(
    root: Path,
    conn_factory,
    issues: list[str],
    sources_ok: list[str],
) -> None:
    issues.append(
        'tradingview_scan_out:ISS-025 no platform search API; ingested origins only',
    )
    factory = _ledger_conn_factory(conn_factory)
    try:
        bundle = _panel_ops.build_panel_bundle(root, factory)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        issues.append(f'tradingview_refresh_failed:{type(exc).__name__}')
        return
    signals = bundle.get('signals') if isinstance(bundle, dict) else []
    if not isinstance(signals, list):
        signals = []
    _panel_ops._unique_tradingview_origins(signals)
    sources_ok.append('tradingview')


def _live_criteria_job(
    root: Path,
    sources: list[str],
    conn_factory,
) -> tuple[list[str], list[str], list[str], str]:
    issues: list[str] = []
    sources_ok: list[str] = []
    c2_next_cursor = ''
    c2_closed_pending: list[str] = []
    if 'collective2' in sources:
        try:
            c2_next_cursor, c2_closed_pending = _live_refresh_collective2(root, issues, sources_ok)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            issues.append(f'collective2_refresh_failed:{type(exc).__name__}')
    if 'prodigy' in sources:
        _live_refresh_prodigy(root, issues, sources_ok)
    if 'tradingview' in sources:
        try:
            _live_refresh_tradingview(root, conn_factory, issues, sources_ok)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            issues.append(f'tradingview_refresh_failed:{type(exc).__name__}')
    return issues, sources_ok, sources, c2_next_cursor, c2_closed_pending


def serve_signals_candidates_refresh(handler, root: Path, conn_factory=None, body=None):
    global _LAST_LIVE_CRITERIA_REFRESH_MONO
    body = body if isinstance(body, dict) else {}
    with _LIVE_CRITERIA_REFRESH_LOCK:
        wait = _live_criteria_cooldown_wait(time.monotonic())
        if wait:
            send_json_response(
                handler,
                429,
                {
                    'reject_code': 'REFRESH_COOLDOWN',
                    'retry_after_seconds': wait,
                    'mode': 'live_criteria',
                    'message': 'Aguarde antes de um novo refresh de critérios ao vivo.',
                },
            )
            return
        sources = _resolve_live_refresh_sources(body)
        issues, sources_ok, sources_attempted, c2_next_cursor, c2_closed_pending = _live_criteria_job(
            root,
            sources,
            conn_factory,
        )
        factory = _ledger_conn_factory(conn_factory)
        try:
            bundle = _panel_ops.build_panel_bundle(root, factory)
        except (OSError, ValueError, TypeError, KeyError):
            send_json_response(
                handler,
                503,
                {'reject_code': 'PANEL_BUNDLE_UNAVAILABLE', 'mode': 'live_criteria'},
            )
            return
        if bundle.get('status') == 'PANEL_OPS_UNAVAILABLE':
            send_json_response(
                handler,
                503,
                {'reject_code': 'PANEL_OPS_UNAVAILABLE', 'mode': 'live_criteria'},
            )
            return
        refreshed_at = datetime.now(timezone.utc).isoformat()
        status = 'partial' if issues else 'ok'
        refresh_record = {
            'mode': 'live_criteria',
            'status': status,
            'refreshed_at': refreshed_at,
            'sources_attempted': sources_attempted,
            'sources_ok': sources_ok,
            'issues': issues,
            'orders_sent': 0,
            'execution_authorized': False,
        }
        if c2_next_cursor:
            refresh_record['c2_search_next_cursor'] = c2_next_cursor
        if c2_closed_pending:
            refresh_record['c2_closed_trades_pending_ids'] = c2_closed_pending
        else:
            refresh_record['c2_closed_trades_pending_ids'] = []
        _panel_ops.persist_candidates_refresh(root, refresh_record)
        try:
            bundle = _panel_ops.build_panel_bundle(root, factory)
        except (OSError, ValueError, TypeError, KeyError):
            pass
        payload = {
            'status': status,
            'mode': 'live_criteria',
            'refreshed_at': refreshed_at,
            'sources_attempted': sources_attempted,
            'sources_ok': sources_ok,
            'issues': issues,
            'message': 'Critérios ao vivo aplicados no servidor (sem envio de ordem).',
            'execution_authorized': False,
            'orders_sent': 0,
            'signals': bundle.get('signals') or [],
            'copy': bundle.get('copy') if isinstance(bundle.get('copy'), dict) else {},
        }
        _LAST_LIVE_CRITERIA_REFRESH_MONO = time.monotonic()
        send_json_response(handler, 200, payload)


def serve_signals_reload(handler, root: Path, conn_factory=None):
    """Honest refresh (N53): re-read build_panel_bundle from disk only.

    N54 will add POST/job + cooldown; no ranking job in this GET path.
    """
    try:
        factory = conn_factory if os.environ.get('LEDGER_DATABASE_URL', '').strip() else None
        bundle = _panel_ops.build_panel_bundle(root, factory)
    except Exception:
        send_json_response(
            handler,
            503,
            {
                'status': 'error',
                'reload': False,
                'message': 'Não foi possível reler o bundle do painel.',
            },
        )
        return
    if bundle.get('status') == 'PANEL_OPS_UNAVAILABLE':
        send_json_response(
            handler,
            503,
            {
                'status': 'error',
                'reload': False,
                'message': 'Painel indisponível para releitura.',
            },
        )
        return
    payload = {
        'status': 'ok',
        'reload': True,
        'mode': 'disk_reread',
        'message': 'Candidatos relidos a partir do disco (sem cálculo de ranking).',
        'refreshed_at': datetime.now(timezone.utc).isoformat(),
        'execution_authorized': False,
        'orders_sent': 0,
        'signals': bundle.get('signals') or [],
        'copy': bundle.get('copy') if isinstance(bundle.get('copy'), dict) else {},
    }
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
    global _LAST_LIVE_CRITERIA_REFRESH_MONO
    _LAST_LIVE_CRITERIA_REFRESH_MONO = None
    db_connect = connect_factory or default_connect

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlsplit(self.path).path
            if path == '/login':
                serve_login_page(self)
                return
            if path == '/api/signals/reload':
                if operator_session and not operator_session_authorized(self.headers, operator_session):
                    send_empty_response(self, 401)
                    return
                serve_signals_reload(self, root, db_connect)
                return
            if path in (
                '/api/signals',
                '/api/performance',
                '/api/orders',
                '/api/history',
                '/api/estrategias',
                '/api/analise-google',
            ):
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
            if path == '/api/strategy-parameters':
                if not operator_session_authorized(self.headers, operator_session):
                    send_empty_response(self, 401)
                    return
                send_json_response(self, 200, strategy_parameters_get_payload())
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
            if path.startswith('/api/strategy-parameters/'):
                if not operator_session_authorized(self.headers, operator_session):
                    send_empty_response(self, 401)
                    return
                try:
                    body = read_json_body(self)
                except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
                    send_json_response(self, 422, {'reject_code': 'INVALID_BODY'})
                    return
                kind, code, payload = strategy_parameters_post(path, body, db_connect)
                if kind == 'not_found':
                    self.send_error(404)
                    return
                respond_mutation(self, kind, code, payload)
                return
            if path == '/api/signals/providers':
                if not operator_session_authorized(self.headers, operator_session):
                    send_empty_response(self, 401)
                    return
                try:
                    body = read_json_body(self)
                except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
                    send_json_response(self, 422, {'reject_code': 'INVALID_BODY'})
                    return
                kind, code, payload = signals_providers_post(body, db_connect, root)
                if kind == 'reject' and code == 'LEDGER_UNAVAILABLE':
                    send_json_response(self, 503, {'reject_code': code})
                    return
                if kind == 'not_found':
                    self.send_error(404)
                    return
                respond_mutation(self, kind, code, payload)
                return
            if path == '/api/signals/candidates/refresh':
                if not operator_session or not operator_session_authorized(
                    self.headers,
                    operator_session,
                ):
                    send_empty_response(self, 401)
                    return
                try:
                    body = read_json_body(self)
                except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
                    send_json_response(self, 422, {'reject_code': 'INVALID_BODY'})
                    return
                serve_signals_candidates_refresh(self, root, db_connect, body)
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
