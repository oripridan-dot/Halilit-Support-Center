import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useConductorCatalog } from '../../hooks/useConductorCatalog';
import { Product, formatPrice } from '../../types';
import { PackageOpen } from 'lucide-react';
import { useNavigationStore } from '../../stores/navigationStore';
import { useDebounceValue } from '../../hooks/useDebounceValue';

interface StockBadgeProps {
  stock: number | null | undefined;
}

const StockBadge: React.FC<StockBadgeProps> = ({ stock }) => {
  if (stock === null || stock === undefined) {
    return (
      <span className="bg-zinc-500 text-zinc-900 text-xs font-medium px-2 py-1 rounded-md">
        Unknown
      </span>
    );
  }
  if (stock === 0) {
    return (
      <span className="bg-red-400 text-red-900 text-xs font-medium px-2 py-1 rounded-md">
        Out of Stock
      </span>
    );
  }
  return (
    <span className="bg-emerald-400 text-emerald-900/80 text-xs font-medium px-2 py-1 rounded-md">
      In Stock
    </span>
  );
};

const PAGE_SIZE = 50;

const InventoryView: React.FC = () => {
  const navigate = useNavigate();
  const { products, isLoading, error, refetch } = useConductorCatalog();
  const { searchQuery, initialCfpFilter, setSearchQuery } = useNavigationStore();

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

  // 1. Sync filterText from navigation store deep-link and apply debounce
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

  const filterStr = debouncedFilterText;

  const sortedProducts = useMemo(() => {
    if (!products) return [];

    const sorted = [...products].sort((a, b) => {
      const stockA = a.stock === null ? 1 : a.stock === 0 ? 2 : 0;
      const stockB = b.stock === null ? 1 : b.stock === 0 ? 2 : 0;

      if (stockA !== stockB) {
        return stockA - stockB;
      }
        
      if (a.price !== null && a.price !== undefined && b.price === null || b.price === undefined) {
        return -1;
      }
      if (b.price !== null && b.price !== undefined && a.price === null || a.price === undefined) {
        return 1;
      }

      return a.id.localeCompare(b.id);
    });
    return sorted;
  }, [products]);


  const filteredProducts = useMemo(() => {
    let filtered = sortedProducts || [];

    filtered = filtered.filter((p) => {
      const matchesSearch =
        filterStr === "" ||
        p.name.toLowerCase().includes(filterStr.toLowerCase()) ||
        p.id.toLowerCase().includes(filterStr.toLowerCase()) ||
        p.brand.toLowerCase().includes(filterStr.toLowerCase()) ||
        (p.category?.toLowerCase().includes(filterStr.toLowerCase()) ||
          p.subcategory?.toLowerCase().includes(filterStr.toLowerCase()));

      const matchesBrand = brandFilter === "" || p.brand === brandFilter;
      const matchesCategory = categoryFilter === "" || p.category === categoryFilter;
      const matchesCfp = !cfpOnly || (p.price === null || p.price === undefined || p.price === 0);

      return matchesSearch && matchesBrand && matchesCategory && matchesCfp;
    });

    return filtered;
  }, [sortedProducts, filterStr, brandFilter, categoryFilter, cfpOnly]);


  const totalPages = useMemo(() => {
    if (!products) return 1;
    return Math.ceil(filteredProducts.length / PAGE_SIZE);
  }, [filteredProducts]);

  const paginatedProducts = useMemo(() => {
    const startIndex = (page - 1) * PAGE_SIZE;
    return filteredProducts.slice(startIndex, startIndex + PAGE_SIZE);
  }, [filteredProducts, page]);

  const handleBrandFilterChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setBrandFilter(event.target.value);
  };

  const handleCategoryFilterChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setCategoryFilter(event.target.value);
  };

  const handleCfpFilterChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setCfpOnly(event.target.checked);
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


  if (error) {
    return <div>Error loading inventory: {error.message}</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Inventory Master</h1>

      <div className="mb-4 flex flex-col gap-2 md:flex-row items-center">
        <input
          type="text"
          placeholder="Search products..."
          value={filterText}
          onChange={(e) => setFilterText(e.target.value)}
          className="shadow appearance-none border rounded w-full md:w-64 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
        />
        <select
          value={brandFilter}
          onChange={handleBrandFilterChange}
          className="shadow appearance-none border rounded w-full md:w-40 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
        >
          <option value="">All Brands</option>
          {Array.from(new Set(products?.map((p) => p.brand).filter(Boolean) || [])).map(
            (brand) => (
              <option key={brand} value={brand}>
                {brand}
              </option>
            ),
          )}
        </select>
        <select
          value={categoryFilter}
          onChange={handleCategoryFilterChange}
          className="shadow appearance-none border rounded w-full md:w-40 py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
        >
          <option value="">All Categories</option>
          {Array.from(new Set(products?.map((p) => p.category).filter(Boolean) || [])).map(
            (category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ),
          )}
        </select>
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={cfpOnly}
            onChange={handleCfpFilterChange}
            className="mr-2"
          />
          Call for Price Only
        </label>
      </div>

      {isLoading ? (
        <div>Loading inventory...</div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="table-auto w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => handleSortChange("name")}>
                    Name {sortField === "name" && (sortDir === "asc" ? "▲" : "▼")}
                  </th>
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => handleSortChange("brand")}>
                    Brand {sortField === "brand" && (sortDir === "asc" ? "▲" : "▼")}
                  </th>
                  <th className="px-4 py-2 text-left">Category</th>
                  <th className="px-4 py-2 text-left">SKU</th>
                  <th className="px-4 py-2 text-left cursor-pointer" onClick={() => handleSortChange("price")}>
                    Price {sortField === "price" && (sortDir === "asc" ? "▲" : "▼")}
                  </th>
                  <th className="px-4 py-2 text-left">Stock</th>
                </tr>
              </thead>
              <tbody>
                {paginatedProducts.map((product) => (
                  <tr key={product.id} className={product.stock === 0 ? "bg-red-100" : ""}>
                    <td className="border px-4 py-2">{product.name}</td>
                    <td className="border px-4 py-2">{product.brand}</td>
                    <td className="border px-4 py-2">{product.category}</td>
                    <td className="border px-4 py-2">{product.id}</td>
                    <td className="border px-4 py-2">{formatPrice(product.price)}</td>
                    <td className="border px-4 py-2">
                      <StockBadge stock={product.stock} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 flex justify-center">
            <button
              onClick={() => handlePageChange(page - 1)}
              disabled={page === 1}
              className="px-4 py-2 mx-1 bg-gray-300 disabled:opacity-50 rounded"
            >
              Previous
            </button>
            <span>Page {page} of {totalPages}</span>
            <button
              onClick={() => handlePageChange(page + 1)}
              disabled={page === totalPages}
              className="px-4 py-2 mx-1 bg-gray-300 disabled:opacity-50 rounded"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default InventoryView;