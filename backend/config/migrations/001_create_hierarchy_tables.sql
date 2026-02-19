-- Migration 001: Create Perfect Hierarchy Structure Tables
-- Implements: Category → Sub Category → Product Type → Brand → Family → Products
-- Date: 2026-02-17

-- =========================================================================
-- 1. CATEGORIES (Top Level)
-- =========================================================================
CREATE TABLE IF NOT EXISTS categories (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(500) NOT NULL UNIQUE,
    description TEXT,
    display_order INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_category_name ON categories(name);
CREATE INDEX IF NOT EXISTS idx_category_order ON categories(display_order);

COMMENT ON TABLE categories IS 'Top-level product categories (e.g., Keyboards & Synthesizers)';

-- =========================================================================
-- 2. SUB CATEGORIES (Level 2)
-- =========================================================================
CREATE TABLE IF NOT EXISTS sub_categories (
    id VARCHAR(255) PRIMARY KEY,
    category_id VARCHAR(255) NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(category_id, name)
);

CREATE INDEX IF NOT EXISTS idx_subcat_category ON sub_categories(category_id);
CREATE INDEX IF NOT EXISTS idx_subcat_name ON sub_categories(name);

COMMENT ON TABLE sub_categories IS 'Subcategories within categories (e.g., Digital Keyboard under Keyboards & Synthesizers)';

-- =========================================================================
-- 3. PRODUCT TYPES (Level 3) - NEW LEVEL
-- =========================================================================
CREATE TABLE IF NOT EXISTS product_types (
    id VARCHAR(255) PRIMARY KEY,
    sub_category_id VARCHAR(255) NOT NULL REFERENCES sub_categories(id) ON DELETE CASCADE,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 100,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sub_category_id, name)
);

CREATE INDEX IF NOT EXISTS idx_product_type_subcat ON product_types(sub_category_id);
CREATE INDEX IF NOT EXISTS idx_product_type_name ON product_types(name);

COMMENT ON TABLE product_types IS 'Product types within subcategories (e.g., Stage Keyboard under Digital Keyboard)';

-- =========================================================================
-- 4. BRANDS (Enhanced) - Level 4
-- =========================================================================
CREATE TABLE IF NOT EXISTS brands (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(500) NOT NULL UNIQUE,
    slug VARCHAR(255) NOT NULL UNIQUE,
    logo_url TEXT,
    description TEXT,
    website_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_brand_slug ON brands(slug);
CREATE INDEX IF NOT EXISTS idx_brand_name ON brands(name);

COMMENT ON TABLE brands IS 'Product brands (e.g., Nord, Roland, Moog)';

-- =========================================================================
-- 5. BRAND-PRODUCT TYPE MAPPING (Many-to-Many)
-- =========================================================================
CREATE TABLE IF NOT EXISTS brand_product_type_mappings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_id VARCHAR(255) NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    product_type_id VARCHAR(255) NOT NULL REFERENCES product_types(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(brand_id, product_type_id)
);

CREATE INDEX IF NOT EXISTS idx_brand_pt_brand ON brand_product_type_mappings(brand_id);
CREATE INDEX IF NOT EXISTS idx_brand_pt_type ON brand_product_type_mappings(product_type_id);

COMMENT ON TABLE brand_product_type_mappings IS 'Maps brands to product types (many-to-many relationship)';

-- =========================================================================
-- 6. PRODUCT FAMILIES (Enhanced) - Level 5
-- =========================================================================
-- Drop existing table if it exists and recreate with new structure
DROP TABLE IF EXISTS product_families CASCADE;

CREATE TABLE product_families (
    id VARCHAR(255) PRIMARY KEY,
    brand_id VARCHAR(255) NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    product_type_id VARCHAR(255) NOT NULL REFERENCES product_types(id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_family_brand ON product_families(brand_id);
CREATE INDEX IF NOT EXISTS idx_family_product_type ON product_families(product_type_id);
CREATE INDEX IF NOT EXISTS idx_family_series ON product_families(series);

COMMENT ON TABLE product_families IS 'Product families/series within brands (e.g., "Stage" product line). Models belong to families.';

-- =========================================================================
-- 6B. PRODUCT MODELS (Level 6) - NEW LEVEL
-- =========================================================================
-- Models are generations/versions within a family (e.g., "Stage 3", "Stage 4", "Stage 5")
-- Variants belong to models (e.g., "88", "73", "Compact" variants of "Stage 4")
CREATE TABLE IF NOT EXISTS product_models (
    id VARCHAR(255) PRIMARY KEY,
    family_id VARCHAR(255) NOT NULL REFERENCES product_families(id) ON DELETE CASCADE,
    model_name VARCHAR(500) NOT NULL,
    model_number INTEGER,  -- e.g., 3, 4, 5 for Stage 3, Stage 4, Stage 5
    generation INTEGER,  -- Same as model_number, for compatibility
    description TEXT,
    official_model_url TEXT,
    hero_image TEXT,
    release_year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(family_id, model_number)
);

CREATE INDEX IF NOT EXISTS idx_model_family ON product_models(family_id);
CREATE INDEX IF NOT EXISTS idx_model_number ON product_models(model_number);
CREATE INDEX IF NOT EXISTS idx_model_name ON product_models(model_name);

COMMENT ON TABLE product_models IS 'Product models/generations within a family (e.g., "Stage 4" within "Stage" family). Variants belong to models.';

-- =========================================================================
-- 7. PRODUCTS/VARIANTS (Enhanced) - Level 7
-- =========================================================================
-- Note: We'll migrate existing canonical_products to this new structure
CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(255) PRIMARY KEY,
    model_id VARCHAR(255) REFERENCES product_models(id) ON DELETE SET NULL,
    family_id VARCHAR(255) REFERENCES product_families(id) ON DELETE SET NULL,  -- Denormalized for fast queries
    product_type_id VARCHAR(255) NOT NULL REFERENCES product_types(id) ON DELETE RESTRICT,
    brand_id VARCHAR(255) NOT NULL REFERENCES brands(id) ON DELETE RESTRICT,
    sub_category_id VARCHAR(255) NOT NULL REFERENCES sub_categories(id) ON DELETE RESTRICT,
    category_id VARCHAR(255) NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
    
    -- Product Identity
    name VARCHAR(500) NOT NULL,
    sku VARCHAR(255),
    halilit_id VARCHAR(255) UNIQUE,
    variant_key VARCHAR(100),  -- e.g., "88", "73", "Compact"
    
    -- Full product data (JSONB) - preserves all existing data
    product_data JSONB NOT NULL DEFAULT '{}',
    
    -- Hierarchy Path (denormalized for fast queries)
    -- Format: category-slug/subcategory-slug/product-type-slug/brand-slug/family-slug/model-slug
    hierarchy_path TEXT NOT NULL,
    
    -- Validation
    hierarchy_validated BOOLEAN DEFAULT false,
    validation_errors JSONB DEFAULT '[]',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_product_model ON products(model_id);
CREATE INDEX IF NOT EXISTS idx_product_family ON products(family_id);
CREATE INDEX IF NOT EXISTS idx_product_type ON products(product_type_id);
CREATE INDEX IF NOT EXISTS idx_product_brand ON products(brand_id);
CREATE INDEX IF NOT EXISTS idx_product_category ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_product_subcategory ON products(sub_category_id);
CREATE INDEX IF NOT EXISTS idx_product_halilit_id ON products(halilit_id);
CREATE INDEX IF NOT EXISTS idx_product_variant_key ON products(variant_key);
CREATE INDEX IF NOT EXISTS idx_product_hierarchy_path ON products(hierarchy_path);
CREATE INDEX IF NOT EXISTS idx_product_validated ON products(hierarchy_validated);

COMMENT ON TABLE products IS 'Product variants (e.g., "88", "73", "Compact" variants of "Stage 4" model). Accessories and related products are linked via product_relationships table.';

-- =========================================================================
-- 8. PRODUCT RELATIONSHIPS (Product-to-Product Only)
-- =========================================================================
-- CRITICAL: Relationships connect PRODUCTS to PRODUCTS, not families
-- Accessories and related products are linked directly to individual products
-- Example: "Soft Case for Nord Stage 4 88" → links to product "Nord Stage 4 88" (not to family)

-- Update existing table structure
ALTER TABLE product_relationships 
    ADD COLUMN IF NOT EXISTS relationship_level VARCHAR(50) DEFAULT 'direct';

ALTER TABLE product_relationships
    ADD CONSTRAINT chk_relationship_level 
    CHECK (relationship_level IN ('direct', 'indirect'));

-- Ensure relationships only connect products (not families)
ALTER TABLE product_relationships
    ADD CONSTRAINT chk_products_only
    CHECK (
        source_product_id IN (SELECT id FROM products) AND
        target_product_id IN (SELECT id FROM products)
    );

CREATE INDEX IF NOT EXISTS idx_rel_level ON product_relationships(relationship_level);

COMMENT ON TABLE product_relationships IS 
    'Product-to-product relationships ONLY. Accessories and related products connect directly to individual products, not families.';
COMMENT ON COLUMN product_relationships.relationship_level IS 
    'direct = same family (e.g., accessory for Stage 4 88), indirect = different family/brand';
COMMENT ON COLUMN product_relationships.source_product_id IS 
    'Source product ID (e.g., accessory product)';
COMMENT ON COLUMN product_relationships.target_product_id IS 
    'Target product ID (e.g., main product the accessory is for)';

-- =========================================================================
-- 9. HIERARCHY VALIDATION LOG
-- =========================================================================
CREATE TABLE IF NOT EXISTS hierarchy_validation_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id VARCHAR(255) REFERENCES products(id) ON DELETE CASCADE,
    validation_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    details JSONB DEFAULT '{}',
    resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (severity IN ('error', 'warning', 'info')),
    CHECK (validation_type IN ('missing_path', 'orphan', 'duplicate', 'invalid_level', 'missing_relationship'))
);

CREATE INDEX IF NOT EXISTS idx_validation_product ON hierarchy_validation_log(product_id);
CREATE INDEX IF NOT EXISTS idx_validation_type ON hierarchy_validation_log(validation_type);
CREATE INDEX IF NOT EXISTS idx_validation_resolved ON hierarchy_validation_log(resolved);

COMMENT ON TABLE hierarchy_validation_log IS 'Tracks validation issues during hierarchy migration';

-- =========================================================================
-- 10. VIEWS FOR REPORTING
-- =========================================================================

-- Complete hierarchy view (with models)
CREATE OR REPLACE VIEW hierarchy_complete AS
SELECT 
    c.id AS category_id,
    c.name AS category_name,
    sc.id AS sub_category_id,
    sc.name AS sub_category_name,
    pt.id AS product_type_id,
    pt.name AS product_type_name,
    b.id AS brand_id,
    b.name AS brand_name,
    pf.id AS family_id,
    pf.family_name,
    pm.id AS model_id,
    pm.model_name,
    pm.model_number,
    COUNT(DISTINCT p.id) AS variant_count
FROM categories c
JOIN sub_categories sc ON sc.category_id = c.id
JOIN product_types pt ON pt.sub_category_id = sc.id
JOIN brand_product_type_mappings bpt ON bpt.product_type_id = pt.id
JOIN brands b ON b.id = bpt.brand_id
LEFT JOIN product_families pf ON pf.brand_id = b.id AND pf.product_type_id = pt.id
LEFT JOIN product_models pm ON pm.family_id = pf.id
LEFT JOIN products p ON p.model_id = pm.id
GROUP BY c.id, c.name, sc.id, sc.name, pt.id, pt.name, b.id, b.name, pf.id, pf.family_name, pm.id, pm.model_name, pm.model_number
ORDER BY c.display_order, sc.display_order, pt.display_order, b.name, pf.family_name, pm.model_number;

-- Products without complete paths
CREATE OR REPLACE VIEW products_missing_hierarchy AS
SELECT 
    p.id,
    p.name,
    p.halilit_id,
    CASE 
        WHEN p.category_id IS NULL THEN 'Missing Category'
        WHEN p.sub_category_id IS NULL THEN 'Missing Subcategory'
        WHEN p.product_type_id IS NULL THEN 'Missing Product Type'
        WHEN p.brand_id IS NULL THEN 'Missing Brand'
        ELSE 'Complete'
    END AS missing_level,
    p.hierarchy_validated,
    p.validation_errors
FROM products p
WHERE p.category_id IS NULL 
   OR p.sub_category_id IS NULL 
   OR p.product_type_id IS NULL 
   OR p.brand_id IS NULL
   OR p.hierarchy_validated = false;

-- =========================================================================
-- 11. PERMISSIONS
-- =========================================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON categories TO "halilit_user";
GRANT SELECT, INSERT, UPDATE, DELETE ON sub_categories TO "halilit_user";
GRANT SELECT, INSERT, UPDATE, DELETE ON product_types TO "halilit_user";
GRANT SELECT, INSERT, UPDATE, DELETE ON brands TO "halilit_user";
GRANT SELECT, INSERT, UPDATE, DELETE ON brand_product_type_mappings TO "halilit_user";
GRANT SELECT, INSERT, UPDATE, DELETE ON product_families TO "halilit_user";
GRANT SELECT, INSERT, UPDATE, DELETE ON product_models TO "halilit_user";
GRANT SELECT, INSERT, UPDATE, DELETE ON products TO "halilit_user";
GRANT SELECT, INSERT, UPDATE ON product_relationships TO "halilit_user";
GRANT SELECT, INSERT, UPDATE ON hierarchy_validation_log TO "halilit_user";
GRANT SELECT ON hierarchy_complete TO "halilit_user";
GRANT SELECT ON products_missing_hierarchy TO "halilit_user";
