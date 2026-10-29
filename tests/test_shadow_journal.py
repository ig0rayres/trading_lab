import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from shadow_journal import capture, summarize


def fixture(day=None):
    day = day or datetime.now(timezone.utc).date().isoformat()
    return {'mode': 'READ_ONLY_RESEARCH_NO_ORDERS', 'health': 'OK_RESEARCH_ONLY',
            'paper_execution_authorized': False, 'live_execution_authorized': False,
            'errors': [], 'paper_account': {'status': 'READ_ONLY_DIAGNOSTIC_NO_ORDERS',
                                           'paper_execution_authorized': False, 'open_orders': 0, 'open_positions': 0},
            'candidates': [{'symbol': sym, 'technical': {'as_of': day, 'last_close': px},
                            'ranking': {'signal': 'NO_TRADE', 'order_eligible': False, 'attention_score': 2,
                                        'blockers': ['CATALYST_NOT_PRIMARY_SOURCE_VERIFIED']},
                            'fundamental': {'status': 'ANNUAL_COMPARABLE'}} for sym, px in [('AAPL', 100), ('SPY', 500)]]}


AFTER_CLOSE = datetime.now(ZoneInfo('America/New_York')).replace(hour=16, minute=30)

class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.j = str(Path(self.temp.name) / 'observations.jsonl')
        self.s = str(Path(self.temp.name) / 'summary.json')

    def test_reject_intraday_current_session(self):
        early = AFTER_CLOSE.replace(hour=13, minute=0)
        with self.assertRaises(ValueError): capture(fixture(), self.j, self.s, now_ny=early)

    def test_capture_only_once_per_session(self):
        a = capture(fixture(), self.j, self.s, now_ny=AFTER_CLOSE)
        b = capture(fixture(), self.j, self.s, now_ny=AFTER_CLOSE)
        self.assertEqual(a['unique_observation_days'], 1)
        self.assertTrue(b['duplicate_market_day_skipped'])
        self.assertEqual(len(Path(self.j).read_text().splitlines()), 1)
        self.assertEqual(b['matured_outcomes'], 0)

    def test_reject_degraded(self):
        f = fixture(); f['health'] = 'PARTIAL_DATA'
        with self.assertRaises(ValueError): capture(f, self.j, self.s, now_ny=AFTER_CLOSE)

    def test_reject_unapproved_signal(self):
        f = fixture(); f['candidates'][0]['ranking']['signal'] = 'BUY'
        with self.assertRaises(ValueError): capture(f, self.j, self.s, now_ny=AFTER_CLOSE)

    def test_reject_open_orders(self):
        f = fixture(); f['paper_account']['open_orders'] = 1
        with self.assertRaises(ValueError): capture(f, self.j, self.s, now_ny=AFTER_CLOSE)

    def test_reject_missing_broker(self):
        f = fixture(); f['paper_account'] = {}
        with self.assertRaises(ValueError): capture(f, self.j, self.s, now_ny=AFTER_CLOSE)

    def test_reject_live_flag(self):
        prior = os.environ.get('LIVE_TRADING_ENABLED')
        os.environ['LIVE_TRADING_ENABLED'] = 'true'
        try:
            with self.assertRaises(ValueError): capture(fixture(), self.j, self.s, now_ny=AFTER_CLOSE)
        finally:
            if prior is None: os.environ.pop('LIVE_TRADING_ENABLED', None)
            else: os.environ['LIVE_TRADING_ENABLED'] = prior

    def test_forward_only_maturity_and_spy(self):
        rows = []
        for d in range(6):
            rows.append({'market_day': f'2026-10-{10 + d:02}', 'assets': {
                'AAPL': {'close': 100+d, 'decision': 'NO_TRADE', 'blockers': []},
                'SPY': {'close': 200+d, 'decision': 'NO_TRADE', 'blockers': []}}})
        r = summarize(rows)
        self.assertEqual(r['matured_outcomes'], 2)
        x = next(o for o in r['outcomes'] if o['symbol'] == 'AAPL')
        self.assertEqual(x['close_to_close_pct'], 5.0)
        self.assertEqual(x['spy_same_period_pct'], 2.5)
        self.assertEqual(x['excess_vs_spy_pct'], 2.5)
        self.assertEqual(x['decision'], 'NO_TRADE')

if __name__ == '__main__': unittest.main()
