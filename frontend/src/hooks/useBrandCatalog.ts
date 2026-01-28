/**
 * useBrandCatalog - Load and cache brand product catalog
 * Fetches pre-built JSON catalog for a specific brand
 * 
 * Follows STANDARDIZED COMMUNICATION PROTOCOL v1.0
 */
import { useCallback, useEffect, useState } from "react";
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
  const [catalog, setCatalog] = useState<BrandCatalog | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const loadCatalog = useCallback(async () => {
    setLoading(true);
    setError(null);

    if (!brandId) {
      setCatalog(null);
      setLoading(false);
      return;
    }

    try {
      // SWR: 1. Try local storage immediately (Stale)
      const storageKey = `brand_catalog_${brandId}`;
      const cached = localStorage.getItem(storageKey);

      if (cached) {
        try {
          const parsed = JSON.parse(cached) as BrandCatalog;
          setCatalog(parsed);
        } catch {
          // Corrupted cache, will be replaced by fresh data
        }
      }

      // SWR: 2. Fetch fresh data (Revalidate)
      const data = await catalogLoader.loadBrand(brandId);
      setCatalog(data);
      setError(null);

      // Persist fresh data
      try {
        localStorage.setItem(storageKey, JSON.stringify(data));
      } catch {
        // Storage full or disabled, continue without caching
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Failed to load brand catalog");
      setError(error);
      // Keep cached data if available
    } finally {
      setLoading(false);
    }
  }, [brandId]);

  // Initial load effect
  useEffect(() => {
    loadCatalog();
  }, [brandId, loadCatalog]);

  return createAsyncResult(catalog, loading, error, loadCatalog);
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
  const [catalogs, setCatalogs] = useState<Map<string, BrandCatalog>>(
    new Map(),
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const loadAllCatalogs = useCallback(async () => {
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
        } catch (err) {
          // Log individual brand failures but continue
          console.warn(`Failed to load catalog for brand ${brandEntry.id}`, err);
        }
      }

      setCatalogs(brandMap);
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Failed to load all catalogs");
      setError(error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAllCatalogs();
  }, [loadAllCatalogs]);

  return createAsyncResult({ catalogs }, loading, error, loadAllCatalogs);
};
