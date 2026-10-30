#!/usr/bin/env bash
# N6: post-build checks for EasyPanel image (no broker, no DB).
set -euo pipefail
IMAGE="${1:-trading-lab:ci}"
docker run --rm --entrypoint python3 "$IMAGE" -c "import psycopg"
docker run --rm --entrypoint test "$IMAGE" -f /app/vendor/day-trader-skill/trader-entry/entry.py
docker run --rm --entrypoint sh "$IMAGE" -c 'test "$LIVE_TRADING_ENABLED" = false'
