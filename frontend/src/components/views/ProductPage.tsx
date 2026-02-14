import {
  X,
  ArrowLeft,
  ExternalLink,
  Layers,
  Shield,
  CheckCircle,
} from "lucide-react";
import React, { useEffect, useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigationStore } from "../../store/navigationStore";
import { ImageWithFallback } from "../ImageWithFallback";
import {
  useConductorCatalog,
  useProductVariants,
  useProductRelationships,
} from "../../hooks/useConductorCatalog";
import type { ConductorProduct } from "../../hooks/useConductorCatalog";
import { getBrandLogoUrl } from "../../lib/brandLogoHelper";
import { getBrandTheme } from "../../styles/brandThemes";

// Cockpit subcomponents
import { CockpitSkeleton } from "../cockpit/CockpitSkeleton";
import { VerdictCard } from "../cockpit/VerdictCard";
import type { VerdictData } from "../cockpit/VerdictCard";
import { TrustedConsensus } from "../cockpit/TrustedConsensus";
import type { ReviewSource } from "../cockpit/TrustedConsensus";
import { FieldNotes } from "../cockpit/FieldNotes";
import type { FieldNotesData } from "../cockpit/FieldNotes";
import { ExplorationDock } from "../cockpit/ExplorationDock";
import type { ExplorationPath } from "../cockpit/ExplorationDock";
import { SmartAccessories } from "../cockpit/SmartAccessories";
import { useJITIntelligence } from "../../hooks/useJITIntelligence";

/**
 * PRODUCT COCKPIT — Mission Control Layout
 *
 * 3-zone design:
 *   Zone 1: HUD Header (sticky — brand logo, name, price, status)
 *   Zone 2: Intelligence Grid (scrollable bento grid)
 *   Zone 3: Action Dock (sticky footer — exploration paths + links)
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

  // JIT Intelligence — connects to SSE stream for live product research
  const jit = useJITIntelligence(productId);
  const jitPhase = jit.phase;
  const verdict = jit.verdict;
  const trustedReviews = jit.trustedReviews;
  const fieldNotes = jit.fieldNotes;
  const explorationPaths = jit.explorationPaths;

  useEffect(() => {
    setLoading(true);
    setActiveImageIndex(0);
    const fromConductor = conductorProducts.find((p) => p.id === productId);
    setProduct(fromConductor ?? null);
    setLoading(false);
  }, [productId, conductorProducts]);

  // Brand theming
  const brandTheme = useMemo(
    () => (product?.brand ? getBrandTheme(product.brand) : null),
    [product?.brand],
  );
  const brandColor = brandTheme?.primary || "#3b82f6";
  const brandLogo = useMemo(
    () => (product?.brand ? getBrandLogoUrl(product.brand) : null),
    [product?.brand],
  );

  // Images
  const images = useMemo(() => {
    if (!product) return [];
    if (product.image_gallery && product.image_gallery.length > 0) {
      return product.image_gallery.map((url) => ({ url }));
    }
    return product.image_url ? [{ url: product.image_url }] : [];
  }, [product]);

  const currentImage = images[activeImageIndex]?.url || "";

  if (!productId) return null;

  // Loading state
  if (loading) {
    return (
      <div className="w-full h-full bg-zinc-950 rounded-xl overflow-hidden flex flex-col">
        <div className="flex items-center gap-4 px-6 py-4 border-b border-zinc-800/60 bg-zinc-900/50">
          <div className="w-10 h-10 rounded-lg bg-zinc-800 animate-pulse" />
          <div className="space-y-2">
            <div className="h-3 w-16 bg-zinc-800 rounded animate-pulse" />
            <div className="h-5 w-48 bg-zinc-800 rounded animate-pulse" />
          </div>
        </div>
        <div className="flex-1 p-6">
          <CockpitSkeleton brandColor={brandColor} />
        </div>
      </div>
    );
  }

  // Not found
  if (!product) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-zinc-950 rounded-xl p-6">
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
            This product may have been removed or is not available.
          </p>
          <button
            onClick={closeProductPage}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-all font-medium text-sm"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full bg-zinc-950 rounded-xl overflow-hidden flex flex-col shadow-2xl relative">
      {/* Brand radial gradient overlay */}
      <div
        className="absolute inset-0 pointer-events-none z-0"
        style={{
          background: `radial-gradient(ellipse at top right, ${brandColor}08, transparent 60%)`,
        }}
      />

      {/* ══════════════════════════════════════════════════════════
          ZONE 1: HUD HEADER (sticky)
         ══════════════════════════════════════════════════════════ */}
      <div className="relative z-10 flex items-center justify-between px-6 py-3 border-b border-zinc-800/60 bg-zinc-950/90 backdrop-blur-md">
        <div className="flex items-center gap-4">
          {/* Back */}
          <button
            onClick={closeProductPage}
            className="p-2 hover:bg-zinc-800 rounded-lg transition-all text-zinc-400 hover:text-white"
          >
            <ArrowLeft size={18} />
          </button>

          <div className="h-5 w-px bg-zinc-800" />

          {/* Brand Logo */}
          {brandLogo && (
            <div className="w-10 h-10 bg-white rounded-lg p-1.5 flex items-center justify-center overflow-hidden shrink-0 shadow-md">
              <img
                src={brandLogo}
                alt={product.brand}
                className="max-w-full max-h-full object-contain"
                onError={(e) => (e.currentTarget.style.display = "none")}
              />
            </div>
          )}

          {/* Name & Brand */}
          <div>
            <div className="flex items-center gap-2">
              <p
                className="text-[10px] font-bold uppercase tracking-[0.15em]"
                style={{ color: brandColor }}
              >
                {product.brand}
              </p>
              <span className="flex items-center gap-1 text-[9px] font-semibold text-emerald-400/80 bg-emerald-500/10 border border-emerald-500/15 rounded-full px-1.5 py-0.5">
                <Shield size={8} />
                HALILIT VERIFIED
              </span>
            </div>
            <h1 className="text-base font-bold text-white leading-tight truncate max-w-md">
              {product.name}
            </h1>
          </div>
        </div>

        {/* Price + Stock */}
        <div className="flex items-center gap-4">
          {/* Price block */}
          <div className="text-right">
            <div className="flex items-baseline gap-2 justify-end">
              <span className="text-xl font-black text-white tracking-tight font-mono">
                {product.price > 0
                  ? `\u20AA${product.price.toLocaleString("he-IL")}`
                  : "Price on request"}
              </span>
              {product.tier && (
                <span
                  className="text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-full border"
                  style={{
                    color: brandColor,
                    borderColor: `${brandColor}30`,
                    backgroundColor: `${brandColor}10`,
                  }}
                >
                  {product.tier}
                </span>
              )}
            </div>
            {product.price_eilat > 0 && (
              <p className="text-[10px] text-zinc-500">
                Eilat:{" "}
                <span className="text-zinc-400 font-semibold">
                  {"\u20AA"}{product.price_eilat.toLocaleString("he-IL")}
                </span>
                {product.price > 0 && (
                  <span className="text-emerald-400 ml-1">
                    -
                    {Math.round(
                      (1 - product.price_eilat / product.price) * 100,
                    )}
                    %
                  </span>
                )}
              </p>
            )}
          </div>

          {/* Stock indicator */}
          <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/15">
            <CheckCircle size={12} className="text-emerald-400" />
            <span className="text-[10px] font-semibold text-emerald-400">
              In Stock
            </span>
          </div>

          <div className="h-5 w-px bg-zinc-800" />

          <button
            onClick={closeProductPage}
            className="p-2 hover:bg-zinc-800 rounded-lg transition-all text-zinc-500 hover:text-white"
          >
            <X size={16} />
          </button>
        </div>
      </div>

      {/* Variant Switcher */}
      {variants.length > 0 && (
        <div className="relative z-10 px-6 py-2 border-b border-zinc-800/40 bg-zinc-900/30 flex items-center gap-3">
          <span className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold shrink-0 flex items-center gap-1.5">
            <Layers size={12} style={{ color: brandColor }} />
            Variants
          </span>
          <div className="flex gap-1 overflow-x-auto">
            <button
              className="px-3 py-1.5 rounded-md text-xs font-semibold text-white shadow-lg shrink-0"
              style={{
                backgroundColor: brandColor,
                boxShadow: `0 2px 8px ${brandColor}30`,
              }}
            >
              {product.variant_key || product.name?.split(" ").pop() || "Current"}
            </button>
            {variants.map((v) => (
              <button
                key={v.id}
                onClick={() => openProductPage(v.id)}
                className="px-3 py-1.5 rounded-md text-xs font-medium bg-zinc-800/60 text-zinc-400 hover:bg-zinc-700 hover:text-white transition-all shrink-0 border border-zinc-700/40"
              >
                {v.variant_key || v.name?.split(" ").pop() || v.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════
          ZONE 2: INTELLIGENCE GRID (scrollable)
         ══════════════════════════════════════════════════════════ */}
      <div className="flex-1 overflow-y-auto relative z-10">
        <div className="p-6 space-y-4">
          <div className="grid grid-cols-12 gap-4">
            {/* ── LEFT COLUMN (4 cols): Hero Image + Quick Stats ── */}
            <div className="col-span-4 space-y-3">
              {/* Hero Image */}
              <div className="relative aspect-square bg-gradient-to-br from-zinc-900/50 to-zinc-800/20 rounded-xl overflow-hidden border border-zinc-800/40 group">
                {currentImage ? (
                  <ImageWithFallback
                    src={currentImage}
                    alt={product.name || "Product"}
                    className="w-full h-full object-contain p-6"
                  />
                ) : (
                  <div className="w-full h-full flex flex-col items-center justify-center gap-4 p-8">
                    {brandLogo && (
                      <img
                        src={brandLogo}
                        alt={product.brand}
                        className="max-w-[50%] max-h-[30%] object-contain opacity-10"
                      />
                    )}
                    <p className="text-xs text-zinc-600 font-mono uppercase tracking-widest">
                      No image yet
                    </p>
                  </div>
                )}

                {/* Image counter */}
                {images.length > 1 && (
                  <div className="absolute bottom-3 right-3 px-2 py-1 bg-black/70 backdrop-blur-sm rounded-md text-[10px] text-zinc-300 font-mono">
                    {activeImageIndex + 1} / {images.length}
                  </div>
                )}

                {/* Brand watermark */}
                <div
                  className="absolute bottom-0 inset-x-0 h-[2px]"
                  style={{
                    background: `linear-gradient(90deg, transparent, ${brandColor}50, transparent)`,
                  }}
                />
              </div>

              {/* Thumbnail Gallery */}
              {images.length > 1 && (
                <div className="flex gap-2 overflow-x-auto pb-1">
                  {images.slice(0, 8).map((img, idx) => (
                    <button
                      key={idx}
                      onClick={() => setActiveImageIndex(idx)}
                      className={`shrink-0 w-14 h-14 rounded-lg overflow-hidden border-2 transition-all duration-200 ${
                        idx === activeImageIndex
                          ? "opacity-100 shadow-lg"
                          : "border-zinc-800 opacity-50 hover:opacity-80"
                      }`}
                      style={
                        idx === activeImageIndex
                          ? {
                              borderColor: brandColor,
                              boxShadow: `0 2px 8px ${brandColor}30`,
                            }
                          : {}
                      }
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

              {/* Quick Stats Card */}
              <div className="rounded-xl bg-zinc-900/70 border border-zinc-800/50 p-4 space-y-3">
                {/* Classification */}
                <div className="grid grid-cols-2 gap-2">
                  <div className="bg-zinc-800/30 rounded-lg p-2.5">
                    <p className="text-[9px] text-zinc-500 uppercase tracking-wider font-semibold mb-0.5">
                      Galaxy
                    </p>
                    <p className="text-[11px] text-white font-medium capitalize">
                      {product.galaxy_id?.replace(/-/g, " ") || "N/A"}
                    </p>
                  </div>
                  <div className="bg-zinc-800/30 rounded-lg p-2.5">
                    <p className="text-[9px] text-zinc-500 uppercase tracking-wider font-semibold mb-0.5">
                      Spectrum
                    </p>
                    <p className="text-[11px] text-white font-medium capitalize">
                      {product.spectrum_id?.replace(/-/g, " ") || "N/A"}
                    </p>
                  </div>
                </div>

                {/* Rating */}
                {product.rating > 0 && (
                  <div className="flex items-center gap-3 pt-2 border-t border-zinc-800/30">
                    <span className="text-2xl font-black text-amber-400 tabular-nums">
                      {product.rating.toFixed(1)}
                    </span>
                    <div>
                      <div className="flex gap-0.5 mb-0.5">
                        {[...Array(5)].map((_, i) => (
                          <svg
                            key={i}
                            className={`w-3.5 h-3.5 ${i < Math.floor(product.rating) ? "text-amber-400" : "text-zinc-700"}`}
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                        ))}
                      </div>
                      <p className="text-[9px] text-zinc-500">
                        {product.review_count} review
                        {product.review_count !== 1 ? "s" : ""}
                      </p>
                    </div>
                  </div>
                )}

                {/* Source links */}
                <div className="pt-2 border-t border-zinc-800/30 space-y-1.5">
                  {product.halilit_url && (
                    <a
                      href={product.halilit_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-[11px] text-blue-400 hover:text-blue-300 transition-colors"
                    >
                      <ExternalLink size={10} />
                      Halilit Page
                    </a>
                  )}
                  {product.official_url && (
                    <a
                      href={product.official_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-[11px] text-emerald-400 hover:text-emerald-300 transition-colors"
                    >
                      <ExternalLink size={10} />
                      {product.brand} Official
                    </a>
                  )}
                </div>
              </div>
            </div>

            {/* ── RIGHT COLUMN (8 cols): Smart Cards ── */}
            <div className="col-span-8 space-y-4">
              {/* Description card — always from inventory */}
              {product.description && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className="rounded-xl bg-zinc-900/70 border border-zinc-800/50 p-5"
                >
                  <h3 className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                    <span
                      className="w-1.5 h-1.5 rounded-full"
                      style={{ backgroundColor: brandColor }}
                    />
                    Overview
                  </h3>
                  <p className="text-sm text-zinc-300 leading-relaxed line-clamp-4">
                    {product.description}
                  </p>
                </motion.div>
              )}

              {/* JIT Status Indicator */}
              {jitPhase !== "idle" && jitPhase !== "complete" && jitPhase !== "error" && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center gap-3 px-4 py-2.5 rounded-xl border border-zinc-800/50 bg-zinc-900/50"
                >
                  <div
                    className="w-2 h-2 rounded-full animate-pulse"
                    style={{ backgroundColor: brandColor }}
                  />
                  <span className="text-xs text-zinc-400 font-medium">
                    {jit.statusMessage || "Gathering intelligence..."}
                  </span>
                  <div className="ml-auto flex gap-1">
                    {[0, 1, 2].map((i) => (
                      <motion.div
                        key={i}
                        className="w-1.5 h-1.5 rounded-full bg-zinc-600"
                        animate={{ opacity: [0.3, 1, 0.3] }}
                        transition={{
                          duration: 1.2,
                          delay: i * 0.2,
                          repeat: Infinity,
                        }}
                      />
                    ))}
                  </div>
                </motion.div>
              )}

              {/* JIT Intelligence Cards — streamed in progressively */}
              <AnimatePresence>
                {/* Verdict Card */}
                <VerdictCard
                  verdict={verdict}
                  brandColor={brandColor}
                  isLoading={jitPhase === "intel"}
                />

                {/* Two-column row: Specs + Trusted Reviews */}
                <div className="grid grid-cols-2 gap-4">
                  {/* Official Specs */}
                  {product.specs && Object.keys(product.specs).length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: 0.1 }}
                      className="rounded-xl bg-zinc-900/70 border border-zinc-800/50 p-5"
                    >
                      <h3 className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                        Key Specs
                      </h3>
                      <div className="space-y-0.5 text-sm">
                        {Object.entries(product.specs)
                          .slice(0, 8)
                          .map(([key, value], idx) => (
                            <div
                              key={key}
                              className={`flex justify-between py-1.5 px-2 rounded ${idx % 2 === 0 ? "bg-zinc-800/20" : ""}`}
                            >
                              <span className="text-zinc-500 capitalize text-[11px]">
                                {key.replace(/_/g, " ")}
                              </span>
                              <span className="text-white font-medium text-right ml-4 text-[11px]">
                                {typeof value === "object"
                                  ? JSON.stringify(value)
                                  : String(value)}
                              </span>
                            </div>
                          ))}
                      </div>
                    </motion.div>
                  )}

                  {/* Trusted Consensus */}
                  <TrustedConsensus
                    reviews={trustedReviews}
                    brandColor={brandColor}
                    isLoading={jitPhase === "wisdom"}
                  />
                </div>

                {/* Features */}
                {product.features && product.features.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: 0.15 }}
                    className="rounded-xl bg-zinc-900/70 border border-zinc-800/50 p-5"
                  >
                    <h3 className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                      <span
                        className="w-1.5 h-1.5 rounded-full"
                        style={{ backgroundColor: brandColor }}
                      />
                      Key Features
                    </h3>
                    <div className="grid grid-cols-2 gap-x-4 gap-y-2">
                      {product.features.slice(0, 8).map((feature: string, idx: number) => (
                        <div key={idx} className="flex items-start gap-2">
                          <span
                            className="mt-1.5 w-1 h-1 rounded-full shrink-0"
                            style={{ backgroundColor: `${brandColor}80` }}
                          />
                          <span className="text-[11px] text-zinc-300 leading-relaxed">
                            {feature}
                          </span>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}

                {/* Field Notes (Pro Tips + Warnings) */}
                <FieldNotes
                  notes={fieldNotes}
                  brandColor={brandColor}
                  isLoading={jitPhase === "wisdom"}
                />

                {/* Pros & Cons */}
                {(product.pros?.length > 0 || product.cons?.length > 0) && (
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: 0.2 }}
                    className="grid grid-cols-2 gap-4"
                  >
                    {product.pros?.length > 0 && (
                      <div className="rounded-xl bg-emerald-950/15 border border-emerald-500/15 p-4">
                        <h3 className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider mb-3">
                          Pros
                        </h3>
                        <ul className="space-y-1.5">
                          {product.pros.map((pro, idx) => (
                            <li
                              key={idx}
                              className="flex items-start gap-2 text-[11px] text-zinc-300"
                            >
                              <span className="text-emerald-400 mt-0.5 shrink-0">
                                +
                              </span>
                              {pro}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {product.cons?.length > 0 && (
                      <div className="rounded-xl bg-orange-950/15 border border-orange-500/15 p-4">
                        <h3 className="text-[11px] font-bold text-orange-400 uppercase tracking-wider mb-3">
                          Cons
                        </h3>
                        <ul className="space-y-1.5">
                          {product.cons.map((con, idx) => (
                            <li
                              key={idx}
                              className="flex items-start gap-2 text-[11px] text-zinc-300"
                            >
                              <span className="text-orange-400 mt-0.5 shrink-0">
                                -
                              </span>
                              {con}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </motion.div>
                )}

                {/* Smart Accessories */}
                <SmartAccessories
                  accessories={accessories.map((a) => ({
                    id: a.id,
                    name: a.name || "",
                    price: a.price,
                    image_url: a.image_url,
                  }))}
                  brandColor={brandColor}
                  onProductClick={openProductPage}
                />

                {/* Variants strip */}
                {variants.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: 0.25 }}
                    className="rounded-xl bg-zinc-900/70 border border-zinc-800/50 p-5"
                  >
                    <div className="flex items-center gap-2 mb-4">
                      <Layers size={14} style={{ color: brandColor }} />
                      <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider">
                        Also in this Series
                      </span>
                      <span className="ml-auto text-[10px] text-zinc-600">
                        {variants.length} variant
                        {variants.length !== 1 ? "s" : ""}
                      </span>
                    </div>
                    <div className="flex gap-3 overflow-x-auto pb-1">
                      {variants.map((v) => (
                        <button
                          key={v.id}
                          onClick={() => openProductPage(v.id)}
                          className="group shrink-0 w-40 bg-zinc-800/40 hover:bg-zinc-800/70 border border-zinc-700/40 rounded-xl p-3 transition-all duration-200 text-left"
                          style={{
                            borderColor: undefined,
                          }}
                        >
                          <div className="aspect-square bg-zinc-900/60 rounded-lg overflow-hidden mb-2">
                            <ImageWithFallback
                              src={v.image_url || ""}
                              alt={v.name || "Variant"}
                              className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-200"
                            />
                          </div>
                          <p className="text-[11px] text-white font-medium truncate">
                            {v.name}
                          </p>
                          {v.variant_key && (
                            <span
                              className="inline-block mt-1 px-1.5 py-0.5 text-[9px] font-semibold rounded border"
                              style={{
                                color: brandColor,
                                borderColor: `${brandColor}20`,
                                backgroundColor: `${brandColor}10`,
                              }}
                            >
                              {v.variant_key}
                            </span>
                          )}
                          {v.price > 0 && (
                            <p className="text-[10px] text-zinc-400 mt-0.5">
                              {"\u20AA"}{v.price.toLocaleString("he-IL")}
                            </p>
                          )}
                        </button>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>

      {/* ══════════════════════════════════════════════════════════
          ZONE 3: ACTION DOCK (sticky footer)
         ══════════════════════════════════════════════════════════ */}
      <ExplorationDock
        paths={explorationPaths}
        halilitUrl={product.halilit_url}
        officialUrl={product.official_url}
        brandName={product.brand}
        brandColor={brandColor}
        onBackToSpectrum={() => {
          if (product.galaxy_id) {
            goToSpectrum(product.galaxy_id, product.spectrum_id, []);
          } else {
            closeProductPage();
          }
        }}
      />

      {/* Bottom brand shine line */}
      <div
        className="absolute bottom-0 inset-x-0 h-[1px] z-20"
        style={{
          background: `linear-gradient(90deg, transparent 20%, ${brandColor}40, transparent 80%)`,
        }}
      />
    </div>
  );
};
