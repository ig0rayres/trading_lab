# Ingest rules

> Part of `signal-ingest`. Return to [hub](../SKILL.md).

## 1. Secret

The header is `X-Webhook-Token`. The configured value must be at least 32 characters. Reject otherwise with no database order row.

## 2. Idempotency

`idempotency_key` is unique. A replay returns the stored `signal_events` row and does not create another one.

## 3. Stop line

This skill ends at `signal_events`. Risk and the broker belong to `paper-order-gate`.
