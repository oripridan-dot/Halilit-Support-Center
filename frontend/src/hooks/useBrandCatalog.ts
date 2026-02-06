/**
 * useBrandCatalog - TanStack Query powered brand catalog hook
 * 
 * Features:
 * - Automatic caching per brand
 * - Deduplication of parallel requests
 * - Automatic refetch on window focus
 * - Automatic refetch on network reconnect
 * 
 * Follows STANDARDIZED COMMUNICATION PROTOCOL v1.0
 */
import { useQuery } from "@tanstack/react-query";
import { catalogLoader, type BrandCatalog } from "../lib/catalogLoader";
import { createAsyncResult, type AsyncResult } from "../lib/communicationProtocol";

/**
 * Hook to load brand catalog by brand ID
 * @param brandId - Brand identifier (e.g., 'roland', 'boss', 'nord', 'moog')
 * @returns AsyncResult with catalog data, loading, and error states
 * 
 * @example
 * const { data: catalog, loading, error, isReady } = useBrandCatalog(brandId)
 */
export const useBrandCatalog = (brandId?: string): AsyncResult<BrandCatalog> => {
  // Use TanStack Query for smart caching and refetching
  const { data, isLoading, error, refetch } = useQuery({
    // Unique key per brand
    queryKey: ["brand-catalog", brandId],
    // Fetch function
    queryFn: async () => {
      if (!brandId) {
        throw new Error("Brand ID is required");
      }
      return await catalogLoader.loadBrand(brandId);
    },
    // Only fetch if brandId is provided
    enabled: !!brandId,
    // Stale-While-Revalidate pattern
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    // Automatic refetch behavior
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
    retry: 1,
  });

  return createAsyncResult(
    data || null,
    isLoading,
    error instanceof Error ? error : null,
    refetch
  );
};

export interface AllBrandCatalogsState {
  catalogs: Map<string, BrandCatalog>;
}

/**
 * Hook to load all brand catalogs
 * @returns AsyncResult with map of brand catalogs
 * 
 * @example
 * const { data, loading, error, isReady } = useAllBrandCatalogs()
 * if (isReady) { const catalog = data.catalogs.get('roland'); }
 */
export const useAllBrandCatalogs = (): AsyncResult<AllBrandCatalogsState> => {
  // Use TanStack Query for all brand catalogs
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["all-brand-catalogs"],
    queryFn: async () => {
      const index = await catalogLoader.loadIndex();
      const brandMap = new Map<string, BrandCatalog>();

      // Load catalogs in parallel using Promise.allSettled
      const catalogPromises = index.brands.map(async (brandEntry) => {
        try {
          const catalog = await catalogLoader.loadBrand(brandEntry.id);
          if (catalog) {
            return { id: brandEntry.id, catalog };
          }
        } catch (err) {
          // Log individual brand failures but continue
          console.warn(`Failed to load catalog for brand ${brandEntry.id}`, err);
        }
        return null;
      });

      const results = await Promise.allSettled(catalogPromises);
      results.forEach((result) => {
        if (result.status === "fulfilled" && result.value) {
          brandMap.set(result.value.id, result.value.catalog);
        }
      });

      return { catalogs: brandMap };
    },
    // Longer cache time since it's all brands
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 20 * 60 * 1000, // 20 minutes
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
    retry: 1,
  });

  return createAsyncResult(
    data || { catalogs: new Map() },
    isLoading,
    error instanceof Error ? error : null,
    refetch
  );
};
