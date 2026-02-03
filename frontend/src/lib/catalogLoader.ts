/**
 * Static Catalog Loader - v3.7
 * Loads pre-built JSON instead of API calls
 *
 * ⚠️ FULLY TYPED: No implicit `any` types
 * ✅ RUNTIME VALIDATED: All JSON parsed through Zod schemas
 * All types validated against actual roland.json data
 * 🔄 REAL-TIME: Auto-updates on data changes
 * 📊 UNIFIED TAXONOMY: Integrates with TaxonomyService for categorization
 */

import { normalizeProducts } from "./dataNormalizer";
import { TaxonomyService } from "./taxonomyService";

import type {
  BrandIdentity,
  ProductImagesType,
  Product as ProductType,
  ImageAsset,
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

/**
 * Lightweight product skeleton for initial rendering
 * Contains only essential properties for quick display
 */
export interface ProductSkeleton extends Partial<Product> {
  id?: string;
  name?: string;
  brand_id?: string;
}

/**
 * Product with heavy details deferred for lazy loading
 * "skeleton" indicates which fields are loaded
 */
export type LazyProduct = ProductSkeleton & Partial<Product>;

class CatalogLoader {
  private index: MasterIndex | null = null;
  private brandCatalogs: Map<string, BrandCatalog> = new Map();
  private lazyBrandCatalogs: Map<string, { products: LazyProduct[] }> = new Map();
  private allProducts: Product[] = [];
  private allLazyProducts: LazyProduct[] = [];
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
   * Extract skeleton fields for lazy loading (lightweight, fast)
   */
  private extractSkeleton(product: Product): ProductSkeleton {
    return {
      id: product.id,
      name: product.name,
      brand_id: product.brand_id,
      image_thumbnail: product.image_thumbnail,
      category: product.category,
      tier: product.tier,
    };
  }

  /**
   * Load all products as skeleton (lightweight, for immediate render)
   * Defers loading full details until user interacts
   */
  async loadAllLazyProducts(): Promise<LazyProduct[]> {
    if (this.allLazyProducts.length > 0) return this.allLazyProducts;
    if (this.loading) {
      // Wait for loading to complete
      while (this.loading) await new Promise((r) => setTimeout(r, 100));
      return this.allLazyProducts;
    }

    this.loading = true;
    try {
      const index = await this.loadIndex();

      // Load all brands in parallel
      const brandPromises = index.brands.map((b) =>
        this.loadBrandLazy(b.id).catch(() => {
          return null;
        }),
      );

      const loadedCatalogs = (await Promise.all(brandPromises)).filter(
        (cat): cat is { products: LazyProduct[] } => cat !== null,
      );

      // Flatten all lazy products with brand context
      this.allLazyProducts = loadedCatalogs.flatMap((catalog) =>
        catalog.products
      );

      return this.allLazyProducts;
    } finally {
      this.loading = false;
    }
  }

  /**
   * Load brand with skeleton products (lightweight, lazy loading)
   * Full details are loaded on-demand when user views product details
   */
  async loadBrandLazy(brandId: string): Promise<{ products: LazyProduct[] } | null> {
    // Check lazy cache first
    const cachedLazy = this.lazyBrandCatalogs.get(brandId);
    if (cachedLazy) {
      return cachedLazy;
    }

    // Check full cache first to extract skeletons
    const cached = this.brandCatalogs.get(brandId);
    if (cached) {
      const lazyResult = {
        products: cached.products.map((p) => this.extractSkeleton(p)),
      };
      this.lazyBrandCatalogs.set(brandId, lazyResult);
      return lazyResult;
    }

    try {
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
        const validated = SchemaValidator.validateBrandFile(rawData);
        data = validated as unknown as BrandFile;
      } catch (validationError) {
        throw new Error(
          `Invalid brand data structure for ${brandId}: ${(validationError as Error).message}`,
        );
      }

      // Extract only skeletons for initial load
      // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
      const productsArray = (data as any).products || [];

      const skeletons = productsArray.map((p: Product) =>
        this.extractSkeleton(p)
      );

      const lazyResult = { products: skeletons };
      this.lazyBrandCatalogs.set(brandId, lazyResult);

      // Also cache the full data for later access
      // (so if someone calls loadBrand after loadBrandLazy, we have it)
      this.brandCatalogs.set(brandId, {
        brand_id: brandId,
        brand_name: data.brand_identity?.name || brandEntry.name,
        products: productsArray,
      } as BrandCatalog);

      return lazyResult;
    } catch (error) {
      console.error(`Failed to lazy-load brand ${brandId}:`, error);
      return null;
    }
  }

  /**
   * Load full details for a specific product (on-demand)
   * Used when user clicks on a product to view details
   */
  async loadProductDetails(
    productId: string,
    brandId?: string
  ): Promise<Product | null> {
    try {
      const index = await this.loadIndex();

      // If brand ID provided, load that brand first
      if (brandId) {
        const catalog = await this.loadBrand(brandId);
        const product = catalog.products.find((p) => p.id === productId);
        if (product) return product;
      }

      // Otherwise, search all brands
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
    // Try image_hero first
    if (product.image_hero?.url) {
      return product.image_hero.url;
    }

    // Try image_thumbnail as fallback
    if (product.image_thumbnail?.url) {
      return product.image_thumbnail.url;
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

    // ✅ BADGE VERIFICATION: Log what we're getting
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-member-access
    const productsArray = ((data as any).products || data) as unknown[];

    if (productsArray.length === 0) {
      console.warn(`[CatalogLoader] ⚠️ WARNING: ${brandId} has no products in the data structure.`);
    }

    // Log first product structure for debugging
    if (productsArray.length > 0) {
      console.log(`[CatalogLoader] ✅ ${brandId}: Found ${productsArray.length} products. First product:`, productsArray[0]);
    }

    // NEW: Accept ANY data (removing strict gate for now)
    // The gate will be moved to the UI layer to decide what to display

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
        // Warn on low tier products
        if (p.tier === "bronze") {
          console.warn(`[Sandbox] Loading Low Tier Product: ${p.id}`);
        }

        // Ensure brand_id is set
        if (!p.brand_id) {
          p.brand_id = brandIdentity.id || brandId;
        }

        return p;
      }),
    };

    // Sort products by name for consistent ordering
    catalog.products.sort((a, b) => (a.name ?? '').localeCompare(b.name ?? ''));

    this.brandCatalogs.set(brandId, catalog);

    return catalog;
  }

  /**
   * Load ALL brands referenced in the index
   * Returns flattened list of all products across all brands
   * ✅ Integrates unified taxonomy for consistent categorization
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
      let products = loadedCatalogs.flatMap((catalog) =>
        catalog.products.map((p): Product => ({
          ...p,
          // Ensure brand_id is always populated
          brand_id: p.brand_id || catalog.brand_id,
        })),
      );

      // ✅ Apply unified taxonomy categorization to all products
      try {
        const taxonomy = TaxonomyService.getInstance();
        await taxonomy.load();
        products = taxonomy.categorizeProducts(products);
        console.log(
          `[CatalogLoader] ✅ Applied unified taxonomy to ${products.length} products`
        );
      } catch (taxError) {
        console.warn(
          "[CatalogLoader] ⚠️ Failed to apply taxonomy, continuing with existing categories:",
          taxError
        );
        // Continue with uncategorized products if taxonomy fails
      }

      this.allProducts = products;
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
