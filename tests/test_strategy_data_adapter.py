import json, tempfile, unittest
from pathlib import Path
from datetime import datetime,timezone,timedelta
from strategy_data_adapter import review

class AdapterTest(unittest.TestCase):
    def test_missing_equity_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);sid='123'
            for typ,rows in [('closed_trades',[]),('daily_equity',[{'DailyEquity':[]}])]:
                (p/f'{sid}_{typ}.json').write_text(json.dumps({'strategy_id':sid,'dataset':typ,'raw':{'Results':rows,'ResponseStatus':{'ErrorCode':0}}}))
            result,obs=review(p)
            self.assertFalse(result['providers'][0]['eligible_for_copy'])
            self.assertIn('EQUITY_NOT_LIST',result['providers'][0]['reasons'])
            self.assertFalse(obs['strategies'][0]['prior_paper_approved'])
    def test_equity_return_not_paper_pnl(self):
        now=datetime.now(timezone.utc);sid='123'
        def dt(x):return (now-timedelta(days=x)).isoformat()
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            rows=[{'Date':dt(200),'Equity':10000},{'Date':dt(170),'Equity':11000},{'Date':dt(2),'Equity':12000}]
            for typ,r in [('closed_trades',[{'CloseDate':dt(3),'ProfitLoss':1000,'Commission':10}]),('daily_equity',[{'DailyEquity':rows}])]:
                (p/f'{sid}_{typ}.json').write_text(json.dumps({'strategy_id':sid,'dataset':typ,'raw':{'Results':r,'ResponseStatus':{'ErrorCode':0}}}))
            result,obs=review(p,now)
            self.assertAlmostEqual(result['providers'][0]['windows']['180']['return_pct'],20.0)
            self.assertEqual(obs['strategies'][0]['trades'],[])
            self.assertFalse(result['providers'][0]['eligible_for_copy'])
    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as d:
            result,obs=review(Path(d))
            self.assertEqual(result['providers'],[])
            self.assertEqual(obs['strategies'],[])

class TimestampFormatTest(unittest.TestCase):
    def test_dotnet_date_and_date_only(self):
        from strategy_data_adapter import timestamp
        self.assertEqual(timestamp('/Date(1760000000000)/').timestamp(),1760000000)
        self.assertEqual(timestamp('2026-10-28').isoformat(),'2026-10-28T00:00:00+00:00')
    def test_error_reports_type_and_safe_detail(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);sid='555'
            (p/f'{sid}_closed_trades.json').write_text(json.dumps({'strategy_id':sid,'dataset':'closed_trades','raw':{'Results':[],'ResponseStatus':{'ErrorCode':5}}}))
            report,_=review(p)
            rec=report['providers'][0]
            self.assertEqual(rec['status'],'INSUFFICIENT_DATA')
            self.assertIn('source_error_type',rec)
            self.assertIn('api error',rec['source_error_detail'])

class Collective2ActualShapeTest(unittest.TestCase):
    def test_http_200_and_equity_with_costs(self):
        now=datetime(2026,10,28,tzinfo=timezone.utc)
        def dt(days):return (now-timedelta(days=days)).strftime('%Y-%m-%dT12:00:00Z')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); sid='148311109'
            equity=[{'Date':dt(190),'Index':7000,'EquityWithCosts':10000,'EquityBeforeCosts':10500},
                    {'Date':dt(30),'Index':7500,'EquityWithCosts':11000,'EquityBeforeCosts':12000},
                    {'Date':dt(1),'Index':7700,'EquityWithCosts':11200,'EquityBeforeCosts':13000}]
            for kind,results in [('daily_equity',[{'StrategyId':int(sid),'DailyEquity':equity}]),
                                 ('closed_trades',[{'CloseDate':dt(1),'ProfitLoss':100,'Commission':2}])]:
                (p/f'{sid}_{kind}.json').write_text(json.dumps({'strategy_id':int(sid),'dataset':kind,'raw':{'Results':results,'ResponseStatus':{'ErrorCode':'200'}}}))
            report,obs=review(p,now)
            rec=report['providers'][0]
            self.assertAlmostEqual(rec['windows']['180']['return_pct'],12.0)
            self.assertEqual(rec['windows']['180']['closed_trades'],1)
            self.assertEqual(rec['windows']['180']['max_drawdown_pct'],0)
            self.assertNotIn('UNRECOGNIZED_EQUITY_FIELDS',rec['reasons'])
            self.assertFalse(rec['eligible_for_copy'])
            self.assertEqual(obs['strategies'][0]['trades'],[])
    def test_unknown_api_status_still_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);sid='123'
            (p/f'{sid}_closed_trades.json').write_text(json.dumps({'strategy_id':sid,'dataset':'closed_trades','raw':{'Results':[],'ResponseStatus':{'ErrorCode':'401'}}}))
            report,_=review(p)
            self.assertIn('INVALID_OR_MISSING_SOURCE_DATA',report['providers'][0]['reasons'])
