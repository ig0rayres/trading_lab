import argparse
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from src import news_audit as a

ENV = {'LIVE_TRADING_ENABLED':'false','ALPACA_PAPER_TRADE':'true', 'ALPACA_BASE_URL':'https://paper-api.alpaca.markets','ALPACA_API_KEY':'fake','ALPACA_SECRET_KEY':'fake'}
ARGS = argparse.Namespace(start='2026-09-01',end='2026-09-15',symbols='AAPL,MSFT',pages=3)

class NewsAuditTests(unittest.TestCase):
    def test_fail_closed_live(self):
        with self.assertRaises(ValueError): a.validate(ARGS, dict(ENV, LIVE_TRADING_ENABLED='true'))
    def test_reject_future(self):
        args = argparse.Namespace(**vars(ARGS));args.end=(datetime.now(timezone.utc)+timedelta(days=20)).strftime('%Y-%m-%d')
        with self.assertRaises(ValueError):a.validate(args, ENV)
    def test_deduplicate_and_quality(self):
        row={'id':1,'created_at':'2026-09-03T10:00:00Z','headline':'Company results','source':'Benzinga','symbols':['AAPL'],'url':'https://example.com'}
        counts,records=a.review_articles([row,row])
        self.assertEqual(counts['unique_articles'],1)
        self.assertEqual(counts['duplicate_articles_removed'],1)
        self.assertEqual(len(records),1)
    def test_multi_page_and_no_orders(self):
        def fetch(params,env):
            if 'page_token' not in params:
                return {'news':[{'id':1,'created_at':'2026-09-03T10:00:00Z'}], 'next_page_token':'next'}
            return {'news':[{'id':2,'created_at':'2026-09-04T10:00:00Z'}]}
        result=a.run_audit(ARGS,ENV,fetch)
        self.assertTrue(result['all_pages_fetched'])
        self.assertEqual(result['coverage']['unique_articles'],2)
        self.assertFalse(result['strategy_eligible'])
        self.assertEqual(result['orders_sent'],0)
    def test_limited_pagination_is_partial(self):
        args=argparse.Namespace(**vars(ARGS));args.pages=1
        result=a.run_audit(args,ENV,lambda p,e:{'news':[],'next_page_token':'next'})
        self.assertEqual(result['health'],'PARTIAL_PAGINATED_COVERAGE')
    def test_only_fixed_host_get(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self,*a): return False
            def read(self):return b'{"news": []}'
        def opener(req,timeout):
            self.assertTrue(req.full_url.startswith('https://data.alpaca.markets/v1beta1/news?'))
            self.assertEqual(req.get_method(),'GET')
            return Response()
        self.assertEqual(a.get_page({'symbols':'AAPL'},ENV,opener)['news'],[])
