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
from panel_ops_data import (
    PERFORMANCE_LABEL_GROSS,
    blocked_context,
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
            ]
            (root / 'paper' / 'order-snapshots.jsonl').write_text(
                '\n'.join(json.dumps(r) for r in rows),
                encoding='utf-8',
            )
            perf = performance_from_snapshots(root)
            self.assertEqual(perf['orders_included'], 1)
            self.assertEqual(perf['total_gross_usd'], '10')
            self.assertEqual(perf['pnl_label'], PERFORMANCE_LABEL_GROSS)


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
