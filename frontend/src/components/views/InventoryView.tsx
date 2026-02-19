import React from 'react';
import { Product } from '../../types';
import { formatPrice } from '../../types';

interface InventoryViewProps {
  products: Product[];
}

const InventoryView: React.FC<InventoryViewProps> = ({ products }) => {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
      {products.map((product) => {
        const isOutOfStock = product.stock === 0;
        const isUnconfirmed = product.stock === null || product.stock === undefined;
        const hasPrice = product.pricing?.price_il !== null && product.pricing?.price_il !== undefined;
        const showOutOfStockBadge = isOutOfStock;
        const showUnconfirmedBadge = isUnconfirmed;

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
            {/* Badges */}
            {(showOutOfStockBadge || showUnconfirmedBadge) && (
              <div className="absolute top-2 right-2 flex flex-col items-end gap-1">
                {showOutOfStockBadge && (
                  <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-sm">
                    OUT OF STOCK
                  </span>
                )}
                {showUnconfirmedBadge && (
                  <span className="bg-amber-500 text-gray-900 text-xs font-bold px-2 py-1 rounded-sm">
                    UNCONFIRMED
                  </span>
                )}
              </div>
            )}

            {/* Content */}
            <div className="flex flex-col gap-2">
              <h3 className="text-text-primary text-lg font-semibold">{product.product_name}</h3>
              <p className="text-text-tertiary text-sm">{product.brand}</p>
              <div className="flex justify-between items-center">
                <p className="text-text-primary font-bold">
                  {product.pricing?.price_il !== null && product.pricing?.price_il !== undefined
                    ? formatPrice(product)
                    : 'Price on request'}
                </p>
                {/* Stock Level */}
                {typeof product.stock === 'number' && (
                  <span className="text-text-muted text-sm">
                    Stock: {product.stock}
                  </span>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default InventoryView;