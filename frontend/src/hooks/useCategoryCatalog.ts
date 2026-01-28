/**
 * useCategoryCatalog - Load products and filters for a category
 * 
 * Follows STANDARDIZED COMMUNICATION PROTOCOL v1.0
 */
import { useCallback, useEffect, useState } from "react";
import type { Product, CategoryPayload } from "../types";
import { createAsyncResult, type AsyncResult } from "../lib/communicationProtocol";

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
      setProducts([]);
      setAvailableFilters([]);
      setLoading(false);
      return;
    }

    try {
      const catId = category.toLowerCase();
      const res = await fetch(`/data/${catId}.json`);

      if (!res.ok) {
        throw new Error(`Failed to load category: ${res.statusText}`);
      }

      const data = (await res.json()) as CategoryPayload;
      setProducts(data.products || []);
      setAvailableFilters(data.metadata?.available_filters || []);
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

