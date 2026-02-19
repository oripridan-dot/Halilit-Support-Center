import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useConductorCatalog } from '../../hooks/useConductorCatalog';
import { Product, formatPrice } from '../../types';
import { PackageOpen } from 'lucide-react';
import { useNavigationStore } from '../../stores/navigationStore';
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
      if (searchQuery === "") setSearchQuery(null);
    }
  }, [searchQuery, setSearchQuery]);

  // Apply the debounced search and initial filters
  useEffect(() => {
    setSearchQuery(debouncedFilterText || null);
  }, [debouncedFilterText, setSearchQuery]);

  // 2. Sync cfpOnly from navigation store deep-link
  useEffect(() => {
    if (initialCfpFilter === true) setCfpOnly(true);
    else if (initialCfpFilter === false) setCfpOnly(false);
  }, [initialCfpFilter]);

  // 3. Reset pagination on any filter/sort change
  useEffect(() => {
    setPage(1);
  }, [filterText, brandFilter, categoryFilter, cfpOnly, sortField, sortDir]);

  const filterStr = typeof filterText === "string" ? filterText : "";

  const filteredProducts = useMemo(() => {
    if (!products) return [];

    let filtered = products.filter(item => {
      const matchesText =
        !filterStr ||
        item.name.toLowerCase().includes(filterStr.toLowerCase()) ||
        (item.brand && item.brand.toLowerCase().includes(filterStr.toLowerCase()));

      const matchesBrand = !brandFilter || item.brand === brandFilter;
      const matchesCategory = !categoryFilter || item.category === categoryFilter;
      const matchesCfp = !cfpOnly || !item.price || item.price === 0;

      return matchesText && matchesBrand && matchesCategory && matchesCfp;
    });

    // Custom sorting logic
    filtered = [...filtered].sort((a, b) => {
      const stockA = a.stock === null || a.stock === undefined ? 1 : a.stock === 0 ? 2 : 0;
      const stockB = b.stock === null || b.stock === undefined ? 1 : b.stock === 0 ? 2 : 0;

      if (stockA !== stockB) {
        return stockA - stockB; // In Stock first, then Unconfirmed, then Out of Stock
      }

      // Within stock status, sort by price (non-CfP before CfP)
      const priceA = a.price === null || a.price === 0 ? 1 : 0;
      const priceB = b.price === null || b.price === 0 ? 1 : 0;

      if (priceA !== priceB) {
        return priceA - priceB;
      }
      // Tie-breaker: sort by ID
      return (a.id || '').localeCompare(b.id || '');
    });

    return filtered;
  }, [products, filterStr, brandFilter, categoryFilter, cfpOnly]);

  const paginatedProducts = useMemo(() => {
    const startIndex = (page - 1) * PAGE_SIZE;
    return filteredProducts.slice(startIndex, startIndex + PAGE_SIZE);
  }, [filteredProducts, page]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  if (!products || products.length === 0) {
    return <div>No products found.</div>;
  }

  return (
    <div>
      <div className="flex items-center mb-4">
        <input
          type="text"
          placeholder="Search products..."
          value={filterText}
          onChange={e => setFilterText(e.target.value)}
          className="border rounded py-2 px-3 mr-2"
        />
        <button
          onClick={() => setCfpOnly(!cfpOnly)}
          className={`py-2 px-3 rounded ${cfpOnly ? 'bg-blue-500 text-white' : 'bg-gray-200'
            }`}
        >
          {cfpOnly ? 'Showing CfP Only' : 'Show CfP'}
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr>
              <th className="px-6 py-3 border-b-2 border-gray-300 text-left text-xs font-medium uppercase tracking-wider">
                Name
              </th>
              <th className="px-6 py-3 border-b-2 border-gray-300 text-left text-xs font-medium uppercase tracking-wider">
                Brand
              </th>
              <th className="px-6 py-3 border-b-2 border-gray-300 text-left text-xs font-medium uppercase tracking-wider">
                Price
              </th>
              <th className="px-6 py-3 border-b-2 border-gray-300 text-left text-xs font-medium uppercase tracking-wider">
                Stock
              </th>
            </tr>
          </thead>
          <tbody>
            {paginatedProducts.map(product => {
              const outOfStock = product.stock === 0;
              const unconfirmed = product.stock === null || product.stock === undefined;
              const hasPrice = product.price !== null && product.price !== 0;

              return (
                <tr
                  key={product.id}
                  className={`hover:bg-gray-100 ${outOfStock ? 'border-red-500 border-2' : unconfirmed ? 'border-amber-500 border-2' : ''
                    }`}
                  onClick={() => goToProduct(product.id)}
                  style={{ cursor: 'pointer' }}
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 relative">
                    {product.name}
                    <StockBadge stock={product.stock} />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{product.brand}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatPrice(product.price)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {product.stock !== null && product.stock !== undefined
                      ? product.stock
                      : 'Unconfirmed'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {/* Pagination Controls */}
      <div className="flex justify-between items-center mt-4">
        <button
          onClick={() => setPage(prev => Math.max(prev - 1, 1))}
          disabled={page === 1}
          className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded opacity-75 disabled:opacity-50"
        >
          Previous
        </button>
        <span>
          Page {page} of {Math.ceil(filteredProducts.length / PAGE_SIZE)}
        </span>
        <button
          onClick={() =>
            setPage(prev => Math.min(prev + 1, Math.ceil(filteredProducts.length / PAGE_SIZE)))
          }
          disabled={page * PAGE_SIZE >= filteredProducts.length}
          className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded opacity-75 disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default InventoryView;