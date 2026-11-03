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

if [ "$(printf '%s' "${DASHBOARD_AUTOSTART:-true}" | tr '[:upper:]' '[:lower:]')" != "false" ]; then
  _dashboard_supervisor &
fi

exec /app/scripts/run.sh v4-scheduler "$@"
