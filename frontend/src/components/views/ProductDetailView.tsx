import React from 'react';

interface ResponsiveImageProps {
  imageBaseUrl: string;
  altText: string;
  className?: string;
  sizes?: {
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
    "2xl"?: number;
  };
}

const ResponsiveImage: React.FC<ResponsiveImageProps> = ({
  imageBaseUrl,
  altText,
  className,
  sizes = {},
}) => {
  const CDN_BASE_URL = process.env.NEXT_PUBLIC_IMAGE_CDN_URL;

  if (!CDN_BASE_URL) {
    console.warn('NEXT_PUBLIC_IMAGE_CDN_URL is not configured.');
    return <img src={imageBaseUrl} alt={altText} loading="lazy" className={`w-full h-full object-cover ${className || ''}`} />;
  }

  const generateSrcSet = (width: number, format: 'avif' | 'webp' | 'jpg') => {
    return `${CDN_BASE_URL}/${imageBaseUrl}?w=${width}&fm=${format}`;
  };

  const breakpoints = {
    sm: sizes.sm || 640,
    md: sizes.md || 768,
    lg: sizes.lg || 1024,
    xl: sizes.xl || 1280,
    "2xl": sizes["2xl"] || 1536,
  };

  return (
    <picture className={className}>
      {Object.entries(breakpoints)
        .sort(([, widthA], [, widthB]) => (widthA as number) - (widthB as number))
        .map(([size, width]) => {
          const maxWidth = width;
          const mediaQuery = `(max-width: ${maxWidth}px)`;

          return (
            <>
              <source
                key={`${size}-avif`}
                srcSet={generateSrcSet(width as number, 'avif')}
                type="image/avif"
                media={mediaQuery}
              />
              <source
                key={`${size}-webp`}
                srcSet={generateSrcSet(width as number, 'webp')}
                type="image/webp"
                media={mediaQuery}
              />
            </>
          );
        })}
      <img
        src={generateSrcSet(Object.values(breakpoints).sort((a,b) => b-a)[0], 'jpg')}
        alt={altText}
        loading="lazy"
        className="w-full h-full object-cover"
      />
    </picture>
  );
};

export default ResponsiveImage;

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
import ResponsiveImage from '@/components/ResponsiveImage/ResponsiveImage';

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
            <div className="bg-zinc-900 rounded-lg animate-pulse h-6 mt-2 w-1/4"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!product) {
    return <div>Product not found</div>;
  }

  return (
    <div className="bg-zinc-950 min-h-screen p-4">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-1">
          {product.image_url ? (
            <ResponsiveImage
              imageBaseUrl={product.image_url}
              altText={product.name}
              sizes={{
                sm: 320,
                md: 640,
                lg: 768,
                xl: 1024,
                "2xl": 1280,
              }}
            />
          ) : (
            <ImageWithFallback alt={product.name} />
          )}
          <div className="mt-4">
            {product.sku && (
              <div className="flex items-center justify-between bg-zinc-900 p-2 rounded-md">
                <span>SKU: {product.sku}</span>
                <button
                  onClick={() => handleCopyClick(product.sku)}
                  className={`px-2 py-1 rounded-md text-sm ${
                    isCopied ? 'bg-green-700' : 'bg-zinc-700'
                  }`}
                >
                  {isCopied ? 'Copied!' : 'Copy'}
                </button>
              </div>
            )}
            {jitData && !isJITLoading && (
              <JITBadge
                jitData={jitData}
                className="mt-2"
              />
            )}
            {isJITLoading && (
              <div className="mt-2 flex items-center justify-center">
                <Loader2 className="animate-spin h-5 w-5 text-zinc-400" />
              </div>
            )}
          </div>
        </div>
        <div className="md:col-span-2">
          <h1 className="text-2xl text-zinc-100">{product.name}</h1>
          <p className="text-sm text-zinc-400 mt-2">{product.description}</p>
          <div className="mt-4 text-zinc-100">{renderPrice(product)}</div>
          <ProductImageCarousel product={product} />
          <EcosystemTab productId={product.id} />
        </div>
      </div>
    </div>
  );
};

export default ProductDetailView;