import React, { useState, useEffect, useRef } from 'react';
import { Product } from '../../types';
import { Copy, AlertTriangle } from 'lucide-react';
import { useNavigationStore } from '../../state/navigationStore';
import { useProductRelationships, RelatedProduct } from '../../hooks/useProductRelationships';
import ProductTile from '../ProductTile';
import { useJITIntelligence, JITPhase, JITIntelligenceState } from '../../hooks/useJITIntelligence';
import { useConductorCatalog } from '../../hooks/useConductorCatalog';
import { formatSpecsAsText } from '../../utils/formatSpecsAsText';
import { Placeholder } from 'lucide-react';

interface Props {
  product: Product | undefined;
}

const RelationshipSection: React.FC<{
  title: string;
  relationshipType: 'accessories' | 'compatibles' | 'alternatives';
  products: RelatedProduct[] | undefined;
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
          <ProductTile key={product.id} product={product as Product} />
        ))}
      </div>
    </div>
  );
};

const SourcingBadge: React.FC<{ source: string }> = ({ source }) => {
  const badgeStyles = {
    'Official Scout': 'bg-blue-100 text-blue-800 dark:bg-blue-700 dark:text-blue-300',
    'Commercial Scout': 'bg-green-100 text-green-800 dark:bg-green-700 dark:text-green-300',
    'JIT Intelligence': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-700 dark:text-yellow-300',
    'Inferred Scout': 'bg-purple-100 text-purple-800 dark:bg-purple-700 dark:text-purple-300',
  };

  const style = badgeStyles[source as keyof typeof badgeStyles];

  if (!style) {
    return null;
  }

  return (
    <span className={`text-xs font-semibold mr-2 px-2.5 py-0.5 rounded ${style}`} aria-label={`Source: ${source}`}>
      {source}
    </span>
  );
};

const ProductDetailView: React.FC = () => {
  const { activeProductId, goToInventory, goToProduct, goBack } = useNavigationStore();
  const { product } = useConductorCatalog(activeProductId);
  const { jitState } = useJITIntelligence(activeProductId);
  const { accessories, alternatives, compatible, isLoading: relationsLoading, relationshipMeta } = useProductRelationships(activeProductId);
  const [copyStatus, setCopyStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [activeTab, setActiveTab] = useState('ecosystem');
  const placeholderImage = '/placeholder.png';

  const displayBrand = product?.brand || jitState?.snap?.brand || '';

  const title = product?.name || jitState?.snap?.name || '';
  const brand = product?.brand || jitState?.snap?.brand || '';
  const ilPrice = product?.price || jitState?.snap?.price;
  const eilatPrice = product?.price_eilat || jitState?.snap?.price_eilat;
  const imageUrl = product?.image_url || jitState?.snap?.thumbnail || placeholderImage;
  const officialSpecs = jitState?.officialSpecs?.specs;
  const catalogSpecs = product?.specs;
  const specsRecord = officialSpecs && Object.keys(officialSpecs).length > 0 ? officialSpecs : catalogSpecs || {};
  const officialUrl = product?.official_url;

  const stockStatus = product?.stock;

  const handleCopySpecs = async () => {
    if (!specsRecord || Object.keys(specsRecord).length === 0) {
      return;
    }
    try {
      const text = formatSpecsAsText(specsRecord);
      await navigator.clipboard.writeText(text);
      setCopyStatus('success');
      setTimeout(() => setCopyStatus('idle'), 1500);
    } catch (err) {
      setCopyStatus('error');
      setTimeout(() => setCopyStatus('idle'), 1500);
    }
  };

  const handleGenerateQuote = () => {
    window.print();
  };

  useEffect(() => {
    if (activeProductId && !product && jitState?.status === 'error') {
      setActiveTab('404');
    } else {
      setActiveTab('ecosystem');
    }
  }, [activeProductId, product, jitState?.status]);

  if (!activeProductId || (product === null && (jitState.status === 'error' || activeTab === '404'))) {
    return (
      <div className="p-8 max-w-md">
        <p className="text-2xl font-bold text-zinc-400 mb-2">Product Not Found</p>
        <p className="text-sm text-zinc-500 mb-6">
          No product with ID "{activeProductId}" exists in the catalog.
        </p>
        <button onClick={goBack} className="bg-zinc-700 hover:bg-zinc-600 text-white font-semibold py-2 px-4 rounded">
          ← Back to Search
        </button>
      </div>
    );
  }

  const renderSkeleton = () => (
    <div className="animate-pulse">
      <div className="bg-white p-4 rounded-md mb-4">
        <div className="aspect-video bg-gray-200 rounded-md" />
      </div>
      <div className="flex items-center justify-between mb-2">
        <div className="h-6 bg-gray-200 rounded-md w-2/3" />
        <div className="h-6 bg-gray-200 rounded-md w-1/4" />
      </div>
      <div className="flex items-center justify-between mb-4">
        <div className="h-4 bg-gray-200 rounded-md w-1/4" />
        <div className="h-4 bg-gray-200 rounded-md w-1/4" />
        <div className="h-4 bg-gray-200 rounded-md w-1/4" />
      </div>
      <div className="flex space-x-2 mb-4">
        <div className="h-10 bg-gray-200 rounded-md w-1/3" />
        <div className="h-10 bg-gray-200 rounded-md w-1/3" />
        <div className="h-10 bg-gray-200 rounded-md w-1/3" />
      </div>
      <div className="flex space-x-2 mb-2">
        <div className="h-8 bg-gray-200 rounded-md w-1/4" />
        <div className="h-8 bg-gray-200 rounded-md w-1/4" />
        <div className="h-8 bg-gray-200 rounded-md w-1/4" />
      </div>
    </div>
  );

  return (
    <>
      {jitState.status === 'loading' || (jitState.status === 'idle' && !product) ? (
        renderSkeleton()
      ) : (
        <>
          <div className="flex items-center mb-4">
            <button onClick={goBack} className="bg-zinc-700 hover:bg-zinc-600 text-white font-semibold py-2 px-4 rounded">
              ← Back
            </button>
          </div>

          <div className="bg-white p-4 rounded-md mb-4">
            <div className="aspect-video relative">
              <img
                src={imageUrl}
                alt={title}
                className="w-full h-full object-contain"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = placeholderImage;
                }}
              />
            </div>
            <div className="flex items-center justify-between mt-2">
              <div className="flex items-center space-x-2">
                <h1 className="text-2xl font-bold">{title}</h1>
                <button
                  className="bg-zinc-700 hover:bg-zinc-600 text-white font-semibold py-1 px-2 rounded text-sm"
                  onClick={() => goToInventory(displayBrand)}
                >
                  {brand}
                </button>
              </div>
              <span className="text-sm text-zinc-500">{activeProductId}</span>
            </div>
            <div className="flex items-center justify-between mt-2">
              <div className="text-sm">
                <span className="text-zinc-500">Category / Subcategory</span>
              </div>
            </div>
            <div className="flex items-center justify-between mt-2">
              <div className="flex items-center space-x-4">
                <div className="text-3xl font-bold">
                  {ilPrice !== undefined && ilPrice !== null ? (
                    `₪${ilPrice.toLocaleString()}`
                  ) : (
                    <span className="text-amber-500">Call for Price</span>
                  )}
                </div>
                <div>
                  {eilatPrice !== undefined && eilatPrice !== null ? (
                    `₪${eilatPrice.toLocaleString()}`
                  ) : (
                    '—'
                  )}
                </div>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${stockStatus === 0 ? 'bg-red-500' : stockStatus === null ? 'bg-gray-400' : 'bg-green-500'}`} />
                  <span>{stockStatus === 0 ? 'Out of Stock' : stockStatus === null ? 'Unknown' : 'In Stock'}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="sticky top-0 bg-zinc-800 p-2 z-10">
            <div className="flex space-x-2">
              <button
                className="bg-zinc-700 hover:bg-zinc-600 text-white font-semibold py-2 px-4 rounded"
                onClick={handleCopySpecs}
                disabled={!specsRecord || Object.keys(specsRecord).length === 0}
              >
                Copy Tech Specs {copyStatus === 'success' && '✓'}
              </button>
              <button
                className="bg-zinc-700 hover:bg-zinc-600 text-white font-semibold py-2 px-4 rounded"
                onClick={handleGenerateQuote}
              >
                Generate Quote PDF
              </button>
              <button
                className="bg-zinc-700 hover:bg-zinc-600 text-white font-semibold py-2 px-4 rounded"
                onClick={() => officialUrl && window.open(officialUrl, '_blank', 'noopener,noreferrer')}
                disabled={!officialUrl}
              >
                Open Official Page
              </button>
            </div>
          </div>
          {jitState.status === 'error' && (
            <div className="bg-amber-100 border border-amber-400 text-amber-700 px-4 py-3 rounded relative mb-4" role="alert">
              <strong className="font-bold">Error!</strong>
              <span className="block sm:inline">Intelligence fetch failed</span>
            </div>
          )}
          <div className="flex items-center space-x-4 mt-4">
            <button
              className={`py-2 px-4 ${activeTab === 'ecosystem' ? 'bg-zinc-700 text-white' : 'bg-zinc-800 text-zinc-300'} rounded`}
              onClick={() => setActiveTab('ecosystem')}
            >
              Ecosystem
            </button>
            <button
              className={`py-2 px-4 ${activeTab === 'specifications' ? 'bg-zinc-700 text-white' : 'bg-zinc-800 text-zinc-300'} rounded`}
              onClick={() => setActiveTab('specifications')}
            >
              Specifications
            </button>
            <button
              className={`py-2 px-4 ${activeTab === 'history' ? 'bg-zinc-700 text-white' : 'bg-zinc-800 text-zinc-300'} rounded`}
              onClick={() => setActiveTab('history')}
            >
              History
            </button>
          </div>
          <div className="mt-4">
            {activeTab === 'ecosystem' && (
              <>
                <RelationshipSection
                  title="Verified Accessories"
                  relationshipType="accessories"
                  products={accessories}
                  loading={relationsLoading}
                  error={''}
                  source={'Verified'}
                />
                <RelationshipSection
                  title="Alternatives"
                  relationshipType="alternatives"
                  products={alternatives}
                  loading={relationsLoading}
                  error={''}
                  source={undefined}
                />
                {compatible && compatible.length > 0 && (
                  <RelationshipSection
                    title="Compatible"
                    relationshipType="compatibles"
                    products={compatible}
                    loading={relationsLoading}
                    error={''}
                    source={undefined}
                  />
                )}
              </>
            )}
            {activeTab === 'specifications' && (
              specsRecord && Object.keys(specsRecord).length > 0 ? (
                <table className="w-full">
                  <tbody>
                    {Object.entries(specsRecord).map(([key, value], index) => (
                      <tr key={key} className={`border-b border-zinc-700 ${index % 2 === 0 ? 'bg-zinc-900/30' : ''}`}>
                        <td className="py-2 px-4 font-semibold">{key}</td>
                        <td className="py-2 px-4">{typeof value === 'object' ? JSON.stringify(value) : String(value)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className="text-zinc-500 text-sm">Official specifications not yet fetched. Run intelligence on this product.</p>
              )
            )}
            {activeTab === 'history' && (
              <p className="text-zinc-500 text-sm">
                Ticket history coming soon. No records for this product yet.
              </p>
            )}
          </div>
        </>
      )}
    </>
  );
};

export default ProductDetailView;