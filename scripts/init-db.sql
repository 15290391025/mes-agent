-- ManuGent database bootstrap.
-- The current MVP keeps demo data in memory; this file reserves the database
-- initialization hook used by docker-compose for future audit/session tables.

CREATE TABLE IF NOT EXISTS audit_events (
    id BIGSERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor TEXT NOT NULL DEFAULT 'demo',
    tool_name TEXT NOT NULL,
    safety_level TEXT NOT NULL,
    params JSONB NOT NULL DEFAULT '{}'::jsonb,
    result_summary TEXT NOT NULL DEFAULT ''
);
