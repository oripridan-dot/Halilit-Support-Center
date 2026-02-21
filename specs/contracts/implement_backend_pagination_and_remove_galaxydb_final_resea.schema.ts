// Contract: Implement Backend Pagination and Remove GalaxyDB (Final + Research Animation)

// Endpoint path
export const CATALOG_ENDPOINT = '/api/conductor/catalog';

// Request body type (query parameters)
export interface CatalogRequestParams {
  page?: number;
  pageSize?: number;
  searchQuery?: string;
  sortBy?: string;
  category?: string;
  brand?: string;
}

// Shared sub-types
export interface ConductorProduct {
  id: string;
  name: string;
  description: string;
  imageUrl: string;
  category: string;
  brand: string;
  price: number;
}

// Response type
export interface PaginatedCatalogResponse {
  products: ConductorProduct[];
  totalItems: number;
  totalPages: number;
  currentPage: number;
  pageSize: number;
}