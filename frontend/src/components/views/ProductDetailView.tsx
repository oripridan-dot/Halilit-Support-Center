import React, { useEffect, useState } from "react";
import { useNavigationStore } from "../../store/navigationStore";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import { ConductorProduct } from "../../types";
import ImageWithFallback from "../ImageWithFallback";
import JITBadge from "../ProductDetail/JITBadge";
import ProductImageCarousel from "../ProductDetail/ProductImageCarousel";
import EcosystemTab from "../ProductDetail/EcosystemTab";
import { ProductDetailHeader } from "../ProductDetail/ProductDetailHeader";

const ProductDetailView: React.FC = () => {
  const navigation = useNavigationStore();
  const { activeProductId } = navigation;
  const { products, isLoading, error } = useConductorCatalog();
  const [product, setProduct] = useState<ConductorProduct | undefined>(
    undefined,
  );

  useEffect(() => {
    if (products && activeProductId) {
      const foundProduct = products.find((p) => p.id === activeProductId);
      setProduct(foundProduct);
    }
  }, [products, activeProductId]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <svg
          className="animate-spin h-10 w-10 text-blue-500"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          ></circle>
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 6.627 5.373 12 12 12v-7.291z"
          ></path>
        </svg>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          <strong className="font-bold">Error!</strong> {error}
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-zinc-300">Product not found.</div>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 min-h-screen pb-6">
      <ProductDetailHeader product={product} />
      <div className="container mx-auto p-4 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="col-span-1 lg:col-span-1">
          <ImageWithFallback
            src={product.image_url || ""}
            alt={product.name}
            className="rounded-lg"
          />
        </div>
        <div className="col-span-1 lg:col-span-1">
          <div className="mb-4">
            <h1 className="text-2xl font-bold text-white">{product.name}</h1>
            <div className="flex items-center space-x-2 mt-2">
              <JITBadge productId={product.id} />
            </div>
            {product.description && (
              <p className="text-zinc-300 mt-2 leading-relaxed">
                {product.description}
              </p>
            )}
          </div>
          <div className="mb-4">
            <ProductImageCarousel productId={product.id} />
          </div>

          <EcosystemTab productId={product.id} />
        </div>
      </div>
    </div>
  );
};

export default ProductDetailView;
