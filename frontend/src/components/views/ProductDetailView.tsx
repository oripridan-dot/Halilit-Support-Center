/**
 * Product Detail View — Operator Console
 * Tabs: Technical Specs, Ecosystem & Relations, Documents & Intelligence.
 */
import React, { useMemo, useState } from "react";
import { useNavigationStore } from "../../store/navigationStore";
import {
  useConductorCatalog,
  useProductRelationships,
} from "../../hooks/useConductorCatalog";
import { useJITIntelligence } from "../../hooks/useJITIntelligence";
import {
  ArrowLeft,
  Cpu,
  Globe,
  Printer,
  AlertCircle,
} from "lucide-react";
import { ProductRelations } from "../cockpit/ProductRelations";

type TabId = "specs" | "relations" | "docs";

const ProductDetailView: React.FC = () => {
  const { activeProductId, goBack } = useNavigationStore();
  const { products } = useConductorCatalog();
  const jitState = useJITIntelligence(activeProductId);
  const {
    accessories,
    compatible,
    alternatives,
    relationshipMeta,
    isLoading: relationsLoading,
  } = useProductRelationships(activeProductId);
  const [activeTab, setActiveTab] = useState<TabId>("specs");

  const product = useMemo(
    () => (activeProductId ? products.find((p) => p.id === activeProductId) : null),
    [activeProductId, products]
  );

  const specs = useMemo(() => {
    const fromJit = jitState.officialSpecs?.specs as Record<string, unknown> | undefined;
    const fromCatalog = product?.specs;
    return fromJit && Object.keys(fromJit).length > 0 ? fromJit : fromCatalog ?? {};
  }, [product?.specs, jitState.officialSpecs]);

  const verdictText =
    jitState.verdict?.text ??
    (jitState.phase === "complete" ? "Analysis complete." : "Analyzing product data…");

  // Map ConductorProduct to RelatedProduct for ProductRelations
  const mapToRelated = (
    items: Array<{ id: string; name: string; price?: number; image_url?: string }>,
    relationType: "accessory" | "compatible" | "alternative"
  ) =>
    items.map((p) => ({
      id: p.id,
      name: p.name,
      price: p.price,
      image_url: p.image_url,
      relationType,
    }));

  const relationsMeta: Record<string, { confidence: number; sources_verified: string[] }> =
    relationshipMeta ?? {};

  if (!activeProductId) {
    return (
      <div className="flex flex-col h-full items-center justify-center gap-4 p-8 text-zinc-500">
        <AlertCircle size={40} aria-hidden />
        <p>Select a product from Inventory or use global search (⌘K).</p>
        <button
          type="button"
          onClick={() => useNavigationStore.getState().goToInventory()}
          className="text-blue-400 hover:underline focus-visible:ring-2 focus-visible:ring-blue-500 rounded"
        >
          Go to Inventory
        </button>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="flex flex-col h-full items-center justify-center gap-4 p-8">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        <span className="text-sm text-zinc-500">Loading product…</span>
      </div>
    );
  }

  const tabs: { id: TabId; label: string }[] = [
    { id: "specs", label: "Technical Specs" },
    { id: "relations", label: "Ecosystem & Relations" },
    { id: "docs", label: "Documents & Intelligence" },
  ];

  return (
    <div className="flex flex-col h-full bg-zinc-950">
      {/* 1. Header Card */}
      <div className="bg-zinc-900 border-b border-zinc-800 p-6 pb-0 shadow-lg z-10 relative">
        <button
          type="button"
          onClick={goBack}
          className="mb-4 flex items-center gap-2 text-xs text-zinc-500 hover:text-white transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 rounded"
        >
          <ArrowLeft size={14} aria-hidden /> Back to Inventory
        </button>

        <div className="flex items-start gap-6 mb-6">
          <div className="w-32 h-32 bg-white rounded-lg p-3 flex-shrink-0 border border-zinc-700/50 shadow-inner">
            <img
              src={product.image_url || "/assets/images/placeholder_product.svg"}
              alt=""
              className="w-full h-full object-contain"
            />
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 mb-2">
              <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 text-[10px] font-bold uppercase tracking-wider border border-blue-500/20">
                {product.brand}
              </span>
              <span className="text-xs text-zinc-500 font-mono">SKU: {product.id}</span>
            </div>
            <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">
              {product.name}
            </h1>
            <p className="text-sm text-zinc-400 max-w-3xl line-clamp-2 leading-relaxed">
              {product.description_short || "No short description available."}
            </p>
          </div>

          <div className="flex flex-col items-end gap-2 bg-zinc-950/50 p-4 rounded-lg border border-zinc-800">
            <div className="flex items-baseline gap-2">
              <span className="text-xs text-zinc-500 uppercase font-bold tracking-wider">
                IL Price
              </span>
              <span className="text-3xl font-mono font-medium text-white">
                ₪{product.price != null ? product.price.toLocaleString() : "N/A"}
              </span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-xs text-zinc-500">Eilat (VAT Free)</span>
              <span className="text-sm font-mono text-zinc-400">
                ₪
                {product.price_eilat != null
                  ? product.price_eilat.toLocaleString()
                  : "N/A"}
              </span>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex items-center justify-between mt-4">
          <div className="flex gap-6">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`pb-3 text-xs font-bold uppercase tracking-wider border-b-2 transition-all focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-900 ${
                  activeTab === tab.id
                    ? "border-blue-500 text-white"
                    : "border-transparent text-zinc-500 hover:text-zinc-300"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="flex gap-2 pb-3">
            {product.official_url && (
              <a
                href={product.official_url}
                target="_blank"
                rel="noreferrer"
                className="p-2 hover:bg-zinc-800 rounded text-zinc-400 hover:text-white transition-colors"
                title="Official Page"
                aria-label="Open official product page"
              >
                <Globe size={16} aria-hidden />
              </a>
            )}
            <button
              type="button"
              className="p-2 hover:bg-zinc-800 rounded text-zinc-400 hover:text-white transition-colors"
              title="Print Spec Sheet"
              aria-label="Print spec sheet"
            >
              <Printer size={16} aria-hidden />
            </button>
          </div>
        </div>
      </div>

      {/* 2. Content Area */}
      <div className="flex-1 overflow-auto p-8 bg-zinc-950">
        <div className="max-w-6xl mx-auto">
          {activeTab === "specs" && (
            <div className="grid grid-cols-12 gap-8">
              <div className="col-span-8 space-y-8">
                <section>
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 pb-2 border-b border-zinc-800">
                    Official Specifications
                  </h3>
                  {Object.keys(specs).length > 0 ? (
                    <dl className="grid grid-cols-1 gap-y-4">
                      {Object.entries(specs).map(([key, val]) => (
                        <div
                          key={key}
                          className="grid grid-cols-3 gap-4 py-2 border-b border-zinc-900"
                        >
                          <dt className="text-sm font-medium text-zinc-500">{key}</dt>
                          <dd className="col-span-2 text-sm text-zinc-300">
                            {val !== null && val !== undefined ? String(val) : "—"}
                          </dd>
                        </div>
                      ))}
                    </dl>
                  ) : (
                    <p className="text-zinc-500 italic">No detailed specifications ingested.</p>
                  )}
                </section>
              </div>

              <div className="col-span-4 space-y-6">
                <div className="bg-zinc-900 rounded-xl p-5 border border-zinc-800 shadow-sm">
                  <h3 className="flex items-center gap-2 text-sm font-bold text-white mb-4">
                    <Cpu size={16} className="text-blue-400" aria-hidden /> Quick Analysis
                  </h3>
                  {jitState.error ? (
                    <div className="text-sm text-amber-400 leading-relaxed">
                      <p className="font-medium mb-2">⚠️ {jitState.error}</p>
                      {jitState.error.includes("GOOGLE_API_KEY") && (
                        <p className="text-xs text-zinc-500 mt-2">
                          Set GOOGLE_API_KEY or GEMINI_API_KEY in your .env file to enable AI analysis.
                        </p>
                      )}
                    </div>
                  ) : (
                    <div className="text-sm text-zinc-400 leading-relaxed">
                      {verdictText}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {activeTab === "relations" && (
            <div className="h-[600px] min-h-[400px]">
              {relationsLoading ? (
                <div className="flex items-center justify-center h-full text-zinc-500">
                  Loading relationships…
                </div>
              ) : (
                <ProductRelations
                  accessories={mapToRelated(accessories, "accessory")}
                  compatible={mapToRelated(compatible, "compatible")}
                  alternatives={mapToRelated(alternatives, "alternative")}
                  relationshipMeta={relationsMeta}
                  onProductClick={(id) => useNavigationStore.getState().goToProduct(id)}
                />
              )}
            </div>
          )}

          {activeTab === "docs" && (
            <div className="text-center py-20 text-zinc-600">
              <p>Documentation and manual viewer integration pending.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductDetailView;
export { ProductDetailView };
