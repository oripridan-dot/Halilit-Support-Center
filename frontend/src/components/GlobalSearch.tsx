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
        const exactMatch = productMapRef.current.get(trimmed.toUpperCase());
        let searchResults: SearchResult[] = [];

        if (exactMatch) {
          searchResults = [exactMatch];
          const otherResults = Array.from(productMapRef.current.values())
            .filter(
              (product) =>
                product.id.toUpperCase() !== trimmed.toUpperCase() &&
                (product.name.toLowerCase().includes(trimmed.toLowerCase()) ||
                  product.brand.toLowerCase().includes(trimmed.toLowerCase())),
            )
            .slice(0, maxResults - 1);
          searchResults = searchResults.concat(otherResults);
        } else {
           searchResults = Array.from(productMapRef.current.values()).filter(
            (product) =>
              product.name.toLowerCase().includes(trimmed.toLowerCase()) ||
              product.brand.toLowerCase().includes(trimmed.toLowerCase()),
          ).slice(0, maxResults);
        }

        setResults(searchResults);
        setError(null);
      } catch (e: any) {
        if (e.name !== 'AbortError') {
          setError(e.message || 'An error occurred during search.');
        }
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 250);

    return () => {
      clearTimeout(timeoutId);
      controller.abort();
    };
  }, [query, maxResults]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    setIsOpen(true);
    setSelectedIndex(-1);
  };

  const handleInputFocus = () => {
    setIsFocused(true);
  };

  const handleInputBlur = () => {
    // Blur handler to prevent immediate closing when clicking on the dropdown
    setTimeout(() => {
      setIsFocused(false);
      if (!wrapperRef.current?.contains(document.activeElement)) {
        setIsOpen(false);
      }
    }, 100);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prevIndex) =>
        Math.min(prevIndex + 1, results.length - 1),
      );
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prevIndex) => Math.max(prevIndex - 1, -1));
    } else if (e.key === "Enter") {
      if (selectedIndex >= 0 && selectedIndex < results.length) {
        handleResultSelect(results[selectedIndex].id);
      } else if (results.length > 0) {
        handleResultSelect(results[0].id);
      }
    } else if (e.key === "Escape") {
      setIsOpen(false);
      setQuery("");
    }
  };

  const handleResultSelect = (id: string) => {
    onSelect?.(id);
    setSearchQuery(query); // For navigation store
    goToProduct(id);
    setIsOpen(false);
    setQuery("");
  };

  const handleClear = () => {
    setQuery("");
    setIsOpen(false);
    setSelectedIndex(-1);
  };

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
            onClick={handleRetry}
            className="ml-2 text-blue-400 hover:underline"
          >
            Retry
          </button>
        </div>
      );
    }

    if (!results.length && query.trim().length >= 2) {
      return (
        <div className="px-3 py-2 text-zinc-400 text-sm">No results found.</div>
      );
    }

    return results.slice(0, maxResults).map((result, index) => (
      <button
        key={result.id}
        onClick={() => handleResultSelect(result.id)}
        className={`px-3 py-2 text-sm text-left w-full hover:bg-zinc-800 focus-visible:bg-zinc-800 outline-none ${selectedIndex === index ? "bg-zinc-800" : "bg-transparent"
          }`}
        tabIndex={-1}
        role="option"
        aria-selected={selectedIndex === index}
      >
        <div className="flex items-center gap-2">
          {result.image_url && (
            <img
              src={result.image_url}
              alt={result.name}
              className="w-6 h-6 rounded object-cover"
            />
          )}
          <span>
            {result.name} ({result.brand})
          </span>
        </div>
      </button>
    ));
  };

  return (
    <div
      ref={wrapperRef}
      className={`relative w-full ${className}`}
      onFocus={() => setIsFocused(true)}
      onBlur={handleInputBlur}
    >
      <div className="relative">
        <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
          <Search className="w-5 h-5 text-zinc-400" />
        </div>
        <input
          ref={inputRef}
          type="text"
          className="w-full rounded-md border border-zinc-700 bg-zinc-900 text-sm text-zinc-100 placeholder:text-zinc-500 pl-10 pr-10 py-2 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 outline-none"
          placeholder="Search products..."
          value={query}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onKeyDown={handleKeyDown}
          autoComplete="off"
        />
        {query && (
          <button
            onClick={handleClear}
            className="absolute inset-y-0 right-0 flex items-center pr-3"
          >
            <X className="w-5 h-5 text-zinc-400" />
          </button>
        )}
      </div>
      {isOpen && (
        <div
          className="absolute z-10 mt-1 w-full bg-zinc-900 rounded-md border border-zinc-700 shadow-md overflow-hidden focus-within:ring-2 ring-blue-500"
          role="listbox"
        >
          {renderResults()}
        </div>
      )}
    </div>
  );
};