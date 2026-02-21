```typescript
// Contract: Enforce Backend Pagination and Remove GalaxyDB (Final + Research Animation + Graceful Error Handling + Polished Animation + Stock and CfP Sorting)

export const CATALOG_ENDPOINT = '/api/conductor/catalog';

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
  // Add other properties as needed based on your actual data structure
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
  sortBy?: string;
  category?: string;
  brand?: string;
}
```