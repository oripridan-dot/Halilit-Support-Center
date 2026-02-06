/**
 * Data Normalizer - LEGACY (Disabled)
 * 
 * ⭐ DEPRECATED: All normalization now happens in backend with Conductor
 * This file kept for reference only - DO NOT USE
 * 
 * Backend (conductor_data_sync.py) handles:
 * - Price extraction (price_il → price + currency)
 * - Image normalization (official_images → image_hero, image_thumbnail, image_gallery)
 * - Taxonomy mapping
 * - Specification extraction
 * 
 * Frontend receives ALREADY-NORMALIZED data from /data/*.json
 */

import type { Product } from "../types";

/**
 * PASS-THROUGH: Frontend data is already normalized by backend Conductor
 * This function exists only for backwards compatibility - it does nothing
 */
export function normalizeProduct(input: any): Product {
  // Backend has already normalized all fields
  // Just return the input as-is
  return input as Product;
}

/**
 * PASS-THROUGH: Batch normalization (all work done backend)
 */
export function normalizeProducts(products: any[]): Product[] {
  // Backend already normalized - return as-is
  return products as Product[];
}


