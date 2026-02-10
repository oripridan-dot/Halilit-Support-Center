/**
 * Price Formatter and Extractor
 * Works with both conductor API shape and static JSON shape
 */

import type { Product } from "../types";

/**
 * Get displayable price from product
 * Handles: conductor API (price field), static JSON (price_il), pricing object
 */
export function getPrice(product: Product): string {
  // price_il is the canonical field from IngestionProductDraft
  if (product.price_il && typeof product.price_il === "number" && product.price_il > 0) {
    return formatPrice(product.price_il, "ILS");
  }

  // Conductor API also adds a top-level "price" field
  const topPrice = (product as any).price;
  if (topPrice && typeof topPrice === "number" && topPrice > 0) {
    return formatPrice(topPrice, "ILS");
  }

  // Check pricing object
  if (product.pricing?.price_il && product.pricing.price_il > 0) {
    return formatPrice(product.pricing.price_il, "ILS");
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

  if (currency === "USD" || currency === "$") {
    return `$${numPrice.toLocaleString("en-US", opts)}`;
  }

  // Default: ILS format
  return `₪${numPrice.toLocaleString("he-IL", opts)}`;
}

/**
 * Extract numeric price value
 */
export function getPriceValue(product: Product): number {
  if (product.price_il && typeof product.price_il === "number") {
    return product.price_il;
  }
  const topPrice = (product as any).price;
  if (topPrice && typeof topPrice === "number") {
    return topPrice;
  }
  if (product.pricing?.price_il) {
    return product.pricing.price_il;
  }
  return 0;
}
