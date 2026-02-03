/**
 * Auto-generated TypeScript types from Pydantic models.
 * Generated: 2026-02-02T14:04:29.361321
 * DO NOT EDIT MANUALLY - run `python -m backend.pipeline types` to regenerate
 */

// Enums

export type TierLevel = 'diamond' | 'gold' | 'silver' | 'bronze';

export type StockStatus = 'in_stock' | 'out_of_stock' | 'pre_order' | 'discontinued' | 'unknown';

// Interfaces

export interface ImageAsset {
  url: string;
  alt: string;
  width?: number | null;
  height?: number | null;
}

export interface SpecItem {
  key: string;
  value: string;
  unit?: string;
}

export interface OptimizedProduct {
  id?: string;
  name?: string;
  slug?: string;
  sku?: string;
  brand_id?: string;
  category?: string;
  subcategories?: string[];
  tier?: string;
  tier_score?: number;
  description_short?: string;
  description_full?: string;
  price?: number;
  currency?: string;
  in_stock?: boolean;
  stock_status?: string;
  image_hero?: Record<string, any>;
  image_thumbnail?: Record<string, any>;
  image_gallery?: Record<string, any>[];
  color_primary?: string;
  specs?: Record<string, any>;
  pros?: string[];
  cons?: string[];
  expert_tips?: string[];
  search_text?: string;
  filter_tags?: string[];
  render_hints?: Record<string, boolean>;
  source_url?: string;
  purchase_url?: string;
  synced_at?: string;
  manuals?: Record<string, string>[];
  related_products?: Record<string, any>[];
  reviews?: Record<string, any>;
  is_bestseller?: boolean;
  badges?: Record<string, string>[];
  features_html?: string;
  features?: string[];
  // --- Manual Patches for UI Support ---
  brand?: string;
  pill_data?: any;
  main_category?: string;
  official_manuals?: any;
  official_gallery?: any;
  necessities?: any;
  accessories?: any;
  related?: any;
  specifications?: any;
  description?: string; // alias for description_full/short checks
}

export interface BrandSummary {
  id?: string;
  name?: string;
  logo_url?: string;
  brand_color?: string;
  product_count?: number;
  verified_count?: number;
  data_file?: string;
}

export interface BrandCatalog {
  brand?: string;
  brand_name?: string;
  brand_color?: string;
  logo_url?: string;
  product_count?: number;
  products?: OptimizedProduct[];
  generated_at?: string;
}

export interface CatalogIndex {
  version?: string;
  build_timestamp?: string;
  total_products?: number;
  total_verified?: number;
  brands?: BrandSummary[];
}
