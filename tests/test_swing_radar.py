import sys
import unittest
from datetime import date, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from swing_radar import technical, rank, sec_fundamentals, yahoo_daily

class SwingRadarTests(unittest.TestCase):
    def candles(self):
        start = date.today()-timedelta(days=79)
        return [{'day': (start+timedelta(days=i)).isoformat(), 'close': 100+i*0.2,
                 'high': 101+i*0.2, 'low': 99+i*0.2, 'volume': 1000} for i in range(80)]

    def test_technical(self):
        t = technical(self.candles())
        self.assertEqual(t['trend'], 'UP')
        self.assertGreater(t['atr14'], 0)
    def test_stale(self):
        c = self.candles()
        for bar in c:
            bar['day'] = '2020-01-01'
        with self.assertRaises(ValueError): technical(c)
    def test_no_orders(self):
        decision = rank(technical(self.candles()), [], {'status':'UNAVAILABLE'})
        self.assertFalse(decision['order_eligible'])
        self.assertEqual(decision['signal'], 'NO_TRADE')
    def test_sec_etf(self):
        self.assertEqual(sec_fundamentals('SPY', {} )['status'], 'NOT_APPLICABLE')
        self.assertEqual(sec_fundamentals('QQQ', {} )['status'], 'NOT_APPLICABLE')
    def test_etfs_never_request_sec_companyfacts(self):
        def forbidden_fetch(url):
            raise AssertionError('ETF should not request SEC companyfacts')
        for symbol in ('SPY', 'QQQ'):
            self.assertEqual(sec_fundamentals(symbol, {symbol: 12345}, fetch=forbidden_fetch)['status'], 'NOT_APPLICABLE')

    def test_yahoo_invalid(self):
        with self.assertRaises(ValueError): yahoo_daily('AAPL', fetch=lambda url: {'chart':{'result':[]}})

if __name__ == '__main__': unittest.main()
