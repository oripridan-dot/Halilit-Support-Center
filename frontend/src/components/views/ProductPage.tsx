import {
  X,
  ArrowLeft,
  Share2,
  Heart,
  ExternalLink,
  Sparkles,
  Users,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import { useNavigationStore } from "../../store/navigationStore";
import { ImageWithFallback } from "../ImageWithFallback";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import type { ConductorProduct } from "../../hooks/useConductorCatalog";
import { getBrandLogoUrl } from "../../lib/brandLogoHelper";

/**
 * PRODUCT PAGE - Screen 3 in Unified Data Pipeline v10
 *
 * Complete product analysis and inspection page.
 * Uses flat ConductorProduct shape — no fallback chains or (as any) casts.
 */
export const ProductPage = ({ productId }: { productId: string }) => {
  const { closeProductPage, goToSpectrum } = useNavigationStore();
  const { products: conductorProducts } = useConductorCatalog();
  const [product, setProduct] = useState<ConductorProduct | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeImageIndex, setActiveImageIndex] = useState(0);

  useEffect(() => {
    const loadProduct = async () => {
      try {
        setLoading(true);

        // Find product in conductor catalog (pre-loaded via React Query)
        const fromConductor = conductorProducts.find((p) => p.id === productId);
        if (fromConductor) {
          setProduct(fromConductor);
          return;
        }

        // Fallback to static JSON
        const { catalogLoader } = await import("../../lib/catalogLoader");
        const loaded = await catalogLoader.findProductById(productId);
        if (loaded) {
          setProduct(loaded as unknown as ConductorProduct);
        }
      } catch (err) {
        console.error("Failed to load product:", err);
      } finally {
        setLoading(false);
      }
    };

    if (productId) {
      loadProduct();
    }
  }, [productId, conductorProducts]);

  if (!productId) return null;

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-slate-950 rounded-lg">
        <div className="flex flex-col items-center gap-3">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
          <p className="text-zinc-400">Loading product...</p>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-slate-950 rounded-lg p-6">
        <div className="text-center">
          <p className="text-red-400 font-medium">Product not found</p>
          <button
            onClick={closeProductPage}
            className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // --- HEALTH CHECK ---
  const hasName = product.name && product.name.trim().length > 0;

  if (!hasName) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-slate-950 rounded-lg p-6 font-mono">
        <div className="text-center max-w-md border border-amber-900/50 bg-amber-950/20 p-8 rounded-xl">
          <div className="text-amber-500 mb-4 flex justify-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <p className="text-amber-400/90 font-bold mb-2">
            PRODUCT DATA INCOMPLETE
          </p>
          <p className="text-zinc-500 text-sm mb-6">
            This item is currently flagged for maintenance. Core data
            (Price/Name) is missing or being updated.
          </p>
          <div className="flex gap-2 justify-center">
            <button
              onClick={closeProductPage}
              className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded text-xs transition"
            >
              Close View
            </button>
          </div>
          <div className="mt-8 pt-4 border-t border-white/5 text-[10px] text-zinc-700 font-mono">
            ID: {product.id}
          </div>
        </div>
      </div>
    );
  }

  // Extract images — v10 provides flat image_url and image_gallery
  const images =
    product.image_gallery && product.image_gallery.length > 0
      ? product.image_gallery.map((url) => ({ url }))
      : product.image_url
        ? [{ url: product.image_url }]
        : [];

  const currentImage = images[activeImageIndex]?.url || "";

  return (
    <div className="w-full h-full bg-slate-950 rounded-lg overflow-hidden flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900">
        <div className="flex items-center gap-4">
          <button
            onClick={closeProductPage}
            className="p-2 hover:bg-slate-800 rounded transition text-zinc-400 hover:text-white"
            title="Close"
          >
            <ArrowLeft size={20} />
          </button>
          <div className="flex items-center gap-4">
            {/* Brand Logo */}
            {product.brand_logo && (
              <div className="w-12 h-12 bg-white rounded-lg p-1 flex items-center justify-center overflow-hidden shrink-0">
                <img
                  src={product.brand_logo}
                  alt={product.brand}
                  className="max-w-full max-h-full object-contain"
                  onError={(e) => (e.currentTarget.style.display = "none")}
                />
              </div>
            )}
            <div>
              <p className="text-xs text-blue-400 font-mono">{product.brand}</p>
              <h1 className="text-xl font-bold text-white truncate">
                {product.name}
              </h1>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            className="p-2 hover:bg-slate-800 rounded transition text-zinc-400 hover:text-red-500"
            title="Favorite"
          >
            <Heart size={20} />
          </button>
          <button
            className="p-2 hover:bg-slate-800 rounded transition text-zinc-400 hover:text-white"
            title="Share"
          >
            <Share2 size={20} />
          </button>
          <button
            onClick={closeProductPage}
            className="p-2 hover:bg-slate-800 rounded transition text-zinc-400 hover:text-white"
            title="Close"
          >
            <X size={20} />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <div className="grid grid-cols-3 gap-6">
          {/* Column 1: Images */}
          <div className="space-y-4">
            {/* Hero Image */}
            <div className="relative h-64 bg-slate-800 rounded overflow-hidden border border-slate-700">
              <ImageWithFallback
                src={currentImage}
                alt={product.name || "Product"}
                className="w-full h-full object-cover"
              />
            </div>

            {/* Thumbnail Gallery */}
            {images.length > 1 && (
              <div className="grid grid-cols-3 gap-2">
                {images.slice(0, 6).map((img, idx) => (
                  <button
                    key={idx}
                    onClick={() => setActiveImageIndex(idx)}
                    className={`h-16 rounded overflow-hidden border-2 transition ${
                      idx === activeImageIndex
                        ? "border-blue-500"
                        : "border-slate-700 hover:border-slate-600"
                    }`}
                  >
                    <ImageWithFallback
                      src={img.url}
                      alt={`Gallery ${idx + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Column 2: Core Details */}
          <div className="space-y-6">
            {/* Pricing */}
            <div className="bg-slate-900 rounded p-4 border border-slate-800">
              <h2 className="text-sm font-bold text-zinc-400 uppercase mb-3">
                Pricing
              </h2>
              <div className="space-y-2">
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-black text-green-400">
                    {product.price > 0
                      ? `₪${product.price.toLocaleString("he-IL")}`
                      : "Price on request"}
                  </span>
                  <span className="text-sm text-zinc-500">
                    {product.tier && `(${product.tier})`}
                  </span>
                </div>
                {product.price_eilat > 0 && (
                  <div className="text-sm text-zinc-400">
                    Eilat price: ₪{product.price_eilat.toLocaleString("he-IL")}
                  </div>
                )}
              </div>
            </div>

            {/* Brand & Category */}
            <div className="bg-slate-900 rounded p-4 border border-slate-800">
              <h2 className="text-sm font-bold text-zinc-400 uppercase mb-3">
                Classification
              </h2>
              <div className="space-y-2 text-sm">
                <div>
                  <p className="text-zinc-500">Galaxy</p>
                  <p className="text-white font-medium capitalize">
                    {product.galaxy_id?.replace(/-/g, " ") || "N/A"}
                  </p>
                </div>
                <div>
                  <p className="text-zinc-500">Spectrum</p>
                  <p className="text-white font-medium capitalize">
                    {product.spectrum_id?.replace(/-/g, " ") || "N/A"}
                  </p>
                </div>
              </div>
            </div>

            {/* Ratings */}
            {product.rating > 0 && (
              <div className="bg-slate-900 rounded p-4 border border-slate-800">
                <h2 className="text-sm font-bold text-zinc-400 uppercase mb-3">
                  Rating
                </h2>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl font-black text-amber-400">
                      {product.rating.toFixed(1)}
                    </span>
                    <span className="text-xs text-zinc-500">
                      / 5 ({product.review_count} reviews)
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Column 3: Specifications & Details */}
          <div className="space-y-6">
            {/* Description */}
            {product.description && (
              <div className="bg-slate-900 rounded p-4 border border-slate-800">
                <h2 className="text-sm font-bold text-zinc-400 uppercase mb-3">
                  Overview
                </h2>
                <p className="text-sm text-zinc-300 leading-relaxed">
                  {product.description_short || product.description}
                </p>
              </div>
            )}

            {/* Features */}
            {product.features && product.features.length > 0 && (
              <div className="bg-slate-900 rounded p-4 border border-slate-800">
                <h2 className="text-sm font-bold text-zinc-400 uppercase mb-3">
                  Features
                </h2>
                <ul className="space-y-1 text-sm text-zinc-300">
                  {product.features
                    .slice(0, 5)
                    .map((feature: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-blue-400 font-bold mt-0.5">
                          ▸
                        </span>
                        <span>{feature}</span>
                      </li>
                    ))}
                </ul>
              </div>
            )}

            {/* Specs */}
            {product.specs && Object.keys(product.specs).length > 0 && (
              <div className="bg-slate-900 rounded p-4 border border-slate-800">
                <h2 className="text-sm font-bold text-zinc-400 uppercase mb-3">
                  Specifications
                </h2>
                <div className="space-y-2 text-sm">
                  {Object.entries(product.specs)
                    .slice(0, 8)
                    .map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="text-zinc-500 capitalize">
                          {key.replace(/_/g, " ")}:
                        </span>
                        <span className="text-white font-medium text-right ml-4">
                          {typeof value === "object"
                            ? JSON.stringify(value)
                            : String(value)}
                        </span>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Full Description Section */}
        {product.description && product.description.length > 200 && (
          <div className="bg-slate-900 rounded p-6 border border-slate-800 mt-6">
            <h2 className="text-lg font-bold text-white mb-4">
              Full Description
            </h2>
            <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
              {product.description}
            </p>
          </div>
        )}

        {/* Reviews Section */}
        {(product.pros.length > 0 || product.cons.length > 0) && (
          <div className="bg-slate-900 rounded p-6 border border-slate-800">
            <h2 className="text-lg font-bold text-white mb-4">
              Reviews & Feedback
            </h2>
            {product.pros.length > 0 && (
              <div className="mb-4">
                <h3 className="text-sm font-bold text-green-400 uppercase mb-2">
                  Pros
                </h3>
                <ul className="space-y-1 text-sm text-zinc-300">
                  {product.pros.map((pro, idx) => (
                    <li key={idx}>✓ {pro}</li>
                  ))}
                </ul>
              </div>
            )}
            {product.cons.length > 0 && (
              <div>
                <h3 className="text-sm font-bold text-orange-400 uppercase mb-2">
                  Cons
                </h3>
                <ul className="space-y-1 text-sm text-zinc-300">
                  {product.cons.map((con, idx) => (
                    <li key={idx}>✗ {con}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Data Provenance — Three Pillars */}
        <div className="bg-slate-900 rounded p-6 border border-slate-800">
          <h2 className="text-lg font-bold text-white mb-4">Data Sources</h2>
          <div className="grid grid-cols-3 gap-4">
            {/* Pillar 1: Halilit */}
            <div
              className={`rounded-lg border p-4 ${product.sources?.includes("halilit") ? "border-blue-500/40 bg-blue-950/20" : "border-slate-700/40 bg-slate-800/20 opacity-40"}`}
            >
              <div className="flex items-center gap-2 mb-3">
                <img
                  src="/assets/logos/halilit_logo.svg"
                  alt="Halilit"
                  className="h-6 rounded"
                  onError={(e) => {
                    e.currentTarget.style.display = "none";
                  }}
                />
                <span className="text-xs font-bold text-blue-400 uppercase">
                  Halilit
                </span>
              </div>
              <p className="text-[10px] text-zinc-500 leading-relaxed">
                Prices, SKU, product catalog, spectrum classification
              </p>
              {product.data_trust && (
                <div className="mt-2 space-y-1">
                  {product.data_trust.price_source === "halilit" && (
                    <span className="block text-[10px] text-blue-400/70">
                      ✓ Price
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* Pillar 2: Official Brand */}
            <div
              className={`rounded-lg border p-4 ${product.sources?.includes("official") ? "border-emerald-500/40 bg-emerald-950/20" : "border-slate-700/40 bg-slate-800/20 opacity-40"}`}
            >
              <div className="flex items-center gap-2 mb-3">
                {(() => {
                  const logoUrl = getBrandLogoUrl(product.brand);
                  return logoUrl ? (
                    <div className="h-6 w-6 bg-white rounded p-0.5 flex items-center justify-center">
                      <img
                        src={logoUrl}
                        alt={product.brand}
                        className="max-w-full max-h-full object-contain"
                      />
                    </div>
                  ) : null;
                })()}
                <span className="text-xs font-bold text-emerald-400 uppercase">
                  Official
                </span>
              </div>
              <p className="text-[10px] text-zinc-500 leading-relaxed">
                Specs, descriptions, images from {product.brand}
              </p>
              {product.data_trust && (
                <div className="mt-2 space-y-1">
                  {product.data_trust.specs_source === "official" && (
                    <span className="block text-[10px] text-emerald-400/70">
                      ✓ Specs
                    </span>
                  )}
                  {product.data_trust.description_source === "official" && (
                    <span className="block text-[10px] text-emerald-400/70">
                      ✓ Description
                    </span>
                  )}
                  {product.data_trust.image_source === "official" && (
                    <span className="block text-[10px] text-emerald-400/70">
                      ✓ Images
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* Pillar 3: Contextual */}
            <div
              className={`rounded-lg border p-4 ${product.sources?.includes("contextual") ? "border-amber-500/40 bg-amber-950/20" : "border-slate-700/40 bg-slate-800/20 opacity-40"}`}
            >
              <div className="flex items-center gap-2 mb-3">
                <Sparkles size={14} className="text-amber-400" />
                <span className="text-xs font-bold text-amber-400 uppercase">
                  Contextual
                </span>
              </div>
              <p className="text-[10px] text-zinc-500 leading-relaxed">
                Reviews, community feedback, audience insights
              </p>
              {product.data_trust && (
                <div className="mt-2 space-y-1">
                  {product.data_trust.review_source === "contextual" && (
                    <span className="block text-[10px] text-amber-400/70">
                      ✓ Reviews
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Audiences & FAQ (contextual data) */}
        {((product.audiences && product.audiences.length > 0) ||
          (product.faq && product.faq.length > 0)) && (
          <div className="bg-slate-900 rounded p-6 border border-slate-800">
            <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <Users size={18} className="text-amber-400" />
              Community & Context
            </h2>
            <div className="grid grid-cols-2 gap-6">
              {product.audiences && product.audiences.length > 0 && (
                <div>
                  <h3 className="text-sm font-bold text-amber-400 uppercase mb-2">
                    Target Audiences
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {product.audiences.map((audience: string, idx: number) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-amber-500/10 text-amber-300 rounded text-xs border border-amber-500/20"
                      >
                        {audience}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {product.faq && product.faq.length > 0 && (
                <div>
                  <h3 className="text-sm font-bold text-zinc-400 uppercase mb-2">
                    FAQ
                  </h3>
                  <div className="space-y-2">
                    {product.faq
                      .slice(0, 3)
                      .map((item: { q: string; a: string }, idx: number) => (
                        <div key={idx} className="text-xs">
                          <p className="text-zinc-300 font-medium">{item.q}</p>
                          <p className="text-zinc-500 mt-0.5">{item.a}</p>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer Actions */}
      <div className="px-6 py-4 border-t border-slate-800 bg-slate-900 flex gap-3">
        <button
          onClick={() => {
            if (product.galaxy_id) {
              goToSpectrum(product.galaxy_id, product.spectrum_id, []);
            }
          }}
          className="flex-1 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded transition font-medium"
        >
          Back to Spectrum
        </button>
        {product.official_url && (
          <button
            onClick={() => window.open(product.official_url!, "_blank")}
            className="flex-1 px-4 py-2 bg-emerald-700 hover:bg-emerald-600 text-white rounded transition font-medium flex items-center justify-center gap-2"
          >
            <ExternalLink size={16} />
            View on {product.brand}
          </button>
        )}
        <button
          onClick={() => {
            if (product.halilit_url) {
              window.open(product.halilit_url, "_blank");
            }
          }}
          className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition font-medium"
        >
          View on Halilit
        </button>
      </div>
    </div>
  );
};
