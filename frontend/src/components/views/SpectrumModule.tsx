import { Activity, ArrowLeft, Maximize2, ScanLine, Search, Sparkles } from "lucide-react";
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
  const idSpice = p.id.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0) % 20;
  
  return Math.min(100, Math.max(0, score + idSpice));
};

export const SpectrumModule = () => {
  const { activeTribeId, goToGalaxy, openProductPop } = useNavigationStore();

  // --------------------------------------------------------------------------
  // 1. DATA INGESTION
  // --------------------------------------------------------------------------
  const { products: fetchedProducts, availableFilters, loading } = useCategoryCatalog(activeTribeId);

  const rawProducts = useMemo(() => {
    return fetchedProducts.map(p => ({
      ...p,
      score: calculateRelevance(p)
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
      base = rawProducts.filter((p) => (p.tags || p.filters)?.includes(activeFilter));
    }
    // Sort primarily by Price (X-Axis), secondary by Score (Y-Axis)
    return base.sort((a, b) => getPriceValue(a) - getPriceValue(b));
  }, [rawProducts, activeFilter]);

  // --------------------------------------------------------------------------
  // 3. THE RENDER
  // --------------------------------------------------------------------------
  return (
    <div className="flex flex-col h-full bg-[#0b0c10] text-white overflow-hidden relative">
      
      {/* --- TOP DECK --- */}
      <Surface variant="panel" className="h-16 flex items-center px-4 gap-4 z-30 !bg-zinc-900/90 backdrop-blur-md border-b border-zinc-800 shadow-2xl shrink-0">
        <Control onClick={goToGalaxy} className="p-2 rounded-full hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Control>
        <div className="h-8 w-px bg-zinc-800 mx-2" />
        <div className="flex-1 flex items-center gap-3">
          <h2 className="text-2xl font-black italic tracking-tighter text-white uppercase">
            {activeTribeId?.toUpperCase().replace("-", " ")}
          </h2>
          <div className="hidden md:flex items-center gap-2 text-xs font-mono text-zinc-500 border border-zinc-800 rounded-full px-3 py-1 bg-black/50">
            <Search className="w-3 h-3" />
            <span className="text-zinc-300">{filteredProducts.length} units</span>
          </div>
        </div>
      </Surface>

      {/* --- DATA SCREENS (Visualizer) --- */}
      <div className="h-64 grid grid-cols-12 gap-1 p-1 bg-black border-b border-zinc-800 z-20 shrink-0">
        
        {/* LEFT: VISUAL FEED */}
        <Surface variant="screen" active={!!hoveredProduct} className="col-span-3 bg-zinc-950 flex flex-col justify-center items-center p-4 relative !overflow-visible">
          {hoveredProduct ? (
            <div className="w-full h-full flex items-center justify-center relative">
              {!imageLoadError ? (
                <img
                  src={resolveProductImage(hoveredProduct)}
                  className="max-w-[90%] max-h-[90%] object-contain drop-shadow-2xl border-2 border-amber-500"
                  alt="Preview"
                  onError={() => setImageLoadError(true)}
                />
              ) : (
                <div className="flex flex-col items-center gap-3 text-zinc-600 text-center p-2">
                  <ScanLine className="w-8 h-8 opacity-50" />
                  <div className="text-[10px] font-mono tracking-widest text-zinc-700">NO VISUAL</div>
                </div>
              )}
              {/* Score Badge */}
              <div className="absolute top-0 right-0 bg-amber-500 text-black text-[10px] font-black px-1.5 py-0.5 rounded-sm shadow-lg">
                 QS: {hoveredProduct.score || 50}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2 opacity-30">
              <ScanLine className="w-8 h-8 text-zinc-500" />
            </div>
          )}
          <div className="absolute top-2 left-2 text-[9px] text-zinc-600 font-mono tracking-widest">VISUAL_FEED</div>
        </Surface>

        {/* CENTER: DATA STREAM */}
        <Surface variant="screen" active={!!hoveredProduct} className="col-span-6 bg-zinc-950 p-6 flex flex-col relative overflow-hidden">
          {hoveredProduct ? (
            <div className="z-10 animate-fade-in space-y-4 h-full flex flex-col justify-center">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  {hoveredProduct.logo_url && <img src={hoveredProduct.logo_url} className="h-4 opacity-60 invert" alt={hoveredProduct.brand} />}
                  <div className="flex gap-1 flex-wrap">
                    {hoveredProduct.filters?.map((f: string) => (
                      <span key={f} className="text-[9px] px-1.5 py-0.5 border border-zinc-800 text-zinc-500 rounded font-mono uppercase">
                        {f}
                      </span>
                    ))}
                  </div>
                </div>
                <h1 className="text-3xl md:text-5xl font-black italic tracking-tighter text-white uppercase line-clamp-2">
                  {hoveredProduct.name.replace(/[\u0590-\u05FF]+\s*/g, "").trim()}
                </h1>
              </div>

              <div className="grid grid-cols-2 gap-x-12 gap-y-3 border-t border-zinc-900/80 pt-4 overflow-y-auto max-h-[140px] pr-2 custom-scrollbar">
                {hoveredProduct.specs_preview?.map((spec: { key: string; val: string }, idx: number) => (
                  <div key={idx} className="flex justify-between items-baseline group/spec">
                    <span className="text-[10px] text-zinc-600 font-bold uppercase tracking-wider group-hover/spec:text-amber-500 transition-colors">{spec.key}</span>
                    <span className="text-sm text-zinc-300 font-mono truncate text-right">{spec.val}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-zinc-800 gap-2">
              <Activity className="w-12 h-12 opacity-20" />
              <span className="text-xs font-mono tracking-widest">AWAITING SIGNAL INPUT</span>
            </div>
          )}
          <div className="absolute top-2 left-2 text-[9px] text-emerald-800 font-mono tracking-widest flex items-center gap-2">
            <div className={`w-1.5 h-1.5 rounded-full ${hoveredProduct ? "bg-emerald-500 animate-pulse" : "bg-zinc-800"}`} />
            DATA_STREAM
          </div>
        </Surface>

        {/* RIGHT: ACTION */}
        <Surface variant="screen" active={!!hoveredProduct} className="col-span-3 bg-zinc-950 flex flex-col justify-center items-center p-6 relative">
          {hoveredProduct ? (
            <div className="animate-slide-up text-center w-full space-y-4">
              <div>
                <div className="text-4xl font-black text-white tracking-tighter">{getPrice(hoveredProduct)}</div>
                <div className="text-[9px] text-zinc-500 mt-1">VAT INCLUDED</div>
              </div>
              <button onClick={() => openProductPop(hoveredProduct.id)} className="w-full bg-amber-500 hover:bg-amber-400 text-black font-bold py-3 uppercase text-xs tracking-widest transition-all hover:scale-105 flex items-center justify-center gap-2 clip-corner">
                <Maximize2 className="w-3 h-3" /> INSPECT
              </button>
            </div>
          ) : null}
          <div className="absolute top-2 left-2 text-[9px] text-zinc-600 font-mono tracking-widest">TRANSACTION</div>
        </Surface>
      </div>

      {/* --- BOTTOM: TIER BAR ENGINE --- */}
      <div className="flex-1 relative bg-gradient-to-b from-[#050505] to-[#0e0e10] p-0 flex flex-col justify-center overflow-hidden px-8">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center text-zinc-700 font-mono animate-pulse">
            <Sparkles className="w-4 h-4 mr-2 animate-spin" /> INITIALIZING SPECTRUM...
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
      <Surface variant="panel" className="h-16 flex items-center px-4 gap-4 z-30 !bg-zinc-900/90 backdrop-blur-md border-t border-zinc-800 shadow-2xl shrink-0">
        <div className="flex items-center justify-center gap-1 overflow-x-auto no-scrollbar py-2 mask-linear-fade flex-1">
          <Control variant="1176" label="ALL" active={activeFilter === "ALL"} onClick={() => setActiveFilter("ALL")} />
          <div className="w-px h-4 bg-zinc-800 mx-1" />
          {availableFilters.map((filter) => (
            <Control key={filter} variant="1176" label={filter} active={activeFilter === filter} onClick={() => setActiveFilter(filter)} />
          ))}
        </div>
      </Surface>
    </div>
  );
};
