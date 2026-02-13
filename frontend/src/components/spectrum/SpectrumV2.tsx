/**
 * SpectrumV2 — The redesigned main Spectrum module with:
 * - Domain-driven instrument family sidebar
 * - Semantic zoom (Galaxy → Constellation → Cluster → Star)
 * - Model grouping with variation subtracks
 * - Non-overlapping zoom consolidation
 *
 * Layout:
 * ┌──────────┬──────────────────────────────────────────┐
 * │          │  Breadcrumb + ZoomControl + Stats         │
 * │  Family  ├──────────────────────────────────────────┤
 * │  Sidebar │                                          │
 * │          │  [Galaxy View: Family Cards]              │
 * │  🎸      │  [Constellation View: Brand Cards]       │
 * │  Guitars │  [Cluster View: Brand → Model Tracks]    │
 * │   ├ Elec │  [Star View: Expanded Variations]        │
 * │   ├ Acou │                                          │
 * │   └ Clas │                                          │
 * │  🎸 Bass │                                          │
 * │  🔊 Amps │                                          │
 * └──────────┴──────────────────────────────────────────┘
 */
import React, {
  useMemo,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";
import { ArrowLeft, Search, X } from "lucide-react";
import { useSpectrumV2Store } from "../../store/spectrumV2Store";
import { useNavigationStore } from "../../store/navigationStore";
import { useSpectrumModels } from "../../hooks/useSpectrumV2";
import { FamilySidebar } from "./FamilySidebar";
import { ZoomControl } from "./ZoomControl";
import { SpectrumTrack } from "./SpectrumTrack";
import { FAMILY_ICONS } from "../../types/spectrum";
import type {
  SpectrumGalaxyResponse,
  SpectrumConstellationResponse,
  SpectrumClusterResponse,
  SpectrumStarResponse,
  ModelGroup,
  FamilySummary,
  BrandSummary,
} from "../../types/spectrum";

export const SpectrumV2: React.FC = () => {
  const {
    zoom,
    activeFamily,
    activeSubCategory,
    activeBodyType,
    activeBrand,
    activeTier,
    expandedModel,
    searchQuery,
    setFamily,
    setBrand,
    setTier,
    setSearchQuery,
    toggleModel,
    reset,
  } = useSpectrumV2Store();

  const { goToGalaxy, openProductPage } = useNavigationStore();
  const { data, isLoading, error } = useSpectrumModels();
  const mainRef = useRef<HTMLDivElement>(null);

  // Debounced search - local state updates instantly, store updates after 300ms
  const [localSearch, setLocalSearch] = useState(searchQuery);
  const searchTimerRef = useRef<ReturnType<typeof setTimeout>>();

  const handleSearchChange = useCallback(
    (value: string) => {
      setLocalSearch(value);
      clearTimeout(searchTimerRef.current);
      searchTimerRef.current = setTimeout(() => {
        setSearchQuery(value);
      }, 300);
    },
    [setSearchQuery],
  );

  const handleSearchClear = useCallback(() => {
    setLocalSearch("");
    setSearchQuery("");
    clearTimeout(searchTimerRef.current);
  }, [setSearchQuery]);

  // Mouse wheel zoom on the track area
  const handleWheel = useCallback((e: WheelEvent) => {
    if (e.ctrlKey || e.metaKey) {
      e.preventDefault();
      if (e.deltaY < 0) {
        useSpectrumV2Store.getState().zoomIn();
      } else {
        useSpectrumV2Store.getState().zoomOut();
      }
    }
  }, []);

  useEffect(() => {
    const el = mainRef.current;
    if (el) {
      el.addEventListener("wheel", handleWheel, { passive: false });
      return () => el.removeEventListener("wheel", handleWheel);
    }
  }, [handleWheel]);

  // ── Derive tracks from model groups ──
  const tracksByBrand = useMemo(() => {
    if (!data) return [];
    if (data.zoom !== "cluster" && data.zoom !== "star") return [];

    const groups =
      (data as SpectrumClusterResponse | SpectrumStarResponse).modelGroups ||
      [];
    const brandMap = new Map<string, ModelGroup[]>();
    for (const group of groups) {
      const existing = brandMap.get(group.brand) || [];
      existing.push(group);
      brandMap.set(group.brand, existing);
    }

    return Array.from(brandMap.entries())
      .sort(([, a], [, b]) => {
        // Sort by total products descending, then brand name
        const countA = a.reduce((s, m) => s + m.variationCount, 0);
        const countB = b.reduce((s, m) => s + m.variationCount, 0);
        if (countB !== countA) return countB - countA;
        return a[0]?.brand.localeCompare(b[0]?.brand) || 0;
      })
      .map(([brand, models]) => ({ brand, models }));
  }, [data]);

  // ── Available tiers for the filter bar ──
  const availableTiers = useMemo(() => {
    if (!data) return [];
    if (data.zoom !== "cluster" && data.zoom !== "star") return [];
    const groups =
      (data as SpectrumClusterResponse | SpectrumStarResponse).modelGroups ||
      [];
    const tiers = new Set<string>();
    for (const g of groups) {
      if (g.primaryTier) tiers.add(g.primaryTier);
      if (g.variations) {
        for (const v of g.variations) {
          if (v.tier) tiers.add(v.tier);
        }
      }
    }
    // Sort: entry, mid, pro, flagship
    const order = ["entry", "mid", "pro", "flagship"];
    return Array.from(tiers).sort(
      (a, b) => order.indexOf(a) - order.indexOf(b),
    );
  }, [data]);

  const handleProductClick = useCallback(
    (productId: string) => {
      openProductPage(productId);
    },
    [openProductPage],
  );

  // ── Error state ──
  if (error) {
    return (
      <div className="flex h-full w-full items-center justify-center flex-col gap-4 p-8 bg-[#0b0c10]">
        <div className="max-w-md w-full border border-red-900/40 bg-red-950/10 rounded-xl p-8 text-center">
          <div className="w-14 h-14 mx-auto mb-4 rounded-full bg-red-500/10 flex items-center justify-center">
            <span className="text-2xl">⚠️</span>
          </div>
          <h3 className="text-red-400 font-bold text-lg mb-2">
            Failed to load spectrum
          </h3>
          <p className="text-sm text-red-300/70 mb-6">
            {(error as Error).message}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2.5 bg-red-900/30 hover:bg-red-900/50 text-red-200 rounded-lg text-sm font-medium transition-colors border border-red-800/30"
          >
            Reload Page
          </button>
        </div>
      </div>
    );
  }

  // ── Breadcrumb text ──
  const breadcrumb = useMemo(() => {
    const parts: string[] = ["Spectrum"];
    if (activeFamily) parts.push(activeFamily.replace(/_/g, " "));
    if (activeSubCategory) parts.push(activeSubCategory.replace(/_/g, " "));
    if (activeBrand) parts.push(activeBrand);
    if (activeBodyType) parts.push(activeBodyType.replace(/_/g, " "));
    return parts;
  }, [activeFamily, activeSubCategory, activeBrand, activeBodyType]);

  return (
    <div className="flex h-full bg-[#0b0c10] text-white overflow-hidden">
      {/* Left Sidebar — Family Navigation */}
      <FamilySidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header
          className="flex items-center justify-between px-4 py-2.5
                          border-b border-zinc-800/60 bg-zinc-900/50 backdrop-blur-sm shrink-0 z-10"
        >
          {/* Left: Back + Breadcrumb */}
          <div className="flex items-center gap-3">
            <button
              onClick={goToGalaxy}
              className="p-1.5 rounded-full hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors"
              title="Back to Galaxy"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>

            <div className="flex items-center gap-1.5 text-sm">
              {breadcrumb.map((part, i) => (
                <React.Fragment key={i}>
                  {i > 0 && <span className="text-zinc-700 text-xs">/</span>}
                  <span
                    className={`capitalize ${i === breadcrumb.length - 1 ? "text-amber-400 font-medium" : "text-zinc-500"}`}
                  >
                    {part}
                  </span>
                </React.Fragment>
              ))}
            </div>
          </div>

          {/* Center: Search + Zoom Control */}
          <div className="flex items-center gap-3">
            {/* Inline search */}
            <div className="relative">
              <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-3 h-3 text-zinc-600" />
              <input
                type="text"
                value={localSearch}
                onChange={(e) => handleSearchChange(e.target.value)}
                placeholder="Search models..."
                className="w-40 bg-zinc-900/80 border border-zinc-800/60 rounded-lg pl-7 pr-7 py-1 text-xs text-white placeholder-zinc-600 focus:outline-none focus:ring-1 focus:ring-amber-500/40 focus:border-amber-500/30 transition-all"
              />
              {localSearch && (
                <button
                  onClick={handleSearchClear}
                  className="absolute right-1.5 top-1/2 -translate-y-1/2 p-0.5 rounded hover:bg-zinc-800 text-zinc-500"
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </div>

            <ZoomControl />
          </div>

          {/* Right: Stats */}
          <div className="text-zinc-500 text-[10px] font-mono">
            {data && "totalModels" in data && (
              <span>
                {data.totalModels} models · {data.totalProducts} products
                {data.elapsed_ms !== undefined && (
                  <span className="text-zinc-700 ml-2">
                    ({data.elapsed_ms}ms)
                  </span>
                )}
              </span>
            )}
          </div>
        </header>

        {/* Main Track Area */}
        <main
          ref={mainRef}
          className="flex-1 overflow-y-auto overflow-x-hidden flex flex-col
                    scrollbar-thin scrollbar-thumb-zinc-800 scrollbar-track-transparent"
        >
          {isLoading ? (
            <LoadingState />
          ) : !data ? (
            <EmptyState onReset={reset} />
          ) : data.zoom === "galaxy" ? (
            <GalaxyView
              families={(data as SpectrumGalaxyResponse).families}
              onFamilyClick={setFamily}
            />
          ) : data.zoom === "constellation" ? (
            <ConstellationView
              brands={(data as SpectrumConstellationResponse).brands}
              onBrandClick={setBrand}
            />
          ) : (
            /* Cluster / Star — Brand Tracks */
            <div className="flex-1 flex flex-col">
              {/* Track Header */}
              <div className="h-7 flex border-b border-zinc-800/30 bg-black/30 text-[9px] text-zinc-600 font-mono items-center px-4 shrink-0">
                <span className="text-zinc-500 uppercase tracking-widest font-bold">
                  Models by Brand
                </span>
                <span className="ml-auto">
                  {tracksByBrand.length} brand
                  {tracksByBrand.length !== 1 ? "s" : ""}
                </span>
              </div>

              {/* Scrollable Track Area */}
              <div className="flex-1 overflow-y-auto">
                {tracksByBrand.length === 0 ? (
                  <EmptyState onReset={reset} />
                ) : (
                  tracksByBrand.map(({ brand, models }) => (
                    <SpectrumTrack
                      key={brand}
                      brand={brand}
                      models={models}
                      expandedModel={expandedModel}
                      onModelClick={toggleModel}
                      onProductClick={handleProductClick}
                    />
                  ))
                )}
              </div>
            </div>
          )}
        </main>

        {/* Bottom Bar — Tier Filters */}
        {(zoom === "cluster" || zoom === "star") && (
          <footer
            className="border-t border-zinc-800/60 bg-zinc-900/80 backdrop-blur-sm
                            px-4 py-2 flex items-center gap-3 shrink-0"
          >
            <span className="text-[9px] font-bold text-zinc-600 uppercase tracking-widest shrink-0">
              Tier
            </span>
            <button
              onClick={() => setTier(null)}
              className={`px-3 py-1 rounded-full text-[10px] font-bold tracking-wide transition-colors ${
                !activeTier
                  ? "bg-amber-500/20 text-amber-400"
                  : "bg-zinc-800 text-zinc-500 hover:bg-zinc-700 hover:text-zinc-300"
              }`}
            >
              ALL
            </button>
            {availableTiers.map((tier) => (
              <button
                key={tier}
                onClick={() => setTier(activeTier === tier ? null : tier)}
                className={`px-3 py-1 rounded-full text-[10px] font-bold tracking-wide transition-colors uppercase ${
                  activeTier === tier
                    ? "bg-amber-500/20 text-amber-400"
                    : "bg-zinc-800 text-zinc-500 hover:bg-zinc-700 hover:text-zinc-300"
                }`}
              >
                {tier}
              </button>
            ))}
          </footer>
        )}
      </div>
    </div>
  );
};

// ═══════════════════════════════════════════════════════════════════════════
// Sub-Views
// ═══════════════════════════════════════════════════════════════════════════

// ── Galaxy View: Family Cards ──

const GalaxyView: React.FC<{
  families: FamilySummary[];
  onFamilyClick: (slug: string) => void;
}> = ({ families, onFamilyClick }) => (
  <div className="p-6">
    <div className="mb-6">
      <h2 className="text-2xl font-black text-white tracking-tight uppercase">
        Instrument Families
      </h2>
      <p className="text-zinc-500 text-sm mt-1">
        Select a family to explore brands and models
      </p>
    </div>

    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {families.map((fam) => (
        <button
          key={fam.family}
          onClick={() => onFamilyClick(fam.family)}
          className="group bg-zinc-900/60 hover:bg-zinc-800 rounded-2xl p-6
                    border border-zinc-800/50 hover:border-amber-500/30
                    transition-all duration-200 text-left"
        >
          <p className="text-3xl mb-3">{FAMILY_ICONS[fam.family] || "🎵"}</p>
          <h3 className="text-white font-bold text-lg group-hover:text-amber-400 transition-colors">
            {fam.label}
          </h3>
          <div className="mt-2 space-y-0.5">
            <p className="text-zinc-500 text-xs">
              {fam.modelCount} models · {fam.productCount} products
            </p>
            <p className="text-zinc-600 text-xs">
              {fam.brandCount} brand{fam.brandCount !== 1 ? "s" : ""}
            </p>
            {fam.priceMin > 0 && (
              <p className="text-amber-400/60 text-xs font-bold mt-1">
                ₪{fam.priceMin.toLocaleString()} – ₪
                {fam.priceMax.toLocaleString()}
              </p>
            )}
          </div>
        </button>
      ))}
    </div>
  </div>
);

// ── Constellation View: Brand Cards ──

const ConstellationView: React.FC<{
  brands: BrandSummary[];
  onBrandClick: (brand: string) => void;
}> = ({ brands, onBrandClick }) => (
  <div className="p-6">
    <div className="mb-6">
      <h2 className="text-xl font-black text-white tracking-tight uppercase">
        Brands
      </h2>
      <p className="text-zinc-500 text-sm mt-1">
        Select a brand to see its model lineup
      </p>
    </div>

    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
      {brands.map((b) => (
        <button
          key={b.brand}
          onClick={() => onBrandClick(b.brand)}
          className="group bg-zinc-900/60 hover:bg-zinc-800 rounded-xl p-4
                    border border-zinc-800/50 hover:border-amber-500/30
                    transition-all duration-200 text-left"
        >
          <h4 className="text-white font-semibold text-sm group-hover:text-amber-400 transition-colors truncate">
            {b.brand}
          </h4>
          <p className="text-zinc-500 text-[10px] mt-1">
            {b.models} model{b.models !== 1 ? "s" : ""} · {b.products} SKUs
          </p>
          {b.priceMin > 0 && (
            <p className="text-amber-400/60 text-[10px] font-bold mt-2">
              ₪{b.priceMin.toLocaleString()} – ₪{b.priceMax.toLocaleString()}
            </p>
          )}

          {/* Top model thumbnails */}
          {b.topModels.length > 0 && (
            <div className="flex gap-1 mt-2">
              {b.topModels.slice(0, 3).map((m, i) => (
                <div
                  key={i}
                  className="w-8 h-8 bg-white/5 rounded overflow-hidden flex items-center justify-center"
                >
                  {m.heroImage ? (
                    <img
                      src={m.heroImage}
                      alt=""
                      className="max-h-full max-w-full object-contain"
                      loading="lazy"
                    />
                  ) : (
                    <span className="text-zinc-700 text-[8px]">🎵</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </button>
      ))}
    </div>
  </div>
);

// ── Loading State ──

const LoadingState: React.FC = () => (
  <div className="flex-1 flex items-center justify-center">
    <div className="flex flex-col items-center gap-4">
      <div className="relative w-12 h-12">
        <div className="absolute inset-0 rounded-full border-2 border-zinc-800" />
        <div className="absolute inset-0 rounded-full border-2 border-t-amber-500 animate-spin" />
      </div>
      <p className="text-zinc-600 text-xs font-mono tracking-widest uppercase animate-pulse">
        Loading Spectrum
      </p>
    </div>
  </div>
);

// ── Empty State ──

const EmptyState: React.FC<{ onReset: () => void }> = ({ onReset }) => (
  <div className="flex-1 flex items-center justify-center">
    <div className="text-center max-w-sm">
      <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-zinc-800/30 flex items-center justify-center">
        <span className="text-2xl opacity-30">🔍</span>
      </div>
      <h3 className="text-zinc-400 font-semibold mb-2">No products found</h3>
      <p className="text-zinc-600 text-sm mb-4">
        Try adjusting your filters or selecting a different family.
      </p>
      <button
        onClick={onReset}
        className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg text-sm transition-colors"
      >
        Reset All Filters
      </button>
    </div>
  </div>
);
