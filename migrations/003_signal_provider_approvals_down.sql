DELETE FROM schema_migrations WHERE version = '003_signal_provider_approvals';

DROP TABLE IF EXISTS signal_provider_approvals;