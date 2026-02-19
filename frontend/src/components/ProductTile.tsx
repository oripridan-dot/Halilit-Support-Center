import React from 'react';

interface Product {
  id: string;
  name: string;
  image_url?: string | null;
  price?: number | null;
  stock?: number | null;
  // Add other product properties as needed
}

interface ProductTileProps {
  product: Product;
}

const ProductTile: React.FC<ProductTileProps> = ({ product }) => {
  const { stock, price } = product;

  const isOutOfStock = stock === 0;
  const isUnconfirmedStock = stock === null || stock === undefined;
  const isCallForPrice = !price || price <= 0;

  let borderClass = '';
  if (isOutOfStock) {
    borderClass = 'border-red-500';
  } else if (isUnconfirmedStock) {
    borderClass = 'border-amber-500';
  }

  return (
    <div className={`relative border rounded-lg shadow-md p-4 ${borderClass}`}>
      {/* Badges */}
      {(isOutOfStock || isUnconfirmedStock) && (
        <div className="absolute top-0 right-0 m-2">
          {isOutOfStock && (
            <span className="bg-red-500 text-white px-2 py-1 rounded-md text-xs">
              OUT OF STOCK
            </span>
          )}
          {isUnconfirmedStock && (
            <span className="bg-amber-500 text-gray-800 px-2 py-1 rounded-md text-xs">
              UNCONFIRMED
            </span>
          )}
        </div>
      )}

      {/* Product Image (Placeholder handled elsewhere) */}
      {/* Assuming an image component handles the actual image display and fallback */}

      {/* Product Name */}
      <h3 className="text-lg font-semibold mb-2">{product.name}</h3>

      {/* Price or Call for Price */}
      {isCallForPrice ? (
        <div className="text-red-500">Call for Price</div>
      ) : (
        <div className="text-gray-700">
          {price !== null && price !== undefined ? `$${price.toFixed(2)}` : ''}
        </div>
      )}
    </div>
  );
};

export default ProductTile;