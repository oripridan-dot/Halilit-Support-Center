import { useQuery, useMutation } from '@tanstack/react-query';
import { useCallback } from 'react';

interface SpectrumDataOptions {
    include_enrichment?: boolean;
    force_refresh?: boolean;
}

interface SpectrumDataResult {
    brand: string;
    timestamp: string;
    total_products: number;
    tracks: any[];
    metadata: any;
}

interface UseSpectrumDataReturn {
    data: SpectrumDataResult | null;
    loading: boolean;
    error: Error | null;
    retry: () => void;
}

/**
 * Hook to fetch enhanced spectrum data from the backend - TanStack Query powered
 * 
 * Usage:
 * const { data, loading, error } = useSpectrumData('Nord', {
 *   include_enrichment: true,
 *   force_refresh: false
 * });
 */
export const useSpectrumData = (
    brand: string,
    options: SpectrumDataOptions = {}
): UseSpectrumDataReturn => {

    const { data, isLoading, error, refetch } = useQuery({
        queryKey: ['spectrum-data', brand, options.include_enrichment, options.force_refresh],
        queryFn: async () => {
            if (!brand) throw new Error('Brand is required');

            const params = new URLSearchParams({
                include_enrichment: String(options.include_enrichment ?? true),
                force_refresh: String(options.force_refresh ?? false),
            });

            const response = await fetch(
                `/api/spectrum/data/${brand}?${params.toString()}`
            );

            if (!response.ok) {
                throw new Error(`Failed to fetch spectrum data: ${response.statusText}`);
            }

            return response.json() as Promise<SpectrumDataResult>;
        },
        enabled: !!brand,
        staleTime: 5 * 60 * 1000, // 5 minutes
        gcTime: 10 * 60 * 1000,   // 10 minutes
        refetchOnWindowFocus: true,
        refetchOnReconnect: true,
        retry: 1,
    });

    return {
        data: data || null,
        loading: isLoading,
        error: error instanceof Error ? error : null,
        retry: () => refetch(),
    };
};

/**
 * Hook to fetch quality report for a brand - TanStack Query powered
 */
export const useSpectrumQualityReport = (brand: string) => {
    const { data: report, isLoading: loading, error } = useQuery({
        queryKey: ['spectrum-quality-report', brand],
        queryFn: async () => {
            if (!brand) throw new Error('Brand is required');

            const response = await fetch(`/api/spectrum/quality-report/${brand}`);

            if (!response.ok) {
                throw new Error(`Failed to fetch quality report: ${response.statusText}`);
            }

            return response.json();
        },
        enabled: !!brand,
        staleTime: 10 * 60 * 1000, // 10 minutes
        gcTime: 20 * 60 * 1000,    // 20 minutes
        refetchOnWindowFocus: true,
        refetchOnReconnect: true,
        retry: 1,
    });

    return { report: report || null, loading, error: error instanceof Error ? error : null };
};

/**
 * Hook to fetch data sources information - TanStack Query powered
 */
export const useSpectrumDataSources = (brand: string) => {
    const { data: sources, isLoading: loading, error } = useQuery({
        queryKey: ['spectrum-sources', brand],
        queryFn: async () => {
            if (!brand) throw new Error('Brand is required');

            const response = await fetch(`/api/spectrum/sources/${brand}`);

            if (!response.ok) {
                throw new Error(`Failed to fetch data sources: ${response.statusText}`);
            }

            return response.json();
        },
        enabled: !!brand,
        staleTime: 10 * 60 * 1000, // 10 minutes
        gcTime: 20 * 60 * 1000,    // 20 minutes
        refetchOnWindowFocus: true,
        refetchOnReconnect: true,
        retry: 1,
    });

    return { sources: sources || null, loading, error: error instanceof Error ? error : null };
};

/**
 * Hook to rebuild spectrum data for a brand - useMutation for POST request
 */
export const useSpectrumRebuild = () => {
    const { mutateAsync: rebuild, isPending: loading, error, data: result } = useMutation({
        mutationFn: async (params: { brand: string; deepRefresh?: boolean }) => {
            const response = await fetch(
                `/api/spectrum/rebuild/${params.brand}?deep_refresh=${params.deepRefresh ?? false}`,
                { method: 'POST' }
            );

            if (!response.ok) {
                throw new Error(`Failed to rebuild spectrum data: ${response.statusText}`);
            }

            return response.json();
        },
    });

    return {
        rebuild: useCallback(
            async (brand: string, deepRefresh: boolean = false) => {
                return rebuild({ brand, deepRefresh });
            },
            [rebuild]
        ),
        loading,
        error: error instanceof Error ? error : null,
        result: result || null,
    };
};
