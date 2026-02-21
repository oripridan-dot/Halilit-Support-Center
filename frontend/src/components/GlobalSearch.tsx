import { Search, X, Command } from "lucide-react";
import React, {
  useEffect,
  useRef,
  useState,
  useCallback,
  useMemo,
} from "react";
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
    const map = new Map<
      string,
      {
        id: string;
        name: string;
        brand: string;
        image_url?: string;
        category?: string;
        subcategory?: string;
      }
    >();
    for (const p of products) {
      map.set(p.id, {
        id: p.id,
        name: p.name,
        brand: p.brand,
        image_url: p.image_url,
        category: p.category,
        subcategory: p.subcategory,
      });
    }
    return map;
  }, [products]);

  // Keep a stable ref to productMap so the search effect doesn't re-run when
  // products array gets a new reference (e.g., React Query background refetch
  // with staleTime:0 in dev). Only query/maxResults/reloadToken should retrigger.
  const productMapRef = useRef(productMap);
  useEffect(() => {
    productMapRef.current = productMap;
  }, [productMap]);

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
        const exactMatch = productMapRef.current.get(trimmed.toUpperCase());
        let searchResults: SearchResult[] = [];

        if (exactMatch) {
          searchResults.push(exactMatch);
        }

        const searchTerm = trimmed.toLowerCase();
        const otherResults = Array.from(productMapRef.current.values())
          .filter(
            (product) =>
              product.name.toLowerCase().includes(searchTerm) ||
              product.brand.toLowerCase().includes(searchTerm) ||
              product.id.toLowerCase().includes(searchTerm),
          )
          .filter(
            (product) => product.id.toUpperCase() !== trimmed.toUpperCase(),
          );

        searchResults = searchResults.concat(
          otherResults.slice(0, maxResults - (exactMatch ? 1 : 0)),
        );

        setResults(searchResults);
        setError(null);
      } catch (e: any) {
        if (e.name !== "AbortError") {
          setError(e.message || "An error occurred during search.");
        }
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => {
      clearTimeout(timeoutId);
      controller.abort();
    };
  }, [query, maxResults, reloadToken]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    setSelectedIndex(-1);
    setIsOpen(true);
  };

  const handleInputFocus = () => {
    setIsFocused(true);
  };

  const handleInputBlur = () => {
    // Delay the closing of the dropdown to allow for click events on the results
    setTimeout(() => {
      setIsFocused(false);
      if (!isFocused) {
        setIsOpen(false);
      }
    }, 150);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prevIndex) =>
        Math.min(prevIndex + 1, results.length - 1),
      );
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prevIndex) => Math.max(prevIndex - 1, -1));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (selectedIndex >= 0 && selectedIndex < results.length) {
        handleResultClick(results[selectedIndex].id);
      } else if (results.length === 1) {
        handleResultClick(results[0].id);
      }
    } else if (e.key === "Escape") {
      setIsOpen(false);
      setQuery("");
    }
  };

  const handleResultClick = (id: string) => {
    if (onSelect) {
      onSelect(id);
    } else {
      goToProduct(id);
    }
    setQuery("");
    setIsOpen(false);
    setSelectedIndex(-1);
  };

  const resultCount = results.length;

  return (
    <div ref={wrapperRef} className={`relative w-full ${className}`}>
      <div className="relative">
        <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
          <Search className="w-5 h-5 text-zinc-400" />
        </div>
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          onKeyDown={handleKeyDown}
          placeholder="Search products..."
          className="w-full rounded-md border border-zinc-700 bg-zinc-800 py-2 pl-10 pr-3 text-sm placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-colors"
        />
        {query.length > 0 && (
          <button
            onClick={() => {
              setQuery("");
              setIsOpen(false);
            }}
            className="absolute inset-y-0 right-0 flex items-center pr-3"
          >
            <X className="w-5 h-5 text-zinc-400" />
          </button>
        )}
      </div>

      {isOpen && (
        <div className="absolute z-10 mt-2 w-full overflow-hidden rounded-md bg-zinc-900 shadow-md ring-1 ring-zinc-700 focus:outline-none">
          {loading && (
            <div className="px-4 py-2 text-sm text-zinc-400">Loading...</div>
          )}
          {error && (
            <div className="px-4 py-2 text-sm text-red-500">
              {error}
              <button
                onClick={handleRetry}
                className="ml-2 text-xs text-blue-400 hover:underline"
              >
                Retry
              </button>
            </div>
          )}
          {!loading &&
            !error &&
            results.length === 0 &&
            query.trim().length > 1 && (
              <div className="px-4 py-2 text-sm text-zinc-400">
                No results found.
              </div>
            )}
          {!loading &&
            !error &&
            results.map((result, index) => (
              <button
                key={result.id}
                onClick={() => handleResultClick(result.id)}
                className={`flex w-full items-center justify-between px-4 py-2 text-sm hover:bg-zinc-700 focus:bg-zinc-700 focus:outline-none ${
                  selectedIndex === index ? "bg-zinc-700" : ""
                }`}
                tabIndex={index === selectedIndex ? 0 : -1}
              >
                <div className="flex flex-col">
                  <span>{result.name}</span>
                  <span className="text-xs text-zinc-400">{result.brand}</span>
                </div>
              </button>
            ))}
          {!loading && !error && results.length > 0 && (
            <div className="px-4 py-2 text-sm text-zinc-400">
              {resultCount} {resultCount === 1 ? "result" : "results"}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
