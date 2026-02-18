/**
 * ProductRelationsPanel Component
 * 
 * Displays product relationships (accessories, related products, compatible items)
 * in a visually rich, interactive panel
 */

import React, { useMemo } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Link2,
  Package,
  Zap,
  ArrowRight,
  ExternalLink,
  ShoppingBag,
} from "lucide-react";
import { ImageWithFallback } from "../ImageWithFallback";
import type { ConductorProduct } from "../../hooks/useConductorCatalog";
import { useNavigationStore } from "../../store/navigationStore";

// Helper functions for dynamic color classes (Tailwind doesn't support dynamic class names)
function getColorBg(color: string): string {
  const colors: Record<string, string> = {
    blue: "rgba(59, 130, 246, 0.1)",
    purple: "rgba(168, 85, 247, 0.1)",
    green: "rgba(34, 197, 94, 0.1)",
    orange: "rgba(249, 115, 22, 0.1)",
  };
  return colors[color] || colors.blue;
}

function getColorBorder(color: string): string {
  const colors: Record<string, string> = {
    blue: "rgba(59, 130, 246, 0.2)",
    purple: "rgba(168, 85, 247, 0.2)",
    green: "rgba(34, 197, 94, 0.2)",
    orange: "rgba(249, 115, 22, 0.2)",
  };
  return colors[color] || colors.blue;
}

function getColorText(color: string): string {
  const colors: Record<string, string> = {
    blue: "rgb(96, 165, 250)",
    purple: "rgb(192, 132, 252)",
    green: "rgb(74, 222, 128)",
    orange: "rgb(251, 146, 60)",
  };
  return colors[color] || colors.blue;
}

interface ProductRelationsPanelProps {
  accessories?: ConductorProduct[];
  related?: ConductorProduct[];
  compatible?: ConductorProduct[];
  alternatives?: ConductorProduct[];
  className?: string;
}

type RelationType = "accessories" | "related" | "compatible" | "alternatives";

interface RelationSection {
  type: RelationType;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  products: ConductorProduct[];
}

export const ProductRelationsPanel: React.FC<ProductRelationsPanelProps> = ({
  accessories = [],
  related = [],
  compatible = [],
  alternatives = [],
  className = "",
}) => {
  const { openProductPage } = useNavigationStore();

  const sections: RelationSection[] = useMemo(
    () => [
      {
        type: "accessories",
        label: "Accessories",
        icon: ShoppingBag,
        color: "blue",
        products: accessories,
      },
      {
        type: "related",
        label: "Related Products",
        icon: Link2,
        color: "purple",
        products: related,
      },
      {
        type: "compatible",
        label: "Compatible",
        icon: Zap,
        color: "green",
        products: compatible,
      },
      {
        type: "alternatives",
        label: "Alternatives",
        icon: Package,
        color: "orange",
        products: alternatives,
      },
    ].filter((section) => section.products.length > 0),
    [accessories, related, compatible, alternatives],
  );

  if (sections.length === 0) {
    return null;
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {sections.map((section, sectionIndex) => (
        <motion.div
          key={section.type}
          className="bg-zinc-900/40 backdrop-blur-sm border border-zinc-800/50 rounded-xl p-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: sectionIndex * 0.1 }}
        >
          {/* Section Header */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div
                className="p-1.5 rounded-lg border"
                style={{
                  backgroundColor: getColorBg(section.color),
                  borderColor: getColorBorder(section.color),
                }}
              >
                <section.icon
                  className="w-4 h-4"
                  style={{ color: getColorText(section.color) }}
                />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">
                  {section.label}
                </h3>
                <p className="text-xs text-zinc-500">
                  {section.products.length}{" "}
                  {section.products.length === 1 ? "item" : "items"}
                </p>
              </div>
            </div>
          </div>

          {/* Products Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            <AnimatePresence mode="popLayout">
              {section.products.map((product, index) => (
                <motion.button
                  key={product.id}
                  type="button"
                  onClick={() => openProductPage(product.id)}
                  className="group relative bg-zinc-800/30 hover:bg-zinc-800/50 rounded-lg p-3 border border-zinc-700/30 hover:border-zinc-600/50 transition-all focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                  whileHover={{ scale: 1.02, y: -2 }}
                  whileTap={{ scale: 0.98 }}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ delay: index * 0.03 }}
                >
                  {/* Product Image */}
                  <div className="relative aspect-square mb-2 rounded overflow-hidden bg-zinc-900/50">
                    {product.image_url ? (
                      <ImageWithFallback
                        src={product.image_url}
                        alt={product.name}
                        className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-200"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-zinc-600 text-xs">
                        No Image
                      </div>
                    )}
                    <div className="absolute inset-0 bg-gradient-to-t from-zinc-900/60 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>

                  {/* Product Info */}
                  <div className="text-left space-y-1">
                    <h4 className="text-xs font-medium text-white truncate group-hover:text-blue-400 transition-colors">
                      {product.name}
                    </h4>
                    {product.brand && (
                      <p className="text-xs text-zinc-500 truncate">
                        {product.brand}
                      </p>
                    )}
                    {product.price && (
                      <p className="text-xs font-semibold text-zinc-300">
                        ₪{product.price.toLocaleString()}
                      </p>
                    )}
                  </div>

                  {/* Hover Arrow */}
                  <motion.div
                    className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                    initial={{ x: -5 }}
                    whileHover={{ x: 0 }}
                  >
                    <ArrowRight className="w-3.5 h-3.5 text-zinc-400" />
                  </motion.div>
                </motion.button>
              ))}
            </AnimatePresence>
          </div>
        </motion.div>
      ))}
    </div>
  );
};
