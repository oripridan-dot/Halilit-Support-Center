/**
 * ProductDetailView.tsx — Spec: specs/03_frontend_ui/product_intelligence_view.md
 * Data Source: /api/jit/product/{id}
 */
import React, { useMemo, useState, useCallback } from "react";
import { useNavigationStore } from "../../store/navigationStore";
import {
  useConductorCatalog,
  useProductRelationships,
} from "../../hooks/useConductorCatalog";
import { useJITIntelligence } from "../../hooks/useJITIntelligence";
import {
  ArrowLeft,
  Copy,
  Check,
  FileText,
  ExternalLink,
  Loader2,
  ThumbsUp,
  ThumbsDown,
} from "lucide-react";
import { ProductRelations } from "../cockpit/ProductRelations";
import type { RelatedProduct } from "../cockpit/ProductRelations";

type TabId = "ecosystem" | "specs" | "history";

const PLACEHOLDER_IMAGE = "/placeholder.png";

function formatSpecsAsText(specs: Record<string, unknown>): string {
  return Object.entries(specs)
    .map(([k, v]) => `${k}: ${v !== null && v !== undefined ? String(v) : "—"}`)
    .join("\n");
}

const ProductDetailView: React.FC = () => {
  const { activeProductId, goBack, goToProduct } = useNavigationStore();
  const { products } = useConductorCatalog();
  const jitState = useJITIntelligence(activeProductId);
  const {
    accessories,
    compatible,
    alternatives,
    relationshipMeta,
    isLoading: relationsLoading,
  } = useProductRelationships(activeProductId);
  const [activeTab, setActiveTab] = useState<TabId>("ecosystem");
  const [copyToast, setCopyToast] = useState(false);
  const [quoteToast, setQuoteToast] = useState(false);

  const product = useMemo(
    () =>
      activeProductId ? products.find((p) => p.id === activeProductId) : null,
    [activeProductId, products],
  );

  const displayName = product?.name ?? jitState.snap?.name ?? "";
  const displayBrand = product?.brand ?? jitState.snap?.brand ?? "";
  const priceIl = product?.price ?? jitState.snap?.price ?? 0;
  const priceEilat = product?.price_eilat ?? jitState.snap?.price_eilat ?? 0;
  const imageUrl =
    product?.image_url || jitState.snap?.thumbnail || PLACEHOLDER_IMAGE;
  const stock: number | null =
    (product as { stock?: number | null })?.stock ?? null;
  const specsRecord = useMemo(() => {
    const fromJit = jitState.officialSpecs?.specs as
      | Record<string, unknown>
      | undefined;
    const fromCatalog = product?.specs;
    return (
      (fromJit && Object.keys(fromJit).length > 0 ? fromJit : fromCatalog) ?? {}
    );
  }, [product?.specs, jitState.officialSpecs]);

  const displayDescription =
    product?.description ||
    (jitState.officialSpecs as { description?: string } | null)?.description ||
    "";

  const pros: string[] = (product as { pros?: string[] })?.pros ?? [];
  const cons: string[] = (product as { cons?: string[] })?.cons ?? [];

  const isJitStreaming =
    jitState.phase === "snap" ||
    jitState.phase === "intel" ||
    jitState.phase === "wisdom";

  const fileLinks = useMemo(() => {
    const links: { label: string; url: string }[] = [];
    if (product?.halilit_url)
      links.push({ label: "Halilit product page", url: product.halilit_url });
    if (product?.official_url)
      links.push({ label: "Official page", url: product.official_url });
    return links;
  }, [product?.halilit_url, product?.official_url]);

  const mapToRelated = useCallback(
    (
      items: Array<{
        id: string;
        name: string;
        price?: number;
        image_url?: string;
      }>,
      relationType: "accessory" | "compatible" | "alternative",
    ): RelatedProduct[] =>
      items.map((p) => ({
        id: p.id,
        name: p.name,
        price: p.price,
        image_url: p.image_url,
        relationType,
      })),
    [],
  );

  const handleCopySpecs = useCallback(() => {
    const text = formatSpecsAsText(specsRecord);
    if (!text.trim()) return;
    navigator.clipboard.writeText(text).then(() => {
      setCopyToast(true);
      setTimeout(() => setCopyToast(false), 2000);
    });
  }, [specsRecord]);

  const handleGenerateQuote = useCallback(() => {
    // Mock: open browser print dialog with a formatted quote
    const lines = [
      `Quote — ${displayName}`,
      `Brand: ${displayBrand}`,
      `SKU: ${activeProductId ?? ""}`,
      `IL Price: ₪${priceIl != null ? Number(priceIl).toLocaleString() : "N/A"}`,
      `Eilat Price: ₪${priceEilat != null ? Number(priceEilat).toLocaleString() : "N/A"}`,
      "",
      "Technical Specifications:",
      formatSpecsAsText(specsRecord),
    ];
    const win = window.open("", "_blank", "width=700,height=900");
    if (win) {
      win.document.write(
        `<pre style="font-family:sans-serif;padding:2rem;">${lines.join("\n")}</pre>`,
      );
      win.document.close();
      win.print();
    }
    setQuoteToast(true);
    setTimeout(() => setQuoteToast(false), 2000);
  }, [
    displayName,
    displayBrand,
    activeProductId,
    priceIl,
    priceEilat,
    specsRecord,
  ]);

  if (!activeProductId) {
    return (
      <div className="flex flex-col h-full items-center justify-center gap-4 p-8 text-zinc-500">
        <p>Select a product from Inventory or use global search (⌘K).</p>
        <button
          type="button"
          onClick={() => useNavigationStore.getState().goToInventory()}
          className="text-blue-400 hover:underline focus-visible:ring-2 focus-visible:ring-blue-500 rounded"
        >
          Back to Grid
        </button>
      </div>
    );
  }

  if (
    jitState.phase === "error" ||
    (jitState.error && jitState.phase !== "idle")
  ) {
    const is404 = jitState.error?.includes("404") ?? false;
    return (
      <div className="flex flex-col h-full items-center justify-center gap-4 p-8 text-zinc-400">
        <h2 className="text-xl font-semibold text-white">
          {is404 ? "404 Product" : "Product Error"}
        </h2>
        <p className="text-sm">
          {is404 ? "This product could not be loaded." : jitState.error}
        </p>
        <button
          type="button"
          onClick={goBack}
          className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg focus-visible:ring-2 focus-visible:ring-blue-500"
        >
          Back to Search
        </button>
      </div>
    );
  }

  const loading = !product && !jitState.snap && jitState.phase !== "complete";
  if (loading) {
    return (
      <div
        className="flex flex-col h-full bg-zinc-950"
        aria-busy
        aria-label="Loading product"
      >
        {/* Skeleton: Header */}
        <div className="border-b border-zinc-800 p-6 pb-0">
          <div className="h-4 w-20 bg-zinc-800 rounded animate-pulse mb-6" />
          <div className="flex items-start gap-6 mb-6">
            <div className="w-32 h-32 rounded-lg bg-zinc-800 animate-pulse flex-shrink-0" />
            <div className="flex-1 space-y-3 pt-2">
              <div className="h-3 w-16 bg-zinc-800 rounded animate-pulse" />
              <div className="h-7 w-2/3 bg-zinc-800 rounded animate-pulse" />
              <div className="h-4 w-1/3 bg-zinc-800 rounded animate-pulse" />
            </div>
            <div className="w-36 bg-zinc-900 border border-zinc-800 rounded-lg p-4 space-y-2">
              <div className="h-3 w-14 bg-zinc-800 rounded animate-pulse" />
              <div className="h-8 w-24 bg-zinc-800 rounded animate-pulse" />
              <div className="h-3 w-10 bg-zinc-800 rounded animate-pulse" />
              <div className="h-5 w-16 bg-zinc-800 rounded animate-pulse" />
            </div>
          </div>
          {/* Skeleton toolbar */}
          <div className="flex gap-3 pb-3">
            <div className="h-9 w-32 bg-zinc-800 rounded animate-pulse" />
            <div className="h-9 w-36 bg-zinc-800 rounded animate-pulse" />
            <div className="h-9 w-36 bg-zinc-800 rounded animate-pulse" />
          </div>
          {/* Skeleton tabs */}
          <div className="flex gap-6 mt-2">
            {["Ecosystem", "Specifications", "History"].map((t) => (
              <div
                key={t}
                className="h-4 w-20 bg-zinc-800 rounded animate-pulse mb-3"
              />
            ))}
          </div>
        </div>
        {/* Skeleton content */}
        <div className="flex-1 p-8 space-y-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-10 bg-zinc-900 rounded animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  const headerBg =
    stock === 0
      ? "bg-red-950/30 border-red-900/30"
      : "bg-zinc-900 border-zinc-800";

  const stockBadge =
    stock === null
      ? { dot: "bg-zinc-500", label: "Unknown", cls: "text-zinc-400" }
      : stock === 0
        ? { dot: "bg-red-500", label: "Out of Stock", cls: "text-red-400" }
        : { dot: "bg-green-500", label: "In Stock", cls: "text-green-400" };

  return (
    <div className="flex flex-col h-full bg-zinc-950">
      {/* Header Zone */}
      <div className={`border-b ${headerBg} p-6 pb-0 shadow-lg z-10 relative`}>
        <button
          type="button"
          onClick={goBack}
          className="mb-4 flex items-center gap-2 text-xs text-zinc-500 hover:text-white transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 rounded"
        >
          <ArrowLeft size={14} aria-hidden /> Back to Grid
        </button>

        <div className="flex items-start gap-6 mb-6">
          <div className="w-32 h-32 bg-white rounded-lg flex-shrink-0 border border-zinc-700/50 overflow-hidden">
            <img
              src={imageUrl}
              alt=""
              className="w-full h-full object-contain transition-opacity"
              onError={(e) => {
                (e.target as HTMLImageElement).style.opacity = "0.2";
              }}
            />
          </div>

          <div className="flex-1 min-w-0">
            <button
              type="button"
              onClick={() => goToInventory(displayBrand)}
              className="inline-block px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 text-[10px] font-bold uppercase tracking-wider border border-blue-500/20 mb-2 hover:bg-blue-500/20 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500"
              title={`View all ${displayBrand} products`}
            >
              {displayBrand}
            </button>
            <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">
              {displayName}
            </h1>
          </div>

          <div className="flex flex-col items-end gap-2 bg-zinc-950/50 p-4 rounded-lg border border-zinc-800">
            <span className="text-xs text-zinc-500 uppercase font-bold tracking-wider">
              IL Price
            </span>
            <span className="text-3xl font-mono font-medium text-white">
              {priceIl ? (
                `₪${Number(priceIl).toLocaleString()}`
              ) : (
                <span className="text-amber-400 text-lg">Call for Price</span>
              )}
            </span>
            <span className="text-xs text-zinc-500">Eilat</span>
            <span className="text-sm font-mono text-zinc-400">
              {priceEilat ? `₪${Number(priceEilat).toLocaleString()}` : "—"}
            </span>
            <div className="flex items-center gap-1.5 mt-1">
              <span className={`w-2 h-2 rounded-full ${stockBadge.dot}`} />
              <span className={`text-xs font-medium ${stockBadge.cls}`}>
                {stockBadge.label}
              </span>
            </div>
          </div>
        </div>

        {displayDescription && (
          <p className="text-sm text-zinc-400 leading-relaxed mb-4 line-clamp-3 max-w-3xl">
            {displayDescription}
          </p>
        )}

        <div className="flex items-center gap-3 pb-3 flex-wrap">
          <button
            type="button"
            onClick={handleCopySpecs}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-sm focus-visible:ring-2 focus-visible:ring-blue-500"
            title="Copy Technical Specifications to clipboard"
          >
            {copyToast ? (
              <Check size={16} aria-hidden />
            ) : (
              <Copy size={16} aria-hidden />
            )}
            {copyToast ? "Copied" : "Copy Tech Specs"}
          </button>
          <button
            type="button"
            onClick={handleGenerateQuote}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-sm focus-visible:ring-2 focus-visible:ring-blue-500"
            title="Generate a printable quote PDF"
          >
            {quoteToast ? (
              <Check size={16} aria-hidden />
            ) : (
              <FileText size={16} aria-hidden />
            )}
            {quoteToast ? "Quote ready" : "Generate Quote PDF"}
          </button>
          {product?.official_url ? (
            <a
              href={product.official_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-sm focus-visible:ring-2 focus-visible:ring-blue-500"
            >
              <ExternalLink size={16} aria-hidden /> Open Official Page
            </a>
          ) : (
            <button
              type="button"
              disabled
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-zinc-900 text-zinc-600 text-sm cursor-not-allowed opacity-40"
              title="No official page available"
            >
              <ExternalLink size={16} aria-hidden /> Open Official Page
            </button>
          )}
          {isJitStreaming && (
            <span className="flex items-center gap-1.5 text-xs text-zinc-500 animate-pulse">
              <Loader2 size={12} className="animate-spin" aria-hidden />
              Fetching intelligence…
            </span>
          )}
        </div>

        {/* Tabs */}
        <div className="flex gap-6 mt-2">
          {(["ecosystem", "specs", "history"] as const).map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setActiveTab(tab)}
              className={`pb-3 text-xs font-bold uppercase tracking-wider border-b-2 transition-all focus-visible:ring-2 focus-visible:ring-blue-500 rounded ${
                activeTab === tab
                  ? "border-blue-500 text-white"
                  : "border-transparent text-zinc-500 hover:text-zinc-300"
              }`}
            >
              {tab === "ecosystem"
                ? "Ecosystem"
                : tab === "specs"
                  ? "Specifications"
                  : "History"}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-8 bg-zinc-950">
        <div className="max-w-6xl mx-auto">
          {activeTab === "ecosystem" && (
            <div className="min-h-[400px]">
              {relationsLoading ? (
                <div className="flex items-center justify-center h-64 text-zinc-500">
                  Loading relationships…
                </div>
              ) : (
                <ProductRelations
                  accessories={mapToRelated(accessories, "accessory")}
                  compatible={mapToRelated(compatible, "compatible")}
                  alternatives={mapToRelated(alternatives, "alternative")}
                  relationshipMeta={relationshipMeta ?? {}}
                  onProductClick={goToProduct}
                />
              )}
            </div>
          )}

          {activeTab === "specs" && (
            <section className="space-y-8">
              {/* Technical Specs */}
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 pb-2 border-b border-zinc-800">
                  Technical Specifications
                </h3>
                {Object.keys(specsRecord).length > 0 ? (
                  <dl className="grid grid-cols-1 gap-y-2">
                    {Object.entries(specsRecord).map(([key, val]) => (
                      <div
                        key={key}
                        className="grid grid-cols-3 gap-4 py-2 border-b border-zinc-900 even:bg-zinc-900/30"
                      >
                        <dt className="text-sm font-medium text-zinc-500">
                          {key}
                        </dt>
                        <dd className="col-span-2 text-sm text-zinc-300">
                          {val !== null && val !== undefined
                            ? String(val)
                            : "—"}
                        </dd>
                      </div>
                    ))}
                  </dl>
                ) : (
                  <p className="text-zinc-500 italic text-sm">
                    Official specifications not yet fetched. Run intelligence on
                    this product.
                  </p>
                )}
              </div>

              {/* Pros & Cons from Trusted Reviews */}
              {(pros.length > 0 || cons.length > 0) && (
                <div>
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 pb-2 border-b border-zinc-800">
                    Real-World Insights
                    <span className="ml-2 text-[10px] font-normal text-zinc-600 normal-case tracking-normal">
                      from trusted reviews
                    </span>
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    {pros.length > 0 && (
                      <div>
                        <h4 className="flex items-center gap-1.5 text-xs font-semibold text-green-400 uppercase tracking-wider mb-3">
                          <ThumbsUp size={12} aria-hidden /> Pros
                        </h4>
                        <ul className="space-y-2">
                          {pros.map((pro, i) => (
                            <li
                              key={i}
                              className="flex items-start gap-2 text-sm text-zinc-300"
                            >
                              <span className="text-green-500 mt-0.5 flex-shrink-0">
                                +
                              </span>
                              {pro}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {cons.length > 0 && (
                      <div>
                        <h4 className="flex items-center gap-1.5 text-xs font-semibold text-red-400 uppercase tracking-wider mb-3">
                          <ThumbsDown size={12} aria-hidden /> Cons
                        </h4>
                        <ul className="space-y-2">
                          {cons.map((con, i) => (
                            <li
                              key={i}
                              className="flex items-start gap-2 text-sm text-zinc-300"
                            >
                              <span className="text-red-500 mt-0.5 flex-shrink-0">
                                −
                              </span>
                              {con}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </section>
          )}

          {activeTab === "history" && (
            <section>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 pb-2 border-b border-zinc-800">
                Support History
              </h3>
              <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 text-center text-zinc-500 mb-6">
                <p className="text-sm italic">
                  No past tickets for this product.
                </p>
                <p className="text-xs mt-1 text-zinc-600">
                  Ticket history integration coming soon.
                </p>
              </div>
              {fileLinks.length > 0 && (
                <>
                  <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-3">
                    Reference Links
                  </h4>
                  <ul className="space-y-2">
                    {fileLinks.map(({ label, url }) => (
                      <li key={url}>
                        <a
                          href={url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1.5 text-blue-400 hover:underline focus-visible:ring-2 focus-visible:ring-blue-500 rounded text-sm"
                        >
                          <ExternalLink size={12} aria-hidden /> {label}
                        </a>
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </section>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductDetailView;
export { ProductDetailView };
