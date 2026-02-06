import { useQuery } from "@tanstack/react-query";
import { GalaxyCatalog, GalaxyProduct } from "../types/galaxy-schema";

/**
 * useGalaxyData - TanStack Query powered data hook
 * 
 * Features:
 * - Automatic caching (5 minute stale time)
 * - Stale-While-Revalidate pattern (serves cache while checking for updates)
 * - Automatic refetch on window focus
 * - Automatic refetch on network reconnect
 * - Deduplication of parallel requests
 * 
 * Benefits:
 * - "Wrong data" issues solved by smart caching
 * - No race conditions between requests
 * - Performance perception improved (instant on cached)
 * - No manual loading/error state management
 */
export const useGalaxyData = () => {
  // Fetch function that loads the single source of truth
  const fetchGalaxyData = async (): Promise<GalaxyCatalog> => {
    const response = await fetch("/data/galaxy_db.json");
    if (!response.ok) {
      throw new Error(`Failed to load Galaxy DB: ${response.statusText}`);
    }
    const data = await response.json();
    console.log(`✅ Loaded ${Array.isArray(data) ? data.length : 0} products from Galaxy DB`);
    return data;
  };

  // Use TanStack Query for smart data fetching
  const { data, isLoading, error, isStale, refetch } = useQuery({
    queryKey: ["galaxy-catalog"],
    queryFn: fetchGalaxyData,
    // Stale-While-Revalidate: Keep data valid for 5 minutes
    staleTime: 5 * 60 * 1000,
    // Keep unused data in cache for 10 minutes
    gcTime: 10 * 60 * 1000,
    // Retry failed requests once
    retry: 1,
    // Refetch on window focus (user tabs back)
    refetchOnWindowFocus: true,
    // Refetch on network reconnect
    refetchOnReconnect: true,
  });

  // Convert array to GalaxyCatalog format for backward compatibility
  const catalog: GalaxyCatalog | null = Array.isArray(data)
    ? {
      products: data,
      categories: extractCategories(data),
    }
    : null;

  /**
   * Helper: Extract categories from products
   */
  function extractCategories(products: GalaxyProduct[]) {
    const cats: Record<string, number> = {};
    products.forEach(p => {
      const cat = (p.taxonomy?.canonical_category as string) || "Uncategorized";
      cats[cat] = (cats[cat] || 0) + 1;
    });
    return cats;
  }

  /**
   * Helper: Semantic search
   */
  const search = (query: string): GalaxyProduct[] => {
    if (!catalog) return [];
    const lowerQ = query.toLowerCase();
    return catalog.products.filter(p => {
      const searchableText = [
        p.product_name?.toLowerCase() ?? "",
        p.brand?.toLowerCase() ?? "",
        p.taxonomy?.canonical_category?.toLowerCase() ?? "",
        p.taxonomy?.keywords?.join(" ").toLowerCase() ?? "",
      ].join(" ");
      return searchableText.includes(lowerQ);
    });
  };

  /**
   * Manually trigger a refetch if needed
   */
  const refreshData = async () => {
    await refetch();
  };

  return {
    catalog,
    products: catalog?.products || [],
    categories: catalog?.categories || {},
    loading: isLoading,
    error: error ? (error as Error).message : null,
    isStale,
    search,
    refresh: refreshData,
  };
};
