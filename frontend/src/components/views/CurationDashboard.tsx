import React, { useState, useEffect, useCallback, useMemo } from "react";
import {
  Layers,
  Link2,
  CheckCircle,
  XCircle,
  ArrowLeft,
  RefreshCw,
  GitMerge,
  ChevronDown,
  ChevronRight,
  AlertTriangle,
  ImageIcon,
  Package,
  Filter,
} from "lucide-react";
import { useNavigationStore } from "../../store/navigationStore";
import { ImageWithFallback } from "../ImageWithFallback";
import { getBrandLogoUrl } from "../../lib/brandLogoHelper";
import { getBrandTheme } from "../../styles/brandThemes";

/* ──────────────────────────────────────────────
   Types for curation API responses
   ────────────────────────────────────────────── */

interface PendingRelationship {
  source_id: string;
  target_id: string;
  relationship_type: string;
  confidence: number;
  notes?: string;
  compatibility_notes?: string;
  source_name?: string;
  target_name?: string;
  source_image?: string;
  target_image?: string;
  source_brand?: string;
  target_brand?: string;
}

interface CurationStats {
  total_families: number;
  total_relationships: number;
  pending_review: number;
  confirmed_relationships: number;
  products_in_families: number;
  products_without_family: number;
  family_coverage_pct: number;
  products_with_accessories: number;
  accessory_coverage_pct: number;
  relationship_type_counts: Record<string, number>;
}

interface FamilyMember {
  id: string;
  name: string;
  variant_key?: string;
  image_url?: string;
}

interface FamilyData {
  id: string;
  brand: string;
  family_name: string;
  series?: string;
  generation?: string;
  member_count: number;
  variant_ids?: string[];
  members: FamilyMember[];
}

interface BrandGroup {
  brand: string;
  family_count: number;
  families: FamilyData[];
}

interface GraphOverview {
  total_families: number;
  total_relationships: number;
  products_in_families: number;
  total_products: number;
  brand_family_counts: Record<string, number>;
  graph_enabled: boolean;
}

/* ──────────────────────────────────────────────
   Brand Logo Component (official logos only)
   ────────────────────────────────────────────── */

const BrandLogo: React.FC<{
  brand: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}> = ({ brand, size = "sm", className = "" }) => {
  const logoUrl = getBrandLogoUrl(brand);
  const sizeClasses = {
    sm: "h-5 max-w-[20px]",
    md: "h-7 max-w-[48px]",
    lg: "h-10 max-w-[80px]",
  };

  if (!logoUrl) {
    const theme = getBrandTheme(brand);
    return (
      <div
        className={`flex items-center justify-center rounded ${size === "sm" ? "w-5 h-5 text-[9px]" : size === "md" ? "w-7 h-7 text-xs" : "w-10 h-10 text-sm"} font-black uppercase ${className}`}
        style={{
          backgroundColor: `${theme.primary}20`,
          color: theme.primary,
          border: `1px solid ${theme.primary}30`,
        }}
        title={brand}
      >
        {brand.charAt(0)}
      </div>
    );
  }

  return (
    <img
      src={logoUrl}
      alt={brand}
      title={brand}
      className={`${sizeClasses[size]} object-contain opacity-80 hover:opacity-100 transition-opacity ${className}`}
    />
  );
};

/* ──────────────────────────────────────────────
   Product Thumbnail with brand accent border
   ────────────────────────────────────────────── */

const ProductThumb: React.FC<{
  imageUrl?: string;
  name: string;
  brand?: string;
  size?: number;
}> = ({ imageUrl, name, brand, size = 40 }) => {
  const theme = brand ? getBrandTheme(brand) : null;
  const borderColor = theme ? theme.primary : "#475569";

  return (
    <div
      className="rounded-lg overflow-hidden shrink-0 bg-slate-800"
      style={{
        width: size,
        height: size,
        border: `2px solid ${borderColor}40`,
      }}
    >
      {imageUrl ? (
        <ImageWithFallback
          src={imageUrl}
          alt={name}
          className="w-full h-full object-contain p-0.5"
        />
      ) : (
        <div className="w-full h-full flex items-center justify-center bg-slate-800/80">
          <ImageIcon size={size * 0.35} className="text-zinc-600" />
        </div>
      )}
    </div>
  );
};

/* ──────────────────────────────────────────────
   Relationship type display config
   ────────────────────────────────────────────── */

const RELATIONSHIP_LABELS: Record<string, { label: string; emoji: string }> = {
  accessory_for: { label: "Accessory", emoji: "🔗" },
  variant_of: { label: "Variant", emoji: "🔀" },
  compatible_with: { label: "Compatible", emoji: "🤝" },
  successor_of: { label: "Successor", emoji: "⬆️" },
  bundle_with: { label: "Bundle", emoji: "📦" },
  alternative_to: { label: "Alternative", emoji: "↔️" },
};

/* ──────────────────────────────────────────────
   CurationDashboard Component
   ────────────────────────────────────────────── */

export const CurationDashboard = () => {
  const { goToGalaxy, openProductPage } = useNavigationStore();

  // Data states
  const [pending, setPending] = useState<PendingRelationship[]>([]);
  const [stats, setStats] = useState<CurationStats | null>(null);
  const [brandGroups, setBrandGroups] = useState<BrandGroup[]>([]);
  const [families, setFamilies] = useState<FamilyData[]>([]);
  const [overview, setOverview] = useState<GraphOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<
    "pending" | "families" | "overview"
  >("overview");
  const [expandedFamily, setExpandedFamily] = useState<string | null>(null);
  const [expandedBrand, setExpandedBrand] = useState<string | null>(null);
  const [pendingBrandFilter, setPendingBrandFilter] = useState<string | null>(
    null,
  );

  // Fetch all data
  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [pendingRes, statsRes, familiesRes, overviewRes] =
        await Promise.all([
          fetch("/api/curation/pending")
            .then((r) => r.json())
            .then((d) => d?.pending ?? d ?? [])
            .catch(() => []),
          fetch("/api/curation/stats")
            .then((r) => r.json())
            .catch(() => null),
          fetch("/api/curation/families")
            .then((r) => r.json())
            .catch(() => ({})),
          fetch("/api/curation/graph/overview")
            .then((r) => r.json())
            .catch(() => null),
        ]);
      setPending(Array.isArray(pendingRes) ? pendingRes : []);
      setStats(statsRes);
      if (familiesRes?.brands) {
        setBrandGroups(familiesRes.brands);
        setFamilies(familiesRes.families ?? []);
      } else {
        const flat = familiesRes?.families ?? familiesRes ?? [];
        setFamilies(Array.isArray(flat) ? flat : []);
        setBrandGroups([]);
      }
      setOverview(overviewRes);
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Unique brands in pending for filter
  const pendingBrands = useMemo(() => {
    const brands = new Set<string>();
    pending.forEach((rel) => {
      if (rel.source_brand) brands.add(rel.source_brand);
      if (rel.target_brand) brands.add(rel.target_brand);
    });
    return Array.from(brands).sort((a, b) => a.localeCompare(b));
  }, [pending]);

  // Filtered pending
  const filteredPending = useMemo(() => {
    if (!pendingBrandFilter) return pending;
    return pending.filter(
      (rel) =>
        rel.source_brand === pendingBrandFilter ||
        rel.target_brand === pendingBrandFilter,
    );
  }, [pending, pendingBrandFilter]);

  // Actions
  const confirmRelationship = async (rel: PendingRelationship) => {
    try {
      await fetch("/api/curation/relationships", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source_id: rel.source_id,
          target_id: rel.target_id,
          relationship_type: rel.relationship_type,
          confidence: 1.0,
        }),
      });
      setPending((prev) =>
        prev.filter(
          (p) =>
            !(p.source_id === rel.source_id && p.target_id === rel.target_id),
        ),
      );
    } catch {
      /* ignore */
    }
  };

  const rejectRelationship = async (rel: PendingRelationship) => {
    try {
      await fetch(
        `/api/curation/relationships?source_id=${encodeURIComponent(rel.source_id)}&target_id=${encodeURIComponent(rel.target_id)}&relationship_type=${encodeURIComponent(rel.relationship_type)}`,
        { method: "DELETE" },
      );
      setPending((prev) =>
        prev.filter(
          (p) =>
            !(p.source_id === rel.source_id && p.target_id === rel.target_id),
        ),
      );
    } catch {
      /* ignore */
    }
  };

  const typeColors: Record<string, string> = {
    variant_of: "text-blue-400 bg-blue-500/15 border-blue-500/20",
    accessory_for: "text-emerald-400 bg-emerald-500/15 border-emerald-500/20",
    compatible_with: "text-violet-400 bg-violet-500/15 border-violet-500/20",
    successor_of: "text-amber-400 bg-amber-500/15 border-amber-500/20",
    bundle_with: "text-cyan-400 bg-cyan-500/15 border-cyan-500/20",
    alternative_to: "text-orange-400 bg-orange-500/15 border-orange-500/20",
  };

  return (
    <div className="w-full h-full bg-slate-950 rounded-xl overflow-hidden flex flex-col shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800/60 bg-gradient-to-r from-slate-900 to-slate-900/80 shrink-0">
        <div className="flex items-center gap-4">
          <button
            onClick={goToGalaxy}
            className="p-2 hover:bg-slate-800 rounded-lg transition-all duration-200 text-zinc-400 hover:text-white"
            title="Back to Galaxy"
          >
            <ArrowLeft size={20} />
          </button>
          <div className="h-6 w-px bg-slate-700/50" />
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-violet-500 to-blue-600 flex items-center justify-center shadow-md">
              <GitMerge size={18} className="text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">
                Product Graph Curation
              </h1>
              <p className="text-[10px] text-zinc-500 uppercase tracking-wider">
                Manage families, relationships & variants
              </p>
            </div>
          </div>
        </div>
        <button
          onClick={fetchData}
          className="p-2 hover:bg-slate-800 rounded-lg transition-all text-zinc-500 hover:text-white"
          title="Refresh"
        >
          <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
        </button>
      </div>

      {/* Tab Strip */}
      <div className="flex gap-1 px-6 pt-3 pb-0 shrink-0">
        {(
          [
            { key: "overview", label: "Overview", icon: Layers },
            {
              key: "pending",
              label: `Pending Review${pending.length > 0 ? ` (${pending.length.toLocaleString()})` : ""}`,
              icon: AlertTriangle,
            },
            {
              key: "families",
              label: `Families${families.length > 0 ? ` (${families.length})` : ""}`,
              icon: Link2,
            },
          ] as const
        ).map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={`px-4 py-2 text-xs font-semibold rounded-t-lg flex items-center gap-2 transition-all ${
              activeTab === key
                ? "bg-slate-900 text-white border border-slate-700/50 border-b-0"
                : "text-zinc-500 hover:text-zinc-300 hover:bg-slate-900/40"
            }`}
          >
            <Icon size={14} />
            {label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6 pt-4 space-y-4 border-t border-slate-700/50 -mt-px">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <RefreshCw
                size={32}
                className="text-zinc-600 animate-spin mx-auto mb-3"
              />
              <p className="text-zinc-500 text-sm">Loading graph data...</p>
            </div>
          </div>
        ) : activeTab === "overview" ? (
          /* ═══════ OVERVIEW TAB ═══════ */
          <div className="space-y-6">
            <div className="grid grid-cols-4 gap-4">
              {[
                {
                  label: "Product Families",
                  value: stats?.total_families ?? overview?.total_families ?? 0,
                  color: "blue",
                  sub: `${stats?.family_coverage_pct ?? 0}% coverage`,
                },
                {
                  label: "Relationships",
                  value: stats?.total_relationships ?? 0,
                  color: "violet",
                  sub: `${Object.keys(stats?.relationship_type_counts ?? {}).length} types`,
                },
                {
                  label: "In Families",
                  value: stats?.products_in_families ?? 0,
                  color: "emerald",
                  sub: `${stats?.products_without_family ?? 0} orphans`,
                },
                {
                  label: "Pending Review",
                  value: stats?.pending_review ?? 0,
                  color: "amber",
                  sub: `${stats?.confirmed_relationships ?? 0} confirmed`,
                },
              ].map((card) => {
                const colorMap: Record<string, string> = {
                  blue: "text-blue-400",
                  violet: "text-violet-400",
                  emerald: "text-emerald-400",
                  amber: "text-amber-400",
                };
                return (
                  <div
                    key={card.label}
                    className="bg-slate-900/80 rounded-xl p-5 border border-slate-800/60"
                  >
                    <p className="text-[10px] text-zinc-500 uppercase tracking-wider font-semibold mb-2">
                      {card.label}
                    </p>
                    <p
                      className={`text-3xl font-black tabular-nums ${colorMap[card.color] ?? "text-zinc-400"}`}
                    >
                      {typeof card.value === "number"
                        ? card.value.toLocaleString()
                        : card.value}
                    </p>
                    <p className="text-[10px] text-zinc-600 mt-1">{card.sub}</p>
                  </div>
                );
              })}
            </div>

            {/* Relationship Type Breakdown */}
            {stats?.relationship_type_counts && (
              <div className="bg-slate-900/80 rounded-xl p-6 border border-slate-800/60">
                <h2 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                  <Link2 size={14} className="text-violet-400" />
                  Relationship Types
                </h2>
                <div className="grid grid-cols-3 gap-3">
                  {Object.entries(stats.relationship_type_counts).map(
                    ([type, count]) => {
                      const info = RELATIONSHIP_LABELS[type] ?? {
                        label: type.replace(/_/g, " "),
                        emoji: "🔗",
                      };
                      return (
                        <div
                          key={type}
                          className={`rounded-lg p-3 border ${typeColors[type] ?? "bg-zinc-800 border-zinc-700"} text-center`}
                        >
                          <p className="text-lg font-black tabular-nums">
                            {count.toLocaleString()}
                          </p>
                          <p className="text-[10px] uppercase tracking-wider mt-0.5 opacity-80">
                            {info.emoji} {info.label}
                          </p>
                        </div>
                      );
                    },
                  )}
                </div>
              </div>
            )}

            {/* Brand Family Overview */}
            {overview?.brand_family_counts && (
              <div className="bg-slate-900/80 rounded-xl p-6 border border-slate-800/60">
                <h2 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                  <Package size={14} className="text-blue-400" />
                  Families by Brand
                </h2>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(overview.brand_family_counts)
                    .sort(([, a], [, b]) => b - a)
                    .map(([brand, count]) => {
                      const theme = getBrandTheme(brand);
                      return (
                        <div
                          key={brand}
                          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all hover:scale-105"
                          style={{
                            backgroundColor: `${theme.primary}10`,
                            borderColor: `${theme.primary}25`,
                          }}
                        >
                          <BrandLogo brand={brand} size="sm" />
                          <span
                            className="text-xs font-bold capitalize"
                            style={{ color: theme.primary }}
                          >
                            {brand}
                          </span>
                          <span className="text-[10px] text-zinc-500 font-mono">
                            {count}
                          </span>
                        </div>
                      );
                    })}
                </div>
              </div>
            )}
          </div>
        ) : activeTab === "pending" ? (
          /* ═══════ PENDING REVIEW TAB ═══════ */
          <div className="space-y-3">
            {/* Brand filter bar */}
            {pendingBrands.length > 1 && (
              <div className="flex items-center gap-2 flex-wrap pb-2 border-b border-slate-800/40">
                <Filter size={12} className="text-zinc-500" />
                <button
                  onClick={() => setPendingBrandFilter(null)}
                  className={`px-2 py-1 rounded text-[10px] font-semibold transition-all ${
                    !pendingBrandFilter
                      ? "bg-white/10 text-white"
                      : "text-zinc-500 hover:text-zinc-300"
                  }`}
                >
                  All ({pending.length.toLocaleString()})
                </button>
                {pendingBrands.map((brand) => {
                  const theme = getBrandTheme(brand);
                  const count = pending.filter(
                    (r) => r.source_brand === brand || r.target_brand === brand,
                  ).length;
                  const isActive = pendingBrandFilter === brand;
                  return (
                    <button
                      key={brand}
                      onClick={() =>
                        setPendingBrandFilter(isActive ? null : brand)
                      }
                      className={`flex items-center gap-1.5 px-2 py-1 rounded text-[10px] font-semibold transition-all ${
                        isActive
                          ? "text-white"
                          : "text-zinc-500 hover:text-zinc-300"
                      }`}
                      style={
                        isActive
                          ? {
                              backgroundColor: `${theme.primary}20`,
                              border: `1px solid ${theme.primary}40`,
                              color: theme.primary,
                            }
                          : {}
                      }
                    >
                      <BrandLogo brand={brand} size="sm" />
                      <span className="capitalize">{brand}</span>
                      <span className="opacity-50">{count}</span>
                    </button>
                  );
                })}
              </div>
            )}

            {filteredPending.length === 0 ? (
              <div className="text-center py-16">
                <CheckCircle
                  size={40}
                  className="text-emerald-400/30 mx-auto mb-3"
                />
                <p className="text-zinc-500 text-sm">
                  {pendingBrandFilter
                    ? `No pending reviews for ${pendingBrandFilter}`
                    : "All relationships reviewed"}
                </p>
              </div>
            ) : (
              filteredPending.map((rel, idx) => {
                const info = RELATIONSHIP_LABELS[rel.relationship_type] ?? {
                  label: rel.relationship_type.replace(/_/g, " "),
                  emoji: "🔗",
                };
                return (
                  <div
                    key={`${rel.source_id}-${rel.target_id}-${idx}`}
                    className="bg-slate-900/80 rounded-xl p-4 border border-slate-800/60 flex items-center gap-4 hover:border-slate-700/60 transition-colors group"
                  >
                    {/* Source product */}
                    <button
                      onClick={() => openProductPage(rel.source_id)}
                      className="flex items-center gap-3 flex-1 min-w-0 text-left hover:bg-slate-800/30 rounded-lg p-2 -m-2 transition-colors"
                    >
                      <ProductThumb
                        imageUrl={rel.source_image}
                        name={rel.source_name || ""}
                        brand={rel.source_brand}
                        size={44}
                      />
                      <div className="min-w-0 flex-1">
                        <p className="text-xs text-white font-medium truncate">
                          {rel.source_name || rel.source_id}
                        </p>
                        {rel.source_brand && (
                          <p className="text-[10px] text-zinc-500 truncate">
                            {rel.source_brand}
                          </p>
                        )}
                      </div>
                    </button>

                    {/* Relationship badge */}
                    <div className="shrink-0 flex flex-col items-center gap-1 min-w-[90px]">
                      <span
                        className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded border whitespace-nowrap ${typeColors[rel.relationship_type] || "text-zinc-400 bg-zinc-800 border-zinc-700"}`}
                      >
                        {info.emoji} {info.label}
                      </span>
                      <div className="flex items-center gap-1.5">
                        <div className="h-0.5 w-8 bg-zinc-700 rounded relative overflow-hidden">
                          <div
                            className="h-full rounded"
                            style={{
                              width: `${(rel.confidence * 100).toFixed(0)}%`,
                              backgroundColor:
                                rel.confidence >= 0.8
                                  ? "#10b981"
                                  : rel.confidence >= 0.6
                                    ? "#f59e0b"
                                    : "#ef4444",
                            }}
                          />
                        </div>
                        <span className="text-[9px] text-zinc-600 tabular-nums font-mono">
                          {(rel.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>

                    {/* Target product */}
                    <button
                      onClick={() => openProductPage(rel.target_id)}
                      className="flex items-center gap-3 flex-1 min-w-0 text-left hover:bg-slate-800/30 rounded-lg p-2 -m-2 transition-colors"
                    >
                      <ProductThumb
                        imageUrl={rel.target_image}
                        name={rel.target_name || ""}
                        brand={rel.target_brand}
                        size={44}
                      />
                      <div className="min-w-0 flex-1">
                        <p className="text-xs text-white font-medium truncate">
                          {rel.target_name || rel.target_id}
                        </p>
                        {rel.target_brand && (
                          <p className="text-[10px] text-zinc-500 truncate">
                            {rel.target_brand}
                          </p>
                        )}
                      </div>
                    </button>

                    {/* Actions */}
                    <div className="flex gap-1.5 shrink-0 opacity-60 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => confirmRelationship(rel)}
                        className="p-2 rounded-lg bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-400 transition-all"
                        title="Confirm relationship"
                      >
                        <CheckCircle size={16} />
                      </button>
                      <button
                        onClick={() => rejectRelationship(rel)}
                        className="p-2 rounded-lg bg-red-600/20 hover:bg-red-600/40 text-red-400 transition-all"
                        title="Reject relationship"
                      >
                        <XCircle size={16} />
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        ) : (
          /* ═══════ FAMILIES TAB (Grouped by Brand) ═══════ */
          <div className="space-y-4">
            {(brandGroups.length > 0
              ? brandGroups
              : (() => {
                  // Client-side grouping fallback
                  const grouped: Record<string, FamilyData[]> = {};
                  families.forEach((fam) => {
                    const key = fam.brand || "Unknown";
                    if (!grouped[key]) grouped[key] = [];
                    grouped[key].push(fam);
                  });
                  return Object.entries(grouped)
                    .sort(([a], [b]) => a.localeCompare(b))
                    .map(([brand, fams]) => ({
                      brand,
                      family_count: fams.length,
                      families: fams,
                    }));
                })()
            ).map((bg) => {
              const theme = getBrandTheme(bg.brand);
              const isExpanded = expandedBrand === bg.brand;
              return (
                <div
                  key={bg.brand}
                  className="rounded-xl overflow-hidden border"
                  style={{ borderColor: `${theme.primary}20` }}
                >
                  {/* Brand Header */}
                  <button
                    onClick={() =>
                      setExpandedBrand(isExpanded ? null : bg.brand)
                    }
                    className="w-full flex items-center gap-4 px-5 py-3 transition-colors text-left"
                    style={{
                      background: `linear-gradient(135deg, ${theme.primary}08 0%, ${theme.primary}03 100%)`,
                    }}
                  >
                    <BrandLogo brand={bg.brand} size="md" />
                    <div className="flex-1 min-w-0">
                      <p
                        className="text-sm font-black uppercase tracking-wide"
                        style={{ color: theme.primary }}
                      >
                        {bg.brand}
                      </p>
                      <p className="text-[10px] text-zinc-500">
                        {bg.family_count} famil
                        {bg.family_count !== 1 ? "ies" : "y"} ·{" "}
                        {bg.families.reduce(
                          (sum, f) => sum + (f.members?.length ?? 0),
                          0,
                        )}{" "}
                        products
                      </p>
                    </div>
                    <div
                      className="text-xs font-bold tabular-nums px-2 py-0.5 rounded"
                      style={{
                        backgroundColor: `${theme.primary}15`,
                        color: theme.primary,
                      }}
                    >
                      {bg.family_count}
                    </div>
                    {isExpanded ? (
                      <ChevronDown size={16} className="text-zinc-500" />
                    ) : (
                      <ChevronRight size={16} className="text-zinc-500" />
                    )}
                  </button>

                  {/* Expanded families */}
                  {isExpanded && (
                    <div className="border-t border-slate-800/40 bg-slate-950/40">
                      {bg.families.map((fam) => (
                        <div
                          key={fam.id}
                          className="border-b border-slate-800/20 last:border-b-0"
                        >
                          <button
                            onClick={() =>
                              setExpandedFamily(
                                expandedFamily === fam.id ? null : fam.id,
                              )
                            }
                            className="w-full flex items-center gap-3 px-6 py-2.5 hover:bg-slate-800/20 transition-colors text-left"
                          >
                            <Layers size={12} className="text-zinc-600" />
                            <div className="flex-1 min-w-0">
                              <p className="text-xs text-white font-semibold truncate">
                                {fam.family_name}
                              </p>
                              <p className="text-[10px] text-zinc-600">
                                {[
                                  fam.series,
                                  fam.generation
                                    ? `Gen ${fam.generation}`
                                    : null,
                                ]
                                  .filter(Boolean)
                                  .join(" · ") || "Base series"}
                              </p>
                            </div>
                            <span className="text-[10px] text-zinc-500 tabular-nums">
                              {fam.members?.length ?? 0} variant
                              {(fam.members?.length ?? 0) !== 1 ? "s" : ""}
                            </span>
                            {expandedFamily === fam.id ? (
                              <ChevronDown
                                size={12}
                                className="text-zinc-600"
                              />
                            ) : (
                              <ChevronRight
                                size={12}
                                className="text-zinc-600"
                              />
                            )}
                          </button>

                          {expandedFamily === fam.id &&
                            fam.members?.length > 0 && (
                              <div className="px-6 py-3 bg-slate-950/60">
                                <div className="grid grid-cols-4 gap-2">
                                  {fam.members.map((member) => (
                                    <button
                                      key={member.id}
                                      onClick={() => openProductPage(member.id)}
                                      className="flex items-center gap-2 bg-slate-800/40 hover:bg-slate-800/70 rounded-lg p-2 border border-slate-700/30 hover:border-opacity-60 transition-all text-left"
                                      style={{
                                        borderColor: `${theme.primary}20`,
                                      }}
                                    >
                                      <ProductThumb
                                        imageUrl={member.image_url}
                                        name={member.name}
                                        brand={bg.brand}
                                        size={36}
                                      />
                                      <div className="min-w-0 flex-1">
                                        <p className="text-[11px] text-white font-medium truncate">
                                          {member.name}
                                        </p>
                                        {member.variant_key && (
                                          <span
                                            className="text-[9px] font-semibold"
                                            style={{ color: theme.primary }}
                                          >
                                            {member.variant_key}
                                          </span>
                                        )}
                                      </div>
                                    </button>
                                  ))}
                                </div>
                              </div>
                            )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
            {families.length === 0 && brandGroups.length === 0 && (
              <div className="text-center py-16">
                <Layers size={40} className="text-zinc-600/30 mx-auto mb-3" />
                <p className="text-zinc-500 text-sm">
                  No product families discovered yet
                </p>
                <p className="text-zinc-600 text-xs mt-1">
                  Run the pipeline to discover product families automatically
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
