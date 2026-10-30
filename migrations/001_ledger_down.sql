-- Rollback 001_ledger (reverse dependency order).

DELETE FROM schema_migrations WHERE version = '001_ledger';

DROP TABLE IF EXISTS ledger_entries;
DROP TABLE IF EXISTS paper_fills;
DROP TABLE IF EXISTS paper_orders;
DROP TABLE IF EXISTS risk_decisions;
DROP TABLE IF EXISTS positions;
DROP TABLE IF EXISTS control_flags;
DROP TABLE IF EXISTS signal_events;
DROP TABLE IF EXISTS strategy_states;

DROP TABLE IF EXISTS schema_migrations;