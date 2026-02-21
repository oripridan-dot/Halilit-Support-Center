/**
 * ProductRelations.tsx — Operator Console Edition
 * -------------------------------------------------
 * High-density, professional grid for product relationships.
 * Strategy: Function First, Trust Second
 * - Group by Intent: Accessories (add-ons) vs Alternatives (substitutes)
 * - Sort by Trust: Official > Store > Likely
 * - Compact grid for quick scanning (8–12 items at a glance)
 */

import React, { useMemo, useState } from "react";
import { motion } from "framer-motion";
import {
  CheckCircle2,
  Store,
  HelpCircle,
  Plug,
  ArrowLeftRight,
  PackageOpen,
} from "lucide-react";
import ImageWithFallback from "../ImageWithFallback";

// ----------------------------------------------------------------------
// 1. TYPES & CONFIGURATION
// ----------------------------------------------------------------------

const OFFICIAL_SOURCES = [
  "official",
  "official_text_match",
  "official_url_match",
  "brand_hierarchy",
];

export type RelationType =
  | "accessory"
  | "compatible"
  | "alternative"
  | "variant";
export type TrustLevel = "verified" | "store" | "likely";

export interface RelatedProduct {
  id: string;
  name: string;
  price?: number;
  image_url?: string;
  relationType: RelationType;
}

export interface RelationMeta {
  confidence: number;
  sources_verified: string[];
}

interface ProductRelationsProps {
  accessories: RelatedProduct[];
  compatible: RelatedProduct[];
  alternatives: RelatedProduct[];
  relationshipMeta: Record<string, RelationMeta>;
  onProductClick: (id: string) => void;
  brandColor?: string;
}

const TRUST_CONFIG: Record<
  TrustLevel,
  {
    label: string;
    icon: React.ComponentType<{ size?: number }>;
    style: string;
    border: string;
  }
> = {
  verified: {
    label: "Official",
    icon: CheckCircle2,
    style: "text-emerald-400 bg-emerald-500/10",
    border: "border-emerald-500/30 hover:border-emerald-400/60",
  },
  store: {
    label: "Store Pick",
    icon: Store,
    style: "text-blue-400 bg-blue-500/10",
    border: "border-blue-500/30 hover:border-blue-400/60",
  },
  likely: {
    label: "Possible",
    icon: HelpCircle,
    style: "text-zinc-500 bg-zinc-500/10",
    border: "border-zinc-800 hover:border-zinc-700",
  },
};

// ----------------------------------------------------------------------
// 2. LOGIC LAYER
// ----------------------------------------------------------------------

function getTrustLevel(meta: RelationMeta | undefined): TrustLevel {
  if (!meta) return "likely";
  const sources = meta.sources_verified || [];

  if (sources.some((s) => OFFICIAL_SOURCES.includes(s))) return "verified";
  if (sources.includes("commercial") || meta.confidence >= 0.85) return "store";
  return "likely";
}

function useRelationBuckets(props: ProductRelationsProps) {
  return useMemo(() => {
    const processItem = (item: RelatedProduct) => ({
      ...item,
      trust: getTrustLevel(props.relationshipMeta[item.id]),
    });

    const sortFn = (a: { trust: TrustLevel }, b: { trust: TrustLevel }) => {
      const score = (t: TrustLevel) =>
        t === "verified" ? 3 : t === "store" ? 2 : 1;
      return score(b.trust) - score(a.trust);
    };

    // Bucket 1: Add-ons (Accessories + Compatible) — "Complete the Sale"
    const addOns = [...props.accessories, ...props.compatible]
      .map(processItem)
      .sort(sortFn);

    // Bucket 2: Substitutes (Alternatives) — "Save the Sale"
    const substitutes = props.alternatives.map(processItem).sort(sortFn);

    return {
      addOns,
      substitutes,
      hasData: addOns.length > 0 || substitutes.length > 0,
    };
  }, [
    props.accessories,
    props.compatible,
    props.alternatives,
    props.relationshipMeta,
  ]);
}

// ----------------------------------------------------------------------
// 3. PRESENTATION LAYER
// ----------------------------------------------------------------------

const TabButton = ({
  isActive,
  onClick,
  icon: Icon,
  label,
  count,
  accent,
}: {
  isActive: boolean;
  onClick: () => void;
  icon: React.ComponentType<{ size?: number }>;
  label: string;
  count: number;
  accent: "emerald" | "blue";
}) => {
  const activeStyles =
    accent === "emerald"
      ? "border-emerald-500 text-white bg-emerald-500/5"
      : "border-blue-500 text-white bg-blue-500/5";
  const badgeStyles =
    accent === "emerald"
      ? "bg-emerald-500/20 text-emerald-300"
      : "bg-blue-500/20 text-blue-300";

  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex-1 flex items-center justify-center gap-2 py-3 text-xs font-medium border-b-2 transition-all duration-200
        ${isActive ? activeStyles : "border-transparent text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/40"}`}
      aria-pressed={isActive}
      aria-label={`${label}, ${count} items`}
    >
      <Icon
        size={14}
        className={
          isActive
            ? accent === "emerald"
              ? "text-emerald-400"
              : "text-blue-400"
            : "opacity-70"
        }
      />
      {label}
      <span
        className={`px-1.5 py-0.5 rounded-full text-[9px] font-mono ${
          isActive ? badgeStyles : "bg-zinc-800 text-zinc-500"
        }`}
      >
        {count}
      </span>
    </button>
  );
};

const RelationCard = ({
  item,
  trust,
  onClick,
}: {
  item: RelatedProduct;
  trust: TrustLevel;
  onClick: (id: string) => void;
}) => {
  const config = TRUST_CONFIG[trust];
  const Icon = config.icon;

  return (
    <button
      type="button"
      onClick={() => onClick(item.id)}
      className={`relative flex flex-col text-left group bg-zinc-900/40 rounded-lg p-2 transition-all duration-200 border ${config.border} focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-900 focus-visible:ring-white/50`}
      aria-label={`${item.name}, ${config.label}`}
    >
      {/* Trust Badge */}
      <div
        className={`absolute top-2 right-2 z-10 flex items-center gap-1 text-[9px] font-bold px-1.5 py-0.5 rounded border border-white/5 backdrop-blur-md shadow-sm ${config.style}`}
      >
        <Icon size={10} />
        <span>{config.label}</span>
      </div>

      {/* Image */}
      <div className="aspect-square w-full rounded bg-zinc-950/50 mb-2 overflow-hidden flex items-center justify-center">
        <ImageWithFallback
          src={item.image_url}
          alt={item.name}
          className="w-full h-full object-contain p-2 opacity-80 group-hover:opacity-100 group-hover:scale-105 transition-all duration-300"
        />
      </div>

      {/* Details */}
      <div className="w-full flex flex-col justify-between flex-1 min-h-[3rem]">
        <div className="text-[11px] font-medium text-zinc-300 leading-tight line-clamp-2 group-hover:text-white transition-colors">
          {item.name}
        </div>

        <div className="mt-2 flex items-center justify-between">
          {item.price != null && item.price > 0 ? (
            <span className="text-[11px] font-mono font-medium text-zinc-400 group-hover:text-blue-400 transition-colors">
              ₪{item.price.toLocaleString("he-IL")}
            </span>
          ) : (
            <span className="text-[10px] text-zinc-600 italic">
              Call for price
            </span>
          )}
        </div>
      </div>
    </button>
  );
};

const EmptyTabState = ({ message }: { message: string }) => (
  <div className="h-40 flex flex-col items-center justify-center text-zinc-600 gap-3">
    <div className="w-12 h-12 rounded-full bg-zinc-900 flex items-center justify-center">
      <PackageOpen size={20} className="opacity-40" />
    </div>
    <span className="text-xs font-medium">{message}</span>
  </div>
);

// ----------------------------------------------------------------------
// 4. MAIN COMPONENT (LAYOUT LAYER)
// ----------------------------------------------------------------------

export function ProductRelations(props: ProductRelationsProps) {
  const [activeTab, setActiveTab] = useState<"accessories" | "alternatives">(
    "accessories",
  );
  const { addOns, substitutes, hasData } = useRelationBuckets(props);

  if (!hasData) return null;

  const currentItems = activeTab === "accessories" ? addOns : substitutes;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.26 }}
      className="flex flex-col h-full bg-zinc-900/30 border border-zinc-800/50 rounded-xl overflow-hidden shadow-sm"
      role="region"
      aria-label="Related products: accessories and alternatives"
    >
      {/* Navigation Header */}
      <div className="flex items-center border-b border-zinc-800 bg-zinc-900/80 backdrop-blur-sm">
        <TabButton
          isActive={activeTab === "accessories"}
          onClick={() => setActiveTab("accessories")}
          icon={Plug}
          label="Accessories"
          count={addOns.length}
          accent="emerald"
        />
        <div className="w-px h-4 bg-zinc-800" aria-hidden />
        <TabButton
          isActive={activeTab === "alternatives"}
          onClick={() => setActiveTab("alternatives")}
          icon={ArrowLeftRight}
          label="Alternatives"
          count={substitutes.length}
          accent="blue"
        />
      </div>

      {/* Grid Content */}
      <div className="p-4 bg-zinc-950/30 min-h-[320px]">
        {currentItems.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
            {currentItems.map((item) => (
              <RelationCard
                key={item.id}
                item={item}
                trust={item.trust}
                onClick={props.onProductClick}
              />
            ))}
          </div>
        ) : (
          <EmptyTabState
            message={
              activeTab === "accessories"
                ? "No accessories found."
                : "No alternatives available."
            }
          />
        )}
      </div>
    </motion.div>
  );
}
