-- Ledger paper tables (docs/db-schema.dbml). Apply once per environment.
-- Requires PostgreSQL 13+ for gen_random_uuid().

CREATE TABLE IF NOT EXISTS schema_migrations (
    version varchar(32) PRIMARY KEY,
    applied_at timestamp NOT NULL DEFAULT now()
);

CREATE TABLE strategy_states (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    strategy_key varchar(64) NOT NULL UNIQUE,
    phase varchar(32) NOT NULL,
    created_at timestamp NOT NULL DEFAULT now(),
    updated_at timestamp NOT NULL DEFAULT now(),
    deleted_at timestamp NULL
);

CREATE TABLE signal_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    idempotency_key varchar(128) NOT NULL UNIQUE,
    source varchar(64) NOT NULL,
    symbol varchar(32) NOT NULL,
    side varchar(8) NOT NULL,
    status varchar(32) NOT NULL,
    reject_code varchar(64) NULL,
    received_at timestamp NOT NULL,
    created_at timestamp NOT NULL DEFAULT now(),
    updated_at timestamp NOT NULL DEFAULT now(),
    deleted_at timestamp NULL
);
CREATE INDEX idx_signal_events_status ON signal_events (status);

CREATE TABLE control_flags (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    kill_switch_on boolean NOT NULL DEFAULT false,
    max_risk_per_trade_cents bigint NOT NULL,
    prodigy_risk_cents bigint NOT NULL,
    created_at timestamp NOT NULL DEFAULT now(),
    updated_at timestamp NOT NULL DEFAULT now(),
    deleted_at timestamp NULL
);

CREATE TABLE positions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol varchar(32) NOT NULL,
    side varchar(8) NOT NULL,
    qty numeric NOT NULL DEFAULT 0,
    created_at timestamp NOT NULL DEFAULT now(),
    updated_at timestamp NOT NULL DEFAULT now(),
    deleted_at timestamp NULL
);
CREATE INDEX idx_positions_symbol ON positions (symbol);

CREATE TABLE risk_decisions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    signal_event_id uuid NOT NULL REFERENCES signal_events (id),
    strategy_key varchar(64) NOT NULL,
    decision varchar(32) NOT NULL,
    reject_code varchar(64) NULL,
    risk_amount_cents bigint NOT NULL DEFAULT 0,
    created_at timestamp NOT NULL DEFAULT now(),
    updated_at timestamp NOT NULL DEFAULT now(),
    deleted_at timestamp NULL
);
CREATE INDEX idx_risk_decisions_signal_event_id ON risk_decisions (signal_event_id);
CREATE INDEX idx_risk_decisions_decision ON risk_decisions (decision);

CREATE TABLE paper_orders (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_decision_id uuid NOT NULL UNIQUE REFERENCES risk_decisions (id),
    position_id uuid NULL REFERENCES positions (id),
    client_order_id varchar(128) NOT NULL UNIQUE,
    broker_order_id varchar(128) NULL UNIQUE,
    symbol varchar(32) NOT NULL,
    side varchar(8) NOT NULL,
    status varchar(32) NOT NULL,
    qty numeric NOT NULL,
    created_at timestamp NOT NULL DEFAULT now(),
    updated_at timestamp NOT NULL DEFAULT now(),
    deleted_at timestamp NULL
);
CREATE INDEX idx_paper_orders_position_id ON paper_orders (position_id);
CREATE INDEX idx_paper_orders_status ON paper_orders (status);

CREATE TABLE paper_fills (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_order_id uuid NOT NULL REFERENCES paper_orders (id),
    broker_fill_id varchar(128) NOT NULL UNIQUE,
    qty numeric NOT NULL,
    price_cents bigint NOT NULL,
    created_at timestamp NOT NULL DEFAULT now(),
    updated_at timestamp NOT NULL DEFAULT now(),
    deleted_at timestamp NULL
);
CREATE INDEX idx_paper_fills_paper_order_id ON paper_fills (paper_order_id);

CREATE TABLE ledger_entries (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_fill_id uuid NOT NULL REFERENCES paper_fills (id),
    amount_cents bigint NOT NULL,
    kind varchar(32) NOT NULL,
    created_at timestamp NOT NULL DEFAULT now(),
    updated_at timestamp NOT NULL DEFAULT now(),
    deleted_at timestamp NULL
);
CREATE INDEX idx_ledger_entries_paper_fill_id ON ledger_entries (paper_fill_id);
CREATE INDEX idx_ledger_entries_kind ON ledger_entries (kind);

INSERT INTO schema_migrations (version) VALUES ('001_ledger')
    ON CONFLICT (version) DO NOTHING;
