/**
 * Halilit Support Center - Unified Types
 * 
 * This is the SINGLE source of truth for all TypeScript types.
 * Types are aligned with the backend pipeline output format.
 * 
 * Run `python -m backend.pipeline types` to regenerate generated.ts
 */

// Re-export auto-generated types from backend
export * from './generated';

// Import for local use
import type { OptimizedProduct, BrandCatalog, CatalogIndex, TierLevel, StockStatus } from './generated';

// ============================================
// TYPE ALIASES (for backward compatibility)
// ============================================

/** Product type - alias for OptimizedProduct */
export type Product = OptimizedProduct;

/** GoldenProduct - legacy alias */
export type GoldenProduct = OptimizedProduct;

/** BrandIdentity - brand metadata */
export interface BrandIdentity {
  id?: string;
  name?: string;
  logo_url?: string | null;
  website?: string | null;
  description?: string | null;
  brand_colors?: { primary?: string; secondary?: string };
  categories?: string[];
}

/** ProductImagesType - legacy images structure */
export type ProductImagesType = {
  main?: string;
  thumbnail?: string;
  gallery?: string[];
} | string[] | string;

// ============================================
// ADDITIONAL UI-SPECIFIC TYPES
// ============================================

/** Image asset structure */
export interface ProductImage {
  url: string;
  alt?: string;
  width?: number;
  height?: number;
  type?: string;
}

/** Images object for products */
export interface ProductImagesObject {
  hero?: ProductImage;
  thumbnail?: ProductImage;
  gallery?: ProductImage[];
}

/** Specification item */
export interface SpecItem {
  key: string;
  value: string;
  unit?: string;
  icon?: string;
}

/** Product pricing info */
export interface ProductPricing {
  regular_price?: number;
  sale_price?: number;
  currency?: string;
}

/** View types for product display */
export type ViewType = 'TierBar' | 'Grid' | 'Table' | 'Galaxy';

/** Product tier levels */
export type Tier = TierLevel;

// ============================================
// CATALOG TYPES
// ============================================

export type { BrandCatalog, CatalogIndex };

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Get product price formatted for display
 */
export function formatPrice(product: Product): string {
  if (!product.price) return 'Price on request';
  const currency = product.currency || 'USD';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency
  }).format(product.price);
}

/**
 * Get product tier color
 */
export function getTierColor(tier: TierLevel): string {
  const colors: Record<TierLevel, string> = {
    diamond: '#60A5FA',
    gold: '#FBBF24',
    silver: '#9CA3AF',
    bronze: '#F59E0B'
  };
  return colors[tier] || colors.bronze;
}

/**
 * Filter products by tier
 */
export function filterByTier(products: Product[], tier: TierLevel): Product[] {
  return products.filter(p => p.tier === tier);
}

/**
 * Search products by text
 */
export function searchProducts(products: Product[], query: string): Product[] {
  const q = query.toLowerCase();
  return products.filter(p =>
    p.search_text?.toLowerCase().includes(q) ||
    p.name?.toLowerCase().includes(q)
  );
}
