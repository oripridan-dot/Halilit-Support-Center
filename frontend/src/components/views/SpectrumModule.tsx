import React from "react";
import {
  Activity,
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  Maximize2,
  ScanLine,
  Search,
  Sparkles,
  Star,
  CheckCircle,
  AlertCircle,
  ExternalLink,
  Package,
  Tag,
  Zap,
} from "lucide-react";
import { useMemo, useState, useCallback } from "react";
import { resolveProductImage } from "../../lib/imageResolver";
import { getPrice, getPriceValue } from "../../lib/priceFormatter";
import { useNavigationStore } from "../../store/navigationStore";
import { getBrandLogoUrl } from "../../lib/brandLogoHelper";
import type { Product } from "../../types";
import {
  useConductorCatalog,
  useConductorProductsByCategory,
} from "../../hooks/useConductorCatalog";
import { getConsolidatedProductCategory } from "../../lib/categoryConsolidator";
import { Control } from "../ui/Control";
import { Surface } from "../ui/Surface";
import { getBrandTheme } from "../../styles/brandThemes";

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

// --- HEALTH CHECK ENGINE ---
const isProductHealthy = (p: Product): boolean => {
  // 1. Critical: Must have a name
  if (!p.product_name || p.product_name.trim().length === 0) return false;

  // 2. Critical: Must have a valid price
  // (We use getPriceValue which handles multiple fields. If 0, it's effectively TBD or invalid)
  const price = getPriceValue(p);
  if (price <= 0) return false;

  return true;
};

// --- BRAND LOGO HELPER ---
const BrandLogo = React.memo(
  ({ brand, className = "h-8" }: { brand: string; className?: string }) => {
    const [error, setError] = useState(false);

    // Use the helper to get the correct mapped logo (handles SVGs, special cases)
    const logoPath =
      getBrandLogoUrl(brand) ||
      `/assets/logos/${brand.toLowerCase().replace(/\s+/g, "-")}_logo.png`;

    if (error || !logoPath) {
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
        className={`object-contain transition-all duration-500 ${className}`}
        onError={(e) => {
          const target = e.currentTarget as HTMLImageElement;
          console.warn(
            `[BrandLogo] Failed to load logo for ${brand}: ${target.src}`,
          );

          // If we started with an SVG and it failed, fail immediately to text
          if (target.src.endsWith(".svg")) {
            setError(true);
            return;
          }

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
  },
);

BrandLogo.displayName = "BrandLogo";

// --- DATA SOURCES BADGE ---
const DataSourcesBadge = ({
  sources = [],
  brand,
}: {
  sources?: string[];
  brand: string;
}) => {
  return (
    <div className="flex gap-4 items-center mt-1">
      {/* Halilit Source (Use pseudo-logo since no image file exists) */}
      <div
        className="flex flex-col items-center gap-1 opacity-80 hover:opacity-100 transition-opacity"
        title="Commercial Source: Halilit.com"
      >
        <div className="h-8 w-8 bg-blue-600 rounded-md flex items-center justify-center shadow-lg shadow-blue-900/20 text-white font-black italic text-[10px] tracking-tighter">
          ZL
        </div>
        <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
          Halilit
        </span>
      </div>

      <div className="h-6 w-px bg-zinc-800" />

      {/* Official Source (Brand Logo) */}
      <div
        className="flex flex-col items-center gap-1 opacity-80 hover:opacity-100 transition-opacity"
        title={`Official Source: ${brand} Website`}
      >
        <BrandLogo brand={brand} className="h-8 w-auto max-w-[60px]" />
        <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
          Official
        </span>
      </div>
    </div>
  );
};

// --- ENRICHMENT INFO PANEL ---
const EnrichmentPanel = React.memo(
  ({
    product,
  }: {
    product: Product & {
      official_specs?: any;
      review_data?: any;
      sources?: string[];
    };
  }) => {
    return (
      <div className="space-y-4 text-[11px]">
        {/* Official Specs Section */}
        {product.official_specs &&
          Object.keys(product.official_specs).length > 0 && (
            <div className="border-l-2 border-emerald-600/50 bg-emerald-950/30 p-3 rounded-sm">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-3 h-3 text-emerald-500" />
                <span className="font-bold text-emerald-400 uppercase tracking-widest">
                  Official Specs
                </span>
              </div>
              <div className="space-y-1 text-zinc-300">
                {Object.entries(product.official_specs)
                  .filter(([key]) => key !== "note" && key !== "extracted_name") // Filter out metadata
                  .slice(0, 5) // Limit just in case
                  .map(([key, value]) => (
                    <div key={key} className="flex gap-1 break-words">
                      <span className="text-emerald-600 mt-0.5">◆</span>
                      <span className="text-emerald-500/80 capitalize">
                        {key.replace(/_/g, " ")}:
                      </span>
                      <span className="text-zinc-200">{String(value)}</span>
                    </div>
                  ))}
              </div>
            </div>
          )}

        {/* Review Data Section */}
        {product.review_data && product.review_data.aggregate_rating && (
          <div className="border-l-2 border-amber-600/50 bg-amber-950/30 p-3 rounded-sm">
            <div className="flex items-center gap-2 mb-2">
              <Star className="w-3 h-3 text-amber-500 fill-amber-500" />
              <span className="font-bold text-amber-400 uppercase tracking-widest">
                Trusted Reviews
              </span>
            </div>
            <div className="space-y-2 text-zinc-300">
              <div className="flex items-center gap-2">
                <div className="flex gap-0.5">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`w-2.5 h-2.5 ${
                        i < Math.floor(product.review_data.aggregate_rating)
                          ? "fill-amber-400 text-amber-400"
                          : "text-zinc-700"
                      }`}
                    />
                  ))}
                </div>
                <span className="font-bold text-amber-400">
                  {product.review_data.aggregate_rating.toFixed(1)}
                </span>
                <span className="text-zinc-600">
                  ({product.review_data.total_reviews} reviews)
                </span>
              </div>
              {product.review_data.pros_and_cons?.pros && (
                <div>
                  <span className="text-amber-500 text-[10px] font-bold">
                    Pros:
                  </span>
                  <div className="text-[10px] text-zinc-400">
                    {product.review_data.pros_and_cons.pros
                      .slice(0, 2)
                      .join(" • ")}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Data Provenance */}
        <div className="border-l-2 border-blue-600/50 bg-blue-950/30 p-3 rounded-sm">
          <div className="flex items-center gap-2 mb-2">
            <Package className="w-3 h-3 text-blue-500" />
            <span className="font-bold text-blue-400 uppercase tracking-widest">
              Data Sources
            </span>
          </div>
          <DataSourcesBadge
            sources={product.sources || ["halilit_direct"]}
            brand={product.brand || "Unknown"}
          />
        </div>
      </div>
    );
  },
);

EnrichmentPanel.displayName = "EnrichmentPanel";

// --- BRAND SWIM LANE (memoized to avoid re-rendering all tracks on hover) ---
interface BrandTrackProps {
  brand: string;
  products: Product[];
  rgbColor: string;
  brandPrimary: string;
  minPrice: number;
  maxPrice: number;
  onHoverProduct: (product: Product | null) => void;
  onClickProduct: (id: string) => void;
}

const BrandTrack = React.memo(
  ({
    brand,
    products,
    rgbColor,
    brandPrimary,
    minPrice,
    maxPrice,
    onHoverProduct,
    onClickProduct,
  }: BrandTrackProps) => {
    const safeMin = minPrice > 0 ? minPrice : 1;

    return (
      <div
        className="flex h-24 border-b transition-colors duration-200 group/row hover:bg-white/5 hover:shadow-lg"
        style={{
          borderColor: `rgba(${rgbColor}, 0.2)`,
          backgroundColor: `rgba(${rgbColor}, 0.04)`,
        }}
      >
        {/* Brand Header */}
        <div
          className="w-32 flex-shrink-0 flex items-center justify-center pl-4 border-r transition-all duration-200"
          style={{
            borderColor: `rgba(${rgbColor}, 0.3)`,
            backgroundColor: `rgba(${rgbColor}, 0.08)`,
          }}
        >
          <div className="flex flex-col gap-1 items-center justify-center flex-1 w-full h-full relative">
            <div className="absolute inset-0 flex items-center justify-center p-2">
              <BrandLogo
                brand={brand}
                className="max-h-full max-w-full w-auto h-auto object-contain transition-opacity opacity-90 hover:opacity-100"
              />
            </div>
            <span
              className="text-[9px] font-bold uppercase tracking-widest absolute bottom-1 right-2 bg-black/50 px-1 rounded backdrop-blur-sm"
              style={{ color: brandPrimary }}
            >
              {products.length}
            </span>
          </div>
        </div>

        {/* The Track */}
        <div className="flex-1 relative flex items-center px-4">
          {products.map((product) => {
            const price = getPriceValue(product);
            const safePrice = price > 0 ? price : 1;

            let pct = 0;
            if (price > 0 && maxPrice > safeMin) {
              pct =
                (Math.log(safePrice) - Math.log(safeMin)) /
                (Math.log(maxPrice) - Math.log(safeMin));
            }
            pct = Math.max(0, Math.min(1, pct));

            return (
              <div
                key={product.id}
                className="absolute top-1/2 -translate-y-1/2 group/item z-0 hover:z-50"
                style={{ left: `${5 + pct * 90}%` }}
              >
                <div
                  className="w-[60px] h-[60px] rounded shadow-lg bg-zinc-900 cursor-pointer hover:scale-110 transition-all duration-200 overflow-hidden relative"
                  style={{
                    borderWidth: "2px",
                    borderColor: brandPrimary,
                    boxShadow:
                      "0 0 0 1px rgba(0,0,0,0.5), 0 4px 6px rgba(0,0,0,0.4)",
                  }}
                  onClick={() => onClickProduct(product.id!)}
                  onMouseEnter={() => onHoverProduct(product)}
                >
                  <img
                    src={resolveProductImage(product)}
                    className="w-full h-full object-contain rounded-sm absolute inset-0 bg-white"
                    loading="lazy"
                    alt={product.name}
                  />
                  <div
                    className="absolute inset-0 rounded pointer-events-none opacity-0 group-hover/item:opacity-100 transition-opacity duration-200"
                    style={{
                      boxShadow: `0 0 12px ${brandPrimary}80, inset 0 0 8px ${brandPrimary}40`,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  },
);

BrandTrack.displayName = "BrandTrack";

// --- UTILITY: hex to RGB string ---
const hexToRgb = (hex: string): string => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}`
    : "100, 100, 100";
};

export const SpectrumModule = () => {
  const { activeTribeId, goToGalaxy, openProductPage } = useNavigationStore();

  // --------------------------------------------------------------------------
  // 1. DATA INGESTION - Using Conductor Verified Data
  // --------------------------------------------------------------------------
  // Get all products from Conductor catalog
  const {
    products: allProducts,
    isLoading,
    error,
    categories,
  } = useConductorCatalog();

  // Filter by category (activeTribeId is a galaxy ID like "keys-production")
  const fetchedProducts = useMemo(() => {
    if (!activeTribeId) return allProducts;

    // Use the consolidator to map each product to its galaxy ID and match
    return allProducts.filter((p) => {
      try {
        const { galaxyId } = getConsolidatedProductCategory(p as any);
        return galaxyId === activeTribeId;
      } catch {
        return false;
      }
    });
  }, [allProducts, activeTribeId]);

  const availableFilters = useMemo(() => {
    // Extract unique display roles, pricing tiers, etc. from fetched products
    const filters = new Set<string>();
    fetchedProducts.forEach((p) => {
      filters.add(p.display.display_role || "All");
      filters.add(p.pricing.tier || "All");
    });
    return Array.from(filters);
  }, [fetchedProducts]);

  const rawProducts = useMemo(() => {
    // Backend normalizer guarantees consistent shape — just add relevance score
    return fetchedProducts.map(
      (p: any) =>
        ({
          ...p,
          score: calculateRelevance(p as any),
        }) as Product,
    );
  }, [fetchedProducts]);

  // --- HEALTH SEGREGATION LAYER ---
  const { cleanProducts, flaggedCount } = useMemo(() => {
    const valid = rawProducts.filter(isProductHealthy);
    const broken = rawProducts.length - valid.length;

    if (broken > 0) {
      console.warn(
        `[HealthGuard] Flagged ${broken} products as broken/incomplete.`,
      );
    }

    return { cleanProducts: valid, flaggedCount: broken };
  }, [rawProducts]);

  // --------------------------------------------------------------------------
  // 2. THE 1176 ENGINE (Filtering)
  // --------------------------------------------------------------------------
  const [activeFilter, setActiveFilter] = useState("ALL");
  const [hoveredProduct, setHoveredProduct] = useState<Product | null>(null);
  const [imageLoadError, setImageLoadError] = useState(false);

  const handleHoverProduct = useCallback((product: Product | null) => {
    setHoveredProduct(product);
    setImageLoadError(false);
  }, []);

  const handleClickProduct = useCallback(
    (id: string) => {
      openProductPage(id);
    },
    [openProductPage],
  );

  const filteredProducts = useMemo(() => {
    let base = cleanProducts;
    if (activeFilter !== "ALL") {
      base = cleanProducts.filter((p) =>
        (p.filter_tags || [])?.includes(activeFilter),
      );
    }
    // Sort primarily by Price (X-Axis), secondary by Score (Y-Axis)
    return base.sort((a, b) => getPriceValue(a) - getPriceValue(b));
  }, [cleanProducts, activeFilter]);

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
      const brand = p.brand_id || p.brand || "Other";
      if (!grouped[brand]) grouped[brand] = [];
      grouped[brand].push(p);
    });

    // 3. Sort Brands Alphabetically (with Nord priority) + pre-compute RGB
    const sortedBrands = Object.entries(grouped)
      .sort((a, b) => {
        const brandA = a[0].toLowerCase();
        const brandB = b[0].toLowerCase();

        // Strict priority for Nord
        if (brandA === "nord") return -1;
        if (brandB === "nord") return 1;

        return a[0].localeCompare(b[0]);
      })
      .map(([brand, products]) => {
        const theme = getBrandTheme(brand);
        return {
          brand,
          products,
          brandPrimary: theme.primary,
          rgbColor: hexToRgb(theme.primary),
        };
      });

    return { brands: sortedBrands, minPrice, maxPrice };
  }, [filteredProducts]);

  // Handle errors
  if (error) {
    return (
      <div className="flex h-full w-full items-center justify-center flex-col gap-4 bg-red-950/20 border border-red-900 rounded-lg">
        <div className="text-red-400 font-bold">Failed to load catalog</div>
        <div className="text-sm text-red-300">{error}</div>
        <button
          onClick={() => window.location.reload()}
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
          {flaggedCount > 0 && (
            <div
              className="hidden md:flex items-center gap-2 text-xs font-mono text-amber-500/80 border border-amber-900/30 rounded-full px-3 py-1 bg-amber-950/20"
              title="Items hidden due to missing price or name"
            >
              <AlertCircle className="w-3 h-3" />
              <span>{flaggedCount} issues resolved</span>
            </div>
          )}
        </div>
      </Surface>

      {/* --- DATA SCREENS (Visualizer) --- */}
      <div className="h-[35vh] grid grid-cols-12 gap-1 p-1 bg-black border-b border-zinc-800 z-40 shrink-0 shadow-2xl relative transition-all duration-300">
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
            <div className="flex flex-col h-full gap-4 overflow-y-auto custom-scrollbar">
              {/* Header */}
              <div className="flex items-center justify-between border-b border-zinc-800 pb-2 shrink-0">
                <div className="flex flex-col overflow-hidden">
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-[10px] text-emerald-500 font-mono tracking-widest">
                      HALILIT SKU:{" "}
                      {hoveredProduct.sku ||
                        (hoveredProduct.id || "").split("-")[1] ||
                        hoveredProduct.id ||
                        "N/A"}
                    </span>
                  </div>
                  <h1 className="text-2xl font-black text-white uppercase tracking-tight mt-1 truncate w-full">
                    {hoveredProduct.name}
                  </h1>
                  <div className="text-xs text-amber-500 font-bold uppercase tracking-widest">
                    {hoveredProduct.brand ||
                      hoveredProduct.brand_id ||
                      "Unknown Brand"}
                  </div>
                </div>
              </div>

              {/* Description */}
              <div className="text-xs text-zinc-400 font-sans leading-relaxed line-clamp-4 border-l-2 border-zinc-800 pl-3 shrink-0">
                {hoveredProduct.description_short ||
                  stripHtml(
                    hoveredProduct.description_full ||
                      hoveredProduct.description || // v6.0 field
                      "No description available.",
                  )}
              </div>

              {/* Halilit Specs Grid */}
              {hoveredProduct.specs && hoveredProduct.specs.length > 0 && (
                <div>
                  <div className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest mb-2">
                    Halilit Specs
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-[10px] font-mono text-zinc-500">
                    {hoveredProduct.specs.slice(0, 4).map((spec, i) => (
                      <div
                        key={i}
                        className="flex flex-col bg-zinc-900/50 p-2 border border-zinc-800/50 rounded-sm"
                      >
                        <span className="text-amber-500/50 uppercase text-[9px] mb-1">
                          {spec.name}
                        </span>
                        <span className="text-zinc-300 truncate">
                          {spec.value}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Enrichment Data Section */}
              <EnrichmentPanel product={hoveredProduct} />
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

        {/* RIGHT: ACTION & DATA */}
        <Surface
          variant="screen"
          active={!!hoveredProduct}
          className="col-span-3 bg-zinc-950 flex flex-col justify-between items-center p-6 relative overflow-y-auto custom-scrollbar"
        >
          {hoveredProduct ? (
            <div className="w-full space-y-4 flex flex-col">
              {/* Price Section */}
              <div className="space-y-2">
                <div className="text-3xl lg:text-4xl font-black text-white tracking-tighter tabular-nums text-shadow-glow">
                  {getPrice(hoveredProduct)}
                </div>
                <div className="text-[10px] text-zinc-500 font-bold tracking-widest uppercase">
                  Price (VAT Included)
                </div>
              </div>

              <div className="w-full h-px bg-zinc-800/50" />

              {/* Category & Tier Info */}
              <div className="space-y-2 text-xs">
                <div className="flex items-start gap-2">
                  <Tag className="w-3 h-3 text-blue-400 mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <div className="text-zinc-500 uppercase text-[9px] tracking-widest mb-1">
                      Category
                    </div>
                    <div className="text-zinc-200 font-semibold truncate">
                      {hoveredProduct.category || "Other"}
                    </div>
                  </div>
                </div>

                {hoveredProduct.tier && (
                  <div className="flex items-start gap-2">
                    <Zap className="w-3 h-3 text-amber-400 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <div className="text-zinc-500 uppercase text-[9px] tracking-widest mb-1">
                        Tier
                      </div>
                      <div className="text-zinc-200 font-semibold capitalize">
                        {hoveredProduct.tier}
                      </div>
                    </div>
                  </div>
                )}

                {hoveredProduct.is_bestseller && (
                  <div className="flex items-start gap-2">
                    <Star className="w-3 h-3 text-yellow-400 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <div className="text-zinc-500 uppercase text-[9px] tracking-widest">
                        Bestseller
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex-1" />

              {/* CTA Button */}
              <button
                onClick={() =>
                  hoveredProduct.id && openProductPage(hoveredProduct.id)
                }
                className="w-full bg-amber-500 hover:bg-amber-400 text-black font-extrabold py-3 uppercase text-sm tracking-widest transition-all hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2 clip-corner shadow-amber-900/20 shadow-xl"
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
        {isLoading ? (
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
              {brandMatrix.brands.map(
                ({ brand, products, rgbColor, brandPrimary }) => (
                  <BrandTrack
                    key={brand}
                    brand={brand}
                    products={products}
                    rgbColor={rgbColor}
                    brandPrimary={brandPrimary}
                    minPrice={brandMatrix.minPrice}
                    maxPrice={brandMatrix.maxPrice}
                    onHoverProduct={handleHoverProduct}
                    onClickProduct={handleClickProduct}
                  />
                ),
              )}
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
