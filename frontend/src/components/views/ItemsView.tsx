/**
 * Structured Items View — products organized by: 1) Brand, 2) What they are (category), 3) Relations (product lines, variants, accessories, related).
 */
import React, { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigationStore } from "../../store/navigationStore";
import { ChevronRight, Package, Grid3X3, Layers, Search, ArrowLeft, ExternalLink } from "lucide-react";
import { HierarchyBreadcrumb } from "../hierarchy/HierarchyBreadcrumb";

const API_BASE =
  (typeof import.meta !== "undefined" &&
    (import.meta as unknown as { env?: { VITE_API_ORIGIN?: string } }).env?.VITE_API_ORIGIN) ||
  "";

const STORAGE_SELECTED_BRAND_KEY = "items:selectedBrandKey";

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

/** Relations: product lines (series/families), variants, accessories, related */
interface RelationItem {
  series_key: string;
  series_label: string;
  families: Family[];
  variant_ids: string[];
  direct_accessory_ids: string[];
  related_ids: string[];
}

/** Category = what they are (product type, e.g. Keyboards, Drums). Backward compat: relations may be as "series". */
interface CategoryItem {
  galaxy_id: string;
  galaxy_label: string;
  spectrum_id: string;
  spectrum_label: string;
  relations?: RelationItem[];
  series?: RelationItem[];
}

interface BrandItem {
  brand: string;
  brand_key: string;
  /** Hierarchy level 2: what they are (category). Backward compat: types */
  categories?: CategoryItem[];
  types?: CategoryItem[];
}

interface StructuredItemsResponse {
  galaxies: unknown[];
  brands: BrandItem[];
  products_by_id: Record<string, ProductSummary>;
}

async function fetchStructuredItems(): Promise<StructuredItemsResponse> {
  // Prefer hierarchy API (uses DB when populated); falls back to structured-items from JSON
  const url = API_BASE ? `${API_BASE}/api/hierarchy/items` : "/api/hierarchy/items";
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Hierarchy items failed: ${res.status}`);
  return res.json();
}

interface BrandIndexEntry {
  id: string;
  name: string;
  product_count: number;
  verified_count: number;
  data_file: string;
  logo_url?: string | null;
  brand_color?: string | null;
  primary_category?: string | null;
}

interface BrandIndexResponse {
  brands: BrandIndexEntry[];
}

function normalizeBrandIndexEntries(entries: BrandIndexEntry[]): BrandIndexEntry[] {
  // index.json can contain duplicates and invalid placeholders; pick a stable "best" row per id.
  const byId = new Map<string, BrandIndexEntry>();
  for (const raw of entries) {
    const id = (raw.id || "").trim().toLowerCase();
    if (!id) continue;
    const current = byId.get(id);
    const score = (b: BrandIndexEntry) =>
      (b.verified_count ?? 0) * 10_000 + (b.product_count ?? 0);
    if (!current || score(raw) > score(current)) {
      byId.set(id, { ...raw, id });
    }
  }
  return Array.from(byId.values()).sort((a, b) => a.name.localeCompare(b.name));
}

async function fetchBrandIndex(): Promise<BrandIndexResponse> {
  const url = API_BASE ? `${API_BASE}/data/index.json` : "/data/index.json";
  const res = await fetch(`${url}?v=${Date.now()}`);
  if (!res.ok) throw new Error(`Brand index failed: ${res.status}`);
  const data = (await res.json()) as BrandIndexResponse;
  return { brands: normalizeBrandIndexEntries(data.brands ?? []) };
}

const STRIP_LABEL_CONTEXT: Record<string, string> = {
  Variants: "Different models or finishes in this product line — click to open product page",
  "Accessories & parts": "Parts and accessories for this product (e.g. covers, flybars) — click to open product page",
  Accessories: "Compatible accessories for this product — click to open product page",
  Related: "Related or alternative products — click to open product page",
};

function ThumbnailStrip({
  ids,
  productsById,
  onSelect,
  label,
  seriesContext,
}: {
  ids: string[];
  productsById: Record<string, ProductSummary>;
  onSelect: (id: string) => void;
  label: string;
  seriesContext?: string;
}) {
  const items = useMemo(
    () => ids.map((id) => productsById[id]).filter(Boolean).slice(0, 12),
    [ids, productsById]
  );
  if (items.length === 0) return null;
  const contextHint = STRIP_LABEL_CONTEXT[label] ?? "Click to open product page";
  const stripId = `strip-${label.replace(/\s+/g, "-").replace(/&/g, "and").replace(/[^a-z0-9-]/gi, "")}`;
  return (
    <div className="mt-3" role="group" aria-labelledby={stripId}>
      <p id={stripId} className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider mb-2">
        {label}
      </p>
      <p className="sr-only">{contextHint}</p>
      <div className="flex flex-wrap gap-2">
        {items.map((p) => {
          const productTitle = p.name || "Product";
          const buttonTitle = seriesContext
            ? `Open ${productTitle} (${seriesContext}) — ${label}`
            : `Open product: ${productTitle}`;
          return (
            <button
              key={p.id}
              type="button"
              onClick={() => onSelect(p.id)}
              className="w-14 h-14 rounded-lg overflow-hidden bg-zinc-800/80 border border-zinc-700/60 hover:border-blue-500/60 focus-visible:ring-2 focus-visible:ring-blue-500 shrink-0 transition-colors"
              title={buttonTitle}
              aria-label={buttonTitle}
            >
              {p.image_url ? (
                <img
                  src={p.image_url}
                  alt={`${productTitle} — product image`}
                  title={productTitle}
                  className="w-full h-full object-cover"
                  loading="lazy"
                />
              ) : (
                <span className="w-full h-full flex items-center justify-center text-zinc-600 text-[10px]" title={productTitle} aria-hidden>
                  —
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function RelationCard({
  item,
  productsById,
  onOpenProduct,
  brandName,
}: {
  item: RelationItem;
  productsById: Record<string, ProductSummary>;
  onOpenProduct: (id: string) => void;
  brandName?: string;
}) {
  const [expanded, setExpanded] = useState(false);
  const heroFamily = item.families[0];
  const heroImage = heroFamily?.hero_image || heroFamily?.variants?.[0]?.image_url;
  const seriesContext = brandName ? `${brandName} — ${item.series_label}` : item.series_label;
  const expandLabel = expanded
    ? `Collapse ${item.series_label} — hide variants, accessories, and related`
    : `Expand ${item.series_label} — show ${item.variant_ids.length} variants, accessories, and related products`;
  const summaryText = `${item.families.length} product family, ${item.variant_ids.length} variant${item.variant_ids.length !== 1 ? "s" : ""}. ${expandLabel}`;

  return (
    <article
      className="rounded-xl border border-zinc-800/80 bg-zinc-900/60 overflow-hidden"
      data-series={item.series_key}
      aria-label={`Product line: ${seriesContext}`}
    >
      <button
        type="button"
        onClick={() => setExpanded((e) => !e)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-zinc-800/40 transition-colors focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-blue-500"
        aria-expanded={expanded}
        aria-label={expandLabel}
        title={expandLabel}
      >
        <div className="flex items-center gap-3 min-w-0">
          {heroImage ? (
            <div className="w-16 h-16 rounded-lg overflow-hidden bg-zinc-800 shrink-0" title={seriesContext}>
              <img
                src={heroImage}
                alt={`${item.series_label} — product line image${brandName ? `, ${brandName}` : ""}`}
                title={seriesContext}
                className="w-full h-full object-cover"
                loading="lazy"
              />
            </div>
          ) : (
            <div
              className="w-16 h-16 rounded-lg bg-zinc-800 shrink-0 flex items-center justify-center"
              title={`No image for ${item.series_label}`}
              aria-label={`No image available for ${item.series_label}`}
            >
              <Package className="w-6 h-6 text-zinc-600" aria-hidden />
            </div>
          )}
          <div className="min-w-0">
            <h3 className="font-semibold text-white truncate" title={seriesContext}>{item.series_label}</h3>
            <p className="text-xs text-zinc-500" aria-hidden>
              {item.families.length} family · {item.variant_ids.length} variants
            </p>
            <p className="sr-only">{summaryText}</p>
          </div>
        </div>
        <ChevronRight
          className={`w-5 h-5 text-zinc-500 shrink-0 transition-transform ${expanded ? "rotate-90" : ""}`}
          aria-hidden
        />
      </button>
      {expanded && (
        <div className="px-4 pb-4 pt-0 border-t border-zinc-800/60" role="region" aria-label={`${item.series_label} — variants, accessories and parts, related products`}>
          <ThumbnailStrip
            ids={item.variant_ids}
            productsById={productsById}
            onSelect={onOpenProduct}
            label="Variants"
            seriesContext={seriesContext}
          />
          <ThumbnailStrip
            ids={item.direct_accessory_ids}
            productsById={productsById}
            onSelect={onOpenProduct}
            label="Accessories & parts"
            seriesContext={seriesContext}
          />
          <ThumbnailStrip
            ids={item.related_ids}
            productsById={productsById}
            onSelect={onOpenProduct}
            label="Related"
            seriesContext={seriesContext}
          />
        </div>
      )}
    </article>
  );
}

function categoryLabel(cat: CategoryItem): string {
  return cat.galaxy_label === cat.spectrum_label ? cat.spectrum_label : `${cat.galaxy_label} → ${cat.spectrum_label}`;
}

function stableCategoryAnchorId(cat: CategoryItem): string {
  const raw = cat.spectrum_id || cat.spectrum_label || "uncategorized";
  return `cat-${raw.toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9-]/g, "")}`;
}

function matchesRelationQuery(rel: RelationItem, q: string, productsById: Record<string, ProductSummary>): boolean {
  const query = q.trim().toLowerCase();
  if (!query) return true;

  const haystacks: string[] = [];
  haystacks.push(rel.series_label || "");
  for (const fam of rel.families ?? []) haystacks.push(fam.family_name || "");
  const idsToScan = [
    ...(rel.variant_ids ?? []),
    ...(rel.direct_accessory_ids ?? []),
    ...(rel.related_ids ?? []),
  ].slice(0, 120);
  for (const id of idsToScan) {
    const p = productsById[id];
    if (p?.name) haystacks.push(p.name);
  }

  return haystacks.some((h) => h.toLowerCase().includes(query));
}

function BrandLogo({
  src,
  name,
  size = 44,
}: {
  src?: string | null;
  name: string;
  size?: number;
}) {
  const initial = (name || "?").trim().charAt(0).toUpperCase();
  if (!src) {
    return (
      <div
        className="rounded-xl bg-zinc-800/70 border border-zinc-700/40 flex items-center justify-center text-sm font-semibold text-zinc-300"
        style={{ width: size, height: size }}
        aria-hidden
      >
        {initial}
      </div>
    );
  }
  return (
    <div
      className="rounded-xl bg-zinc-900/60 border border-zinc-800/60 overflow-hidden flex items-center justify-center"
      style={{ width: size, height: size }}
      aria-hidden
    >
      <img
        src={src}
        alt=""
        className="w-full h-full object-contain p-1"
        loading="lazy"
        onError={(e) => {
          e.currentTarget.style.display = "none";
        }}
      />
    </div>
  );
}

export const ItemsView = () => {
  const { goToGalaxy, openProductPage } = useNavigationStore();
  const [selectedBrandKey, setSelectedBrandKey] = useState<string | null>(null);
  const [brandListQuery, setBrandListQuery] = useState("");
  const [brandPageQuery, setBrandPageQuery] = useState("");
  const hasInitialBrand = React.useRef(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ["structured-items"],
    queryFn: fetchStructuredItems,
    staleTime: 5 * 60 * 1000,
  });

  const { data: brandIndexData } = useQuery({
    queryKey: ["brand-index"],
    queryFn: fetchBrandIndex,
    staleTime: 30 * 60 * 1000,
  });

  const brands = data?.brands ?? [];
  const productsById = data?.products_by_id ?? {};

  const brandIndexById = useMemo(() => {
    const map = new Map<string, BrandIndexEntry>();
    for (const b of brandIndexData?.brands ?? []) {
      map.set((b.id || "").toLowerCase(), b);
    }
    return map;
  }, [brandIndexData]);

  React.useEffect(() => {
    if (brands.length === 0 || hasInitialBrand.current) return;
    hasInitialBrand.current = true;
    const stored =
      typeof window !== "undefined" ? window.sessionStorage.getItem(STORAGE_SELECTED_BRAND_KEY) : null;
    const initialKey = stored && brands.some((b) => b.brand_key === stored) ? stored : null;
    setSelectedBrandKey(initialKey);
  }, [brands]);

  React.useEffect(() => {
    if (typeof window === "undefined") return;
    if (!selectedBrandKey) {
      window.sessionStorage.removeItem(STORAGE_SELECTED_BRAND_KEY);
    } else {
      window.sessionStorage.setItem(STORAGE_SELECTED_BRAND_KEY, selectedBrandKey);
    }
  }, [selectedBrandKey]);

  const selectedBrand = useMemo(
    () => brands.find((b) => b.brand_key === selectedBrandKey) ?? brands[0],
    [brands, selectedBrandKey]
  );

  const filteredBrandList = useMemo(() => {
    const q = brandListQuery.trim().toLowerCase();
    if (!q) return brands;
    return brands.filter((b) => (b.brand || "").toLowerCase().includes(q));
  }, [brands, brandListQuery]);

  const selectedBrandMeta = useMemo(() => {
    if (!selectedBrandKey) return null;
    return brandIndexById.get(selectedBrandKey.toLowerCase()) ?? null;
  }, [brandIndexById, selectedBrandKey]);

  const brandCategories = useMemo(() => {
    if (!selectedBrandKey || !selectedBrand) return [];
    return (selectedBrand.categories ?? selectedBrand.types ?? []).slice();
  }, [selectedBrand, selectedBrandKey]);

  const filteredCategories = useMemo(() => {
    const q = brandPageQuery.trim();
    if (!q) return brandCategories;
    return brandCategories
      .map((cat) => {
        const rels = (cat.relations ?? cat.series ?? []).filter((rel) =>
          matchesRelationQuery(rel, q, productsById),
        );
        return { ...cat, relations: rels, series: rels };
      })
      .filter((cat) => (cat.relations ?? cat.series ?? []).length > 0);
  }, [brandCategories, brandPageQuery, productsById]);

  const categoryNavItems = useMemo(() => {
    const source = filteredCategories;
    return source.map((cat) => ({
      key: cat.spectrum_id || cat.spectrum_label || "uncategorized",
      label: categoryLabel(cat),
      anchorId: stableCategoryAnchorId(cat),
      count: (cat.relations ?? cat.series ?? []).length,
    }));
  }, [filteredCategories]);

  const brandTotals = useMemo(() => {
    const cats = brandCategories;
    const totalCategories = cats.length;
    const totalLines = cats.reduce((sum, c) => sum + (c.relations ?? c.series ?? []).length, 0);
    const visibleLines = filteredCategories.reduce((sum, c) => sum + (c.relations ?? c.series ?? []).length, 0);
    return { totalCategories, totalLines, visibleLines };
  }, [brandCategories, filteredCategories]);

  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center bg-black/80" aria-live="polite" aria-busy="true">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-2 border-zinc-700 border-t-blue-500 animate-spin" aria-hidden />
          <p className="text-sm text-zinc-500">Loading structured items…</p>
          <p className="sr-only">Loading products by brand, category, and product line. Please wait.</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="h-full flex items-center justify-center bg-black/80 p-6" role="alert">
        <div className="text-center max-w-md">
          <p className="text-zinc-400 mb-4">Could not load items. Check backend and try again.</p>
          <button
            type="button"
            onClick={goToGalaxy}
            className="px-4 py-2 rounded-lg bg-zinc-800 text-white hover:bg-zinc-700 focus-visible:ring-2 focus-visible:ring-blue-500"
            title="Return to dashboard"
            aria-label="Back to dashboard"
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
          <h1 className="text-lg font-semibold text-white" id="items-view-title">
            Items
          </h1>
        </div>
        <button
          type="button"
          onClick={goToGalaxy}
          className="text-sm text-zinc-500 hover:text-white focus-visible:ring-2 focus-visible:ring-blue-500 rounded px-2 py-1"
          title="Return to dashboard"
          aria-label="Return to dashboard"
        >
          ← Dashboard
        </button>
      </div>

      <div className="flex-1 flex min-h-0">
        {/* Brand sidebar */}
        <aside
          className="w-52 shrink-0 border-r border-zinc-800/60 overflow-y-auto py-2"
          aria-label="Brands — select a brand to view its products by category and product line"
        >
          <div className="px-3 pt-2 pb-3">
            <button
              type="button"
              onClick={() => {
                setSelectedBrandKey(null);
                setBrandPageQuery("");
              }}
              className={`w-full flex items-center justify-between gap-2 px-3 py-2 rounded-lg text-sm border transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 ${
                !selectedBrandKey
                  ? "bg-blue-500/15 border-blue-500/30 text-white"
                  : "bg-zinc-900/40 border-zinc-800/60 text-zinc-300 hover:bg-zinc-800/40"
              }`}
              title="All brands"
              aria-label="All brands"
              aria-current={!selectedBrandKey ? "true" : undefined}
            >
              <span className="truncate">All brands</span>
              <span className="text-[10px] text-zinc-500 tabular-nums">{brands.length}</span>
            </button>
            <div className="mt-2 relative">
              <Search className="w-4 h-4 text-zinc-600 absolute left-3 top-1/2 -translate-y-1/2" aria-hidden />
              <input
                type="text"
                value={brandListQuery}
                onChange={(e) => setBrandListQuery(e.target.value)}
                placeholder="Filter brands…"
                className="w-full pl-9 pr-3 py-2 rounded-lg bg-zinc-900/60 border border-zinc-800/70 text-sm text-zinc-200 placeholder:text-zinc-600 focus-visible:ring-2 focus-visible:ring-blue-500 focus:outline-none"
                aria-label="Filter brands"
              />
            </div>
          </div>
          <p className="sr-only">Select a brand to open its brand home page and browse products by category and product line.</p>
          {filteredBrandList.map((b) => {
            const meta = brandIndexById.get(b.brand_key.toLowerCase());
            const isActive = selectedBrandKey === b.brand_key;
            return (
              <button
                key={b.brand_key}
                type="button"
                onClick={() => {
                  setSelectedBrandKey(b.brand_key);
                  setBrandPageQuery("");
                }}
                className={`w-full text-left px-4 py-2.5 text-sm focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-blue-500 ${
                  isActive
                    ? "bg-blue-500/20 text-white font-medium border-l-2 border-blue-500"
                    : "text-zinc-400 hover:bg-zinc-800/60 hover:text-white border-l-2 border-transparent"
                }`}
                title={isActive ? `Viewing ${b.brand}` : `Open ${b.brand} home`}
                aria-label={isActive ? `${b.brand} — currently selected` : `Open ${b.brand} home`}
                aria-current={isActive ? "true" : undefined}
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="truncate">{b.brand}</span>
                  {meta?.product_count ? (
                    <span className={`text-[10px] tabular-nums ${isActive ? "text-blue-200" : "text-zinc-600"}`}>
                      {meta.product_count}
                    </span>
                  ) : null}
                </div>
              </button>
            );
          })}
        </aside>

        {/* Category → Relations content */}
        <main
          className="flex-1 overflow-y-auto p-6"
          aria-label={
            selectedBrandKey && selectedBrand
              ? `${selectedBrand.brand} — brand home page with products by category and product line`
              : "Brands index — choose a brand to open its home page"
          }
        >
          {!selectedBrandKey ? (
            <section aria-label="All brands">
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                  <Grid3X3 className="w-5 h-5 text-zinc-500" aria-hidden />
                  Brands
                </h2>
                <p className="text-xs text-zinc-500 mt-2 max-w-3xl">
                  Each brand opens as a full, interactive home page: products are organized first by <strong>category (what they are)</strong>, then by <strong>main product line</strong>. Accessories and parts do not show as their own cards — expand a product line to see variants, accessories &amp; parts, and related products.
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4" role="list" aria-label="Brand tiles">
                {filteredBrandList.map((b) => {
                  const meta = brandIndexById.get(b.brand_key.toLowerCase());
                  const subtitleParts: string[] = [];
                  if (meta?.product_count) subtitleParts.push(`${meta.product_count} products`);
                  if (meta?.verified_count) subtitleParts.push(`${meta.verified_count} verified`);
                  const subtitle = subtitleParts.join(" · ");
                  return (
                    <button
                      key={`tile-${b.brand_key}`}
                      type="button"
                      onClick={() => setSelectedBrandKey(b.brand_key)}
                      className="rounded-2xl border border-zinc-800/70 bg-zinc-900/40 hover:bg-zinc-800/40 transition-colors p-4 text-left focus-visible:ring-2 focus-visible:ring-blue-500"
                      aria-label={`Open ${b.brand} home`}
                      title={`Open ${b.brand} home`}
                    >
                      <div className="flex items-center gap-3">
                        <BrandLogo src={meta?.logo_url} name={b.brand} />
                        <div className="min-w-0 flex-1">
                          <div className="text-sm font-semibold text-white truncate">{b.brand}</div>
                          <div className="text-xs text-zinc-500 truncate">{subtitle || "Browse by category and product line"}</div>
                        </div>
                        <ChevronRight className="w-4 h-4 text-zinc-600 shrink-0" aria-hidden />
                      </div>
                    </button>
                  );
                })}
              </div>
            </section>
          ) : selectedBrand ? (
            <section aria-label={`${selectedBrand.brand} brand home`}>
              <div className="flex items-start justify-between gap-6 flex-wrap">
                <div className="min-w-0">
                  <div className="flex items-center gap-3">
                    <BrandLogo src={selectedBrandMeta?.logo_url} name={selectedBrand.brand} size={52} />
                    <div className="min-w-0">
                      <h2 id="items-brand-heading" className="text-2xl font-semibold text-white truncate">
                        {selectedBrand.brand}
                      </h2>
                      <p className="text-xs text-zinc-500 mt-1" id="items-context-desc">
                        {brandTotals.totalCategories} categories · {brandTotals.visibleLines}/{brandTotals.totalLines} product lines
                        {selectedBrandMeta?.product_count ? ` · ${selectedBrandMeta.product_count} products` : ""}
                      </p>
                    </div>
                  </div>
                  <p className="text-xs text-zinc-500 mt-3 max-w-3xl">
                    Policy: category → main product line. Accessories &amp; parts (covers, flybars, cases, stands) are nested under their parent product line. Expand a card to browse variants, accessories &amp; parts, and related products. Click any thumbnail to open that product.
                  </p>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedBrandKey(null);
                      setBrandPageQuery("");
                    }}
                    className="h-10 px-3 rounded-lg bg-zinc-900/60 border border-zinc-800/70 text-sm text-zinc-200 hover:bg-zinc-800/60 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 flex items-center gap-2"
                    title="Back to brands"
                    aria-label="Back to brands"
                  >
                    <ArrowLeft className="w-4 h-4" aria-hidden />
                    Brands
                  </button>
                  {selectedBrandMeta?.data_file ? (
                    <a
                      href={`/data/${selectedBrandMeta.data_file}`}
                      target="_blank"
                      rel="noreferrer"
                      className="h-10 px-3 rounded-lg bg-zinc-900/60 border border-zinc-800/70 text-sm text-zinc-200 hover:bg-zinc-800/60 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 flex items-center gap-2"
                      title="Open raw brand JSON (new tab)"
                      aria-label="Open raw brand JSON (new tab)"
                    >
                      <ExternalLink className="w-4 h-4" aria-hidden />
                      JSON
                    </a>
                  ) : null}
                </div>
              </div>

              {/* Sticky tools: in-brand search + category jump */}
              <div className="sticky top-0 z-10 -mx-6 px-6 pt-4 pb-3 bg-black/90 border-b border-zinc-800/50 backdrop-blur-md">
                <div className="flex flex-col gap-3">
                  <div className="relative max-w-xl">
                    <Search className="w-4 h-4 text-zinc-600 absolute left-3 top-1/2 -translate-y-1/2" aria-hidden />
                    <input
                      type="text"
                      value={brandPageQuery}
                      onChange={(e) => setBrandPageQuery(e.target.value)}
                      placeholder={`Search within ${selectedBrand.brand}…`}
                      className="w-full h-10 pl-9 pr-3 rounded-lg bg-zinc-900/60 border border-zinc-800/70 text-sm text-zinc-200 placeholder:text-zinc-600 focus-visible:ring-2 focus-visible:ring-blue-500 focus:outline-none"
                      aria-label={`Search within ${selectedBrand.brand}`}
                    />
                  </div>
                  <div className="flex gap-2 overflow-x-auto pb-1 custom-scrollbar" role="navigation" aria-label="Jump to category">
                    {categoryNavItems.map((c) => (
                      <button
                        key={c.key}
                        type="button"
                        onClick={() => {
                          const el = document.getElementById(c.anchorId);
                          el?.scrollIntoView({ behavior: "smooth", block: "start" });
                        }}
                        className="shrink-0 h-9 px-3 rounded-full border border-zinc-800/70 bg-zinc-900/40 text-xs text-zinc-300 hover:bg-zinc-800/50 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 flex items-center gap-2"
                        title={`Jump to ${c.label}`}
                        aria-label={`Jump to ${c.label}`}
                      >
                        <span className="truncate max-w-[14rem]">{c.label}</span>
                        <span className="text-[10px] text-zinc-500 tabular-nums">{c.count}</span>
                      </button>
                    ))}
                    {categoryNavItems.length === 0 && (
                      <span className="text-xs text-zinc-600 py-2">
                        No matches. Try a different search.
                      </span>
                    )}
                  </div>
                </div>
              </div>

              <div className="space-y-6 pt-4" role="list" aria-labelledby="items-brand-heading">
                {filteredCategories.map((cat) => {
                  const label = categoryLabel(cat);
                  const anchorId = stableCategoryAnchorId(cat);
                  const rels = cat.relations ?? cat.series ?? [];
                  return (
                    <section
                      key={cat.spectrum_id || label}
                      className="space-y-3 scroll-mt-24"
                      aria-labelledby={anchorId}
                      aria-label={`${selectedBrand.brand} — ${label} products`}
                    >
                      <div className="flex items-end justify-between gap-4">
                        <div className="flex-1">
                          <h3
                            id={anchorId}
                            className="text-sm font-semibold text-zinc-300 mb-2"
                            title={`Category: ${label}`}
                          >
                            {label}
                          </h3>
                          {/* Hierarchy Breadcrumb */}
                          <HierarchyBreadcrumb
                            hierarchy={{
                              category: cat.galaxy_label || cat.spectrum_label,
                              subCategory: cat.spectrum_label !== cat.galaxy_label ? cat.spectrum_label : undefined,
                              productType: undefined, // Will be populated from product data
                              brand: selectedBrand.brand,
                            }}
                            className="text-xs"
                          />
                        </div>
                        <p className="text-[11px] text-zinc-600 tabular-nums" aria-hidden>
                          {rels.length} line{rels.length !== 1 ? "s" : ""}
                        </p>
                      </div>
                      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3" role="list">
                        {rels.map((rel) => (
                          <RelationCard
                            key={`${cat.spectrum_id}-${rel.series_key}`}
                            item={rel}
                            productsById={productsById}
                            onOpenProduct={openProductPage}
                            brandName={selectedBrand.brand}
                          />
                        ))}
                      </div>
                    </section>
                  );
                })}
              </div>
            </section>
          ) : (
            <div className="text-zinc-400">Select a brand.</div>
          )}
        </main>
      </div>
    </div>
  );
};
