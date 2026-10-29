import io
import json
import unittest
from unittest.mock import patch
from v4_alpaca_activities import parse_activity, normalize_pages, fetch_pages


def activity(i, **kw):
    a = {'id': str(i), 'activity_type': 'FILL', 'symbol': 'AAPL', 'side': 'buy',
         'qty': '2', 'price': '101.1', 'transaction_time': '2026-10-29T18:00:00Z'}
    a.update(kw)
    return a


class Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): self.close()


class Tests(unittest.TestCase):
    def test_normal(self):
        self.assertEqual(parse_activity(activity('a'))['fee'], None)
        self.assertFalse(normalize_pages([[activity('a')]])['complete'])
    def test_no_false_verified_pnl(self):
        r=normalize_pages([[activity('a')]])
        self.assertFalse(r['fees_verified'])
        self.assertFalse(r['broker_reconciled'])
        self.assertFalse(r['execution_authorized'])
        self.assertEqual(r['orders_sent'], 0)
    def test_duplicate(self):
        with self.assertRaisesRegex(ValueError,'DUPLICATE'):
            normalize_pages([[activity('a')],[activity('a')]])
    def test_conflicting_duplicate(self):
        with self.assertRaisesRegex(ValueError,'CONFLICTING'):
            normalize_pages([[activity('a')],[activity('a',price='99')]])
    def test_bad_prices(self):
        for bad in ['NaN','-1','0','Infinity']:
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                parse_activity(activity('a',qty=bad))
    def test_bad_timestamp(self):
        with self.assertRaises(ValueError):
            parse_activity(activity('a',transaction_time='2026-10-29T18:00:00'))
    def test_not_fill(self):
        with self.assertRaises(ValueError):
            parse_activity(activity('a',activity_type='DIV'))
    def test_fetch_pagination(self):
        env={'LIVE_TRADING_ENABLED':'false','ALPACA_PAPER_TRADE':'true',
             'ALPACA_BASE_URL':'https://paper-api.alpaca.markets',
             'ALPACA_API_KEY':'test','ALPACA_SECRET_KEY':'test', 'USD_BRL_REFERENCE':'5'}
        pages=[[activity('2'),activity('1')],[]]
        urls=[]
        def opener(req,timeout):
            self.assertEqual(req.get_method(),'GET')
            urls.append(req.full_url)
            return Response(json.dumps(pages.pop(0)).encode())
        r=fetch_pages(env,opener=opener,page_size=2)
        self.assertEqual(r['activity_count'],2)
        self.assertEqual(len(urls),2)
        self.assertIn('page_token=1',urls[-1])
    def test_page_limit_not_complete(self):
        env={'LIVE_TRADING_ENABLED':'false','ALPACA_PAPER_TRADE':'true',
             'ALPACA_BASE_URL':'https://paper-api.alpaca.markets',
             'ALPACA_API_KEY':'test','ALPACA_SECRET_KEY':'test', 'USD_BRL_REFERENCE':'5'}
        r=fetch_pages(env,opener=lambda req,timeout:Response(json.dumps([activity('1')]).encode()), max_pages=1,page_size=1)
        self.assertTrue(r['pagination_limit_hit'])
        self.assertFalse(r['complete'])
    def test_live_flag_blocks_before_network(self):
        with self.assertRaises(ValueError):
            fetch_pages({'LIVE_TRADING_ENABLED':'true'},opener=lambda *a: self.fail('network'))

if __name__ == '__main__':unittest.main()
