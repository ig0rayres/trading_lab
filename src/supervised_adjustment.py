"""Supervised strategy parameter adjustments (Feature 11 / N28.2–4).

Proposal-first: unknown or incomplete ranges → suggestion only (no silent apply).
Never mutates risk anchors (control_flags). Audit via append-only ledger + optional trigger_changes.
"""
from __future__ import annotations

import fcntl
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from strategy_catalog import KNOWN_STRATEGY_KEYS, normalize_strategy_key

# Mirror v4_web_dashboard.TRIGGER_PATCH_FIELDS — kept here to avoid import cycles in tests.
RISK_ANCHOR_FIELDS = frozenset({
    'kill_switch_on', 'demo_operation_on', 'capital_cents', 'max_risk_per_trade_cents',
    'max_open_positions', 'max_aggregate_risk_cents', 'max_daily_loss_cents',
    'max_weekly_loss_cents', 'prodigy_risk_cents',
})

LABEL_SUPERVISED = 'continuous_improvement'
DEFAULT_CATALOG = Path(__file__).resolve().parents[1] / 'config' / 'strategy_parameter_catalog.json'


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def evolution_root() -> Path:
    return Path(os.environ.get('EVOLUTION_DIR', '/app/reports/evolution'))


def catalog_path() -> Path:
    raw = os.environ.get('STRATEGY_PARAMETER_CATALOG', '')
    return Path(raw) if raw.strip() else DEFAULT_CATALOG


def load_catalog(path: Path | None = None) -> dict:
    p = path or catalog_path()
    if not p.exists():
        return {'schema_version': 'strategy-parameter-catalog-1', 'strategies': {}}
    data = json.loads(p.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        raise ValueError('catalog must be a JSON object')
    return data


def _strategy_block(catalog: dict, strategy_key: str) -> dict | None:
    strategies = catalog.get('strategies') or {}
    return strategies.get(strategy_key)


def _param_spec(block: dict | None, parameter: str) -> dict | None:
    if not block:
        return None
    params = block.get('parameters') or {}
    spec = params.get(parameter)
    return spec if isinstance(spec, dict) else None


def range_is_complete(spec: dict) -> bool:
    """Full min+max required before an operator may apply (not suggestion-only)."""
    if spec.get('type') == 'int':
        return spec.get('min') is not None and spec.get('max') is not None
    return False


def value_in_range(spec: dict, value: Any) -> bool:
    if spec.get('type') == 'int':
        if not isinstance(value, int) or isinstance(value, bool):
            return False
        lo, hi = spec.get('min'), spec.get('max')
        if lo is not None and value < int(lo):
            return False
        if hi is not None and value > int(hi):
            return False
        return True
    return False


def is_risk_anchor(field_name: str) -> bool:
    return field_name in RISK_ANCHOR_FIELDS


def adjustments_ledger_path(root: Path | None = None) -> Path:
    base = root or evolution_root()
    return base / 'parameter_adjustments.jsonl'


def overrides_path(root: Path | None = None) -> Path:
    base = root or evolution_root()
    return base / 'strategy_parameter_overrides.json'


def read_adjustments(root: Path | None = None) -> list[dict]:
    path = adjustments_ledger_path(root)
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            if isinstance(row, dict):
                rows.append(row)
        except json.JSONDecodeError:
            continue
    return rows


def _append_ledger(row: dict, root: Path | None = None) -> dict:
    path = adjustments_ledger_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        stream.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    return row


def load_overrides(root: Path | None = None) -> dict:
    path = overrides_path(root)
    if not path.exists():
        return {'schema_version': 'strategy-parameter-overrides-1', 'strategies': {}}
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict):
        return {'schema_version': 'strategy-parameter-overrides-1', 'strategies': {}}
    data.setdefault('strategies', {})
    return data


def save_overrides(data: dict, root: Path | None = None) -> None:
    path = overrides_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    tmp.replace(path)


def get_current_value(strategy_key: str, parameter: str, root: Path | None = None) -> Any | None:
    overrides = load_overrides(root)
    strat = (overrides.get('strategies') or {}).get(strategy_key) or {}
    if parameter in strat:
        return strat[parameter]
    return None


def propose_adjustment(
    *,
    strategy_key: str,
    parameter: str,
    proposed_value: Any,
    reason: str,
    catalog: dict | None = None,
    root: Path | None = None,
) -> dict:
    """Create a labeled proposal. Apply only when range is documented and value in range."""
    key = normalize_strategy_key(strategy_key)
    if not key or key not in KNOWN_STRATEGY_KEYS:
        return _proposal_row(
            status='rejected',
            reject_code='UNKNOWN_STRATEGY',
            strategy_key=strategy_key,
            parameter=parameter,
            reason=reason,
        )
    if is_risk_anchor(parameter):
        return _proposal_row(
            status='rejected',
            reject_code='RISK_ANCHOR_FORBIDDEN',
            strategy_key=key,
            parameter=parameter,
            reason=reason,
        )
    catalog = catalog if catalog is not None else load_catalog()
    spec = _param_spec(_strategy_block(catalog, key), parameter)
    if spec is None:
        return _proposal_row(
            status='suggestion_only',
            reject_code='PARAMETER_NOT_IN_ORIGINAL',
            strategy_key=key,
            parameter=parameter,
            proposed_value=proposed_value,
            reason=reason,
            label='suggestion',
            can_apply=False,
        )
    before = get_current_value(key, parameter, root)
    complete = range_is_complete(spec)
    in_range = value_in_range(spec, proposed_value) if complete else False
    if not complete:
        return _proposal_row(
            status='suggestion_only',
            reject_code='RANGE_UNKNOWN',
            strategy_key=key,
            parameter=parameter,
            proposed_value=proposed_value,
            before_value=before,
            reason=reason,
            label='suggestion',
            can_apply=False,
        )
    if not in_range:
        return _proposal_row(
            status='rejected',
            reject_code='OUT_OF_ORIGINAL_RANGE',
            strategy_key=key,
            parameter=parameter,
            proposed_value=proposed_value,
            before_value=before,
            reason=reason,
            label='suggestion',
            can_apply=False,
        )
    row = _proposal_row(
        status='proposed',
        strategy_key=key,
        parameter=parameter,
        proposed_value=proposed_value,
        before_value=before,
        reason=reason,
        label=LABEL_SUPERVISED,
        can_apply=True,
        execution_authorized=False,
        paper_allowed=False,
        orders_sent=0,
    )
    return _append_ledger(row, root)


def _proposal_row(**fields) -> dict:
    now = _utc_now()
    base = {
        'id': str(uuid.uuid4()),
        'at': _iso(now),
        'kind': 'parameter_adjustment',
        'execution_authorized': False,
        'paper_allowed': False,
        'orders_sent': 0,
    }
    base.update(fields)
    return base


def apply_proposal(
    proposal_id: str,
    *,
    root: Path | None = None,
    conn_factory: Callable | None = None,
    insert_trigger_change: Callable | None = None,
    fetch_strategy_row: Callable | None = None,
) -> tuple[dict | None, str | None]:
    """Apply a prior proposal that has can_apply=True. Never touches control_flags."""
    rows = read_adjustments(root)
    proposal = next((r for r in rows if r.get('id') == proposal_id and r.get('status') == 'proposed'), None)
    if proposal is None:
        return None, 'PROPOSAL_NOT_FOUND'
    if not proposal.get('can_apply'):
        return None, 'SUGGESTION_ONLY'
    parameter = proposal.get('parameter', '')
    if is_risk_anchor(parameter):
        return None, 'RISK_ANCHOR_FORBIDDEN'
    strategy_key = proposal.get('strategy_key')
    new_value = proposal.get('proposed_value')
    before = proposal.get('before_value')
    if before is None:
        before = get_current_value(strategy_key, parameter, root)

    overrides = load_overrides(root)
    strategies = overrides.setdefault('strategies', {})
    strat = strategies.setdefault(strategy_key, {})
    strat[parameter] = new_value
    save_overrides(overrides, root)

    applied = {
        **proposal,
        'id': str(uuid.uuid4()),
        'proposal_id': proposal_id,
        'status': 'applied',
        'at': _iso(_utc_now()),
        'before_value': before,
        'after_value': new_value,
        'kind': 'parameter_adjustment',
    }
    _append_ledger(applied, root)

    if conn_factory and insert_trigger_change and fetch_strategy_row:
        try:
            with conn_factory() as conn:
                row = fetch_strategy_row(conn, strategy_key)
                if row:
                    insert_trigger_change(
                        conn,
                        target_table='strategy_states',
                        target_id=row['id'],
                        field_name=f'param:{parameter}',
                        old_value=before,
                        new_value=new_value,
                    )
                    conn.commit()
        except Exception:
            pass

    return applied, None


def undo_adjustment(
    applied_id: str,
    *,
    reason: str = 'operator_undo',
    root: Path | None = None,
    conn_factory: Callable | None = None,
    insert_trigger_change: Callable | None = None,
    fetch_strategy_row: Callable | None = None,
) -> tuple[dict | None, str | None]:
    rows = read_adjustments(root)
    applied = next((r for r in rows if r.get('id') == applied_id and r.get('status') == 'applied'), None)
    if applied is None:
        return None, 'APPLIED_NOT_FOUND'
    strategy_key = applied.get('strategy_key')
    parameter = applied.get('parameter')
    if is_risk_anchor(parameter):
        return None, 'RISK_ANCHOR_FORBIDDEN'
    before = applied.get('before_value')
    after = applied.get('after_value')

    overrides = load_overrides(root)
    strat = (overrides.get('strategies') or {}).get(strategy_key) or {}
    if before is None:
        strat.pop(parameter, None)
    else:
        strat[parameter] = before
    if strat:
        overrides.setdefault('strategies', {})[strategy_key] = strat
    else:
        overrides.get('strategies', {}).pop(strategy_key, None)
    save_overrides(overrides, root)

    undo_row = {
        'id': str(uuid.uuid4()),
        'at': _iso(_utc_now()),
        'kind': 'parameter_adjustment',
        'status': 'undone',
        'undoes_id': applied_id,
        'strategy_key': strategy_key,
        'parameter': parameter,
        'before_value': after,
        'after_value': before,
        'reason': reason[:250],
        'execution_authorized': False,
        'paper_allowed': False,
        'orders_sent': 0,
    }
    _append_ledger(undo_row, root)

    if conn_factory and insert_trigger_change and fetch_strategy_row:
        try:
            with conn_factory() as conn:
                row = fetch_strategy_row(conn, strategy_key)
                if row:
                    insert_trigger_change(
                        conn,
                        target_table='strategy_states',
                        target_id=row['id'],
                        field_name=f'param:{parameter}',
                        old_value=after,
                        new_value=before,
                    )
                    conn.commit()
        except Exception:
            pass

    return undo_row, None


def list_adjustment_history(root: Path | None = None, *, limit: int = 50) -> list[dict]:
    rows = read_adjustments(root)
    return rows[-limit:]


def parameter_catalog_public_view(catalog: dict | None = None) -> dict:
    catalog = catalog if catalog is not None else load_catalog()
    return {
        'schema_version': catalog.get('schema_version'),
        'strategies': catalog.get('strategies') or {},
        'risk_anchors_blocked': sorted(RISK_ANCHOR_FIELDS),
        'label': LABEL_SUPERVISED,
        'execution_authorized': False,
        'paper_allowed': False,
    }