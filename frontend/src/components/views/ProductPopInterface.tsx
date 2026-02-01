import { X } from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigationStore } from "../../store/navigationStore";
import ProductSpecs from "../ProductSpecs";
import { ImageWithFallback } from "../ImageWithFallback";
import type { Product } from "../../types";

export const ProductPopInterface = ({ productId }: { productId: string }) => {
  const { closeProductPop } = useNavigationStore();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeDetailTab, setActiveDetailTab] = useState<"specs" | "insights">(
    "specs",
  );

  useEffect(() => {
    // Load product data from catalog
    const loadProduct = async () => {
      try {
        setLoading(true);
        const { catalogLoader } = await import("../../lib/catalogLoader");
        const loadedProduct = await catalogLoader.findProductById(productId);
        setProduct(loadedProduct || null);
      } catch {
        setProduct(null);
      } finally {
        setLoading(false);
      }
    };

    loadProduct();
  }, [productId]);

  if (loading) {
    return (
      <div className="w-full max-w-4xl h-[80vh] bg-zinc-900 border border-zinc-700 rounded-xl relative shadow-2xl flex flex-col overflow-hidden items-center justify-center">
        <div className="text-zinc-400">Loading product details...</div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="w-full max-w-4xl h-[80vh] bg-zinc-900 border border-zinc-700 rounded-xl relative shadow-2xl flex flex-col overflow-hidden items-center justify-center">
        <div className="text-zinc-400">Product not found</div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl h-[80vh] bg-zinc-900 border border-zinc-700 rounded-xl relative shadow-2xl flex flex-col overflow-hidden">
      {/* Header */}
      <div className="h-12 bg-zinc-800 border-b border-zinc-700 flex items-center justify-between px-4">
        <div className="flex items-center gap-4">
          <span className="text-sm font-bold text-white">{product.name}</span>
          <span className="text-xs font-mono text-zinc-500">{product.id}</span>
        </div>
        <button
          onClick={closeProductPop}
          className="text-zinc-400 hover:text-white transition-colors"
        >
          <X className="w-6 h-6" />
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Product Overview */}
        <div className="grid grid-cols-3 gap-6">
          {/* Left: Image & Basic Info */}
          <div className="col-span-1 space-y-4">
            {product.image_hero && (
              <div className="bg-zinc-800 rounded-lg p-4 aspect-square flex items-center justify-center border border-zinc-700 overflow-hidden">
                <ImageWithFallback
                  src={product.image_hero.url}
                  alt={product.name || "Product image"}
                  fallbackText={product.id || "Product"}
                  className="w-full h-full object-cover"
                />
              </div>
            )}

            {/* Key Info */}
            <div className="bg-zinc-800/60 rounded-lg p-4 space-y-3 border border-zinc-700">
              <div>
                <p className="text-xs text-zinc-500 uppercase font-mono mb-1">
                  Brand
                </p>
                <p className="text-sm text-white font-semibold">
                  {product.brand_id || "Unknown"}
                </p>
              </div>
              <div>
                <p className="text-xs text-zinc-500 uppercase font-mono mb-1">
                  Category
                </p>
                <p className="text-sm text-white">
                  {product.category || "Uncategorized"}
                </p>
              </div>
              {product.price && (
                <div>
                  <p className="text-xs text-zinc-500 uppercase font-mono mb-1">
                    Price
                  </p>
                  <p className="text-sm text-amber-400 font-semibold">
                    {product.currency} {product.price.toLocaleString()}
                  </p>
                </div>
              )}
              <div>
                <p className="text-xs text-zinc-500 uppercase font-mono mb-1">
                  Stock Status
                </p>
                <p className="text-sm capitalize text-white">
                  {product.stock_status || "Unknown"}
                </p>
              </div>
              <div>
                <p className="text-xs text-zinc-500 uppercase font-mono mb-1">
                  Tier
                </p>
                <p className="text-sm text-white font-semibold">
                  {product.tier?.toUpperCase() || "UNKNOWN"} (
                  {product.tier_score}/100)
                </p>
              </div>
            </div>
          </div>

          {/* Center: Description */}
          <div className="col-span-1 space-y-3">
            <div>
              <h3 className="text-sm font-mono text-zinc-500 uppercase mb-2">
                Description
              </h3>
              <p className="text-sm text-zinc-300 leading-relaxed">
                {product.description_full ||
                  product.description_short ||
                  "No description available"}
              </p>
            </div>

            {/* Filter Tags */}
            {product.filter_tags && product.filter_tags.length > 0 && (
              <div>
                <h3 className="text-sm font-mono text-zinc-500 uppercase mb-2">
                  Tags
                </h3>
                <div className="flex flex-wrap gap-1">
                  {product.filter_tags.slice(0, 6).map((tag, idx) => (
                    <span
                      key={idx}
                      className="text-xs px-2 py-1 rounded bg-zinc-700 text-zinc-300"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right: Gallery */}
          <div className="col-span-1 space-y-3">
            <h3 className="text-sm font-mono text-zinc-500 uppercase mb-2">
              Gallery
            </h3>
            {product.image_gallery && product.image_gallery.length > 0 ? (
              <div className="grid grid-cols-2 gap-2">
                {product.image_gallery.slice(0, 4).map((img, idx) => (
                  <div
                    key={idx}
                    className="aspect-square bg-zinc-800 rounded-lg border border-zinc-700 overflow-hidden"
                  >
                    <img
                      src={img.url}
                      alt={img.alt || `Gallery ${idx + 1}`}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.currentTarget.style.display = "none";
                      }}
                    />
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-zinc-500">No gallery images</p>
            )}
          </div>
        </div>

        {/* Details Tabs */}
        <div className="border-t border-zinc-700 pt-6">
          <div className="flex gap-2 border-b border-zinc-700 mb-4 overflow-x-auto">
            <button
              onClick={() => setActiveDetailTab("specs")}
              className={`px-4 py-2 text-xs font-semibold whitespace-nowrap border-b-2 transition-colors ${
                activeDetailTab === "specs"
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-zinc-500 hover:text-zinc-300"
              }`}
            >
              Specifications
            </button>
            <button
              onClick={() => setActiveDetailTab("insights")}
              className={`px-4 py-2 text-xs font-semibold whitespace-nowrap border-b-2 transition-colors ${
                activeDetailTab === "insights"
                  ? "border-blue-500 text-blue-400"
                  : "border-transparent text-zinc-500 hover:text-zinc-300"
              }`}
            >
              Insights
            </button>
          </div>

          {/* Tab Content */}
          <div className="bg-zinc-800/50 rounded-lg p-4 border border-zinc-700">
            {activeDetailTab === "specs" && product.specs && (
              <ProductSpecs specs={product.specs} category={product.category} />
            )}

            {activeDetailTab === "insights" && (
              <div className="space-y-6">
                {/* Pros */}
                {product.pros && product.pros.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-green-400 text-sm mb-3 flex items-center gap-2">
                      <span>✅</span> Strengths
                    </h4>
                    <ul className="space-y-2">
                      {product.pros.map((pro, idx) => (
                        <li
                          key={idx}
                          className="text-xs text-zinc-300 pl-6 border-l-2 border-green-500"
                        >
                          {pro}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Cons */}
                {product.cons && product.cons.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-amber-400 text-sm mb-3 flex items-center gap-2">
                      <span>⚠️</span> Considerations
                    </h4>
                    <ul className="space-y-2">
                      {product.cons.map((con, idx) => (
                        <li
                          key={idx}
                          className="text-xs text-zinc-300 pl-6 border-l-2 border-amber-500"
                        >
                          {con}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Expert Tips */}
                {product.expert_tips && product.expert_tips.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-blue-400 text-sm mb-3 flex items-center gap-2">
                      <span>💡</span> Expert Tips
                    </h4>
                    <ul className="space-y-2">
                      {product.expert_tips.map((tip, idx) => (
                        <li
                          key={idx}
                          className="text-xs text-zinc-300 pl-6 border-l-2 border-blue-500"
                        >
                          {tip}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {(!product.pros || product.pros.length === 0) &&
                  (!product.cons || product.cons.length === 0) &&
                  (!product.expert_tips ||
                    product.expert_tips.length === 0) && (
                    <p className="text-xs text-zinc-500 text-center py-4">
                      No insights available
                    </p>
                  )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
