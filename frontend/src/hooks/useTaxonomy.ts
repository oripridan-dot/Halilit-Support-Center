/**
 * useTaxonomy - Load and cache brand taxonomy structure
 * Provides access to the official category hierarchy from any brand
 * 
 * Follows STANDARDIZED COMMUNICATION PROTOCOL v1.0
 */
import { useCallback, useEffect, useState } from "react";
import {
    ROLAND_TAXONOMY,
    BOSS_TAXONOMY,
    NORD_TAXONOMY,
    MOOG_TAXONOMY,
    type BrandTaxonomy
} from "../lib/brandTaxonomy";
import { createAsyncResult, type AsyncResult } from "../lib/communicationProtocol";

// Map of available taxonomies
const TAXONOMIES: Record<string, BrandTaxonomy> = {
    roland: ROLAND_TAXONOMY,
    boss: BOSS_TAXONOMY,
    nord: NORD_TAXONOMY,
    moog: MOOG_TAXONOMY,
};

/**
 * Hook to load brand taxonomy (category structure)
 * @param brandId - Brand identifier (e.g., 'roland', 'boss', 'nord', 'moog')
 * @returns AsyncResult with taxonomy data, loading, and error states
 * 
 * @example
 * const { data: taxonomy, loading, error, isReady } = useTaxonomy('roland')
 */
export const useTaxonomy = (brandId?: string): AsyncResult<BrandTaxonomy> => {
    const [taxonomy, setTaxonomy] = useState<BrandTaxonomy | null>(null);
    const [loading, setLoading] = useState(!!brandId);
    const [error, setError] = useState<Error | null>(null);

    const loadTaxonomy = useCallback(async () => {
        if (!brandId) {
            setTaxonomy(null);
            setLoading(false);
            setError(null);
            return;
        }

        setLoading(true);
        setError(null);

        try {
            // Taxonomies are pre-loaded static data, no async operation needed
            // but we use setTimeout to simulate async behavior for consistency
            await new Promise((resolve) => setTimeout(resolve, 0));

            const foundTaxonomy = TAXONOMIES[brandId.toLowerCase()];

            if (!foundTaxonomy) {
                throw new Error(`Taxonomy not found for brand: ${brandId}`);
            }

            setTaxonomy(foundTaxonomy);
            setError(null);
        } catch (err) {
            const error = err instanceof Error ? err : new Error("Failed to load taxonomy");
            setError(error);
            setTaxonomy(null);
        } finally {
            setLoading(false);
        }
    }, [brandId]);

    // Load taxonomy when brandId changes
    useEffect(() => {
        loadTaxonomy();
    }, [loadTaxonomy]);
    const retry = useCallback(() => {
        loadTaxonomy();
    }, [loadTaxonomy]);

    return createAsyncResult(taxonomy, loading, error, retry);
};
