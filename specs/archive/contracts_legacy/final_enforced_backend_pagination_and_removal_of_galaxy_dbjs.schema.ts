```typescript
// Contract: Final Enforced Backend Pagination and Removal of galaxy_db.json (Performance Enhanced)

export const CATALOG_ENDPOINT = '/api/conductor/catalog';

export interface ConductorProduct {
  id: string;
  name: string;
  description: string;
  imageUrl: string;
  brand: string;
  category: string;
  price: string;
  inStock: boolean;
}

export interface PaginatedCatalogResponse {
  products: ConductorProduct[];
  totalItems: number;
  totalPages: number;
  currentPage: number;
  pageSize: number;
}

export interface CatalogParams {
  page?: number;
  pageSize?: number;
  searchQuery?: string;
  sortBy?: string;
  category?: string;
  brand?: string;
}
```