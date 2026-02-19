/**
 * Halilit Support Center — Unified Types (JIT Architecture v9)
 *
 * This is the SINGLE source of truth for all TypeScript types.
 * Types are aligned with the backend pipeline output format.
 *
 * Types auto-generated from backend data models.
 */

// ============================================
// PRODUCT TYPES
// ============================================

/** Backward-compat alias — used by some older components */
export interface Product {
    halilit_id?: string;
    product_name?: string;
    official_name?: string;
    model_number?: string;
    brand?: string;
    sku?: string | null;
    price_il?: number;
    price_eilat?: number;
    description?: string;
    page_description?: string;
    image_url?: string;
    image_gallery?: string[];
    official_images?: Array<{
        url: string;
        type?: string;
        display_purpose?: string;
        source?: string;
        priority?: number;
    }>;
    features?: string[];
    faq?: Array<{ question: string; answer: string }>;
    audiences?: string[];
    [key: string]: any;
}

/** Brand identity metadata */
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

/** Format a product's IL price as a localized currency string. */
export function formatPrice(product: Product): string {
    const price = product.price_il ?? product.pricing?.price_il;
    if (price == null) return 'Call for Price';
    return new Intl.NumberFormat('he-IL', { style: 'currency', currency: 'ILS' }).format(price);
}
