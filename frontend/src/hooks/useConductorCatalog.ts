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
// ── Product Graph Types ──

export type RelationshipType =
    | 'variant_of'
    | 'accessory_for'
    | 'compatible_with'
    | 'successor_of'
    | 'bundle_with'
    | 'alternative_to';

export interface ProductRelationship {
    source_id: string;
    target_id: string;
    relationship_type: RelationshipType;
    direction: 'unidirectional' | 'bidirectional';
    confidence: number;
    ai_discovered: boolean;
    manually_curated: boolean;
    compatibility_notes: string;
    discovered_from: string;
}

export interface ProductFamily {
    id: string;
    brand: string;
    family_name: string;
    series: string;
    generation: number | null;
    product_line: string;
    variant_ids: string[];
    accessory_ids: string[];
    hero_image: string;
    description: string;
}

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
    market_price_estimate: number;
    market_price_peers: number;
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
    data_status: 'COMPLETE' | 'GOOD' | 'PARTIAL' | 'MINIMAL';
    data_missing: string[];
    halilit_url: string;
    official_url: string;
    sources: string[];
    data_trust: {
        price_source: 'halilit' | 'official' | 'estimated' | 'none';
        specs_source: 'halilit' | 'official' | 'none';
        description_source: 'halilit' | 'official' | 'synthesized' | 'none';
        image_source: 'halilit' | 'official' | 'none';
        review_source: 'contextual' | 'none';
    };
    search_text: string;
    // ── Product Graph fields (additive) ──
    family_id: string | null;
    variant_key: string | null;
    variant_is_default: boolean | null;
}

export interface CatalogIndexes {
    by_galaxy: Record<string, number[]>;
    by_spectrum: Record<string, number[]>;
    by_brand: Record<string, number[]>;
    // Product Graph indexes
    by_family?: Record<string, number[]>;
    relationships?: Record<string, ProductRelationship[]>;
}

export interface GraphStats {
    total_families: number;
    total_relationships: number;
    confirmed_relationships: number;
    pending_review: number;
    products_in_families: number;
    products_without_family: number;
    relationship_type_counts: Record<string, number>;
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
    // Health metrics from catalog validator
    health_score?: number;
    health_status?: 'COMPLETE' | 'GOOD' | 'PARTIAL' | 'MINIMAL';
    status_counts?: Record<string, number>;
    field_coverage?: Record<string, number>;
    top_issues?: string[];
    // Product Graph metrics
    graph_stats?: GraphStats;
}

export interface FamilyMeta {
    id: string;
    family_name: string;
    brand: string;
    series: string;
    hero_image: string;
    variant_count: number;
}

export interface ConductorCatalog {
    products: ConductorProduct[];
    indexes: CatalogIndexes;
    metadata: CatalogMetadata;
    families?: Record<string, FamilyMeta>;
}

/** Catalog request timeout (first load can take 1–2 min with 7k+ products). */
const CATALOG_FETCH_TIMEOUT_MS = 120_000;

/**
 * Load unified Conductor catalog — the single data source for all 3 screens.
 */
export const useConductorCatalog = () => {
    const { data, isLoading, error, refetch } = useQuery<ConductorCatalog>({
        queryKey: ['conductor-catalog'],
        queryFn: async () => {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), CATALOG_FETCH_TIMEOUT_MS);
            try {
                const response = await fetch('/api/conductor/catalog', {
                    signal: controller.signal,
                });
                clearTimeout(timeoutId);
                if (response.status === 503) {
                    const body = await response.json().catch(() => ({}));
                    throw new Error(
                        body?.error || 'Catalog is still building. Wait a minute and click Retry.'
                    );
                }
                if (!response.ok) {
                    throw new Error(`Failed to load catalog: ${response.status} ${response.statusText}`);
                }
                const catalog: ConductorCatalog = await response.json();
                if (import.meta.env.DEV) {
                    console.log(
                        `✅ Catalog v10: ${catalog.metadata.total_products} products, ` +
                        `${catalog.metadata.brands.length} brands, ` +
                        `${Object.keys(catalog.metadata.galaxy_counts).length} galaxies, ` +
                        `health: ${catalog.metadata.health_score ?? '?'}/100`
                    );
                }
                return catalog;
            } catch (err) {
                clearTimeout(timeoutId);
                if (err instanceof Error) {
                    if (err.name === 'AbortError') {
                        throw new Error(
                            'Catalog request timed out. The first load can take 1–2 minutes. Click Retry.'
                        );
                    }
                    throw err;
                }
                throw err;
            }
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
        families: data?.families || {},
        isLoading,
        error: error ? (error as Error).message : null,
        refetch,
        totalProducts: data?.metadata.total_products || 0,
        brands: data?.metadata.brands || [],
        galaxyCounts: data?.metadata.galaxy_counts || {},
        spectrumCounts: data?.metadata.spectrum_counts || {},
        galaxies: data?.metadata.galaxies || [],
        graphStats: data?.metadata.graph_stats || null,
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


// ═══════════════════════════════════════════════════════════════════════════
// PRODUCT GRAPH HOOKS — Family & Relationship Awareness
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Get all products in the same family as a given product.
 * O(1) index lookup.
 */
export const useProductFamily = (familyId: string | null) => {
    const { products, indexes, isLoading } = useConductorCatalog();

    const familyProducts = useMemo(() => {
        if (!familyId || !indexes.by_family?.[familyId]) return [];
        return indexes.by_family[familyId].map(idx => products[idx]).filter(Boolean);
    }, [familyId, indexes, products]);

    return {
        products: familyProducts,
        count: familyProducts.length,
        isLoading,
    };
};

/**
 * Get all variants in the same family as this product (excludes self).
 */
export const useProductVariants = (productId: string | null) => {
    const { products, indexes, isLoading } = useConductorCatalog();

    const variants = useMemo(() => {
        if (!productId) return [];
        const product = products.find(p => p.id === productId);
        if (!product?.family_id || !indexes.by_family?.[product.family_id]) return [];
        return indexes.by_family[product.family_id]
            .map(idx => products[idx])
            .filter(p => p && p.id !== productId);
    }, [productId, indexes, products]);

    return {
        variants,
        count: variants.length,
        isLoading,
    };
};

/**
 * Get all relationships for a product from the pre-computed index.
 */
export const useProductRelationships = (productId: string | null) => {
    const { products, indexes, isLoading } = useConductorCatalog();

    const result = useMemo(() => {
        if (!productId || !indexes.relationships?.[productId]) {
            return { accessories: [], compatible: [], alternatives: [], all: [] };
        }

        const rels = indexes.relationships[productId];
        const productMap = new Map(products.map(p => [p.id, p]));

        const accessories: ConductorProduct[] = [];
        const compatible: ConductorProduct[] = [];
        const alternatives: ConductorProduct[] = [];

        for (const rel of rels) {
            const otherId = rel.source_id === productId ? rel.target_id : rel.source_id;
            const other = productMap.get(otherId);
            if (!other) continue;

            switch (rel.relationship_type) {
                case 'accessory_for':
                    // Source is the accessory, target is the main product
                    if (rel.target_id === productId) accessories.push(productMap.get(rel.source_id)!);
                    break;
                case 'compatible_with':
                    compatible.push(other);
                    break;
                case 'alternative_to':
                    alternatives.push(other);
                    break;
            }
        }

        return {
            accessories: accessories.filter(Boolean),
            compatible: compatible.filter(Boolean),
            alternatives: alternatives.filter(Boolean),
            all: rels,
        };
    }, [productId, indexes, products]);

    return { ...result, isLoading };
};

