/**
 * SizeComparison Component
 * 
 * Visual comparison of product variants showing relative sizes
 * Uses proportional scaling based on actual dimensions when available
 */

import React, { useMemo } from "react";
import { motion } from "framer-motion";
import { Ruler, Maximize2, Minimize2 } from "lucide-react";
import { ImageWithFallback } from "../ImageWithFallback";
import type { ConductorProduct } from "../../hooks/useConductorCatalog";
import {
  extractDimensions,
  formatDimensions,
  getSizeCategory,
  calculateSizeRatio,
  type ProductDimensions,
} from "../../lib/sizeUtils";

interface SizeComparisonProps {
  variants: ConductorProduct[];
  currentProductId: string;
  brandColor?: string;
  onVariantClick: (productId: string) => void;
}

export const SizeComparison: React.FC<SizeComparisonProps> = ({
  variants,
  currentProductId,
  brandColor = "#3b82f6",
  onVariantClick,
}) => {
  // Extract dimensions for all variants
  const variantsWithDimensions = useMemo(() => {
    return variants.map((variant) => ({
      variant,
      dimensions: extractDimensions(variant.specs || {}),
    }));
  }, [variants]);

  // Find the smallest variant as baseline for proportional scaling
  const baselineVariant = useMemo(() => {
    let smallest: { variant: ConductorProduct; dimensions: ProductDimensions | null } | null = null;
    let smallestVolume = Infinity;

    for (const item of variantsWithDimensions) {
      const volume = item.dimensions?.volume;
      if (volume && volume < smallestVolume) {
        smallestVolume = volume;
        smallest = item;
      }
    }

    return smallest || variantsWithDimensions[0];
  }, [variantsWithDimensions]);

  // Check if we have enough dimension data to show comparison
  const hasDimensionData = variantsWithDimensions.some(
    (item) => item.dimensions !== null
  );

  if (!hasDimensionData) {
    return null; // Don't show if no dimension data available
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-xs text-zinc-500 uppercase tracking-wider">
        <Ruler className="w-3.5 h-3.5" />
        <span>Size Comparison</span>
      </div>

      <div className="relative bg-zinc-900/50 rounded-lg p-4 border border-zinc-800/50">
        {/* Scale reference line */}
        <div className="absolute bottom-2 left-4 right-4 h-px bg-zinc-700/50 flex items-center justify-between">
          <div className="text-[9px] text-zinc-600 font-mono">0</div>
          <div className="text-[9px] text-zinc-600 font-mono">Scale</div>
          <div className="text-[9px] text-zinc-600 font-mono">100%</div>
        </div>

        {/* Variants in proportional size */}
        <div className="flex items-end justify-center gap-4 pb-6 min-h-[200px]">
          {variantsWithDimensions.map((item, index) => {
            const { variant, dimensions } = item;
            const isCurrent = variant.id === currentProductId;
            const variantKey =
              variant.variant_key ||
              variant.name?.split(" ").pop() ||
              `Variant ${index + 1}`;

            // Calculate scale factor relative to baseline
            let scaleFactor = 1;
            if (baselineVariant.dimensions?.volume && dimensions?.volume) {
              scaleFactor = Math.sqrt(dimensions.volume / baselineVariant.dimensions.volume);
            } else if (
              baselineVariant.dimensions?.height &&
              dimensions?.height
            ) {
              scaleFactor = dimensions.height / baselineVariant.dimensions.height;
            }

            // Clamp scale factor to reasonable bounds
            scaleFactor = Math.max(0.3, Math.min(2, scaleFactor));

            return (
              <motion.button
                key={variant.id}
                onClick={() => onVariantClick(variant.id)}
                className={`
                  relative flex flex-col items-center group
                  ${isCurrent ? "z-10" : "z-0"}
                `}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                {/* Product image with proportional sizing */}
                <div
                  className={`
                    relative rounded-lg overflow-hidden border-2 transition-all
                    ${isCurrent
                      ? "border-blue-500/60 shadow-lg shadow-blue-500/20"
                      : "border-zinc-700/40 hover:border-zinc-600/60"
                    }
                  `}
                  style={{
                    width: `${80 * scaleFactor}px`,
                    height: `${80 * scaleFactor}px`,
                    minWidth: "40px",
                    minHeight: "40px",
                    maxWidth: "160px",
                    maxHeight: "160px",
                    backgroundColor: isCurrent ? `${brandColor}10` : "transparent",
                  }}
                >
                  {variant.image_url ? (
                    <ImageWithFallback
                      src={variant.image_url}
                      alt={variant.name || "Variant"}
                      className="w-full h-full object-contain p-1.5"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-zinc-600 text-[10px]">
                      No Image
                    </div>
                  )}

                  {/* Current indicator */}
                  {isCurrent && (
                    <motion.div
                      className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full border-2 border-zinc-900"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ type: "spring", stiffness: 500 }}
                    />
                  )}
                </div>

                {/* Variant label */}
                <div className="mt-2 text-center">
                  <div
                    className={`
                      text-xs font-semibold mb-0.5
                      ${isCurrent ? "text-blue-400" : "text-zinc-300"}
                    `}
                  >
                    {variantKey}
                  </div>

                  {/* Dimensions */}
                  {dimensions && (
                    <div className="text-[10px] text-zinc-500 space-y-0.5">
                      {dimensions.height && dimensions.width && dimensions.depth && (
                        <div className="font-mono">
                          {dimensions.width.toFixed(0)}×{dimensions.height.toFixed(0)}×{dimensions.depth.toFixed(0)} cm
                        </div>
                      )}
                      {dimensions.weight && (
                        <div className="text-zinc-600">
                          {dimensions.weight.toFixed(1)} kg
                        </div>
                      )}
                      {dimensions.volume && (
                        <div className="text-[9px] text-zinc-700 mt-1">
                          {getSizeCategory(dimensions)}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Size difference indicator */}
                  {baselineVariant.variant.id !== variant.id &&
                    baselineVariant.dimensions?.volume &&
                    dimensions?.volume && (
                      <div className="mt-1 flex items-center justify-center gap-1">
                        {dimensions.volume > baselineVariant.dimensions.volume ? (
                          <>
                            <Maximize2 className="w-2.5 h-2.5 text-emerald-400" />
                            <span className="text-[9px] text-emerald-400 font-semibold">
                              +{Math.round(
                                ((dimensions.volume - baselineVariant.dimensions.volume) /
                                  baselineVariant.dimensions.volume) *
                                  100
                              )}%
                            </span>
                          </>
                        ) : dimensions.volume < baselineVariant.dimensions.volume ? (
                          <>
                            <Minimize2 className="w-2.5 h-2.5 text-amber-400" />
                            <span className="text-[9px] text-amber-400 font-semibold">
                              {Math.round(
                                ((dimensions.volume - baselineVariant.dimensions.volume) /
                                  baselineVariant.dimensions.volume) *
                                  100
                              )}%
                            </span>
                          </>
                        ) : null}
                      </div>
                    )}
                </div>
              </motion.button>
            );
          })}
        </div>

        {/* Legend */}
        <div className="mt-4 pt-3 border-t border-zinc-800/30 flex items-center justify-between text-[10px] text-zinc-600">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 border border-zinc-700 rounded" />
            <span>Proportional to actual size</span>
          </div>
          <div className="text-zinc-700">
            Baseline: {baselineVariant.variant.variant_key || "Smallest"}
          </div>
        </div>
      </div>
    </div>
  );
};
