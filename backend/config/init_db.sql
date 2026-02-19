-- Initialize PostgreSQL for Halilit Support Center v8.5
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
-- Product Families (Canonical Product Graph)
-- Groups of related product variants sharing a common identity
-- e.g., "Nord Stage 4" family with variants: 88, 73, Compact
-- =========================================================================
CREATE TABLE IF NOT EXISTS product_families (
    id VARCHAR(255) PRIMARY KEY,
    brand VARCHAR(255) NOT NULL,
    family_name VARCHAR(500) NOT NULL,
    series VARCHAR(255),
    generation INTEGER,
    product_line VARCHAR(500),
    official_family_url TEXT,
    description TEXT,
    hero_image TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_family_brand ON product_families(brand);
CREATE INDEX idx_family_series ON product_families(series);

-- =========================================================================
-- Product Relationships (Edges in the Product Graph)
-- Multi-parent capable: one accessory can link to multiple products
-- =========================================================================
CREATE TABLE IF NOT EXISTS product_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_product_id VARCHAR(255) NOT NULL,
    target_product_id VARCHAR(255) NOT NULL,
    relationship_type VARCHAR(50) NOT NULL,
    confidence FLOAT DEFAULT 0.0,
    ai_discovered BOOLEAN DEFAULT true,
    manually_curated BOOLEAN DEFAULT false,
    compatibility_notes TEXT,
    discovered_from TEXT,
    sources_verified JSONB DEFAULT '[]',
    bidirectional BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_rel_source ON product_relationships(source_product_id);
CREATE INDEX idx_rel_target ON product_relationships(target_product_id);
CREATE INDEX idx_rel_type ON product_relationships(relationship_type);
CREATE INDEX idx_rel_confidence ON product_relationships(confidence);
CREATE INDEX idx_rel_curated ON product_relationships(manually_curated);

-- =========================================================================
-- Canonical Products (Graph-augmented product data)
-- Stores family_id and variant info; full product data stays in JSON pipeline
-- =========================================================================
CREATE TABLE IF NOT EXISTS canonical_products (
    id VARCHAR(255) PRIMARY KEY,
    family_id VARCHAR(255) REFERENCES product_families(id) ON DELETE SET NULL,
    variant_key VARCHAR(100),
    brand VARCHAR(255),
    product_data JSONB NOT NULL DEFAULT '{}',
    graph_version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_canonical_family ON canonical_products(family_id);
CREATE INDEX idx_canonical_brand ON canonical_products(brand);
CREATE INDEX idx_canonical_variant ON canonical_products(variant_key);

-- =========================================================================
-- Product Graph overview (reporting view)
-- =========================================================================
CREATE OR REPLACE VIEW product_graph_overview AS
SELECT
    pf.id AS family_id,
    pf.brand,
    pf.family_name,
    pf.series,
    pf.generation,
    COUNT(DISTINCT cp.id) AS variant_count,
    COUNT(DISTINCT CASE WHEN pr.relationship_type = 'accessory_for' THEN pr.source_product_id END) AS accessory_count,
    COUNT(DISTINCT pr.id) AS total_relationships
FROM product_families pf
LEFT JOIN canonical_products cp ON cp.family_id = pf.id
LEFT JOIN product_relationships pr ON pr.target_product_id = cp.id
GROUP BY pf.id, pf.brand, pf.family_name, pf.series, pf.generation
ORDER BY pf.brand, pf.family_name;

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
GRANT SELECT, INSERT, UPDATE, DELETE ON product_families TO "halilit_user";
GRANT SELECT, INSERT, UPDATE, DELETE ON product_relationships TO "halilit_user";
GRANT SELECT, INSERT, UPDATE ON canonical_products TO "halilit_user";
GRANT SELECT ON product_graph_overview TO "halilit_user";
