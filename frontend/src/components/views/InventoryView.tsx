/**
 * Inventory View — Operator Console
 * Data grid powered by useConductorCatalog with filter and product navigation.
 */
import React, { useMemo, useState, useEffect } from "react";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import { useNavigationStore } from "../../store/navigationStore";
import { PackageOpen, Filter } from "lucide-react";
import type { ConductorProduct } from "../../hooks/useConductorCatalog";

const InventoryView: React.FC = () => {
  const { products, isLoading, error, refetch } = useConductorCatalog();
  const { goToProduct, goToIngestionStatus, searchQuery, setSearchQuery } = useNavigationStore();
  const [filterText, setFilterText] = useState(searchQuery || "");
  
  // Sync filterText with searchQuery from navigation store
  useEffect(() => {
    if (searchQuery) {
      setFilterText(searchQuery);
    }
  }, [searchQuery]);

  const filteredProducts = useMemo(() => {
    if (!filterText) return products;
    const lower = filterText.toLowerCase();
    return products.filter(
      (p) =>
        (p.name ?? "").toLowerCase().includes(lower) ||
        (p.id ?? "").toLowerCase().includes(lower) ||
        (p.brand ?? "").toLowerCase().includes(lower)
    );
  }, [products, filterText]);

  if (isLoading) {
    return (
      <div className="p-8 text-zinc-500 text-sm">
        Loading inventory…
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
      <div className="h-14 border-b border-zinc-800 flex items-center justify-between px-6 shrink-0 bg-zinc-950/50">
        <div className="flex items-center gap-4">
          <h1 className="text-sm font-semibold text-white">All Products</h1>
          <span className="text-xs text-zinc-500 bg-zinc-900 px-2 py-0.5 rounded-full border border-zinc-800">
            {filteredProducts.length} items
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Filter size={14} className="text-zinc-500" aria-hidden />
          <input
            type="text"
            placeholder="Search by name, SKU or brand…"
            className="bg-zinc-900 border border-zinc-800 rounded px-3 py-1.5 text-xs text-zinc-200 w-72 focus:outline-none focus:border-blue-500 transition-colors"
            value={filterText}
            onChange={(e) => setFilterText(e.target.value)}
            aria-label="Filter products"
          />
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        <table className="w-full text-left border-collapse">
          <thead className="sticky top-0 bg-zinc-950/95 backdrop-blur z-10 border-b border-zinc-800 shadow-sm">
            <tr>
              <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase w-[40%]">
                Product Name
              </th>
              <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase">Brand</th>
              <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase">Category</th>
              <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase text-right">
                Price (IL)
              </th>
              <th className="px-6 py-3 text-xs font-medium text-zinc-500 uppercase text-right">
                Eilat
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/50">
            {filteredProducts.map((item: ConductorProduct) => (
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
                className="hover:bg-blue-900/10 cursor-pointer group transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-inset"
              >
                <td className="px-6 py-3">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded bg-white p-1 flex-shrink-0 border border-zinc-800 overflow-hidden">
                      <img
                        src={item.image_url || "/placeholder.png"}
                        alt=""
                        className="w-full h-full object-contain"
                        loading="lazy"
                        onError={(e) => {
                          e.currentTarget.style.opacity = "0.2";
                        }}
                      />
                    </div>
                    <div className="min-w-0">
                      <div className="text-sm font-medium text-zinc-200 group-hover:text-blue-400 truncate max-w-md transition-colors">
                        {item.name}
                      </div>
                      <div className="text-[10px] text-zinc-600 font-mono flex items-center gap-2">
                        {item.id}
                        {item.official_url && (
                          <span
                            className="w-1.5 h-1.5 rounded-full bg-emerald-500/50"
                            title="Verified Link"
                            aria-hidden
                          />
                        )}
                      </div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-3 text-xs text-zinc-400 font-medium">{item.brand}</td>
                <td className="px-6 py-3">
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-zinc-900 text-zinc-500 border border-zinc-800">
                    {item.subcategory || item.category || "General"}
                  </span>
                </td>
                <td className="px-6 py-3 text-right text-sm font-mono text-zinc-300">
                  {item.price != null ? `₪${item.price.toLocaleString()}` : "—"}
                </td>
                <td className="px-6 py-3 text-right text-sm font-mono text-zinc-500">
                  {item.price_eilat != null ? `₪${item.price_eilat.toLocaleString()}` : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredProducts.length === 0 && (
          <div className="flex flex-col items-center justify-center h-96 text-zinc-600 gap-3">
            <div className="w-16 h-16 bg-zinc-900 rounded-full flex items-center justify-center">
              <PackageOpen size={32} className="opacity-40" aria-hidden />
            </div>
            <span className="text-sm">
              No products found matching &quot;{filterText}&quot;
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default InventoryView;
export { InventoryView };
