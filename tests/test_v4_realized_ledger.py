import copy
import unittest
from v4_realized_ledger import calculate


def fill(i, side, qty, price, fee='0', symbol='AAPL'):
    return {'id': i, 'symbol': symbol, 'side': side, 'qty': qty, 'price': price, 'fee': fee, 'timestamp': '2026-10-29T16:00:00Z'}


def data(*activities):
    return {'currency': 'USD', 'complete': True, 'activities': list(activities)}


class RealizedLedgerTests(unittest.TestCase):
    def test_closed_trade_with_fees(self):
        r = calculate(data(fill('1', 'buy', '2', '100', '1'), fill('2', 'sell', '2', '105', '1')))
        self.assertEqual(float(r['realized_pnl_calculated']), 8.0)
        self.assertFalse(r['realized_pnl_verified'])
    def test_partial_exit_fifo(self):
        r = calculate(data(fill('1','buy','2','100'), fill('2','buy','2','110'), fill('3','sell','3','120')))
        self.assertEqual(r['realized_pnl_calculated'], '50')
        self.assertEqual(r['open_positions']['AAPL'], '1')
    def test_multiple_symbols(self):
        r = calculate(data(fill('1','buy','1','10'), fill('2','buy','1','20',symbol='MSFT'), fill('3','sell','1','9')))
        self.assertEqual(r['realized_pnl_calculated'], '-1')
        self.assertEqual(r['open_positions']['MSFT'], '1')
    def test_no_sales_no_profit(self):
        self.assertEqual(calculate(data(fill('1','buy','1','10')))['realized_pnl_calculated'], '0')
    def test_duplicate_rejected(self):
        with self.assertRaisesRegex(ValueError, 'DUPLICATE'):
            calculate(data(fill('1','buy','1','10'), fill('1','sell','1','11')))
    def test_missing_history_rejected(self):
        with self.assertRaisesRegex(ValueError, 'SHORT_OR_MISSING'):
            calculate(data(fill('1','sell','1','11')))
    def test_missing_fee_rejected(self):
        x = fill('1','buy','1','10'); del x['fee']
        with self.assertRaisesRegex(ValueError, 'UNKNOWN_FEES'):
            calculate(data(x))
    def test_incomplete_rejected(self):
        x=data(fill('1','buy','1','10')); x['complete']=False
        with self.assertRaisesRegex(ValueError, 'INCOMPLETE'):
            calculate(x)
    def test_invalid_numeric_rejected(self):
        for val in ('NaN','Infinity','-1','0'):
            with self.subTest(val=val), self.assertRaises(ValueError):
                calculate(data(fill('1','buy',val,'10')))
    def test_currency_separate(self):
        x=data(fill('1','buy','1','10')); x['currency']='EUR'
        with self.assertRaisesRegex(ValueError, 'UNSUPPORTED_CURRENCY'):
            calculate(x)
    def test_negative_fee_rejected(self):
        with self.assertRaisesRegex(ValueError, 'INVALID_FEE'):
            calculate(data(fill('1','buy','1','10','-1')))

if __name__ == '__main__': unittest.main()
