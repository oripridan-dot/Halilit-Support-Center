/**
 * useStockStatus — focused stock-level query per product.
 *
 * Spec: evolution_tanstack_query_formerly_react_query.md
 * Uses @tanstack/react-query (already a project dependency) to poll for
 * out-of-stock signals on a per-product basis without re-fetching the entire
 * catalog.
 *
 * Backend: hits /api/products/:id — if the endpoint returns 404 the hook
 * marks the product as unknown (not out-of-stock) so the UI stays safe.
 */
import { useQuery, useQueryClient } from '@tanstack/react-query';

export interface StockStatus {
    productId: string;
    /** null = unknown (endpoint not available) */
    inStock: boolean | null;
    /** Raw stock field from catalog, e.g. "in_stock", "out_of_stock", "cfp" */
    stockRaw: string | null;
    price: number | null;
}

const STOCK_STALE_TIME = 30_000;   // 30 s
const STOCK_REFETCH_INTERVAL = 60_000;  // 1 min

async function fetchStockStatus(productId: string): Promise<StockStatus> {
    if (!productId) {
        return { productId, inStock: null, stockRaw: null, price: null };
    }
    try {
        const res = await fetch(`/api/products/${productId}`, {
            headers: { Accept: 'application/json' },
        });
        if (!res.ok) {
            return { productId, inStock: null, stockRaw: null, price: null };
        }
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const data: any = await res.json();
        const stockRaw: string | null = data?.stock_status ?? data?.stock ?? null;
        const inStock = stockRaw == null ? null : stockRaw === 'in_stock';
        const price: number | null = data?.price_il ?? data?.price ?? null;
        return { productId, inStock, stockRaw, price };
    } catch {
        return { productId, inStock: null, stockRaw: null, price: null };
    }
}

/**
 * Query the stock status of a single product, auto-refreshing every minute.
 */
export function useStockStatus(productId: string | undefined) {
    return useQuery<StockStatus>({
        queryKey: ['stockStatus', productId],
        queryFn: () => fetchStockStatus(productId!),
        enabled: Boolean(productId),
        staleTime: STOCK_STALE_TIME,
        refetchInterval: STOCK_REFETCH_INTERVAL,
    });
}

/**
 * Programmatically invalidate the stock cache for a product (call after
 * a mutation that changes stock level).
 */
export function useInvalidateStock() {
    const qc = useQueryClient();
    return (productId: string) =>
        qc.invalidateQueries({ queryKey: ['stockStatus', productId] });
}
