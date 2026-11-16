"""Optional TimesFM (google-research/timesfm) context for evolution daily — research-only."""
from __future__ import annotations

import os
from typing import Any, Callable

RESEARCH_LABEL = 'research_tip'


def _env_enabled() -> bool:
    return os.environ.get('TIMESFM_ENABLED', '').strip().lower() in ('1', 'true', 'yes')


def _unavailable(*, note: str = '') -> dict[str, Any]:
    block: dict[str, Any] = {'timesfm_status': 'UNAVAILABLE', 'tips': []}
    if note:
        block['note'] = note
    return block


def run_timesfm_forecast(
    context_values: list[float],
    *,
    horizon: int = 8,
    checkpoint: str,
) -> dict[str, Any]:
    """Invoke official TimesFM when installed and configured. Never raises to callers."""
    if not context_values or horizon < 1:
        return {}
    try:
        import numpy as np
    except ImportError:
        return {}
    try:
        from timesfm3.mlx import TimesFM3Forecaster  # type: ignore

        forecaster = TimesFM3Forecaster.from_pretrained(checkpoint)
        arr = np.asarray(context_values, dtype=np.float32)
        out = forecaster.predict(arr, horizon=horizon, return_quantiles=False)
        forecast = getattr(out, 'forecast', out)
        shape = tuple(np.asarray(forecast).shape)
        return {'model_id': checkpoint, 'horizon': horizon, 'forecast_shape': shape}
    except ImportError:
        try:
            import timesfm  # type: ignore

            model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(checkpoint)
            model.compile()
            arr = np.asarray(context_values, dtype=np.float32)
            point_forecast, _quantile_forecast = model.forecast(
                horizon=horizon,
                inputs=[arr.tolist()],
            )
            shape = tuple(np.asarray(point_forecast).shape)
            return {'model_id': checkpoint, 'horizon': horizon, 'forecast_shape': shape}
        except Exception:
            return {}
    except Exception:
        return {}


def build_timesfm_block(
    *,
    day: str,
    context_values: list[float] | None = None,
    forecast_runner: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return labeled research tips or UNAVAILABLE — never fabricate forecast numbers."""
    if not _env_enabled():
        return _unavailable(note='TIMESFM_ENABLED off')
    checkpoint = (os.environ.get('TIMESFM_CHECKPOINT') or '').strip()
    if not checkpoint:
        return _unavailable(note='TIMESFM_CHECKPOINT unset')
    runner = forecast_runner or run_timesfm_forecast
    series = list(context_values or [])
    if len(series) < 4:
        return _unavailable(note='insufficient_context_series')
    meta = runner(series, horizon=int(os.environ.get('TIMESFM_HORIZON', '8')), checkpoint=checkpoint)
    if not meta:
        return _unavailable(note='runtime_unavailable')
    tip = {
        'label': RESEARCH_LABEL,
        'kind': 'timesfm_context',
        'summary': (
            f'TimesFM research context for {day}: model {meta.get("model_id", checkpoint)} '
            f'(horizon={meta.get("horizon", "n/a")}); not an order authorization.'
        ),
        'execution_authorized': False,
        'paper_allowed': False,
        'orders_sent': 0,
    }
    return {
        'timesfm_status': 'OK',
        'tips': [tip],
        'metadata': {k: v for k, v in meta.items() if k != 'forecast'},
    }