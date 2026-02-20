/**
 * InventoryView — Inventory Master  (Spec 02 v2.0 · Stitch redesign)
 * Dense data table, not a card grid. Power-user tool.
 */
import React, { useState, useEffect, useMemo } from "react";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import type { ConductorProduct } from "../../hooks/useConductorCatalog";
import { useNavigationStore } from "../../store/navigationStore";
import { useDebounceValue } from "../../hooks/useDebounceValue";
import {
  Search,
  ChevronUp,
  ChevronDown,
  ChevronsUpDown,
  AlertTriangle,
  Package,
  ExternalLink,
} from "lucide-react";

// ── StockBadge ─────────────────────────────────────────────────────────────────
const StockBadge: React.FC<{ stock?: number | null }> = ({ stock }) => {
  if (stock === 0)
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-red-950/40 text-red-400 border border-red-900/40">
        OUT OF STOCK
      </span>
    );
  if (stock === null || stock === undefined)
    return (
      <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-zinc-900 text-zinc-600 border border-zinc-800">
        UNKNOWN
      </span>
    );
  return (
    <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold bg-emerald-950/30 text-emerald-400 border border-emerald-900/30">
      IN STOCK
    </span>
  );
};

// ── SortIcon ───────────────────────────────────────────────────────────────────
const SortIcon: React.FC<{ field: string; active: string; dir: string }> = ({ field, active, dir }) => {
  if (active !== field) return <ChevronsUpDown size={11} className="text-zinc-700" />;
  return dir === "asc"
    ? <ChevronUp size={11} className="text-blue-400" />
    : <ChevronDown size={11} className="text-blue-400" />;
};

// ── Constants ──────────────────────────────────────────────────────────────────
const PAGE_SIZE = 50;

type SortField = "name" | "id" | "brand" | "price";
type SortDir   = "asc" | "desc";

// ── InventoryView ──────────────────────────────────────────────────────────────
const InventoryView: React.FC = () => {
  const { products, isLoading, error, refetch } = useConductorCatalog();
  const { searchQuery, initialCfpFilter, setSearchQuery, goToProduct } = useNavigationStore();

  const [filterText, setFilterText]       = useState(typeof searchQuery === "string" ? searchQuery : "");
  const debouncedFilter                   = useDebounceValue(filterText, 150);
  const [brandFilter, setBrandFilter]     = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [cfpOnly, setCfpOnly]             = useState(initialCfpFilter ?? false);
  const [sortField, setSortField]         = useState<SortField>("name");
  const [sortDir, setSortDir]             = useState<SortDir>("asc");
  const [page, setPage]                   = useState(1);

  // Deep-link sync
  useEffect(() => {
    if (typeof searchQuery === "string" && searchQuery !== null) setFilterText(searchQuery);
  }, [searchQuery]);

  useEffect(() => {
    setSearchQuery(
      typeof debouncedFilter === "string" && debouncedFilter ? debouncedFilter : null
    );
  }, [debouncedFilter, setSearchQuery]);

  useEffect(() => { setCfpOnly(initialCfpFilter ?? false); }, [initialCfpFilter]);
  useEffect(() => { setPage(1); }, [filterText, brandFilter, categoryFilter, cfpOnly, sortField, sortDir]);

  // Derived lists for filter selects
  const { brands, categories } = useMemo(() => {
    if (!products) return { brands: [] as string[], categories: [] as string[] };
    const b = Array.from(new Set(products.map(p => p.brand).filter(Boolean))).sort();
    const c = Array.from(new Set(products.map(p => p.category || "General").filter(Boolean))).sort();
    return { brands: b, categories: c };
  }, [products]);

  const filterStr = typeof debouncedFilter === "string" ? debouncedFilter : "";

  // Total count before pagination (for header)
  const [totalFiltered, setTotalFiltered] = useState(0);

  const pagedProducts = useMemo(() => {
    if (!products) return [];
    let list = products.filter(item => {
      const q = filterStr.toLowerCase();
      const textMatch = !filterStr
        || item.name?.toLowerCase().includes(q)
        || item.id?.toLowerCase().includes(q)
        || item.brand?.toLowerCase().includes(q)
        || item.category?.toLowerCase().includes(q);
      const brandMatch    = !brandFilter    || item.brand === brandFilter;
      const catMatch      = !categoryFilter || (item.category || "General") === categoryFilter;
      const cfpMatch      = !cfpOnly        || (item.price == null || item.price === 0);
      return textMatch && brandMatch && catMatch && cfpMatch;
    });

    // Sort
    list = [...list].sort((a, b) => {
      const d = sortDir === "asc" ? 1 : -1;
      switch (sortField) {
        case "id":    return a.id.localeCompare(b.id) * d;
        case "brand": return (a.brand ?? "").localeCompare(b.brand ?? "") * d;
        case "price": return ((a.price ?? Number.MAX_VALUE) - (b.price ?? Number.MAX_VALUE)) * d;
        default:      return (a.name ?? "").localeCompare(b.name ?? "") * d;
      }
    });

    setTotalFiltered(list.length);
    const startIdx = (page - 1) * PAGE_SIZE;
    return list.slice(startIdx, startIdx + PAGE_SIZE);
  }, [products, filterStr, brandFilter, categoryFilter, cfpOnly, sortField, sortDir, page]);

  const totalPages = Math.max(1, Math.ceil(totalFiltered / PAGE_SIZE));

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir(d => d === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDir("asc");
    }
  };

  // ── Column header ────────────────────────────────────────────────────────────
  const ColHeader: React.FC<{ field?: SortField; children: React.ReactNode; className?: string }> = ({ field, children, className = "" }) => (
    <th
      onClick={field ? () => toggleSort(field) : undefined}
      className={`
        px-4 py-2.5 text-left text-[11px] font-medium text-zinc-500 uppercase tracking-wider
        border-b border-zinc-900 whitespace-nowrap
        ${field ? "cursor-pointer hover:text-zinc-300 select-none" : ""}
        ${className}
      `}
    >
      <span className="inline-flex items-center gap-1.5">
        {children}
        {field && <SortIcon field={field} active={sortField} dir={sortDir} />}
      </span>
    </th>
  );

  // ── Loading skeleton ─────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="p-6">
        <div className="h-8 w-48 rounded-lg bg-zinc-900 animate-pulse mb-6" />
        <div className="rounded-xl border border-zinc-900 overflow-hidden">
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="flex items-center gap-4 px-4 py-3 border-b border-zinc-900 last:border-0">
              <div className="w-8 h-8 rounded bg-zinc-900 animate-pulse shrink-0" />
              <div className="flex-1 space-y-1.5">
                <div className="h-3.5 w-48 rounded bg-zinc-900 animate-pulse" />
                <div className="h-2.5 w-24 rounded bg-zinc-900 animate-pulse" />
              </div>
              <div className="h-3.5 w-20 rounded bg-zinc-900 animate-pulse" />
              <div className="h-5 w-16 rounded bg-zinc-900 animate-pulse" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  // ── Error state ──────────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="p-8">
        <div className="flex items-center gap-3 p-4 rounded-xl bg-red-950/20 border border-red-900/40 max-w-lg">
          <AlertTriangle size={14} className="text-red-400 shrink-0" />
          <p className="text-sm text-red-300">Failed to load catalog</p>
          <button onClick={() => refetch()} className="ml-auto text-xs text-zinc-400 hover:text-zinc-200 underline">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* ── Toolbar ── */}
      <div className="flex items-center gap-2.5 px-5 py-3 border-b border-zinc-900 bg-[#0a0a0a] shrink-0 flex-wrap">
        {/* Count label */}
        <span className="text-[11px] text-zinc-600 font-medium mr-1">
          {totalFiltered.toLocaleString()} results
        </span>

        {/* Search */}
        <div className="relative">
          <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-zinc-600 pointer-events-none" />
          <input
            type="text"
            placeholder="Search name, SKU, brand…"
            value={filterText}
            onChange={e => setFilterText(e.target.value)}
            className="h-7 pl-7 pr-3 text-xs bg-zinc-900 border border-zinc-800 rounded-md text-zinc-200
              placeholder:text-zinc-700 focus:outline-none focus:border-blue-800 focus:bg-zinc-900 w-52"
          />
        </div>

        {/* Brand filter */}
        <select
          value={brandFilter}
          onChange={e => setBrandFilter(e.target.value)}
          className="h-7 px-2 text-xs bg-zinc-900 border border-zinc-800 rounded-md text-zinc-400
            focus:outline-none focus:border-blue-800"
        >
          <option value="">All brands</option>
          {brands.map(b => <option key={b} value={b}>{b}</option>)}
        </select>

        {/* Category filter */}
        <select
          value={categoryFilter}
          onChange={e => setCategoryFilter(e.target.value)}
          className="h-7 px-2 text-xs bg-zinc-900 border border-zinc-800 rounded-md text-zinc-400
            focus:outline-none focus:border-blue-800"
        >
          <option value="">All categories</option>
          {categories.map(c => <option key={c} value={c}>{c}</option>)}
        </select>

        {/* CfP toggle */}
        <button
          aria-pressed={cfpOnly}
          onClick={() => setCfpOnly(v => !v)}
          className={`h-7 px-3 text-xs rounded-md border font-medium transition-all ${
            cfpOnly
              ? "bg-amber-500/15 border-amber-700/50 text-amber-400"
              : "bg-zinc-900 border-zinc-800 text-zinc-500 hover:text-zinc-300"
          }`}
        >
          📞 Call for Price
        </button>

        {/* Sort select */}
        <select
          value={`${sortField}:${sortDir}`}
          onChange={e => {
            const [f, d] = e.target.value.split(":") as [SortField, SortDir];
            setSortField(f);
            setSortDir(d);
          }}
          className="h-7 px-2 text-xs bg-zinc-900 border border-zinc-800 rounded-md text-zinc-400
            focus:outline-none focus:border-blue-800 ml-auto"
        >
          <option value="name:asc">Name A→Z</option>
          <option value="name:desc">Name Z→A</option>
          <option value="id:asc">SKU A→Z</option>
          <option value="id:desc">SKU Z→A</option>
          <option value="brand:asc">Brand A→Z</option>
          <option value="price:asc">Price Low→High</option>
          <option value="price:desc">Price High→Low</option>
        </select>
      </div>

      {/* ── Table ── */}
      <div className="flex-1 overflow-auto">
        <table className="w-full border-collapse text-sm">
          <thead className="sticky top-0 bg-[#0a0a0a] z-10">
            <tr>
              <th className="w-10 border-b border-zinc-900" />
              <ColHeader field="name">Product</ColHeader>
              <ColHeader field="id">SKU</ColHeader>
              <ColHeader field="brand">Brand</ColHeader>
              <ColHeader>Category</ColHeader>
              <ColHeader field="price">Price (IL)</ColHeader>
              <ColHeader>Price (Eilat)</ColHeader>
              <ColHeader>Stock</ColHeader>
            </tr>
          </thead>
          <tbody>
            {pagedProducts.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-16 text-center">
                  <div className="flex flex-col items-center gap-3">
                    <Package size={28} className="text-zinc-800" />
                    <p className="text-sm text-zinc-600">No products match your filters.</p>
                  </div>
                </td>
              </tr>
            ) : (
              pagedProducts.map(item => (
                <ProductRow key={item.id} item={item} onSelect={() => goToProduct(item.id)} />
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* ── Pagination ── */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-5 py-2.5 border-t border-zinc-900 bg-[#0a0a0a] shrink-0">
          <span className="text-xs text-zinc-600">
            Page {page} of {totalPages} · {totalFiltered.toLocaleString()} results
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="h-6 px-3 text-xs rounded border border-zinc-800 bg-zinc-900 text-zinc-400
                hover:text-zinc-200 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Prev
            </button>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="h-6 px-3 text-xs rounded border border-zinc-800 bg-zinc-900 text-zinc-400
                hover:text-zinc-200 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// ── ProductRow ─────────────────────────────────────────────────────────────────
const ProductRow: React.FC<{ item: ConductorProduct; onSelect: () => void }> = ({ item, onSelect }) => {
  const isOos = item.stock === 0;

  const isCfp = item.price == null || item.price === 0;
  const displayIlPrice = isCfp
    ? <span className="text-amber-400 font-medium">CfP</span>
    : <span>₪{(item.price ?? 0).toLocaleString()}</span>;

  const displayEilatPrice = item.price_eilat
    ? <span>₪{item.price_eilat.toLocaleString()}</span>
    : <span className="text-zinc-700">—</span>;

  return (
    <tr
      role="button"
      tabIndex={0}
      onClick={onSelect}
      onKeyDown={e => (e.key === "Enter" || e.key === " ") && onSelect()}
      className={`
        border-b border-zinc-900/60 cursor-pointer transition-colors
        hover:bg-zinc-900/40 focus:outline-none focus:bg-zinc-900/60
        ${isOos ? "bg-red-950/5" : ""}
      `}
    >
      {/* Thumb */}
      <td className="pl-4 pr-2 py-2.5 w-10">
        <div className="w-8 h-8 rounded bg-zinc-900 overflow-hidden shrink-0">
          {item.image_url ? (
            <img
              src={item.image_url}
              alt=""
              className="w-full h-full object-contain"
              onError={(e) => { (e.target as HTMLImageElement).style.opacity = "0"; }}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Package size={12} className="text-zinc-700" />
            </div>
          )}
        </div>
      </td>

      {/* Name */}
      <td className="px-4 py-2.5 max-w-[280px]">
        <span className="block text-sm text-zinc-200 font-medium truncate">{item.name}</span>
      </td>

      {/* SKU */}
      <td className="px-4 py-2.5 whitespace-nowrap">
        <span className="font-mono text-xs text-zinc-500 inline-flex items-center gap-1.5">
          {item.id}
          {item.official_url && (
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" title="Official URL verified" />
          )}
        </span>
      </td>

      {/* Brand */}
      <td className="px-4 py-2.5">
        <span className="text-xs text-zinc-400">{item.brand}</span>
      </td>

      {/* Category */}
      <td className="px-4 py-2.5">
        <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] bg-zinc-900 text-zinc-500 border border-zinc-800">
          {item.subcategory ?? item.category ?? "General"}
        </span>
      </td>

      {/* IL Price */}
      <td className="px-4 py-2.5 text-sm">{displayIlPrice}</td>

      {/* Eilat Price */}
      <td className="px-4 py-2.5 text-sm text-zinc-400">{displayEilatPrice}</td>

      {/* Stock */}
      <td className="px-4 py-2.5">
        <StockBadge stock={item.stock} />
      </td>
    </tr>
  );
};

export default InventoryView;
