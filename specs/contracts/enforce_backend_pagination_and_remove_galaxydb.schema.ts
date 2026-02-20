```typescript
// Contract: Enforce Backend Pagination and Remove GalaxyDB

// Shared Types
interface ConductorProduct {
  id: string;
  name: string;
  description: string;
  imageUrl: string;
  category: string;
  brand: string;
  price: number;
  // Add other product properties as needed
}

// Endpoint Path
export const CONDUCTOR_CATALOG_ENDPOINT = '/api/conductor/catalog';

// Request Body (None for this endpoint, using query parameters)
// type ConductorCatalogRequest = {};

// Response Type
export interface PaginatedCatalogResponse {
  products: ConductorProduct[];
  totalItems: number;
  totalPages: number;
  currentPage: number;
  pageSize: number;
}
```