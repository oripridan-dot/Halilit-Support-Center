import { X } from "lucide-react";
import React, { useEffect, useState } from "react";
import { useNavigationStore } from "../../store/navigationStore";
import { ImageWithFallback } from "../ImageWithFallback";
import { getPrice } from "../../lib/priceFormatter";
import type { Product } from "../../types";

/**
 * Simple inline product detail card - v6.0 Simplified
 * Removes ProductPopInterface modal complexity
 * Shows only: image, name, brand, price, description
 */
export const ProductPopInterface = ({ productId }: { productId: string }) => {
  const { closeProductPop } = useNavigationStore();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProduct = async () => {
      try {
        setLoading(true);
        const { catalogLoader } = await import("../../lib/catalogLoader");
        const loaded = await catalogLoader.findProductById(productId);
        if (loaded) {
          setProduct(loaded);
        }
      } catch (err) {
        console.error("Failed to load product:", err);
      } finally {
        setLoading(false);
      }
    };

    if (productId) {
      loadProduct();
    }
  }, [productId]);

  if (!productId) return null;

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <div className="bg-slate-900 border border-cyan-500/30 rounded-lg max-w-md w-full max-h-96 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-cyan-500/20">
          <h3 className="text-sm font-bold text-white truncate">
            Product Details
          </h3>
          <button
            onClick={closeProductPop}
            className="p-1 text-zinc-400 hover:text-cyan-400 transition"
          >
            <X size={16} />
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-80 p-4 space-y-3">
          {loading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-cyan-500" />
            </div>
          ) : product ? (
            <>
              {/* Image */}
              <div className="relative h-32 bg-slate-800 rounded overflow-hidden">
                <ImageWithFallback
                  src={
                    (typeof product.images?.main === "string"
                      ? product.images.main
                      : product.images?.main?.url) ||
                    (typeof product.image_hero === "string"
                      ? product.image_hero
                      : product.image_hero?.url) ||
                    (typeof product.image === "string"
                      ? product.image
                      : product.image?.url) ||
                    undefined
                  }
                  alt={product.name || "Product"}
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Details */}
              <div>
                <p className="text-xs text-cyan-400 font-mono">
                  {product.brand}
                </p>
                <p className="text-sm font-bold text-white truncate">
                  {product.name}
                </p>
              </div>

              {/* Price */}
              <div className="text-lg font-black text-green-400">
                {getPrice(product) || "Price TBD"}
              </div>

              {/* Description */}
              <div className="text-xs text-zinc-300 line-clamp-3">
                {product.description ||
                  product.description_short ||
                  "No description"}
              </div>

              {/* Category */}
              {product.category && (
                <div className="text-xs text-zinc-500">{product.category}</div>
              )}
            </>
          ) : (
            <div className="text-xs text-zinc-400">Product not found</div>
          )}
        </div>
      </div>
    </div>
  );
};
