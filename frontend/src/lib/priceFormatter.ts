/**
 * Price Formatter and Extractor
 * Handles pricing data from different sources
 */

import type { Product } from "../types";

/**
 * Get displayable price from product
 * Tries multiple pricing locations
 */
export function getPrice(product: Product): string {
  // Try direct pricing object
  if (product.pricing) {
    if (typeof product.pricing === "number") {
      return formatPrice(product.pricing);
    }
    if (product.pricing.regular_price) {
      return formatPrice(product.pricing.regular_price);
    }
    if (product.pricing.eilat_price) {
      return formatPrice(product.pricing.eilat_price);
    }
  }

  // Try direct price field
  if (product.price && typeof product.price === "number") {
    return formatPrice(product.price);
  }

  // Try nested commercial pricing
  if (product.commercial?.price) {
    return formatPrice(product.commercial.price);
  }

  return "TBD";
}

/**
 * Format a price number for display
 */
export function formatPrice(price: number | string): string {
  if (!price) return "TBD";

  const numPrice = typeof price === "string" ? parseFloat(price) : price;

  if (isNaN(numPrice)) return "TBD";

  // Format with currency symbol
  return `₪${numPrice.toLocaleString("he-IL")}`;
}

/**
 * Extract numeric price value
 */
export function getPriceValue(product: Product): number {
  // Try direct pricing object
  if (product.pricing) {
    if (typeof product.pricing === "number") {
      return product.pricing;
    }
    if (
      product.pricing.regular_price &&
      typeof product.pricing.regular_price === "number"
    ) {
      return product.pricing.regular_price;
    }
  }

  // Try direct price field
  if (product.price && typeof product.price === "number") {
    return product.price;
  }

  // Try nested commercial pricing
  if (
    product.commercial?.price &&
    typeof product.commercial.price === "number"
  ) {
    return product.commercial.price;
  }

  return 0;
}
