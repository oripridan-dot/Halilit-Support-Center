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

    return products.filter(item => {
      const matchesText =
        !filterStr ||
        item.name.toLowerCase().includes(filterStr.toLowerCase()) ||
        item.id.toLowerCase().includes(filterStr.toLowerCase()) ||
        item.brand.toLowerCase().includes(filterStr.toLowerCase()) ||
        (item.category || "").toLowerCase().includes(filterStr.toLowerCase()) ||
        (item.subcategory || "").toLowerCase().includes(filterStr.toLowerCase());
      const matchesBrand = !brandFilter || item.brand === brandFilter;
      const matchesCategory = !categoryFilter || (item.category || "General") === categoryFilter || (item.subcategory || "General") === categoryFilter;
      const matchesCfp = !cfpOnly || item.price === null || item.price === 0;

      return matchesText && matchesBrand && matchesCategory && matchesCfp;
    });
  }, [products, filterStr, brandFilter, categoryFilter, cfpOnly]);

  const sortedProducts = useMemo(() => {
    const sorted = [...filteredProducts].sort((a, b) => {
      const stockA = a.stock === null ? 1 : a.stock === 0 ? 2 : 0;
      const stockB = b.stock === null ? 1 : b.stock === 0 ? 2 : 0;

      if (stockA !== stockB) {
        return stockA - stockB;
      }

      switch (sortField) {
        case "name":
          return a.name.localeCompare(b.name) * (sortDir === "asc" ? 1 : -1);
        case "id":
          return a.id.localeCompare(b.id) * (sortDir === "asc" ? 1 : -1);
        case "brand":
          return a.brand.localeCompare(b.brand) * (sortDir === "asc" ? 1 : -1);
        case "price":
          const priceA = a.price ?? Number.MAX_VALUE;
          const priceB = b.price ?? Number.MAX_VALUE;
          return (priceA - priceB) * (sortDir === "asc" ? 1 : -1);
        default:
          return 0;
      }
    });

    return sorted;
  }, [filteredProducts, sortField, sortDir]);

  const startIndex = (page - 1) * PAGE_SIZE;
  const endIndex = startIndex + PAGE_SIZE;
  const paginatedProducts = sortedProducts.slice(startIndex, endIndex);
  const totalPages = Math.max(1, Math.ceil(sortedProducts.length / PAGE_SIZE));

  const uniqueBrands = useMemo(() => {
    if (!products) return [];
    return [...new Set(products.map(p => p.brand))].sort();
  }, [products]);

  const uniqueCategories = useMemo(() => {
    if (!products) return [];
    return [...new Set(products.map(p => p.subcategory || p.category || "General"))].sort();
  }, [products]);

  const handleBrandChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setBrandFilter(e.target.value);
  };

  const handleCategoryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setCategoryFilter(e.target.value);
  };

  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const [field, dir] = e.target.value.split(":");
    setSortField(field);
    setSortDir(dir as "asc" | "desc");
  };

  const handleClearSearch = () => {
    setSearchQuery(null);
  }

  if (isLoading) {
    return (
      <div className="flex flex-col gap-4 p-4">
        <div className="flex items-center gap-2">
          <div className="h-4 w-32 bg-zinc-800 rounded animate-pulse" />
        </div>
        {[...Array(12)].map((_, i) => (
          <div key={i} className="h-12 bg-zinc-900 rounded animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-amber-100 border border-amber-400 text-amber-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Error!</strong>
        <span className="block sm:inline">{error}</span>
        <div className="absolute top-0 bottom-0 right-0 px-2 py-1">
          <button onClick={refetch} className="bg-amber-500 hover:bg-amber-700 text-white text-xs font-medium py-1 px-2 rounded">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (sortedProducts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <PackageOpen size={32} className="opacity-40" />
        <span>No products match. Adjust filters or search.</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 p-4">
      <div className="flex items-center gap-2">
        <div className="w-[240px] flex items-center gap-2 border rounded-md px-2 py-1">
          <Search size={16} className="text-zinc-500" />
          <input
            type="text"
            placeholder="Search by name, SKU or brand…"
            className="w-full bg-transparent text-sm placeholder-zinc-500 focus:outline-none"
            value={filterText}
            onChange={(e) => {
              setFilterText(e.target.value);
              if (e.target.value !== "" && searchQuery !== null) {
                handleClearSearch()
              }
            }}
          />
        </div>
        <select
          className="bg-zinc-800 text-zinc-100 text-sm rounded-md px-2 py-1 focus:outline-none"
          value={brandFilter}
          onChange={handleBrandChange}
        >
          <option value="">Brand</option>
          {uniqueBrands.map(brand => (
            <option key={brand} value={brand}>{brand}</option>
          ))}
        </select>
        <select
          className="bg-zinc-800 text-zinc-100 text-sm rounded-md px-2 py-1 focus:outline-none"
          value={categoryFilter}
          onChange={handleCategoryChange}
        >
          <option value="">Category</option>
          {uniqueCategories.map(category => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>
        <button
          aria-pressed={cfpOnly}
          className={`bg-${cfpOnly ? 'amber' : 'zinc'}-800 text-${cfpOnly ? 'amber' : 'zinc'}-100 text-sm rounded-md px-2 py-1 focus:outline-none`}
          onClick={() => setCfpOnly(!cfpOnly)}
        >
          📞 Call for Price
        </button>
        <select
          className="bg-zinc-800 text-zinc-100 text-sm rounded-md px-2 py-1 focus:outline-none"
          value={`${sortField}:${sortDir}`}
          onChange={handleSortChange}
        >
          <option value="name:asc">Name A→Z</option>
          <option value="name:desc">Name Z→A</option>
          <option value="id:asc">SKU A→Z</option>
          <option value="id:desc">SKU Z→A</option>
          <option value="brand:asc">Brand A→Z</option>
          <option value="price:asc">Price Low→High</option>
          <option value="price:desc">Price High→Low</option>
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-zinc-900 text-zinc-100">
            <tr>
              <th className="py-2 px-4">Product Name</th>
              <th className="py-2 px-4">SKU</th>
              <th className="py-2 px-4">Brand</th>
              <th className="py-2 px-4">Category</th>
              <th className="py-2 px-4">Price (IL)</th>
              <th className="py-2 px-4">Price (Eilat)</th>
              <th className="py-2 px-4">Stock</th>
            </tr>
          </thead>
          <tbody>
            {paginatedProducts.map(item => (
              <tr
                key={item.id}
                role="button"
                tabIndex={0}
                onClick={() => goToProduct(item.id)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === 'Space') {
                    goToProduct(item.id);
                  }
                }}
                className={`hover:bg-zinc-900 ${item.stock === 0 ? 'bg-red-950/10' : ''}`}
              >
                <td className="py-2 px-4">
                  <div className="flex items-center gap-2">
                    <img
                      src={item.image_url}
                      alt={item.name}
                      className="w-9 h-9 rounded object-cover"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.opacity = '0.3';
                      }}
                    />
                    <span>{item.name.substring(0, 30)}</span>
                  </div>
                </td>
                <td className="py-2 px-4">
                  <span className="font-mono">{item.id}</span>
                  {item.official_url && <Check size={16} className="inline ml-1 text-emerald-400" />}
                </td>
                <td className="py-2 px-4">{item.brand}</td>
                <td className="py-2 px-4">
                  <span className="bg-zinc-700 text-zinc-100 text-xs font-medium px-2 py-1 rounded-md">
                    {item.subcategory ?? item.category ?? "General"}
                  </span>
                </td>
                <td className="py-2 px-4">
                  {item.price === null ? (
                    <span className="bg-amber-700 text-amber-100 text-xs font-medium px-2 py-1 rounded-md">
                      CfP
                    </span>
                  ) : (
                    `₪${item.price.toFixed(2)}`
                  )}
                </td>
                <td className="py-2 px-4">
                  {item.price_eilat !== null ? `₪${item.price_eilat.toFixed(2)}` : "-"}
                </td>
                <td className="py-2 px-4">
                  <StockBadge stock={item.stock} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between text-sm">
          <span>Page {page} of {totalPages} · {sortedProducts.length} results</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(prev => Math.max(1, prev - 1))}
              disabled={page === 1}
              className="bg-zinc-800 text-zinc-100 px-2 py-1 rounded-md disabled:opacity-50"
            >
              Prev
            </button>
            <button
              onClick={() => setPage(prev => Math.min(totalPages, prev + 1))}
              disabled={page === totalPages}
              className="bg-zinc-800 text-zinc-100 px-2 py-1 rounded-md disabled:opacity-50"
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