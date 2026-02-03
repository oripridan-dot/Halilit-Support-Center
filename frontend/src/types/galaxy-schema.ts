/**
 * THE GALAXY STANDARD
 * Extended type definitions for the unified product catalog.
 * This is the Single Source of Truth for the UI.
 */

/**
 * Core Galaxy Product Interface
 * Represents a single product after refinement and validation.
 */
export interface GalaxyProduct {
    // Core Identity
    id: string; // SKU or UUID
    name: string;
    brand: string; // Normalized (e.g., "Nord" not "Nord Keyboards")

    // Taxonomy
    category: string;
    subCategory: string;
    tier: 'entry' | 'mid' | 'pro' | 'flagship';

    // Visuals
    images: {
        main: string;
        thumbnail: string;
        gallery: string[];
    };

    // Commerce
    price: number;
    stockStatus: 'in_stock' | 'low_stock' | 'out_of_stock' | 'pre_order';

    // The "Brain" Data (For Frontend AI Features)
    aiTags: string[]; // e.g. ["warm sound", "analog", "vintage", "entry"]
    specs: Record<string, string>; // { "polyphony": "128", "weight": "10kg" }
    searchTokens: string; // Pre-computed search string for speed
    description: string; // Product description/summary
}

/**
 * Full Catalog Container
 * The unified database exported by the backend refinery.
 */
export interface GalaxyCatalog {
    generatedAt: string; // ISO 8601 timestamp
    version: string; // Semantic version
    stats: {
        totalProducts: number;
        brandsCount: number;
    };
    products: GalaxyProduct[];
    categories: Record<string, string[]>; // Map Category -> SubCategories
}

/**
 * Search Result
 * Returned from semantic search operations.
 */
export interface SearchResult {
    product: GalaxyProduct;
    relevance: number; // 0-1, confidence score
}

/**
 * Tier Statistics
 * For analytics and filtering
 */
export interface TierStats {
    tier: 'entry' | 'mid' | 'pro' | 'flagship';
    count: number;
    avgPrice: number;
    minPrice: number;
    maxPrice: number;
}

/**
 * Brand Profile
 * Metadata about a brand
 */
export interface BrandProfile {
    name: string;
    productCount: number;
    categories: Set<string>;
    avgPrice: number;
    tiers: Record<string, number>; // tier -> count
}

/**
 * Category Statistics
 */
export interface CategoryStats {
    name: string;
    productCount: number;
    brands: string[];
    subCategories: Record<string, number>; // subcategory -> product count
    priceRange: {
        min: number;
        max: number;
        avg: number;
    };
}
