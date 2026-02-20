import React, { useState, useEffect } from 'react';
import { useConductorCatalog } from './hooks/useConductorCatalog';
import { useDebounceValue } from './hooks/useDebounceValue';
import { InventoryItem } from '../../specs/contracts/enhanced_inventory_search_debounce_with_throttle.schema';
import { useNavigationStore } from './stores/navigationStore';

interface InventoryViewProps {
  // No props needed
}

const InventoryView: React.FC<InventoryViewProps> = () => {
  const [filterText, setFilterText] = useState('');
  const debouncedFilterText = useDebounceValue(filterText, 150);
  const { initialCfpFilter, searchQuery } = useNavigationStore();
  const { data, isLoading, error } = useConductorCatalog({
    searchQuery: debouncedFilterText,
    initialCfpFilter,
  });

  useEffect(() => {
    setFilterText(searchQuery || '');
  }, [searchQuery]);

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFilterText(event.target.value);
  };

  return (
    <div className="dark:bg-zinc-900 min-h-screen p-4">
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search inventory..."
          value={filterText}
          onChange={handleInputChange}
          className="dark:bg-zinc-800 dark:text-zinc-100 rounded-md p-2 w-full"
        />
      </div>

      {isLoading && <p className="dark:text-zinc-300">Loading...</p>}
      {error && <p className="dark:text-red-500">Error: {error.message}</p>}

      {data && data.items && data.items.length === 0 && !isLoading && !error && (
        <p className="dark:text-zinc-300">No items found.</p>
      )}

      {data && data.items && data.items.length > 0 && !isLoading && !error && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {data.items.map((item: InventoryItem) => (
            <div key={item.id} className="dark:bg-zinc-800 rounded-md p-4">
              <h3 className="dark:text-zinc-100 font-semibold">{item.name}</h3>
              <p className="dark:text-zinc-400">{item.description}</p>
              <p className="dark:text-zinc-400">SKU: {item.sku}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default InventoryView;