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
    const map = new Map<string, { id: string, name: string, brand: string, image_url?: string, category?: string, subcategory?: string }>();
    for (const p of products) {
      map.set(p.id, { id: p.id, name: p.name, brand: p.brand, image_url: p.image_url, category: p.category, subcategory: p.subcategory });
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
        const res = await fetch(
          `/api/products/search?q=${encodeURIComponent(trimmed)}`,
          { signal: controller.signal },
        );
        if (!res.ok) {
          throw new Error(`Search failed: ${res.status} ${res.statusText}`);
        }
        const body = await res.json();

        let exactMatch: SearchResult | null = null;
        const otherResults: SearchResult[] = [];

        if (productMapRef.current) {
          const lowerCaseQuery = trimmed.toLowerCase();
          for (const product of body.results as SearchResult[]) {
            if (productMapRef.current.has(trimmed.toUpperCase()) && product.id.toLowerCase() === lowerCaseQuery) {
              exactMatch = product;
            } else {
              otherResults.push(product);
            }
          }
        }
        let finalResults: SearchResult[] = [];

        if (exactMatch) {
            finalResults.push(exactMatch);
            finalResults = finalResults.concat(otherResults);
        } else {
            finalResults = otherResults;
        }


        setResults(finalResults.slice(0, maxResults));
        setError(null);
      } catch (err: any) {
        if (err.name === "AbortError") {
          console.log("Search aborted");
        } else {
          setError(err.message || "An unexpected error occurred.");
        }
      } finally {
        setLoading(false);
      }
    }, 250);

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
    // Delay the closing of the dropdown to allow for clicks on the results
    setTimeout(() => {
      setIsOpen(false);
      setIsFocused(false);
    }, 150);
  };


  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (!isOpen) {
        if (e.key === "Enter" || (e.ctrlKey || e.metaKey) && e.key === "k") {
          e.preventDefault();
          setIsOpen(true);
          inputRef.current?.focus();
        }
        return;
      }

      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prevIndex) =>
          Math.min(prevIndex + 1, results.length - 1),
        );
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prevIndex) => Math.max(prevIndex - 1, 0));
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < results.length) {
          handleResultSelect(results[selectedIndex].id);
        } else if (results.length === 1) {
            handleResultSelect(results[0].id)
        }
      } else if (e.key === "Escape") {
        e.preventDefault();
        setIsOpen(false);
        setQuery("");
        setSelectedIndex(-1);
        inputRef.current?.blur();
      }
    },
    [isOpen, results.length, selectedIndex, handleResultSelect],
  );

  const handleResultSelect = useCallback(
    (id: string) => {
      onSelect?.(id);
      goToProduct(id);
      setQuery("");
      setIsOpen(false);
      setSelectedIndex(-1);
    },
    [onSelect, goToProduct],
  );


  const handleClickOutside = useCallback(
    (event: Event) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSelectedIndex(-1);
      }
    },
    [],
  );

  useEffect(() => {
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [handleClickOutside]);


  const renderResults = () => {
    if (loading) {
      return (
        <div className="px-3 py-2 text-zinc-400 text-sm">Loading...</div>
      );
    }

    if (error) {
      return (
        <div className="px-3 py-2 text-red-500 text-sm">
          {error}
          <button
            className="ml-2 text-xs text-blue-400 hover:underline"
            onClick={handleRetry}
          >
            Retry
          </button>
        </div>
      );
    }

    if (!results.length) {
      return (
        <div className="px-3 py-2 text-zinc-400 text-sm">No results found.</div>
      );
    }

    return results.map((result, index) => (
      <button
        key={result.id}
        className={`w-full text-left px-3 py-2 text-sm hover:bg-zinc-800 focus:bg-zinc-800 outline-none ${
          selectedIndex === index ? "bg-zinc-800" : "bg-zinc-900"
        }`}
        onClick={() => handleResultSelect(result.id)}
        onMouseEnter={() => setSelectedIndex(index)}
        onMouseLeave={() => {
          if (selectedIndex === index) {
            setSelectedIndex(-1);
          }
        }}
        tabIndex={0}
      >
        <div className="flex items-center justify-between">
          <span>{result.name}</span>
          <span className="text-xs text-zinc-400">{result.brand}</span>
        </div>
        <span className="text-xs text-zinc-500">{result.id}</span>
      </button>
    ));
  };


  return (
    <div
      ref={wrapperRef}
      className={`relative w-full ${className}`}
    >
      <div className="flex items-center w-full px-4 py-2 bg-zinc-900 rounded-md border border-zinc-700 focus-within:border-blue-400 transition-colors">
        <Search className="mr-2 h-4 w-4 text-zinc-400" />
        <input
          ref={inputRef}
          type="text"
          placeholder="Search products..."
          value={query}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          onKeyDown={handleKeyDown}
          className="bg-transparent w-full text-sm outline-none"
        />
        {query && (
          <button onClick={() => setQuery("")} className="ml-2">
            <X className="h-4 w-4 text-zinc-400" />
          </button>
        )}
        <div className="absolute right-2 top-2">
          {(isFocused || isOpen) && (
            <Command
              size={16}
              className="text-zinc-400 hover:text-white"
            />
          )}
        </div>
      </div>
      {isOpen && (
        <div className="absolute z-10 mt-1 w-full bg-zinc-900 rounded-md shadow-md overflow-hidden border border-zinc-700">
          {renderResults()}
        </div>
      )}
    </div>
  );
};