/**
 * v3.7.6 Static Catalog Library
 * Exports for easy importing - Zero backend dependency
 */

export { catalogLoader } from "./catalogLoader";
export type { BrandCatalog, MasterIndex, Product } from "./catalogLoader";
export { instantSearch } from "./instantSearch";
export type { SearchOptions } from "./instantSearch";

// Taxonomy Registry - Re-export from brandTaxonomy
export {
  BRAND_TAXONOMIES,
  getAllCategoryLabels,
  getBrandTaxonomy,
  getCategoryPath,
  getChildCategories,
  getRootCategories,
  normalizeCategory,
  validateCategory,
} from "./brandTaxonomy";
export type { BrandTaxonomy, CategoryNode } from "./brandTaxonomy";

// Helper functions for compatibility
export { getAvailableBrands } from "./brandTaxonomy";

// Dynamic Thumbnails (Most Expensive Product Selection)
export {
  buildDynamicThumbnailMap,
  getMostExpensiveProductImage,
  getThumbnailForCategory,
  getTopProductsByCategory,
} from "./dynamicThumbnails";
export type { CategoryThumbnail } from "./dynamicThumbnails";
