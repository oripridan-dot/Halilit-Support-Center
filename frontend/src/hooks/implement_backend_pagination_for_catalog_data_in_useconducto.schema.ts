/**
 * Schema contract for useConductorCatalog paginated API
 * Source: specs/contracts — Backend Pagination Contract
 */

export const CATALOG_ENDPOINT = '/api/conductor/catalog';

export interface ConductorProduct {
    id: string;
    name: string;
    brand: string;
    brand_logo?: string;
    galaxy_id?: string;
    spectrum_id?: string;
    category?: string;
    price?: number;
    price_eilat?: number;
    tier?: string;
    image_url?: string;
    image_gallery?: string[];
    description?: string;
    description_short?: string;
    specs?: Record<string, unknown>;
    features?: string[];
    rating?: number;
    review_count?: number;
    pros?: string[];
    cons?: string[];
    quality_score?: number;
    data_status?: string;
    data_missing?: string[];
    halilit_url?: string;
    official_url?: string;
    sources?: string[];
    family_id?: string | null;
    variant_key?: string | null;
    relationship_ids?: string[];
}

export interface ConductorCatalogResponse {
    products: ConductorProduct[];
    total: number;
    brand_count?: number;
    indexes?: Record<string, unknown>;
}

export interface PaginatedCatalogResponse {
    products: ConductorProduct[];
    totalItems: number;
    totalPages: number;
    currentPage: number;
    pageSize: number;
}
