# Unified Taxonomy System - v1.0

## Overview

The **Unified Taxonomy System** learns and aggregates taxonomies from all brand catalogs to create a comprehensive, unified category structure. This ensures that:

✅ No products are uncategorized  
✅ All categories are discoverable across brands  
✅ Products can be consistently categorized even with incomplete data  
✅ Category aliases provide flexible matching

---

## Architecture

### 1. Taxonomy Learning Phase (Backend)

```
Each Brand Catalog
    ↓
TaxonomyAggregator
    ↓
Extract:
  • Main categories (product.main_category)
  • Spec categories (specs keys)
  • Brand-specific specs
  ↓
Aggregate
  • Collect all unique categories
  • Build brand-to-category mapping
  • Create alias mappings
  ↓
Unified Taxonomy (taxonomy.json)
```

### 2. Taxonomy Structure

The unified taxonomy contains:

```json
{
  "version": "1.0",
  "generated_at": "2026-01-31",

  // Statistics
  "total_brands": 6,
  "total_products": 6,

  // Discovered Categories
  "main_categories": [
    "Audio Equipment",
    "Audio Gear",
    "Percussion",
    "Studio Monitors",
    "Testing"
  ],

  "spec_categories": [
    "Audio Equipment",
    "Audio Gear",
    "Percussion",
    "Studio Monitors",
    "Testing"
  ],

  // Brand-to-Category Mapping
  "brand_category_mapping": {
    "adam-audio": {
      "brand_name": "ADAM Audio",
      "categories": ["Studio Monitors"]
    }
    // ... more brands
  },

  // Category Hierarchy
  "category_hierarchy": {
    "Studio Monitors": ["ADAM Audio", "Amphion"],
    "Audio Equipment": ["Bespeco"],
    "Percussion": ["Drumdots"],
    "Audio Gear": ["Fzone"],
    "Testing": ["Test Brand"]
  },

  // Uncategorized Prevention Rules
  "categorization_rules": {
    "primary_category_required": true,
    "fallback_strategy": "use_spec_category_or_brand_category",
    "default_category": "General Audio Equipment",
    "category_aliases": {
      "Monitor": "Studio Monitors",
      "Speaker": "Audio Gear",
      "Equipment": "Audio Equipment",
      "Instrument": "Percussion",
      "Test": "Testing"
    },
    "must_categorize": true,
    "allow_uncategorized": false
  }
}
```

### 3. Current Brand Taxonomy

```
ADAM Audio (adam-audio)
  └─ Studio Monitors
      • Brand: ADAM Audio
      • Category: Studio Monitors
      • Type: Professional

Amphion (amphion)
  └─ Studio Monitors
      • Brand: Amphion
      • Category: Studio Monitors
      • Type: Professional

Bespeco (bespeco)
  └─ Audio Equipment
      • Brand: Bespeco
      • Category: Audio Equipment
      • Type: Professional

Drumdots (drumdots)
  └─ Percussion
      • Brand: Drumdots
      • Category: Percussion
      • Type: Professional

Fzone (fzone)
  └─ Audio Gear
      • Brand: Fzone
      • Category: Audio Gear
      • Type: Professional

Test Brand (test-brand)
  └─ Testing
      • Brand: Test Brand
      • Category: Testing
      • Type: Professional
```

---

## Backend: Taxonomy Aggregation

### Running the Aggregator

```bash
python backend/ingestion/taxonomy_aggregator.py
```

**Output:**

- `frontend/public/data/taxonomy.json` - Unified taxonomy file
- Console output with summary

### TaxonomyAggregator API

```python
from backend.ingestion.taxonomy_aggregator import TaxonomyAggregator

# Initialize
aggregator = TaxonomyAggregator()

# Learn from all brands
aggregator.aggregate_all_brands()

# Get unified taxonomy
taxonomy = aggregator.unified_taxonomy

# Save to file
aggregator.save(Path("frontend/public/data/taxonomy.json"))

# Print summary
aggregator.print_summary()
```

**Methods:**

```python
# Learn taxonomy from single brand
taxonomy = aggregator.learn_brand_taxonomy(Path("frontend/public/data/adam-audio.json"))

# Aggregate all brands
aggregator.aggregate_all_brands()

# Create hierarchy
hierarchy = aggregator._create_category_hierarchy()

# Create categorization rules
rules = aggregator._create_categorization_rules()

# Save to JSON
aggregator.save(output_path)

# Print summary
aggregator.print_summary()
```

---

## Frontend: Taxonomy Service

### TaxonomyService

Singleton service that manages the unified taxonomy in the browser.

```typescript
import { taxonomyService } from "./lib/taxonomyService";

// Load taxonomy
const taxonomy = await taxonomyService.load();

// Get all categories
const categories = taxonomyService.getMainCategories();

// Get brand categories
const brandCats = taxonomyService.getBrandCategories("adam-audio");

// Ensure product is categorized
const categorized = taxonomyService.ensureCategorized(product);

// Categorize multiple products
const products = taxonomyService.categorizeProducts(productList);

// Get statistics
const stats = await taxonomyService.getStatistics();

// Debug
taxonomyService.debug();
```

**Categorization Strategy:**

When a product needs categorization, the service tries in this order:

1. **Use existing main_category** if it's in the unified taxonomy
2. **Apply alias mapping** (e.g., "Monitor" → "Studio Monitors")
3. **Extract from specs** (use spec category keys)
4. **Brand mapping** (use brand's known categories)
5. **Use default** ("General Audio Equipment")

### useUnifiedTaxonomy Hook

React hook for component access to taxonomy:

```typescript
import { useUnifiedTaxonomy } from './hooks/useUnifiedTaxonomy';

function MyComponent() {
  const {
    taxonomy,
    loading,
    error,
    mainCategories,
    getBrandCategories,
    ensureCategorized,
    categorizeProducts,
    getStats
  } = useUnifiedTaxonomy();

  if (loading) return <div>Loading taxonomy...</div>;
  if (error) return <div>Error: {error.message}</div>;

  // Use taxonomy in component
  const products = categorizeProducts(myProducts);
  const stats = await getStats();

  return (
    <div>
      <p>Categories: {mainCategories.join(', ')}</p>
      <p>Products: {products.length}</p>
    </div>
  );
}
```

---

## How It Works: Step by Step

### Example: Ensuring Product is Categorized

```typescript
// Start with a product that might be incomplete
const product = {
  id: 'some-product',
  name: 'Monitor Speaker',
  brand: 'ADAM Audio',
  main_category: undefined, // ⚠️ Uncategorized
  specs: {
    'Audio Equipment': [
      { key: 'Type', value: 'Speaker' }
    ]
  }
};

// Apply taxonomy categorization
const categorized = taxonomyService.ensureCategorized(product);

// Result:
{
  id: 'some-product',
  name: 'Monitor Speaker',
  brand: 'ADAM Audio',
  main_category: 'Studio Monitors', // ✅ Now categorized!
  // ... rest of product
}
```

**Why it works:**

1. Check `main_category` - undefined
2. Apply alias mapping - no direct alias
3. Extract from specs - "Audio Equipment" isn't in unified categories
4. Brand mapping - ADAM Audio has category "Studio Monitors"
5. Use that category! ✅

### Example: Category Aliasing

```typescript
// Product with alternative category name
const product = {
  main_category: 'Studio Monitor' // Singular, slightly different
};

// Taxonomy has alias mapping:
category_aliases: {
  'Studio Monitor': 'Studio Monitors'
}

// Result: Mapped to canonical "Studio Monitors" ✅
```

---

## Data Flow: Backend to Frontend

```
backend/ingestion/manifest.json
(6 brands defined)
         ↓
backend/pipeline/run
(Processes each brand)
         ↓
backend/data/5_golden/*.json
(Golden data with category info)
         ↓
TaxonomyAggregator.aggregate_all_brands()
(Learns from all brands)
         ↓
frontend/public/data/taxonomy.json
(Deployed unified taxonomy)
         ↓
[Browser loads taxonomy.json]
         ↓
TaxonomyService.load()
(Caches in browser)
         ↓
useUnifiedTaxonomy()
(Available to components)
         ↓
ensureCategorized(product)
(Applies fallback rules)
         ↓
Product displayed with correct category ✅
```

---

## Integration with Frontend Components

### In CatalogLoader

Products are automatically categorized when loaded:

```typescript
async loadBrand(brandId: string): Promise<BrandCatalog> {
  // ... existing code ...

  // NEW: Categorize products using taxonomy
  const products = data.products.map(p =>
    taxonomyService.ensureCategorized(p)
  );

  return {
    // ... existing catalog ...
    products, // ✅ All products guaranteed to have category
  };
}
```

### In GalaxyDashboard

Use taxonomy to display categories:

```typescript
function GalaxyDashboard() {
  const { mainCategories } = useUnifiedTaxonomy();

  return (
    <div>
      {mainCategories.map(category => (
        <CategoryCard key={category} category={category} />
      ))}
    </div>
  );
}
```

### In SpectrumModule

Filter products by unified categories:

```typescript
function SpectrumModule({ selectedCategory }) {
  const { taxonomy } = useUnifiedTaxonomy();
  const products = useProducts();

  // Filter using unified categories
  const filtered = products.filter(p =>
    p.main_category === selectedCategory
  );

  return <ProductGrid products={filtered} />;
}
```

---

## Preventing Uncategorized Products

### Rules Applied Automatically

1. **Primary Category Required** - Every product must have a category
2. **No Uncategorized Products** - Even incomplete data gets categorized
3. **Fallback Strategy** - Try multiple methods to find category
4. **Consistent Aliasing** - Similar category names are normalized
5. **Default Fallback** - "General Audio Equipment" for unknowns

### Example: Handling Edge Cases

```typescript
// Edge Case 1: Empty specs
const product1 = {
  name: "Mystery Product",
  brand: "bespeco",
  specs: {}, // Empty
};
// → Gets category "Audio Equipment" (from brand mapping)

// Edge Case 2: Wrong category name
const product2 = {
  name: "Speaker System",
  main_category: "Loudspeaker", // Not standard
};
// → Alias "Speaker" maps to "Audio Gear"
// → Then categorized as "Audio Gear"

// Edge Case 3: No category at all
const product3 = {
  name: "Unknown Item",
  brand: "unknown-brand",
};
// → Gets default category "General Audio Equipment"
```

---

## Extending the Taxonomy

### Adding a New Category

1. **Add to brand catalog** (e.g., new product with `main_category: "Mixers"`):

```json
{
  "products": [
    {
      "id": "mixer-001",
      "name": "Audio Mixer",
      "main_category": "Mixers"
    }
  ]
}
```

2. **Re-run aggregator**:

```bash
python backend/ingestion/taxonomy_aggregator.py
```

3. **New category appears** in `taxonomy.json` and is available to frontend ✅

### Adding Aliases

Edit `_create_categorization_rules()` in `TaxonomyAggregator`:

```python
"category_aliases": {
  "Mixer": "Mixers",           # Add this
  "Audio Mixer": "Mixers",     # Add this
  # ... existing aliases
}
```

Then re-run aggregator.

---

## Monitoring & Debugging

### Get Taxonomy Statistics

```typescript
const stats = await taxonomyService.getStatistics();
console.log(stats);
// {
//   totalCategories: 5,
//   totalBrands: 6,
//   totalProducts: 6,
//   coverage: {
//     "Studio Monitors": 2,
//     "Audio Equipment": 1,
//     "Percussion": 1,
//     "Audio Gear": 1,
//     "Testing": 1
//   }
// }
```

### Debug Taxonomy

```typescript
taxonomyService.debug();
// Prints detailed information about loaded taxonomy
```

### Log Categorization

```typescript
const product = taxonomyService.ensureCategorized(myProduct);
// Console logs when product was uncategorized and got fallback category
```

---

## Testing

### Unit Test Example

```typescript
describe("TaxonomyService", () => {
  it("should categorize uncategorized products", () => {
    const uncategorized = {
      id: "test-1",
      name: "Test Product",
      main_category: undefined,
    };

    const result = taxonomyService.ensureCategorized(uncategorized);

    expect(result.main_category).toBeDefined();
    expect(result.main_category).toEqual("General Audio Equipment");
  });

  it("should apply category aliases", () => {
    const aliased = {
      id: "test-2",
      main_category: "Monitor",
    };

    const result = taxonomyService.ensureCategorized(aliased);

    expect(result.main_category).toEqual("Studio Monitors");
  });
});
```

---

## Files Involved

```
Backend:
  • backend/ingestion/taxonomy_aggregator.py - Aggregation logic
  • backend/ingestion/manifest.json - Brand definitions
  • frontend/public/data/taxonomy.json - Generated taxonomy

Frontend:
  • frontend/src/lib/taxonomyService.ts - Browser service
  • frontend/src/hooks/useUnifiedTaxonomy.ts - React hook
  • frontend/src/lib/catalogLoader.ts - Uses taxonomy when loading
```

---

## Summary

**The Unified Taxonomy System:**

✅ Learns categories from all brand catalogs  
✅ Creates comprehensive unified taxonomy  
✅ Prevents uncategorized products with fallback rules  
✅ Provides category aliasing for flexibility  
✅ Works seamlessly with frontend components  
✅ Automatically applied when loading products

**Result:** Every product always has a category, improving discoverability and UX! 🎯

---

**Status:** ✅ IMPLEMENTED & DEPLOYED
**Version:** 1.0
**Last Updated:** 2026-01-31
