/**
 * Structured Items View — brand → type → series with variants, accessories, related.
 * Large hero images and product thumbnails; click any product to open Product Page (switch to interconnected product).
 */
import React, { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigationStore } from "../../store/navigationStore";
import { ChevronRight, Package, Grid3X3, Layers } from "lucide-react";

const API_BASE =
  (typeof import.meta !== "undefined" &&
    (import.meta as unknown as { env?: { VITE_API_ORIGIN?: string } }).env?.VITE_API_ORIGIN) ||
  "";

interface ProductSummary {
  id: string;
  name: string;
  image_url: string;
  price?: number;
  brand?: string;
}

interface Family {
  family_id: string;
  family_name: string;
  hero_image: string;
  variant_count: number;
  variants: { id: string; name: string; image_url: string; price: number }[];
}

interface SeriesItem {
  series_key: string;
  series_label: string;
  families: Family[];
  variant_ids: string[];
  direct_accessory_ids: string[];
  related_ids: string[];
}

interface TypeItem {
  galaxy_id: string;
  galaxy_label: string;
  spectrum_id: string;
  spectrum_label: string;
  series: SeriesItem[];
}

interface BrandItem {
  brand: string;
  brand_key: string;
  types: TypeItem[];
}

interface StructuredItemsResponse {
  galaxies: unknown[];
  brands: BrandItem[];
  products_by_id: Record<string, ProductSummary>;
}

async function fetchStructuredItems(): Promise<StructuredItemsResponse> {
  const url = API_BASE ? `${API_BASE}/api/structured-items` : "/api/structured-items";
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Structured items failed: ${res.status}`);
  return res.json();
}

function ThumbnailStrip({
  ids,
  productsById,
  onSelect,
  label,
}: {
  ids: string[];
  productsById: Record<string, ProductSummary>;
  onSelect: (id: string) => void;
  label: string;
}) {
  const items = useMemo(
    () => ids.map((id) => productsById[id]).filter(Boolean).slice(0, 12),
    [ids, productsById]
  );
  if (items.length === 0) return null;
  return (
    <div className="mt-3">
      <p className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider mb-2">
        {label}
      </p>
      <div className="flex flex-wrap gap-2">
        {items.map((p) => (
          <button
            key={p.id}
            type="button"
            onClick={() => onSelect(p.id)}
            className="w-14 h-14 rounded-lg overflow-hidden bg-zinc-800/80 border border-zinc-700/60 hover:border-blue-500/60 focus-visible:ring-2 focus-visible:ring-blue-500 shrink-0 transition-colors"
            title={p.name}
          >
            {p.image_url ? (
              <img
                src={p.image_url}
                alt=""
                className="w-full h-full object-cover"
                loading="lazy"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-zinc-600 text-[10px]">
                —
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

function SeriesCard({
  item,
  productsById,
  onOpenProduct,
}: {
  item: SeriesItem;
  productsById: Record<string, ProductSummary>;
  onOpenProduct: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const heroFamily = item.families[0];
  const heroImage = heroFamily?.hero_image || heroFamily?.variants?.[0]?.image_url;

  return (
    <article
      className="rounded-xl border border-zinc-800/80 bg-zinc-900/60 overflow-hidden"
      data-series={item.series_key}
    >
      <button
        type="button"
        onClick={() => setExpanded((e) => !e)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-zinc-800/40 transition-colors focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-blue-500"
      >
        <div className="flex items-center gap-3 min-w-0">
          {heroImage ? (
            <div className="w-16 h-16 rounded-lg overflow-hidden bg-zinc-800 shrink-0">
              <img
                src={heroImage}
                alt=""
                className="w-full h-full object-cover"
                loading="lazy"
              />
            </div>
          ) : (
            <div className="w-16 h-16 rounded-lg bg-zinc-800 shrink-0 flex items-center justify-center">
              <Package className="w-6 h-6 text-zinc-600" />
            </div>
          )}
          <div className="min-w-0">
            <h3 className="font-semibold text-white truncate">{item.series_label}</h3>
            <p className="text-xs text-zinc-500">
              {item.families.length} family · {item.variant_ids.length} variants
            </p>
          </div>
        </div>
        <ChevronRight
          className={`w-5 h-5 text-zinc-500 shrink-0 transition-transform ${expanded ? "rotate-90" : ""}`}
        />
      </button>
      {expanded && (
        <div className="px-4 pb-4 pt-0 border-t border-zinc-800/60">
          {/* Variants */}
          <ThumbnailStrip
            ids={item.variant_ids}
            productsById={productsById}
            onSelect={onOpenProduct}
            label="Variants"
          />
          <ThumbnailStrip
            ids={item.direct_accessory_ids}
            productsById={productsById}
            onSelect={onOpenProduct}
            label="Accessories"
          />
          <ThumbnailStrip
            ids={item.related_ids}
            productsById={productsById}
            onSelect={onOpenProduct}
            label="Related"
          />
        </div>
      )}
    </article>
  );
}

export const ItemsView = () => {
  const { goToGalaxy, openProductPage } = useNavigationStore();
  const [selectedBrandKey, setSelectedBrandKey] = useState<string | null>(null);
  const hasInitialBrand = React.useRef(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ["structured-items"],
    queryFn: fetchStructuredItems,
    staleTime: 5 * 60 * 1000,
  });

  const brands = data?.brands ?? [];
  const productsById = data?.products_by_id ?? {};
  React.useEffect(() => {
    if (brands.length > 0 && !hasInitialBrand.current) {
      hasInitialBrand.current = true;
      setSelectedBrandKey(brands[0].brand_key);
    }
  }, [brands]);
  const selectedBrand = useMemo(
    () => brands.find((b) => b.brand_key === selectedBrandKey) ?? brands[0],
    [brands, selectedBrandKey]
  );

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center bg-black/80">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-2 border-zinc-700 border-t-blue-500 animate-spin" />
          <p className="text-sm text-zinc-500">Loading structured items…</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="h-full flex items-center justify-center bg-black/80 p-6">
        <div className="text-center max-w-md">
          <p className="text-zinc-400 mb-4">Could not load items. Check backend and try again.</p>
          <button
            type="button"
            onClick={goToGalaxy}
            className="px-4 py-2 rounded-lg bg-zinc-800 text-white hover:bg-zinc-700 focus-visible:ring-2 focus-visible:ring-blue-500"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-black/90 overflow-hidden">
      <div className="shrink-0 flex items-center justify-between gap-4 px-6 py-4 border-b border-zinc-800/60">
        <div className="flex items-center gap-2">
          <Layers className="w-5 h-5 text-blue-400" aria-hidden />
          <h1 className="text-lg font-semibold text-white">Structured Items</h1>
        </div>
        <button
          type="button"
          onClick={goToGalaxy}
          className="text-sm text-zinc-500 hover:text-white focus-visible:ring-2 focus-visible:ring-blue-500 rounded px-2 py-1"
        >
          ← Dashboard
        </button>
      </div>

      <div className="flex-1 flex min-h-0">
        {/* Brand sidebar */}
        <aside className="w-52 shrink-0 border-r border-zinc-800/60 overflow-y-auto py-2">
          {brands.map((b) => (
            <button
              key={b.brand_key}
              type="button"
              onClick={() => setSelectedBrandKey(b.brand_key)}
              className={`w-full text-left px-4 py-2.5 text-sm focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-blue-500 ${
                selectedBrandKey === b.brand_key
                  ? "bg-blue-500/20 text-white font-medium border-l-2 border-blue-500"
                  : "text-zinc-400 hover:bg-zinc-800/60 hover:text-white border-l-2 border-transparent"
              }`}
            >
              {b.brand}
            </button>
          ))}
        </aside>

        {/* Type → Series content */}
        <main className="flex-1 overflow-y-auto p-6">
          {selectedBrand && (
            <>
              <h2 className="text-xl font-semibold text-white mb-2 flex items-center gap-2">
                <Grid3X3 className="w-5 h-5 text-zinc-500" />
                {selectedBrand.brand}
              </h2>
              <p className="text-xs text-zinc-500 mb-6">
                Brand → type → series. Expand a series to see variants, accessories, and related;
                click any product to open it.
              </p>
              <div className="space-y-4">
                {selectedBrand.types.map((t) => (
                  <section key={t.spectrum_id || "uncategorized"} className="space-y-3">
                    <h3 className="text-sm font-semibold text-zinc-400 flex items-center gap-2">
                      {t.galaxy_label} → {t.spectrum_label}
                    </h3>
                    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                      {t.series.map((s) => (
                        <SeriesCard
                          key={s.series_key}
                          item={s}
                          productsById={productsById}
                          onOpenProduct={openProductPage}
                        />
                      ))}
                    </div>
                  </section>
                ))}
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
};
