import json
import os
import tempfile
import threading
import unittest
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
