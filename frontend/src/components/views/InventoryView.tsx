/**
 * Inventory View (Operator Console) — Data grid for products with price (IL/Eilat), brand, category.
 * Optimized for information density and quick scanning.
 */
import React from "react";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import { useNavigationStore } from "../../store/navigationStore";
import type { ConductorProduct } from "../../hooks/useConductorCatalog";
import { Filter, ArrowUpDown } from "lucide-react";

interface DataTableProps {
  data: ConductorProduct[];
  onRowClick: (id: string) => void;
}

const DataTable: React.FC<DataTableProps> = ({ data, onRowClick }) => {
  return (
    <div className="w-full text-left border-collapse">
      <div className="grid grid-cols-12 gap-4 px-6 py-3 border-b border-zinc-800 bg-zinc-900/50 text-xs font-medium text-zinc-500 uppercase tracking-wider sticky top-0 backdrop-blur-md z-10">
        <div className="col-span-4 flex items-center gap-2 cursor-pointer hover:text-zinc-300">
          Product Name <ArrowUpDown size={12} aria-hidden />
        </div>
        <div className="col-span-2">Brand</div>
        <div className="col-span-2">Category</div>
        <div className="col-span-2 text-right">Price (IL)</div>
        <div className="col-span-2 text-right">Eilat</div>
      </div>

      <div className="divide-y divide-zinc-800/50">
        {data.map((item) => (
          <div
            key={item.id}
            role="button"
            tabIndex={0}
            onClick={() => onRowClick(item.id)}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onRowClick(item.id);
              }
            }}
            className="grid grid-cols-12 gap-4 px-6 py-3 items-center hover:bg-blue-900/10 cursor-pointer group transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-inset"
          >
            <div className="col-span-4 flex items-center gap-3">
              <div className="w-8 h-8 rounded bg-zinc-800 overflow-hidden flex-shrink-0">
                {item.image_url ? (
                  <img
                    src={item.image_url}
                    alt=""
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-[10px] font-mono text-zinc-500">
                    —
                  </div>
                )}
              </div>
              <div className="min-w-0">
                <div className="text-sm font-medium text-zinc-200 truncate group-hover:text-blue-400 transition-colors">
                  {item.name}
                </div>
                <div className="text-[10px] text-zinc-500 font-mono">{item.id}</div>
              </div>
            </div>

            <div className="col-span-2 text-xs text-zinc-400">{item.brand}</div>
            <div className="col-span-2">
              <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-zinc-800 text-zinc-400 border border-zinc-700">
                {item.subcategory || "General"}
              </span>
            </div>

            <div className="col-span-2 text-right text-sm font-mono text-zinc-300">
              ₪{item.price?.toLocaleString() ?? "—"}
            </div>
            <div className="col-span-2 text-right text-sm font-mono text-zinc-500">
              ₪{item.price_eilat?.toLocaleString() ?? "—"}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export const InventoryView: React.FC = () => {
  const { products, isLoading } = useConductorCatalog();
  const { openProductPage } = useNavigationStore();

  if (isLoading) {
    return (
      <div className="flex flex-col h-full">
        <div className="h-16 border-b border-zinc-800 flex items-center px-6 shrink-0 bg-zinc-950">
          <h1 className="text-lg font-semibold text-white">Inventory</h1>
        </div>
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="flex flex-col items-center gap-3">
            <div
              className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"
              aria-hidden
            />
            <span className="text-sm text-zinc-500">Loading inventory…</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="h-16 border-b border-zinc-800 flex items-center justify-between px-6 shrink-0 bg-zinc-950">
        <div className="flex items-center gap-4">
          <h1 className="text-lg font-semibold text-white">Inventory</h1>
          <div className="h-4 w-px bg-zinc-800" aria-hidden />
          <span className="text-xs text-zinc-500">{products.length} items active</span>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            className="flex items-center gap-2 px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded text-xs font-medium text-zinc-400 hover:text-white hover:border-zinc-700 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500"
          >
            <Filter size={14} aria-hidden />
            Filter
          </button>
          <button
            type="button"
            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-medium transition-colors focus-visible:ring-2 focus-visible:ring-blue-500"
          >
            Add Product
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-auto">
        <DataTable data={products} onRowClick={openProductPage} />
      </div>
    </div>
  );
};

export default InventoryView;
