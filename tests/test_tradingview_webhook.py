import unittest, tempfile, pathlib, os, sys
from datetime import datetime, timezone
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'src'))
from tradingview_webhook import ingest
class TVTests(unittest.TestCase):
 def signal(self):
  return {'provider':'tradingview','signal_id':'SAMPLE_123456','symbol':'AAPL','side':'buy','asset_class':'us_equity','sent_at_utc':datetime.now(timezone.utc).isoformat(),'entry':'150','stop':'145','target':'160','quantity':1,'ttl_seconds':30}
 def test_queue_and_dedupe(self):
  with tempfile.TemporaryDirectory() as d:
   os.environ['SIGNAL_COPY_SECRET']='x'*48
   a=ingest(self.signal(),'a'*48,pathlib.Path(d)/'pending')
   b=ingest(self.signal(),'a'*48,pathlib.Path(d)/'pending')
   self.assertEqual(a[0],202);self.assertEqual(b[1]['status'],'DUPLICATE_IGNORED')
 def test_invalid_direction(self):
  s=self.signal();s['side']='sell'
  with tempfile.TemporaryDirectory() as d:self.assertEqual(ingest(s,'a'*48,pathlib.Path(d))[0],422)
 def test_invalid_timestamp(self):
  s=self.signal();s['sent_at_utc']='2020-01-01T00:00:00Z'
  with tempfile.TemporaryDirectory() as d:self.assertEqual(ingest(s,'a'*48,pathlib.Path(d))[0],422)
