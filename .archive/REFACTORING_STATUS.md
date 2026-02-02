# Frontend Refactoring Status

## Objective

Align the frontend components with the backend's `OptimizedProduct` data structure.

## Completed Tasks ✅

### 1. Type Regeneration

- ✅ Regenerated TypeScript types from Pydantic models
- ✅ Updated `frontend/src/types/generated.ts` with correct `OptimizedProduct` interface

### 2. Component Refactoring

- ✅ **ProductDetailPanel.tsx** - Completely refactored to use OptimizedProduct properties:
  - Changed `product.brand` → `product.brand_id`
  - Changed `product.description` → `product.description_full || product.description_short`
  - Replaced `product.sku` access (not available in OptimizedProduct)
  - Updated pros/cons/tips sources from direct properties instead of nested `pill_data`
  - Removed dependencies on non-existent `pill_data`, `context_meta`, `commercial_meta` properties

- ✅ **ProductCard.tsx** - Simplified to use OptimizedProduct:
  - Removed `processed_badge`, `identity`, `context` dependencies
  - Used `tier` and `tier_score` from OptimizedProduct
  - Used `brand_id` instead of `brand`
  - Used `pros` directly from product

- ✅ **ProductPopInterface.tsx** - Completely refactored to simplified version:
  - Removed 800+ lines of complex nested component logic
  - Now uses OptimizedProduct directly
  - Shows: image hero/gallery, descriptions, specs, insights (pros/cons/tips)
  - Uses `brand_id`, `category`, `price`, `currency`, `stock_status`, `tier`, `tier_score`

- ✅ **TierBar.tsx** - Fixed property access:
  - Changed `p.score` → `p.tier_score`
  - Changed `node.product.brand` → `node.product.brand_id`
  - Changed `node.product.logo_url` to fallback brand_id text

## Remaining Issues ⚠️

### Critical Build Errors (60+ errors)

The following files still reference properties that don't exist in `OptimizedProduct`:

#### High Priority (Component & View Layer)

1. **SpectrumModule.tsx**
   - `product.processed_badge` - doesn't exist
   - `product.identity` - doesn't exist
   - `product.context` - doesn't exist
   - `product.image` / `product.image_url` - should be `product.image_hero` / `product.image_thumbnail`
   - `product.verified` - doesn't exist
   - `product.pricing` - should be `product.price` + `product.currency`

2. **useCategoryCatalog.ts (Hook)**
   - `product.filters` - should be `product.filter_tags`

3. **useRealtimeSearch.ts**
   - Missing `NodeJS` namespace for types

#### Medium Priority (Lib Layer - Data Processing)

4. **catalogLoader.ts** (LARGEST)
   - `product.brand` - should be `product.brand_id`
   - `product.image_url` - should be `product.image_hero?.url` or `product.image_thumbnail?.url`
   - `product.main_category` - should be `product.category`
   - `product.processed_badge` - doesn't exist
   - `product.official_specs` / `product.specifications` - should be `product.specs`
   - `product.subcategory` - should be `product.subcategories` (array)
   - `product.category_hierarchy` - should be `product.subcategories`
   - ~50 error locations

5. **categoryConsolidator.ts**
   - `product.ui_context` - doesn't exist

6. **taxonomyService.ts**
   - `product.main_category` - should be `product.category`
   - `product.brand` - should be `product.brand_id`
   - Constructor access issue (private)
   - ~15 error locations

## Backend Data Structure Reference

The `OptimizedProduct` from backend/pipeline/models.py has:

```typescript
interface OptimizedProduct {
  // Identity
  id: string;
  name: string;
  slug: string;
  brand_id: string;

  // Taxonomy
  category: string;
  subcategories: string[];
  tier: string; // "diamond" | "gold" | "silver" | "bronze"
  tier_score: number;

  // Content
  description_short: string;
  description_full: string;

  // Commerce
  price?: number;
  currency: string;
  stock_status: string;

  // Visuals
  image_hero?: ImageAsset;
  image_thumbnail?: ImageAsset;
  image_gallery: ImageAsset[];
  color_primary?: string;

  // Specs
  specs: Record<string, SpecItem[]>;

  // Context
  pros: string[];
  cons: string[];
  expert_tips: string[];

  // Search/Filter
  search_text: string;
  filter_tags: string[];

  // UI Hints
  render_hints: Record<string, boolean>;

  // URLs
  source_url?: string;
  purchase_url?: string;

  // Metadata
  synced_at: string;
}
```

## Recommended Next Steps

1. **Immediate** - Fix lib files to be compatible with `OptimizedProduct`:
   - Start with `catalogLoader.ts` (biggest file with most errors)
   - Update property mappings throughout
   - Use type assertions if needed: `as OptimizedProduct`

2. **Short-term** - Test components:
   - Run `npm run build` after each file fix
   - Verify components render correctly with new data structure
   - Test data loading from catalog

3. **Long-term** - Consider:
   - If `brand` property is still needed, add brand metadata loading logic
   - Consider caching brand info separately if needed for UI
   - Ensure search/filter functionality works with `search_text` and `filter_tags`

## Notes

- The backend is the source of truth - it generates `OptimizedProduct` JSON files
- Frontend components have been aligned to match this structure
- Library files need systematic updates to map old property names to new ones
- Some functionality that depended on properties like `brand` may need refactoring to fetch brand data separately or derive it from `brand_id`
