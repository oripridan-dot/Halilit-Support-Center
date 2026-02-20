import React, { useState, useEffect, useRef } from 'react';
import { useQuery } from 'react-query';
import { InventorySearchRequest, InventorySearchResponse, InventoryItem, INVENTORY_SEARCH_ENDPOINT } from '../../specs/contracts/enhanced_inventory_search_debounce_with_throttle.schema';
import { useDebouncedValue } from '../../hooks/useDebouncedValue';
import { useNavigationStore } from '../../stores/navigationStore';

interface UseThrottledValueProps<T> {
  value: T;
  delay: number;
}

const useThrottledValue = <T>({ value, delay }: UseThrottledValueProps<T>): T => {
  const [throttledValue, setThrottledValue] = useState<T>(value);
  const lastExecuted = useRef<number>(0);

  useEffect(() => {
    const now = Date.now();
    if (now - lastExecuted.current >= delay) {
      lastExecuted.current = now;
      setThrottledValue(value);
    } else {
      const timeoutId = setTimeout(() => {
        lastExecuted.current = Date.now();
        setThrottledValue(value);
      }, delay - (now - lastExecuted.current));
      return () => clearTimeout(timeoutId);
    }
  }, [value, delay]);

  return throttledValue;
};


const fetchInventory = async (params: InventorySearchRequest): Promise<InventorySearchResponse> => {
    const url = `${INVENTORY_SEARCH_ENDPOINT}`;
    const queryParams = new URLSearchParams(params).toString();
    const response = await fetch(`${url}?${queryParams}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
};

const InventoryView = () => {
    const [filterText, setFilterText] = useState<string>('');
    const { searchQuery: initialSearchQuery, initialCfpFilter } = useNavigationStore();
    const [cfpFilter, setCfpFilter] = useState<boolean>(initialCfpFilter || false);

    const debouncedFilterText = useDebouncedValue(filterText, 150);
    const throttledFilterText = useThrottledValue({ value: debouncedFilterText, delay: 300 });

    const { data: inventoryData, isLoading, isError, error } = useQuery<InventorySearchResponse, Error>(
        ['inventory', throttledFilterText, cfpFilter],
        () => fetchInventory({ searchQuery: throttledFilterText, cfpFilter }),
        {
            enabled: true,
        }
    );

    useEffect(() => {
        if (initialSearchQuery && !filterText) {
            setFilterText(initialSearchQuery);
        }
    }, [initialSearchQuery, filterText]);


    return (
        <div className="bg-slate-900 min-h-screen p-4">
            <input
                type="text"
                placeholder="Search by SKU, Brand, or Name..."
                value={filterText}
                onChange={(e) => setFilterText(e.target.value)}
                className="bg-slate-800 text-zinc-300 border border-zinc-700 rounded px-4 py-2 w-full mb-4"
            />
            <div className="flex items-center mb-4">
                <label htmlFor="cfpFilter" className="text-zinc-200 mr-2">
                    Call for Price Only
                </label>
                <input
                    type="checkbox"
                    id="cfpFilter"
                    checked={cfpFilter}
                    onChange={(e) => setCfpFilter(e.target.checked)}
                    className="mr-2"
                />
            </div>

            {isLoading && <p className="text-zinc-200">Loading...</p>}
            {isError && <p className="text-red-500">Error: {error?.message}</p>}
            {!isLoading && !isError && inventoryData && (
                <div className="overflow-x-auto">
                    <table className="table-auto w-full">
                        <thead>
                            <tr className="bg-slate-700">
                                <th className="px-4 py-2 text-left text-zinc-200">SKU</th>
                                <th className="px-4 py-2 text-left text-zinc-200">Product Name</th>
                                <th className="px-4 py-2 text-left text-zinc-200">Brand</th>
                                <th className="px-4 py-2 text-left text-zinc-200">Price</th>
                                <th className="px-4 py-2 text-left text-zinc-200">Stock Level</th>
                            </tr>
                        </thead>
                        <tbody>
                            {inventoryData.items.map((product) => (
                                <tr key={product.id} className="bg-slate-900">
                                    <td className="px-4 py-2 text-zinc-200">{product.sku}</td>
                                    <td className="px-4 py-2 text-zinc-200">{product.name}</td>
                                    <td className="px-4 py-2 text-zinc-200">{product.description}</td>
                                    <td className="px-4 py-2 text-zinc-200">{product.price}</td>
                                    <td className="px-4 py-2 text-zinc-200">{product.stock}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
            {inventoryData && inventoryData.items.length === 0 && !isLoading && !isError && (
                <p className="text-zinc-200">No products found.</p>
            )}
        </div>
    );
};

export default InventoryView;