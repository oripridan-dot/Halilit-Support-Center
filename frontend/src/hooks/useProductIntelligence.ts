/**
 * useProductIntelligence — JIT enrichment hook
 *
 * Fetches live product intelligence from the backend ProductSynthesizer.
 * Data is cached by React Query (5min stale) + backend file cache (7-day TTL).
 * Returns: enriched data, loading state, and research progress.
 */

import { useQuery } from '@tanstack/react-query';
import type { ReviewVerdict, BrandTheme, FamousUser, KnownIssue, LayoutHints } from '../types';

export interface ProductIntelligence {
    product_id: string;
    product_name: string;
    brand: string;

    // Enriched content
    enriched_description: string;
    key_features: string[];
    specifications: Record<string, string>;

    // Reviews from trusted sources
    review_verdicts: ReviewVerdict[];
    consensus_score: number; // 0-100

    // Brand theme
    brand_theme: BrandTheme;

    // Community & context
    famous_users: FamousUser[];
    known_issues: KnownIssue[];
    best_for: string[];
    avoid_if: string[];

    // Layout hints
    layout_hints: LayoutHints;

    // Metadata
    sources_used: string[];
    cached: boolean;
    generated_at: string;
}

/**
 * Fetch JIT intelligence for a single product.
 * Only fires when productId is truthy — safe to call unconditionally.
 */
export const useProductIntelligence = (productId: string | null) => {
    const { data, isLoading, error, refetch, isFetching } = useQuery<ProductIntelligence>({
        queryKey: ['product-intelligence', productId],
        queryFn: async () => {
            const response = await fetch(`/api/product/${productId}/intelligence`);
            if (!response.ok) {
                throw new Error(`Intelligence fetch failed: ${response.statusText}`);
            }
            return response.json();
        },
        enabled: !!productId,
        staleTime: 5 * 60 * 1000,        // 5 min
        gcTime: 15 * 60 * 1000,           // 15 min
        retry: 1,
        refetchOnWindowFocus: false,
    });

    return {
        intelligence: data ?? null,
        isResearching: isLoading || isFetching,
        error: error ? (error as Error).message : null,
        refetch,
    };
};
