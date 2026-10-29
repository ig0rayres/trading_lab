import sys
import unittest
sys.path.insert(0, '/app/src' if __import__('os').path.exists('/app/src/event_verifier.py') else __import__('os').path.join(__import__('os').path.dirname(__file__), '..', 'src'))
from event_verifier import assess, build_report

class EvidenceTriageTests(unittest.TestCase):
    def test_third_party_earnings_not_attributed(self):
        r=assess({'headline':'Dell crushes earnings; Nvidia supplier reacts','requested_symbols_mentioned':['NVDA'],'candidate_types':['EARNINGS']})
        self.assertEqual(r['relation'],'DIRECT_MENTION_NEEDS_REVIEW')
        self.assertFalse(r['strategy_eligible'])
        r=assess({'headline':'Dell crushes earnings','requested_symbols_mentioned':['NVDA'],'candidate_types':['EARNINGS']})
        self.assertEqual(r['relation'],'EARNINGS_NOT_ATTRIBUTABLE_TO_TRACKED_ISSUER')
    def test_direct_issuer_is_not_verified(self):
        r=assess({'headline':'Microsoft adjusts guidance','requested_symbols_mentioned':['MSFT'],'candidate_types':['GUIDANCE']})
        self.assertEqual(r['relation'],'DIRECT_MENTION_NEEDS_REVIEW')
        self.assertFalse(r['primary_source_verified'])
    def test_no_duplicates_auto_merge(self):
        a={'article_id':1,'headline':'Nvidia announces major acquisition of Hugging Face','requested_symbols_mentioned':['NVDA'],'candidate_types':['CORPORATE_ACTION']}
        b={'article_id':2,'headline':'Nvidia major acquisition of Hugging Face announced','requested_symbols_mentioned':['NVDA'],'candidate_types':['CORPORATE_ACTION']}
        r=build_report({'mode':'NEWS_EVENT_CATALOG_READ_ONLY','health':'OK_UNVERIFIED_LEADS','events':[a,b]})
        self.assertEqual(len(r['review_queue']),2)
        self.assertEqual(len(r['duplicate_suggestions']),1)
        self.assertEqual(r['summary']['verified_events'],0)
        self.assertFalse(r['authorized_to_trade'])
    def test_fail_closed(self):
        with self.assertRaises(ValueError): build_report({'mode':'wrong','events':[]})
if __name__ == '__main__': unittest.main()
