import React from "react";
import {
  LayoutGrid,
  Guitar,
  Music,
  Piano,
  Mic2,
  Speaker,
  Plug,
  HelpCircle,
  Layers,
} from "lucide-react";
import { useNavigationStore } from "../../store/navigationStore";
import { UNIVERSAL_CATEGORIES } from "../../lib/universalCategories";
import { CategorySlot } from "./galaxy/CategorySlot";
import { extractBrandFromSpectrumId } from "../../lib/brandExtraction";
import { getContextBackground } from "../../lib/slotBackgrounds";
import { useProductCounts } from "../../hooks/useProductCounts";

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
  const { goToSpectrum, showTierBar } = useNavigationStore();
  const { counts, loading } = useProductCounts();

  // Directly handle navigation to a subcategory
  const onSlotClick = (mainId: string, subId: string) => {
    goToSpectrum(mainId, subId, []);
  };

  return (
    <div className="flex h-full bg-[#050505] text-white overflow-hidden relative flex-col">
      {/* ------------------------------------------------------------------
          HEADER: ULTRA COMPACT WITH TIER BAR BUTTON
         ------------------------------------------------------------------ */}
      <header className="h-14 flex items-center justify-between px-6 bg-gradient-to-b from-transparent to-black/20 z-10 border-b border-zinc-900/50 shrink-0">
        <div className="flex items-center gap-3">
          <LayoutGrid className="w-6 h-6 text-zinc-500" />
          <h1 className="text-zinc-100 font-bold tracking-tight text-3xl">
            GALAXIES
          </h1>
        </div>

        {/* Tier Bar Button */}
        <button
          onClick={showTierBar}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 hover:text-blue-300 border border-blue-500/30 hover:border-blue-500 transition-all duration-200"
        >
          <Layers className="w-4 h-4" />
          <span className="text-sm font-semibold">Tier Bar</span>
        </button>
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
              {/* Sector Header */}
              <div className="px-4 py-3 border-b border-zinc-800/60 bg-[#0f0f0f] flex items-center gap-3 shrink-0 h-12">
                <div
                  className="w-6 h-6 rounded flex items-center justify-center text-xs font-bold shadow-lg shrink-0"
                  style={{ backgroundColor: sector.color }}
                >
                  {/* Render Icon component */}
                  {React.createElement(sector.iconComponent, {
                    className: "w-4 h-4",
                    color: "#fff",
                  })}
                </div>
                <h2 className="font-bold uppercase tracking-tight text-zinc-100 text-sm truncate">
                  {sector.name}
                </h2>
              </div>

              {/* Subcategory Grid */}
              <div className="flex-1 p-3 grid grid-cols-4 gap-3 content-start overflow-hidden">
                {sector.children.map((sub) => {
                  return (
                    <CategorySlot
                      key={sub.id}
                      id={sub.id}
                      name={sub.name}
                      image={sub.image}
                      fallbackGradient={sub.fallbackGradient}
                      icon={sector.iconComponent}
                      mainColor={sector.color}
                      count={loading ? undefined : counts[sub.id] || 0}
                      onClick={() => onSlotClick(sector.id, sub.id)}
                    />
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
