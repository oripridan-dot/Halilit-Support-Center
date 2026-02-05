/**
 * useCategoryCatalog - Load products and filters for a category
 * 
 * Follows STANDARDIZED COMMUNICATION PROTOCOL v1.0
 */
import { useCallback, useEffect, useState } from "react";
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
  const [products, setProducts] = useState<Product[]>([]);
  const [availableFilters, setAvailableFilters] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchCategory = useCallback(async () => {
    setLoading(true);
    setError(null);

    if (!category) {
      console.warn('[useCategoryCatalog] Category is null, clearing products');
      setProducts([]);
      setAvailableFilters([]);
      setLoading(false);
      return;
    }

    try {
      // 1. Ensure Index is loaded
      await catalogLoader.loadIndex();

      // 2. Load all "Badged" Products from the 6 valid brands
      const allProducts = await catalogLoader.loadAllProducts();

      console.log(`[useCategoryCatalog] Loaded ${allProducts.length} total products`);

      if (allProducts.length === 0) {
        console.warn('[useCategoryCatalog] WARNING: No products loaded at all!');
      }

      // 3. Filter by Galaxy/Tribe
      // The 'category' param here corresponds to the 'Galaxy ID' (e.g. 'guitars-bass', 'keys-production')
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
      // Find the Galaxy Definition to get the Spectrum list (order matters)
      const galaxyDef = CONSOLIDATED_CATEGORIES.find(g => g.id === category);

      const filterSet = new Set<string>();

      filteredProducts.forEach(p => {
        const { spectrumId } = getConsolidatedProductCategory(p);
        // Find the label for this spectrumId
        const specDef = galaxyDef?.spectrum.find(s => s.id === spectrumId);
        if (specDef) {
          filterSet.add(specDef.label);
          // Inject this label as a "filter_tags" tag so SpectrumModule's 1176 engine can use it
          if (!p.filter_tags) p.filter_tags = [];
          if (!p.filter_tags.includes(specDef.label)) p.filter_tags.push(specDef.label);
        }
      });

      // Sort filters based on Galaxy definition order
      const sortedFilters = galaxyDef
        ? galaxyDef.spectrum.map(s => s.label).filter(l => filterSet.has(l))
        : Array.from(filterSet).sort();

      setProducts(filteredProducts);
      setAvailableFilters(sortedFilters);
      setError(null);
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Unknown error loading category");
      setError(error);
      setProducts([]);
      setAvailableFilters([]);
    } finally {
      setLoading(false);
    }
  }, [category]);

  useEffect(() => {
    fetchCategory();
  }, [category, fetchCategory]);

  return createAsyncResult(
    {
      products,
      availableFilters,
    },
    loading,
    error,
    fetchCategory,
  );
};

