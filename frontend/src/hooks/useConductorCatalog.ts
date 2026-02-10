/**
 * useConductorCatalog v9.0
 *
 * PRIMARY HOOK for all frontend data loading.
 *
 * All product data is fetched from /api/conductor/catalog endpoint.
 * Backend normalizes every product into a predictable flat shape via
 * product_normalizer.normalize_product(), so the frontend can trust
 * that price, image_url, name, etc. always exist and are valid.
 */

import { useQuery } from '@tanstack/react-query';

/**
 * Canonical product shape — matches backend product_normalizer output exactly.
 * No fallback chains needed: every field is guaranteed present by the backend.
 */
export interface ConductorProduct {
    id: string;
    halilit_id: string;
    name: string;
    product_name: string;
    brand: string;
    category: string;
    /** Always > 0 (backend quality gate) */
    price: number;
    price_il: number;
    currency: string;
    /** Always a valid URL (backend quality gate) */
    image_url: string;
    description: string;
    image_hero: string;
    image_gallery: Array<{ url: string }>;
    official_images: Array<{ url?: string; display_purpose?: string }>;
    taxonomy: {
        canonical_category: string;
        canonical_subcategory?: string;
        keywords?: string[];
    };
    display: {
        hero_image: { url: string };
        color_hint: string;
        display_role: string;
        should_highlight: boolean;
    };
    sources: string[];
    official_specs: Record<string, any>;
    specifications: Record<string, any>;
    quality_score: number;
    data_completeness: number;
    review_data: {
        aggregate_rating: number;
        total_reviews: number;
        pros_and_cons: Record<string, any>;
    };
    pricing: {
        price_il: number;
        price_eilat: number;
        tier: string;
    };
}

export interface ConductorCatalog {
    products: ConductorProduct[];
    metadata: {
        total_products: number;
        brands: string[];
        categories: Record<string, number>;
        timestamp: string;
        source: 'conductor_verified';
        verification_status: 'complete' | 'error';
        cache_ttl_seconds: number;
    };
}

/**
 * Load unified Conductor catalog
 */
export const useConductorCatalog = () => {
    const { data, isLoading, error, refetch } = useQuery<ConductorCatalog>({
        queryKey: ['conductor-catalog'],
        queryFn: async () => {
            const response = await fetch('/api/conductor/catalog');
            if (!response.ok) {
                throw new Error(`Failed to load Conductor catalog: ${response.statusText}`);
            }
            const data = await response.json();
            console.log(`✅ Enriched Catalog v8.2: ${data.metadata.total_products} products with full descriptions, images, and specs from ${data.metadata.brands.length} brands`);
            console.log(`📊 Data Quality: ${data.metadata.source}`);
            return data;
        },
        staleTime: 5 * 60 * 1000, // 5 minutes
        gcTime: 10 * 60 * 1000, // 10 minutes (was cacheTime)
        retry: 2,
        refetchOnWindowFocus: true,
        refetchOnReconnect: true,
    });

    return {
        catalog: data || null,
        products: data?.products || [],
        isLoading,
        error: error ? (error as Error).message : null,
        refetch,
        totalProducts: data?.metadata.total_products || 0,
        brands: data?.metadata.brands || [],
        categories: data?.metadata.categories || {},
    };
};

/**
 * Get products by category (uses cached catalog data)
 * Supports both canonical category names and galaxy IDs
 */
export const useConductorProductsByCategory = (category: string | null) => {
    const { catalog, isLoading: catalogLoading } = useConductorCatalog();

    const products = (catalog?.products || []).filter(
        p => {
            if (!category) return true;
            // Match by canonical category name or galaxy ID
            return p.taxonomy.canonical_category === category
                || p.taxonomy.canonical_category?.toLowerCase().includes(category.toLowerCase());
        }
    );

    return {
        products,
        count: products.length,
        isLoading: catalogLoading,
    };
};
