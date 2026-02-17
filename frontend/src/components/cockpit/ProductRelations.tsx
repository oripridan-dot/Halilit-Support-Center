/**
 * ProductRelations — Unified relations UI with confidence tiers.
 * Shows Verified (manufacturer), Store recommended, and Likely compatible
 * in one section with clear badges and one grid per tier.
 */

import React, { useMemo } from "react";
import { motion } from "framer-motion";
import { Link2, CheckCircle, Store, AlertCircle } from "lucide-react";
import { ImageWithFallback } from "../ImageWithFallback";

const OFFICIAL_SOURCES = ["official", "official_text_match", "official_url_match"];

export interface RelatedProduct {
  id: string;
  name: string;
  price?: number;
  image_url?: string;
  /** accessory_for | compatible_with | alternative_to */
  relationType: "accessory" | "compatible" | "alternative";
}

export interface RelationMeta {
  confidence: number;
  sources_verified: string[];
}

type Tier = "verified" | "store" | "likely";

function getTier(meta: RelationMeta | undefined): Tier {
  if (!meta) return "likely";
  const verified = (meta.sources_verified || []).some((s) =>
    OFFICIAL_SOURCES.includes(s),
  );
  if (verified || meta.confidence >= 0.95) return "verified";
  if (
    (meta.sources_verified || []).includes("commercial") ||
    meta.confidence >= 0.8
  )
    return "store";
  return "likely";
}

interface ProductRelationsProps {
  accessories: RelatedProduct[];
  compatible: RelatedProduct[];
  alternatives: RelatedProduct[];
  relationshipMeta: Record<string, RelationMeta>;
  brandColor?: string;
  onProductClick: (id: string) => void;
}

const TIER_CONFIG: Record<
  Tier,
  { label: string; icon: React.ReactNode; className: string; badge: string }
> = {
  verified: {
    label: "Verified compatible",
    icon: <CheckCircle size={12} aria-hidden />,
    className: "text-emerald-400 border-emerald-500/30 bg-emerald-500/10",
    badge: "Verified",
  },
  store: {
    label: "Store recommended",
    icon: <Store size={12} aria-hidden />,
    className: "text-blue-400 border-blue-500/30 bg-blue-500/10",
    badge: "Store",
  },
  likely: {
    label: "Likely compatible",
    icon: <AlertCircle size={12} aria-hidden />,
    className: "text-amber-400/90 border-amber-500/30 bg-amber-500/10",
    badge: "Check",
  },
};

function RelationProductCard({
  item,
  tier,
  index,
  brandColor,
  onProductClick,
}: {
  item: RelatedProduct;
  tier: Tier;
  index: number;
  brandColor: string;
  onProductClick: (id: string) => void;
}) {
  const config = TIER_CONFIG[tier];
  const typeLabel =
    item.relationType === "accessory"
      ? "Accessory"
      : item.relationType === "compatible"
        ? "Compatible"
        : "Alternative";

  return (
    <button
      type="button"
      onClick={() => onProductClick(item.id)}
      className="group shrink-0 w-36 bg-zinc-800/40 hover:bg-zinc-800/70 border border-zinc-700/40 rounded-xl p-3 transition-all duration-200 text-left focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-900 focus-visible:ring-white/50"
      aria-label={`${item.name}, ${typeLabel}, ${config.badge}`}
    >
      <div className="aspect-square bg-zinc-900/60 rounded-lg overflow-hidden mb-2 relative">
        <ImageWithFallback
          src={item.image_url || ""}
          alt={item.name || typeLabel}
          className="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-200"
        />
        <span
          className={`absolute bottom-1 right-1 text-[9px] font-bold px-1.5 py-0.5 rounded border ${config.className}`}
          title={config.label}
        >
          {config.badge}
        </span>
      </div>
      <p className="text-[11px] text-white font-medium truncate">{item.name}</p>
      <p className="text-[9px] text-zinc-500 mt-0.5">{typeLabel}</p>
      {item.price != null && item.price > 0 && (
        <p className="text-[10px] text-zinc-400 mt-1 font-medium">
          {"\u20AA"}
          {item.price.toLocaleString("he-IL")}
        </p>
      )}
    </button>
  );
}

export function ProductRelations({
  accessories,
  compatible,
  alternatives,
  relationshipMeta,
  brandColor = "#3b82f6",
  onProductClick,
}: ProductRelationsProps) {
  const { verified, store, likely } = useMemo(() => {
    const items: RelatedProduct[] = [
      ...accessories.map((a) => ({ ...a, relationType: "accessory" as const })),
      ...compatible.map((c) => ({ ...c, relationType: "compatible" as const })),
      ...alternatives.map((a) => ({ ...a, relationType: "alternative" as const })),
    ];
    const seen = new Set<string>();
    const deduped = items.filter((i) => {
      if (seen.has(i.id)) return false;
      seen.add(i.id);
      return true;
    });

    const verifiedList: RelatedProduct[] = [];
    const storeList: RelatedProduct[] = [];
    const likelyList: RelatedProduct[] = [];

    for (const item of deduped) {
      const meta = relationshipMeta[item.id];
      const tier = getTier(meta);
      if (tier === "verified") verifiedList.push(item);
      else if (tier === "store") storeList.push(item);
      else likelyList.push(item);
    }

    return { verified: verifiedList, store: storeList, likely: likelyList };
  }, [accessories, compatible, alternatives, relationshipMeta]);

  const hasAny = verified.length > 0 || store.length > 0 || likely.length > 0;
  if (!hasAny) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.26 }}
      className="rounded-xl bg-zinc-900/70 border border-zinc-800/50 p-5"
      role="region"
      aria-label="Related products"
    >
      <div className="flex items-center gap-2 mb-4">
        <Link2 size={14} style={{ color: brandColor }} aria-hidden />
        <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider">
          Related products
        </span>
        <span className="ml-auto text-[10px] text-zinc-600">
          {verified.length + store.length + likely.length} total
        </span>
      </div>

      {verified.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <span
              className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-1 rounded border ${TIER_CONFIG.verified.className}`}
            >
              {TIER_CONFIG.verified.icon}
              {TIER_CONFIG.verified.label}
            </span>
          </div>
          <div className="flex gap-3 overflow-x-auto pb-1">
            {verified.map((item, i) => (
              <RelationProductCard
                key={`verified-${item.id}-${i}`}
                item={item}
                tier="verified"
                index={i}
                brandColor={brandColor}
                onProductClick={onProductClick}
              />
            ))}
          </div>
        </div>
      )}

      {store.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <span
              className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-1 rounded border ${TIER_CONFIG.store.className}`}
            >
              {TIER_CONFIG.store.icon}
              {TIER_CONFIG.store.label}
            </span>
          </div>
          <div className="flex gap-3 overflow-x-auto pb-1">
            {store.map((item, i) => (
              <RelationProductCard
                key={`store-${item.id}-${i}`}
                item={item}
                tier="store"
                index={i}
                brandColor={brandColor}
                onProductClick={onProductClick}
              />
            ))}
          </div>
        </div>
      )}

      {likely.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span
              className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-1 rounded border ${TIER_CONFIG.likely.className}`}
            >
              {TIER_CONFIG.likely.icon}
              {TIER_CONFIG.likely.label}
            </span>
            <span className="text-[9px] text-zinc-500">
              Double-check before buying
            </span>
          </div>
          <div className="flex gap-3 overflow-x-auto pb-1">
            {likely.map((item, i) => (
              <RelationProductCard
                key={`likely-${item.id}-${i}`}
                item={item}
                tier="likely"
                index={i}
                brandColor={brandColor}
                onProductClick={onProductClick}
              />
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
