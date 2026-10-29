import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from paper_monitor import analyze, record
from paper_reconcile import reconcile

class Reply(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *a): self.close()

class MonitorTests(unittest.TestCase):
    def setUp(self):
        self.env={'LIVE_TRADING_ENABLED':'false','ALPACA_PAPER_TRADE':'true','ALPACA_BASE_URL':'https://paper-api.alpaca.markets',
                  'ALPACA_API_KEY':'test','ALPACA_SECRET_KEY':'test','USD_BRL_REFERENCE':'5.00'}
        self.cid='demo-'+'a'*20
    def test_demo_bracket_read_only(self):
        payload={'client_order_id':self.cid,'id':'id','status':'filled','symbol':'AAPL','order_class':'bracket',
                 'filled_qty':'1','filled_avg_price':'349.85','legs':[{'type':'limit','status':'new','filled_qty':'0'},
                 {'type':'stop','status':'held','filled_qty':'0'}]}
        def opener(req,timeout):
            self.assertEqual(req.get_method(),'GET')
            self.assertIn('nested=true',req.full_url)
            return Reply(json.dumps(payload).encode())
        order=reconcile(self.cid,self.env,opener)
        self.assertEqual(analyze(order)['remaining_qty'],'1')
        self.assertTrue(analyze(order)['bracket_legs_observed'])
        self.assertEqual(analyze(order)['orders_sent'],0)
    def test_closed_pnl(self):
        order={'status':'RECONCILED','client_order_id':self.cid,'filled_qty':'1','filled_avg_price':'349.85',
               'legs':[{'type':'limit','filled_qty':'1','filled_avg_price':'353.85'}, {'type':'stop','filled_qty':'0'}]}
        data=analyze(order)
        self.assertEqual(data['remaining_qty'],'0')
        self.assertEqual(data['realized_gross_pnl_usd'],'4.00')
    def test_invalid_id_never_calls_broker(self):
        self.assertEqual(reconcile('hello',self.env,lambda *args: self.fail('called'))['status'],'BLOCKED')
    def test_append_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'log.jsonl'
            record({'status':'MONITORED','orders_sent':0},path)
            self.assertEqual(len(path.read_text().splitlines()),1)

if __name__=='__main__':unittest.main()
