/**
 * Product Detail View (Operator Console) — Tabs: Specs, Intelligence, History, Assets.
 * Professional layout with pricing always visible and JIT intelligence summary.
 */
import React, { useState, useMemo } from "react";
import { useNavigationStore } from "../../store/navigationStore";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import { useJITIntelligence } from "../../hooks/useJITIntelligence";
import { Cpu, Printer, Share2 } from "lucide-react";

type TabId = "specs" | "intelligence" | "history" | "assets";

export const ProductDetailView: React.FC = () => {
  const { activeProductId } = useNavigationStore();
  const { products } = useConductorCatalog();
  const jitState = useJITIntelligence(activeProductId);
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

  const verdict = jitState.verdict;
  const pros = verdict?.pros ?? [];
  const cons = verdict?.cons ?? [];
  const verdictText = verdict?.text ?? (jitState.phase === "complete" ? "Analysis complete." : "Analyzing product data…");

  if (!activeProductId) {
    return (
      <div className="flex flex-col h-full items-center justify-center gap-4 p-8 text-zinc-500">
        <p className="text-sm">Select a product from Inventory or use global search (⌘K).</p>
        <button
          type="button"
          onClick={() => useNavigationStore.getState().goToItems()}
          className="text-sm text-blue-400 hover:text-blue-300 focus-visible:ring-2 focus-visible:ring-blue-500 rounded"
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

  const tabs: TabId[] = ["specs", "intelligence", "history", "assets"];

  return (
    <div className="flex flex-col h-full bg-zinc-950">
      {/* 1. PRODUCT HEADER */}
      <div className="bg-zinc-900 border-b border-zinc-800 p-6 pb-0">
        <div className="flex items-start gap-6 mb-6">
          <div className="w-24 h-24 bg-white rounded-lg p-2 flex-shrink-0 border border-zinc-700/50">
            <img
              src={product.image_url || "/placeholder.png"}
              alt=""
              className="w-full h-full object-contain"
            />
          </div>

          <div className="flex-1">
            <div className="flex items-center gap-3 mb-1">
              <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 text-[10px] font-bold uppercase tracking-wider border border-blue-500/20">
                {product.brand}
              </span>
              <span className="text-xs text-zinc-500 font-mono">SKU: {product.id}</span>
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">{product.name}</h1>
            <p className="text-sm text-zinc-400 max-w-3xl line-clamp-2">
              {product.description_short || "No description available."}
            </p>
          </div>

          <div className="flex flex-col items-end gap-1">
            <div className="flex items-baseline gap-1">
              <span className="text-xs text-zinc-500">IL Price</span>
              <span className="text-2xl font-mono font-medium text-white">
                ₪{product.price?.toLocaleString() ?? "—"}
              </span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-xs text-zinc-500">Eilat</span>
              <span className="text-sm font-mono text-zinc-400">
                ₪{product.price_eilat?.toLocaleString() ?? "—"}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1">
          {tabs.map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors capitalize focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-900 ${
                activeTab === tab
                  ? "border-blue-500 text-white"
                  : "border-transparent text-zinc-500 hover:text-zinc-300"
              }`}
            >
              {tab}
            </button>
          ))}
          <div className="flex-1 border-b border-zinc-800" />

          <div className="flex items-center gap-2 pb-2 pl-4">
            <button
              type="button"
              className="p-2 hover:bg-zinc-800 rounded text-zinc-400 hover:text-white focus-visible:ring-2 focus-visible:ring-blue-500"
              title="Print Sheet"
            >
              <Printer size={16} aria-hidden />
            </button>
            <button
              type="button"
              className="p-2 hover:bg-zinc-800 rounded text-zinc-400 hover:text-white focus-visible:ring-2 focus-visible:ring-blue-500"
              title="Share"
            >
              <Share2 size={16} aria-hidden />
            </button>
          </div>
        </div>
      </div>

      {/* 2. TAB CONTENT */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-5xl mx-auto">
          {activeTab === "specs" && (
            <div className="grid grid-cols-2 gap-8">
              <div className="space-y-6">
                <section>
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 border-b border-zinc-800 pb-2">
                    Technical Specifications
                  </h3>
                  <dl className="space-y-2 text-sm">
                    {Object.entries(specs).map(([key, val]) => (
                      <div
                        key={key}
                        className="grid grid-cols-3 gap-4 py-1 border-b border-zinc-800/50"
                      >
                        <dt className="text-zinc-500 font-medium">{key}</dt>
                        <dd className="col-span-2 text-zinc-300">
                          {val !== null && val !== undefined ? String(val) : "—"}
                        </dd>
                      </div>
                    ))}
                    {Object.keys(specs).length === 0 && (
                      <p className="text-zinc-500 text-sm">No specifications available.</p>
                    )}
                  </dl>
                </section>
              </div>

              <div className="space-y-6">
                <section className="bg-zinc-900 rounded-xl p-5 border border-zinc-800">
                  <h3 className="flex items-center gap-2 text-sm font-bold text-white mb-4">
                    <Cpu size={16} className="text-blue-400" aria-hidden />
                    System Intelligence
                  </h3>
                  <div className="space-y-4 text-sm text-zinc-300">
                    <p>{verdictText}</p>
                    <div className="grid grid-cols-2 gap-2 mt-4">
                      <div className="bg-emerald-900/20 border border-emerald-900/50 p-3 rounded">
                        <span className="text-emerald-400 font-bold block mb-1">Pros</span>
                        <ul className="list-disc list-inside text-xs text-emerald-200/80">
                          {pros.slice(0, 3).map((p, i) => (
                            <li key={i}>{p}</li>
                          ))}
                          {pros.length === 0 && <li>—</li>}
                        </ul>
                      </div>
                      <div className="bg-red-900/20 border border-red-900/50 p-3 rounded">
                        <span className="text-red-400 font-bold block mb-1">Cons</span>
                        <ul className="list-disc list-inside text-xs text-red-200/80">
                          {cons.slice(0, 3).map((c, i) => (
                            <li key={i}>{c}</li>
                          ))}
                          {cons.length === 0 && <li>—</li>}
                        </ul>
                      </div>
                    </div>
                  </div>
                </section>
              </div>
            </div>
          )}

          {activeTab === "intelligence" && (
            <section className="bg-zinc-900 rounded-xl p-5 border border-zinc-800">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
                JIT Intelligence
              </h3>
              <p className="text-sm text-zinc-400">{verdictText}</p>
              <div className="grid grid-cols-2 gap-4 mt-4">
                <div className="bg-emerald-900/20 border border-emerald-900/50 p-4 rounded-lg">
                  <span className="text-emerald-400 font-bold block mb-2">Pros</span>
                  <ul className="list-disc list-inside text-sm text-zinc-300 space-y-1">
                    {pros.map((p, i) => (
                      <li key={i}>{p}</li>
                    ))}
                    {pros.length === 0 && <li className="text-zinc-500">—</li>}
                  </ul>
                </div>
                <div className="bg-red-900/20 border border-red-900/50 p-4 rounded-lg">
                  <span className="text-red-400 font-bold block mb-2">Cons</span>
                  <ul className="list-disc list-inside text-sm text-zinc-300 space-y-1">
                    {cons.map((c, i) => (
                      <li key={i}>{c}</li>
                    ))}
                    {cons.length === 0 && <li className="text-zinc-500">—</li>}
                  </ul>
                </div>
              </div>
            </section>
          )}

          {activeTab === "history" && (
            <section className="bg-zinc-900 rounded-xl p-5 border border-zinc-800">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
                History
              </h3>
              <p className="text-sm text-zinc-500">History and activity for this product.</p>
            </section>
          )}

          {activeTab === "assets" && (
            <section className="bg-zinc-900 rounded-xl p-5 border border-zinc-800">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
                Assets
              </h3>
              <p className="text-sm text-zinc-500">Files and media assets.</p>
            </section>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductDetailView;
