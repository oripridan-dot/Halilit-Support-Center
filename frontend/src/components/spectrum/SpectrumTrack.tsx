/**
 * SpectrumTrack — A horizontal "track" for a single brand,
 * displaying model group cards with expandable variation subtracks.
 *
 * Layout:
 * ┌──────────────────────────────────────────────────────────┐
 * │ [Brand Logo]  Brand Name  ·  12 models · 47 products    │
 * │ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐            │
 * │ │ Model  │ │ Model  │ │ Model  │ │ Model  │ ← cards    │
 * │ │ ₪2,643 │ │ ₪3,100 │ │ ₪1,200 │ │ ₪4,500 │            │
 * │ │  3 ▼   │ │  7 ▼   │ │  ──    │ │  4 ▼   │            │
 * │ └────────┘ └────────┘ └────────┘ └────────┘            │
 * │            ┌────┐┌────┐┌────┐                           │
 * │            │Var1││Var2││Var3│  ← expanded subtrack      │
 * │            └────┘└────┘└────┘                           │
 * └──────────────────────────────────────────────────────────┘
 */
import React, { useCallback, useRef } from "react";
import type { ModelGroup, ModelVariation } from "../../types/spectrum";
import { getBrandLogoUrl } from "../../lib/brandLogoHelper";
import { getBrandTheme } from "../../styles/brandThemes";

interface SpectrumTrackProps {
  brand: string;
  models: ModelGroup[];
  expandedModel: string | null;
  onModelClick: (modelKey: string) => void;
  onProductClick: (productId: string) => void;
}

export const SpectrumTrack: React.FC<SpectrumTrackProps> = ({
  brand,
  models,
  expandedModel,
  onModelClick,
  onProductClick,
}) => {
  const trackRef = useRef<HTMLDivElement>(null);
  const theme = getBrandTheme(brand);
  const brandPrimary = theme.primary;

  const formatPrice = useCallback((amount: number) => {
    if (amount <= 0) return "POA";
    return `₪${amount.toLocaleString("he-IL")}`;
  }, []);

  // Brand logo with fallback
  const logoUrl = getBrandLogoUrl(brand);

  return (
    <div
      className="border-b border-zinc-800/40 transition-colors hover:bg-white/[0.02]"
      style={{ backgroundColor: `${brandPrimary}04` }}
    >
      {/* Brand Lane Header */}
      <div className="flex items-center gap-3 px-4 py-2 border-b border-zinc-800/20">
        <div
          className="w-10 h-10 rounded-lg flex items-center justify-center overflow-hidden border border-zinc-800/50 shrink-0"
          style={{ backgroundColor: `${brandPrimary}08` }}
        >
          {logoUrl ? (
            <img
              src={logoUrl}
              alt={brand}
              className="max-h-7 max-w-8 object-contain"
            />
          ) : (
            <span
              className="text-[10px] font-black uppercase tracking-tight"
              style={{ color: brandPrimary }}
            >
              {brand.slice(0, 3)}
            </span>
          )}
        </div>
        <div className="min-w-0">
          <h3 className="text-white font-semibold text-sm tracking-wide uppercase truncate">
            {brand}
          </h3>
          <span className="text-zinc-500 text-[10px]">
            {models.length} model{models.length !== 1 ? "s" : ""} ·{" "}
            {models.reduce((sum, m) => sum + m.variationCount, 0)} products
          </span>
        </div>
      </div>

      {/* Model Cards Track (horizontal scroll) */}
      <div
        ref={trackRef}
        className="flex gap-2.5 overflow-x-auto px-4 py-3 scrollbar-thin
                   scrollbar-thumb-zinc-800 scrollbar-track-transparent"
      >
        {models.map((model) => (
          <ModelCard
            key={model.modelKey}
            model={model}
            brandPrimary={brandPrimary}
            isExpanded={expandedModel === model.modelKey}
            onModelClick={onModelClick}
            onProductClick={onProductClick}
            formatPrice={formatPrice}
          />
        ))}
      </div>
    </div>
  );
};

// ── Individual Model Card ──

interface ModelCardProps {
  model: ModelGroup;
  brandPrimary: string;
  isExpanded: boolean;
  onModelClick: (modelKey: string) => void;
  onProductClick: (productId: string) => void;
  formatPrice: (amount: number) => string;
}

const ModelCard: React.FC<ModelCardProps> = ({
  model,
  brandPrimary,
  isExpanded,
  onModelClick,
  onProductClick,
  formatPrice,
}) => {
  // Strip brand from display name
  const displayName =
    model.modelName
      .replace(new RegExp(`^${model.brand}\\s*`, "i"), "")
      .trim() || model.modelName;

  return (
    <div className="flex-shrink-0">
      {/* Model Card */}
      <button
        onClick={() => onModelClick(model.modelKey)}
        className={`
          group relative w-32 rounded-xl overflow-hidden transition-all duration-200
          ${
            isExpanded
              ? "ring-2 ring-amber-500/70 bg-zinc-800 scale-[1.02]"
              : "bg-zinc-900/60 hover:bg-zinc-800/80 hover:ring-1 hover:ring-zinc-700"
          }
        `}
      >
        {/* Product Image */}
        <div className="aspect-square p-2 flex items-center justify-center bg-white/5">
          {model.heroImage ? (
            <img
              src={model.heroImage}
              alt={model.modelName}
              className="max-h-full max-w-full object-contain
                         group-hover:scale-110 transition-transform duration-300"
              loading="lazy"
            />
          ) : (
            <div className="text-zinc-700 text-2xl">🎵</div>
          )}
        </div>

        {/* Model Info */}
        <div className="p-2 space-y-1">
          <p
            className="text-white text-[11px] font-semibold truncate leading-tight"
            title={displayName}
          >
            {displayName}
          </p>

          {/* Price Range */}
          <div className="flex items-baseline gap-1">
            <span className="text-amber-400 text-[11px] font-bold">
              {formatPrice(model.priceRange.min)}
            </span>
            {model.priceRange.max > model.priceRange.min &&
              model.priceRange.min > 0 && (
                <span className="text-zinc-600 text-[9px]">
                  – {formatPrice(model.priceRange.max)}
                </span>
              )}
          </div>

          {/* Variation Count Badge */}
          {model.variationCount > 1 && (
            <div
              className={`flex items-center gap-1 text-[9px] font-medium ${
                isExpanded ? "text-amber-400" : "text-zinc-500"
              }`}
            >
              <span>{model.variationCount} variants</span>
              <svg
                className={`w-2.5 h-2.5 transition-transform duration-200 ${
                  isExpanded ? "rotate-180" : ""
                }`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </div>
          )}

          {/* Body Type Tag */}
          {model.bodyType && model.bodyType !== "general" && (
            <span
              className="inline-block bg-zinc-800/60 text-zinc-500
                             text-[8px] px-1.5 py-0.5 rounded-full uppercase tracking-wider"
            >
              {model.bodyType.replace(/_/g, " ")}
            </span>
          )}

          {/* Confidence Indicator */}
          {model.avgConfidence > 0 && (
            <div className="flex items-center gap-1">
              <div className="flex-1 h-0.5 bg-zinc-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    model.avgConfidence >= 75
                      ? "bg-emerald-500"
                      : model.avgConfidence >= 50
                        ? "bg-amber-500"
                        : "bg-red-500"
                  }`}
                  style={{ width: `${Math.min(100, model.avgConfidence)}%` }}
                />
              </div>
              <span className="text-[8px] text-zinc-600">
                {Math.round(model.avgConfidence)}%
              </span>
            </div>
          )}
        </div>
      </button>

      {/* Expanded Variations Subtrack */}
      {isExpanded && model.variations && model.variations.length > 0 && (
        <div
          className="mt-2 pl-2 border-l-2 border-amber-500/30 space-y-1 max-h-60 overflow-y-auto
                        scrollbar-thin scrollbar-thumb-zinc-800 scrollbar-track-transparent"
        >
          {model.variations.map((variation, idx) => (
            <VariationRow
              key={variation.id || idx}
              variation={variation}
              brandPrimary={brandPrimary}
              onProductClick={onProductClick}
              formatPrice={formatPrice}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// ── Variation Row (within expanded subtrack) ──

interface VariationRowProps {
  variation: ModelVariation;
  brandPrimary: string;
  onProductClick: (productId: string) => void;
  formatPrice: (amount: number) => string;
}

const VariationRow: React.FC<VariationRowProps> = ({
  variation,
  onProductClick,
  formatPrice,
}) => {
  return (
    <button
      onClick={() => onProductClick(variation.id)}
      className="w-full flex items-center gap-2 p-1.5 rounded-lg
                 bg-zinc-900/40 hover:bg-zinc-800/60 transition-colors
                 text-left group/var"
    >
      {/* Mini thumbnail */}
      <div
        className="w-8 h-8 bg-white/5 rounded flex-shrink-0
                      flex items-center justify-center overflow-hidden"
      >
        {variation.image_url ? (
          <img
            src={variation.image_url}
            alt={variation.variation}
            className="max-h-full max-w-full object-contain"
            loading="lazy"
          />
        ) : (
          <span className="text-zinc-700 text-[9px]">🎵</span>
        )}
      </div>

      {/* Variation info */}
      <div className="flex-1 min-w-0">
        <p className="text-white text-[10px] font-medium truncate">
          {variation.variation}
        </p>
        <p className="text-amber-400/80 text-[9px] font-bold">
          {formatPrice(variation.price)}
        </p>
      </div>

      {/* Source indicators */}
      <div className="flex gap-0.5 shrink-0">
        {variation.sources?.includes("halilit") && (
          <div
            className="w-1.5 h-1.5 rounded-full bg-blue-500"
            title="Halilit data"
          />
        )}
        {variation.sources?.includes("official") && (
          <div
            className="w-1.5 h-1.5 rounded-full bg-emerald-500"
            title="Official data"
          />
        )}
        {variation.sources?.includes("contextual") && (
          <div
            className="w-1.5 h-1.5 rounded-full bg-purple-500"
            title="Review data"
          />
        )}
      </div>

      {/* Tier badge */}
      {variation.tier && (
        <span
          className={`text-[7px] px-1 py-0.5 rounded font-bold uppercase tracking-wider shrink-0 ${
            variation.tier === "flagship"
              ? "bg-amber-500/20 text-amber-400"
              : variation.tier === "pro"
                ? "bg-blue-500/20 text-blue-400"
                : variation.tier === "mid"
                  ? "bg-zinc-700/50 text-zinc-400"
                  : "bg-zinc-800/50 text-zinc-500"
          }`}
        >
          {variation.tier}
        </span>
      )}
    </button>
  );
};
