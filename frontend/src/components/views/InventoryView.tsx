import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useConductorCatalog } from '../../hooks/useConductorCatalog';
import { Product, formatPrice } from '../../types';
import { PackageOpen } from 'lucide-react';
import { useNavigationStore } from '../../store/navigationStore';
import { useDebounceValue } from '../../hooks/useDebounceValue';
import { Check, ChevronDown, ChevronRight, ChevronsUpDown, Package, Search } from 'lucide-react';

interface StockBadgeProps {
  stock: number | null | undefined;
}

const StockBadge: React.FC<StockBadgeProps> = ({ stock }) => {
  if (stock === null || stock === undefined) {
    return (
      <span className="bg-amber-500 text-zinc-900 text-xs font-medium px-2 py-1 rounded-md">
        UNCONFIRMED
      </span>
    );
  }
  if (stock === 0) {
    return (
      <span className="bg-red-500 text-white text-xs font-medium px-2 py-1 rounded-md">
        OUT OF STOCK
      </span>
    );
  }
  return null;
};

const PAGE_SIZE = 50;

const InventoryView: React.FC = () => {
  const navigate = useNavigate();
  const { products, isLoading, error, refetch } = useConductorCatalog();
  const { searchQuery, initialCfpFilter, setSearchQuery, goToProduct } = useNavigationStore();

  const [filterText, setFilterText] = useState(
    typeof searchQuery === "string" ? searchQuery : "",
  );
  const debouncedFilterText = useDebounceValue(filterText, 150);
  const [brandFilter, setBrandFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [cfpOnly, setCfpOnly] = useState(initialCfpFilter ?? false);
  const [sortField, setSortField] = useState("name");
  const [sortDir, setSortDir] = useState("asc");
  const [page, setPage] = useState(1);

  // 1. Sync filterText from navigation store deep-link
  useEffect(() => {
    if (typeof searchQuery === "string" && searchQuery !== null) {
      setFilterText(searchQuery);
    }
  }, [searchQuery]);

  // Apply the debounced search and initial filters
  useEffect(() => {
      setSearchQuery(debouncedFilterText || null);
  }, [debouncedFilterText, setSearchQuery]);

  // 2. Sync cfpOnly from navigation store deep-link
  useEffect(() => {
    setCfpOnly(initialCfpFilter ?? false);
  }, [initialCfpFilter]);

  // 3. Reset pagination on any filter/sort change
  useEffect(() => {
    setPage(1);
  }, [filterText, brandFilter, categoryFilter, cfpOnly, sortField, sortDir]);

  const filterStr = typeof debouncedFilterText === "string" ? debouncedFilterText : "";

  const filteredProducts = useMemo(() => {
    if (!products) return [];

    let filtered = products.filter(item => {
      const matchesText =
        !filterStr ||
        item.name.toLowerCase().includes(filterStr.toLowerCase()) ||
        (item.brand && item.brand.toLowerCase().includes(filterStr.toLowerCase()));

      const matchesBrand = !brandFilter || item.brand === brandFilter;
      const matchesCategory = !categoryFilter || item.category === categoryFilter;
      const matchesCfp = !cfpOnly || item.data_status === "COMPLETE";

      return matchesText && matchesBrand && matchesCategory && matchesCfp;
    });

    return filtered;
  }, [products, filterStr, brandFilter, categoryFilter, cfpOnly]);

  const sortedProducts = useMemo(() => {
    if (!filteredProducts) return [];

    const sorted = [...filteredProducts].sort((a, b) => {
      const fieldA = a[sortField as keyof Product];
      const fieldB = b[sortField as keyof Product];

      let comparison = 0;
      if (fieldA < fieldB) {
        comparison = -1;
      }
      if (fieldA > fieldB) {
        comparison = 1;
      }
      if (sortDir === "desc") {
        comparison *= -1;
      }
      return comparison;
    });

    return sorted;
  }, [filteredProducts, sortField, sortDir]);

  const paginatedProducts = useMemo(() => {
    if (!sortedProducts) return [];
    const startIndex = (page - 1) * PAGE_SIZE;
    return sortedProducts.slice(startIndex, startIndex + PAGE_SIZE);
  }, [sortedProducts, page]);

  const handleProductClick = (productId: string) => {
    goToProduct(productId);
  };

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDir("asc");
    }
  };

  return (
    <div className="container mx-auto py-4">
      <div className="flex items-center mb-4">
        <div className="relative w-full">
          <input
            type="text"
            placeholder="Search products..."
            value={filterText}
            onChange={(e) => setFilterText(e.target.value)}
            className="w-full py-2 pl-10 pr-4 rounded-md text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <div className="absolute top-0 left-0 py-2 pl-3">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
        </div>
      </div>

      <div className="flex items-center mb-2">
        <label htmlFor="cfp-only" className="mr-2">
          CFP Only:
        </label>
        <input
          type="checkbox"
          id="cfp-only"
          checked={cfpOnly}
          onChange={(e) => setCfpOnly(e.target.checked)}
          className="mr-2"
        />
      </div>

      {isLoading && (
        <div className="text-center py-4">Loading...</div>
      )}

      {error && (
        <div className="text-center py-4 text-red-500">Error: {error.message}</div>
      )}

      {(!isLoading && !error && paginatedProducts.length === 0) && (
        <div className="text-center py-4">No products found.</div>
      )}

      {(!isLoading && !error && paginatedProducts.length > 0) && (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th
                  onClick={() => handleSort('name')}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                >
                  Name
                  {sortField === 'name' && (
                    sortDir === 'asc' ? (
                      <ChevronDown className="inline ml-1 h-4 w-4" />
                    ) : (
                      <ChevronRight className="inline ml-1 h-4 w-4" />
                    )
                  )}
                </th>
                <th
                  onClick={() => handleSort('brand')}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                >
                  Brand
                  {sortField === 'brand' && (
                    sortDir === 'asc' ? (
                      <ChevronDown className="inline ml-1 h-4 w-4" />
                    ) : (
                      <ChevronRight className="inline ml-1 h-4 w-4" />
                    )
                  )}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th
                  onClick={() => handleSort('price')}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                >
                  Price
                  {sortField === 'price' && (
                    sortDir === 'asc' ? (
                      <ChevronDown className="inline ml-1 h-4 w-4" />
                    ) : (
                      <ChevronRight className="inline ml-1 h-4 w-4" />
                    )
                  )}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stock
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {paginatedProducts.map((product) => (
                <tr
                  key={product.id}
                  className="hover:bg-gray-100 cursor-pointer"
                  onClick={() => handleProductClick(product.id)}
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {product.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {product.brand}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {product.category}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatPrice(product.price)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <StockBadge stock={product.specs?.stock} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="flex items-center justify-between mt-4">
            <button
              onClick={() => setPage(page - 1)}
              disabled={page === 1}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded opacity-75 disabled:opacity-50"
            >
              Previous
            </button>
            <span>Page {page}</span>
            <button
              onClick={() => setPage(page + 1)}
              disabled={!sortedProducts || (page * PAGE_SIZE) >= sortedProducts.length}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded opacity-75 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default InventoryView;