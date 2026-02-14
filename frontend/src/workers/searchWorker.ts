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
 * Initialize search engine with items from search_index.json or search_index_min.json.
 * If the file is missing or returns HTML (e.g. SPA fallback), uses empty array so the app does not crash.
 */
async function initializeSearch(): Promise<void> {
  if (initialized) return;

  const urls = [
    `/data/search_index_min.json?v=${Date.now()}`,
    `/data/search_index.json?v=${Date.now()}`,
  ];

  for (const url of urls) {
    try {
      const response = await fetch(url);
      if (!response.ok) continue;

      const contentType = response.headers.get("content-type") || "";
      if (!contentType.includes("application/json")) continue;

      const text = await response.text();
      if (!text.trim() || text.trimStart().startsWith("<")) continue;

      const parsed = JSON.parse(text) as SearchItem[];
      items = Array.isArray(parsed) ? parsed : [];
      break;
    } catch {
      continue;
    }
  }

  fuse = new Fuse(items, {
    keys: [
      { name: "label", weight: 2.0 },
      { name: "brand_name", weight: 1.5 },
      { name: "keywords", weight: 1.2 },
      { name: "category", weight: 1.0 },
      { name: "subcategory", weight: 0.8 },
      { name: "description", weight: 0.5 },
    ],
    threshold: 0.3,
    includeScore: true,
    useExtendedSearch: true,
    minMatchCharLength: 2,
    ignoreLocation: true,
  });

  initialized = true;
  if (import.meta.env?.DEV && items.length === 0) {
    console.log("[SearchWorker] Initialized with 0 items (no search index or empty catalog)");
  } else {
    console.log(`[SearchWorker] Initialized with ${items.length} items`);
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
