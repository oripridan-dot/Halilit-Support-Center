/**
 * useConductorCatalog v7.3
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
import { useCallback } from 'react';

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

export interface ConductorTaxonomy {
    universal_categories: Array<{
        id: string;
        name: string;
        icon?: string;
        subcategories?: string[];
    }>;
    all_brands: string[];
    pricing_tiers: string[];
    display_roles: string[];
    statuses: string[];
    confidence_levels: string[];
    timestamp: string;
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
 * Load Conductor taxonomy schema
 */
export const useConductorTaxonomy = () => {
    const { data, isLoading, error } = useQuery<ConductorTaxonomy>({
        queryKey: ['conductor-taxonomy'],
        queryFn: async () => {
            const response = await fetch('/api/conductor/taxonomy');
            if (!response.ok) {
                throw new Error(`Failed to load taxonomy: ${response.statusText}`);
            }
            const data = await response.json();
            console.log(`✅ Loaded Conductor taxonomy with ${data.universal_categories.length} categories`);
            return data;
        },
        staleTime: 30 * 60 * 1000, // 30 minutes (taxonomy changes less frequently)
        gcTime: 60 * 60 * 1000, // 1 hour
        retry: 2,
    });

    return {
        taxonomy: data || null,
        categories: data?.universal_categories || [],
        brands: data?.all_brands || [],
        pricingTiers: data?.pricing_tiers || [],
        displayRoles: data?.display_roles || [],
        isLoading,
        error: error ? (error as Error).message : null,
    };
};

/**
 * Filter Conductor products with flexible options
 */
export const useConductorFilter = (filters: {
    brand?: string | string[];
    category?: string | string[];
    subcategory?: string | string[];
    pricing_tier?: string | string[];
    min_price?: number;
    max_price?: number;
    display_role?: string | string[];
    search_query?: string;
}) => {
    const { data, isLoading, error, refetch } = useQuery<any>({
        queryKey: ['conductor-filter', filters],
        queryFn: async () => {
            const response = await fetch('/api/conductor/filter', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(filters),
            });
            if (!response.ok) {
                throw new Error(`Filter failed: ${response.statusText}`);
            }
            return response.json();
        },
        enabled: Object.keys(filters).length > 0,
        staleTime: 2 * 60 * 1000, // 2 minutes
        gcTime: 5 * 60 * 1000, // 5 minutes
    });

    return {
        products: data?.products || [],
        totalResults: data?.total_results || 0,
        filtersApplied: data?.filters_applied || {},
        isLoading,
        error: error ? (error as Error).message : null,
        refetch,
    };
};

/**
 * Get category summary for navigation
 */
export const useConductorCategories = () => {
    const { data, isLoading, error } = useQuery<any>({
        queryKey: ['conductor-categories'],
        queryFn: async () => {
            const response = await fetch('/api/conductor/categories');
            if (!response.ok) {
                throw new Error(`Failed to load categories: ${response.statusText}`);
            }
            return response.json();
        },
        staleTime: 10 * 60 * 1000, // 10 minutes
        gcTime: 30 * 60 * 1000, // 30 minutes
        retry: 2,
    });

    return {
        categories: data?.categories || [],
        isLoading,
        error: error ? (error as Error).message : null,
    };
};

/**
 * Get products by category
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

/**
 * Get products by brand
 */
export const useConductorProductsByBrand = (brand: string | null) => {
    const { catalog, isLoading: catalogLoading } = useConductorCatalog();

    const products = (catalog?.products || []).filter(
        p => p.brand.toLowerCase() === brand?.toLowerCase()
    );

    return {
        products,
        count: products.length,
        isLoading: catalogLoading,
    };
};

/**
 * Trigger catalog refresh after Conductor pipeline completes
 */
export const useConductorCatalogRefresh = () => {
    const refresh = useCallback(async () => {
        try {
            const response = await fetch('/api/conductor/refresh');
            if (!response.ok) {
                throw new Error('Refresh failed');
            }
            const result = await response.json();
            console.log(`✅ Catalog refreshed: ${result.product_count} products`);
            return result;
        } catch (error) {
            console.error('❌ Catalog refresh failed:', error);
            throw error;
        }
    }, []);

    return { refresh };
};
