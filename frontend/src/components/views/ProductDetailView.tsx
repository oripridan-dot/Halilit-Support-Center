import React, { useMemo } from 'react';
import { useConductorCatalog, useJITIntelligence } from '../../hooks';
import { Product } from '../../types';

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
    if (JITStatus === 'success' && JITState?.snap?.thumbnail) {
        return JITState.snap.thumbnail;
    }
    return catalogProduct?.image_url || '';
  }, [catalogProduct?.image_url, JITState?.snap?.thumbnail, JITStatus]);

  const getBadgeSource = (dataType: 'name' | 'brand' | 'price' | 'image'): 'Official Scout' | 'Commercial Scout' | 'JIT Intelligence' | 'Inferred Scout' | null => {
    if (JITStatus === 'success') {
      switch (dataType) {
        case 'name':
          return JITState?.snap?.name ? 'JIT Intelligence' : 'Official Scout';
        case 'brand':
          return JITState?.snap?.brand ? 'JIT Intelligence' : 'Official Scout';
        case 'price':
          return JITState?.snap?.price || JITState?.snap?.price_eilat ? 'JIT Intelligence' : 'Commercial Scout';
        case 'image':
            return JITState?.snap?.thumbnail ? 'Inferred Scout' : 'Official Scout';
        default:
          return null;
      }
    }
    switch (dataType) {
        case 'name':
        case 'brand':
          return 'Official Scout';
        case 'price':
          return 'Commercial Scout';
        case 'image':
            return 'Official Scout';
        default:
          return null;
      }
  };

  if (isCatalogLoading) {
    return <div>Loading product details...</div>;
  }

  if (isCatalogError) {
    return <div>Error loading product details.</div>;
  }

  if (!catalogProduct) {
    return <div>Product not found.</div>;
  }

  return (
    <div>
      {/* Product Name */}
      {productName && (
        <SourcingBadge
          source={getBadgeSource('name') || 'Official Scout'}
          aria-label={`Source: ${getBadgeSource('name') || 'Official Scout'}`}
        >
          <h1>{productName}</h1>
        </SourcingBadge>
      )}

      {/* Brand Name */}
      {brandName && (
        <SourcingBadge
          source={getBadgeSource('brand') || 'Official Scout'}
          aria-label={`Source: ${getBadgeSource('brand') || 'Official Scout'}`}
        >
          <p>Brand: {brandName}</p>
        </SourcingBadge>
      )}

      {/* Price */}
      {priceIL !== null && (
        <SourcingBadge
          source={getBadgeSource('price') || 'Commercial Scout'}
          aria-label={`Source: ${getBadgeSource('price') || 'Commercial Scout'}`}
        >
          <p>Price (IL): {priceIL}</p>
        </SourcingBadge>
      )}

      {priceEilat !== null && (
          <SourcingBadge
              source={getBadgeSource('price') || 'Commercial Scout'}
              aria-label={`Source: ${getBadgeSource('price') || 'Commercial Scout'}`}
          >
              <p>Price (Eilat): {priceEilat}</p>
          </SourcingBadge>
      )}

      {/* Image */}
      {imageUrl && (
        <SourcingBadge
            source={getBadgeSource('image') || 'Official Scout'}
            aria-label={`Source: ${getBadgeSource('image') || 'Official Scout'}`}
        >
          <img src={imageUrl} alt={productName} width={200} />
        </SourcingBadge>
      )}

       {/* Specifications -  This part needs to be reviewed and potentially refactored. The spec refers to ALL specs,
            but there's no spec on what constitutes a spec.
       */}
        {catalogProduct.specifications && Object.entries(catalogProduct.specifications).map(([key, value]) => (
            <SourcingBadge
                key={key}
                source={'Official Scout'}
                aria-label="Source: Official Scout"
            >
                <p>{key}: {value}</p>
            </SourcingBadge>
        ))}
    </div>
  );
};

export default ProductDetailView;