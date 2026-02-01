import React, { useEffect, useMemo, useState } from "react";
import {
  Activity,
  ArrowLeft,
  Search,
  SlidersHorizontal,
  Zap,
  Tag,
  Info,
  ExternalLink,
  BookOpen,
  Box,
  CheckCircle2,
  AlertCircle,
  Factory,
  Globe,
  Settings,
  ChevronRight,
} from "lucide-react";
import { useNavigationStore } from "../../store/navigationStore";
import { catalogLoader } from "../../lib/catalogLoader";
import { resolveProductImage } from "../../lib/imageResolver";
import { brandThemes, getBrandTheme } from "../../styles/brandThemes";
import type { Product, ImageAsset } from "../../types";
import { formatPrice } from "../../lib/priceFormatter";

// --- Internal Components ---

/**
 * ProductDisplayStage: The main detail view located at the top of the screen.
 * Populates with data from the hovered product below.
 */
const ProductDisplayStage = ({
  product,
  brandMeta,
}: {
  product: Product | null;
  brandMeta: Record<string, { logo_url?: string | null; name: string }>;
}) => {
  const { goToGalaxy } = useNavigationStore();
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  // Reset selected image when product changes
  useEffect(() => {
    if (product) {
      setSelectedImage(resolveProductImage(product));
    }
  }, [product]);

  if (!product) {
    return (
      <div className="h-[60vh] flex flex-col items-center justify-center text-zinc-600 border-b border-zinc-800 bg-[#080808] relative">
        <button
          onClick={goToGalaxy}
          className="absolute top-6 left-6 flex items-center gap-2 text-zinc-500 hover:text-white transition-colors z-50 text-sm font-medium"
        >
          <ArrowLeft size={16} /> Galaxy View
        </button>
        <Activity size={48} className="opacity-20 mb-4 animate-pulse" />
        <h2 className="text-xl font-light tracking-wide">AWAITING SIGNAL</h2>
        <p className="text-sm opacity-50 mt-2 font-mono">
          Hover over the spectrum to analyze products
        </p>
      </div>
    );
  }

  const brandName =
    brandMeta[product.brand_id || ""]?.name ||
    product.brand_id ||
    "Unknown Brand";
  const brandTheme = getBrandTheme(product.brand_id || "");
  const price = product.price && product.price > 0 ? product.price : null;

  // Process Images
  const mainImage = selectedImage || resolveProductImage(product);
  const gallery = product.image_gallery || [];
  // Ensure gallery has valid objects or strings
  const galleryImages: string[] = gallery
    .map((g) => {
      if (typeof g === "string") return g;
      // @ts-ignore - types might be loose here
      return g.url || "";
    })
    .filter((url) => !!url);

  // Add main image to gallery for navigation if not present
  const allImages = [
    resolveProductImage(product),
    ...galleryImages.filter((url) => url !== resolveProductImage(product)),
  ].slice(0, 6); // Limit to 6

  return (
    <div
      className="h-[60vh] flex bg-[#080808] border-b border-zinc-800 relative shadow-[0_10px_40px_-10px_rgba(0,0,0,0.5)] z-30 transition-colors duration-500"
      style={{ borderTopColor: brandTheme.primary }}
    >
      {/* Back Button Overlay */}
      <button
        onClick={goToGalaxy}
        className="absolute top-6 left-6 flex items-center gap-2 text-zinc-500 hover:text-white transition-colors z-50 text-sm font-medium bg-black/20 backdrop-blur px-3 py-1.5 rounded-full border border-white/5 hover:border-white/20"
      >
        <ArrowLeft size={16} /> Galaxy View
      </button>

      {/* 1. VISUALS COLUMN (Left) */}
      <div className="w-1/3 p-8 flex flex-col items-center justify-center border-r border-zinc-800/50 bg-gradient-to-b from-[#0a0a0a] to-[#050505] relative overflow-hidden">
        <div
          className="absolute inset-0 opacity-[0.03] pointer-events-none"
          style={{
            background: `radial-gradient(circle at center, ${brandTheme.primary}, transparent 70%)`,
          }}
        />

        <div className="relative w-full aspect-square max-h-[400px] mb-6 flex items-center justify-center p-4">
          {/* Glow behind image */}
          <div
            className="absolute inset-0 opacity-20 blur-3xl rounded-full"
            style={{ backgroundColor: brandTheme.primary }}
          />
          <img
            src={mainImage}
            alt={product.name}
            className="relative w-full h-full object-contain drop-shadow-2xl z-10 transition-all duration-300"
          />
          {product.is_bestseller && (
            <div className="absolute top-4 right-4 z-20 bg-yellow-500/10 border border-yellow-500/50 text-yellow-500 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 backdrop-blur-md">
              <Zap size={12} fill="currentColor" /> BESTSELLER
            </div>
          )}
        </div>

        {/* Thumbnails */}
        {allImages.length > 1 && (
          <div className="flex gap-2 overflow-x-auto max-w-full pb-2 no-visible-scrollbar z-20">
            {allImages.map((img, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedImage(img)}
                className={`w-14 h-14 rounded-md border bg-black/50 p-1 flex-shrink-0 transition-all ${selectedImage === img ? "border-zinc-400 ring-1 ring-zinc-700" : "border-zinc-800 hover:border-zinc-600 opacity-60 hover:opacity-100"}`}
              >
                <img
                  src={img}
                  alt=""
                  className="w-full h-full object-contain"
                />
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 2. DETAILS COLUMN (Center) */}
      <div className="flex-1 p-8 flex flex-col overflow-y-auto custom-scrollbar">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            <span className="text-xs font-bold uppercase tracking-widest px-2 py-0.5 rounded text-zinc-400 bg-zinc-900 border border-zinc-800">
              {brandName}
            </span>
            <ChevronRight size={12} className="text-zinc-600" />
            <span className="text-xs font-mono text-indigo-400 uppercase font-bold tracking-wider">
              {product.category || "Uncategorized"}
            </span>
            {product.subcategories && product.subcategories.length > 0 && (
              <>
                <ChevronRight size={12} className="text-zinc-600" />
                <span className="text-xs font-mono text-zinc-500 uppercase">
                  {product.subcategories.join(", ")}
                </span>
              </>
            )}
          </div>

          <h1 className="text-4xl font-black tracking-tight text-white mb-3 shadow-black drop-shadow-sm leading-none">
            {product.name}
          </h1>
        </div>

        {/* Tabs / Content */}
        <div className="grid grid-cols-2 gap-8 mb-8">
          {/* Description */}
          <div className="col-span-2 text-zinc-400 text-sm leading-relaxed max-w-3xl bg-zinc-900/30 p-5 rounded-lg border border-white/5 shadow-inner">
            {product.description_full ||
              product.description_short ||
              "No description available."}
          </div>
        </div>

        {/* Sources Data Grid */}
        <div className="grid grid-cols-3 gap-4 mt-auto">
          {/* OFFICIAL DATA */}
          <div className="bg-zinc-900/40 border border-zinc-800 p-4 rounded group hover:border-zinc-700 transition-colors">
            <div className="flex items-center gap-2 mb-3 text-xs font-bold text-zinc-500 uppercase tracking-wider">
              <Factory size={14} /> Official Specs
            </div>
            <div className="space-y-2">
              {product.specs && Object.keys(product.specs).length > 0 ? (
                <div className="text-xs text-zinc-400 space-y-1">
                  {Object.entries(product.specs)
                    .slice(0, 6)
                    .map(([key, val], i) => (
                      <div
                        key={i}
                        className="flex justify-between border-b border-white/5 pb-1"
                      >
                        <span className="opacity-70">{key}:</span>
                        <span className="font-mono text-zinc-300">Yes</span>
                      </div>
                    ))}
                  {Object.keys(product.specs).length > 6 && (
                    <div className="pt-1 text-indigo-400 text-[10px] cursor-pointer hover:underline">
                      View Full Specs (+{Object.keys(product.specs).length - 6}{" "}
                      more)
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-xs text-zinc-600 italic">
                  Standard specs configuration
                </div>
              )}

              {product.source_url && (
                <a
                  href={product.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-1.5 text-xs text-indigo-400 mt-3 hover:text-indigo-300"
                >
                  <BookOpen size={12} /> Manufacturer Page
                </a>
              )}
            </div>
          </div>

          {/* COMMERCIAL DATA */}
          <div className="bg-zinc-900/40 border border-zinc-800 p-4 rounded group hover:border-zinc-700 transition-colors">
            <div className="flex items-center gap-2 mb-3 text-xs font-bold text-zinc-500 uppercase tracking-wider">
              <Globe size={14} /> Commercial (Halilit)
            </div>
            <div className="space-y-3">
              <div>
                <div className="text-[10px] text-zinc-500 uppercase mb-1">
                  List Price
                </div>
                <div className="text-xl font-mono font-bold text-white flex items-baseline gap-1">
                  {price ? (
                    formatPrice(price, "ILS")
                  ) : (
                    <span className="text-zinc-600 text-base">
                      Contact for price
                    </span>
                  )}
                </div>
              </div>

              <div>
                <div className="text-[10px] text-zinc-500 uppercase mb-1">
                  Status
                </div>
                <div
                  className={`inline-flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium border ${
                    product.stock_status === "in_stock"
                      ? "bg-emerald-950/50 border-emerald-900 text-emerald-400"
                      : "bg-zinc-800 border-zinc-700 text-zinc-400"
                  }`}
                >
                  {product.stock_status === "in_stock" ? (
                    <CheckCircle2 size={12} />
                  ) : (
                    <AlertCircle size={12} />
                  )}
                  {product.stock_status
                    ? product.stock_status.replace(/_/g, " ").toUpperCase()
                    : "CHECK STOCK"}
                </div>
              </div>
            </div>
          </div>

          {/* CONTEXTUAL DATA */}
          <div className="bg-zinc-900/40 border border-zinc-800 p-4 rounded group hover:border-zinc-700 transition-colors">
            <div className="flex items-center gap-2 mb-3 text-xs font-bold text-zinc-500 uppercase tracking-wider">
              <Box size={14} /> Contextual (AI)
            </div>
            <div className="space-y-2">
              {(product.pros && product.pros.length > 0) ||
              (product.expert_tips && product.expert_tips.length > 0) ? (
                <ul className="text-xs text-zinc-400 space-y-1.5">
                  {/* Show 1 Pro or 1 Tip */}
                  {(product.pros || []).slice(0, 1).map((pro, i) => (
                    <li key={`p-${i}`} className="flex gap-2">
                      <CheckCircle2
                        size={12}
                        className="text-emerald-500 flex-shrink-0 mt-0.5"
                      />
                      <span className="line-clamp-2">{pro}</span>
                    </li>
                  ))}
                  {(product.expert_tips || []).slice(0, 1).map((tip, i) => (
                    <li key={`t-${i}`} className="flex gap-2">
                      <Info
                        size={12}
                        className="text-indigo-500 flex-shrink-0 mt-0.5"
                      />
                      <span className="line-clamp-2">{tip}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="text-xs text-zinc-600 italic">
                  No AI insights generated yet.
                </div>
              )}
              <div className="mt-2 flex gap-1">
                {["reviews", "manuals", "comparison"].map((tag) => (
                  <span
                    key={tag}
                    className="text-[9px] px-1.5 py-0.5 bg-zinc-800 rounded text-zinc-500"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * SpectrumNode: A point on the frequency spectrum representing a product.
 * Now a "Card" style for video-track look.
 */
const SpectrumNode = ({
  product,
  color,
  positionPercent,
  laneOffset,
  onHover,
  isActive,
}: {
  product: Product;
  color: string;
  positionPercent: number;
  laneOffset: number;
  onHover: (p: Product | null) => void;
  isActive: boolean;
}) => {
  // Stagger vertical position more aggressively for cards
  // 3 lanes: 10%, 35%, 60%
  const topPosition = `${10 + laneOffset * 28}%`;
  const image = resolveProductImage(product);

  return (
    <div
      className={`absolute flex flex-col group transition-all duration-300 z-10 hover:z-50 cursor-pointer ${isActive ? "z-50 scale-110" : "hover:scale-105"}`}
      style={{
        left: `${positionPercent}%`, // Position based on wider container
        top: topPosition,
        transform: "translateX(-50%)",
        width: "100px",
      }}
      onMouseEnter={() => onHover(product)}
    >
      {/* The "Clip" Card */}
      <div
        className={`relative h-14 w-full rounded-md border overflow-hidden shadow-lg bg-zinc-900 flex items-center justify-center ${
          isActive
            ? "border-white ring-2 ring-white/30"
            : "border-zinc-700/50 hover:border-zinc-500"
        }`}
      >
        {/* Background tint */}
        <div
          className="absolute inset-0 opacity-20"
          style={{ backgroundColor: color }}
        />

        {/* Thumbnail */}
        <img
          src={image}
          alt=""
          className="w-full h-full object-cover opacity-80 group-hover:opacity-100"
        />

        {/* Price Tag Overlay */}
        <div className="absolute bottom-0 right-0 bg-black/80 px-1 py-0.5 text-[9px] font-mono text-white rounded-tl">
          {product.price ? formatPrice(product.price, "ILS", 0) : "N/A"}
        </div>
      </div>

      {/* Label underneath */}
      <div
        className={`mt-1 text-[9px] font-medium leading-tight text-center transition-colors truncate px-1 rounded ${isActive ? "text-white bg-black/50" : "text-zinc-500 group-hover:text-zinc-300"}`}
      >
        {product.name}
      </div>

      {/* Vertical Guideline (active only) */}
      {isActive && (
        <div className="absolute top-14 left-1/2 -translate-x-1/2 w-px h-[500px] bg-gradient-to-b from-white to-transparent opacity-30 pointer-events-none z-0" />
      )}
    </div>
  );
};

// --- Internal Components ---
interface PriceRange {
  min: number;
  max: number;
}

/**
 * BrandTrack: Represents a single horizontal lane.
 * Fixed width (100% of container), products positioned by price.
 */
const BrandTrack = ({
  brandName,
  logoUrl,
  products,
  color,
  globalRange,
  onHover,
  activeProductId,
}: {
  brandName: string;
  logoUrl?: string | null;
  products: Product[];
  color: string;
  globalRange: PriceRange;
  onHover: (p: Product | null) => void;
  activeProductId: string | null;
}) => {
  const [imgSrc, setImgSrc] = useState<string | null>(logoUrl || null);

  // If logoUrl is just a filename or missing, try local assets
  useEffect(() => {
    if (!logoUrl) {
      // Try to construct asset URL from brand name
      const slug = brandName.toLowerCase().replace(/\s+/g, "-");
      setImgSrc(`/assets/logos/${slug}_logo.png`);
    } else {
      setImgSrc(logoUrl);
    }
  }, [brandName, logoUrl]);

  // Logarithmic Scale Positioning
  const getPosition = (price: number) => {
    if (!price || price <= 0) return 0;

    // Logarithmic scale: x = (log(price) - log(min)) / (log(max) - log(min))
    // We define a logical "min" floor (e.g., 10 or 100) to avoid -Infinity issues with low numbers if min is 0
    const minLog = Math.log(Math.max(globalRange.min, 10));
    const maxLog = Math.log(globalRange.max);
    const priceLog = Math.log(Math.max(price, 10));

    const normalized = (priceLog - minLog) / (maxLog - minLog);

    // Clamp between 0 and 1
    const clamped = Math.max(0, Math.min(1, normalized));

    // Map to 1% - 99% of the WIDE container
    return 1 + clamped * 98;
  };

  return (
    <div className="flex bg-zinc-950/30 border-b border-white/5 group h-24 shrink-0 relative hover:bg-white/5 transition-colors">
      {/* TRACK HEADER (Sticky Left - Branding) */}
      <div className="sticky left-0 w-32 flex-shrink-0 flex flex-col justify-center p-3 border-r border-white/5 bg-black/95 backdrop-blur-md z-30 shadow-[4px_0_20px_-5px_rgba(0,0,0,0.5)]">
        <div
          className="absolute inset-y-0 left-0 w-1 opacity-50 group-hover:opacity-100 transition-opacity"
          style={{ backgroundColor: color }}
        />

        <div className="flex items-center gap-2">
          <div className="w-8 h-8 flex items-center justify-center p-0.5 bg-white/5 rounded overflow-hidden">
            {imgSrc ? (
              <img
                src={imgSrc}
                alt={brandName}
                className="max-w-full max-h-full object-contain opacity-80 group-hover:opacity-100 transition-all"
                onError={(e) => {
                  // Fallback to text if image fails
                  e.currentTarget.style.display = "none";
                  setImgSrc(null);
                }}
              />
            ) : (
              <div
                className="w-full h-full flex items-center justify-center text-[10px] font-bold text-zinc-500"
                style={{ color }}
              >
                {brandName.substring(0, 2).toUpperCase()}
              </div>
            )}
          </div>

          <div className="min-w-0">
            <h3 className="text-xs font-bold text-zinc-400 truncate group-hover:text-white transition-colors">
              {brandName}
            </h3>
            <div className="text-[9px] text-zinc-600 font-mono mt-0.5">
              {products.length} Products
            </div>
          </div>
        </div>
      </div>

      {/* TRACK CANVAS (Right Area - Absolute positioning within Wide Container) */}
      <div className="flex-1 relative w-full overflow-hidden">
        {/* Full Track Ambient Background */}
        <div
          className="absolute inset-0 opacity-[0.01] group-hover:opacity-[0.04] transition-opacity pointer-events-none"
          style={{ backgroundColor: color }}
        />

        {/* Grid Lines for reference (Log Scale Ticks) */}
        {[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9].map((tick) => (
          <div
            key={tick}
            className="absolute inset-y-0 w-px bg-white/5"
            style={{ left: `${tick * 100}%` }}
          />
        ))}

        {products.map((product, idx) => {
          const price = product.price || 0;
          if (price <= 0) return null; // Skip invalid prices

          const pos = getPosition(price);
          return (
            <SpectrumNode
              key={`${brandName}-${product.id}-${idx}`}
              product={product}
              color={color}
              positionPercent={pos}
              laneOffset={idx % 3} // Stagger
              onHover={onHover}
              isActive={activeProductId === product.id}
            />
          );
        })}
      </div>
    </div>
  );
};

// --- Main Component ---

const SpectrumModule: React.FC = () => {
  const { activeTribeId, goToGalaxy } = useNavigationStore();
  const [products, setProducts] = useState<Product[]>([]);
  const [brandMeta, setBrandMeta] = useState<
    Record<string, { logo_url?: string | null; name: string }>
  >({});
  const [loading, setLoading] = useState(true);
  const [hoveredProduct, setHoveredProduct] = useState<Product | null>(null);

  // 1. Fetch Data
  useEffect(() => {
    async function fetchData() {
      try {
        console.log("[SpectrumModule] Starting data fetch...");
        // Directly load the index and fetch all brand catalogs
        const index = await catalogLoader.loadIndex();

        // Build brand metadata map
        const meta: Record<string, { logo_url?: string | null; name: string }> =
          {};
        index.brands.forEach((b) => {
          meta[b.id] = { logo_url: b.logo_url, name: b.name };
        });
        setBrandMeta(meta);

        const allBrandProducts: Product[] = [];

        for (const brandEntry of index.brands) {
          try {
            const catalog = await catalogLoader.loadBrand(brandEntry.id);
            allBrandProducts.push(...catalog.products);
          } catch (err) {
            console.warn(
              `[SpectrumModule] Failed to load brand ${brandEntry.id}:`,
              err,
            );
          }
        }

        setProducts(allBrandProducts);
      } catch (error) {
        console.error("[SpectrumModule] Failed to load products:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  // Helper to ensure every product has a visual price
  const getDisplayPrice = (p: Product) => {
    if (p.price && p.price > 0) return p.price;
    // Synthetic price generation for demo/null data
    // Map tier_score (0-100) to range
    const score = p.tier_score || 50;
    // Add deterministic noise from ID
    const noise =
      p.id.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0) % 500;
    return score * 50 + noise + 100;
  };

  // 2. Process Data: Group by Brand & Sort by Price
  const { organizedData, globalRange } = useMemo(() => {
    if (!products || products.length === 0)
      return { organizedData: null, globalRange: { min: 0, max: 0 } };

    // Calculate Global Min/Max for scaling using display prices
    const prices = products.map(getDisplayPrice);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    // Add buffer
    const globalRange = { min: minPrice, max: maxPrice * 1.1 };

    // Group by Manufacturer (Brand)
    const grouped: Record<string, Product[]> = {};
    products.forEach((p) => {
      const brand = p.brand_id || "Generic";
      if (!grouped[brand]) grouped[brand] = [];
      grouped[brand].push(p);
    });

    // Sort Brands alphabetically
    const sortedBrands = Object.keys(grouped).sort();

    // Within each brand, sort products by Price (Low -> High)
    const result = sortedBrands.map((brand) => {
      const brandProducts = grouped[brand].sort(
        (a, b) => getDisplayPrice(a) - getDisplayPrice(b),
      );

      // Map products to include their computed display price for positioning
      const productsWithPos = brandProducts.map((p) => ({
        ...p,
        // We temporarily override price for the visualization view if it's missing
        price: p.price && p.price > 0 ? p.price : getDisplayPrice(p),
      }));

      const displayName = brandMeta[brand]?.name || brand;
      // Use getBrandTheme for safer color resolution
      const theme = getBrandTheme(brand);

      return {
        brandName: displayName,
        logoUrl: brandMeta[brand]?.logo_url,
        items: productsWithPos,
        color: theme.primary,
      };
    });

    return { organizedData: result, globalRange };
  }, [products, brandMeta]);

  if (loading) {
    return (
      <div className="h-full w-full flex items-center justify-center bg-slate-950 text-slate-500 font-mono animate-pulse">
        <Activity className="mr-2" />
        LOADING SPECTRUM ENGINE...
      </div>
    );
  }

  if (!organizedData || organizedData.length === 0) {
    return (
      <div className="h-full w-full flex flex-col items-center justify-center bg-slate-950 text-slate-400">
        <Search size={48} className="mb-4 opacity-20" />
        <h2 className="text-xl">No Signal Detected</h2>
        <p className="text-sm opacity-50 mt-2">This frequency band is empty.</p>
        <button
          onClick={goToGalaxy}
          className="mt-6 text-indigo-400 hover:text-indigo-300 text-sm flex items-center"
        >
          <ArrowLeft size={16} className="mr-2" /> Return to Galaxy
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-black text-zinc-200 overflow-hidden">
      {/* TOP: Product Display Stage (Context) - ~60% Height */}
      <ProductDisplayStage product={hoveredProduct} brandMeta={brandMeta} />

      {/* MIDDLE: Timeline Header / Legend */}
      <div className="h-10 bg-[#080808] border-b border-zinc-800 flex items-center justify-between px-4 z-10 shrink-0 shadow-lg">
        <div className="flex items-center gap-2 text-xs text-zinc-500 font-bold uppercase tracking-widest pl-[120px]">
          <SlidersHorizontal size={14} className="text-indigo-500" />
          <span className="text-white">Spectrum:</span>{" "}
          {activeTribeId?.replace(/-/g, " ") || "All Products"}
        </div>

        <div className="flex items-center gap-6">
          <div className="text-[10px] text-zinc-600 font-mono">
            LOGARITHMIC SCALE (Price)
          </div>
          {/* Scale Axis Visual */}
          <div className="flex items-center gap-2 text-[10px] font-mono text-zinc-500">
            <span>{formatPrice(globalRange.min, "ILS", 0)}</span>
            <div className="w-64 h-2 bg-gradient-to-r from-zinc-800 via-zinc-700 to-zinc-600 rounded-full relative overflow-hidden">
              {[0.25, 0.5, 0.75].map((p) => (
                <div
                  key={p}
                  className="absolute top-0 bottom-0 w-px bg-black/50"
                  style={{ left: `${p * 100}%` }}
                />
              ))}
            </div>
            <span>{formatPrice(globalRange.max, "ILS", 0)}+</span>
          </div>
        </div>
      </div>

      {/* BOTTOM: Tracks (Spectrum) - Horizontal Scroll enabled */}
      <div className="flex-1 overflow-auto bg-[#030303] relative custom-scrollbar">
        {/* WIDE Content Area for Horizontal Scrolling */}
        <div className="min-w-[300%] relative pb-10">
          {/* Grid Background Lines (DAW style) - Expanded across wide area */}
          <div className="absolute inset-0 pointer-events-none opacity-[0.03] z-0">
            {/* Logarithmic Grid Approximation for visuals */}
            {[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9].map((tick) => (
              <div
                key={`grid-${tick}`}
                className="absolute inset-y-0 w-px bg-slate-400 border-l border-dashed border-slate-500"
                style={{ left: `${tick * 100}%` }}
              />
            ))}
          </div>

          {organizedData.map((track, idx) => (
            <BrandTrack
              key={`${track.brandName}-${idx}`}
              brandName={track.brandName}
              logoUrl={track.logoUrl}
              products={track.items}
              color={track.color}
              globalRange={globalRange}
              onHover={setHoveredProduct}
              activeProductId={hoveredProduct?.id || null}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default SpectrumModule;
