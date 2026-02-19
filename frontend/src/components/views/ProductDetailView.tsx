import React, { useMemo } from 'react';
import { useConductorCatalog, useJITIntelligence } from '../../hooks';
import { Product } from '../../types';
import SourcingBadge from '../ProductDetail/SourcingBadge';
import JITBadge from '../ProductDetail/JITBadge';
import ProductImage from '../ProductImage';

interface SourcingBadgeProps {
  source: 'Official Scout' | 'Commercial Scout' | 'JIT Intelligence' | 'Inferred Scout';
  children: React.ReactNode;
  'aria-label': string;
}

const SourcingBadge: React.FC<SourcingBadgeProps> = ({ source, children, 'aria-label': ariaLabel }) => {
  let badgeStyle = '';
  let badgeText = '';

  switch (source) {
    case 'Official Scout':
      badgeStyle = 'bg-blue-100 text-blue-800 dark:bg-blue-700 dark:text-blue-300';
      badgeText = 'Official Scout';
      break;
    case 'Commercial Scout':
      badgeStyle = 'bg-green-100 text-green-800 dark:bg-green-700 dark:text-green-300';
      badgeText = 'Commercial Scout';
      break;
    case 'JIT Intelligence':
      badgeStyle = 'bg-yellow-100 text-yellow-800 dark:bg-yellow-700 dark:text-yellow-300';
      badgeText = 'JIT';
      break;
    case 'Inferred Scout':
      badgeStyle = 'bg-purple-100 text-purple-800 dark:bg-purple-700 dark:text-purple-300';
      badgeText = 'Inferred Scout';
      break;
  }

  return (
    <>
      {children}
      <span
        aria-label={ariaLabel}
        className={`text-xs font-semibold mr-2 px-2.5 py-0.5 rounded ${badgeStyle}`}
      >
        {badgeText}
      </span>
    </>
  );
};

const ProductDetailView: React.FC<{ productId: string }> = ({ productId }) => {
  const { data: catalogProduct, isLoading: isCatalogLoading, isError: isCatalogError } = useConductorCatalog(productId);
  const { data: JITState, status: JITStatus } = useJITIntelligence(productId);

  const productName = useMemo(() => {
    if (JITStatus === 'success' && JITState?.snap?.name) {
      return JITState.snap.name;
    }
    return catalogProduct?.name || '';
  }, [catalogProduct?.name, JITState?.snap?.name, JITStatus]);

  const brandName = useMemo(() => {
    if (JITStatus === 'success' && JITState?.snap?.brand) {
      return JITState.snap.brand;
    }
    return catalogProduct?.brand || '';
  }, [catalogProduct?.brand, JITState?.snap?.brand, JITStatus]);

  const priceIL = useMemo(() => {
    if (JITStatus === 'success' && JITState?.snap?.price) {
      return JITState.snap.price;
    }
    return catalogProduct?.price || null;
  }, [catalogProduct?.price, JITState?.snap?.price, JITStatus]);

  const priceEilat = useMemo(() => {
    if (JITStatus === 'success' && JITState?.snap?.price_eilat) {
        return JITState.snap.price_eilat;
    }
    return catalogProduct?.price_eilat || null;
  }, [catalogProduct?.price_eilat, JITState?.snap?.price_eilat, JITStatus]);


  const imageUrl = useMemo(() => {
    if (JITStatus === 'success' && JITState?.snap?.thumbnail && JITState.status === "complete") {
        return JITState.snap.thumbnail;
    }
    return catalogProduct?.image_url || '';
  }, [catalogProduct?.image_url, JITState?.snap?.thumbnail, JITStatus]);

  const getBadgeSource = (dataType: 'name' | 'brand' | 'price' | 'image'): 'Official Scout' | 'Commercial Scout' | 'JIT Intelligence' | undefined => {
    if (dataType === 'name' || dataType === 'brand' || dataType === 'image') {
      return 'Official Scout';
    }
    if (dataType === 'price') {
      return 'Commercial Scout';
    }
    return undefined;
  };

  const getNameBadgeSource = (): 'Official Scout' | 'JIT Intelligence' | 'Official Scout + JIT' | undefined => {
    if (JITStatus === 'success' && JITState?.snap?.name) {
      return 'JIT Intelligence';
    }
    return 'Official Scout';
  };

  const getBrandBadgeSource = (): 'Official Scout' | 'JIT Intelligence' | 'Official Scout + JIT' | undefined => {
    if (JITStatus === 'success' && JITState?.snap?.brand) {
      return 'JIT Intelligence';
    }
    return 'Official Scout';
  };

  const getPriceBadgeSource = (): 'Commercial Scout' | 'JIT Intelligence' | 'Commercial Scout + JIT' | undefined => {
    if (JITStatus === 'success' && (JITState?.snap?.price || JITState?.snap?.price_eilat)) {
      return 'JIT Intelligence';
    }
    return 'Commercial Scout';
  };



  if (isCatalogLoading) {
    return <div>Loading...</div>;
  }

  if (isCatalogError) {
    return <div>Error loading product data</div>;
  }

  return (
    <div>
      {/* Product Name */}
      {productName && (
        <div className="mb-2">
          <span className="font-bold">Name: {productName}</span>
          <SourcingBadge
            source={getNameBadgeSource() || 'Official Scout'}
            aria-label={`Source: ${getNameBadgeSource()}`}
          />
          <JITBadge productId={productId} />
        </div>
      )}

      {/* Brand Name */}
      {brandName && (
        <div className="mb-2">
          <span className="font-bold">Brand: {brandName}</span>
          <SourcingBadge
            source={getBrandBadgeSource() || 'Official Scout'}
            aria-label={`Source: ${getBrandBadgeSource()}`}
          />
        </div>
      )}

      {/* Price */}
      {(priceIL !== null || priceEilat !== null) ? (
        <div className="mb-2">
          <span className="font-bold">Price: {priceIL !== null ? `${priceIL} IL` : ''} {priceEilat !== null ? `(${priceEilat} Eilat)` : ''}</span>
          <SourcingBadge
              source={getPriceBadgeSource() || 'Commercial Scout'}
              aria-label={`Source: ${getPriceBadgeSource()}`}
          />
        </div>
      ) : (
          <div className="mb-2">
            <span className="font-bold">Price: Call for Price</span>
          </div>
      )}

      {/* Image */}
      <div className="mb-2">
        {imageUrl && <ProductImage imageUrl={imageUrl} altText={productName || 'Product'} />}
      </div>

      <SourcingBadge productId={productId} />
    </div>
  );
};

export default ProductDetailView;