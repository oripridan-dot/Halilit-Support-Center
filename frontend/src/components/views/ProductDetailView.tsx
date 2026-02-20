import React, { useState, useEffect } from 'react';
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
import ResponsiveImage from '@/components/ResponsiveImage/ResponsiveImage';

const ProductDetailView: React.FC = () => {
  const { products } = useConductorCatalog();
  const { activeProductId } = useNavigationStore();
  const [isCopied, setIsCopied] = useState(false);
  const { jitProductData } = useJITIntelligence();

  const product = React.useMemo(() => {
    return products.find((p) => p.id === activeProductId);
  }, [products, activeProductId]);

  if (!product) {
    return (
      <div className="flex items-center justify-center h-screen dark:bg-zinc-900">
        <Loader2 className="animate-spin h-8 w-8 text-blue-500" />
      </div>
    );
  }

  return (
    <div className="dark:bg-zinc-900 min-h-screen">
      <div className="container mx-auto py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <ResponsiveImage
              imageBaseUrl={product.image_url}
              altText={product.name}
              className="rounded-lg shadow-md"
              sizes={{
                sm: 640,
                md: 768,
                lg: 1024,
                xl: 1280,
                "2xl": 1536,
              }}
            />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-zinc-100">{product.name}</h1>
            <p className="text-zinc-400 mt-2">{product.description}</p>
            <div className="mt-4">
              <ProductBadge product={product} />
            </div>
            {jitProductData && jitProductData[product.id] && (
              <JITBadge jitData={jitProductData[product.id]} />
            )}
            <div className="mt-6">
              <ProductImageCarousel product={product} />
            </div>
            <div className="mt-6">
              <EcosystemTab product={product} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailView;