-- Add sources_verified for triple-checked relationship support.
-- Run this if product_relationships already exists without this column.
ALTER TABLE product_relationships
  ADD COLUMN IF NOT EXISTS sources_verified JSONB DEFAULT '[]';
