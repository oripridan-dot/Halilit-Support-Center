import { useEffect, useState } from "react";
import type { SearchItem, SearchOptions } from "../lib/instantSearch";
import { instantSearch } from "../lib/instantSearch";

export function useRealtimeSearch(query: string, options?: SearchOptions) {
  const [results, setResults] = useState<SearchItem[]>([]);
  const [isReady, setIsReady] = useState(false);

  // Initialize engine once
  useEffect(() => {
    instantSearch.initialize().then(() => setIsReady(true));
  }, []);

  // Compute results
  useEffect(() => {
    if (!isReady) return;

    // Debounce search slightly to avoid UI flicker
    const timeoutId = setTimeout(() => {
      const hits = instantSearch.search(query, options);
      setResults(hits);
    }, 150);

    return () => clearTimeout(timeoutId);
  }, [query, isReady, options?.brand, options?.category]);

  return {
    results,
    isReady,
  };
}
