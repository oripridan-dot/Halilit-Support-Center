/**
 * useGalaxyData - Smart Consumer Hook for Galaxy Catalog
 * 
 * Loads the unified Galaxy database and provides:
 * - Reactive catalog state
 * - Semantic search with pre-computed tokens
 * - Category/Brand navigation
 * - Analytics helpers
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { GalaxyCatalog, GalaxyProduct, SearchResult, TierStats, BrandProfile, CategoryStats } from '../types/galaxy-schema';

interface UseGalaxyDataResult {
    catalog: GalaxyCatalog | null;
    products: GalaxyProduct[];
    categories: Record<string, string[]>;
    loading: boolean;
    error: string | null;

    // Search & Filter
    search: (query: string) => SearchResult[];
    getProductsByTier: (tier: 'entry' | 'mid' | 'pro' | 'flagship') => GalaxyProduct[];
    getProductsByBrand: (brand: string) => GalaxyProduct[];
    getProductsByCategory: (category: string) => GalaxyProduct[];

    // Analytics
    getTierStats: () => TierStats[];
    getBrandProfile: (brand: string) => BrandProfile | null;
    getCategoryStats: (category: string) => CategoryStats | null;
    getAllBrands: () => string[];
}

export const useGalaxyData = (): UseGalaxyDataResult => {
    const [data, setData] = useState<GalaxyCatalog | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Load the single source of truth
    useEffect(() => {
        const loadData = async () => {
            try {
                const response = await fetch('/data/galaxy_db.json');
                if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load Galaxy DB`);

                const catalog: GalaxyCatalog = await response.json();

                // Validate catalog structure
                if (!catalog.products || !Array.isArray(catalog.products)) {
                    throw new Error("Invalid catalog structure: missing products array");
                }

                setData(catalog);
                setError(null);
                console.log(`✅ Galaxy DB loaded: ${catalog.products.length} products from ${Object.keys(catalog.categories).length} categories`);
            } catch (err) {
                const message = err instanceof Error ? err.message : 'Unknown error';
                console.error("❌ CRITICAL DATA FAILURE:", message);
                setError(message);
                setData(null);
            } finally {
                setLoading(false);
            }
        };

        loadData();
    }, []);

    /**
     * Semantic search using pre-computed search tokens
     * Finds products matching the query string
     */
    const search = useCallback((query: string): SearchResult[] => {
        if (!data || !query) return [];

        const lowerQ = query.toLowerCase();
        const results: SearchResult[] = [];

        for (const product of data.products) {
            const tokens = product.searchTokens.split(' ');

            // Simple token matching (could be enhanced with fuzzy matching)
            let matchCount = 0;
            for (const token of tokens) {
                if (token.includes(lowerQ) || lowerQ.includes(token)) {
                    matchCount++;
                }
            }

            if (matchCount > 0) {
                const relevance = Math.min(1, matchCount / tokens.length);
                results.push({ product, relevance });
            }
        }

        // Sort by relevance
        return results.sort((a, b) => b.relevance - a.relevance);
    }, [data]);

    /**
     * Filter products by tier
     */
    const getProductsByTier = useCallback((tier: 'entry' | 'mid' | 'pro' | 'flagship'): GalaxyProduct[] => {
        return data?.products.filter(p => p.tier === tier) || [];
    }, [data]);

    /**
     * Filter products by brand
     */
    const getProductsByBrand = useCallback((brand: string): GalaxyProduct[] => {
        return data?.products.filter(p => p.brand.toLowerCase() === brand.toLowerCase()) || [];
    }, [data]);

    /**
     * Filter products by category
     */
    const getProductsByCategory = useCallback((category: string): GalaxyProduct[] => {
        return data?.products.filter(p => p.category === category) || [];
    }, [data]);

    /**
     * Get statistics about product tiers
     */
    const getTierStats = useCallback((): TierStats[] => {
        if (!data) return [];

        const tiers: Record<string, TierStats> = {
            entry: { tier: 'entry', count: 0, avgPrice: 0, minPrice: Infinity, maxPrice: 0 },
            mid: { tier: 'mid', count: 0, avgPrice: 0, minPrice: Infinity, maxPrice: 0 },
            pro: { tier: 'pro', count: 0, avgPrice: 0, minPrice: Infinity, maxPrice: 0 },
            flagship: { tier: 'flagship', count: 0, avgPrice: 0, minPrice: Infinity, maxPrice: 0 },
        };

        for (const product of data.products) {
            const tier = product.tier;
            tiers[tier].count++;
            tiers[tier].avgPrice += product.price;
            tiers[tier].minPrice = Math.min(tiers[tier].minPrice, product.price);
            tiers[tier].maxPrice = Math.max(tiers[tier].maxPrice, product.price);
        }

        // Finalize averages
        for (const tier of Object.values(tiers)) {
            if (tier.count > 0) {
                tier.avgPrice = Math.round(tier.avgPrice / tier.count);
            }
            if (tier.minPrice === Infinity) {
                tier.minPrice = 0;
            }
        }

        return Object.values(tiers);
    }, [data]);

    /**
     * Get profile for a specific brand
     */
    const getBrandProfile = useCallback((brand: string): BrandProfile | null => {
        if (!data) return null;

        const products = data.products.filter(p => p.brand === brand);
        if (products.length === 0) return null;

        const tiers: Record<string, number> = { entry: 0, mid: 0, pro: 0, flagship: 0 };
        const categories = new Set<string>();
        let totalPrice = 0;

        for (const product of products) {
            tiers[product.tier]++;
            categories.add(product.category);
            totalPrice += product.price;
        }

        return {
            name: brand,
            productCount: products.length,
            categories,
            avgPrice: Math.round(totalPrice / products.length),
            tiers,
        };
    }, [data]);

    /**
     * Get statistics for a specific category
     */
    const getCategoryStats = useCallback((category: string): CategoryStats | null => {
        if (!data) return null;

        const products = data.products.filter(p => p.category === category);
        if (products.length === 0) return null;

        const subCategories: Record<string, number> = {};
        const brands = new Set<string>();
        let minPrice = Infinity;
        let maxPrice = 0;
        let totalPrice = 0;

        for (const product of products) {
            subCategories[product.subCategory] = (subCategories[product.subCategory] || 0) + 1;
            brands.add(product.brand);
            minPrice = Math.min(minPrice, product.price);
            maxPrice = Math.max(maxPrice, product.price);
            totalPrice += product.price;
        }

        return {
            name: category,
            productCount: products.length,
            brands: Array.from(brands),
            subCategories,
            priceRange: {
                min: minPrice === Infinity ? 0 : minPrice,
                max: maxPrice,
                avg: Math.round(totalPrice / products.length),
            },
        };
    }, [data]);

    /**
     * Get all unique brands
     */
    const getAllBrands = useCallback((): string[] => {
        if (!data) return [];
        const brands = new Set(data.products.map(p => p.brand));
        return Array.from(brands).sort();
    }, [data]);

    // Memoize computed products and categories for stable references
    const memoizedProducts = useMemo(() => data?.products || [], [data?.products]);
    const memoizedCategories = useMemo(() => data?.categories || {}, [data?.categories]);

    return {
        catalog: data,
        products: memoizedProducts,
        categories: memoizedCategories,
        loading,
        error,
        search,
        getProductsByTier,
        getProductsByBrand,
        getProductsByCategory,
        getTierStats,
        getBrandProfile,
        getCategoryStats,
        getAllBrands,
    };
};
