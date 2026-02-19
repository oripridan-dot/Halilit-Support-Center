import React, { useState, useEffect, useRef } from 'react';
import { Product, ProductImage } from '../../types';
import { useProductRelationships } from '../../hooks/useProductRelationships';
import { useNavigationStore } from '../../stores/navigationStore';
import { formatPrice } from '../../types';

interface AccessoryTileProps {
  accessory: Product;
}

const AccessoryTile: React.FC<AccessoryTileProps> = ({ accessory }) => {
  const navigateToProduct = useNavigationStore((state) => state.goToProduct);
  const [imageError, setImageError] = useState(false);

  const handleImageError = () => {
    setImageError(true);
  };

  const handleAccessoryClick = () => {
    navigateToProduct(accessory.id);
  };

  const imageUrl = accessory.images?.hero?.url || accessory.images?.thumbnail?.url;

  return (
    <div
      className="flex flex-col items-center w-40 rounded-lg shadow-md bg-bg-elevated overflow-hidden transition-shadow hover:shadow-lg focus:shadow-lg focus-within:ring-2 focus-within:ring-primary focus-within:outline-none"
      onClick={handleAccessoryClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === 'Space') {
          e.preventDefault();
          handleAccessoryClick();
        }
      }}
      tabIndex={0}
      role="button"
      aria-label={`View details for ${accessory.product_name}`}
    >
      {/* Image */}
      <div className="w-full h-32 relative">
        <img
          src={imageError ? '/placeholder.png' : imageUrl || '/placeholder.png'}
          alt={accessory.product_name}
          className="w-full h-full object-cover"
          onError={handleImageError}
        />
      </div>

      {/* Content */}
      <div className="p-2 w-full">
        <h3 className="text-sm font-medium text-text-primary truncate">{accessory.product_name}</h3>
        <p className="text-xs text-text-muted mt-1">
          {accessory.pricing?.price_il === null || accessory.pricing?.price_il === undefined
            ? 'Call for Price'
            : formatPrice(accessory)}
        </p>
      </div>
    </div>
  );
};


const AccessorySection = ({ productId }: { productId: string }) => {
  const { data, isLoading, error, refetch } = useProductRelationships(productId);
  const accessories = data?.accessories || [];
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  const handleWheel = (e: React.WheelEvent<HTMLDivElement>) => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollLeft += e.deltaY;
    }
  };

  const handleDrag = (e: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    if (!scrollContainerRef.current) return;
    scrollContainerRef.current.scrollLeft -= e.movementX;
  };


  return (
    <section className="mt-8">
      <h2 className="text-lg font-semibold text-text-primary mb-2">Recommended Accessories</h2>

      {isLoading && (
        <div className="flex space-x-4 overflow-x-auto pb-4" ref={scrollContainerRef} onWheel={handleWheel}>
          {[...Array(3)].map((_, i) => (
            <div key={i} className="w-40 h-56 rounded-lg shadow-md bg-bg-elevated animate-pulse"></div>
          ))}
        </div>
      )}

      {error && (
        <div className="bg-error text-text-primary rounded-md p-4 flex items-center justify-between">
          <span>Error loading accessories: {error.message}</span>
          <button
            onClick={refetch}
            className="px-3 py-1 rounded-md bg-text-primary text-bg-error hover:opacity-80 transition-opacity"
          >
            Refetch
          </button>
        </div>
      )}

      {!isLoading && !error && accessories.length === 0 && (
        <div className="bg-warning text-text-primary rounded-md p-4">
          No accessories found. Please check the product graph and add compatible accessories.
        </div>
      )}

      {!isLoading && !error && accessories.length > 0 && (
        <div className="flex space-x-4 overflow-x-auto pb-4" ref={scrollContainerRef} onWheel={handleWheel} onMouseMove={handleDrag} onMouseDown={() => {}} onMouseUp={() => {}}>
          {accessories.map((accessory) => (
            <AccessoryTile key={accessory.id} accessory={accessory} />
          ))}
        </div>
      )}
    </section>
  );
};

export default AccessorySection;