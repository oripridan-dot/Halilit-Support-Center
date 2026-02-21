// Contract: Implement Backend Pagination for `useConductorCatalog`

// Endpoint path
export const CONDUCTOR_CATALOG_ENDPOINT = "/api/conductor/catalog";

// Shared types
export interface ConductorProduct {
    id: string;
    name: string;
    description: string;
    imageUrl: string;
    price: number;
    category: string;
    brand: string;
    rating: number;
}

// Response type
export interface PaginatedCatalogResponse {
    products: ConductorProduct[];
    totalItems: number;
    totalPages: number;
    currentPage: number;
    pageSize: number;
}

// Request body - GET requests don't typically have bodies, define query params instead
export interface ConductorCatalogParams {
    page?: number;
    pageSize?: number;
    searchQuery?: string;
    sortBy?: string;
    category?: string;
    brand?: string;
}