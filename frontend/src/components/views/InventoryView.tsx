import React from 'react';
import { Product } from '../../types';
import { formatPrice } from '../../types';

interface InventoryViewProps {
  products: Product[];
}

const InventoryView: React.FC<InventoryViewProps> = ({ products }) => {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {products.map((product) => {
        const isOutOfStock = product.stock === 0;
        const isUnconfirmed = product.stock === null || product.stock === undefined;
        const hasPrice = product.pricing?.price_il !== null && product.pricing?.price_il !== undefined;

        let borderClass = '';
        if (isOutOfStock) {
          borderClass = 'border-2 border-red-500';
        } else if (isUnconfirmed) {
          borderClass = 'border-2 border-amber-500';
        }

        return (
          <div
            key={product.product_id}
            className={`relative rounded-lg shadow-md bg-bg-elevated p-4 ${borderClass}`}
          >
            {(isOutOfStock || isUnconfirmed) && (
              <div className="absolute top-2 right-2">
                {isOutOfStock && (
                  <span className="bg-red-500 text-white text-xs font-medium px-2 py-1 rounded-md">
                    OUT OF STOCK
                  </span>
                )}
                {isUnconfirmed && (
                  <span className="bg-amber-500 text-gray-900 text-xs font-medium px-2 py-1 rounded-md">
                    UNCONFIRMED
                  </span>
                )}
              </div>
            )}
            <div className="flex items-center justify-center h-32 mb-4">
              {/* Placeholder for product image */}
              <div className="w-24 h-24 bg-gray-200 rounded-md"></div>
            </div>
            <h3 className="text-lg font-medium text-text-primary mb-2">{product.product_name}</h3>
            <p className="text-text-tertiary text-sm mb-2">{product.brand}</p>
            {hasPrice ? (
              <p className="text-text-primary font-medium">{formatPrice(product)}</p>
            ) : (
              <p className="text-text-primary font-medium">Call for Price</p>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default InventoryView;