/**
 * ProductCard Component
 * 
 * Enhanced product card with full hierarchy context and relationships.
 * Used in Spectrum and other list views.
 * 
 * Features:
 * - Hierarchy breadcrumb
 * - Product image gallery
 * - Variant indicators
 * - Relationship badges
 * - Interactive hover states
 */

import React, { useState, useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Package,
  Link2,
  ChevronRight,
  ExternalLink,
  Layers,
} from "lucide-react";
import { ImageWithFallback } from "../ImageWithFallback";
import type { ConductorProduct } from "../../hooks/useConductorCatalog";
import { useNavigationStore } from "../../store/navigationStore";
import { HierarchyBreadcrumb } from "./HierarchyBreadcrumb";

interface ProductCardProps {
  product: ConductorProduct;
  variants?: ConductorProduct[];
  showHierarchy?: boolean;
  showRelations?: boolean;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export const ProductCard: React.FC<ProductCardProps> = ({
  product,
  variants = [],
  showHierarchy = true,
  showRelations = true,
  size = "md",
  className = "",
}) => {
  const { openProductPage } = useNavigationStore();
  const [imageIndex, setImageIndex] = useState(0);
  const [isHovered, setIsHovered] = useState(false);

  const images = useMemo(() => {
    if (product.image_gallery && product.image_gallery.length > 0) {
      return product.image_gallery;
    }
    return product.image_url ? [product.image_url] : [];
  }, [product]);

  const currentImage = images[imageIndex] || "";

  const hasVariants = variants.length > 1;
  const hasRelations =
    (product.product_data?.accessory_count || 0) > 0 ||
    (product.product_data?.related_count || 0) > 0;

  // Size variants
  const sizeClasses = {
    sm: {
      card: "p-3",
      image: "h-32",
      title: "text-sm",
      text: "text-xs",
    },
    md: {
      card: "p-4",
      image: "h-48",
      title: "text-base",
      text: "text-sm",
    },
    lg: {
      card: "p-6",
      image: "h-64",
      title: "text-lg",
      text: "text-base",
    },
  };

  const classes = sizeClasses[size];

  return (
    <motion.div
      className={`
        group relative bg-zinc-900/40 backdrop-blur-sm border border-zinc-800/50 rounded-xl
        hover:border-zinc-700/70 hover:bg-zinc-900/60 transition-all
        ${classes.card} ${className}
        focus-within:ring-2 focus-within:ring-blue-500 focus-within:outline-none
      `}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      whileHover={{ y: -2 }}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      {/* Hierarchy Breadcrumb */}
      {showHierarchy && (
        <div className="mb-3">
          <HierarchyBreadcrumb
            hierarchy={{
              category: product.category,
              subCategory: product.subcategory,
              productType: product.product_data?.product_type,
              brand: product.brand,
              family: product.family_name || product.product_data?.family_name,
              model: product.model_name || product.product_data?.model_name,
            }}
            className="text-xs"
          />
        </div>
      )}

      {/* Clickable Area */}
      <button
        type="button"
        onClick={() => openProductPage(product.id)}
        className="w-full text-left focus:outline-none"
      >
        {/* Image Section */}
        <div
          className={`
            relative rounded-lg overflow-hidden bg-gradient-to-br from-zinc-900/50 to-zinc-800/20
            border border-zinc-800/40 mb-3 ${classes.image}
            group-hover:border-zinc-700/60 transition-all
          `}
        >
          {currentImage ? (
            <ImageWithFallback
              src={currentImage}
              alt={product.name}
              className="w-full h-full object-contain p-4 group-hover:scale-105 transition-transform duration-300"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-zinc-600">
              <Package className="w-12 h-12 opacity-20" />
            </div>
          )}

          {/* Image Gallery Indicator */}
          {images.length > 1 && (
            <div className="absolute bottom-2 right-2 px-2 py-1 bg-black/70 backdrop-blur-sm rounded-md text-[10px] text-zinc-300 font-mono">
              {imageIndex + 1} / {images.length}
            </div>
          )}

          {/* Variant Badge */}
          {hasVariants && (
            <div className="absolute top-2 left-2 px-2 py-1 bg-blue-500/20 backdrop-blur-sm rounded-md border border-blue-500/30">
              <div className="flex items-center gap-1.5">
                <Layers className="w-3 h-3 text-blue-400" />
                <span className="text-[10px] font-semibold text-blue-300">
                  {variants.length} variants
                </span>
              </div>
            </div>
          )}

          {/* Relations Badge */}
          {hasRelations && showRelations && (
            <div className="absolute top-2 right-2 px-2 py-1 bg-purple-500/20 backdrop-blur-sm rounded-md border border-purple-500/30">
              <div className="flex items-center gap-1.5">
                <Link2 className="w-3 h-3 text-purple-400" />
                <span className="text-[10px] font-semibold text-purple-300">
                  Related
                </span>
              </div>
            </div>
          )}

          {/* Hover Overlay */}
          <AnimatePresence>
            {isHovered && (
              <motion.div
                className="absolute inset-0 bg-gradient-to-t from-zinc-900/80 via-transparent to-transparent"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between">
                  <span className="text-xs font-medium text-white">
                    View Details
                  </span>
                  <ChevronRight className="w-4 h-4 text-white" />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Product Info */}
        <div className="space-y-2">
          {/* Brand */}
          <div className="flex items-center justify-between">
            <p className={`text-zinc-500 font-medium ${classes.text}`}>
              {product.brand}
            </p>
            {product.price > 0 && (
              <span className={`font-bold text-white ${classes.text}`}>
                ₪{product.price.toLocaleString()}
              </span>
            )}
          </div>

          {/* Name */}
          <h3
            className={`font-semibold text-white line-clamp-2 group-hover:text-blue-400 transition-colors ${classes.title}`}
          >
            {product.name}
          </h3>

          {/* Variant Key */}
          {product.variant_key && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-zinc-500 bg-zinc-800/50 px-2 py-0.5 rounded">
                {product.variant_key}
              </span>
            </div>
          )}

          {/* Quick Stats */}
          <div className="flex items-center gap-3 pt-1">
            {product.tier && (
              <span className="text-[10px] font-semibold text-zinc-500 uppercase tracking-wider bg-zinc-800/50 px-2 py-0.5 rounded">
                {product.tier}
              </span>
            )}
            {product.rating > 0 && (
              <span className="text-[10px] text-zinc-500">
                ⭐ {product.rating.toFixed(1)}
              </span>
            )}
          </div>
        </div>
      </button>

      {/* Variant Thumbnails (on hover) */}
      {hasVariants && isHovered && (
        <motion.div
          className="absolute top-full left-0 right-0 mt-2 p-3 bg-zinc-900/95 backdrop-blur-md rounded-lg border border-zinc-800/50 shadow-xl z-10"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
        >
          <div className="text-xs text-zinc-500 mb-2 font-semibold uppercase tracking-wider">
            Variants
          </div>
          <div className="grid grid-cols-4 gap-2">
            {variants.slice(0, 4).map((variant) => (
              <button
                key={variant.id}
                type="button"
                onClick={() => openProductPage(variant.id)}
                className="relative aspect-square rounded overflow-hidden bg-zinc-800/50 hover:bg-zinc-800 transition-all border border-zinc-700/30 hover:border-blue-500/50"
              >
                {variant.image_url ? (
                  <ImageWithFallback
                    src={variant.image_url}
                    alt={variant.name}
                    className="w-full h-full object-contain p-1"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-zinc-600 text-[10px]">
                    {variant.variant_key || "V"}
                  </div>
                )}
                {variant.id === product.id && (
                  <div className="absolute inset-0 border-2 border-blue-500 rounded" />
                )}
              </button>
            ))}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};
