import React, { memo } from "react";
import type { OptimizedProduct } from "../../types";

const ProductCardComponent = ({ product }: { product: OptimizedProduct }) => {
  // Determine tier level for styling
  const tier = product.tier || "bronze";
  const tierLevel = tier.toUpperCase();

  return (
    <div
      className={`card tier-${tier} p-4 border rounded-md mb-2 bg-zinc-900 border-zinc-800 relative`}
    >
      {/* Quality badge */}
      {tier === "diamond" && (
        <div className="badge-diamond inline-flex items-center gap-1 text-xs font-bold text-emerald-400 bg-emerald-950/30 px-2 py-0.5 rounded border border-emerald-500/50 mb-2">
          💎 {tierLevel}
        </div>
      )}
      {tier === "gold" && (
        <div className="badge-gold inline-flex items-center gap-1 text-xs font-bold text-amber-400 bg-amber-950/30 px-2 py-0.5 rounded border border-amber-500/50 mb-2">
          🏆 {tierLevel}
        </div>
      )}
      {(tier === "silver" || tier === "bronze") && (
        <div className="badge-lower inline-flex items-center gap-1 text-xs font-bold text-slate-400 bg-slate-950/30 px-2 py-0.5 rounded border border-slate-500/50 mb-2">
          ⚠️ {tierLevel}
        </div>
      )}

      {/* HEADER: Product Name */}
      <h3 className="text-lg font-bold text-white mb-2">
        {product.name || "Unknown Product"}
      </h3>

      {/* Category and SKU */}
      <div className="text-sm text-zinc-400 mb-2">
        <p className="text-xs text-zinc-500">{product.category}</p>
      </div>

      {/* Pros/Strengths */}
      {product.pros && product.pros.length > 0 && (
        <div className="text-sm text-zinc-400 mt-3 mb-2">
          <p className="text-xs font-semibold text-emerald-500 mb-1">Pros:</p>
          <ul className="space-y-1">
            {product.pros.slice(0, 2).map((pro, idx) => (
              <li key={idx} className="flex items-start gap-2 text-xs">
                <span className="text-emerald-500 flex-shrink-0">✓</span>
                <span>{pro}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Price and Stock Status */}
      {(product.price || product.stock_status) && (
        <div className="text-xs text-zinc-500 mt-3 pt-3 border-t border-zinc-800">
          {product.price && (
            <p className="mb-1">
              <span className="font-semibold">{product.currency}</span>{" "}
              {product.price}
            </p>
          )}
          {product.stock_status && (
            <p>
              Stock: <span className="capitalize">{product.stock_status}</span>
            </p>
          )}
        </div>
      )}
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
