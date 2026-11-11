import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import paper_gateway_queue as pgq
from signal_copy import sign

TEST_SIGNAL_COPY_SECRET = 'x' * 32


def _signal():
    return {
        'provider': 'tradingview',
        'signal_id': 'QUEUE_TEST_001',
        'symbol': 'AAPL',
        'side': 'buy',
        'asset_class': 'us_equity',
        'entry': '100',
        'stop': '99',
        'target': '102',
        'quantity': 1,
        'strategy_key': 'signal_copy',
    }


class PaperGatewayQueueTest(unittest.TestCase):
    def test_queue_never_calls_broker(self):
        decision = {'decision': 'paper_allowed', 'risk_amount_cents': 500}
        env = {'LIVE_TRADING_ENABLED': 'false', 'PAPER_SIGNAL_AUTO_ENABLED': 'false'}
        with patch.object(pgq, 'paper_run') as broker:
            out = pgq.process_after_gate_b(_signal(), decision, env, broker_run=broker)
        broker.assert_not_called()
        self.assertEqual(out['status'], 'QUEUED')
        self.assertEqual(out['mode'], 'PAPER_GATEWAY_QUEUE_ONLY')
        self.assertEqual(out['orders_sent'], 0)
        self.assertIn('client_order_id', out)

    def test_rejected_gate_b_no_queue(self):
        decision = {'decision': 'rejected', 'reject_code': 'LOSS'}
        out = pgq.process_after_gate_b(_signal(), decision, {})
        self.assertEqual(out['status'], 'BLOCKED')
        self.assertEqual(out['orders_sent'], 0)

    def test_auto_allowed_delegates_to_paper_run(self):
        decision = {'decision': 'paper_allowed', 'risk_amount_cents': 500}
        env = {
            'LIVE_TRADING_ENABLED': 'false',
            'PAPER_SIGNAL_AUTO_ENABLED': 'true',
            'PAPER_EXECUTION_ENABLED': 'true',
            'PAPER_SIGNAL_ACCOUNT_ACK': 'I_AUTHORIZE_ALPACA_PAPER_ONLY',
        }
        submitted = {
            'status': 'PAPER_SUBMITTED',
            'orders_sent': 1,
            'client_order_id': 'nf-deadbeef',
        }

        def fake_run(signal, env, ledger=None, **kwargs):
            return submitted

        with patch('risk_control_flags.demo_send_allowed', return_value=(True, None)):
            with patch.object(pgq, 'paper_run', side_effect=fake_run) as broker:
                out = pgq.process_after_gate_b(_signal(), decision, env, broker_run=broker)
            broker.assert_called_once()
            self.assertEqual(out['status'], 'PAPER_SUBMITTED')
            self.assertEqual(out['orders_sent'], 1)

    def test_demo_operation_off_blocks_broker_even_with_auto_flags(self):
        decision = {'decision': 'paper_allowed', 'risk_amount_cents': 500}
        env = {
            'LIVE_TRADING_ENABLED': 'false',
            'PAPER_SIGNAL_AUTO_ENABLED': 'true',
            'PAPER_EXECUTION_ENABLED': 'true',
            'PAPER_SIGNAL_ACCOUNT_ACK': 'I_AUTHORIZE_ALPACA_PAPER_ONLY',
        }

        def fake_run(signal, env, ledger=None, **kwargs):
            raise AssertionError('broker must not run when demo_operation_on is false')

        with patch.object(pgq, 'paper_run', side_effect=fake_run) as broker:
            out = pgq.process_after_gate_b(_signal(), decision, env, broker_run=broker)
        broker.assert_not_called()
        self.assertEqual(out['status'], 'BLOCKED')
        self.assertEqual(out['orders_sent'], 0)
        self.assertIn('DEMO_OPERATION_OFF', out['reasons'])


ALPACA_PAPER_HOST = 'https://paper-api.alpaca.markets'
MOCK_BROKER_ORDER_ID = 'alpaca-mock-order-id-n19-3'
# N19.3/N19.4 stable reject literal for B3_EQUITY and FOREX (ADR-010; no invented broker).
NO_DEMO_ACCOUNT_REJECT = 'NO_DEMO_ACCOUNT_PATH'


def _auto_env_with_snapshot(tmp_dir: str) -> dict[str, str]:
    snapshot = Path(tmp_dir) / 'risk.json'
    snapshot.write_text(
        json.dumps(
            {
                'at_utc': datetime.now(timezone.utc).isoformat(),
                'alpaca_positions_count': 0,
                'alpaca_open_orders_count': 0,
                'complete': True,
                'daily_pnl_verified': True,
                'weekly_pnl_verified': True,
                'broker_reconciled': True,
                'positions': [],
                'daily_pnl_brl': '0',
                'weekly_pnl_brl': '0',
                'available_cash_brl': '10000',
                'has_pending_orders': False,
            }
        )
    )
    return {
        'LIVE_TRADING_ENABLED': 'false',
        'PAPER_SIGNAL_AUTO_ENABLED': 'true',
        'PAPER_EXECUTION_ENABLED': 'true',
        'PAPER_SIGNAL_ACCOUNT_ACK': 'I_AUTHORIZE_ALPACA_PAPER_ONLY',
        'PAPER_DAILY_RISK_CONFIRMED': 'true',
        'ALPACA_PAPER_TRADE': 'true',
        'ALPACA_BASE_URL': ALPACA_PAPER_HOST,
        'ALPACA_API_KEY': 'test',
        'ALPACA_SECRET_KEY': 'test',
        'USD_BRL_REFERENCE': '5',
        'SIGNAL_COPY_SECRET': TEST_SIGNAL_COPY_SECRET,
        'V4_RISK_SNAPSHOT_FILE': str(snapshot),
    }


def _gated_signal(signal_id: str, *, secret: str = TEST_SIGNAL_COPY_SECRET) -> dict:
    sig = _signal()
    sig['signal_id'] = signal_id
    sig['sent_at_utc'] = datetime.now(timezone.utc).isoformat()
    sig['ttl_seconds'] = 60
    sig['entry'] = 100
    sig['stop'] = 99
    sig['target'] = 102
    sig['provider_signature'] = sign(sig, secret)
    return sig


def _mocked_paper_run(signal, env, ledger=None):
    import signal_paper_runner as spr

    def getter(endpoint, _env):
        if endpoint.endswith('account'):
            return {
                'status': 'ACTIVE',
                'currency': 'USD',
                'trading_blocked': False,
                'cash': '5000',
                'equity': '5000',
            }
        return []

    alpaca_posts: list[str] = []

    def poster(body, post_env, opener=None):
        base = post_env.get('ALPACA_BASE_URL', '').rstrip('/')
        alpaca_posts.append(base)
        if base == ALPACA_PAPER_HOST:
            return {'id': MOCK_BROKER_ORDER_ID, 'status': 'accepted'}
        raise AssertionError(f'unexpected broker host {base!r}')

    result = spr.run(signal, env, ledger, broker_get=getter, broker_post=poster)
    result['_alpaca_posts'] = alpaca_posts
    return result


def _snapshot_with_market_position(snapshot_path: Path, market: str, symbol: str) -> None:
    data = json.loads(snapshot_path.read_text())
    data['positions'] = [
        {
            'market': market,
            'symbol': symbol,
            'notional_brl': '500',
            'planned_risk_brl': '20',
        }
    ]
    snapshot_path.write_text(json.dumps(data))


def _assert_n19_4_no_demo_block(test: unittest.TestCase, result: dict) -> None:
    """N19.4: visible stable reason, zero orders, never Alpaca paper POST."""
    test.assertEqual(result.get('status'), 'BLOCKED')
    test.assertEqual(result.get('orders_sent'), 0)
    test.assertEqual(result.get('_alpaca_posts', []), [])
    reasons = result.get('reasons') or []
    reject_code = result.get('reject_code')
    test.assertTrue(
        reject_code == NO_DEMO_ACCOUNT_REJECT or NO_DEMO_ACCOUNT_REJECT in reasons,
        msg=f'expected {NO_DEMO_ACCOUNT_REJECT!r} in reject_code or reasons, got {result!r}',
    )


class PaperAlpacaMarketGuardTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.env = _auto_env_with_snapshot(self.tmp.name)
        self.ledger = str(Path(self.tmp.name) / 'signal-orders.jsonl')

    def _run_with_market(self, market: str) -> dict:
        signal = _gated_signal(f'MKT_{market}_001')
        signal['market'] = market
        return _mocked_paper_run(signal, self.env, self.ledger)

    @patch('signal_paper_runner.validate', return_value=[])
    def test_b3_equity_never_posts_alpaca_paper_host(self, _mock_validate):
        """Once `market` is accepted on the signal, B3 must not hit Alpaca paper."""
        result = self._run_with_market('B3_EQUITY')
        _assert_n19_4_no_demo_block(self, result)

    @patch('signal_paper_runner.validate', return_value=[])
    def test_forex_never_posts_alpaca_paper_host(self, _mock_validate):
        result = self._run_with_market('FOREX')
        _assert_n19_4_no_demo_block(self, result)

    @patch('signal_paper_runner.validate', return_value=[])
    def test_n19_4_b3_with_snapshot_position_blocked_visible_reason(self, _mock_validate):
        """ADR-010: B3 snapshot may list positions; without demo account path, block before Alpaca."""
        snap = Path(self.env['V4_RISK_SNAPSHOT_FILE'])
        _snapshot_with_market_position(snap, 'B3_EQUITY', 'ITUB4')
        result = self._run_with_market('B3_EQUITY')
        _assert_n19_4_no_demo_block(self, result)

    @patch('risk_control_flags.demo_send_allowed', return_value=(True, None))
    @patch('signal_paper_runner.validate', return_value=[])
    def test_n19_4_forex_blocked_via_gateway_queue_no_alpaca(
        self, _mock_validate, _mock_demo,
    ):
        signal = _gated_signal('N19_4_FOREX_GW')
        signal['market'] = 'FOREX'
        decision = {'decision': 'paper_allowed', 'risk_amount_cents': 500}
        out = pgq.process_after_gate_b(
            signal,
            decision,
            self.env,
            ledger=self.ledger,
            broker_run=_mocked_paper_run,
        )
        _assert_n19_4_no_demo_block(self, out)


@unittest.skipUnless(os.environ.get('LEDGER_DATABASE_URL'), 'LEDGER_DATABASE_URL not set')
class GateBLedgerIntegrationTest(unittest.TestCase):
    def setUp(self):
        import ledger_migrate as lm

        lm.apply()

    def test_intent_persists_paper_order(self):
        import ledger_store as store
        from gate_a_signal import record_signal_event, idempotency_key
        from paper_gateway_queue import persist_intent, queue_intent

        signal = _signal()
        signal['provider'] = 'tradingview'
        signal['signal_id'] = 'LEDGER_B_001'
        decision = {'decision': 'paper_allowed', 'risk_amount_cents': 500}
        queued = queue_intent(signal, decision)
        with store.connect() as conn:
            record_signal_event(
                conn,
                payload=signal,
                http_status=202,
                body={'status': 'QUEUED', 'orders_sent': 0},
            )
            conn.commit()
        persist_intent(signal, decision, queued)
        with store.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT po.status FROM paper_orders po "
                    "JOIN risk_decisions rd ON rd.id = po.risk_decision_id "
                    "JOIN signal_events se ON se.id = rd.signal_event_id "
                    'WHERE se.idempotency_key = %s',
                    (idempotency_key('tradingview', 'LEDGER_B_001'),),
                )
                row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 'queued_intent')

    def test_persist_uses_queue_stem_when_signal_id_hashed(self):
        import hashlib

        import ledger_store as store
        from gate_a_signal import idempotency_key, record_signal_event
        from paper_gateway_queue import persist_intent, queue_intent

        original_id = 'TV_QUEUE_HASH_001'
        gate_payload = _signal()
        gate_payload['signal_id'] = original_id
        queue_key = idempotency_key('tradingview', original_id)
        queued_signal = dict(gate_payload)
        queued_signal['signal_id'] = hashlib.sha256(original_id.encode()).hexdigest()[:32]
        decision = {'decision': 'paper_allowed', 'risk_amount_cents': 500}
        queued = queue_intent(queued_signal, decision)
        with store.connect() as conn:
            record_signal_event(
                conn,
                payload=gate_payload,
                http_status=202,
                body={'status': 'QUEUED', 'orders_sent': 0},
            )
            conn.commit()
        persist_intent(
            queued_signal,
            decision,
            queued,
            queue_idempotency_key=queue_key,
        )
        with store.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT po.status FROM paper_orders po "
                    "JOIN risk_decisions rd ON rd.id = po.risk_decision_id "
                    "JOIN signal_events se ON se.id = rd.signal_event_id "
                    'WHERE se.idempotency_key = %s',
                    (queue_key,),
                )
                row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 'queued_intent')

    def test_reject_persists_risk_decision(self):
        import ledger_store as store
        from gate_a_signal import idempotency_key, record_signal_event

        signal = _signal()
        signal['signal_id'] = 'GATEB_REJ_001'
        with store.connect() as conn:
            record_signal_event(
                conn,
                payload=signal,
                http_status=202,
                body={'status': 'QUEUED', 'orders_sent': 0},
            )
            conn.commit()
        decision = {'decision': 'rejected', 'reject_code': 'LOSS', 'risk_amount_cents': 0}
        pgq.persist_risk_decision(signal, decision)
        with store.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT rd.decision, rd.reject_code, rd.strategy_key FROM risk_decisions rd "
                    "JOIN signal_events se ON se.id = rd.signal_event_id "
                    'WHERE se.idempotency_key = %s',
                    (idempotency_key('tradingview', 'GATEB_REJ_001'),),
                )
                row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 'rejected')
        self.assertEqual(row[1], 'LOSS')
        self.assertEqual(row[2], 'signal_copy')

    def test_seed_and_strategy_key_on_risk_row(self):
        import ledger_store as store
        import strategy_catalog as sc
        from gate_a_signal import idempotency_key, record_signal_event

        sc.ensure_strategy_defaults()
        signal = _signal()
        signal['signal_id'] = 'GATEB_SK_001'
        signal['strategy_key'] = 'momentum'
        with store.connect() as conn:
            record_signal_event(
                conn,
                payload=signal,
                http_status=202,
                body={'status': 'QUEUED', 'orders_sent': 0},
            )
            conn.commit()
        decision = {
            'decision': 'rejected',
            'reject_code': 'STRATEGY_PHASE_BLOCKED',
            'risk_amount_cents': 0,
        }
        pgq.persist_risk_decision(signal, decision)
        with store.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT phase FROM strategy_states WHERE strategy_key = %s',
                    ('momentum',),
                )
                phase_row = cur.fetchone()
                cur.execute(
                    "SELECT rd.strategy_key FROM risk_decisions rd "
                    "JOIN signal_events se ON se.id = rd.signal_event_id "
                    'WHERE se.idempotency_key = %s',
                    (idempotency_key('tradingview', 'GATEB_SK_001'),),
                )
                sk_row = cur.fetchone()
        self.assertEqual(phase_row[0], 'research')
        self.assertEqual(sk_row[0], 'momentum')

    @patch('risk_control_flags.demo_send_allowed', return_value=(True, None))
    def test_auto_submit_persists_broker_order_id_not_queued_intent(self, _mock_demo):
        import ledger_store as store
        from gate_a_signal import idempotency_key, record_signal_event

        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        signal = _gated_signal('N19_BROKER_PERSIST_001')
        decision = {'decision': 'paper_allowed', 'risk_amount_cents': 500}
        env = _auto_env_with_snapshot(tmp.name)
        ledger = str(Path(tmp.name) / 'signal-orders.jsonl')
        with store.connect() as conn:
            record_signal_event(
                conn,
                payload=signal,
                http_status=202,
                body={'status': 'QUEUED', 'orders_sent': 0},
            )
            with conn.cursor() as cur:
                cur.execute(
                    'UPDATE control_flags SET demo_operation_on = TRUE '
                    'WHERE id = (SELECT id FROM control_flags WHERE deleted_at IS NULL '
                    'ORDER BY created_at DESC LIMIT 1)'
                )
            conn.commit()
        out = pgq.process_after_gate_b(
            signal,
            decision,
            env,
            ledger=ledger,
            broker_run=_mocked_paper_run,
        )
        self.assertEqual(out['status'], 'PAPER_SUBMITTED', out)
        self.assertEqual(out.get('broker_id'), MOCK_BROKER_ORDER_ID)
        with store.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'SELECT po.status, po.broker_order_id '
                    'FROM paper_orders po '
                    'JOIN risk_decisions rd ON rd.id = po.risk_decision_id '
                    'JOIN signal_events se ON se.id = rd.signal_event_id '
                    'WHERE se.idempotency_key = %s',
                    (idempotency_key('tradingview', signal['signal_id']),),
                )
                row = cur.fetchone()
        self.assertIsNotNone(row)
        status, broker_order_id = row
        self.assertIsNotNone(broker_order_id)
        self.assertEqual(broker_order_id, MOCK_BROKER_ORDER_ID)
        self.assertNotEqual(status, 'queued_intent')


if __name__ == '__main__':
    unittest.main()
