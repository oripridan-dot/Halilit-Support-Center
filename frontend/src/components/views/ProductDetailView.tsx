import React, { useMemo, useState, useEffect } from 'react';
import { useConductorCatalog, useJITIntelligence, useProductRelationships, useNavigationStore } from '../../hooks';
import { Product } from '../../types';
import ProductImage from '../ProductImage';
import { ArrowLeft, ExternalLink, ClipboardCopy, FileText } from 'lucide-react';
import { formatSpecsAsText } from '../../utils';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import SourcingBadge from '../ProductDetail/SourcingBadge';

interface RelatedProduct {
  id: string;
  name: string;
  price?: number;
  image_url?: string;
}

interface SourceBadgeProps {
  source: 'Official Scout' | 'Commercial Scout' | 'JIT' | 'Official Scout + JIT';
  'aria-label': string;
}

const SourceBadge: React.FC<SourceBadgeProps> = ({ source, 'aria-label': ariaLabel }) => {
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
    case 'JIT':
      badgeStyle = 'bg-purple-100 text-purple-800 dark:bg-purple-700 dark:text-purple-300';
      badgeText = 'JIT';
      break;
    case 'Official Scout + JIT':
      badgeStyle = 'bg-yellow-100 text-yellow-800 dark:bg-yellow-700 dark:text-yellow-300';
      badgeText = 'Official Scout + JIT';
      break;
  }

  return (
    <span
      aria-label={ariaLabel}
      className={`text-xs font-semibold mr-2 px-2.5 py-0.5 rounded ${badgeStyle}`}
    >
      {badgeText}
    </span>
  );
};

const ProductDetailView: React.FC<{ productId: string }> = ({ productId }) => {
  const { data: product, isLoading: isCatalogLoading, isError: isCatalogError } = useConductorCatalog(productId);
  const { data: jitState, status: jitStatus } = useJITIntelligence(productId);
  const { accessories, compatible, alternatives, isLoading: relationsLoading } = useProductRelationships(productId);
  const { goToInventory, goToProduct, goBack } = useNavigationStore();
  const [isCopying, setIsCopying] = useState(false);

  const displayBrand = useMemo(() => jitState?.snap?.brand || product?.brand || '', [jitState?.snap?.brand, product?.brand]);
  const brandSource = useMemo(() => {
    return jitState?.snap?.brand ? (product?.brand ? 'Official Scout + JIT' : 'JIT') : 'Official Scout';
  }, [jitState?.snap?.brand, product?.brand]);

  const productName = useMemo(() => {
    return product?.name || jitState?.snap?.name || '';
  }, [product?.name, jitState?.snap?.name]);
  const nameSource = useMemo(() => {
      return jitState?.snap?.name ? (product?.name ? 'Official Scout + JIT' : 'JIT') : 'Official Scout';
  }, [jitState?.snap?.name, product?.name]);

  const brandName = useMemo(() => {
    return product?.brand || jitState?.snap?.brand || '';
  }, [product?.brand, jitState?.snap?.brand]);


  const ilPrice = useMemo(() => {
    return product?.price !== null && product?.price !== undefined ? product.price : jitState?.snap?.price !== null && jitState?.snap?.price !== undefined ? jitState.snap.price : null;
  }, [product?.price, jitState?.snap?.price]);

  const eilatPrice = useMemo(() => {
    return product?.price_eilat !== null && product?.price_eilat !== undefined ? product.price_eilat : jitState?.snap?.price_eilat !== null && jitState?.snap?.price_eilat !== undefined ? jitState.snap.price_eilat : null;
  }, [product?.price_eilat, jitState?.snap?.price_eilat]);

  const priceSource = useMemo(() => {
    return jitState?.snap?.price || jitState?.snap?.price_eilat ? 'JIT' : 'Commercial Scout';
  }, [jitState?.snap?.price, jitState?.snap?.price_eilat]);


  const imageUrl = useMemo(() => {
    return product?.image_url || jitState?.snap?.thumbnail || '/placeholder.png';
  }, [product?.image_url, jitState?.snap?.thumbnail]);

  const specsRecord = useMemo(() => {
    if (jitState?.officialSpecs?.specs && Object.keys(jitState.officialSpecs.specs).length > 0) {
      return jitState.officialSpecs.specs;
    }
    return product?.specs || {};
  }, [product?.specs, jitState?.officialSpecs?.specs]);

  const handleCopySpecs = async () => {
    setIsCopying(true);
    try {
      const text = formatSpecsAsText(specsRecord);
      await navigator.clipboard.writeText(text);
      toast.success('✓ Copied', {
        position: "bottom-right",
        autoClose: 1500,
        hideProgressBar: true,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
    } catch (err) {
      toast.error('Failed to copy specs', {
        position: "bottom-right",
        autoClose: 1500,
        hideProgressBar: true,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
    } finally {
      setIsCopying(false);
    }
  };

  if (isCatalogLoading || relationsLoading) {
    return <div>Loading...</div>;
  }

  if (isCatalogError) {
    return <div>Error loading product details</div>;
  }

  return (
    <div className="container mx-auto py-4">
      <button onClick={goBack} className="flex items-center text-blue-500 hover:underline mb-4">
        <ArrowLeft size={16} className="mr-2" /> Back
      </button>

      <div className="flex flex-col md:flex-row gap-4">
        <div className="md:w-1/3">
          <ProductImage imageUrl={imageUrl} altText={productName} />
        </div>

        <div className="md:w-2/3">
          <h1 className="text-2xl font-bold flex items-center">
            {productName}{nameSource && <SourceBadge source={nameSource} aria-label={`Source: ${nameSource}`} />}
          </h1>
          <div className="flex items-center">
            <h2 className="text-lg font-semibold mr-2">{displayBrand}</h2>
            {brandSource && <SourceBadge source={brandSource} aria-label={`Source: ${brandSource}`} />}
          </div>

          <div className="mt-4">
            <h3 className="font-medium">Prices</h3>
            {ilPrice !== null && ilPrice !== undefined && (
              <div className="flex items-center">
                <span>IL: ${ilPrice}</span>
                {ilPrice !== null && ilPrice !== undefined && priceSource && <SourceBadge source={priceSource} aria-label={`Source: ${priceSource}`} />}
              </div>
            )}
            {eilatPrice !== null && eilatPrice !== undefined && (
              <div className="flex items-center">
                <span>Eilat: ${eilatPrice}</span>
                {eilatPrice !== null && eilatPrice !== undefined && priceSource && <SourceBadge source={priceSource} aria-label={`Source: ${priceSource}`} />}
              </div>
            )}
            {(ilPrice === null || ilPrice === undefined) && (eilatPrice === null || eilatPrice === undefined) && (
              <div>Call for Price</div>
            )}

            <SourcingBadge productId={productId} />
          </div>

          <div className="mt-4">
            <h3 className="font-medium">Specifications</h3>
            {Object.entries(specsRecord).map(([key, value]) => (
              <div key={key} className="flex items-center">
                <span className="mr-2">{key}: {value}</span>
                <SourceBadge source="Official Scout" aria-label="Source: Official Scout" />
              </div>
            ))}
          </div>

          <div className="mt-4">
            <button
              onClick={handleCopySpecs}
              disabled={isCopying}
              className={`flex items-center px-4 py-2 rounded font-medium ${isCopying ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-700'} text-white`}
            >
              {isCopying ? (
                <>
                  <FileText size={16} className="mr-2 animate-spin" />
                  Copying...
                </>
              ) : (
                <>
                  <ClipboardCopy size={16} className="mr-2" />
                  Copy Specs
                </>
              )}
            </button>
          </div>

          {/* Related Products Section */}
          <div className="mt-6">
            <h3 className="font-medium mb-2">Related Products</h3>
            {accessories && accessories.length > 0 && (
              <div>
                <h4 className="font-semibold mb-1">Accessories</h4>
                <div className="flex flex-wrap gap-2">
                  {accessories.map((accessory) => (
                    <div key={accessory.id} className="border p-2 rounded w-40">
                      <p className="font-medium">{accessory.name}</p>
                      {accessory.price && <p>${accessory.price}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}
            {compatible && compatible.length > 0 && (
              <div className="mt-4">
                <h4 className="font-semibold mb-1">Compatible Products</h4>
                <div className="flex flex-wrap gap-2">
                  {compatible.map((compatibleProduct) => (
                    <div key={compatibleProduct.id} className="border p-2 rounded w-40">
                      <p className="font-medium">{compatibleProduct.name}</p>
                      {compatibleProduct.price && <p>${compatibleProduct.price}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}
            {alternatives && alternatives.length > 0 && (
              <div className="mt-4">
                <h4 className="font-semibold mb-1">Alternatives</h4>
                <div className="flex flex-wrap gap-2">
                  {alternatives.map((alternative) => (
                    <div key={alternative.id} className="border p-2 rounded w-40">
                      <p className="font-medium">{alternative.name}</p>
                      {alternative.price && <p>${alternative.price}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailView;