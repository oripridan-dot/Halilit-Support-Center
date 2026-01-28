/**
 * useCategoryProducts - Load products filtered by category/subcategory
 * Fetches all products and filters them based on consolidated category logic
 * 
 * Follows STANDARDIZED COMMUNICATION PROTOCOL v1.0
 */
import { useCallback, useEffect, useState } from "react";
import { catalogLoader } from "../lib/catalogLoader";
import { getConsolidatedProductCategory } from "../lib/categoryConsolidator";
import { createAsyncResult, type AsyncResult } from "../lib/communicationProtocol";
import type { Product } from "../types";

/**
 * Hook to load and filter products by subcategory
 * @param subcategoryId - The spectrum subcategory ID to filter by
 * @returns AsyncResult with filtered products, loading, and error states
 * 
 * @example
 * const { data: products, loading, error, isReady } = useCategoryProducts(subcategoryId)
 */
export const useCategoryProducts = (
  subcategoryId: string | null
): AsyncResult<Product[]> => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const loadProducts = useCallback(async () => {
    setLoading(true);
    setError(null);

    if (!subcategoryId) {
      setProducts([]);
      setLoading(false);
      return;
    }

    try {
      // 1. Efficiently load ALL products (leveraging catalogLoader cache)
      const allProducts = await catalogLoader.loadAllProducts();

      // 2. Filter using the Single Source of Truth Logic
      // This ensures what you see in the "Galaxy" view matches search/filtering elsewhere
      const filtered = allProducts.filter((p) => {
        const { spectrumId } = getConsolidatedProductCategory(p);
        return spectrumId === subcategoryId;
      });

      setProducts(filtered);
      setError(null);
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Failed to load category products");
      setError(error);
      setProducts([]);
    } finally {
      setLoading(false);
    }
  }, [subcategoryId]);

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

  const retry = useCallback(() => {
    loadProducts();
  }, [loadProducts]);

  return createAsyncResult(products, loading, error, retry);
};
