/**
 * Zod Runtime Schema Validation - v3.7
 * Validates JSON catalog data at runtime
 *
 * Protects against:
 * - Missing required fields
 * - Type mismatches
 * - Malformed nested structures
 * - Backend generation errors
 */

import { z } from "zod";

// ============================================================================
// PRODUCT SCHEMAS
// ============================================================================

export const ProductImageSchema = z.object({
  url: z.string().min(1, "Image URL/Path required"), // Relaxed from .url() to support relative paths
  type: z
    .enum(["main", "thumbnail", "gallery", "detail", "technical"])
    .optional()
    .nullable(),
  alt: z.string().optional().nullable(),
  alt_text: z.string().optional().nullable(), // Added to support backend mismatch
  width: z.number().positive().optional().nullable(),
  height: z.number().positive().optional().nullable(),
});

export const ProductImagesObjectSchema = z.record(
  z.string(),
  z
    .union([z.string(), z.array(z.string())])
    .optional()
    .nullable(),
);

export const SpecificationSchema = z.object({
  key: z.string().min(1, "Specification key required"),
  value: z.union([z.string(), z.number(), z.boolean()]),
  unit: z.string().optional().nullable(),
  category: z.string().optional().nullable(),
});

export const ProductManualSchema = z.object({
  title: z.string().min(1, "Manual title required"),
  url: z.string().min(1, "Manual URL/Path required"), // Relaxed from .url()
  pages: z.number().positive().optional().nullable(),
  language: z.string().optional().nullable(),
  format: z.enum(["pdf", "html", "video"]).optional().nullable(),
});

export const ProductPricingSchema = z.object({
  regular_price: z.number().nonnegative().optional().nullable(),
  eilat_price: z.number().nonnegative().optional().nullable(),
  sale_price: z.number().nonnegative().optional().nullable(),
  currency: z.string().optional().nullable(),
  source: z.enum(["brand", "halilit", "estimated"]).optional().nullable(),
});

export const ProductRelationshipSchema = z.object({
  id: z.string().min(1, "Relationship ID required"),
  name: z.string().min(1, "Relationship name required"),
  type: z.enum(["accessory", "related", "alternative", "upgrade", "bundle"]),
  category: z.string().optional().nullable(),
  relevance: z.number().min(0).max(1).optional().nullable(),
});

// Core product schema - minimal required fields
// UPDATED v4.6.1: Supports both Flat (Normal) and Nested (Golden/Refinery) formats
export const ProductSchema = z
  .object({
    id: z.string().min(1, "Product ID required"),
    // Name can be at root OR inside identity
    name: z.string().optional().nullable(),
    brand: z.string().optional().nullable(),

    // Golden Context Support
    identity: z.object({
      name: z.string().optional(),
      brand: z.string().optional(),
      images: z.array(z.string()).optional()
    }).optional().nullable(),

    category: z.string().default("Uncategorized"),
    description: z.string().optional().nullable(),
    image_url: z.string().optional().nullable(),
    images: z
      .union([
        z.array(z.union([z.string(), ProductImageSchema])),
        ProductImagesObjectSchema,
      ])
      .optional()
      .nullable(),
    specifications: z.array(SpecificationSchema).optional().nullable(),
    manuals: z.array(ProductManualSchema).optional().nullable(),
    pricing: ProductPricingSchema.optional().nullable(),
    verified: z.boolean().default(true),
    relationships: z.array(ProductRelationshipSchema).optional().nullable(),
    // Allow additional fields from backend
  })
  .passthrough();

// ============================================================================
// BRAND SCHEMAS
// ============================================================================

export const BrandColorsSchema = z.object({
  primary: z
    .string()
    .regex(/^#[0-9a-f]{6}$/i, "Invalid hex color")
    .optional()
    .nullable(),
  secondary: z
    .string()
    .regex(/^#[0-9a-f]{6}$/i, "Invalid hex color")
    .optional()
    .nullable(),
});

export const BrandCategorySchema = z.object({
  id: z.string(),
  label: z.string(),
  icon: z.string().optional(),
  description: z.string().optional(),
  children: z.array(z.string()).optional(),
});

export const BrandIdentitySchema = z.object({
  id: z.string().min(1, "Brand ID required"),
  name: z.string().min(1, "Brand name required"),
  logo_url: z.string().optional().nullable(), // Relaxed from .url()
  website: z.string().optional().nullable(), // Relaxed from .url()
  description: z.string().optional().nullable(),
  brand_colors: BrandColorsSchema.optional().nullable(),
  categories: z
    .array(z.union([z.string(), BrandCategorySchema]))
    .optional()
    .nullable(),
});

export const BrandStatsSchema = z.object({
  total_products: z.number().nonnegative().optional().nullable(),
  verified_products: z.number().nonnegative().optional().nullable(),
  categories: z.array(z.string()).optional().nullable(),
});

export const BrandFileSchema = z
  .union([
    // Format 1: Object with products array (new format)
    z.object({
      brand_identity: BrandIdentitySchema.optional().nullable(),
      brand_name: z.string().optional().nullable(),
      products: z.array(ProductSchema),
      stats: BrandStatsSchema.optional(),
    }).passthrough(),
    // Format 2: Direct array of products (legacy format used in current data)
    z.array(ProductSchema).transform(products => ({
      products,
      brand_identity: undefined,
      brand_name: undefined,
      stats: undefined,
    })),
  ]);

// ============================================================================
// INDEX/CATALOG SCHEMAS
// ============================================================================

export const BrandIndexEntrySchema = z
  .object({
    id: z.string().min(1, "Brand ID required"),
    name: z.string().min(1, "Brand name required"),
    slug: z.string().optional(), // Added for compatibility
    brand_color: z
      .string()
      .regex(/^#[0-9a-f]{6}$/i, "Invalid hex color")
      .optional()
      .nullable(),
    logo_url: z.string().optional().nullable(), // Relaxed from .url()
    product_count: z.number().nonnegative(),
    verified_count: z.number().nonnegative().optional().default(0),
    data_file: z.string().min(1, "Data file path required"),
  })
  .passthrough(); // Allow other fields like 'last_updated' to pass through

export const MasterIndexSchema = z
  .object({
    build_timestamp: z.string(), // Relaxed from .datetime() to accept variations
    version: z.string().min(1, "Version required"),
    total_products: z.number().nonnegative(),
    total_verified: z.number().nonnegative().optional().default(0),
    brands: z.array(BrandIndexEntrySchema),
  })
  .passthrough();

// ============================================================================
// RUNTIME VALIDATORS (Safe parsing with error handling)
// ============================================================================

export class SchemaValidator {
  static validateProduct(data: unknown) {
    const result = ProductSchema.safeParse(data);
    if (!result.success) {
      throw new Error(
        `Invalid product data: ${result.error.errors[0].message}`,
      );
    }
    return result.data;
  }

  static validateBrandFile(data: unknown) {
    const result = BrandFileSchema.safeParse(data);
    if (!result.success) {
      throw new Error(`Invalid brand file: ${result.error.errors[0].message}`);
    }
    return result.data;
  }

  static validateMasterIndex(data: unknown) {
    const result = MasterIndexSchema.safeParse(data);
    if (!result.success) {
      throw new Error(`Invalid index: ${result.error.errors[0].message}`);
    }
    return result.data;
  }

  static validateBrandIndexEntry(data: unknown) {
    const result = BrandIndexEntrySchema.safeParse(data);
    if (!result.success) {
      throw new Error(`Invalid brand entry: ${result.error.errors[0].message}`);
    }
    return result.data;
  }
}
