import json
import os
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from http.server import ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen

from gate_b_risk import evaluate_signed_signal
from panel_ops_html import render_central_page
from panel_ops_data import (
    PERFORMANCE_LABEL_GROSS,
    PREAPPROVAL_METRICS_LABEL,
    blocked_context,
    build_panel_bundle,
    build_preapproval_queue,
    load_c2_paper_copy_approved_ids,
    load_panel_signals,
    performance_from_snapshots,
    resolve_c2_paper_copy_approved_ids,
    signal_destination,
    upsert_signal_provider_approval,
)
from v4_web_dashboard import build_snapshot, make_handler


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _patch(url, body, *, session=None, method='PATCH'):
    headers = {'Content-Type': 'application/json'}
    if session:
        headers['Cookie'] = 'trading_lab_session=' + session
    return Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method=method)


def _get(url, *, session=None):
    headers = {}
    if session:
        headers['Cookie'] = 'trading_lab_session=' + session
    return Request(url, headers=headers)


def _post(url, body, *, session=None):
    headers = {'Content-Type': 'application/json'}
    if session:
        headers['Cookie'] = 'trading_lab_session=' + session
    return Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')


def _write_c2_research_fixture(root: Path, *, provider_id: str = '501', win_rate: float = 55.0) -> None:
    intel = root / 'intelligence'
    intel.mkdir(parents=True, exist_ok=True)
    (intel / 'provider-research-top10-latest.json').write_text(
        json.dumps(
            {
                'top_10_research': [
                    {
                        'provider_id': provider_id,
                        'name': 'C2-%s' % provider_id,
                        'win_rate_pct': win_rate,
                        'reported_pnl_sum': 900.25,
                    }
                ]
            }
        ),
        encoding='utf-8',
    )


class _ApprovalsMemoryCursor:
    def __init__(self, store):
        self._store = store
        self._all = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        params = params or ()
        normalized = ' '.join(sql.split())
        if 'FROM signal_provider_approvals ORDER' in normalized:
            self._all = [
                (
                    row['platform'],
                    row['provider_id'],
                    row['status'],
                    row['source'],
                    None,
                )
                for row in self._store['signal_provider_approvals'].values()
            ]
            return
        if normalized.startswith('INSERT INTO signal_provider_approvals'):
            platform, provider_id, status = params[:3]
            key = (platform, provider_id)
            self._store['signal_provider_approvals'][key] = {
                'platform': platform,
                'provider_id': provider_id,
                'status': status,
                'source': 'panel',
            }
            return
        raise AssertionError('unexpected SQL: %s' % normalized)

    def fetchall(self):
        return self._all or []

    def fetchone(self):
        return None


class _ApprovalsMemoryConn:
    def __init__(self, store):
        self._store = store

    def cursor(self):
        return _ApprovalsMemoryCursor(self._store)

    def commit(self):
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def _approvals_memory_connect(store):
    def connect():
        return _ApprovalsMemoryConn(store)
    return connect


def _write_webhook_journal(root: Path, rows: list[dict]) -> None:
    wh = root / 'webhooks'
    wh.mkdir(parents=True, exist_ok=True)
    (wh / 'journal.jsonl').write_text(
        '\n'.join(json.dumps(r) for r in rows),
        encoding='utf-8',
    )


def _write_order_snapshots(root: Path, rows: list[dict]) -> None:
    paper = root / 'paper'
    paper.mkdir(parents=True, exist_ok=True)
    (paper / 'order-snapshots.jsonl').write_text(
        '\n'.join(json.dumps(r) for r in rows),
        encoding='utf-8',
    )


def _clear_order_snapshots(root: Path) -> None:
    _write_order_snapshots(root, [])


def _write_prodigy_research_copy(
    root: Path,
    *,
    provider: str = 'prov-research',
    symbol: str = 'META',
) -> None:
    evo = root / 'evolution'
    evo.mkdir(parents=True, exist_ok=True)
    (evo / 'decisions.jsonl').write_text(
        json.dumps(
            {
                'kind': 'signal_copy',
                'provider': provider,
                'symbol': symbol,
                'signal_id': 'SIG-RES-1',
            }
        ),
        encoding='utf-8',
    )


def _write_signal_orders_journal(
    root: Path,
    rows: list[dict],
) -> None:
    paper = root / 'paper'
    paper.mkdir(parents=True, exist_ok=True)
    (paper / 'signal-orders.jsonl').write_text(
        '\n'.join(json.dumps(r) for r in rows),
        encoding='utf-8',
    )


def _write_prodigy_pool_fixture(root: Path, *, use_provider_id: bool = False) -> None:
    intel = root / 'intelligence'
    intel.mkdir(parents=True, exist_ok=True)
    row = {
        'status': 'candidate',
        'prodigy_score': '0.42',
    }
    if use_provider_id:
        row['provider_id'] = 'provider-77'
    else:
        row['provider'] = 'prov-a'
    payload = {
        'mode': 'PRODIGY_RANK_RESEARCH_ONLY',
        'as_of': '2026-11-17',
        'top_10_research': [row],
        'score_warning': 'Research rank only; does not authorize orders.',
    }
    (intel / 'prodigy-top10-latest.json').write_text(json.dumps(payload), encoding='utf-8')


def _write_c2_allowlist_fixture(root: Path, approved_ids: list[str]) -> None:
    cfg = root / 'config'
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / 'c2_paper_copy_allowlist.json').write_text(
        json.dumps({'approved_ids': approved_ids}, indent=2),
        encoding='utf-8',
    )


def _write_c2_active_orders_snapshot(root: Path) -> None:
    out = root / 'reports' / 'providers' / 'signals'
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        'mode': 'C2_ACTIVE_ORDERS_READ_ONLY',
        'as_of': '2026-11-17T12:00:00+00:00',
        'strategy_ids': ['999001'],
        'records': [{'StrategyId': '999001', 'Symbol': 'SPY'}],
        'execution_authorized': False,
        'orders_sent': 0,
    }
    (out / 'active-orders-latest.json').write_text(json.dumps(payload), encoding='utf-8')


def _write_signal_copy_panel_fixture(root: Path) -> None:
    _write_order_snapshots(
        root,
        [
            {
                'client_order_id': 'copy-open-aapl',
                'status': 'MONITORED',
                'symbol': 'AAPL',
                'side': 'buy',
                'entry_qty': 1,
                'remaining_qty': 1,
                'broker_status': 'accepted',
                'strategy_key': 'signal_copy',
            },
            {
                'client_order_id': 'copy-fill-msft',
                'status': 'MONITORED',
                'symbol': 'MSFT',
                'side': 'buy',
                'entry_qty': 1,
                'remaining_qty': 0,
                'broker_fill_confirmed': True,
                'realized_gross_pnl_usd': '7',
                'strategy_key': 'signal_copy',
            },
            {
                'client_order_id': 'copy-queue-nvda',
                'status': 'MONITORED',
                'symbol': 'NVDA',
                'side': 'buy',
                'entry_qty': 1,
                'remaining_qty': 1,
                'paper_status': 'queued_intent',
                'strategy_key': 'signal_copy',
            },
            {
                'client_order_id': 'other-momentum',
                'status': 'MONITORED',
                'symbol': 'TSLA',
                'side': 'buy',
                'entry_qty': 1,
                'remaining_qty': 0,
                'broker_fill_confirmed': True,
                'realized_gross_pnl_usd': '3',
                'strategy_key': 'momentum',
            },
        ],
    )
    _write_webhook_journal(
        root,
        [
            {
                'payload': {'provider': 'tradingview', 'symbol': 'AAPL'},
                'result': {'reject_code': 'MAX_POSITIONS'},
                'received_at': '2026-11-16T10:00:00+00:00',
            },
        ],
    )


def _write_evolution_daily_timesfm(
    root: Path,
    timesfm: dict,
    *,
    day: str = '2026-11-17',
) -> None:
    daily = root / 'evolution' / 'daily'
    daily.mkdir(parents=True, exist_ok=True)
    (daily / f'{day}.json').write_text(
        json.dumps({'day': day, 'timesfm': timesfm}),
        encoding='utf-8',
    )


def _unauthenticated_panel_status(base: str, path: str) -> int:
    opener = build_opener(_NoRedirect)
    try:
        opener.open(_get(base + path), timeout=3)
        return 200
    except HTTPError as exc:
        return exc.code


_OLD_KILL_COPY = (
    'Ligar parada',
    'Desligar parada',
    'Parada geral ligada',
    'Parada geral',
    'Operando',
    'operação demo permitida',
    'Liberar operação demo',
)


class RenderCentralPageFreioCopyTests(unittest.TestCase):
    def _render(self, kill: bool | None) -> str:
        flags: dict = {}
        if kill is not None:
            flags['kill_switch_on'] = kill
        triggers = {'control_flags': flags, 'market_controls': []}
        return render_central_page({'signals': []}, triggers)

    def _assert_no_old_copy(self, html: str) -> None:
        for fragment in _OLD_KILL_COPY:
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, html)

    def _assert_single_brake_cta(self, html: str) -> None:
        self.assertEqual(html.count('class="brake-strip__cta"'), 1)

    def _assert_brake_strip_not_warn(self, html: str) -> None:
        start = html.find('class="brake-strip')
        self.assertGreater(start, -1)
        chunk = html[start : start + 400]
        self.assertNotIn('class="warn"', chunk)
        self.assertNotIn('brake-strip warn', chunk)

    def test_kill_on_shows_emergency_brake_copy(self):
        html = self._render(True)
        self.assertIn('brake-strip--active', html)
        self.assertIn('Freio de emergência ativo', html)
        self.assertIn('Ordens demo novas bloqueadas.', html)
        self.assertIn('id="kill-off"', html)
        self.assertIn('>Liberar freio<', html)
        self.assertNotIn('id="kill-on"', html)
        self.assertNotIn('>Ativar freio<', html)
        self.assertIn('kill_switch_on', html)
        self._assert_single_brake_cta(html)
        self._assert_brake_strip_not_warn(html)
        self._assert_no_old_copy(html)

    def test_kill_off_shows_released_brake_copy(self):
        html = self._render(False)
        self.assertIn('brake-strip--released', html)
        self.assertIn('Freio liberado', html)
        self.assertIn('Outros limites ainda valem.', html)
        self.assertIn('>Ativar freio<', html)
        self.assertIn('id="kill-on"', html)
        self.assertNotIn('>Liberar freio<', html)
        self.assertNotIn('id="kill-off"', html)
        self.assertIn('Conta demo · Live desligado (sem botão)', html)
        self.assertIn('Live desligado', html)
        self.assertNotIn('>Live<', html)
        self.assertNotIn('id="live"', html)
        self._assert_single_brake_cta(html)
        self._assert_brake_strip_not_warn(html)
        self._assert_no_old_copy(html)

    def test_kill_missing_flag_defaults_to_released_status(self):
        html = self._render(None)
        self.assertIn('brake-strip--released', html)
        self.assertIn('Freio liberado', html)
        self.assertIn('Outros limites ainda valem.', html)
        self.assertIn('id="kill-on"', html)
        self.assertNotIn('id="kill-off"', html)
        self._assert_single_brake_cta(html)
        self._assert_no_old_copy(html)

    def test_kill_script_binds_conditionally(self):
        html = self._render(False)
        self.assertIn("const killOn=document.getElementById('kill-on');", html)
        self.assertIn('if(killOn)killOn.onclick', html)
        self.assertIn("const killOff=document.getElementById('kill-off');", html)
        self.assertIn('if(killOff)killOff.onclick', html)
        self.assertNotIn("getElementById('kill-on').onclick", html)


class PanelOpsDataTests(unittest.TestCase):
    def test_signal_destination_blocked_vs_queue(self):
        self.assertEqual(signal_destination(event_status='rejected', reject_code='KILL_SWITCH'), 'blocked')
        self.assertEqual(signal_destination(event_status='accepted', paper_status='queued_intent'), 'queue')
        self.assertEqual(signal_destination(event_status='accepted', paper_status='filled'), 'order')

    def test_blocked_context_exposes_gate_and_anchor(self):
        ctx = blocked_context('MAX_POSITIONS', {'max_open_positions': 3})
        self.assertEqual(ctx['gate'], 'gate_b')
        self.assertEqual(ctx['anchor_field'], 'max_open_positions')
        self.assertEqual(ctx['anchor_value'], 3)

    def test_performance_excludes_unfilled_orders(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'paper').mkdir()
            rows = [
                {
                    'client_order_id': 'a',
                    'status': 'MONITORED',
                    'entry_qty': 1,
                    'remaining_qty': 0,
                    'broker_fill_confirmed': True,
                    'realized_gross_pnl_usd': '10',
                    'strategy_key': 'signal_copy',
                },
                {
                    'client_order_id': 'b',
                    'status': 'MONITORED',
                    'entry_qty': 1,
                    'remaining_qty': 1,
                    'broker_status': 'accepted',
                    'realized_gross_pnl_usd': '99',
                    'strategy_key': 'signal_copy',
                },
                {
                    'client_order_id': 'c',
                    'status': 'MONITORED',
                    'entry_qty': 1,
                    'remaining_qty': 0,
                    'broker_fill_confirmed': True,
                    'realized_gross_pnl_usd': '5',
                    'strategy_key': 'momentum',
                },
            ]
            (root / 'paper' / 'order-snapshots.jsonl').write_text(
                '\n'.join(json.dumps(r) for r in rows),
                encoding='utf-8',
            )
            perf = performance_from_snapshots(root)
            self.assertEqual(perf['orders_included'], 2)
            self.assertEqual(perf['total_gross_usd'], '15')
            self.assertEqual(perf['pnl_label'], PERFORMANCE_LABEL_GROSS)
            self.assertIn('strategies', perf)
            by_key = {row['strategy_key']: row for row in perf['strategies']}
            self.assertEqual(set(by_key), {'momentum', 'signal_copy'})
            self.assertEqual(by_key['signal_copy']['gross_usd'], '10')
            self.assertEqual(by_key['momentum']['gross_usd'], '5')
            self.assertEqual(by_key['signal_copy']['pnl_label'], PERFORMANCE_LABEL_GROSS)

    def test_load_panel_signals_exposes_origin_destination_and_reject_reason(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_webhook_journal(
                root,
                [
                    {
                        'payload': {'provider': 'tradingview', 'symbol': 'MSFT', 'market': 'US_EQUITY'},
                        'result': {'status': 'rejected', 'reject_code': 'KILL_SWITCH'},
                        'received_at': '2026-11-16T12:00:00+00:00',
                    },
                    {
                        'payload': {'provider': 'prodigy', 'symbol': 'NVDA'},
                        'result': {'status': 'QUEUED'},
                        'received_at': '2026-11-16T13:00:00+00:00',
                    },
                ],
            )
            flags = {'kill_switch_on': True, 'max_open_positions': 3}
            items = load_panel_signals(root, None, flags)
            self.assertGreaterEqual(len(items), 2)
            blocked = next(i for i in items if i['symbol'] == 'MSFT')
            self.assertEqual(blocked['origin'], 'tradingview')
            self.assertEqual(blocked['destination'], 'blocked')
            self.assertEqual(blocked['reject_reason'], 'KILL_SWITCH')
            queued = next(i for i in items if i['symbol'] == 'NVDA')
            self.assertEqual(queued['origin'], 'prodigy')
            self.assertEqual(queued['destination'], 'queue')

    def test_snapshot_panel_ops_prodigy_ranking_and_copied_signals(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            intel = root / 'intelligence'
            intel.mkdir()
            (intel / 'prodigy-top10-latest.json').write_text(
                json.dumps(
                    {
                        'mode': 'PRODIGY_RANK_RESEARCH_ONLY',
                        'top_10_research': [
                            {'provider': 'prov-a', 'status': 'watch', 'prodigy_score': 9},
                        ],
                    }
                ),
                encoding='utf-8',
            )
            evo = root / 'evolution'
            evo.mkdir()
            (evo / 'decisions.jsonl').write_text(
                json.dumps(
                    {
                        'kind': 'signal_copy',
                        'provider': 'prov-a',
                        'symbol': 'AAPL',
                        'signal_id': 'SIG-1',
                    }
                ),
                encoding='utf-8',
            )
            data = build_snapshot(root)
            prodigy = data['panel_ops']['prodigy']
            ranking = prodigy['ranking']
            self.assertIsInstance(ranking, dict)
            self.assertEqual(ranking['items'][0]['provider'], 'prov-a')
            copied = prodigy['copied_signals']
            self.assertEqual(len(copied), 1)
            self.assertEqual(copied[0]['provider'], 'prov-a')
            self.assertEqual(copied[0]['symbol'], 'AAPL')

    def test_build_panel_bundle_prodigy_copied_signals_structure(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            evo = root / 'evolution'
            evo.mkdir()
            (evo / 'decisions.jsonl').write_text(
                json.dumps({'kind': 'signal_copy', 'provider': 'p1', 'symbol': 'TSLA'}),
                encoding='utf-8',
            )
            bundle = build_panel_bundle(root, conn_factory=None)
            self.assertIn('copied_signals', bundle['prodigy'])
            self.assertEqual(bundle['prodigy']['copied_signals'][0]['symbol'], 'TSLA')

    def test_build_panel_bundle_open_order_snapshot_row(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_order_snapshots(
                root,
                [
                    {
                        'client_order_id': 'open-aapl',
                        'status': 'MONITORED',
                        'symbol': 'AAPL',
                        'side': 'buy',
                        'entry_qty': 2,
                        'remaining_qty': 2,
                        'broker_status': 'accepted',
                        'strategy_key': 'signal_copy',
                    },
                ],
            )
            bundle = build_panel_bundle(root, conn_factory=None)
            self.assertIn('open_orders', bundle)
            self.assertIn('order_history', bundle)
            open_rows = bundle['open_orders']
            self.assertEqual(len(open_rows), 1)
            self.assertEqual(open_rows[0]['symbol'], 'AAPL')
            self.assertEqual(open_rows[0]['status'], 'MONITORED')
            self.assertEqual(bundle['order_history'], [])

    def test_build_panel_bundle_confirmed_fill_in_order_history_only(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_order_snapshots(
                root,
                [
                    {
                        'client_order_id': 'fill-msft',
                        'status': 'MONITORED',
                        'symbol': 'MSFT',
                        'side': 'buy',
                        'entry_qty': 1,
                        'remaining_qty': 0,
                        'broker_fill_confirmed': True,
                        'realized_gross_pnl_usd': '12',
                        'strategy_key': 'signal_copy',
                    },
                    {
                        'client_order_id': 'queue-nvda',
                        'status': 'MONITORED',
                        'symbol': 'NVDA',
                        'side': 'buy',
                        'entry_qty': 1,
                        'remaining_qty': 1,
                        'paper_status': 'queued_intent',
                        'strategy_key': 'signal_copy',
                    },
                ],
            )
            bundle = build_panel_bundle(root, conn_factory=None)
            history = bundle['order_history']
            symbols_hist = {row['symbol'] for row in history}
            self.assertIn('MSFT', symbols_hist)
            self.assertNotIn('NVDA', symbols_hist)
            open_syms = {row['symbol'] for row in bundle['open_orders']}
            self.assertIn('NVDA', open_syms)

    def test_ledger_order_rows_json_serializable_with_decimal_qty(self):
        class _LedgerCursor:
            def __init__(self) -> None:
                self._sql = ''

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def execute(self, sql, params=None):
                self._sql = sql.lower()

            def fetchall(self):
                if 'from paper_orders po' in self._sql and 'paper_fills' not in self._sql:
                    return [
                        (
                            'cid-1',
                            'AAPL',
                            'buy',
                            'accepted',
                            Decimal('2.5'),
                            'brk-1',
                            'signal_copy',
                            'tradingview',
                            'se-uuid-1',
                        ),
                    ]
                if 'pf.filled_at' in self._sql:
                    filled = datetime(2026, 11, 17, 12, 0, tzinfo=timezone.utc)
                    return [
                        (
                            'cid-2',
                            'MSFT',
                            'sell',
                            'filled',
                            'brk-2',
                            'momentum',
                            Decimal('1'),
                            1500,
                            filled,
                            'tradingview',
                            'se-uuid-2',
                        ),
                    ]
                if 'from signal_events' in self._sql:
                    return []
                if 'from ledger_entries le' in self._sql:
                    return [('momentum', 1500, 'filled')]
                return []

            def fetchone(self):
                return None

        class _LedgerConn:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def cursor(self):
                return _LedgerCursor()

        def _factory():
            return _LedgerConn()

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bundle = build_panel_bundle(root, conn_factory=_factory)
            json.dumps(bundle, allow_nan=False)
            self.assertEqual(bundle['open_orders'][0]['entry_qty'], '2.5')
            self.assertEqual(bundle['order_history'][0]['entry_qty'], '1')


class PanelOpsHttpTests(unittest.TestCase):
    def _server(self, tmp, session='panel-secret', token=None):
        handler = make_handler(Path(tmp), token=token, operator_session=session)
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server, thread, 'http://127.0.0.1:' + str(server.server_port)

    def _shutdown(self, server, thread):
        server.shutdown()
        server.server_close()
        thread.join(3)

    def test_root_redirects_to_login_without_cookie(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                req = _get(base + '/')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                    self.assertIn('Entrar', body)
            finally:
                self._shutdown(server, thread)

    def test_login_sets_cookie_and_opens_central(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                login = Request(
                    base + '/api/login',
                    data=b'password=prototype',
                    headers={'Content-Type': 'application/x-www-form-urlencoded'},
                    method='POST',
                )
                opener = build_opener(_NoRedirect)
                try:
                    opener.open(login, timeout=3)
                except HTTPError as resp:
                    cookies = resp.headers.get('Set-Cookie') or ''
                    self.assertEqual(resp.code, 303)
                else:
                    self.fail('login should redirect with Set-Cookie')
                self.assertIn('trading_lab_session=panel-secret', cookies)
                req = _get(base + '/', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                    self.assertIn('Central', body)
                    self.assertIn('Live desligado', body)
                    self.assertIn('Ativar freio', body)
            finally:
                self._shutdown(server, thread)

    def test_bearer_alone_still_401_on_patch(self):
        token = 'sample-token-' + 'x' * 30
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d, token=token)
            try:
                req = _patch(base + '/api/triggers', {'kill_switch_on': True}, session=None)
                req.add_header('Authorization', 'Bearer ' + token)
                with self.assertRaises(HTTPError) as err:
                    urlopen(req, timeout=3)
                self.assertEqual(err.exception.code, 401)
            finally:
                self._shutdown(server, thread)

    def test_api_signals_requires_session(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                with self.assertRaises(HTTPError) as err:
                    urlopen(base + '/api/signals', timeout=3)
                self.assertEqual(err.exception.code, 401)
            finally:
                self._shutdown(server, thread)

    def test_snapshot_includes_panel_ops(self):
        with tempfile.TemporaryDirectory() as d:
            data = build_snapshot(d)
            self.assertIn('panel_ops', data)
            self.assertIn('performance_panel', data)

    def test_api_signals_json_origin_destination_reject_reason(self):
        with patch.dict(os.environ, {'LEDGER_DATABASE_URL': ''}, clear=False):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _write_webhook_journal(
                    root,
                    [
                        {
                            'payload': {'provider': 'tradingview', 'symbol': 'AAPL'},
                            'result': {'reject_code': 'MAX_POSITIONS'},
                            'received_at': '2026-11-16T10:00:00+00:00',
                        },
                    ],
                )
                server, thread, base = self._server(str(root))
                try:
                    req = _get(base + '/api/signals', session='panel-secret')
                    with urlopen(req, timeout=3) as resp:
                        payload = json.load(resp)
                    signals = payload['signals']
                    self.assertEqual(len(signals), 1)
                    row = signals[0]
                    self.assertEqual(row['origin'], 'tradingview')
                    self.assertEqual(row['destination'], 'blocked')
                    self.assertEqual(row['reject_reason'], 'MAX_POSITIONS')
                finally:
                    self._shutdown(server, thread)


class PanelOrdersHistoryHttpTests(unittest.TestCase):
    def setUp(self):
        self._ledger_env = patch.dict(os.environ, {'LEDGER_DATABASE_URL': ''}, clear=False)
        self._ledger_env.start()

    def tearDown(self):
        self._ledger_env.stop()

    def _server(self, tmp, session='panel-secret', token=None):
        handler = make_handler(Path(tmp), token=token, operator_session=session)
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server, thread, 'http://127.0.0.1:' + str(server.server_port)

    def _shutdown(self, server, thread):
        server.shutdown()
        server.server_close()
        thread.join(3)

    def test_unauthenticated_ordens_historico_match_sinais_gate(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                reference = _unauthenticated_panel_status(base, '/sinais')
                for path in ('/ordens', '/historico'):
                    with self.subTest(path=path):
                        self.assertEqual(
                            _unauthenticated_panel_status(base, path),
                            reference,
                        )
            finally:
                self._shutdown(server, thread)

    def test_ordens_empty_shows_paper_copy(self):
        with tempfile.TemporaryDirectory() as d:
            _clear_order_snapshots(Path(d))
            server, thread, base = self._server(d)
            try:
                req = _get(base + '/ordens', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn('Nenhuma ordem aberta no paper.', body)
            finally:
                self._shutdown(server, thread)

    def test_historico_empty_shows_confirmed_fill_copy(self):
        with tempfile.TemporaryDirectory() as d:
            _clear_order_snapshots(Path(d))
            server, thread, base = self._server(d)
            try:
                req = _get(base + '/historico', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn('Nenhum fill confirmado no histórico.', body)
            finally:
                self._shutdown(server, thread)

    def test_fixture_open_order_on_ordens_not_as_history_fill(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_order_snapshots(
                root,
                [
                    {
                        'client_order_id': 'live-open',
                        'status': 'MONITORED',
                        'symbol': 'AAPL',
                        'side': 'buy',
                        'entry_qty': 1,
                        'remaining_qty': 1,
                        'broker_status': 'accepted',
                        'strategy_key': 'signal_copy',
                    },
                ],
            )
            server, thread, base = self._server(root)
            try:
                req = _get(base + '/ordens', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    ordens = resp.read().decode('utf-8')
                self.assertIn('AAPL', ordens)
                self.assertIn('accepted', ordens.lower())
                req = _get(base + '/historico', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    historico = resp.read().decode('utf-8')
                self.assertIn('Nenhum fill confirmado no histórico.', historico)
                self.assertNotIn('live-open', historico)
            finally:
                self._shutdown(server, thread)

    def test_fixture_fill_on_historico_queued_intent_excluded(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_order_snapshots(
                root,
                [
                    {
                        'client_order_id': 'done-msft',
                        'status': 'MONITORED',
                        'symbol': 'MSFT',
                        'side': 'sell',
                        'entry_qty': 1,
                        'remaining_qty': 0,
                        'broker_fill_confirmed': True,
                        'realized_gross_pnl_usd': '3',
                        'strategy_key': 'momentum',
                    },
                    {
                        'client_order_id': 'queue-only',
                        'status': 'MONITORED',
                        'symbol': 'NVDA',
                        'side': 'buy',
                        'entry_qty': 1,
                        'remaining_qty': 1,
                        'paper_status': 'queued_intent',
                        'strategy_key': 'signal_copy',
                    },
                ],
            )
            server, thread, base = self._server(root)
            try:
                req = _get(base + '/historico', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    historico = resp.read().decode('utf-8')
                self.assertIn('MSFT', historico)
                self.assertNotIn('queue-only', historico)
                self.assertNotIn('queued_intent', historico.lower())
                req = _get(base + '/ordens', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    ordens = resp.read().decode('utf-8')
                self.assertIn('NVDA', ordens)
            finally:
                self._shutdown(server, thread)

    def test_nav_after_login_lists_ordens_and_historico(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                req = _get(base + '/central', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn('href="/ordens"', body)
                self.assertIn('href="/historico"', body)
                self.assertIn('Ordens', body)
                self.assertIn('Histórico', body)
            finally:
                self._shutdown(server, thread)

    def test_api_orders_and_history_require_session(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                signals_code = None
                for path in ('/api/orders', '/api/history'):
                    with self.subTest(path=path):
                        with self.assertRaises(HTTPError) as err:
                            urlopen(base + path, timeout=3)
                        if signals_code is None:
                            with self.assertRaises(HTTPError) as sig_err:
                                urlopen(base + '/api/signals', timeout=3)
                            signals_code = sig_err.exception.code
                        self.assertEqual(err.exception.code, signals_code)
            finally:
                self._shutdown(server, thread)

    def test_api_orders_and_history_empty_json_lists(self):
        with tempfile.TemporaryDirectory() as d:
            _clear_order_snapshots(Path(d))
            server, thread, base = self._server(d)
            try:
                req = _get(base + '/api/orders', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    orders_payload = json.load(resp)
                self.assertEqual(orders_payload.get('orders'), [])
                req = _get(base + '/api/history', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    history_payload = json.load(resp)
                self.assertEqual(history_payload.get('history'), [])
            finally:
                self._shutdown(server, thread)

    def test_regression_sinais_performance_central_still_render(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                cases = (
                    ('/sinais', 'Sinais'),
                    ('/performance', PERFORMANCE_LABEL_GROSS),
                    ('/central', 'Central'),
                )
                for path, needle in cases:
                    with self.subTest(path=path):
                        req = _get(base + path, session='panel-secret')
                        with urlopen(req, timeout=3) as resp:
                            body = resp.read().decode('utf-8')
                        self.assertIn(needle, body)
            finally:
                self._shutdown(server, thread)


N42_EMPTY_CATALOG_COPY = 'Catálogo indisponível (ledger)'

_N42_CATALOG_FIXTURE = [
    {
        'strategy_key': 'momentum',
        'phase': 'research',
        'paper_allowed': False,
        'promotion': 'operator_only',
    },
    {
        'strategy_key': 'orb',
        'phase': 'shadow',
        'paper_allowed': False,
        'promotion': 'operator_only',
    },
    {
        'strategy_key': 'signal_copy',
        'phase': 'paper_limited',
        'paper_allowed': True,
        'promotion': 'operator_only',
    },
]


class PanelStrategiesHttpTests(unittest.TestCase):
    def setUp(self):
        self._ledger_env = patch.dict(os.environ, {'LEDGER_DATABASE_URL': ''}, clear=False)
        self._ledger_env.start()

    def tearDown(self):
        self._ledger_env.stop()

    def _server(self, tmp, session='panel-secret', token=None):
        handler = make_handler(Path(tmp), token=token, operator_session=session)
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server, thread, 'http://127.0.0.1:' + str(server.server_port)

    def _shutdown(self, server, thread):
        server.shutdown()
        server.server_close()
        thread.join(3)

    def test_unauthenticated_estrategias_and_api_match_sinais_gate(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                reference = _unauthenticated_panel_status(base, '/sinais')
                self.assertEqual(_unauthenticated_panel_status(base, '/estrategias'), reference)
                signals_code = None
                with self.assertRaises(HTTPError) as err:
                    urlopen(base + '/api/estrategias', timeout=3)
                with self.assertRaises(HTTPError) as sig_err:
                    urlopen(base + '/api/signals', timeout=3)
                signals_code = sig_err.exception.code
                self.assertEqual(err.exception.code, signals_code)
            finally:
                self._shutdown(server, thread)

    def test_estrategias_auth_empty_shows_catalog_unavailable_copy(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                req = _get(base + '/estrategias', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn(N42_EMPTY_CATALOG_COPY, body)
            finally:
                self._shutdown(server, thread)

    def test_estrategias_fixture_rows_show_strategy_key_and_phase(self):
        catalog_patch = patch(
            'strategy_catalog.list_strategy_states',
            return_value=_N42_CATALOG_FIXTURE,
        )
        with catalog_patch:
            with tempfile.TemporaryDirectory() as d:
                server, thread, base = self._server(d)
                try:
                    req = _get(base + '/estrategias', session='panel-secret')
                    with urlopen(req, timeout=3) as resp:
                        body = resp.read().decode('utf-8')
                    self.assertIn('momentum', body)
                    self.assertTrue('research' in body or 'pesquisa' in body)
                    self.assertIn('orb', body)
                    self.assertTrue('shadow' in body or 'sombra' in body)
                    self.assertIn('signal_copy', body)
                    self.assertTrue(
                        'paper_limited' in body or 'paper limitado' in body.lower()
                    )
                finally:
                    self._shutdown(server, thread)

    def test_nav_includes_estrategias_menu_link(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                req = _get(base + '/central', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn('href="/estrategias"', body)
                self.assertIn('Estratégias', body)
            finally:
                self._shutdown(server, thread)

    def test_estrategias_page_has_no_phase_promotion_controls(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                req = _get(base + '/estrategias', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                lowered = body.lower()
                self.assertNotIn('/api/strategies', body)
                self.assertNotIn('method="patch"', lowered)
                self.assertNotIn("method='patch'", lowered)
                self.assertNotIn('promover', lowered)
            finally:
                self._shutdown(server, thread)

    def test_api_estrategias_returns_strategies_list_with_session(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                req = _get(base + '/api/estrategias', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    payload = json.load(resp)
                self.assertIn('strategies', payload)
                self.assertIsInstance(payload['strategies'], list)
            finally:
                self._shutdown(server, thread)

    def test_regression_ordens_historico_sinais_still_render(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                cases = (
                    ('/ordens', 'Ordens'),
                    ('/historico', 'Histórico'),
                    ('/sinais', 'Sinais'),
                )
                for path, needle in cases:
                    with self.subTest(path=path):
                        req = _get(base + path, session='panel-secret')
                        with urlopen(req, timeout=3) as resp:
                            body = resp.read().decode('utf-8')
                        self.assertIn(needle, body)
            finally:
                self._shutdown(server, thread)


N43_UNAVAILABLE_MAIN = (
    'Análise Google indisponível: modelo ou dependência ausente.'
)
N43_SUBTITLE = 'Dica de pesquisa — não autoriza ordem. Live desligado.'
N43_FOOTER = 'Esta análise é só pesquisa. Não autoriza ordem.'
N43_REASON_PREFIX = 'Motivo:'
_N43_REASON_MARKERS = (
    'Motivo: modelo ou dependência ausente.',
    'Motivo: modelo desligado neste ambiente.',
    'Motivo: checkpoint não configurado.',
    'Motivo: série de contexto insuficiente.',
)
_N43_TIMESFM_OK_FIXTURE = {
    'timesfm_status': 'OK',
    'tips': [
        {
            'label': 'research_tip',
            'summary': 'Horizonte de oito barras como contexto de pesquisa.',
            'execution_authorized': False,
            'paper_allowed': False,
            'orders_sent': 0,
        },
        {
            'label': 'suggestion',
            'summary': 'Revisar parâmetro de risco no catálogo.',
            'execution_authorized': False,
            'paper_allowed': False,
            'orders_sent': 0,
        },
    ],
    'execution_authorized': False,
    'paper_allowed': False,
}


class PanelAnaliseGoogleHttpTests(unittest.TestCase):
    def setUp(self):
        self._ledger_env = patch.dict(os.environ, {'LEDGER_DATABASE_URL': ''}, clear=False)
        self._ledger_env.start()

    def tearDown(self):
        self._ledger_env.stop()

    def _server(self, tmp, session='panel-secret', token=None):
        handler = make_handler(Path(tmp), token=token, operator_session=session)
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server, thread, 'http://127.0.0.1:' + str(server.server_port)

    def _shutdown(self, server, thread):
        server.shutdown()
        server.server_close()
        thread.join(3)

    def _assert_motivo_present(self, body: str) -> None:
        self.assertIn(N43_REASON_PREFIX, body)
        self.assertTrue(any(marker in body for marker in _N43_REASON_MARKERS))

    def test_unauthenticated_analise_google_and_api_match_sinais_gate(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                reference = _unauthenticated_panel_status(base, '/sinais')
                self.assertEqual(
                    _unauthenticated_panel_status(base, '/analise-google'),
                    reference,
                )
                with self.assertRaises(HTTPError) as err:
                    urlopen(base + '/api/analise-google', timeout=3)
                with self.assertRaises(HTTPError) as sig_err:
                    urlopen(base + '/api/signals', timeout=3)
                self.assertEqual(err.exception.code, sig_err.exception.code)
            finally:
                self._shutdown(server, thread)

    def test_analise_google_auth_unavailable_shows_empty_main_and_footer(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                req = _get(base + '/analise-google', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn(N43_UNAVAILABLE_MAIN, body)
                self.assertIn(N43_SUBTITLE, body)
                self.assertIn(N43_FOOTER, body)
                self._assert_motivo_present(body)
            finally:
                self._shutdown(server, thread)

    def test_analise_google_fixture_ok_shows_labeled_tips_no_order_auth(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_evolution_daily_timesfm(root, _N43_TIMESFM_OK_FIXTURE)
            server, thread, base = self._server(root)
            try:
                req = _get(base + '/analise-google', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn(
                    'Horizonte de oito barras como contexto de pesquisa.',
                    body,
                )
                self.assertIn(
                    'Revisar parâmetro de risco no catálogo.',
                    body,
                )
                self.assertIn('dica de pesquisa', body)
                self.assertIn('sugestão', body)
                self.assertIn(N43_SUBTITLE, body)
                self.assertIn(N43_FOOTER, body)
                self.assertNotIn('execution_authorized": true', body.lower())
                self.assertNotIn('execution_authorized":true', body.lower())
                self.assertNotIn('enviar ordem', body.lower())
            finally:
                self._shutdown(server, thread)

    def test_nav_includes_analise_google_menu_link(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                req = _get(base + '/central', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn('href="/analise-google"', body)
                self.assertIn('Análise Google', body)
            finally:
                self._shutdown(server, thread)

    def test_analise_google_page_has_no_order_submit_controls(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                req = _get(base + '/analise-google', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                lowered = body.lower()
                self.assertNotIn('process_after_gate_b', body)
                self.assertNotIn('>Live<', body)
                self.assertNotIn('enviar ordem', lowered)
                self.assertNotIn('method="post"', lowered)
            finally:
                self._shutdown(server, thread)

    def test_api_analise_google_returns_research_payload_with_session(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                req = _get(base + '/api/analise-google', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    payload = json.load(resp)
                self.assertIn('timesfm_status', payload)
                self.assertIn('tips', payload)
                self.assertIsInstance(payload['tips'], list)
                self.assertFalse(payload.get('execution_authorized'))
                self.assertFalse(payload.get('paper_allowed', True))
                self.assertNotIn('forecast', payload)
                self.assertNotIn('forecast_values', payload)
            finally:
                self._shutdown(server, thread)

    def test_regression_estrategias_ordens_historico_sinais_still_render(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                cases = (
                    ('/estrategias', 'Estratégias'),
                    ('/ordens', 'Ordens'),
                    ('/historico', 'Histórico'),
                    ('/sinais', 'Sinais'),
                )
                for path, needle in cases:
                    with self.subTest(path=path):
                        req = _get(base + path, session='panel-secret')
                        with urlopen(req, timeout=3) as resp:
                            body = resp.read().decode('utf-8')
                        self.assertIn(needle, body)
            finally:
                self._shutdown(server, thread)


N48_SECTION_AUDIT = 'Auditoria de ingresso'
N48_COPY_EMPTY = 'Nenhuma cópia de terceiro em operação.'
N48_COPY_PERF_EMPTY = 'Sem fills confirmados nesta cópia.'
N50_OPERATING_SECTION = 'Em operação / assinados'
N50_C2_SECTION = 'Collective2'
N50_C2_EMPTY = 'Collective2: cópia paper fechada — nenhum provedor na lista nomeada.'
N50_C2_ALLOWLIST = 'Collective2: cópia paper só para os provedores nomeados.'
N50_POOL_SECTION = 'Candidatos Prodígio (pesquisa)'
N48_AUDIT_EMPTY = 'Nenhum sinal neste destino.'
N48_AUDIT_SUBTITLE = 'Auditoria de ingresso — origem, destino e motivo. Não é fill.'
N48_COPY_SUBTITLE = 'Cópia de terceiros (TradingView / provedores). Não é fill.'
N48_FOOTER = (
    'O painel não envia ordem. Live desligado. Valores brutos se o custo não estiver completo.'
)


class PanelSinaisCopyAuditHttpTests(unittest.TestCase):
    def setUp(self):
        self._ledger_env = patch.dict(os.environ, {'LEDGER_DATABASE_URL': ''}, clear=False)
        self._ledger_env.start()

    def tearDown(self):
        self._ledger_env.stop()

    def _server(self, tmp, session='panel-secret', token=None):
        handler = make_handler(Path(tmp), token=token, operator_session=session)
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        return server, thread, 'http://127.0.0.1:' + str(server.server_port)

    def _shutdown(self, server, thread):
        server.shutdown()
        server.server_close()
        thread.join(3)

    def _assert_copy_object_shape(self, copy: dict) -> None:
        for key in (
            'operating',
            'history',
            'performance',
            'collective2',
            'inventory',
            'adoption',
            'prodigy_pool',
        ):
            self.assertIn(key, copy)
        collective2 = copy['collective2']
        self.assertIsInstance(collective2, dict)
        self.assertIn('approved_ids', collective2)
        if not collective2.get('approved_ids'):
            self.assertFalse(collective2.get('approved_for_paper_copy'))
        lowered = json.dumps(copy).lower()
        self.assertNotIn('per_signal', lowered)
        self.assertNotIn('provider_pnl', lowered)

    def test_unauthenticated_sinais_and_api_match_sinais_gate(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                sinais_unauth = _unauthenticated_panel_status(base, '/sinais')
                self.assertNotEqual(sinais_unauth, 200)
                with self.assertRaises(HTTPError) as err:
                    urlopen(base + '/api/signals', timeout=3)
                self.assertEqual(err.exception.code, 401)
            finally:
                self._shutdown(server, thread)

    def test_sinais_auth_empty_copy_audit_strings_and_collective2(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                req = _get(base + '/sinais', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn(N51_PREAPPROVAL_SECTION, body)
                self.assertIn(N50_OPERATING_SECTION, body)
                self.assertIn(N48_SECTION_AUDIT, body)
                self.assertIn(N50_C2_SECTION, body)
                self.assertLess(body.index(N51_PREAPPROVAL_SECTION), body.index(N50_OPERATING_SECTION))
                self.assertLess(body.index(N50_OPERATING_SECTION), body.index(N48_SECTION_AUDIT))
                self.assertLess(body.index(N50_C2_SECTION), body.index(N48_SECTION_AUDIT))
                self.assertIn(N48_COPY_EMPTY, body)
                self.assertIn(N48_COPY_PERF_EMPTY, body)
                self.assertIn(N50_C2_EMPTY, body)
                self.assertIn(N48_AUDIT_EMPTY, body)
                self.assertIn(N48_AUDIT_SUBTITLE, body)
                self.assertIn(N48_COPY_SUBTITLE, body)
                self.assertIn(N48_FOOTER, body)
            finally:
                self._shutdown(server, thread)

    def test_sinais_fixture_copy_sections_and_audit_feature9(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_signal_copy_panel_fixture(root)
            server, thread, base = self._server(root)
            try:
                req = _get(base + '/sinais', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn(N50_C2_EMPTY, body)
                self.assertIn(PERFORMANCE_LABEL_GROSS, body)
                self.assertIn('AAPL', body)
                self.assertIn('MSFT', body)
                self.assertNotIn(N48_COPY_EMPTY, body)
                self.assertNotIn('TSLA', body)
                audit_region = body.split(N48_SECTION_AUDIT, 1)[-1]
                self.assertIn('tradingview', audit_region)
                self.assertIn('blocked', audit_region)
                self.assertIn('MAX_POSITIONS', audit_region)
                lowered = body.lower()
                self.assertNotIn('por sinal', lowered)
                self.assertNotIn('p&l por provedor', lowered)
            finally:
                self._shutdown(server, thread)

    def test_api_signals_fixture_copy_object_and_feature9_signals(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_signal_copy_panel_fixture(root)
            server, thread, base = self._server(root)
            try:
                req = _get(base + '/api/signals', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    payload = json.load(resp)
                signals = payload['signals']
                self.assertEqual(len(signals), 1)
                row = signals[0]
                self.assertEqual(row['origin'], 'tradingview')
                self.assertEqual(row['destination'], 'blocked')
                self.assertEqual(row['reject_reason'], 'MAX_POSITIONS')
                copy = payload['copy']
                self._assert_copy_object_shape(copy)
                operating_syms = {r.get('symbol') for r in copy['operating']}
                history_syms = {r.get('symbol') for r in copy['history']}
                self.assertIn('AAPL', operating_syms)
                self.assertIn('MSFT', history_syms)
                self.assertNotIn('NVDA', history_syms)
                self.assertIn('NVDA', operating_syms)
                perf = copy['performance']
                self.assertEqual(perf.get('pnl_label'), PERFORMANCE_LABEL_GROSS)
                by_key = {r['strategy_key']: r for r in perf.get('strategies', [])}
                self.assertIn('signal_copy', by_key)
                self.assertNotIn('momentum', by_key)
            finally:
                self._shutdown(server, thread)

    def test_api_signals_research_copies_not_merged_into_operating(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_prodigy_research_copy(root)
            _clear_order_snapshots(root)
            server, thread, base = self._server(root)
            try:
                req = _get(base + '/api/signals', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    payload = json.load(resp)
                copy = payload['copy']
                self._assert_copy_object_shape(copy)
                self.assertEqual(copy['operating'], [])
                research = copy.get('research_copies') or []
                research_syms = {r.get('symbol') for r in research}
                self.assertIn('META', research_syms)
                operating_syms = {r.get('symbol') for r in copy['operating']}
                self.assertNotIn('META', operating_syms)
            finally:
                self._shutdown(server, thread)

    def test_sinais_page_no_order_submit_and_no_copy_route(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                req = _get(base + '/sinais', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                lowered = body.lower()
                self.assertNotIn('href="/copy"', body)
                self.assertNotIn('process_after_gate_b', body)
                self.assertNotIn('method="post"', lowered)
                self.assertNotIn('enviar ordem', lowered)
                nav_req = _get(base + '/central', session='panel-secret')
                with urlopen(nav_req, timeout=3) as nav_resp:
                    nav = nav_resp.read().decode('utf-8')
                self.assertNotIn('href="/copy"', nav)
            finally:
                self._shutdown(server, thread)

    def test_n49_unknown_provenance_strings_on_operating_rows(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_signal_copy_panel_fixture(root)
            server, thread, base = self._server(root)
            try:
                req = _get(base + '/sinais', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn('origem desconhecida', body)
                self.assertIn('sem vínculo com sinal', body)
            finally:
                self._shutdown(server, thread)

    def test_n49_linked_provenance_with_signal_orders_overlay(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_signal_copy_panel_fixture(root)
            _write_signal_orders_journal(
                root,
                [
                    {
                        'client_order_id': 'copy-open-aapl',
                        'provider': 'tradingview',
                        'signal_id': 'abc123hashed',
                    },
                ],
            )
            server, thread, base = self._server(root)
            try:
                req = _get(base + '/api/signals', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    payload = json.load(resp)
                operating = payload['copy']['operating']
                aapl = next(r for r in operating if r.get('symbol') == 'AAPL')
                self.assertEqual(aapl.get('origin'), 'tradingview')
                self.assertEqual(aapl.get('signal_id'), 'abc123hashed')
                self.assertEqual(aapl.get('provenance_status'), 'linked')
            finally:
                self._shutdown(server, thread)

    def test_n49_adoption_inventory_pool_api_shape(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_prodigy_pool_fixture(root)
            server, thread, base = self._server(root)
            try:
                req = _get(base + '/api/signals', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    payload = json.load(resp)
                copy = payload['copy']
                self._assert_copy_object_shape(copy)
                adoption = copy['adoption']
                joined = ' '.join(adoption.get('criteria_pt') or [])
                self.assertIn('15 dias', joined)
                self.assertIn('5 operações', joined)
                self.assertIn('3 dias', joined)
                self.assertIn('R$ 20', joined)
                self.assertFalse(adoption.get('auto_promote'))
                pool = copy['prodigy_pool']
                self.assertTrue(pool.get('items'))
                self.assertEqual((pool['items'][0].get('label') or ''), 'research_tip')
                inventory = copy['inventory']
                self.assertEqual(inventory.get('empty_label'), 'Nenhum sinal neste inventário.')
            finally:
                self._shutdown(server, thread)

    def test_n49_sinais_html_sections_visible(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                req = _get(base + '/sinais', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn('Critérios de adoção', body)
                self.assertIn('Inventário de sinais', body)
                self.assertIn(N50_POOL_SECTION, body)
                self.assertIn(N50_OPERATING_SECTION, body)
                self.assertIn(N48_SECTION_AUDIT, body)
            finally:
                self._shutdown(server, thread)

    def test_regression_menu_routes_still_render_after_n48_sinais_copy(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                cases = (
                    ('/sinais', N50_OPERATING_SECTION),
                    ('/ordens', 'Ordens'),
                    ('/historico', 'Histórico'),
                    ('/estrategias', 'Estratégias'),
                    ('/performance', PERFORMANCE_LABEL_GROSS),
                    ('/central', 'Central'),
                    ('/prodigy', 'Prodígio'),
                )
                for path, needle in cases:
                    with self.subTest(path=path):
                        req = _get(base + path, session='panel-secret')
                        with urlopen(req, timeout=3) as resp:
                            body = resp.read().decode('utf-8')
                        self.assertIn(needle, body)
            finally:
                self._shutdown(server, thread)


class PanelSinaisN50HttpTests(unittest.TestCase):
    """N50 — named C2 allowlist, section order, prodigy provider_id."""

    def setUp(self):
        self._panel_tests = PanelSinaisCopyAuditHttpTests()
        self._panel_tests.setUp()

    def tearDown(self):
        self._panel_tests.tearDown()

    def _server(self, root=None):
        return self._panel_tests._server(root)

    def _shutdown(self, server, thread):
        self._panel_tests._shutdown(server, thread)

    def test_n50_empty_allowlist_collective2_closed_api(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_allowlist_fixture(root, [])
            server, thread, base = self._server(root)
            try:
                req = _get(base + '/api/signals', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    payload = json.load(resp)
                c2 = payload['copy']['collective2']
                self.assertEqual(c2.get('approved_ids'), [])
                self.assertFalse(c2.get('approved_for_paper_copy'))
                self.assertEqual(c2.get('status'), 'closed')
            finally:
                self._shutdown(server, thread)

    def test_n50_one_named_id_allowlist_only_that_id(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_allowlist_fixture(root, ['12345', '67890'])
            server, thread, base = self._server(root)
            try:
                req = _get(base + '/api/signals', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    payload = json.load(resp)
                c2 = payload['copy']['collective2']
                self.assertEqual(c2.get('approved_ids'), ['12345', '67890'])
                self.assertTrue(c2.get('approved_for_paper_copy'))
                self.assertEqual({s['provider_id'] for s in c2.get('subscribed') or []}, {'12345', '67890'})
                req_html = _get(base + '/sinais', session='panel-secret')
                with urlopen(req_html, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn(N50_C2_ALLOWLIST, body)
                self.assertIn('12345', body)
                self.assertNotIn('30415311', body)
            finally:
                self._shutdown(server, thread)

    def test_n50_prodigy_pool_provider_id_not_none(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_prodigy_pool_fixture(root, use_provider_id=True)
            bundle = build_panel_bundle(root, conn_factory=None)
            item = bundle['copy']['prodigy_pool']['items'][0]
            self.assertEqual(item.get('provider'), 'provider-77')
            server, thread, base = self._server(root)
            try:
                req = _get(base + '/prodigy', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn('provider-77', body)
                self.assertNotIn('>None<', body)
            finally:
                self._shutdown(server, thread)

    def test_n50_c2_snapshot_not_ticket(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_active_orders_snapshot(root)
            bundle = build_panel_bundle(root, conn_factory=None)
            snap = bundle['copy']['collective2'].get('active_orders_snapshot')
            self.assertIsInstance(snap, dict)
            self.assertFalse(snap.get('execution_authorized'))
            self.assertEqual(snap.get('active_orders_count'), 1)

    def test_n50_load_c2_ids_env_overlay(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_allowlist_fixture(root, ['100'])
            with patch.dict(os.environ, {'C2_PAPER_COPY_APPROVED_IDS': '200,abc,300'}):
                ids = load_c2_paper_copy_approved_ids(root)
            self.assertEqual(ids, ['100', '200', '300'])


class PanelKillSwitchCycleTests(unittest.TestCase):
    def test_kill_switch_from_panel_blocks_next_eval(self):
        import sys

        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import test_panel_triggers as pt
        from v4_web_dashboard import apply_trigger_patch

        store = pt._default_store()
        conn_factory = pt._memory_connect(store)

        with conn_factory() as conn:
            updated, err = apply_trigger_patch(conn, {'kill_switch_on': True})
            conn.commit()
        self.assertIsNone(err)
        self.assertTrue(updated['kill_switch_on'])
        sig = {
            'provider': 'tradingview',
            'signal_id': 'KS1',
            'symbol': 'AAPL',
            'side': 'buy',
            'asset_class': 'us_equity',
            'entry': '100',
            'stop': '99',
            'target': '102',
            'quantity': 1,
            'strategy_key': 'signal_copy',
        }
        def kill_from_store(env=None):
            return bool(store['control_flags']['kill_switch_on'])

        with patch('gate_b_risk.kill_switch_active', kill_from_store):
            decision = evaluate_signed_signal(
                sig,
                fx=Decimal('5'),
                strategy_phase='paper_limited',
                conn_factory=conn_factory,
            )
        self.assertEqual(decision['reject_code'], 'KILL_SWITCH')


N51_PREAPPROVAL_SECTION = 'Pré-aprovação de provedores'
N51_PREAPPROVAL_EMPTY = (
    'Nenhum provedor aguardando análise no momento. Novos candidatos aparecerão aqui.'
)
N52_PREAPPROVAL_METRIC_SNIPPETS = (
    'Percentual de acertos (pesquisa)',
    'Acertos encolhidos % (pesquisa)',
    'Fator de lucro (pesquisa)',
    'Resultado reportado (pesquisa)',
    'Retorno líquido % (pesquisa)',
    'Drawdown máximo % (pesquisa)',
    'Score Prodígio (pesquisa)',
    'Score (pesquisa)',
    'Status (pesquisa)',
)


class PanelSinaisN51Tests(unittest.TestCase):
    def _server(self, root, *, connect_factory=None, session='panel-secret'):
        handler = make_handler(
            root,
            operator_session=session,
            connect_factory=connect_factory,
        )
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:' + str(server.server_port)
        return server, thread, base

    def _shutdown(self, server, thread):
        server.shutdown()
        server.server_close()
        thread.join(3)

    def test_n51_preapproval_metrics_reused_not_zero(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_research_fixture(root, provider_id='777', win_rate=61.2)
            queue = build_preapproval_queue(root, None, signals=[])
            item = queue['queue'][0]
            self.assertEqual(item['metrics']['win_rate_pct'], 61.2)
            self.assertEqual(item['metrics_label'], PREAPPROVAL_METRICS_LABEL)
            self.assertNotIn('eligible', item['metrics'])

    def test_n51_tradingview_without_rank_unavailable(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            signals = [{'origin': 'tradingview:alerts', 'source': 'tradingview', 'symbol': 'SPY'}]
            queue = build_preapproval_queue(root, None, signals=signals)
            tv = [r for r in queue['queue'] if r['platform'] == 'tradingview'][0]
            self.assertEqual(tv['metrics'], {})

    def test_n51_reject_beats_seed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_allowlist_fixture(root, ['100'])
            store = {'signal_provider_approvals': {}}
            conn = _approvals_memory_connect(store)
            upsert_signal_provider_approval(conn, 'collective2', '100', 'reject')
            ids = resolve_c2_paper_copy_approved_ids(root, conn)
            self.assertNotIn('100', ids)

    def test_cq001_collective2_non_numeric_approve_invalid_body(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            store = {'signal_provider_approvals': {}}
            conn = _approvals_memory_connect(store)
            with self.assertRaises(ValueError) as err:
                upsert_signal_provider_approval(conn, 'collective2', 'bad-id', 'approve')
            self.assertEqual(str(err.exception), 'INVALID_BODY')
            bundle = build_panel_bundle(root, conn)
            self.assertIsInstance(bundle, dict)
            self.assertIn('copy', bundle)

    def test_cq001_resolve_c2_sort_tolerates_non_digit_ledger_ids(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            store = {
                'signal_provider_approvals': {
                    ('collective2', '2'): {
                        'platform': 'collective2',
                        'provider_id': '2',
                        'status': 'approved',
                        'source': 'panel',
                    },
                    ('collective2', 'legacy-name'): {
                        'platform': 'collective2',
                        'provider_id': 'legacy-name',
                        'status': 'approved',
                        'source': 'panel',
                    },
                },
            }
            conn = _approvals_memory_connect(store)
            ids = resolve_c2_paper_copy_approved_ids(root, conn)
            self.assertEqual(ids, ['2', 'legacy-name'])

    def test_n51_seed_without_ledger_still_eligible(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_allowlist_fixture(root, ['200'])
            ids = resolve_c2_paper_copy_approved_ids(root, None)
            self.assertEqual(ids, ['200'])

    def test_n51_html_preapproval_section(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_research_fixture(root)
            server, thread, base = self._server(root)
            try:
                req = _get(base + '/sinais', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn(N51_PREAPPROVAL_SECTION, body)
                self.assertIn('55.0', body)
                self.assertIn('Aprovar', body)
            finally:
                self._shutdown(server, thread)

    def test_n51_post_providers_requires_session(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            server, thread, base = self._server(root)
            try:
                req = _post(
                    base + '/api/signals/providers',
                    {'platform': 'collective2', 'provider_id': '1', 'action': 'approve'},
                )
                with self.assertRaises(HTTPError) as caught:
                    urlopen(req, timeout=3)
                self.assertEqual(caught.exception.code, 401)
            finally:
                self._shutdown(server, thread)

    def test_n51_post_providers_persists_approve(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            store = {'signal_provider_approvals': {}}
            server, thread, base = self._server(root, connect_factory=_approvals_memory_connect(store))
            try:
                req = _post(
                    base + '/api/signals/providers',
                    {'platform': 'collective2', 'provider_id': '42', 'action': 'approve'},
                    session='panel-secret',
                )
                with urlopen(req, timeout=3) as resp:
                    payload = json.loads(resp.read().decode('utf-8'))
                self.assertEqual(payload['status'], 'approved')
                self.assertFalse(payload.get('execution_authorized'))
                self.assertEqual(payload.get('orders_sent'), 0)
                key = ('collective2', '42')
                self.assertEqual(store['signal_provider_approvals'][key]['status'], 'approved')
            finally:
                self._shutdown(server, thread)

    def test_n51_post_root_still_read_only(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            server, thread, base = self._server(root)
            try:
                req = _post(base + '/api/orders', {}, session='panel-secret')
                with self.assertRaises(HTTPError) as caught:
                    urlopen(req, timeout=3)
                self.assertEqual(caught.exception.code, 405)
            finally:
                self._shutdown(server, thread)

    def test_n51_api_signals_json_preapproval(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_research_fixture(root)
            server, thread, base = self._server(root)
            try:
                req = _get(base + '/api/signals', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    payload = json.loads(resp.read().decode('utf-8'))
                pre = payload['copy']['preapproval']
                self.assertIn('queue', pre)
                self.assertTrue(pre['queue'])
            finally:
                self._shutdown(server, thread)


class PanelSinaisN52Tests(unittest.TestCase):
    def setUp(self):
        self._ledger_env = patch.dict(os.environ, {'LEDGER_DATABASE_URL': ''}, clear=False)
        self._ledger_env.start()

    def tearDown(self):
        self._ledger_env.stop()

    def _server(self, root, *, connect_factory=None, session='panel-secret'):
        handler = make_handler(
            root,
            operator_session=session,
            connect_factory=connect_factory,
        )
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:' + str(server.server_port)
        return server, thread, base

    def _shutdown(self, server, thread):
        server.shutdown()
        server.server_close()
        thread.join(3)

    def test_n52_unauthenticated_sinais_and_provider_post(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                sinais_unauth = _unauthenticated_panel_status(base, '/sinais')
                self.assertNotEqual(sinais_unauth, 200)
                req = _post(
                    base + '/api/signals/providers',
                    {'platform': 'collective2', 'provider_id': '1', 'action': 'approve'},
                )
                with self.assertRaises(HTTPError) as caught:
                    urlopen(req, timeout=3)
                self.assertEqual(caught.exception.code, 401)
            finally:
                self._shutdown(server, thread)

    def test_n52_empty_preapproval_humanized(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # Isolate from repo intelligence/ allowlist fallback and CI ledger.
            with patch('panel_ops_data._repo_config_root', return_value=root):
                server, thread, base = self._server(root)
                try:
                    req = _get(base + '/sinais', session='panel-secret')
                    with urlopen(req, timeout=3) as resp:
                        body = resp.read().decode('utf-8')
                    self.assertIn(N51_PREAPPROVAL_EMPTY, body)
                    self.assertIn('empty-state', body)
                finally:
                    self._shutdown(server, thread)

    def test_n52_preapproval_research_metrics_visible(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            intel = root / 'intelligence'
            intel.mkdir(parents=True, exist_ok=True)
            (intel / 'provider-research-top10-latest.json').write_text(
                json.dumps(
                    {
                        'top_10_research': [
                            {
                                'provider_id': '132169',
                                'win_rate_pct': 65.4,
                                'profit_factor_reported': 1.82,
                                'max_drawdown_pct': -12.4,
                            }
                        ]
                    }
                ),
                encoding='utf-8',
            )
            server, thread, base = self._server(root)
            try:
                req = _get(base + '/sinais', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn('metrics-block', body)
                self.assertIn('65.4', body)
                self.assertIn('1.82', body)
                self.assertIn('-12.4', body)
                self.assertIn('pesquisa', body)
                for snippet in N52_PREAPPROVAL_METRIC_SNIPPETS:
                    self.assertIn(snippet, body)
            finally:
                self._shutdown(server, thread)

    def test_n52_missing_metric_shows_indisponivel_not_zero(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_research_fixture(root, provider_id='304', win_rate=50.0)
            server, thread, base = self._server(root)
            try:
                req = _get(base + '/sinais', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                idx_net = body.find('Retorno líquido % (pesquisa)')
                self.assertGreater(idx_net, -1)
                chunk = body[idx_net : idx_net + 120]
                self.assertIn('indisponível', chunk)
                self.assertNotRegex(
                    chunk,
                    r'Retorno líquido % \(pesquisa\):\s*</strong>\s*0\b',
                )
            finally:
                self._shutdown(server, thread)

    def test_n52_html_section_hierarchy_decision_first(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_research_fixture(root)
            server, thread, base = self._server(root)
            try:
                req = _get(base + '/sinais', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertLess(
                    body.index(N51_PREAPPROVAL_SECTION),
                    body.index(N50_OPERATING_SECTION),
                )
                self.assertLess(
                    body.index(N50_OPERATING_SECTION),
                    body.index(N48_SECTION_AUDIT),
                )
            finally:
                self._shutdown(server, thread)

    def test_n52_design_tokens_and_no_order_submit_in_sinais(self):
        with tempfile.TemporaryDirectory() as d:
            server, thread, base = self._server(d)
            try:
                req = _get(base + '/sinais', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    sinais = resp.read().decode('utf-8')
                self.assertIn('--bg-canvas', sinais)
                self.assertIn('--color-canvas', sinais)
                self.assertIn('metrics-block', sinais)
                self.assertNotIn('process_after_gate_b', sinais)
                self.assertNotIn('method="post"', sinais.lower())
                req_c = _get(base + '/central', session='panel-secret')
                with urlopen(req_c, timeout=3) as resp:
                    central = resp.read().decode('utf-8')
                self.assertIn('brake-strip--active', central)
                self.assertIn('--bg-canvas', central)
                self.assertIn('panel-topbar', central)
            finally:
                self._shutdown(server, thread)


class N53PanelShellRefreshTests(unittest.TestCase):
    """ISS-023: PanelShell v2 + honest GET /api/signals/reload."""

    def _server(self, root=None, session='panel-secret'):
        root = Path(root or tempfile.mkdtemp())
        handler = make_handler(root, operator_session=session)
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:' + str(server.server_port)
        return root, server, thread, base

    def _shutdown(self, server, thread):
        server.shutdown()
        server.server_close()
        thread.join(3)

    def test_n53_panel_shell_tokens_across_menu_routes(self):
        with tempfile.TemporaryDirectory() as d:
            _, server, thread, base = self._server(d)
            try:
                for path in ('/', '/ordens', '/historico', '/sinais', '/estrategias', '/prodigy', '/performance', '/analise-google'):
                    with self.subTest(path=path):
                        req = _get(base + path, session='panel-secret')
                        with urlopen(req, timeout=3) as resp:
                            body = resp.read().decode('utf-8')
                        self.assertIn('panel-shell', body)
                        self.assertIn('panel-topbar', body)
                        self.assertIn('Paper · Live desligado', body)
                        self.assertIn('--color-sidebar', body)
                        self.assertIn('nav-link', body)
            finally:
                self._shutdown(server, thread)

    def test_n53_login_uses_design_v2_card(self):
        with tempfile.TemporaryDirectory() as d:
            _, server, thread, base = self._server(d)
            try:
                req = _get(base + '/login')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn('login-card', body)
                self.assertIn('Paper · Live desligado', body)
                self.assertIn('--color-canvas', body)
                self.assertNotIn('<header class="panel-topbar"', body)
                self.assertNotIn('panel-shell', body.split('</style>', 1)[-1])
            finally:
                self._shutdown(server, thread)

    def test_n53_atualizar_candidatos_visible_on_sinais(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_research_fixture(root)
            _, server, thread, base = self._server(root)
            try:
                req = _get(base + '/sinais', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn('Atualizar candidatos', body)
                self.assertIn('id="reload-candidates"', body)
                self.assertIn('btn-outline', body)
                self.assertIn('/api/signals/candidates/refresh', body)
                self.assertIn('Prodígio 15d', body)
                self.assertIn('Rejeitar', body)
                self.assertNotIn('collective2.com', body.lower())
                self.assertNotIn('api4-general', body.lower())
                self.assertIn('aria-live="polite"', body)
                self.assertLess(
                    body.index(N51_PREAPPROVAL_SECTION),
                    body.index(N50_OPERATING_SECTION),
                )
                self.assertLess(
                    body.index(N50_OPERATING_SECTION),
                    body.index(N48_SECTION_AUDIT),
                )
            finally:
                self._shutdown(server, thread)

    def test_n53_reload_requires_session(self):
        with tempfile.TemporaryDirectory() as d:
            _, server, thread, base = self._server(d)
            try:
                with self.assertRaises(HTTPError) as err:
                    urlopen(base + '/api/signals/reload', timeout=3)
                self.assertEqual(err.exception.code, 401)
            finally:
                self._shutdown(server, thread)

    def test_n53_reload_rereads_bundle_json(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_research_fixture(root)
            _, server, thread, base = self._server(root)
            try:
                req = _get(base + '/api/signals/reload', session='panel-secret')
                with urlopen(req, timeout=3) as resp:
                    payload = json.load(resp)
                self.assertEqual(payload.get('status'), 'ok')
                self.assertTrue(payload.get('reload'))
                self.assertIn('copy', payload)
                self.assertIn('signals', payload)
                self.assertIn('message', payload)
            finally:
                self._shutdown(server, thread)

    def test_n53_no_prodigy_rank_calculate_in_panel_modules(self):
        html_src = (Path(__file__).resolve().parents[1] / 'src' / 'panel_ops_html.py').read_text(encoding='utf-8')
        dash_src = (Path(__file__).resolve().parents[1] / 'src' / 'v4_web_dashboard.py').read_text(encoding='utf-8')
        self.assertNotIn('prodigy_rank.calculate', html_src)
        reload_block = dash_src.split('def serve_signals_reload', 1)[-1].split('def serve_public_get', 1)[0]
        self.assertNotIn('prodigy_rank', reload_block)


def _post_candidates_refresh(url, body=None, *, session=None):
    headers = {}
    if session:
        headers['Cookie'] = 'trading_lab_session=' + session
    data = None
    if body is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(body).encode('utf-8')
    return Request(url, data=data, headers=headers, method='POST')


_N54_FAKE_RANK = {
    'mode': 'PRODIGY_RANK_RESEARCH_ONLY',
    'execution_authorized': False,
    'orders_sent': 0,
    'top_10_research': [
        {'provider_id': '9', 'status': 'PRODIGY_CANDIDATE_RESEARCH', 'prodigy_score': 0.55},
    ],
    'providers': [],
    'score_warning': 'Research rank only; does not authorize orders.',
}


def _n54_mock_c2_fetch(strategy_ids, key, out_dir, opener=None, **kwargs):
    del key
    label = str(strategy_ids or '')
    for k in ('path', 'endpoint', 'url'):
        if kwargs.get(k):
            label = str(kwargs[k])
    if 'SearchStrategies' in label:
        return {'status': 'ok', 'strategy_ids': [], 'next_cursor': '', 'written': []}
    del kwargs
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ids = sorted({str(x) for x in (strategy_ids or [])})
    if not ids:
        ids = ['44']
    written: list[str] = []
    for sid in ids:
        payload = {
            'strategy_id': sid,
            'dataset': 'closed_trades',
            'raw': {'ResponseStatus': {'ErrorCode': '200'}, 'Results': []},
        }
        name = f'{sid}_closed_trades.json'
        (out / name).write_text(json.dumps(payload), encoding='utf-8')
        written.append(name)
    return {'status': 'ok', 'written': written, 'opener_used': opener is not None}


def _n54_mock_c2_snapshot(strategy_ids, key, out_dir, opener=None, **kwargs):
    del strategy_ids, key, out_dir, kwargs
    return {
        'mode': 'C2_ACTIVE_ORDERS_READ_ONLY',
        'orders_sent': 0,
        'execution_authorized': False,
        'new_or_changed_count': 0,
        'opener_used': opener is not None,
    }


def _n54_write_prodigy_raw_trades(root: Path) -> None:
    raw = root / 'providers' / 'raw'
    raw.mkdir(parents=True, exist_ok=True)
    trades = [
        {'CloseDate': '2026-11-10T12:00:00+00:00', 'ProfitLoss': 120.0},
        {'CloseDate': '2026-11-11T12:00:00+00:00', 'ProfitLoss': -30.0},
        {'CloseDate': '2026-11-12T12:00:00+00:00', 'ProfitLoss': 80.0},
        {'CloseDate': '2026-11-13T12:00:00+00:00', 'ProfitLoss': 40.0},
        {'CloseDate': '2026-11-14T12:00:00+00:00', 'ProfitLoss': 25.0},
    ]
    payload = {
        'strategy_id': '9',
        'dataset': 'closed_trades',
        'raw': {'ResponseStatus': {'ErrorCode': '200'}, 'Results': trades},
    }
    (raw / '9_closed_trades.json').write_text(json.dumps(payload), encoding='utf-8')


def _n56_write_prodigy_raw_trades_doubled_legacy(root: Path) -> None:
    """Legacy doubled nest only — must not be read by live-criteria refresh."""
    raw = root / 'reports' / 'providers' / 'raw'
    raw.mkdir(parents=True, exist_ok=True)
    trades = [
        {'CloseDate': '2026-11-10T12:00:00+00:00', 'ProfitLoss': 120.0},
        {'CloseDate': '2026-11-11T12:00:00+00:00', 'ProfitLoss': -30.0},
        {'CloseDate': '2026-11-12T12:00:00+00:00', 'ProfitLoss': 80.0},
        {'CloseDate': '2026-11-13T12:00:00+00:00', 'ProfitLoss': 40.0},
        {'CloseDate': '2026-11-14T12:00:00+00:00', 'ProfitLoss': 25.0},
    ]
    payload = {
        'strategy_id': '9',
        'dataset': 'closed_trades',
        'raw': {'ResponseStatus': {'ErrorCode': '200'}, 'Results': trades},
    }
    (raw / '9_closed_trades.json').write_text(json.dumps(payload), encoding='utf-8')


class N54LiveCriteriaRefreshHttpTests(unittest.TestCase):
    """N54.1 — POST /api/signals/candidates/refresh + GET reload mode contract."""

    def setUp(self):
        self._ledger_env = patch.dict(os.environ, {'LEDGER_DATABASE_URL': ''}, clear=False)
        self._ledger_env.start()

    def tearDown(self):
        self._ledger_env.stop()

    def _server(self, root=None, session='panel-secret'):
        root = Path(root or tempfile.mkdtemp())
        handler = make_handler(root, operator_session=session)
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:' + str(server.server_port)
        return root, server, thread, base

    def _shutdown(self, server, thread):
        server.shutdown()
        server.server_close()
        thread.join(3)

    def test_n54_post_candidates_refresh_requires_session(self):
        with tempfile.TemporaryDirectory() as d:
            _, server, thread, base = self._server(d)
            try:
                req = _post_candidates_refresh(base + '/api/signals/candidates/refresh')
                with self.assertRaises(HTTPError) as err:
                    urlopen(req, timeout=3)
                self.assertEqual(err.exception.code, 401)
            finally:
                self._shutdown(server, thread)

    def test_n54_post_refresh_live_criteria_orders_sent_zero(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_research_fixture(root)
            _n54_write_prodigy_raw_trades(root)
            _, server, thread, base = self._server(root)
            patches = [
                patch('v4_web_dashboard.prodigy_rank.calculate', return_value=_N54_FAKE_RANK),
                patch('v4_web_dashboard.c2_history_collect.fetch', side_effect=_n54_mock_c2_fetch),
                patch('v4_web_dashboard.c2_signal_feed.snapshot', side_effect=_n54_mock_c2_snapshot),
                patch.dict(os.environ, {'C2_API4_KEY': 'test-c2-secret'}, clear=False),
            ]
            try:
                for p in patches:
                    p.start()
                req = _post_candidates_refresh(
                    base + '/api/signals/candidates/refresh',
                    {},
                    session='panel-secret',
                )
                with urlopen(req, timeout=5) as resp:
                    payload = json.load(resp)
                self.assertEqual(resp.status, 200)
                self.assertEqual(payload.get('mode'), 'live_criteria')
                self.assertEqual(payload.get('orders_sent'), 0)
                self.assertFalse(payload.get('execution_authorized', True))
                self.assertIn(payload.get('status'), ('ok', 'partial'))
                self.assertIn('copy', payload)
            finally:
                for p in reversed(patches):
                    p.stop()
                self._shutdown(server, thread)

    def test_n54_post_refresh_without_c2_key_partial_preserves_queue(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_research_fixture(root, provider_id='501', win_rate=58.0)
            _, server, thread, base = self._server(root)
            rank_mock = MagicMock(return_value=_N54_FAKE_RANK)
            env = {k: v for k, v in os.environ.items() if k != 'C2_API4_KEY'}
            patches = [
                patch('v4_web_dashboard.prodigy_rank.calculate', rank_mock),
                patch.dict(os.environ, env, clear=True),
            ]
            try:
                for p in patches:
                    p.start()
                before_req = _get(base + '/api/signals', session='panel-secret')
                with urlopen(before_req, timeout=3) as resp:
                    before = json.load(resp)
                queue_len = len((before.get('copy') or {}).get('preapproval', {}).get('queue') or [])
                self.assertGreater(queue_len, 0)
                req = _post_candidates_refresh(
                    base + '/api/signals/candidates/refresh',
                    {},
                    session='panel-secret',
                )
                with urlopen(req, timeout=5) as resp:
                    payload = json.load(resp)
                self.assertEqual(payload.get('mode'), 'live_criteria')
                self.assertEqual(payload.get('orders_sent'), 0)
                self.assertEqual(payload.get('status'), 'partial')
                issues = payload.get('issues') or []
                self.assertTrue(issues)
                after_req = _get(base + '/api/signals', session='panel-secret')
                with urlopen(after_req, timeout=3) as resp:
                    after = json.load(resp)
                after_queue = (after.get('copy') or {}).get('preapproval', {}).get('queue') or []
                self.assertGreaterEqual(len(after_queue), 1)
                provider_ids = {str(row.get('provider_id')) for row in after_queue if isinstance(row, dict)}
                self.assertIn('9', provider_ids)
                self.assertIn('C2_API4_KEY_missing', issues)
                rank_mock.assert_called_once()
                prodigy_path = root / 'intelligence' / 'prodigy-top10-latest.json'
                self.assertTrue(prodigy_path.is_file())
            finally:
                for p in reversed(patches):
                    p.stop()
                self._shutdown(server, thread)

    def test_n54_post_refresh_cooldown_ref_refresh_cooldown(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_research_fixture(root)
            _, server, thread, base = self._server(root)
            patches = [
                patch('v4_web_dashboard.prodigy_rank.calculate', return_value=_N54_FAKE_RANK),
                patch('v4_web_dashboard.c2_history_collect.fetch', side_effect=_n54_mock_c2_fetch),
                patch('v4_web_dashboard.c2_signal_feed.snapshot', side_effect=_n54_mock_c2_snapshot),
                patch.dict(os.environ, {'C2_API4_KEY': 'test-c2-secret'}, clear=False),
            ]
            try:
                for p in patches:
                    p.start()
                url = base + '/api/signals/candidates/refresh'
                first = _post_candidates_refresh(url, {}, session='panel-secret')
                with urlopen(first, timeout=5) as resp:
                    self.assertEqual(resp.status, 200)
                second = _post_candidates_refresh(url, {}, session='panel-secret')
                with self.assertRaises(HTTPError) as err:
                    urlopen(second, timeout=5)
                self.assertEqual(err.exception.code, 429)
                body = json.loads(err.exception.read().decode('utf-8'))
                self.assertEqual(body.get('reject_code'), 'REFRESH_COOLDOWN')
                self.assertEqual(body.get('mode'), 'live_criteria')
            finally:
                for p in reversed(patches):
                    p.stop()
                self._shutdown(server, thread)

    def test_n54_get_reload_disk_reread_skips_prodigy_calculate(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_research_fixture(root)
            _, server, thread, base = self._server(root)
            try:
                calculate_mock = MagicMock(
                    side_effect=AssertionError('prodigy_rank.calculate on GET reload'),
                )
                with patch('prodigy_rank.calculate', calculate_mock):
                    req = _get(base + '/api/signals/reload', session='panel-secret')
                    with urlopen(req, timeout=3) as resp:
                        payload = json.load(resp)
                calculate_mock.assert_not_called()
                self.assertEqual(payload.get('mode'), 'disk_reread')
                self.assertEqual(payload.get('orders_sent'), 0)
                self.assertFalse(payload.get('execution_authorized', True))
                self.assertEqual(payload.get('status'), 'ok')
                self.assertTrue(payload.get('reload'))
            finally:
                self._shutdown(server, thread)

    def test_n54_regression_providers_post_unchanged_after_refresh_route(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            store = {'signal_provider_approvals': {}}
            handler = make_handler(
                root,
                operator_session='panel-secret',
                connect_factory=_approvals_memory_connect(store),
            )
            server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = 'http://127.0.0.1:' + str(server.server_port)
            try:
                req = _post(
                    base + '/api/signals/providers',
                    {'platform': 'collective2', 'provider_id': '88', 'action': 'approve'},
                    session='panel-secret',
                )
                with urlopen(req, timeout=3) as resp:
                    payload = json.load(resp)
                self.assertEqual(payload.get('status'), 'approved')
                self.assertEqual(payload.get('orders_sent'), 0)
                self.assertFalse(payload.get('execution_authorized'))
            finally:
                server.shutdown()
                server.server_close()
                thread.join(3)


_N55_EMPTY_RANK = {
    'mode': 'PRODIGY_RANK_RESEARCH_ONLY',
    'execution_authorized': False,
    'orders_sent': 0,
    'top_10_research': [],
    'providers': [],
    'score_warning': 'Research rank only; does not authorize orders.',
}


def _n55_write_tradingview_ingest_fixture(root: Path) -> None:
    _write_webhook_journal(
        root,
        [
            {
                'payload': {
                    'provider': 'tradingview',
                    'symbol': 'SPY',
                    'market': 'US_EQUITY',
                },
                'result': {'status': 'rejected', 'reject_code': 'NO_TRADE'},
                'received_at': '2026-11-16T11:00:00+00:00',
            },
        ],
    )


def _n55_write_all_platform_fixtures(root: Path) -> None:
    _write_c2_research_fixture(root, provider_id='44', win_rate=56.0)
    _write_c2_allowlist_fixture(root, ['44'])
    _n54_write_prodigy_raw_trades(root)
    _n55_write_tradingview_ingest_fixture(root)


def _n55_preapproval_queue(payload: dict) -> list[dict]:
    return (payload.get('copy') or {}).get('preapproval', {}).get('queue') or []


def _n55_platforms_in_queue(queue: list[dict]) -> set[str]:
    return {str(row.get('platform')) for row in queue if isinstance(row, dict) and row.get('platform')}


def _n55_bundle_refresh_meta(copy: dict) -> dict:
    """N55.2 contract: persisted partial refresh survives GET /api/signals."""
    block = copy.get('candidates_refresh')
    if isinstance(block, dict) and block.get('issues') is not None:
        return block
    pre = copy.get('preapproval') or {}
    if pre.get('refresh_issues') is not None:
        return {
            'issues': pre.get('refresh_issues') or [],
            'status': pre.get('refresh_status'),
            'sources_ok': pre.get('refresh_sources_ok') or [],
        }
    raise AssertionError('expected copy.candidates_refresh (or preapproval.refresh_issues) on GET bundle')


def _n55_live_criteria_patch_stack(*, rank_return=_N54_FAKE_RANK, c2_key='test-c2-secret'):
    patches = [
        patch('v4_web_dashboard.prodigy_rank.calculate', return_value=rank_return),
        patch('v4_web_dashboard.c2_history_collect.fetch', side_effect=_n54_mock_c2_fetch),
        patch('v4_web_dashboard.c2_signal_feed.snapshot', side_effect=_n54_mock_c2_snapshot),
        patch.dict(
            os.environ,
            {'C2_API4_KEY': c2_key, 'LIVE_TRADING_ENABLED': 'false'},
            clear=False,
        ),
    ]
    return patches


def _n55_write_prodigy_rank_prior(root: Path, *, score: float = 0.71) -> tuple[dict, Path]:
    intel = root / 'intelligence'
    intel.mkdir(parents=True, exist_ok=True)
    prior = {
        'mode': 'PRODIGY_RANK_RESEARCH_ONLY',
        'execution_authorized': False,
        'orders_sent': 0,
        'top_10_research': [
            {
                'provider_id': '9',
                'status': 'PRODIGY_CANDIDATE_RESEARCH',
                'prodigy_score': score,
            },
        ],
    }
    path = intel / 'prodigy-top10-latest.json'
    path.write_text(json.dumps(prior), encoding='utf-8')
    return prior, path


class N55MultiPlatformLiveCriteriaTests(unittest.TestCase):
    """N55.3 — multi-platform preapproval queue + fail-closed per source."""

    def setUp(self):
        self._ledger_env = patch.dict(os.environ, {'LEDGER_DATABASE_URL': ''}, clear=False)
        self._ledger_env.start()
        self._cooldown_patch = patch(
            'v4_web_dashboard._live_criteria_cooldown_wait',
            return_value=0,
        )
        self._cooldown_patch.start()

    def tearDown(self):
        self._cooldown_patch.stop()
        self._ledger_env.stop()

    def _server(self, root=None, session='panel-secret'):
        root = Path(root or tempfile.mkdtemp())
        handler = make_handler(root, operator_session=session)
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:' + str(server.server_port)
        return root, server, thread, base

    def _shutdown(self, server, thread):
        server.shutdown()
        server.server_close()
        thread.join(3)

    def _post_refresh(self, base: str) -> dict:
        req = _post_candidates_refresh(
            base + '/api/signals/candidates/refresh',
            {},
            session='panel-secret',
        )
        with urlopen(req, timeout=5) as resp:
            return json.load(resp)

    def test_n55_refresh_queue_includes_collective2_prodigy_tradingview(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _n55_write_all_platform_fixtures(root)
            _, server, thread, base = self._server(root)
            patches = _n55_live_criteria_patch_stack()
            try:
                for p in patches:
                    p.start()
                payload = self._post_refresh(base)
                queue = _n55_preapproval_queue(payload)
                platforms = _n55_platforms_in_queue(queue)
                self.assertEqual(
                    platforms,
                    {'collective2', 'prodigy', 'tradingview'},
                    msg='preapproval queue must union all eligible platforms after live refresh',
                )
                c2_rows = [r for r in queue if r.get('platform') == 'collective2']
                prodigy_rows = [r for r in queue if r.get('platform') == 'prodigy']
                self.assertTrue(c2_rows)
                self.assertEqual(str(c2_rows[0].get('provider_id')), '44')
                self.assertTrue(prodigy_rows)
                self.assertEqual(prodigy_rows[0].get('provider_id'), '9')
                research_path = root / 'intelligence' / 'provider-research-top10-latest.json'
                c2_research = json.loads(research_path.read_text(encoding='utf-8'))
                top = (c2_research.get('top_10_research') or [{}])[0]
                self.assertEqual(str(top.get('provider_id')), '44')
            finally:
                for p in reversed(patches):
                    p.stop()
                self._shutdown(server, thread)

    def test_n55_missing_c2_key_issues_keep_other_platforms_and_prior_research(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_research_fixture(root, provider_id='44', win_rate=58.0)
            _n55_write_tradingview_ingest_fixture(root)
            _n55_write_prodigy_rank_prior(root)
            c2_path = root / 'intelligence' / 'provider-research-top10-latest.json'
            prior_c2_text = c2_path.read_text(encoding='utf-8')
            _, server, thread, base = self._server(root)
            env = {k: v for k, v in os.environ.items() if k != 'C2_API4_KEY'}
            env['LIVE_TRADING_ENABLED'] = 'false'
            patches = [
                patch('v4_web_dashboard.prodigy_rank.calculate', return_value=_N54_FAKE_RANK),
                patch.dict(os.environ, env, clear=True),
            ]
            try:
                for p in patches:
                    p.start()
                payload = self._post_refresh(base)
                self.assertEqual(payload.get('status'), 'partial')
                issues = payload.get('issues') or []
                self.assertIn('C2_API4_KEY_missing', issues)
                platforms = _n55_platforms_in_queue(_n55_preapproval_queue(payload))
                self.assertIn('prodigy', platforms)
                self.assertIn('tradingview', platforms)
                self.assertEqual(c2_path.read_text(encoding='utf-8'), prior_c2_text)
            finally:
                for p in reversed(patches):
                    p.stop()
                self._shutdown(server, thread)

    def test_n55_empty_prodigy_calculate_does_not_overwrite_prior_rank_json(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_research_fixture(root, provider_id='44', win_rate=57.0)
            _write_c2_allowlist_fixture(root, ['44'])
            _n55_write_tradingview_ingest_fixture(root)
            prior, prodigy_path = _n55_write_prodigy_rank_prior(root, score=0.63)
            prior_text = prodigy_path.read_text(encoding='utf-8')
            _, server, thread, base = self._server(root)
            patches = _n55_live_criteria_patch_stack(rank_return=_N55_EMPTY_RANK)
            try:
                for p in patches:
                    p.start()
                payload = self._post_refresh(base)
                self.assertEqual(payload.get('status'), 'partial')
                issues = payload.get('issues') or []
                self.assertTrue(issues)
                self.assertTrue(
                    any('closed_trades' in issue.lower() or 'raw' in issue.lower() for issue in issues),
                    msg='issues must name missing Prodígio raw provider files',
                )
                self.assertEqual(json.loads(prodigy_path.read_text(encoding='utf-8')), prior)
                self.assertEqual(prodigy_path.read_text(encoding='utf-8'), prior_text)
                platforms = _n55_platforms_in_queue(_n55_preapproval_queue(payload))
                self.assertIn('collective2', platforms)
                self.assertIn('tradingview', platforms)
            finally:
                for p in reversed(patches):
                    p.stop()
                self._shutdown(server, thread)

    def test_n55_tradingview_refresh_failure_records_issue_without_wiping_queue(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _n55_write_all_platform_fixtures(root)
            _, server, thread, base = self._server(root)

            def _tv_fail(root, conn_factory, sources_ok):
                del root, conn_factory, sources_ok
                raise OSError('tradingview_refresh_failed')

            patches = _n55_live_criteria_patch_stack()
            patches.append(patch('v4_web_dashboard._live_refresh_tradingview', side_effect=_tv_fail))
            try:
                for p in patches:
                    p.start()
                try:
                    payload = self._post_refresh(base)
                except Exception as exc:
                    self.fail(
                        'refresh must return 200 partial with issues when TradingView fails '
                        '(F-018), not drop the connection: %s' % exc,
                    )
                issues = payload.get('issues') or []
                self.assertEqual(payload.get('status'), 'partial')
                self.assertTrue(
                    any('tradingview' in issue.lower() for issue in issues),
                    msg='F-018: TradingView failures must surface in issues',
                )
                platforms = _n55_platforms_in_queue(_n55_preapproval_queue(payload))
                self.assertIn('collective2', platforms)
                self.assertIn('prodigy', platforms)
            finally:
                for p in reversed(patches):
                    p.stop()
                self._shutdown(server, thread)

    def test_cq002_collective2_non_numeric_strategy_id_partial_refresh(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_research_fixture(root, provider_id='bad-c2-id', win_rate=58.0)
            _n55_write_tradingview_ingest_fixture(root)
            _n55_write_prodigy_rank_prior(root)
            _, server, thread, base = self._server(root)
            patches = _n55_live_criteria_patch_stack()
            try:
                for p in patches:
                    p.start()
                try:
                    payload = self._post_refresh(base)
                except Exception as exc:
                    self.fail(
                        'refresh must stay fail-closed on bad C2 strategy id, not crash: %s' % exc,
                    )
                issues = payload.get('issues') or []
                self.assertEqual(payload.get('status'), 'partial')
                self.assertTrue(
                    any('collective2' in issue.lower() for issue in issues),
                    msg='bad C2 id must surface collective2_refresh_failed issue',
                )
                platforms = _n55_platforms_in_queue(_n55_preapproval_queue(payload))
                self.assertIn('prodigy', platforms)
                self.assertIn('tradingview', platforms)
            finally:
                for p in reversed(patches):
                    p.stop()
                self._shutdown(server, thread)

    def test_n55_partial_issues_persist_on_get_api_signals_after_refresh(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_research_fixture(root, provider_id='44', win_rate=59.0)
            _n55_write_prodigy_rank_prior(root)
            _n55_write_tradingview_ingest_fixture(root)
            _, server, thread, base = self._server(root)
            env = {k: v for k, v in os.environ.items() if k != 'C2_API4_KEY'}
            env['LIVE_TRADING_ENABLED'] = 'false'
            patches = [
                patch('v4_web_dashboard.prodigy_rank.calculate', return_value=_N54_FAKE_RANK),
                patch.dict(os.environ, env, clear=True),
            ]
            try:
                for p in patches:
                    p.start()
                self._post_refresh(base)
                with urlopen(_get(base + '/api/signals', session='panel-secret'), timeout=3) as resp:
                    after = json.load(resp)
                meta = _n55_bundle_refresh_meta(after.get('copy') or {})
                persisted = meta.get('issues') or []
                self.assertIn('C2_API4_KEY_missing', persisted)
                self.assertIn(meta.get('status'), ('partial', 'ok', None))
            finally:
                for p in reversed(patches):
                    p.stop()
                self._shutdown(server, thread)

    def test_n55_partial_warning_rendered_on_sinais_from_bundle(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_research_fixture(root, provider_id='44', win_rate=59.0)
            _n55_write_prodigy_rank_prior(root)
            _n55_write_tradingview_ingest_fixture(root)
            _, server, thread, base = self._server(root)
            env = {k: v for k, v in os.environ.items() if k != 'C2_API4_KEY'}
            env['LIVE_TRADING_ENABLED'] = 'false'
            patches = [
                patch('v4_web_dashboard.prodigy_rank.calculate', return_value=_N54_FAKE_RANK),
                patch.dict(os.environ, env, clear=True),
            ]
            try:
                for p in patches:
                    p.start()
                self._post_refresh(base)
                with urlopen(_get(base + '/sinais', session='panel-secret'), timeout=3) as resp:
                    body = resp.read().decode('utf-8')
                self.assertIn('C2_API4_KEY_missing', body)
                self.assertNotIn('test-c2-secret', body)
                self.assertNotIn('collective2.com', body.lower())
            finally:
                for p in reversed(patches):
                    p.stop()
                self._shutdown(server, thread)

    def test_n55_live_refresh_never_calls_process_after_gate_b(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _n55_write_all_platform_fixtures(root)
            _, server, thread, base = self._server(root)
            gate_mock = MagicMock(side_effect=AssertionError('process_after_gate_b'))
            patches = _n55_live_criteria_patch_stack()
            patches.append(patch('paper_gateway_queue.process_after_gate_b', gate_mock))
            try:
                for p in patches:
                    p.start()
                payload = self._post_refresh(base)
                gate_mock.assert_not_called()
                self.assertEqual(payload.get('orders_sent'), 0)
                self.assertFalse(payload.get('execution_authorized', True))
            finally:
                for p in reversed(patches):
                    p.stop()
                self._shutdown(server, thread)


def _n56_prodigy_now() -> datetime:
    return datetime(2026, 11, 16, 12, 0, tzinfo=timezone.utc)


def _n56_write_closed_trades_file(raw_dir: Path, strategy_id: str, trades: list[dict]) -> None:
    raw_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        'strategy_id': strategy_id,
        'dataset': 'closed_trades',
        'raw': {'ResponseStatus': {'ErrorCode': '200'}, 'Results': trades},
    }
    (raw_dir / f'{strategy_id}_closed_trades.json').write_text(json.dumps(payload), encoding='utf-8')


def _n56_write_prodigy_raw_eligible_canonical(root: Path, *, strategy_id: str = '9') -> Path:
    """Production layout: tmp root == REPORTS_DIR; raw under root/providers/raw."""
    raw = root / 'providers' / 'raw'
    trades = [
        {'CloseDate': '2026-11-10T12:00:00+00:00', 'ProfitLoss': 120.0},
        {'CloseDate': '2026-11-11T12:00:00+00:00', 'ProfitLoss': -30.0},
        {'CloseDate': '2026-11-12T12:00:00+00:00', 'ProfitLoss': 80.0},
        {'CloseDate': '2026-11-13T12:00:00+00:00', 'ProfitLoss': 40.0},
        {'CloseDate': '2026-11-14T12:00:00+00:00', 'ProfitLoss': 25.0},
    ]
    _n56_write_closed_trades_file(raw, strategy_id, trades)
    return raw


def _n56_write_prodigy_raw_unscorable_canonical(root: Path, strategy_id: str) -> None:
    """Characterizing: trades outside 15d window → UNSCORABLE, closed_trades_15d=0 (not queue-eligible)."""
    raw = root / 'providers' / 'raw'
    now = _n56_prodigy_now()
    trades = [
        {'CloseDate': (now - timedelta(days=190)).isoformat(), 'ProfitLoss': 100.0}
        for _ in range(5)
    ]
    _n56_write_closed_trades_file(raw, strategy_id, trades)


def _n56_assert_calculate_raw_dir(calculate_mock, root: Path) -> Path:
    if not calculate_mock.call_args:
        raise AssertionError('prodigy_rank.calculate was not called')
    args, kwargs = calculate_mock.call_args
    raw_dir = kwargs.get('raw_dir') if kwargs.get('raw_dir') is not None else args[0]
    canonical = (root / 'providers' / 'raw').resolve()
    resolved = Path(raw_dir).resolve()
    if resolved != canonical:
        doubled = (root / 'reports' / 'providers' / 'raw').resolve()
        raise AssertionError(
            'calculate must read {}/providers/raw (got {!r}; doubled nest was {!r})'.format(
                root, resolved, doubled,
            )
        )
    return canonical


def _n56_rank_from_calc_call(calculate_mock, calculate_fn):
    """Use wrapped return_value when set — re-calling calculate reads raw after C2 refresh."""
    if not calculate_mock.call_args:
        raise AssertionError('prodigy_rank.calculate was not called')
    if calculate_mock._mock_wraps is not None:
        ranked = calculate_mock.return_value
        if isinstance(ranked, dict):
            return ranked
    args, kwargs = calculate_mock.call_args
    return calculate_fn(*args, **kwargs)


class N56ProdigyCanonicalRawPathTests(unittest.TestCase):
    """N56.2 — live refresh reads {root}/providers/raw under production --root layout."""

    def setUp(self):
        self._ledger_env = patch.dict(os.environ, {'LEDGER_DATABASE_URL': ''}, clear=False)
        self._ledger_env.start()
        self._cooldown_patch = patch(
            'v4_web_dashboard._live_criteria_cooldown_wait',
            return_value=0,
        )
        self._cooldown_patch.start()
        from prodigy_rank import calculate as prodigy_calculate

        self._prodigy_calculate = prodigy_calculate

    def tearDown(self):
        self._cooldown_patch.stop()
        self._ledger_env.stop()

    def _server(self, root=None, session='panel-secret'):
        root = Path(root or tempfile.mkdtemp())
        handler = make_handler(root, operator_session=session)
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:' + str(server.server_port)
        return root, server, thread, base

    def _shutdown(self, server, thread):
        server.shutdown()
        server.server_close()
        thread.join(3)

    def _post_refresh(self, base: str) -> dict:
        req = _post_candidates_refresh(
            base + '/api/signals/candidates/refresh',
            {},
            session='panel-secret',
        )
        with urlopen(req, timeout=5) as resp:
            return json.load(resp)

    def test_n56_refresh_calculate_sees_canonical_raw_providers_gt_zero(self):
        """Files only at root/providers/raw; empty root/reports/providers/raw must not block."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _n56_write_prodigy_raw_eligible_canonical(root)
            doubled = root / 'reports' / 'providers' / 'raw'
            doubled.mkdir(parents=True, exist_ok=True)
            _write_c2_research_fixture(root, provider_id='44', win_rate=56.0)
            _, server, thread, base = self._server(root)
            patches = [
                patch('v4_web_dashboard.c2_history_collect.fetch', side_effect=_n54_mock_c2_fetch),
                patch('v4_web_dashboard.c2_signal_feed.snapshot', side_effect=_n54_mock_c2_snapshot),
                patch.dict(
                    os.environ,
                    {'C2_API4_KEY': 'test-c2-secret', 'LIVE_TRADING_ENABLED': 'false'},
                    clear=False,
                ),
            ]
            try:
                for p in patches:
                    p.start()
                with patch(
                    'v4_web_dashboard.prodigy_rank.calculate',
                    wraps=self._prodigy_calculate,
                ) as calc_mock:
                    payload = self._post_refresh(base)
                    self.assertEqual(payload.get('orders_sent'), 0)
                    _n56_assert_calculate_raw_dir(calc_mock, root)
                    rank = _n56_rank_from_calc_call(calc_mock, self._prodigy_calculate)
                    self.assertGreater(
                        len(rank.get('providers') or []),
                        0,
                        msg='canonical closed_trades files must feed calculate (providers>0)',
                    )
                    issues = payload.get('issues') or []
                    self.assertFalse(
                        any('prodigy_raw_missing' in issue for issue in issues),
                        msg='eligible raw on canonical path must not report prodigy_raw_missing',
                    )
            finally:
                for p in reversed(patches):
                    p.stop()
                self._shutdown(server, thread)

    def test_n56_doubled_reports_raw_alone_does_not_feed_calculate(self):
        """Only root/reports/providers/raw populated — canonical empty — must not count as success."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _n56_write_prodigy_raw_trades_doubled_legacy(root)
            canonical = root / 'providers' / 'raw'
            self.assertFalse(any(canonical.glob('*_closed_trades.json')))
            _write_c2_research_fixture(root, provider_id='44', win_rate=56.0)
            _, server, thread, base = self._server(root)
            patches = [
                patch('v4_web_dashboard.c2_history_collect.fetch', side_effect=_n54_mock_c2_fetch),
                patch('v4_web_dashboard.c2_signal_feed.snapshot', side_effect=_n54_mock_c2_snapshot),
                patch.dict(
                    os.environ,
                    {'C2_API4_KEY': 'test-c2-secret', 'LIVE_TRADING_ENABLED': 'false'},
                    clear=False,
                ),
            ]
            try:
                for p in patches:
                    p.start()
                captured_ranks: list[dict] = []

                def _capture_prodigy_calculate(*args, **kwargs):
                    rank = self._prodigy_calculate(*args, **kwargs)
                    captured_ranks.append(rank)
                    return rank

                with patch(
                    'v4_web_dashboard.prodigy_rank.calculate',
                    side_effect=_capture_prodigy_calculate,
                ) as calc_mock:
                    payload = self._post_refresh(base)
                    self.assertTrue(calc_mock.called)
                    _n56_assert_calculate_raw_dir(calc_mock, root)
                    self.assertEqual(len(captured_ranks), 1)
                    providers = captured_ranks[0].get('providers') or []
                    issues = payload.get('issues') or []
                    self.assertEqual(
                        len(providers),
                        0,
                        msg='canonical empty: doubled nest must not be the data source for calculate',
                    )
                    self.assertTrue(
                        any('prodigy_raw_missing' in issue for issue in issues),
                        msg='missing canonical raw files must surface prodigy_raw_missing',
                    )
            finally:
                for p in reversed(patches):
                    p.stop()
                self._shutdown(server, thread)

    def test_n56_unscorable_zero_15d_absent_from_queue_without_raw_missing(self):
        """UNSCORABLE + closed_trades_15d=0 on disk: no prodigy_raw_missing; not in preapproval queue."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for sid in ('101', '102', '103'):
                _n56_write_prodigy_raw_unscorable_canonical(root, sid)
            _write_c2_research_fixture(root, provider_id='44', win_rate=56.0)
            _write_c2_allowlist_fixture(root, ['44'])
            _n55_write_tradingview_ingest_fixture(root)
            _, server, thread, base = self._server(root)
            patches = [
                patch('v4_web_dashboard.c2_history_collect.fetch', side_effect=_n54_mock_c2_fetch),
                patch('v4_web_dashboard.c2_signal_feed.snapshot', side_effect=_n54_mock_c2_snapshot),
                patch.dict(
                    os.environ,
                    {'C2_API4_KEY': 'test-c2-secret', 'LIVE_TRADING_ENABLED': 'false'},
                    clear=False,
                ),
            ]
            try:
                for p in patches:
                    p.start()
                with patch(
                    'v4_web_dashboard.prodigy_rank.calculate',
                    wraps=self._prodigy_calculate,
                ) as calc_mock:
                    payload = self._post_refresh(base)
                    _n56_assert_calculate_raw_dir(calc_mock, root)
                    issues = payload.get('issues') or []
                    self.assertFalse(
                        any('prodigy_raw_missing' in issue for issue in issues),
                        msg='present but unscorable raw files are not missing-volume',
                    )
                    queue = _n55_preapproval_queue(payload)
                    prodigy_rows = [r for r in queue if r.get('platform') == 'prodigy']
                    self.assertEqual(
                        prodigy_rows,
                        [],
                        msg='UNSCORABLE closed_trades_15d=0 correctly absent from Prodígio preapproval queue',
                    )
                    rank = _n56_rank_from_calc_call(calc_mock, self._prodigy_calculate)
                    for row in rank.get('providers') or []:
                        if str(row.get('provider_id')) in {'101', '102', '103'}:
                            self.assertEqual(row.get('status'), 'UNSCORABLE')
                            self.assertEqual(row.get('closed_trades_15d'), 0)
            finally:
                for p in reversed(patches):
                    p.stop()
                self._shutdown(server, thread)


_N57_OPERATOR_C2_IDS = ('132169961', '148311109', '30415311')


def _n57_env_without_c2_paper_copy_ids() -> dict:
    env = {k: v for k, v in os.environ.items() if k != 'C2_PAPER_COPY_APPROVED_IDS'}
    env['LIVE_TRADING_ENABLED'] = 'false'
    return env


def _n57_write_operator_c2_raw_canonical(root: Path) -> None:
    raw = root / 'providers' / 'raw'
    for sid in _N57_OPERATOR_C2_IDS:
        _n56_write_closed_trades_file(raw, sid, [])


def _n57_pending_collective2_rows(queue_items: list[dict]) -> list[dict]:
    return [r for r in queue_items if r.get('platform') == 'collective2']


def _n57_assert_collective2_pending_discovered(test_case, rows: list[dict]) -> None:
    test_case.assertEqual(
        len(rows),
        len(_N57_OPERATOR_C2_IDS),
        msg='canonical raw must surface each Collective2 strategy id as a queue row',
    )
    ids = {str(r.get('provider_id')) for r in rows}
    test_case.assertEqual(ids, set(_N57_OPERATOR_C2_IDS))
    for row in rows:
        test_case.assertEqual(row.get('status'), 'pending')
        test_case.assertEqual(row.get('source'), 'discovered')


def _n57_post_live_refresh(base: str, prodigy_calculate):
    patches = [
        patch('v4_web_dashboard.c2_history_collect.fetch', side_effect=_n54_mock_c2_fetch),
        patch('v4_web_dashboard.c2_signal_feed.snapshot', side_effect=_n54_mock_c2_snapshot),
        patch.dict(
            os.environ,
            {**_n57_env_without_c2_paper_copy_ids(), 'C2_API4_KEY': 'test-c2-secret'},
            clear=True,
        ),
    ]
    for p in patches:
        p.start()
    try:
        with patch('v4_web_dashboard.prodigy_rank.calculate', wraps=prodigy_calculate) as calc_mock:
            req = _post_candidates_refresh(
                base + '/api/signals/candidates/refresh',
                {},
                session='panel-secret',
            )
            with urlopen(req, timeout=5) as resp:
                payload = json.load(resp)
            return payload, calc_mock
    finally:
        for p in reversed(patches):
            p.stop()


class N57Collective2RawQueueDiscoveryTests(unittest.TestCase):
    """N57.2 — Collective2 pending rows from canonical raw without allowlist show-prerequisite."""

    def setUp(self):
        self._ledger_env = patch.dict(os.environ, {'LEDGER_DATABASE_URL': ''}, clear=False)
        self._ledger_env.start()
        self._cooldown_patch = patch(
            'v4_web_dashboard._live_criteria_cooldown_wait',
            return_value=0,
        )
        self._cooldown_patch.start()
        from prodigy_rank import calculate as prodigy_calculate

        self._prodigy_calculate = prodigy_calculate

    def tearDown(self):
        self._cooldown_patch.stop()
        self._ledger_env.stop()

    def _server(self, root=None, *, connect_factory=None, session='panel-secret'):
        root = Path(root or tempfile.mkdtemp())
        handler = make_handler(
            root,
            operator_session=session,
            connect_factory=connect_factory,
        )
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:' + str(server.server_port)
        return root, server, thread, base

    def _shutdown(self, server, thread):
        server.shutdown()
        server.server_close()
        thread.join(3)

    def test_n57_empty_allowlist_raw_files_pending_c2_after_disk_and_live_refresh(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_allowlist_fixture(root, [])
            _n57_write_operator_c2_raw_canonical(root)
            disk_queue = build_preapproval_queue(root, None, signals=[])
            _n57_assert_collective2_pending_discovered(
                self,
                _n57_pending_collective2_rows(disk_queue.get('queue') or []),
            )

            _, server, thread, base = self._server(root)
            try:
                payload, _ = _n57_post_live_refresh(base, self._prodigy_calculate)
                self.assertEqual(payload.get('orders_sent'), 0)
                self.assertFalse(payload.get('execution_authorized', True))
                _n57_assert_collective2_pending_discovered(
                    self,
                    _n57_pending_collective2_rows(_n55_preapproval_queue(payload)),
                )
                c2_copy = (payload.get('copy') or {}).get('collective2') or {}
                self.assertEqual(c2_copy.get('approved_ids'), [])
                self.assertFalse(c2_copy.get('approved_for_paper_copy'))
            finally:
                self._shutdown(server, thread)

    def test_n57_allowlist_still_gates_paper_copy_not_raw_visibility(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_allowlist_fixture(root, [])
            _n57_write_operator_c2_raw_canonical(root)
            with patch.dict(os.environ, _n57_env_without_c2_paper_copy_ids(), clear=True):
                resolved = resolve_c2_paper_copy_approved_ids(root, None)
            self.assertEqual(resolved, [])
            bundle = build_panel_bundle(root, conn_factory=None)
            c2 = (bundle.get('copy') or {}).get('collective2') or {}
            self.assertFalse(c2.get('approved_for_paper_copy'))
            self.assertEqual(c2.get('approved_ids'), [])
            queue = build_preapproval_queue(root, None, signals=[])
            c2_rows = _n57_pending_collective2_rows(queue.get('queue') or [])
            _n57_assert_collective2_pending_discovered(self, c2_rows)
            for sid in _N57_OPERATOR_C2_IDS:
                self.assertNotIn(sid, resolve_c2_paper_copy_approved_ids(root, None))

    def test_n57_refresh_no_ledger_upsert_live_false_prodigy_research_only(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_allowlist_fixture(root, [])
            for sid in _N57_OPERATOR_C2_IDS:
                _n56_write_prodigy_raw_unscorable_canonical(root, sid)
            _n56_write_prodigy_raw_eligible_canonical(root)
            store = {'signal_provider_approvals': {}}
            _, server, thread, base = self._server(
                root,
                connect_factory=_approvals_memory_connect(store),
            )
            try:
                payload, calc_mock = _n57_post_live_refresh(base, self._prodigy_calculate)
                self.assertEqual(payload.get('orders_sent'), 0)
                self.assertFalse(payload.get('execution_authorized', True))
                self.assertEqual(store['signal_provider_approvals'], {})
                prodigy_ids = {
                    str(r.get('provider_id'))
                    for r in _n55_preapproval_queue(payload)
                    if r.get('platform') == 'prodigy'
                }
                self.assertIn('9', prodigy_ids)
                for sid in _N57_OPERATOR_C2_IDS:
                    self.assertNotIn(sid, prodigy_ids)
                calc_mock.assert_called_once()
                rank_path = root / 'intelligence' / 'prodigy-top10-latest.json'
                self.assertTrue(rank_path.is_file())
                rank = json.loads(rank_path.read_text(encoding='utf-8'))
                for row in rank.get('providers') or []:
                    pid = str(row.get('provider_id'))
                    if pid in _N57_OPERATOR_C2_IDS:
                        self.assertEqual(row.get('status'), 'UNSCORABLE')
                    if pid == '9':
                        self.assertEqual(row.get('status'), 'PRODIGY_CANDIDATE_RESEARCH')
            finally:
                self._shutdown(server, thread)


_N58_SCAN_ELIGIBLE_ID = '88001001'
_N58_SCAN_INELIGIBLE_ID = '88001002'
_N58_FORBIDDEN_C2_PATHS = ('SearchHistoricalStrategies', 'GetLeaderBoard')
_N58_SEARCH_STRATEGIES_PATH = '/Strategies/SearchStrategies'


def _n58_eligible_closed_trades() -> list[dict]:
    now = _n56_prodigy_now()
    return [
        {'CloseDate': (now - timedelta(days=d)).isoformat(), 'ProfitLoss': pl}
        for d, pl in ((6, 120.0), (5, -30.0), (4, 80.0), (3, 40.0), (2, 25.0))
    ]


def _n58_ineligible_closed_trades() -> list[dict]:
    now = _n56_prodigy_now()
    return [
        {'CloseDate': (now - timedelta(days=190)).isoformat(), 'ProfitLoss': 100.0}
        for _ in range(5)
    ]


def _n58_call_path_label(args: tuple, kwargs: dict) -> str:
    for key in ('path', 'endpoint', 'url'):
        if kwargs.get(key):
            return str(kwargs[key])
    if args:
        first = str(args[0])
        if '/Strategies/' in first or 'SearchStrategies' in first:
            return first
    return ''


def _n58_make_search_strategies_fetch_mock(
    *,
    next_cursor: str = '',
    fetch_log: list | None = None,
    search_seen: list | None = None,
):
    """Mock GET SearchStrategies + closed_trades for scan IDs (N58 contract)."""
    log = fetch_log if fetch_log is not None else []
    seen = search_seen if search_seen is not None else []

    def _fetch(strategy_ids, key, out_dir, opener=None, **kwargs):
        del key, opener
        label = _n58_call_path_label((strategy_ids,), kwargs)
        log.append(label or repr(strategy_ids))
        for forbidden in _N58_FORBIDDEN_C2_PATHS:
            if forbidden in label:
                raise AssertionError('forbidden Collective2 path in fetch: %s' % forbidden)

        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)

        if _N58_SEARCH_STRATEGIES_PATH in label or 'SearchStrategies' in label:
            seen.append(True)
            snap = {
                'dataset': 'search_strategies',
                'raw': {
                    'ResponseStatus': {'ErrorCode': '200'},
                    'Results': [
                        {
                            'StrategyId': int(_N58_SCAN_ELIGIBLE_ID),
                            'IsAlive': True,
                            'IsPrivate': False,
                        },
                        {
                            'StrategyId': int(_N58_SCAN_INELIGIBLE_ID),
                            'IsAlive': True,
                            'IsPrivate': False,
                        },
                    ],
                    'Pagination': {'next_cursor': next_cursor},
                },
            }
            (out / 'c2_search_strategies_latest.json').write_text(
                json.dumps(snap),
                encoding='utf-8',
            )
            return {
                'status': 'ok',
                'written': ['c2_search_strategies_latest.json'],
                'strategy_ids': [_N58_SCAN_ELIGIBLE_ID, _N58_SCAN_INELIGIBLE_ID],
                'next_cursor': next_cursor,
            }

        ids = sorted({str(x) for x in (strategy_ids or [])})
        written: list[str] = []
        for sid in ids:
            if sid == _N58_SCAN_ELIGIBLE_ID:
                trades = _n58_eligible_closed_trades()
            elif sid == _N58_SCAN_INELIGIBLE_ID:
                trades = _n58_ineligible_closed_trades()
            else:
                trades = []
            _n56_write_closed_trades_file(out, sid, trades)
            written.append(f'{sid}_closed_trades.json')
        return {'status': 'ok', 'written': written, 'opener_used': False}

    return _fetch


def _n58_collective2_queue_rows(queue: list[dict]) -> list[dict]:
    return [r for r in queue if r.get('platform') == 'collective2']


def _n58_post_refresh_with_fetch(
    base: str,
    prodigy_calculate,
    *,
    fetch_side_effect,
    c2_key: str | None = 'test-c2-secret',
    connect_factory=None,
) -> tuple[dict, list]:
    env = _n57_env_without_c2_paper_copy_ids()
    if c2_key is not None:
        env['C2_API4_KEY'] = c2_key
    else:
        env.pop('C2_API4_KEY', None)
    patches = [
        patch('v4_web_dashboard.c2_history_collect.fetch', side_effect=fetch_side_effect),
        patch('v4_web_dashboard.c2_signal_feed.snapshot', side_effect=_n54_mock_c2_snapshot),
        patch.dict(os.environ, env, clear=True),
    ]
    for p in patches:
        p.start()
    try:
        with patch('v4_web_dashboard.prodigy_rank.calculate', wraps=prodigy_calculate):
            req = _post_candidates_refresh(
                base + '/api/signals/candidates/refresh',
                {},
                session='panel-secret',
            )
            with urlopen(req, timeout=5) as resp:
                payload = json.load(resp)
        return payload, []
    finally:
        for p in reversed(patches):
            p.stop()


class N58Collective2SearchStrategiesScanTests(unittest.TestCase):
    """N58.2 — Atualizar varre Collective2 via SearchStrategies; fila só elegíveis 15d."""

    def setUp(self):
        self._ledger_env = patch.dict(os.environ, {'LEDGER_DATABASE_URL': ''}, clear=False)
        self._ledger_env.start()
        self._cooldown_patch = patch(
            'v4_web_dashboard._live_criteria_cooldown_wait',
            return_value=0,
        )
        self._cooldown_patch.start()
        from prodigy_rank import calculate as prodigy_calculate

        self._prodigy_calculate = prodigy_calculate
        self._fetch_log: list = []
        self._search_seen: list = []

    def tearDown(self):
        self._cooldown_patch.stop()
        self._ledger_env.stop()

    def _server(self, root=None, *, connect_factory=None, session='panel-secret'):
        root = Path(root or tempfile.mkdtemp())
        handler = make_handler(
            root,
            operator_session=session,
            connect_factory=connect_factory,
        )
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:' + str(server.server_port)
        return root, server, thread, base

    def _shutdown(self, server, thread):
        server.shutdown()
        server.server_close()
        thread.join(3)

    def _fetch_mock(self, *, next_cursor: str = ''):
        return _n58_make_search_strategies_fetch_mock(
            next_cursor=next_cursor,
            fetch_log=self._fetch_log,
            search_seen=self._search_seen,
        )

    def _post_refresh(self, base: str, *, next_cursor: str = '') -> dict:
        payload, _ = _n58_post_refresh_with_fetch(
            base,
            self._prodigy_calculate,
            fetch_side_effect=self._fetch_mock(next_cursor=next_cursor),
        )
        return payload

    def test_n58_empty_allowlist_scan_eligible_pending_without_raw_on_disk(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_allowlist_fixture(root, [])
            raw = root / 'providers' / 'raw'
            self.assertFalse((raw / f'{_N58_SCAN_ELIGIBLE_ID}_closed_trades.json').exists())
            _, server, thread, base = self._server(root)
            try:
                payload = self._post_refresh(base)
                self.assertTrue(self._search_seen, msg='refresh must call GET SearchStrategies via fetch')
                queue = _n58_collective2_queue_rows(_n55_preapproval_queue(payload))
                ids = {str(r.get('provider_id')) for r in queue}
                self.assertIn(
                    _N58_SCAN_ELIGIBLE_ID,
                    ids,
                    msg='eligible scanned Collective2 id must appear without allowlist',
                )
                self.assertNotIn(_N58_SCAN_INELIGIBLE_ID, ids)
                for row in queue:
                    if str(row.get('provider_id')) == _N58_SCAN_ELIGIBLE_ID:
                        self.assertEqual(row.get('status'), 'pending')
                        self.assertIn(
                            row.get('source'),
                            ('scanned', 'discovered'),
                            msg='scanned Collective2 row source must be scanned or discovered',
                        )
                c2 = (payload.get('copy') or {}).get('collective2') or {}
                self.assertFalse(c2.get('approved_for_paper_copy'))
            finally:
                self._shutdown(server, thread)

    def test_n58_fetch_must_not_use_leaderboard_or_historical_strategies_post(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_allowlist_fixture(root, [])
            _, server, thread, base = self._server(root)
            try:
                self._post_refresh(base)
                joined = ' '.join(self._fetch_log)
                self.assertIn('SearchStrategies', joined)
                for forbidden in _N58_FORBIDDEN_C2_PATHS:
                    self.assertNotIn(forbidden, joined)
            finally:
                self._shutdown(server, thread)

    def test_n58_missing_c2_api4_key_no_fake_scan(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_allowlist_fixture(root, [])

            def _forbidden_fetch(*_a, **_kw):
                raise AssertionError('fetch must not run when C2_API4_KEY is missing')

            _, server, thread, base = self._server(root)
            try:
                payload, _ = _n58_post_refresh_with_fetch(
                    base,
                    self._prodigy_calculate,
                    fetch_side_effect=_forbidden_fetch,
                    c2_key=None,
                )
                issues = payload.get('issues') or []
                self.assertIn('C2_API4_KEY_missing', issues)
                self.assertFalse(self._search_seen)
            finally:
                self._shutdown(server, thread)

    def test_n58_tradingview_ingested_no_search_scan_out_iss025(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_allowlist_fixture(root, [])
            _n55_write_tradingview_ingest_fixture(root)
            _, server, thread, base = self._server(root)
            try:
                payload = self._post_refresh(base)
                platforms = _n55_platforms_in_queue(_n55_preapproval_queue(payload))
                self.assertIn('tradingview', platforms)
                issues_text = ' '.join(str(i) for i in (payload.get('issues') or [])).lower()
                self.assertTrue(
                    'tradingview' in issues_text
                    and (
                        'scan' in issues_text
                        or 'iss-025' in issues_text
                        or '025' in issues_text
                        or 'out' in issues_text
                        or 'not' in issues_text
                    ),
                    msg='refresh must record TradingView scan is OUT (ISS-025), not invent search',
                )
                joined = ' '.join(self._fetch_log)
                self.assertNotIn('tradingview.com/search', joined.lower())
            finally:
                self._shutdown(server, thread)

    def test_n58_refresh_no_auto_approve_live_false_orders_sent_zero(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_allowlist_fixture(root, [])
            store = {'signal_provider_approvals': {}}
            _, server, thread, base = self._server(
                root,
                connect_factory=_approvals_memory_connect(store),
            )
            try:
                payload = self._post_refresh(base)
                self.assertEqual(payload.get('orders_sent'), 0)
                self.assertFalse(payload.get('execution_authorized', True))
                self.assertEqual(store['signal_provider_approvals'], {})
            finally:
                self._shutdown(server, thread)

    def test_n58_next_cursor_surfaces_incomplete_scan_issue(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write_c2_allowlist_fixture(root, [])
            _, server, thread, base = self._server(root)
            try:
                payload = self._post_refresh(base, next_cursor='cursor-page-2')
                issues = [str(i).lower() for i in (payload.get('issues') or [])]
                self.assertTrue(
                    any(
                        token in ' '.join(issues)
                        for token in ('incomplete', 'next_cursor', 'pagination', 'partial')
                    ),
                    msg='non-empty SearchStrategies next_cursor must warn scan is incomplete',
                )
            finally:
                self._shutdown(server, thread)

    def test_n58_prodigy_rank_constants_unchanged(self):
        import prodigy_rank

        self.assertEqual(prodigy_rank.WINDOW_DAYS, 15)
        self.assertEqual(prodigy_rank.MIN_TRADES, 5)


def _n59_http_error_414() -> HTTPError:
    return HTTPError(
        url='https://api.collective2.com/Strategies/GetStrategyActiveOrders',
        code=414,
        msg='URI Too Long',
        hdrs={},
        fp=BytesIO(),
    )


def _n59_post_refresh_snapshot_side_effect(
    base: str,
    prodigy_calculate,
    *,
    fetch_side_effect,
    snapshot_side_effect,
    root_allowlist: Path,
    approved_ids: list[str],
    c2_key: str | None = 'test-c2-secret',
) -> tuple[dict, list]:
    _write_c2_allowlist_fixture(root_allowlist, approved_ids)
    env = _n57_env_without_c2_paper_copy_ids()
    if c2_key is not None:
        env['C2_API4_KEY'] = c2_key
    else:
        env.pop('C2_API4_KEY', None)
    snapshot_calls: list = []
    seen = snapshot_calls

    def _wrapped_snapshot(strategy_ids, key, out_dir, **kwargs):
        seen.append(list(strategy_ids or []))
        if snapshot_side_effect is not None:
            return snapshot_side_effect(strategy_ids, key, out_dir, **kwargs)
        return _n54_mock_c2_snapshot(strategy_ids, key, out_dir, **kwargs)

    patches = [
        patch('v4_web_dashboard.c2_history_collect.fetch', side_effect=fetch_side_effect),
        patch('v4_web_dashboard.c2_signal_feed.snapshot', side_effect=_wrapped_snapshot),
        patch.dict(os.environ, env, clear=True),
    ]
    for p in patches:
        p.start()
    try:
        with patch('v4_web_dashboard.prodigy_rank.calculate', wraps=prodigy_calculate):
            req = _post_candidates_refresh(
                base + '/api/signals/candidates/refresh',
                {},
                session='panel-secret',
            )
            with urlopen(req, timeout=5) as resp:
                payload = json.load(resp)
        return payload, snapshot_calls
    finally:
        for p in reversed(patches):
            p.stop()


class N59Collective2SnapshotIsolationTests(unittest.TestCase):
    """N59 — active-orders snapshot must not abort SearchStrategies scan (F-022)."""

    def setUp(self):
        self._ledger_env = patch.dict(os.environ, {'LEDGER_DATABASE_URL': ''}, clear=False)
        self._ledger_env.start()
        self._cooldown_patch = patch(
            'v4_web_dashboard._live_criteria_cooldown_wait',
            return_value=0,
        )
        self._cooldown_patch.start()
        from prodigy_rank import calculate as prodigy_calculate

        self._prodigy_calculate = prodigy_calculate
        self._fetch_log: list = []
        self._search_seen: list = []

    def tearDown(self):
        self._cooldown_patch.stop()
        self._ledger_env.stop()

    def _server(self, root=None, *, connect_factory=None, session='panel-secret'):
        root = Path(root or tempfile.mkdtemp())
        handler = make_handler(
            root,
            operator_session=session,
            connect_factory=connect_factory,
        )
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:' + str(server.server_port)
        return root, server, thread, base

    def _shutdown(self, server, thread):
        server.shutdown()
        server.server_close()
        thread.join(3)

    def _fetch_mock(self, *, next_cursor: str = ''):
        return _n58_make_search_strategies_fetch_mock(
            next_cursor=next_cursor,
            fetch_log=self._fetch_log,
            search_seen=self._search_seen,
        )

    def test_n59_empty_allowlist_scan_ok_snapshot_skips_scan_page_ids(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _, server, thread, base = self._server(root)
            try:
                payload, snap_calls = _n59_post_refresh_snapshot_side_effect(
                    base,
                    self._prodigy_calculate,
                    fetch_side_effect=self._fetch_mock(),
                    snapshot_side_effect=lambda *_a, **_kw: (_ for _ in ()).throw(_n59_http_error_414()),
                    root_allowlist=root,
                    approved_ids=[],
                )
                self.assertTrue(self._search_seen)
                queue = _n58_collective2_queue_rows(_n55_preapproval_queue(payload))
                ids = {str(r.get('provider_id')) for r in queue}
                self.assertIn(_N58_SCAN_ELIGIBLE_ID, ids)
                issues = [str(i) for i in (payload.get('issues') or [])]
                self.assertFalse(any('collective2_refresh_failed' in i for i in issues))
                self.assertFalse(snap_calls, msg='empty paper-copy allowlist must skip snapshot')
                sources = payload.get('sources_ok') or []
                self.assertIn('collective2', sources)
                c2 = (payload.get('copy') or {}).get('collective2') or {}
                self.assertFalse(c2.get('approved_for_paper_copy'))
            finally:
                self._shutdown(server, thread)

    def test_n59_snapshot_414_with_allowlist_does_not_abort_collective2_source(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            store = {'signal_provider_approvals': {}}
            _, server, thread, base = self._server(
                root,
                connect_factory=_approvals_memory_connect(store),
            )
            paper_id = '88001001'
            try:
                payload, snap_calls = _n59_post_refresh_snapshot_side_effect(
                    base,
                    self._prodigy_calculate,
                    fetch_side_effect=self._fetch_mock(),
                    snapshot_side_effect=lambda *_a, **_kw: (_ for _ in ()).throw(_n59_http_error_414()),
                    root_allowlist=root,
                    approved_ids=[paper_id],
                )
                queue = _n58_collective2_queue_rows(_n55_preapproval_queue(payload))
                ids = {str(r.get('provider_id')) for r in queue}
                self.assertIn(_N58_SCAN_ELIGIBLE_ID, ids)
                issues = [str(i) for i in (payload.get('issues') or [])]
                self.assertTrue(
                    any('collective2_active_orders_snapshot_failed' in i for i in issues),
                    msg='snapshot HTTPError must be isolated issue',
                )
                self.assertTrue(
                    any('414' in i or 'HTTPError' in i for i in issues),
                    msg='issue must name HTTP 414 or HTTPError without secrets',
                )
                self.assertFalse(any('collective2_refresh_failed' in i for i in issues))
                self.assertIn('collective2', payload.get('sources_ok') or [])
                self.assertEqual(snap_calls, [[int(paper_id)]])
                self.assertEqual(payload.get('orders_sent'), 0)
                self.assertEqual(store['signal_provider_approvals'], {})
            finally:
                self._shutdown(server, thread)


class PanelOpsRunbookTest(unittest.TestCase):
    def test_daily_runbook_points_to_panel_not_exec(self):
        doc = Path(__file__).resolve().parents[1] / 'docs' / 'DASHBOARD-OPERATIONS.md'
        text = doc.read_text(encoding='utf-8')
        self.assertIn('Entrar', text)
        self.assertIn('Exec', text)
        self.assertIn('painel', text.lower())
