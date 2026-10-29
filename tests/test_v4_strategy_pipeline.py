import copy
import unittest
from datetime import datetime, timedelta, timezone
from src.v4_strategy_pipeline import assess_feed, run

NOW = datetime(2026, 10, 29, tzinfo=timezone.utc)


def fixture(market='B3_EQUITY'):
    crypto = market == 'CRYPTO'
    symbol = 'BTCBRL' if crypto else ('ITUB4' if market == 'B3_EQUITY' else 'AAPL')
    suffix = '_brl' if crypto else ''
    bars = []
    for i, price in enumerate([100, 101, 102, 101, 96, 89, 91]):
        bars.append({'at_utc': (NOW - timedelta(days=8-i)).isoformat(),
                     'close'+suffix: str(price), 'high'+suffix: str(price+1),
                     'low'+suffix: str(price-1), 'complete': True, 'verified': False})
    return {'market':market,'symbol':symbol,'denomination':'USD' if market == 'US_EQUITY' else 'BRL',
            'venue':'TEST', 'source_sha256':'a'*64, 'bars':bars,
            'provenance_level':'SINGLE_PUBLIC_EXCHANGE_RESPONSE' if crypto else 'SINGLE_PUBLIC_DATA_PROVIDER',
            'usable_for_live_trading':False, 'independent_market_verification':False}


class PipelineTest(unittest.TestCase):
    def test_three_markets_remain_shadow(self):
        for market in ('US_EQUITY','B3_EQUITY','CRYPTO'):
            result = assess_feed(fixture(market), now=NOW)
            self.assertTrue(result['radar_candidate'])
            self.assertFalse(result['tradable_signal'])
            self.assertFalse(result['paper_approved'])
            self.assertIn('QUALITY_UNVERIFIED', result['issues'])
            self.assertIn('CATALYST_NOT_REVIEWED', result['issues'])
            self.assertFalse(result['volume_available'])

    def test_blocks_wrong_currency(self):
        feed=fixture();feed['denomination']='USD'
        with self.assertRaises(ValueError):assess_feed(feed,now=NOW)

    def test_blocks_verified_vendor_claim(self):
        feed=fixture();feed['bars'][0]['verified']=True
        with self.assertRaises(ValueError):assess_feed(feed,now=NOW)

    def test_blocks_future_bar(self):
        feed=fixture();feed['bars'][-1]['at_utc']=(NOW+timedelta(days=1)).isoformat()
        with self.assertRaises(ValueError):assess_feed(feed,now=NOW)

    def test_blocks_live_eligible_feed(self):
        feed=fixture();feed['usable_for_live_trading']=True
        with self.assertRaises(ValueError):assess_feed(feed,now=NOW)

    def test_errors_isolated(self):
        feed=fixture()
        result=run({'results':{'B3_EQUITY:ITUB4':feed,'BAD:FOO':copy.deepcopy(feed)},'errors':{},
                    'automatic_order_submission':False,'usable_for_live_trading':False},now=NOW)
        self.assertEqual(len(result['observations']),1)
        self.assertIn('BAD:FOO',result['errors'])
        self.assertFalse(result['automatic_order_submission'])

    def test_unsafe_cycle_refused(self):
        with self.assertRaises(ValueError):run({'automatic_order_submission': True, 'usable_for_live_trading':False,'results':{}})

    def test_duplicate_bar_rejected(self):
        feed=fixture();feed['bars'][3]['at_utc']=feed['bars'][2]['at_utc']
        with self.assertRaises(ValueError):assess_feed(feed,now=NOW)
