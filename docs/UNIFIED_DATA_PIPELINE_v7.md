# UNIFIED DATA PIPELINE ARCHITECTURE v7.0

## Complete System Alignment & Synchronization Guide

---

## Executive Summary

This document defines the **unified data pipeline** for the Halilit Support Center, ensuring all 3 screens consume data from a **single source of truth** with perfect naming consistency and type safety.

### The 3 Screens (Unified):

1. **GalaxyDashboard** - Main category browser
   - Data Source: `catalogLoader.loadAllProducts()`
   - Type: `Product[]` (filtered by `taxonomy.canonical_category`)
2. **SpectrumModule** - Product spectrum by brand & price
   - Data Source: `catalogLoader.loadAllProducts()`
   - Type: `Product[]` (grouped by `brand`, sorted by `price_il`)
   - Display: Horizontal tracks of products spread by price tier

3. **ProductPage** - Full product analysis & inspection
   - Data Source: `catalogLoader.findProductById(id)`
   - Type: `Product` (single, fully enriched)
   - Display: Complete specs, images, reviews, enrichment data

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────┐
│        BACKEND INGESTION PIPELINE                       │
│  (Halilit × Official × Community → UnifiedProduct)      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────────┐
│        CONDUCTOR VALIDATION GATES                       │
│  - Schema compliance (UnifiedProduct)                   │
│  - Naming consistency (all fields standardized)         │
│  - Data completeness (all images, specs, reviews)      │
│  - Cross-pipeline verification                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────────┐
│        FRONTEND DATA (JSON Catalogs)                    │
│  /frontend/public/data/brands/*.json                   │
└────────────────┬────────────────────────────────────────┘
                 │
         ┌───────┴────────┬────────────────┐
         ↓                ↓                ↓
    ┌─────────┐      ┌─────────┐      ┌─────────┐
    │  Screen │      │ Screen  │      │ Screen  │
    │    1    │      │   2     │      │   3     │
    │ Galaxy  │      │Spectrum │      │ Product │
    │DashBoard│      │ Module  │      │  Page   │
    └────┬────┘      └────┬────┘      └────┬────┘
         │                │                │
         └────────────────┴────────────────┘
                 ↓
        ┌──────────────────┐
        │ SINGLE DATA TYPE │
        │   UnifiedProduct │
        │ (via typeScript) │
        └──────────────────┘
```

---

## Unified Product Type Definition

### Frontend Type (TypeScript)

```typescript
// frontend/src/types/index.ts
export type Product = IngestionProductDraft;

// Maps to backend UnifiedProduct with these key fields:
interface UnifiedProduct {
  // IDENTITY (Required)
  id: string; // Unique product ID
  name: string; // Product name
  brand: string; // Brand name
  halilit_id: string; // Original SKU

  // PRICING (Required - Source of Truth: Halilit)
  price_il: number; // Primary Israel price (NIS)
  currency: string; // "ILS" (primary)
  pricing: Dict[PricePoint]; // All prices: {currency: {amount, region, ...}}
  pricing_tier: string; // "entry" | "mid" | "pro" | "flagship" | "legacy"

  // IMAGES
  images: ImageAsset[]; // Array: {url, alt, purpose, source}
  image_hero?: string; // Quick access (main image)
  image_thumbnail?: string; // Quick access (thumbnail)

  // SPECIFICATIONS
  specifications: {
    short_description?: string;
    long_description?: string;
    specs: Record<string, any>; // {polyphony, power, connectivity, ...}
    features: string[]; // Feature list
    sku?: string;
    model_number?: string;
    official_name?: string;
    official_url?: string;
  };

  // REVIEWS
  reviews: {
    average_rating?: number; // 0-5
    total_reviews: number;
    pros: string[];
    cons: string[];
    synthesis?: string;
    sources: string[];
  };

  // TAXONOMY (Required)
  taxonomy: {
    canonical_category: string; // "guitars-bass" | "drums-percussion" | ...
    canonical_subcategory: string; // "electric-guitars" | "synthesizers" | ...
    brand_specific_category?: string;
    keywords: string[];
  };

  // PROVENANCE
  provenance: {
    sources: string[]; // ["halilit", "official_brand", ...]
    halilit_confidence: number; // 0-1
    official_confidence: number; // 0-1
    community_confidence: number; // 0-1
    verification_status: string; // "approved" | "pending" | "rejected"
  };

  // STATUS
  status: string; // "approved" | "rejected" | ...
  in_stock: boolean;

  // TIMESTAMPS
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}
```

---

## Naming Conventions (Unified)

### Product Identity Fields

| Use Case     | Field Name   | Type   | Source                  |
| ------------ | ------------ | ------ | ----------------------- |
| Primary ID   | `id`         | string | Halilit ID (halilit_id) |
| Product Name | `name`       | string | Halilit + Brand         |
| Brand Name   | `brand`      | string | Halilit                 |
| Legacy SKU   | `halilit_id` | string | Halilit source          |

### Price Fields

| Use Case         | Field Name     | Type   | Source                      |
| ---------------- | -------------- | ------ | --------------------------- |
| Primary Price    | `price_il`     | number | Halilit (Israel mainland)   |
| Primary Currency | `currency`     | string | "ILS"                       |
| Price Tier       | `pricing_tier` | string | Computed from price range   |
| All Prices       | `pricing`      | Dict   | {currency: PricePoint, ...} |

**RULE**: All screens access price via `product.price_il` for primary display. Full pricing available in `product.pricing` object.

### Image Fields

| Use Case         | Field Name           | Type         | Source                                                 |
| ---------------- | -------------------- | ------------ | ------------------------------------------------------ |
| All Images       | `images`             | ImageAsset[] | Consolidated from all sources                          |
| Hero/Main        | `image_hero`         | string       | `images.find(img => img.purpose === "hero")?.url`      |
| Thumbnail        | `image_thumbnail`    | string       | `images.find(img => img.purpose === "thumbnail")?.url` |
| Legacy Fallbacks | `image`, `image_url` | string       | Same as `image_hero`                                   |

**RULE**: Primary display uses `images` array. Quick access via `image_hero`/`image_thumbnail` for compatibility.

### Category/Taxonomy Fields

| Use Case       | Field Name                         | Type     | Source                     |
| -------------- | ---------------------------------- | -------- | -------------------------- |
| Main Category  | `taxonomy.canonical_category`      | string   | Universal galaxy ID        |
| Subcategory    | `taxonomy.canonical_subcategory`   | string   | Universal spectrum tier    |
| Brand-Specific | `taxonomy.brand_specific_category` | string   | Brand's own categorization |
| Keywords       | `taxonomy.keywords`                | string[] | Search/discovery terms     |

**RULE**: All screens use `taxonomy` object. Never access legacy `category` or `tribe_id` fields.

---

## Screen-Specific Implementation

### Screen 1: GalaxyDashboard

```typescript
// Load all products, group by main category
const allProducts = await catalogLoader.loadAllProducts();
const galaxies = groupBy(allProducts, (p) => p.taxonomy.canonical_category);

// For each galaxy, show sub-categories
galaxies.forEach((galaxy) => {
  const subCategories = groupBy(
    galaxy,
    (p) => p.taxonomy.canonical_subcategory,
  );
  // Render sub-category slots with product counts
});
```

**Data Flow**:

1. Load: `catalogLoader.loadAllProducts()` → `Product[]`
2. Filter: By `taxonomy.canonical_category`
3. Display: Show subcategory slots with product counts from `taxonomy.canonical_subcategory`

**Key Fields Used**:

- `id`, `name`, `brand`
- `taxonomy.canonical_category` (main grouping)
- `taxonomy.canonical_subcategory` (sub-grouping)
- `image_hero` (thumbnail)
- `price_il` (if displayed)

---

### Screen 2: SpectrumModule (TierBar)

```typescript
// Load products for clicked subcategory
const products = await catalogLoader.loadProductsBySubcategory(subcategoryId);

// Group by brand
const brandTracks = groupBy(products, (p) => p.brand);

// Sort each track by price (price_il ascending)
brandTracks.forEach((track) => {
  track.sort((a, b) => a.price_il - b.price_il);
});

// Render horizontal tracks with products spread by price
```

**Data Flow**:

1. Load: `catalogLoader.loadAllProducts()` → filter by `taxonomy.canonical_subcategory`
2. Group: By `brand`
3. Sort: By `price_il` (ascending)
4. Display: Horizontal scrollable tracks

**Key Fields Used**:

- `id`, `name`, `brand`
- `price_il` (primary sort/display)
- `pricing_tier` (visual tier indicator)
- `image_hero` (product card)
- `in_stock` (stock status badge)
- `reviews.average_rating` (optional rating)

---

### Screen 3: ProductPage

```typescript
// Load single product with all enrichment
const product = await catalogLoader.findProductById(productId);

// Display complete information
renderFullPage({
  hero: product.image_hero,
  gallery: product.images,
  specs: product.specifications.specs,
  features: product.specifications.features,
  reviews: product.reviews,
  pricing: product.pricing,
  provenance: product.provenance,
});
```

**Data Flow**:

1. Load: `catalogLoader.findProductById(productId)` → `Product`
2. Display: All available fields

**Key Fields Used**:

- Complete `Product` object
- All `specifications` fields
- All `reviews` data
- All `images` (with purposes)
- Complete `pricing` object
- Complete `provenance` (sources, confidence)
- `taxonomy.keywords` (related products)

---

## Data Loading Functions (Single Source)

### CatalogLoader Class

```typescript
// frontend/src/lib/catalogLoader.ts

class CatalogLoader {
  // Load ALL products (used by GalaxyDashboard & SpectrumModule)
  async loadAllProducts(): Promise<Product[]>;

  // Load single product by ID (used by ProductPage)
  async findProductById(productId: string): Promise<Product | null>;

  // Load products by category (optimized for GalaxyDashboard)
  async loadProductsByCategory(categoryId: string): Promise<Product[]>;

  // Load products by subcategory (optimized for SpectrumModule)
  async loadProductsBySubcategory(subcategoryId: string): Promise<Product[]>;

  // Load products by brand (optimized for TierBar brand tracks)
  async loadProductsByBrand(brandName: string): Promise<Product[]>;

  // Load brand catalog with metadata
  async loadBrand(brandId: string): Promise<BrandCatalog>;

  // Load master index (brands, categories, stats)
  async loadIndex(): Promise<MasterIndex>;
}
```

**RULE**: All three screens MUST use `CatalogLoader` exclusively. No direct JSON loading in components.

---

## Validation Checkpoints

### Pre-Render Validation

Every product entering the UI must pass:

```python
# backend/data_pipeline_validator.py

def validate_product(product: UnifiedProduct) -> ValidationResult:
    # 1. Schema Compliance
    assert product.id, "Missing product ID"
    assert product.name, "Missing product name"
    assert product.brand, "Missing brand"
    assert product.price_il > 0, "Invalid price"
    assert product.taxonomy, "Missing taxonomy"

    # 2. Naming Consistency
    assert not product.get("image"), "Use 'images' array instead of 'image'"
    assert not product.get("tribe_id"), "Use 'taxonomy.canonical_category'"

    # 3. Data Completeness
    if product.specifications.specs:
        assert product.specifications.specs, "Specs should not be empty"

    # 4. Image Integrity
    for image in product.images:
        assert image.url, "Image must have URL"
        assert image.purpose, "Image must have purpose"

    return ValidationResult(is_valid=True)
```

### Conductor Validation Gates

```bash
# Validate pipeline before serving to UI
python backend/conductor_main.py validate

# Expected output:
# ✓ Frontend data (brands JSON)
# ✓ Backend data (ingestion outputs)
# ✓ Cross-screen consistency
# ✓ Schema compliance
# ✓ Naming conventions
# ✓ API contracts

# Full build + validate (recommended workflow)
python backend/conductor_main.py validate-sync
```

---

## Migration Path (v6.0 → v7.0)

### Step 1: Update Frontend Type

- ✅ Created: `backend/unified_schema.py` with `UnifiedProduct`
- ✅ Created: `backend/data_pipeline_validator.py`
- ✅ Update: `frontend/src/types/generated.ts` (auto-gen from schema)

### Step 2: Update Navigation Store

- ⏳ Rename: `PRODUCT_POP` → `PRODUCT_PAGE`
- ⏳ Update: All related handlers

### Step 3: Update Three Screens

- ⏳ GalaxyDashboard: Verify uses `taxonomy.canonical_category`
- ⏳ SpectrumModule: Verify uses `taxonomy.canonical_subcategory`, groups by `brand`
- ⏳ ProductPage: Enhance with full specifications display

### Step 4: Add Conductor Integration

- ✅ Created: Validation commands in Conductor
- ⏳ Create: Unified API endpoints

### Step 5: Testing

- ⏳ Run: `python backend/conductor_main.py validate-sync`
- ⏳ Verify: All 3 screens load same data
- ⏳ Audit: Naming consistency across codebase

---

## API Contracts (Backend)

### GET /api/products/all

Returns all products using unified schema.

```json
{
  "products": [UnifiedProduct],
  "total_count": 1234,
  "timestamp": "2026-02-06T..."
}
```

### GET /api/products/:id

Returns single product with all enrichment.

```json
{
  "product": UnifiedProduct,
  "timestamp": "2026-02-06T..."
}
```

### GET /api/products/by-category/:category

Returns products in category.

```json
{
  "products": [UnifiedProduct],
  "category": "guitars-bass",
  "count": 234,
  "timestamp": "2026-02-06T..."
}
```

### GET /api/products/by-brand/:brand

Returns products by brand, sorted by price.

```json
{
  "brand": "Nord",
  "products": [UnifiedProduct],
  "count": 45,
  "timestamp": "2026-02-06T..."
}
```

---

## Deployment Checklist

- [ ] Unified schema in place (`backend/unified_schema.py`)
- [ ] Validator running (`backend/data_pipeline_validator.py`)
- [ ] Conductor validates on build (`python conductor_main.py validate-sync`)
- [ ] Three screens use consistent data loading
- [ ] All image fields normalized to `images` array
- [ ] All price fields use `price_il` for primary
- [ ] All category fields use `taxonomy` object
- [ ] Navigation store updated (PRODUCT_POP → PRODUCT_PAGE)
- [ ] API endpoints return UnifiedProduct
- [ ] All tests pass (frontend + backend)

---

## Support & Troubleshooting

### "Products not showing in SpectrumModule"

→ Check: Are products being loaded from `catalogLoader.loadAllProducts()`?
→ Debug: `console.log(products)` to see data structure
→ Validate: Run `python backend/conductor_main.py validate`

### "Images not appearing"

→ Check: Is `images` array populated? Or legacy fields?
→ Convert: Use `image_hero` helper for quick access
→ Validate: `python backend/data_pipeline_validator.py`

### "Price tiers not calculating"

→ Check: Is `pricing_tier` computed?
→ Fallback: Derive from `price_il` value
→ Rules: entry (<500), mid (500-1500), pro (1500-4000), flagship (>4000)

---

Generated: February 6, 2026
Version: 7.0 (Unified Data Pipeline)
Status: IMPLEMENTATION PHASE
