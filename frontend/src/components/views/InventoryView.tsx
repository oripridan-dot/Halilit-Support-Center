import React, { useState, useEffect, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import { Product, formatPrice } from "../../types";
import { PackageOpen } from "lucide-react";
import { useNavigationStore } from "../../store/navigationStore";
import { useDebounceValue } from "../../hooks/useDebounceValue";
import {
  Check,
  ChevronDown,
  ChevronRight,
  ChevronsUpDown,
  Package,
  Search,
} from "lucide-react";

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
  const { searchQuery, initialCfpFilter, setSearchQuery, goToProduct } =
    useNavigationStore();

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

  const filterStr =
    typeof debouncedFilterText === "string" ? debouncedFilterText : "";

  const filteredProducts = useMemo(() => {
    if (!products) return [];

    let filtered = products.filter((item) => {
      const matchesText =
        !filterStr ||
        item.name.toLowerCase().includes(filterStr.toLowerCase()) ||
        (item.brand &&
          item.brand.toLowerCase().includes(filterStr.toLowerCase()));

      const matchesBrand = !brandFilter || item.brand === brandFilter;
      const matchesCategory = !categoryFilter || item.category === categoryFilter;
      const matchesCfp = !cfpOnly || item.contextual_data?.cfp === "yes";

      return matchesText && matchesBrand && matchesCategory && matchesCfp;
    });

    const sortProducts = (a: Product, b: Product) => {
      const dir = sortDir === "asc" ? 1 : -1;
      if (sortField === "name") {
        return a.name.localeCompare(b.name) * dir;
      }
      if (sortField === "price") {
        return (a.price - b.price) * dir;
      }
      return 0;
    };

    filtered = [...filtered].sort(sortProducts);

    const startIndex = (page - 1) * PAGE_SIZE;
    const endIndex = startIndex + PAGE_SIZE;
    return filtered.slice(startIndex, endIndex);
  }, [
    products,
    filterStr,
    brandFilter,
    categoryFilter,
    cfpOnly,
    sortField,
    sortDir,
    page,
  ]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFilterText(e.target.value);
  };

  if (error) {
    return <div>Error loading inventory</div>;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Inventory Master</h1>

      <div className="mb-4 flex items-center space-x-4">
        <div className="flex items-center border rounded-md p-2 w-64">
          <Search className="h-4 w-4 mr-2 text-gray-400" />
          <input
            type="text"
            placeholder="Search products..."
            className="w-full outline-none"
            value={filterText}
            onChange={handleSearchChange}
          />
        </div>

        <div>
          <label htmlFor="brandFilter" className="mr-2">
            Brand:
          </label>
          <select
            id="brandFilter"
            value={brandFilter}
            onChange={(e) => setBrandFilter(e.target.value)}
            className="border rounded-md px-2 py-1"
          >
            <option value="">All</option>
            {/* Replace with actual brand options */}
            <option value="Roland">Roland</option>
            <option value="Fender">Fender</option>
          </select>
        </div>

        <div>
          <label htmlFor="categoryFilter" className="mr-2">
            Category:
          </label>
          <select
            id="categoryFilter"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="border rounded-md px-2 py-1"
          >
            <option value="">All</option>
            {/* Replace with actual category options */}
            <option value="Guitar">Guitar</option>
            <option value="Keyboard">Keyboard</option>
          </select>
        </div>

        <label className="flex items-center">
          <input
            type="checkbox"
            checked={cfpOnly}
            onChange={(e) => setCfpOnly(e.target.checked)}
            className="mr-2"
          />
          CFP Only
        </label>
      </div>

      <div className="mb-4 flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => {
              setSortField("name");
              setSortDir(sortDir === "asc" ? "desc" : "asc");
            }}
            className="flex items-center px-2 py-1 border rounded-md"
          >
            Name
            {sortField === "name" &&
              (sortDir === "asc" ? (
                <ChevronDown className="w-4 h-4 ml-1" />
              ) : (
                <ChevronRight className="w-4 h-4 ml-1 rotate-180" />
              ))}
          </button>
          <button
            onClick={() => {
              setSortField("price");
              setSortDir(sortDir === "asc" ? "desc" : "asc");
            }}
            className="flex items-center px-2 py-1 border rounded-md"
          >
            Price
            {sortField === "price" &&
              (sortDir === "asc" ? (
                <ChevronDown className="w-4 h-4 ml-1" />
              ) : (
                <ChevronRight className="w-4 h-4 ml-1 rotate-180" />
              ))}
          </button>
        </div>
      </div>

      {isLoading && <div>Loading...</div>}

      {products && !isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredProducts.map((product) => (
            <div
              key={product.id}
              className="border rounded-md p-4 hover:shadow-md cursor-pointer"
              onClick={() => goToProduct(product.id)}
            >
              <img
                src={product.image_url}
                alt={product.name}
                className="w-full h-48 object-contain mb-2"
              />
              <h3 className="text-lg font-medium mb-1">{product.name}</h3>
              <p className="text-gray-600 mb-2">{product.brand}</p>
              <div className="flex items-center justify-between">
                <div>{formatPrice(product.price)}</div>
                <StockBadge stock={product.specs?.stock} />
              </div>
            </div>
          ))}
        </div>
      )}

      {products && !isLoading && filteredProducts.length === 0 && (
        <div>No products found.</div>
      )}

      {products && !isLoading && filteredProducts.length > 0 && (
        <div className="mt-4 flex justify-center">
          <button
            onClick={() => setPage(page - 1)}
            disabled={page === 1}
            className="px-4 py-2 mr-2 border rounded-md disabled:opacity-50"
          >
            Previous
          </button>
          <span>Page {page}</span>
          <button
            onClick={() => {
              if (products && products.length > page * PAGE_SIZE) {
                setPage(page + 1);
              }
            }}
            disabled={!products || products.length <= page * PAGE_SIZE}
            className="px-4 py-2 ml-2 border rounded-md disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default InventoryView;