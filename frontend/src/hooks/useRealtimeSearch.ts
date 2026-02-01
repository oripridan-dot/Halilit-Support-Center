/**
 * useRealtimeSearch - Real-time instant search across product catalog
 * 
 * ⚡ OPTIMIZED: Uses Web Worker to offload search processing
 * Follows STANDARDIZED COMMUNICATION PROTOCOL v1.0
 * Returns AsyncResult pattern for consistent error handling and loading states
 */
import { useCallback, useEffect, useRef, useState } from "react";
import type { SearchItem, SearchOptions } from "../lib/instantSearch";
import { createAsyncResult, type AsyncResult } from "../lib/communicationProtocol";

// Reusable worker instance (shared across all hook instances)
let searchWorker: Worker | null = null;
let workerInitialized = false;
let workerInitPromise: Promise<void> | null = null;

function getSearchWorker(): Worker {
  if (!searchWorker) {
    searchWorker = new Worker(
      new URL("../workers/searchWorker.ts", import.meta.url),
      { type: "module" }
    );
  }
  return searchWorker;
}

function initializeWorker(): Promise<void> {
  if (workerInitialized) {
    return Promise.resolve();
  }

  if (workerInitPromise) {
    return workerInitPromise;
  }

  workerInitPromise = new Promise((resolve, reject) => {
    const worker = getSearchWorker();
    const timeout = setTimeout(() => {
      reject(new Error("Worker initialization timeout"));
    }, 5000);

    const messageHandler = (event: MessageEvent) => {
      if (event.data.type === "initialized") {
        clearTimeout(timeout);
        worker.removeEventListener("message", messageHandler);
        worker.removeEventListener("error", errorHandler);
        workerInitialized = true;
        resolve();
      }
    };

    const errorHandler = (error: ErrorEvent) => {
      clearTimeout(timeout);
      worker.removeEventListener("message", messageHandler);
      worker.removeEventListener("error", errorHandler);
      reject(error.error || new Error("Worker initialization failed"));
    };

    worker.addEventListener("message", messageHandler);
    worker.addEventListener("error", errorHandler);
    worker.postMessage({ type: "initialize" });
  });

  return workerInitPromise;
}

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
  const debounceTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const messageHandlerRef = useRef<((event: MessageEvent) => void) | null>(null);

  // Initialize worker once
  useEffect(() => {
    const init = async () => {
      try {
        await initializeWorker();
        setLoading(false);
      } catch (err) {
        setError(
          err instanceof Error
            ? err
            : new Error("Failed to initialize search worker")
        );
        setLoading(false);
      }
    };

    init();
  }, []);

  const performSearch = useCallback(() => {
    if (loading || error || !workerInitialized) return;

    // Clear previous debounce timeout
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }

    // Debounce search slightly to avoid excessive worker messages
    debounceTimeoutRef.current = setTimeout(() => {
      try {
        const worker = getSearchWorker();

        // Remove old message handler if it exists
        if (messageHandlerRef.current) {
          worker.removeEventListener("message", messageHandlerRef.current);
        }

        // Create new message handler for this search
        const newHandler = (event: MessageEvent) => {
          if (event.data.type === "searchResults") {
            setResults(event.data.results || []);
            setError(null);
          } else if (event.data.type === "error") {
            setError(new Error(event.data.error || "Search failed"));
            setResults([]);
          }
        };

        messageHandlerRef.current = newHandler;
        worker.addEventListener("message", newHandler);

        // Send search request to worker
        worker.postMessage({
          type: "search",
          query,
          options,
        });
      } catch (err) {
        setError(
          err instanceof Error ? err : new Error("Search failed")
        );
        setResults([]);
      }
    }, 150); // Debounce delay

    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, [query, loading, error, options?.brand, options?.category]);

  // Execute search when query or options change
  useEffect(() => {
    const cleanup = performSearch();
    return cleanup;
  }, [performSearch]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
      if (messageHandlerRef.current) {
        try {
          const worker = getSearchWorker();
          worker.removeEventListener("message", messageHandlerRef.current);
        } catch (e) {
          // Ignore cleanup errors
        }
      }
    };
  }, []);

  const retry = useCallback(() => {
    setError(null);
    performSearch();
  }, [performSearch]);

  return createAsyncResult(results, loading, error, retry);
}
