-- Operator pre-approval decisions for signal providers (ISS-021 / Sprint N51).
-- Does not alter risk anchor tables.

CREATE TABLE IF NOT EXISTS signal_provider_approvals (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    platform varchar(32) NOT NULL,
    provider_id varchar(128) NOT NULL,
    status varchar(16) NOT NULL,
    source varchar(32) NOT NULL,
    decided_at timestamp NULL,
    created_at timestamp NOT NULL DEFAULT now(),
    updated_at timestamp NOT NULL DEFAULT now(),
    UNIQUE (platform, provider_id),
    CONSTRAINT signal_provider_approvals_status_check
        CHECK (status IN ('pending', 'approved', 'rejected')),
    CONSTRAINT signal_provider_approvals_source_check
        CHECK (source IN ('panel', 'seed_json', 'seed_env', 'discovered'))
);

CREATE INDEX IF NOT EXISTS idx_signal_provider_approvals_platform
    ON signal_provider_approvals (platform);

INSERT INTO schema_migrations (version) VALUES ('003_signal_provider_approvals')
    ON CONFLICT (version) DO NOTHING;