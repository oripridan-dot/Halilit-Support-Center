```typescript
// Contract: Enforce Backend Pagination and Remove GalaxyDB

export const CONDUCTOR_CATALOG_ENDPOINT = '/api/conductor/catalog';

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

export interface PaginatedCatalogResponse {
  products: ConductorProduct[];
  totalItems: number;
  totalPages: number;
  currentPage: number;
  pageSize: number;
}

export interface ConductorCatalogParams {
    page?: number;
    pageSize?: number;
    searchQuery?: string;
    sortBy?: string;
    category?: string;
    brand?: string;
}

export interface ConductorCatalogResponse extends PaginatedCatalogResponse {}
```