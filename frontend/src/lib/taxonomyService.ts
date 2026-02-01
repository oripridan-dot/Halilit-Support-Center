/**
 * Taxonomy Service - v1.0
 * 
 * Provides unified taxonomy loaded from aggregated brand taxonomies.
 * Ensures no products are uncategorized by providing fallback categorization.
 */

import type { Product } from '../types/index';

export interface TaxonomyData {
    version: string;
    generated_at: string;
    total_brands: number;
    total_products: number;
    main_categories: string[];
    spec_categories: string[];
    brand_category_mapping: Record<string, {
        brand_name: string;
        categories: string[];
    }>;
    category_hierarchy: Record<string, string[]>;
    categorization_rules: {
        primary_category_required: boolean;
        fallback_strategy: string;
        default_category: string;
        category_aliases: Record<string, string>;
        must_categorize: boolean;
        allow_uncategorized: boolean;
    };
}

export class TaxonomyService {
    private taxonomy: TaxonomyData | null = null;
    private loaded: boolean = false;
    private static instance: TaxonomyService | null = null;

    constructor() { }

    /**
     * Get singleton instance
     */
    static getInstance(): TaxonomyService {
        if (!TaxonomyService.instance) {
            TaxonomyService.instance = new TaxonomyService();
        }
        return TaxonomyService.instance;
    }

    /**
     * Load unified taxonomy from JSON
     */
    async load(): Promise<TaxonomyData> {
        if (this.taxonomy) return this.taxonomy;

        try {
            const response = await fetch('/data/taxonomy.json');
            if (!response.ok) {
                throw new Error('Failed to load taxonomy');
            }
            this.taxonomy = (await response.json()) as TaxonomyData;
            this.loaded = true;
            console.log('[TaxonomyService] ✅ Taxonomy loaded:', {
                brands: this.taxonomy.total_brands,
                products: this.taxonomy.total_products,
                categories: this.taxonomy.main_categories.length,
            });
            return this.taxonomy;
        } catch (error) {
            console.error('[TaxonomyService] Error loading taxonomy:', error);
            throw error;
        }
    }

    /**
     * Get all main categories
     */
    getMainCategories(): string[] {
        // Always return categories, with fallback if taxonomy not yet loaded
        return this.taxonomy?.main_categories || [
            'Audio Equipment',
            'Audio Gear',
            'Percussion',
            'Studio Monitors',
            'Testing',
        ];
    }

    /**
     * Get categories for a specific brand
     */
    getBrandCategories(brandId: string): string[] {
        if (!this.taxonomy) return [];
        const mapping = this.taxonomy.brand_category_mapping[brandId];
        return mapping?.categories || [];
    }

    /**
     * Ensure product has a category - apply fallback if needed
     */
    ensureCategorized(product: Product): Product {
        // If taxonomy not loaded, return product with default categorization
        if (!this.taxonomy) {
            if (!product.category) {
                return {
                    ...product,
                    category: 'Audio Equipment', // Fallback default
                };
            }
            return product;
        }

        const category = this._getCategory(product);

        if (!category) {
            // Apply categorization rules
            const rules = this.taxonomy.categorization_rules;

            let assignedCategory = product.category;

            // Try alias mapping
            if (!assignedCategory && product.category) {
                assignedCategory =
                    rules.category_aliases[product.category] || product.category;
            }

            // Use default if still uncategorized
            if (!assignedCategory) {
                assignedCategory = rules.default_category;
                console.warn(
                    `[TaxonomyService] Product ${product.id} was uncategorized, assigned default: ${assignedCategory}`
                );
            }

            return {
                ...product,
                category: assignedCategory,
            };
        }

        return product;
    }

    /**
     * Categorize a list of products
     */
    categorizeProducts(products: Product[]): Product[] {
        if (!this.loaded) {
            console.warn('[TaxonomyService] Taxonomy not loaded, returning products as-is');
            return products;
        }

        return products.map((product) => this.ensureCategorized(product));
    }

    /**
     * Get category for a product with various fallback strategies
     */
    private _getCategory(product: Product): string | null {
        if (!this.taxonomy) return null;

        // Try 1: category
        if (product.category && this._isValidCategory(product.category)) {
            return product.category;
        }

        // Try 2: Apply alias
        if (product.category) {
            const aliased =
                this.taxonomy.categorization_rules.category_aliases[product.category];
            if (aliased && this._isValidCategory(aliased)) {
                return aliased;
            }
        }

        // Try 3: Extract from specs
        if (product.specs && typeof product.specs === 'object') {
            const specKeys = Object.keys(product.specs);
            for (const key of specKeys) {
                if (this._isValidCategory(key)) {
                    return key;
                }
            }
        }

        // Try 4: Brand mapping
        if (product.brand_id) {
            // Find mapping for brand_id
            const mapping = this.taxonomy.brand_category_mapping[product.brand_id];
            if (mapping && mapping.categories.length > 0) {
                return mapping.categories[0];
            }
        }

        return null;
    }

    /**
     * Check if a category is in the unified taxonomy
     */
    private _isValidCategory(category: string): boolean {
        if (!this.taxonomy) return false;
        return this.taxonomy.main_categories.includes(category);
    }

    /**
     * Get statistics about taxonomy coverage
     */
    async getStatistics(): Promise<{
        totalCategories: number;
        totalBrands: number;
        totalProducts: number;
        coverage: Record<string, number>;
    }> {
        if (!this.taxonomy) {
            await this.load();
        }

        if (!this.taxonomy) {
            throw new Error('Failed to load taxonomy');
        }

        // Count products per category
        const coverage: Record<string, number> = {};
        this.taxonomy.main_categories.forEach((cat) => {
            coverage[cat] = 0;
        });

        // For now, simulate from brand mappings
        for (const mapping of Object.values(this.taxonomy.brand_category_mapping)) {
            for (const category of mapping.categories) {
                coverage[category] = (coverage[category] || 0) + 1;
            }
        }

        return {
            totalCategories: this.taxonomy.main_categories.length,
            totalBrands: this.taxonomy.total_brands,
            totalProducts: this.taxonomy.total_products,
            coverage,
        };
    }

    /**
     * Debug: Print full taxonomy
     */
    debug(): void {
        if (!this.taxonomy) {
            console.log('[TaxonomyService] Taxonomy not loaded');
            return;
        }

        console.group('[TaxonomyService] Debug Info');
        console.table({
            Version: this.taxonomy.version,
            Brands: this.taxonomy.total_brands,
            Products: this.taxonomy.total_products,
            Categories: this.taxonomy.main_categories.length,
        });

        console.log('Main Categories:', this.taxonomy.main_categories);
        console.log('Brand → Category Mapping:', this.taxonomy.brand_category_mapping);
        console.log('Categorization Rules:', this.taxonomy.categorization_rules);

        console.groupEnd();
    }
}

// Export singleton instance
export const taxonomyService = new TaxonomyService();
