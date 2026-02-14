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
