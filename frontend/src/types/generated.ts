/**
 * Auto-generated TypeScript types from Pydantic models.
 * Generated: 2026-01-31T20:49:07.487372
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
  brand_id?: string;
  brand?: string; // Alias for brand_id
  category?: string;
  subcategory?: string; // Primary subcategory
  subcategories?: string[];
  main_category?: string; // For category filtering
  category_hierarchy?: string[]; // Category breadcrumb
  tier?: string;
  tier_score?: number;
  score?: number; // TierBar score
  description_short?: string;
  short_description?: string; // Legacy alias
  description_full?: string;
  description?: string; // Legacy description field
  price?: number | null;
  currency?: string;
  stock_status?: string;
  sku?: string; // Product SKU
  image_hero?: Record<string, any>;
  image_thumbnail?: Record<string, any>;
  image_gallery?: Record<string, any>[];
  image_url?: string; // Legacy single image
  image?: string; // Legacy single image alias
  images?: any; // Legacy images object/array
  logo_url?: string; // Brand logo
  color_primary?: string | null;
  specs?: Record<string, Record<string, string>[]> | { name: string; value: string }[];
  specifications?: Record<string, any>; // Legacy specs format
  official_specs?: Record<string, any>; // Official specs
  official_gallery?: string[]; // Official gallery images
  official_manuals?: any; // Official manuals
  pros?: string[];
  cons?: string[];
  expert_tips?: string[];
  search_text?: string;
  filter_tags?: string[];
  filters?: string[]; // Dynamic filter tags
  tags?: string[]; // Legacy filter tags
  render_hints?: Record<string, boolean>;
  ui_context?: Record<string, any>; // UI metadata
  ui_meta?: Record<string, any>; // Legacy UI metadata
  processed_badge?: { level?: string; score?: number }; // Quality badge
  source_url?: string | null;
  purchase_url?: string | null;
  synced_at?: string;
  // Legacy v4 properties
  identity?: { name?: string; brand?: string; images?: string[]; official_images?: string[] };
  context?: { verified_pros?: string[]; verified_cons?: string[]; trusted_sources?: { name: string; url?: string }[] };
  verified?: boolean;
  pricing?: { price?: number; currency?: string; sale_price?: number };
  pill_data?: Record<string, any>; // Refinery pill data
  necessities?: any; // Related necessities
  accessories?: any; // Related accessories
  related?: any; // Related products
}

export interface BrandSummary {
  id?: string;
  name?: string;
  logo_url?: string | null;
  brand_color?: string | null;
  product_count?: number;
  verified_count?: number;
  data_file?: string;
}

export interface BrandCatalog {
  brand?: string;
  brand_name?: string;
  brand_color?: string | null;
  logo_url?: string | null;
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
