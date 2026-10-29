import unittest
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from day_radar import assess,bars_from_yahoo,run

class DayRadarTests(unittest.TestCase):
    def setUp(self):
        self.now=datetime(2026,10,27,11,0,tzinfo=ZoneInfo('America/New_York'))
        self.bars=[{'day':'2026-10-27','time':t,'open':100,'high':101,'low':99,'close':100,'volume':1000}
                   for t in ['09:30','09:35','09:40']]
    def test_no_breakout(self):
        x=assess('AAPL',self.bars,self.now)
        self.assertEqual(x['signal'],'NO_TRADE');self.assertIn('NO_COMPLETED_CONFIRMATION_BAR',x['blockers'])
    def test_breakout_not_trade(self):
        b=self.bars+[{'day':'2026-10-27','time':'09:45','open':100,'high':103,'low':100,'close':102,'volume':3000}]
        x=assess('AAPL',b,self.now)
        self.assertEqual(x['research_setup']['kind'],'ORB_15M_BREAKOUT')
        self.assertFalse(x['order_eligible']);self.assertEqual(x['signal'],'NO_TRADE')
    def test_short_breakdown_diagnostic_only(self):
        b=self.bars+[{'day':'2026-10-27','time':'09:45','open':100,'high':100,'low':97,'close':98,'volume':3000}]
        x=assess('AAPL',b,self.now)
        self.assertEqual(x['research_setups']['SHORT']['kind'],'ORB_15M_BREAKDOWN')
        self.assertIsNone(x['research_setups']['LONG'])
        self.assertIn('SHORT_BORROW_AND_MARGIN_NOT_VERIFIED',x['directions']['SHORT']['blockers'])
        self.assertFalse(x['directions']['SHORT']['order_eligible'])
        self.assertEqual(x['signal'],'NO_TRADE')
    def test_both_directions_not_orders(self):
        b=self.bars+[
          {'day':'2026-10-27','time':'09:45','open':100,'high':103,'low':100,'close':102,'volume':3000},
          {'day':'2026-10-27','time':'09:50','open':102,'high':103,'low':97,'close':98,'volume':3000}]
        x=assess('AAPL',b,self.now)
        self.assertEqual(x['research_setups']['LONG']['first_confirmation_bar_ny'],'09:45')
        self.assertEqual(x['research_setups']['SHORT']['first_confirmation_bar_ny'],'09:50')
        self.assertEqual(x['signal'],'NO_TRADE')
        self.assertTrue(all(not z['order_eligible'] for z in x['directions'].values()))
    def test_short_requires_close_below_low(self):
        b=self.bars+[{'day':'2026-10-27','time':'09:45','open':100,'high':102,'low':95,'close':99,'volume':3000}]
        x=assess('AAPL',b,self.now)
        self.assertIsNone(x['research_setups']['SHORT'])
        self.assertIn('NO_ORB_BREAKDOWN',x['directions']['SHORT']['blockers'])
    def test_wrong_time(self):
        x=assess('AAPL',self.bars,self.now.replace(hour=9,minute=40))
        self.assertIn('OUTSIDE_ORB_WINDOW',x['blockers'])
    def test_incomplete_bar_not_read(self):
        utc=datetime(2026,10,27,13,33,tzinfo=timezone.utc)
        payload={'chart':{'result':[{'timestamp':[int(datetime(2026,10,27,13,30,tzinfo=timezone.utc).timestamp())],
                'indicators':{'quote':[{'open':[100],'high':[101],'low':[99],'close':[100],'volume':[50]}]}}]}}
        self.assertEqual(bars_from_yahoo(payload,'AAA',utc),[])
    def test_run_zero_orders(self):
        o=run(['AAPL'],now_utc=self.now.astimezone(timezone.utc),fetch=lambda s,t:self.bars,output=None)
        self.assertEqual(o['broker_orders_sent'],0)
        self.assertEqual(o['candidates'][0]['signal'],'NO_TRADE')
    def test_data_failure(self):
        def bad(s,t):raise RuntimeError('network')
        r=run(['AAPL'],now_utc=self.now.astimezone(timezone.utc),fetch=bad,output=None)
        self.assertEqual(r['health'],'PARTIAL_DATA');self.assertFalse(r['candidates'][0]['order_eligible'])
