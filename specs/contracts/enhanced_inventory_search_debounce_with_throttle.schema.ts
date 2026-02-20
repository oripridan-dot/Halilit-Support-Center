```typescript
// Contract: Enhanced Inventory Search Debounce with Throttle

// Endpoint Path
const INVENTORY_SEARCH_ENDPOINT = "/api/inventory/search";

// Request Body Type (adjust as needed, example is provided)
interface InventorySearchRequest {
  searchQuery?: string;
  // other filter parameters as needed
  [key: string]: any;
}

// Response Type (adjust as needed, example is provided)
interface InventoryItem {
  id: string;
  name: string;
  description: string;
  sku: string;
  // other properties
  [key: string]: any;
}

interface InventorySearchResponse {
  items: InventoryItem[];
  totalCount: number;
}

// Shared Sub-types (if any, adjust as needed)
interface FilterParams {
    initialCfpFilter?: string;
    searchQuery?: string;
}
```