/**
 * Brand Logo Helper - Maps brands to logo paths
 * Extracts brands from products in each category for visual display
 */

import type { Product } from "../types";

// Map brand names to their logo file names (in public/assets/logos/)
const BRAND_LOGO_MAP: Record<string, string> = {
    nord: "nord_logo.png",
    roland: "roland_logo.png",
    moog: "moog_logo.png",
    boss: "boss_logo.png",
    korg: "korg_logo.png", // Fallback if exists
    yamaha: "yamaha_logo.png", // Fallback
    rode: "rode_logo.png", // Assuming exists
    shure: "shure_logo.png", // Assuming exists
    "drumdots": "drumdots_logo.png",
    "universal audio": "universal-audio_logo.jpg",
    "universal-audio": "universal-audio_logo.jpg",
};

/**
 * Get logo URL for a brand
 */
export function getBrandLogoUrl(brandName: string): string | null {
    const normalized = brandName.toLowerCase().trim();
    const logoFile = BRAND_LOGO_MAP[normalized];

    if (!logoFile) {
        return null;
    }

    return `/assets/logos/${logoFile}`;
}

/**
 * Extract unique brands from products in a specific category
 */
export function extractBrandsForCategory(
    products: Product[] | any[],
    categoryId: string
): string[] {
    const uniqueBrands = new Set<string>();

    products.forEach((product: any) => {
        // Check if product belongs to this category
        const productCategory = product.taxonomy?.canonical_category
            || product.category
            || (typeof product === 'object' ? Object.values(product).find(v => typeof v === 'string' && v.includes(categoryId)) : null);

        // Simple string matching (adjust based on your category mapping)
        if (productCategory && productCategory.toString().includes(categoryId)) {
            if (product.brand) {
                uniqueBrands.add(product.brand);
            }
        }
    });

    return Array.from(uniqueBrands).sort();
}

/**
 * Get top brands (with logos) for a category
 * Returns array of { brand, logoUrl } objects, limited to N brands
 */
export function getTopBrandsForCategory(
    products: Product[] | any[],
    categoryId: string,
    limit: number = 5
): Array<{ brand: string; logoUrl: string | null }> {
    const brands = extractBrandsForCategory(products, categoryId);

    return brands
        .slice(0, limit)
        .map((brand) => ({
            brand,
            logoUrl: getBrandLogoUrl(brand),
        }));
}

/**
 * Get brands with valid logos for a category
 */
export function getBrandsWithLogos(
    products: Product[] | any[],
    categoryId: string,
    limit: number = 5
): Array<{ brand: string; logoUrl: string }> {
    return getTopBrandsForCategory(products, categoryId, limit)
        .filter((b) => b.logoUrl !== null)
        .map((b) => ({ brand: b.brand, logoUrl: b.logoUrl! }));
}
