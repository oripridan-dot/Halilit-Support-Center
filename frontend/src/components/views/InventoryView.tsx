import React, { useState, useEffect, useRef } from 'react';
import { useDebounceValue } from '../../hooks/useDebounceValue';
import { useNavigationStore } from '../../store/navigationStore';
import { useConductorCatalog } from '../../hooks/useConductorCatalog';
import type { ConductorProduct } from '../../hooks/useConductorCatalog';

// ── Inline throttle hook (no external dep required) ──────────────────────────

interface ThrottleProps<T> {
    value: T;
    delay: number;
}

function useThrottledValue<T,>({ value, delay }: ThrottleProps<T>): T {
    const [throttled, setThrottled] = useState<T>(value);
    const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    useEffect(() => {
        if (timerRef.current) clearTimeout(timerRef.current);
        timerRef.current = setTimeout(() => {
            setThrottled(value);
            timerRef.current = null;
        }, delay);
        return () => {
            if (timerRef.current) clearTimeout(timerRef.current);
        };
    }, [value, delay]);

    return throttled;
}

// ─────────────────────────────────────────────────────────────────────────────

const InventoryView: React.FC = () => {
    const { searchQuery: initialSearchQuery, initialCfpFilter } = useNavigationStore();
    const [filterText, setFilterText] = useState<string>(initialSearchQuery ?? '');
    const [cfpFilter, setCfpFilter] = useState<boolean>(initialCfpFilter ?? false);

    const debouncedFilter = useDebounceValue(filterText, 150);
    const throttledFilter = useThrottledValue({ value: debouncedFilter, delay: 300 });


    // Sync navigation store's searchQuery on mount only
    useEffect(() => {
        if (initialSearchQuery && !filterText) {
            setFilterText(initialSearchQuery);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Canonical catalog from backend
    const { products, isLoading, error } = useConductorCatalog();
    const isError = !!error;

    // Client-side filter over the full catalog — fast, no extra fetch
    const filtered: ConductorProduct[] = React.useMemo(() => {
        if (!products) return [];
        const q = throttledFilter.toLowerCase();
        return products.filter((p) => {
            if (cfpFilter && p.price !== null && p.price !== undefined) return false;
            if (!q) return true;
            return (
                p.name?.toLowerCase().includes(q) ||
                p.brand?.toLowerCase().includes(q) ||
                p.sku?.toLowerCase().includes(q)
            );
        });
    }, [products, throttledFilter, cfpFilter]);

    return (
        <div className="bg-slate-900 min-h-screen p-4">
            {/* Search bar */}
            <input
                type="text"
                placeholder="Search by SKU, Brand, or Name…"
                value={filterText}
                onChange={(e) => setFilterText(e.target.value)}
                className="bg-slate-800 text-zinc-300 border border-zinc-700 rounded px-4 py-2 w-full mb-4 focus:outline-none focus:border-blue-500"
            />

            {/* CfP filter */}
            <div className="flex items-center mb-4 gap-2">
                <input
                    type="checkbox"
                    id="cfpFilter"
                    checked={cfpFilter}
                    onChange={(e) => setCfpFilter(e.target.checked)}
                    className="accent-blue-500"
                />
                <label htmlFor="cfpFilter" className="text-zinc-300 text-sm cursor-pointer">
                    Show Call-for-Price only
                </label>
            </div>

            {/* States */}
            {isLoading && <p className="text-zinc-400 text-sm">Loading inventory…</p>}
            {isError && (
                <p className="text-red-400 text-sm">
                    Error: {error ?? 'Failed to load catalog'}
                </p>
            )}
            {!isLoading && !isError && filtered.length === 0 && (
                <p className="text-zinc-500 text-sm">No products match your search.</p>
            )}

            {/* Product list */}
            {filtered.length > 0 && (
                <div className="divide-y divide-zinc-800">
                    {filtered.map((item) => (
                        <div key={item.id} className="py-3 px-2 flex items-center gap-4">
                            {item.image_url && (
                                <img
                                    src={item.image_url}
                                    alt={item.name}
                                    className="w-12 h-12 object-contain rounded bg-slate-800"
                                />
                            )}
                            <div className="flex-1 min-w-0">
                                <p className="text-zinc-100 font-medium truncate">{item.name}</p>
                                <p className="text-zinc-500 text-xs">{item.brand}</p>
                            </div>
                            <div className="text-right shrink-0">
                                {item.price != null ? (
                                    <p className="text-blue-400 font-semibold">₪{item.price}</p>
                                ) : (
                                    <p className="text-amber-500 text-sm font-medium">CfP</p>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default InventoryView;