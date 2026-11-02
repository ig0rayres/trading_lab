#!/usr/bin/env bash
# MVP demo smoke — no broker submit. Run inside container or CI-like env with PYTHONPATH=src.
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export LIVE_TRADING_ENABLED="${LIVE_TRADING_ENABLED:-false}"
export PYTHONPATH="${PYTHONPATH:-src}"

if [ "$LIVE_TRADING_ENABLED" != "false" ]; then
  echo "FAIL: LIVE_TRADING_ENABLED must be false"
  exit 2
fi

echo "== MVP smoke: live lock =="
python3 -c "import os; assert os.environ.get('LIVE_TRADING_ENABLED','false')=='false'"

echo "== MVP smoke: Dockerfile pin =="
if [ -f Dockerfile ]; then
  grep -q 'LIVE_TRADING_ENABLED=false' Dockerfile || { echo "FAIL: Dockerfile live lock"; exit 2; }
fi

echo "== MVP smoke: readiness (no secrets required) =="
python3 "$ROOT/src/v4_readiness.py" --reports "${REPORTS_ROOT:-$ROOT/reports}" 2>/dev/null || true

echo "== MVP smoke: core unittest (no LEDGER required) =="
python3 -m unittest \
  tests.test_strategy_homolog_traceability \
  tests.test_paper_gateway_queue.PaperGatewayQueueTest \
  tests.test_signal_paper_runner.PaperRunnerTests \
  -v

if [ -n "${LEDGER_DATABASE_URL:-}" ]; then
  echo "== MVP smoke: ledger migrate dry (LEDGER_DATABASE_URL set) =="
  bash "$ROOT/scripts/run.sh" ledger-migrate status 2>/dev/null || true
else
  echo "SKIP: ledger checks (LEDGER_DATABASE_URL unset)"
fi

if [ -n "${TV_WEBHOOK_TOKEN:-}" ] && command -v curl >/dev/null 2>&1; then
  echo "== MVP smoke: webhook health (optional) =="
  curl -sf "http://127.0.0.1:${TV_WEBHOOK_PORT:-8080}/health" || echo "WARN: webhook not listening on :8080"
else
  echo "SKIP: webhook health (no token or curl)"
fi

echo "OK: MVP demo smoke finished (no paper order placed)"
