```typescript
// Contract: Implement Backend Pagination for useConductorCatalog (Final + Skeleton Loading)

// Endpoint path
export const CATALOG_ENDPOINT = "/api/conductor/catalog";

// Shared types
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

// Request body type (if any - this endpoint uses query parameters)
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