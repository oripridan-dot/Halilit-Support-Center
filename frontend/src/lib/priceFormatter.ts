/**
 * Price Formatter and Extractor
 * Works with backend-normalized data (price field is now guaranteed to exist)
 */

import type { Product } from "../types";

/**
 * Get displayable price from product
 * Now works with backend-normalized price field
 */
export function getPrice(product: Product): string {
  // Top-level price field (from backend normalization)
  if (product.price && typeof product.price === "number" && product.price > 0) {
    return formatPrice(product.price, product.currency || "ILS");
  }

  // Fallback: price_il from ingestion format
  if (product.price_il && typeof product.price_il === "number" && product.price_il > 0) {
    return formatPrice(product.price_il, "ILS");
  }

  // Check pricing object
  if (product.pricing?.regular_price && product.pricing.regular_price > 0) {
    return formatPrice(product.pricing.regular_price, product.pricing.currency || "ILS");
  }

  return "TBD";
}

/**
 * Format a price number for display
 */
export function formatPrice(price: number | string, currency: string = "ILS", digits: number = 0): string {
  if (!price) return "TBD";

  const numPrice = typeof price === "string" ? parseFloat(price) : price;

  if (isNaN(numPrice) || numPrice === 0) return "TBD";

  const opts = { minimumFractionDigits: digits, maximumFractionDigits: digits };

  // Format based on currency
  if (currency === "ILS" || currency === "₪") {
    return `₪${numPrice.toLocaleString("he-IL", opts)}`;
  }

  if (currency === "USD" || currency === "$") {
    return `$${numPrice.toLocaleString("en-US", opts)}`;
  }

  // Default: shekel format
  return `₪${numPrice.toLocaleString("he-IL", opts)}`;
}

/**
 * Extract numeric price value
 */
export function getPriceValue(product: Product): number {
  if (product.price && typeof product.price === "number") {
    return product.price;
  }
  if (product.price_il && typeof product.price_il === "number") {
    return product.price_il;
  }
  if (product.pricing?.regular_price) {
    return product.pricing.regular_price;
  }
  return 0;
}
