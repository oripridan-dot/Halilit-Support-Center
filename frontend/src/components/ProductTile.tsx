import React from 'react';

interface Product {
  id: string;
  name: string;
  image_url?: string | null;
  stock: number | null | undefined;
  price: number | null;
}

interface Props {
  product: Product;
}

const ProductTile: React.FC<Props> = ({ product }) => {
  const { stock, price, name, image_url } = product;

  const isOutOfStock = stock === 0;
  const isUnconfirmedStock = stock === null || stock === undefined;
  const isCallForPrice = price === null || price === 0;

  const borderColor = isOutOfStock ? 'border-red-500' : isUnconfirmedStock ? 'border-amber-500' : '';
  const hasIndicators = isOutOfStock || isUnconfirmedStock || isCallForPrice;

  return (
    <div className={`relative border rounded-md shadow-md ${borderColor}`}>
      {/* Badges */}
      {(isOutOfStock || isUnconfirmedStock) && (
        <div className="absolute top-0 right-0 p-2">
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

      {/* Product Image */}
      <img
        src={image_url || '/placeholder.png'}
        alt={name}
        className="w-full h-48 object-cover rounded-t-md"
        onError={(e) => {
          (e.target as HTMLImageElement).src = '/placeholder.png';
        }}
      />

      <div className="p-2">
        <h3 className="text-lg font-medium">{name}</h3>

        {/* Price or Call for Price */}
        {isCallForPrice ? (
          <p className="text-red-500">Call for Price</p>
        ) : (
          <p className="font-bold">${price?.toFixed(2)}</p>
        )}
      </div>
    </div>
  );
};

export default ProductTile;