#!/bin/sh
set -eu
cd /app
[ "${LIVE_TRADING_ENABLED:-false}" = false ] || { echo 'Research lab refuses LIVE_TRADING_ENABLED=true'; exit 2; }
case "${1:-idle}" in
 v4-alpaca-reconcile)
   shift
   exec python3 /app/src/v4_alpaca_reconcile.py "$@"
   ;;
 v4-scheduler)
   shift
   exec python3 /app/src/v4_scheduler.py "$@"
   ;;
 v4-fill-position-check)
   shift
   exec python3 /app/src/v4_fill_position_check.py "$@"
   ;;
 v4-run-once)
   shift
   exec python3 /app/src/v4_run_once.py "$@"
   ;;
 v4-dashboard)
   shift
   exec python3 /app/src/v4_web_dashboard.py "$@"
   ;;
 v4-alpaca-activities)
   shift
   exec python3 /app/src/v4_alpaca_activities.py "$@"
   ;;
 v4-realized-ledger)
   shift
   exec python3 /app/src/v4_realized_ledger.py "$@"
   ;;
 v4-fill-journal)
   shift
   exec python3 /app/src/v4_fill_journal.py "$@"
   ;;
 v4-order-lifecycle)
   shift
   exec python3 /app/src/v4_order_lifecycle.py "$@"
   ;;
 v4-broker-snapshot)
   shift
   exec python3 /app/src/v4_broker_snapshot.py "$@"
   ;;
 v4-decision-risk)
   shift
   exec python3 /app/src/v4_decision_risk.py "$@"
   ;;
 v4-decision-cycle)
   shift
   exec python3 /app/src/v4_decision_cycle.py "$@"
   ;;
 v4-signal-intelligence)
   shift
   exec python3 /app/src/v4_signal_intelligence.py "$@"
   ;;
 v4-strategy-pipeline)
   shift
   exec python3 /app/src/v4_strategy_pipeline.py "$@"
   ;;
 v4-market-cycle)
   shift
   exec python3 /app/src/v4_market_cycle.py "$@"
   ;;
 v4-equity-feed)
   shift
   exec python3 /app/src/v4_equity_feed.py "$@"
   ;;
 v4-crypto-feed)
   shift
   exec python3 /app/src/v4_crypto_feed.py "$@"
   ;;
 v4-import-prices)
   shift
   exec python3 /app/src/v4_market_data_import.py "$@"
   ;;
 v4-shadow-audit)
   shift
   exec python3 /app/src/v4_shadow_audit.py "$@"
   ;;
 v4-cycle)
   shift
   exec python3 /app/src/v4_cycle.py "$@"
   ;;
 v4-readiness)
   shift
   exec python3 /app/src/v4_readiness.py "$@"
   ;;
 opportunity-scan)
   shift
   exec python3 /app/src/market_opportunities.py "$@"
   ;;
 dashboard-data)
   shift
   exec python3 /app/src/trading_dashboard_data.py "$@"
   ;;
 evolution-daily)
   shift
   exec python3 /app/src/evolution_engine.py "$@"
   ;;
 tv-webhook)
   shift
   exec python3 /app/src/tradingview_webhook.py "$@"
   ;;
 tv-worker)
   shift
   exec python3 /app/src/tradingview_worker.py "$@"
   ;;
 c2-signal-feed)
   shift
   exec python3 /app/src/c2_signal_feed.py "$@"
   ;;
 signal-paper)
   shift
   exec python3 /app/src/signal_paper_runner.py "$@"
   ;;
 idle)
   echo "Trading Lab v4.0 research package ready: live trading disabled; automatic Paper integration not homologated."
   exec tail -f /dev/null
   ;;
 ledger-migrate)
   shift
   exec python3 /app/src/ledger_migrate.py "$@"
   ;;
 prodigy-rank)
   shift
   exec python3 /app/src/prodigy_rank.py "$@"
   ;;
 continuous-review)
   shift
   exec python3 /app/src/strategy_data_adapter.py "$@"
   ;;
 strategy-intelligence)
   shift
   exec python3 /app/src/strategy_intelligence.py "$@"
   ;;
 paper-monitor)
   shift
   exec python3 /app/src/paper_monitor.py "$@"
   ;;
 paper-reconcile)
   shift
   exec python3 /app/src/paper_reconcile.py "$@"
   ;;
 provider-rank)
   shift
   exec python3 /app/src/provider_rank.py "$@"
   ;;
 signal-copy)
   shift
   exec python3 /app/src/signal_copy.py "$@"
   ;;
 paper-gateway)
   shift
   exec python3 /app/src/paper_gateway.py "$@"
   ;;
 news-cycle)
   shift
   exec python3 /app/src/news_cycle.py "$@"
   ;;
 news-sim)
   shift
   exec python3 /app/src/news_first_sim.py "$@"
   ;;
 event-verify)
   shift
   exec python3 /app/src/event_verifier.py "$@"
   ;;
 news-catalog)
   shift
   exec python3 /app/src/news_catalog.py "$@"
   ;;
 news-audit)
   shift
   exec python3 /app/src/news_audit.py "$@"
   ;;
 strategy-compare)
   shift
   exec python3 /app/src/strategy_comparison.py "$@"
   ;;
 day-replay)
   shift
   exec python3 /app/src/day_replay.py "$@"
   ;;
 day-radar)
   shift
   exec python3 /app/src/day_radar.py "$@"
   ;;
 dual-daemon)
   shift
   exec python3 /app/src/dual_daemon.py "$@"
   ;;
 replay-10d)
   shift
   exec python3 /app/src/ten_day_replay.py "$@"
   ;;
 shadow-journal)
   shift
   exec python3 /app/src/shadow_journal.py "$@"
   ;;
 swing-radar)
   shift
   exec python3 /app/src/swing_radar.py "$@"
   ;;
 radar-daemon)
   shift
   exec python3 /app/src/swing_radar.py --schedule "$@"
   ;;
 paper-audit)
   shift
   exec python3 /app/src/paper_audit.py "$@"
   ;;
 test-local)
   exec python3 -m unittest discover -s /app/tests -v
   ;;
 verify)
   echo '1/3 Local tests (offline fixtures)'
   python3 -m unittest discover -s /app/tests -v
   echo '2/3 Original modules: real code integration fixture (no market network)'
   python3 /app/src/vendor_verify.py
   echo '3/3 Full original upstream test suite'
   test -f /app/vendor/day-trader-skill/trader-entry/entry.py || { echo 'Missing original vendor repo'; exit 2; }
   cd /app/vendor/day-trader-skill
   exec python3 -m unittest discover -s tests -v
   ;;
 original-verify)
   shift
   exec python3 /app/src/vendor_verify.py "$@"
   ;;
 smoke)
   exec python3 /app/src/lab.py --csv /app/data/SYNTHETIC_SMOKE_ONLY.csv --output /app/reports/synthetic_smoke
   ;;
 orb-batch)
   shift
   date=2026-10-26
   intraday=false
   previous=
   for arg in "$@"; do
      if [ "$previous" = '--date' ]; then date=$arg; fi
      [ "$arg" != '--intraday' ] || intraday=true
      previous=$arg
   done
   if [ "$intraday" = true ]; then output="/app/reports/orb/intraday-$date"; else output="/app/reports/orb/batch-$date";fi
   exec python3 /app/src/orb_batch.py --watchlist "/app/reports/orb/watchlist-$date.json" --output "$output" "$@"
   ;;
 c2-history)
   shift
   exec python3 /app/src/c2_history_collect.py "$@"
   ;;
 timemachine-audit)
   shift
   exec python3 /app/src/time_machine_audit.py "$@"
   ;;
 research-audit)
   shift
   exec python3 /app/src/research_audit.py "$@"
   ;;
 overnight-research)
   shift
   exec python3 /app/src/overnight_research.py "$@"
   ;;
 candidate-research)
   shift
   exec python3 /app/src/candidate_research.py "$@"
   ;;
 pair-robustness)
   shift
   exec python3 /app/src/pair_robustness.py "$@"
   ;;
 external-research)
   shift
   exec python3 /app/src/external_research.py "$@"
   ;;
 multistrategy)
   shift
   exec python3 /app/src/multistrategy.py "$@"
   ;;
 history)
   shift
   exec python3 /app/src/history.py "$@"
   ;;
 orb-parity)
   shift
   exec python3 /app/src/parity.py "$@"
   ;;
 upstream-tests)
   mkdir -p /app/vendor
   if [ ! -d /app/vendor/day-trader-skill/.git ]; then
      [ "${ALLOW_GITHUB_FETCH:-false}" = true ] || { echo 'Set ALLOW_GITHUB_FETCH=true for a first-time fetch'; exit 2; }
      git clone --depth 1 https://github.com/Jakeschincariol/day-trader-skill.git /app/vendor/day-trader-skill
   fi
   cd /app/vendor/day-trader-skill
   if [ -n "${UPSTREAM_COMMIT:-}" ]; then
      current=$(git rev-parse HEAD)
      [ "$current" = "$UPSTREAM_COMMIT" ] || { echo "Wrong upstream SHA $current (expected $UPSTREAM_COMMIT). Cannot change it silently."; exit 2; }
   fi
   echo "Original upstream commit: $(git rev-parse HEAD)"
   exec python3 -m unittest discover -s tests -v
   ;;
 *) echo 'Commands: c2-history | paper-gateway | news-cycle | news-sim | event-verify | news-catalog | news-audit | strategy-compare | day-replay | day-radar | dual-daemon | replay-10d | idle | test-local | verify | original-verify | smoke | upstream-tests | orb-batch | history | timemachine-audit | orb-parity | multistrategy | research-audit | external-research | pair-robustness | candidate-research | overnight-research | paper-audit | swing-radar | radar-daemon | shadow-journal'; exit 2;;
esac
