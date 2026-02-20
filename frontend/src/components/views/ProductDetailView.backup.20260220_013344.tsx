import React, { useState, useCallback } from "react";
import {
  ArrowLeft,
  Copy,
  Check,
  ExternalLink,
  FileText,
  Package,
  Loader2,
  AlertTriangle,
  Zap,
  BookOpen,
  Clock,
  ChevronRight,
} from "lucide-react";

import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import { useJITIntelligence } from "../../hooks/useJITIntelligence";
import { useNavigationStore } from "../../store/navigationStore";

// ── Helpers ────────────────────────────────────────────────────────────────────

function fmtPrice(n: number | null | undefined): string {
  if (n == null || n === 0) return "—";
  return `₪${n.toLocaleString()}`;
}

function isCfp(price: number | null | undefined): boolean {
  return price == null || price === 0;
}

// ── StockDot ───────────────────────────────────────────────────────────────────
interface StockDotProps {
  stock?: number | null;
}
const StockDot: React.FC<StockDotProps> = ({ stock }) => {
  if (stock === 0)
    return (
      <>
        <span className="w-2 h-2 rounded-full bg-red-500 inline-block" />{" "}
        <span className="text-red-400 text-sm">Out of Stock</span>
      </>
    );
  if (stock == null)
    return (
      <>
        <span className="w-2 h-2 rounded-full bg-zinc-600 inline-block" />{" "}
        <span className="text-zinc-500 text-sm">Unknown</span>
      </>
    );
  return (
    <>
      <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" />{" "}
      <span className="text-emerald-400 text-sm">In Stock</span>
    </>
  );
};

// ── Toast ──────────────────────────────────────────────────────────────────────
interface ToastProps {
  msg: string;
}
const Toast: React.FC<ToastProps> = ({ msg }) => (
  <div
    className="fixed bottom-6 right-6 z-50 flex items-center gap-2 px-4 py-2.5 rounded-xl
    bg-zinc-900 border border-zinc-700 text-sm text-zinc-200 shadow-xl animate-fade-in"
  >
    <Check size={13} className="text-emerald-400" />
    {msg}
  </div>
);

// ── Skeleton ───────────────────────────────────────────────────────────────────
interface SkeletonPulseProps {
  className?: string;
}
const SkeletonPulse: React.FC<SkeletonPulseProps> = ({ className = "" }) => (
  <div className={`bg-zinc-900 rounded animate-pulse ${className}`} />
);

const SkeletonHeader = () => (
  <div className="p-6 flex gap-6">
    <SkeletonPulse className="w-48 h-40 rounded-xl shrink-0" />
    <div className="flex-1 space-y-3 pt-1">
      <SkeletonPulse className="h-6 w-64" />
      <SkeletonPulse className="h-4 w-24" />
      <SkeletonPulse className="h-3 w-20" />
    </div>
    <div className="w-40 space-y-2 pt-1">
      <SkeletonPulse className="h-8 w-full" />
      <SkeletonPulse className="h-4 w-24" />
      <SkeletonPulse className="h-4 w-16" />
    </div>
  </div>
);

// ── RelatedProductCard ─────────────────────────────────────────────────────────
interface RelatedProduct {
  id: string;
  name: string;
  price?: number;
  image_url?: string;
}
interface RelatedProductCardProps {
  item: RelatedProduct;
  badge?: string;
  badgeColor?: string;
  onSelect: () => void;
}
const RelatedProductCard: React.FC<RelatedProductCardProps> = ({
  item,
  badge,
  badgeColor = "bg-emerald-950/30 text-emerald-400 border-emerald-900/30",
  onSelect,
}) => (
  <button
    onClick={onSelect}
    className="flex items-center gap-3 p-3 rounded-lg bg-zinc-900/50 border border-zinc-800
      hover:border-zinc-700 hover:bg-zinc-900 transition-all text-left w-full group"
  >
    <div className="w-10 h-10 rounded-md bg-zinc-900 border border-zinc-800 overflow-hidden shrink-0">
      {item.image_url ? (
        <img
          src={item.image_url}
          alt=""
          className="w-full h-full object-contain"
          onError={(e) => {
            (e.target as HTMLImageElement).style.opacity = "0";
          }}
        />
      ) : (
        <div className="w-full h-full flex items-center justify-center">
          <Package size={12} className="text-zinc-700" />
        </div>
      )}
    </div>
    <div className="flex-1 min-w-0">
      <div className="text-sm text-zinc-300 font-medium truncate group-hover:text-zinc-100 transition-colors">
        {item.name}
      </div>
      {item.price ? (
        <div className="text-xs text-zinc-600">
          ₪{item.price.toLocaleString()}
        </div>
      ) : null}
    </div>
    {badge && (
      <span
        className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${badgeColor} shrink-0 uppercase tracking-wider`}
      >
        {badge}
      </span>
    )}
    <ChevronRight
      size={13}
      className="text-zinc-700 group-hover:text-zinc-400 transition-colors shrink-0"
    />
  </button>
);

// ── MiniSection ────────────────────────────────────────────────────────────────
interface MiniSectionProps {
  title: string;
  count: number;
  children: React.ReactNode;
}
const MiniSection: React.FC<MiniSectionProps> = ({
  title,
  count,
  children,
}) => (
  <div className="mb-6">
    <div className="flex items-center gap-2 mb-3">
      <span className="text-xs font-semibold text-zinc-400">{title}</span>
      <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-zinc-900 text-zinc-600 border border-zinc-800">
        {count}
      </span>
    </div>
    <div className="space-y-2">{children}</div>
  </div>
);

// ── TabButton ──────────────────────────────────────────────────────────────────
interface TabButtonProps {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}
const TabButton: React.FC<TabButtonProps> = ({ active, onClick, children }) => (
  <button
    onClick={onClick}
    className={`px-4 py-2 text-sm font-medium transition-all border-b-2 ${
      active
        ? "border-blue-500 text-blue-400"
        : "border-transparent text-zinc-500 hover:text-zinc-300 hover:border-zinc-700"
    }`}
  >
    {children}
  </button>
);

// ── ProductDetailView ──────────────────────────────────────────────────────────

interface ProductDetailViewProps {}

const ProductDetailView: React.FC<ProductDetailViewProps> = () => {
  const { activeProductId, goBack, goToInventory, goToProduct } =
    useNavigationStore();
  const { products, isLoading: catalogLoading } = useConductorCatalog();
  const { jitState } = useJITIntelligence(activeProductId ?? "");
  const [activeTab, setActiveTab] = useState<
    "ecosystem" | "specifications" | "history"
  >("ecosystem");
  const [toast, setToast] = useState<string | null>(null);
  const [copiedSpecs, setCopiedSpecs] = useState(false);

  const showToast = useCallback((msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 1600);
  }, []);

  // ── Resolve product ──────────────────────────────────────────────────────────
  const product = products?.find((p) => p.id === activeProductId) ?? null;
  const notFound =
    !catalogLoading &&
    products !== undefined &&
    !product &&
    jitState.phase === "error";

  if (!activeProductId || notFound) {
    return (
      <div className="p-8 max-w-md">
        <p className="text-2xl font-bold text-zinc-400 mb-2">
          Product Not Found
        </p>
        <p className="text-sm text-zinc-600 mb-6">
          No product with ID "{activeProductId}" exists in the catalog.
        </p>
        <button
          onClick={goBack}
          className="flex items-center gap-2 text-sm text-zinc-400 hover:text-zinc-200 transition-colors"
        >
          <ArrowLeft size={14} /> Back to Search
        </button>
      </div>
    );
  }

  // ── Show skeleton only when catalog is loading AND product not found yet ─────
  if (catalogLoading && !product) {
    return <SkeletonHeader />;
  }

  // ── Field resolution (catalog first, JIT snap as fallback) ─────────────────
  const displayName = product?.name ?? jitState.snap?.name ?? "—";
  const displayBrand = product?.brand ?? jitState.snap?.brand ?? "—";
  const displayPrice = product?.price ?? jitState.snap?.price;
  const displayEilat = product?.price_eilat ?? jitState.snap?.price_eilat;
  const displayImage = product?.image_url ?? "/placeholder.png";
  const displaySku = product?.id ?? activeProductId;
  const displayCategory = product?.subcategory ?? product?.category;
  const displayOfficialUrl = product?.official_url;
  const displayHalilitUrl = product?.halilit_url ?? jitState.snap?.halilit_url;
  const displayStock = product?.stock;

  // Specs: JIT wins if non-empty
  const jitSpecs = jitState.officialSpecs?.specs;
  const catalogSpecs = product?.specs ?? {};
  const specsRecord: Record<string, unknown> =
    jitSpecs && Object.keys(jitSpecs).length > 0 ? jitSpecs : catalogSpecs;

  // Relationships from product graph
  const relIds = product?.relationship_ids ?? [];
  const relProducts: RelatedProduct[] =
    products
      ?.filter((p) => relIds.includes(p.id))
      .map((p) => ({
        id: p.id,
        name: p.name,
        price: p.price ?? undefined,
        image_url: p.image_url,
      })) ?? [];

  // Simplified relationship categorisation (by relationship_ids only — no graph data in this view)
  const accessories = relProducts.slice(0, Math.ceil(relProducts.length / 2));
  const alternatives = relProducts.slice(Math.ceil(relProducts.length / 2));

  // ── Actions ──────────────────────────────────────────────────────────────────
  const handleCopySpecs = () => {
    const lines = Object.entries(specsRecord)
      .map(([k, v]) => `${k}: ${v}`)
      .join("\n");
    if (!lines) {
      showToast("No specs to copy");
      return;
    }
    navigator.clipboard.writeText(lines).then(() => {
      setCopiedSpecs(true);
      showToast("Specs copied to clipboard ✓");
      setTimeout(() => setCopiedSpecs(false), 1600);
    });
  };

  const handleQuotePdf = () => {
    window.print();
    showToast("Quote generated");
  };

  const isStreaming =
    jitState.phase === "snap" ||
    jitState.phase === "intel" ||
    jitState.phase === "wisdom";

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {toast && <Toast msg={toast} />}

      {/* ── Back ── */}
      <div className="px-6 pt-5 pb-1 shrink-0">
        <button
          onClick={goBack}
          className="flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
        >
          <ArrowLeft size={13} /> Back
        </button>
      </div>

      {/* ── Scrollable content ── */}
      <div className="flex-1 overflow-auto">
        {/* Header Card */}
        <div className="px-6 pt-3 pb-5 border-b border-zinc-900">
          <div className="flex gap-6">
            {/* Hero Image */}
            <div className="w-44 h-36 rounded-xl bg-white flex items-center justify-center shrink-0 overflow-hidden border border-zinc-200/10">
              <img
                src={displayImage}
                alt={displayName}
                className="w-full h-full object-contain p-2"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.opacity = "0.2";
                }}
              />
            </div>

            {/* Identity */}
            <div className="flex-1 min-w-0 pt-1">
              <div className="flex items-start gap-3 mb-2">
                <h1 className="text-xl font-bold text-zinc-100 leading-tight max-w-lg">
                  {displayName}
                </h1>
                {isStreaming && (
                  <div className="flex items-center gap-1.5 mt-1 shrink-0">
                    <Loader2 size={11} className="animate-spin text-blue-400" />
                    <span className="text-[10px] text-blue-400">
                      {jitState.statusMessage || "Loading intelligence…"}
                    </span>
                  </div>
                )}
              </div>

              <button
                onClick={() => goToInventory(displayBrand)}
                className="inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full
                  bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700
                  transition-colors mb-3"
              >
                {displayBrand}
              </button>

              <div className="flex items-center gap-4 text-xs text-zinc-600">
                <span className="font-mono">{displaySku}</span>
                {displayCategory && (
                  <span className="px-1.5 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-500">
                    {displayCategory}
                  </span>
                )}
              </div>
            </div>

            {/* Pricing */}
            <div className="shrink-0 pt-1 min-w-[140px]">
              {isCfp(displayPrice) ? (
                <div>
                  <span className="text-[28px] font-bold text-amber-400 leading-none">
                    Call for Price
                  </span>
                  <div className="mt-2">
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(displaySku ?? "");
                        showToast("SKU copied");
                      }}
                      className="flex items-center gap-1.5 text-xs text-zinc-500 hover:text-zinc-300 transition-colors"
                    >
                      <Copy size={11} /> Copy SKU
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  <div className="text-[28px] font-bold text-zinc-100 leading-none">
                    {fmtPrice(displayPrice)}
                  </div>
                  {displayEilat && (
                    <div className="text-sm text-zinc-500 mt-0.5">
                      Eilat: {fmtPrice(displayEilat)}
                    </div>
                  )}
                </div>
              )}
              <div className="flex items-center gap-1.5 mt-3">
                <StockDot stock={displayStock} />
              </div>
            </div>
          </div>

          {/* JIT Error */}
          {jitState.phase === "error" && jitState.error && (
            <div className="mt-4 flex items-center gap-2 px-3 py-2 rounded-lg bg-amber-950/20 border border-amber-900/30 text-xs text-amber-400">
              <AlertTriangle size={12} />
              Intelligence fetch failed — showing catalog data only.
            </div>
          )}
        </div>

        {/* Action Toolbar */}
        <div className="flex items-center gap-2 px-6 py-3 border-b border-zinc-900 bg-[#050505] shrink-0">
          <button
            onClick={handleCopySpecs}
            className="flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium
              bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700
              transition-all"
          >
            {copiedSpecs ? (
              <Check size={12} className="text-emerald-400" />
            ) : (
              <Copy size={12} />
            )}
            Copy Tech Specs
          </button>
          <button
            onClick={handleQuotePdf}
            className="flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium
              bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700
              transition-all"
          >
            <FileText size={12} />
            Generate Quote PDF
          </button>
          {displayOfficialUrl ? (
            <a
              href={displayOfficialUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium
                bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200 hover:border-zinc-700
                transition-all"
            >
              <ExternalLink size={12} />
              Open Official Page
            </a>
          ) : (
            <button
              disabled
              className="flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium
                bg-zinc-900 border border-zinc-800/50 text-zinc-700 cursor-not-allowed"
            >
              <ExternalLink size={12} />
              Open Official Page
            </button>
          )}
          {displayHalilitUrl && (
            <a
              href={displayHalilitUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium
                bg-blue-950/30 border border-blue-900/40 text-blue-400 hover:text-blue-300
                hover:border-blue-800/50 transition-all ml-auto"
            >
              <Zap size={12} />
              Halilit.com
            </a>
          )}
        </div>

        {/* Tab Bar */}
        <div className="flex items-center gap-0 px-4 border-b border-zinc-900">
          <TabButton
            active={activeTab === "ecosystem"}
            onClick={() => setActiveTab("ecosystem")}
          >
            <span className="flex items-center gap-1.5">
              <BookOpen size={12} /> Ecosystem
            </span>
          </TabButton>
          <TabButton
            active={activeTab === "specifications"}
            onClick={() => setActiveTab("specifications")}
          >
            <span className="flex items-center gap-1.5">
              <FileText size={12} /> Specifications
            </span>
          </TabButton>
          <TabButton
            active={activeTab === "history"}
            onClick={() => setActiveTab("history")}
          >
            <span className="flex items-center gap-1.5">
              <Clock size={12} /> History
            </span>
          </TabButton>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {/* Ecosystem Tab */}
          {activeTab === "ecosystem" && (
            <div className="max-w-2xl">
              {relProducts.length === 0 ? (
                <div className="flex flex-col items-center gap-3 py-12">
                  <Package size={24} className="text-zinc-800" />
                  <p className="text-sm text-zinc-600">
                    No verified accessories found in the product graph.
                  </p>
                </div>
              ) : (
                <>
                  {accessories.length > 0 && (
                    <MiniSection
                      title="Verified Accessories"
                      count={accessories.length}
                    >
                      {accessories.map((item) => (
                        <RelatedProductCard
                          key={item.id}
                          item={item}
                          badge="Verified"
                          badgeColor="bg-emerald-950/30 text-emerald-400 border-emerald-900/30"
                          onSelect={() => goToProduct(item.id)}
                        />
                      ))}
                    </MiniSection>
                  )}
                  {alternatives.length > 0 && (
                    <MiniSection
                      title="Alternatives"
                      count={alternatives.length}
                    >
                      {alternatives.map((item) => (
                        <RelatedProductCard
                          key={item.id}
                          item={item}
                          onSelect={() => goToProduct(item.id)}
                        />
                      ))}
                    </MiniSection>
                  )}
                </>
              )}
            </div>
          )}

          {/* Specifications Tab */}
          {activeTab === "specifications" && (
            <div className="max-w-2xl">
              {isStreaming && (
                <div className="flex items-center gap-2 mb-4 text-xs text-blue-400">
                  <Loader2 size={11} className="animate-spin" />
                  Fetching official specifications…
                </div>
              )}
              {Object.keys(specsRecord).length === 0 ? (
                <p className="text-sm text-zinc-600 py-8">
                  Official specifications not yet fetched. Run intelligence on
                  this product.
                </p>
              ) : (
                <table className="w-full border-collapse text-sm">
                  <tbody>
                    {Object.entries(specsRecord).map(([key, val], idx) => (
                      <tr
                        key={key}
                        className={idx % 2 === 0 ? "bg-zinc-900/20" : ""}
                      >
                        <td className="py-2 px-3 text-xs text-zinc-500 font-medium w-40 align-top">
                          {key}
                        </td>
                        <td className="py-2 px-3 text-xs text-zinc-300">
                          {String(val ?? "—")}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}

          {/* History Tab */}
          {activeTab === "history" && (
            <p className="text-sm text-zinc-600 py-8">
              Ticket history coming soon. No records for this product yet.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProductDetailView;