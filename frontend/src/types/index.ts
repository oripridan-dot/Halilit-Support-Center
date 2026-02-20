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
// NOTE: IngestionProductDraft and PricingTier are defined inline below.

/** Backend pipeline model — NOT for UI rendering. Use Product instead.
 *  Defined inline — no generated.ts required. */
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

/** Product image structure */
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

/** Spec item */
export interface SpecItem {
    key: string;
    value: string;
    unit?: string;
    icon?: string;
}

/** Pricing info */
export interface ProductPricing {
    regular_price?: number;
    sale_price?: number;
    currency?: string;
}

/** View types */
export type ViewType = 'TierBar' | 'Grid' | 'Table' | 'Galaxy';

/** Pricing tiers */
export type PricingTier = 'entry' | 'mid' | 'pro' | 'flagship' | 'legacy';
export type Tier = PricingTier;

/** Ingestion status (kept for backward compat) */
export type IngestionStatus = 'harvested' | 'enriched' | 'validated' | 'approved' | 'rejected' | 'archived';

/** Legacy alias — points to Product */
export type IngestionProductDraft = Product;

// ============================================
// JIT INTELLIGENCE TYPES
// ============================================

/** Review verdict from a trusted source */
export interface ReviewVerdict {
    source: string;
    summary: string;
    sentiment: 'positive' | 'neutral' | 'negative';
    url: string;
    logo_key: string;
}

/** Brand visual theme */
export interface BrandTheme {
    primary_color: string;
    secondary_color: string;
    background_style: 'dark' | 'light' | 'gradient';
}

/** Famous user/artist association */
export interface FamousUser {
    name: string;
    context: string;
}

/** Known product issue */
export interface KnownIssue {
    issue: string;
    severity: 'low' | 'medium' | 'high';
    source: string;
}

/** Layout hints from JIT agent */
export interface LayoutHints {
    show_comparison?: boolean;
    show_signal_chain?: boolean;
    show_artist_spotlight?: boolean;
    show_family_tree?: boolean;
    product_category?: string;
}

/** Product comparison result */
export interface ProductComparison {
    summary: string;
    winner: string;
    spec_comparison: Array<{
        feature: string;
        product_a_value: string;
        product_b_value: string;
        advantage: 'a' | 'b' | 'tie';
    }>;
    price_value: string;
    use_case_a: string;
    use_case_b: string;
    recommendation: string;
    product_a: { id: string; name: string; price: number };
    product_b: { id: string; name: string; price: number };
}

// ============================================
// JIT STREAMING TYPES (HSC JIT Architecture)
// ============================================

/** Exploration path — an interactive "mission button" in the Action Dock */
export interface ExplorationPath {
    type: 'comparison' | 'deep_dive' | 'how_to' | 'artist_spotlight' | 'field_notes' | 'accessories';
    label: string;
    icon: string;
    description: string;
    action: {
        type: 'compare' | 'show_specs' | 'explore';
        topic?: string;
        target_id?: string;
    };
}

/** SSE Snap phase data — instant skeleton */
export interface JITSnap {
    id: string;
    name: string;
    brand: string;
    price: number;
    price_eilat: number;
    tier: string;
    image_url: string;
    image_gallery: string[];
    brand_logo: string;
    halilit_url: string;
    official_url: string;
    galaxy_id: string;
    spectrum_id: string;
    description: string;
    features: string[];
    specs: Record<string, string>;
    family_id: string;
    variant_key: string;
    quality_score: number;
    data_status: string;
}

/** SSE Promise phase data — research progress */
export interface JITPromise {
    step: string;
    message: string;
    progress: number;
}

/** SSE Deliver phase data — full intelligence */
export interface JITDelivery {
    description: string;
    description_short: string;
    specs: Record<string, string>;
    features: string[];
    pros: string[];
    cons: string[];
    rating: number;
    review_verdicts: ReviewVerdict[];
    brand_theme: BrandTheme;
    famous_users: FamousUser[];
    known_issues: KnownIssue[];
    suggested_accessories: string[];
    layout_hints: LayoutHints;
    official_url: string;
    exploration_paths: ExplorationPath[];
    enriched?: boolean;
}

/** Complete JIT stream state */
export interface JITStreamState {
    phase: 'idle' | 'snap' | 'promise' | 'deliver' | 'complete' | 'error';
    snap: JITSnap | null;
    promise: JITPromise | null;
    delivery: JITDelivery | null;
    error: string | null;
    cached: boolean;
    durationMs: number;
}

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
