/**
 * HierarchyBreadcrumb Component
 * 
 * Displays the complete hierarchy path for a product:
 * Category → Sub Category → Product Type → Brand → Family → Model
 * 
 * Interactive breadcrumb navigation with smooth transitions
 */

import React from "react";
import { motion } from "framer-motion";
import { ChevronRight, Home } from "lucide-react";
import { useNavigationStore } from "../../store/navigationStore";

export interface HierarchyPath {
  category?: string;
  subCategory?: string;
  productType?: string;
  brand?: string;
  family?: string;
  model?: string;
}

interface HierarchyBreadcrumbProps {
  hierarchy: HierarchyPath;
  onNavigate?: (level: string, value: string) => void;
  className?: string;
}

export const HierarchyBreadcrumb: React.FC<HierarchyBreadcrumbProps> = ({
  hierarchy,
  onNavigate,
  className = "",
}) => {
  const { goToGalaxy, goToSpectrum } = useNavigationStore();

  const levels = [
    { key: "category", label: hierarchy.category, icon: Home },
    { key: "subCategory", label: hierarchy.subCategory },
    { key: "productType", label: hierarchy.productType },
    { key: "brand", label: hierarchy.brand },
    { key: "family", label: hierarchy.family },
    { key: "model", label: hierarchy.model },
  ].filter((level) => level.label);

  const handleClick = (level: { key: string; label?: string }) => {
    if (!level.label || !onNavigate) return;

    // Default navigation behavior
    if (level.key === "category") {
      goToGalaxy();
    } else if (level.key === "subCategory") {
      goToSpectrum(level.label);
    }

    onNavigate(level.key, level.label);
  };

  return (
    <nav
      className={`flex items-center gap-1 text-xs font-medium ${className}`}
      aria-label="Product hierarchy breadcrumb"
    >
      {levels.map((level, index) => {
        const isLast = index === levels.length - 1;
        const Icon = level.icon;

        return (
          <React.Fragment key={level.key}>
            <motion.button
              type="button"
              onClick={() => handleClick(level)}
              disabled={isLast}
              className={`
                flex items-center gap-1.5 px-2 py-1 rounded-md transition-all
                ${isLast
                  ? "text-zinc-400 cursor-default"
                  : "text-zinc-500 hover:text-white hover:bg-zinc-800/50 focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
                }
              `}
              whileHover={!isLast ? { scale: 1.05 } : {}}
              whileTap={!isLast ? { scale: 0.95 } : {}}
              aria-current={isLast ? "page" : undefined}
            >
              {Icon && <Icon className="w-3 h-3" />}
              <span className="truncate max-w-[120px] sm:max-w-[200px]">
                {level.label}
              </span>
            </motion.button>

            {!isLast && (
              <ChevronRight className="w-3 h-3 text-zinc-700 flex-shrink-0" />
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};
