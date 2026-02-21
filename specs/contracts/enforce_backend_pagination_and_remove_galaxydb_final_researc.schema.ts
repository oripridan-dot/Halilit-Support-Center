```typescript
// Contract: Enforce Backend Pagination and Remove GalaxyDB (Final + Research Animation + Graceful Error Handling)

// Endpoint path
export const CATALOG_ENDPOINT = '/api/conductor/catalog';

// Shared sub-types
export interface ConductorProduct {
  id: string;
  name: string;
  description: string;
  imageUrl: string;
  category: string;
  brand: string;
  price: number;
  // Add other product properties as needed
}

// Request body type (if any) - In this case, the request uses query parameters, so no body is defined.
export interface CatalogRequestParams {
  page?: number;
  pageSize?: number;
  searchQuery?: string;
  sortBy?: string;
  category?: string;
  brand?: string;
}

// Response type
export interface PaginatedCatalogResponse {
  products: ConductorProduct[];
  totalItems: number;
  totalPages: number;
  currentPage: number;
  pageSize: number;
}
```