/**
 * Data Normalizer: Handles different data structures from various brands
 * Normalizes all product data to a consistent format
 */

import type { Product, ProductImage, ProductPricing } from "../types";

// Loose interface for incoming raw data
interface RawProductInput {
  id?: string;
  name?: string;
  brand?: string;
  category?: string;
  main_category?: string;
  description?: string;
  image_url?: string;
  image?: string;
  media?: {
    thumbnail?: string;
    gallery?: string[];
  };
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  pricing?: any;
  price?: number;
  logo_url?: string;
  url?: string;
  commercial?: {
    link?: string;
    price?: number;
    description?: string;
  };
  sku?: string;
  halilit_id?: string;
  status?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  images?: any[];
  official_gallery?: string[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  specifications?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  specs?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  official_specs?: any;
  features?: string[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  official_manuals?: any;
  manual_urls?: string[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  necessities?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  accessories?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  related?: any;

  // v4.6.1 Standard
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ui_meta?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  processed_badge?: any;

  // Refinery v5 Legacy
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  pill_data?: any;
}

/**
 * Normalize a raw product from any brand to standard Product format
 * Handles differences in data structure across Roland, Boss, Nord, etc.
 * 
 * V6.0: Now supports IngestionProductDraft schema (halilit_id, product_name, etc.)
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function normalizeProduct(input: any): Product {
  const rawProduct = input as RawProductInput;

  // v6.0: Handle IngestionProductDraft schema with fallback to legacy formats
  // eslint-disable-next-line @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-explicit-any
  const identity = (input as any).identity || {};

  // Start with a copy of the raw product
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const product: any = {
    // Map from IngestionProductDraft fields (v6.0)
    id: rawProduct.halilit_id || rawProduct.id || "",
    name: rawProduct.product_name || rawProduct.name || identity.name || "Unknown Product",
    brand: rawProduct.brand || identity.brand || "",

    // Category from taxonomy (v6.0 canonical source)
    category:
      (typeof rawProduct.taxonomy === 'object' && rawProduct.taxonomy?.canonical_category) ||
      rawProduct.category ||
      rawProduct.main_category ||
      "uncategorized",
    main_category:
      (typeof rawProduct.taxonomy === 'object' && rawProduct.taxonomy?.canonical_category) ||
      rawProduct.main_category ||
      rawProduct.category ||
      "uncategorized",

    description:
      rawProduct.description_long ||
      rawProduct.description_short ||
      rawProduct.description ||
      rawProduct.official_description ||
      rawProduct.commercial?.description ||
      "",

    // v4.6.1 CRITICAL: Preserve Refinery Metadata
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    ui_meta: rawProduct.ui_meta || null,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    processed_badge: rawProduct.processed_badge || null,

    // Image URL: Try multiple locations (v6.0 supports official_images array)
    image_url:
      (Array.isArray(rawProduct.official_images) && rawProduct.official_images[0]?.url) || // IngestionProductDraft
      (typeof rawProduct.display === 'object' && rawProduct.display?.hero_image) ||
      rawProduct.image_url || // Roland format
      identity.images?.[0] || // Golden Identity format
      rawProduct.image || // Alternative format
      rawProduct.media?.thumbnail || // Boss/Nord nested format
      rawProduct.media?.gallery?.[0] || // Gallery fallback
      "",

    // Pricing: Extract from pricing object or fallback
    pricing: extractPrice(rawProduct),

    // Optional fields
    logo_url: rawProduct.logo_url,
    url: rawProduct.url || rawProduct.halilit_url || rawProduct.commercial?.link,
    sku: rawProduct.sku || rawProduct.halilit_id || rawProduct.id,
    status: rawProduct.status || "IN_STOCK",

    // Media/Gallery - support official_images from IngestionProductDraft
    images: normalizeImages(rawProduct),
    official_gallery:
      rawProduct.official_gallery ||
      (Array.isArray(rawProduct.official_images) ? rawProduct.official_images.map((img: any) => img.url) : []) ||
      rawProduct.media?.gallery ||
      [],

    // Specs and details
    specs: normalizeSpecs(
      rawProduct.specifications ||
      rawProduct.specs ||
      rawProduct.official_specs
    ),
    features: rawProduct.features || rawProduct.feature_list || [],

    // Documentation
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    official_manuals: rawProduct.official_manuals || rawProduct.manual_urls,

    // Relationships
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    necessities: rawProduct.necessities,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    accessories: rawProduct.accessories,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    related: rawProduct.related,

    // NEW: Refinery v5 Pill Data (The 3 Pillars)
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    pill_data: rawProduct.pill_data || null,

    // v6.0: Pass through IngestionProductDraft fields for advanced features
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    taxonomy: rawProduct.taxonomy || null,
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    display: rawProduct.display || null,
    official_specs: rawProduct.official_specs || null,
    official_images: rawProduct.official_images || [],
    official_url: rawProduct.official_url || null,
    reviews: rawProduct.reviews || [],
    review_synthesis: rawProduct.review_synthesis || null,
    average_rating: rawProduct.average_rating || null,
    data_completeness: rawProduct.data_completeness || 0,
    quality_score: rawProduct.quality_score || 0,
    description_long: rawProduct.description_long || "",
    description_short: rawProduct.description_short || "",

    // Metadata
    verified: true,
  };

  return product as Product;
}

/**
 * Extract price from various data structures
 */
function extractPrice(product: RawProductInput): ProductPricing {
  // Try direct pricing object first (IngestionProductDraft format)
  if (product.pricing && typeof product.pricing === "object") {
    return product.pricing as ProductPricing;
  }

  // Try IngestionProductDraft price_il field directly
  if (product.price_il !== undefined && product.price_il !== null) {
    return {
      regular_price: product.price_il,
      currency: "ILS",
    };
  }

  // Try nested commercial pricing
  if (
    product.commercial?.price !== undefined &&
    product.commercial.price !== null
  ) {
    return {
      regular_price: product.commercial.price,
      currency: "ILS",
    };
  }

  // Try direct price field
  if (product.price !== undefined && product.price !== null) {
    return {
      regular_price: product.price,
      currency: "ILS",
    };
  }

  // Return empty object if no pricing found
  return {};
}

/**
 * Normalize images array to consistent format
 */
function normalizeImages(product: RawProductInput): ProductImage[] {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
  const identityImages = (product as any).identity?.images;

  // Try official_images first (IngestionProductDraft format)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const officialImages = (product as any).official_images as any[];
  if (Array.isArray(officialImages) && officialImages.length > 0) {
    return officialImages.map(img => ({
      url: img.url || "",
      type: img.display_purpose || "gallery",
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
    })) as ProductImage[];
  }

  const images = product.images || identityImages || [];

  // If empty, try to build from other sources
  if (!Array.isArray(images) || images.length === 0) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    const imageUrl = product.image_url || product.image || (product as any).identity?.images?.[0];
    if (imageUrl) {
      return [
        {
          url: imageUrl,
          type: "main",
        },
      ];
    }
    return [];
  }

  // Assuming the array contains items compatible with ProductImage
  return images as ProductImage[];
}

/**
 * Batch normalize products
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function normalizeProducts(rawProducts: any[]): Product[] {
  if (!Array.isArray(rawProducts)) {
    return [];
  }

  return rawProducts.map((p) => {
    try {
      return normalizeProduct(p);
    } catch {
      return normalizeProduct({}); // Return empty normalized product
    }
  });
}

/**
 * Normalize specs to array format
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function normalizeSpecs(rawSpecs: any): { name: string; value: string }[] {
  if (!rawSpecs) return [];
  if (Array.isArray(rawSpecs)) return rawSpecs;
  if (typeof rawSpecs === "object") {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
    return Object.entries(rawSpecs).map(([key, val]) => ({
      name: key.replace(/_/g, " "),
      value: String(val),
    }));
  }
  return [];
}
