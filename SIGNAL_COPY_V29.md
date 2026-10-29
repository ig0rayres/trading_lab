# Trading Lab v2.9 — Signal Copy intake + Paper reconciliation

## Scope and honesty

- Adds a signed, risk-only **signal preflight** that does not require News First or technical agreement.
- Adds a **read-only Paper order reconciler** by client_order_id (`nf-` + 24 lowercase hex digits).
- The original v2.8 `paper-gateway` remains, with explicit per-ticket approval.
- **This build does not provide an HTTP webhook listener, automatic copying, account-wide daily loss enforcement, complete order lifecycle monitoring, or automatic order execution.** This is infrastructure for the next execution integration, not a finished autonomous robot.
- All `signal-copy` paths return `orders_sent: 0` and do not use broker credentials.

## Where real signals can originate

1. TradingView alerts: JSON sent by HTTP POST to a future authenticated listener. Alert creation and strategy/provider selection occur in TradingView. A user-created TradingView alert is not evidence that an independent expert signal provider was purchased.
2. TrendSpider alerts: webhooks can POST JSON as well, with similar normalization requirements.
3. Dedicated vendors: only integrate those with authenticated documented delivery, explicit licensing, full entry/stop/target and usable timestamps. No vendor is pre-connected.

Do not expose `SIGNAL_COPY_SECRET` in webhook payloads. For the adapter's offline signed JSON, the upstream trusted connector signs the canonical payload, not the trading-signal vendor.

## Commands

Test the build (from EasyPanel container):

```sh
/app/scripts/run.sh test-local
```

Preview a **signed** incoming signal JSON file:

```sh
/app/scripts/run.sh signal-copy --signal /app/data/my-signed-signal.json
```

Requires `SIGNAL_COPY_SECRET` (minimum 24 chars) and `USD_BRL_REFERENCE` (BRL per USD, 2–12). The adapter has no option to submit an order. Failure is `BLOCKED`, success `SIGNAL_ACCEPTED_RISK_PREVIEW`.

Reconcile an ambiguous previously-submitted Paper order without retrying:

```sh
/app/scripts/run.sh paper-reconcile --client-order-id nf-0123456789abcdef01234567
```

This requires configured Alpaca Paper read-only credentials. It never submits an order. The identifier above is only an illustration, not a real order.

## Next release work needed for true low-latency copy

- HTTPS ingress + verified authentication (provider-specific and internal HMAC after ingress); persistent replay protection and source/provider allowlists.
- Verify live quote against signal entry tolerance and age, executable instrument, market session, current FX and exposure, including risk in *existing* open stops.
- Risk budget and P&L durable across positions, pending orders, strategies and service restarts; daily circuit breaker.
- All broker write paths via a single synchronized executor with idempotency and unknown-state reconciliation.
- Fill/partial-fill/cancel/expiry lifecycle tracking and end-to-end Paper sandbox verification with explicit authorization.
- Production-quality monitoring, rate-limit handling and audit logs.

No third-party signal provider performance is established by this build.
