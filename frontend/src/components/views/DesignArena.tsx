import React, { useState } from "react";
import { Monitor, Zap, Hexagon, LayoutGrid, ScanLine } from "lucide-react";

// Arena variant components - create these files and uncomment
// import { GalaxyDashboardA } from "./arena/GalaxyDashboardA";
// import { GalaxyDashboardB } from "./arena/GalaxyDashboardB";
// import { GalaxyDashboardC } from "./arena/GalaxyDashboardC";
// import { SpectrumModuleA } from "./arena/SpectrumModuleA";
// import { SpectrumModuleB } from "./arena/SpectrumModuleB";
// import { SpectrumModuleC } from "./arena/SpectrumModuleC";

type ComponentType = "GalaxyDashboard" | "SpectrumModule";
type Variant = "A" | "B" | "C";

export const DesignArena = () => {
  const [activeComponent, setActiveComponent] =
    useState<ComponentType>("GalaxyDashboard");
  const [activeVariant, setActiveVariant] = useState<Variant>("A");

  return (
    <div className="w-full h-full flex flex-col bg-[#050505] text-white">
      {/* Tab bar: Component + Variant switcher */}
      <div className="h-16 border-b border-zinc-800 flex items-center justify-between px-6 bg-zinc-950/95 z-50 shrink-0">
        <div className="flex items-center gap-4">
          <span className="text-zinc-500 font-mono text-xs tracking-widest uppercase mr-2">
            Design Competition
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setActiveComponent("GalaxyDashboard")}
              className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 ${
                activeComponent === "GalaxyDashboard"
                  ? "bg-blue-600/80 text-white"
                  : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"
              }`}
            >
              <LayoutGrid size={14} /> Galaxy
            </button>
            <button
              onClick={() => setActiveComponent("SpectrumModule")}
              className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 ${
                activeComponent === "SpectrumModule"
                  ? "bg-blue-600/80 text-white"
                  : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"
              }`}
            >
              <ScanLine size={14} /> Spectrum
            </button>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveVariant("A")}
            className={`px-4 py-2 rounded-full text-xs font-bold flex items-center gap-2 transition-all ${
              activeVariant === "A"
                ? "bg-amber-600 text-white shadow-lg shadow-amber-900/50"
                : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"
            }`}
          >
            <Monitor size={14} /> Industrial
          </button>
          <button
            onClick={() => setActiveVariant("B")}
            className={`px-4 py-2 rounded-full text-xs font-bold flex items-center gap-2 transition-all ${
              activeVariant === "B"
                ? "bg-purple-600 text-white shadow-lg shadow-purple-900/50"
                : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"
            }`}
          >
            <Zap size={14} /> Futurist
          </button>
          <button
            onClick={() => setActiveVariant("C")}
            className={`px-4 py-2 rounded-full text-xs font-bold flex items-center gap-2 transition-all ${
              activeVariant === "C"
                ? "bg-white text-black shadow-lg shadow-white/20"
                : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"
            }`}
          >
            <Hexagon size={14} /> Minimalist
          </button>
        </div>
      </div>

      {/* Stage - replace with actual components once variant files exist */}
      <div className="flex-1 overflow-hidden relative">
        <div className="absolute inset-0 flex flex-col items-center justify-center text-zinc-500 font-mono text-sm pointer-events-none">
          <p className="mb-2">Create arena variants and uncomment imports above.</p>
          <p className="text-xs opacity-60">
            {activeComponent} variant {activeVariant}
          </p>
        </div>
        {/* Uncomment when variant files exist:
        <div className="w-full h-full overflow-auto">
          {activeComponent === "GalaxyDashboard" && activeVariant === "A" && <GalaxyDashboardA />}
          {activeComponent === "GalaxyDashboard" && activeVariant === "B" && <GalaxyDashboardB />}
          {activeComponent === "GalaxyDashboard" && activeVariant === "C" && <GalaxyDashboardC />}
          {activeComponent === "SpectrumModule" && activeVariant === "A" && <SpectrumModuleA />}
          {activeComponent === "SpectrumModule" && activeVariant === "B" && <SpectrumModuleB />}
          {activeComponent === "SpectrumModule" && activeVariant === "C" && <SpectrumModuleC />}
        </div>
        */}
      </div>
    </div>
  );
};
