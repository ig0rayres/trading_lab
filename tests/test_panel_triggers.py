import json
import os
import re
import threading
import unittest
import uuid
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from v4_web_dashboard import (
    CONTROL_FLAG_RESPONSE_FIELDS,
    VALID_MARKETS,
    apply_trigger_patch,
    make_handler,
    operator_session_from_env,
)

# N27.3 / N19.4: stable literal when operator has not named a demo account (G-MKT).
NO_DEMO_ACCOUNT_REJECT = 'NO_DEMO_ACCOUNT_PATH'
DEMO_PANEL_MARKETS = frozenset({'B3_EQUITY', 'CRYPTO', 'FOREX'})


class _MemoryCursor:
    def __init__(self, store):
        self._store = store
        self._one = None
        self._all = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        params = params or ()
        normalized = ' '.join(sql.split())
        if normalized.startswith('SELECT id,') and 'FROM control_flags' in normalized:
            row = self._store['control_flags']
            self._one = tuple(row[name] for name in ('id',) + CONTROL_FLAG_RESPONSE_FIELDS)
            return
        if 'FROM market_controls' in normalized and 'market = ANY' in normalized:
            self._all = [
                (m['id'], m['market'], m['operation_on'])
                for market in sorted(VALID_MARKETS)
                for m in [self._store['market_controls'][market]]
            ]
            return
        if normalized.startswith('UPDATE control_flags SET'):
            match = re.match(r'UPDATE control_flags SET (\w+) = %s', normalized)
            field = match.group(1)
            new_value, _updated, row_id = params
            row = self._store['control_flags']
            if str(row['id']) == str(row_id):
                row[field] = new_value
            return
        if normalized.startswith('UPDATE market_controls SET operation_on'):
            new_on, _updated, row_id = params
            for market in self._store['market_controls'].values():
                if str(market['id']) == str(row_id):
                    market['operation_on'] = new_on
            return
        if 'FROM strategy_states' in normalized and 'strategy_key = %s' in normalized:
            key = params[0]
            state = self._store['strategy_states'].get(key)
            self._one = (state['id'], state['phase']) if state else None
            return
        if normalized.startswith('UPDATE strategy_states SET phase'):
            new_phase, _updated, row_id = params
            for state in self._store['strategy_states'].values():
                if str(state['id']) == str(row_id):
                    state['phase'] = new_phase
            return
        if normalized.startswith('INSERT INTO trigger_changes'):
            columns = re.search(r'INSERT INTO trigger_changes \((.+)\) VALUES', normalized)
            names = [part.strip() for part in columns.group(1).split(',')]
            row = dict(zip(names, params))
            self._store['trigger_changes'].append(row)
            return
        raise AssertionError('unexpected SQL: %s' % normalized)

    def fetchone(self):
        return self._one

    def fetchall(self):
        return self._all or []


class _MemoryConn:
    def __init__(self, store):
        self._store = store

    def cursor(self):
        return _MemoryCursor(self._store)

    def commit(self):
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def _default_store():
    control_id = str(uuid.uuid4())
    store = {
        'control_flags': {
            'id': control_id,
            'kill_switch_on': False,
            'demo_operation_on': False,
            'capital_cents': 500_000,
            'max_risk_per_trade_cents': 5_000,
            'max_open_positions': 3,
            'max_aggregate_risk_cents': 20_000,
            'max_daily_loss_cents': 20_000,
            'max_weekly_loss_cents': 50_000,
            'prodigy_risk_cents': 2_000,
        },
        'market_controls': {
            market: {
                'id': str(uuid.uuid4()),
                'market': market,
                'operation_on': False,
            }
            for market in sorted(VALID_MARKETS)
        },
        'strategy_states': {
            'orb': {'id': str(uuid.uuid4()), 'strategy_key': 'orb', 'phase': 'shadow'},
            'momentum': {'id': str(uuid.uuid4()), 'strategy_key': 'momentum', 'phase': 'research'},
        },
        'trigger_changes': [],
        'paper_orders': [],
    }
    return store


def _memory_connect(store):
    def connect():
        return _MemoryConn(store)
    return connect


def _patch(url, body, *, session=None, bearer=None, method='PATCH'):
    headers = {'Content-Type': 'application/json'}
    if session is not None:
        headers['Cookie'] = 'trading_lab_session=' + session
    if bearer is not None:
        headers['Authorization'] = 'Bearer ' + bearer
    payload = json.dumps(body).encode('utf-8')
    return Request(url, data=payload, headers=headers, method=method)


def _get(url, *, session=None):
    headers = {}
    if session is not None:
        headers['Cookie'] = 'trading_lab_session=' + session
    return Request(url, headers=headers)


class PanelTriggerHttpTests(unittest.TestCase):
    def _server(self, store=None, token=None):
        store = store or _default_store()
        handler = make_handler(
            Path('/tmp'),
            token=token,
            operator_session='op-session-token',
            connect_factory=_memory_connect(store),
        )
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:' + str(server.server_port)
        return server, thread, base, store

    def _shutdown(self, server, thread):
        server.shutdown()
        server.server_close()
        thread.join(3)

    def test_post_root_still_405(self):
        server, thread, base, _store = self._server()
        try:
            with self.assertRaises(HTTPError) as caught:
                urlopen(_patch(base + '/', {}, method='POST'), timeout=3)
            self.assertEqual(caught.exception.code, 405)
        finally:
            self._shutdown(server, thread)

    def test_patch_triggers_bearer_only_is_401(self):
        token = 'sample-token-' + 'x' * 30
        server, thread, base, _store = self._server(token=token)
        try:
            req = _patch(base + '/api/triggers', {'kill_switch_on': True}, bearer=token)
            with self.assertRaises(HTTPError) as caught:
                urlopen(req, timeout=3)
            self.assertEqual(caught.exception.code, 401)
        finally:
            self._shutdown(server, thread)

    def test_patch_triggers_with_cookie_updates_audit(self):
        store = _default_store()
        server, thread, base, _store = self._server(store=store)
        try:
            req = _patch(
                base + '/api/triggers',
                {'kill_switch_on': True},
                session='op-session-token',
            )
            with urlopen(req, timeout=3) as response:
                body = json.load(response)
            self.assertTrue(body['kill_switch_on'])
            self.assertTrue(store['control_flags']['kill_switch_on'])
            self.assertEqual(len(store['trigger_changes']), 1)
            audit = store['trigger_changes'][0]
            self.assertEqual(audit['field_name'], 'kill_switch_on')
            self.assertEqual(audit['target_table'], 'control_flags')
        finally:
            self._shutdown(server, thread)

    def test_capital_cents_zero_is_422(self):
        server, thread, base, _store = self._server()
        try:
            req = _patch(
                base + '/api/triggers',
                {'capital_cents': 0},
                session='op-session-token',
            )
            with self.assertRaises(HTTPError) as caught:
                urlopen(req, timeout=3)
            self.assertEqual(caught.exception.code, 422)
            payload = json.loads(caught.exception.read().decode('utf-8'))
            self.assertEqual(payload['reject_code'], 'BELOW_MINIMUM')
        finally:
            self._shutdown(server, thread)

    def test_invalid_market_is_422(self):
        server, thread, base, _store = self._server()
        try:
            req = _patch(
                base + '/api/markets/US_EQUITY',
                {'operation_on': True},
                session='op-session-token',
            )
            with self.assertRaises(HTTPError) as caught:
                urlopen(req, timeout=3)
            self.assertEqual(caught.exception.code, 422)
        finally:
            self._shutdown(server, thread)

    def test_missing_strategy_is_404(self):
        server, thread, base, _store = self._server()
        try:
            req = _patch(
                base + '/api/strategies/unknown_key',
                {'phase': 'research'},
                session='op-session-token',
            )
            with self.assertRaises(HTTPError) as caught:
                urlopen(req, timeout=3)
            self.assertEqual(caught.exception.code, 404)
        finally:
            self._shutdown(server, thread)

    def test_orb_to_paper_limited_is_422(self):
        server, thread, base, _store = self._server()
        try:
            req = _patch(
                base + '/api/strategies/orb',
                {'phase': 'paper_limited'},
                session='op-session-token',
            )
            with self.assertRaises(HTTPError) as caught:
                urlopen(req, timeout=3)
            self.assertEqual(caught.exception.code, 422)
            payload = json.loads(caught.exception.read().decode('utf-8'))
            self.assertEqual(payload['reject_code'], 'STRATEGY_PAPER_FORBIDDEN')
        finally:
            self._shutdown(server, thread)

    def test_successful_patch_does_not_insert_paper_order(self):
        store = _default_store()
        server, thread, base, _store = self._server(store=store)
        try:
            req = _patch(
                base + '/api/triggers',
                {'demo_operation_on': True},
                session='op-session-token',
            )
            with urlopen(req, timeout=3) as response:
                json.load(response)
            self.assertEqual(store['paper_orders'], [])
        finally:
            self._shutdown(server, thread)


class N27DemoMarketPanelTests(unittest.TestCase):
    def _server(self, store=None, token=None):
        store = store or _default_store()
        handler = make_handler(
            Path('/tmp'),
            token=token,
            operator_session='op-session-token',
            connect_factory=_memory_connect(store),
        )
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:' + str(server.server_port)
        return server, thread, base, store

    def _shutdown(self, server, thread):
        server.shutdown()
        server.server_close()
        thread.join(3)

    def test_n27_valid_markets_include_forex_and_demo_scope(self):
        self.assertIn('FOREX', VALID_MARKETS)
        self.assertTrue(DEMO_PANEL_MARKETS <= set(VALID_MARKETS))

    def test_n27_3_get_triggers_lists_demo_markets_barred_with_reason(self):
        server, thread, base, _store = self._server()
        try:
            with urlopen(_get(base + '/api/triggers', session='op-session-token'), timeout=3) as resp:
                body = json.load(resp)
            by_market = {row['market']: row for row in body['market_controls']}
            self.assertTrue(DEMO_PANEL_MARKETS <= set(by_market))
            for market in DEMO_PANEL_MARKETS:
                row = by_market[market]
                self.assertFalse(row['operation_on'], market)
                block = row.get('block_reason') or row.get('demo_block_code')
                self.assertEqual(
                    block,
                    NO_DEMO_ACCOUNT_REJECT,
                    msg=f'{market} must expose {NO_DEMO_ACCOUNT_REJECT!r}, got {row!r}',
                )
        finally:
            self._shutdown(server, thread)


class PanelTriggerUnitTests(unittest.TestCase):
    def test_operator_session_from_env(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(operator_session_from_env())
        with patch.dict(os.environ, {'DASHBOARD_OPERATOR_SESSION': '  secret-value  '}):
            self.assertEqual(operator_session_from_env(), 'secret-value')
        with patch.dict(os.environ, {'DASHBOARD_OPERATOR_SESSION': '   '}):
            self.assertIsNone(operator_session_from_env())

    def test_patch_with_env_operator_session_not_401(self):
        store = _default_store()
        session = 'panel-op-session'
        with patch.dict(os.environ, {'DASHBOARD_OPERATOR_SESSION': session}):
            op_session = operator_session_from_env()
        handler = make_handler(
            Path('/tmp'),
            operator_session=op_session,
            connect_factory=_memory_connect(store),
        )
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:' + str(server.server_port)
        try:
            req = _patch(
                base + '/api/triggers',
                {'kill_switch_on': True},
                session=session,
            )
            with urlopen(req, timeout=3) as response:
                self.assertEqual(response.status, 200)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(3)

    def test_apply_trigger_patch_appends_audit(self):
        store = _default_store()
        conn = _MemoryConn(store)
        updated, err = apply_trigger_patch(conn, {'max_open_positions': 5})
        self.assertIsNone(err)
        self.assertEqual(updated['max_open_positions'], 5)
        self.assertEqual(len(store['trigger_changes']), 1)
