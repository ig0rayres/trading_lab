import json
import tempfile
from pathlib import Path
from v4_web_dashboard import research_overview, build_snapshot, render_page


def _write(root, name, obj):
    (root / ('v4_' + name + '.json')).write_text(json.dumps(obj))


def test_dashboard_show_research_without_trades():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d) / 'v4'; root.mkdir()
        _write(root, 'manifest', {'schema_version': 'v4-once-1', 'status': 'RESEARCH_ONLY', 'orders_sent': 0, 'execution_authorized': False, 'automatic_order_submission': False})
        _write(root, 'market', {'results': {'A': {}, 'B': {}}, 'errors': {'C':'timeout'}})
        _write(root, 'decisions', {'orders_sent': 0, 'automatic_order_submission': False, 'decisions': [
            {'kind': 'MARKET_SHADOW', 'candidate': True, 'decision': 'RESEARCH_ONLY', 'paper_approved': False, 'orders_sent': 0},
            {'kind': 'NEWS_REVIEW', 'decision': 'RESEARCH_ONLY', 'paper_approved': False, 'orders_sent': 0}]})
        _write(root, 'risk', {'results': [{'risk_preview': 'BLOCKED'}], 'orders_sent': 0, 'automatic_order_submission': False})
        snap = build_snapshot(d)
        assert snap['research_overview']['counts']['market_candidates'] == 1
        assert snap['research_overview']['counts']['news_reviews'] == 1
        assert snap['research_overview']['counts']['feed_errors'] == 1
        assert snap['operational_acceptance'] is False
        assert 'Candidatos Shadow' in render_page(snap)


def test_dashboard_rejects_report_that_claims_orders():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        _write(root, 'manifest', {'schema_version': 'v4-once-1', 'status': 'RESEARCH_ONLY', 'orders_sent': 1, 'execution_authorized': False, 'automatic_order_submission': False})
        for key in ('market', 'decisions', 'risk'):
            _write(root, key, {})
        assert research_overview(root)['status'] == 'UNTRUSTED'


def test_dashboard_rejects_symlink_reports():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / 'v4_manifest.json').symlink_to('/etc/passwd')
        assert research_overview(root)['status'] == 'INCOMPLETE'
