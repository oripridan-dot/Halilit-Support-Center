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
  const { goToSpectrum } = useNavigationStore();
  const { products, isLoading, galaxyCounts, spectrumCounts, indexes } =
    useConductorCatalog();

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
          HEADER: GALAXIES
         ------------------------------------------------------------------ */}
      <header className="h-16 flex items-center justify-between px-8 bg-gradient-to-b from-[#0f0f0f] via-[#0a0a0a] to-black/50 z-10 border-b border-zinc-800/40 shrink-0 shadow-lg">
        <div className="flex items-center gap-4">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg ring-1 ring-blue-400/30">
            <LayoutGrid className="w-5 h-5 text-white" strokeWidth={2.5} />
          </div>
          <h1
            className="text-zinc-50 font-bold tracking-[0.06em] text-3xl drop-shadow-lg"
            style={{
              textShadow:
                "0 2px 8px rgba(0,0,0,0.6), 0 0 12px rgba(59, 130, 246, 0.2)",
            }}
          >
            GALAXIES
          </h1>
        </div>
      </header>

      {/* ------------------------------------------------------------------
          MAIN CONTENT: 6 SECTOR CARDS GRID WITH SUBCATEGORIES
         ------------------------------------------------------------------ */}
      <div className="flex-1 p-6 min-h-0 w-full h-full text-[10px]">
        {/* Force 2 rows, 3 columns, fitting height */}
        <div className="grid grid-cols-3 grid-rows-2 gap-6 h-full w-full mx-auto">
          {galaxy.map((sector) => (
            <div
              key={sector.id}
              className="bg-[#0a0a0a] rounded-xl border border-zinc-800/60 overflow-hidden flex flex-col shadow-2xl min-h-0"
            >
              {/* Sector Header - Enhanced styling */}
              <div className="px-4 py-3 border-b border-zinc-700/40 bg-gradient-to-r from-[#0f0f0f] to-[#0a0a0a] flex items-center gap-3 shrink-0 h-12 shadow-lg">
                <div
                  className="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold shadow-lg shrink-0 ring-1 ring-white/10"
                  style={{
                    backgroundColor: sector.color,
                    boxShadow: `0 0 12px ${sector.color}40`,
                  }}
                >
                  {/* Render Icon component */}
                  {React.createElement(sector.iconComponent, {
                    className: "w-4 h-4",
                    color: "#fff",
                  })}
                </div>
                <h2
                  className="font-bold uppercase tracking-[0.04em] text-zinc-50 text-sm truncate transition-all duration-300"
                  style={{
                    textShadow: `0 2px 4px rgba(0,0,0,0.5), 0 0 8px ${sector.color}30`,
                  }}
                >
                  {sector.name}
                </h2>
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
      </div>
    </div>
  );
};
