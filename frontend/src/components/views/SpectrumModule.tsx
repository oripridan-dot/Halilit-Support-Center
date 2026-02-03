import {
  Activity,
  ArrowLeft,
  Maximize2,
  ScanLine,
  Search,
  Sparkles,
} from "lucide-react";
import { useMemo, useState } from "react";
import { resolveProductImage } from "../../lib/imageResolver";
import { getPrice, getPriceValue } from "../../lib/priceFormatter";
import { useNavigationStore } from "../../store/navigationStore";
import type { Product } from "../../types";
import { useCategoryCatalog } from "../../hooks/useCategoryCatalog";
import { TierBar } from "../smart-views/TierBar";
import { Control } from "../ui/Control";
import { Surface } from "../ui/Surface";

// --- RELEVANCE ENGINE ---
// Calculates a 0-100 score for Y-Axis positioning
const calculateRelevance = (p: Product): number => {
  let score = 50; // Base score

  // 1. Data Quality Bonuses
  if (p.image || p.image_url) score += 20;
  if (p.verified) score += 15;
  if (p.pricing) score += 10;

  // 2. "Flagship" detection (Arbitrary heuristic for demo)
  // In a real app, this would come from analytics or sales data
  const price = getPriceValue(p);
  if (price > 2000 && price < 15000) score += 10; // Sweet spot for pro gear

  // 3. Penalty for "Ghost" items
  if (!p.image && !p.image_url) score -= 30;

  // 4. Deterministic "Random" spice based on ID (so it stays consistent)
  const idSpice =
    p.id.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0) % 20;

  return Math.min(100, Math.max(0, score + idSpice));
};

export const SpectrumModule = () => {
  const { activeTribeId, goToGalaxy, openProductPop } = useNavigationStore();

  // --------------------------------------------------------------------------
  // 1. DATA INGESTION
  // --------------------------------------------------------------------------
  const catalogResult = useCategoryCatalog(activeTribeId);
  const fetchedProducts = catalogResult.data?.products || [];
  const availableFilters = catalogResult.data?.availableFilters || [];
  const { loading, error } = catalogResult;

  const rawProducts = useMemo(() => {
    return fetchedProducts.map((p) => ({
      ...p,
      score: calculateRelevance(p),
    }));
  }, [fetchedProducts]);

  // --------------------------------------------------------------------------
  // 2. THE 1176 ENGINE (Filtering)
  // --------------------------------------------------------------------------
  const [activeFilter, setActiveFilter] = useState("ALL");
  const [hoveredProduct, setHoveredProduct] = useState<Product | null>(null);
  const [imageLoadError, setImageLoadError] = useState(false);

  const handleHoverProduct = (product: Product | null) => {
    setHoveredProduct(product);
    setImageLoadError(false);
  };

  const filteredProducts = useMemo(() => {
    let base = rawProducts;
    if (activeFilter !== "ALL") {
      base = rawProducts.filter((p) =>
        (p.tags || p.filters)?.includes(activeFilter),
      );
    }
    // Sort primarily by Price (X-Axis), secondary by Score (Y-Axis)
    return base.sort((a, b) => getPriceValue(a) - getPriceValue(b));
  }, [rawProducts, activeFilter]);

  // Handle errors
  if (error) {
    return (
      <div className="flex h-full w-full items-center justify-center flex-col gap-4 bg-red-950/20 border border-red-900 rounded-lg">
        <div className="text-red-400 font-bold">Failed to load catalog</div>
        <div className="text-sm text-red-300">{error.message}</div>
        <button
          onClick={() => catalogResult.retry()}
          className="px-4 py-2 bg-red-900 hover:bg-red-800 text-red-100 rounded text-xs"
        >
          Retry
        </button>
      </div>
    );
  }

  // --------------------------------------------------------------------------
  // 3. THE RENDER
  // --------------------------------------------------------------------------
  const stripHtml = (html: string) => html.replace(/<[^>]*>?/gm, "");

  return (
    <div className="flex flex-col h-full bg-[#0b0c10] text-white overflow-hidden relative">
      {/* --- TOP DECK --- */}
      <Surface
        variant="panel"
        className="h-16 flex items-center px-4 gap-4 z-30 !bg-zinc-900/90 backdrop-blur-md border-b border-zinc-800 shadow-2xl shrink-0"
      >
        <Control
          onClick={goToGalaxy}
          className="p-2 rounded-full hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </Control>
        <div className="h-8 w-px bg-zinc-800 mx-2" />
        <div className="flex-1 flex items-center gap-3">
          <h2 className="text-2xl font-black italic tracking-tighter text-white uppercase">
            {activeTribeId?.toUpperCase().replace("-", " ")}
          </h2>
          <div className="hidden md:flex items-center gap-2 text-xs font-mono text-zinc-500 border border-zinc-800 rounded-full px-3 py-1 bg-black/50">
            <Search className="w-3 h-3" />
            <span className="text-zinc-300">
              {filteredProducts.length} units
            </span>
          </div>
        </div>
      </Surface>

      {/* --- DATA SCREENS (Visualizer) --- */}
      <div className="h-[45vh] grid grid-cols-12 gap-1 p-1 bg-black border-b border-zinc-800 z-40 shrink-0 shadow-2xl relative transition-all duration-300">
        {/* LEFT: VISUAL FEED (IMAGE ONLY) */}
        <Surface
          variant="screen"
          active={!!hoveredProduct}
          className="col-span-4 bg-zinc-950 flex flex-col justify-center items-center p-4 relative overflow-hidden"
        >
          {hoveredProduct ? (
            <div className="w-full h-full flex items-center justify-center relative bg-white/5 p-4 rounded-sm">
              {!imageLoadError ? (
                <img
                  src={resolveProductImage(hoveredProduct)}
                  className="max-w-full max-h-full object-contain drop-shadow-2xl transition-transform duration-500 will-change-transform"
                  alt="Preview"
                  onError={() => setImageLoadError(true)}
                />
              ) : (
                <div className="flex flex-col items-center gap-2 text-zinc-600 text-center p-2">
                  <ScanLine className="w-8 h-8 opacity-50" />
                  <span className="text-[10px] font-mono uppercase tracking-widest">
                    NO VISUAL
                  </span>
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center gap-4 text-zinc-800">
              <Sparkles className="w-12 h-12 opacity-20" />
              <div className="text-xs font-mono tracking-[0.2em] uppercase opacity-50">
                AWAITING SIGNAL
              </div>
            </div>
          )}
        </Surface>

        {/* MIDDLE: SPECS AND INFO */}
        <Surface
          variant="screen"
          active={!!hoveredProduct}
          className="col-span-5 bg-zinc-950 flex flex-col p-6 relative overflow-hidden"
        >
          {hoveredProduct ? (
            <div className="flex flex-col h-full gap-4">
              {/* Header */}
              <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
                <div className="flex flex-col overflow-hidden">
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-[10px] text-emerald-500 font-mono tracking-widest">
                      ID REF:{" "}
                      {hoveredProduct.id.split("_")[1] || hoveredProduct.id}
                    </span>
                  </div>
                  <h1 className="text-2xl font-black text-white uppercase tracking-tight mt-1 truncate w-full">
                    {hoveredProduct.name}
                  </h1>
                  <div className="text-xs text-amber-500 font-bold uppercase tracking-widest">
                    {hoveredProduct.brand}
                  </div>
                </div>
              </div>

              {/* Description (New) */}
              <div className="text-xs text-zinc-400 font-sans leading-relaxed line-clamp-4 border-l-2 border-zinc-800 pl-3">
                {hoveredProduct.short_description ||
                  stripHtml(
                    hoveredProduct.description || "No description available.",
                  )}
              </div>

              {/* Specs Grid */}
              <div className="mt-auto grid grid-cols-2 gap-2 text-[10px] font-mono text-zinc-500">
                {hoveredProduct.specs?.slice(0, 4).map((spec, i) => (
                  <div
                    key={i}
                    className="flex flex-col bg-zinc-900/50 p-2 border border-zinc-800/50 rounded-sm"
                  >
                    <span className="text-amber-500/50 uppercase text-[9px] mb-1">
                      {spec.name}
                    </span>
                    <span className="text-zinc-300 truncate">{spec.value}</span>
                  </div>
                ))}
                {(!hoveredProduct.specs ||
                  hoveredProduct.specs.length === 0) && (
                  <div className="col-span-2 text-center text-zinc-700 italic py-2">
                    Technical specifications unavailable
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="h-full w-full flex items-center justify-center">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-zinc-800 animate-pulse" />
                <span className="text-zinc-800 text-xs font-mono tracking-widest">
                  NO DATA STREAM
                </span>
              </div>
            </div>
          )}
        </Surface>

        {/* RIGHT: ACTION & PRICE */}
        <Surface
          variant="screen"
          active={!!hoveredProduct}
          className="col-span-3 bg-zinc-950 flex flex-col justify-center items-center p-6 relative"
        >
          {hoveredProduct ? (
            <div className="animate-slide-up text-center w-full space-y-6">
              <div>
                <div className="text-4xl lg:text-5xl font-black text-white tracking-tighter tabular-nums text-shadow-glow">
                  {getPrice(hoveredProduct)}
                </div>
                <div className="text-[10px] text-zinc-500 font-bold tracking-widest uppercase mt-2">
                  Price (VAT Included)
                </div>
              </div>

              <div className="w-full h-px bg-zinc-800" />

              <button
                onClick={() => openProductPop(hoveredProduct.id)}
                className="w-full bg-amber-500 hover:bg-amber-400 text-black font-extrabold py-4 uppercase text-sm tracking-widest transition-all hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2 clip-corner shadow-amber-900/20 shadow-xl"
              >
                <Maximize2 className="w-4 h-4" />
                <span>Analyze</span>
              </button>
            </div>
          ) : null}
        </Surface>
      </div>

      {/* --- BOTTOM: TIER BAR ENGINE --- */}
      <div className="flex-1 relative bg-gradient-to-b from-[#050505] to-[#0e0e10] p-0 flex flex-col justify-center overflow-hidden px-8">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center text-zinc-700 font-mono animate-pulse">
            <Sparkles className="w-4 h-4 mr-2 animate-spin" /> INITIALIZING
            SPECTRUM...
          </div>
        ) : (
          <div className="w-full h-full relative z-10">
            <TierBar
              products={filteredProducts}
              onHoverProduct={handleHoverProduct}
              onSelectProduct={openProductPop}
            />
          </div>
        )}
      </div>

      {/* --- BOTTOM DECK: 1176 FILTER CONTROLS --- */}
      <Surface
        variant="panel"
        className="h-16 flex items-center px-4 gap-4 z-30 !bg-zinc-900/90 backdrop-blur-md border-t border-zinc-800 shadow-2xl shrink-0"
      >
        <div className="flex items-center justify-center gap-1 overflow-x-auto no-scrollbar py-2 mask-linear-fade flex-1">
          <Control
            variant="1176"
            label="ALL"
            active={activeFilter === "ALL"}
            onClick={() => setActiveFilter("ALL")}
          />
          <div className="w-px h-4 bg-zinc-800 mx-1" />
          {availableFilters.map((filter) => (
            <Control
              key={filter}
              variant="1176"
              label={filter}
              active={activeFilter === filter}
              onClick={() => setActiveFilter(filter)}
            />
          ))}
        </div>
      </Surface>
    </div>
  );
};
