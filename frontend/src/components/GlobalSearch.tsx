import { Search, X, Command } from "lucide-react";
import React, { useEffect, useRef, useState, useCallback, useMemo } from "react";
import { useConductorCatalog } from "../hooks/useConductorCatalog";
import { useNavigationStore } from "../store/navigationStore";
import { BaseComponentProps, EventHandler } from "../types/componentUtils";

interface GlobalSearchProps extends BaseComponentProps {
  onSelect?: EventHandler<string>;
  maxResults?: number;
}

interface SearchResult {
  id: string;
  name: string;
  brand: string;
  image_url?: string;
  category?: string;
  subcategory?: string;
}

/**
 * GlobalSearch Component
 *
 * Provides real-time product search functionality with:
 * - Debounced search input
 * - Keyboard shortcuts (Ctrl/Cmd+K to focus, Escape to close)
 * - Dropdown results display with result count
 * - Click-outside detection for dropdown close
 * - Accessible keyboard navigation
 */
export const GlobalSearch: React.FC<GlobalSearchProps> = ({
  onSelect,
  maxResults = 10,
  className,
}) => {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [reloadToken, setReloadToken] = useState(0);
  const { products } = useConductorCatalog();
  const { goToProduct, goToInventory, setSearchQuery } = useNavigationStore();
  const wrapperRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const productMap = useMemo(() => {
    const map = new Map<string, ReturnType<typeof products[number]>>();
    for (const p of products) {
      map.set(p.id, p);
    }
    return map;
  }, [products]);

  const handleRetry = useCallback(() => {
    setReloadToken((t) => t + 1);
  }, []);

  useEffect(() => {
    const trimmed = query.trim();
    if (!trimmed || trimmed.length < 2) {
      setResults([]);
      setLoading(false);
      setError(null);
      return;
    }

    setLoading(true);
    setError(null);

    const controller = new AbortController();
    const timeoutId = window.setTimeout(async () => {
      try {
        const res = await fetch(
          `/api/products/search?q=${encodeURIComponent(trimmed)}`,
          { signal: controller.signal },
        );
        if (!res.ok) {
          throw new Error(`Search failed: ${res.status} ${res.statusText}`);
        }
        const body = await res.json();
        const items = (body?.products ?? []) as Array<{
          id: string;
          product_name?: string;
          brand?: string;
        }>;

        const mapped: SearchResult[] = items.slice(0, maxResults).map((item) => {
          const p = productMap.get(item.id);
          return {
            id: item.id,
            name: p?.name ?? item.product_name ?? item.id,
            brand: p?.brand ?? item.brand ?? "",
            image_url: p?.image_url,
            category: p?.category,
            subcategory: p?.subcategory,
          };
        }).filter(Boolean); // Remove any undefined/null results

        setResults(mapped);
        setLoading(false);
      } catch (err) {
        if ((err as Error).name === "AbortError") {
          return;
        }
        setError(
          err instanceof Error ? err.message : "Search failed. Please try again.",
        );
        setResults([]);
        setLoading(false);
      }
    }, 200);

    return () => {
      window.clearTimeout(timeoutId);
      controller.abort();
    };
  }, [query, maxResults, productMap, reloadToken]);

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
        setIsFocused(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Keyboard shortcut: Ctrl/Cmd+K to focus
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        inputRef.current?.focus();
        setIsFocused(true);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleSelect = useCallback(
    (productId: string) => {
      goToProduct(productId);
      onSelect?.(productId);
      setIsOpen(false);
      setQuery("");
      setSelectedIndex(-1);
      setSearchQuery(null);
      inputRef.current?.blur();
    },
    [goToProduct, onSelect, setSearchQuery],
  );

  const handleSearchSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      const trimmed = query.trim();
      if (!trimmed) {
        setIsOpen(false);
        setSearchQuery(null);
        return;
      }
      setSearchQuery(trimmed);
      goToInventory(trimmed);
      setIsOpen(false);
      setQuery("");
      setSelectedIndex(-1);
      inputRef.current?.blur();
    },
    [query, setSearchQuery, goToInventory],
  );

  // Keyboard navigation in results
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Escape") {
        setQuery("");
        setIsOpen(false);
        setSelectedIndex(-1);
        setSearchQuery(null);
        inputRef.current?.blur();
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) =>
          Math.min(prev + 1, (results?.length || 0) - 1),
        );
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) => Math.max(prev - 1, -1));
      } else if (
        e.key === "Enter" &&
        selectedIndex >= 0 &&
        results?.[selectedIndex]
      ) {
        handleSelect(results[selectedIndex].id);
      }
    },
    [results, selectedIndex, handleSelect],
  );

  return (
    <form
      onSubmit={handleSearchSubmit}
      className={`relative w-full max-w-md hidden md:block ${className ?? ""}`.trim()}
      ref={wrapperRef}
    >
      <div
        className={`relative group flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all duration-200 ${
          isFocused
            ? "bg-zinc-900 border-zinc-600 shadow-lg shadow-blue-500/5 ring-1 ring-blue-500/20"
            : "bg-zinc-900/80 border-zinc-800 hover:border-zinc-700"
        }`}
      >
        <Search
          className={`h-4 w-4 shrink-0 transition-colors ${isFocused ? "text-blue-400" : "text-zinc-500"}`}
        />
        <input
          ref={inputRef}
          type="text"
          className="flex-1 bg-transparent text-zinc-300 placeholder-zinc-500 focus:outline-none sm:text-sm"
          placeholder={loading ? "Initializing..." : "Search products..."}
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
            setSelectedIndex(-1);
          }}
          onFocus={() => {
            setIsFocused(true);
            setIsOpen(true);
          }}
          onBlur={() => setIsFocused(false)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && query.trim()) {
              e.preventDefault();
              handleSearchSubmit(e);
            } else {
              handleKeyDown(e);
            }
          }}
        />

        {/* Result count */}
        {query && !loading && results.length > 0 && (
          <span className="text-[10px] text-zinc-500 tabular-nums shrink-0">
            {results.length} found
          </span>
        )}

        {/* Clear button */}
        {query && (
          <button
            type="button"
            className="p-0.5 text-zinc-500 hover:text-white transition-colors rounded hover:bg-zinc-700/50"
            onClick={() => {
              setQuery("");
              setIsOpen(false);
              setSelectedIndex(-1);
              setSearchQuery(null);
              inputRef.current?.focus();
            }}
            aria-label="Clear search"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        )}

        {/* Keyboard shortcut hint */}
        {!query && !isFocused && (
          <kbd
            className="hidden sm:inline-flex items-center gap-0.5 px-1.5 py-0.5 text-[10px] 
                          text-zinc-600 bg-zinc-800/80 rounded border border-zinc-700/50 font-mono"
          >
            <Command className="w-2.5 h-2.5" />K
          </kbd>
        )}
      </div>

      {/* Search Results Dropdown */}
      {isOpen && query.length > 1 && (
        <div className="absolute mt-2 w-full bg-zinc-900/95 backdrop-blur-md border border-zinc-700/50 rounded-xl shadow-2xl shadow-black/50 z-50 overflow-hidden max-h-[420px] overflow-y-auto custom-scrollbar animate-fade-in">
          {error ? (
            // Error State
            <div className="p-6 text-center">
              <div className="w-10 h-10 mx-auto mb-3 rounded-full bg-red-500/10 flex items-center justify-center">
                <svg
                  className="w-5 h-5 text-red-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
              <p className="text-sm text-red-400 mb-2">{error}</p>
              <button
                onClick={handleRetry}
                className="text-xs text-red-400 hover:text-red-300 underline underline-offset-2 transition-colors"
              >
                Retry search
              </button>
            </div>
          ) : loading ? (
            // Loading State — skeleton
            <div className="p-3 space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <div
                  key={i}
                  className="flex items-center gap-3 px-3 py-2.5 animate-pulse"
                >
                  <div className="w-10 h-10 bg-zinc-800 rounded-lg" />
                  <div className="flex-1 space-y-1.5">
                    <div className="h-3.5 bg-zinc-800 rounded w-3/4" />
                    <div className="h-2.5 bg-zinc-800/60 rounded w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : (results || []).length === 0 ? (
            // Empty State
            <div className="p-8 text-center">
              <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-zinc-800/50 flex items-center justify-center">
                <Search className="w-5 h-5 text-zinc-600" />
              </div>
              <p className="text-sm text-zinc-400 mb-1">No results found</p>
              <p className="text-xs text-zinc-600">
                Try a different search term for "{query}"
              </p>
            </div>
          ) : (
            // Results List
            <div className="py-1.5">
              <div className="px-4 py-1.5 text-[10px] text-zinc-600 font-mono uppercase tracking-wider">
                {results.length} result{results.length !== 1 ? "s" : ""}
              </div>
              {(results || []).map((item, idx) => (
                <button
                  key={item.id}
                  onClick={() => handleSelect(item.id)}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`w-full text-left px-4 py-3 flex items-center gap-3 group transition-all duration-100 ${
                    idx === selectedIndex
                      ? "bg-blue-500/10 border-l-2 border-blue-500"
                      : "hover:bg-zinc-800/50 border-l-2 border-transparent"
                  }`}
                >
                  {item.image_url ? (
                    <img
                      src={item.image_url}
                      alt=""
                      className="w-10 h-10 object-contain bg-white/5 rounded-lg border border-zinc-700/50 p-0.5"
                      onError={(e) => (e.currentTarget.style.display = "none")}
                    />
                  ) : (
                    <div className="w-10 h-10 bg-zinc-800/80 rounded-lg flex items-center justify-center text-xs font-bold text-zinc-500 border border-zinc-700/30">
                      {(item.brand ?? "").charAt(0) || "?"}
                    </div>
                  )}

                  <div className="min-w-0 flex-1">
                    <div
                      className={`text-sm font-medium truncate transition-colors ${
                        idx === selectedIndex
                          ? "text-blue-300"
                          : "text-zinc-200 group-hover:text-blue-300"
                      }`}
                    >
                      {item.name}
                    </div>
                    <div className="text-xs text-zinc-500 flex items-center gap-2 mt-0.5">
                      <span className="text-zinc-600 uppercase tracking-wider text-[10px] font-semibold">
                        {item.brand ?? "—"}
                      </span>
                      {item.category && (
                        <>
                          <span className="text-zinc-700">·</span>
                          <span className="text-zinc-500">{item.category}</span>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Arrow indicator for selected */}
                  {idx === selectedIndex && (
                    <svg
                      className="w-4 h-4 text-blue-400 shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  )}
                </button>
              ))}

              {/* Keyboard hint footer */}
              <div className="px-4 py-2 border-t border-zinc-800/50 flex items-center gap-4 text-[10px] text-zinc-600">
                <span className="flex items-center gap-1">
                  <kbd className="px-1 py-0.5 bg-zinc-800 rounded text-[9px]">
                    ↑↓
                  </kbd>{" "}
                  navigate
                </span>
                <span className="flex items-center gap-1">
                  <kbd className="px-1 py-0.5 bg-zinc-800 rounded text-[9px]">
                    ↵
                  </kbd>{" "}
                  select
                </span>
                <span className="flex items-center gap-1">
                  <kbd className="px-1 py-0.5 bg-zinc-800 rounded text-[9px]">
                    esc
                  </kbd>{" "}
                  close
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </form>
  );
};
