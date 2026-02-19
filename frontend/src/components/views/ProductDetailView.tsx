import React, { useState, useEffect } from 'react';
import { Product } from '../../types';
import { Copy, AlertTriangle } from 'lucide-react';
import { useNavigationStore } from '../../state/navigationStore';
import { useProductRelationships } from '../../hooks/useProductRelationships';
import ProductTile from '../ProductTile';

interface Props {
  product: Product | undefined;
}

const RelationshipSection: React.FC<{
  title: string;
  relationshipType: 'accessories' | 'compatibles' | 'bundles' | 'alternatives';
  products: Product[] | undefined;
  source: 'Verified' | 'Inferred' | undefined;
  loading: boolean;
  error: string | null;
}> = ({ title, relationshipType, products, source, loading, error }) => {
  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Error!</strong>
        <span className="block sm:inline">{error}</span>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="mb-4">
        <h3 className="font-semibold mb-2">{title}</h3>
        <div className="flex space-x-4 overflow-x-auto">
          {Array(3).fill(null).map((_, index) => (
            <div key={index} className="w-48 h-32 bg-gray-200 animate-pulse rounded-md" />
          ))}
        </div>
      </div>
    );
  }

  if (!products || products.length === 0) {
    return (
      <div className="mb-4">
        <h3 className="font-semibold mb-2">{title}</h3>
        <div className="bg-amber-100 border border-amber-400 text-amber-700 px-4 py-3 rounded relative flex items-center">
          <AlertTriangle className="h-5 w-5 mr-2" />
          No {title.toLowerCase()} found for this product.
        </div>
      </div>
    );
  }

  return (
    <div className="mb-4">
      <h3 className="font-semibold mb-2">{title}</h3>
      <div className="flex space-x-4 overflow-x-auto">
        {products.map((product) => (
          <ProductTile key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
};

const EcosystemTab: React.FC<Props> = ({ product }) => {
  const {
    accessories,
    compatibles,
    bundles,
    alternatives,
    accessoriesLoading,
    compatiblesLoading,
    bundlesLoading,
    alternativesLoading,
    error,
  } = useProductRelationships(product?.id);
  const navigationStore = useNavigationStore();

  if (!product) {
    return null;
  }

  return (
    <div>
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline">{error}</span>
        </div>
      )}

      <RelationshipSection
        title="Accessories"
        relationshipType="accessories"
        products={accessories?.products}
        source={accessories?.source}
        loading={accessoriesLoading}
        error={error}
      />
      <RelationshipSection
        title="Compatibles"
        relationshipType="compatibles"
        products={compatibles?.products}
        source={compatibles?.source}
        loading={compatiblesLoading}
        error={error}
      />
      <RelationshipSection
        title="Bundles"
        relationshipType="bundles"
        products={bundles?.products}
        source={bundles?.source}
        loading={bundlesLoading}
        error={error}
      />
      <RelationshipSection
        title="Alternatives"
        relationshipType="alternatives"
        products={alternatives?.products}
        source={alternatives?.source}
        loading={alternativesLoading}
        error={error}
      />
    </div>
  );
};

const ProductDetailView: React.FC<Props> = ({ product }) => {
  const [copyStatus, setCopyStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [activeTab, setActiveTab] = useState<'details' | 'ecosystem' | 'specifications' | 'history'>('details');


  useEffect(() => {
    if (copyStatus !== 'idle') {
      const timeout = setTimeout(() => {
        setCopyStatus('idle');
      }, 2000);
      return () => clearTimeout(timeout);
    }
  }, [copyStatus]);

  const handleCopySku = async () => {
    if (!product?.id) return;
    try {
      await navigator.clipboard.writeText(product.id);
      setCopyStatus('success');
    } catch (err) {
      console.error('Failed to copy SKU: ', err);
      setCopyStatus('error');
    }
  };

  const shouldShowCopyButton = product?.price === null || product?.price === 0;

  return (
    <div>
      {/* Product Detail Content */}
      {product && (
        <>
          <div className="flex items-center space-x-2 mb-2">
            <span className="font-semibold">SKU:</span>
            <span>{product.id}</span>
            {shouldShowCopyButton && (
              <button
                onClick={handleCopySku}
                className="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <Copy className="mr-1 h-4 w-4" />
                {copyStatus === 'success'
                  ? 'Copied!'
                  : copyStatus === 'error'
                  ? 'Copy Failed'
                  : 'Copy SKU'}
              </button>
            )}
          </div>
          {/* Price Display */}
          <div className="mb-4">
            {product.price === null || product.price === 0 ? (
              <span>Price on request</span>
            ) : (
              <span>{product.pricing?.price_il} ILS</span>
            )}
          </div>
          {copyStatus === 'error' && (
            <div className="text-red-500 text-sm">
              Copy failed. Please copy the SKU manually.
            </div>
          )}

          <div className="mb-4">
            <button
                className={`px-4 py-2 rounded-md ${activeTab === 'details' ? 'bg-gray-200' : 'bg-gray-100'} mr-2`}
                onClick={() => setActiveTab('details')}
            >
              Details
            </button>
            <button
                className={`px-4 py-2 rounded-md ${activeTab === 'ecosystem' ? 'bg-gray-200' : 'bg-gray-100'} mr-2`}
                onClick={() => setActiveTab('ecosystem')}
            >
              Ecosystem
            </button>
          </div>

          {activeTab === 'details' && (
            <div>
               {/* Details Content (Placeholder) */}
              <p>Product Details Content Here</p>
            </div>
          )}
          {activeTab === 'ecosystem' && (
            <EcosystemTab product={product} />
          )}

        </>
      )}
    </div>
  );
};

export default ProductDetailView;