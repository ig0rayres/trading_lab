import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen, Request

from v4_web_dashboard import build_snapshot, render_page, make_handler

class DashboardTests(unittest.TestCase):
    def test_empty_data_never_invents_pnl(self):
        with tempfile.TemporaryDirectory() as d:
            result = build_snapshot(d)
            self.assertIsNone(result['realized_gross_pnl_usd'])
            self.assertFalse(result['operational_acceptance'])
            self.assertEqual(result['execution_state'], 'READ_ONLY_NO_ORDER_SUBMISSION')

    def test_html_escapes_data(self):
        with tempfile.TemporaryDirectory() as d:
            data = build_snapshot(d)
            data['limitations'] = ['<script>alert(1)</script>']
            page = render_page(data)
            self.assertNotIn('<script>', page)
            self.assertIn('&lt;script&gt;', page)

    def test_http_read_only_contract(self):
        with tempfile.TemporaryDirectory() as d:
            server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(Path(d)))
            task = threading.Thread(target=server.serve_forever, daemon=True)
            task.start()
            base = 'http://127.0.0.1:' + str(server.server_port)
            try:
                with urlopen(base + '/api/status', timeout=3) as response:
                    data = json.load(response)
                    self.assertFalse(data['operational_acceptance'])
                with self.assertRaises(HTTPError) as caught:
                    urlopen(Request(base + '/', data=b'{}', method='POST'), timeout=3)
                self.assertEqual(caught.exception.code, 405)
            finally:
                server.shutdown()
                server.server_close()
                task.join(3)

class DashboardAuthenticationTests(unittest.TestCase):
    def test_token_protects_status_and_liveness(self):
        with tempfile.TemporaryDirectory() as d:
            server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(Path(d), 'sample-token-' + 'x' * 30))
            task = threading.Thread(target=server.serve_forever, daemon=True)
            task.start()
            base = 'http://127.0.0.1:' + str(server.server_port)
            try:
                for route in ('/api/status', '/', '/healthz'):
                    with self.assertRaises(HTTPError) as err:
                        urlopen(base + route, timeout=3)
                    self.assertEqual(err.exception.code, 401)
                req = Request(base + '/api/status', headers={'Authorization': 'Bearer sample-token-' + 'x' * 30})
                with urlopen(req, timeout=3) as response:
                    self.assertEqual(json.load(response)['execution_state'], 'READ_ONLY_NO_ORDER_SUBMISSION')
            finally:
                server.shutdown()
                server.server_close()
                task.join(3)

    def test_research_manifest_does_not_claim_execution(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d) / 'v4'
            folder.mkdir()
            (folder / 'v4_manifest.json').write_text(json.dumps({'schema_version':'v4-once-1',
                'status':'PARTIAL_OR_BLOCKED','orders_sent':0,'market_count':2}))
            result = build_snapshot(d)
            self.assertEqual(result['research_cycle']['status'], 'INCOMPLETE')
            self.assertFalse(result['research_cycle']['trusted'])
            self.assertFalse(result['operational_acceptance'])
