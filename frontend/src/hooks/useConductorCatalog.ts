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
import {
    CATALOG_ENDPOINT,
    ConductorProduct,
    ConductorCatalogResponse,
    PaginatedCatalogResponse,
} from './../specs/contracts/implement_backend_pagination_for_catalog_data_in_useconducto.schema';

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
    sources_verified?: string[];
    is_triple_checked?: boolean;
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

interface UseConductorCatalogParams {
    page?: number;
    pageSize?: number;
    searchQuery?: string;
    sortBy?: string;
}

const useConductorCatalog = ({
    page = 1,
    pageSize = 25,
    searchQuery = '',
    sortBy = '',
}: UseConductorCatalogParams): ConductorCatalogResponse => {
    const { data, isLoading, error, refetch } = useQuery<PaginatedCatalogResponse, any>(
        ['conductorCatalog', page, pageSize, searchQuery, sortBy],
        async () => {
            const url = new URL(CATALOG_ENDPOINT, window.location.origin);
            url.searchParams.append('page', String(page));
            url.searchParams.append('pageSize', String(pageSize));
            url.searchParams.append('searchQuery', searchQuery);
            url.searchParams.append('sortBy', sortBy);
            const response = await fetch(url.toString());
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data: PaginatedCatalogResponse = await response.json();
            return data;
        },
    );

    const products: ConductorProduct[] = useMemo(() => data?.products || [], [data?.products]);
    const totalItems = data?.totalItems || 0;
    const totalPages = data?.totalPages || 0;
    const currentPage = data?.currentPage || 1;
    const currentPageSize = data?.pageSize || 25;

    return {
        data: {
            products,
            totalItems,
            totalPages,
            currentPage,
            pageSize: currentPageSize,
        },
        isLoading,
        error,
        refetch,
    };
};

export default useConductorCatalog;