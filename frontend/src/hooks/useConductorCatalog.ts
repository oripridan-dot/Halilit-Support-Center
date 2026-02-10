/**
 * useConductorCatalog v8.0
 *
 * PRIMARY HOOK for all frontend data loading.
 *
 * All product data is fetched from /api/conductor/catalog endpoint,
 * which serves ONLY Conductor-verified products.
 *
 * This ensures:
 * ✅ 100% of data has been through the 6-phase Conductor pipeline
 * ✅ Consistent taxonomy across the entire catalog
 * ✅ Data validity and compliance verification
 * ✅ Single source of truth (no conflicting data sources)
 */

import { useQuery } from '@tanstack/react-query';

export interface ConductorProduct {
    id: string;
    product_name: string;
    brand: string;
    taxonomy: {
        canonical_category: string;
        canonical_subcategory: string;
        keywords: string[];
    };
    pricing: {
        price_il: number;
        price_eilat: number;
        tier: 'entry' | 'mid' | 'pro' | 'flagship' | 'legacy';
        currency: string;
    };
    display: {
        display_role: 'hero' | 'cornerstone' | 'specialist' | 'entry' | 'hidden';
        hero_image?: string;
        thumbnail_image?: string;
        color_hint?: string;
        should_highlight: boolean;
    };
    specifications: Record<string, any>;
    description_short: string;
    description_long: string;
    validation_status: string;
    source: string;
    confidence: string;
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
            console.log(`✅ Loaded Conductor catalog: ${data.metadata.total_products} products from ${data.metadata.brands.length} brands`);
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
 */
export const useConductorProductsByCategory = (category: string | null) => {
    const { catalog, isLoading: catalogLoading } = useConductorCatalog();

    const products = (catalog?.products || []).filter(
        p => p.taxonomy.canonical_category === category
    );

    return {
        products,
        count: products.length,
        isLoading: catalogLoading,
    };
};
