import sys,unittest,io,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from paper_reconcile import reconcile
class FakeResponse(io.BytesIO):
    def __enter__(self):return self
    def __exit__(self,*a):self.close()
class Tests(unittest.TestCase):
    def setUp(self):
        self.env={'ALPACA_PAPER_TRADE':'true','ALPACA_BASE_URL':'https://paper-api.alpaca.markets',
                  'ALPACA_API_KEY':'test','ALPACA_SECRET_KEY':'test','USD_BRL_REFERENCE':'5'}
        self.cid='nf-'+'a'*24
    def test_reconcile_read_only(self):
        def opener(req,timeout):
            self.assertEqual(req.get_method(),'GET');self.assertIn(self.cid,req.full_url)
            return FakeResponse(json.dumps({'id':'abc','client_order_id':self.cid,'status':'filled'}).encode())
        result=reconcile(self.cid,self.env,opener)
        self.assertEqual(result['status'],'RECONCILED');self.assertEqual(result['orders_sent'],0)
    def test_unknown_stays_unknown(self):
        def broken(*a,**kw): raise TimeoutError()
        self.assertEqual(reconcile(self.cid,self.env,broken)['status'],'UNKNOWN_BROKER_STATE')
    def test_invalid_id(self):
        self.assertEqual(reconcile('bad',self.env)['status'],'BLOCKED')

    def test_n21_canceled_maps_to_terminal_reconcile(self):
        def opener(req, timeout):
            self.assertEqual(req.get_method(), 'GET')
            payload = {
                'id': 'broker-cancel-1',
                'client_order_id': self.cid,
                'status': 'canceled',
                'filled_qty': '0',
            }
            return FakeResponse(json.dumps(payload).encode())

        result = reconcile(self.cid, self.env, opener)
        self.assertEqual(result['status'], 'RECONCILED')
        self.assertEqual(result.get('broker_status'), 'canceled')
        self.assertEqual(result['orders_sent'], 0)
        self.assertTrue(result.get('terminal'))

    def test_n21_expired_maps_to_terminal_reconcile(self):
        def opener(req, timeout):
            payload = {
                'id': 'broker-exp-1',
                'client_order_id': self.cid,
                'status': 'expired',
                'filled_qty': '0',
            }
            return FakeResponse(json.dumps(payload).encode())

        result = reconcile(self.cid, self.env, opener)
        self.assertEqual(result['status'], 'RECONCILED')
        self.assertEqual(result.get('broker_status'), 'expired')
        self.assertFalse(result.get('treated_as_fill'))
        self.assertTrue(result.get('terminal'))
