```typescript
// Contract: Enforce Backend Pagination and Remove GalaxyDB (Final)

// Endpoint path
export const CATALOG_ENDPOINT = '/api/conductor/catalog';

// Shared types
export interface ConductorProduct {
  id: string;
  name: string;
  description: string;
  imageUrl: string;
  category: string;
  brand: string;
  price: number;
  // Add other properties as needed
}

// Request body type (if any - based on the spec, it seems to be query params)
// export interface CatalogRequestParams { } // No request body

// Response type
export interface PaginatedCatalogResponse {
  products: ConductorProduct[];
  totalItems: number;
  totalPages: number;
  currentPage: number;
  pageSize: number;
}
```