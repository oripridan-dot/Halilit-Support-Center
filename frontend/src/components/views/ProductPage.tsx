import {
  X,
  ArrowLeft,
  Share2,
  Heart,
  ExternalLink,
  Sparkles,
  Users,
  Layers,
  Package,
  Link2,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import { useNavigationStore } from "../../store/navigationStore";
import { ImageWithFallback } from "../ImageWithFallback";
import {
  useConductorCatalog,
  useProductVariants,
  useProductRelationships,
} from "../../hooks/useConductorCatalog";
import type { ConductorProduct } from "../../hooks/useConductorCatalog";
import { getBrandLogoUrl } from "../../lib/brandLogoHelper";

/**
 * PRODUCT PAGE - Screen 3 in Unified Data Pipeline v10
 *
 * Complete product analysis and inspection page.
 * Uses flat ConductorProduct shape — no fallback chains or (as any) casts.
 */
export const ProductPage = ({ productId }: { productId: string }) => {
  const { closeProductPage, goToSpectrum, openProductPage } =
    useNavigationStore();
  const { products: conductorProducts } = useConductorCatalog();
  const [product, setProduct] = useState<ConductorProduct | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeImageIndex, setActiveImageIndex] = useState(0);
  const { variants } = useProductVariants(productId);
  const { accessories, compatible, alternatives } =
    useProductRelationships(productId);

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
        if (import.meta.env.DEV) console.error("Failed to load product:", err);
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
      <div className="w-full h-full bg-slate-950 rounded-lg overflow-hidden flex flex-col animate-pulse">
        {/* Header skeleton */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-slate-800" />
            <div className="space-y-2">
              <div className="h-3 w-16 bg-slate-800 rounded" />
              <div className="h-5 w-48 bg-slate-800 rounded" />
            </div>
          </div>
          <div className="flex gap-2">
            <div className="w-9 h-9 rounded-lg bg-slate-800" />
            <div className="w-9 h-9 rounded-lg bg-slate-800" />
          </div>
        </div>
        {/* Content skeleton */}
        <div className="flex-1 p-6">
          <div className="grid grid-cols-3 gap-6">
            <div className="h-64 rounded-lg bg-slate-800" />
            <div className="space-y-4">
              <div className="h-24 rounded-lg bg-slate-800" />
              <div className="h-24 rounded-lg bg-slate-800" />
              <div className="h-24 rounded-lg bg-slate-800" />
            </div>
            <div className="space-y-4">
              <div className="h-32 rounded-lg bg-slate-800" />
              <div className="h-32 rounded-lg bg-slate-800" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-slate-950 rounded-lg p-6">
        <div className="text-center max-w-sm">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-zinc-800/30 flex items-center justify-center">
            <svg
              className="w-7 h-7 text-zinc-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
          <h3 className="text-zinc-300 font-semibold text-lg mb-2">
            Product not found
          </h3>
          <p className="text-zinc-500 text-sm mb-6">
            The product you're looking for may have been removed or is not
            available.
          </p>
          <button
            onClick={closeProductPage}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-all duration-200 font-medium text-sm shadow-lg shadow-blue-500/20"
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
    <div className="w-full h-full bg-slate-950 rounded-xl overflow-hidden flex flex-col shadow-2xl">
      {/* Header — refined */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800/60 bg-gradient-to-r from-slate-900 to-slate-900/80">
        <div className="flex items-center gap-4">
          <button
            onClick={closeProductPage}
            className="p-2 hover:bg-slate-800 rounded-lg transition-all duration-200 text-zinc-400 hover:text-white"
            title="Close"
          >
            <ArrowLeft size={20} />
          </button>
          <div className="h-6 w-px bg-slate-700/50" />
          <div className="flex items-center gap-4">
            {/* Brand Logo */}
            {product.brand_logo && (
              <div className="w-11 h-11 bg-white rounded-lg p-1.5 flex items-center justify-center overflow-hidden shrink-0 shadow-md">
                <img
                  src={product.brand_logo}
                  alt={product.brand}
                  className="max-w-full max-h-full object-contain"
                  onError={(e) => (e.currentTarget.style.display = "none")}
                />
              </div>
            )}
            <div>
              <p className="text-[11px] text-blue-400 font-semibold uppercase tracking-wider">
                {product.brand}
              </p>
              <h1 className="text-lg font-bold text-white truncate leading-tight">
                {product.name}
              </h1>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-1.5">
          <button
            className="p-2 hover:bg-slate-800 rounded-lg transition-all duration-200 text-zinc-500 hover:text-red-400"
            title="Favorite"
          >
            <Heart size={18} />
          </button>
          <button
            className="p-2 hover:bg-slate-800 rounded-lg transition-all duration-200 text-zinc-500 hover:text-white"
            title="Share"
          >
            <Share2 size={18} />
          </button>
          <div className="h-5 w-px bg-slate-700/50 mx-1" />
          <button
            onClick={closeProductPage}
            className="p-2 hover:bg-slate-800 rounded-lg transition-all duration-200 text-zinc-500 hover:text-white"
            title="Close"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Variant Switcher Strip */}
      {variants.length > 0 && (
        <div className="px-6 py-2.5 border-b border-slate-800/60 bg-slate-900/50 flex items-center gap-3">
          <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold shrink-0 flex items-center gap-1.5">
            <Layers size={12} className="text-blue-400" />
            Variants
          </span>
          <div className="flex gap-1 overflow-x-auto custom-scrollbar">
            {/* Current product tab */}
            <button className="px-3 py-1.5 rounded-md text-xs font-semibold bg-blue-600 text-white shadow-lg shadow-blue-500/20 shrink-0">
              {product.variant_key ||
                product.name?.split(" ").pop() ||
                "Current"}
            </button>
            {/* Sibling variant tabs */}
            {variants.map((v) => (
              <button
                key={v.id}
                onClick={() => openProductPage(v.id)}
                className="px-3 py-1.5 rounded-md text-xs font-medium bg-slate-800/60 text-zinc-400 hover:bg-slate-700 hover:text-white transition-all duration-200 shrink-0 border border-slate-700/40"
              >
                {v.variant_key || v.name?.split(" ").pop() || v.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <div className="grid grid-cols-3 gap-6">
          {/* Column 1: Images — improved gallery */}
          <div className="space-y-3">
            {/* Hero Image */}
            <div className="relative aspect-square bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl overflow-hidden border border-slate-700/40 group">
              <ImageWithFallback
                src={currentImage}
                alt={product.name || "Product"}
                className="w-full h-full object-contain p-6"
              />
              {/* Image counter badge */}
              {images.length > 1 && (
                <div className="absolute bottom-3 right-3 px-2 py-1 bg-black/70 backdrop-blur-sm rounded-md text-[10px] text-zinc-300 font-mono">
                  {activeImageIndex + 1} / {images.length}
                </div>
              )}
            </div>

            {/* Thumbnail Gallery */}
            {images.length > 1 && (
              <div className="flex gap-2 overflow-x-auto pb-1 custom-scrollbar">
                {images.slice(0, 8).map((img, idx) => (
                  <button
                    key={idx}
                    onClick={() => setActiveImageIndex(idx)}
                    className={`shrink-0 w-16 h-16 rounded-lg overflow-hidden border-2 transition-all duration-200 ${
                      idx === activeImageIndex
                        ? "border-blue-500 shadow-lg shadow-blue-500/20 opacity-100"
                        : "border-slate-700/50 hover:border-slate-500/50 opacity-60 hover:opacity-100"
                    }`}
                  >
                    <ImageWithFallback
                      src={img.url}
                      alt={`Gallery ${idx + 1}`}
                      className="w-full h-full object-contain p-1"
                    />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Column 2: Core Details */}
          <div className="space-y-6">
            {/* Pricing — improved hierarchy */}
            <div className="bg-gradient-to-br from-slate-900 to-slate-900/80 rounded-xl p-5 border border-slate-800/60">
              <h2 className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
                Pricing
              </h2>
              <div className="space-y-3">
                <div className="flex items-baseline gap-3">
                  <span className="text-3xl font-black text-white tracking-tight">
                    {product.price > 0
                      ? `₪${product.price.toLocaleString("he-IL")}`
                      : "Price on request"}
                  </span>
                  {product.tier && (
                    <span
                      className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                        product.tier === "flagship"
                          ? "bg-blue-500/15 text-blue-400 border border-blue-500/20"
                          : product.tier === "pro"
                            ? "bg-amber-500/15 text-amber-400 border border-amber-500/20"
                            : product.tier === "mid"
                              ? "bg-zinc-500/15 text-zinc-400 border border-zinc-500/20"
                              : "bg-zinc-800/50 text-zinc-500 border border-zinc-700/30"
                      }`}
                    >
                      {product.tier}
                    </span>
                  )}
                </div>
                {product.price_eilat > 0 && (
                  <div className="flex items-center gap-2 text-sm text-zinc-400 bg-slate-800/30 rounded-lg px-3 py-2">
                    <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold">
                      Eilat
                    </span>
                    <span className="font-semibold text-zinc-300">
                      ₪{product.price_eilat.toLocaleString("he-IL")}
                    </span>
                    {product.price > 0 && product.price_eilat > 0 && (
                      <span className="text-emerald-400 text-xs font-semibold ml-auto">
                        Save{" "}
                        {Math.round(
                          (1 - product.price_eilat / product.price) * 100,
                        )}
                        %
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Brand & Category — cleaner design */}
            <div className="bg-slate-900/80 rounded-xl p-5 border border-slate-800/60">
              <h2 className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                Classification
              </h2>
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-slate-800/30 rounded-lg p-3">
                  <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold mb-1">
                    Galaxy
                  </p>
                  <p className="text-sm text-white font-medium capitalize">
                    {product.galaxy_id?.replace(/-/g, " ") || "N/A"}
                  </p>
                </div>
                <div className="bg-slate-800/30 rounded-lg p-3">
                  <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold mb-1">
                    Spectrum
                  </p>
                  <p className="text-sm text-white font-medium capitalize">
                    {product.spectrum_id?.replace(/-/g, " ") || "N/A"}
                  </p>
                </div>
              </div>
            </div>

            {/* Data Quality Score — improved */}
            <div className="bg-slate-900/80 rounded-xl p-5 border border-slate-800/60">
              <h2 className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                Data Quality
              </h2>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="relative w-12 h-12">
                    <svg className="w-12 h-12 -rotate-90" viewBox="0 0 36 36">
                      <circle
                        cx="18"
                        cy="18"
                        r="15.9"
                        fill="none"
                        stroke="#1e293b"
                        strokeWidth="3"
                      />
                      <circle
                        cx="18"
                        cy="18"
                        r="15.9"
                        fill="none"
                        strokeWidth="3"
                        strokeDasharray={`${product.quality_score || 0} ${100 - (product.quality_score || 0)}`}
                        strokeLinecap="round"
                        className={
                          (product.quality_score || 0) >= 90
                            ? "stroke-emerald-400"
                            : (product.quality_score || 0) >= 70
                              ? "stroke-green-400"
                              : (product.quality_score || 0) >= 40
                                ? "stroke-amber-400"
                                : "stroke-red-400"
                        }
                      />
                    </svg>
                    <span className="absolute inset-0 flex items-center justify-center text-xs font-black text-white">
                      {product.quality_score || 0}
                    </span>
                  </div>
                  <div>
                    <span
                      className={`text-xs font-bold uppercase tracking-wider ${
                        product.data_status === "COMPLETE"
                          ? "text-emerald-400"
                          : product.data_status === "GOOD"
                            ? "text-green-400"
                            : product.data_status === "PARTIAL"
                              ? "text-amber-400"
                              : "text-red-400"
                      }`}
                    >
                      {product.data_status || "UNKNOWN"}
                    </span>
                    {product.data_missing &&
                      product.data_missing.length > 0 && (
                        <p className="text-[10px] text-zinc-500 mt-0.5">
                          Missing: {product.data_missing.join(", ")}
                        </p>
                      )}
                  </div>
                </div>
                {/* Mini field coverage bar */}
                <div className="flex gap-0.5">
                  {[
                    "name",
                    "price",
                    "image",
                    "description",
                    "specs",
                    "features",
                    "rating",
                    "classification",
                    "sources",
                  ].map((field) => {
                    const missing = product.data_missing || [];
                    const ok = !missing.includes(field);
                    return (
                      <div
                        key={field}
                        title={`${field}: ${ok ? "OK" : "missing"}`}
                        className={`h-1.5 flex-1 rounded-full transition ${ok ? "bg-emerald-500/70" : "bg-zinc-700"}`}
                      />
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Ratings — improved */}
            {product.rating > 0 && (
              <div className="bg-slate-900/80 rounded-xl p-5 border border-slate-800/60">
                <h2 className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                  Rating
                </h2>
                <div className="flex items-center gap-4">
                  <span className="text-3xl font-black text-amber-400">
                    {product.rating.toFixed(1)}
                  </span>
                  <div className="flex-1">
                    <div className="flex gap-0.5 mb-1">
                      {[...Array(5)].map((_, i) => (
                        <svg
                          key={i}
                          className={`w-4 h-4 ${i < Math.floor(product.rating) ? "text-amber-400" : "text-zinc-700"}`}
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                      ))}
                    </div>
                    <p className="text-xs text-zinc-500">
                      Based on {product.review_count} review
                      {product.review_count !== 1 ? "s" : ""}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Column 3: Specifications & Details — improved */}
          <div className="space-y-4">
            {/* Description */}
            {product.description && (
              <div className="bg-slate-900/80 rounded-xl p-5 border border-slate-800/60">
                <h2 className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-violet-400" />
                  Overview
                </h2>
                <p className="text-sm text-zinc-300 leading-relaxed">
                  {product.description_short || product.description}
                </p>
              </div>
            )}

            {/* Features */}
            {product.features && product.features.length > 0 && (
              <div className="bg-slate-900/80 rounded-xl p-5 border border-slate-800/60">
                <h2 className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                  Key Features
                </h2>
                <ul className="space-y-2 text-sm text-zinc-300">
                  {product.features
                    .slice(0, 6)
                    .map((feature: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2.5">
                        <span className="mt-1.5 w-1 h-1 rounded-full bg-blue-400/70 shrink-0" />
                        <span className="leading-relaxed">{feature}</span>
                      </li>
                    ))}
                </ul>
              </div>
            )}

            {/* Specs — improved table layout */}
            {product.specs && Object.keys(product.specs).length > 0 && (
              <div className="bg-slate-900/80 rounded-xl p-5 border border-slate-800/60">
                <h2 className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  Specifications
                </h2>
                <div className="space-y-0.5 text-sm">
                  {Object.entries(product.specs)
                    .slice(0, 10)
                    .map(([key, value], idx) => (
                      <div
                        key={key}
                        className={`flex justify-between py-2 px-2 rounded ${idx % 2 === 0 ? "bg-slate-800/20" : ""}`}
                      >
                        <span className="text-zinc-500 capitalize text-xs">
                          {key.replace(/_/g, " ")}
                        </span>
                        <span className="text-white font-medium text-right ml-4 text-xs">
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

        {/* Full Description Section — improved */}
        {product.description && product.description.length > 200 && (
          <div className="bg-slate-900/80 rounded-xl p-6 border border-slate-800/60 mt-4">
            <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-violet-400" />
              Full Description
            </h2>
            <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
              {product.description}
            </p>
          </div>
        )}

        {/* Reviews Section — improved */}
        {(product.pros.length > 0 || product.cons.length > 0) && (
          <div className="bg-slate-900/80 rounded-xl p-6 border border-slate-800/60">
            <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
              Reviews & Feedback
            </h2>
            <div className="grid grid-cols-2 gap-4">
              {product.pros.length > 0 && (
                <div className="bg-emerald-950/20 border border-emerald-500/20 rounded-lg p-4">
                  <h3 className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider mb-3">
                    Pros
                  </h3>
                  <ul className="space-y-2 text-sm text-zinc-300">
                    {product.pros.map((pro, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-emerald-400 mt-0.5 shrink-0">
                          ✓
                        </span>
                        <span>{pro}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {product.cons.length > 0 && (
                <div className="bg-orange-950/20 border border-orange-500/20 rounded-lg p-4">
                  <h3 className="text-[11px] font-bold text-orange-400 uppercase tracking-wider mb-3">
                    Cons
                  </h3>
                  <ul className="space-y-2 text-sm text-zinc-300">
                    {product.cons.map((con, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-orange-400 mt-0.5 shrink-0">
                          ✗
                        </span>
                        <span>{con}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Data Provenance — Three Pillars — improved */}
        <div className="bg-slate-900/80 rounded-xl p-6 border border-slate-800/60">
          <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
            Data Sources
            <span className="text-[10px] text-zinc-600 font-normal ml-2 uppercase tracking-wider">
              Three Source Rules
            </span>
          </h2>
          <div className="grid grid-cols-3 gap-3">
            {/* Pillar 1: Halilit */}
            <div
              className={`rounded-xl border p-4 transition-all duration-200 ${product.sources?.includes("halilit") ? "border-blue-500/30 bg-blue-950/15 shadow-lg shadow-blue-500/5" : "border-slate-700/30 bg-slate-800/10 opacity-40"}`}
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
                  {product.data_trust.price_source === "estimated" && (
                    <span className="block text-[10px] text-amber-400/70">
                      ~ Price (estimated)
                    </span>
                  )}
                </div>
              )}
            </div>

            {/* Pillar 2: Official Brand */}
            <div
              className={`rounded-xl border p-4 transition-all duration-200 ${product.sources?.includes("official") ? "border-emerald-500/30 bg-emerald-950/15 shadow-lg shadow-emerald-500/5" : "border-slate-700/30 bg-slate-800/10 opacity-40"}`}
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
                  {product.data_trust.description_source === "synthesized" && (
                    <span className="block text-[10px] text-amber-400/70">
                      ~ Description (auto)
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
              className={`rounded-xl border p-4 transition-all duration-200 ${product.sources?.includes("contextual") ? "border-amber-500/30 bg-amber-950/15 shadow-lg shadow-amber-500/5" : "border-slate-700/30 bg-slate-800/10 opacity-40"}`}
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

        {/* Audiences & FAQ (contextual data) — improved */}
        {((product.audiences && product.audiences.length > 0) ||
          (product.faq && product.faq.length > 0)) && (
          <div className="bg-slate-900/80 rounded-xl p-6 border border-slate-800/60">
            <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <Users size={16} className="text-amber-400" />
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
                      .map(
                        (
                          item: { question: string; answer: string },
                          idx: number,
                        ) => (
                          <div key={idx} className="text-xs">
                            <p className="text-zinc-300 font-medium">
                              {item.question}
                            </p>
                            <p className="text-zinc-500 mt-0.5">
                              {item.answer}
                            </p>
                          </div>
                        ),
                      )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Compatible Accessories */}
        {accessories.length > 0 && (
          <div className="bg-slate-900/80 rounded-xl p-6 border border-slate-800/60">
            <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <Package size={16} className="text-emerald-400" />
              Compatible Accessories
              <span className="ml-auto text-[10px] text-zinc-500 font-normal">
                {accessories.length} item{accessories.length !== 1 ? "s" : ""}
              </span>
            </h2>
            <div className="grid grid-cols-4 gap-3">
              {accessories.slice(0, 8).map((acc) => (
                <button
                  key={acc.id}
                  onClick={() => openProductPage(acc.id)}
                  className="group bg-slate-800/40 hover:bg-slate-800/70 border border-slate-700/40 hover:border-emerald-500/30 rounded-xl p-3 transition-all duration-200 text-left"
                >
                  <div className="aspect-square bg-slate-900/60 rounded-lg overflow-hidden mb-2">
                    <ImageWithFallback
                      src={acc.image_url || ""}
                      alt={acc.name || "Accessory"}
                      className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-200"
                    />
                  </div>
                  <p className="text-xs text-white font-medium truncate">
                    {acc.name}
                  </p>
                  {acc.price > 0 && (
                    <p className="text-[10px] text-emerald-400 font-semibold mt-0.5">
                      ₪{acc.price.toLocaleString("he-IL")}
                    </p>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Also in this Series (Variant siblings) */}
        {variants.length > 0 && (
          <div className="bg-slate-900/80 rounded-xl p-6 border border-slate-800/60">
            <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <Layers size={16} className="text-blue-400" />
              Also in this Series
              <span className="ml-auto text-[10px] text-zinc-500 font-normal">
                {variants.length} variant{variants.length !== 1 ? "s" : ""}
              </span>
            </h2>
            <div className="flex gap-3 overflow-x-auto pb-2 custom-scrollbar">
              {variants.map((v) => (
                <button
                  key={v.id}
                  onClick={() => openProductPage(v.id)}
                  className="group shrink-0 w-44 bg-slate-800/40 hover:bg-slate-800/70 border border-slate-700/40 hover:border-blue-500/30 rounded-xl p-3 transition-all duration-200 text-left"
                >
                  <div className="aspect-square bg-slate-900/60 rounded-lg overflow-hidden mb-2">
                    <ImageWithFallback
                      src={v.image_url || ""}
                      alt={v.name || "Variant"}
                      className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-200"
                    />
                  </div>
                  <p className="text-xs text-white font-medium truncate">
                    {v.name}
                  </p>
                  {v.variant_key && (
                    <span className="inline-block mt-1 px-1.5 py-0.5 bg-blue-500/15 text-blue-400 text-[10px] font-semibold rounded border border-blue-500/20">
                      {v.variant_key}
                    </span>
                  )}
                  {v.price > 0 && (
                    <p className="text-[10px] text-zinc-400 mt-0.5">
                      ₪{v.price.toLocaleString("he-IL")}
                    </p>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Related Products (compatible + alternatives) */}
        {(compatible.length > 0 || alternatives.length > 0) && (
          <div className="bg-slate-900/80 rounded-xl p-6 border border-slate-800/60">
            <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <Link2 size={16} className="text-violet-400" />
              Related Products
            </h2>
            {compatible.length > 0 && (
              <div className="mb-4">
                <h3 className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider mb-3">
                  Compatible With
                </h3>
                <div className="flex gap-3 overflow-x-auto pb-2 custom-scrollbar">
                  {compatible.slice(0, 6).map((p) => (
                    <button
                      key={p.id}
                      onClick={() => openProductPage(p.id)}
                      className="group shrink-0 w-36 bg-slate-800/40 hover:bg-slate-800/70 border border-slate-700/40 hover:border-violet-500/30 rounded-xl p-3 transition-all duration-200 text-left"
                    >
                      <div className="aspect-square bg-slate-900/60 rounded-lg overflow-hidden mb-2">
                        <ImageWithFallback
                          src={p.image_url || ""}
                          alt={p.name || ""}
                          className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-200"
                        />
                      </div>
                      <p className="text-[11px] text-white font-medium truncate">
                        {p.name}
                      </p>
                      <p className="text-[10px] text-zinc-500 truncate">
                        {p.brand}
                      </p>
                    </button>
                  ))}
                </div>
              </div>
            )}
            {alternatives.length > 0 && (
              <div>
                <h3 className="text-[11px] font-bold text-zinc-500 uppercase tracking-wider mb-3">
                  Alternatives
                </h3>
                <div className="flex gap-3 overflow-x-auto pb-2 custom-scrollbar">
                  {alternatives.slice(0, 6).map((p) => (
                    <button
                      key={p.id}
                      onClick={() => openProductPage(p.id)}
                      className="group shrink-0 w-36 bg-slate-800/40 hover:bg-slate-800/70 border border-slate-700/40 hover:border-amber-500/30 rounded-xl p-3 transition-all duration-200 text-left"
                    >
                      <div className="aspect-square bg-slate-900/60 rounded-lg overflow-hidden mb-2">
                        <ImageWithFallback
                          src={p.image_url || ""}
                          alt={p.name || ""}
                          className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-200"
                        />
                      </div>
                      <p className="text-[11px] text-white font-medium truncate">
                        {p.name}
                      </p>
                      <p className="text-[10px] text-zinc-500 truncate">
                        {p.brand}
                      </p>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer Actions — improved */}
      <div className="px-6 py-4 border-t border-slate-800/60 bg-gradient-to-r from-slate-900 to-slate-900/80 flex gap-3">
        <button
          onClick={() => {
            if (product.galaxy_id) {
              goToSpectrum(product.galaxy_id, product.spectrum_id, []);
            }
          }}
          className="flex-1 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-all duration-200 font-medium text-sm"
        >
          Back to Spectrum
        </button>
        {product.official_url && (
          <button
            onClick={() => window.open(product.official_url!, "_blank")}
            className="flex-1 px-4 py-2.5 bg-emerald-700 hover:bg-emerald-600 text-white rounded-lg transition-all duration-200 font-medium flex items-center justify-center gap-2 text-sm"
          >
            <ExternalLink size={14} />
            View on {product.brand}
          </button>
        )}
        <button
          onClick={() => {
            if (product.halilit_url) {
              window.open(product.halilit_url, "_blank");
            }
          }}
          className="flex-1 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-all duration-200 font-medium text-sm shadow-lg shadow-blue-500/10"
        >
          View on Halilit
        </button>
      </div>
    </div>
  );
};
