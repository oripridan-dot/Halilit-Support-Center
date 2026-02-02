import React, { memo } from "react";
import type { OptimizedProduct } from "../../types";

const ProductCardComponent = ({ product }: { product: OptimizedProduct }) => {

  // Minimal Display: SKU & Price Emphasis
  return (
    <div
      className={`card p-4 border rounded-md mb-2 bg-zinc-900 border-zinc-800 relative hover:border-zinc-600 transition-colors`}
    >
      {/* HEADER: Product Name */}
      <h3 className="text-md font-bold text-white mb-2 leading-tight">
        {product.name || "Unknown Product"}
      </h3>

      {/* SKU & Category */}
      <div className="flex justify-between items-start mb-2">
         {product.sku && (
            <span className="text-xs font-mono text-emerald-500/80 bg-emerald-950/20 px-1.5 py-0.5 rounded">
              {product.sku}
            </span>
         )}
         <span className="text-xs text-zinc-500 truncate max-w-[50%]">
           {product.category}
         </span>
      </div>

      {/* Price Emphasis */}
      <div className="mt-3 pt-3 border-t border-zinc-800 flex justify-between items-end">
        {product.price ? (
          <div className="text-amber-400 font-mono font-bold text-lg">
            {product.currency} {product.price.toLocaleString()}
          </div>
        ) : (
           <div className="text-zinc-600 text-sm">Price N/A</div>
        )}
        
        {/* Simple Stock Indicator */}
        {product.in_stock ? (
           <div className="w-2 h-2 rounded-full bg-emerald-500 mb-2" title="In Stock"/>
        ) : (
           <div className="w-2 h-2 rounded-full bg-red-500 mb-2" title="No Stock"/>
        )}
      </div>

    </div>
  );
};

/**
 * Memoized ProductCard - Prevents re-renders when parent state changes
 * but product data hasn't. Critical for performance in virtualized grids.
 *
 * Without memo: Every parent state change re-renders all visible cards
 * With memo: Only cards with changed product data re-render
 *
 * Example performance gain: 1000 cards -> 99% fewer re-renders during scrolling
 */
export const ProductCard = memo(ProductCardComponent);
