import React, { useState, useEffect, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useDebounceValue } from "../../hooks/useDebounceValue";
import { CheckCircleIcon, XCircleIcon } from "lucide-react";
import { useNavigationStore } from "../../store/navigationStore";
import { ConductorProduct } from "../../types";
import { fetchProducts } from "../../api/products";

const InventoryView: React.FC = () => {
  const { initialCfpFilter, searchQuery, goToProduct } = useNavigationStore();
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [debouncedSearchTerm] = useDebounceValue(searchTerm, 150);

  useEffect(() => {
    if (searchQuery) {
      setSearchTerm(searchQuery);
    }
  }, [searchQuery]);

  const {
    data: products,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ["products", debouncedSearchTerm],
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

      return (a.id || "").localeCompare(b.id || "");
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
      <div className="flex items-center justify-center h-full">Loading...</div>
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
        className="w-full p-2 mb-4 text-zinc-900 bg-zinc-100 rounded-md dark:bg-zinc-700 dark:text-zinc-100"
      />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
        {sortedProducts.map((product) => (
          <div
            key={product.id}
            className="relative p-4 border rounded-md dark:border-zinc-700 hover:shadow-md transition duration-200 ease-in-out dark:bg-zinc-800"
            onClick={() => goToProduct(product.id)}
          >
            {renderStockStatus(product)}
            {renderCallForPrice(product)}
            <img
              src={product.image_url}
              alt={product.name}
              className="w-full h-40 object-contain mb-2"
            />
            <h3 className="text-zinc-100 font-semibold truncate">{product.name}</h3>
            <p className="text-zinc-400 text-sm truncate">{product.description_short}</p>
            <div className="mt-2 flex items-center justify-between">
              <span className="text-zinc-100 font-bold">${product.price}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default InventoryView;