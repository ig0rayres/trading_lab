import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from v4_web_dashboard import research_overview


def test_manifest_detects_mixed_reports():
    with TemporaryDirectory() as d:
        root = Path(d)
        reports = {
            'market': {'results': {}, 'errors': {}},
            'decisions': {'decisions': [], 'orders_sent': 0, 'automatic_order_submission': False},
            'risk': {'results': [], 'orders_sent': 0, 'automatic_order_submission': False},
        }
        digests = {}
        for name, value in reports.items():
            p = root / f'v4_{name}.json'
            p.write_text(json.dumps(value))
            digests[name] = hashlib.sha256(p.read_bytes()).hexdigest()
        manifest = {'schema_version': 'v4-once-1', 'orders_sent': 0,
                    'automatic_order_submission': False, 'execution_authorized': False,
                    'status': 'RESEARCH_ONLY', 'component_sha256': digests}
        (root / 'v4_manifest.json').write_text(json.dumps(manifest))
        assert research_overview(root)['status'] == 'RESEARCH_ONLY'
        (root / 'v4_market.json').write_text(json.dumps({'results': {'AAPL': {}}, 'errors': {}}))
        assert research_overview(root)['status'] == 'INCONSISTENT_CYCLE'


def test_rejects_malformed_manifest_hashes():
    with TemporaryDirectory() as d:
        root = Path(d)
        for name in ('market', 'decisions', 'risk'):
            (root / f'v4_{name}.json').write_text('{}')
        (root / 'v4_manifest.json').write_text(json.dumps({'component_sha256': {'market': 'invalid'}}))
        assert research_overview(root)['status'] == 'UNTRUSTED'


def test_dashboard_never_promotes_tampered_manifest_to_visible_success():
    import tempfile
    from v4_web_dashboard import build_snapshot
    import hashlib
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder) / 'v4'
        root.mkdir()
        components = {
            'market': {'results': {'AAPL': {}}, 'errors': {}},
            'decisions': {'decisions': [], 'orders_sent': 0, 'automatic_order_submission': False},
            'risk': {'results': [], 'orders_sent': 0, 'automatic_order_submission': False},
        }
        digests = {}
        for name, payload in components.items():
            target = root / ('v4_' + name + '.json')
            target.write_text(json.dumps(payload))
            digests[name] = hashlib.sha256(target.read_bytes()).hexdigest()
        (root / 'v4_manifest.json').write_text(json.dumps({
            'schema_version':'v4-once-1', 'status':'FINISHED_RESEARCH',
            'orders_sent':0, 'execution_authorized':False,
            'automatic_order_submission':False, 'component_sha256': digests,
        }))
        assert build_snapshot(folder)['research_cycle']['trusted'] is True
        components['market']['results']['FAKE'] = {}
        (root / 'v4_market.json').write_text(json.dumps(components['market']))
        snap = build_snapshot(folder)
        assert snap['research_cycle'] == {'status': 'INCONSISTENT_CYCLE', 'trusted': False}
        assert snap['research_overview']['counts'] is None
