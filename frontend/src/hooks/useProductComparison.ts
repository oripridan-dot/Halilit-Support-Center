/**
 * useProductComparison — JIT comparison hook
 *
 * Fetches a live AI-powered comparison between two products.
 * Both product IDs must be set before the query fires.
 */

import { useQuery } from '@tanstack/react-query';
import type { ProductComparison } from '../types';

/**
 * Compare two products via the JIT comparison endpoint.
 * Only fires when both IDs are truthy.
 */
export const useProductComparison = (
    productIdA: string | null,
    productIdB: string | null,
) => {
    const enabled = !!productIdA && !!productIdB;

    const { data, isLoading, error, refetch, isFetching } = useQuery<ProductComparison>({
        queryKey: ['product-comparison', productIdA, productIdB],
        queryFn: async () => {
            const response = await fetch(
                `/api/product/${productIdA}/compare/${productIdB}`,
            );
            if (!response.ok) {
                throw new Error(`Comparison failed: ${response.statusText}`);
            }
            return response.json();
        },
        enabled,
        staleTime: 10 * 60 * 1000,       // 10 min
        gcTime: 30 * 60 * 1000,           // 30 min
        retry: 1,
        refetchOnWindowFocus: false,
    });

    return {
        comparison: data ?? null,
        isComparing: isLoading || isFetching,
        error: error ? (error as Error).message : null,
        refetch,
    };
};
