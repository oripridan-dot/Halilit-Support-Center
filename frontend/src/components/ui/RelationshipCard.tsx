import { AlertTriangle, ChevronRight, ShoppingCart } from "lucide-react";
import React from "react";

export interface RelationshipCardProduct {
  sku: string;
  name: string;
  brand: string;
  price: string | number;
  image_url?: string;
  logo_url?: string;
  category?: string;
  inStock?: boolean;
}

export interface RelationshipCardProps {
  product: RelationshipCardProduct;
  variant?: "necessity" | "accessory" | "related" | "ghost";
  onSelect?: (product: RelationshipCardProduct) => void;
}

/**
 * RelationshipCard
 *
 * Displays related products (Necessities, Accessories, Related Products).
 * Each variant has different visual hierarchy and urgency.
 *
 * Variants:
 * - "necessity": Red border, warning icon (required for operation)
 * - "accessory": Green border, shopping icon (optional but recommended)
 * - "related": Gray border, chevron icon (similar products)
 * - "ghost": Minimal (used in compact grids)
 */
export const RelationshipCard: React.FC<RelationshipCardProps> = ({
  product,
  variant = "related",
  onSelect,
}) => {
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

export default RelationshipCard;
