/**
 * ProductIntelligenceCard — JIT Interactive "Mini-PDP" for the Spectrum Module
 *
 * Replaces the passive hover list with a structured card:
 * - Header: Family name + inventory status across variants
 * - Variant selector: Chips to switch model (88 Keys, 73 Keys, etc.) and update price/stock instantly
 * - Essential Pairings: Curated accessories designed for this product
 * - Intel: Opportunities (e.g. open box, deals) when available
 */

import React, { useMemo, useState } from "react";
import { Maximize2, Package } from "lucide-react";
import {
  useConductorCatalog,
  useProductVariants,
  useProductRelationships,
} from "../../hooks/useConductorCatalog";
import type { ConductorProduct } from "../../hooks/useConductorCatalog";

// ═══════════════════════════════════════════════════════════════════════════
// Stock indicator — JIT: show availability across variants when we have data
// ═══════════════════════════════════════════════════════════════════════════

function StockIndicator({ product }: { product: ConductorProduct }) {
  const hasPrice = product.price > 0;
  return (
    <span
      className={`text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded ${
        hasPrice
          ? "bg-emerald-500/20 text-emerald-400"
          : "bg-amber-500/20 text-amber-400"
      }`}
    >
      {hasPrice ? "Available" : "On request"}
    </span>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Accessory thumbnail — one item in "Essential Pairings"
// ═══════════════════════════════════════════════════════════════════════════

function AccessoryThumbnail({
  item,
  onOpen,
}: {
  item: ConductorProduct;
  onOpen: (id: string) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onOpen(item.id)}
      className="flex flex-col items-center gap-0.5 flex-shrink-0 w-14 rounded border border-zinc-700 bg-zinc-900 overflow-hidden hover:border-emerald-500 transition-colors group"
      title={item.name}
    >
      {item.image_url ? (
        <img
          src={item.image_url}
          alt=""
          className="w-full h-10 object-contain bg-white"
        />
      ) : (
        <div className="w-full h-10 flex items-center justify-center bg-zinc-800">
          <span className="text-[8px] text-zinc-500 font-bold">ACC</span>
        </div>
      )}
      <span className="text-[8px] text-zinc-500 truncate w-full px-0.5 text-center group-hover:text-emerald-400 transition-colors">
        {item.name?.split(" ").slice(0, 2).join(" ") || "—"}
      </span>
    </button>
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// ProductIntelligenceCard
// ═══════════════════════════════════════════════════════════════════════════

export interface ProductIntelligenceCardProps {
  product: ConductorProduct;
  familyProducts: ConductorProduct[];
  openProductPage: (id: string) => void;
}

export const ProductIntelligenceCard = React.memo(function ProductIntelligenceCard({
  product,
  familyProducts,
  openProductPage,
}: ProductIntelligenceCardProps) {
  const { families } = useConductorCatalog();
  const { variants } = useProductVariants(product.id);
  const { accessories } = useProductRelationships(product.id);

  const [selectedVariant, setSelectedVariant] = useState<ConductorProduct>(product);

  const allVariants = useMemo(() => {
    const seen = new Set<string>([product.id]);
    const result: ConductorProduct[] = [product];
    for (const p of familyProducts) {
      if (!seen.has(p.id)) {
        result.push(p);
        seen.add(p.id);
      }
    }
    for (const v of variants) {
      if (!seen.has(v.id)) {
        result.push(v);
        seen.add(v.id);
      }
    }
    return result;
  }, [product, familyProducts, variants]);

  const familyName =
    (product.family_id && families[product.family_id]?.family_name) ||
    product.name?.split(" ").slice(0, 3).join(" ") ||
    product.name ||
    "Product";

  const displayProduct = allVariants.some((v) => v.id === selectedVariant.id)
    ? selectedVariant
    : product;

  return (
    <div className="jit-card-container w-full space-y-4 flex flex-col">
      {/* 1. Header & Status */}
      <div className="flex justify-between items-center gap-2">
        <h3 className="font-bold text-lg text-white truncate" title={familyName}>
          {familyName}
        </h3>
        <StockIndicator product={displayProduct} />
      </div>

      {/* Price for selected variant */}
      <div className="space-y-0.5">
        {displayProduct.price > 0 ? (
          <>
            <div className="text-3xl lg:text-4xl font-black text-white tracking-tighter tabular-nums">
              ₪{displayProduct.price.toLocaleString("he-IL")}
            </div>
            <div className="text-[10px] text-zinc-500 font-bold tracking-widest uppercase">
              Price (VAT Included)
            </div>
          </>
        ) : (
          <>
            <div className="text-xl font-bold text-zinc-400 tracking-tight">
              Price on request
            </div>
            {displayProduct.market_price_estimate > 0 && (
              <div className="flex items-center gap-1.5 mt-1">
                <span className="text-[10px] text-amber-500/70 font-bold uppercase tracking-widest">
                  Est. market:
                </span>
                <span className="text-sm text-amber-400/60 font-mono">
                  ~₪{displayProduct.market_price_estimate.toLocaleString("he-IL")}
                </span>
              </div>
            )}
            <div className="text-[10px] text-zinc-600 font-bold tracking-widest uppercase">
              Contact Halilit for pricing
            </div>
          </>
        )}
      </div>

      <div className="w-full h-px bg-zinc-800/50" />

      {/* 2. Fashion-style variant selector */}
      {allVariants.length > 1 && (
        <div className="variant-selector space-y-1.5">
          <span className="text-xs text-zinc-500 uppercase tracking-widest font-bold">
            Select model
          </span>
          <div className="flex flex-wrap gap-2">
            {allVariants.map((v) => (
              <button
                key={v.id}
                type="button"
                onClick={() => {
                  setSelectedVariant(v);
                }}
                className={`chip px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  v.id === selectedVariant.id
                    ? "bg-blue-500 text-white ring-1 ring-blue-400/50"
                    : "bg-zinc-800 text-zinc-300 hover:bg-zinc-700 hover:text-white border border-zinc-700"
                }`}
              >
                {v.variant_key || v.name?.split(" ").slice(-2).join(" ") || v.id.slice(0, 8)}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 3. Essential Pairings (smart accessories) */}
      {accessories.length > 0 && (
        <div className="smart-accessories bg-zinc-900/60 p-3 rounded-lg border border-zinc-800/50">
          <span className="text-xs font-bold text-zinc-400 uppercase tracking-widest flex items-center gap-1.5 mb-2">
            <Package className="w-3 h-3 text-emerald-400" />
            Essential pairings
          </span>
          <div className="grid grid-cols-3 gap-2">
            {accessories.slice(0, 3).map((acc) => (
              <AccessoryThumbnail
                key={acc.id}
                item={acc}
                onOpen={openProductPage}
              />
            ))}
          </div>
        </div>
      )}

      {/* 4. Intel — tier, availability hint; extend later with open box / deals when backend supports */}
      <div className="intel text-[10px] text-zinc-400 space-y-0.5">
        {displayProduct.tier && (
          <span className="font-medium uppercase tracking-widest text-zinc-500">
            Tier: <span className="text-amber-400/90 capitalize">{displayProduct.tier}</span>
          </span>
        )}
        {!displayProduct.price && displayProduct.price_eilat > 0 && (
          <span className="block text-amber-400/80">
            Eilat price available — contact for quote
          </span>
        )}
      </div>

      <div className="flex-1 min-h-[1rem]" />

      <button
        type="button"
        onClick={() => openProductPage(displayProduct.id)}
        className="w-full bg-gradient-to-r from-amber-500 to-amber-400 hover:from-amber-400 hover:to-amber-300 text-black font-extrabold py-3 uppercase text-sm tracking-widest transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] flex items-center justify-center gap-2 rounded-lg shadow-lg shadow-amber-900/30"
      >
        <Maximize2 className="w-4 h-4" />
        <span>View details</span>
      </button>
    </div>
  );
});
