"""No-secrets deployment/readiness contract, always READ ONLY and never submits orders."""
import argparse
import json
import os
from pathlib import Path
from trading_dashboard_data import summary

def readiness(env,root):
    paper=env.get('ALPACA_BASE_URL','').rstrip('/')=='https://paper-api.alpaca.markets' and env.get('ALPACA_PAPER_TRADE','').lower()=='true'
    live=env.get('LIVE_TRADING_ENABLED','false').lower()=='false'
    auto=env.get('PAPER_SIGNAL_AUTO_ENABLED','false').lower()=='true'
    risk_ack=env.get('PAPER_DAILY_RISK_CONFIRMED','false').lower()=='true'
    d=summary(root)
    bindings={'news_cycle':(Path('/app/src/news_cycle.py').exists()),'signal_copy':(Path('/app/src/signal_copy.py').exists()),'paper_gateway':Path('/app/src/paper_gateway.py').exists()}
    blockers=[]
    if not live:blockers.append('LIVE_FLAG_UNSAFE')
    if not paper:blockers.append('PAPER_ENDPOINT_NOT_VERIFIED')
    if auto:blockers.append('AUTO_SIGNAL_ON_REQUIRES_INDEPENDENT_RISK_VALIDATION')
    if not risk_ack:blockers.append('DAILY_RISK_NOT_ATTESTED')
    blockers.extend(['B3_BROKER_ADAPTER_NOT_IMPLEMENTED','CRYPTO_BRACKET_MANAGEMENT_NOT_IMPLEMENTED','SHADOW_STRATEGIES_NOT_PROMOTED'])
    return {'mode':'READ_ONLY_NO_ORDERS','live_trading_disabled':live,'paper_endpoint_configured':paper,
            'signal_auto_enabled':auto,'daily_risk_attested':risk_ack,'code_components_present':bindings,
            'dashboard':d,'autonomous_multimarket_ready':False,'blockers':blockers,'orders_sent':0}

def main():
    a=argparse.ArgumentParser();a.add_argument('--reports',default='/app/reports');args=a.parse_args()
    print(json.dumps(readiness(os.environ,Path(args.reports)),indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
