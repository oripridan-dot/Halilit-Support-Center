```typescript
// Contract: Implement Backend Pagination for Catalog Data

export const CATALOG_ENDPOINT = '/api/conductor/catalog';

export interface ConductorProduct {
  id: string;
  name: string;
  description: string;
  imageUrl: string;
  price: number;
  category: string;
}

export interface PaginatedCatalogResponse {
  products: ConductorProduct[];
  totalItems: number;
  totalPages: number;
  currentPage: number;
  pageSize: number;
}

export interface CatalogParams {
  page: number;
  pageSize: number;
}
```