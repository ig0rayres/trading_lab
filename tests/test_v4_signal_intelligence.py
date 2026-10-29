import copy
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from src.v4_signal_intelligence import consolidate
from src.signal_copy import sign

NOW = datetime(2026, 10, 29, 16, tzinfo=timezone.utc)
BASE = {'automatic_order_submission': False, 'usable_for_live_trading': False,
        'observations': {'B3_EQUITY:ITUB4': {'market': 'B3_EQUITY', 'symbol': 'ITUB4',
            'source_sha256': 'a'*64, 'market_data_source': 'TEST', 'radar_candidate': True,
            'issues': ['QUALITY_UNVERIFIED'], 'tradable_signal': False,
            'paper_approved': False, 'orders_sent': 0}}, 'errors': {}}
NEWS = {'mode': 'NEWS_FIRST_INTERNAL_SIMULATION', 'authorized_to_trade': False,
        'orders_sent': 0, 'signals': [{'symbol': 'AAPL', 'article_id': 'article1',
         'decision': 'NO_TRADE', 'research_status': 'EVIDENCE_PENDING', 'quantity': 0,
         'blocker_reasons': ['SOURCE_UNVERIFIED']}]}
SECRET = 'secret-from-test-only-do-not-use-in-prod-123'
SIGNAL = {'provider': 'tradingview', 'signal_id': 'testsignal-123456', 'symbol': 'AAPL',
          'side': 'buy', 'asset_class': 'us_equity', 'sent_at_utc': NOW.isoformat(),
          'entry': '100', 'stop': '99', 'target': '102', 'quantity': 1, 'ttl_seconds': 30}

class TestSignalIntelligence(unittest.TestCase):
    def test_merges_three_sources_without_execution(self):
        payload = dict(SIGNAL); payload['provider_signature'] = sign(payload, SECRET)
        out = consolidate(BASE, NEWS, [payload], secret=SECRET, fx=Decimal('5'), now=NOW)
        self.assertEqual(len(out['decisions']), 3)
        self.assertFalse(out['automatic_order_submission'])
        self.assertEqual(out['orders_sent'], 0)
        self.assertTrue(all(x['decision'] == 'RESEARCH_ONLY' and not x['paper_approved'] for x in out['decisions']))
        self.assertTrue(out['decisions'][-1]['candidate'])
        self.assertIn('BROKER_PRICE_AND_PORTFOLIO_NOT_RECONCILED', out['decisions'][-1]['blockers'])

    def test_bad_signature_is_not_candidate(self):
        payload = dict(SIGNAL); payload['provider_signature'] = 'invalid'
        out = consolidate(BASE, signals=[payload], secret=SECRET, fx=Decimal('5'), now=NOW)
        self.assertFalse(out['decisions'][-1]['candidate'])
        self.assertIn('AUTH_FAILED', out['decisions'][-1]['blockers'])

    def test_duplicate_signal_detected(self):
        out = consolidate(BASE, NEWS, [dict(SIGNAL), dict(SIGNAL)], secret=SECRET, fx=Decimal('5'), now=NOW)
        self.assertIn('external:1', out['errors'])
        self.assertEqual(len(out['decisions']), 3)

    def test_unsafe_market_report_refused(self):
        report = copy.deepcopy(BASE); report['automatic_order_submission'] = True
        with self.assertRaises(ValueError): consolidate(report)

    def test_unsafe_news_refused(self):
        news = copy.deepcopy(NEWS); news['authorized_to_trade'] = True
        with self.assertRaises(ValueError): consolidate(BASE, news)

    def test_unsafe_individual_observation_isolated(self):
        report = copy.deepcopy(BASE); report['observations']['B3_EQUITY:ITUB4']['paper_approved'] = True
        out = consolidate(report)
        self.assertEqual(len(out['decisions']), 0)
        self.assertIn('market:B3_EQUITY:ITUB4', out['errors'])

    def test_malformed_news_isolated(self):
        news = copy.deepcopy(NEWS); news['signals'].append({'symbol': 'AAPL', 'quantity': 2})
        out = consolidate(BASE, news)
        self.assertEqual(out['status'], 'PARTIAL_OR_BLOCKED')
        self.assertEqual(len(out['decisions']), 2)

if __name__ == '__main__': unittest.main()
