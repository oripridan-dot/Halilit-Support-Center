import React, { useState, useEffect, useRef } from "react";
import { Boxes } from "lucide-react";
import { ResearchAnimation } from "../product/ResearchAnimation";
import { GlobalErrorBoundary } from "../ui/GlobalErrorBoundary";
import { ConductorProduct } from "../../hooks/useConductorCatalog";

// Inline SourceBadge — lightweight; no external dependency needed here
const SOURCE_COLORS: Record<string, string> = {
  COMMERCIAL: "bg-green-900 text-green-300 border-green-600",
  OFFICIAL: "bg-blue-900 text-blue-300 border-blue-600",
  CONTEXTUAL: "bg-amber-900 text-amber-300 border-amber-600",
};
function SourceBadge({
  type,
  label,
  unavailable,
}: {
  type: string;
  label: string;
  unavailable?: boolean;
}) {
  const colors =
    SOURCE_COLORS[type] ?? "bg-zinc-800 text-zinc-400 border-zinc-600";
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded border text-xs font-semibold ${colors} ${unavailable ? "opacity-40" : ""}`}
    >
      {unavailable && <span title="Source unavailable">🔒</span>}
      {label}
    </span>
  );
}

interface ExplorerViewProps {
  // Add any necessary props here
}

enum PricingTier {
  ENTRY = "ENTRY",
  MID = "MID",
  PRO = "PRO",
  FLAGSHIP = "FLAGSHIP",
  LEGACY = "LEGACY",
}

enum DataSourceConfidence {
  OFFICIAL = "OFFICIAL",
  TRUSTED = "TRUSTED",
  COMMERCIAL = "COMMERCIAL",
  USER = "USER",
  INFERRED = "INFERRED",
}

interface IngestionProductDraft {
  id: string;
  name: string;
  brand: string;
  description: string;
  price: number;
  pricing_tier: PricingTier;
  data_source_confidence: DataSourceConfidence;
  // ... other properties
}

const ExplorerView: React.FC<ExplorerViewProps> = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [product, setProduct] = useState<ConductorProduct | null>(null);
  const [jitComputing, setJitComputing] = useState(false);
  const [rendered, setRendered] = useState(false);
  const [renderedPartial, setRenderedPartial] = useState(false);
  const [relatedOpen, setRelatedOpen] = useState(false);
  const [streamingText, setStreamingText] = useState("");
  const sseRef = useRef<EventSource | null>(null);

  const handleProductSelect = (selectedProduct: ConductorProduct) => {
    setProduct(selectedProduct);
    setIsLoading(false); // Assuming immediate transition
    setJitComputing(true);
    setRendered(false);
    setRenderedPartial(false);
    setStreamingText("");

    // Start SSE stream
    const eventSource = new EventSource(
      `/api/product/${selectedProduct.id}/jit`,
    ); // Replace with your actual endpoint
    sseRef.current = eventSource;

    eventSource.onopen = () => {
      console.log("SSE connection opened");
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "text") {
          setStreamingText((prevText) => prevText + data.content);
        }
      } catch (err) {
        console.error("Error parsing SSE message:", err);
        setError("Error processing data from the server.");
      }
    };

    eventSource.onerror = (error) => {
      console.error("SSE error:", error);
      setError("Failed to fetch data. Please try again.");
      setJitComputing(false);
      setRenderedPartial(true);
    };

    eventSource.addEventListener("complete", () => {
      console.log("SSE stream completed");
      setJitComputing(false);
      setRendered(true);
    });

    eventSource.addEventListener("timeout", () => {
      console.log("SSE stream timed out");
      setJitComputing(false);
      setRenderedPartial(true);
    });
  };

  useEffect(() => {
    return () => {
      // Cleanup on unmount (STRICT_JIT)
      if (sseRef.current) {
        sseRef.current.close();
        console.log("SSE connection closed");
      }
    };
  }, []);

  const availableSources = ["COMMERCIAL", "OFFICIAL", "CONTEXTUAL"]; // Replace with actual sources from data
  const unavailableSources = ["CONTEXTUAL"]; // Example of unavailable sources. Replace with logic from the JIT data.

  return (
    <GlobalErrorBoundary>
      <div className="min-h-screen bg-zinc-900 text-zinc-100">
        {isLoading && (
          <div className="flex flex-col items-center justify-center h-screen">
            <div className="animate-pulse bg-zinc-700 rounded p-8">
              <Boxes size={48} className="text-zinc-400" />
            </div>
            <p className="mt-4 text-zinc-400 italic">Loading...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-900/10 border border-red-500 text-red-400 rounded p-4">
            Error: {error}
          </div>
        )}

        {!isLoading && !error && !product && (
          <div className="flex flex-col items-center justify-center h-screen">
            <Boxes size={48} className="text-zinc-400" />
            <p className="text-slate-400 italic text-center py-12">
              Select a product
            </p>
          </div>
        )}

        {jitComputing && (
          <div className="flex flex-col items-center justify-center h-screen">
            <ResearchAnimation
              brandName={product?.brand}
              brandColor="#3b82f6"
              message={streamingText || "Processing..."}
              step="synthesis"
              progress={
                streamingText.length > 0 ? streamingText.length % 100 : 0
              }
            />
          </div>
        )}

        {rendered && product && (
          <div className="opacity-100 transition-opacity duration-300 p-4">
            <h2 className="text-2xl font-semibold mb-4">{product.name}</h2>
            <div className="flex gap-2">
              {availableSources.map((source) => (
                <SourceBadge key={source} type={source} label={source} />
              ))}
            </div>
          </div>
        )}

        {renderedPartial && product && (
          <div className="opacity-100 transition-opacity duration-300 p-4">
            <h2 className="text-2xl font-semibold mb-4">{product.name}</h2>
            <div className="flex gap-2">
              {availableSources.map((source) => (
                <SourceBadge
                  key={source}
                  type={source}
                  label={source}
                  unavailable={unavailableSources.includes(source)}
                />
              ))}
            </div>
          </div>
        )}

        {/* Example Product Selection (Replace with your actual product selection) */}
        {!isLoading &&
          !error &&
          !jitComputing &&
          !rendered &&
          !renderedPartial &&
          product === null && (
            <div className="p-4">
              <h3 className="text-lg font-medium mb-2">Available Products</h3>
              {/* Replace with actual product list */}
              <button
                onClick={() =>
                  handleProductSelect({
                    id: "product123",
                    name: "Example Product",
                    brand: "Example Brand",
                    brand_logo: "",
                    galaxy_id: "galaxy1",
                    spectrum_id: "spectrum1",
                    category: "category",
                    subcategory: "subcategory",
                    price: 100,
                    price_eilat: 110,
                    currency: "USD",
                    tier: "MID",
                    market_price_estimate: 120,
                    market_price_peers: 115,
                    image_url: "",
                    image_gallery: [],
                    description: "",
                    description_short: "",
                    specs: {},
                    features: [],
                    faq: [],
                    audiences: [],
                    rating: 4.5,
                    review_count: 10,
                    pros: [],
                    cons: [],
                    contextual_data: {},
                    quality_score: 85,
                    data_status: "GOOD",
                    data_missing: [],
                    halilit_url: "",
                    official_url: "",
                    sources: [],
                  } as ConductorProduct)
                }
                className="bg-zinc-700 hover:bg-zinc-600 text-zinc-100 font-medium py-2 px-4 rounded"
              >
                Select Example Product
              </button>
            </div>
          )}
      </div>
    </GlobalErrorBoundary>
  );
};

export default ExplorerView;
