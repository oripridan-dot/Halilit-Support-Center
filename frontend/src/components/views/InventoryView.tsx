import React, { useState, useEffect, useRef } from 'react';
import { useDebounceValue } from '../../hooks/useDebounceValue';
import { useConductorCatalog } from '../../hooks/useConductorCatalog';
import { InventorySearchRequest, InventoryItem, INVENTORY_SEARCH_ENDPOINT } from '../../specs/contracts/enhanced_inventory_search_debounce_with_throttle.schema';
import { Search, ChevronUp, ChevronDown, Package, Phone } from 'lucide-react';
import { Select } from 'react-select';
import { useNavigationStore } from '../../stores/navigationStore';


const InventoryView: React.FC = () => {
    const [filterText, setFilterText] = useState<string>('');
    const [brandFilter, setBrandFilter] = useState<any>(null); // Replace 'any' with the correct type for your brand filter options
    const [categoryFilter, setCategoryFilter] = useState<any>(null); // Replace 'any' with the correct type for your category filter options
    const [cfpFilter, setCfpFilter] = useState<boolean>(false);
    const { initialCfpFilter, searchQuery, setInitialSearchQuery } = useNavigationStore();
    const debouncedFilterText = useDebounceValue(filterText, 150);
    const [throttleFlag, setThrottleFlag] = useState(false);
    const throttleTimeoutRef = useRef<number | null>(null);

    const { data, isLoading, error, refetch } = useConductorCatalog<InventorySearchResponse>(
        INVENTORY_SEARCH_ENDPOINT,
        {
            searchQuery: debouncedFilterText,
            // brand: brandFilter?.value,
            // category: categoryFilter?.value,
            cfp: cfpFilter,
        },
        {
            enabled: false,
        }
    );

    useEffect(() => {
        setInitialSearchQuery(searchQuery || '');
        setFilterText(searchQuery || '');
        setCfpFilter(initialCfpFilter || false);
    }, [searchQuery, initialCfpFilter, setInitialSearchQuery]);

    const handleSearchChange = (value: string) => {
        setFilterText(value);
        if (throttleTimeoutRef.current) {
            clearTimeout(throttleTimeoutRef.current);
        }

        throttleTimeoutRef.current = window.setTimeout(() => {
            if (debouncedFilterText) {
                refetch({ searchQuery: debouncedFilterText });
            } else {
                refetch({});
            }
            setThrottleFlag(true);
        }, 300);
    };

    useEffect(() => {
        if (throttleFlag && !isLoading) {
            setThrottleFlag(false);
        }
    }, [isLoading, throttleFlag]);

    const handleBrandChange = (selectedOption: any) => {
        setBrandFilter(selectedOption);
        if (throttleTimeoutRef.current) {
            clearTimeout(throttleTimeoutRef.current);
        }

        throttleTimeoutRef.current = window.setTimeout(() => {
            refetch({
                searchQuery: debouncedFilterText,
                // brand: selectedOption?.value,
            });
            setThrottleFlag(true);
        }, 300);
    };

    const handleCategoryChange = (selectedOption: any) => {
        setCategoryFilter(selectedOption);
        if (throttleTimeoutRef.current) {
            clearTimeout(throttleTimeoutRef.current);
        }

        throttleTimeoutRef.current = window.setTimeout(() => {
            refetch({
                searchQuery: debouncedFilterText,
                // category: selectedOption?.value,
            });
            setThrottleFlag(true);
        }, 300);
    };

    const handleCfpChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setCfpFilter(e.target.checked);
        if (throttleTimeoutRef.current) {
            clearTimeout(throttleTimeoutRef.current);
        }

        throttleTimeoutRef.current = window.setTimeout(() => {
            refetch({
                searchQuery: debouncedFilterText,
                cfp: e.target.checked,
            });
            setThrottleFlag(true);
        }, 300);
    };

    const inventoryItems = data?.items || [];
    const totalCount = data?.totalCount || 0;

    return (
        <div className="bg-slate-900 min-h-screen p-4">
            <div className="flex flex-col space-y-4">
                <div className="flex space-x-2">
                    <div className="relative w-full">
                        <Search className="absolute left-2 top-2 h-4 w-4 text-zinc-400" />
                        <input
                            type="text"
                            placeholder="Search products..."
                            value={filterText}
                            onChange={(e) => handleSearchChange(e.target.value)}
                            className="w-full pl-8 pr-2 py-2 rounded-md bg-zinc-800 text-zinc-100 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                </div>
                <div className="flex space-x-2">
                    <Select
                        placeholder="Select Brand..."
                        options={[]} // Replace with your brand options
                        value={brandFilter}
                        onChange={handleBrandChange}
                        className="w-1/3 bg-zinc-800 text-zinc-100"
                        styles={{
                            control: (provided) => ({
                                ...provided,
                                backgroundColor: '#1e293b', // slate-900
                                borderColor: '#334155', // zinc-700
                                color: '#f0f9ff', // zinc-100
                                padding: '0.5rem',
                                borderRadius: '0.375rem',
                                '&:hover': {
                                    borderColor: '#64748b', // zinc-500
                                },
                            }),
                            option: (provided, state) => ({
                                ...provided,
                                backgroundColor: state.isSelected ? '#3b82f6' : '#1e293b', // blue-500 : slate-900
                                color: state.isSelected ? '#f0f9ff' : '#f0f9ff', // zinc-100
                                '&:hover': {
                                    backgroundColor: '#60a5fa', // blue-300
                                },
                            }),
                            placeholder: (provided) => ({
                                ...provided,
                                color: '#a1a1aa', // zinc-400
                            }),
                            singleValue: (provided) => ({
                                ...provided,
                                color: '#f0f9ff', // zinc-100
                            }),
                            menu: (provided) => ({
                                ...provided,
                                backgroundColor: '#1e293b', // slate-900
                            }),
                        }}
                    />
                    <Select
                        placeholder="Select Category..."
                        options={[]} // Replace with your category options
                        value={categoryFilter}
                        onChange={handleCategoryChange}
                        className="w-1/3 bg-zinc-800 text-zinc-100"
                        styles={{
                            control: (provided) => ({
                                ...provided,
                                backgroundColor: '#1e293b', // slate-900
                                borderColor: '#334155', // zinc-700
                                color: '#f0f9ff', // zinc-100
                                padding: '0.5rem',
                                borderRadius: '0.375rem',
                                '&:hover': {
                                    borderColor: '#64748b', // zinc-500
                                },
                            }),
                            option: (provided, state) => ({
                                ...provided,
                                backgroundColor: state.isSelected ? '#3b82f6' : '#1e293b', // blue-500 : slate-900
                                color: state.isSelected ? '#f0f9ff' : '#f0f9ff', // zinc-100
                                '&:hover': {
                                    backgroundColor: '#60a5fa', // blue-300
                                },
                            }),
                            placeholder: (provided) => ({
                                ...provided,
                                color: '#a1a1aa', // zinc-400
                            }),
                            singleValue: (provided) => ({
                                ...provided,
                                color: '#f0f9ff', // zinc-100
                            }),
                            menu: (provided) => ({
                                ...provided,
                                backgroundColor: '#1e293b', // slate-900
                            }),
                        }}
                    />
                    <div className="flex items-center space-x-1">
                        <input
                            type="checkbox"
                            id="cfp-toggle"
                            checked={cfpFilter}
                            onChange={handleCfpChange}
                            className="rounded text-blue-500 focus:ring-blue-500"
                        />
                        <label htmlFor="cfp-toggle" className="text-zinc-100">
                            Call for Price Only
                        </label>
                    </div>
                </div>
                <div className="overflow-x-auto">
                    <table className="min-w-full bg-zinc-800 rounded-md">
                        <thead className="bg-zinc-700">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-zinc-300 uppercase tracking-wider">
                                    Name
                                    {/* Implement sorting with ChevronUp/Down */}
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-zinc-300 uppercase tracking-wider">
                                    Brand
                                    {/* Implement sorting with ChevronUp/Down */}
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-zinc-300 uppercase tracking-wider">
                                    Price
                                    {/* Implement sorting with ChevronUp/Down */}
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-zinc-300 uppercase tracking-wider">
                                    Stock
                                </th>
                            </tr>
                        </thead>
                        <tbody className="bg-zinc-800 divide-y divide-zinc-700">
                            {isLoading ? (
                                <tr>
                                    <td colSpan={4} className="px-6 py-4 whitespace-nowrap text-zinc-400 text-center">
                                        Loading...
                                    </td>
                                </tr>
                            ) : error ? (
                                <tr>
                                    <td colSpan={4} className="px-6 py-4 whitespace-nowrap text-zinc-400 text-center">
                                        Error loading inventory.
                                    </td>
                                </tr>
                            ) : inventoryItems.length === 0 ? (
                                <tr>
                                    <td colSpan={4} className="px-6 py-4 whitespace-nowrap text-zinc-400 text-center">
                                        No products found.
                                    </td>
                                </tr>
                            ) : (
                                inventoryItems.map((item: InventoryItem) => (
                                    <tr key={item.id}>
                                        <td className="px-6 py-4 whitespace-nowrap text-zinc-100">
                                            {item.name}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-zinc-100">
                                            {/* Brand Placeholder */}
                                            Brand Name Placeholder
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-zinc-100">
                                            {item.price === null || item.price === 0 ? (
                                                <div className="flex items-center space-x-1">
                                                    <Phone className="h-4 w-4 text-green-500" />
                                                    <span>Call for Price</span>
                                                </div>
                                            ) : (
                                                `₪${item.price.toFixed(2)}`
                                            )}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            {item.stock_status === 'in_stock' ? (
                                                <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                                    <Package className="w-3 h-3 mr-1" />
                                                    In Stock
                                                </div>
                                            ) : item.stock_status === 'out_of_stock' ? (
                                                <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                                    <Package className="w-3 h-3 mr-1" />
                                                    Out of Stock
                                                </div>
                                            ) : (
                                                <div className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-zinc-100 text-zinc-800">
                                                    <Package className="w-3 h-3 mr-1" />
                                                    Unknown
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default InventoryView;