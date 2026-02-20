/**
 * ExplorerView — Natural Catalog Explorer (Spec 04 v1.0)
 *
 * Cascading Miller-Columns UX:
 *   Brands → Categories → Series → Products
 *
 * Designed for the Halilit Operator Console.
 * Data: useTaxonomyTree (derived from useConductorCatalog)
 * Navigation: useNavigationStore
 */

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ChevronRight,
  Layers,
  Package,
  Music,
  Tag,
  ArrowLeft,
  Telescope,
  AlertCircle,
} from "lucide-react";
import { useNavigationStore } from "../../store/navigationStore";
import { useTaxonomyTree } from "../../hooks/useTaxonomyTree";
import type {
  BrandNode,
  FamilyNode,
  SeriesNode,
  TaxonomyProduct,
} from "../../hooks/useTaxonomyTree";

// ─────────────────────────────────────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────────────────────────────────────

/** Generic list column with a header */
function ExplorerColumn({
  title,
  icon: Icon,
  items,
  selectedId,
  onSelect,
  columnIndex,
}: {
  title: string;
  icon: React.ElementType;
  items: { id: string; label: string; count: number }[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  columnIndex: number;
}) {
  return (
    <motion.div
      key={`col-${columnIndex}`}
      initial={{ x: 40, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -20, opacity: 0 }}
      transition={{ duration: 0.18, ease: "easeOut" }}
      className="flex flex-col w-52 shrink-0 bg-zinc-900 border-r border-zinc-800 overflow-hidden"
    >
      {/* Column header */}
      <div className="flex items-center gap-2 px-3 py-2.5 border-b border-zinc-800 bg-zinc-900/80 shrink-0">
        <Icon size={12} className="text-zinc-500 shrink-0" />
        <span className="text-[11px] font-semibold text-zinc-500 uppercase tracking-widest">
          {title}
        </span>
      </div>

      {/* Rows */}
      <div className="flex-1 overflow-y-auto">
        {items.length === 0 ? (
          <p className="text-zinc-700 text-xs italic p-4">No items found.</p>
        ) : (
          items.map((item) => {
            const active = item.id === selectedId;
            return (
              <button
                key={item.id}
                aria-label={`Select ${item.label}`}
                onClick={() => onSelect(item.id)}
                className={`w-full text-left flex items-center justify-between px-4 py-2.5 text-sm transition-all group
                  ${
                    active
                      ? "bg-emerald-500/10 border-l-2 border-emerald-500 text-white font-medium pl-[14px]"
                      : "text-zinc-400 hover:bg-zinc-800 hover:text-white border-l-2 border-transparent"
                  }`}
              >
                <span className="truncate flex-1 mr-2">{item.label}</span>
                <span
                  className={`text-[10px] px-1.5 py-0.5 rounded font-mono shrink-0
                  ${active ? "bg-emerald-500/20 text-emerald-400" : "bg-zinc-800 text-zinc-600 group-hover:text-zinc-400"}`}
                >
                  {item.count}
                </span>
              </button>
            );
          })
        )}
      </div>
    </motion.div>
  );
}

/** Stock dot indicator */
function StockDot({ stock }: { stock?: number | null }) {
  if (stock === null || stock === undefined) {
    return (
      <span className="inline-flex items-center gap-1 text-[10px] text-zinc-500">
        <span className="w-1.5 h-1.5 rounded-full bg-zinc-600 inline-block" />
        Unknown
      </span>
    );
  }
  if (stock === 0) {
    return (
      <span className="inline-flex items-center gap-1 text-[10px] text-red-400">
        <span className="w-1.5 h-1.5 rounded-full bg-red-500 inline-block" />
        Out of Stock
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 text-[10px] text-emerald-400">
      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" />
      In Stock
    </span>
  );
}

/** Single product card in the products column */
function ProductCard({
  product,
  onClick,
}: {
  product: TaxonomyProduct;
  onClick: () => void;
}) {
  const [imgError, setImgError] = useState(false);
  const hasPrice = product.price && product.price > 0;

  return (
    <button
      aria-label={`Open ${product.name}`}
      onClick={onClick}
      className="w-full text-left bg-zinc-900 border border-zinc-800 rounded-xl p-3 flex gap-3
        hover:bg-zinc-800 hover:border-zinc-700 transition-all group"
    >
      {/* Thumbnail */}
      <div className="w-14 h-14 bg-white rounded-lg p-1 shrink-0 flex items-center justify-center overflow-hidden">
        {product.image_url && !imgError ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="w-full h-full object-contain"
            onError={() => setImgError(true)}
          />
        ) : (
          <Package size={20} className="text-zinc-300 opacity-40" />
        )}
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-white truncate group-hover:text-emerald-300 transition-colors">
          {product.name}
        </p>
        <p className="text-[10px] font-mono text-zinc-500 mt-0.5 truncate">
          {product.id}
        </p>

        <div className="mt-1.5 flex items-center justify-between gap-2">
          <div>
            {hasPrice ? (
              <span className="text-sm font-bold text-white">
                ₪{product.price.toLocaleString()}
              </span>
            ) : (
              <span className="text-xs text-amber-400">Call for Price</span>
            )}
            {product.price_eilat > 0 && (
              <span className="text-[10px] text-zinc-500 ml-1.5">
                Eilat ₪{product.price_eilat.toLocaleString()}
              </span>
            )}
          </div>
          <StockDot stock={product.stock} />
        </div>
      </div>
    </button>
  );
}

/** Products column — flex-1, scrollable grid of cards */
function ProductsColumn({
  products,
  onSelect,
}: {
  products: TaxonomyProduct[];
  onSelect: (id: string) => void;
}) {
  return (
    <motion.div
      key="products-col"
      initial={{ x: 40, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: -20, opacity: 0 }}
      transition={{ duration: 0.18, ease: "easeOut" }}
      className="flex flex-col flex-1 min-w-0 bg-zinc-950 overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-2.5 border-b border-zinc-800 bg-zinc-900/50 shrink-0">
        <Package size={12} className="text-zinc-500" />
        <span className="text-[11px] font-semibold text-zinc-500 uppercase tracking-widest">
          Products
        </span>
        <span className="ml-2 text-[10px] px-1.5 py-0.5 bg-zinc-800 text-zinc-500 rounded font-mono">
          {products.length}
        </span>
      </div>

      {/* Cards */}
      <div className="flex-1 overflow-y-auto p-3">
        {products.length === 0 ? (
          <p className="text-zinc-700 text-xs italic p-4">
            No products in this series.
          </p>
        ) : (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-2">
            {products.map((p) => (
              <ProductCard
                key={p.id}
                product={p}
                onClick={() => onSelect(p.id)}
              />
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}

/** Skeleton column */
function SkeletonColumn({ width = "w-52" }: { width?: string }) {
  return (
    <div
      className={`${width} flex flex-col bg-zinc-900 border-r border-zinc-800 shrink-0`}
    >
      <div className="h-9 border-b border-zinc-800 bg-zinc-900/80" />
      <div className="p-3 space-y-2">
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={i}
            className="h-8 rounded bg-zinc-800 animate-pulse"
            style={{ opacity: 1 - i * 0.08 }}
          />
        ))}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main component
// ─────────────────────────────────────────────────────────────────────────────

const ExplorerView: React.FC = () => {
  const { goToDashboard, goToProduct } = useNavigationStore();
  const { tree, isLoading } = useTaxonomyTree();

  // Drill-down state — local (not persisted to URL for now)
  const [selectedBrandId, setSelectedBrandId] = useState<string | null>(null);
  const [selectedFamilyId, setSelectedFamilyId] = useState<string | null>(null);
  const [selectedSeriesId, setSelectedSeriesId] = useState<string | null>(null);

  // Resolve selected nodes
  const selectedBrand: BrandNode | null =
    tree.brands.find((b) => b.id === selectedBrandId) ?? null;

  const selectedFamily: FamilyNode | null =
    selectedBrand?.families.find((f) => f.id === selectedFamilyId) ?? null;

  const selectedSeries: SeriesNode | null =
    selectedFamily?.series.find((s) => s.id === selectedSeriesId) ?? null;

  // Breadcrumb segments
  const breadcrumbs: { label: string; onClick: () => void }[] = [
    {
      label: "Explorer",
      onClick: () => {
        setSelectedBrandId(null);
        setSelectedFamilyId(null);
        setSelectedSeriesId(null);
      },
    },
  ];
  if (selectedBrand) {
    breadcrumbs.push({
      label: selectedBrand.label,
      onClick: () => {
        setSelectedFamilyId(null);
        setSelectedSeriesId(null);
      },
    });
  }
  if (selectedFamily) {
    breadcrumbs.push({
      label: selectedFamily.label,
      onClick: () => setSelectedSeriesId(null),
    });
  }
  if (selectedSeries) {
    breadcrumbs.push({
      label: selectedSeries.label,
      onClick: () => {},
    });
  }

  // ── Handlers ──────────────────────────────────────────────────────────────

  function handleBrandSelect(id: string) {
    setSelectedBrandId(id);
    setSelectedFamilyId(null);
    setSelectedSeriesId(null);
  }

  function handleFamilySelect(id: string) {
    setSelectedFamilyId(id);
    setSelectedSeriesId(null);
  }

  function handleSeriesSelect(id: string) {
    setSelectedSeriesId(id);
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <div className="flex flex-col h-full bg-zinc-950 overflow-hidden">
      {/* ── Top bar ── */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-zinc-900 bg-[#0a0a0a] shrink-0">
        <button
          aria-label="Go back to Dashboard"
          onClick={goToDashboard}
          className="flex items-center gap-1.5 text-zinc-500 hover:text-white text-xs font-medium transition-colors"
        >
          <ArrowLeft size={13} />
          Back
        </button>

        <span className="text-zinc-800">|</span>

        {/* Breadcrumb */}
        <div className="flex items-center gap-1 text-xs">
          <Telescope size={12} className="text-emerald-500 shrink-0" />
          {breadcrumbs.map((crumb, i) => (
            <React.Fragment key={i}>
              {i > 0 && <ChevronRight size={10} className="text-zinc-700" />}
              <button
                onClick={crumb.onClick}
                className={`px-1.5 py-0.5 rounded transition-colors ${
                  i === breadcrumbs.length - 1
                    ? "text-white font-semibold cursor-default"
                    : "text-zinc-400 hover:text-white"
                }`}
              >
                {crumb.label}
              </button>
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* ── Columns ── */}
      <div className="flex flex-1 min-h-0 overflow-hidden">
        {isLoading ? (
          <>
            <SkeletonColumn />
            <SkeletonColumn />
            <SkeletonColumn />
            <div className="flex-1 bg-zinc-950 p-4 space-y-2">
              {Array.from({ length: 6 }).map((_, i) => (
                <div
                  key={i}
                  className="h-20 rounded-xl bg-zinc-800 animate-pulse"
                />
              ))}
            </div>
          </>
        ) : tree.brands.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center gap-3 text-zinc-600">
            <AlertCircle size={28} />
            <p className="text-sm">
              No catalog data available. Run the ingestion pipeline first.
            </p>
          </div>
        ) : (
          <AnimatePresence mode="popLayout" initial={false}>
            {/* Col 0 — Brands */}
            <ExplorerColumn
              key="brands"
              title="Brands"
              icon={Music}
              columnIndex={0}
              items={tree.brands.map((b) => ({
                id: b.id,
                label: b.label,
                count: b.count,
              }))}
              selectedId={selectedBrandId}
              onSelect={handleBrandSelect}
            />

            {/* Col 1 — Families / Categories */}
            {selectedBrand && (
              <ExplorerColumn
                key={`families-${selectedBrand.id}`}
                title="Categories"
                icon={Layers}
                columnIndex={1}
                items={selectedBrand.families.map((f) => ({
                  id: f.id,
                  label: f.label,
                  count: f.count,
                }))}
                selectedId={selectedFamilyId}
                onSelect={handleFamilySelect}
              />
            )}

            {/* Col 2 — Series */}
            {selectedFamily && (
              <ExplorerColumn
                key={`series-${selectedFamily.id}`}
                title="Series"
                icon={Tag}
                columnIndex={2}
                items={selectedFamily.series.map((s) => ({
                  id: s.id,
                  label: s.label,
                  count: s.count,
                }))}
                selectedId={selectedSeriesId}
                onSelect={handleSeriesSelect}
              />
            )}

            {/* Col 3 — Products */}
            {selectedSeries && (
              <ProductsColumn
                key={`products-${selectedSeries.id}`}
                products={selectedSeries.products}
                onSelect={(id) => goToProduct(id)}
              />
            )}

            {/* Placeholder when nothing is drilled in yet */}
            {!selectedBrand && (
              <motion.div
                key="placeholder"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex-1 flex flex-col items-center justify-center gap-3 text-zinc-700 select-none"
              >
                <Telescope size={36} className="text-zinc-800" />
                <p className="text-sm text-zinc-600">
                  Select a brand to begin exploring.
                </p>
                <p className="text-xs text-zinc-700">
                  {tree.brands.length} brands ·{" "}
                  {tree.brands.reduce((s, b) => s + b.count, 0)} products
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        )}
      </div>
    </div>
  );
};

export default ExplorerView;
