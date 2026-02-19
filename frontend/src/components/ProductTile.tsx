import React from 'react';

interface Product {
  id: string;
  name: string;
  image_url?: string | null;
  price: number | null;
  stock: number | null | undefined;
}

interface ProductTileProps {
  product: Product;
}

const ProductTile: React.FC<ProductTileProps> = ({ product }) => {
  const { price, stock } = product;
  const isOutOfStock = stock === 0;
  const isUnconfirmedStock = stock === null || stock === undefined;
  const isCallForPrice = !price || price <= 0;

  const borderClass = isOutOfStock
    ? 'border-red-500'
    : isUnconfirmedStock
    ? 'border-amber-500'
    : '';

  return (
    <div
      className={`relative border rounded-lg shadow-md p-4 ${borderClass}`}
    >
      {/* Badges */}
      {(isOutOfStock || isUnconfirmedStock) && (
        <div className="absolute top-2 right-2">
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

      {/* Image and other product details (implementation will vary based on project structure) */}
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
          <p className="text-gray-700">${price?.toFixed(2)}</p>
        )}
      </div>
    </div>
  );
};

export default ProductTile;