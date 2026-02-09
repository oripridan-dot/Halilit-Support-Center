/**
 * Halilit Galaxy UI 2.0 - Galaxy View Type Definitions
 *
 * These types are specific to the Galaxy view layout.
 * The canonical Product type is in ./index.ts (aliased from generated.ts).
 */

/** Product shape for Galaxy view rendering */
export interface GalaxyProduct {
    uuid: string;
    name: string;
    brand: string;
    category: string;
    subCategory: string;
    image: string;
    price?: number;
    specs: Record<string, string>;
    description: string;
    tier: 'entry' | 'mid' | 'pro' | 'flagship';
}

/** Galaxy category for the dashboard view */
export type GalaxyCategory = CategoryBucket;

export interface CategoryBucket {
    id: string;
    title: string;
    thumbnail: string;
    subCategories: SubCategory[];
}

export interface SubCategory {
    id: string;
    title: string;
    brands: string[];
}
