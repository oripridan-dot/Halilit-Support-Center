import React, { useMemo } from 'react';
import { useConductorCatalog, useJITIntelligence } from '../../hooks';
import SourcingBadge from '../ProductDetail/SourcingBadge';
import JITBadge from '../ProductDetail/JITBadge';
import ProductImage from '../ProductImage';

interface ProductDetailProps {
  productId: string;
}

const ProductDetailView: React.FC<ProductDetailProps> = ({ productId }) => {
  const { data: catalogData, isLoading: isCatalogLoading, error: catalogError } = useConductorCatalog(productId);
  const { jitState } = useJITIntelligence(productId);

  const productName = useMemo(() => {
    if (jitState?.snap?.name) {
      return jitState.snap.name;
    }
    return catalogData?.name;
  }, [catalogData?.name, jitState?.snap?.name]);

  const brandName = useMemo(() => {
    if (jitState?.snap?.brand) {
      return jitState.snap.brand;
    }
    return catalogData?.brand;
  }, [catalogData?.brand, jitState?.snap?.brand]);

  const price = useMemo(() => {
    if (jitState?.snap?.price) {
      return jitState.snap.price;
    }
    return catalogData?.price;
  }, [catalogData?.price, jitState?.snap?.price]);

  const priceEilat = useMemo(() => {
    if (jitState?.snap?.price_eilat) {
        return jitState.snap.price_eilat
    }
    return catalogData?.price_eilat;
  }, [catalogData?.price_eilat, jitState?.snap?.price_eilat]);

  const imageUrl = useMemo(() => {
    if (jitState?.snap?.thumbnail && jitState.status === 'complete') {
      return jitState.snap.thumbnail;
    }
    return catalogData?.image_url;
  }, [catalogData?.image_url, jitState?.snap?.thumbnail, jitState.status]);

  const renderBadge = (source: 'Official Scout' | 'Commercial Scout' | 'JIT Intelligence' | 'Inferred Scout', label: string) => {
    let badgeStyle = '';
    let badgeText = '';
    let ariaLabel = `Source: ${label}`;

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
        badgeStyle = 'bg-purple-100 text-purple-800 dark:bg-purple-700 dark:text-purple-300';
        badgeText = 'JIT Intelligence';
        break;
      case 'Inferred Scout':
        badgeStyle = 'bg-purple-100 text-purple-800 dark:bg-purple-700 dark:text-purple-300';
        badgeText = 'Inferred Scout';
        break;
    }

    return (
      <span aria-label={ariaLabel} className={`text-xs font-semibold mr-2 px-2.5 py-0.5 rounded ${badgeStyle}`}>
        {badgeText}
      </span>
    );
  };

  const renderProductName = () => {
    if (!productName) return null;

    let badgeSource: 'Official Scout' | 'JIT Intelligence' = 'Official Scout';
    if (jitState?.snap?.name) {
      badgeSource = 'JIT Intelligence';
    }

    return (
      <div className="flex items-center">
        {productName}
        {badgeSource && renderBadge(badgeSource, badgeSource)}
      </div>
    );
  };

  const renderBrandName = () => {
    if (!brandName) return null;

    let badgeSource: 'Official Scout' | 'JIT Intelligence' = 'Official Scout';
    if (jitState?.snap?.brand) {
      badgeSource = 'JIT Intelligence';
    }

    return (
      <div className="flex items-center">
        {brandName}
        {badgeSource && renderBadge(badgeSource, badgeSource)}
      </div>
    );
  };

  const renderPrice = () => {
    if (price === null || price === undefined) {
      return (
        <div>
          Call for Price
          <JITBadge productId={productId} />
        </div>
      );
    }
    let badgeSource: 'Commercial Scout' | 'JIT Intelligence' = 'Commercial Scout';
    if (jitState?.snap?.price) {
      badgeSource = 'JIT Intelligence';
    }

    return (
      <div className="flex items-center">
        {price}
        {badgeSource && renderBadge(badgeSource, badgeSource)}
      </div>
    );
  };

  const renderPriceEilat = () => {
      if (priceEilat === null || priceEilat === undefined) {
          return null;
      }

      let badgeSource: 'Commercial Scout' | 'JIT Intelligence' = 'Commercial Scout';
      if(jitState?.snap?.price_eilat) {
          badgeSource = 'JIT Intelligence';
      }

      return(
          <div className="flex items-center">
              {priceEilat}
              {badgeSource && renderBadge(badgeSource, badgeSource)}
          </div>
      )
  }

  const renderSpecifications = () => {
    if (!catalogData?.specifications) return null;

    return (
      <div>
        {Object.entries(catalogData.specifications).map(([key, value]) => (
          <div key={key} className="flex items-center">
            {key}: {value}
            {renderBadge('Official Scout', 'Official Scout')}
          </div>
        ))}
      </div>
    );
  };

  if (isCatalogLoading) {
    return <div>Loading...</div>;
  }

  if (catalogError) {
    return <div>Error: {catalogError.message}</div>;
  }

  return (
    <div>
      <ProductImage imageUrl={imageUrl} altText={productName || 'Product Image'} />
      {renderProductName()}
      {renderBrandName()}
      {renderPrice()}
      {renderPriceEilat()}
      {renderSpecifications()}
      <SourcingBadge productId={productId} />
      <JITBadge productId={productId} />
    </div>
  );
};

export default ProductDetailView;