/**
 * Spectrum V2 Types — Domain-driven instrument families,
 * model grouping, and semantic zoom for the redesigned Spectrum view.
 */

// ═══════════════════════════════════════════════════════════════════════════
// Zoom Levels
// ═══════════════════════════════════════════════════════════════════════════

export type ZoomLevel = 'galaxy' | 'constellation' | 'cluster' | 'star';

export const ZOOM_ORDER: ZoomLevel[] = ['galaxy', 'constellation', 'cluster', 'star'];

export const ZOOM_META: Record<ZoomLevel, { label: string; icon: string; description: string }> = {
    galaxy: { label: 'Families', icon: '🌌', description: 'Instrument families overview' },
    constellation: { label: 'Brands', icon: '✨', description: 'Brands within family' },
    cluster: { label: 'Models', icon: '⭐', description: 'Model groups with price ranges' },
    star: { label: 'Variants', icon: '💫', description: 'All product variations' },
};

// ═══════════════════════════════════════════════════════════════════════════
// Instrument Family Tree
// ═══════════════════════════════════════════════════════════════════════════

export interface BodyType {
    slug: string;
    label: string;
}

export interface SubCategory {
    slug: string;
    label: string;
    bodyTypes: BodyType[];
}

export interface InstrumentFamily {
    slug: string;
    label: string;
    icon: string;
    subCategories: SubCategory[];
}

// ═══════════════════════════════════════════════════════════════════════════
// Model Groups (from API)
// ═══════════════════════════════════════════════════════════════════════════

export interface ModelVariation {
    id: string;
    name: string;
    variation: string;
    price: number;
    price_eilat: number;
    tier: string;
    image_url: string;
    sources: string[];
    quality_score: number;
    data_status: string;
    specs: Record<string, any>;
    rating: number;
    family_id: string | null;
}

export interface PriceRange {
    min: number;
    max: number;
    currency: string;
}

export interface ModelGroup {
    modelName: string;
    modelKey: string;
    brand: string;
    family: string;
    subCategory: string;
    bodyType: string;
    variationCount: number;
    priceRange: PriceRange;
    heroImage: string;
    avgConfidence: number;
    primaryTier?: string;
    variations?: ModelVariation[];
}

// ═══════════════════════════════════════════════════════════════════════════
// API Response Shapes
// ═══════════════════════════════════════════════════════════════════════════

export interface FamilySummary {
    family: string;
    label: string;
    modelCount: number;
    productCount: number;
    brandCount: number;
    priceMin: number;
    priceMax: number;
}

export interface BrandSummary {
    brand: string;
    models: number;
    products: number;
    priceMin: number;
    priceMax: number;
    families: string[];
    topModels: {
        modelName: string;
        heroImage: string;
        variationCount: number;
    }[];
}

export interface SpectrumGalaxyResponse {
    zoom: 'galaxy';
    families: FamilySummary[];
    totalModels: number;
    totalProducts: number;
    elapsed_ms: number;
}

export interface SpectrumConstellationResponse {
    zoom: 'constellation';
    brands: BrandSummary[];
    totalModels: number;
    totalProducts: number;
    elapsed_ms: number;
}

export interface SpectrumClusterResponse {
    zoom: 'cluster';
    modelGroups: ModelGroup[];
    totalModels: number;
    totalProducts: number;
    elapsed_ms: number;
}

export interface SpectrumStarResponse {
    zoom: 'star';
    modelGroups: ModelGroup[];
    totalModels: number;
    totalProducts: number;
    elapsed_ms: number;
}

export type SpectrumResponse =
    | SpectrumGalaxyResponse
    | SpectrumConstellationResponse
    | SpectrumClusterResponse
    | SpectrumStarResponse;

export interface FamiliesResponse {
    families: InstrumentFamily[];
}

// ═══════════════════════════════════════════════════════════════════════════
// Family Icons (for sidebar & galaxy view)
// ═══════════════════════════════════════════════════════════════════════════

export const FAMILY_ICONS: Record<string, string> = {
    guitars: '🎸',
    bass: '🎸',
    amps_effects: '🔊',
    drums_percussion: '🥁',
    keys_production: '🎹',
    studio_recording: '🎙️',
    live_pa: '🔈',
    accessories: '🎵',
    uncategorized: '📦',
};
