import React, { useState, useEffect } from 'react';
import { useDebounce } from './useDebounce';
import { useThrottle } from './useThrottle';
import { Loader2, XCircle } from 'lucide-react';
import { INVENTORY_SEARCH_ENDPOINT } from '../specs/contracts/enhanced_inventory_search_debounce_with_throttle.schema';
import { InventorySearchRequest, InventorySearchResponse, InventoryItem } from '../specs/contracts/enhanced_inventory_search_debounce_with_throttle.schema';

interface InventorySearchProps {
}

const InventorySearch: React.FC<InventorySearchProps> = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState('');
  const [throttledSearchQuery, setThrottledSearchQuery] = useState('');
  const [inventoryItems, setInventoryItems] = useState<InventoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const debounceDelay = 300;
  const throttleInterval = 500;

  useDebounce(
    () => {
      setDebouncedSearchQuery(searchQuery);
    },
    debounceDelay,
    [searchQuery]
  );

  useThrottle(
    () => {
      setThrottledSearchQuery(debouncedSearchQuery);
    },
    throttleInterval,
    [debouncedSearchQuery]
  );

  useEffect(() => {
    const fetchData = async () => {
      if (!throttledSearchQuery) {
        setInventoryItems([]);
        setError(null);
        return;
      }

      setIsLoading(true);
      setError(null);

      const requestBody: InventorySearchRequest = {
        query: throttledSearchQuery,
      };

      try {
        const response = await fetch(
          `${INVENTORY_SEARCH_ENDPOINT}?query=${encodeURIComponent(throttledSearchQuery)}`,
          {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data: InventorySearchResponse = await response.json();
        setInventoryItems(data.items);
      } catch (error: any) {
        setError(error.message || 'Error fetching inventory items.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [throttledSearchQuery]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
  };

  const handleClear = () => {
    setSearchQuery('');
    setInventoryItems([]);
    setError(null);
  };

  return (
    <div className="dark:bg-zinc-900 p-4 rounded-lg shadow-md">
      <div className="relative">
        <input
          type="text"
          placeholder="Search inventory..."
          value={searchQuery}
          onChange={handleInputChange}
          className="dark:bg-zinc-800 dark:text-zinc-100 placeholder-zinc-400 w-full rounded-md py-2 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        {searchQuery && (
          <button
            onClick={handleClear}
            className="absolute inset-y-0 right-0 pr-3 flex items-center"
          >
            <XCircle size={20} className="dark:text-zinc-400 hover:dark:text-zinc-100" />
          </button>
        )}
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-4">
          <Loader2 className="animate-spin h-6 w-6 dark:text-zinc-400" />
        </div>
      )}

      {error && (
        <div className="text-red-500 py-4">
          {error}
        </div>
      )}

      {!isLoading && !error && inventoryItems.length === 0 && throttledSearchQuery && (
        <div className="py-4 text-zinc-400">
          No items found.
        </div>
      )}

      {!isLoading && !error && inventoryItems.length > 0 && (
        <ul className="mt-2">
          {inventoryItems.map((item) => (
            <li key={item.id} className="dark:text-zinc-100 py-2 border-b dark:border-zinc-700 last:border-none">
              <div className="font-semibold">{item.name}</div>
              <div>{item.description}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default InventorySearch;