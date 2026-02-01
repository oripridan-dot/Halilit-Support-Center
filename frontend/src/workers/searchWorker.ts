/**
 * Search Worker - Handles all search operations on a separate thread
 * This keeps the main UI thread responsive during large searches
 */

import Fuse from "fuse.js";

export interface SearchItem {
  id: string;
  label: string;
  brand: string;
  brand_name: string;
  category: string;
  subcategory?: string;
  keywords: string[];
  description: string;
  image_url?: string;
}

export interface SearchOptions {
  brand?: string;
  category?: string;
  limit?: number;
}

interface SearchRequest {
  type: "initialize" | "search" | "getStatus";
  query?: string;
  options?: SearchOptions;
}

interface SearchResponse {
  type: "initialized" | "searchResults" | "error" | "status";
  results?: SearchItem[];
  error?: string;
  itemCount?: number;
  initialized?: boolean;
}

let fuse: Fuse<SearchItem> | null = null;
let items: SearchItem[] = [];
let initialized = false;

/**
 * Initialize search engine with items from search_index.json
 */
async function initializeSearch(): Promise<void> {
  if (initialized) return;

  try {
    const response = await fetch(`/data/search_index.json?v=${Date.now()}`);
    if (!response.ok) {
      throw new Error(`Failed to load search index: ${response.status}`);
    }

    items = (await response.json()) as SearchItem[];

    // Configure Fuse.js for fuzzy search
    fuse = new Fuse(items, {
      keys: [
        { name: "label", weight: 2.0 }, // Product name
        { name: "brand_name", weight: 1.5 }, // Brand name
        { name: "keywords", weight: 1.2 }, // Keywords
        { name: "category", weight: 1.0 }, // Category
        { name: "subcategory", weight: 0.8 }, // Subcategory
        { name: "description", weight: 0.5 }, // Description
      ],
      threshold: 0.3, // 70% match required
      includeScore: true,
      useExtendedSearch: true,
      minMatchCharLength: 2,
      ignoreLocation: true,
    });

    initialized = true;
    console.log(`[SearchWorker] Initialized with ${items.length} items`);
  } catch (error) {
    console.error("[SearchWorker] Initialization failed:", error);
    throw error;
  }
}

/**
 * Perform search operation
 */
function performSearch(
  query: string,
  options?: SearchOptions
): SearchItem[] {
  if (!fuse || !initialized) {
    return [];
  }

  // If no query, return filtered products
  if (!query || query.trim().length < 2) {
    let results = [...items];
    results = applyFilters(results, options);
    return results.slice(0, options?.limit || 20);
  }

  // Perform fuzzy search
  const fuseResults = fuse.search(query, {
    limit: options?.limit || 20,
  });

  let results = fuseResults.map((result) => result.item);

  // Apply filters
  results = applyFilters(results, options);

  return results;
}

/**
 * Apply brand and category filters to results
 */
function applyFilters(
  results: SearchItem[],
  options?: SearchOptions
): SearchItem[] {
  if (!options) return results;

  if (options.brand) {
    results = results.filter(
      (item) =>
        item.brand.toLowerCase() === options.brand!.toLowerCase() ||
        item.brand_name.toLowerCase() === options.brand!.toLowerCase()
    );
  }

  if (options.category) {
    results = results.filter(
      (item) =>
        item.category.toLowerCase() === options.category!.toLowerCase()
    );
  }

  return results;
}

/**
 * Handle messages from main thread
 */
self.onmessage = async (event: MessageEvent<SearchRequest>) => {
  const { type, query, options } = event.data;

  try {
    switch (type) {
      case "initialize":
        await initializeSearch();
        const response: SearchResponse = {
          type: "initialized",
          itemCount: items.length,
          initialized: true,
        };
        self.postMessage(response);
        break;

      case "search":
        if (!initialized) {
          await initializeSearch();
        }
        const results = performSearch(query || "", options);
        self.postMessage({
          type: "searchResults",
          results,
        } as SearchResponse);
        break;

      case "getStatus":
        self.postMessage({
          type: "status",
          initialized,
          itemCount: items.length,
        } as SearchResponse);
        break;

      default:
        self.postMessage({
          type: "error",
          error: `Unknown message type: ${type}`,
        } as SearchResponse);
    }
  } catch (error) {
    self.postMessage({
      type: "error",
      error: error instanceof Error ? error.message : "Unknown error",
    } as SearchResponse);
  }
};
