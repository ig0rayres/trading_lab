import unittest
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
s=spec_from_file_location('news_catalog', Path(__file__).resolve().parents[1]/'src'/'news_catalog.py')
m=module_from_spec(s);s.loader.exec_module(m)

class CatalogTests(unittest.TestCase):
    def audit(self):
        return {'mode':'NEWS_COVERAGE_AUDIT_READ_ONLY','health':'OK_DATA_COVERAGE_DIAGNOSTIC',
                'all_pages_fetched':True,'requested_symbols':['AAPL'],'articles':[
                    {'id':1,'created_at':'2026-09-01T10:00:00Z','symbols':['AAPL','MSFT'],
                     'headline':'Apple beats earnings estimates','url':'https://example.com/article','source':'benzinga'},
                    {'id':2,'created_at':'2026-09-01T11:00:00Z','symbols':['MSFT'],
                     'headline':'Microsoft earnings','url':'https://example.com/2'},
                ]}
    def test_requires_complete_pagination(self):
        a=self.audit();a['all_pages_fetched']=False
        with self.assertRaises(ValueError):m.build_catalog(a)
    def test_tags_are_not_verified(self):
        r=m.build_catalog(self.audit());self.assertEqual(r['summary']['relevant_articles'],1)
        self.assertEqual(r['events'][0]['candidate_types'], ['EARNINGS'])
        self.assertFalse(r['events'][0]['strategy_eligible'])
        self.assertFalse(r['authorized_to_trade']);self.assertEqual(r['orders_sent'],0)
    def test_rejects_missing_timestamp(self):
        a=self.audit();a['articles'][0]['created_at']='bad'
        self.assertEqual(m.build_catalog(a)['summary']['relevant_articles'],0)
    def test_no_direction_inferred(self):
        self.assertEqual(m.build_catalog(self.audit())['events'][0]['direction'],'UNKNOWN')
    def test_no_false_earnings_keyword(self):
        self.assertEqual(m.classify('Apple releases a new MacBook'), [])
if __name__=='__main__':unittest.main()
