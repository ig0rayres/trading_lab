import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from v4_run_once import build, parse_universe, atomic_json


class TestOnce(unittest.TestCase):
    def test_universe(self):
        self.assertEqual(parse_universe([{'market': 'B3_EQUITY', 'symbol': 'ITUB4'}]), [('B3_EQUITY', 'ITUB4')])
        for invalid in ([], [{}], [{'market': 'CRYPTO', 'symbol': '../BTC'}],
                        [{'market': 'US_EQUITY', 'symbol': 'AAPL'}] * 2):
            with self.assertRaises(ValueError):
                parse_universe(invalid)

    def test_n27_parse_universe_accepts_forex_symbol(self):
        """N27.1: FOREX is a first-class universe market, not junk."""
        parsed = parse_universe([{'market': 'FOREX', 'symbol': 'EURUSD'}])
        self.assertEqual(parsed, [('FOREX', 'EURUSD')])

    def test_n27_config_universe_lists_forex_pair(self):
        """N27.1: shipped universe.json includes at least one FOREX pair."""
        path = Path(__file__).resolve().parents[1] / 'config' / 'universe.json'
        rows = json.loads(path.read_text(encoding='utf-8'))
        forex = [row for row in rows if row.get('market') == 'FOREX']
        self.assertGreaterEqual(len(forex), 1)
        self.assertTrue(all(row.get('symbol', '').strip() for row in forex))

    def test_full_readonly_path(self):
        def broken(**kwargs):
            raise TimeoutError('upstream missing')
        result = build([('B3_EQUITY', 'ITUB4'), ('CRYPTO', 'BTCBRL')], equity_fetch=broken, crypto_fetch=broken)
        self.assertEqual(result['manifest']['status'], 'PARTIAL_OR_BLOCKED')
        self.assertFalse(result['manifest']['execution_authorized'])
        self.assertEqual(result['manifest']['orders_sent'], 0)
        self.assertEqual(len(result['market']['errors']), 2)

    def test_atomic_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'report.json'
            atomic_json(path, {'orders_sent': 0})
            self.assertIn('orders_sent', path.read_text())
            with self.assertRaises(ValueError):
                atomic_json(Path(tmp) / 'wrong.txt', {})

if __name__ == '__main__':
    unittest.main()
