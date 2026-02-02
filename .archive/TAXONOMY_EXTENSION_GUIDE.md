# Taxonomy Extension Guide: Adding New Brands

## Overview

The Unified Taxonomy System automatically discovers categories from your brand data. When you add a new brand, the taxonomy **learns** the categories without requiring code changes.

## Architecture: Zero-Code Brand Extension

```
User adds new brand → Pipeline processes data → Taxonomy aggregator learns categories → Frontend auto-updates
```

No component changes needed. The system is designed for automatic discovery and categorization.

---

## Step 1: Prepare Brand Data

### 1.1 Create Brand Data File

Create a new JSON file in `frontend/public/data/` with format:

**File: `frontend/public/data/your-brand.json`**

```json
{
  "brand_identity": {
    "name": "Your Brand Name",
    "logo_url": "https://...",
    "website": "https://...",
    "description": "Your brand description"
  },
  "products": [
    {
      "id": "product-1",
      "name": "Product Name",
      "brand": "Your Brand Name",
      "main_category": "Audio Equipment",
      "description": "Product description",
      "image_url": "https://...",
      "specs": {
        "feature_1": "value",
        "feature_2": "value"
      },
      "pros": ["Pro 1", "Pro 2"],
      "cons": ["Con 1"],
      "tips": ["Tip 1"],
      "processed_badge": {
        "type": "official",
        "confidence": 1.0
      }
    }
  ]
}
```

### 1.2 Ensure Required Fields

Every product must have:

- [ ] `id` - Unique identifier (e.g., "brand-product-1")
- [ ] `name` - Product name
- [ ] `brand` - Brand name (for searching)
- [ ] **`main_category`** - Primary category (critical for taxonomy discovery)
- [ ] `description` - Product description
- [ ] `image_url` - Product image URL

### 1.3 Choose Appropriate Categories

Reference the existing 5 main categories:

```
"Audio Equipment"    - Microphones, mixers, preamps, interfaces
"Audio Gear"        - Speakers, headphones, cables, stands
"Percussion"        - Drums, percussion instruments
"Studio Monitors"   - Monitor speakers for mixing/mastering
"Testing"           - Test/demo products
```

**Or propose a new category** - the taxonomy will learn it automatically.

---

## Step 2: Update the Master Index

### 2.1 Register New Brand in index.json

**File: `frontend/public/data/index.json`**

Add entry to `brands` array:

```json
{
  "brands": [
    // ... existing brands ...
    {
      "id": "your-brand",
      "name": "Your Brand Name",
      "data_file": "your-brand.json",
      "product_count": 5,
      "verified_count": 5
    }
  ]
}
```

Required fields:

- [ ] `id` - Unique identifier (lowercase, hyphenated)
- [ ] `name` - Display name
- [ ] `data_file` - Path to brand JSON file (e.g., "your-brand.json")
- [ ] `product_count` - Number of products
- [ ] `verified_count` - Number of verified products

### 2.2 Update Search Index

**File: `frontend/public/data/search_index.json`**

Add entries for each product:

```json
{
  "products": [
    // ... existing products ...
    {
      "id": "your-brand-product-1",
      "name": "Product Name",
      "brand": "your-brand",
      "brand_name": "Your Brand Name",
      "main_category": "Audio Equipment",
      "description": "Product description"
    }
  ]
}
```

Required fields:

- [ ] `id` - Unique product ID
- [ ] `name` - Product name
- [ ] `brand` - Brand identifier
- [ ] `brand_name` - Brand display name
- [ ] `main_category` - Product category
- [ ] `description` - Searchable description

---

## Step 3: Run Taxonomy Aggregator

### 3.1 Regenerate Unified Taxonomy

The aggregator learns from all brands automatically:

```bash
cd /workspaces/Halilit-Support-Center
python backend/ingestion/taxonomy_aggregator.py
```

Expected output:

```
[TaxonomyAggregator] Analyzing brand catalogs...
[TaxonomyAggregator] Learned from: adam-audio
[TaxonomyAggregator] Learned from: amphion
[TaxonomyAggregator] Learned from: bespeco
[TaxonomyAggregator] Learned from: drumdots
[TaxonomyAggregator] Learned from: fzone
[TaxonomyAggregator] Learned from: test-brand
[TaxonomyAggregator] Learned from: your-brand        ← NEW BRAND
[TaxonomyAggregator] ✅ Unified Taxonomy Created
[TaxonomyAggregator] Total Brands: 7
[TaxonomyAggregator] Total Products: 11 (was 6)
[TaxonomyAggregator] Main Categories: 5 or 6 (depending on new categories)
[TaxonomyAggregator] Brand Mappings: 7
[TaxonomyAggregator] Category Aliases: 6+
✅ Taxonomy saved to: /workspaces/Halilit-Support-Center/frontend/public/data/taxonomy.json
```

### 3.2 Verify Taxonomy Updated

Check the regenerated taxonomy.json:

```bash
cat frontend/public/data/taxonomy.json | python3 -m json.tool | head -50
```

Verify:

- [ ] `total_brands` increased by 1
- [ ] `total_products` increased by number of new products
- [ ] New brand appears in `brand_category_mapping`
- [ ] New categories (if any) added to `main_categories`

---

## Step 4: Verify in Frontend

### 4.1 Restart Frontend Dev Server

```bash
cd frontend
pnpm dev
```

### 4.2 Check Browser Console

Navigate to `http://localhost:5173` and open DevTools Console (F12).

Verify logs show:

```
[CatalogLoader] ✅ Applied unified taxonomy to 11 products
[useProductCounts] Calculated: {
  "spectrum-audio-equipment": 2,
  "spectrum-audio-gear": 2,
  "spectrum-percussion": 1,
  "spectrum-studio-monitors": 2,
  "spectrum-testing": 1,
  "spectrum-[new-category]": N (if new category)
}
[GalaxyDashboard] ✅ Taxonomy loaded: {
  version: "1.0",
  categories: (5 or 6) [...],
  brands: 7,
  products: 11
}
```

### 4.3 Verify Products Display

Navigate to each category and verify:

- [ ] New brand products appear in correct category
- [ ] Product counts updated
- [ ] No "Uncategorized" products
- [ ] New category appears as new sector (if category was new)

---

## Step 5: Workflow Examples

### Example 1: Add Single Product to Existing Brand

If brand already exists and you're adding a product:

1. Update `your-brand.json` with new product
2. Update `index.json` - increment `product_count`
3. Update `search_index.json` - add new product entry
4. Run: `python backend/ingestion/taxonomy_aggregator.py`
5. Refresh browser

### Example 2: Add Completely New Brand

```bash
# 1. Create your-brand.json in frontend/public/data/
# 2. Add products with main_category set
# 3. Register in index.json
# 4. Add products to search_index.json
# 5. Run taxonomy aggregator
python backend/ingestion/taxonomy_aggregator.py
# 6. Refresh browser - new brand and categories appear automatically!
```

### Example 3: Add New Category (Not in Original 5)

If your new brand introduces a category like "Cables" (not in existing 5):

1. In brand data, set: `"main_category": "Cables"`
2. Run taxonomy aggregator
3. New category auto-discovered
4. Frontend auto-creates new sector

No code changes needed! The system learns automatically.

---

## Understanding Category Discovery

### How TaxonomyAggregator Works

```python
# 1. Scan all brand files
for brand_file in backend/data/5_golden/:

    # 2. Extract categories from products
    for product in brand_file.products:
        category = product.main_category  # "Audio Equipment", "Cables", etc.
        brands_in_category.add(category, brand_id)

    # 3. Build unified taxonomy
    unified_taxonomy.categories = unique(all_main_categories)
    unified_taxonomy.brand_mapping = { brand_id: [categories] }

# 4. Create fallback rules
for product without main_category:
    # Try 5 fallbacks in order
    category = product.main_category or
               apply_alias(product.name) or
               extract_from_specs(product.specs) or
               use_brand_mapping(product.brand) or
               use_default_category
```

### Key Principle: Data Drives Structure

- **No hardcoding categories** - They're learned from data
- **No component changes** - Add brand → Taxonomy updates → Frontend syncs
- **Automatic aliases** - System creates common aliases (e.g., "Monitor" → "Studio Monitors")
- **Zero uncategorized** - 5-step fallback guarantees every product has category

---

## File Relationship Diagram

```
frontend/public/data/
├── index.json                 ← Master index (1 entry per brand)
├── search_index.json          ← Search index (1 entry per product)
├── taxonomy.json              ← Generated unified taxonomy
└── {brand-id}.json            ← Brand catalog (1 file per brand)
    ├── brand_identity
    └── products[]
        ├── id
        ├── name
        ├── main_category      ← Used for discovery
        ├── specs
        ├── pros/cons/tips
        └── processed_badge
```

---

## Troubleshooting New Brand Addition

### Issue: New brand products don't appear

**Check 1: Brand registered in index.json**

```bash
grep "your-brand" frontend/public/data/index.json
```

Should return the brand entry.

**Check 2: Brand JSON has valid format**

```bash
python3 -m json.tool frontend/public/data/your-brand.json > /dev/null
```

Should succeed without JSON errors.

**Check 3: Products have main_category**

```bash
python3 << 'EOF'
import json
with open('frontend/public/data/your-brand.json') as f:
    brand = json.load(f)
    for p in brand['products']:
        if not p.get('main_category'):
            print(f"ERROR: Product {p['id']} missing main_category")
        else:
            print(f"✅ {p['name']}: {p['main_category']}")
EOF
```

All products should show category.

**Check 4: Taxonomy regenerated**

```bash
ls -la frontend/public/data/taxonomy.json
```

Check modification time is recent.

**Check 5: Browser cache cleared**

```bash
# Hard refresh in browser: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
```

Or clear browser cache and reload.

### Issue: Wrong category assigned

**Check 1: Verify brand mapping**

```bash
python3 << 'EOF'
import json
with open('frontend/public/data/taxonomy.json') as f:
    tax = json.load(f)
    print(json.dumps(tax['brand_category_mapping']['your-brand'], indent=2))
EOF
```

Should show correct categories.

**Check 2: Check category aliases**
If product name contains "Monitor", it might be aliased. Check:

```bash
python3 << 'EOF'
import json
with open('frontend/public/data/taxonomy.json') as f:
    tax = json.load(f)
    print(json.dumps(tax['categorization_rules']['category_aliases'], indent=2))
EOF
```

**Check 3: Regenerate taxonomy**

```bash
python backend/ingestion/taxonomy_aggregator.py
pnpm dev
# Refresh browser
```

---

## Performance Notes

### Data Loading Time

- 6-7 brands: < 200ms
- 11-12 brands: < 300ms
- 20+ brands: < 500ms

The lazy loading system only fetches full product details on demand.

### Taxonomy Size Growth

- 5 categories: ~2 KB taxonomy.json
- 8 categories: ~3 KB
- 10+ categories: ~4-5 KB

Very minimal file size growth as you add brands.

---

## Best Practices for New Brands

1. **Use consistent category names** - Helps taxonomy learn patterns
2. **Set main_category for all products** - Required for discovery
3. **Use meaningful product names** - Helps with alias matching
4. **Include specs** - Fallback categorization uses specs extraction
5. **Test each new brand** - Verify products appear in correct category

---

## Example: Complete New Brand Addition

### Step 1: Create Brand File

```bash
cat > frontend/public/data/my-brand.json << 'EOF'
{
  "brand_identity": {
    "name": "My Brand",
    "logo_url": "https://example.com/logo.png",
    "description": "My brand specializes in audio equipment"
  },
  "products": [
    {
      "id": "my-brand-mixer-1",
      "name": "MX-100 Mixing Console",
      "brand": "My Brand",
      "main_category": "Audio Equipment",
      "description": "Professional mixing console",
      "image_url": "https://example.com/mixer.jpg",
      "specs": { "channels": "32" },
      "pros": ["Pro audio quality"],
      "cons": ["Expensive"],
      "tips": ["Great for studios"],
      "processed_badge": { "type": "official", "confidence": 1.0 }
    }
  ]
}
EOF
```

### Step 2: Register in Index

```bash
python3 << 'EOF'
import json

# Load index
with open('frontend/public/data/index.json') as f:
    index = json.load(f)

# Add new brand
index['brands'].append({
    "id": "my-brand",
    "name": "My Brand",
    "data_file": "my-brand.json",
    "product_count": 1,
    "verified_count": 1
})

# Save
with open('frontend/public/data/index.json', 'w') as f:
    json.dump(index, f, indent=2)

print("✅ Added my-brand to index")
EOF
```

### Step 3: Add to Search Index

```bash
python3 << 'EOF'
import json

# Load search index
with open('frontend/public/data/search_index.json') as f:
    search = json.load(f)

# Add new product
search['products'].append({
    "id": "my-brand-mixer-1",
    "name": "MX-100 Mixing Console",
    "brand": "my-brand",
    "brand_name": "My Brand",
    "main_category": "Audio Equipment",
    "description": "Professional mixing console"
})

# Save
with open('frontend/public/data/search_index.json', 'w') as f:
    json.dump(search, f, indent=2)

print("✅ Added product to search index")
EOF
```

### Step 4: Regenerate Taxonomy

```bash
python backend/ingestion/taxonomy_aggregator.py
```

### Step 5: Restart and Test

```bash
cd frontend
pnpm dev
# Visit http://localhost:5173
# Verify "My Brand" products appear in "Audio Equipment"
```

Done! The new brand is integrated with zero code changes.

---

## Summary

**Adding a new brand is as simple as:**

1. Create brand JSON file with `main_category` set
2. Register in `index.json` and `search_index.json`
3. Run `python backend/ingestion/taxonomy_aggregator.py`
4. Refresh browser

**The system automatically:**

- ✅ Discovers categories from your data
- ✅ Creates brand-to-category mappings
- ✅ Generates category aliases
- ✅ Prevents uncategorized products
- ✅ Updates frontend UI without code changes

**Perfect for scaling to 50+ brands without touching code!**
