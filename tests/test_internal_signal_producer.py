import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from gate_b_risk import evaluate_signed_signal, signal_to_bracket_order
from internal_signal_producer import emit_internal_signal, enqueue_signed_signal, plan_levels_from_close, provider_for_strategy
from original import load_original
from portfolio_risk_v4 import evaluate as portfolio_evaluate
from risk_control_flags import TIGHT_DEFAULTS
from signal_copy import validate


class InternalSignalProducerTests(unittest.TestCase):
    def setUp(self):
        self.secret = 's' * 32
        self.now = datetime(2026, 10, 28, 19, 0, tzinfo=timezone.utc)
        os.environ['SIGNAL_COPY_SECRET'] = self.secret
        os.environ['USD_BRL_REFERENCE'] = '5'
        os.environ['LIVE_TRADING_ENABLED'] = 'false'
        self.orig = load_original()

    def test_provider_mapping_not_tradingview(self):
        self.assertEqual(provider_for_strategy('momentum'), 'lab_momentum')
        self.assertNotEqual(provider_for_strategy('momentum'), 'tradingview')

    def test_plan_levels_uses_upstream_exit_and_budget(self):
        levels = plan_levels_from_close(
            self.orig,
            symbol='TEST',
            entry_price=100.0,
            bar_date='2026-10-27',
            fx=Decimal('5'),
        )
        self.assertIsNotNone(levels)
        self.assertGreater(int(levels['quantity']), 0)
        self.assertGreater(Decimal(levels['entry']), Decimal(levels['stop']))

    def test_missing_strategy_key_does_not_enqueue(self):
        with tempfile.TemporaryDirectory() as td:
            q = Path(td)
            sig = {
                'provider': 'lab_momentum',
                'signal_id': 'momentum_abc123456789',
                'symbol': 'AAPL',
                'side': 'buy',
                'asset_class': 'us_equity',
                'sent_at_utc': self.now.isoformat(),
                'entry': '100',
                'stop': '99',
                'target': '102',
                'quantity': 1,
                'ttl_seconds': 30,
                'provider_signature': 'x',
            }
            body = enqueue_signed_signal(sig, queue=q, now=self.now, secret=self.secret)
            self.assertEqual(body['reason'], 'STRATEGY_KEY_REQUIRED')
            self.assertEqual(list(q.glob('*.json')), [])

    def test_enqueue_dedup_and_validate_auth_failed_on_tamper(self):
        levels = {'entry': '100', 'stop': '99', 'target': '102', 'quantity': 1}
        with tempfile.TemporaryDirectory() as td:
            q = Path(td)
            first = emit_internal_signal(
                strategy_key='momentum',
                symbol='AAPL',
                asset_class='us_equity',
                bar_date='2026-10-27',
                levels=levels,
                queue=q,
                now=self.now,
                secret=self.secret,
            )
            self.assertEqual(first['status'], 'QUEUED')
            dup = emit_internal_signal(
                strategy_key='momentum',
                symbol='AAPL',
                asset_class='us_equity',
                bar_date='2026-10-27',
                levels=levels,
                queue=q,
                now=self.now,
                secret=self.secret,
            )
            self.assertEqual(dup['status'], 'DUPLICATE_IGNORED')
            pending = next(q.glob('*.json'))
            bad = json.loads(pending.read_text())
            bad['quantity'] = 2
            pending.write_text(json.dumps(bad))
            errs = validate(bad, self.secret, Decimal('5'), now=self.now)
            self.assertIn('AUTH_FAILED', errs)

    def test_crypto_high_price_fractional_qty_queues(self):
        levels = plan_levels_from_close(
            self.orig,
            symbol='BTCUSD',
            entry_price=95000.0,
            bar_date='2026-10-27',
            fx=Decimal('5'),
            flags=TIGHT_DEFAULTS,
            asset_class='crypto',
        )
        self.assertIsNotNone(levels)
        qty = Decimal(str(levels['quantity']))
        self.assertGreater(qty, 0)
        self.assertLess(qty, 1)
        with tempfile.TemporaryDirectory() as td:
            q = Path(td)
            out = emit_internal_signal(
                strategy_key='momentum',
                symbol='BTCUSD',
                asset_class='crypto',
                bar_date='2026-10-27',
                levels=levels,
                queue=q,
                now=self.now,
                secret=self.secret,
            )
            self.assertEqual(out['status'], 'QUEUED')
            sig = json.loads(next(q.glob('*.json')).read_text())
        self.assertEqual(sig['asset_class'], 'crypto')
        self.assertEqual(validate(sig, self.secret, Decimal('5'), now=self.now), [])
        order = signal_to_bracket_order(sig)
        self.assertNotIn('order_class', order)
        self.assertEqual(order['qty'], levels['quantity'])
        entry = Decimal(sig['entry'])
        stop = Decimal(sig['stop'])
        fx = Decimal('5')
        snap = {
            'complete': True,
            'daily_pnl_verified': True,
            'weekly_pnl_verified': True,
            'broker_reconciled': True,
            'daily_loss_halt_active': False,
            'weekly_loss_halt_active': False,
            'positions': [],
            'daily_pnl_brl': '0',
            'weekly_pnl_brl': '0',
            'available_cash_brl': '1000000',
            'has_pending_orders': False,
        }
        candidate = {
            'market': 'CRYPTO',
            'symbol': 'BTCUSD',
            'side': 'buy',
            'verified': True,
            'trading_mode': 'PAPER',
            'quantity': sig['quantity'],
            'entry_brl': str(entry * fx),
            'stop_brl': str(stop * fx),
        }
        self.assertTrue(portfolio_evaluate(candidate, snap)['allowed'])

    def test_research_phase_blocks_paper_at_gate_b(self):
        levels = {'entry': '100', 'stop': '99', 'target': '102', 'quantity': 1}
        with tempfile.TemporaryDirectory() as td:
            q = Path(td)
            emit_internal_signal(
                strategy_key='momentum',
                symbol='AAPL',
                asset_class='us_equity',
                bar_date='2026-10-27',
                levels=levels,
                queue=q,
                now=self.now,
                secret=self.secret,
            )
            sig = json.loads(next(q.glob('*.json')).read_text())
        decision = evaluate_signed_signal(sig, fx=Decimal('5'), now=self.now, strategy_phase='research')
        self.assertEqual(decision['reject_code'], 'STRATEGY_PHASE_BLOCKED')
        self.assertNotEqual(decision.get('decision'), 'paper_allowed')


if __name__ == '__main__':
    unittest.main()