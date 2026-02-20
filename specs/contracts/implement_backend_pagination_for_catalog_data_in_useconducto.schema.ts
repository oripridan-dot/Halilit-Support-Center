// Contract: Implement Backend Pagination for Catalog Data in `useConductorCatalog`

// Endpoint
export const CATALOG_ENDPOINT = "/api/conductor/catalog";

// Request (Query Parameters)
export interface CatalogRequestParams {
    page?: number;
    pageSize?: number;
    searchQuery?: string;
    sortBy?: string;
    category?: string;
    brand?: string;
}

// Shared Types
export interface ConductorProduct {
    id: string;
    name: string;
    description: string;
    imageUrl: string;
    brand: string;
    category: string;
    price: number;
}

// Response
export interface PaginatedCatalogResponse {
    products: ConductorProduct[];
    totalItems: number;
    totalPages: number;
    currentPage: number;
    pageSize: number;
}