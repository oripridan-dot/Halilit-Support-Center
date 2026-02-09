-- Initialize PostgreSQL for Halilit Support Center v8.0
-- Creates tables for task results, audit logs, and learning system

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =========================================================================
-- Task Results Table (Celery result backend)
-- =========================================================================
CREATE TABLE IF NOT EXISTS celery_taskmeta (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL,
    result TEXT,
    date_done TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    traceback TEXT,
    children TEXT,
    meta TEXT
);

CREATE INDEX idx_celery_task_id ON celery_taskmeta(task_id);
CREATE INDEX idx_celery_status ON celery_taskmeta(status);
CREATE INDEX idx_celery_date_done ON celery_taskmeta(date_done);

-- =========================================================================
-- Task Audit Log (Compliance & traceability)
-- =========================================================================
CREATE TABLE IF NOT EXISTS task_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id VARCHAR(255) NOT NULL,
    task_type VARCHAR(100),
    brand VARCHAR(255),
    product_count INTEGER,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_seconds NUMERIC,
    status VARCHAR(50),
    error_message TEXT,
    user_id VARCHAR(255),
    request_source VARCHAR(50)
);

CREATE INDEX idx_audit_task_id ON task_audit_log(task_id);
CREATE INDEX idx_audit_brand ON task_audit_log(brand);
CREATE INDEX idx_audit_status ON task_audit_log(status);
CREATE INDEX idx_audit_started_at ON task_audit_log(started_at);

-- =========================================================================
-- Product Enrichment History (Track changes over time)
-- =========================================================================
CREATE TABLE IF NOT EXISTS product_enrichment_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id VARCHAR(255) NOT NULL,
    brand VARCHAR(255),
    task_id VARCHAR(255),
    enrichment_stage VARCHAR(50),
    enriched_data JSONB,
    risk_score INTEGER,
    passed_validation BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_enrichment_product_id ON product_enrichment_history(product_id);
CREATE INDEX idx_enrichment_brand ON product_enrichment_history(brand);
CREATE INDEX idx_enrichment_created_at ON product_enrichment_history(created_at);

-- =========================================================================
-- Learning Feedback (User corrections & agent learnings)
-- =========================================================================
CREATE TABLE IF NOT EXISTS learning_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id VARCHAR(255) NOT NULL,
    feedback_type VARCHAR(50),
    feedback_data JSONB,
    user_id VARCHAR(255),
    agent_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_feedback_product_id ON learning_feedback(product_id);
CREATE INDEX idx_feedback_type ON learning_feedback(feedback_type);
CREATE INDEX idx_feedback_agent ON learning_feedback(agent_name);

-- =========================================================================
-- Worker Health Metrics (Monitoring)
-- =========================================================================
CREATE TABLE IF NOT EXISTS worker_health_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    worker_name VARCHAR(255),
    queue_name VARCHAR(100),
    active_tasks INTEGER,
    queue_length INTEGER,
    cpu_percent NUMERIC,
    memory_percent NUMERIC,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_worker ON worker_health_metrics(worker_name);
CREATE INDEX idx_metrics_timestamp ON worker_health_metrics(timestamp);

-- =========================================================================
-- Task Sync Progress (Track real-time progress)
-- =========================================================================
CREATE TABLE IF NOT EXISTS sync_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sync_id VARCHAR(255) UNIQUE,
    brand VARCHAR(255),
    total_products INTEGER,
    harvested_count INTEGER,
    enriched_count INTEGER,
    validated_count INTEGER,
    failed_count INTEGER,
    status VARCHAR(50),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_sync_brand ON sync_progress(brand);
CREATE INDEX idx_sync_status ON sync_progress(status);
CREATE INDEX idx_sync_started_at ON sync_progress(started_at);

-- =========================================================================
-- Create Views for Reporting
-- =========================================================================

-- Sync success rate by brand
CREATE OR REPLACE VIEW audit_brand_success_rate AS
SELECT
    brand,
    COUNT(*) as total_syncs,
    COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_syncs,
    ROUND(100.0 * COUNT(CASE WHEN status = 'success' THEN 1 END) / COUNT(*), 2) as success_rate,
    AVG(duration_seconds) as avg_duration_seconds
FROM task_audit_log
WHERE brand IS NOT NULL
GROUP BY brand
ORDER BY success_rate DESC;

-- Recent failures for debugging
CREATE OR REPLACE VIEW recent_failures AS
SELECT
    task_id,
    task_type,
    brand,
    error_message,
    started_at
FROM task_audit_log
WHERE status = 'failure'
ORDER BY started_at DESC
LIMIT 50;

-- Worker queue depths (current state)
CREATE OR REPLACE VIEW current_queue_depths AS
SELECT
    worker_name,
    queue_name,
    active_tasks,
    queue_length,
    timestamp
FROM worker_health_metrics
WHERE timestamp = (SELECT MAX(timestamp) FROM worker_health_metrics);

-- =========================================================================
-- Initialize permissions (if using non-superuser)
-- =========================================================================
GRANT SELECT, INSERT, UPDATE ON celery_taskmeta TO "halilit_user";
GRANT SELECT, INSERT ON task_audit_log TO "halilit_user";
GRANT SELECT, INSERT ON product_enrichment_history TO "halilit_user";
GRANT SELECT, INSERT ON learning_feedback TO "halilit_user";
GRANT SELECT, INSERT ON worker_health_metrics TO "halilit_user";
GRANT SELECT, INSERT, UPDATE ON sync_progress TO "halilit_user";
GRANT SELECT ON audit_brand_success_rate TO "halilit_user";
GRANT SELECT ON recent_failures TO "halilit_user";
GRANT SELECT ON current_queue_depths TO "halilit_user";
