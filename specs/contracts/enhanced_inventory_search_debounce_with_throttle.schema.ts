```typescript
// Contract: Enhanced Inventory Search Debounce with Throttle

export const INVENTORY_SEARCH_ENDPOINT = '/api/inventory/search';

export interface InventorySearchRequest {
  searchQuery?: string;
}

export interface InventoryItem {
  id: string;
  name: string;
  description: string;
  sku: string;
  // ... other properties
}

export interface InventorySearchResponse {
  items: InventoryItem[];
  totalCount: number;
}
```