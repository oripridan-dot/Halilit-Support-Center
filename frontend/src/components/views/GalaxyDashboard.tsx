import React, { useMemo, useCallback } from "react";
import {
  LayoutGrid,
  Guitar,
  Music,
  Piano,
  Mic2,
  Speaker,
  Plug,
  HelpCircle,
  Database,
  Layers,
} from "lucide-react";
import { useNavigationStore } from "../../store/navigationStore";
import { UNIVERSAL_CATEGORIES } from "../../lib/universalCategories";
import { CategorySlot } from "./galaxy/CategorySlot";
import { getContextBackground } from "../../lib/slotBackgrounds";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import { getBrandLogoUrl } from "../../lib/brandLogoHelper";

// Icon mapping for sectors
const ICON_MAP: Record<string, React.ElementType> = {
  Guitar,
  Music,
  Piano,
  Mic2,
  Speaker,
  Plug,
  HelpCircle,
};

// --- ADAPTATION LAYER: Map Universal Categories to "Galaxy" shape ---
const galaxy = UNIVERSAL_CATEGORIES.map((cat) => {
  return {
    id: cat.id,
    name: cat.label,
    icon: cat.iconName,
    iconComponent: ICON_MAP[cat.iconName] || HelpCircle,
    color: cat.color,
    children: cat.spectrum.map((sub) => {
      const bgConfig = getContextBackground(sub.id);
      return {
        id: sub.id,
        name: sub.label,
        image: bgConfig.imageUrl,
        fallbackGradient: bgConfig.fallbackGradient,
      };
    }),
  };
});

export const GalaxyDashboard = () => {
  const { goToSpectrum, goToCuration } = useNavigationStore();
  const {
    products,
    isLoading,
    galaxyCounts,
    spectrumCounts,
    indexes,
    metadata,
  } = useConductorCatalog();

  // Stable callback — avoids re-creating on every render
  const onSlotClick = useCallback(
    (mainId: string, subId: string) => goToSpectrum(mainId, subId, []),
    [goToSpectrum],
  );

  // Use spectrum-level counts for individual subcategory slots
  const categorySpectrumCounts = spectrumCounts;

  // Pre-compute brand logos per spectrum using index-based lookups
  const brandsBySpectrum = useMemo(() => {
    const map: Record<string, Array<{ brand: string; logoUrl: string }>> = {};
    for (const sector of galaxy) {
      for (const sub of sector.children) {
        const specIdxs = indexes.by_spectrum[sub.id] || [];
        // Extract unique brands from pre-filtered products
        const seen = new Set<string>();
        const logos: Array<{ brand: string; logoUrl: string }> = [];
        for (const i of specIdxs) {
          const p = products[i];
          if (!p?.brand || seen.has(p.brand)) continue;
          seen.add(p.brand);
          const logoUrl = getBrandLogoUrl(p.brand);
          if (logoUrl) {
            logos.push({ brand: p.brand, logoUrl });
            if (logos.length >= 4) break;
          }
        }
        map[sub.id] = logos;
      }
    }
    return map;
  }, [products, indexes]);

  return (
    <div className="flex h-full bg-[#050505] text-white overflow-hidden relative flex-col">
      {/* ------------------------------------------------------------------
          HEADER
         ------------------------------------------------------------------ */}
      <header className="h-14 flex items-center justify-between px-6 bg-zinc-950/80 backdrop-blur-md z-10 border-b border-zinc-800/50 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-md">
            <LayoutGrid className="w-4 h-4 text-white" strokeWidth={2.5} />
          </div>
          <h1 className="text-zinc-100 font-bold tracking-wide text-lg">
            Galaxies
          </h1>
          {metadata?.total_products !== undefined && (
            <span className="text-[10px] text-zinc-500 font-medium ml-1">
              {metadata.total_products} products
            </span>
          )}
          {metadata?.graph_stats && metadata.graph_stats.total_families > 0 && (
            <span className="flex items-center gap-1 text-[10px] text-blue-400/70 font-medium ml-2 bg-blue-500/10 border border-blue-500/15 rounded-full px-2 py-0.5">
              <Layers size={10} />
              {metadata.graph_stats.total_families} families
            </span>
          )}
        </div>

        {/* Catalog Health Indicator */}
        {metadata?.health_score !== undefined && (
          <div className="flex items-center gap-2 bg-zinc-900/60 border border-zinc-800/50 rounded-lg px-3 py-1.5">
            <Database className="w-3 h-3 text-zinc-500" />
            <div className="flex items-center gap-1.5">
              <div
                className={`w-1.5 h-1.5 rounded-full animate-pulse ${
                  metadata.health_status === "COMPLETE"
                    ? "bg-emerald-400"
                    : metadata.health_status === "GOOD"
                      ? "bg-green-400"
                      : metadata.health_status === "PARTIAL"
                        ? "bg-amber-400"
                        : "bg-red-400"
                }`}
              />
              <span
                className={`text-xs font-bold tabular-nums ${
                  metadata.health_status === "COMPLETE"
                    ? "text-emerald-400"
                    : metadata.health_status === "GOOD"
                      ? "text-green-400"
                      : metadata.health_status === "PARTIAL"
                        ? "text-amber-400"
                        : "text-red-400"
                }`}
              >
                {metadata.health_score}%
              </span>
            </div>
            {metadata.status_counts && (
              <div className="flex gap-1 ml-1 border-l border-zinc-800 pl-2">
                {Object.entries(metadata.status_counts).map(
                  ([status, count]) =>
                    (count as number) > 0 && (
                      <span
                        key={status}
                        className={`text-[9px] px-1.5 py-0.5 rounded-md font-semibold ${
                          status === "COMPLETE"
                            ? "bg-emerald-500/10 text-emerald-400"
                            : status === "GOOD"
                              ? "bg-green-500/10 text-green-400"
                              : status === "PARTIAL"
                                ? "bg-amber-500/10 text-amber-400"
                                : "bg-red-500/10 text-red-400"
                        }`}
                      >
                        {count as number}
                      </span>
                    ),
                )}
              </div>
            )}
          </div>
        )}
        {/* Curation button */}
        <button
          onClick={goToCuration}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-violet-600/15 hover:bg-violet-600/30 border border-violet-500/20 rounded-lg text-violet-400 text-xs font-semibold transition-all ml-2"
          title="Product Graph Curation"
        >
          <Layers size={12} />
          Curation
        </button>
      </header>

      {/* ------------------------------------------------------------------
          MAIN CONTENT: 6 SECTOR CARDS GRID WITH SUBCATEGORIES
         ------------------------------------------------------------------ */}
      <div className="flex-1 p-5 min-h-0 w-full h-full text-[10px]">
        {isLoading ? (
          /* Loading skeleton grid */
          <div className="grid grid-cols-3 grid-rows-2 gap-5 h-full w-full mx-auto animate-pulse">
            {Array.from({ length: 6 }).map((_, i) => (
              <div
                key={i}
                className="bg-zinc-900/50 rounded-xl border border-zinc-800/40 overflow-hidden flex flex-col"
              >
                <div className="h-11 border-b border-zinc-800/30 bg-zinc-900/30 flex items-center gap-3 px-4">
                  <div className="w-6 h-6 rounded-lg bg-zinc-800/60" />
                  <div className="h-3 w-24 bg-zinc-800/60 rounded" />
                </div>
                <div className="flex-1 p-3 grid grid-cols-4 gap-3 content-start">
                  {Array.from({ length: 4 }).map((_, j) => (
                    <div
                      key={j}
                      className="aspect-square rounded-xl bg-zinc-800/30"
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* Sector cards grid */
          <div className="grid grid-cols-3 grid-rows-2 gap-5 h-full w-full mx-auto">
            {galaxy.map((sector, sectorIdx) => (
              <div
                key={sector.id}
                className="bg-zinc-950 rounded-xl border border-zinc-800/50 overflow-hidden flex flex-col shadow-lg hover:border-zinc-700/60 transition-colors duration-300 min-h-0"
                style={{ animationDelay: `${sectorIdx * 50}ms` }}
              >
                {/* Sector Header */}
                <div className="px-4 py-2.5 border-b border-zinc-800/40 bg-zinc-900/40 flex items-center gap-3 shrink-0 h-11">
                  <div
                    className="w-6 h-6 rounded-lg flex items-center justify-center shadow-md shrink-0"
                    style={{
                      backgroundColor: `${sector.color}20`,
                      border: `1px solid ${sector.color}40`,
                    }}
                  >
                    {React.createElement(sector.iconComponent, {
                      className: "w-3.5 h-3.5",
                      color: sector.color,
                    })}
                  </div>
                  <h2 className="font-semibold uppercase tracking-wider text-zinc-200 text-xs truncate">
                    {sector.name}
                  </h2>
                  {/* Sector product count */}
                  {galaxyCounts[sector.id] !== undefined && (
                    <span className="ml-auto text-[9px] text-zinc-600 font-medium tabular-nums shrink-0">
                      {galaxyCounts[sector.id]}
                    </span>
                  )}
                </div>

                {/* Subcategory Grid */}
                <div className="flex-1 p-3 grid grid-cols-4 gap-3 content-start overflow-hidden">
                  {sector.children.map((sub) => (
                    <CategorySlot
                      key={sub.id}
                      id={sub.id}
                      name={sub.name}
                      image={sub.image}
                      fallbackGradient={sub.fallbackGradient}
                      icon={sector.iconComponent}
                      mainColor={sector.color}
                      count={
                        isLoading
                          ? undefined
                          : (categorySpectrumCounts[sub.id] ?? 0)
                      }
                      brands={brandsBySpectrum[sub.id] ?? []}
                      onClick={() => onSlotClick(sector.id, sub.id)}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
