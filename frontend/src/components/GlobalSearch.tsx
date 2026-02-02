import { Search, X } from "lucide-react";
import { useEffect, useRef, useState, useCallback } from "react";
import { useRealtimeSearch } from "../hooks/useRealtimeSearch";
import { useNavigationStore } from "../store/navigationStore";
import { BaseComponentProps, EventHandler } from "../types/componentUtils";

interface GlobalSearchProps extends BaseComponentProps {
  onSelect?: EventHandler<string>;
  maxResults?: number;
}

/**
 * GlobalSearch Component
 *
 * Provides real-time product search functionality with:
 * - Debounced search input
 * - Dropdown results display
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
  const searchResult = useRealtimeSearch(query, { limit: maxResults });
  const { data: results = [], loading, error } = searchResult;
  const { openProductPop } = useNavigationStore();
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelect = useCallback(
    (productId: string) => {
      openProductPop(productId);
      onSelect?.(productId);
      setIsOpen(false);
      setQuery("");
    },
    [openProductPop, onSelect],
  );

  return (
    <div className="relative w-full max-w-md hidden md:block" ref={wrapperRef}>
      <div className="relative group">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <Search
            className={`h-4 w-4 ${isOpen ? "text-emerald-500" : "text-zinc-500"}`}
          />
        </div>
        <input
          type="text"
          className="block w-full pl-10 pr-3 py-1.5 border border-zinc-800 rounded-md leading-5 bg-zinc-900 text-zinc-300 placeholder-zinc-500 focus:outline-none focus:bg-zinc-950 focus:border-zinc-700 focus:ring-1 focus:ring-zinc-700 sm:text-sm transition-all"
          placeholder={loading ? "Initializing..." : "Search catalog..."}
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
        />
        {query && (
          <button
            className="absolute inset-y-0 right-0 pr-3 flex items-center text-zinc-500 hover:text-white"
            onClick={() => {
              setQuery("");
              setIsOpen(false);
            }}
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Search Results Dropdown */}
      {isOpen && query.length > 1 && (
        <div className="absolute mt-1 w-full bg-zinc-900 border border-zinc-800 rounded-md shadow-xl z-50 overflow-hidden max-h-96 overflow-y-auto">
          {error ? (
            // Error State
            <div className="p-4 text-center text-red-500 text-xs">
              <p>{error.message}</p>
              <button
                onClick={searchResult.retry}
                className="mt-2 text-xs text-red-400 hover:text-red-300 underline"
              >
                Retry
              </button>
            </div>
          ) : loading ? (
            // Loading State
            <div className="p-4 text-center text-zinc-500 text-xs">
              <div className="inline-block h-3 w-3 animate-spin rounded-full border border-zinc-600 border-r-transparent" />
              <p className="mt-2">Searching...</p>
            </div>
          ) : (results || []).length === 0 ? (
            // Empty State
            <div className="p-4 text-center text-zinc-500 text-xs">
              No products found for "{query}"
            </div>
          ) : (
            // Results List
            <div className="py-1">
              {(results || []).map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleSelect(item.id)}
                  className="w-full text-left px-4 py-3 hover:bg-zinc-800 flex items-center gap-3 group transition-colors border-b border-zinc-800/50 last:border-0"
                >
                  {item.image_url ? (
                    <img
                      src={item.image_url}
                      alt=""
                      className="w-8 h-8 object-contain bg-white/5 rounded-sm"
                      onError={(e) => (e.currentTarget.style.display = "none")}
                    />
                  ) : (
                    <div className="w-8 h-8 bg-zinc-800 rounded-sm flex items-center justify-center text-xs font-bold text-zinc-600">
                      {item.brand_name.charAt(0)}
                    </div>
                  )}

                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-medium text-zinc-200 group-hover:text-emerald-400 truncate">
                      {item.label}
                    </div>
                    <div className="text-xs text-zinc-500 flex items-center gap-2">
                      <span className="text-zinc-600 uppercase tracking-wider text-[10px]">
                        {item.brand_name}
                      </span>
                      <span>•</span>
                      <span>{item.category}</span>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
