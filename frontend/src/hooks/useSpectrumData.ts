import { useEffect, useState, useCallback } from 'react';

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
 * Hook to fetch enhanced spectrum data from the backend
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
    const [data, setData] = useState<SpectrumDataResult | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);
    const [retryCount, setRetryCount] = useState(0);

    const fetchData = useCallback(async () => {
        if (!brand) return;

        setLoading(true);
        setError(null);

        try {
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

            const result = await response.json();
            setData(result);
        } catch (err) {
            setError(err instanceof Error ? err : new Error(String(err)));
            console.error('Error fetching spectrum data:', err);
        } finally {
            setLoading(false);
        }
    }, [brand, options]);

    useEffect(() => {
        fetchData();
    }, [brand, options.include_enrichment, options.force_refresh, fetchData]);

    const retry = useCallback(() => {
        setRetryCount(prev => prev + 1);
        fetchData();
    }, [fetchData]);

    return {
        data,
        loading,
        error,
        retry,
    };
};

/**
 * Hook to fetch quality report for a brand
 */
export const useSpectrumQualityReport = (brand: string) => {
    const [report, setReport] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        if (!brand) return;

        const fetchReport = async () => {
            setLoading(true);
            setError(null);

            try {
                const response = await fetch(`/api/spectrum/quality-report/${brand}`);

                if (!response.ok) {
                    throw new Error(`Failed to fetch quality report: ${response.statusText}`);
                }

                const data = await response.json();
                setReport(data);
            } catch (err) {
                setError(err instanceof Error ? err : new Error(String(err)));
                console.error('Error fetching quality report:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchReport();
    }, [brand]);

    return { report, loading, error };
};

/**
 * Hook to fetch data sources information
 */
export const useSpectrumDataSources = (brand: string) => {
    const [sources, setSources] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        if (!brand) return;

        const fetchSources = async () => {
            setLoading(true);
            setError(null);

            try {
                const response = await fetch(`/api/spectrum/sources/${brand}`);

                if (!response.ok) {
                    throw new Error(`Failed to fetch data sources: ${response.statusText}`);
                }

                const data = await response.json();
                setSources(data);
            } catch (err) {
                setError(err instanceof Error ? err : new Error(String(err)));
                console.error('Error fetching data sources:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchSources();
    }, [brand]);

    return { sources, loading, error };
};

/**
 * Hook to rebuild spectrum data for a brand
 */
export const useSpectrumRebuild = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);
    const [result, setResult] = useState<any>(null);

    const rebuild = useCallback(
        async (brand: string, deepRefresh: boolean = false) => {
            setLoading(true);
            setError(null);

            try {
                const response = await fetch(
                    `/api/spectrum/rebuild/${brand}?deep_refresh=${deepRefresh}`,
                    { method: 'POST' }
                );

                if (!response.ok) {
                    throw new Error(`Failed to rebuild spectrum data: ${response.statusText}`);
                }

                const data = await response.json();
                setResult(data);
                return data;
            } catch (err) {
                const error = err instanceof Error ? err : new Error(String(err));
                setError(error);
                console.error('Error rebuilding spectrum data:', err);
                throw error;
            } finally {
                setLoading(false);
            }
        },
        []
    );

    return { rebuild, loading, error, result };
};
