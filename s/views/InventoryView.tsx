import React, { useMemo, useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { Search } from "lucide-react";

const debounce = (func: (...args: any[]) => void, delay: number) => {
  let timeout: NodeJS.Timeout | null = null;
  return (...args: any[]) => {
    if (timeout) {
      clearTimeout(timeout);
    }
    timeout = setTimeout(() => {
      func(...args);
      timeout = null;
    }, delay);
  };
};

const InventoryView: React.FC = () => {
  const { products } = useConductorCatalog();
  const { goToProduct } = useNavigationStore();
  const [searchText, setSearchText] = useState("");
  const [debouncedSearchText, setDebouncedSearchText] = useState("");
  const [sortOrder, setSortOrder] = useState<
    "inStock" | "unconfirmed" | "outOfStock" | "cfp" | null
  >(null);

  useEffect(() => {
    const handleSearch = debounce((text: string) => {
      setDebouncedSearchText(text);
    }, 300);

    handleSearch(searchText);

    return () => {
      // cleanup
    };
  }, [searchText]);

  const filteredProducts = useMemo(() => {
    let filtered = products;

    if (debouncedSearchText) {
      filtered = filtered.filter((product) =>
        product.name?.toLowerCase().includes(debouncedSearchText.toLowerCase())
      );
    }

    return filtered;
  }, [products, debouncedSearchText]);

  const sortedProducts = useMemo(() => {
    let sorted = [...filteredProducts];

    sorted.sort((a, b) => {
      const aStock = a.stock ?? null;
      const bStock = b.stock ?? null;
      const aCfp = a.price === 0 || !a.price;
      const bCfp = b.price === 0 || !b.price;

      if (sortOrder === "inStock") {
        if ((bStock ?? 0) > 0 && (aStock ?? 0) <= 0) return 1;
        if ((aStock ?? 0) > 0 && (bStock ?? 0) <= 0) return -1;
      } else if (sortOrder === "unconfirmed") {
        if (bStock === null && aStock !== null) return 1;
        if (aStock === null && bStock !== null) return -1;
      } else if (sortOrder === "outOfStock") {
        if (bStock === 0 && aStock !== 0) return 1;
        if (aStock === 0 && bStock !== 0) return -1;
      } else if (sortOrder === "cfp") {
          if (bCfp && !aCfp) return 1;
          if (aCfp && !bCfp) return -1;
      }


      if (aStock === null && bStock !== null) return 1;
      if (bStock === null && aStock !== null) return -1;
      if ((bStock ?? 0) > (aStock ?? 0)) return 1;
      if ((aStock ?? 0) > (bStock ?? 0)) return -1;

      if (bCfp && !aCfp) return 1;
      if (aCfp && !bCfp) return -1;


      return 0;
    });

    return sorted;
  }, [filteredProducts, sortOrder]);


  const handleRowClick = useCallback(
    (productId: string) => {
      goToProduct(productId);
    },
    [goToProduct]
  );


  return (
    <div className="p-4">
      <div className="mb-4 flex items-center">
        <div className="relative w-full">
          <input
            type="text"
            placeholder="Search products..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            className="w-full pr-10 py-2 pl-3 rounded-md bg-zinc-700 text-zinc-100 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors duration-200"
          />
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-zinc-400" />
          </div>
        </div>
      </div>

      <div className="mb-4 flex space-x-4">
        <button
          onClick={() => setSortOrder(sortOrder === "inStock" ? null : "inStock")}
          className={`px-3 py-2 rounded-md text-sm font-medium ${
            sortOrder === "inStock"
              ? "bg-blue-500 text-white"
              : "bg-zinc-700 text-zinc-300 hover:bg-zinc-600"
          } transition-colors duration-200`}
        >
          In Stock
        </button>
        <button
          onClick={() =>
            setSortOrder(sortOrder === "unconfirmed" ? null : "unconfirmed")
          }
          className={`px-3 py-2 rounded-md text-sm font-medium ${
            sortOrder === "unconfirmed"
              ? "bg-amber-500 text-white"
              : "bg-zinc-700 text-zinc-300 hover:bg-zinc-600"
          } transition-colors duration-200`}
        >
          Unconfirmed
        </button>
        <button
          onClick={() =>
            setSortOrder(sortOrder === "outOfStock" ? null : "outOfStock")
          }
          className={`px-3 py-2 rounded-md text-sm font-medium ${
            sortOrder === "outOfStock"
              ? "bg-red-500 text-white"
              : "bg-zinc-700 text-zinc-300 hover:bg-zinc-600"
          } transition-colors duration-200`}
        >
          Out of Stock
        </button>
        <button
            onClick={() => setSortOrder(sortOrder === "cfp" ? null : "cfp")}
            className={`px-3 py-2 rounded-md text-sm font-medium ${
                sortOrder === "cfp"
                    ? "bg-amber-500 text-white"
                    : "bg-zinc-700 text-zinc-300 hover:bg-zinc-600"
            } transition-colors duration-200`}
        >
            CfP
        </button>
      </div>


      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left text-zinc-400">
          <thead className="text-xs uppercase bg-zinc-800 text-zinc-400">
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
            </tr>
          </thead>
          <tbody>
            {sortedProducts.map((product) => {
              const isOutOfStock = product.stock === 0;
              const isUnconfirmed = product.stock === null || product.stock === undefined;
              const isCfp = product.price === 0 || !product.price;

              return (
                <tr
                  key={product.id}
                  className={`bg-zinc-900 border-b border-zinc-700 hover:bg-zinc-700 cursor-pointer ${
                    isOutOfStock ? "border-red-500" : ""
                  } ${isUnconfirmed ? "border-amber-500" : ""}`}
                  onClick={() => handleRowClick(product.id)}
                >
                  <td className="px-6 py-4">
                    {product.name}
                  </td>
                  <td className="px-6 py-4">{product.brand}</td>
                  <td className="px-6 py-4">{product.price}</td>
                  <td className="px-6 py-4 relative">
                    {isOutOfStock && (
                      <span className="absolute top-0 right-0 px-2 py-0.5 text-xs font-medium text-red-400 bg-red-900/50 rounded-full">
                        OUT OF STOCK
                      </span>
                    )}
                    {isUnconfirmed && (
                      <span className="absolute top-0 right-0 px-2 py-0.5 text-xs font-medium text-amber-400 bg-amber-900/50 rounded-full">
                        UNCONFIRMED
                      </span>
                    )}
                    {isCfp && !isOutOfStock && !isUnconfirmed && (
                        <span className="absolute top-0 right-0 px-2 py-0.5 text-xs font-medium text-amber-400 bg-amber-900/50 rounded-full">
                          CfP
                        </span>
                    )}

                    {product.stock !== null && product.stock !== undefined && product.stock > 0 && (
                        <span>In Stock</span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default InventoryView;

// frontend/src/hooks/useConductorCatalog.ts
import { useState, useEffect } from "react";

export interface ConductorProduct extends CatalogProduct {
  /**
   * Stock status from Halilit inventory (Commercial source).
   * null = unconfirmed (no data), 0 = out of stock, >0 = in stock (quantity).
   */
  stock?: number | null;
}

export const useConductorCatalog = () => {
  const { get } = useBackendApi();
  const [products, setProducts] = useState<ConductorProduct[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCatalog = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await get<ConductorProduct[]>("/api/catalog");
        setProducts(data);
      } catch (err: any) {
        setError(err.message || "Failed to fetch catalog");
      } finally {
        setIsLoading(false);
      }
    };

    fetchCatalog();
  }, [get]);

  return { products, isLoading, error };
};