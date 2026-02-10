/**
 * Image Resolver v9.0 — Simplified
 *
 * The backend normalizer guarantees every product has a valid `image_url`.
 * This module is now a thin accessor with a transparent-pixel fallback,
 * not a 370-line fallback cascade.
 */

import type { Product } from "../types";

const TRANSPARENT_PIXEL =
  "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";

/**
 * Check if an image URL looks valid (basic sanity check).
 */
function isValidImageUrl(url: string | null | undefined): boolean {
  if (!url || typeof url !== "string") return false;
  if (url.includes("brand.com") || url.includes("example.com") || url === "undefined") {
    return false;
  }
  return url.startsWith("http") || url.startsWith("/") || url.startsWith("data:");
}

/**
 * Get a resolved image URL for a product.
 *
 * Priority (simple — backend already did the heavy lifting):
 * 1. image_url  (canonical, set by backend normalizer)
 * 2. display.hero_image.url
 * 3. First official_images entry
 * 4. Transparent pixel fallback
 */
export function resolveProductImage(product: Product | null | undefined): string {
  if (!product) return TRANSPARENT_PIXEL;

  // 1. Canonical field (backend-guaranteed for healthy products)
  const imageUrl = (product as any).image_url;
  if (isValidImageUrl(imageUrl)) return imageUrl;

  // 2. display.hero_image
  const heroImage = (product as any).display?.hero_image;
  if (heroImage) {
    const url = typeof heroImage === "object" ? heroImage.url : heroImage;
    if (isValidImageUrl(url)) return url;
  }

  // 3. First official image
  const officialImages = (product as any).official_images;
  if (Array.isArray(officialImages) && officialImages.length > 0) {
    const first = officialImages[0];
    const url = typeof first === "object" ? first.url : first;
    if (isValidImageUrl(url)) return url;
  }

  return TRANSPARENT_PIXEL;
}

/**
 * Generate a placeholder SVG for products with no image at all.
 */
export function generatePlaceholderImage(productName: string): string {
  const svg = `<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg">
    <rect width="300" height="300" fill="#1a1a1a"/>
    <text x="150" y="160" font-family="monospace" font-size="11" font-weight="bold"
      fill="#ff9900" text-anchor="middle" opacity="0.6">
      ${productName.substring(0, 15).toUpperCase()}
    </text>
  </svg>`;
  return `data:image/svg+xml;base64,${btoa(svg)}`;
}

/**
 * Batch resolve images for multiple products.
 */
export function resolveProductImages(
  products: Product[],
): Array<Product & { resolved_image_url: string }> {
  return products.map((product) => ({
    ...product,
    resolved_image_url: resolveProductImage(product),
  }));
}
