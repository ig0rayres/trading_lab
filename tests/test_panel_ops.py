import json
import os
import tempfile
import threading
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen

from gate_b_risk import evaluate_signed_signal
from panel_ops_html import render_central_page
from panel_ops_data import (
    PERFORMANCE_LABEL_GROSS,
    blocked_context,
    build_panel_bundle,
    load_panel_signals,
    performance_from_snapshots,
    signal_destination,
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
                        ('cid-1', 'AAPL', 'buy', 'accepted', Decimal('2.5'), 'brk-1', 'signal_copy'),
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


class PanelOpsRunbookTest(unittest.TestCase):
    def test_daily_runbook_points_to_panel_not_exec(self):
        doc = Path(__file__).resolve().parents[1] / 'docs' / 'DASHBOARD-OPERATIONS.md'
        text = doc.read_text(encoding='utf-8')
        self.assertIn('Entrar', text)
        self.assertIn('Exec', text)
        self.assertIn('painel', text.lower())
