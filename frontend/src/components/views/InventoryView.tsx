import React from 'react';
import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ArrowUpDown } from 'lucide-react';
import { useDebounce } from '../../hooks/useDebounce';
import { useNavigationStore } from '../../store/navigationStore';
import { useConductorCatalog } from '../../hooks/useConductorCatalog';
import { ConductorProduct } from '../../types';

const InventoryView = () => {
  const { data: products, isLoading, isError } = useConductorCatalog();
  const [searchText, setSearchText] = React.useState('');
  const debouncedSearchText = useDebounce(searchText, 300);
  const goToProduct = useNavigationStore((state) => state.goToProduct);

  const handleRowClick = (productId: string) => {
    goToProduct(productId);
  };

  const filteredProducts = useMemo(() => {
    if (!products) {
      return [];
    }
    return products.filter((product) => {
      const searchTerm = debouncedSearchText.toLowerCase();
      return (
        product.name.toLowerCase().includes(searchTerm) ||
        product.brand?.toLowerCase().includes(searchTerm)
      );
    });
  }, [products, debouncedSearchText]);

  const sortedProducts = useMemo(() => {
    if (!filteredProducts) {
      return [];
    }

    const sortProducts = (a: ConductorProduct, b: ConductorProduct) => {
      // Prioritize In Stock
      if ((b.stock ?? 0) > 0 && (a.stock ?? 0) <= 0) return 1;
      if ((a.stock ?? 0) > 0 && (b.stock ?? 0) <= 0) return -1;

      // Prioritize Call for Price within In Stock
      if ((a.stock ?? 0) > 0 && (b.stock ?? 0) > 0) {
        if ((a.price === null || a.price === 0) && (b.price !== null && b.price !== 0)) return 1;
        if ((b.price === null || b.price === 0) && (a.price !== null && a.price !== 0)) return -1;
      }

      // Prioritize Unconfirmed after In Stock
      if ((b.stock ?? null) === null && (a.stock ?? 0) > 0) return 1;
      if ((a.stock ?? null) === null && (b.stock ?? 0) > 0) return -1;

      // Prioritize Out of Stock Last
      if ((a.stock ?? 0) === 0 && (b.stock ?? 0) !== 0) return 1;
      if ((b.stock ?? 0) === 0 && (a.stock ?? 0) !== 0) return -1;

       // Sort CFP after in-stock, before out of stock.
       if ((a.stock ?? 0) === 0 && (b.price ?? 1) > 0) return 1;
       if ((b.stock ?? 0) === 0 && (a.price ?? 1) > 0) return -1;

      return a.id.localeCompare(b.id);
    };

    return [...filteredProducts].sort(sortProducts);
  }, [filteredProducts]);

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
    <div className="w-full overflow-x-auto">
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search by name or brand"
          className="w-full px-4 py-2 text-zinc-900 placeholder-zinc-400 bg-zinc-100 rounded-md dark:bg-zinc-700 dark:text-zinc-100 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
        />
      </div>
      <table className="min-w-full divide-y divide-zinc-700">
        <thead className="bg-zinc-800">
          <tr>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-300"
            >
              <div className="flex items-center">
                Product Name
                <ArrowUpDown className="w-4 h-4 ml-2" />
              </div>
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-300"
            >
              Brand
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-300"
            >
              Price (IL)
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-300"
            >
              Price (Eilat)
            </th>
            <th
              scope="col"
              className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-zinc-300"
            >
              Stock Status
            </th>
          </tr>
        </thead>
        <tbody className="bg-zinc-900 divide-y divide-zinc-700">
          {sortedProducts.map((product) => (
            <tr
              key={product.id}
              className={`hover:bg-zinc-800 cursor-pointer ${
                (product.stock === 0) && 'border-red-500 border-2' ||
                (product.stock === null || product.stock === undefined) && 'border-amber-500 border-2' ||
                ''
              }`}
              onClick={() => handleRowClick(product.id)}
            >
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-zinc-200">
                {product.name}
                {(product.stock === 0) && (
                  <span className="ml-2 px-2 py-1 text-xs font-bold leading-none text-white bg-red-500 rounded-full">
                    OUT OF STOCK
                  </span>
                )}
                {(product.stock === null || product.stock === undefined) && (
                  <span className="ml-2 px-2 py-1 text-xs font-bold leading-none text-zinc-900 bg-amber-500 rounded-full">
                    UNCONFIRMED
                  </span>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-zinc-400">{product.brand}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-zinc-200">
                {product.price !== null && product.price !== 0 ? `₪${product.price.toFixed(2)}` : 'Call for Price'}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-zinc-200">{product.price_eilat !== null ? `₪${product.price_eilat.toFixed(2)}` : '-'}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-zinc-200">
                {(product.stock !== null && product.stock !== undefined) ? (
                  product.stock > 0 ? 'In Stock' : 'Out of Stock'
                ) : (
                  'Unconfirmed'
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default InventoryView;