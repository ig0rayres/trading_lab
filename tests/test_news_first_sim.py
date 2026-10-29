import sys,unittest,tempfile,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from news_first_sim import make_report,persist

class NewsFirstSimTests(unittest.TestCase):
    def sample(self):
        return {'mode':'NEWS_EVENT_EVIDENCE_TRIAGE_READ_ONLY','health':'OK_UNVERIFIED_REVIEW_QUEUE',
            'review_queue':[{'article_id':123,'tracked_symbols':['AAPL'], 'direct_issuer_mentions':['AAPL'],
            'headline':'Apple results','provider_created_at_utc':'2026-10-01T12:00:00+00:00'}]}
    def test_no_trade(self):
        r=make_report(self.sample()); self.assertEqual(r['signals'][0]['decision'],'NO_TRADE');self.assertEqual(r['orders_sent'],0)
        self.assertEqual(r['signals'][0]['quantity'],0);self.assertEqual(r['summary']['actionable_signals'],0)
    def test_indirect_blocked(self):
        r=self.sample();r['review_queue'][0]['direct_issuer_mentions']=[]
        self.assertIn('ISSUER_NOT_CONFIRMED_DIRECT',make_report(r)['signals'][0]['blocker_reasons'])
    def test_unhealthy_refused(self):
        r=self.sample();r['health']='BLOCKED_INPUT'
        with self.assertRaises(ValueError):make_report(r)
    def test_idempotent(self):
        with tempfile.TemporaryDirectory() as t:
            r=make_report(self.sample());a=f'{t}/a.json';b=f'{t}/b.jsonl'
            self.assertEqual(persist(r,a,b),1);self.assertEqual(persist(r,a,b),0)
            self.assertEqual(len(Path(b).read_text().splitlines()),1)
    def test_empty(self):
        r=self.sample();r['review_queue']=[]
        self.assertEqual(make_report(r)['summary']['review_signals'],0)
