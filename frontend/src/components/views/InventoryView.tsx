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
      const matchesCfp = !cfpOnly || item.price === null || item.price === 0;

      return matchesText && matchesBrand && matchesCategory && matchesCfp;
    });


    filtered.sort((a, b) => {
        const stockA = a.stock === null ? 1 : a.stock === 0 ? 2 : 0;
        const stockB = b.stock === null ? 1 : b.stock === 0 ? 2 : 0;

        if (stockA !== stockB) {
            return stockA - stockB;
        }

        const priceA = a.price === null || a.price === 0 ? 1 : 0;
        const priceB = b.price === null || b.price === 0 ? 1 : 0;

        if (stockA === 0) {
            return priceA - priceB;
        }
        if (stockA === 1) {
            return priceA - priceB;
        }

        if (priceA !== priceB) {
            return priceA - priceB;
        }

        return a.id.localeCompare(b.id);
    });

    const startIndex = (page - 1) * PAGE_SIZE;
    const endIndex = startIndex + PAGE_SIZE;
    return filtered.slice(startIndex, endIndex);
  }, [products, filterStr, brandFilter, categoryFilter, cfpOnly, page]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilterText(e.target.value);
  };

  const handleBrandFilterChange = (brand: string) => {
    setBrandFilter(brand);
  };

  const handleCategoryFilterChange = (category: string) => {
    setCategoryFilter(category);
  };

  const handleCfpOnlyChange = (checked: boolean) => {
    setCfpOnly(checked);
  };

  const handleSortChange = (field: string) => {
    if (sortField === field) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDir("asc");
    }
  };

  const handlePageChange = (newPage: number) => {
    setPage(newPage);
  };

  const totalPages = useMemo(() => {
    if (!products) return 0;
    return Math.ceil(products.length / PAGE_SIZE);
  }, [products]);

  return (
    <div className="container mx-auto py-4">
      <div className="mb-4 flex items-center space-x-4">
        <div className="flex-1">
          <label htmlFor="search" className="sr-only">
            Search
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <Search className="w-5 h-5 text-gray-400" />
            </div>
            <input
              type="text"
              id="search"
              className="block w-full p-2 pl-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Search by name or brand"
              value={filterText}
              onChange={handleSearchChange}
            />
          </div>
        </div>
        <button
          onClick={() => navigate('/inventory/new')}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        >
          Add Product
        </button>
      </div>

      <div className="mb-4 flex space-x-4">
        <div className="flex-1">
          <label htmlFor="brandFilter" className="block text-sm font-medium text-gray-700">
            Brand
          </label>
          <input
            type="text"
            id="brandFilter"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
            value={brandFilter}
            onChange={(e) => handleBrandFilterChange(e.target.value)}
          />
        </div>
        <div className="flex-1">
          <label htmlFor="categoryFilter" className="block text-sm font-medium text-gray-700">
            Category
          </label>
          <input
            type="text"
            id="categoryFilter"
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50"
            value={categoryFilter}
            onChange={(e) => handleCategoryFilterChange(e.target.value)}
          />
        </div>
        <div>
          <label className="inline-flex items-center">
            <input
              type="checkbox"
              className="form-checkbox h-4 w-4 text-blue-600 transition duration-150 ease-in-out"
              checked={cfpOnly}
              onChange={(e) => handleCfpOnlyChange(e.target.checked)}
            />
            <span className="ml-2 text-sm text-gray-700">Call for Price Only</span>
          </label>
        </div>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-10">
          Loading...
        </div>
      )}

      {error && (
        <div className="flex items-center justify-center py-10 text-red-500">
          Error: {error.message}
        </div>
      )}

      {products && !isLoading && !error && (
        <>
          <div className="overflow-x-auto rounded-lg shadow hidden md:block">
            <table className="w-full text-left">
              <thead className="bg-gray-50">
                <tr>
                  <th
                    onClick={() => handleSortChange('name')}
                    className="px-6 py-3 text-xs font-medium text-gray-500 uppercase hover:bg-gray-100 cursor-pointer"
                  >
                    Name
                    {sortField === 'name' && (
                      sortDir === 'asc' ? <ChevronDown className="inline ml-1 w-4 h-4" /> : <ChevronRight className="inline ml-1 w-4 h-4" />
                    )}
                  </th>
                  <th
                    onClick={() => handleSortChange('brand')}
                    className="px-6 py-3 text-xs font-medium text-gray-500 uppercase hover:bg-gray-100 cursor-pointer"
                  >
                    Brand
                    {sortField === 'brand' && (
                      sortDir === 'asc' ? <ChevronDown className="inline ml-1 w-4 h-4" /> : <ChevronRight className="inline ml-1 w-4 h-4" />
                    )}
                  </th>
                  <th
                    onClick={() => handleSortChange('category')}
                    className="px-6 py-3 text-xs font-medium text-gray-500 uppercase hover:bg-gray-100 cursor-pointer"
                  >
                    Category
                    {sortField === 'category' && (
                      sortDir === 'asc' ? <ChevronDown className="inline ml-1 w-4 h-4" /> : <ChevronRight className="inline ml-1 w-4 h-4" />
                    )}
                  </th>
                  <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase">
                    Stock
                  </th>
                  <th
                    onClick={() => handleSortChange('price')}
                    className="px-6 py-3 text-xs font-medium text-gray-500 uppercase hover:bg-gray-100 cursor-pointer"
                  >
                    Price
                    {sortField === 'price' && (
                      sortDir === 'asc' ? <ChevronDown className="inline ml-1 w-4 h-4" /> : <ChevronRight className="inline ml-1 w-4 h-4" />
                    )}
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredProducts.map((product) => (
                  <tr
                    key={product.id}
                    className="hover:bg-gray-100 cursor-pointer"
                    onClick={() => goToProduct(product.id)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {product.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {product.brand}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {product.category}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <StockBadge stock={product.stock} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatPrice(product.price, product.currency)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="md:hidden">
            {filteredProducts.map((product) => (
              <div
                key={product.id}
                className="p-4 border-b border-gray-200 hover:bg-gray-100 cursor-pointer"
                onClick={() => goToProduct(product.id)}
              >
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-gray-900">{product.name}</span>
                  <StockBadge stock={product.stock} />
                </div>
                <p className="text-sm text-gray-500">{product.brand} - {product.category}</p>
                <p className="text-sm text-gray-500">{formatPrice(product.price, product.currency)}</p>
              </div>
            ))}
          </div>


          <div className="flex items-center justify-between mt-4">
            <div className="text-sm text-gray-700">
              Showing {(page - 1) * PAGE_SIZE + 1} -{" "}
              {Math.min(page * PAGE_SIZE, products.length)} of{" "}
              {products.length}
            </div>
            <div className="inline-flex items-center">
              <button
                onClick={() => handlePageChange(page - 1)}
                disabled={page === 1}
                className={`px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-l-lg hover:bg-gray-100 ${page === 1 ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
              >
                <span className="sr-only">Previous</span>
                <ChevronLeft className="w-5 h-5" />
              </button>
              <span className="px-3 py-2 text-sm font-medium text-gray-700">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => handlePageChange(page + 1)}
                disabled={page === totalPages}
                className={`px-3 py-2 text-sm font-medium text-gray-500 bg-white border border-gray-300 rounded-r-lg hover:bg-gray-100 ${page === totalPages ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
              >
                <span className="sr-only">Next</span>
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default InventoryView;