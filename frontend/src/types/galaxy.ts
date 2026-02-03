/**
 * Halilit Galaxy UI 2.0 - Core Type Definitions
 * Strict TypeScript contracts to prevent future breakage
 */

export interface Product {
    uuid: string;
    name: string;
    brand: string;
    category: string;
    subCategory: string;
    image: string;
    price?: number;
    specs: Record<string, string>; // e.g., { "polyphony": "128", "weight": "10kg" }
    description: string;
    tier: 'entry' | 'mid' | 'pro' | 'flagship'; // For the Spectrum Tier Bar
}

export interface CategoryBucket {
    id: string;
    title: string;
    thumbnail: string; // Path to svg/webp
    subCategories: SubCategory[];
}

export interface SubCategory {
    id: string;
    title: string;
    brands: string[]; // List of brands in this subcategory (e.g., ["Nord", "Yamaha"])
}
