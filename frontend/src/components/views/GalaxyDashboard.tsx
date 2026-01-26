import {
  Guitar,
  HelpCircle,
  LayoutGrid,
  List,
  Mic2,
  Music,
  Piano,
  Plug,
  Speaker,
} from "lucide-react";
import React, { useState } from "react";
import SPECTRUM_BRAND_COLORS from "../../lib/generatedSpectrumBrands.json";
import { UNIVERSAL_CATEGORIES } from "../../lib/universalCategories";
import { useNavigationStore } from "../../store/navigationStore";

// Icon map to avoid wildcard imports
const ICON_MAP: Record<string, React.ElementType> = {
  Guitar,
  Music,
  Piano,
  Mic2,
  Speaker,
  Plug,
  HelpCircle,
};

export const GalaxyDashboard = () => {
  const { goToSpectrum } = useNavigationStore();
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  return (
    <div className="w-full h-full bg-[#0e0e10] flex flex-col">
      {/* Header Area */}
      <div className="shrink-0 pt-6 px-6 lg:px-8 bg-[#0e0e10] z-20">
        <div className="flex items-end gap-4 justify-between mb-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-black italic tracking-tighter text-white/90 leading-none">
              GALAXIES
            </h1>
            <span className="block text-xs md:text-sm font-bold not-italic tracking-widest text-zinc-500 mt-1">
              SECTOR VIEW
            </span>
          </div>

          {/* View Toggle */}
          <div className="flex bg-[#18181b] p-1 rounded-lg border border-white/5">
            <button
              onClick={() => setViewMode("grid")}
              className={`p-2 rounded ${
                viewMode === "grid"
                  ? "bg-[#25252a] text-white shadow-sm"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
            >
              <LayoutGrid size={18} />
            </button>
            <button
              onClick={() => setViewMode("list")}
              className={`p-2 rounded ${
                viewMode === "list"
                  ? "bg-[#25252a] text-white shadow-sm"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
            >
              <List size={18} />
            </button>
          </div>
        </div>
        <div className="h-px w-full bg-gradient-to-r from-zinc-800 to-transparent mb-6" />
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto xl:overflow-hidden px-4 md:px-6 lg:px-8 pb-4 h-full">
        <div
          className={
            viewMode === "grid"
              ? "grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 xl:grid-rows-2 gap-4 xl:h-full pb-20 xl:pb-0"
              : "flex flex-col gap-3 xl:h-full xl:gap-2 pb-20 xl:pb-0"
          }
        >
          {UNIVERSAL_CATEGORIES.map((tribe, index) => {
            // Dynamic Icon Resolution with map
            const IconComponent = ICON_MAP[tribe.iconName] || HelpCircle;

            if (viewMode === "list") {
              return (
                <div
                  key={tribe.id}
                  className="bg-[#18181b] rounded-lg border border-white/5 px-4 flex items-center gap-6 group hover:bg-[#202023] transition-colors flex-1 min-h-0 py-2 xl:py-0"
                >
                  {/* Left: Category Info */}
                  <div className="flex items-center gap-4 shrink-0 w-32 md:w-64">
                    <div
                      className="w-8 h-8 rounded flex items-center justify-center shadow-lg"
                      style={{ backgroundColor: tribe.color }}
                    >
                      <IconComponent className="w-4 h-4 text-black" />
                    </div>
                    <div>
                      <span className="block text-[8px] font-black uppercase tracking-widest text-zinc-500 leading-none mb-0.5">
                        SECTOR 0{index + 1}
                      </span>
                      <h2 className="text-sm md:text-base font-bold uppercase tracking-tight text-white leading-none">
                        {tribe.label}
                      </h2>
                    </div>
                  </div>

                  {/* Right: Horizontal Scrollable Subcategories */}
                  <div className="flex-1 flex gap-2 overflow-x-auto h-full items-center scrollbar-none mask-linear-fade">
                    {tribe.spectrum.map((sub) => (
                      <button
                        key={sub.id}
                        onClick={() => goToSpectrum(tribe.id, sub.id, [])}
                        className="flex-shrink-0 w-28 md:w-36 h-[90%] bg-[#0a0a0c] rounded border border-white/5 flex items-center p-1.5 gap-2 hover:bg-[#25252a] transition-all group/item"
                      >
                        <div className="w-8 h-full flex items-center justify-center shrink-0">
                          <img
                            src={sub.image}
                            className="max-w-full max-h-full opacity-70 group-hover/item:opacity-100 transition-opacity object-contain"
                            alt={sub.label}
                          />
                        </div>
                        <span className="text-[9px] font-bold text-zinc-400 uppercase tracking-wider text-left leading-tight group-hover/item:text-white line-clamp-2">
                          {sub.label}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              );
            }

            return (
              <div
                key={tribe.id}
                className="group relative bg-[#18181b] rounded-t-xl overflow-hidden shadow-2xl flex flex-col min-h-[180px] xl:min-h-0"
                style={{
                  boxShadow: `0 20px 40px -10px rgba(0,0,0,0.5)`,
                }}
              >
                {/* Shelf Top (The "Lip") */}
                <div className="relative h-10 bg-[#202023] border-b border-black flex items-center px-3 justify-between z-10 transition-colors duration-300 group-hover:bg-[#25252a] shrink-0">
                  {/* Top Highlight for 3D effect */}
                  <div className="absolute top-0 left-0 right-0 h-px bg-white/10" />

                  <div className="flex items-center gap-2">
                    <div
                      className="w-6 h-6 rounded flex items-center justify-center shadow-lg transform group-hover:scale-110 transition-transform duration-300"
                      style={{ backgroundColor: tribe.color }}
                    >
                      <IconComponent className="w-3 h-3 text-black" />
                    </div>
                    <div>
                      <h2 className="text-sm font-bold uppercase tracking-tight text-zinc-200 leading-none group-hover:text-white transition-colors">
                        {tribe.label}
                      </h2>
                    </div>
                  </div>
                </div>

                {/* The "Carved" Shelf Body */}
                <div className="relative bg-[#0a0a0c] p-2 shadow-[inset_0_10px_20px_rgba(0,0,0,0.8)] border-t border-black flex-1 min-h-0 overflow-hidden flex flex-col">
                  {/* Texture Overlay */}
                  <div className="absolute inset-0 pointer-events-none opacity-50 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-zinc-800/20 via-transparent to-transparent" />

                  {/* The Modules (Subcategories) - Fit logic */}
                  <div className="relative z-10 grid grid-cols-2 2xl:grid-cols-3 gap-2 h-full content-start overflow-y-auto scrollbar-thin scrollbar-thumb-zinc-800 scrollbar-track-transparent pr-1">
                    {tribe.spectrum.map((sub) => {
                      const rigColors =
                        (SPECTRUM_BRAND_COLORS as Record<string, string[]>)[
                          sub.id
                        ] || (sub.glowColor ? [sub.glowColor] : [tribe.color]);
                      const mainLight = rigColors[0];

                      return (
                        <button
                          key={sub.id}
                          onClick={() => goToSpectrum(tribe.id, sub.id, [])}
                          className="group/item relative flex flex-col items-center justify-between rounded-lg bg-[#050505] overflow-hidden transition-all duration-300 hover:ring-1 hover:ring-white/10 shadow-[rgba(0,0,0,0.5)_0px_3px_8px] border border-white/5 aspect-[4/3] min-h-0"
                        >
                          {/* 1. The Stage Set (Wall & Floor) */}
                          <div className="absolute inset-x-0 top-0 h-[75%] bg-gradient-to-b from-[#020202] via-[#080808] to-[#000000] z-0" />
                          <div className="absolute inset-x-0 bottom-0 h-[25%] bg-[#050505] z-0 border-t border-white/[0.08]">
                            {/* Floor Reflection - The hot spot where the light hits */}
                            <div
                              className="absolute inset-x-0 top-0 h-full opacity-40 group-hover/item:opacity-60 transition-opacity duration-500 mix-blend-screen"
                              style={{
                                background: `radial-gradient(ellipse 60% 80% at 50% 0%, ${mainLight}, transparent 70%)`,
                              }}
                            />
                            {/* Floor Depth Gradient - Darkens foreground */}
                            <div className="absolute inset-0 bg-gradient-to-b from-transparent via-black/40 to-black/90" />
                          </div>

                          {/* 2. Stage Lighting Rig */}
                          {/* The Main Beam - Focused Cone in the air (Wall) */}
                          <div
                            className="absolute inset-x-0 top-0 h-[75%] opacity-30 group-hover/item:opacity-50 transition-opacity duration-500 mix-blend-screen pointer-events-none z-10"
                            style={{
                              background: `radial-gradient(ellipse 20% 90% at 50% -10%, ${mainLight}, transparent 90%)`,
                            }}
                          />
                          {/* Ambient Spill */}
                          <div
                            className="absolute inset-x-0 top-0 h-[75%] opacity-10 group-hover/item:opacity-20 transition-opacity duration-500 mix-blend-screen pointer-events-none z-10"
                            style={{
                              background: `radial-gradient(circle at 50% 0%, ${mainLight}, transparent 60%)`,
                            }}
                          />

                          {/* The Light Fixtures (Source Dots) */}
                          <div className="absolute top-[3px] left-0 right-0 flex justify-center gap-1.5 z-30 opacity-60 group-hover/item:opacity-100 transition-opacity">
                            {rigColors.slice(0, 5).map((color, idx) => (
                              <div
                                key={idx}
                                className="w-1 h-1 rounded-full blur-[0.5px] bg-white ring-1 ring-white/20"
                                style={{
                                  boxShadow: `0 0 6px 1px ${color}, 0 0 2px ${color}`,
                                }}
                              />
                            ))}
                          </div>

                          {/* 3. Product Thumbnail */}
                          <div className="relative w-full h-[85%] flex items-end justify-center pb-2 z-20 overflow-hidden transform group-hover/item:scale-105 transition-transform duration-500">
                            {/* Shadow on Floor */}
                            <div className="absolute bottom-2 w-1/2 h-2 bg-black/80 blur-md rounded-[100%]" />

                            <img
                              src={sub.image}
                              alt={sub.label}
                              className="w-[90%] h-[90%] object-contain filter brightness-[0.80] contrast-[1.1] saturate-[0.9] group-hover/item:brightness-105 group-hover/item:saturate-[1.1] transition-all duration-300 drop-shadow-2xl"
                            />
                          </div>

                          {/* 4. Label Plate */}
                          <div className="w-full py-1.5 bg-[#030303] border-t border-white/10 z-30 flex items-center justify-center relative shrink-0 shadow-lg">
                            <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest group-hover/item:text-zinc-200 transition-colors truncate px-2">
                              {sub.label}
                            </span>
                            {/* Active Indicator Color */}
                            <div
                              className="absolute bottom-0 left-0 right-0 h-[1px] opacity-0 group-hover/item:opacity-100 transition-opacity shadow-[0_0_8px_1px_rgba(255,255,255,0.2)]"
                              style={{ backgroundColor: mainLight }}
                            />
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Shelf Bottom Lip */}
                <div className="h-1 bg-[#202023] border-t border-white/5 shadow-lg relative rounded-b-xl shrink-0">
                  <div className="absolute inset-x-0 bottom-0 h-px bg-black opacity-50" />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
