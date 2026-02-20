/**
 * useTaxonomyTree v1.0
 *
 * Derives a 4-level taxonomy tree from the flat catalog returned by useConductorCatalog.
 * Brand → Category → Subcategory (Series-level) → Products
 *
 * Zero additional API calls — pure memoised computation over the catalog.
 */

import { useMemo } from 'react';
import { useConductorCatalog } from './useConductorCatalog';
import type { ConductorProduct } from './useConductorCatalog';

// ─────────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────────

export interface TaxonomyProduct {
    id: string;
    name: string;
    brand: string;
    category: string;
    subcategory: string;
    price: number;
    price_eilat: number;
    image_url: string;
    stock?: number | null;
    halilit_url: string;
    official_url: string;
}

export interface SeriesNode {
    id: string;        // slugified subcategory
    label: string;     // subcategory display name
    count: number;
    products: TaxonomyProduct[];
}

export interface FamilyNode {
    id: string;        // slugified category
    label: string;     // category display name
    count: number;
    series: SeriesNode[];
}

export interface BrandNode {
    id: string;        // slugified brand
    label: string;     // brand display name
    count: number;
    families: FamilyNode[];
}

export interface TaxonomyTree {
    brands: BrandNode[];
}

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

function slug(str: string): string {
    return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

function toTaxonomyProduct(p: ConductorProduct): TaxonomyProduct {
    return {
        id: p.id,
        name: p.name,
        brand: p.brand,
        category: p.category,
        subcategory: p.subcategory,
        price: p.price,
        price_eilat: p.price_eilat,
        image_url: p.image_url,
        stock: p.stock,
        halilit_url: p.halilit_url,
        official_url: p.official_url,
    };
}

// ─────────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────────

export function useTaxonomyTree(): { tree: TaxonomyTree; isLoading: boolean } {
    const { products, isLoading } = useConductorCatalog();

    const tree = useMemo<TaxonomyTree>(() => {
        if (!products || products.length === 0) return { brands: [] };

        // brand → category → subcategory grouping
        const brandMap = new Map<string, Map<string, Map<string, TaxonomyProduct[]>>>();

        for (const p of products) {
            const brandKey = p.brand || 'Unknown Brand';
            const catKey = p.category || 'Uncategorised';
            const subKey = p.subcategory || catKey;

            if (!brandMap.has(brandKey)) brandMap.set(brandKey, new Map());
            const catMap = brandMap.get(brandKey)!;

            if (!catMap.has(catKey)) catMap.set(catKey, new Map());
            const subMap = catMap.get(catKey)!;

            if (!subMap.has(subKey)) subMap.set(subKey, []);
            subMap.get(subKey)!.push(toTaxonomyProduct(p));
        }

        const brands: BrandNode[] = [];

        for (const [brandLabel, catMap] of brandMap) {
            const families: FamilyNode[] = [];

            for (const [catLabel, subMap] of catMap) {
                const series: SeriesNode[] = [];

                for (const [subLabel, products] of subMap) {
                    series.push({
                        id: slug(subLabel),
                        label: subLabel,
                        count: products.length,
                        products: products.sort((a, b) => a.name.localeCompare(b.name)),
                    });
                }

                series.sort((a, b) => b.count - a.count);

                const familyCount = series.reduce((s, n) => s + n.count, 0);
                families.push({
                    id: slug(catLabel),
                    label: catLabel,
                    count: familyCount,
                    series,
                });
            }

            families.sort((a, b) => b.count - a.count);

            const brandCount = families.reduce((s, n) => s + n.count, 0);
            brands.push({
                id: slug(brandLabel),
                label: brandLabel,
                count: brandCount,
                families,
            });
        }

        brands.sort((a, b) => b.count - a.count);

        return { brands };
    }, [products]);

    return { tree, isLoading };
}
