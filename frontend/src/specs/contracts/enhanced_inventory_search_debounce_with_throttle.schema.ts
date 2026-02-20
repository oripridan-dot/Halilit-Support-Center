/**
 * Contract schema: Enhanced Inventory Search with debounce + throttle.
 * Source of truth for InventorySearch.tsx and the backend /api/inventory/search endpoint.
 */

// ---------------------------------------------------------------------------
// Endpoint
// ---------------------------------------------------------------------------
export const INVENTORY_SEARCH_ENDPOINT = '/api/inventory/search' as const;

// ---------------------------------------------------------------------------
// Request / Response types
// ---------------------------------------------------------------------------
export interface InventorySearchRequest {
    /** Free-text search query */
    query: string;
    /** Maximum number of results (optional, default 50) */
    limit?: number;
}

export interface InventoryItem {
    /** Unique product SKU or internal ID */
    id: string;
    /** Human-readable product name */
    name: string;
    /** Short product description */
    description: string;
    /** Brand name */
    brand?: string;
    /** Hero image URL */
    image_url?: string;
    /** IL price in NIS */
    price_il?: number;
    /** Eilat price in NIS */
    price_eilat?: number;
}

export interface InventorySearchResponse {
    items: InventoryItem[];
    total: number;
    query: string;
}
