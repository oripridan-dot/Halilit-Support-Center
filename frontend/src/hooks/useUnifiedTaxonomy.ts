/**
 * useUnifiedTaxonomy Hook - v1.0
 * 
 * Provides access to unified taxonomy aggregated from all brand catalogs.
 * Ensures no products are uncategorized by using fallback categorization rules.
 */

import { useEffect, useState } from 'react';
import { taxonomyService, type TaxonomyData } from '../lib/taxonomyService';
import type { Product } from '../types/index';

export interface UseUnifiedTaxonomyReturn {
    taxonomy: TaxonomyData | null;
    loading: boolean;
    error: Error | null;
    mainCategories: string[];
    getBrandCategories: (brandId: string) => string[];
    ensureCategorized: (product: Product) => Product;
    categorizeProducts: (products: Product[]) => Product[];
    getStats: () => Promise<{
        totalCategories: number;
        totalBrands: number;
        totalProducts: number;
        coverage: Record<string, number>;
    }>;
}

/**
 * Hook to load and use unified taxonomy
 * Learns taxonomy from all brands and provides categorization services
 */
export function useUnifiedTaxonomy(): UseUnifiedTaxonomyReturn {
    const [taxonomy, setTaxonomy] = useState<TaxonomyData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        let mounted = true;

        const loadTaxonomy = async () => {
            try {
                const data = await taxonomyService.load();
                if (mounted) {
                    setTaxonomy(data);
                    setError(null);
                    console.log('[useUnifiedTaxonomy] ✅ Taxonomy loaded:', {
                        categories: data.main_categories.length,
                        brands: data.total_brands,
                        products: data.total_products,
                    });
                }
            } catch (err) {
                if (mounted) {
                    const error = err instanceof Error ? err : new Error(String(err));
                    setError(error);
                    console.error('[useUnifiedTaxonomy] Error loading taxonomy:', err);
                }
            } finally {
                if (mounted) {
                    setLoading(false);
                }
            }
        };

        loadTaxonomy();

        return () => {
            mounted = false;
        };
    }, []);

    const getStats = async () => {
        try {
            return await taxonomyService.getStatistics();
        } catch (error) {
            console.error('[useUnifiedTaxonomy] Error getting statistics:', error);
            throw error;
        }
    };

    return {
        taxonomy,
        loading,
        error,
        mainCategories: taxonomy?.main_categories || taxonomyService.getMainCategories(),
        getBrandCategories: (brandId: string) =>
            taxonomyService.getBrandCategories(brandId),
        ensureCategorized: (product: Product) =>
            taxonomyService.ensureCategorized(product),
        categorizeProducts: (products: Product[]) =>
            taxonomyService.categorizeProducts(products),
        getStats,
    };
}
