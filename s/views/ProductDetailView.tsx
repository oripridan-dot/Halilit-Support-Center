import React, { useState, useCallback, useMemo } from "react";
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
  Lock,
} from "lucide-react";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import { useNavigationStore } from "../../store/navigationStore";
import { ProductImageCarousel } from "../ProductImageCarousel";
import { EcosystemTab } from "../EcosystemTab";
import { JITBadge } from "../JITBadge";
import { useJITIntelligence } from "../../hooks/useJITIntelligence";

// ── Helpers ────────────────────────────────────────────────────────────────────

function fmtPrice(n: number | null | undefined): string {
  if (n == null || n === 0) return "—";
  return `₪${n.toLocaleString("he-IL")}`;
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

// Pure loading skeleton — NO mock data, only animated placeholder shapes.
const SkeletonHeader = () => (
  <div
    role="status"
    aria-label="Loading product data…"
    className="p-6 flex gap-6"
  >
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
    <span className="sr-only">Loading product data...</span>
  </div>
);
const SkeletonOverview = () => (
  <div className="space-y-4 p-4">
    <SkeletonPulse className="h-6 w-full" />
    <SkeletonPulse className="h-4 w-3/4" />
    <SkeletonPulse className="h-4 w-1/2" />
    <SkeletonPulse className="h-4 w-full" />
    <SkeletonPulse className="h-4 w-1/2" />
    <SkeletonPulse className="h-4 w-3/4" />
  </div>
);
const SkeletonSpecs = () => (
  <div className="space-y-2 p-4">
    <SkeletonPulse className="h-4 w-1/3" />
    <SkeletonPulse className="h-4 w-2/3" />
    <SkeletonPulse className="h-4 w-1/2" />
    <SkeletonPulse className="h-4 w-1/4" />
    <SkeletonPulse className="h-4 w-3/4" />
    <SkeletonPulse className="h-4 w-1/3" />
  </div>
);
const SkeletonReviews = () => (
  <div className="space-y-4 p-4">
    <SkeletonPulse className="h-6 w-24" />
    <SkeletonPulse className="h-4 w-1/2" />
    <SkeletonPulse className="h-4 w-3/4" />
  </div>
);

// ── ImageWithFallback ──────────────────────────────────────────────────────────
interface ImageWithFallbackProps {
  src: string | null | undefined;
  alt: string;
  className?: string;
}
const ImageWithFallback: React.FC<ImageWithFallbackProps> = ({
  src,
  alt,
  className,
}) => {
  const [isError, setIsError] = useState(false);
  const handleError = useCallback(() => {
    setIsError(true);
  }, []);

  if (isError || !src) {
    return (
      <div
        className={`bg-zinc-800 rounded-xl flex items-center justify-center ${className}`}
        style={{ width: "100%", height: "200px" }}
      >
        <FileText size={48} className="text-zinc-600" />
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={alt}
      onError={handleError}
      className={`rounded-xl ${className}`}
      style={{ width: "100%", height: "auto", objectFit: "contain" }}
    />
  );
};

// ── ProductDetailView ──────────────────────────────────────────────────────────
export const ProductDetailView: React.FC = () => {
  const { products, isLoading, error } = useConductorCatalog();
  const { activeProductId } = useNavigationStore();
  const product = useMemo(
    () => products.find((p) => p.id === activeProductId) ?? null,
    [products, activeProductId],
  );
  const { jitData, jitLoading, jitError } = useJITIntelligence(
    product?.id || "",
  );
  const [copyStatus, setCopyStatus] = useState<"idle" | "copied">("idle");

  const handleCopyClick = useCallback(async () => {
    if (!product?.id) return;
    await navigator.clipboard.writeText(product.id);
    setCopyStatus("copied");
    setTimeout(() => setCopyStatus("idle"), 2000);
  }, [product?.id]);

  const priceBadge = product?.data_trust?.price_source;
  const specsBadge = product?.data_trust?.specs_source;

  const renderBadgeLabel = (source: string | undefined): string => {
    switch (source) {
      case "halilit":
        return "Commercial";
      case "official":
        return "Official";
      case "estimated":
        return "Estimated";
      default:
        return "";
    }
  };

  if (isLoading || !product) {
    return (
      <div className="bg-zinc-950 min-h-screen p-4">
        <SkeletonHeader />
        <div className="grid md:grid-cols-3 gap-6 mt-4">
          <div className="md:col-span-1">
            <SkeletonPulse className="w-full h-80 rounded-xl" />
          </div>
          <div className="md:col-span-2">
            <SkeletonOverview />
          </div>
        </div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="bg-zinc-950 min-h-screen flex flex-col items-center justify-center p-4">
        <AlertTriangle size={48} className="text-red-500" />
        <p className="text-zinc-400 text-center mt-4">Product not found</p>
        <button
          onClick={() => window.history.back()}
          className="mt-4 px-4 py-2 bg-zinc-800 text-zinc-200 rounded-md hover:bg-zinc-700 transition"
        >
          <ArrowLeft size={16} className="inline-block mr-2" />
          Back
        </button>
      </div>
    );
  }

  return (
    <div className="bg-zinc-950 min-h-screen p-4">
      <div className="grid md:grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="md:col-span-1">
          <ImageWithFallback
            src={product.image_url}
            alt={product.name}
            className="mb-4"
          />
          <ProductImageCarousel images={product.image_gallery || []} />
          <div className="flex items-center justify-between mt-4">
            <div className="flex items-center gap-2">
              <span className="text-zinc-400 text-sm">SKU:</span>
              <span className="bg-zinc-800 text-zinc-200 text-sm px-2 py-1 rounded-md">
                {product.id}
              </span>
              <button onClick={handleCopyClick}>
                {copyStatus === "idle" ? (
                  <Copy size={16} className="text-zinc-400 hover:text-zinc-300 transition" />
                ) : (
                  <Check size={16} className="text-emerald-400" />
                )}
              </button>
            </div>
          </div>
          <div className="mt-4">
            {isCfp(product.price) ? (
              <div className="text-red-400">Call for Price (IL)</div>
            ) : (
              <>
                {product.price && (
                  <div>
                    {fmtPrice(product.price)} (IL)
                  </div>
                )}
                {product.price_eilat && (
                  <div>
                    {fmtPrice(product.price_eilat)} (Eilat)
                  </div>
                )}
              </>
            )}
            {priceBadge && (
              <span className="text-zinc-400 text-xs">
                Source: {renderBadgeLabel(priceBadge)}
              </span>
            )}
          </div>
          {product.halilit_url && (
            <a
              href={product.halilit_url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-zinc-800 text-zinc-200 rounded-md hover:bg-zinc-700 transition"
            >
              <ExternalLink size={16} />
              Halilit URL
            </a>
          )}
          {specsBadge && (
            <div className="mt-4 text-zinc-400 text-xs">
              Specs Source: {renderBadgeLabel(specsBadge)}
            </div>
          )}
        </div>

        {/* Right Column */}
        <div className="md:col-span-2">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl text-zinc-200 font-semibold">
                {product.name}
              </h1>
              <p className="text-zinc-400 text-sm">{product.brand}</p>
              {jitLoading && <Loader2 className="animate-spin h-4 w-4 text-blue-500" />}
              {jitError && (
                <AlertTriangle size={16} className="text-red-500 inline-block mr-2" />
              )}
            </div>
            <JITBadge productId={product.id} />
          </div>

          <div className="mt-4">
            {/* Overview Tab */}
            <div>
              <h2 className="text-lg text-zinc-200 font-medium">Overview</h2>
              <p className="text-zinc-400 mt-2">{product.description_short}</p>
              <h3 className="text-md text-zinc-200 font-medium mt-4">
                Features
              </h3>
              <ul>
                {product.features?.map((feature, index) => (
                  <li key={index} className="text-zinc-400 mt-1">
                    {feature}
                  </li>
                ))}
              </ul>
              <h3 className="text-md text-zinc-200 font-medium mt-4">Pros</h3>
              <ul>
                {product.pros?.map((pro, index) => (
                  <li key={index} className="text-zinc-400 mt-1">
                    {pro}
                  </li>
                ))}
              </ul>
              <h3 className="text-md text-zinc-200 font-medium mt-4">Cons</h3>
              <ul>
                {product.cons?.map((con, index) => (
                  <li key={index} className="text-zinc-400 mt-1">
                    {con}
                  </li>
                ))}
              </ul>
            </div>
            {/* Specs Tab */}
            <div className="mt-6">
              <h2 className="text-lg text-zinc-200 font-medium">Specs</h2>
              <table className="mt-2 w-full">
                <tbody>
                  {product.specs &&
                    Object.entries(product.specs).map(([key, value]) => (
                      <tr key={key}>
                        <td className="text-zinc-400 pr-4 py-1 whitespace-nowrap">
                          {key}:
                        </td>
                        <td className="text-zinc-200 py-1">{value}</td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>

            {/* Ecosystem Tab */}
            <div className="mt-6">
              <EcosystemTab productId={product.id} />
            </div>

            {/* Reviews Tab */}
            <div className="mt-6">
              <h2 className="text-lg text-zinc-200 font-medium">Reviews</h2>
              {product.rating && (
                <div className="flex items-center gap-2">
                  <BookOpen size={16} className="text-zinc-400" />
                  <span className="text-zinc-400">
                    {product.rating.toFixed(1)} / 5
                  </span>
                </div>
              )}
              {product.review_synthesis_summary && (
                <p className="text-zinc-400 mt-2">
                  {product.review_synthesis_summary}
                </p>
              )}
              {product.real_world_insights && (
                <p className="text-zinc-400 mt-2">
                  {product.real_world_insights}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};