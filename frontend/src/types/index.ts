/**
 * Halilit Support Center - Unified Types  v9.7.0
 *
 * SINGLE source of truth for all frontend TypeScript types.
 *
 * ARCHITECTURE:
 *   - `Product` / `ConductorProduct` = catalog API shape (id, name, price, specs, …)
 *   - `PipelineProduct` / `IngestionProductDraft` = internal backend pipeline model
 *
 * ⚠️  Do NOT access pipeline-model fields (halilit_id, product_name, price_il,
 *     display?.hero_image) in UI components. Use ConductorProduct fields instead.
 */

// ── Backend pipeline types (internal / non-UI) ────────────────────────────────
export * from './generated';
import type { IngestionProductDraft, PricingTier } from './generated';

/** Backend pipeline model — NOT for UI rendering. Use Product instead. */
export type PipelineProduct = IngestionProductDraft;

// ── Canonical frontend product type ──────────────────────────────────────────
export type { ConductorProduct } from '../hooks/useConductorCatalog';
import type { ConductorProduct } from '../hooks/useConductorCatalog';

// ── Type aliases ─────────────────────────────────────────────────────────────

/**
 * Product — canonical UI type backed by ConductorProduct.
 * API fields: id, name, brand, price, price_eilat, image_url, image_gallery,
 *             specs, features, description, data_trust, quality_score, stock, …
 */
export type Product = ConductorProduct;

/** @deprecated Use Product (ConductorProduct) */
export type OptimizedProduct = ConductorProduct;

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

/** Format IL price for display */
export function formatPrice(product: Product): string {
  const price = product.price;
  if (!price || price === 0) return 'Call for Price';
  return new Intl.NumberFormat('he-IL', {
    style: 'currency',
    currency: 'ILS',
    maximumFractionDigits: 0,
  }).format(price);
}

/** Format Eilat price for display */
export function formatPriceEilat(product: Product): string {
  const price = product.price_eilat;
  if (!price || price === 0) return 'Call for Price';
  return new Intl.NumberFormat('he-IL', {
    style: 'currency',
    currency: 'ILS',
    maximumFractionDigits: 0,
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

/** Filter products by tier */
export function filterByTier(products: Product[], tier: PricingTier): Product[] {
  return products.filter(p => p.tier === tier);
}

/** Search products by text (uses pre-built search_text index or name/brand fallback) */
export function searchProducts(products: Product[], query: string): Product[] {
  const q = query.toLowerCase();
  return products.filter(p =>
    p.search_text?.toLowerCase().includes(q) ||
    p.name?.toLowerCase().includes(q) ||
    p.brand?.toLowerCase().includes(q)
  );
}
