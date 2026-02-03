import {
  Activity,
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
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
import { Control } from "../ui/Control";
import { Surface } from "../ui/Surface";

// --- RELEVANCE ENGINE ---
// Calculates a 0-100 score for Y-Axis positioning
const calculateRelevance = (p: Product): number => {
  let score = 50; // Base score

  // 1. Data Quality Bonuses
  if (p.image_hero || p.image_thumbnail) score += 20;
  if (p.is_bestseller) score += 15;
  if (p.price) score += 10;

  // 2. "Flagship" detection (Arbitrary heuristic for demo)
  // In a real app, this would come from analytics or sales data
  const price = getPriceValue(p);
  if (price > 2000 && price < 15000) score += 10; // Sweet spot for pro gear

  // 3. Penalty for "Ghost" items
  if (!p.image_hero && !p.image_thumbnail) score -= 30;

  // 4. Deterministic "Random" spice based on ID (so it stays consistent)
  const idSpice =
    (p.id || "").split("").reduce((acc, char) => acc + char.charCodeAt(0), 0) %
    20;

  return Math.min(100, Math.max(0, score + idSpice));
};

// --- BRAND LOGO HELPER ---
const BrandLogo = ({
  brand,
  className = "h-8",
}: {
  brand: string;
  className?: string;
}) => {
  const [error, setError] = useState(false);

  // Normalize brand name for file path
  // e.g., "Universal Audio" -> "universal-audio"
  const brandSlug = brand.toLowerCase().replace(/\s+/g, "-");

  // Try to load the logo
  const logoPath = `/assets/logos/${brandSlug}_logo.png`;

  if (error) {
    return (
      <span
        className={`font-black italic uppercase text-lg text-transparent bg-clip-text bg-gradient-to-br from-zinc-500 to-zinc-800 ${className} flex items-center justify-center text-center`}
      >
        {brand}
      </span>
    );
  }

  return (
    <img
      src={logoPath}
      alt={brand}
      className={`object-contain transition-all duration-500 grayscale hover:grayscale-0 ${className}`}
      onError={(e) => {
        const target = e.currentTarget as HTMLImageElement;
        // Fallback chain: png -> jpg -> svg -> text
        if (target.src.endsWith(".png")) {
          target.src = target.src.replace(".png", ".jpg");
        } else if (target.src.endsWith(".jpg")) {
          target.src = target.src.replace(".jpg", ".svg");
        } else {
          setError(true);
        }
      }}
    />
  );
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
  const [scrollPositions, setScrollPositions] = useState<
    Record<string, number>
  >({});

  const handleHoverProduct = (product: Product | null) => {
    setHoveredProduct(product);
    setImageLoadError(false);
  };

  const handleScroll = (trackId: string, direction: "left" | "right") => {
    const trackElement = document.getElementById(`track-${trackId}`);
    if (!trackElement) return;

    const scrollAmount = 400;
    const newPosition =
      (scrollPositions[trackId] || 0) +
      (direction === "right" ? scrollAmount : -scrollAmount);

    trackElement.scrollTo({
      left: newPosition,
      behavior: "smooth",
    });

    setScrollPositions((prev) => ({
      ...prev,
      [trackId]: newPosition,
    }));
  };

  const filteredProducts = useMemo(() => {
    let base = rawProducts;
    if (activeFilter !== "ALL") {
      base = rawProducts.filter((p) =>
        (p.filter_tags || [])?.includes(activeFilter),
      );
    }
    // Sort primarily by Price (X-Axis), secondary by Score (Y-Axis)
    return base.sort((a, b) => getPriceValue(a) - getPriceValue(b));
  }, [rawProducts, activeFilter]);

  // --- BRAND MATRIX ENGINE ---
  const brandMatrix = useMemo(() => {
    if (filteredProducts.length === 0)
      return { brands: [], minPrice: 0, maxPrice: 0 };

    // 1. Calculate Global Range
    const prices = filteredProducts
      .map((p) => getPriceValue(p))
      .filter((p) => p > 0);
    const minPrice = Math.min(...prices) || 0;
    const maxPrice = Math.max(...prices) || 10000;

    // 2. Group by Brand
    const grouped: Record<string, Product[]> = {};
    filteredProducts.forEach((p) => {
      const brand = p.brand_id || "Other";
      if (!grouped[brand]) grouped[brand] = [];
      grouped[brand].push(p);
    });

    // 3. Sort Brands Alphabetically
    const sortedBrands = Object.entries(grouped)
      .sort((a, b) => a[0].localeCompare(b[0]))
      .map(([brand, products]) => ({ brand, products }));

    return { brands: sortedBrands, minPrice, maxPrice };
  }, [filteredProducts]);

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
                      {(hoveredProduct.id || "").split("_")[1] ||
                        hoveredProduct.id ||
                        "N/A"}
                    </span>
                  </div>
                  <h1 className="text-2xl font-black text-white uppercase tracking-tight mt-1 truncate w-full">
                    {hoveredProduct.name}
                  </h1>
                  <div className="text-xs text-amber-500 font-bold uppercase tracking-widest">
                    {hoveredProduct.brand_id || "Unknown Brand"}
                  </div>
                </div>
              </div>

              {/* Description (New) */}
              <div className="text-xs text-zinc-400 font-sans leading-relaxed line-clamp-4 border-l-2 border-zinc-800 pl-3">
                {hoveredProduct.description_short ||
                  stripHtml(
                    hoveredProduct.description_full ||
                      "No description available.",
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
                onClick={() =>
                  hoveredProduct.id && openProductPop(hoveredProduct.id)
                }
                className="w-full bg-amber-500 hover:bg-amber-400 text-black font-extrabold py-4 uppercase text-sm tracking-widest transition-all hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2 clip-corner shadow-amber-900/20 shadow-xl"
              >
                <Maximize2 className="w-4 h-4" />
                <span>Analyze</span>
              </button>
            </div>
          ) : null}
        </Surface>
      </div>

      {/* --- BOTTOM: BRAND SWIMLANES ENGINE --- */}
      <div className="flex-1 relative bg-[#050505] overflow-hidden flex flex-col">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center text-zinc-700 font-mono animate-pulse">
            <Sparkles className="w-4 h-4 mr-2 animate-spin" /> INITIALIZING
            MATRIX...
          </div>
        ) : filteredProducts.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center text-zinc-700 font-mono">
            <div className="text-center">
              <ScanLine className="w-8 h-8 mx-auto mb-4 opacity-50" />
              <span>No products in this sector</span>
            </div>
          </div>
        ) : (
          <div className="w-full h-full flex flex-col">
            {/* Header / Axis Labels (Logarithmic approx labels) */}
            <div className="h-8 flex border-b border-zinc-800/50 bg-black/40 text-[9px] text-zinc-600 font-mono items-end pb-1 px-32 relative">
              <span className="absolute left-32">LOW PRICE</span>
              <div className="flex-1 flex justify-between px-10">
                <span>Entry</span>
                <span>Mid-Range</span>
                <span>Premium</span>
                <span>Elite</span>
              </div>
              <span className="absolute right-8">HIGH PRICE</span>
            </div>

            {/* Scrollable Matrix */}
            <div className="flex-1 overflow-y-auto custom-scrollbar">
              {brandMatrix.brands.map(({ brand, products }) => (
                <div
                  key={brand}
                  className="flex h-20 border-b border-zinc-800/30 hover:bg-zinc-900/20 transition-colors group/row"
                >
                  {/* Brand Header */}
                  <div className="w-32 flex-shrink-0 flex items-center justify-start pl-4 border-r border-zinc-800/30 bg-black/20">
                    <BrandLogo
                      brand={brand}
                      className="max-h-8 max-w-[80px] opacity-50 group-hover/row:opacity-100 transition-opacity"
                    />
                  </div>

                  {/* The Track */}
                  <div className="flex-1 relative flex items-center px-4">
                    {/* We use specific positioning logic: 
                            Logarithmic scale to prevent overlap at low prices 
                        */}
                    {products.map((product) => {
                      const price = getPriceValue(product);
                      // Avoid DBZ
                      const safePrice = price > 0 ? price : 1;
                      const safeMin =
                        brandMatrix.minPrice > 0 ? brandMatrix.minPrice : 1;
                      const safeMax = brandMatrix.maxPrice;

                      // Log scale calculation:
                      // pos = (log(price) - log(min)) / (log(max) - log(min))
                      let pct = 0; // Default (TBD prices go to left)
                      if (price > 0 && safeMax > safeMin) {
                        pct =
                          (Math.log(safePrice) - Math.log(safeMin)) /
                          (Math.log(safeMax) - Math.log(safeMin));
                      }

                      // Clamp
                      pct = Math.max(0, Math.min(1, pct));

                      return (
                        <div
                          key={product.id}
                          className="absolute top-1/2 -translate-y-1/2 group/item z-0 hover:z-50"
                          style={{ left: `${pct * 90}%` }} // limit to 90% so last item doesn't overflow right
                        >
                          {/* The Dot / Thumbnail */}
                          <div
                            className="w-10 h-10 rounded shadow-lg border border-zinc-700 bg-zinc-900 cursor-pointer 
                                    hover:scale-150 hover:border-blue-500 transition-all duration-200 overflow-hidden relative"
                            onClick={() => openProductPop(product.id!)}
                            // Hover Logic
                            onMouseEnter={() => handleHoverProduct(product)}
                            // onMouseLeave={() => handleHoverProduct(null)} // Stickiness feels better
                          >
                            {product.image_thumbnail ? (
                              <img
                                src={resolveProductImage(product)}
                                className="w-full h-full object-cover"
                              />
                            ) : (
                              <div className="w-full h-full bg-zinc-800 flex items-center justify-center text-[8px] text-zinc-500">
                                IMG
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
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
