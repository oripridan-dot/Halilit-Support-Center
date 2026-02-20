import React, { useState, useMemo, useEffect } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { LucideIcon } from "lucide-react";
import { ArrowDown, ArrowUp } from "lucide-react";

import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";
import { useNavigationStore } from "../../stores/navigationStore";
import { ConductorProduct } from "../../types";
import { EnhancedInventorySearchDebounceWithThrottleSchema } from "../../specs/contracts/enhanced_inventory_search_debounce_with_throttle.schema"; // Assuming this contract exists, adjust path if necessary

interface SortOption {
  label: string;
  value: string;
  icon?: LucideIcon;
}

const sortOptions: SortOption[] = [
  { label: "In Stock", value: "stock_asc" },
  { label: "Unconfirmed", value: "unconfirmed_asc" },
  { label: "Out of Stock", value: "out_of_stock_asc" },
  { label: "CfP", value: "cfp_asc" },
  { label: "Name (A-Z)", value: "name_asc" },
  { label: "Name (Z-A)", value: "name_desc" },
];

const InventoryView = () => {
  const { products } = useConductorCatalog();
  const [searchText, setSearchText] = useState<string>("");
  const [sort, setSort] = useState<string>("stock_asc");
  const debouncedSearchText = useDebouncedValue(searchText, 300);
  const { goToProduct } = useNavigationStore();

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchText(event.target.value);
  };

  const handleSortChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSort(event.target.value);
  };

  const filteredProducts = useMemo(() => {
    let filtered = products;

    if (debouncedSearchText) {
      filtered = filtered.filter((product) =>
        product.name.toLowerCase().includes(debouncedSearchText.toLowerCase())
      );
    }

    return filtered;
  }, [products, debouncedSearchText]);

  const sortedProducts = useMemo(() => {
    const sorted = [...filteredProducts];

    sorted.sort((a, b) => {
      if (sort === "stock_asc") {
        const stockA = a.stock === null || a.stock === undefined ? 1 : a.stock === 0 ? 2 : 0;
        const stockB = b.stock === null || b.stock === undefined ? 1 : b.stock === 0 ? 2 : 0;
        return stockA - stockB;
      } else if (sort === "unconfirmed_asc") {
        const stockA = a.stock === null || a.stock === undefined ? 0 : 2;
        const stockB = b.stock === null || b.stock === undefined ? 0 : 2;
        return stockA - stockB;
      } else if (sort === "out_of_stock_asc") {
        const stockA = a.stock === 0 ? 0 : 2;
        const stockB = b.stock === 0 ? 0 : 2;
        return stockA - stockB;
      } else if (sort === "cfp_asc") {
        const cfpA = (a.price === 0 || !a.price) ? 0 : 1;
        const cfpB = (b.price === 0 || !b.price) ? 0 : 1;
        return cfpA - cfpB;
      }
        else if (sort === "name_asc") {
            return a.name.localeCompare(b.name);
        } else if (sort === "name_desc") {
            return b.name.localeCompare(a.name);
        }
      return 0;
    });

    return sorted;
  }, [filteredProducts, sort]);


  return (
    <div className="container mx-auto py-4 dark:bg-zinc-900 dark:text-zinc-100">
      <h1 className="text-2xl font-semibold mb-4">Inventory</h1>

      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-4">
        <input
          type="text"
          placeholder="Search by name"
          value={searchText}
          onChange={handleSearchChange}
          className="dark:bg-zinc-800 dark:border-zinc-700 dark:text-zinc-100 border border-gray-300 rounded-md px-3 py-2 w-full md:w-64"
        />

        <div className="flex items-center gap-2">
          <label htmlFor="sort" className="text-sm font-medium">
            Sort by:
          </label>
          <select
            id="sort"
            value={sort}
            onChange={handleSortChange}
            className="dark:bg-zinc-800 dark:border-zinc-700 dark:text-zinc-100 border border-gray-300 rounded-md px-3 py-2"
          >
            {sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {sortedProducts.length === 0 ? (
        <div className="text-center py-8 dark:text-zinc-400">
          No products found.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg shadow-md">
          <table className="min-w-full divide-y divide-zinc-700">
            <thead className="dark:bg-zinc-800">
              <tr>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider dark:text-zinc-300"
                >
                  Name
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider dark:text-zinc-300"
                >
                  Brand
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider dark:text-zinc-300"
                >
                  Price
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider dark:text-zinc-300"
                >
                  Eilat Price
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider dark:text-zinc-300"
                >
                  Stock
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800">
              {sortedProducts.map((product) => (
                <tr
                  key={product.id}
                  className={`cursor-pointer hover:bg-zinc-800 transition-colors duration-200 ${
                    product.stock === 0
                      ? "border-red-500"
                      : product.stock === null || product.stock === undefined
                      ? "border-amber-500"
                      : ""
                  }`}
                  onClick={() => goToProduct(product.id)}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    {product.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {product.brand}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {product.price !== undefined ? product.price : "N/A"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {product.price_eilat !== undefined
                      ? product.price_eilat
                      : "N/A"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap relative">
                    {product.stock === 0 && (
                      <span className="absolute top-0 right-0 px-2 py-0.5 text-xs font-medium rounded-full bg-red-900/50 text-red-400 border border-red-700">
                        OUT OF STOCK
                      </span>
                    )}
                    {(product.stock === null || product.stock === undefined) && (
                      <span className="absolute top-0 right-0 px-2 py-0.5 text-xs font-medium rounded-full bg-amber-900/50 text-amber-400 border border-amber-700">
                        UNCONFIRMED
                      </span>
                    )}
                    {(product.price === 0 || !product.price) &&
                      (product.stock !== 0) &&
                      (product.stock !== null) &&
                      (product.stock !== undefined) && (
                        <span className="absolute top-0 right-0 px-2 py-0.5 text-xs font-medium rounded-full bg-amber-900/50 text-amber-400 border border-amber-700">
                          CfP
                        </span>
                      )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default InventoryView;

import React, { useState, useMemo, useEffect } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { LucideIcon } from "lucide-react";
import { ArrowDown, ArrowUp } from "lucide-react";

import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import { useDebouncedValue } from "../../hooks/useDebouncedValue";
import { useNavigationStore } from "../../stores/navigationStore";
import { ConductorProduct } from "../../types";
import { EnhancedInventorySearchDebounceWithThrottleSchema } from "../../specs/contracts/enhanced_inventory_search_debounce_with_throttle.schema";

interface SortOption {
  label: string;
  value: string;
  icon?: LucideIcon;
}

const sortOptions: SortOption[] = [
  { label: "In Stock", value: "stock_asc" },
  { label: "Unconfirmed", value: "unconfirmed_asc" },
  { label: "Out of Stock", value: "out_of_stock_asc" },
  { label: "CfP", value: "cfp_asc" },
  { label: "Name (A-Z)", value: "name_asc" },
  { label: "Name (Z-A)", value: "name_desc" },
];

const InventoryView = () => {
  const { products } = useConductorCatalog();
  const [searchText, setSearchText] = useState<string>("");
  const [sort, setSort] = useState<string>("stock_asc");
  const debouncedSearchText = useDebouncedValue(searchText, 300);
  const { goToProduct } = useNavigationStore();

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchText(event.target.value);
  };

  const handleSortChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSort(event.target.value);
  };

  const filteredProducts = useMemo(() => {
    let filtered = products;

    if (debouncedSearchText) {
      filtered = filtered.filter((product) =>
        product.name.toLowerCase().includes(debouncedSearchText.toLowerCase())
      );
    }

    return filtered;
  }, [products, debouncedSearchText]);

  const sortedProducts = useMemo(() => {
    const sorted = [...filteredProducts];

    sorted.sort((a, b) => {
      if (sort === "stock_asc") {
        const stockA = a.stock === null || a.stock === undefined ? 1 : a.stock === 0 ? 2 : 0;
        const stockB = b.stock === null || b.stock === undefined ? 1 : b.stock === 0 ? 2 : 0;
        return stockA - stockB;
      } else if (sort === "unconfirmed_asc") {
        const stockA = a.stock === null || a.stock === undefined ? 0 : 2;
        const stockB = b.stock === null || b.stock === undefined ? 0 : 2;
        return stockA - stockB;
      } else if (sort === "out_of_stock_asc") {
        const stockA = a.stock === 0 ? 0 : 2;
        const stockB = b.stock === 0 ? 0 : 2;
        return stockA - stockB;
      } else if (sort === "cfp_asc") {
        const cfpA = (a.price === 0 || !a.price) ? 0 : 1;
        const cfpB = (b.price === 0 || !b.price) ? 0 : 1;
        return cfpA - cfpB;
      }
        else if (sort === "name_asc") {
            return a.name.localeCompare(b.name);
        } else if (sort === "name_desc") {
            return b.name.localeCompare(a.name);
        }
      return 0;
    });

    return sorted;
  }, [filteredProducts, sort]);


  return (
    <div className="container mx-auto py-4 dark:bg-zinc-900 dark:text-zinc-100">
      <h1 className="text-2xl font-semibold mb-4">Inventory</h1>

      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-4">
        <input
          type="text"
          placeholder="Search by name"
          value={searchText}
          onChange={handleSearchChange}
          className="dark:bg-zinc-800 dark:border-zinc-700 dark:text-zinc-100 border border-gray-300 rounded-md px-3 py-2 w-full md:w-64"
        />

        <div className="flex items-center gap-2">
          <label htmlFor="sort" className="text-sm font-medium">
            Sort by:
          </label>
          <select
            id="sort"
            value={sort}
            onChange={handleSortChange}
            className="dark:bg-zinc-800 dark:border-zinc-700 dark:text-zinc-100 border border-gray-300 rounded-md px-3 py-2"
          >
            {sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {sortedProducts.length === 0 ? (
        <div className="text-center py-8 dark:text-zinc-400">
          No products found.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg shadow-md">
          <table className="min-w-full divide-y divide-zinc-700">
            <thead className="dark:bg-zinc-800">
              <tr>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider dark:text-zinc-300"
                >
                  Name
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider dark:text-zinc-300"
                >
                  Brand
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider dark:text-zinc-300"
                >
                  Price
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider dark:text-zinc-300"
                >
                  Eilat Price
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider dark:text-zinc-300"
                >
                  Stock
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800">
              {sortedProducts.map((product) => (
                <tr
                  key={product.id}
                  className={`cursor-pointer hover:bg-zinc-800 transition-colors duration-200 ${
                    product.stock === 0
                      ? "border-red-500"
                      : product.stock === null || product.stock === undefined
                      ? "border-amber-500"
                      : ""
                  }`}
                  onClick={() => goToProduct(product.id)}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    {product.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {product.brand}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {product.price !== undefined ? product.price : "N/A"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {product.price_eilat !== undefined
                      ? product.price_eilat
                      : "N/A"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap relative">
                    {product.stock === 0 && (
                      <span className="absolute top-0 right-0 px-2 py-0.5 text-xs font-medium rounded-full bg-red-900/50 text-red-400 border border-red-700">
                        OUT OF STOCK
                      </span>
                    )}
                    {(product.stock === null || product.stock === undefined) && (
                      <span className="absolute top-0 right-0 px-2 py-0.5 text-xs font-medium rounded-full bg-amber-900/50 text-amber-400 border border-amber-700">
                        UNCONFIRMED
                      </span>
                    )}
                    {(product.price === 0 || !product.price) &&
                      (product.stock !== 0) &&
                      (product.stock !== null) &&
                      (product.stock !== undefined) && (
                        <span className="absolute top-0 right-0 px-2 py-0.5 text-xs font-medium rounded-full bg-amber-900/50 text-amber-400 border border-amber-700">
                          CfP
                        </span>
                      )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default InventoryView;