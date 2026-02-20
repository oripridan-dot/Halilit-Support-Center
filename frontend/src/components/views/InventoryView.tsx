import React, { useState, useEffect } from 'react';
import { useConductorCatalog } from '../../hooks/useConductorCatalog';
import { useDebounce } from '../../hooks/useDebounce';
import { InventoryItem, InventorySearchResponse } from '../../specs/contracts/enhanced_inventory_search_debounce_with_throttle.schema';
import { navigationStore } from '../../stores/navigationStore';

interface InventoryViewProps {}

const InventoryView: React.FC<InventoryViewProps> = () => {
  const [filterText, setFilterText] = useState<string>('');
  const debouncedFilterText = useDebounce(filterText, 150);
  const { initialCfpFilter, searchQuery } = navigationStore.getState();

  const { data, isLoading, isError } = useConductorCatalog({
    searchQuery: debouncedFilterText,
  });

  useEffect(() => {
    if (searchQuery) {
      setFilterText(searchQuery);
    } else if (initialCfpFilter) {
      setFilterText(initialCfpFilter);
    }
  }, []);

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFilterText(event.target.value);
  };


  return (
    <div className="bg-zinc-900 min-h-screen p-4">
      <input
        type="text"
        placeholder="Search..."
        value={filterText}
        onChange={handleSearchChange}
        className="dark:bg-zinc-800 dark:text-zinc-100 rounded-md p-2 w-full mb-4"
      />

      {isLoading && <p className="text-zinc-400">Loading...</p>}
      {isError && <p className="text-red-500">Error loading inventory.</p>}

      {data && data.items && data.items.length === 0 && !isLoading && !isError && (
        <p className="text-zinc-400">No items found.</p>
      )}

      {data && data.items && data.items.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {data.items.map((item: InventoryItem) => (
            <div key={item.id} className="dark:bg-zinc-800 rounded-md p-4">
              <h3 className="text-zinc-100 font-semibold">{item.name}</h3>
              <p className="text-zinc-400">{item.description}</p>
              <p className="text-zinc-400">SKU: {item.sku}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default InventoryView;