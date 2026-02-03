import {
  AlertTriangle,
  ChevronRight,
  FileText,
  ShoppingCart,
  SquareArrowOutUpRight,
  X,
  Zap,
  Shield,
  Activity,
} from "lucide-react";
import { useEffect, useState } from "react";
import { getPrice } from "../../lib/priceFormatter";
import { useNavigationStore } from "../../store/navigationStore";
import ProductSpecs from "../ProductSpecs";
import ConfidenceBadge from "../ConfidenceBadge";
import ValidationPipeline from "../ValidationPipeline";
import { ImageWithFallback } from "../ImageWithFallback";
import type { Product } from "../../types";

interface OfficialMedia {
  url: string;
  type: string; // 'pdf', 'image', 'video', 'specification'
  label: string;
  source_domain?: string;
}

interface RelatedProduct {
  sku?: string;
  name: string;
  brand: string;
  price?: string | number;
  image_url?: string;
  logo_url?: string;
  category?: string;
  inStock?: boolean;
}

interface ProductData {
  id: string;
  name: string;
  brand: string;
  category: string;
  description: string;
  price?: string;
  official_manuals?: OfficialMedia[];
  official_gallery?: string[];
  necessities?: RelatedProduct[];
  accessories?: RelatedProduct[];
  related?: RelatedProduct[];
  media?: {
    thumbnail?: string;
    gallery?: string[];
  };
  commercial?: {
    price?: string;
    link?: string;
  };
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  specs?: Record<string, any>;
}

export const ProductPopInterface = ({ productId }: { productId: string }) => {
  const { closeProductPop } = useNavigationStore();
  const [product, setProduct] = useState<ProductData | null>(null);
  const [fullProduct, setFullProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [_selectedMediaIndex, _setSelectedMediaIndex] = useState(0);
  const [activeDetailTab, setActiveDetailTab] = useState<
    "specs" | "confidence" | "pipeline" | "insights"
  >("specs");

  useEffect(() => {
    // Load product data from catalog
    const loadProduct = async () => {
      try {
        setLoading(true);
        const { catalogLoader } = await import("../../lib/catalogLoader");
        const loadedProduct = await catalogLoader.findProductById(productId);

        if (loadedProduct) {
          setFullProduct(loadedProduct); // Store full product for detail components

          // Transform loaded product to ProductData format
          const productData: ProductData = {
            id: loadedProduct.id || productId,
            name: loadedProduct.name || "Unknown Product",
            brand: loadedProduct.brand || "Unknown Brand",
            category:
              loadedProduct.main_category ||
              loadedProduct.category ||
              "Uncategorized",
            description:
              loadedProduct.description || "No description available",
            price: getPrice(loadedProduct),
            official_manuals: loadedProduct.official_manuals,
            official_gallery: loadedProduct.official_gallery,
            // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-explicit-any
            necessities: loadedProduct.necessities as any,
            // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-explicit-any
            accessories: loadedProduct.accessories as any,
            // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-explicit-any
            related: loadedProduct.related as any,
            specs: loadedProduct.specifications,
          };
          setProduct(productData);
        } else {
          setProduct(null);
        }
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

  return (
    <div className="w-full max-w-4xl h-[80vh] bg-zinc-900 border border-zinc-700 rounded-xl relative shadow-2xl flex flex-col overflow-hidden">
      {/* Header */}
      <div className="h-12 bg-zinc-800 border-b border-zinc-700 flex items-center justify-between px-4">
        <span className="text-xs font-mono text-zinc-500">{productId}</span>
        <button
          onClick={closeProductPop}
          className="text-zinc-400 hover:text-white transition-colors"
        >
          <X className="w-6 h-6" />
        </button>
      </div>

      {/* Main Content Area - Two Sections */}
      <div className="flex-1 overflow-y-auto">
        {/* Top Section: Product Info & Official Resources (3-column grid) */}
        <div className="p-8 grid grid-cols-3 gap-6 border-b border-zinc-700">
          {/* Left Column: Product Info */}
          <div className="col-span-1 space-y-4">
            <div className="space-y-3">
              <div>
                <h2 className="text-2xl font-bold text-white mb-1">
                  {product?.name || productId}
                </h2>
                <p className="text-sm text-zinc-400">
                  {product?.brand || "Brand Unknown"}
                </p>
              </div>

              {/* Info Panel: Badges, Confidence, Price, Key Specs */}
              <div className="bg-zinc-800/60 border border-amber-500/30 rounded-lg p-3 space-y-3">
                {/* Confidence & Badges Row */}
                <div className="flex items-center gap-3">
                  {/* Confidence Score */}
                  <div className="flex items-center gap-2 flex-1">
                    <div className="text-[10px] font-mono text-zinc-500 uppercase">
                      Confidence
                    </div>
                    <div className="flex-1 h-1.5 bg-zinc-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-amber-500"
                        style={{
                          width: `${fullProduct?.pill_data?.ui_meta?.y_axis_score || 0}%`,
                        }}
                      />
                    </div>
                    <span className="text-[11px] font-bold text-amber-500 min-w-[2.5rem] text-right">
                      {fullProduct?.pill_data?.ui_meta?.y_axis_score || 0}%
                    </span>
                  </div>

                  {/* Badges */}
                  {fullProduct?.pill_data?.ui_meta?.badges &&
                    fullProduct.pill_data.ui_meta.badges.length > 0 && (
                      <div className="flex gap-1">
                        {fullProduct.pill_data.ui_meta.badges.map((badge) => (
                          <span
                            key={badge}
                            className="text-[9px] font-bold px-2 py-0.5 rounded bg-amber-500/20 border border-amber-500/50 text-amber-400 whitespace-nowrap"
                          >
                            {badge}
                          </span>
                        ))}
                      </div>
                    )}
                </div>

                {/* Price & Category */}
                <div className="flex gap-3 text-sm">
                  <div>
                    <p className="text-[10px] text-zinc-500 uppercase font-mono">
                      Price
                    </p>
                    <p className="text-amber-400 font-semibold">
                      ₪
                      {Math.round(
                        fullProduct?.pill_data?.commercial_meta?.price ||
                          fullProduct?.price ||
                          product?.price ||
                          0,
                      ).toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-[10px] text-zinc-500 uppercase font-mono">
                      Category
                    </p>
                    <p className="text-zinc-300">
                      {product?.category || "Unknown"}
                    </p>
                  </div>
                </div>

                {/* Key Specs (first 3) */}
                {fullProduct?.pill_data?.specs &&
                  Object.keys(fullProduct.pill_data.specs).length > 0 && (
                    <div className="space-y-1 pt-2 border-t border-zinc-700">
                      <p className="text-[10px] text-zinc-500 uppercase font-mono">
                        Key Specs
                      </p>
                      <div className="grid grid-cols-1 gap-1">
                        {Object.entries(fullProduct.pill_data.specs)
                          .slice(0, 3)
                          .map(([key, value]) => (
                            <div
                              key={key}
                              className="flex justify-between text-[10px]"
                            >
                              <span className="text-zinc-500 capitalize">
                                {key.replace(/_/g, " ")}
                              </span>
                              <span className="text-zinc-300 font-mono text-right">
                                {String(value).substring(0, 25)}
                              </span>
                            </div>
                          ))}
                      </div>
                    </div>
                  )}

                {/* Verified Sources */}
                {fullProduct?.pill_data?.context_meta?.sources_of_truth &&
                  fullProduct.pill_data.context_meta.sources_of_truth.length >
                    0 && (
                    <div className="space-y-1 pt-2 border-t border-zinc-700">
                      <p className="text-[10px] text-zinc-500 uppercase font-mono">
                        Verified By
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {fullProduct.pill_data.context_meta.sources_of_truth
                          .slice(0, 2)
                          .map((source, idx) => (
                            <span
                              key={idx}
                              className="text-[9px] px-2 py-0.5 rounded bg-green-500/10 border border-green-500/30 text-green-400 whitespace-nowrap"
                            >
                              ✓{" "}
                              {typeof source === "string"
                                ? source
                                : source.name}
                            </span>
                          ))}
                      </div>
                    </div>
                  )}

                {/* Key Pros/Tips */}
                {fullProduct?.pill_data?.context_meta?.pros &&
                  fullProduct.pill_data.context_meta.pros.length > 0 && (
                    <div className="space-y-1 pt-2 border-t border-zinc-700">
                      <p className="text-[10px] text-zinc-500 uppercase font-mono">
                        Key Points
                      </p>
                      <ul className="space-y-0.5">
                        {fullProduct.pill_data.context_meta.pros
                          .slice(0, 2)
                          .map((pro, idx) => (
                            <li key={idx} className="text-[9px] text-zinc-300">
                              • {pro.substring(0, 40)}
                              {pro.length > 40 ? "..." : ""}
                            </li>
                          ))}
                      </ul>
                    </div>
                  )}
              </div>
            </div>

            {/* Media Thumbnail Preview */}
            <div className="bg-zinc-800 rounded-lg p-4 aspect-square flex items-center justify-center border border-zinc-700 overflow-hidden">
              <ImageWithFallback
                src={product?.official_gallery?.[_selectedMediaIndex]}
                alt={product?.name || "Product image"}
                fallbackText={product?.id || "Product"}
                className="w-full h-full"
              />
            </div>
          </div>

          {/* Center Column: Details & Specs */}
          <div className="col-span-1 space-y-4">
            <div className="space-y-2">
              <p className="text-xs font-mono text-zinc-500 uppercase">
                Details
              </p>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-zinc-500">Category:</span>
                  <span className="text-white">
                    {product?.category || "Unknown"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-500">Price:</span>
                  <span className="text-white font-semibold">
                    {product?.price || "TBD"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-500">Status:</span>
                  <span className="text-green-500">In Stock</span>
                </div>
              </div>
            </div>

            {/* Description Section */}
            <div className="space-y-2">
              <p className="text-xs font-mono text-zinc-500 uppercase">
                Description
              </p>
              <p className="text-sm text-zinc-300 leading-relaxed">
                {product?.description ||
                  "No description available for this product."}
              </p>
            </div>
          </div>

          {/* Right Column: MediaBar (Official Resources) */}
          <div className="col-span-1 space-y-4">
            <div className="space-y-2">
              <p className="text-xs font-mono text-zinc-500 uppercase flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Official Resources
              </p>
              <p className="text-xs text-zinc-600">
                Documentation and media from the official manufacturer
              </p>
            </div>

            {/* MediaBar - Official Manuals & Resources */}
            <MediaBar manuals={[]} gallery={[]} productId={productId} />
          </div>
        </div>

        {/* Bottom Section: Product Relationships (Necessities, Accessories, Related) */}
        <div className="p-8 border-t border-zinc-700">
          <div className="mb-6">
            <h3 className="text-xs font-mono text-zinc-500 uppercase mb-4 flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Enhanced Details
            </h3>

            {/* Tab Navigation */}
            <div className="flex gap-2 border-b border-zinc-700 overflow-x-auto">
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
                onClick={() => setActiveDetailTab("confidence")}
                className={`px-4 py-2 text-xs font-semibold whitespace-nowrap border-b-2 transition-colors ${
                  activeDetailTab === "confidence"
                    ? "border-blue-500 text-blue-400"
                    : "border-transparent text-zinc-500 hover:text-zinc-300"
                }`}
              >
                Trust & Sources
              </button>
              <button
                onClick={() => setActiveDetailTab("pipeline")}
                className={`px-4 py-2 text-xs font-semibold whitespace-nowrap border-b-2 transition-colors ${
                  activeDetailTab === "pipeline"
                    ? "border-blue-500 text-blue-400"
                    : "border-transparent text-zinc-500 hover:text-zinc-300"
                }`}
              >
                Validation
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
          </div>

          {/* Tab Content */}
          <div className="bg-zinc-800/50 rounded-lg p-6 border border-zinc-700">
            {activeDetailTab === "specs" && fullProduct && (
              <ProductSpecs
                specs={fullProduct.pill_data?.specs || fullProduct.specs}
                category={fullProduct.category}
              />
            )}

            {activeDetailTab === "confidence" && fullProduct?.pill_data && (
              <ConfidenceBadge
                score={fullProduct.pill_data.ui_meta?.y_axis_score}
                badges={fullProduct.pill_data.ui_meta?.badges}
                sourcesOfTruth={
                  fullProduct.pill_data.context_meta?.sources_of_truth
                }
                showDetailed={true}
              />
            )}

            {activeDetailTab === "pipeline" && fullProduct?.pill_data && (
              <ValidationPipeline
                pipeline={fullProduct.pill_data.validation_pipeline}
                score={fullProduct.pill_data.ui_meta?.y_axis_score}
              />
            )}

            {activeDetailTab === "insights" &&
              fullProduct?.pill_data?.context_meta && (
                <div className="space-y-6">
                  {fullProduct.pill_data.context_meta.pros &&
                    fullProduct.pill_data.context_meta.pros.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-green-400 text-sm mb-3 flex items-center gap-2">
                          <span>✅</span> Strengths
                        </h4>
                        <ul className="space-y-2">
                          {fullProduct.pill_data.context_meta.pros.map(
                            (pro, idx) => (
                              <li
                                key={idx}
                                className="text-xs text-zinc-300 pl-6 border-l-2 border-green-500"
                              >
                                {pro}
                              </li>
                            ),
                          )}
                        </ul>
                      </div>
                    )}

                  {fullProduct.pill_data.context_meta.cons &&
                    fullProduct.pill_data.context_meta.cons.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-amber-400 text-sm mb-3 flex items-center gap-2">
                          <span>⚠️</span> Considerations
                        </h4>
                        <ul className="space-y-2">
                          {fullProduct.pill_data.context_meta.cons.map(
                            (con, idx) => (
                              <li
                                key={idx}
                                className="text-xs text-zinc-300 pl-6 border-l-2 border-amber-500"
                              >
                                {con}
                              </li>
                            ),
                          )}
                        </ul>
                      </div>
                    )}

                  {fullProduct.pill_data.context_meta.tips &&
                    fullProduct.pill_data.context_meta.tips.length > 0 && (
                      <div>
                        <h4 className="font-semibold text-blue-400 text-sm mb-3 flex items-center gap-2">
                          <span>💡</span> Expert Tips
                        </h4>
                        <ul className="space-y-2">
                          {fullProduct.pill_data.context_meta.tips.map(
                            (tip, idx) => (
                              <li
                                key={idx}
                                className="text-xs text-zinc-300 pl-6 border-l-2 border-blue-500"
                              >
                                {tip}
                              </li>
                            ),
                          )}
                        </ul>
                      </div>
                    )}

                  {!fullProduct.pill_data.context_meta.pros &&
                    !fullProduct.pill_data.context_meta.cons &&
                    !fullProduct.pill_data.context_meta.tips && (
                      <p className="text-xs text-zinc-500 text-center py-4">
                        No insights available
                      </p>
                    )}
                </div>
              )}
          </div>
        </div>

        {/* Original Relationships Section */}
        <div className="p-8">
          <RelationshipSection
            necessities={[]}
            accessories={[]}
            related={[]}
            onSelectProduct={(_product) => {
              // Handle product selection from relationships
            }}
          />
        </div>
      </div>
    </div>
  );
};

// ============================================================================
// MediaBar Component - Official Documentation & Resources
// ============================================================================

interface MediaBarProps {
  manuals: OfficialMedia[];
  gallery: string[];
  productId?: string;
}

const MediaBar = ({ manuals, gallery }: MediaBarProps) => {
  const [activeTab, setActiveTab] = useState<"manuals" | "gallery">("manuals");

  if (manuals.length === 0 && gallery.length === 0) {
    return (
      <div className="bg-zinc-800 rounded-lg p-4 border border-zinc-700 text-center">
        <p className="text-xs text-zinc-500">
          No official resources available yet
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Tab Navigation */}
      {manuals.length > 0 && gallery.length > 0 && (
        <div className="flex gap-2 border-b border-zinc-700">
          <button
            onClick={() => setActiveTab("manuals")}
            className={`px-3 py-2 text-xs font-mono border-b-2 transition-colors ${
              activeTab === "manuals"
                ? "border-blue-500 text-blue-400"
                : "border-transparent text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Manuals ({manuals.length})
          </button>
          <button
            onClick={() => setActiveTab("gallery")}
            className={`px-3 py-2 text-xs font-mono border-b-2 transition-colors ${
              activeTab === "gallery"
                ? "border-blue-500 text-blue-400"
                : "border-transparent text-zinc-500 hover:text-zinc-300"
            }`}
          >
            Gallery ({gallery.length})
          </button>
        </div>
      )}

      {/* Manuals List */}
      {activeTab === "manuals" && manuals.length > 0 && (
        <div className="space-y-2">
          {manuals.map((manual, idx) => (
            <a
              key={idx}
              href={manual.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 p-3 bg-zinc-800 rounded-lg border border-zinc-700 hover:border-blue-500 hover:bg-zinc-700 transition-colors group"
            >
              <FileText className="w-4 h-4 text-blue-400 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-white truncate">
                  {manual.label}
                </p>
                <p className="text-xs text-zinc-500">
                  {manual.source_domain || "Official Source"}
                </p>
              </div>
              <SquareArrowOutUpRight className="w-4 h-4 text-zinc-500 group-hover:text-blue-400 flex-shrink-0" />
            </a>
          ))}
        </div>
      )}

      {/* Gallery Preview */}
      {activeTab === "gallery" && gallery.length > 0 && (
        <div className="grid grid-cols-2 gap-2">
          {gallery.slice(0, 4).map((url, idx) => (
            <a
              key={idx}
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="aspect-square bg-zinc-800 rounded-lg border border-zinc-700 overflow-hidden hover:border-blue-500 transition-colors flex items-center justify-center group"
            >
              <div className="text-center">
                <img
                  src={url}
                  alt={`Gallery ${idx + 1}`}
                  className="w-full h-full object-cover group-hover:opacity-80 transition-opacity"
                  onError={(e) => {
                    e.currentTarget.style.display = "none";
                  }}
                />
              </div>
            </a>
          ))}
        </div>
      )}

      {/* No Content Message */}
      {activeTab === "manuals" && manuals.length === 0 && (
        <div className="text-center p-4 text-zinc-500 text-xs">
          No manuals available
        </div>
      )}

      {activeTab === "gallery" && gallery.length === 0 && (
        <div className="text-center p-4 text-zinc-500 text-xs">
          No gallery images available
        </div>
      )}

      {/* Official Source Attribution */}
      <div className="border-t border-zinc-700 pt-2 mt-3">
        <p className="text-xs text-zinc-600 flex items-center gap-1">
          <span className="w-1 h-1 bg-green-500 rounded-full" />
          All content sourced from official manufacturer websites
        </p>
      </div>
    </div>
  );
};

// ============================================================================
// RelationshipSection Component - Necessities, Accessories, Related Products
// ============================================================================

interface RelationshipSectionProps {
  necessities: RelatedProduct[];
  accessories: RelatedProduct[];
  related: RelatedProduct[];
  onSelectProduct?: (product: RelatedProduct) => void;
}

const RelationshipSection = ({
  necessities,
  accessories,
  related,
  onSelectProduct,
}: RelationshipSectionProps) => {
  const hasAnyRelationships =
    necessities.length > 0 || accessories.length > 0 || related.length > 0;

  if (!hasAnyRelationships) {
    return (
      <div className="text-center py-8 text-zinc-600">
        <ChevronRight className="w-8 h-8 mx-auto mb-2 opacity-30" />
        <p className="text-sm">No related products available</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Necessities Section - High Priority */}
      {necessities.length > 0 && (
        <section className="space-y-3">
          <h3 className="text-sm font-bold uppercase tracking-wider text-red-400 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4" />
            Required for Operation
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {necessities.slice(0, 4).map((product) => (
              <RelationshipCardComponent
                key={product.sku}
                product={product}
                variant="necessity"
                onSelect={onSelectProduct}
              />
            ))}
          </div>
        </section>
      )}

      {/* Accessories Section */}
      {accessories.length > 0 && (
        <section className="space-y-3">
          <h3 className="text-sm font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-2">
            <ShoppingCart className="w-4 h-4" />
            Official Accessories
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
            {accessories.slice(0, 8).map((product) => (
              <RelationshipCardComponent
                key={product.sku}
                product={product}
                variant="accessory"
                onSelect={onSelectProduct}
              />
            ))}
          </div>
        </section>
      )}

      {/* Related Products Section */}
      {related.length > 0 && (
        <section className="space-y-3">
          <h3 className="text-sm font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-2">
            <ChevronRight className="w-4 h-4" />
            Similar Models
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {related.slice(0, 6).map((product) => (
              <RelationshipCardComponent
                key={product.sku}
                product={product}
                variant="related"
                onSelect={onSelectProduct}
              />
            ))}
          </div>
        </section>
      )}
    </div>
  );
};

// ============================================================================
// RelationshipCard Component - Individual relationship card
// ============================================================================

interface RelationshipCardComponentProps {
  product: RelatedProduct;
  variant?: "necessity" | "accessory" | "related" | "ghost";
  onSelect?: (product: RelatedProduct) => void;
}

const RelationshipCardComponent = ({
  product,
  variant = "related",
  onSelect,
}: RelationshipCardComponentProps) => {
  const getVariantStyles = () => {
    const baseStyles =
      "relative p-3 rounded border transition-all hover:shadow-lg cursor-pointer group";

    switch (variant) {
      case "necessity":
        return `${baseStyles} border-red-500/50 bg-red-950/20 hover:border-red-400 hover:bg-red-950/40`;
      case "accessory":
        return `${baseStyles} border-emerald-500/50 bg-emerald-950/20 hover:border-emerald-400 hover:bg-emerald-950/40`;
      case "ghost":
        return `${baseStyles} border-zinc-700/50 bg-transparent hover:border-zinc-600 hover:bg-zinc-900/50`;
      case "related":
      default:
        return `${baseStyles} border-zinc-600/50 bg-zinc-900/30 hover:border-zinc-500 hover:bg-zinc-900/60`;
    }
  };

  const getIconColor = () => {
    switch (variant) {
      case "necessity":
        return "text-red-400";
      case "accessory":
        return "text-emerald-400";
      case "related":
      case "ghost":
      default:
        return "text-zinc-400";
    }
  };

  const getIcon = () => {
    switch (variant) {
      case "necessity":
        return <AlertTriangle className={`w-4 h-4 ${getIconColor()}`} />;
      case "accessory":
        return <ShoppingCart className={`w-4 h-4 ${getIconColor()}`} />;
      case "related":
      case "ghost":
      default:
        return <ChevronRight className={`w-4 h-4 ${getIconColor()}`} />;
    }
  };

  const handleClick = () => {
    if (onSelect) {
      onSelect(product);
    }
  };

  return (
    <div
      className={getVariantStyles()}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      aria-label={`View ${product.name}`}
    >
      {/* Stock Status Badge */}
      {product.inStock === false && (
        <div className="absolute top-1 right-1 px-2 py-0.5 bg-red-500/80 text-white text-xs rounded">
          Out of Stock
        </div>
      )}

      <div className="flex items-start justify-between gap-2">
        <div className="flex-1">
          {/* Brand Logo (if available) */}
          {product.logo_url && (
            <img
              src={product.logo_url}
              alt={product.brand}
              className="h-4 grayscale opacity-70 mb-2"
            />
          )}

          {/* Product Name */}
          <h4 className="text-sm font-semibold text-white line-clamp-2 group-hover:text-emerald-300 transition-colors">
            {product.name}
          </h4>

          {/* Brand + Category */}
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-zinc-500">{product.brand}</span>
            {product.category && (
              <>
                <span className="text-zinc-700">•</span>
                <span className="text-xs text-zinc-500">
                  {product.category}
                </span>
              </>
            )}
          </div>

          {/* Price */}
          <div className="mt-2 text-sm font-mono font-bold text-emerald-400">
            {typeof product.price === "number"
              ? `$${product.price.toFixed(2)}`
              : product.price}
          </div>
        </div>

        {/* Icon (Right Side) */}
        <div className="flex-shrink-0 mt-1">{getIcon()}</div>
      </div>

      {/* Variant Label (for necessity) */}
      {variant === "necessity" && (
        <div className="mt-2 text-xs text-red-300 flex items-center gap-1 font-semibold">
          <AlertTriangle className="w-3 h-3" />
          REQUIRED
        </div>
      )}

      {/* Hover Overlay with Product Image */}
      {product.image_url && variant !== "ghost" && (
        <div className="absolute inset-0 rounded opacity-0 group-hover:opacity-20 transition-opacity pointer-events-none overflow-hidden">
          <img
            src={product.image_url}
            alt={product.name}
            className="w-full h-full object-cover blur-sm"
          />
        </div>
      )}
    </div>
  );
};
