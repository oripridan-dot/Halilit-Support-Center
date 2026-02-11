/**
 * useConductorCatalog v10.0
 *
 * PRIMARY HOOK for all frontend data loading.
 *
 * All product data is fetched from /api/conductor/catalog.
 * The backend normalizer v10 pre-indexes the catalog:
 *   - products[]  — flat array of canonical product shapes
 *   - indexes     — by_galaxy, by_spectrum, by_brand (product index maps)
 *   - metadata    — galaxy_counts, spectrum_counts, brand_counts, galaxies
 *
 * Frontend does ZERO classification — all galaxy/spectrum assignment
 * is done once at normalization time in the backend.
 */

import { useQuery } from '@tanstack/react-query';
import { useMemo } from 'react';

/**
 * Canonical product shape — matches backend product_normalizer.normalize_product() exactly.
 * Every field is guaranteed present; no fallback chains needed.
 */
export interface ConductorProduct {
    id: string;
    name: string;
    brand: string;
    brand_logo: string;
    galaxy_id: string;
    spectrum_id: string;
    category: string;
    subcategory: string;
    price: number;
    price_eilat: number;
    currency: string;
    tier: string;
    image_url: string;
    image_gallery: string[];
    description: string;
    description_short: string;
    specs: Record<string, any>;
    features: string[];
    faq: Array<{ question: string; answer: string }>;
    audiences: string[];
    rating: number;
    review_count: number;
    pros: string[];
    cons: string[];
    contextual_data: Record<string, any>;
    quality_score: number;
    halilit_url: string;
    official_url: string;
    sources: string[];
    data_trust: {
        price_source: 'halilit' | 'official' | 'none';
        specs_source: 'halilit' | 'official' | 'none';
        description_source: 'halilit' | 'official' | 'none';
        image_source: 'halilit' | 'official' | 'none';
        review_source: 'contextual' | 'none';
    };
    search_text: string;
}

export interface CatalogIndexes {
    by_galaxy: Record<string, number[]>;
    by_spectrum: Record<string, number[]>;
    by_brand: Record<string, number[]>;
}

export interface GalaxyDef {
    id: string;
    label: string;
    spectrums: { id: string; label: string }[];
}

export interface CatalogMetadata {
    total_products: number;
    brands: string[];
    galaxy_counts: Record<string, number>;
    spectrum_counts: Record<string, number>;
    brand_counts: Record<string, number>;
    galaxies: GalaxyDef[];
    source: string;
    cache_ttl_seconds: number;
    timestamp?: string;
}

export interface ConductorCatalog {
    products: ConductorProduct[];
    indexes: CatalogIndexes;
    metadata: CatalogMetadata;
}

/**
 * Load unified Conductor catalog — the single data source for all 3 screens.
 */
export const useConductorCatalog = () => {
    const { data, isLoading, error, refetch } = useQuery<ConductorCatalog>({
        queryKey: ['conductor-catalog'],
        queryFn: async () => {
            const response = await fetch('/api/conductor/catalog');
            if (!response.ok) {
                throw new Error(`Failed to load catalog: ${response.statusText}`);
            }
            const catalog: ConductorCatalog = await response.json();
            console.log(
                `✅ Catalog v10: ${catalog.metadata.total_products} products, ` +
                `${catalog.metadata.brands.length} brands, ` +
                `${Object.keys(catalog.metadata.galaxy_counts).length} galaxies`
            );
            return catalog;
        },
        staleTime: 5 * 60 * 1000,
        gcTime: 10 * 60 * 1000,
        retry: 2,
        refetchOnWindowFocus: true,
        refetchOnReconnect: true,
    });

    return {
        catalog: data || null,
        products: data?.products || [],
        indexes: data?.indexes || { by_galaxy: {}, by_spectrum: {}, by_brand: {} },
        metadata: data?.metadata || null,
        isLoading,
        error: error ? (error as Error).message : null,
        refetch,
        totalProducts: data?.metadata.total_products || 0,
        brands: data?.metadata.brands || [],
        galaxyCounts: data?.metadata.galaxy_counts || {},
        spectrumCounts: data?.metadata.spectrum_counts || {},
        galaxies: data?.metadata.galaxies || [],
    };
};

/**
 * Get products for a specific galaxy using pre-computed indexes.
 * O(1) lookup — no iteration or regex classification.
 */
export const useProductsByGalaxy = (galaxyId: string | null) => {
    const { products, indexes, isLoading } = useConductorCatalog();

    const galaxyProducts = useMemo(() => {
        if (!galaxyId || !indexes.by_galaxy[galaxyId]) return products;
        return indexes.by_galaxy[galaxyId].map(idx => products[idx]).filter(Boolean);
    }, [galaxyId, indexes, products]);

    return {
        products: galaxyProducts,
        count: galaxyProducts.length,
        isLoading,
    };
};

/**
 * Get products for a specific spectrum using pre-computed indexes.
 */
export const useProductsBySpectrum = (spectrumId: string | null) => {
    const { products, indexes, isLoading } = useConductorCatalog();

    const spectrumProducts = useMemo(() => {
        if (!spectrumId || !indexes.by_spectrum[spectrumId]) return [];
        return indexes.by_spectrum[spectrumId].map(idx => products[idx]).filter(Boolean);
    }, [spectrumId, indexes, products]);

    return {
        products: spectrumProducts,
        count: spectrumProducts.length,
        isLoading,
    };
};

/**
 * @deprecated Use useProductsByGalaxy or useProductsBySpectrum instead.
 */
export const useConductorProductsByCategory = (category: string | null) => {
    const { products, indexes, isLoading } = useConductorCatalog();

    const filtered = useMemo(() => {
        if (!category) return products;
        // Try galaxy index first, then spectrum
        const galaxyIdxs = indexes.by_galaxy[category];
        if (galaxyIdxs) return galaxyIdxs.map(i => products[i]).filter(Boolean);
        const specIdxs = indexes.by_spectrum[category];
        if (specIdxs) return specIdxs.map(i => products[i]).filter(Boolean);
        return [];
    }, [category, indexes, products]);

    return { products: filtered, count: filtered.length, isLoading };
};

