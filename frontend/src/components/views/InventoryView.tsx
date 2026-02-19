import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useConductorCatalog } from '../../hooks/useConductorCatalog';
import { Product, formatPrice } from '../../types';
import { PackageOpen } from 'lucide-react';
import { useNavigationStore } from '../../stores/navigationStore';

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
    let filtered = products || [];

    filtered = filtered.filter((p) => {
      const matchesSearch =
        filterStr === "" ||
        p.name.toLowerCase().includes(filterStr.toLowerCase()) ||
        p.id.toLowerCase().includes(filterStr.toLowerCase()) ||
        p.brand.toLowerCase().includes(filterStr.toLowerCase()) ||
        (p.category?.toLowerCase().includes(filterStr.toLowerCase()) ||
          p.subcategory?.toLowerCase().includes(filterStr.toLowerCase()));

      const matchesBrand = brandFilter === "" || p.brand === brandFilter;
      const matchesCategory =
        categoryFilter === "" || (p.category || "General") === categoryFilter;
      const matchesCfp = cfpOnly ? p.price === null || p.price === 0 : true;

      return matchesSearch && matchesBrand && matchesCategory && matchesCfp;
    });

    return filtered;
  }, [products, filterStr, brandFilter, categoryFilter, cfpOnly]);

  const sortedProducts = useMemo(() => {
    const sorted = [...filteredProducts];

    sorted.sort((a, b) => {
      let valueA: string | number | null = "";
      let valueB: string | number | null = "";

      switch (sortField) {
        case "name":
        case "id":
        case "brand":
          valueA = a[sortField] || "";
          valueB = b[sortField] || "";
          return valueA.localeCompare(valueB);
        case "price":
          valueA = a.price ?? Number.MAX_VALUE;
          valueB = b.price ?? Number.MAX_VALUE;
          return valueA - valueB;
        default:
          return 0;
      }
    });

    if (sortDir === "desc") {
      sorted.reverse();
    }

    return sorted;
  }, [filteredProducts, sortField, sortDir]);

  const goToProduct = (productId: string) => {
    navigate(`/product/${productId}`);
    // No need to set activeProductId in navigationStore here.  Handled by the product detail view
  };

  const totalPages = Math.max(1, Math.ceil(sortedProducts.length / PAGE_SIZE));
  const startIndex = (page - 1) * PAGE_SIZE;
  const endIndex = startIndex + PAGE_SIZE;
  const paginatedProducts = sortedProducts.slice(startIndex, endIndex);

  const uniqueBrands = useMemo(() => {
    if (!products) return [];
    const brands = [...new Set(products.map((p) => p.brand))];
    return brands.sort();
  }, [products]);

  const uniqueCategories = useMemo(() => {
    if (!products) return [];
    const categories = [
      ...new Set(
        products.map((p) => p.subcategory ?? p.category ?? "General"),
      ),
    ];
    return categories.sort();
  }, [products]);


  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <div className="bg-bg-elevated p-4 shadow-md flex items-center gap-4">
        <label className="text-sm text-text-secondary">
          {sortedProducts.length} results
        </label>
        <input
          type="text"
          placeholder="Search by name, SKU or brand…"
          className="w-60 px-2 py-1 rounded-md text-sm bg-zinc-700/50 text-text-primary focus:outline-none"
          value={filterText}
          onChange={(e) => {
            setFilterText(e.target.value);
            if (searchQuery !== null) setSearchQuery(null);
          }}
        />
        <select
          className="px-2 py-1 rounded-md text-sm bg-zinc-700/50 text-text-primary focus:outline-none"
          value={brandFilter}
          onChange={(e) => setBrandFilter(e.target.value)}
        >
          <option value="">Brand</option>
          {uniqueBrands.map((brand) => (
            <option key={brand} value={brand}>
              {brand}
            </option>
          ))}
        </select>
        <select
          className="px-2 py-1 rounded-md text-sm bg-zinc-700/50 text-text-primary focus:outline-none"
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
        >
          <option value="">Category</option>
          {uniqueCategories.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
        <button
          aria-pressed={cfpOnly}
          className={`px-2 py-1 rounded-md text-sm focus:outline-none ${
            cfpOnly
              ? "bg-amber-500 text-gray-900"
              : "bg-zinc-700/50 text-text-primary"
          }`}
          onClick={() => setCfpOnly(!cfpOnly)}
        >
          Call for Price
        </button>
        <select
          className="px-2 py-1 rounded-md text-sm bg-zinc-700/50 text-text-primary focus:outline-none"
          value={`${sortField}:${sortDir}`}
          onChange={(e) => {
            const [field, direction] = e.target.value.split(":");
            setSortField(field);
            setSortDir(direction);
          }}
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

      {/* Loading state */}
      {isLoading && (
        <div className="flex-1 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 p-4">
          <div className="rounded-lg shadow-md bg-zinc-900 p-4 animate-pulse">
            <div className="h-32 bg-zinc-800 rounded-md mb-4"></div>
            <div className="h-4 w-32 bg-zinc-800 rounded-md mb-2"></div>
            <div className="h-4 w-24 bg-zinc-800 rounded-md"></div>
          </div>
          <div className="rounded-lg shadow-md bg-zinc-900 p-4 animate-pulse">
            <div className="h-32 bg-zinc-800 rounded-md mb-4"></div>
            <div className="h-4 w-32 bg-zinc-800 rounded-md mb-2"></div>
            <div className="h-4 w-24 bg-zinc-800 rounded-md"></div>
          </div>
          <div className="rounded-lg shadow-md bg-zinc-900 p-4 animate-pulse">
            <div className="h-32 bg-zinc-800 rounded-md mb-4"></div>
            <div className="h-4 w-32 bg-zinc-800 rounded-md mb-2"></div>
            <div className="h-4 w-24 bg-zinc-800 rounded-md"></div>
          </div>
          <div className="rounded-lg shadow-md bg-zinc-900 p-4 animate-pulse">
            <div className="h-32 bg-zinc-800 rounded-md mb-4"></div>
            <div className="h-4 w-32 bg-zinc-800 rounded-md mb-2"></div>
            <div className="h-4 w-24 bg-zinc-800 rounded-md"></div>
          </div>
          <div className="rounded-lg shadow-md bg-zinc-900 p-4 animate-pulse">
            <div className="h-32 bg-zinc-800 rounded-md mb-4"></div>
            <div className="h-4 w-32 bg-zinc-800 rounded-md mb-2"></div>
            <div className="h-4 w-24 bg-zinc-800 rounded-md"></div>
          </div>
          <div className="rounded-lg shadow-md bg-zinc-900 p-4 animate-pulse">
            <div className="h-32 bg-zinc-800 rounded-md mb-4"></div>
            <div className="h-4 w-32 bg-zinc-800 rounded-md mb-2"></div>
            <div className="h-4 w-24 bg-zinc-800 rounded-md"></div>
          </div>
          <div className="rounded-lg shadow-md bg-zinc-900 p-4 animate-pulse">
            <div className="h-32 bg-zinc-800 rounded-md mb-4"></div>
            <div className="h-4 w-32 bg-zinc-800 rounded-md mb-2"></div>
            <div className="h-4 w-24 bg-zinc-800 rounded-md"></div>
          </div>
          <div className="rounded-lg shadow-md bg-zinc-900 p-4 animate-pulse">
            <div className="h-32 bg-zinc-800 rounded-md mb-4"></div>
            <div className="h-4 w-32 bg-zinc-800 rounded-md mb-2"></div>
            <div className="h-4 w-24 bg-zinc-800 rounded-md"></div>
          </div>
        </div>
      )}

      {/* Error state */}
      {error && !isLoading && (
        <div className="flex-1 flex items-center justify-center p-4">
          <div className="bg-amber-100 border border-amber-400 text-amber-700 px-4 py-3 rounded relative">
            <strong className="font-bold">Error!</strong>
            <span className="block sm:inline">{error}</span>
            <button
              className="absolute top-0 right-0 p-2"
              onClick={refetch}
            >
              Retry
            </button>
            <button
              className="absolute bottom-0 right-0 p-2"
            >
              Ingestion Status
            </button>
          </div>
        </div>
      )}

      {/* Empty state */}
      {!isLoading && !error && sortedProducts.length === 0 && (
        <div className="flex-1 flex flex-col items-center justify-center p-4">
          <PackageOpen size={32} className="opacity-40" />
          <span className="opacity-60">
            No products match. Adjust filters or search.
          </span>
        </div>
      )}

      {/* Product grid */}
      {!isLoading && !error && sortedProducts.length > 0 && (
        <div className="flex-1 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 p-4">
          {paginatedProducts.map((item) => (
            <div
              key={item.id}
              role="button"
              tabIndex={0}
              className={`relative rounded-lg shadow-md bg-bg-elevated p-4 hover:bg-zinc-800 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                item.stock === 0 ? "bg-red-950/10" : ""
              }`}
              onClick={() => goToProduct(item.id)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === 'Space') {
                  goToProduct(item.id);
                }
              }}
            >
              {/* Stock badge */}
              <StockBadge stock={item.stock} />

              <div className="flex items-center justify-center h-24 mb-4">
                {/* Placeholder for product image */}
                <div className="w-20 h-20 bg-gray-200 rounded-md"></div>
              </div>
              <h3 className="text-lg font-medium text-text-primary truncate">
                {item.name}
              </h3>
              <p className="text-text-tertiary text-sm truncate">{item.brand}</p>
              <p className="text-text-tertiary text-sm truncate">
                {item.subcategory ?? item.category ?? "General"}
              </p>
              <div className="flex items-center justify-between">
                {item.price === null || item.price === undefined ? (
                  <span className="text-amber-500 font-medium">Call for Price</span>
                ) : (
                  <p className="text-text-primary font-medium">
                    {formatPrice(item)}
                  </p>
                )}
                {item.official_url && (
                    <span className="text-green-500 text-xs">●</span>
                )}
                {item.price_eilat !== null && item.price_eilat !== undefined && (
                  <span>
                    {formatPrice({ ...item, price: item.price_eilat })}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination footer */}
      {!isLoading && !error && totalPages > 1 && (
        <div className="bg-bg-elevated p-4 text-sm text-text-secondary flex items-center justify-between">
          <span>
            Page {page} of {totalPages} · {sortedProducts.length} results
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((prev) => Math.max(1, prev - 1))}
              disabled={page === 1}
              className="px-2 py-1 rounded-md bg-zinc-700/50 disabled:opacity-50"
            >
              Prev
            </button>
            <button
              onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
              disabled={page === totalPages}
              className="px-2 py-1 rounded-md bg-zinc-700/50 disabled:opacity-50"
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