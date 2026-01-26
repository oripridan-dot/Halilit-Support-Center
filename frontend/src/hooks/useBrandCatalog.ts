/**
 * useBrandCatalog - Load and cache brand product catalog
 * Fetches pre-built JSON catalog for a specific brand
 */
import { useEffect, useState } from "react";
import { catalogLoader, type BrandCatalog } from "../lib/catalogLoader";

/**
 * Hook to load brand catalog by brand ID
 * @param brandId - Brand identifier (e.g., 'roland', 'boss', 'nord', 'moog')
 * @returns BrandCatalog with products, or null if loading/error
 */
export const useBrandCatalog = (brandId?: string): BrandCatalog | null => {
  const [catalog, setCatalog] = useState<BrandCatalog | null>(null);

  useEffect(() => {
    let isMounted = true;

    const loadCatalog = async () => {
      if (!brandId) {
        if (isMounted) setCatalog(null);
        return;
      }

      // SWR: 1. Try local storage immediately (Stale)
      const storageKey = `brand_catalog_${brandId}`;
      const cached = localStorage.getItem(storageKey);

      if (isMounted && cached) {
        try {
          setCatalog(JSON.parse(cached));
        } catch {
          // ignore
        }
      }

      try {
        // SWR: 2. Fetch fresh data (Revalidate)
        const data = await catalogLoader.loadBrand(brandId);

        if (isMounted) {
          setCatalog(data);
          // Persist fresh data
          try {
            localStorage.setItem(storageKey, JSON.stringify(data));
          } catch {
            // ignore
          }
        }
      } catch {
        // Only reset if we don't have cached data and error is critical?
        // Actually if fetch fails, we keep cached data usually.
        // But if no cache, ensure null.
        if (isMounted && !cached) {
          setCatalog(null);
        }
      }
    };

    loadCatalog();

    return () => {
      isMounted = false;
    };
  }, [brandId]);

  return catalog;
};

/**
 * Hook to load all brand catalogs
 * @returns Map of brand ID to catalog
 */
export const useAllBrandCatalogs = () => {
  const [catalogs, setCatalogs] = useState<Map<string, BrandCatalog>>(
    new Map(),
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadAllCatalogs = async () => {
      setLoading(true);
      setError(null);
      try {
        const index = await catalogLoader.loadIndex();
        const brandMap = new Map<string, BrandCatalog>();

        for (const brandEntry of index.brands) {
          try {
            const catalog = await catalogLoader.loadBrand(brandEntry.id);
            if (catalog) {
              brandMap.set(brandEntry.id, catalog);
            }
          } catch {
            // ignore
          }
        }

        setCatalogs(brandMap);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to load catalogs";
        setError(message);
      } finally {
        setLoading(false);
      }
    };

    loadAllCatalogs();
  }, []);

  return { catalogs, loading, error };
};
