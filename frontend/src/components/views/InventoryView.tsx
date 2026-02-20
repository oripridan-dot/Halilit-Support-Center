import React, { useState, useEffect, useRef } from 'react';
import { useDebouncedValue } from '../../../hooks/useDebouncedValue';
import { useConductorCatalog } from '../../../hooks/useConductorCatalog';
import { InventorySearchRequest, InventorySearchResponse, INVENTORY_SEARCH_ENDPOINT } from '../../../specs/contracts/enhanced_inventory_search_debounce_with_throttle.schema';
import { XCircle } from 'lucide-react';
import { useNavigationStore } from '../../../stores/navigationStore';

const InventoryView: React.FC = () => {
    const [filterText, setFilterText] = useState<string>('');
    const debouncedFilterText = useDebouncedValue(filterText, 150);
    const { initialCfpFilter, searchQuery, updateSearchQuery } = useNavigationStore();
    const [throttledSearchQuery, setThrottledSearchQuery] = useState<string | undefined>(searchQuery);
    const throttleRef = useRef<NodeJS.Timeout | null>(null);
    const lastApiCallTime = useRef<number>(0);

    const { data, isLoading, isError, error } = useConductorCatalog<InventorySearchResponse>(
        INVENTORY_SEARCH_ENDPOINT,
        {
            searchQuery: throttledSearchQuery,
        },
        {
            enabled: !!throttledSearchQuery,
        }
    );

    useEffect(() => {
        const now = Date.now();
        const timeSinceLastCall = now - lastApiCallTime.current;

        if (throttleRef.current) {
            clearTimeout(throttleRef.current);
        }

        if (timeSinceLastCall >= 300) {
            setThrottledSearchQuery(debouncedFilterText);
            lastApiCallTime.current = now;
        } else {
            throttleRef.current = setTimeout(() => {
                setThrottledSearchQuery(debouncedFilterText);
                lastApiCallTime.current = Date.now();
            }, 300 - timeSinceLastCall);
        }

        return () => {
            if (throttleRef.current) {
                clearTimeout(throttleRef.current);
            }
        };
    }, [debouncedFilterText]);


    useEffect(() => {
        if (searchQuery) {
            setFilterText(searchQuery);
        }
    }, [searchQuery]);


    useEffect(() => {
        if (initialCfpFilter) {
            // Apply CFP filter logic here if needed. For now, it's just a placeholder.
        }
    }, [initialCfpFilter]);


    const handleClear = () => {
        setFilterText('');
        updateSearchQuery('');
    };

    return (
        <div className="flex flex-col dark:bg-zinc-900 p-4">
            <div className="flex items-center dark:bg-zinc-800 rounded-md p-2">
                <input
                    type="text"
                    placeholder="Search inventory..."
                    value={filterText}
                    onChange={(e) => setFilterText(e.target.value)}
                    className="dark:bg-zinc-700 dark:text-zinc-100 rounded-md py-2 px-4 flex-grow"
                    aria-label="Search Inventory"
                />
                {filterText && (
                    <button onClick={handleClear} className="ml-2">
                        <XCircle size={20} className="dark:text-zinc-400 hover:dark:text-zinc-200" />
                    </button>
                )}
            </div>
            {isLoading && <p className="dark:text-zinc-400">Loading...</p>}
            {isError && <p className="dark:text-red-500">Error: {JSON.stringify(error)}</p>}
            {data && data.items && (
                <div className="mt-4">
                    <p className="dark:text-zinc-100">Total Items: {data.totalCount}</p>
                    {data.items.map((item) => (
                        <div key={item.id} className="dark:text-zinc-100 py-2 border-b dark:border-zinc-700">
                            <p>Name: {item.name}</p>
                            <p>SKU: {item.sku}</p>
                            {/* Display other item properties as needed */}
                        </div>
                    ))}
                </div>
            )}
            {data && data.items && data.items.length === 0 && !isLoading && !isError && (
                <p className="dark:text-zinc-400">No items found.</p>
            )}
        </div>
    );
};

export default InventoryView;