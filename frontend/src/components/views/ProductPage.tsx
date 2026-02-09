import { X, ArrowLeft, Share2, Heart } from "lucide-react";
import React, { useEffect, useState } from "react";
import { useNavigationStore } from "../../store/navigationStore";
import { ImageWithFallback } from "../ImageWithFallback";
import { getPrice } from "../../lib/priceFormatter";
import type { Product } from "../../types";

/**
 * PRODUCT PAGE - Screen 3 in Unified Data Pipeline v7.0
 *
 * Complete product analysis and inspection page.
 * Displays all available product information:
 * - High-res images and gallery
 * - Complete specifications
 * - Reviews and ratings
 * - Enrichment data (sources, confidence)
 * - Related products
 * - Full pricing across regions
 */
export const ProductPage = ({ productId }: { productId: string }) => {
  const { closeProductPage, goToSpectrum } = useNavigationStore();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeImageIndex, setActiveImageIndex] = useState(0);

  useEffect(() => {
    const loadProduct = async () => {
      try {
        setLoading(true);
        const { catalogLoader } = await import("../../lib/catalogLoader");
        const loaded = await catalogLoader.findProductById(productId);
        if (loaded) {
          setProduct(loaded);
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
  }, [productId]);

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
  // Ensure we don't display broken products with missing core data
  const hasName =
    product.product_name && product.product_name.trim().length > 0;
  const hasPrice = getPrice(product) !== "TBD" && getPrice(product) !== "0"; // getPrice handles formatting

  if (!hasName || !hasPrice) {
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
            ID: {product.halilit_id || product.id}
          </div>
        </div>
      </div>
    );
  }

  // Extract images
  const images = Array.isArray(product?.images)
    ? product.images
    : [(product?.image_hero || product?.image_url || "") as any].filter(
        (img) => img,
      );

  const currentImage =
    images[activeImageIndex]?.url || String(images[activeImageIndex]) || "";

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
            {/* Brand Logo - Added per v7.5 request */}
            {(product as any).brand_logo && (
              <div className="w-12 h-12 bg-white rounded-lg p-1 flex items-center justify-center overflow-hidden shrink-0">
                <img
                  src={(product as any).brand_logo}
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
                      src={(img?.url || String(img)) as string}
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
                    {getPrice(product) || "TBD"}
                  </span>
                  <span className="text-sm text-zinc-500">
                    {product?.pricing_tier && `(${product.pricing_tier})`}
                  </span>
                </div>
                {product?.in_stock !== undefined && (
                  <div className="text-sm">
                    <span
                      className={`px-2 py-1 rounded text-xs font-bold ${
                        product.in_stock
                          ? "bg-green-600/30 text-green-400"
                          : "bg-red-600/30 text-red-400"
                      }`}
                    >
                      {product.in_stock ? "In Stock" : "Out of Stock"}
                    </span>
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
                  <p className="text-zinc-500">Category</p>
                  <p className="text-white font-medium">
                    {product?.taxonomy?.canonical_category || "N/A"}
                  </p>
                </div>
                <div>
                  <p className="text-zinc-500">Subcategory</p>
                  <p className="text-white font-medium">
                    {product?.taxonomy?.canonical_subcategory || "N/A"}
                  </p>
                </div>
              </div>
            </div>

            {/* Ratings */}
            {product?.reviews?.average_rating && (
              <div className="bg-slate-900 rounded p-4 border border-slate-800">
                <h2 className="text-sm font-bold text-zinc-400 uppercase mb-3">
                  Rating
                </h2>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl font-black text-amber-400">
                      {product.reviews.average_rating.toFixed(1)}
                    </span>
                    <span className="text-xs text-zinc-500">
                      / 5 ({product.reviews.total_reviews} reviews)
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Column 3: Specifications & Details */}
          <div className="space-y-6">
            {/* Description */}
            {(product?.description_short ||
              product?.official_description ||
              product?.specifications?.short_description) && (
              <div className="bg-slate-900 rounded p-4 border border-slate-800">
                <h2 className="text-sm font-bold text-zinc-400 uppercase mb-3">
                  Overview
                </h2>
                <p className="text-sm text-zinc-300 leading-relaxed">
                  {product.description_short ||
                    product.official_description ||
                    product.specifications?.short_description}
                </p>
              </div>
            )}

            {/* Features */}
            {(product?.feature_list || product?.specifications?.features) &&
              (product.feature_list || product.specifications?.features || [])
                .length > 0 && (
                <div className="bg-slate-900 rounded p-4 border border-slate-800">
                  <h2 className="text-sm font-bold text-zinc-400 uppercase mb-3">
                    Features
                  </h2>
                  <ul className="space-y-1 text-sm text-zinc-300">
                    {(
                      product.feature_list ||
                      product.specifications?.features ||
                      []
                    )
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
            {product?.specifications &&
              Object.keys(product.specifications).length > 0 && (
                <div className="bg-slate-900 rounded p-4 border border-slate-800">
                  <h2 className="text-sm font-bold text-zinc-400 uppercase mb-3">
                    Specifications
                  </h2>
                  <div className="space-y-2 text-sm">
                    {/* Handle both unified (direct dict) and legacy (nested .specs) structures */}
                    {Object.entries(
                      product.specifications?.specs || product.specifications,
                    )
                      .filter(
                        ([key]) =>
                          key !== "specs" &&
                          key !== "features" &&
                          key !== "short_description" &&
                          key !== "long_description",
                      )
                      .slice(0, 8)
                      .map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="text-zinc-500 capitalize">
                            {key}:
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

        {/* Full Specifications Section (if there are more) */}
        {(product?.description_long ||
          product?.specifications?.long_description) && (
          <div className="bg-slate-900 rounded p-6 border border-slate-800 mt-6">
            <h2 className="text-lg font-bold text-white mb-4">
              Full Description
            </h2>
            <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
              {product.description_long ||
                product.specifications?.long_description}
            </p>
          </div>
        )}

        {/* Reviews Section */}
        {product?.reviews && (
          <div className="bg-slate-900 rounded p-6 border border-slate-800">
            <h2 className="text-lg font-bold text-white mb-4">
              Reviews & Feedback
            </h2>
            {product.reviews.pros && product.reviews.pros.length > 0 && (
              <div className="mb-4">
                <h3 className="text-sm font-bold text-green-400 uppercase mb-2">
                  Pros
                </h3>
                <ul className="space-y-1 text-sm text-zinc-300">
                  {product.reviews.pros.map((pro, idx) => (
                    <li key={idx}>✓ {pro}</li>
                  ))}
                </ul>
              </div>
            )}
            {product.reviews.cons && product.reviews.cons.length > 0 && (
              <div>
                <h3 className="text-sm font-bold text-orange-400 uppercase mb-2">
                  Cons
                </h3>
                <ul className="space-y-1 text-sm text-zinc-300">
                  {product.reviews.cons.map((con, idx) => (
                    <li key={idx}>✗ {con}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Data Provenance */}
        {product?.provenance && (
          <div className="bg-slate-900 rounded p-6 border border-slate-800">
            <h2 className="text-lg font-bold text-white mb-4">Data Sources</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-zinc-500">Sources</p>
                <div className="flex flex-wrap gap-3 mt-2 items-center">
                  {/* Halilit Source (Local Commercial) */}
                  <div
                    className="flex items-center gap-2 bg-white/5 pr-3 rounded-lg overflow-hidden border border-white/10"
                    title="Halilit (Commercial Data)"
                  >
                    <div className="bg-blue-600 h-8 w-8 flex items-center justify-center font-bold text-white text-xs">
                      H
                    </div>
                    <span className="text-zinc-300 font-medium text-xs">
                      Halilit.com
                    </span>
                  </div>

                  {/* Brand Source (Official) */}
                  {(product as any).brand_logo && (
                    <div
                      className="flex items-center gap-2 bg-white/5 pr-3 rounded-lg overflow-hidden border border-white/10"
                      title="Official Brand Data"
                    >
                      <div className="bg-white h-8 w-8 p-1 flex items-center justify-center">
                        <img
                          src={(product as any).brand_logo}
                          alt="Brand"
                          className="max-w-full max-h-full object-contain"
                        />
                      </div>
                      <span className="text-zinc-300 font-medium text-xs">
                        Official
                      </span>
                    </div>
                  )}

                  {/* Other sources */}
                  {product.provenance.sources
                    ?.filter((s) => s !== "halilit" && !s.includes("official"))
                    .map((source, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 bg-slate-800 text-zinc-400 rounded text-xs border border-slate-700"
                      >
                        {source}
                      </span>
                    ))}
                </div>
              </div>
              <div>
                <p className="text-zinc-500">Verification</p>
                <p className="text-white font-medium mt-2 uppercase text-xs">
                  {product.provenance.verification_status}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer Actions */}
      <div className="px-6 py-4 border-t border-slate-800 bg-slate-900 flex gap-3">
        <button
          onClick={() => {
            if (product?.taxonomy?.canonical_subcategory) {
              goToSpectrum(
                product.taxonomy.canonical_category || "",
                product.taxonomy.canonical_subcategory,
                [],
              );
            }
          }}
          className="flex-1 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded transition font-medium"
        >
          Back to Spectrum
        </button>
        <button
          onClick={() => {
            if (product?.halilit_url) {
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
