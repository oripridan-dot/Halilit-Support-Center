import React from 'react';

interface Product {
  id: string;
  name: string;
  image_url?: string | null;
  stock: number | null | undefined;
  price: number | null;
  [key: string]: any;
}

interface ProductTileProps {
  product: Product;
}

const ProductTile: React.FC<ProductTileProps> = ({ product }) => {
  const { stock, price } = product;

  const isOutOfStock = stock === 0;
  const isUnconfirmedStock = stock === null || stock === undefined;
  const isCallForPrice = price === null || price === 0;

  const borderClass = isOutOfStock
    ? 'border-red-500'
    : isUnconfirmedStock
    ? 'border-amber-500'
    : '';

  const badgePositionClass = 'absolute top-2 right-2';

  return (
    <div className={`relative border rounded-lg shadow-md p-4 ${borderClass}`}>
      {isOutOfStock && (
        <div className={`${badgePositionClass} bg-red-500 text-white px-2 py-1 rounded-md text-xs z-10`}>
          OUT OF STOCK
        </div>
      )}
      {isUnconfirmedStock && (
        <div className={`${badgePositionClass} bg-amber-500 text-gray-800 px-2 py-1 rounded-md text-xs z-10`}>
          UNCONFIRMED
        </div>
      )}

      {/* Product Image - Placeholder and Fallback implemented in a separate spec */}
      <img
        src={product.image_url || '/placeholder.png'}
        alt={product.name}
        onError={(e) => {
          (e.target as HTMLImageElement).src = '/placeholder.png';
        }}
        className="w-full h-40 object-cover rounded-md"
      />

      <div className="mt-2">
        <h3 className="text-lg font-semibold">{product.name}</h3>

        {isCallForPrice ? (
          <p className="text-red-500">Call for Price</p>
        ) : (
          <p className="text-gray-700">
            {price !== null && price !== undefined ? `$${price.toFixed(2)}` : ''}
          </p>
        )}
      </div>
    </div>
  );
};

export default ProductTile;