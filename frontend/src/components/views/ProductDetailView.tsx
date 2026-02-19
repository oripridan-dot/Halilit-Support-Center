import React, { useState, useEffect, useRef } from 'react';
import { Product } from '../../types';
import { Copy, AlertTriangle } from 'lucide-react';
import { useNavigationStore } from '../../state/navigationStore';
import { useProductRelationships } from '../../hooks/useProductRelationships';
import ProductTile from '../ProductTile';
import { useJITIntelligence, JITPhase, JITIntelligenceState } from '../../hooks/useJITIntelligence';
import { useConductorCatalog } from '../../hooks/useConductorCatalog';

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


const ProductDetailView: React.FC<Props> = ({ product }) => {
  const { activeProductId } = useNavigationStore();
  const { jitState } = useJITIntelligence(activeProductId || null);
  const { catalogProduct, isLoading: isCatalogLoading, error: catalogError } = useConductorCatalog(activeProductId || null);
  const [name, setName] = useState<string | undefined>(catalogProduct?.name);
  const [brand, setBrand] = useState<string | undefined>(catalogProduct?.brand);
  const [price, setPrice] = useState<number | null | undefined>(catalogProduct?.price);
  const [priceEilat, setPriceEilat] = useState<number | null | undefined>(catalogProduct?.price_eilat);
  const [imageUrl, setImageUrl] = useState<string | undefined>(catalogProduct?.image_url);
  const [nameBadge, setNameBadge] = useState<string | undefined>('Official Scout');
  const [brandBadge, setBrandBadge] = useState<string | undefined>('Official Scout');
  const [priceBadge, setPriceBadge] = useState<string | undefined>('Commercial Scout');
  const [imageBadge, setImageBadge] = useState<string | undefined>('Official Scout');
  const [isImageLoading, setIsImageLoading] = useState(false);
  const imageRef = useRef<HTMLImageElement | null>(null);

  useEffect(() => {
    if (catalogProduct) {
      setName(catalogProduct.name);
      setBrand(catalogProduct.brand);
      setPrice(catalogProduct.price);
      setPriceEilat(catalogProduct.price_eilat);
      setImageUrl(catalogProduct.image_url);
      setNameBadge('Official Scout');
      setBrandBadge('Official Scout');
      setPriceBadge('Commercial Scout');
      setImageBadge('Official Scout');
    }
  }, [catalogProduct]);


  useEffect(() => {
    if (jitState?.snap) {
      if (jitState.snap.name !== name) {
        setName(jitState.snap.name);
        setNameBadge('JIT Intelligence');
      }
      if (jitState.snap.brand !== brand) {
        setBrand(jitState.snap.brand);
        setBrandBadge('JIT Intelligence');
      }

      if (jitState.snap.price !== price) {
        setPrice(jitState.snap.price);
        setPriceBadge('JIT Intelligence');
      }
      if (jitState.snap.price_eilat !== priceEilat) {
        setPriceEilat(jitState.snap.price_eilat);
        setPriceBadge('JIT Intelligence');
      }

      if (jitState.snap.thumbnail && jitState.phase === 'complete') {
        setImageUrl(jitState.snap.thumbnail);
        setImageBadge('Inferred Scout');
      }
    }
  }, [jitState, name, brand, price, priceEilat]);

  useEffect(() => {
    if (jitState?.error) {
      setName(catalogProduct?.name);
      setBrand(catalogProduct?.brand);
      setPrice(catalogProduct?.price);
      setPriceEilat(catalogProduct?.price_eilat);
      setImageUrl(catalogProduct?.image_url);
      setNameBadge('Official Scout');
      setBrandBadge('Official Scout');
      setPriceBadge('Commercial Scout');
      setImageBadge('Official Scout');
    }
  }, [jitState?.error, catalogProduct]);


  const handleImageLoad = () => {
    setIsImageLoading(false);
  };

  const handleImageError = () => {
    setIsImageLoading(false);
    setImageUrl(catalogProduct?.image_url);
  };


  if (!product && isCatalogLoading) {
    return <div>Loading...</div>;
  }

  if (catalogError) {
    return <div>Error: {catalogError}</div>;
  }

  if (!product && !catalogProduct) {
    return <div>Product not found</div>;
  }

  return (
    <div className="p-4">
      {/* Header Card */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-4">
        <div className="flex items-center mb-2">
          {imageUrl ? (
            <img
              ref={imageRef}
              src={imageUrl}
              alt={name || 'Product Image'}
              className="w-20 h-20 object-cover rounded mr-4"
              onLoad={handleImageLoad}
              onError={handleImageError}
              style={{ display: isImageLoading ? 'none' : 'block' }}
            />
          ) : (
            <div className="w-20 h-20 bg-gray-200 rounded mr-4 flex items-center justify-center">
              <span className="text-gray-500">No Image</span>
            </div>
          )}
          <div className="flex-1">
            <h1 className="text-xl font-semibold flex items-center">
              {name}
              {nameBadge && <SourcingBadge source={nameBadge} />}
            </h1>
            <p className="text-gray-700 flex items-center">
              {brand}
              {brandBadge && <SourcingBadge source={brandBadge} />}
            </p>
            {/* SKU (from catalog) -  badge should not be on SKU */}
            <p className="text-gray-500">SKU: {product?.id}</p>
            <div className="flex items-center">
              <span className="font-bold mr-1">IL: </span>
              <span>{price !== null && price !== undefined ? price : 'Call for Price'}</span>
              {price !== null && price !== undefined && priceBadge && <SourcingBadge source={priceBadge} />}
            </div>
            <div className="flex items-center">
              <span className="font-bold mr-1">Eilat: </span>
              <span>{priceEilat !== null && priceEilat !== undefined ? priceEilat : 'Call for Price'}</span>
              {priceEilat !== null && priceEilat !== undefined && priceBadge && <SourcingBadge source={priceBadge} />}
            </div>
          </div>
        </div>
      </div>

    </div>
  );
};

export default ProductDetailView;