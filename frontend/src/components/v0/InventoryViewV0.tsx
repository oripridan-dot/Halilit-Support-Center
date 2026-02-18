/**
 * Inventory View v0 — Best UX/UI for operator console
 *
 * Features:
 * - Inline search with instant filter
 * - Brand & category filter chips
 * - Sortable columns (name, brand, price)
 * - Responsive: dense table (desktop), cards (mobile)
 * - Clear visual hierarchy, design tokens
 * - Accessible, keyboard-friendly
 * - Skeleton loading, empty state
 */
import React, { useMemo, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  ChevronUp,
  ChevronDown,
  X,
  Grid3X3,
  List,
  Package,
  ArrowUpDown,
} from "lucide-react";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import { useNavigationStore } from "../../store/navigationStore";
import type { ConductorProduct } from "../../hooks/useConductorCatalog";

type SortKey = "name" | "brand" | "category" | "price" | "price_eilat";
type SortDir = "asc" | "desc";
type ViewMode = "table" | "cards";

const ROW_HEIGHT = 56;
const CARD_MIN_HEIGHT = 120;

function SkeletonRow() {
  return (
    <div
      className="grid grid-cols-12 gap-4 px-4 sm:px-6 py-3 animate-pulse"
      style={{ minHeight: ROW_HEIGHT }}
    >
      <div className="col-span-4 flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-zinc-800/80" />
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-zinc-800/80 rounded w-3/4" />
          <div className="h-3 bg-zinc-800/50 rounded w-1/3" />
        </div>
      </div>
      <div className="col-span-2 hidden sm:block">
        <div className="h-4 bg-zinc-800/60 rounded w-20" />
      </div>
      <div className="col-span-2 hidden md:block">
        <div className="h-5 bg-zinc-800/50 rounded w-24" />
      </div>
      <div className="col-span-2 sm:col-span-4 md:col-span-2 text-right">
        <div className="h-4 bg-zinc-800/80 rounded w-16 ml-auto" />
      </div>
      <div className="col-span-2 hidden sm:block text-right">
        <div className="h-4 bg-zinc-800/60 rounded w-14 ml-auto" />
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center py-16 px-6 text-center"
    >
      <div className="w-16 h-16 rounded-2xl bg-zinc-800/50 flex items-center justify-center mb-4">
        <Package className="w-8 h-8 text-zinc-500" aria-hidden />
      </div>
      <h3 className="text-base font-semibold text-zinc-200 mb-1">
        No products match your filters
      </h3>
      <p className="text-sm text-zinc-500 max-w-sm">
        Try adjusting your search or filters to see more products.
      </p>
    </motion.div>
  );
}

function ProductRow({
  item,
  onSelect,
}: {
  item: ConductorProduct;
  onSelect: (id: string) => void;
}) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      role="button"
      tabIndex={0}
      onClick={() => onSelect(item.id)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onSelect(item.id);
        }
      }}
      className="grid grid-cols-12 gap-2 sm:gap-4 px-4 sm:px-6 py-3 items-center
        hover:bg-zinc-800/40 cursor-pointer group transition-colors duration-150
        focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-inset
        min-h-[52px] sm:min-h-[56px]"
      aria-label={`View ${item.name}`}
    >
      <div className="col-span-4 flex items-center gap-3 min-w-0">
        <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-lg bg-zinc-800/80 overflow-hidden flex-shrink-0 border border-zinc-700/50">
          {item.image_url ? (
            <img
              src={item.image_url}
              alt=""
              className="w-full h-full object-contain p-0.5"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-[10px] font-bold text-zinc-500">
              {item.brand?.charAt(0) || "?"}
            </div>
          )}
        </div>
        <div className="min-w-0 flex-1">
          <div className="text-sm font-medium text-zinc-200 truncate group-hover:text-blue-400 transition-colors">
            {item.name}
          </div>
          <div className="text-[11px] text-zinc-500 font-mono truncate hidden sm:block">
            {item.id}
          </div>
        </div>
      </div>
      <div className="col-span-2 hidden sm:block text-sm text-zinc-400 truncate">
        {item.brand}
      </div>
      <div className="col-span-2 hidden md:block">
        <span className="inline-flex px-2 py-0.5 rounded-md text-[11px] font-medium bg-zinc-800/80 text-zinc-400 border border-zinc-700/50">
          {item.subcategory || item.category || "—"}
        </span>
      </div>
      <div className="col-span-4 sm:col-span-2 md:col-span-2 text-right">
        <span className="text-sm font-semibold text-zinc-100 tabular-nums">
          ₪{item.price != null ? item.price.toLocaleString() : "—"}
        </span>
      </div>
      <div className="col-span-2 hidden sm:block text-right text-sm text-zinc-500 tabular-nums">
        ₪{item.price_eilat != null ? item.price_eilat.toLocaleString() : "—"}
      </div>
    </motion.div>
  );
}

function ProductCard({
  item,
  onSelect,
}: {
  item: ConductorProduct;
  onSelect: (id: string) => void;
}) {
  return (
    <motion.button
      layout
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0 }}
      type="button"
      onClick={() => onSelect(item.id)}
      className="w-full text-left p-4 rounded-xl bg-zinc-900/60 border border-zinc-800/80
        hover:bg-zinc-800/50 hover:border-zinc-700 transition-all duration-200
        focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-950
        min-h-[120px] flex flex-col gap-3"
      style={{ minHeight: CARD_MIN_HEIGHT }}
    >
      <div className="flex gap-4 flex-1 min-w-0">
        <div className="w-16 h-16 rounded-lg bg-zinc-800 overflow-hidden flex-shrink-0 border border-zinc-700/50">
          {item.image_url ? (
            <img
              src={item.image_url}
              alt=""
              className="w-full h-full object-contain p-1"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-lg font-bold text-zinc-500">
              {item.brand?.charAt(0) || "?"}
            </div>
          )}
        </div>
        <div className="min-w-0 flex-1">
          <div className="font-medium text-zinc-200 line-clamp-2 mb-0.5">
            {item.name}
          </div>
          <div className="text-xs text-zinc-500">{item.brand}</div>
          <div className="mt-2 flex items-center gap-2 flex-wrap">
            <span className="text-sm font-semibold text-zinc-100">
              ₪{item.price != null ? item.price.toLocaleString() : "—"}
            </span>
            {item.price_eilat != null && (
              <span className="text-xs text-zinc-500">
                Eilat: ₪{item.price_eilat.toLocaleString()}
              </span>
            )}
          </div>
        </div>
      </div>
    </motion.button>
  );
}

export const InventoryViewV0: React.FC = () => {
  const { products, metadata, isLoading } = useConductorCatalog();
  const { openProductPage } = useNavigationStore();

  const [search, setSearch] = useState("");
  const [brandFilter, setBrandFilter] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);
  const [sortKey, setSortKey] = useState<SortKey>("name");
  const [sortDir, setSortDir] = useState<SortDir>("asc");
  const [viewMode, setViewMode] = useState<ViewMode>("table");

  // Extract unique brands and categories
  const { brands, categories } = useMemo(() => {
    const b = new Set<string>();
    const c = new Set<string>();
    products.forEach((p) => {
      if (p.brand) b.add(p.brand);
      const cat = p.subcategory || p.category;
      if (cat) c.add(cat);
    });
    return {
      brands: Array.from(b).sort(),
      categories: Array.from(c).sort(),
    };
  }, [products]);

  // Filter and sort
  const filteredProducts = useMemo(() => {
    let list = products;

    if (search.trim()) {
      const q = search.trim().toLowerCase();
      list = list.filter(
        (p) =>
          p.name?.toLowerCase().includes(q) ||
          p.brand?.toLowerCase().includes(q) ||
          p.subcategory?.toLowerCase().includes(q) ||
          p.category?.toLowerCase().includes(q) ||
          p.id?.toLowerCase().includes(q)
      );
    }
    if (brandFilter) {
      list = list.filter((p) => p.brand === brandFilter);
    }
    if (categoryFilter) {
      list = list.filter(
        (p) => (p.subcategory || p.category) === categoryFilter
      );
    }

    const sorted = [...list].sort((a, b) => {
      let cmp = 0;
      switch (sortKey) {
        case "name":
          cmp = (a.name ?? "").localeCompare(b.name ?? "");
          break;
        case "brand":
          cmp = (a.brand ?? "").localeCompare(b.brand ?? "");
          break;
        case "category":
          cmp = (a.subcategory ?? a.category ?? "").localeCompare(
            b.subcategory ?? b.category ?? ""
          );
          break;
        case "price":
          cmp = (a.price ?? 0) - (b.price ?? 0);
          break;
        case "price_eilat":
          cmp = (a.price_eilat ?? 0) - (b.price_eilat ?? 0);
          break;
        default:
          cmp = 0;
      }
      return sortDir === "asc" ? cmp : -cmp;
    });

    return sorted;
  }, [
    products,
    search,
    brandFilter,
    categoryFilter,
    sortKey,
    sortDir,
  ]);

  const toggleSort = useCallback((key: SortKey) => {
    setSortKey(key);
    setSortDir((d) => (d === "asc" ? "desc" : "asc"));
  }, []);

  const clearFilters = useCallback(() => {
    setSearch("");
    setBrandFilter(null);
    setCategoryFilter(null);
  }, []);

  const hasActiveFilters = search || brandFilter || categoryFilter;

  if (isLoading) {
    return (
      <div className="flex flex-col h-full bg-[var(--studio-bg,#0e0e10)]">
        <div className="h-14 sm:h-16 border-b border-zinc-800 flex items-center px-4 sm:px-6 shrink-0">
          <h1 className="text-lg font-semibold text-white">Inventory</h1>
        </div>
        <div className="flex-1 overflow-auto">
          <div className="divide-y divide-zinc-800/50">
            {Array.from({ length: 12 }).map((_, i) => (
              <SkeletonRow key={i} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-[var(--studio-bg,#0e0e10)]">
      {/* Header */}
      <header className="shrink-0 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-sm">
        <div className="px-4 sm:px-6 py-4 sm:py-5">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-xl font-semibold text-white tracking-tight">
                Inventory
              </h1>
              <p className="text-sm text-zinc-500 mt-0.5">
                {filteredProducts.length.toLocaleString()} of{" "}
                {products.length.toLocaleString()} products
                {metadata?.brands?.length && ` · ${metadata.brands.length} brands`}
              </p>
            </div>

            {/* View toggle - desktop only */}
            <div className="hidden sm:flex items-center gap-1 p-1 rounded-lg bg-zinc-900/80 border border-zinc-800">
              <button
                type="button"
                onClick={() => setViewMode("table")}
                className={`p-2 rounded-md transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 ${
                  viewMode === "table"
                    ? "bg-zinc-700 text-white"
                    : "text-zinc-500 hover:text-zinc-300"
                }`}
                aria-label="Table view"
              >
                <List size={18} />
              </button>
              <button
                type="button"
                onClick={() => setViewMode("cards")}
                className={`p-2 rounded-md transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 ${
                  viewMode === "cards"
                    ? "bg-zinc-700 text-white"
                    : "text-zinc-500 hover:text-zinc-300"
                }`}
                aria-label="Card view"
              >
                <Grid3X3 size={18} />
              </button>
            </div>
          </div>

          {/* Search + filters */}
          <div className="mt-4 flex flex-col gap-3">
            <div className="flex flex-col sm:flex-row gap-2">
              <div className="relative flex-1">
                <Search
                  className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500"
                  aria-hidden
                />
                <input
                  type="search"
                  placeholder="Search by name, brand, category, ID…"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full pl-10 pr-10 py-2.5 sm:py-3 rounded-lg
                    bg-zinc-900 border border-zinc-800 text-zinc-200 placeholder-zinc-500
                    focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50
                    text-sm transition-colors"
                  aria-label="Search products"
                />
                {search && (
                  <button
                    type="button"
                    onClick={() => setSearch("")}
                    className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded text-zinc-500 hover:text-white hover:bg-zinc-700 transition-colors"
                    aria-label="Clear search"
                  >
                    <X size={16} />
                  </button>
                )}
              </div>
              <select
                value={brandFilter ?? ""}
                onChange={(e) =>
                  setBrandFilter(e.target.value || null)
                }
                className="px-4 py-2.5 sm:py-3 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300 text-sm
                  focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 min-w-[140px]"
                aria-label="Filter by brand"
              >
                <option value="">All brands</option>
                {brands.map((b) => (
                  <option key={b} value={b}>
                    {b}
                  </option>
                ))}
              </select>
              <select
                value={categoryFilter ?? ""}
                onChange={(e) =>
                  setCategoryFilter(e.target.value || null)
                }
                className="px-4 py-2.5 sm:py-3 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300 text-sm
                  focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 min-w-[140px]"
                aria-label="Filter by category"
              >
                <option value="">All categories</option>
                {categories.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
              {hasActiveFilters && (
                <button
                  type="button"
                  onClick={clearFilters}
                  className="flex items-center gap-2 px-4 py-2.5 sm:py-3 rounded-lg
                    bg-zinc-800/80 text-zinc-400 hover:text-white hover:bg-zinc-700
                    text-sm font-medium transition-colors focus-visible:ring-2 focus-visible:ring-blue-500"
                >
                  <X size={14} />
                  Clear
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Table header - table mode only */}
        {viewMode === "table" && (
          <div
            className="hidden sm:grid grid-cols-12 gap-4 px-4 sm:px-6 py-2.5
              bg-zinc-900/30 text-xs font-semibold text-zinc-500 uppercase tracking-wider"
          >
            <button
              type="button"
              onClick={() => toggleSort("name")}
              className="col-span-4 flex items-center gap-1 text-left hover:text-zinc-300 transition-colors"
            >
              Product
              {sortKey === "name" ? (
                sortDir === "asc" ? (
                  <ChevronUp size={12} />
                ) : (
                  <ChevronDown size={12} />
                )
              ) : (
                <ArrowUpDown size={12} className="opacity-50" />
              )}
            </button>
            <button
              type="button"
              onClick={() => toggleSort("brand")}
              className="col-span-2 flex items-center gap-1 text-left hover:text-zinc-300 transition-colors"
            >
              Brand
              {sortKey === "brand" &&
                (sortDir === "asc" ? (
                  <ChevronUp size={12} />
                ) : (
                  <ChevronDown size={12} />
                ))}
            </button>
            <div className="col-span-2">Category</div>
            <button
              type="button"
              onClick={() => toggleSort("price")}
              className="col-span-2 flex items-center justify-end gap-1 hover:text-zinc-300 transition-colors"
            >
              Price (IL)
              {sortKey === "price" &&
                (sortDir === "asc" ? (
                  <ChevronUp size={12} />
                ) : (
                  <ChevronDown size={12} />
                ))}
            </button>
            <button
              type="button"
              onClick={() => toggleSort("price_eilat")}
              className="col-span-2 flex items-center justify-end gap-1 hover:text-zinc-300 transition-colors"
            >
              Eilat
              {sortKey === "price_eilat" &&
                (sortDir === "asc" ? (
                  <ChevronUp size={12} />
                ) : (
                  <ChevronDown size={12} />
                ))}
            </button>
          </div>
        )}
      </header>

      {/* Content */}
      <div className="flex-1 overflow-auto min-h-0">
        {filteredProducts.length === 0 ? (
          <EmptyState />
        ) : viewMode === "table" ? (
          <div className="divide-y divide-zinc-800/50">
            <AnimatePresence mode="popLayout">
              {filteredProducts.map((item) => (
                <ProductRow
                  key={item.id}
                  item={item}
                  onSelect={openProductPage}
                />
              ))}
            </AnimatePresence>
          </div>
        ) : (
          <div className="p-4 sm:p-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4">
            <AnimatePresence mode="popLayout">
              {filteredProducts.map((item) => (
                <ProductCard
                  key={item.id}
                  item={item}
                  onSelect={openProductPage}
                />
              ))}
            </AnimatePresence>
          </div>
        )}
      </div>
    </div>
  );
};

export default InventoryViewV0;
