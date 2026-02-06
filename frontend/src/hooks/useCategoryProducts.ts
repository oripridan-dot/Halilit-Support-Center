/**
 * useCategoryProducts - TanStack Query powered category products hook
 * 
 * Follows STANDARDIZED COMMUNICATION PROTOCOL v1.0
 */
import { useQuery } from "@tanstack/react-query";
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
  // Use TanStack Query for smart data fetching
  const { data, isLoading, error, refetch } = useQuery({
    // Unique key per subcategory
    queryKey: ["category-products", subcategoryId],
    queryFn: async () => {
      if (!subcategoryId) {
        throw new Error("Subcategory ID is required");
      }

      // 1. Efficiently load ALL products (leveraging catalogLoader cache)
      const allProducts = await catalogLoader.loadAllProducts();

      // 2. Filter using the Single Source of Truth Logic
      const filtered = allProducts.filter((p) => {
        const { spectrumId } = getConsolidatedProductCategory(p);
        return spectrumId === subcategoryId;
      });

      console.log(`[useCategoryProducts] Filtered ${allProducts.length} down to ${filtered.length} for subcategory ${subcategoryId}`);
      return filtered;
    },
    // Only fetch if subcategoryId is provided
    enabled: !!subcategoryId,
    // Cache for reasonable time
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
    retry: 1,
  });

  return createAsyncResult(
    data || [],
    isLoading,
    error instanceof Error ? error : null,
    refetch
  );
};
