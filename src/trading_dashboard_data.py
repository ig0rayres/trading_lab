"""Read-only event aggregation for dashboard; missing data is unknown, never profit."""
import argparse
import json
import os
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

SUGGESTION_SURFACE_KEYS = (
    'opportunities',
    'ta_barato_shadow',
    'continuous_improvement',
    'supervised_adjustments',
)
SUGGESTION_ITEM_LABELS = frozenset({'research_tip', 'continuous_improvement', 'shadow_suggestion'})


def suggestion_surface_meta(content_label: str) -> dict:
    """Contract fields for read-only tips — never authorize broker submission."""
    return {
        'surface_kind': 'suggestion',
        'content_label': content_label,
        'execution_authorized': False,
        'paper_allowed': False,
        'orders_sent': 0,
    }


def _apply_suggestion_surface(surface: dict, content_label: str) -> dict:
    merged = {**surface, **suggestion_surface_meta(content_label)}
    merged.setdefault(
        'disclaimer',
        'Research suggestion only; does not authorize orders or paper submission.',
    )
    return merged


def validate_command_panel_suggestions(panel: dict) -> list[str]:
    """Return human-readable violations; empty list means all suggestion surfaces are labeled."""
    if not isinstance(panel, dict):
        return ['command_panel must be a dict']
    violations: list[str] = []
    for key in SUGGESTION_SURFACE_KEYS:
        surface = panel.get(key)
        if not isinstance(surface, dict):
            violations.append(f'{key}: missing or not a dict')
            continue
        if surface.get('surface_kind') != 'suggestion':
            violations.append(f'{key}: surface_kind must be suggestion')
        if surface.get('paper_allowed') is True:
            violations.append(f'{key}: paper_allowed must not be true on suggestions')
        if surface.get('execution_authorized') is True:
            violations.append(f'{key}: execution_authorized must not be true on suggestions')
        if int(surface.get('orders_sent') or 0) != 0:
            violations.append(f'{key}: orders_sent must be 0 on suggestions')
        for idx, row in enumerate(surface.get('items') or []):
            if not isinstance(row, dict):
                continue
            label = row.get('label')
            if label not in SUGGESTION_ITEM_LABELS:
                violations.append(f'{key}.items[{idx}]: label {label!r} not in suggestion set')
            if row.get('paper_allowed') is True or row.get('paper_approved') is True:
                violations.append(f'{key}.items[{idx}]: must not claim paper approval')
        for idx, row in enumerate(surface.get('recent') or []):
            if not isinstance(row, dict):
                continue
            label = row.get('label')
            if label not in SUGGESTION_ITEM_LABELS:
                violations.append(f'{key}.recent[{idx}]: label {label!r} not in suggestion set')
    return violations


def read_jsonl(path):
    if not path.exists(): return []
    rows=[]
    for line in path.read_text().splitlines():
        try:
            x=json.loads(line)
            if isinstance(x,dict):rows.append(x)
        except (ValueError,TypeError):pass
    return rows

def _load_ta_barato_shadow(root):
    """Read-only homolog slice for strategy_key ta_barato (N17). Not an upstream formula."""
    pin = '3d0f4ef6986f4984b7c6bd46f7ff4f87744c3abd'
    base = {
        'strategy_key': 'ta_barato',
        'upstream_formula': 'BLOCKED',
        'upstream_vendor_sha': pin,
        'upstream_paths_searched': [
            'trader-entry/',
            'trader-exit/',
            'trader-risk/',
            'trader-budget/',
            'trader-scanner/',
            'trader-news/',
            'trader-analyst/',
            '(full tree)',
        ],
        'local_shadow_module': 'src/market_opportunities.py',
        'local_shadow_note': (
            'Lab drawdown radar for homolog only; does not satisfy G-FORM or authorize paper.'
        ),
        'paper_authorized': False,
        'execution_authorized': False,
        'orders_sent': 0,
    }
    path = Path(root) / 'research' / 'opportunities-latest.json'
    if not path.is_file():
        return _apply_suggestion_surface(
            {**base, 'status': 'NOT_RUN', 'items': [], 'mode': 'SHADOW_ONLY'},
            'research_tip',
        )
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError, TypeError):
        return _apply_suggestion_surface(
            {**base, 'status': 'UNREADABLE', 'items': [], 'mode': 'SHADOW_ONLY'},
            'research_tip',
        )
    if not isinstance(payload, dict) or payload.get('mode') != 'SHADOW_ONLY':
        return _apply_suggestion_surface(
            {**base, 'status': 'UNTRUSTED', 'items': [], 'mode': 'SHADOW_ONLY'},
            'research_tip',
        )
    opps = payload.get('opportunities') or []
    items = []
    for row in opps[:12]:
        if not isinstance(row, dict):
            continue
        items.append(
            {
                'market': row.get('market'),
                'symbol': row.get('symbol'),
                'drop_pct': row.get('drop_pct_from_previous_5_bar_peak'),
                'radar_candidate': row.get('radar_candidate'),
                'mode': row.get('mode', 'SHADOW_ONLY'),
                'paper_approved': False,
                'label': 'shadow_suggestion',
            }
        )
    return _apply_suggestion_surface(
        {
            **base,
            'status': 'OK',
            'as_of': payload.get('schema_version'),
            'items': items,
            'mode': 'SHADOW_ONLY',
        },
        'research_tip',
    )


def _load_prodigy_opportunities(root):
    path = Path(root) / 'intelligence' / 'prodigy-top10-latest.json'
    if not path.is_file():
        return _apply_suggestion_surface(
            {'status': 'NOT_RUN', 'items': [], 'disclaimer': 'Research rank only; does not authorize orders.'},
            'research_tip',
        )
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError, TypeError):
        return _apply_suggestion_surface(
            {'status': 'UNREADABLE', 'items': [], 'disclaimer': 'Research rank only; does not authorize orders.'},
            'research_tip',
        )
    if not isinstance(payload, dict) or payload.get('mode') != 'PRODIGY_RANK_RESEARCH_ONLY':
        return _apply_suggestion_surface(
            {'status': 'UNTRUSTED', 'items': [], 'disclaimer': 'Research rank only; does not authorize orders.'},
            'research_tip',
        )
    top = payload.get('top_10_research') or payload.get('providers') or []
    items = []
    for row in top[:10]:
        if not isinstance(row, dict):
            continue
        provider = row.get('provider') or row.get('provider_id')
        items.append(
            {
                'provider': provider,
                'status': row.get('status'),
                'prodigy_score': row.get('prodigy_score'),
                'label': 'research_tip',
            }
        )
    return _apply_suggestion_surface(
        {
            'status': 'OK',
            'as_of': payload.get('as_of'),
            'items': items,
            'disclaimer': str(payload.get('score_warning') or 'Research rank only; does not authorize orders.'),
        },
        'research_tip',
    )

def _latest_evolution_daily_tips(root: Path, limit: int = 8) -> list[dict]:
    daily_dir = root / 'evolution' / 'daily'
    if not daily_dir.is_dir():
        return []
    daily_files = sorted(daily_dir.glob('*.json'), reverse=True)
    if not daily_files:
        return []
    try:
        payload = json.loads(daily_files[0].read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return []
    tips = payload.get('tips') or []
    out = []
    for tip in tips[-limit:]:
        if not isinstance(tip, dict):
            continue
        label = tip.get('label') or 'continuous_improvement'
        if label not in SUGGESTION_ITEM_LABELS:
            label = 'suggestion'
        out.append(
            {
                'at': payload.get('date_utc'),
                'kind': tip.get('kind') or 'daily_tip',
                'summary': tip.get('summary') or tip.get('note'),
                'label': label,
            }
        )
    return out


def _load_supervised_adjustments(root, limit=8):
    try:
        from supervised_adjustment import list_adjustment_history, load_overrides

        evo = Path(root) / 'evolution'
        recent = list_adjustment_history(evo, limit=limit)
        return _apply_suggestion_surface(
            {
                'count': len(recent),
                'recent': recent,
                'override_keys': list((load_overrides(evo).get('strategies') or {}).keys()),
            },
            'continuous_improvement',
        )
    except ImportError:
        return _apply_suggestion_surface(
            {'count': 0, 'recent': [], 'status': 'UNAVAILABLE'},
            'continuous_improvement',
        )


def _load_evolution_recent(root, limit=8):
    rows = read_jsonl(Path(root) / 'evolution' / 'decisions.jsonl')
    recent = []
    for row in rows[-limit:]:
        if not isinstance(row, dict):
            continue
        recent.append(
            {
                'at': row.get('at') or row.get('timestamp'),
                'kind': row.get('kind') or row.get('decision'),
                'summary': row.get('summary') or row.get('note'),
                'label': 'continuous_improvement',
            }
        )
    daily_tips = _latest_evolution_daily_tips(Path(root), limit=limit)
    merged = (daily_tips + recent)[:limit]
    return _apply_suggestion_surface(
        {'count': len(rows) + len(daily_tips), 'recent': merged, 'items': daily_tips},
        'continuous_improvement',
    )

def _load_strategy_catalog():
    try:
        from strategy_catalog import list_strategy_states

        rows = list_strategy_states()
    except ImportError:
        rows = None
    if rows is None:
        return {'status': 'LEDGER_UNAVAILABLE', 'strategies': []}
    return {'status': 'OK', 'strategies': rows, 'note': 'Phase changes are operator-only; dashboard is read-only.'}

def command_panel(root):
    root = Path(root)
    ledger = None
    try:
        from ledger_reconcile import ledger_snapshot

        ledger = ledger_snapshot()
    except ImportError:
        ledger = None
    fills = 0
    if isinstance(ledger, dict):
        fills = int(ledger.get('paper_fills') or 0)
    queued = int(ledger.get('paper_queued_intent') or 0) if isinstance(ledger, dict) else 0
    panel = {
        'schema_version': 'command-panel-v1',
        'suggestion_policy': {
            'surface_keys': list(SUGGESTION_SURFACE_KEYS),
            'never_fields': ['paper_allowed', 'order_authorized'],
            'note': 'Dashboard tips are suggestions only; broker path requires signed signal + Gate B.',
        },
        'financial_health': {
            'ledger_connected': isinstance(ledger, dict) and ledger.get('status') != 'LEDGER_UNAVAILABLE',
            'paper_fills_recorded': fills,
            'paper_queued_intent': queued,
            'queued_is_not_fill': queued > 0 and fills == 0,
            'performance_credibility': 'verified_fills' if fills > 0 else 'awaiting_operator_homologation',
        },
        'strategy_catalog': _load_strategy_catalog(),
        'opportunities': _load_prodigy_opportunities(root),
        'ta_barato_shadow': _load_ta_barato_shadow(root),
        'continuous_improvement': _load_evolution_recent(root),
        'supervised_adjustments': _load_supervised_adjustments(root),
        'history': {'postgres_ledger_counts': ledger},
    }
    violations = validate_command_panel_suggestions(panel)
    panel['suggestion_policy']['self_check_ok'] = not violations
    if violations:
        panel['suggestion_policy']['self_check_violations'] = violations
    return panel

def summary(root):
    root=Path(root)
    snaps=read_jsonl(root/'paper/order-snapshots.jsonl')
    latest={}
    for s in snaps:
        key=s.get('client_order_id')
        if key and s.get('status')=='MONITORED': latest[key]=s
    closed=[];open_count=0
    for s in latest.values():
        try:
            entry=Decimal(str(s.get('entry_qty') or 0));remaining=Decimal(str(s.get('remaining_qty') or 0))
            if entry>0 and remaining==0:closed.append(Decimal(str(s['realized_gross_pnl_usd'])))
            elif entry>0: open_count+=1
        except (InvalidOperation,KeyError):continue
    journal=read_jsonl(root/'webhooks/journal.jsonl')
    decisions=read_jsonl(root/'evolution/decisions.jsonl')
    statuses=Counter(str(x.get('result',{}).get('status','UNKNOWN')) for x in journal)
    ledger = None
    try:
        from ledger_reconcile import ledger_snapshot

        ledger = ledger_snapshot()
    except ImportError:
        ledger = None
    shadow = {
        'decision_events': len(decisions),
        'webhook_journal_events': len(journal),
        'worker_statuses': dict(statuses),
    }
    paper = {
        'orders_monitored': len(latest),
        'positions_open': open_count,
        'closed_with_pnl': len(closed),
    }
    return {'schema_version':'trading-dashboard-v4','mode':'READ_ONLY','currency':'USD',
       'paper_orders_monitored':len(latest),'positions_not_fully_closed':open_count,
       'closed_orders_with_pnl':len(closed),
       'realized_gross_pnl_usd':str(sum(closed,Decimal(0))) if closed else None,
       'pnl_unavailable_reason':None if closed else 'NO_CLOSED_MONITORED_ORDERS',
       'journal_events':len(journal),'worker_statuses':dict(statuses),
       'decision_events':len(decisions), 'win_rate':None if not closed else sum(x>0 for x in closed)/len(closed),
       'shadow_vs_paper': {'shadow': shadow, 'paper_snapshots': paper, 'postgres_ledger': ledger},
       'command_panel': command_panel(root),
       'orders_sent':0,'limitations':['P&L excludes fees/slippage','Only recorded snapshots are counted',
           'No provider performance inferred from shadow candidates',
           'Postgres ledger is audit trail; broker_reconciled stays false until operator homologation',
           'Prodigy opportunities and evolution entries are research tips, not trade instructions',
           'Strategy phases shown here cannot be changed from the dashboard']}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--root',default='/app/reports');parser.add_argument('--output')
    args=parser.parse_args();d=summary(Path(args.root))
    if args.output:
        p=Path(args.output);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2))
    print(json.dumps(d,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
