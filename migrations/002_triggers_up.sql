-- Triggers, market columns, and fill quote fields (docs/DATABASE.md §6). PostgreSQL 13+.

ALTER TABLE signal_events ADD COLUMN IF NOT EXISTS market varchar(16);
ALTER TABLE paper_orders ADD COLUMN IF NOT EXISTS market varchar(16);
ALTER TABLE positions ADD COLUMN IF NOT EXISTS market varchar(16);

DO $$
BEGIN
    ALTER TABLE signal_events ADD CONSTRAINT signal_events_market_check
        CHECK (market IS NULL OR market IN ('B3_EQUITY', 'CRYPTO', 'FOREX'));
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE paper_orders ADD CONSTRAINT paper_orders_market_check
        CHECK (market IS NULL OR market IN ('B3_EQUITY', 'CRYPTO', 'FOREX'));
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    ALTER TABLE positions ADD CONSTRAINT positions_market_check
        CHECK (market IS NULL OR market IN ('B3_EQUITY', 'CRYPTO', 'FOREX'));
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

CREATE UNIQUE INDEX IF NOT EXISTS idx_positions_market_symbol_open
    ON positions (market, symbol)
    WHERE deleted_at IS NULL;

ALTER TABLE control_flags ADD COLUMN IF NOT EXISTS demo_operation_on boolean NOT NULL DEFAULT false;
ALTER TABLE control_flags ADD COLUMN IF NOT EXISTS capital_cents bigint NOT NULL DEFAULT 500000;
ALTER TABLE control_flags ADD COLUMN IF NOT EXISTS max_open_positions integer NOT NULL DEFAULT 3;
ALTER TABLE control_flags ADD COLUMN IF NOT EXISTS max_aggregate_risk_cents bigint NOT NULL DEFAULT 20000;
ALTER TABLE control_flags ADD COLUMN IF NOT EXISTS max_daily_loss_cents bigint NOT NULL DEFAULT 20000;
ALTER TABLE control_flags ADD COLUMN IF NOT EXISTS max_weekly_loss_cents bigint NOT NULL DEFAULT 50000;

CREATE TABLE IF NOT EXISTS market_controls (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    market varchar(16) NOT NULL UNIQUE,
    operation_on boolean NOT NULL DEFAULT false,
    created_at timestamp NOT NULL DEFAULT now(),
    updated_at timestamp NOT NULL DEFAULT now(),
    deleted_at timestamp NULL,
    CONSTRAINT market_controls_market_check
        CHECK (market IN ('B3_EQUITY', 'CRYPTO', 'FOREX'))
);

INSERT INTO market_controls (market, operation_on)
VALUES ('B3_EQUITY', false),
       ('CRYPTO', false),
       ('FOREX', false)
ON CONFLICT (market) DO NOTHING;

CREATE TABLE IF NOT EXISTS trigger_changes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    target_table varchar(64) NOT NULL,
    target_id uuid NOT NULL,
    field_name varchar(64) NOT NULL,
    old_value varchar(255) NULL,
    new_value varchar(255) NOT NULL,
    changed_at timestamp NOT NULL DEFAULT now(),
    created_at timestamp NOT NULL DEFAULT now(),
    updated_at timestamp NOT NULL DEFAULT now(),
    deleted_at timestamp NULL,
    CONSTRAINT trigger_changes_target_table_check
        CHECK (target_table IN ('control_flags', 'market_controls', 'strategy_states'))
);

CREATE INDEX IF NOT EXISTS idx_trigger_changes_target_id ON trigger_changes (target_id);
CREATE INDEX IF NOT EXISTS idx_trigger_changes_changed_at ON trigger_changes (changed_at);

ALTER TABLE paper_fills ADD COLUMN IF NOT EXISTS quote_currency varchar(8) NULL;
ALTER TABLE paper_fills ADD COLUMN IF NOT EXISTS price_quote numeric(24, 8) NULL;
ALTER TABLE paper_fills ALTER COLUMN price_cents DROP NOT NULL;

ALTER TABLE ledger_entries ALTER COLUMN amount_cents DROP NOT NULL;

INSERT INTO schema_migrations (version) VALUES ('002_triggers')
    ON CONFLICT (version) DO NOTHING;
