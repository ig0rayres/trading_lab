#!/bin/sh
# Trading Lab ops layout: research scheduler (foreground) + read-only dashboard (supervised).
# LIVE_TRADING_ENABLED must stay false (enforced in run.sh).
set -eu

_dashboard_supervisor() {
  host="${DASHBOARD_HOST:-}"
  if [ -z "$host" ]; then
    if [ "$(printf '%s' "${DASHBOARD_ALLOW_REMOTE:-false}" | tr '[:upper:]' '[:lower:]')" = "true" ]; then
      host="0.0.0.0"
    else
      host="127.0.0.1"
    fi
  fi
  port="${DASHBOARD_PORT:-8765}"
  root="${DASHBOARD_ROOT:-/app/reports}"
  while true; do
    echo "v4-ops: starting read-only dashboard on ${host}:${port}" >&2
    /app/scripts/run.sh v4-dashboard --root "$root" --host "$host" --port "$port" || true
    echo "v4-ops: dashboard stopped; restarting in 3s" >&2
    sleep 3
  done
}

_tv_worker_supervisor() {
  interval="${TV_WORKER_INTERVAL_SEC:-30}"
  while true; do
    echo "v4-ops: tv-worker --once (interval ${interval}s)" >&2
    /app/scripts/run.sh tv-worker --once || true
    sleep "${interval}"
  done
}

_risk_snapshot_supervisor() {
  interval="${RISK_SNAPSHOT_INTERVAL_SEC:-60}"
  while true; do
    echo "v4-ops: risk-snapshot-refresh --once (interval ${interval}s)" >&2
    /app/scripts/run.sh risk-snapshot-refresh --once || true
    sleep "${interval}"
  done
}

_paper_track_supervisor() {
  interval="${PAPER_TRACK_INTERVAL_SEC:-30}"
  while true; do
    echo "v4-ops: paper-track-open --once (interval ${interval}s)" >&2
    /app/scripts/run.sh paper-track-open --once || true
    sleep "${interval}"
  done
}

_strategy_producer_supervisor() {
  interval="${STRATEGY_PRODUCER_INTERVAL_SEC:-900}"
  while true; do
    echo "v4-ops: strategy-producer --once (interval ${interval}s)" >&2
    /app/scripts/run.sh strategy-producer --once || true
    sleep "${interval}"
  done
}

if [ "$(printf '%s' "${DASHBOARD_AUTOSTART:-true}" | tr '[:upper:]' '[:lower:]')" != "false" ]; then
  _dashboard_supervisor &
fi

if [ "$(printf '%s' "${TV_WORKER_AUTOSTART:-true}" | tr '[:upper:]' '[:lower:]')" != "false" ]; then
  _tv_worker_supervisor &
fi

if [ "$(printf '%s' "${RISK_SNAPSHOT_AUTOSTART:-true}" | tr '[:upper:]' '[:lower:]')" != "false" ]; then
  _risk_snapshot_supervisor &
fi

if [ "$(printf '%s' "${PAPER_TRACK_AUTOSTART:-true}" | tr '[:upper:]' '[:lower:]')" != "false" ]; then
  _paper_track_supervisor &
fi

if [ "$(printf '%s' "${INTERNAL_PRODUCER_AUTOSTART:-true}" | tr '[:upper:]' '[:lower:]')" != "false" ]; then
  _strategy_producer_supervisor &
fi

exec /app/scripts/run.sh v4-scheduler "$@"
