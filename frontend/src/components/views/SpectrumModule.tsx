import React from "react";
import {
  Activity,
  ArrowLeft,
  Maximize2,
  ScanLine,
  Search,
  Sparkles,
  Star,
  CheckCircle,
  AlertCircle,
  Package,
  Tag,
  Zap,
} from "lucide-react";
import { useMemo, useState, useCallback, useEffect } from "react";
import { useNavigationStore } from "../../store/navigationStore";
import { getBrandLogoUrl } from "../../lib/brandLogoHelper";
import type { ConductorProduct } from "../../hooks/useConductorCatalog";
import {
  useConductorCatalog,
  useProductsBySpectrum,
  useProductVariants,
  useProductRelationships,
} from "../../hooks/useConductorCatalog";
import { Control } from "../ui/Control";
import { Surface } from "../ui/Surface";
import { getBrandTheme } from "../../styles/brandThemes";
import { generateSmartTags } from "../../lib/smartTags";

// --- RELEVANCE ENGINE ---
// Calculates a 0-100 score for Y-Axis positioning
const calculateRelevance = (p: ConductorProduct): number => {
  let score = 50; // Base score

  // 1. Data Quality Bonuses
  if (p.image_url) score += 20;
  if (p.price > 0) score += 10;
  if (p.rating > 0) score += 10;

  // 2. "Flagship" detection
  if (p.price > 2000 && p.price < 15000) score += 10;

  // 3. Penalty for missing images
  if (!p.image_url) score -= 30;

  // 4. Deterministic "Random" spice based on ID
  const idSpice =
    (p.id || "").split("").reduce((acc, char) => acc + char.charCodeAt(0), 0) %
    20;

  return Math.min(100, Math.max(0, score + idSpice));
};

// --- HEALTH CHECK ENGINE ---
const isProductHealthy = (p: ConductorProduct): boolean => {
  // Must have a name
  if (!p.name || p.name.trim().length === 0) return false;
  // Must have a price (0 = "Price on request" → still show it)
  // Only hide truly broken entries
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
          if (import.meta.env.DEV) {
            console.warn(
              `[BrandLogo] Failed to load logo for ${brand}: ${target.src}`,
            );
          }

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
// Shows three data pillars: Halilit (commercial) | Official (brand) | Contextual (community)
const DataSourcesBadge = ({
  sources = [],
  brand,
  dataTrust,
}: {
  sources?: string[];
  brand: string;
  dataTrust?: ConductorProduct["data_trust"];
}) => {
  const hasHalilit = sources.includes("halilit");
  const hasOfficial = sources.includes("official");
  const hasContextual = sources.includes("contextual");

  return (
    <div className="flex gap-3 items-center mt-1">
      {/* Halilit Source (Golden List — commercial data) */}
      <div
        className={`flex flex-col items-center gap-1 transition-opacity ${hasHalilit ? "opacity-100" : "opacity-30"}`}
        title="Commercial Source: Halilit.com (Prices, SKU, Availability)"
      >
        <div className="h-7 w-16 bg-blue-600 rounded flex items-center justify-center shadow-lg shadow-blue-900/20 overflow-hidden">
          <img
            src="/assets/logos/halilit_logo.svg"
            alt="Halilit"
            className="h-5 w-auto"
            onError={(e) => {
              e.currentTarget.style.display = "none";
              e.currentTarget.parentElement!.innerHTML =
                '<span class="text-white font-black italic text-[10px] tracking-tight">Halilit</span>';
            }}
          />
        </div>
        <span className="text-[8px] font-bold text-blue-400 uppercase tracking-widest">
          Prices
        </span>
      </div>

      <div className="h-5 w-px bg-zinc-800" />

      {/* Official Source (Brand — specs, descriptions, images) */}
      <div
        className={`flex flex-col items-center gap-1 transition-opacity ${hasOfficial ? "opacity-100" : "opacity-30"}`}
        title={`Official Source: ${brand} (Specs, Description, Images)`}
      >
        <div className="h-7 w-auto max-w-[60px] flex items-center justify-center">
          <BrandLogo brand={brand} className="h-7 w-auto max-w-[60px]" />
        </div>
        <span className="text-[8px] font-bold text-emerald-400 uppercase tracking-widest">
          Official
        </span>
      </div>

      <div className="h-5 w-px bg-zinc-800" />

      {/* Contextual Source (Community — reviews, insights) */}
      <div
        className={`flex flex-col items-center gap-1 transition-opacity ${hasContextual ? "opacity-100" : "opacity-30"}`}
        title="Contextual Source: Reviews, Community Insights"
      >
        <div className="h-7 w-7 bg-amber-600/80 rounded flex items-center justify-center shadow-lg shadow-amber-900/20">
          <Sparkles className="w-3.5 h-3.5 text-amber-100" />
        </div>
        <span className="text-[8px] font-bold text-amber-400 uppercase tracking-widest">
          Context
        </span>
      </div>
    </div>
  );
};

// --- ENRICHMENT INFO PANEL ---
const EnrichmentPanel = React.memo(
  ({ product }: { product: ConductorProduct }) => {
    return (
      <div className="space-y-3 text-[11px]">
        {/* Official Specs Section */}
        {product.specs && Object.keys(product.specs).length > 0 && (
          <div className="border-l-2 border-emerald-600/50 bg-emerald-950/20 p-2.5 rounded-sm">
            <div className="flex items-center gap-2 mb-1.5">
              <CheckCircle className="w-3 h-3 text-emerald-500" />
              <span className="font-bold text-emerald-400 uppercase tracking-widest text-[9px]">
                Official Specs
              </span>
              <BrandLogo
                brand={product.brand}
                className="h-3.5 w-auto ml-auto opacity-60"
              />
            </div>
            <div className="space-y-0.5 text-zinc-300">
              {Object.entries(product.specs)
                .filter(
                  ([key]) =>
                    key !== "note" && key !== "extracted_name" && key !== "sku",
                )
                .slice(0, 4)
                .map(([key, value]) => (
                  <div key={key} className="flex gap-1 break-words">
                    <span className="text-emerald-600 mt-0.5 text-[8px]">
                      ◆
                    </span>
                    <span className="text-emerald-500/70 capitalize text-[10px]">
                      {key.replace(/_/g, " ")}:
                    </span>
                    <span className="text-zinc-200 text-[10px]">
                      {String(value)}
                    </span>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Contextual Data Section — Reviews & Community */}
        {(product.rating > 0 ||
          (product.audiences && product.audiences.length > 0)) && (
          <div className="border-l-2 border-amber-600/50 bg-amber-950/20 p-2.5 rounded-sm">
            <div className="flex items-center gap-2 mb-1.5">
              <Sparkles className="w-3 h-3 text-amber-500" />
              <span className="font-bold text-amber-400 uppercase tracking-widest text-[9px]">
                Community & Context
              </span>
            </div>
            <div className="space-y-1.5 text-zinc-300">
              {/* Rating */}
              {product.rating > 0 && (
                <div className="flex items-center gap-2">
                  <div className="flex gap-0.5">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-2.5 h-2.5 ${
                          i < Math.floor(product.rating)
                            ? "fill-amber-400 text-amber-400"
                            : "text-zinc-700"
                        }`}
                      />
                    ))}
                  </div>
                  <span className="font-bold text-amber-400 text-[10px]">
                    {product.rating.toFixed(1)}
                  </span>
                  {product.review_count > 0 && (
                    <span className="text-zinc-600 text-[10px]">
                      ({product.review_count})
                    </span>
                  )}
                </div>
              )}
              {/* Pros */}
              {product.pros && product.pros.length > 0 && (
                <div className="text-[10px] text-zinc-400 leading-snug">
                  <span className="text-emerald-500">▸</span>{" "}
                  {product.pros.slice(0, 2).join(" • ")}
                </div>
              )}
              {/* Audiences */}
              {product.audiences && product.audiences.length > 0 && (
                <div className="text-[10px]">
                  <span className="text-amber-500/70 text-[9px] font-bold">
                    For:{" "}
                  </span>
                  <span className="text-zinc-400">
                    {product.audiences.slice(0, 2).join(" · ")}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Data Provenance — Three Pillars */}
        <div className="border-l-2 border-zinc-700/50 bg-zinc-900/30 p-2.5 rounded-sm">
          <div className="flex items-center gap-2 mb-1.5">
            <Package className="w-3 h-3 text-zinc-500" />
            <span className="font-bold text-zinc-400 uppercase tracking-widest text-[9px]">
              Data Sources
            </span>
            {/* Quality Score Badge */}
            <span
              className={`ml-auto text-[9px] font-black px-1.5 py-0.5 rounded ${
                (product.quality_score || 0) >= 90
                  ? "bg-emerald-500/20 text-emerald-400"
                  : (product.quality_score || 0) >= 70
                    ? "bg-green-500/20 text-green-400"
                    : (product.quality_score || 0) >= 40
                      ? "bg-amber-500/20 text-amber-400"
                      : "bg-red-500/20 text-red-400"
              }`}
            >
              {product.quality_score || 0}%
            </span>
          </div>
          <DataSourcesBadge
            sources={product.sources || ["halilit"]}
            brand={product.brand || "Unknown"}
            dataTrust={product.data_trust}
          />
        </div>
      </div>
    );
  },
);

EnrichmentPanel.displayName = "EnrichmentPanel";

// --- HOVER RIGHT PANEL (Price, Category, Variants, Accessories) ---
const HoverRightPanel = React.memo(
  ({
    product,
    openProductPage,
  }: {
    product: ConductorProduct;
    openProductPage: (id: string) => void;
  }) => {
    const { variants } = useProductVariants(product.id);
    const { accessories } = useProductRelationships(product.id);

    return (
      <div className="w-full space-y-3 flex flex-col">
        {/* Price Section */}
        <div className="space-y-1">
          <div className="text-3xl lg:text-4xl font-black text-white tracking-tighter tabular-nums text-shadow-glow">
            {product.price > 0
              ? `₪${product.price.toLocaleString("he-IL")}`
              : "Price on request"}
          </div>
          <div className="text-[10px] text-zinc-500 font-bold tracking-widest uppercase">
            Price (VAT Included)
          </div>
        </div>

        <div className="w-full h-px bg-zinc-800/50" />

        {/* Category & Tier */}
        <div className="space-y-2 text-xs">
          <div className="flex items-start gap-2">
            <Tag className="w-3 h-3 text-blue-400 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <div className="text-zinc-500 uppercase text-[9px] tracking-widest mb-0.5">
                Category
              </div>
              <div className="text-zinc-200 font-semibold truncate">
                {product.spectrum_id?.replace(/-/g, " ") ||
                  product.category ||
                  "Other"}
              </div>
            </div>
          </div>
          {product.tier && (
            <div className="flex items-start gap-2">
              <Zap className="w-3 h-3 text-amber-400 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <div className="text-zinc-500 uppercase text-[9px] tracking-widest mb-0.5">
                  Tier
                </div>
                <div className="text-zinc-200 font-semibold capitalize">
                  {product.tier}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Variants — if this product belongs to a family */}
        {variants.length > 0 && (
          <div className="space-y-1.5">
            <div className="w-full h-px bg-zinc-800/50" />
            <div className="text-[9px] font-bold text-blue-400 uppercase tracking-widest flex items-center gap-1">
              <Sparkles className="w-2.5 h-2.5" />
              Also in this Series ({variants.length + 1})
            </div>
            <div className="flex gap-1.5 overflow-x-auto pb-1">
              {variants.slice(0, 4).map((v) => (
                <button
                  key={v.id}
                  onClick={() => openProductPage(v.id)}
                  className="flex-shrink-0 w-10 h-10 rounded border border-zinc-700 bg-zinc-900 overflow-hidden hover:border-blue-500 transition-colors group/var"
                  title={v.variant_key || v.name}
                >
                  {v.image_url ? (
                    <img
                      src={v.image_url}
                      className="w-full h-full object-contain bg-white"
                      alt={v.name}
                    />
                  ) : (
                    <span className="text-[6px] text-zinc-500 flex items-center justify-center w-full h-full">
                      {v.variant_key || "?"}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Accessories */}
        {accessories.length > 0 && (
          <div className="space-y-1.5">
            <div className="w-full h-px bg-zinc-800/50" />
            <div className="text-[9px] font-bold text-emerald-400 uppercase tracking-widest flex items-center gap-1">
              <Package className="w-2.5 h-2.5" />
              Accessories ({accessories.length})
            </div>
            <div className="flex gap-1.5 overflow-x-auto pb-1">
              {accessories.slice(0, 3).map((a) => (
                <button
                  key={a.id}
                  onClick={() => openProductPage(a.id)}
                  className="flex-shrink-0 w-10 h-10 rounded border border-zinc-700 bg-zinc-900 overflow-hidden hover:border-emerald-500 transition-colors"
                  title={a.name}
                >
                  {a.image_url ? (
                    <img
                      src={a.image_url}
                      className="w-full h-full object-contain bg-white"
                      alt={a.name}
                    />
                  ) : (
                    <span className="text-[6px] text-zinc-500 flex items-center justify-center w-full h-full">
                      ACC
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="flex-1" />

        {/* CTA Button */}
        <button
          onClick={() => product.id && openProductPage(product.id)}
          className="w-full bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-400 hover:to-amber-300 text-black font-extrabold py-3 uppercase text-sm tracking-widest transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2 rounded-lg shadow-lg shadow-amber-900/30"
        >
          <Maximize2 className="w-4 h-4" />
          <span>View Details</span>
        </button>
      </div>
    );
  },
);

HoverRightPanel.displayName = "HoverRightPanel";

// --- BRAND SWIM LANE (memoized to avoid re-rendering all tracks on hover) ---
interface BrandTrackProps {
  brand: string;
  products: ConductorProduct[];
  rgbColor: string;
  brandPrimary: string;
  onHoverProduct: (product: ConductorProduct | null) => void;
  onClickProduct: (id: string) => void;
}

const BrandTrack = React.memo(
  ({
    brand,
    products,
    rgbColor,
    brandPrimary,
    onHoverProduct,
    onClickProduct,
  }: BrandTrackProps) => {
    // Sort products by price (ascending) for consistent display
    const sorted = useMemo(
      () => [...products].sort((a, b) => a.price - b.price),
      [products],
    );

    return (
      <div
        className="flex border-b transition-colors duration-200 group/row hover:bg-white/5"
        style={{
          borderColor: `rgba(${rgbColor}, 0.15)`,
          backgroundColor: `rgba(${rgbColor}, 0.03)`,
        }}
      >
        {/* Brand Header */}
        <div
          className="w-28 flex-shrink-0 flex items-center justify-center border-r"
          style={{
            borderColor: `rgba(${rgbColor}, 0.25)`,
            backgroundColor: `rgba(${rgbColor}, 0.06)`,
          }}
        >
          <div className="flex flex-col gap-0.5 items-center justify-center w-full py-2 px-2 relative">
            <BrandLogo
              brand={brand}
              className="max-h-10 max-w-[88px] w-auto object-contain opacity-90"
            />
            <span
              className="text-[9px] font-bold uppercase tracking-widest bg-black/40 px-1.5 py-0.5 rounded backdrop-blur-sm"
              style={{ color: brandPrimary }}
            >
              {products.length}
            </span>
          </div>
        </div>

        {/* Product Grid — horizontal flow, scrollable */}
        <div className="flex-1 overflow-x-auto py-1.5 px-2 custom-scrollbar">
          <div
            className="flex flex-wrap gap-1 content-start"
            style={{ minWidth: "fit-content" }}
          >
            {sorted.map((product) => {
              // Family badge: count siblings in this track
              const familySiblings = product.family_id
                ? products.filter((p) => p.family_id === product.family_id)
                    .length
                : 0;
              const isFirstInFamily = product.family_id
                ? sorted.findIndex((p) => p.family_id === product.family_id) ===
                  sorted.indexOf(product)
                : false;

              return (
                <div
                  key={product.id}
                  className="group/item relative flex-shrink-0"
                >
                  <div
                    className="w-[52px] h-[52px] rounded shadow-md bg-zinc-900 cursor-pointer hover:scale-110 hover:z-50 transition-all duration-150 overflow-hidden relative"
                    style={{
                      borderWidth: "1.5px",
                      borderColor: brandPrimary,
                      boxShadow:
                        "0 0 0 1px rgba(0,0,0,0.4), 0 2px 4px rgba(0,0,0,0.3)",
                    }}
                    onClick={() => onClickProduct(product.id)}
                    onMouseEnter={() => onHoverProduct(product)}
                  >
                    {product.image_url ? (
                      <img
                        src={product.image_url}
                        className="w-full h-full object-contain bg-white"
                        loading="lazy"
                        alt={product.name}
                      />
                    ) : (
                      <div className="w-full h-full bg-gradient-to-br from-zinc-800 to-zinc-900 flex flex-col items-center justify-center gap-0.5 p-0.5">
                        <span className="text-[6px] font-semibold text-zinc-500 text-center leading-[1.1] line-clamp-2">
                          {product.name.split(" ").slice(0, 3).join(" ")}
                        </span>
                      </div>
                    )}
                    {/* Hover glow */}
                    <div
                      className="absolute inset-0 rounded pointer-events-none opacity-0 group-hover/item:opacity-100 transition-opacity duration-150"
                      style={{
                        boxShadow: `0 0 10px ${brandPrimary}80, inset 0 0 6px ${brandPrimary}40`,
                      }}
                    />
                    {/* Family badge */}
                    {isFirstInFamily && familySiblings > 1 && (
                      <div className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-blue-500 text-white text-[7px] font-black flex items-center justify-center z-10 shadow-md">
                        {familySiblings}
                      </div>
                    )}
                  </div>
                  {/* Price label on hover */}
                  <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 hidden group-hover/item:block bg-black/90 text-[7px] text-zinc-300 px-1 py-0.5 rounded whitespace-nowrap backdrop-blur-sm z-50 font-mono">
                    {product.price > 0
                      ? `₪${product.price.toLocaleString("he-IL")}`
                      : "POA"}
                  </div>
                </div>
              );
            })}
          </div>
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
  const { activeTribeId, activeSubcategoryId, goToGalaxy, openProductPage } =
    useNavigationStore();

  // --------------------------------------------------------------------------
  // 1. DATA INGESTION - Using pre-indexed Conductor data (v10)
  //    Now filtering by SPECTRUM (subcategory) instead of galaxy
  // --------------------------------------------------------------------------
  const { isLoading, error, galaxies } = useConductorCatalog();

  // Get products for this spectrum via pre-computed index — O(1) lookup
  const { products: fetchedProducts } =
    useProductsBySpectrum(activeSubcategoryId);

  // Resolve the spectrum display label from galaxies metadata
  const spectrumLabel = useMemo(() => {
    if (!activeTribeId || !activeSubcategoryId) return "";
    for (const g of galaxies) {
      if (g.id === activeTribeId) {
        for (const s of g.spectrums) {
          if (s.id === activeSubcategoryId) return s.label;
        }
      }
    }
    // Fallback: humanize the ID
    return activeSubcategoryId.replace(/-/g, " ");
  }, [activeTribeId, activeSubcategoryId, galaxies]);

  const rawProducts = useMemo(() => {
    // Backend normalizer guarantees consistent shape — just add relevance score
    return fetchedProducts.map((p) => ({
      ...p,
      score: calculateRelevance(p),
    }));
  }, [fetchedProducts]);

  // --- HEALTH SEGREGATION LAYER ---
  const { cleanProducts, flaggedCount } = useMemo(() => {
    const valid = rawProducts.filter(isProductHealthy);
    const broken = rawProducts.length - valid.length;

    if (broken > 0 && import.meta.env.DEV) {
      console.warn(
        `[HealthGuard] Flagged ${broken} products as broken/incomplete.`,
      );
    }

    return { cleanProducts: valid, flaggedCount: broken };
  }, [rawProducts]);

  // --------------------------------------------------------------------------
  // 2. THE 1176 ENGINE (Filtering) + SMART TAGS
  // --------------------------------------------------------------------------
  const [activeFilter, setActiveFilter] = useState("ALL");
  const [activeSmartTag, setActiveSmartTag] = useState<string | null>(null);
  const [hoveredProduct, setHoveredProduct] = useState<ConductorProduct | null>(
    null,
  );
  const [imageLoadError, setImageLoadError] = useState(false);

  // Generate smart tags from clean products
  const smartTags = useMemo(() => {
    return generateSmartTags(cleanProducts, activeSubcategoryId || "");
  }, [cleanProducts, activeSubcategoryId]);

  // Reset smart tag and tier filter when subcategory changes
  useEffect(() => {
    setActiveSmartTag(null);
    setActiveFilter("ALL");
    setHoveredProduct(null);
  }, [activeSubcategoryId]);

  const handleHoverProduct = useCallback((product: ConductorProduct | null) => {
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
    // Apply tier filter
    if (activeFilter === "ALL") {
      // no tier filter
    } else if (
      activeFilter === "entry" ||
      activeFilter === "mid" ||
      activeFilter === "pro" ||
      activeFilter === "flagship"
    ) {
      base = base.filter((p) => p.tier === activeFilter);
    }
    // Apply smart tag filter
    if (activeSmartTag) {
      const tag = smartTags.find((t) => t.label === activeSmartTag);
      if (tag) {
        base = base.filter((p) => tag.matchedIds.has(p.id));
      }
    }
    // Sort by Price (X-Axis)
    return base.sort((a, b) => a.price - b.price);
  }, [cleanProducts, activeFilter, activeSmartTag, smartTags]);

  // Available tier filters from the data
  const availableFilters = useMemo(() => {
    const tiers = new Set<string>();
    cleanProducts.forEach((p) => {
      if (p.tier) tiers.add(p.tier);
    });
    return Array.from(tiers);
  }, [cleanProducts]);

  // --- BRAND MATRIX ENGINE ---
  const brandMatrix = useMemo(() => {
    if (filteredProducts.length === 0) return { brands: [] };

    // 1. Group by Brand
    const grouped: Record<string, ConductorProduct[]> = {};
    filteredProducts.forEach((p) => {
      const brand = p.brand || "Other";
      if (!grouped[brand]) grouped[brand] = [];
      grouped[brand].push(p);
    });

    // 2. Sort Brands: most products first, then alphabetically
    const sortedBrands = Object.entries(grouped)
      .sort((a, b) => {
        // Sort by product count descending, then alphabetically
        if (b[1].length !== a[1].length) return b[1].length - a[1].length;
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

    return { brands: sortedBrands };
  }, [filteredProducts]);

  // Handle errors
  if (error) {
    return (
      <div className="flex h-full w-full items-center justify-center flex-col gap-4 p-8">
        <div className="max-w-md w-full border border-red-900/40 bg-red-950/10 rounded-xl p-8 text-center backdrop-blur-sm">
          <div className="w-14 h-14 mx-auto mb-4 rounded-full bg-red-500/10 flex items-center justify-center">
            <svg
              className="w-7 h-7 text-red-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>
          <h3 className="text-red-400 font-bold text-lg mb-2">
            Failed to load catalog
          </h3>
          <p className="text-sm text-red-300/70 mb-6">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2.5 bg-red-900/30 hover:bg-red-900/50 text-red-200 rounded-lg text-sm font-medium transition-all duration-200 border border-red-800/30 hover:border-red-700/50"
          >
            Reload Page
          </button>
        </div>
      </div>
    );
  }

  // --------------------------------------------------------------------------
  // 3. THE RENDER
  // --------------------------------------------------------------------------

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
            {spectrumLabel ||
              activeSubcategoryId?.replace(/-/g, " ") ||
              "SPECTRUM"}
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
              {hoveredProduct.image_url && !imageLoadError ? (
                <img
                  src={hoveredProduct.image_url}
                  className="max-w-full max-h-full object-contain drop-shadow-2xl transition-all duration-500 will-change-transform animate-scale-in"
                  alt="Preview"
                  onError={() => setImageLoadError(true)}
                />
              ) : (
                <div className="flex flex-col items-center justify-center gap-3 text-zinc-600 text-center p-4 w-full h-full">
                  {hoveredProduct.brand_logo ? (
                    <img
                      src={hoveredProduct.brand_logo}
                      alt={hoveredProduct.brand}
                      className="max-w-[60%] max-h-[40%] object-contain opacity-20"
                      onError={(e) => {
                        e.currentTarget.style.display = "none";
                      }}
                    />
                  ) : (
                    <div className="w-16 h-16 rounded-full bg-zinc-800/30 flex items-center justify-center">
                      <ScanLine className="w-7 h-7 opacity-50" />
                    </div>
                  )}
                  <span className="text-[10px] font-mono uppercase tracking-widest text-zinc-700">
                    Image not yet scraped
                  </span>
                  {hoveredProduct.halilit_url && (
                    <a
                      href={hoveredProduct.halilit_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[9px] text-blue-500/60 hover:text-blue-400 transition-colors underline underline-offset-2"
                    >
                      View on Halilit.com
                    </a>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center gap-4 text-zinc-800">
              <div className="w-16 h-16 rounded-full bg-zinc-900/50 flex items-center justify-center">
                <Sparkles className="w-8 h-8 opacity-20" />
              </div>
              <div className="text-xs font-mono tracking-[0.15em] uppercase opacity-50">
                Hover a product to preview
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
            <div className="flex flex-col h-full gap-3 overflow-y-auto custom-scrollbar">
              {/* Header — Brand logo + product identity */}
              <div className="flex items-center justify-between border-b border-zinc-800 pb-2 shrink-0">
                <div className="flex flex-col overflow-hidden flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-[10px] text-emerald-500 font-mono tracking-widest">
                      SKU: {hoveredProduct.id || "N/A"}
                    </span>
                  </div>
                  <h1 className="text-xl font-black text-white uppercase tracking-tight mt-1 truncate w-full">
                    {hoveredProduct.name}
                  </h1>
                </div>
                {/* Brand logo beside name */}
                <div className="flex-shrink-0 ml-3">
                  <BrandLogo
                    brand={hoveredProduct.brand}
                    className="h-10 w-auto max-w-[80px] opacity-80"
                  />
                </div>
              </div>

              {/* Description */}
              {(hoveredProduct.description_short ||
                hoveredProduct.description) && (
                <div className="text-[11px] text-zinc-400 font-sans leading-relaxed line-clamp-3 border-l-2 border-zinc-800 pl-3 shrink-0">
                  {hoveredProduct.description_short ||
                    hoveredProduct.description}
                </div>
              )}

              {/* Specs Grid — more compact */}
              {hoveredProduct.specs &&
                Object.keys(hoveredProduct.specs).length > 0 && (
                  <div>
                    <div className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest mb-1.5 flex items-center gap-1.5">
                      <CheckCircle className="w-2.5 h-2.5 text-emerald-500" />
                      Specifications
                    </div>
                    <div className="grid grid-cols-2 gap-1.5 text-[10px] font-mono text-zinc-500">
                      {Object.entries(hoveredProduct.specs)
                        .filter(
                          ([key]) =>
                            key !== "sku" &&
                            key !== "note" &&
                            key !== "extracted_name",
                        )
                        .slice(0, 4)
                        .map(([key, value], i) => (
                          <div
                            key={i}
                            className="flex flex-col bg-zinc-900/50 p-1.5 border border-zinc-800/50 rounded-sm"
                          >
                            <span className="text-emerald-500/50 uppercase text-[8px] mb-0.5 truncate">
                              {key.replace(/_/g, " ")}
                            </span>
                            <span className="text-zinc-300 truncate">
                              {String(value)}
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
            <HoverRightPanel
              product={hoveredProduct}
              openProductPage={openProductPage}
            />
          ) : null}
        </Surface>
      </div>

      {/* --- BOTTOM: BRAND SWIMLANES ENGINE --- */}
      <div className="flex-1 relative bg-[#050505] overflow-hidden flex flex-col">
        {isLoading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="flex flex-col items-center gap-4">
              <div className="relative w-14 h-14">
                <div className="absolute inset-0 rounded-full border-2 border-zinc-800" />
                <div className="absolute inset-0 rounded-full border-2 border-t-blue-500 animate-spin" />
              </div>
              <div className="flex items-center gap-2 text-zinc-600 font-mono text-xs tracking-widest uppercase">
                <span>Loading Spectrum</span>
              </div>
            </div>
          </div>
        ) : filteredProducts.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center max-w-sm">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-zinc-800/30 flex items-center justify-center">
                <ScanLine className="w-7 h-7 text-zinc-700" />
              </div>
              <h3 className="text-zinc-400 font-semibold mb-2">
                No products found
              </h3>
              <p className="text-zinc-600 text-sm mb-4">
                {activeSmartTag || activeFilter !== "ALL"
                  ? "Try adjusting your filters to see more products."
                  : "This spectrum doesn't have any products yet."}
              </p>
              {(activeSmartTag || activeFilter !== "ALL") && (
                <button
                  onClick={() => {
                    setActiveSmartTag(null);
                    setActiveFilter("ALL");
                  }}
                  className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg text-sm transition-colors"
                >
                  Clear All Filters
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="w-full h-full flex flex-col">
            {/* Header */}
            <div className="h-8 flex border-b border-zinc-800/50 bg-black/40 text-[9px] text-zinc-600 font-mono items-center px-4">
              <div className="w-28 shrink-0 text-center uppercase tracking-widest font-bold text-zinc-500">
                Brand
              </div>
              <div className="flex-1 flex items-center gap-2 pl-2">
                <span className="text-zinc-500">
                  Products sorted by price (low → high)
                </span>
                <span className="ml-auto text-zinc-600">
                  {filteredProducts.length} total
                </span>
              </div>
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
                    onHoverProduct={handleHoverProduct}
                    onClickProduct={handleClickProduct}
                  />
                ),
              )}
            </div>
          </div>
        )}
      </div>

      {/* --- BOTTOM DECK: SMART TAG FILTERS + 1176 TIER CONTROLS --- */}
      <Surface
        variant="panel"
        className="flex flex-col gap-0 z-30 !bg-zinc-900/90 backdrop-blur-md border-t border-zinc-800 shadow-2xl shrink-0"
      >
        {/* Smart Tags Row */}
        {smartTags.length > 0 && (
          <div className="flex items-center gap-1 overflow-x-auto no-scrollbar px-4 py-2 border-b border-zinc-800/50">
            <span className="text-[9px] font-bold text-zinc-600 uppercase tracking-widest mr-2 shrink-0">
              Filter
            </span>
            <button
              className={`px-3 py-1.5 rounded-full text-[11px] font-bold tracking-wide transition-all duration-200 shrink-0 ${
                !activeSmartTag
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-900/30"
                  : "bg-zinc-800/80 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-200"
              }`}
              onClick={() => setActiveSmartTag(null)}
            >
              ALL
            </button>
            {smartTags.map((tag) => (
              <button
                key={tag.id}
                className={`px-3 py-1.5 rounded-full text-[11px] font-bold tracking-wide transition-all duration-200 shrink-0 ${
                  activeSmartTag === tag.label
                    ? "bg-amber-500 text-black shadow-lg shadow-amber-900/30"
                    : "bg-zinc-800/80 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-200"
                }`}
                onClick={() =>
                  setActiveSmartTag(
                    activeSmartTag === tag.label ? null : tag.label,
                  )
                }
                title={`${tag.count} products`}
              >
                {tag.label}
                <span
                  className={`ml-1.5 text-[9px] ${
                    activeSmartTag === tag.label
                      ? "text-black/60"
                      : "text-zinc-600"
                  }`}
                >
                  {tag.count}
                </span>
              </button>
            ))}
          </div>
        )}

        {/* Tier Filter Row */}
        <div className="flex items-center px-4 gap-4 h-12">
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
        </div>
      </Surface>
    </div>
  );
};
