/**
 * Price Formatter v9.0 — Simplified
 *
 * Backend normalizer guarantees `price` and `price_il` are always > 0.
 * No more 3-way fallback chains.
 */

import type { Product } from "../types";

/**
 * Get displayable price string from a product.
 */
export function getPrice(product: Product): string {
  const value = getPriceValue(product);
  return value > 0 ? formatPrice(value, "ILS") : "TBD";
}

/**
 * Format a numeric price for display.
 */
export function formatPrice(price: number | string, currency: string = "ILS", digits: number = 0): string {
  const numPrice = typeof price === "string" ? parseFloat(price) : price;
  if (!numPrice || isNaN(numPrice)) return "TBD";

  const opts = { minimumFractionDigits: digits, maximumFractionDigits: digits };

  if (currency === "USD" || currency === "$") {
    return `$${numPrice.toLocaleString("en-US", opts)}`;
  }
  return `₪${numPrice.toLocaleString("he-IL", opts)}`;
}

/**
 * Extract the numeric price value from a product.
 * Backend guarantees `price` exists, but we keep one fallback for safety.
 */
export function getPriceValue(product: Product): number {
  return (product as any).price || product.price_il || product.pricing?.price_il || 0;
}
