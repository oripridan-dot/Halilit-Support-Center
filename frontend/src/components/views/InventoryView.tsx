import React from 'react';
import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useDebounce } from 'use-debounce';
import { CheckCircleIcon, XCircleIcon } from 'lucide-react';
import { useNavigationStore } from '../../store/navigationStore';
import { ConductorProduct } from '../../types';
import { fetchProducts } from '../../api/products';

const InventoryView: React.FC = () => {
  const { goToProduct } = useNavigationStore();
  const [searchTerm, setSearchTerm] = React.useState<string>('');
  const [debouncedSearchTerm] = useDebounce(searchTerm, 300);

  const { data: products, isLoading, isError } = useQuery({
    queryKey: ['products', debouncedSearchTerm],
    queryFn: () => fetchProducts(debouncedSearchTerm),
    staleTime: 5000,
  });

  const sortedProducts = useMemo(() => {
    if (!products) {
      return [];
    }

    return [...products].sort((a, b) => {
      const stockA = a.stock === null ? 1 : a.stock === 0 ? 2 : 0;
      const stockB = b.stock === null ? 1 : b.stock === 0 ? 2 : 0;

      if (stockA !== stockB) {
        return stockA - stockB;
      }

      const priceA = a.price === null || a.price === 0 ? 1 : 0;
      const priceB = b.price === null || b.price === 0 ? 1 : 0;

      if (priceA !== priceB) {
        return priceA - priceB;
      }

      return (a.id || '').localeCompare(b.id || '');
    });
  }, [products]);

  const renderStockStatus = (product: ConductorProduct) => {
    if (product.stock === 0) {
      return (
        <div className="absolute top-0 right-0 p-1 bg-red-500 text-white text-xs font-bold rounded-bl-md z-10">
          OUT OF STOCK
        </div>
      );
    }
    if (product.stock === null || product.stock === undefined) {
      return (
        <div className="absolute top-0 right-0 p-1 bg-amber-500 text-zinc-900 text-xs font-bold rounded-bl-md z-10">
          UNCONFIRMED
        </div>
      );
    }
    return null;
  };

  const renderCallForPrice = (product: ConductorProduct) => {
    if (product.price === null || product.price === 0) {
      return (
        <div className="absolute top-0 right-0 p-1 bg-amber-500 text-zinc-900 text-xs font-bold rounded-bl-md z-10">
          Call for Price
        </div>
      );
    }
    return null;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        Loading...
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex items-center justify-center h-full text-red-500">
        Error loading products.
      </div>
    );
  }

  if (!products || products.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-zinc-400">
        No products found.
      </div>
    );
  }

  return (
    <div className="p-4">
      <input
        type="text"
        placeholder="Search products..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="w-full p-2 mb-4 text-zinc-900 rounded-md shadow-md dark:bg-zinc-700 dark:text-white"
      />
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left rtl:text-right text-zinc-400 dark:text-zinc-400">
          <thead className="text-xs uppercase bg-zinc-700 dark:bg-zinc-700 text-zinc-400 dark:text-zinc-400">
            <tr>
              <th scope="col" className="px-6 py-3">
                Name
              </th>
              <th scope="col" className="px-6 py-3">
                Brand
              </th>
              <th scope="col" className="px-6 py-3">
                Price
              </th>
              <th scope="col" className="px-6 py-3">
                Stock
              </th>
              <th scope="col" className="px-6 py-3">
                Status
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedProducts.map((product) => (
              <tr
                key={product.id}
                className={`bg-zinc-800 border-b border-zinc-700 dark:bg-zinc-800 dark:border-zinc-700 hover:bg-zinc-700 cursor-pointer relative ${
                  product.stock === 0
                    ? 'border-red-500'
                    : product.stock === null || product.stock === undefined
                    ? 'border-amber-500'
                    : ''
                }`}
                onClick={() => goToProduct(product.id)}
              >
                <td className="px-6 py-4 font-medium text-white whitespace-nowrap dark:text-white">
                  {product.name}
                  {renderStockStatus(product)}
                  {renderCallForPrice(product)}
                </td>
                <td className="px-6 py-4">{product.brand}</td>
                <td className="px-6 py-4">
                  {product.price !== null ? `₪${product.price.toFixed(2)}` : 'Call for Price'}
                </td>
                <td className="px-6 py-4">
                  {product.stock !== null && product.stock !== undefined
                    ? product.stock
                    : 'Unconfirmed'}
                </td>
                <td className="px-6 py-4">
                  {product.data_status === 'active' ? (
                    <CheckCircleIcon className="w-4 h-4 text-green-500" />
                  ) : (
                    <XCircleIcon className="w-4 h-4 text-red-500" />
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default InventoryView;