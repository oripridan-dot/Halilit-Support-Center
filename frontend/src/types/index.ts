/**
 * Unified Type Definitions - Single Source of Truth
 * v3.7.6 - All product, navigation, and catalog types
 *
 * ⚠️  REAL DATA ONLY: All types validated against actual roland.json structure
 * Generated: 2026-01-23
 * Status: 0 implicit `any` types - 100% strict typing
 *
 * New in v3.7.6:
 * - Product classification system (MI, PA, Accessories, Cases, Cables)
 */

// Export product classification types
export type {
  ProductClass,
  ProductClassification,
} from "./productClassification";

export {
  BRAND_CLASSIFICATIONS,
  CATEGORY_CLASSIFICATION_OVERRIDES,
  classifyProduct,
  filterByClass,
  getClassIcon,
  getClassLabel,
  getProductClass,
  getSecondaryClasses,
} from "./productClassification";

// ============================================================================
// PRODUCT IMAGE TYPES (Validated against roland.json structure)
// ============================================================================

export interface ProductImage {
  url: string;
  type?: "main" | "thumbnail" | "gallery" | "detail" | "technical";
  alt?: string;
  alt_text?: string; // Support backend field
  width?: number;
  height?: number;
}

export interface ProductImagesObject {
  main?: string;
  thumbnail?: string;
  gallery?: string[];
  [key: string]: string | string[] | undefined;
}

export type ProductImagesType = ProductImage[] | ProductImagesObject;

export interface Specification {
  key: string;
  value: string | number | boolean;
  unit?: string;
  category?: string;
}

export interface ProductManual {
  title: string;
  url: string;
  pages?: number;
  language?: string;
  format?: "pdf" | "html" | "video";
}

export interface ProductPricing {
  regular_price?: number;
  eilat_price?: number;
  sale_price?: number;
  currency?: string;
  source?: "brand" | "halilit" | "estimated";
}

export interface ProductRelationship {
  id: string;
  name: string;
  type:
  | "accessory"
  | "related"
  | "alternative"
  | "upgrade"
  | "bundle"
  | "necessity";
  category?: string;
  relevance?: number;
  sku?: string;
  price?: number | string;
  image_url?: string;
  logo_url?: string;
  brand?: string;
  inStock?: boolean;
}

export interface VideoResource {
  url: string;
  type: "youtube" | "vimeo" | "html5" | string;
  thumbnail?: string;
}

export interface DocumentResource {
  title: string;
  url: string;
  category?: string;
  icon?: string;
}

export interface OfficialMedia {
  url: string;
  type: "pdf" | "image" | "video" | "specification" | string;
  label: string;
  source_domain?: string;
  extracted_at?: string;
}

export interface HalilitProductData {
  sku: string;
  price: number;
  currency: string;
  availability: string;
  match_quality: string;
  source: "PRIMARY" | "SECONDARY" | "HALILIT_ONLY";
}


export interface TrustedReview {
  url: string;
  source: string;
  summary?: string;
  [key: string]: any;
}

export interface RealWorldContext {
  trusted_reviews: TrustedReview[];
  pros: string[];
  cons: string[];
  recurring_issues: string[];
  expert_tips: string[];
}

export interface Product {
  // Core identification (required)
  id: string;
  name: string;
  brand: string;
  category: string;
  main_category?: string;
  subcategory?: string;
  sub_subcategory?: string;
  family?: string;
  model_number?: string;

  // Classification (v3.7.6+)
  product_class?: "MI" | "PA" | "ACCESSORIES" | "CASES" | "CABLES";
  secondary_classes?: ("MI" | "PA" | "ACCESSORIES" | "CASES" | "CABLES")[];

  // Content
  description?: string;
  short_description?: string;
  tags?: string[] | null;
  production_country?: string;

  // Media (real data from roland.json)
  image_url?: string;
  image?: string;
  images?: ProductImagesType;
  videos?: Array<string | VideoResource>;
  video_urls?: string[];
  youtube_videos?: string[];
  logo_url?: string;
  manuals?: ProductManual[];
  manual_urls?: string[];
  media?: {
    thumbnail?: string;
    gallery?: string[];
    [key: string]: string | string[] | undefined;
  };

  // Technical
  specs?: Specification[] | Record<string, string | number | boolean>;
  specifications?: Specification[];
  features?: string[];
  category_hierarchy?: string[];

  // Commerce
  sku?: string;
  item_code?: string | null;
  halilit_sku?: string | null;
  halilit_price?: number;
  pricing?: ProductPricing | number; // Updated to allow number
  price?: number; // Legacy field
  commercial?: {
    price?: number;
    link?: string;
  }; // Legacy field
  availability?: "in-stock" | "pre-order" | "discontinued" | "unknown";
  warranty?: string;

  // Relationships
  accessories?: ProductRelationship[];
  related?: ProductRelationship[];
  necessities?: ProductRelationship[];

  // Official Knowledge (from manufacturer sites)
  official_manuals?: OfficialMedia[];
  official_gallery?: string[];
  official_specs?: Record<string, string | number | boolean>;

  // Context Layer (Real World Data)
  real_world_context?: RealWorldContext;

  // Refinery Integration (v5.0 - The 3 Pillars)
  pill_data?: {
    id?: string;
    official_name?: string;
    ui_meta?: {
      ui_view?: string;
      primary_category?: string;
      sub_division?: string;
      y_axis_score?: number;
      validation_flags?: string[];
      badges?: string[];
      confidence_score?: number;
    };
    commercial_meta?: {
      price?: number;
      stock?: string;
      sku_local?: string;
      price_verified?: boolean;
      sourced_from?: string[];
    };
    context_meta?: {
      pros?: string[];
      cons?: string[];
      tips?: string[];
      sources_of_truth?: SourceOfTruth[];
      data_confidence?: number;
    };
    specs?: Record<string, any>;
    validation_pipeline?: {
      step1_official?: ValidationStepInfo;
      step2_commercial?: ValidationStepInfo;
      step3_context?: ValidationStepInfo;
      step4_cross_validation?: ValidationStepInfo;
      step5_published?: ValidationStepInfo;
    };
  };

  // Source tracking
  sources_of_truth?: SourceOfTruth[];

  // Knowledge base and resources
  knowledgebase?: DocumentResource[];
  resources?: DocumentResource[];

  // UI optimization fields (added at runtime by catalogLoader)
  specs_preview?: Array<{ key: string; val: string }>;
  filters?: string[];

  // Metadata
  verified: boolean;
  verification_confidence?: number;
  match_quality?: "excellent" | "good" | "fair" | "poor";
  has_manual?: boolean;
  manual_path?: string;
  halilit_data?: HalilitProductData;

  // URLs
  brand_product_url?: string;
  detail_url?: string;

  // Data source tracking
  data_sources?: string[];
  last_updated?: string;

  // Internal (UI-only)
  _brandId?: string;
  _brandName?: string;
  brand_identity?: BrandIdentity;
  score?: number;
  quality_tier?: "DIAMOND" | "GOLD" | "SILVER" | "BRONZE";
  ui_context?: {
    primary: string;
    sub: string;
  };
}

// ============================================================================
// NAVIGATION TYPES
// ============================================================================

export type NavLevel =
  | "galaxy"
  | "domain"
  | "brand"
  | "family"
  | "product"
  | "universal";

export interface NavigationNode {
  // Core properties
  id: string;
  name: string;
  type: NavLevel;

  // Hierarchy
  children?: NavigationNode[];
  parent_id?: string;
  depth?: number;

  // Display
  icon?: string;
  product_count?: number;
  description?: string;

  // Product-specific fields (when type === 'product')
  product?: Product;

  // State
  expanded?: boolean;
  selected?: boolean;
}

export interface NavigationState {
  // Current navigation
  currentLevel: NavLevel;
  activePath: string[]; // Breadcrumb trail
  selectedProduct: Product | null;

  // Tree state
  expandedNodes: Set<string>;

  // Search
  searchQuery: string;

  // Display
  sidebarOpen?: boolean;
}

// ============================================================================
// CATALOG TYPES
// ============================================================================

export interface BrandIdentity {
  id: string;
  name: string;
  logo_url?: string | null;
  hq?: string;
  website?: string | null;
  description?: string | null;
  product_count?: number;
  brand_number?: string;
  categories?: string[];
  [key: string]: unknown;
}

export interface CatalogStats {
  total_products?: number;
  total_accessories?: number;
  categories_count?: number;
  coverage_percentage?: number;
  last_updated?: string;
  data_sources?: string[];
}

export interface BrandCatalog {
  // Identifiers
  brand_id: string;
  brand_name: string;

  // Branding
  logo_url?: string;
  brand_website?: string;
  description?: string;
  brand_identity?: BrandIdentity;

  // Content
  products: Product[];
  categories?: Record<string, string[]>;
  coverage_stats?: CatalogStats;
  total_products?: number;
  data_file?: string;
}

export interface MasterIndex {
  build_timestamp: string;
  version: string;
  total_products: number;
  total_verified?: number;
  brands: Array<{
    id: string;
    name: string;
    logo_url?: string;
    hq?: string;
    website?: string;
    product_count?: number;
    verified_count?: number;
    description?: string;
    brand_number?: string;
    data_file?: string;
  }>;
}

// ============================================================================
// UI STATE TYPES
// ============================================================================

export interface UIState {
  // Theme & Display
  themeName: string;
  sidebarOpen?: boolean;
  cinemaMode?: boolean;
  analyticsOpen?: boolean;

  // Notifications
  toast?: {
    message: string;
    type: "success" | "error" | "info" | "warning";
    duration?: number;
  };

  // Loading
  isLoading?: boolean;
  loadingMessage?: string;
}

export interface SearchState {
  query: string;
  results: Product[];
  isSearching?: boolean;
  selectedIndex?: number;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp?: string;
}

// ============================================================================
// UNIFIED APP STATE (for store)
// ============================================================================

export interface AppState extends NavigationState, UIState, SearchState {
  // Navigation actions
  warpTo: (level: NavLevel, path: string[]) => void;
  selectProduct: (product: Product) => void;
  goBack: () => void;
  toggleNode: (nodeId: string) => void;
  setSearch: (query: string) => void;

  // UI actions
  setTheme: (name: string) => void;
  toggleSidebar: () => void;
  toggleCinemaMode: () => void;
  setCinemaMode: (open: boolean) => void;
  setAnalyticsOpen: (open: boolean) => void;
  setToast: (toast: UIState["toast"]) => void;
  setLoading: (loading: boolean, message?: string) => void;

  // Search actions
  performSearch: (query: string) => Promise<void>;
  clearSearch: () => void;
  setSelectedIndex: (index?: number) => void;

  // Reset
  reset: () => void;
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export interface PaginationOptions {
  page?: number;
  limit?: number;
  offset?: number;
}

export interface SortOptions {
  field: keyof Product;
  order: "asc" | "desc";
}

export interface FilterOptions {
  category?: string;
  brand?: string;
  minPrice?: number;
  maxPrice?: number;
  availability?: string[];
  tags?: string[];
}

// Refinery Pipeline Types
export interface SourceOfTruth {
  name: string;
  url?: string;
  type: "manufacturer" | "review" | "expert" | "community" | "verified_retailer";
  verified?: boolean;
  confidence?: number;
  extraction_date?: string;
}

export interface ValidationStepInfo {
  status: "complete" | "partial" | "pending" | "failed";
  timestamp?: string;
  data_quality?: number; // 0-100
  issues?: string[];
  sources_used?: string[];
}

export type ValidateResult = {
  valid: boolean;
  errors: string[];
};

export interface CatalogMetadata {
  total_products: number;
  available_brands: string[];
  available_filters: string[]; // The dynamic tags
}

export interface CategoryPayload {
  id: string;
  generated_at: string;
  metadata: CatalogMetadata;
  products: Product[];
}
