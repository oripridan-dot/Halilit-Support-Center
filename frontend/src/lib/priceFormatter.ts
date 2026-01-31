/**
 * Price Formatter and Extractor
 * Aligned with OptimizedProduct type from pipeline
 */

import type { Product } from "../types";

/**
 * Get displayable price from product
 */
export function getPrice(product: Product): string {
  // Direct price field (from OptimizedProduct)
  if (product.price && typeof product.price === "number") {
    return formatPrice(product.price, product.currency);
  }

  return "TBD";
}

/**
 * Format a price number for display
 */
export function formatPrice(price: number | string, currency?: string): string {
  if (!price) return "TBD";

  const numPrice = typeof price === "string" ? parseFloat(price) : price;

  if (isNaN(numPrice)) return "TBD";

  // Format based on currency
  if (currency === "ILS" || currency === "₪") {
    return `₪${numPrice.toLocaleString("he-IL")}`;
  }
  
  if (currency === "USD" || currency === "$") {
    return `$${numPrice.toLocaleString("en-US")}`;
  }

  // Default: shekel format
  return `₪${numPrice.toLocaleString("he-IL")}`;
}

/**
 * Extract numeric price value
 */
export function getPriceValue(product: Product): number {
  if (product.price && typeof product.price === "number") {
    return product.price;
  }
  return 0;
}
