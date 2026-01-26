import {
  AlertTriangle,
  ChevronRight,
  FileText,
  ShoppingCart,
  SquareArrowOutUpRight,
  X,
} from "lucide-react";
import { useEffect, useState } from "react";
import { getPrice } from "../../lib/priceFormatter";
import { useNavigationStore } from "../../store/navigationStore";

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
  const [loading, setLoading] = useState(true);
  const [_selectedMediaIndex, _setSelectedMediaIndex] = useState(0);

  useEffect(() => {
    // Load product data from catalog
    const loadProduct = async () => {
      try {
        setLoading(true);
        const { catalogLoader } = await import("../../lib/catalogLoader");
        const loadedProduct = await catalogLoader.findProductById(productId);

        if (loadedProduct) {
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
      {/* Flight Case Header */}
      <div className="h-12 bg-zinc-800 border-b border-zinc-700 flex items-center justify-between px-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span className="ml-2 text-xs font-mono text-zinc-400">
            PRODUCT_ID: {productId}
          </span>
        </div>
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
            <div>
              <h2 className="text-2xl font-bold text-white mb-1">
                {product?.name || productId}
              </h2>
              <p className="text-sm text-zinc-400">
                {product?.brand || "Brand Unknown"}
              </p>
            </div>

            {/* Media Thumbnail Preview */}
            <div className="bg-zinc-800 rounded-lg p-4 aspect-square flex items-center justify-center border border-zinc-700 overflow-hidden">
              {product?.official_gallery?.[_selectedMediaIndex] ? (
                <img
                  src={product.official_gallery[_selectedMediaIndex]}
                  alt={product.name}
                  className="w-full h-full object-contain"
                  onError={() => {}}
                />
              ) : (
                <div className="text-center">
                  <p className="text-zinc-400 text-sm">No Image Available</p>
                  <p className="text-xs text-zinc-600 mt-2">
                    ({product?.id || "Product"})
                  </p>
                </div>
              )}
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
