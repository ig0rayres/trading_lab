import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from v4_cost_model import economic_result


def ticket():
    return {'currency':'BRL','quantity':100,'entry_price':10,'exit_price':10.2,
            'costs':{'entry_commission':1,'exit_commission':1,'exchange_fees':0.5,
                     'taxes':0,'spread_bps_entry':10,'spread_bps_exit':10,
                     'slippage_bps_entry':5,'slippage_bps_exit':5,
                     'funding':0,'fx_fees':0,'monthly_subscriptions':120,
                     'monthly_data':60,'monthly_infra':30,'expected_monthly_trades':10,
                     'impact_already_in_fill':False}}

class TestEconomicCosts(unittest.TestCase):
    def test_all_costs_and_overhead(self):
        result=economic_result(ticket())
        self.assertEqual(result['gross_pnl'],'20.0')
        self.assertEqual(result['allocated_overhead'],'21')
        self.assertFalse(result['net_positive'])
        self.assertLess(float(result['economic_net_pnl']),0)
    def test_missing_cost_fails_closed(self):
        t=ticket();del t['costs']['taxes']
        with self.assertRaisesRegex(ValueError,'MISSING_COST_TAXES'): economic_result(t)
    def test_double_count_fails(self):
        t=ticket();del t['costs']['impact_already_in_fill']
        with self.assertRaisesRegex(ValueError,'AMBIGUOUS_IMPACT'):economic_result(t)
    def test_negative_and_nan_rejected(self):
        for v in ('NaN',-1):
            t=ticket();t['costs']['funding']=v
            with self.assertRaises(ValueError):economic_result(t)
    def test_zero_trades_rejected(self):
        t=ticket();t['costs']['expected_monthly_trades']=0
        with self.assertRaises(ValueError):economic_result(t)
    def test_no_double_count_with_executable_fills(self):
        t=ticket();t['costs']['impact_already_in_fill']=True
        for k in ('spread_bps_entry','spread_bps_exit','slippage_bps_entry','slippage_bps_exit'):
            t['costs'][k]=0
        self.assertIn('economic_net_pnl',economic_result(t))

if __name__=='__main__':unittest.main()
