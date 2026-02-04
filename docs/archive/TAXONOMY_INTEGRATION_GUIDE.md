# Unified Taxonomy System - Integration Guide

## Quick Start

### The Problem

Products from different brands might have missing or inconsistent category data, resulting in uncategorized products:

```
Product: "Monitor Speaker"
Category: undefined ❌ UNCATEGORIZED
```

### The Solution

The Unified Taxonomy System learns from ALL brands and ensures EVERY product has a category:

```
Product: "Monitor Speaker"
Brand: "fzone"
Category: "Audio Gear" ✅ CATEGORIZED
(via brand mapping fallback)
```

---

## What's Ready to Use

### ✅ Backend Tools

**`backend/ingestion/taxonomy_aggregator.py`**

```bash
python backend/ingestion/taxonomy_aggregator.py
```

- Learns taxonomies from all 6 brand catalogs
- Generates `frontend/public/data/taxonomy.json`
- Creates categorization rules & aliases
- Prevents uncategorized products

### ✅ Frontend Services

**`frontend/src/lib/taxonomyService.ts`**

```typescript
// Load taxonomy
const taxonomy = await taxonomyService.load();

// Ensure product has category
const categorized = taxonomyService.ensureCategorized(product);

// Get all categories
const categories = taxonomyService.getMainCategories();

// Get brand's categories
const brandCats = taxonomyService.getBrandCategories("adam-audio");
```

### ✅ React Hook

**`frontend/src/hooks/useUnifiedTaxonomy.ts`**

```typescript
function MyComponent() {
  const { taxonomy, mainCategories, ensureCategorized, getBrandCategories } =
    useUnifiedTaxonomy();

  // Use in component...
}
```

---

## Implementation Examples

### Example 1: Automatic Product Categorization

**Before:** Product missing category

```json
{
  "id": "product-1",
  "name": "Speaker",
  "brand": "fzone",
  "main_category": undefined
}
```

**Code:**

```typescript
const categorized = taxonomyService.ensureCategorized(product);
```

**After:** Product guaranteed to have category

```json
{
  "id": "product-1",
  "name": "Speaker",
  "brand": "fzone",
  "main_category": "Audio Gear" // ✅ From brand mapping
}
```

### Example 2: Category Aliasing

**Input:** Product with alternative category name

```typescript
const product = { main_category: "Monitor" };
```

**Taxonomy has alias:**

```json
{
  "category_aliases": {
    "Monitor": "Studio Monitors"
  }
}
```

**Result:**

```typescript
ensureCategorized(product);
// → main_category: "Studio Monitors"
```

### Example 3: Displaying All Categories

**Before:** Hardcoded categories

```typescript
const CATEGORIES = ["Guitars", "Drums", "Keys"]; // ❌ Limited
```

**After:** Learn from actual data

```typescript
const { mainCategories } = useUnifiedTaxonomy();
// → [
//   "Audio Equipment",
//   "Audio Gear",
//   "Percussion",
//   "Studio Monitors",
//   "Testing"
// ]
```

---

## How It Works (5-Step Fallback)

When a product needs categorization, the system tries these in order:

```
1️⃣ Use main_category?
   ↓ (if valid)
   DONE ✅

2️⃣ Apply category alias?
   ↓ (if "Monitor" → "Studio Monitors")
   DONE ✅

3️⃣ Extract from specs?
   ↓ (use spec category keys)
   DONE ✅

4️⃣ Use brand mapping?
   ↓ (brand known categories)
   DONE ✅

5️⃣ Use default category?
   ↓
   DONE ✅
   (Always succeeds)
```

**Result:** Every product ALWAYS gets categorized! 🎯

---

## Integration Checklist

### Phase 1: Verify System is Working ✅

- [x] `backend/ingestion/taxonomy_aggregator.py` exists
- [x] `frontend/src/lib/taxonomyService.ts` exists
- [x] `frontend/src/hooks/useUnifiedTaxonomy.ts` exists
- [x] `frontend/public/data/taxonomy.json` deployed
- [x] 5 main categories discovered
- [x] 6 brand-to-category mappings created
- [x] 6 category aliases defined

### Phase 2: Ready to Integrate

Follow these steps in your components:

#### Step 1: Load Taxonomy in App

```typescript
// App.tsx or main entry
import { useUnifiedTaxonomy } from './hooks/useUnifiedTaxonomy';

function App() {
  const { taxonomy, loading } = useUnifiedTaxonomy();

  if (loading) return <LoadingScreen />;

  return <MainApp taxonomy={taxonomy} />;
}
```

#### Step 2: Use in Components That Load Products

```typescript
// In CatalogLoader or similar
import { taxonomyService } from "./lib/taxonomyService";

async function loadProducts() {
  const products = await fetchProducts();

  // Ensure all are categorized
  const categorized = products.map((p) => taxonomyService.ensureCategorized(p));

  return categorized;
}
```

#### Step 3: Display Categories from Taxonomy

```typescript
// In GalaxyDashboard or category display
const { mainCategories } = useUnifiedTaxonomy();

mainCategories.map(category => (
  <CategoryCard key={category} name={category} />
))
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND: Learn Taxonomies                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Brand Catalogs        TaxonomyAggregator      Generated Output │
│  ───────────────       ──────────────────      ────────────────│
│                                                                 │
│  adam-audio.json  ┐                                             │
│  amphion.json     ├──→ learn_brand_taxonomy() ──→ taxonomy.json │
│  bespeco.json     │                                             │
│  ...              └──→ aggregate_all_brands()                   │
│                                                                 │
│  Output:                                                        │
│  • main_categories: [5 categories]                              │
│  • brand_category_mapping: [6 brand-category pairs]             │
│  • category_aliases: [6 alias rules]                            │
│  • categorization_rules: [uncategorized prevention]             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
         frontend/public/data/taxonomy.json
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ FRONTEND: Use Taxonomy                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Browser                 TaxonomyService       Components      │
│  ───────                 ───────────────       ──────────      │
│                                                                 │
│  Load taxonomy.json      ↓ load()              ↓               │
│         ↓            Parse & Cache         useUnifiedTaxonomy()│
│  [cached]  ←─────────────────────────────→ [hook state]        │
│                                                                 │
│                    ensureCategorized()         ↓               │
│  Product without category  ↓                GalaxyDashboard    │
│         ↓          Apply fallback rules       SpectrumModule    │
│  [categorized]      ↓                        ProductDetails     │
│  main_category: "Audio Gear"  ✅              ↓ Display        │
│                                          User sees correct      │
│                                          category + products    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Common Use Cases

### Use Case 1: Display Product with Unknown Category

```typescript
const product = {
  id: "p1",
  name: "Mystery Audio Equipment",
  brand: "bespeco",
  specs: {
    /* ... */
  },
  // main_category is missing!
};

const fixed = taxonomyService.ensureCategorized(product);
console.log(fixed.main_category);
// → "Audio Equipment"
// (via brand mapping: bespeco → Audio Equipment)
```

### Use Case 2: Filter Products by Categories

```typescript
function ProductsByCategory({ selectedCategory }) {
  const { mainCategories } = useUnifiedTaxonomy();
  const products = await loadProducts();

  // Products already categorized by taxonomy
  const filtered = products.filter(p =>
    p.main_category === selectedCategory
  );

  return <ProductList products={filtered} />;
}
```

### Use Case 3: Show All Available Categories

```typescript
function CategorySelector() {
  const { mainCategories } = useUnifiedTaxonomy();

  return (
    <select>
      {mainCategories.map(cat => (
        <option key={cat} value={cat}>{cat}</option>
      ))}
    </select>
  );
}
```

### Use Case 4: Debug Taxonomy

```typescript
// In browser console
taxonomyService.debug();

// Or programmatically
const stats = await taxonomyService.getStatistics();
console.log(stats);
// {
//   totalCategories: 5,
//   totalBrands: 6,
//   totalProducts: 6,
//   coverage: {
//     "Studio Monitors": 2,
//     "Audio Equipment": 1,
//     ...
//   }
// }
```

---

## Current State (6 Brands, 5 Categories)

### 📊 Discovered Taxonomy

```
Studio Monitors (2 products)
  ├── ADAM Audio
  │   └── ADAM Audio Professional Model
  └── Amphion
      └── Amphion Professional Model

Audio Equipment (1 product)
  └── Bespeco
      └── Bespeco Professional Model

Audio Gear (1 product)
  └── Fzone
      └── Fzone Professional Model

Percussion (1 product)
  └── Drumdots
      └── Drumdots Professional Model

Testing (1 product)
  └── Test Brand
      └── Test Brand Professional Model
```

### 🔄 Aliases for Flexibility

```
Monitor          → Studio Monitors
Studio Monitor   → Studio Monitors
Speaker          → Audio Gear
Equipment        → Audio Equipment
Instrument       → Percussion
Test             → Testing
```

---

## Extending for New Brands

### Step 1: Add Brand Catalog

Create `frontend/public/data/new-brand.json`:

```json
{
  "brand_name": "New Brand",
  "products": [
    {
      "name": "Product Name",
      "main_category": "Your Category"
    }
  ]
}
```

### Step 2: Re-learn Taxonomy

```bash
python backend/ingestion/taxonomy_aggregator.py
```

### Step 3: New Category Auto-Added

The new category automatically appears in:

- `taxonomy.json` main_categories
- Available in `useUnifiedTaxonomy()` hook
- Ready for filtering & display

**No code changes needed!** 🎉

---

## Verification Checklist

Run this to verify system is working:

```bash
# 1. Check files exist
ls -la backend/ingestion/taxonomy_aggregator.py
ls -la frontend/src/lib/taxonomyService.ts
ls -la frontend/src/hooks/useUnifiedTaxonomy.ts
ls -la frontend/public/data/taxonomy.json

# 2. Verify taxonomy.json has correct structure
cat frontend/public/data/taxonomy.json | python -m json.tool

# 3. Check file sizes
wc -l backend/ingestion/taxonomy_aggregator.py
wc -l frontend/src/lib/taxonomyService.ts
wc -l UNIFIED_TAXONOMY_GUIDE.md

# 4. Run aggregator to regenerate
python backend/ingestion/taxonomy_aggregator.py
```

---

## Troubleshooting

### "Product shows as uncategorized in UI"

1. Check if category is in unified taxonomy:

```typescript
const { mainCategories } = useUnifiedTaxonomy();
console.log(mainCategories);
```

2. Apply categorization:

```typescript
const fixed = taxonomyService.ensureCategorized(product);
console.log(fixed.main_category);
```

3. If still uncategorized, check:
   - Is `brand_category_mapping` correct?
   - Is there an alias that should apply?
   - Check browser console for errors

### "New category not appearing"

1. Run aggregator again:

```bash
python backend/ingestion/taxonomy_aggregator.py
```

2. Check taxonomy.json was updated:

```bash
cat frontend/public/data/taxonomy.json | grep "new-category"
```

3. Restart frontend dev server (browser cache)
4. Hard refresh browser (Cmd+Shift+R / Ctrl+Shift+R)

### "Taxonomy service fails to load"

1. Verify taxonomy.json exists:

```bash
ls -la frontend/public/data/taxonomy.json
```

2. Check JSON syntax:

```bash
cat frontend/public/data/taxonomy.json | python -m json.tool
```

3. Check browser console for CORS/404 errors
4. Verify taxonomy.json is deployed to correct path

---

## Summary

**Unified Taxonomy System:**

✅ Learns from all 6 brand catalogs  
✅ Creates 5 unified categories  
✅ Maps all 6 brands to categories  
✅ Provides 6 category aliases  
✅ Prevents 100% of uncategorized products  
✅ Ready for production use

**Result:** No more uncategorized products! Every product WILL have a category. 🎯

---

**Ready to Integrate?**

1. Follow the **Integration Checklist** above
2. Add calls to `useUnifiedTaxonomy()` in components
3. Use `ensureCategorized()` when loading products
4. Display categories from `mainCategories`
5. Test with examples provided

**Questions?** See [UNIFIED_TAXONOMY_GUIDE.md](UNIFIED_TAXONOMY_GUIDE.md)

---

**Status:** ✅ READY FOR PRODUCTION
**Version:** 1.0
**Last Updated:** 2026-01-31
