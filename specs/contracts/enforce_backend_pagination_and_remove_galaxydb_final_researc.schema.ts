```typescript
// Contract: Enforce Backend Pagination and Remove GalaxyDB (Final + Research Animation + Graceful Error Handling + Polished Animation + Stock and CfP Sorting + Skeleton Placeholder)

export const CONDUCTOR_CATALOG_ENDPOINT = '/api/conductor/catalog';

export interface ConductorProduct {
  id: string;
  name: string;
  description: string;
  imageUrl: string;
  brand: string;
  category: string;
  price: number;
  inStock: boolean;
  cfp: boolean;
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
```