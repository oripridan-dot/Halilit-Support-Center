/**
 * THE GALAXY STANDARD
 * This interface is the Single Source of Truth for the UI.
 */

export interface GalaxyProduct {
  // Core Identity
  id: string; // SKU or UUID
  name: string;
  brand: string; // Normalized (e.g., "Nord" not "Nord Keyboards")
  
  // Taxonomy
  category: string;
  subCategory: string;
  tier: "entry" | "mid" | "pro" | "flagship";
  
  // Visuals
  images: {
    main: string;
    thumbnail: string;
    gallery: string[];
  };
  
  // Commerce
  price: number;
  stockStatus: "in_stock" | "low_stock" | "out_of_stock" | "pre_order";
  
  // The "Brain" Data (For Frontend AI)
  aiTags: string[]; // e.g. ["warm sound", "analog", "vintage"]
  specs: Record<string, string>; // { "polyphony": "128", "weight": "10kg" }
  searchTokens: string; // Pre-computed search string for speed
}

export interface GalaxyCatalog {
  generatedAt: string;
  version: string;
  stats: {
    totalProducts: number;
    brandsCount: number;
  };
  products: GalaxyProduct[];
  categories: Record<string, string[]>; // Map Category -> SubCategories
}
