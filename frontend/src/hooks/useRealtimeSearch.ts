/**
 * useRealtimeSearch - Real-time instant search across product catalog
 * 
 * Follows STANDARDIZED COMMUNICATION PROTOCOL v1.0
 * Returns AsyncResult pattern for consistent error handling and loading states
 */
import { useCallback, useEffect, useState } from "react";
import type { SearchItem, SearchOptions } from "../lib/instantSearch";
import { instantSearch } from "../lib/instantSearch";
import { createAsyncResult, type AsyncResult } from "../lib/communicationProtocol";

/**
 * Hook to perform real-time search across the catalog
 * @param query - Search query string
 * @param options - Search options (brand filter, category filter, etc.)
 * @returns AsyncResult with search results, loading, and error states
 * 
 * @example
 * const { data: results, loading, error, isReady } = useRealtimeSearch(searchQuery, { brand: 'roland' })
 */
export function useRealtimeSearch(
  query: string,
  options?: SearchOptions
): AsyncResult<SearchItem[]> {
  const [results, setResults] = useState<SearchItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Initialize search engine once
  useEffect(() => {
    const initEngine = async () => {
      try {
        await instantSearch.initialize();
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err : new Error("Failed to initialize search"));
        setLoading(false);
      }
    };

    initEngine();
  }, []);

  const performSearch = useCallback(() => {
    if (loading || error) return;

    try {
      // Debounce search slightly to avoid UI flicker
      const timeoutId = setTimeout(() => {
        const hits = instantSearch.search(query, options);
        setResults(hits);
        setError(null);
      }, 150);

      return () => clearTimeout(timeoutId);
    } catch (err) {
      setError(err instanceof Error ? err : new Error("Search failed"));
      setResults([]);
    }
  }, [query, loading, error, options?.brand, options?.category]);

  // Execute search when query or options change
  useEffect(() => {
    const cleanup = performSearch();
    return cleanup;
  }, [performSearch]);

  const retry = useCallback(() => {
    setError(null);
    performSearch();
  }, [performSearch]);

  return createAsyncResult(results, loading, error, retry);
}
