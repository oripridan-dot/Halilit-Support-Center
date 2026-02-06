/**
 * useCategoryCatalog - TanStack Query powered category catalog hook
 * 
 * Follows STANDARDIZED COMMUNICATION PROTOCOL v1.0
 */
import { useQuery } from "@tanstack/react-query";
import type { Product } from "../types";
import { createAsyncResult, type AsyncResult } from "../lib/communicationProtocol";
import { catalogLoader } from "../lib/catalogLoader";
import { getConsolidatedProductCategory, productMatchesGalaxy, CONSOLIDATED_CATEGORIES } from "../lib/categoryConsolidator";

export interface CategoryCatalogState {
  products: Product[];
  availableFilters: string[];
}

/**
 * Hook to load category catalog with products and available filters
 * @param category - Category identifier to load
 * @returns AsyncResult with products and filters
 * 
 * @example
 * const { data, loading, error, isReady } = useCategoryCatalog(categoryId)
 * if (isReady) { products = data.products; filters = data.availableFilters; }
 */
export const useCategoryCatalog = (
  category: string | null,
): AsyncResult<CategoryCatalogState> => {
  // Use TanStack Query for smart data fetching
  const { data, isLoading, error, refetch } = useQuery({
    // Unique key per category
    queryKey: ["category-catalog", category],
    queryFn: async () => {
      if (!category) {
        return { products: [], availableFilters: [] };
      }

      try {
        // 1. Ensure Index is loaded
        await catalogLoader.loadIndex();

        // 2. Load all "Badged" Products from the 6 valid brands
        const allProducts = await catalogLoader.loadAllProducts();

        console.log(`[useCategoryCatalog] Loaded ${allProducts.length} total products`);

        if (allProducts.length === 0) {
          console.warn('[useCategoryCatalog] WARNING: No products loaded at all!');
          return { products: [], availableFilters: [] };
        }

        // 3. Filter by Galaxy/Tribe
        const filteredProducts = allProducts.filter(p => productMatchesGalaxy(p, category));

        console.log(`[useCategoryCatalog] Category: ${category}`);
        console.log(`[useCategoryCatalog] Filtered to ${filteredProducts.length} products for galaxy: ${category}`);

        if (filteredProducts.length === 0) {
          console.warn(`[useCategoryCatalog] WARNING: No products matched galaxy ${category}!`);
          if (allProducts.length > 0) {
            console.log('[useCategoryCatalog] Sample product for debugging:', {
              name: allProducts[0].name,
              brand_id: allProducts[0].brand_id,
              category: allProducts[0].category,
            });
          }
        }

        // 4. Generate Smart Filters based on actual content
        const galaxyDef = CONSOLIDATED_CATEGORIES.find(g => g.id === category);
        const filterSet = new Set<string>();

        filteredProducts.forEach(p => {
          const { spectrumId } = getConsolidatedProductCategory(p);
          const specDef = galaxyDef?.spectrum.find(s => s.id === spectrumId);
          if (specDef) {
            filterSet.add(specDef.label);
            if (!p.filter_tags) p.filter_tags = [];
            if (!p.filter_tags.includes(specDef.label)) p.filter_tags.push(specDef.label);
          }
        });

        const sortedFilters = galaxyDef
          ? galaxyDef.spectrum.map(s => s.label).filter(l => filterSet.has(l))
          : Array.from(filterSet).sort();

        return {
          products: filteredProducts,
          availableFilters: sortedFilters,
        };
      } catch (err) {
        console.error("[useCategoryCatalog] Error loading category:", err);
        // Return empty but valid result instead of throwing
        return { products: [], availableFilters: [] };
      }
    },
    // Only fetch if category is provided
    enabled: !!category,
    // Cache for reasonable time since we're loading all products
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
    retry: 1,
  });

  return createAsyncResult(
    data || { products: [], availableFilters: [] },
    isLoading,
    error instanceof Error ? error : null,
    refetch,
  );
};

