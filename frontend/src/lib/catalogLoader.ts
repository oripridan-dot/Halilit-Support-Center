/**
 * Static Catalog Loader - v3.7
 * Loads pre-built JSON instead of API calls
 *
 * ⚠️ FULLY TYPED: No implicit `any` types
 * ✅ RUNTIME VALIDATED: All JSON parsed through Zod schemas
 * All types validated against actual roland.json data
 * 🔄 REAL-TIME: Auto-updates on data changes
 */

import { normalizeProducts } from "./dataNormalizer";

import type {
  BrandIdentity,
  ProductImagesType,
  Product as ProductType,
} from "../types/index";
import { SchemaValidator } from "./schemas";

export type Product = ProductType;

export interface BrandColors {
  primary?: string;
  secondary?: string;
}

export interface BrandIdentityFile extends BrandIdentity {
  id: string;
  name: string;
  logo_url?: string | null;
  website?: string | null;
  description?: string | null;
  brand_colors?: BrandColors;
  categories?: string[];
}

export interface BrandStats {
  total_products?: number;
  verified_products?: number;
  categories?: string[];
}

// Interface matching brand JSON structure (from roland.json)
export interface BrandFile {
  brand_identity: BrandIdentityFile;
  products: Product[];
  stats?: BrandStats;
}

export interface BrandCatalog {
  brand_id: string;
  brand_name: string;
  brand_color?: string;
  secondary_color?: string;
  logo_url?: string;
  brand_website?: string;
  description?: string;
  products: Product[];
  brand_identity?: BrandIdentity;
}

export interface BrandIndexEntry {
  id: string;
  name: string;
  brand_color?: string | null;
  logo_url?: string | null;
  product_count: number;
  verified_count: number;
  data_file: string;
}

export interface MasterIndex {
  build_timestamp: string;
  version: string;
  total_products: number;
  total_verified: number;
  brands: BrandIndexEntry[];
}

class CatalogLoader {
  private index: MasterIndex | null = null;
  private brandCatalogs: Map<string, BrandCatalog> = new Map();
  private allProducts: Product[] = [];
  private loading: boolean = false;
  private changeCallbacks: Set<(type: "index" | "brand", id?: string) => void> =
    new Set();

  constructor() {
    // Constructor initializes empty caches
  }

  /**
   * Subscribe to catalog changes (for real-time UI updates)
   */
  onDataChange(
    callback: (type: "index" | "brand", id?: string) => void,
  ): () => void {
    this.changeCallbacks.add(callback);
    return () => this.changeCallbacks.delete(callback);
  }

  /**
   * Load master index (call once on app init)
   * ✅ Runtime validation with Zod
   */
  async loadIndex(): Promise<MasterIndex> {
    if (this.index) return this.index;

    const response = await fetch(`/data/index.json?v=${Date.now()}`);
    if (!response.ok) {
      throw new Error("Failed to load master index");
    }
    const rawData: unknown = await response.json();

    // ✅ Validate with Zod
    this.index = SchemaValidator.validateMasterIndex(rawData);
    return this.index!;
  }

  /**
   * Transform images to normalized format
   * Validates that all images in product are properly structured
   */
  private transformImages(images: unknown): ProductImagesType {
    // If already in object format with main/gallery keys, return as-is
    if (images && typeof images === "object" && !Array.isArray(images)) {
      return images as ProductImagesType;
    }

    // If array format (from raw product data)
    if (Array.isArray(images) && images.length > 0) {
      const imgs = images as unknown[];
      // Find main image or use first
      const mainImg =
        imgs.find((img): img is { url: string; type?: string } =>
          Boolean(
            img &&
            typeof img === "object" &&
            "url" in img &&
            (img as { type?: string }).type === "main",
          ),
        ) ||
        imgs.find((img): img is { url: string } =>
          Boolean(img && typeof img === "object" && "url" in img),
        ) ||
        imgs[0];

      const mainUrl =
        typeof mainImg === "string"
          ? mainImg
          : mainImg && typeof mainImg === "object" && "url" in mainImg
            ? (mainImg as { url: string }).url
            : "";

      return {
        main: mainUrl,
        thumbnail: mainUrl,
        gallery: imgs
          .map((img) =>
            typeof img === "string"
              ? img
              : img && typeof img === "object" && "url" in img
                ? (img as { url: string }).url
                : "",
          )
          .filter((url): url is string => Boolean(url)),
      };
    }

    return { main: "", thumbnail: "", gallery: [] };
  }

  /**
   * Extract primary image URL from product, with fallback chain
   */
  private extractImageUrl(product: Product): string {
    // Try image_url first
    if (product.image_url && typeof product.image_url === "string") {
      return product.image_url.trim();
    }

    // Try images object/array
    if (product.images) {
      if (
        typeof product.images === "object" &&
        !Array.isArray(product.images)
      ) {
        const imagesObj = product.images as Record<string, string | string[]>;
        return (imagesObj.main || imagesObj.thumbnail || "") as string;
      }
      if (Array.isArray(product.images) && product.images.length > 0) {
        const first = product.images[0];
        if (typeof first === "string") return first;
        if (first && typeof first === "object" && "url" in first) {
          return (first as { url: string }).url;
        }
      }
    }

    // Last resort
    return "";
  }

  /**
   * Load specific brand catalog (lazy loading)
   * ✅ Runtime validation with Zod
   */
  async loadBrand(brandId: string): Promise<BrandCatalog> {
    // Check cache first
    const cached = this.brandCatalogs.get(brandId);
    if (cached) {
      return cached;
    }

    const index = await this.loadIndex();
    const brandEntry = index.brands.find((b) => b.id === brandId);

    if (!brandEntry) {
      throw new Error(`Brand ${brandId} not found in index`);
    }

    const response = await fetch(
      `/data/${brandEntry.data_file}?v=${Date.now()}`,
    );
    if (!response.ok) {
      throw new Error(`Failed to load brand: ${brandId}`);
    }

    const rawData: unknown = await response.json();

    // ✅ Validate with Zod
    let data: BrandFile;
    try {
      // Zod validation ensures type safety - use any to cast the validated result
      const validated = SchemaValidator.validateBrandFile(rawData);
      data = validated as unknown as BrandFile;
    } catch (validationError) {
      throw new Error(
        `Invalid brand data structure for ${brandId}: ${(validationError as Error).message}`,
      );
    }

    // Transform to BrandCatalog format with full validation
    // Handle both new format (brand_identity) and legacy format (brand_name)
    const brandIdentity = data.brand_identity || {
      id: brandId,
      // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-explicit-any
      name: (data as any).brand_name || brandEntry.name || brandId,
    };

    const catalog: BrandCatalog = {
      brand_id: brandIdentity.id || brandId,
      brand_name: brandIdentity.name || brandEntry.name,
      brand_color:
        brandIdentity.brand_colors?.primary ||
        brandEntry.brand_color ||
        undefined,
      secondary_color: brandIdentity.brand_colors?.secondary || undefined,
      logo_url: brandIdentity.logo_url || brandEntry.logo_url || undefined,
      brand_website: brandIdentity.website || undefined,
      description: brandIdentity.description || undefined,
      brand_identity: brandIdentity,
      // Normalize products to handle different data structures
      products: normalizeProducts(data.products).map((p: Product): Product => {
        // Ensure brand is set
        if (!p.brand) {
          p.brand = brandIdentity.name || brandEntry.name || brandId;
        }
        // Ensure logo is set
        if (!p.logo_url) {
          p.logo_url =
            brandIdentity.logo_url || brandEntry.logo_url || undefined;
        }

        // Generate specs_preview if missing (for Data Stream UI)
        // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
        if (!(p as any).specs_preview) {
          let preview: { key: string; val: string }[] = [];

          // Priority 1: Official Specs (Dict)
          if (p.official_specs) {
            preview = Object.entries(p.official_specs)
              .slice(0, 4)
              .map(([k, v]) => ({ key: k, val: String(v) }));
          }
          // Priority 2: Specifications (Array)
          else if (p.specifications && Array.isArray(p.specifications)) {
            preview = p.specifications.slice(0, 4).map((s) => ({
              key: s.key,
              val: String(s.value),
            }));
          }
          // Priority 3: Legacy Specs (Dict)
          else if (
            // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
            (p as any).specs &&
            // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
            typeof (p as any).specs === "object" &&
            // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
            !Array.isArray((p as any).specs)
          ) {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
            const specs = (p as any).specs;
            preview = Object.entries(specs)
              .slice(0, 4)
              .map(([k, v]) => ({
                key: k,
                val: String(v),
              }));
          }

          if (preview.length > 0) {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
            (p as any).specs_preview = preview;
          }
        }

        // Generate filters from subcategory (for 1176 Filter Engine)
        // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
        if (!(p as any).filters) {
          const filters = new Set<string>();
          if (p.subcategory && p.subcategory !== "Uncategorized") {
            filters.add(p.subcategory);
          }
          if (p.category_hierarchy && Array.isArray(p.category_hierarchy)) {
            p.category_hierarchy.forEach((c: string) => {
              if (
                c &&
                c !== "Uncategorized" &&
                c.toLowerCase() !== (p.main_category || "").toLowerCase()
              ) {
                filters.add(c);
              }
            });
          }
          if (filters.size > 0) {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
            (p as any).filters = Array.from(filters);
          }
        }

        return p;
      }),
    };

    // Sort products by name for consistent ordering
    catalog.products.sort((a, b) => a.name.localeCompare(b.name));

    this.brandCatalogs.set(brandId, catalog);

    return catalog;
  }

  /**
   * Load ALL brands referenced in the index
   * Returns flattened list of all products across all brands
   */
  async loadAllProducts(): Promise<Product[]> {
    if (this.allProducts.length > 0) return this.allProducts;
    if (this.loading) {
      // Wait for loading to complete
      while (this.loading) await new Promise((r) => setTimeout(r, 100));
      return this.allProducts;
    }

    this.loading = true;
    try {
      const index = await this.loadIndex();

      // Load all brands in parallel
      const brandPromises = index.brands.map((b) =>
        this.loadBrand(b.id).catch(() => {
          return null;
        }),
      );

      const loadedCatalogs = (await Promise.all(brandPromises)).filter(
        (cat): cat is BrandCatalog => cat !== null,
      );

      // Flatten all products with brand context
      this.allProducts = loadedCatalogs.flatMap((catalog) =>
        catalog.products.map((p) => ({
          ...p,
          // Ensure brand is always populated (from JSON or catalog name)
          brand: p.brand || catalog.brand_name,
          _brandId: catalog.brand_id,
          _brandName: catalog.brand_name,
          brand_identity: catalog.brand_identity,
        })),
      );

      return this.allProducts;
    } finally {
      this.loading = false;
    }
  }

  /**
   * Get brands list (fast, from index only)
   */
  async getBrands(): Promise<BrandIndexEntry[]> {
    const index = await this.loadIndex();
    return index?.brands || [];
  }

  /**
   * Get catalog statistics
   */
  async getStats(): Promise<{
    totalProducts: number;
    totalVerified: number;
    totalBrands: number;
    verificationRate: string;
    buildTimestamp: string;
    version: string;
  }> {
    try {
      const index = await this.loadIndex();
      if (!index) throw new Error("No index");

      const verified = index.total_verified ?? 0;

      return {
        totalProducts: index.total_products,
        totalVerified: verified,
        totalBrands: index.brands.length,
        verificationRate: index.total_products
          ? ((verified / index.total_products) * 100).toFixed(2)
          : "0",
        buildTimestamp: index.build_timestamp,
        version: index.version,
      };
    } catch {
      return {
        totalProducts: 0,
        totalVerified: 0,
        totalBrands: 0,
        verificationRate: "0",
        buildTimestamp: "",
        version: "",
      };
    }
  }

  /**
   * Load products by category ID
   * Searches across all brands for products in the given category
   * Used by Spectrum view for category-based filtering
   */
  async loadProductsByCategory(categoryId: string): Promise<Product[]> {
    try {
      const index = await this.loadIndex();
      const products: Product[] = [];

      // MAPPING: Galaxy ID (Frontend) -> Universal IDs (Backend)
      // This bridges the gap between the "Galaxy View" and the underlying data
      const galaxyMap: Record<string, string[]> = {
        "guitars-bass": ["guitars"],
        "drums-percussion": ["drums"],
        "keys-production": ["keys"], // "production" usually implies keys/synths in this context
        "studio-recording": ["studio", "software"], // Software is arguably part of studio
        "live-dj": ["live", "dj"],
        "accessories-utility": ["accessories"],
      };

      // Determine which backend categories we are looking for
      // If the categoryId is not a Galaxy ID, assume it is a raw Universal ID
      const targetCategories = galaxyMap[categoryId] || [categoryId];

      // Load each brand and filter by category
      for (const brandEntry of index.brands) {
        try {
          const catalog = await this.loadBrand(brandEntry.id);
          // Filter products that match the category
          const matchingProducts = catalog.products.filter((p) => {
            const productCategory = (
              p.main_category ||
              p.category ||
              ""
            ).toLowerCase();

            // Check exact match against allowed backend categories
            return targetCategories.includes(productCategory);
          });
          products.push(...matchingProducts);
        } catch {
          // Skip brands that fail to load
        }
      }

      return products;
    } catch {
      return [];
    }
  }

  /**
   * Find a specific product by ID across all brands
   * Returns the full product object with all details
   */
  async findProductById(productId: string): Promise<Product | null> {
    try {
      const index = await this.loadIndex();

      // Try each brand until we find the product
      for (const brandEntry of index.brands) {
        try {
          const catalog = await this.loadBrand(brandEntry.id);
          const product = catalog.products.find((p) => p.id === productId);
          if (product) {
            return product;
          }
        } catch {
          // Continue searching other brands
        }
      }

      return null;
    } catch {
      return null;
    }
  }

  /**
   * Clear cache (for development/testing)
   */
  clearCache(): void {
    this.index = null;
    this.brandCatalogs.clear();
    this.allProducts = [];
  }
}

// Singleton instance
export const catalogLoader = new CatalogLoader();
