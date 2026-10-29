import unittest
from datetime import datetime, timezone
from unittest.mock import patch
from swing_radar import sec_fundamentals, rank

class Preservation(unittest.TestCase):
    def test_mismatched_annual_periods_blocked(self):
        def f(url):
            return {'facts': {'us-gaap': {
                'Revenues': {'units': {'USD': [{'start':'2025-01-01','end':'2025-12-31','filed':'2026-02-01','form':'10-K','val':200}]}},
                'NetIncomeLoss': {'units': {'USD': [{'start':'2024-01-01','end':'2024-12-31','filed':'2025-02-01','form':'10-K','val':50}]}}
            }}}
        r = sec_fundamentals('AAPL', {'AAPL':320193}, fetch=f)
        self.assertEqual(r['status'], 'UNAVAILABLE_UNVERIFIED')
        self.assertIn('MISMATCHED_PERIODS', r['quality_flags'])

    def test_ytd_quarter_does_not_masquerade_as_annual(self):
        def f(url):
            return {'facts': {'us-gaap': {
                'Revenues': {'units': {'USD': [{'start':'2026-01-01','end':'2026-09-30','filed':'2026-10-15','form':'10-Q','val':200}]}},
                'NetIncomeLoss': {'units': {'USD': [{'start':'2026-01-01','end':'2026-09-30','filed':'2026-10-15','form':'10-Q','val':50}]}}
            }}}
        r = sec_fundamentals('AAPL', {'AAPL':320193}, fetch=f)
        self.assertEqual(r['status'], 'UNAVAILABLE_UNVERIFIED')

    def test_ranking_never_eligible_even_if_all_positive(self):
        tech={'trend':'UP','data_age_days':0,'volume_ratio20':1.9,'rsi14':55,'atr14':5,'last_close':100}
        paper={'status':'READ_ONLY_DIAGNOSTIC_NO_ORDERS','capital_ceiling_usd':'1000','planned_risk_per_trade_usd':'10'}
        r=rank(tech,[{'headline_tag':'POSITIVE_CLAIM'}],{'status':'ANNUAL_COMPARABLE'},'AAPL',paper)
        self.assertFalse(r['order_eligible'])
        self.assertEqual(r['signal'],'NO_TRADE')
        self.assertLessEqual(r['hypothetical_risk']['planned_loss_usd_if_stop_fills'], 10)
        self.assertLessEqual(r['hypothetical_risk']['position_notional_usd'], 333.34)
        self.assertIn('CATALYST_NOT_PRIMARY_SOURCE_VERIFIED',r['blockers'])

    def test_missing_broker_blocks_risk(self):
        tech={'trend':'UP','data_age_days':0,'volume_ratio20':1.9,'rsi14':55,'atr14':5,'last_close':100}
        r=rank(tech,[],{'status':'ANNUAL_COMPARABLE'},paper=None)
        self.assertIn('RISK_BUDGET_NOT_VERIFIED',r['blockers'])
        self.assertEqual(r['hypothetical_risk']['shares_cap_fractional_theoretical'],0)

if __name__ == '__main__': unittest.main()
