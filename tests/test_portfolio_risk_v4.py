import unittest
from portfolio_risk_v4 import evaluate


def setup():
    c = dict(market='B3_EQUITY', symbol='ITUB4', side='buy', verified=True,
             trading_mode='PAPER', quantity=10, entry_brl='40', stop_brl='37')
    s = dict(complete=True, daily_pnl_verified=True, weekly_pnl_verified=True,
             broker_reconciled=True, positions=[], daily_pnl_brl='0', weekly_pnl_brl='0',
             available_cash_brl='10000', has_pending_orders=False)
    return c,s

class PortfolioRiskTests(unittest.TestCase):
    def test_safe_paper_candidate(self):
        c,s=setup();self.assertTrue(evaluate(c,s)['allowed'])
    def test_rejects_missing_snapshot(self):
        c,s=setup();s['complete']=False;self.assertFalse(evaluate(c,s)['allowed'])
    def test_rejects_daily_halt(self):
        c,s=setup();s['daily_pnl_brl']='-200';self.assertIn('DAILY_LOSS_HALT',evaluate(c,s)['reasons'])
    def test_rejects_weekly_halt(self):
        c,s=setup();s['weekly_pnl_brl']='-500';self.assertIn('WEEKLY_LOSS_HALT',evaluate(c,s)['reasons'])
    def test_prodigy_lower_limit(self):
        c,s=setup();c['prodigy']=True;self.assertIn('DEFAULT_TRADE_RISK',evaluate(c,s)['reasons'])
    def test_duplicate_cross_market_portfolio(self):
        c,s=setup();s['positions']=[dict(market='B3_EQUITY',symbol='ITUB4',notional_brl=100,planned_risk_brl=10)];self.assertIn('DUPLICATE_EXPOSURE',evaluate(c,s)['reasons'])
    def test_aggregate_risk(self):
        c,s=setup();s['positions']=[dict(market='CRYPTO',symbol='BTC',notional_brl=800,planned_risk_brl=190)];self.assertIn('AGGREGATE_RISK_LIMIT',evaluate(c,s)['reasons'])
    def test_loss_budget_includes_new_trade(self):
        c,s=setup();s['daily_pnl_brl']='-175'
        self.assertIn('DAILY_LOSS_HALT',evaluate(c,s)['reasons'])
        c,s=setup();s['weekly_pnl_brl']='-480'
        self.assertIn('WEEKLY_LOSS_HALT',evaluate(c,s)['reasons'])
    def test_invalid_existing_position_blocks(self):
        c,s=setup();s['positions']=[dict(market='INVALID',symbol='BTC',notional_brl=100,planned_risk_brl=10)]
        self.assertFalse(evaluate(c,s)['allowed'])
    def test_duplicate_case_insensitive(self):
        c,s=setup();s['positions']=[dict(market='B3_EQUITY',symbol='itub4',notional_brl=100,planned_risk_brl=10)]
        self.assertIn('DUPLICATE_EXPOSURE',evaluate(c,s)['reasons'])
    def test_crypto_fractional_quantity(self):
        c,s=setup();c.update(market='CRYPTO',symbol='BTCUSDT',quantity='0.001',entry_brl='300000',stop_brl='290000')
        self.assertTrue(evaluate(c,s)['allowed'])
    def test_equity_fractional_quantity_blocked(self):
        c,s=setup();c['quantity']='0.5'
        self.assertIn('INVALID_ENTRY_STOP_OR_QUANTITY',evaluate(c,s)['reasons'])
    def test_cannot_self_approve_higher_risk(self):
        c,s=setup();c['quantity']=20;c['risk_override_approved']=True
        self.assertIn('DEFAULT_TRADE_RISK',evaluate(c,s)['reasons'])
    def test_duplicate_existing_positions_blocked(self):
        c,s=setup();s['positions']=[
          dict(market='CRYPTO',symbol='btc',notional_brl=100,planned_risk_brl=2),
          dict(market='CRYPTO',symbol='BTC',notional_brl=100,planned_risk_brl=2)]
        self.assertIn('DUPLICATE_EXISTING_POSITIONS',evaluate(c,s)['reasons'])
    def test_zero_existing_position_risk_blocked(self):
        c,s=setup();s['positions']=[dict(market='CRYPTO',symbol='BTC',notional_brl=100,planned_risk_brl=0)]
        self.assertIn('INVALID_EXISTING_POSITION',evaluate(c,s)['reasons'])
    def test_fail_closed_missing(self):
        c,s=setup();del s['available_cash_brl'];self.assertFalse(evaluate(c,s)['allowed'])
    def test_no_live(self):
        c,s=setup();c['trading_mode']='LIVE';self.assertIn('NOT_PAPER',evaluate(c,s)['reasons'])
    def test_oversized(self):
        c,s=setup();c['quantity']=40;self.assertIn('MAX_TRADE_RISK',evaluate(c,s)['reasons'])

if __name__=='__main__':unittest.main()
