// Contract: Implement Backend Pagination for Catalog Data in `useConductorCatalog`

export const CATALOG_ENDPOINT = '/api/conductor/catalog';

export interface ConductorProduct {
  [key: string]: any; // Define the actual properties of a ConductorProduct
}

export interface PaginatedCatalogResponse {
  products: ConductorProduct[];
  totalItems: number;
  totalPages: number;
  currentPage: number;
  pageSize: number;
}

export interface CatalogRequestParams {
  page?: number;
  pageSize?: number;
  searchQuery?: string;
  [key: string]: any; // Allows for other potential query params, such as sorting
}

export type CatalogResponse = PaginatedCatalogResponse;