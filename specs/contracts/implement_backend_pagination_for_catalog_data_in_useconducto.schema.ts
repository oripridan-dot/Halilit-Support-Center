```typescript
// Contract: Implement Backend Pagination for Catalog Data in `useConductorCatalog`

// Endpoint path
export const CATALOG_ENDPOINT = '/api/conductor/catalog';

// Shared types
export interface ConductorProduct {
  [key: string]: any; // represents an arbitrary product shape.  The backend defines the shape.
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