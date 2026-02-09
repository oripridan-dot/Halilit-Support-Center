/**
 * Image Resolver: Ensures every product has a valid image URL
 * Aligned with OptimizedProduct type from pipeline
 */

import type { Product } from "../types";

export const PLACEHOLDER_COLORS = {
  primary: "#1a1a1a",
  accent: "#ff9900",
};

// Map categories to local thumbnail assets (public/assets/thumbs/)
// REMOVED: User prefers "real" images only or raw placeholder
/*
const CATEGORY_THUMB_MAP: Record<string, string> = {
  ...
};
*/


// Transparent pixel for "no image" state (User request: "real images only")
const TRANSPARENT_PIXEL = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";

/**
 * Resolve a valid image URL for a product
 * Uses: image_hero > image_thumbnail > image_gallery > placeholder
 */
export function resolveProductImage(
  product: Product | null | undefined,
): string {
  if (!product) {
    return TRANSPARENT_PIXEL;
  }

  // 1. Try hero image (new structure: display.hero_image.url OR top-level image_url)
  if (product.image_url && isValidImageUrl(product.image_url)) {
    return product.image_url;
  }

  // Legacy structure support
  if (product.image_hero?.url && isValidImageUrl(product.image_hero.url)) {
    return product.image_hero.url;
  }

  // Try display object structure
  if (product.display?.hero_image?.url && isValidImageUrl(product.display.hero_image.url)) {
    return product.display.hero_image.url;
  }

  // 2. Try thumbnail image
  if (product.image_thumbnail?.url && isValidImageUrl(product.image_thumbnail.url)) {
    return product.image_thumbnail.url;
  }

  // 3. Try first gallery image
  if (product.image_gallery && product.image_gallery.length > 0) {
    const firstImage = product.image_gallery[0];
    if (firstImage?.url && isValidImageUrl(firstImage.url)) {
      return firstImage.url;
    }
  }

  // 4. Return transparent pixel (No generated placeholders)
  return TRANSPARENT_PIXEL;
}


/**
 * Check if image URL looks valid
 */
function isValidImageUrl(url: string): boolean {
  if (!url || typeof url !== "string") return false;

  // Accept URLs with image extensions or cloudfront URLs
  const imageExtensions = /\.(jpg|jpeg|png|gif|svg|webp)$/i;
  // Reject known dummy domains
  if (url.includes("brand.com") || url.includes("example.com")) return false;

  return imageExtensions.test(url) || url.includes("cloudfront.net");
}

/**
 * Resolve category thumbnail based on product metadata
 * DISABLED: User requested "only real images"
 */
/*
function resolveCategoryThumbnail(product: Product): string | null {
 ...
}
*/


/**
 * Generate a data URL placeholder image
 */
export function generatePlaceholderImage(_productName: string): string {
  const svg = `<svg width="300" height="300" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:${PLACEHOLDER_COLORS.primary};stop-opacity:1" />
        <stop offset="100%" style="stop-color:#0a0a0a;stop-opacity:1" />
      </linearGradient>
    </defs>
    <rect width="300" height="300" fill="url(#grad)"/>
    <circle cx="150" cy="120" r="50" fill="${PLACEHOLDER_COLORS.accent}" opacity="0.2"/>
    <rect x="40" y="190" width="220" height="80" fill="${PLACEHOLDER_COLORS.accent}" opacity="0.15" rx="4"/>
    <text x="150" y="275" font-family="monospace" font-size="11" font-weight="bold" fill="${PLACEHOLDER_COLORS.accent}" text-anchor="middle" opacity="0.6">
      LOADING IMAGE...
    </text>
  </svg>`;
  return `data:image/svg+xml;base64,${btoa(svg)}`;
}

/**
 * Batch resolve images for multiple products
 */
export function resolveProductImages(
  products: Product[],
): Array<Product & { resolved_image_url: string }> {
  return products.map((product) => ({
    ...product,
    resolved_image_url: resolveProductImage(product),
  }));
}
