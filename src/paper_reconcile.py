"""Read-only Alpaca Paper reconciliation, including bracket exits and known demo IDs.

Never submits, modifies, or cancels orders. A known order ID is required.
"""
import argparse
import json
import os
import re
from urllib.parse import quote
from urllib.request import Request, urlopen
from paper_audit import PAPER_URL, validate_env

ID_PATTERN = re.compile(r'(?:nf-[0-9a-f]{24}|demo-[0-9a-f]{20})\Z')


def reconcile(client_order_id, env, opener=urlopen):
    validate_env(env)
    if not isinstance(client_order_id, str) or not ID_PATTERN.fullmatch(client_order_id):
        return {'status': 'BLOCKED', 'reason': 'INVALID_CLIENT_ORDER_ID', 'orders_sent': 0}
    url = PAPER_URL + '/v2/orders:by_client_order_id?client_order_id=' + quote(client_order_id, safe='') + '&nested=true'
    req = Request(url, headers={'APCA-API-KEY-ID': env['ALPACA_API_KEY'],
                                'APCA-API-SECRET-KEY': env['ALPACA_SECRET_KEY']}, method='GET')
    try:
        with opener(req, timeout=15) as response:
            order = json.load(response)
        if not isinstance(order, dict) or order.get('client_order_id') != client_order_id:
            return {'status': 'UNKNOWN_BROKER_STATE', 'reason': 'UNEXPECTED_BROKER_RESPONSE', 'orders_sent': 0}
        legs = order.get('legs') or []
        if not isinstance(legs, list):
            return {'status': 'UNKNOWN_BROKER_STATE', 'reason': 'INVALID_LEGS', 'orders_sent': 0}
        return {
            'status': 'RECONCILED', 'client_order_id': client_order_id,
            'broker_order_id': order.get('id'), 'symbol': order.get('symbol'),
            'broker_status': order.get('status'), 'order_class': order.get('order_class'),
            'filled_qty': order.get('filled_qty'), 'filled_avg_price': order.get('filled_avg_price'),
            'filled_at': order.get('filled_at'),
            'legs': [{'id': l.get('id'), 'type': l.get('type'), 'side': l.get('side'),
                      'status': l.get('status'), 'filled_qty': l.get('filled_qty'),
                      'filled_avg_price': l.get('filled_avg_price'), 'filled_at': l.get('filled_at'),
                      'limit_price': l.get('limit_price'), 'stop_price': l.get('stop_price')}
                     for l in legs if isinstance(l, dict)],
            'orders_sent': 0,
        }
    except Exception as exc:
        return {'status': 'UNKNOWN_BROKER_STATE', 'reason': type(exc).__name__,
                'client_order_id': client_order_id, 'orders_sent': 0}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--client-order-id', required=True)
    args = parser.parse_args()
    try:
        result = reconcile(args.client_order_id, os.environ)
    except Exception as exc:
        result = {'status': 'BLOCKED', 'reason': type(exc).__name__, 'orders_sent': 0}
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'RECONCILED' else 2


if __name__ == '__main__':
    raise SystemExit(main())
