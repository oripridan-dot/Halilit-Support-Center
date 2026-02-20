import React, { useState, useEffect, useMemo } from 'react';
import { useNavigationStore } from '@/stores/navigationStore';
import { useConductorCatalog } from '@/hooks/useConductorCatalog';
import {
  ExternalLink,
  Check,
  Loader2,
} from 'lucide-react';
import ImageWithFallback from '@/components/common/ImageWithFallback';
import ProductImageCarousel from '@/components/ProductDetail/ProductImageCarousel';
import EcosystemTab from '@/components/ProductDetail/EcosystemTab';
import JITBadge from '@/components/ProductDetail/JITBadge';
import { useJITIntelligence } from '@/hooks/useJITIntelligence';
import { ConductorProduct } from '@/types/catalog';
import { ProductBadge } from '@/components/common/ProductBadge';

const ProductDetailView: React.FC = () => {
  const { products } = useConductorCatalog();
  const { activeProductId } = useNavigationStore();
  const [isCopied, setIsCopied] = useState(false);
  const { jitData, isLoading: isJITLoading, error: jitError } = useJITIntelligence(activeProductId);

  const product = useMemo(
    () => products.find((p) => p.id === activeProductId) ?? null,
    [products, activeProductId],
  );

  const isLoading = !product && !jitError;

  const handleCopyClick = async (sku: string | undefined) => {
    if (!sku) return;
    try {
      await navigator.clipboard.writeText(sku);
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const renderPrice = (product: ConductorProduct | null) => {
    if (!product) return null;
    if (product.price === 0 || !product.price) {
      return (
        <>
          ₪ Call for Price (IL)
          {product.data_trust.price_source && (
            <ProductBadge source={product.data_trust.price_source} />
          )}
        </>
      );
    }
    return (
      <>
        ₪ {product.price.toLocaleString('he-IL')} (IL)
        {product.price_eilat > 0 && (
          <span> | ₪ {product.price_eilat.toLocaleString('he-IL')} (Eilat)</span>
        )}
        {product.data_trust.price_source && (
            <ProductBadge source={product.data_trust.price_source} />
          )}
      </>
    );
  };

  if (isLoading) {
    return (
      <div className="bg-zinc-950 min-h-screen p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-1">
            <div className="bg-zinc-900 rounded-lg animate-pulse h-64"></div>
            <div className="bg-zinc-900 rounded-lg animate-pulse h-8 mt-2 w-2/3"></div>
            <div className="bg-zinc-900 rounded-lg animate-pulse h-6 mt-2 w-1/2"></div>
            <div className="bg-zinc-900 rounded-lg animate-pulse h-6 mt-2 w-1/4"></div>
          </div>
          <div className="md:col-span-2">
            <div className="bg-zinc-900 rounded-lg animate-pulse h-12 w-full"></div>
            <div className="bg-zinc-900 rounded-lg animate-pulse h-8 mt-2 w-3/4"></div>
            <div className="bg-zinc-900 rounded-lg animate-pulse h-6 mt-2 w-1/2"></div>
            <div className="bg-zinc-900 rounded-lg animate-pulse h-6 mt-2 w-1/3"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="bg-zinc-950 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-zinc-300 text-lg">Product not found</p>
          <button className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600">
            Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-zinc-950 min-h-screen p-4">
      {jitError && (
        <div className="bg-red-500 text-white p-2 rounded-md mb-4">
          Error loading JIT data.
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-1">
          <ImageWithFallback
            src={product.image_url}
            alt={product.name}
            className="rounded-lg w-full h-64 object-cover"
          />
          <ProductImageCarousel images={product.image_gallery || []} />
          <div className="flex items-center justify-between mt-2">
            <div className="flex items-center space-x-2">
              <span className="text-zinc-400">SKU:</span>
              <span className="text-zinc-200">{product.id}</span>
              <button
                onClick={() => handleCopyClick(product.id)}
                className="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 text-xs rounded-md px-2 py-1 flex items-center"
              >
                {isCopied ? <Check size={16} /> : "Copy"}
              </button>
            </div>
          </div>
          <div className="mt-2 text-zinc-200">{renderPrice(product)}</div>
          {product.halilit_url && (
            <a
              href={product.halilit_url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-2 inline-flex items-center px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            >
              <ExternalLink size={16} className="mr-2" />
              Halilit URL
            </a>
          )}
          <JITBadge productId={product.id} />
        </div>
        <div className="md:col-span-2">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-zinc-100 text-2xl font-semibold">{product.name}</h1>
              <p className="text-zinc-400">{product.brand}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailView;