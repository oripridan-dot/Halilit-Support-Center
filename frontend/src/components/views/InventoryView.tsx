import React, { useState, useEffect } from 'react';
import { useConductorCatalog, ConductorProduct } from '../../hooks/useConductorCatalog';
import { useDebounce } from '../../hooks/useDebounce';
import { navigationStore } from '../../store/navigationStore';

const InventoryView: React.FC = () => {
  const { searchQuery, initialCfpFilter } = navigationStore.getState();
  const [filterText, setFilterText] = useState<string>(searchQuery || initialCfpFilter || '');

  const debouncedFilter = useDebounce(filterText, 150);

  const { data, isLoading, error } = useConductorCatalog();

  // Sync external navigation-store search to local filter
  useEffect(() => {
    if (searchQuery) setFilterText(searchQuery);
  }, [searchQuery]);

  const products: ConductorProduct[] = data?.products ?? [];
  const filtered = debouncedFilter
    ? products.filter((p) =>
        (p.search_text ?? '').toLowerCase().includes(debouncedFilter.toLowerCase()) ||
        p.name.toLowerCase().includes(debouncedFilter.toLowerCase()) ||
        p.brand.toLowerCase().includes(debouncedFilter.toLowerCase())
      )
    : products;

  return (
    <div className="bg-zinc-900 min-h-screen p-4">
      <input
        type="text"
        placeholder="Search inventory..."
        value={filterText}
        onChange={(e) => setFilterText(e.target.value)}
        className="bg-zinc-800 text-zinc-100 placeholder-zinc-500 rounded-md p-2 w-full mb-4 outline-none focus:ring-2 focus:ring-blue-500"
      />

      {isLoading && <p className="text-zinc-400">Loading...</p>}
      {error && <p className="text-red-400">Error: {error}</p>}

      {!isLoading && !error && filtered.length === 0 && (
        <p className="text-zinc-500">No items found.</p>
      )}

      {filtered.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filtered.map((item: ConductorProduct) => (
            <div key={item.id} className="bg-zinc-800 rounded-md p-4 hover:bg-zinc-750 transition-colors">
              {item.image_url && (
                <img
                  src={item.image_url}
                  alt={item.name}
                  className="w-full h-32 object-contain mb-2 rounded"
                />
              )}
              <h3 className="text-zinc-100 font-semibold text-sm leading-tight">{item.name}</h3>
              <p className="text-zinc-400 text-xs mt-1">{item.brand}</p>
              {item.price > 0 && (
                <p className="text-blue-400 text-sm font-medium mt-2">₪{item.price.toLocaleString()}</p>
              )}
              <span
                className={`inline-block mt-2 text-xs px-2 py-0.5 rounded-full ${
                  item.data_status === 'COMPLETE'
                    ? 'bg-green-900 text-green-300'
                    : item.data_status === 'GOOD'
                    ? 'bg-blue-900 text-blue-300'
                    : 'bg-zinc-700 text-zinc-400'
                }`}
              >
                {item.data_status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default InventoryView;
