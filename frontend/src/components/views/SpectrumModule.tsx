import { Activity, ArrowLeft, Maximize2, ScanLine, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { resolveProductImage } from "../../lib/imageResolver";
import { getPrice, getPriceValue } from "../../lib/priceFormatter";
import { useNavigationStore } from "../../store/navigationStore";
import type { Product } from "../../types";
import { TierBar } from "../smart-views/TierBar";
import { Control } from "../ui/Control";
import { Surface } from "../ui/Surface";

export const SpectrumModule = () => {
  const { activeTribeId, goToGalaxy, openProductPop } = useNavigationStore();

  // --------------------------------------------------------------------------
  // 1. DATA INGESTION (The Superfast Category Catalog)
  // --------------------------------------------------------------------------
  const [rawProducts, setRawProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load products by category ID
    const loadCatalog = async () => {
      setLoading(true);
      try {
        const { catalogLoader } = await import("../../lib/catalogLoader");

        if (!activeTribeId) {
          setRawProducts([]);
          setLoading(false);
          return;
        }

        // Load all products that match the category
        const products =
          await catalogLoader.loadProductsByCategory(activeTribeId);

        if (Array.isArray(products)) {
          setRawProducts(products);
        } else {
          setRawProducts([]);
        }
      } catch {
        setRawProducts([]);
      } finally {
        setLoading(false);
      }
    };
    if (activeTribeId) {
      loadCatalog();
    } else {
      setLoading(false);
    }
  }, [activeTribeId]);

  // --------------------------------------------------------------------------
  // 2. THE 1176 ENGINE (Automatic Sub-Division)
  // --------------------------------------------------------------------------
  const [activeFilter, setActiveFilter] = useState("ALL");
  const [hoveredProduct, setHoveredProduct] = useState<Product | null>(null);
  const [imageLoadError, setImageLoadError] = useState(false);

  // A. Extract Unique Filters dynamically from the data
  //    This ensures buttons only exist if products exist for them.
  const availableFilters = useMemo(() => {
    const filterSet = new Set<string>();
    rawProducts.forEach((p) => {
      if (p.filters) p.filters.forEach((f: string) => filterSet.add(f));
    });
    return Array.from(filterSet).sort();
  }, [rawProducts]);

  // Reset image error state when product changes
  useEffect(() => {
    setImageLoadError(false);
  }, [hoveredProduct]);

  // B. Apply Filter to TierBar
  const filteredProducts = useMemo(() => {
    let base = rawProducts;

    if (activeFilter !== "ALL") {
      base = rawProducts.filter((p) => p.filters?.includes(activeFilter));
    }

    // Sort by price for the TierBar logic
    return base.sort((a, b) => getPriceValue(a) - getPriceValue(b));
  }, [rawProducts, activeFilter]);

  // --------------------------------------------------------------------------
  // 3. THE RENDER
  // --------------------------------------------------------------------------
  return (
    <div className="flex flex-col h-full bg-[#0b0c10] text-white overflow-hidden relative">
      {/* --- TOP DECK: SPECTRUM MODULE TITLE --- */}
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

        {/* Active Search Title */}
        <div className="flex-1 flex items-center gap-3">
          <h2 className="text-2xl font-black italic tracking-tighter text-white uppercase">
            {activeTribeId?.toUpperCase().replace("-", " ")}
          </h2>
          <div className="hidden md:flex items-center gap-2 text-xs font-mono text-zinc-500 border border-zinc-800 rounded-full px-3 py-1 bg-black/50">
            <Search className="w-3 h-3" />
            <span className="text-zinc-300">
              {filteredProducts.length} results
            </span>
          </div>
        </div>
      </Surface>

      {/* --- DATA SCREENS (The Flight Case Displays) --- */}
      <div className="h-64 grid grid-cols-12 gap-1 p-1 bg-black border-b border-zinc-800 z-20 shrink-0">
        {/* LEFT: VISUAL FEED */}
        <Surface
          variant="screen"
          active={!!hoveredProduct}
          className="col-span-3 bg-zinc-950 flex flex-col justify-center items-center p-4 relative !overflow-visible"
        >
          {hoveredProduct ? (
            <div className="w-full h-full flex items-center justify-center relative">
              {!imageLoadError ? (
                <img
                  src={resolveProductImage(hoveredProduct)}
                  className="max-w-[90%] max-h-[90%] object-contain drop-shadow-2xl border-2 border-amber-500"
                  alt="Preview"
                  onError={(_e) => {
                    setImageLoadError(true);
                  }}
                  onLoad={() => {
                    setImageLoadError(false);
                  }}
                />
              ) : (
                <div className="flex flex-col items-center gap-3 text-zinc-600 text-center p-2">
                  <div className="text-4xl opacity-20">📸</div>
                  <div className="text-xs font-mono tracking-widest text-zinc-700">
                    IMAGE FAILED TO LOAD
                  </div>
                  <div className="text-[8px] font-mono text-zinc-600 break-all max-w-full">
                    {resolveProductImage(hoveredProduct)}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2 opacity-30">
              <ScanLine className="w-8 h-8 text-zinc-500" />
            </div>
          )}
          <div className="absolute top-2 left-2 text-[9px] text-zinc-600 font-mono tracking-widest">
            VISUAL_FEED
          </div>
        </Surface>

        {/* CENTER: DATA STREAM */}
        <Surface
          variant="screen"
          active={!!hoveredProduct}
          className="col-span-6 bg-zinc-950 p-6 flex flex-col relative overflow-hidden"
        >
          {hoveredProduct ? (
            <div className="z-10 animate-fade-in space-y-4 h-full flex flex-col justify-center">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <img
                    src={hoveredProduct.logo_url}
                    className="h-5 opacity-60 invert"
                    alt={hoveredProduct.brand}
                  />
                  <div className="flex gap-1">
                    {hoveredProduct.filters?.slice(0, 3).map((f: string) => (
                      <span
                        key={f}
                        className="text-[9px] px-1.5 py-0.5 border border-zinc-800 text-zinc-500 rounded font-mono uppercase"
                      >
                        {f}
                      </span>
                    ))}
                  </div>
                </div>
                <h1 className="text-3xl md:text-5xl font-black italic tracking-tighter text-white uppercase line-clamp-2">
                  {hoveredProduct.name
                    .replace(/[\u0590-\u05FF]+\s*/g, "")
                    .trim()}
                </h1>
              </div>

              <div className="grid grid-cols-2 gap-x-12 gap-y-3 border-t border-zinc-900/80 pt-4">
                {hoveredProduct.specs_preview?.map(
                  (spec: { key: string; val: string }, idx: number) => (
                    <div
                      key={idx}
                      className="flex justify-between items-baseline group/spec"
                    >
                      <span className="text-[10px] text-zinc-600 font-bold uppercase tracking-wider group-hover/spec:text-amber-500 transition-colors">
                        {spec.key}
                      </span>
                      <span className="text-sm text-zinc-300 font-mono truncate text-right">
                        {spec.val}
                      </span>
                    </div>
                  ),
                )}
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-zinc-800 gap-2">
              <Activity className="w-12 h-12 opacity-20" />
              <span className="text-xs font-mono tracking-widest">
                AWAITING SIGNAL INPUT
              </span>
            </div>
          )}
          <div className="absolute top-2 left-2 text-[9px] text-emerald-800 font-mono tracking-widest flex items-center gap-2">
            <div
              className={`w-1.5 h-1.5 rounded-full ${hoveredProduct ? "bg-emerald-500 animate-pulse" : "bg-zinc-800"}`}
            />
            DATA_STREAM
          </div>
        </Surface>

        {/* RIGHT: ACTION */}
        <Surface
          variant="screen"
          active={!!hoveredProduct}
          className="col-span-3 bg-zinc-950 flex flex-col justify-center items-center p-6 relative"
        >
          {hoveredProduct ? (
            <div className="animate-slide-up text-center w-full space-y-4">
              <div>
                <div className="text-4xl font-black text-white tracking-tighter">
                  {getPrice(hoveredProduct)}
                </div>
                <div className="text-[9px] text-zinc-500 mt-1">
                  VAT INCLUDED
                </div>
              </div>
              <button
                onClick={() => openProductPop(hoveredProduct.id)}
                className="w-full bg-amber-500 hover:bg-amber-400 text-black font-bold py-3 uppercase text-xs tracking-widest transition-all hover:scale-105 flex items-center justify-center gap-2 clip-corner"
              >
                <Maximize2 className="w-3 h-3" /> Inspect
              </button>
            </div>
          ) : null}
          <div className="absolute top-2 left-2 text-[9px] text-zinc-600 font-mono tracking-widest">
            TRANSACTION
          </div>
        </Surface>
      </div>

      {/* --- BOTTOM: TIER BAR ENGINE --- */}
      <div className="flex-1 relative bg-gradient-to-b from-[#050505] to-[#0e0e10] p-4 flex flex-col justify-center overflow-hidden">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center text-zinc-700 font-mono animate-pulse">
            INITIALIZING SPECTRUM...
          </div>
        ) : (
          <div className="w-full max-w-[98%] mx-auto relative z-10 h-full flex items-end pb-20">
            <TierBar
              products={filteredProducts}
              onHoverProduct={setHoveredProduct}
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
        <div className="flex items-center gap-1 overflow-x-auto no-scrollbar py-2 mask-linear-fade flex-1">
          {/* Master Reset Button */}
          <Control
            variant="1176"
            label="ALL"
            active={activeFilter === "ALL"}
            onClick={() => setActiveFilter("ALL")}
          />

          {/* Separator */}
          <div className="w-px h-4 bg-zinc-800 mx-1" />

          {/* Dynamic Sub-Divisions */}
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
