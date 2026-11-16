import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

from original import load_original
from scanner_family_producer import TA_BARATO_SETUPS, load_producer_universe, run_once


def _equity_row(closes, bar_date='2026-10-27'):
    bars = [{'at_utc': f'{bar_date}T00:00:00+00:00', 'close': str(c)} for c in closes]
    return {'market': 'US_EQUITY', 'symbol': 'TEST', 'bars': bars}


class ScannerFamilyProducerTests(unittest.TestCase):
    def setUp(self):
        os.environ['SIGNAL_COPY_SECRET'] = 's' * 32
        os.environ['USD_BRL_REFERENCE'] = '5'
        os.environ['LIVE_TRADING_ENABLED'] = 'false'
        self.now = datetime(2026, 10, 28, 19, 0, tzinfo=timezone.utc)
        self.orig = load_original()

    def test_universe_excludes_b3_and_forex(self):
        rows = load_producer_universe()
        markets = {m for m, _s in rows}
        self.assertIn('US_EQUITY', markets)
        self.assertIn('CRYPTO', markets)
        self.assertNotIn('B3_EQUITY', markets)
        self.assertNotIn('FOREX', markets)

    def test_momentum_tag_emits_momentum_not_ta_barato(self):
        closes = [100.0] * 34 + [150.0]
        tags, _ = self.orig.scanner.find_setups(closes)
        self.assertIn('breakout_20d', tags)
        self.assertFalse(TA_BARATO_SETUPS & set(tags))

        def fake_equity_fetch(**_kwargs):
            return _equity_row(closes)

        with tempfile.TemporaryDirectory() as td:
            q = Path(td)
            report = run_once(
                orig=self.orig,
                universe=[('US_EQUITY', 'TEST')],
                equity_fetch=fake_equity_fetch,
                crypto_fetch=lambda **_k: {'bars': []},
                queue=q,
                now=self.now,
                secret='s' * 32,
            )
        keys = [r.get('strategy_key') for r in report['signals'] if r.get('status') == 'QUEUED']
        self.assertIn('momentum', keys)
        self.assertNotIn('ta_barato', keys)
        self.assertEqual(report['orders_sent'], 0)

    def test_oversold_only_emits_ta_barato(self):
        def fake_find(closes):
            return (['oversold'], {'rsi': 25.0})

        scanner = SimpleNamespace(find_setups=fake_find, rsi=self.orig.scanner.rsi)
        orig = SimpleNamespace(
            scanner=scanner,
            exit=self.orig.exit,
            budget=self.orig.budget,
        )
        closes = [100.0] * 35

        def fake_equity_fetch(**_kwargs):
            return _equity_row(closes)

        with tempfile.TemporaryDirectory() as td:
            q = Path(td)
            report = run_once(
                orig=orig,
                universe=[('US_EQUITY', 'TEST')],
                equity_fetch=fake_equity_fetch,
                crypto_fetch=lambda **_k: {'bars': []},
                queue=q,
                now=self.now,
                secret='s' * 32,
            )
        keys = [r.get('strategy_key') for r in report['signals'] if r.get('status') == 'QUEUED']
        self.assertIn('ta_barato', keys)
        self.assertNotIn('momentum', keys)

    def test_crypto_momentum_fractional_not_skip_size(self):
        closes = [95000.0] * 34 + [96000.0]

        def fake_crypto_fetch(**_kwargs):
            bars = [{'at_utc': '2026-10-27T00:00:00+00:00', 'close_brl': str(c)} for c in closes]
            return {'market': 'CRYPTO', 'symbol': 'BTCUSD', 'bars': bars}

        with tempfile.TemporaryDirectory() as td:
            report = run_once(
                orig=self.orig,
                universe=[('CRYPTO', 'BTCUSD')],
                equity_fetch=lambda **_k: {'bars': []},
                crypto_fetch=fake_crypto_fetch,
                queue=Path(td),
                now=self.now,
                secret='s' * 32,
            )
        queued = [r for r in report['signals'] if r.get('status') == 'QUEUED']
        self.assertTrue(any(r.get('strategy_key') == 'momentum' for r in queued))
        self.assertFalse(any(r.get('status') == 'SKIP_SIZE' for r in report['signals']))

    def test_breakout_only_zero_ta_barato(self):
        closes = [100.0] * 34 + [150.0]

        def fake_equity_fetch(**_kwargs):
            return _equity_row(closes)

        with tempfile.TemporaryDirectory() as td:
            report = run_once(
                orig=self.orig,
                universe=[('US_EQUITY', 'TEST')],
                equity_fetch=fake_equity_fetch,
                crypto_fetch=lambda **_k: {'bars': []},
                queue=Path(td),
                now=self.now,
                secret='s' * 32,
            )
        ta = [r for r in report['signals'] if r.get('strategy_key') == 'ta_barato']
        self.assertEqual(ta, [])


if __name__ == '__main__':
    unittest.main()