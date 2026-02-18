/**
 * ProductHierarchyContext Component
 * 
 * Displays the complete hierarchy context for a product:
 * - Family information
 * - Model information
 * - Variants in the same model
 * - Visual representation of the hierarchy
 */

import React, { useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Layers,
  Package,
  Tag,
  ChevronRight,
  ExternalLink,
  Ruler,
} from "lucide-react";
import { ImageWithFallback } from "../ImageWithFallback";
import type { ConductorProduct } from "../../hooks/useConductorCatalog";
import { useProductVariants } from "../../hooks/useConductorCatalog";
import { useNavigationStore } from "../../store/navigationStore";
import { SizeComparison } from "./SizeComparison";
import {
  extractDimensions,
  formatDimensions,
  getSizeCategory,
} from "../../lib/sizeUtils";

interface ProductHierarchyContextProps {
  product: ConductorProduct;
  variants?: ConductorProduct[];
  className?: string;
}

export const ProductHierarchyContext: React.FC<
  ProductHierarchyContextProps
> = ({ product, variants: externalVariants, className = "" }) => {
  const { openProductPage } = useNavigationStore();
  const { variants: hookVariants } = useProductVariants(product.id);
  const variants = externalVariants || hookVariants;

  // Extract hierarchy from product data
  const hierarchy = useMemo(() => {
    // Try to extract from hierarchy_path if available
    const path = product.hierarchy_path || "";
    const parts = path.split("/");

    // Fallback to extracting from product data
    const familyName =
      product.family_name ||
      product.product_data?.family_name ||
      extractFamilyFromName(product.name, product.brand);
    const modelName =
      product.model_name ||
      product.product_data?.model_name ||
      extractModelFromName(product.name, product.brand);
    const variantKey =
      product.variant_key ||
      product.product_data?.variant_key ||
      extractVariantFromName(product.name);

    return {
      category: parts[0]?.replace(/-/g, " ") || product.category || "",
      subCategory: parts[1]?.replace(/-/g, " ") || product.subcategory || "",
      productType: parts[2]?.replace(/-/g, " ") || "",
      brand: product.brand || "",
      family: familyName,
      model: modelName,
      variant: variantKey,
    };
  }, [product]);

  const hasVariants = variants && variants.length > 1;
  const currentVariant = variants?.find((v) => v.id === product.id);

  // Check if variants have dimension data for size comparison
  const hasDimensionData = useMemo(() => {
    if (!variants || variants.length < 2) return false;
    return variants.some((v) => extractDimensions(v.specs || {}) !== null);
  }, [variants]);

  return (
    <div
      className={`bg-zinc-900/40 backdrop-blur-sm border border-zinc-800/50 rounded-xl p-4 space-y-4 ${className}`}
    >
      {/* Hierarchy Path */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-xs text-zinc-500 uppercase tracking-wider">
          <Layers className="w-3.5 h-3.5" />
          <span>Product Hierarchy</span>
        </div>

        {/* Family & Model Info */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {/* Family Card */}
          {hierarchy.family && (
            <motion.div
              className="bg-zinc-800/30 rounded-lg p-3 border border-zinc-700/30"
              whileHover={{ borderColor: "rgba(59, 130, 246, 0.5)" }}
              transition={{ duration: 0.2 }}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-zinc-500 mb-1">Family</div>
                  <div className="text-sm font-medium text-white truncate">
                    {hierarchy.family}
                  </div>
                </div>
                <Package className="w-4 h-4 text-zinc-600 flex-shrink-0 ml-2" />
              </div>
            </motion.div>
          )}

          {/* Model Card */}
          {hierarchy.model && (
            <motion.div
              className="bg-zinc-800/30 rounded-lg p-3 border border-zinc-700/30"
              whileHover={{ borderColor: "rgba(59, 130, 246, 0.5)" }}
              transition={{ duration: 0.2 }}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-zinc-500 mb-1">Model</div>
                  <div className="text-sm font-medium text-white truncate">
                    {hierarchy.model}
                  </div>
                </div>
                <Tag className="w-4 h-4 text-zinc-600 flex-shrink-0 ml-2" />
              </div>
            </motion.div>
          )}
        </div>
      </div>

      {/* Size Comparison Section - Show if we have dimension data */}
      {hasVariants && hasDimensionData && (
        <div className="pt-2 border-t border-zinc-800/50">
          <SizeComparison
            variants={variants}
            currentProductId={product.id}
            brandColor="#3b82f6"
            onVariantClick={openProductPage}
          />
        </div>
      )}

      {/* Variants Section */}
      {hasVariants && (
        <div className="space-y-2 pt-2 border-t border-zinc-800/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs text-zinc-500 uppercase tracking-wider">
              <Package className="w-3.5 h-3.5" />
              <span>Variants ({variants.length})</span>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            <AnimatePresence mode="popLayout">
              {variants.map((variant, index) => {
                const isCurrent = variant.id === product.id;
                const variantKey =
                  variant.variant_key ||
                  extractVariantFromName(variant.name) ||
                  `Variant ${index + 1}`;
                
                // Extract dimensions for this variant
                const dimensions = extractDimensions(variant.specs || {});
                const sizeCategory = dimensions ? getSizeCategory(dimensions) : null;

                return (
                  <motion.button
                    key={variant.id}
                    type="button"
                    onClick={() => openProductPage(variant.id)}
                    className={`
                      relative group rounded-lg p-2.5 border transition-all
                      ${isCurrent
                        ? "border-blue-500/50 bg-blue-500/10"
                        : "border-zinc-700/30 bg-zinc-800/20 hover:border-zinc-600/50 hover:bg-zinc-800/40"
                      }
                      focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none
                    `}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    {/* Variant Image */}
                    <div className="relative aspect-square mb-2 rounded overflow-hidden bg-zinc-900/50">
                      {variant.image_url ? (
                        <ImageWithFallback
                          src={variant.image_url}
                          alt={variant.name}
                          className="w-full h-full object-contain p-1.5"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-zinc-600 text-xs">
                          No Image
                        </div>
                      )}
                      {isCurrent && (
                        <div className="absolute inset-0 bg-blue-500/20" />
                      )}
                    </div>

                    {/* Variant Info */}
                    <div className="text-left space-y-1">
                      <div
                        className={`text-xs font-medium truncate ${isCurrent ? "text-blue-400" : "text-zinc-300"
                          }`}
                      >
                        {variantKey}
                      </div>
                      
                      {/* Dimensions Badge */}
                      {dimensions && (
                        <div className="flex items-center gap-1 text-[9px] text-zinc-500">
                          <Ruler className="w-2.5 h-2.5" />
                          <span className="truncate">
                            {dimensions.width && dimensions.height && dimensions.depth
                              ? `${dimensions.width.toFixed(0)}×${dimensions.height.toFixed(0)}×${dimensions.depth.toFixed(0)}`
                              : dimensions.height
                                ? `H: ${dimensions.height.toFixed(0)}cm`
                                : "Size available"}
                          </span>
                        </div>
                      )}

                      {/* Size Category Badge */}
                      {sizeCategory && sizeCategory !== "Unknown" && (
                        <div className="inline-block px-1.5 py-0.5 text-[9px] font-semibold rounded bg-zinc-700/50 text-zinc-400 border border-zinc-600/30">
                          {sizeCategory}
                        </div>
                      )}

                      {variant.price && (
                        <div className="text-xs text-zinc-500 mt-0.5">
                          ₪{variant.price.toLocaleString()}
                        </div>
                      )}
                    </div>

                    {/* Current Indicator */}
                    {isCurrent && (
                      <motion.div
                        className="absolute top-1 right-1 w-2 h-2 bg-blue-500 rounded-full"
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: "spring", stiffness: 500 }}
                      />
                    )}
                  </motion.button>
                );
              })}
            </AnimatePresence>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper functions to extract hierarchy from product names
function extractFamilyFromName(name: string, brand: string): string {
  // Example: "Nord Stage 4 88" → "Stage"
  const nameLower = name.toLowerCase();
  const brandLower = brand.toLowerCase();
  const withoutBrand = nameLower.replace(brandLower, "").trim();

  // Common patterns: "Stage 4", "Piano 5", etc.
  const match = withoutBrand.match(/^([a-z]+)\s+\d+/i);
  return match ? match[1].charAt(0).toUpperCase() + match[1].slice(1) : "";
}

function extractModelFromName(name: string, brand: string): string {
  // Example: "Nord Stage 4 88" → "Stage 4"
  const nameLower = name.toLowerCase();
  const brandLower = brand.toLowerCase();
  const withoutBrand = nameLower.replace(brandLower, "").trim();

  const match = withoutBrand.match(/^([a-z]+\s+\d+)/i);
  return match ? match[1].charAt(0).toUpperCase() + match[1].slice(1) : "";
}

function extractVariantFromName(name: string): string {
  // Example: "Nord Stage 4 88" → "88"
  // Look for common variant patterns: numbers (88, 73), words (Compact, HP)
  const match = name.match(/\s+(\d+|Compact|HP|SE|Pro|Plus)$/i);
  return match ? match[1] : "";
}
