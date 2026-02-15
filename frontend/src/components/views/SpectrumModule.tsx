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
  Zap,
  RotateCcw,
} from "lucide-react";
import { useMemo, useState, useCallback, useEffect, useRef } from "react";
import { useNavigationStore } from "../../store/navigationStore";
import { getBrandLogoUrl } from "../../lib/brandLogoHelper";
import type {
  ConductorProduct,
  FamilyMeta,
} from "../../hooks/useConductorCatalog";
import {
  useConductorCatalog,
  useProductsBySpectrum,
  useSpectrumStar,
} from "../../hooks/useConductorCatalog";
import { Control } from "../ui/Control";
import { Surface } from "../ui/Surface";
import { ProductIntelligenceCard } from "../spectrum/ProductIntelligenceCard";
import { getBrandTheme } from "../../styles/brandThemes";
import { generateSmartTags } from "../../lib/smartTags";

// ===================================================================
// CONSTANTS
// ===================================================================

const ACCESSORY_PATTERNS =
  /\b(bag|gig bag|case|hardcase|hard case|cover|strap|string|strings|pick|picks|plectrum|stand|mount|bracket|clamp|adapter|cable|cord|lead|tuner|capo|pedal|footswitch|power supply|charger|battery|replacement|spare|pad set|head set|mute|dampener|polish|cleaner|wax|oil|lube|cloth|toolkit|wrench|key|allen|screw|bolt|felt|washer|sleeve|bushing|grommet|wing nut|cymbal felt|hi hat clutch|drum key|practice pad)\b/i;

// Tier price boundaries (ILS)
const TIER_BOUNDARIES: Record<
  string,
  { min: number; max: number; color: string; label: string }
> = {
  entry: { min: 0, max: 500, color: "#22c55e", label: "Entry" },
  mid: { min: 500, max: 1500, color: "#3b82f6", label: "Mid" },
  pro: { min: 1500, max: 4000, color: "#a855f7", label: "Pro" },
  flagship: { min: 4000, max: 200000, color: "#f59e0b", label: "Flagship" },
};


// ===================================================================
// TYPES
// ===================================================================

interface DisplayItem {
  type: "product" | "family";
  representative: ConductorProduct;
  variantCount: number;
  familyId: string | null;
  familyProducts: ConductorProduct[];
  sortPrice: number;
  series: string | null;
}

interface SubTrackData {
  key: string;
  label: string;
  items: DisplayItem[];
}

// ===================================================================
// UTILITY FUNCTIONS
// ===================================================================

const isAccessoryProduct = (
  product: ConductorProduct,
  spectrumId: string,
): boolean => {
  const name = product.name || "";
  const nameLower = name.toLowerCase();
  if (
    spectrumId.includes("accessor") ||
    spectrumId.includes("parts") ||
    spectrumId.includes("supplies") ||
    spectrumId.includes("cables") ||
    spectrumId.includes("stands") ||
    spectrumId.includes("bags") ||
    spectrumId.includes("strings")
  ) {
    return false;
  }
  if (ACCESSORY_PATTERNS.test(nameLower)) return true;
  return false;
};

const calculateRelevance = (p: ConductorProduct): number => {
  let score = 50;
  if (p.image_url) score += 20;
  if (p.price > 0) score += 10;
  if (p.rating > 0) score += 10;
  if (p.price > 2000 && p.price < 15000) score += 10;
  if (!p.image_url) score -= 30;
  const idSpice =
    (p.id || "").split("").reduce((acc, char) => acc + char.charCodeAt(0), 0) %
    20;
  return Math.min(100, Math.max(0, score + idSpice));
};

const isProductHealthy = (p: ConductorProduct): boolean => {
  if (!p.name || p.name.trim().length === 0) return false;
  return true;
};

const isRealImage = (url: string | undefined): boolean => {
  if (!url) return false;
  return (
    url.startsWith("http") &&
    !url.includes("placeholder") &&
    !url.includes("brand.com") &&
    !url.includes("example.com") &&
    url.length > 20
  );
};

const stringToHue = (str: string): number => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  return Math.abs(hash) % 360;
};

const hexToRgb = (hex: string): string => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}`
    : "100, 100, 100";
};

/** Get effective price for positioning (uses market estimate as fallback) */
const getEffectivePrice = (p: ConductorProduct): number => {
  if (p.price > 0) return p.price;
  if (p.market_price_estimate > 0) return p.market_price_estimate;
  return 0;
};

/**
 * Focus-zone image preloader — debounced preloading of images for products
 * that enter the focus zone. Two strategies:
 *   1. Browser preload: for products that already have image URLs
 *   2. Batch lookup: for products missing images, check JIT cache via API
 * Context-zone products never trigger any image requests.
 */
const useFocusImagePreloader = (
  products: ConductorProduct[],
  focusRange: [number, number],
) => {
  const preloadedRef = useRef(new Set<string>());
  const lookedUpRef = useRef(new Set<string>());
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (timerRef.current) clearTimeout(timerRef.current);

    // Debounce: wait 400ms after focus range stops changing
    timerRef.current = setTimeout(() => {
      const [fMin, fMax] = focusRange;
      const toPreload: string[] = [];
      const missingImageIds: string[] = [];

      for (const p of products) {
        const price = getEffectivePrice(p);
        const inFocus = (price >= fMin && price <= fMax) || price === 0;
        if (!inFocus) continue;

        if (isRealImage(p.image_url)) {
          // Strategy 1: preload existing images
          if (!preloadedRef.current.has(p.image_url)) {
            toPreload.push(p.image_url);
            preloadedRef.current.add(p.image_url);
          }
        } else if (!lookedUpRef.current.has(p.id)) {
          // Strategy 2: check JIT cache for missing images
          missingImageIds.push(p.id);
          lookedUpRef.current.add(p.id);
        }
      }

      // Preload existing images in batches
      const BATCH_SIZE = 10;
      for (let i = 0; i < Math.min(toPreload.length, 50); i += BATCH_SIZE) {
        const batch = toPreload.slice(i, i + BATCH_SIZE);
        setTimeout(() => {
          for (const url of batch) {
            const img = new Image();
            img.src = url;
          }
        }, (i / BATCH_SIZE) * 200);
      }

      // Batch lookup for missing images (non-blocking, fire and forget)
      if (missingImageIds.length > 0 && missingImageIds.length <= 100) {
        fetch("/api/batch-image-lookup", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ product_ids: missingImageIds.slice(0, 50) }),
        })
          .then((res) => res.json())
          .then((data) => {
            // If images were found in JIT cache, preload them
            const images = data?.images || {};
            for (const url of Object.values(images) as string[]) {
              if (url && !preloadedRef.current.has(url)) {
                const img = new Image();
                img.src = url;
                preloadedRef.current.add(url);
              }
            }
          })
          .catch(() => {
            /* silently fail — this is best-effort enrichment */
          });
      }
    }, 400);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [products, focusRange]);
};

/** Get the tier color for a given price */
const getTierColor = (price: number): string => {
  if (price <= 0) return "#71717a"; // zinc-500 for POA
  if (price < 500) return TIER_BOUNDARIES.entry.color;
  if (price < 1500) return TIER_BOUNDARIES.mid.color;
  if (price < 4000) return TIER_BOUNDARIES.pro.color;
  return TIER_BOUNDARIES.flagship.color;
};

/** Log-space price to 0-1 normalized position */
const priceToNorm = (
  price: number,
  pMin: number,
  pMax: number,
): number => {
  if (pMax <= pMin || price <= 0) return 0;
  const logMin = Math.log(Math.max(pMin, 1));
  const logMax = Math.log(Math.max(pMax, 2));
  const logP = Math.log(Math.max(price, 1));
  return Math.max(0, Math.min(1, (logP - logMin) / (logMax - logMin)));
};

/** Normalized 0-1 position back to price (log-space) */
const normToPrice = (
  t: number,
  pMin: number,
  pMax: number,
): number => {
  const logMin = Math.log(Math.max(pMin, 1));
  const logMax = Math.log(Math.max(pMax, 2));
  return Math.exp(logMin + t * (logMax - logMin));
};

/** Convert a price to a percentage position within the current focus window (log-space) */
const priceToFocusPercent = (
  price: number,
  focusRange: [number, number],
  priceExtent: [number, number],
): number => {
  const [pMin, pMax] = priceExtent;
  const normP = priceToNorm(price, pMin, pMax);
  const normFMin = priceToNorm(focusRange[0], pMin, pMax);
  const normFMax = priceToNorm(focusRange[1], pMin, pMax);
  const focusWidth = normFMax - normFMin;
  if (focusWidth <= 0) return 50;
  return ((normP - normFMin) / focusWidth) * 100;
};

/** Generate price axis tick marks for the current focus window */
const generatePriceTicks = (
  focusRange: [number, number],
  priceExtent: [number, number],
): Array<{ price: number; percent: number; label: string; isMajor: boolean }> => {
  const [fMin, fMax] = focusRange;
  const range = fMax - fMin;

  let majorInterval: number;
  let minorInterval: number;
  if (range > 100000) { majorInterval = 50000; minorInterval = 10000; }
  else if (range > 50000) { majorInterval = 10000; minorInterval = 5000; }
  else if (range > 10000) { majorInterval = 5000; minorInterval = 1000; }
  else if (range > 5000) { majorInterval = 2000; minorInterval = 500; }
  else if (range > 2000) { majorInterval = 1000; minorInterval = 250; }
  else if (range > 500) { majorInterval = 500; minorInterval = 100; }
  else { majorInterval = 100; minorInterval = 50; }

  const ticks: Array<{ price: number; percent: number; label: string; isMajor: boolean }> = [];
  const start = Math.ceil(fMin / minorInterval) * minorInterval;

  for (let price = start; price <= fMax; price += minorInterval) {
    const percent = priceToFocusPercent(price, focusRange, priceExtent);
    if (percent >= 2 && percent <= 98) {
      const isMajor = price % majorInterval === 0;
      ticks.push({
        price,
        percent,
        label: isMajor
          ? price >= 1000
            ? `₪${(price / 1000).toFixed(price % 1000 === 0 ? 0 : 1)}K`
            : `₪${price}`
          : "",
        isMajor,
      });
    }
  }
  return ticks;
};

/** Detect product series/line from name (e.g., "RCF ART 910" → "ART") */
const detectSeries = (product: ConductorProduct): string | null => {
  const name = product.name || "";
  const brand = (product.brand || "").trim();
  let cleaned = name;
  if (brand && cleaned.toLowerCase().startsWith(brand.toLowerCase())) {
    cleaned = cleaned.slice(brand.length).trim();
  }
  // Strip leading Hebrew characters
  cleaned = cleaned.replace(/^[^\u0000-\u007F]+\s*/u, "").trim();
  // Match first series identifier: 2+ uppercase alphanumeric characters
  const match = cleaned.match(/^([A-Z][A-Z0-9\-]{1,12})/);
  if (match && match[1].length >= 2) return match[1];
  return null;
};

/** Extract a base-model key for implicit family grouping (strips color/variant suffixes) */
const COLOR_SUFFIXES =
  /\s*[-–]\s*(Black|White|Red|Blue|Silver|Gold|Gray|Grey|Green|Natural|Sunburst|Vintage|Matte|Satin|Gloss|Chrome|Walnut|Cherry|Ebony|Ivory|Maple|Ash|Mahogany|Pink|Purple|Orange|Yellow|Tobacco|Burst|Sparkle|Metallic|Transparent|Trans|Brown|Cream|Clear|Sand|Light|Dark)\s*$/i;
const VERSION_SUFFIXES =
  /\s*[-–]?\s*(MK\s*II|MK\s*2|MK\s*III|MK\s*3|MK\s*IV|MK\s*4|V2|V3|GEN\s*\d|II|III|IV)\s*$/i;

const detectBaseModel = (product: ConductorProduct): string => {
  let name = product.name || "";
  const brand = (product.brand || "").trim();
  if (brand && name.toLowerCase().startsWith(brand.toLowerCase())) {
    name = name.slice(brand.length).trim();
  }
  // Strip Hebrew prefix
  name = name.replace(/^[^\u0000-\u007F]+\s*/u, "").trim();
  // Strip color and version suffixes
  name = name.replace(COLOR_SUFFIXES, "");
  name = name.replace(VERSION_SUFFIXES, "");
  // Normalize whitespace and case
  name = name.replace(/\s+/g, " ").trim().toLowerCase();
  return `${brand.toLowerCase()} ${name}`.trim();
};

/** Product-line key for visual stacking: brand + first meaningful word of name (e.g. "yamaha pacifica", "squier classic"). */
const productLineKey = (product: ConductorProduct): string => {
  let name = (product.name || "").trim();
  const brand = (product.brand || "").trim().toLowerCase();
  if (brand && name.toLowerCase().startsWith(brand)) {
    name = name.slice(brand.length).trim();
  }
  name = name.replace(/^[^\u0000-\u007F]+\s*/u, "").trim();
  const firstWord = name.split(/\s+/)[0]?.toLowerCase() || "";
  if (!firstWord) return brand || "other";
  return `${brand} ${firstWord}`.trim();
};

/** Group display items into series-based sub-tracks within a brand */
const buildSubTracks = (
  items: DisplayItem[],
): SubTrackData[] => {
  const seriesMap = new Map<string, DisplayItem[]>();
  const noSeries: DisplayItem[] = [];

  for (const item of items) {
    const series =
      item.series || detectSeries(item.representative);
    if (series) {
      const existing = seriesMap.get(series);
      if (existing) existing.push(item);
      else seriesMap.set(series, [item]);
    } else {
      noSeries.push(item);
    }
  }

  // Series with only 1 item merge into the general track
  for (const [series, members] of seriesMap) {
    if (members.length < 2) {
      noSeries.push(...members);
      seriesMap.delete(series);
    }
  }

  const tracks: SubTrackData[] = [];

  // Named series tracks (sorted by minimum price)
  const sortedSeries = [...seriesMap.entries()].sort((a, b) => {
    const aMin = a[1][0]?.sortPrice || 0;
    const bMin = b[1][0]?.sortPrice || 0;
    return aMin - bMin;
  });

  for (const [series, members] of sortedSeries) {
    members.sort((a, b) => a.sortPrice - b.sortPrice);
    tracks.push({ key: series, label: series, items: members });
  }

  // General track for ungrouped items
  if (noSeries.length > 0) {
    noSeries.sort((a, b) => a.sortPrice - b.sortPrice);
    tracks.push({ key: "_general", label: "", items: noSeries });
  }

  return tracks;
};

// ===================================================================
// SMALL COMPONENTS
// ===================================================================

const BrandLogo = React.memo(
  ({ brand, className = "h-8" }: { brand: string; className?: string }) => {
    const [error, setError] = useState(false);
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
          if (target.src.endsWith(".svg")) {
            setError(true);
            return;
          }
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

// ===================================================================
// ENRICHMENT PANEL (unchanged)
// ===================================================================

const EnrichmentPanel = React.memo(
  ({ product }: { product: ConductorProduct }) => {
    return (
      <div className="space-y-3 text-[11px]">
        {product.specs && Object.keys(product.specs).length > 0 && (
          <div
            className={
              product.data_trust?.specs_source === "official"
                ? "border-l-2 border-emerald-600/50 bg-emerald-950/20 p-2.5 rounded-sm"
                : "border-l-2 border-zinc-600/50 bg-zinc-900/20 p-2.5 rounded-sm"
            }
          >
            <div className="flex items-center gap-2 mb-1.5">
              {product.data_trust?.specs_source === "official" ? (
                <CheckCircle className="w-3 h-3 text-emerald-500" />
              ) : (
                <Package className="w-3 h-3 text-zinc-500" />
              )}
              <span
                className={
                  product.data_trust?.specs_source === "official"
                    ? "font-bold text-emerald-400 uppercase tracking-widest text-[9px]"
                    : "font-bold text-zinc-400 uppercase tracking-widest text-[9px]"
                }
              >
                {product.data_trust?.specs_source === "official"
                  ? "Official Specs"
                  : "Specifications"}
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
                    <span
                      className={
                        product.data_trust?.specs_source === "official"
                          ? "text-emerald-600 mt-0.5 text-[8px]"
                          : "text-zinc-500 mt-0.5 text-[8px]"
                      }
                    >
                      ◆
                    </span>
                    <span
                      className={
                        product.data_trust?.specs_source === "official"
                          ? "text-emerald-500/70 capitalize text-[10px]"
                          : "text-zinc-400 capitalize text-[10px]"
                      }
                    >
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
              {product.pros && product.pros.length > 0 && (
                <div className="text-[10px] text-zinc-400 leading-snug">
                  <span className="text-emerald-500">▸</span>{" "}
                  {product.pros.slice(0, 2).join(" • ")}
                </div>
              )}
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

        <div className="border-l-2 border-zinc-700/50 bg-zinc-900/30 p-2.5 rounded-sm">
          <div className="flex items-center gap-2 mb-1.5">
            <Package className="w-3 h-3 text-zinc-500" />
            <span className="font-bold text-zinc-400 uppercase tracking-widest text-[9px]">
              Data Sources
            </span>
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

// ===================================================================
// PRODUCT TILE — LOD-aware (size adapts based on zoom)
// ===================================================================

const ProductTile = React.memo(
  ({
    item,
    brandPrimary,
    tileSize,
    isPinned,
    onHoverProduct,
    onHoverOut,
    onClickProduct,
  }: {
    item: DisplayItem;
    brandPrimary: string;
    tileSize: number;
    isPinned?: boolean;
    onHoverProduct: (
      product: ConductorProduct,
      familyProducts: ConductorProduct[],
    ) => void;
    onHoverOut: () => void;
    onClickProduct: (id: string) => void;
  }) => {
    const product = item.representative;
    const isFamily = item.type === "family";
    const [imageError, setImageError] = React.useState(false);
    const hasImage = isRealImage(product.image_url) && !imageError;
    const placeholderHue = useMemo(
      () => stringToHue(product.id || product.name),
      [product.id, product.name],
    );
    const tierColor = getTierColor(item.sortPrice);

    // LOD: All sizes now show images when available
    // Large (72+) → image + name + price overlay
    // Medium (48) → image + price on hover
    // Small (32) → tiny image thumbnail or tier-colored placeholder
    const showImage = hasImage; // always show image if we have one
    const showName = tileSize >= 64;
    const showPrice = tileSize >= 32;

    return (
      <div className="group/item relative flex-shrink-0">
        <div
          className={`rounded shadow-md cursor-pointer hover:scale-110 hover:z-50 transition-all duration-150 overflow-hidden relative ${
            isPinned ? "ring-2 ring-amber-400 ring-offset-1 ring-offset-black scale-110 z-50" : ""
          }`}
          style={{
            width: tileSize,
            height: tileSize,
            borderWidth: isFamily ? "2px" : tileSize >= 48 ? "1.5px" : "1px",
            borderColor: isPinned ? "#f59e0b" : tileSize >= 32 ? brandPrimary : tierColor,
            boxShadow: isPinned
              ? `0 0 16px rgba(245, 158, 11, 0.4), 0 0 0 1px rgba(0,0,0,0.4)`
              : isFamily
                ? `0 0 8px ${brandPrimary}30, 0 0 0 1px rgba(0,0,0,0.4)`
                : "0 0 0 1px rgba(0,0,0,0.4), 0 1px 3px rgba(0,0,0,0.3)",
            backgroundColor: showImage ? "#ffffff" : undefined,
            background: showImage
              ? "#ffffff"
              : `linear-gradient(135deg, hsl(${placeholderHue}, 25%, 15%) 0%, hsl(${placeholderHue + 30}, 20%, 8%) 100%)`,
          }}
          onClick={(e) => { e.stopPropagation(); onClickProduct(product.id); }}
          onMouseEnter={() => onHoverProduct(product, item.familyProducts)}
          onMouseLeave={onHoverOut}
        >
          {showImage ? (
            <>
              <img
                src={product.image_url}
                className="w-full h-full object-contain"
                style={{ padding: tileSize >= 48 ? 2 : 1 }}
                loading="lazy"
                alt={product.name}
                onError={() => setImageError(true)}
              />
              {tileSize >= 48 && (
                <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent pointer-events-none" />
              )}
            </>
          ) : (
            /* No image: show brand-tinted placeholder with name */
            <div
              className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none"
              style={{
                background: `linear-gradient(135deg, hsl(${placeholderHue}, 25%, 15%) 0%, hsl(${placeholderHue + 30}, 20%, 8%) 100%)`,
              }}
            >
              <span
                className="font-black uppercase tracking-wider opacity-40 text-center leading-tight px-0.5"
                style={{
                  color: brandPrimary,
                  fontSize: tileSize >= 48 ? 7 : 5,
                }}
              >
                {product.name
                  .replace(/^[^\w]*/, "")
                  .split(" ")
                  .slice(0, tileSize >= 48 ? 2 : 1)
                  .join("\n")}
              </span>
              {/* Tier accent bar on all non-image tiles */}
              <div
                className="absolute bottom-0 left-0 right-0"
                style={{
                  height: tileSize >= 48 ? 3 : 2,
                  backgroundColor: tierColor,
                  opacity: 0.7,
                }}
              />
            </div>
          )}

          {/* Name overlay for large tiles */}
          {showName && (
            <div className="absolute inset-0 flex flex-col items-center justify-end p-0.5 pb-1 pointer-events-none">
              <span
                className={`text-[7px] font-semibold text-center leading-[1.1] line-clamp-2 ${
                  hasImage
                    ? "text-white/90 drop-shadow-[0_1px_2px_rgba(0,0,0,0.8)]"
                    : "text-white/70"
                }`}
              >
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
          {isFamily && item.variantCount > 1 && tileSize >= 32 && (
            <div
              className="absolute -top-1 -right-1 min-w-[14px] h-[14px] px-0.5 rounded-full text-white text-[7px] font-black flex items-center justify-center z-10 shadow-lg"
              style={{ backgroundColor: brandPrimary }}
            >
              {item.variantCount}
            </div>
          )}

          {/* No-price indicator */}
          {product.price <= 0 && tileSize >= 48 && (
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-amber-500/40" />
          )}

          {/* Pinned indicator */}
          {isPinned && tileSize >= 32 && (
            <div className="absolute top-0 left-0 right-0 h-[3px] bg-amber-400 rounded-t" />
          )}
        </div>

        {/* Price label on hover */}
        {showPrice && (
          <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 hidden group-hover/item:block bg-black/90 text-[7px] text-zinc-300 px-1 py-0.5 rounded whitespace-nowrap backdrop-blur-sm z-50 font-mono">
            {product.price > 0
              ? `₪${product.price.toLocaleString("he-IL")}`
              : product.market_price_estimate > 0
                ? `~₪${product.market_price_estimate.toLocaleString("he-IL")}`
                : "POA"}
            {isFamily && item.variantCount > 1 && (
              <span className="text-blue-400 ml-1">
                +{item.variantCount - 1}
              </span>
            )}
          </div>
        )}
      </div>
    );
  },
);
ProductTile.displayName = "ProductTile";

// ===================================================================
// STACK TILE — wider tile showing family/variant group as a unit
// ===================================================================

const StackTile = React.memo(
  ({
    item,
    brandPrimary,
    tileSize,
    isPinned,
    onHoverProduct,
    onHoverOut,
    onClickProduct,
  }: {
    item: DisplayItem;
    brandPrimary: string;
    tileSize: number;
    isPinned?: boolean;
    onHoverProduct: (
      product: ConductorProduct,
      familyProducts: ConductorProduct[],
    ) => void;
    onHoverOut: () => void;
    onClickProduct: (id: string) => void;
  }) => {
    const rep = item.representative;
    const members = item.familyProducts;
    const count = members.length;
    const [imageError, setImageError] = React.useState(false);
    const hasImage = isRealImage(rep.image_url) && !imageError;
    const tierColor = getTierColor(item.sortPrice);

    // Variant thumbnails (excluding representative)
    const variants = useMemo(
      () => members.filter((m) => m.id !== rep.id),
      [members, rep.id],
    );
    const thumbSize = Math.max(14, Math.floor(tileSize * 0.35));
    const showThumbs = tileSize >= 36 && variants.length > 0;
    const maxThumbs = tileSize >= 46 ? 4 : 2;
    const visibleThumbs = showThumbs ? variants.slice(0, maxThumbs) : [];
    const thumbCols = Math.min(visibleThumbs.length, tileSize >= 46 ? 2 : 1);

    // Stack width: adapts to tile size
    const stackWidth = showThumbs && thumbCols > 0
      ? tileSize + thumbCols * (thumbSize + 2) + 10
      : tileSize + Math.max(6, Math.floor(tileSize * 0.4));

    // Price range
    const prices = useMemo(
      () => members.map((m) => getEffectivePrice(m)).filter((p) => p > 0),
      [members],
    );
    const minPrice = prices.length > 0 ? Math.min(...prices) : 0;
    const maxPrice = prices.length > 0 ? Math.max(...prices) : 0;

    return (
      <div className="group/stack relative flex-shrink-0">
        <div
          className={`cursor-pointer hover:z-50 transition-all duration-150 overflow-hidden flex ${
            isPinned
              ? tileSize >= 20
                ? "ring-2 ring-amber-400 ring-offset-1 ring-offset-black z-50"
                : "ring-1 ring-amber-400 z-50"
              : ""
          }`}
          style={{
            width: stackWidth,
            height: tileSize,
            borderRadius: tileSize >= 20 ? 8 : 4,
            border: `${tileSize >= 20 ? 2 : 1}px solid ${isPinned ? "#f59e0b" : `${brandPrimary}60`}`,
            backgroundColor: `${brandPrimary}08`,
            boxShadow: isPinned
              ? "0 0 12px rgba(245, 158, 11, 0.3)"
              : tileSize >= 20
                ? `0 0 6px ${brandPrimary}18, 0 0 0 1px rgba(0,0,0,0.3)`
                : `0 0 3px ${brandPrimary}15`,
          }}
          onClick={(e) => {
            e.stopPropagation();
            onClickProduct(rep.id);
          }}
          onMouseEnter={() => onHoverProduct(rep, members)}
          onMouseLeave={onHoverOut}
        >
          {/* Representative image */}
          <div
            className="flex-shrink-0 overflow-hidden"
            style={{
              width: Math.max(tileSize - 4, 8),
              height: Math.max(tileSize - 4, 8),
              background: hasImage
                ? "#fff"
                : `hsl(${stringToHue(rep.id)}, 20%, 12%)`,
            }}
          >
            {hasImage ? (
              <img
                src={rep.image_url}
                className="w-full h-full object-contain"
                style={{ padding: tileSize >= 24 ? 2 : 0 }}
                loading="lazy"
                alt={rep.name}
                onError={() => setImageError(true)}
              />
            ) : (
              tileSize >= 20 ? (
                <div className="w-full h-full flex items-center justify-center">
                  <span
                    className="font-black opacity-40 text-center leading-tight"
                    style={{ color: brandPrimary, fontSize: Math.max(5, tileSize * 0.12) }}
                  >
                    {rep.name
                      .split(" ")
                      .slice(0, 2)
                      .join("\n")}
                  </span>
                </div>
              ) : null
            )}
          </div>

          {/* Variant strip + info */}
          {showThumbs ? (
            <div className="flex-1 flex flex-col justify-between p-0.5 overflow-hidden min-w-0">
              {/* Variant thumbnails */}
              <div className="flex flex-wrap gap-[2px]">
                {visibleThumbs.map((v) => {
                  const vHasImage = isRealImage(v.image_url);
                  return (
                    <div
                      key={v.id}
                      className="rounded-sm overflow-hidden border border-white/10 cursor-pointer hover:border-white/30 transition-colors"
                      style={{
                        width: thumbSize,
                        height: thumbSize,
                        background: vHasImage ? "#fff" : `${brandPrimary}15`,
                      }}
                      onClick={(e) => {
                        e.stopPropagation();
                        onClickProduct(v.id);
                      }}
                      onMouseEnter={() => onHoverProduct(v, members)}
                    >
                      {vHasImage ? (
                        <img
                          src={v.image_url}
                          className="w-full h-full object-contain"
                          loading="lazy"
                          alt={v.variant_key || ""}
                        />
                      ) : (
                        <span
                          className="text-[5px] font-bold flex items-center justify-center w-full h-full opacity-40"
                          style={{ color: brandPrimary }}
                        >
                          {v.variant_key || "?"}
                        </span>
                      )}
                    </div>
                  );
                })}
                {variants.length > maxThumbs && (
                  <div
                    className="rounded-sm flex items-center justify-center"
                    style={{
                      width: thumbSize,
                      height: thumbSize,
                      backgroundColor: `${brandPrimary}15`,
                    }}
                  >
                    <span
                      className="text-[7px] font-bold"
                      style={{ color: brandPrimary }}
                    >
                      +{variants.length - maxThumbs}
                    </span>
                  </div>
                )}
              </div>

              {/* Family label + count */}
              <div className="flex items-center justify-between mt-auto">
                <span
                  className="text-[6px] font-bold uppercase tracking-wider truncate opacity-60"
                  style={{ color: brandPrimary }}
                >
                  {item.series ||
                    rep.name.split(" ").slice(0, 2).join(" ")}
                </span>
                <span
                  className="text-[7px] font-black ml-0.5 flex-shrink-0 px-1 rounded-sm"
                  style={{
                    backgroundColor: `${brandPrimary}25`,
                    color: brandPrimary,
                  }}
                >
                  ×{count}
                </span>
              </div>
            </div>
          ) : (
            /* Compact: count badge — scales with tile size */
            <div className="flex-1 flex items-center justify-center min-w-0">
              <span
                className="font-black leading-none"
                style={{
                  color: brandPrimary,
                  fontSize: Math.max(5, Math.min(8, tileSize * 0.3)),
                }}
              >
                {count}
              </span>
            </div>
          )}
        </div>

        {/* Hover price tooltip */}
        <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 hidden group-hover/stack:block bg-black/90 text-[7px] text-zinc-300 px-1.5 py-0.5 rounded whitespace-nowrap backdrop-blur-sm z-50 font-mono">
          {minPrice > 0 ? (
            maxPrice > minPrice ? (
              <span>
                ₪{minPrice.toLocaleString("he-IL")} – ₪
                {maxPrice.toLocaleString("he-IL")}
              </span>
            ) : (
              <span>₪{minPrice.toLocaleString("he-IL")}</span>
            )
          ) : (
            "POA"
          )}
          <span className="text-blue-400 ml-1">×{count}</span>
        </div>
      </div>
    );
  },
);
StackTile.displayName = "StackTile";

// ===================================================================
// BRAND TRACK — sub-track layout with horizontal scroll support
// ===================================================================

interface BrandTrackProps {
  brand: string;
  products: ConductorProduct[];
  /** When provided (from spectrum star API model_groups), use neuron view: nucleus + inner variations */
  displayItems?: DisplayItem[] | null;
  rgbColor: string;
  brandPrimary: string;
  families: Record<string, FamilyMeta>;
  priceExtent: [number, number];
  focusRange: [number, number]; // for tick generation + tile sizing
  pinnedProductId: string | null;
  onHoverProduct: (
    product: ConductorProduct,
    familyProducts: ConductorProduct[],
  ) => void;
  onHoverOut: () => void;
  onClickProduct: (id: string) => void;
}

const TRACK_PAD = 4;
const TRACK_GAP = 4;
const MAX_LANES = 4;
const BrandTrack = React.memo(
  ({
    brand,
    products,
    displayItems: displayItemsProp,
    rgbColor,
    brandPrimary,
    families,
    priceExtent,
    focusRange,
    pinnedProductId,
    onHoverProduct,
    onHoverOut,
    onClickProduct,
  }: BrandTrackProps) => {
    const trackRef = useRef<HTMLDivElement>(null);
    const [trackWidth, setTrackWidth] = useState(600);

    // Measure track width via ResizeObserver
    useEffect(() => {
      const el = trackRef.current;
      if (!el) return;
      const observer = new ResizeObserver((entries) => {
        for (const entry of entries) {
          setTrackWidth(entry.contentRect.width);
        }
      });
      observer.observe(el);
      setTrackWidth(el.clientWidth);
      return () => observer.disconnect();
    }, []);

    // Use neuron display items (from spectrum star API) when provided; else build from products
    const displayItems = useMemo(() => {
      if (displayItemsProp != null && displayItemsProp.length > 0) {
        return displayItemsProp;
      }
      const items: DisplayItem[] = [];
      const familyGroups = new Map<string, ConductorProduct[]>();
      const standalones: ConductorProduct[] = [];

      // 1. Separate products with explicit family_id
      for (const p of products) {
        if (p.family_id) {
          const existing = familyGroups.get(p.family_id);
          if (existing) existing.push(p);
          else familyGroups.set(p.family_id, [p]);
        } else {
          standalones.push(p);
        }
      }

      // 2. Emit explicit families
      for (const [familyId, members] of familyGroups) {
        const representative =
          members.find((m) => m.variant_is_default) ||
          members.find((m) => isRealImage(m.image_url)) ||
          members[0];
        const prices = members
          .map((m) => getEffectivePrice(m))
          .filter((p) => p > 0);
        const minPrice = prices.length > 0 ? Math.min(...prices) : 0;
        const familyMeta = families[familyId];
        items.push({
          type: members.length > 1 ? "family" : "product",
          representative,
          variantCount: members.length,
          familyId,
          familyProducts: members,
          sortPrice: minPrice,
          series: familyMeta?.series || null,
        });
      }

      // 3. Group standalones by product line (brand + first word of name) so StackTiles appear
      const lineGroups = new Map<string, ConductorProduct[]>();
      for (const p of standalones) {
        const key = productLineKey(p);
        const existing = lineGroups.get(key);
        if (existing) existing.push(p);
        else lineGroups.set(key, [p]);
      }

      for (const [, members] of lineGroups) {
        // Sort by price so representative and ordering are consistent
        members.sort((a, b) => getEffectivePrice(a) - getEffectivePrice(b));
        if (members.length > 1) {
          const representative =
            members.find((m) => isRealImage(m.image_url)) || members[0];
          const prices = members
            .map((m) => getEffectivePrice(m))
            .filter((p) => p > 0);
          const minPrice = prices.length > 0 ? Math.min(...prices) : 0;
          items.push({
            type: "family",
            representative,
            variantCount: members.length,
            familyId: null,
            familyProducts: members,
            sortPrice: minPrice,
            series: detectSeries(representative),
          });
        } else {
          const p = members[0];
          items.push({
            type: "product",
            representative: p,
            variantCount: 1,
            familyId: null,
            familyProducts: [p],
            sortPrice: getEffectivePrice(p),
            series: null,
          });
        }
      }

      items.sort((a, b) => a.sortPrice - b.sortPrice);
      return items;
    }, [products, families, displayItemsProp]);

    // Continuous tile size: 4px micro-dot at full zoom-out → 54px at max zoom
    const tileSize = useMemo(() => {
      const normMin = priceToNorm(focusRange[0], priceExtent[0], priceExtent[1]);
      const normMax = priceToNorm(focusRange[1], priceExtent[0], priceExtent[1]);
      const zoomRatio = Math.max(0.01, normMax - normMin);
      // Continuous curve: grows faster at the micro end for responsive feel
      const t = Math.pow(1 - zoomRatio, 0.7);
      return Math.round(Math.max(4, Math.min(54, 4 + t * 50)));
    }, [focusRange, priceExtent]);

    // Build sub-tracks by series
    const subTracks = useMemo(
      () => buildSubTracks(displayItems),
      [displayItems],
    );

    // Compute item width for lane assignment (StackTile is wider at all sizes)
    const getItemWidthPx = useCallback(
      (item: DisplayItem): number => {
        // At micro-dot sizes, everything is the same width
        if (tileSize < 12) return tileSize;
        if (item.type === "family" && item.variantCount > 1) {
          if (tileSize >= 36) {
            // Full thumb layout
            const thumbSize = Math.max(14, Math.floor(tileSize * 0.35));
            const thumbCols = Math.min(
              item.variantCount - 1,
              tileSize >= 46 ? 2 : 1,
            );
            return tileSize + thumbCols * (thumbSize + 2) + 10;
          }
          // Compact StackTile: image + count badge
          return tileSize + Math.max(6, Math.floor(tileSize * 0.4));
        }
        return tileSize;
      },
      [tileSize],
    );

    // Position items per sub-track with lane assignment (full price range)
    const [pMin, pMax] = priceExtent;
    type PositionedItem = DisplayItem & { xPercent: number; lane: number };

    const renderedSubTracks = useMemo(() => {
      return subTracks.map((st) => {
        const positioned: PositionedItem[] = [];
        for (const item of st.items) {
          const price = item.sortPrice;
          const xPercent =
            price > 0
              ? priceToNorm(price, pMin, pMax) * 100
              : 1; // POA at left edge
          positioned.push({ ...item, xPercent, lane: 0 });
        }

        // Greedy lane assignment
        positioned.sort((a, b) => a.xPercent - b.xPercent);
        const lanes: number[] = [];
        for (const item of positioned) {
          const halfW =
            trackWidth > 0
              ? (getItemWidthPx(item) / 2 / trackWidth) * 100
              : 3;
          const gapPct =
            trackWidth > 0 ? (TRACK_GAP / trackWidth) * 100 : 0.5;

          let assigned = -1;
          for (let i = 0; i < lanes.length; i++) {
            if (item.xPercent - halfW - lanes[i] >= gapPct) {
              assigned = i;
              break;
            }
          }
          if (assigned === -1) {
            if (lanes.length < MAX_LANES) {
              assigned = lanes.length;
              lanes.push(-Infinity);
            } else {
              assigned = MAX_LANES - 1;
            }
          }
          lanes[assigned] = item.xPercent + halfW;
          item.lane = assigned;
        }

        return {
          ...st,
          positioned,
          laneCount: Math.max(1, lanes.length),
        };
      });
    }, [subTracks, pMin, pMax, trackWidth, getItemWidthPx]);

    // Pre-compute sub-track y-offsets and total height
    const { subTrackOffsets, totalHeight } = useMemo(() => {
      const labelsVisible = tileSize >= 16;
      const offsets: number[] = [];
      let h = 0;
      for (const st of renderedSubTracks) {
        offsets.push(h);
        const stHeight =
          st.laneCount * (tileSize + TRACK_GAP) + TRACK_PAD;
        h += stHeight + (labelsVisible && st.label ? 14 : 0);
      }
      return {
        subTrackOffsets: offsets,
        totalHeight: Math.max(h + TRACK_PAD, tileSize < 12 ? 20 : 40),
      };
    }, [renderedSubTracks, tileSize]);

    // Tier bands (positioned in full price range)
    const tierBands = useMemo(
      () =>
        Object.entries(TIER_BOUNDARIES)
          .map(([key, tier]) => {
            const l = priceToNorm(Math.max(tier.min, 1), pMin, pMax) * 100;
            const r = priceToNorm(tier.max, pMin, pMax) * 100;
            if (r < 0 || l > 100) return null;
            const cl = Math.max(0, l);
            const cr = Math.min(100, r);
            if (cr - cl < 0.5) return null;
            return { key, cl, cr, color: tier.color, label: tier.label };
          })
          .filter(Boolean) as Array<{
          key: string;
          cl: number;
          cr: number;
          color: string;
          label: string;
        }>,
      [pMin, pMax],
    );

    // Price ticks (generated for visible range, positioned in full range)
    const ticks = useMemo(() => {
      const raw = generatePriceTicks(focusRange, priceExtent);
      // Re-map tick percent to full-range coordinates
      return raw.map((t) => ({
        ...t,
        percent: priceToNorm(t.price, pMin, pMax) * 100,
      }));
    }, [focusRange, priceExtent, pMin, pMax]);

    // Show sub-track labels only at readable sizes
    const showLabels = tileSize >= 16;

    // ── Always render price-axis layout (micro-dots at zoom-out → tiles at zoom-in) ──
    return (
      <div
        className="flex border-b transition-colors duration-200 group/row"
        style={{
          borderColor: `rgba(${rgbColor}, 0.1)`,
          backgroundColor: `rgba(${rgbColor}, 0.015)`,
        }}
      >
        {/* Brand Header — sticky on horizontal scroll */}
        <div
          className="sticky left-0 z-20 w-28 flex-shrink-0 flex items-center justify-center border-r"
          style={{
            borderColor: `rgba(${rgbColor}, 0.2)`,
            backgroundColor: `rgba(${rgbColor}, 0.04)`,
          }}
        >
          <div className="flex flex-col gap-1 items-center justify-center w-full py-2 px-2">
            <BrandLogo
              brand={brand}
              className="max-h-10 max-w-[88px] w-auto object-contain opacity-90"
            />
            <div className="flex items-baseline gap-1">
              <span
                className="text-[10px] font-black tabular-nums"
                style={{ color: brandPrimary }}
              >
                {products.length}
              </span>
            </div>
          </div>
        </div>

        {/* Price-axis Track with sub-tracks */}
        <div
          ref={trackRef}
          className="flex-1 relative"
          style={{ minHeight: Math.max(totalHeight, 40) }}
        >
          {/* Tier background bands */}
          {tierBands.map((b) => (
            <div
              key={b.key}
              className="absolute top-0 bottom-0 pointer-events-none"
              style={{
                left: `${b.cl}%`,
                width: `${b.cr - b.cl}%`,
                backgroundColor: `${b.color}05`,
                borderRight:
                  b.cr < 98 ? `1px dashed ${b.color}15` : "none",
              }}
            />
          ))}

          {/* Price tick marks */}
          {ticks.map((tick) => (
            <div
              key={tick.price}
              className="absolute top-0 bottom-0 pointer-events-none"
              style={{
                left: `${tick.percent}%`,
                width: 1,
                backgroundColor: tick.isMajor
                  ? "rgba(255,255,255,0.05)"
                  : "rgba(255,255,255,0.02)",
              }}
            >
              {tick.label && (
                <span
                  className="absolute bottom-0.5 left-1 text-[7px] font-mono whitespace-nowrap select-none"
                  style={{
                    color: tick.isMajor
                      ? "rgba(255,255,255,0.18)"
                      : "rgba(255,255,255,0.08)",
                  }}
                >
                  {tick.label}
                </span>
              )}
            </div>
          ))}

          {/* Sub-tracks */}
          {renderedSubTracks.map((st, stIdx) => {
            const stLaneH =
              st.laneCount * (tileSize + TRACK_GAP) + TRACK_PAD;
            const labelH = showLabels && st.label ? 14 : 0;
            const stTop = subTrackOffsets[stIdx] ?? 0;

            return (
              <div
                key={st.key}
                className="absolute left-0 right-0"
                style={{ top: stTop, height: stLaneH + labelH }}
              >
                {/* Sub-track label (hidden at micro-dot sizes) */}
                {showLabels && st.label && (
                  <div
                    className="sticky left-0 z-10 inline-block px-1.5 py-0.5 text-[8px] font-bold uppercase tracking-widest rounded-br-sm"
                    style={{
                      color: `${brandPrimary}90`,
                      backgroundColor: `${brandPrimary}0a`,
                      borderBottom: `1px solid ${brandPrimary}15`,
                      borderRight: `1px solid ${brandPrimary}15`,
                    }}
                  >
                    {st.label}
                    <span className="text-zinc-600 ml-1 font-mono text-[7px]">
                      {st.items.length}
                    </span>
                  </div>
                )}

                {/* Items positioned on price axis */}
                {st.positioned.map((item) => {
                  const isMicro = tileSize < 12;
                  const isPinned =
                    pinnedProductId === item.representative.id;

                  // ── Micro-dot mode (< 12px): starfield glow dots ──
                  if (isMicro) {
                    const dotSize = tileSize;
                    const tierColor = getTierColor(item.sortPrice);
                    const isFamily =
                      item.type === "family" && item.variantCount > 1;
                    // Pseudo-random animation offset — very slow, staggered shimmer
                    const hash =
                      ((item.representative.id.charCodeAt(0) || 0) * 37 +
                        (item.representative.id.charCodeAt(2) || 0) * 13) %
                      100;
                    const starDelay = (hash / 100) * 12; // 0-12s wide stagger
                    const starDur = 7 + (hash % 40) / 5; // 7-15s very slow cycle
                    return (
                      <div
                        key={item.representative.id}
                        className="absolute"
                        style={{
                          left: `${item.xPercent}%`,
                          top:
                            (showLabels && st.label ? labelH : 0) +
                            TRACK_PAD +
                            item.lane * (tileSize + TRACK_GAP),
                          transform: "translateX(-50%)",
                        }}
                      >
                        <div
                          className={`rounded-full cursor-pointer hover:!opacity-80 hover:!brightness-150 transition-opacity duration-300 ${
                            isPinned ? "" : "animate-star"
                          }`}
                          style={{
                            width: isFamily
                              ? dotSize +
                                Math.min(item.variantCount, 4) * 2
                              : dotSize,
                            height: dotSize,
                            backgroundColor: tierColor,
                            opacity: isPinned ? 0.9 : undefined,
                            boxShadow: isPinned
                              ? `0 0 6px ${tierColor}80`
                              : `0 0 ${dotSize * 0.8}px ${tierColor}25`,
                            borderRadius: isFamily
                              ? dotSize / 2
                              : "50%",
                            ["--star-delay" as string]: `${starDelay}s`,
                            ["--star-dur" as string]: `${starDur}s`,
                          }}
                          onClick={(e) => {
                            e.stopPropagation();
                            onClickProduct(item.representative.id);
                          }}
                          onMouseEnter={() =>
                            onHoverProduct(
                              item.representative,
                              item.familyProducts,
                            )
                          }
                          onMouseLeave={onHoverOut}
                        />
                      </div>
                    );
                  }

                  // ── Normal tile / stack tile mode (≥ 12px) ──
                  return (
                    <div
                      key={item.representative.id}
                      className="absolute"
                      style={{
                        left: `${item.xPercent}%`,
                        top:
                          (showLabels && st.label ? labelH : 0) +
                          TRACK_PAD +
                          item.lane * (tileSize + TRACK_GAP),
                        transform: "translateX(-50%)",
                        zIndex: isPinned ? 20 : 1,
                      }}
                    >
                      {item.type === "family" &&
                      item.variantCount > 1 ? (
                        <StackTile
                          item={item}
                          brandPrimary={brandPrimary}
                          tileSize={tileSize}
                          isPinned={isPinned}
                          onHoverProduct={onHoverProduct}
                          onHoverOut={onHoverOut}
                          onClickProduct={onClickProduct}
                        />
                      ) : (
                        <ProductTile
                          item={item}
                          brandPrimary={brandPrimary}
                          tileSize={tileSize}
                          isPinned={isPinned}
                          onHoverProduct={onHoverProduct}
                          onHoverOut={onHoverOut}
                          onClickProduct={onClickProduct}
                        />
                      )}
                    </div>
                  );
                })}
              </div>
            );
          })}
        </div>
      </div>
    );
  },
);
BrandTrack.displayName = "BrandTrack";

// ===================================================================
// MINI SPECTRUM — product dots minimap with draggable focus range
// ===================================================================

const MiniSpectrum = React.memo(
  ({
    focusRange,
    priceExtent,
    products,
    onFocusRangeChange,
    onReset,
    onDragStateChange,
  }: {
    focusRange: [number, number];
    priceExtent: [number, number];
    products: ConductorProduct[];
    onFocusRangeChange: (range: [number, number]) => void;
    onReset: () => void;
    onDragStateChange?: (isDragging: boolean) => void;
  }) => {
    const barRef = useRef<HTMLDivElement>(null);
    const [dragging, setDragging] = useState<
      "left" | "right" | "middle" | null
    >(null);
    const dragStartRef = useRef<{
      x: number;
      rangeNorm: [number, number];
    }>({ x: 0, rangeNorm: [0, 1] });
    // Track recent drag to prevent click-after-drag repositioning
    const justDraggedRef = useRef(false);
    // Refs for current values to avoid stale closures in drag handlers
    const focusRangeRef = useRef(focusRange);
    const priceExtentRef = useRef(priceExtent);
    const onChangeRef = useRef(onFocusRangeChange);
    const onDragStateChangeRef = useRef(onDragStateChange);
    focusRangeRef.current = focusRange;
    priceExtentRef.current = priceExtent;
    onChangeRef.current = onFocusRangeChange;
    onDragStateChangeRef.current = onDragStateChange;

    const [pMin, pMax] = priceExtent;
    const [fMin, fMax] = focusRange;

    // Build product dots: position each product by price (log-space)
    const productDots = useMemo(() => {
      const dots: Array<{
        id: string;
        percent: number;
        color: string;
        hasImage: boolean;
        imageUrl: string;
        tier: string;
        y: number; // vertical offset (0-1) to avoid overlap
      }> = [];

      // Sort by price for consistent y-stacking
      const sorted = [...products]
        .filter((p) => getEffectivePrice(p) > 0)
        .sort((a, b) => getEffectivePrice(a) - getEffectivePrice(b));

      // Use buckets to compute y offset (avoid overlap)
      const MINI_BUCKETS = 120;
      const bucketCounts = new Array(MINI_BUCKETS).fill(0);

      for (const p of sorted) {
        const price = getEffectivePrice(p);
        const norm = priceToNorm(price, pMin, pMax);
        const bucket = Math.min(
          MINI_BUCKETS - 1,
          Math.floor(norm * MINI_BUCKETS),
        );
        const yOffset = bucketCounts[bucket];
        bucketCounts[bucket]++;

        dots.push({
          id: p.id,
          percent: norm * 100,
          color: getTierColor(price),
          hasImage: isRealImage(p.image_url),
          imageUrl: p.image_url || "",
          tier: p.tier || "poa",
          y: yOffset,
        });
      }

      // Normalize y offsets
      const maxStack = Math.max(...bucketCounts, 1);
      for (const dot of dots) {
        dot.y = maxStack > 1 ? dot.y / maxStack : 0.5;
      }

      return dots;
    }, [products, pMin, pMax]);

    const leftPercent = priceToNorm(fMin, pMin, pMax) * 100;
    const rightPercent = priceToNorm(fMax, pMin, pMax) * 100;

    // Tier boundary positions
    const tierMarkers = useMemo(
      () =>
        Object.entries(TIER_BOUNDARIES)
          .filter(
            ([, t]) => t.max < 200000 && t.max > pMin && t.max < pMax,
          )
          .map(([key, t]) => ({
            key,
            percent: priceToNorm(t.max, pMin, pMax) * 100,
            label: t.label,
            color: t.color,
          })),
      [pMin, pMax],
    );

    // Mouse handlers for dragging — uses refs to avoid stale closures
    const handleMouseDown = useCallback(
      (e: React.MouseEvent, handle: "left" | "right" | "middle") => {
        e.preventDefault();
        e.stopPropagation();
        const [curFMin, curFMax] = focusRangeRef.current;
        const [curPMin, curPMax] = priceExtentRef.current;
        setDragging(handle);
        justDraggedRef.current = false;
        onDragStateChangeRef.current?.(true);
        dragStartRef.current = {
          x: e.clientX,
          rangeNorm: [
            priceToNorm(curFMin, curPMin, curPMax),
            priceToNorm(curFMax, curPMin, curPMax),
          ],
        };
      },
      [],
    );

    useEffect(() => {
      if (!dragging) return;

      const handleMouseMove = (e: MouseEvent) => {
        const bar = barRef.current;
        if (!bar) return;
        const rect = bar.getBoundingClientRect();
        const barWidth = rect.width;
        if (barWidth <= 0) return;

        // Read current values from refs — always fresh, no stale closure issues
        const [curFMin, curFMax] = focusRangeRef.current;
        const [curPMin, curPMax] = priceExtentRef.current;

        const currentNorm = Math.max(
          0,
          Math.min(1, (e.clientX - rect.left) / barWidth),
        );

        // Pure cursor-following: no snapping, no rounding, no zones.
        // Only constraint: handles cannot cross each other.
        const eps = 1e-9;
        if (dragging === "left") {
          const rightNorm = priceToNorm(curFMax, curPMin, curPMax);
          const newLeftNorm = Math.min(currentNorm, Math.max(0, rightNorm - eps));
          const newPrice = normToPrice(newLeftNorm, curPMin, curPMax);
          onChangeRef.current([newPrice, curFMax]);
        } else if (dragging === "right") {
          const leftNorm = priceToNorm(curFMin, curPMin, curPMax);
          const newRightNorm = Math.max(currentNorm, Math.min(1, leftNorm + eps));
          const newPrice = normToPrice(newRightNorm, curPMin, curPMax);
          onChangeRef.current([curFMin, newPrice]);
        } else if (dragging === "middle") {
          const dx = e.clientX - dragStartRef.current.x;
          const dNorm = dx / barWidth;
          const [startMinN, startMaxN] = dragStartRef.current.rangeNorm;
          const rangeWidth = startMaxN - startMinN;
          let newMinN = startMinN + dNorm;
          let newMaxN = startMaxN + dNorm;
          if (newMinN < 0) {
            newMinN = 0;
            newMaxN = rangeWidth;
          }
          if (newMaxN > 1) {
            newMaxN = 1;
            newMinN = 1 - rangeWidth;
          }
          onChangeRef.current([
            normToPrice(newMinN, curPMin, curPMax),
            normToPrice(newMaxN, curPMin, curPMax),
          ]);
        }
        justDraggedRef.current = true;
      };

      const handleMouseUp = () => {
        setDragging(null);
        onDragStateChangeRef.current?.(false);
        // Keep justDraggedRef true so the bar click is suppressed
        // Reset it after a tick so subsequent genuine clicks work
        setTimeout(() => { justDraggedRef.current = false; }, 50);
      };

      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
      return () => {
        window.removeEventListener("mousemove", handleMouseMove);
        window.removeEventListener("mouseup", handleMouseUp);
      };
    }, [dragging]); // Only re-register when drag mode changes — values come from refs

    // Click on dimmed region to shift focus there
    // Suppressed immediately after a drag to prevent handle jumping
    const handleBarClick = useCallback(
      (e: React.MouseEvent) => {
        const bar = barRef.current;
        if (!bar || dragging || justDraggedRef.current) return;
        const [curFMin, curFMax] = focusRangeRef.current;
        const [curPMin, curPMax] = priceExtentRef.current;
        const rect = bar.getBoundingClientRect();
        const norm = Math.max(
          0,
          Math.min(1, (e.clientX - rect.left) / rect.width),
        );
        const clickPrice = normToPrice(norm, curPMin, curPMax);
        const halfWidth = (curFMax - curFMin) / 2;
        const newMin = Math.max(curPMin, clickPrice - halfWidth);
        const newMax = Math.min(curPMax, clickPrice + halfWidth);
        onChangeRef.current([newMin, newMax]);
      },
      [dragging],
    );

    // Is the focus range close to the full extent?
    const isFullRange =
      Math.abs(fMin - pMin) < 10 && Math.abs(fMax - pMax) < 10;

    return (
      <div className="flex items-center gap-2 mx-4 my-1.5 select-none">
        {/* Reset / zoom-out button */}
        {!isFullRange && (
          <button
            className="flex-shrink-0 w-7 h-7 flex items-center justify-center rounded-md bg-zinc-800/80 hover:bg-zinc-700 text-zinc-400 hover:text-zinc-200 transition-all border border-zinc-700/50 hover:border-zinc-600"
            onClick={(e) => {
              e.stopPropagation();
              onReset();
            }}
            title="Reset zoom — show all products"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        )}

        <div
          className="relative h-12 flex-1 rounded-lg overflow-hidden bg-zinc-950 border border-zinc-800/60"
          ref={barRef}
          onClick={handleBarClick}
        >
        {/* Product dots — mini spectrum visualization */}
        <div className="absolute inset-0 px-0.5 pointer-events-none">
          {productDots.map((dot) => {
            const inFocus =
              dot.percent >= leftPercent && dot.percent <= rightPercent;
            return (
              <div
                key={dot.id}
                className="absolute rounded-full transition-opacity duration-200"
                style={{
                  left: `${dot.percent}%`,
                  top: `${10 + dot.y * 70}%`,
                  width: dot.hasImage ? 6 : 4,
                  height: dot.hasImage ? 6 : 4,
                  backgroundColor: dot.color,
                  opacity: inFocus ? 0.9 : 0.2,
                  transform: "translate(-50%, -50%)",
                  boxShadow: inFocus
                    ? `0 0 4px ${dot.color}60`
                    : "none",
                }}
              />
            );
          })}
        </div>

        {/* Left curtain */}
        <div
          className="absolute top-0 bottom-0 left-0 bg-black/60 backdrop-blur-[1px] z-[1]"
          style={{ width: `${leftPercent}%` }}
        />

        {/* Right curtain */}
        <div
          className="absolute top-0 bottom-0 right-0 bg-black/60 backdrop-blur-[1px] z-[1]"
          style={{ width: `${100 - rightPercent}%` }}
        />

        {/* Focus window — draggable center */}
        <div
          className={`absolute top-0 bottom-0 z-[2] transition-colors duration-100 ${
            dragging === "middle"
              ? "cursor-grabbing bg-blue-500/10"
              : "cursor-grab hover:bg-blue-500/8"
          }`}
          style={{
            left: `${leftPercent}%`,
            right: `${100 - rightPercent}%`,
            borderLeft: "2px solid rgba(96, 165, 250, 0.5)",
            borderRight: "2px solid rgba(96, 165, 250, 0.5)",
          }}
          onMouseDown={(e) => handleMouseDown(e, "middle")}
        />

        {/* Left handle */}
        <div
          className={`absolute top-0 bottom-0 w-5 -ml-2.5 z-[3] flex items-center justify-center ${
            dragging === "left" ? "cursor-grabbing" : "cursor-ew-resize"
          }`}
          style={{ left: `${leftPercent}%` }}
          onMouseDown={(e) => handleMouseDown(e, "left")}
        >
          <div className="w-1 h-8 bg-blue-400 rounded-full shadow-lg shadow-blue-500/40 hover:bg-blue-300 hover:w-1.5 transition-all" />
        </div>

        {/* Right handle */}
        <div
          className={`absolute top-0 bottom-0 w-5 -ml-2.5 z-[3] flex items-center justify-center ${
            dragging === "right" ? "cursor-grabbing" : "cursor-ew-resize"
          }`}
          style={{ left: `${rightPercent}%` }}
          onMouseDown={(e) => handleMouseDown(e, "right")}
        >
          <div className="w-1 h-8 bg-blue-400 rounded-full shadow-lg shadow-blue-500/40 hover:bg-blue-300 hover:w-1.5 transition-all" />
        </div>

        {/* Tier markers */}
        {tierMarkers.map((m) => (
          <div
            key={m.key}
            className="absolute top-0 bottom-0 w-px z-[4] pointer-events-none"
            style={{ left: `${m.percent}%`, backgroundColor: `${m.color}35` }}
          >
            <span
              className="absolute top-0.5 left-1/2 -translate-x-1/2 text-[7px] font-bold uppercase tracking-wider whitespace-nowrap px-1 py-0.5 bg-black/80 rounded-sm"
              style={{ color: m.color }}
            >
              {m.label}
            </span>
          </div>
        ))}

        {/* Price labels at handles */}
        <div
          className="absolute bottom-0.5 z-[5] text-[7px] text-blue-400/80 font-mono font-bold"
          style={{
            left: `${leftPercent}%`,
            transform: "translateX(-100%)",
            paddingRight: 4,
          }}
        >
          ₪{Math.round(fMin).toLocaleString()}
        </div>
        <div
          className="absolute bottom-0.5 z-[5] text-[7px] text-blue-400/80 font-mono font-bold"
          style={{
            left: `${rightPercent}%`,
            paddingLeft: 4,
          }}
        >
          ₪{Math.round(fMax).toLocaleString()}
        </div>
        </div>
      </div>
    );
  },
);
MiniSpectrum.displayName = "MiniSpectrum";

// ===================================================================
// VISUAL FEED PANEL — shows hovered product + variant images side by side
// ===================================================================

const VisualFeedPanel = React.memo(
  ({
    product,
    familyProducts,
    imageLoadError,
    onImageError,
    onProductClick,
  }: {
    product: ConductorProduct;
    familyProducts: ConductorProduct[];
    imageLoadError: boolean;
    onImageError: () => void;
    onProductClick: (id: string) => void;
  }) => {
    const [hoveredVariantId, setHoveredVariantId] = useState<string | null>(
      null,
    );

    // Get related variant products (excluding self) that have images
    const variantsWithImages = useMemo(() => {
      const seen = new Set<string>([product.id]);
      const result: ConductorProduct[] = [];
      for (const p of familyProducts) {
        if (!seen.has(p.id) && isRealImage(p.image_url)) {
          result.push(p);
          seen.add(p.id);
        }
      }
      return result;
    }, [product.id, familyProducts]);

    const hasVariants = variantsWithImages.length > 0;
    const hoveredVariant = hoveredVariantId
      ? variantsWithImages.find((v) => v.id === hoveredVariantId) || null
      : null;

    const mainHasImage = isRealImage(product.image_url) && !imageLoadError;

    return (
      <div className="w-full h-full flex flex-col gap-1.5">
        {/* Main image area — split into two if a variant is hovered */}
        <div className={`flex-1 flex gap-1.5 min-h-0 ${hasVariants ? "" : ""}`}>
          {/* Primary product image */}
          <div
            className={`relative bg-white/5 rounded-sm flex items-center justify-center overflow-hidden transition-all duration-300 ${
              hoveredVariant ? "flex-1" : "flex-1"
            }`}
          >
            {mainHasImage ? (
              <img
                src={product.image_url}
                className="max-w-full max-h-full object-contain drop-shadow-2xl transition-all duration-400 will-change-transform animate-scale-in p-2"
                alt="Preview"
                onError={onImageError}
              />
            ) : (
              <div className="flex flex-col items-center justify-center gap-2 text-zinc-600 text-center p-3 w-full h-full">
                <BrandLogo
                  brand={product.brand}
                  className="max-h-12 max-w-[60%] w-auto opacity-30"
                />
                <span className="text-[9px] font-mono uppercase tracking-widest text-zinc-700">
                  No image
                </span>
              </div>
            )}
            {/* Tiny product name label */}
            <div className="absolute bottom-1 left-1 right-1 text-center">
              <span className="text-[7px] font-bold text-zinc-500 bg-black/60 px-1.5 py-0.5 rounded-sm truncate inline-block max-w-full">
                {product.variant_key || product.name?.split(" ").slice(-2).join(" ")}
              </span>
            </div>
          </div>

          {/* Variant large preview — appears when a variant thumbnail is hovered */}
          {hoveredVariant && (
            <div
              className="flex-1 relative bg-white/5 rounded-sm flex items-center justify-center overflow-hidden animate-scale-in cursor-pointer"
              onClick={() => onProductClick(hoveredVariant.id)}
            >
              <img
                src={hoveredVariant.image_url}
                className="max-w-full max-h-full object-contain drop-shadow-2xl p-2 transition-all duration-300"
                alt={hoveredVariant.name}
              />
              <div className="absolute bottom-1 left-1 right-1 text-center">
                <span className="text-[7px] font-bold text-blue-400 bg-black/60 px-1.5 py-0.5 rounded-sm truncate inline-block max-w-full">
                  {hoveredVariant.variant_key || hoveredVariant.name?.split(" ").slice(-2).join(" ")}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Variant thumbnail strip at the bottom */}
        {hasVariants && (
          <div className="flex gap-1 overflow-x-auto shrink-0 py-0.5 px-0.5">
            {variantsWithImages.slice(0, 8).map((v) => (
              <button
                key={v.id}
                className={`flex-shrink-0 w-10 h-10 rounded border overflow-hidden transition-all duration-150 ${
                  hoveredVariantId === v.id
                    ? "border-blue-400 ring-1 ring-blue-400/40 scale-105"
                    : "border-zinc-700/60 hover:border-zinc-500"
                }`}
                onMouseEnter={() => setHoveredVariantId(v.id)}
                onMouseLeave={() => setHoveredVariantId(null)}
                onClick={() => onProductClick(v.id)}
                title={v.variant_key || v.name}
              >
                <img
                  src={v.image_url}
                  className="w-full h-full object-contain bg-white p-0.5"
                  alt={v.variant_key || v.name}
                />
              </button>
            ))}
            {variantsWithImages.length > 8 && (
              <div className="flex-shrink-0 w-10 h-10 rounded border border-zinc-800 bg-zinc-900/50 flex items-center justify-center">
                <span className="text-[8px] text-zinc-500 font-bold">
                  +{variantsWithImages.length - 8}
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    );
  },
);
VisualFeedPanel.displayName = "VisualFeedPanel";

// ===================================================================
// MAIN: SPECTRUM MODULE
// ===================================================================

export const SpectrumModule = () => {
  const { activeTribeId, activeSubcategoryId, goToGalaxy, openProductPage } =
    useNavigationStore();

  // --------------------------------------------------------------------------
  // 1. DATA INGESTION
  // --------------------------------------------------------------------------
  const { isLoading, error, galaxies, families } = useConductorCatalog();
  const { products: fetchedProducts } =
    useProductsBySpectrum(activeSubcategoryId);
  // CPG neuron view: SpectrumStarResponse (ModelGroups = nucleus + variations, relationships = synapses)
  const {
    modelGroups: spectrumStarModelGroups,
    relationships: spectrumStarRelationships,
    zoomLevels: spectrumZoomLevels,
    productCount: spectrumStarProductCount,
    isLoading: spectrumStarLoading,
  } = useSpectrumStar(activeSubcategoryId);

  const spectrumLabel = useMemo(() => {
    if (!activeTribeId || !activeSubcategoryId) return "";
    for (const g of galaxies) {
      if (g.id === activeTribeId) {
        for (const s of g.spectrums) {
          if (s.id === activeSubcategoryId) return s.label;
        }
      }
    }
    return activeSubcategoryId.replace(/-/g, " ");
  }, [activeTribeId, activeSubcategoryId, galaxies]);

  const rawProducts = useMemo(() => {
    return fetchedProducts.map((p) => ({
      ...p,
      score: calculateRelevance(p),
    }));
  }, [fetchedProducts]);

  const { cleanProducts, flaggedCount } = useMemo(() => {
    const valid = rawProducts.filter(isProductHealthy);
    const broken = rawProducts.length - valid.length;
    return { cleanProducts: valid, flaggedCount: broken };
  }, [rawProducts]);

  // --------------------------------------------------------------------------
  // 2. FILTERING ENGINE
  // --------------------------------------------------------------------------
  const [activeSmartTag, setActiveSmartTag] = useState<string | null>(null);
  const [hoveredProduct, setHoveredProduct] = useState<ConductorProduct | null>(
    null,
  );
  const [hoveredFamilyProducts, setHoveredFamilyProducts] = useState<
    ConductorProduct[]
  >([]);
  const [imageLoadError, setImageLoadError] = useState(false);
  const [pinnedProductId, setPinnedProductId] = useState<string | null>(null);
  const hoverTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingHoverRef = useRef<{
    product: ConductorProduct;
    familyProducts: ConductorProduct[];
  } | null>(null);

  const smartTags = useMemo(() => {
    return generateSmartTags(cleanProducts, activeSubcategoryId || "");
  }, [cleanProducts, activeSubcategoryId]);

  // --------------------------------------------------------------------------
  // 3. ZOOM LENS STATE + SCROLL SYNC
  // --------------------------------------------------------------------------
  const [focusRange, setFocusRange] = useState<[number, number]>([0, 200000]);
  const tracksRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const isScrollProgrammatic = useRef(false);

  // Compute price extent from all products (log-scale friendly)
  const priceExtent = useMemo((): [number, number] => {
    let min = Infinity;
    let max = -Infinity;
    for (const p of cleanProducts) {
      const price = getEffectivePrice(p);
      if (price > 0) {
        min = Math.min(min, price);
        max = Math.max(max, price);
      }
    }
    if (min === Infinity) return [10, 10000];
    // Small padding
    return [Math.max(1, min * 0.8), max * 1.1];
  }, [cleanProducts]);

  // Reset zoom and filters when spectrum changes
  useEffect(() => {
    setActiveSmartTag(null);
    setFocusRange(priceExtent);
    setHoveredProduct(null);
    setHoveredFamilyProducts([]);
    setPinnedProductId(null);
  }, [activeSubcategoryId]); // eslint-disable-line react-hooks/exhaustive-deps

  // Also reset focus range when priceExtent is first calculated
  const priceExtentRef = useRef(priceExtent);
  useEffect(() => {
    if (
      priceExtent[0] !== priceExtentRef.current[0] ||
      priceExtent[1] !== priceExtentRef.current[1]
    ) {
      priceExtentRef.current = priceExtent;
      setFocusRange(priceExtent);
    }
  }, [priceExtent]);

  // Determine if we're in aggregate (full zoom-out) mode
  const isAggregate = useMemo(() => {
    const focusSpan = focusRange[1] - focusRange[0];
    const totalSpan = priceExtent[1] - priceExtent[0];
    return totalSpan > 0 && focusSpan / totalSpan > 0.85;
  }, [focusRange, priceExtent]);

  // Zoom ratio and canvas width for horizontal scrolling
  const zoomRatio = useMemo(() => {
    const [pMin, pMax] = priceExtent;
    const normFMin = priceToNorm(focusRange[0], pMin, pMax);
    const normFMax = priceToNorm(focusRange[1], pMin, pMax);
    return Math.max(0.01, normFMax - normFMin);
  }, [focusRange, priceExtent]);

  const canvasWidthPercent = useMemo(
    () => Math.min(100 / zoomRatio, 2000), // cap at 2000% to prevent perf issues
    [zoomRatio],
  );

  // Sync focus range → scroll position (one-way: minimap drives scroll)
  useEffect(() => {
    const el = scrollContainerRef.current;
    if (!el) return;
    const [pMin, pMax] = priceExtent;
    const normFMin = priceToNorm(focusRange[0], pMin, pMax);
    const innerWidth = el.scrollWidth;
    const scrollTarget = normFMin * innerWidth;
    isScrollProgrammatic.current = true;
    el.scrollLeft = scrollTarget;
    // Reset flag after TWO frames to ensure no race condition with scroll events
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        isScrollProgrammatic.current = false;
      });
    });
  }, [focusRange, priceExtent, canvasWidthPercent]);

  // Sync scroll position → focus range (suppressed during minimap drag)
  const handleScrollSync = useCallback(
    (e: React.UIEvent<HTMLDivElement>) => {
      // Skip if this scroll was caused by our programmatic update
      if (isScrollProgrammatic.current) return;
      // Skip if user is actively dragging the minimap handles
      if (isDraggingMinimapRef.current) return;
      const el = e.currentTarget;
      const scrollWidth = el.scrollWidth;
      if (scrollWidth <= 0) return;
      const normFMin = el.scrollLeft / scrollWidth;
      const normFMax = (el.scrollLeft + el.clientWidth) / scrollWidth;
      const [pMin, pMax] = priceExtent;
      const newFMin = normToPrice(
        Math.max(0, Math.min(1, normFMin)),
        pMin,
        pMax,
      );
      const newFMax = normToPrice(
        Math.max(0, Math.min(1, normFMax)),
        pMin,
        pMax,
      );
      if (
        Math.abs(newFMin - focusRange[0]) > 1 ||
        Math.abs(newFMax - focusRange[1]) > 1
      ) {
        setFocusRange([newFMin, newFMax]);
      }
    },
    [priceExtent, focusRange],
  );

  // Preload images for products entering the focus zone
  useFocusImagePreloader(cleanProducts, focusRange);

  // --------------------------------------------------------------------------
  // 4. FILTERED + SORTED PRODUCTS
  // --------------------------------------------------------------------------
  const filteredProducts = useMemo(() => {
    let base = cleanProducts;
    const spectrumId = activeSubcategoryId || "";
    base = base.filter((p) => !isAccessoryProduct(p, spectrumId));
    // Smart tag filter only (tiers now control zoom, not filtering)
    if (activeSmartTag) {
      const tag = smartTags.find((t) => t.label === activeSmartTag);
      if (tag) {
        base = base.filter((p) => tag.matchedIds.has(p.id));
      }
    }
    return base.sort((a, b) => getEffectivePrice(a) - getEffectivePrice(b));
  }, [cleanProducts, activeSmartTag, smartTags, activeSubcategoryId]);

  // Neuron view: when spectrum star API returns model_groups, build display items
  // by brand so the track shows ModelGroups (nucleus) + variations (inner) instead of flat list.
  const neuronDisplayItemsByBrand = useMemo((): Record<string, DisplayItem[]> | null => {
    if (!activeSubcategoryId || spectrumStarModelGroups.length === 0 || cleanProducts.length === 0) {
      return null;
    }
    const spectrumId = activeSubcategoryId;
    const productPool = cleanProducts.filter((p) => !isAccessoryProduct(p, spectrumId));
    const productMap = new Map(productPool.map((p) => [p.id, p]));

    const idsInGroups = new Set(
      spectrumStarModelGroups.flatMap((g) => g.variations.map((v) => v.id)),
    );
    const byBrand = new Map<string, DisplayItem[]>();

    for (const group of spectrumStarModelGroups) {
      const familyProducts: ConductorProduct[] = group.variations
                        .map((v) => productMap.get(v.id))
                        .filter((p): p is ConductorProduct => p != null);
      if (familyProducts.length === 0) continue;
      const representative =
                        familyProducts.find((m) => isRealImage(m.image_url)) ?? familyProducts[0];
      const prices = familyProducts
                        .map((m) => getEffectivePrice(m))
                        .filter((p) => p > 0);
      const sortPrice = prices.length > 0 ? Math.min(...prices) : 0;
      const brand = group.brand || "Other";
      const item: DisplayItem = {
        type: familyProducts.length > 1 ? "family" : "product",
        representative,
        variantCount: familyProducts.length,
        familyId: group.modelKey,
        familyProducts,
        sortPrice,
        series: null,
      };
      const arr = byBrand.get(brand) ?? [];
      arr.push(item);
      byBrand.set(brand, arr);
    }

    const standalones = productPool.filter((p) => !idsInGroups.has(p.id));
    for (const p of standalones) {
      const brand = p.brand || "Other";
      const item: DisplayItem = {
        type: "product",
        representative: p,
        variantCount: 1,
        familyId: null,
        familyProducts: [p],
        sortPrice: getEffectivePrice(p),
        series: null,
      };
      const arr = byBrand.get(brand) ?? [];
      arr.push(item);
      byBrand.set(brand, arr);
    }

    const out: Record<string, DisplayItem[]> = {};
    for (const [brand, items] of byBrand) {
      items.sort((a, b) => a.sortPrice - b.sortPrice);
      out[brand] = items;
    }
    return out;
  }, [
    activeSubcategoryId,
    spectrumStarModelGroups,
    cleanProducts,
  ]);

  // Count products with images in focus range (for stats)
  const focusStats = useMemo(() => {
    let inFocus = 0;
    let withImage = 0;
    for (const p of filteredProducts) {
      const price = getEffectivePrice(p);
      if (
        (price >= focusRange[0] && price <= focusRange[1]) ||
        price === 0
      ) {
        inFocus++;
        if (isRealImage(p.image_url)) withImage++;
      }
    }
    return { inFocus, withImage };
  }, [filteredProducts, focusRange]);

  // Available tier filters from the data
  const availableFilters = useMemo(() => {
    const tiers = new Set<string>();
    cleanProducts.forEach((p) => {
      if (p.tier) tiers.add(p.tier);
    });
    return Array.from(tiers);
  }, [cleanProducts]);

  // --------------------------------------------------------------------------
  // 5. BRAND MATRIX
  // --------------------------------------------------------------------------
  const brandMatrix = useMemo(() => {
    if (filteredProducts.length === 0) return { brands: [] };
    const grouped: Record<string, ConductorProduct[]> = {};
    filteredProducts.forEach((p) => {
      const brand = p.brand || "Other";
      if (!grouped[brand]) grouped[brand] = [];
      grouped[brand].push(p);
    });
    const sortedBrands = Object.entries(grouped)
      .sort((a, b) => {
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

  // --------------------------------------------------------------------------
  // 6. EVENT HANDLERS
  // --------------------------------------------------------------------------
  // Debounced hover: only update preview after cursor rests for 180ms.
  // If a product is pinned, hover previews are suppressed.
  const handleHoverProduct = useCallback(
    (product: ConductorProduct, familyProducts: ConductorProduct[]) => {
      // If this product is already displayed, skip
      if (hoveredProduct?.id === product.id) return;
      // If a product is pinned, don't allow hover to override
      if (pinnedProductId) return;

      // Store pending hover and start debounce timer
      pendingHoverRef.current = { product, familyProducts };
      if (hoverTimerRef.current) clearTimeout(hoverTimerRef.current);
      hoverTimerRef.current = setTimeout(() => {
        const pending = pendingHoverRef.current;
        if (pending) {
          setHoveredProduct(pending.product);
          setHoveredFamilyProducts(pending.familyProducts);
          setImageLoadError(false);
          pendingHoverRef.current = null;
        }
      }, 180);
    },
    [hoveredProduct?.id, pinnedProductId],
  );

  const handleHoverOut = useCallback(() => {
    // Cancel any pending hover (cursor left before debounce fired)
    if (hoverTimerRef.current) {
      clearTimeout(hoverTimerRef.current);
      hoverTimerRef.current = null;
    }
    pendingHoverRef.current = null;
    // Don't clear the preview — keep the last product visible (sticky)
  }, []);

  // Click-to-pin: first click pins the product in the preview panel.
  // Second click on the same pinned product navigates to the detail page.
  // Clicking a different product pins that one instead.
  const handleClickProduct = useCallback(
    (id: string) => {
      if (pinnedProductId === id) {
        // Second click on same product → navigate to detail page
        setPinnedProductId(null);
        openProductPage(id);
      } else {
        // First click → pin this product
        setPinnedProductId(id);
        // Find the product in filtered data and set it in the preview
        const product = filteredProducts.find((p) => p.id === id);
        if (product) {
          setHoveredProduct(product);
          setHoveredFamilyProducts([product]);
          setImageLoadError(false);
        }
      }
    },
    [pinnedProductId, openProductPage, filteredProducts],
  );

  // Unpin when clicking outside the tiles (on the background)
  const handleBackgroundClick = useCallback(() => {
    if (pinnedProductId) {
      setPinnedProductId(null);
    }
  }, [pinnedProductId]);

  // Clean up hover timer on unmount
  useEffect(() => {
    return () => {
      if (hoverTimerRef.current) clearTimeout(hoverTimerRef.current);
    };
  }, []);

  // Track whether the minimap handles are being dragged to suppress scroll sync
  const isDraggingMinimapRef = useRef(false);

  const handleFocusRangeChange = useCallback(
    (range: [number, number]) => {
      // Direct range update — no rounding, no snapping, no zones.
      // Only clamp to absolute boundaries.
      setFocusRange([
        Math.max(priceExtent[0], range[0]),
        Math.min(priceExtent[1], range[1]),
      ]);
    },
    [priceExtent],
  );

  // Tier zoom presets (user clicks a tier button → jump to that range)
  const handleSnapTier = useCallback(
    (tier: string) => {
      const tb = TIER_BOUNDARIES[tier];
      if (tb) {
        const min = Math.max(priceExtent[0], tb.min || 1);
        const max = Math.min(priceExtent[1], tb.max);
        setFocusRange([min, max]);
      }
    },
    [priceExtent],
  );

  // --------------------------------------------------------------------------
  // 7. MOUSE WHEEL ZOOM (Ctrl/Cmd+wheel or pinch only — regular scroll is free)
  // --------------------------------------------------------------------------
  const handleWheel = useCallback(
    (e: React.WheelEvent) => {
      // Only intercept Ctrl+wheel (pinch-to-zoom on trackpads reports ctrlKey=true)
      // or Meta+wheel. Regular scroll (vertical + horizontal) passes through natively.
      if (!e.ctrlKey && !e.metaKey) return;

      e.preventDefault();
      const [fMin, fMax] = focusRange;
      const [pMin, pMax] = priceExtent;
      const span = fMax - fMin;
      const totalSpan = pMax - pMin;

      // Zoom factor — use smaller steps for pinch gestures (ctrlKey)
      const zoomSpeed = e.ctrlKey ? 0.08 : 0.15;
      const delta = e.deltaY > 0 ? 1 + zoomSpeed : 1 - zoomSpeed;

      // Calculate where the mouse is pointing (as a ratio of the visible viewport)
      const el = scrollContainerRef.current;
      const rect = el?.getBoundingClientRect();
      const mouseRatio = rect
        ? Math.max(
            0,
            Math.min(1, (e.clientX - rect.left) / rect.width),
          )
        : 0.5;

      // The price at the cursor position
      const cursorPrice = fMin + mouseRatio * span;

      // New span
      const newSpan = Math.max(50, Math.min(totalSpan, span * delta));

      // Anchor on cursor position
      const newMin = Math.max(pMin, cursorPrice - mouseRatio * newSpan);
      const newMax = Math.min(pMax, newMin + newSpan);

      setFocusRange([newMin, newMax]);
    },
    [focusRange, priceExtent],
  );

  // --------------------------------------------------------------------------
  // 8. RENDER
  // --------------------------------------------------------------------------
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
            {neuronDisplayItemsByBrand != null && (
              <span className="text-[9px] text-emerald-400/80 font-bold uppercase tracking-wider ml-1" title="View grouped by model (nucleus + variations)">
                Neuron
              </span>
            )}
          </div>
          {!isAggregate && (
            <div className="hidden md:flex items-center gap-2 text-xs font-mono text-blue-500/70 border border-blue-900/30 rounded-full px-3 py-1 bg-blue-950/20">
              <Zap className="w-3 h-3" />
              <span>
                {focusStats.inFocus} in focus
                {focusStats.withImage > 0 && (
                  <span className="text-zinc-600 ml-1">
                    ({focusStats.withImage} with image)
                  </span>
                )}
              </span>
            </div>
          )}
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
        {/* LEFT: VISUAL FEED — main product + variant images */}
        <Surface
          variant="screen"
          active={!!hoveredProduct}
          className="col-span-4 bg-zinc-950 flex flex-col justify-center items-center p-2 relative overflow-hidden"
        >
          {hoveredProduct ? (
            <VisualFeedPanel
              product={hoveredProduct}
              familyProducts={hoveredFamilyProducts}
              imageLoadError={imageLoadError}
              onImageError={() => setImageLoadError(true)}
              onProductClick={openProductPage}
            />
          ) : (
            <div className="flex flex-col items-center justify-center gap-4 text-zinc-800">
              <div className="w-16 h-16 rounded-full bg-zinc-900/50 flex items-center justify-center">
                <Sparkles className="w-8 h-8 opacity-20" />
              </div>
              <div className="text-xs font-mono tracking-[0.15em] uppercase opacity-50 text-center leading-relaxed">
                Hover to preview<br/>
                <span className="text-[9px] text-zinc-700">Click to pin &middot; Double-click for details</span>
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
              <div className="flex items-center justify-between border-b border-zinc-800 pb-2 shrink-0">
                <div className="flex flex-col overflow-hidden flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <div className={`w-1.5 h-1.5 rounded-full ${pinnedProductId === hoveredProduct.id ? 'bg-amber-400' : 'bg-emerald-500 animate-pulse'}`} />
                    <span className={`text-[10px] font-mono tracking-widest ${pinnedProductId === hoveredProduct.id ? 'text-amber-400' : 'text-emerald-500'}`}>
                      {pinnedProductId === hoveredProduct.id ? 'PINNED' : 'SKU:'} {hoveredProduct.id || "N/A"}
                    </span>
                    {pinnedProductId === hoveredProduct.id && (
                      <button
                        onClick={() => setPinnedProductId(null)}
                        className="text-[9px] text-zinc-500 hover:text-zinc-300 transition-colors ml-1 px-1.5 py-0.5 rounded bg-zinc-800/50 hover:bg-zinc-700/50"
                      >
                        unpin
                      </button>
                    )}
                  </div>
                  <h1 className="text-xl font-black text-white uppercase tracking-tight mt-1 truncate w-full">
                    {hoveredProduct.name}
                  </h1>
                </div>
                <div className="flex-shrink-0 ml-3">
                  <BrandLogo
                    brand={hoveredProduct.brand}
                    className="h-10 w-auto max-w-[80px] opacity-80"
                  />
                </div>
              </div>

              {(hoveredProduct.description_short ||
                hoveredProduct.description) && (
                <div className="text-[11px] text-zinc-400 font-sans leading-relaxed line-clamp-3 border-l-2 border-zinc-800 pl-3 shrink-0">
                  {hoveredProduct.description_short ||
                    hoveredProduct.description}
                </div>
              )}

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
            <ProductIntelligenceCard
              product={hoveredProduct}
              familyProducts={hoveredFamilyProducts}
              openProductPage={openProductPage}
            />
          ) : null}
        </Surface>
      </div>

      {/* --- PRICE RANGE SLIDER --- */}
      {!isLoading && filteredProducts.length > 0 && (
        <div className="shrink-0 bg-[#080808] border-b border-zinc-800/50 pt-4 pb-2">
          <div className="flex items-center px-4 mb-1">
            <div className="w-28 shrink-0 text-center">
              <span className="text-[9px] font-bold text-zinc-600 uppercase tracking-widest">
                Brand
              </span>
            </div>
            <div className="flex-1 flex items-center gap-2 text-[9px] text-zinc-600 font-mono">
              <span className="text-zinc-500 uppercase tracking-widest font-bold">
                Price Spectrum
              </span>
              <span className="ml-auto text-zinc-600">
                {filteredProducts.length} total
              </span>
            </div>
          </div>
          <div className="flex items-center">
            <div className="w-28 shrink-0" />
            <div className="flex-1">
              <MiniSpectrum
                focusRange={focusRange}
                priceExtent={priceExtent}
                products={filteredProducts}
                onFocusRangeChange={handleFocusRangeChange}
                onReset={() => setFocusRange(priceExtent)}
                onDragStateChange={(isDragging) => { isDraggingMinimapRef.current = isDragging; }}
              />
            </div>
          </div>
        </div>
      )}

      {/* --- BRAND SWIMLANES ENGINE (scrollable) --- */}
      <div
        className="flex-1 relative bg-[#050505] overflow-hidden flex flex-col"
        ref={tracksRef}
        onWheel={handleWheel}
      >
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
                {activeSmartTag
                  ? "Try adjusting your filters to see more products."
                  : "This spectrum doesn't have any products yet."}
              </p>
              {activeSmartTag && (
                <button
                  onClick={() => setActiveSmartTag(null)}
                  className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg text-sm transition-colors"
                >
                  Clear All Filters
                </button>
              )}
            </div>
          </div>
        ) : (
          <div
            ref={scrollContainerRef}
            className="flex-1 overflow-auto custom-scrollbar"
            onScroll={handleScrollSync}
            onClick={handleBackgroundClick}
          >
            <div
              style={{
                width: `${canvasWidthPercent}%`,
                minWidth: "100%",
              }}
            >
              {brandMatrix.brands.map(
                ({ brand, products, rgbColor, brandPrimary }) => (
                  <BrandTrack
                    key={brand}
                    brand={brand}
                    products={products}
                    displayItems={neuronDisplayItemsByBrand?.[brand]}
                    rgbColor={rgbColor}
                    brandPrimary={brandPrimary}
                    families={families}
                    priceExtent={priceExtent}
                    focusRange={focusRange}
                    pinnedProductId={pinnedProductId}
                    onHoverProduct={handleHoverProduct}
                    onHoverOut={handleHoverOut}
                    onClickProduct={handleClickProduct}
                  />
                ),
              )}
            </div>
          </div>
        )}
      </div>

      {/* --- BOTTOM DECK: SMART TAG FILTERS + TIER ZOOM CONTROLS --- */}
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

        {/* Tier Zoom Controls — these snap the focus range to a tier */}
        <div className="flex items-center px-4 gap-4 h-12">
          <div className="flex items-center justify-center gap-1 overflow-x-auto no-scrollbar py-2 mask-linear-fade flex-1">
            <Control
              variant="1176"
              label="ALL"
              active={isAggregate}
              onClick={() => setFocusRange(priceExtent)}
            />
            <div className="w-px h-4 bg-zinc-800 mx-1" />
            {availableFilters.map((filter) => {
              const tb = TIER_BOUNDARIES[filter];
              const isActive =
                !isAggregate &&
                tb &&
                Math.abs(focusRange[0] - Math.max(priceExtent[0], tb.min || 1)) < 50 &&
                Math.abs(focusRange[1] - Math.min(priceExtent[1], tb.max)) < 50;
              return (
                <Control
                  key={filter}
                  variant="1176"
                  label={filter}
                  active={isActive}
                  onClick={() => handleSnapTier(filter)}
                />
              );
            })}
          </div>
        </div>
      </Surface>
    </div>
  );
};
