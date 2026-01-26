/**
 * Instant Search - v3.9
 * Client-side fuzzy search using Fuse.js
 * Decoupled from full catalog - uses lightweight search_index.json
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

class InstantSearch {
  private fuse: Fuse<SearchItem> | null = null;
  private items: SearchItem[] = [];
  private initialized: boolean = false;

  /**
   * Initialize search engine (call once on app load)
   */
  async initialize(): Promise<void> {
    if (this.initialized) {
      return;
    }

    try {
      // Load optimized search index with cache busting
      const response = await fetch(`/data/search_index.json?v=${Date.now()}`);
      if (!response.ok)
        throw new Error(`Failed to load search index: ${response.status}`);
      this.items = await response.json();

      // Configure Fuse.js for fuzzy search
      this.fuse = new Fuse(this.items, {
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

      this.initialized = true;
      console.log(
        `[InstantSearch] Initialized with ${this.items.length} items`,
      );
    } catch (error) {
      console.error("[InstantSearch] Initialization failed:", error);
    }
  }

  /**
   * Search products (instant, <50ms target)
   */
  search(query: string, options?: SearchOptions): SearchItem[] {
    if (!this.fuse || !this.initialized) {
      return [];
    }

    // If no query, return filtered products (empty query = partial list)
    if (!query || query.trim().length < 2) {
      // Logic: If plain list requested, apply filters to raw list
      // Note: This might return too many results, relying on limit
      let results = [...this.items];
      results = this.applyFilters(results, options);
      return results.slice(0, options?.limit || 20);
    }

    // Perform fuzzy search
    const fuseResults = this.fuse.search(query, {
      limit: options?.limit || 20,
    });

    let results = fuseResults.map((result) => result.item);

    // Apply filters
    results = this.applyFilters(results, options);

    return results;
  }

  /**
   * Apply filters to results
   */
  private applyFilters(
    results: SearchItem[],
    options?: SearchOptions,
  ): SearchItem[] {
    let filtered = results;

    if (options?.brand) {
      filtered = filtered.filter((p) => p.brand === options.brand);
    }

    if (options?.category) {
      filtered = filtered.filter((p) => p.category === options.category);
    }

    return filtered;
  }
}

export const instantSearch = new InstantSearch();
