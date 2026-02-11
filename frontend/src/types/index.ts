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
import type { IngestionProductDraft, PricingTier, IngestionStatus } from './generated';

// ============================================
// TYPE ALIASES (for backward compatibility)
// ============================================

/** Product type - alias for IngestionProductDraft */
export type Product = IngestionProductDraft;
export type OptimizedProduct = IngestionProductDraft; // Legacy support

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
export type Tier = PricingTier;

// ============================================
// HELPER FUNCTIONS
// ============================================

/**
 * Get product price formatted for display
 * @deprecated Prefer inline formatting in components
 */
export function formatPrice(product: Product): string {
  const price = (product as any).price || product.pricing?.price_il || product.price_il;
  if (!price) return 'Price on request';
  return new Intl.NumberFormat('en-IL', {
    style: 'currency',
    currency: 'ILS'
  }).format(price);
}

/**
 * Get product tier color
 */
export function getTierColor(tier: PricingTier): string {
  const colors: Record<string, string> = {
    entry: '#F59E0B',   // Bronze
    mid: '#9CA3AF',     // Silver
    pro: '#FBBF24',     // Gold
    flagship: '#60A5FA', // Diamond/Blue
    legacy: '#4B5563'   // Grey
  };
  return colors[tier] || colors.entry;
}

/**
 * Filter products by tier
 */
export function filterByTier(products: Product[], tier: PricingTier): Product[] {
  return products.filter(p => (p.pricing?.tier || (p as any).tier) === tier);
}

/**
 * Search products by text
 */
export function searchProducts(products: Product[], query: string): Product[] {
  const q = query.toLowerCase();
  return products.filter(p =>
    p.product_name?.toLowerCase().includes(q) ||
    p.brand?.toLowerCase().includes(q)
  );
}
