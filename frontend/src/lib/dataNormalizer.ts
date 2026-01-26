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
}

/**
 * Normalize a raw product from any brand to standard Product format
 * Handles differences in data structure across Roland, Boss, Nord, etc.
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function normalizeProduct(input: any): Product {
  const rawProduct = input as RawProductInput;
  // Start with a copy of the raw product
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const product: any = {
    id: rawProduct.id || "",
    name: rawProduct.name || "Unknown Product",
    brand: rawProduct.brand || "",
    category:
      rawProduct.category || rawProduct.main_category || "uncategorized",
    main_category:
      rawProduct.main_category || rawProduct.category || "uncategorized",
    description: rawProduct.description || "",

    // Image URL: Try multiple locations
    image_url:
      rawProduct.image_url || // Roland format
      rawProduct.image || // Alternative format
      rawProduct.media?.thumbnail || // Boss/Nord nested format
      rawProduct.media?.gallery?.[0] || // Gallery fallback
      "",

    // Pricing: Try multiple locations

    pricing: extractPrice(rawProduct),

    // Optional fields
    logo_url: rawProduct.logo_url,
    url: rawProduct.url || rawProduct.commercial?.link,
    sku: rawProduct.sku || rawProduct.halilit_id,
    status: rawProduct.status || "IN_STOCK",

    // Media/Gallery

    images: normalizeImages(rawProduct),
    official_gallery:
      rawProduct.official_gallery || rawProduct.media?.gallery || [],

    // Specs and details
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
    specifications:
      rawProduct.specifications ||
      rawProduct.specs ||
      rawProduct.official_specs,
    features: rawProduct.features || [],

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

    // Metadata
    verified: true,
  };

  return product as Product;
}

/**
 * Extract price from various data structures
 */
function extractPrice(product: RawProductInput): ProductPricing {
  // Try direct pricing object first
  if (product.pricing && typeof product.pricing === "object") {
    // We assume the raw pricing object matches sufficiently or cast it
    // Using unknown cast to break 'any' chain if needed, but here we just return it
    return product.pricing as ProductPricing;
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
  const images = product.images || [];

  // If empty, try to build from other sources
  if (!Array.isArray(images) || images.length === 0) {
    const imageUrl = product.image_url || product.image;
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
