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
  const { stock, price } = product;

  const isOutOfStock = stock === 0;
  const isUnconfirmedStock = stock === null || stock === undefined;
  const isCallForPrice = price === null || price === 0;

  const borderClass = isOutOfStock ? 'border-red-500' : isUnconfirmedStock ? 'border-amber-500' : '';
  const badgePositionClass = 'absolute top-0 right-0';
  const badgeCommonClasses = 'px-2 py-1 rounded-md text-xs';

  return (
    <div className={`relative border rounded-md shadow-md ${borderClass}`}>
      {isOutOfStock && (
        <div className={`${badgePositionClass} bg-red-500 text-white ${badgeCommonClasses}`}>
          OUT OF STOCK
        </div>
      )}
      {isUnconfirmedStock && !isOutOfStock && (
        <div className={`${badgePositionClass} bg-amber-500 text-gray-800 ${badgeCommonClasses}`}>
          UNCONFIRMED
        </div>
      )}
      <div className="p-4">
        <img
          src={product.image_url || '/placeholder.png'}
          alt={product.name}
          className="w-full h-48 object-cover mb-2"
          onError={(e) => {
            (e.target as HTMLImageElement).src = '/placeholder.png';
          }}
        />
        <h3 className="text-lg font-semibold">{product.name}</h3>
        {isCallForPrice ? (
          <div className="text-red-500">Call for Price</div>
        ) : (
          <div className="text-gray-700">${price !== null ? price.toFixed(2) : ''}</div>
        )}
      </div>
    </div>
  );
};

export default ProductTile;