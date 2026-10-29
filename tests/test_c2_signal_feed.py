import io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from c2_signal_feed import snapshot, fetch_orders

class Context(io.BytesIO):
    def __enter__(self):return self
    def __exit__(self,*args):self.close()

class C2FeedTests(unittest.TestCase):
    def test_poll_baseline_and_change(self):
        state=[{'Id':1,'StrategyId':44,'OrderStatus':'Open'}]
        def opener(req,timeout=0):
            self.assertIn('Bearer secret',req.get_header('Authorization'))
            return Context(json.dumps({'Results':state,'ResponseStatus':{'ErrorCode':'200'}}).encode())
        with tempfile.TemporaryDirectory() as d:
            a=snapshot([44],'secret',d,opener=opener)
            self.assertTrue(a['first_snapshot']); self.assertEqual(a['new_or_changed_count'],0)
            b=snapshot([44],'secret',d,opener=opener)
            self.assertEqual(b['new_or_changed_count'],0)
            state.append({'Id':2,'StrategyId':44,'OrderStatus':'Open'})
            c=snapshot([44],'secret',d,opener=opener)
            self.assertEqual(c['new_or_changed_count'],1)
            self.assertEqual(c['orders_sent'],0)
            self.assertFalse(json.loads(Path(d,'active-orders-latest.json').read_text())['execution_authorized'])
    def test_api_errors_fail_closed(self):
        def opener(req,timeout=0):return Context(json.dumps({'Results':[],'ResponseStatus':{'ErrorCode':'403'}}).encode())
        with self.assertRaises(ValueError):fetch_orders([1],'secret',opener)
    def test_empty_key(self):
        with self.assertRaises(ValueError):fetch_orders([1],'')

if __name__=='__main__':unittest.main()
