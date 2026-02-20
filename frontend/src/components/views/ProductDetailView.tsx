import React from 'react';
import SourcingBadge from '../ProductDetail/SourcingBadge';
import JITBadge from '../ProductDetail/JITBadge';
import { useConductorCatalog, useJITIntelligence } from '../../hooks';

interface ProductDetailProps {
  productId: string;
}

const ProductDetailView: React.FC<ProductDetailProps> = ({ productId }) => {
  const { data: catalogData, isLoading: catalogIsLoading, error: catalogError } = useConductorCatalog(productId);
  const { jitState } = useJITIntelligence(productId);

  if (catalogIsLoading) {
    return <div>Loading...</div>;
  }

  if (catalogError) {
    return <div>Error: {catalogError.message}</div>;
  }

  if (!catalogData) {
    return <div>Product not found</div>;
  }

  const productName = jitState.snap?.name || catalogData.name;
  const brandName = jitState.snap?.brand || catalogData.brand;
  const price = jitState.snap?.price || catalogData.price;
  const priceEilat = jitState.snap?.price_eilat || catalogData.price_eilat;
  const imageUrl = jitState.snap?.thumbnail || catalogData.image_url;


  const renderBadge = (source: 'Official Scout' | 'Commercial Scout' | 'JIT Intelligence' | 'Inferred Scout', label?: string) => {
    let badgeText = label || source;
    let badgeStyle = '';
    let ariaLabel = `Source: ${badgeText}`;

    switch (source) {
      case 'Official Scout':
        badgeStyle = 'bg-blue-100 text-blue-800 dark:bg-blue-700 dark:text-blue-300';
        break;
      case 'Commercial Scout':
        badgeStyle = 'bg-green-100 text-green-800 dark:bg-green-700 dark:text-green-300';
        break;
      case 'JIT Intelligence':
        badgeStyle = 'bg-yellow-100 text-yellow-800 dark:bg-yellow-700 dark:text-yellow-300';
        break;
      case 'Inferred Scout':
        badgeStyle = 'bg-purple-100 text-purple-800 dark:bg-purple-700 dark:text-purple-300';
        break;
    }
    return (
      <span aria-label={ariaLabel} className={`text-xs font-semibold mr-2 px-2.5 py-0.5 rounded ${badgeStyle}`}>
        {badgeText}
      </span>
    );
  };

  return (
    <div>
      <h2>Product Detail</h2>
      <div>
        <h3>Product Name</h3>
        <div>
          {productName}
          {(jitState.snap?.name && jitState.status === 'complete') ? renderBadge('JIT Intelligence') : renderBadge('Official Scout')}
        </div>
      </div>
      <div>
        <h3>Brand Name</h3>
        <div>
          {brandName}
          {(jitState.snap?.brand && jitState.status === 'complete') ? renderBadge('JIT Intelligence') : renderBadge('Official Scout')}
        </div>
      </div>
      <div>
        <h3>Price (IL)</h3>
        <div>
          {price !== null ? (
            <>
              {price}
              {(jitState.snap?.price !== undefined && jitState.status === 'complete') ? renderBadge('JIT Intelligence') : renderBadge('Commercial Scout')}
            </>
          ) : (
            'Call for Price'
          )}
        </div>
      </div>
      <div>
        <h3>Price (Eilat)</h3>
        <div>
          {priceEilat !== null ? (
            <>
              {priceEilat}
              {(jitState.snap?.price_eilat !== undefined && jitState.status === 'complete') ? renderBadge('JIT Intelligence') : renderBadge('Commercial Scout')}
            </>
          ) : (
            'Call for Price'
          )}
        </div>
      </div>
      <div>
        <h3>Image</h3>
        <div>
            {imageUrl ? (
                <img src={imageUrl} alt="Product" style={{ maxWidth: '200px' }} />
            ) : (
                <img src="/placeholder.jpg" alt="Product" style={{ maxWidth: '200px' }} />
            )}

            {jitState.snap?.thumbnail && jitState.status === 'complete' ? renderBadge('Inferred Scout') : renderBadge('Official Scout')}
        </div>
      </div>
      <div>
        <h3>Specifications</h3>
        {catalogData.specifications && Object.entries(catalogData.specifications).map(([key, value]) => (
          <div key={key}>
            {key}: {value} {renderBadge('Official Scout')}
          </div>
        ))}
      </div>
      <SourcingBadge productId={productId} />
      <JITBadge productId={productId} />
    </div>
  );
};

export default ProductDetailView;