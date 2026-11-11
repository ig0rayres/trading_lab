-- Rollback 002_triggers only. Does not drop 001 ledger tables or delete fill rows.

DELETE FROM schema_migrations WHERE version = '002_triggers';

DROP TABLE IF EXISTS trigger_changes;
DROP TABLE IF EXISTS market_controls;

DROP INDEX IF EXISTS idx_positions_market_symbol_open;

ALTER TABLE positions DROP CONSTRAINT IF EXISTS positions_market_check;
ALTER TABLE paper_orders DROP CONSTRAINT IF EXISTS paper_orders_market_check;
ALTER TABLE signal_events DROP CONSTRAINT IF EXISTS signal_events_market_check;

ALTER TABLE positions DROP COLUMN IF EXISTS market;
ALTER TABLE paper_orders DROP COLUMN IF EXISTS market;
ALTER TABLE signal_events DROP COLUMN IF EXISTS market;

ALTER TABLE control_flags DROP COLUMN IF EXISTS demo_operation_on;
ALTER TABLE control_flags DROP COLUMN IF EXISTS capital_cents;
ALTER TABLE control_flags DROP COLUMN IF EXISTS max_open_positions;
ALTER TABLE control_flags DROP COLUMN IF EXISTS max_aggregate_risk_cents;
ALTER TABLE control_flags DROP COLUMN IF EXISTS max_daily_loss_cents;
ALTER TABLE control_flags DROP COLUMN IF EXISTS max_weekly_loss_cents;

ALTER TABLE paper_fills DROP COLUMN IF EXISTS quote_currency;
ALTER TABLE paper_fills DROP COLUMN IF EXISTS price_quote;
ALTER TABLE paper_fills ALTER COLUMN price_cents SET NOT NULL;

ALTER TABLE ledger_entries ALTER COLUMN amount_cents SET NOT NULL;
