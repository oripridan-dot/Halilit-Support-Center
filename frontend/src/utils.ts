/**
 * Utility functions — frontend/src/utils.ts
 */

import { ConductorProduct } from './hooks/useConductorCatalog';

/**
 * Converts a product's specs record into a plain text string suitable for
 * clipboard copy or AI context injection.
 * Format: "Key: Value\n"
 */
export function formatSpecsAsText(
    specs: Record<string, string | number | boolean | null | undefined> | null | undefined
): string {
    if (!specs || typeof specs !== 'object') return '';
    return Object.entries(specs)
        .filter(([, v]) => v != null && v !== '')
        .map(([k, v]) => `${k}: ${v}`)
        .join('\n');
}

/**
 * Format a price number as a locale-aware currency string.
 * Returns "Call for Price" if price is null/zero.
 */
export function formatPrice(
    price: number | null | undefined,
    currency = '₪'
): string {
    if (price == null || price === 0) return 'Call for Price';
    return `${currency}${price.toLocaleString('he-IL')}`;
}

/**
 * Returns true if a product has a valid, non-placeholder image.
 */
export function hasValidImage(product: Pick<ConductorProduct, 'hero_image'>): boolean {
    const src = product?.hero_image;
    return typeof src === 'string' && src.length > 0 && !src.includes('placeholder');
}
