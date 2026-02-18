/**
 * Inventory View — Inventory Master
 * Spec: specs/interface/02_inventory_grid.md
 * Features: columns (SKU, Title, Brand, Category, IL Price, Eilat Price, Stock Status),
 *   sort (name/SKU/price asc-desc/brand), filters (brand, category, CfP toggle, text search),
 *   pagination (50/page), row click → Product Detail.
 */
import React, { useMemo, useState, useEffect } from "react";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import { useNavigationStore } from "../../store/navigationStore";
import {
  PackageOpen,
  ChevronDown,
  ChevronUp,
  ChevronsUpDown,
  PhoneCall,
} from "lucide-react";
import type { ConductorProduct } from "../../hooks/useConductorCatalog";

const PAGE_SIZE = 50;

type SortField = "name" | "id" | "price" | "brand";
type SortDir = "asc" | "desc";

function getStock(item: ConductorProduct): number | null {
  const s = (item as unknown as Record<string, unknown>)["stock"];
  return typeof s === "number" ? s : null;
}

function StockBadge({ item }: { item: ConductorProduct }) {
  const stock = getStock(item);
  if (stock === null)
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-zinc-900 text-zinc-500 border border-zinc-800">
        Unknown
      </span>
    );
  if (stock === 0)
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-red-900/30 text-red-400 border border-red-900/40">
        Out of Stock
      </span>
    );
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-900/20 text-emerald-400 border border-emerald-900/30">
      In Stock
    </span>
  );
}

function SortIcon({
  field,
  sortField,
  sortDir,
}: {
  field: SortField;
  sortField: SortField;
  sortDir: SortDir;
}) {
  if (sortField !== field)
    return (
      <ChevronsUpDown
        size={12}
        className="text-zinc-600 inline ml-1"
        aria-hidden
      />
    );
  return sortDir === "asc" ? (
    <ChevronUp size={12} className="text-blue-400 inline ml-1" aria-hidden />
  ) : (
    <ChevronDown size={12} className="text-blue-400 inline ml-1" aria-hidden />
  );
}

const InventoryView: React.FC = () => {
  const { products, isLoading, error, refetch } = useConductorCatalog();
  const { goToProduct, goToIngestionStatus, searchQuery, setSearchQuery } =
    useNavigationStore();
  const [filterText, setFilterText] = useState(searchQuery || "");
  const [brandFilter, setBrandFilter] = useState<string>("");
  const [categoryFilter, setCategoryFilter] = useState<string>("");
  const [cfpOnly, setCfpOnly] = useState(false);
  const [sortField, setSortField] = useState<SortField>("name");
  const [sortDir, setSortDir] = useState<SortDir>("asc");
  const [page, setPage] = useState(1);

  // Sync filterText with searchQuery from navigation store
  useEffect(() => {
    if (searchQuery !== null) {
      setFilterText(searchQuery);
      if (searchQuery === "") setSearchQuery(null);
    }
  }, [searchQuery, setSearchQuery]);

  // Reset page when filters change
  useEffect(() => {
    setPage(1);
  }, [filterText, brandFilter, categoryFilter, cfpOnly, sortField, sortDir]);

  // Build unique brand / category lists
  const brandOptions = useMemo(
    () =>
      Array.from(new Set(products.map((p) => p.brand).filter(Boolean))).sort(),
    [products],
  );
  const categoryOptions = useMemo(
    () =>
      Array.from(
        new Set(products.map((p) => p.category || "General").filter(Boolean)),
      ).sort(),
    [products],
  );

  // Filter
  const filtered = useMemo(() => {
    let list = products;
    if (filterText) {
      const lower = filterText.toLowerCase();
      list = list.filter(
        (p) =>
          (p.name ?? "").toLowerCase().includes(lower) ||
          (p.id ?? "").toLowerCase().includes(lower) ||
          (p.brand ?? "").toLowerCase().includes(lower),
      );
    }
    if (brandFilter) list = list.filter((p) => p.brand === brandFilter);
    if (categoryFilter)
      list = list.filter((p) => (p.category || "General") === categoryFilter);
    if (cfpOnly) list = list.filter((p) => p.price == null || p.price === 0);
    return list;
  }, [products, filterText, brandFilter, categoryFilter, cfpOnly]);

  // Sort
  const sorted = useMemo(() => {
    return [...filtered].sort((a, b) => {
      let cmp = 0;
      if (sortField === "name")
        cmp = (a.name ?? "").localeCompare(b.name ?? "");
      else if (sortField === "id") cmp = (a.id ?? "").localeCompare(b.id ?? "");
      else if (sortField === "brand")
        cmp = (a.brand ?? "").localeCompare(b.brand ?? "");
      else if (sortField === "price") {
        // Missing price → bottom
        const ap = a.price ?? Number.MAX_VALUE;
        const bp = b.price ?? Number.MAX_VALUE;
        cmp = ap - bp;
      }
      return sortDir === "asc" ? cmp : -cmp;
    });
  }, [filtered, sortField, sortDir]);

  // Paginate
  const totalPages = Math.max(1, Math.ceil(sorted.length / PAGE_SIZE));
  const pageItems = sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  function toggleSort(field: SortField) {
    if (sortField === field) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortField(field);
      setSortDir("asc");
    }
  }

  function thCls(field: SortField) {
    return `px-4 py-3 text-xs font-medium text-zinc-500 uppercase cursor-pointer select-none hover:text-zinc-300 transition-colors${sortField === field ? " text-blue-400" : ""}`;
  }

  if (isLoading) {
    return (
      <div className="flex flex-col h-full">
        <div className="h-14 border-b border-zinc-800 bg-zinc-950/50 flex items-center px-6">
          <div className="h-4 w-32 bg-zinc-800 rounded animate-pulse" />
        </div>
        <div className="flex-1 p-6 space-y-2">
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="h-12 bg-zinc-900 rounded animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 max-w-xl">
        <div className="bg-amber-900/20 border border-amber-500/30 rounded-xl p-6">
          <p className="text-amber-400 font-medium mb-2">Catalog unavailable</p>
          <p className="text-sm text-zinc-400 mb-4">{error}</p>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => refetch()}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg"
            >
              Retry
            </button>
            <button
              type="button"
              onClick={goToIngestionStatus}
              className="px-4 py-2 bg-zinc-700 hover:bg-zinc-600 text-zinc-200 text-sm font-medium rounded-lg"
            >
              Ingestion Status
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="border-b border-zinc-800 bg-zinc-950/50 px-4 py-2 shrink-0 flex flex-wrap items-center gap-2">
        <span className="text-xs font-semibold text-zinc-400 mr-1">
          {sorted.length.toLocaleString()} items
        </span>

        {/* Text search */}
        <input
          type="text"
          placeholder="Search by name, SKU or brand…"
          className="bg-zinc-900 border border-zinc-800 rounded px-3 py-1.5 text-xs text-zinc-200 w-60 focus:outline-none focus:border-blue-500 transition-colors"
          value={filterText}
          onChange={(e) => {
            setFilterText(e.target.value);
            if (searchQuery !== null) setSearchQuery(null);
          }}
          aria-label="Filter products"
        />

        {/* Brand filter */}
        <select
          value={brandFilter}
          onChange={(e) => setBrandFilter(e.target.value)}
          className="bg-zinc-900 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-300 focus:outline-none focus:border-blue-500 transition-colors"
          aria-label="Filter by brand"
        >
          <option value="">All Brands</option>
          {brandOptions.map((b) => (
            <option key={b} value={b}>
              {b}
            </option>
          ))}
        </select>

        {/* Category filter */}
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="bg-zinc-900 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-300 focus:outline-none focus:border-blue-500 transition-colors"
          aria-label="Filter by category"
        >
          <option value="">All Categories</option>
          {categoryOptions.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>

        {/* CfP toggle */}
        <button
          type="button"
          onClick={() => setCfpOnly((v) => !v)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium border transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 ${
            cfpOnly
              ? "bg-amber-500/10 border-amber-500/40 text-amber-400"
              : "bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-zinc-200"
          }`}
          aria-pressed={cfpOnly}
        >
          <PhoneCall size={12} aria-hidden /> Call for Price
        </button>

        {/* Sort */}
        <select
          value={`${sortField}:${sortDir}`}
          onChange={(e) => {
            const [f, d] = e.target.value.split(":") as [SortField, SortDir];
            setSortField(f);
            setSortDir(d);
          }}
          className="ml-auto bg-zinc-900 border border-zinc-800 rounded px-2 py-1.5 text-xs text-zinc-300 focus:outline-none focus:border-blue-500 transition-colors"
          aria-label="Sort products"
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

      {/* Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full text-left border-collapse">
          <thead className="sticky top-0 bg-zinc-950/95 backdrop-blur z-10 border-b border-zinc-800 shadow-sm">
            <tr>
              <th
                className={thCls("name") + " w-[30%]"}
                onClick={() => toggleSort("name")}
              >
                Product Name{" "}
                <SortIcon
                  field="name"
                  sortField={sortField}
                  sortDir={sortDir}
                />
              </th>
              <th className={thCls("id")} onClick={() => toggleSort("id")}>
                SKU{" "}
                <SortIcon field="id" sortField={sortField} sortDir={sortDir} />
              </th>
              <th
                className={thCls("brand")}
                onClick={() => toggleSort("brand")}
              >
                Brand{" "}
                <SortIcon
                  field="brand"
                  sortField={sortField}
                  sortDir={sortDir}
                />
              </th>
              <th className="px-4 py-3 text-xs font-medium text-zinc-500 uppercase">
                Category
              </th>
              <th
                className={thCls("price") + " text-right"}
                onClick={() => toggleSort("price")}
              >
                Price (IL){" "}
                <SortIcon
                  field="price"
                  sortField={sortField}
                  sortDir={sortDir}
                />
              </th>
              <th className="px-4 py-3 text-xs font-medium text-zinc-500 uppercase text-right">
                Eilat
              </th>
              <th className="px-4 py-3 text-xs font-medium text-zinc-500 uppercase">
                Stock
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/50">
            {pageItems.map((item: ConductorProduct) => {
              const stock = getStock(item);
              const isOos = stock === 0;
              return (
                <tr
                  key={item.id}
                  onClick={() => goToProduct(item.id)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      goToProduct(item.id);
                    }
                  }}
                  role="button"
                  tabIndex={0}
                  className={`hover:bg-blue-900/10 cursor-pointer group transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-inset ${isOos ? "bg-red-950/10" : ""}`}
                >
                  {/* Title + image */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded bg-white p-1 flex-shrink-0 border border-zinc-800 overflow-hidden">
                        <img
                          src={
                            item.image_url ||
                            "/assets/images/placeholder_product.svg"
                          }
                          alt={item.name || "Product image"}
                          className="w-full h-full object-contain"
                          loading="lazy"
                          onError={(e) => {
                            e.currentTarget.style.opacity = "0.2";
                          }}
                        />
                      </div>
                      <div className="min-w-0">
                        <div className="text-sm font-medium text-zinc-200 group-hover:text-blue-400 truncate max-w-xs transition-colors">
                          {item.name}
                        </div>
                      </div>
                    </div>
                  </td>
                  {/* SKU */}
                  <td className="px-4 py-3 text-[11px] font-mono text-zinc-400">
                    {item.id}
                    {item.official_url && (
                      <span
                        className="ml-1.5 w-1.5 h-1.5 inline-block rounded-full bg-emerald-500/50"
                        title="Verified Link"
                        aria-hidden
                      />
                    )}
                  </td>
                  {/* Brand */}
                  <td className="px-4 py-3 text-xs text-zinc-400 font-medium">
                    {item.brand}
                  </td>
                  {/* Category */}
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-zinc-900 text-zinc-500 border border-zinc-800">
                      {item.subcategory || item.category || "General"}
                    </span>
                  </td>
                  {/* Price IL */}
                  <td className="px-4 py-3 text-right text-sm font-mono text-zinc-300">
                    {item.price != null && item.price > 0 ? (
                      `₪${item.price.toLocaleString()}`
                    ) : (
                      <span className="text-amber-500/80 text-[10px] font-semibold">
                        CfP
                      </span>
                    )}
                  </td>
                  {/* Price Eilat */}
                  <td className="px-4 py-3 text-right text-sm font-mono text-zinc-500">
                    {item.price_eilat != null && item.price_eilat > 0
                      ? `₪${item.price_eilat.toLocaleString()}`
                      : "—"}
                  </td>
                  {/* Stock */}
                  <td className="px-4 py-3">
                    <StockBadge item={item} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {sorted.length === 0 && (
          <div className="flex flex-col items-center justify-center h-72 text-zinc-600 gap-3">
            <div className="w-16 h-16 bg-zinc-900 rounded-full flex items-center justify-center">
              <PackageOpen size={32} className="opacity-40" aria-hidden />
            </div>
            <span className="text-sm">
              No products match. Adjust filters or search.
            </span>
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="shrink-0 border-t border-zinc-800 bg-zinc-950/50 flex items-center justify-between px-6 py-2">
          <span className="text-xs text-zinc-500">
            Page {page} of {totalPages} · {sorted.length.toLocaleString()}{" "}
            results
          </span>
          <div className="flex gap-2">
            <button
              type="button"
              disabled={page === 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="px-3 py-1 text-xs rounded bg-zinc-800 border border-zinc-700 text-zinc-300 disabled:opacity-30 hover:bg-zinc-700 transition-colors"
            >
              ← Prev
            </button>
            <button
              type="button"
              disabled={page === totalPages}
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              className="px-3 py-1 text-xs rounded bg-zinc-800 border border-zinc-700 text-zinc-300 disabled:opacity-30 hover:bg-zinc-700 transition-colors"
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default InventoryView;
export { InventoryView };
