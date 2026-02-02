# Taxonomy Integration Test Guide

## Overview

This guide provides step-by-step instructions to verify that the Unified Taxonomy System is properly integrated into the frontend and working correctly with all 6 brands and 5 categories.

## Prerequisites

- Backend pipeline has been run successfully
- Frontend dev server is running at `http://localhost:5173`
- All data files are deployed to `frontend/public/data/`
- taxonomy.json is in place

## Phase 1: Frontend Application Status

### 1.1 Start the Frontend Server

```bash
cd frontend
pnpm dev
```

Expected output:

```
VITE v7.3.1 ready in 123 ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

### 1.2 Open Application in Browser

Navigate to `http://localhost:5173` and verify:

- [ ] Page loads without errors
- [ ] GALAXIES header displays
- [ ] 6 category sectors are visible (2 rows × 3 columns)
- [ ] No console errors in browser DevTools (F12)

### 1.3 Check Taxonomy Load Status

In browser DevTools Console (F12), you should see:

```
[GalaxyDashboard] Loading unified taxonomy...
[GalaxyDashboard] ✅ Taxonomy loaded: {
  version: "1.0",
  categories: ["Audio Equipment", "Audio Gear", "Percussion", "Studio Monitors", "Testing"],
  brands: 6,
  products: 6
}
[CatalogLoader] ✅ Applied unified taxonomy to 6 products
```

If you see these logs, proceed to Phase 2. If not, see troubleshooting at end.

---

## Phase 2: Verify Taxonomy Data Structure

### 2.1 Check taxonomy.json File

In browser Console, run:

```javascript
fetch("/data/taxonomy.json")
  .then((r) => r.json())
  .then((d) => console.log(JSON.stringify(d, null, 2)));
```

Verify output contains:

```json
{
  "version": "1.0",
  "total_brands": 6,
  "total_products": 6,
  "main_categories": [
    "Audio Equipment",
    "Audio Gear",
    "Percussion",
    "Studio Monitors",
    "Testing"
  ],
  "brand_category_mapping": {
    "adam-audio": {
      "brand_name": "ADAM Audio",
      "categories": ["Studio Monitors"]
    },
    "amphion": { "brand_name": "Amphion", "categories": ["Studio Monitors"] },
    "bespeco": { "brand_name": "Bespeco", "categories": ["Audio Equipment"] },
    "drumdots": { "brand_name": "Drumdots", "categories": ["Percussion"] },
    "fzone": { "brand_name": "Fzone", "categories": ["Audio Gear"] },
    "test-brand": { "brand_name": "Test Brand", "categories": ["Testing"] }
  },
  "categorization_rules": {
    "primary_category_required": true,
    "allow_uncategorized": false,
    "must_categorize": true,
    "category_aliases": {
      "Equipment": "Audio Equipment",
      "Instrument": "Percussion",
      "Monitor": "Studio Monitors",
      "Speaker": "Audio Gear",
      "Studio Monitor": "Studio Monitors",
      "Test": "Testing"
    }
  }
}
```

- [ ] All 5 main_categories present
- [ ] All 6 brands in brand_category_mapping
- [ ] Categorization rules enforced
- [ ] 6 category aliases defined

### 2.2 Check Brand Catalogs Have Categories

In browser Console, run:

```javascript
Promise.all([
  fetch("/data/adam-audio.json").then((r) => r.json()),
  fetch("/data/amphion.json").then((r) => r.json()),
  fetch("/data/bespeco.json").then((r) => r.json()),
  fetch("/data/drumdots.json").then((r) => r.json()),
  fetch("/data/fzone.json").then((r) => r.json()),
  fetch("/data/test-brand.json").then((r) => r.json()),
]).then((catalogs) => {
  catalogs.forEach((cat, i) => {
    const products = cat.products || [];
    console.log(`Brand ${i}: ${products.length} products`);
    products.forEach((p) => {
      console.log(`  - ${p.name}: "${p.main_category}"`);
    });
  });
});
```

Expected output:

```
Brand 0: 1 products
  - A7X Monitor: "Studio Monitors"
Brand 1: 1 products
  - Amphion One18: "Studio Monitors"
Brand 2: 1 products
  - Microphone 01: "Audio Equipment"
Brand 3: 1 products
  - Percussion Instrument 1: "Percussion"
Brand 4: 1 products
  - F-Zone Speakers: "Audio Gear"
Brand 5: 1 products
  - Test Product 1: "Testing"
```

- [ ] All 6 brands have products
- [ ] All products have main_category assigned
- [ ] No "Uncategorized" products visible

---

## Phase 3: UI Category Display Verification

### 3.1 View All 6 Category Sectors

On the GALAXIES page, verify you see 6 sectors arranged in 2 rows × 3 columns:

**Top Row (Left to Right):**

- [ ] Sector 1: 1st category with icon and subcategories
- [ ] Sector 2: 2nd category with icon and subcategories
- [ ] Sector 3: 3rd category with icon and subcategories

**Bottom Row (Left to Right):**

- [ ] Sector 4: 4th category with icon and subcategories
- [ ] Sector 5: 5th category with icon and subcategories
- [ ] Sector 6: 6th category with icon and subcategories

Each sector should show:

- [ ] Category name (e.g., "AUDIO EQUIPMENT", "STUDIO MONITORS")
- [ ] Category icon (colored square in header)
- [ ] Subcategory slots (4 columns × variable rows)
- [ ] Product count on each subcategory

### 3.2 Verify Product Count Badges

On each subcategory slot, verify:

- [ ] Number badge shows (e.g., "1", "2", etc.)
- [ ] No subcategory shows "0" products
- [ ] No "undefined" or "NaN" values

Hover over subcategory slots and verify:

- [ ] Hover effect activates (brightness increase)
- [ ] Cursor changes to pointer
- [ ] Tooltip or hover hint appears (if implemented)

### 3.3 Verify Taxonomy Status Indicator

In top-right of header, verify one of:

- [ ] Green dot "Unified taxonomy active" - GOOD, proceed
- [ ] Yellow dot "Loading taxonomy..." - Wait a few seconds, refresh page
- [ ] Red dot "Taxonomy unavailable" - See troubleshooting

---

## Phase 4: Product Categorization Verification

### 4.1 Click Into a Category

Click on any subcategory slot to open SpectrumModule (product list).

Verify:

- [ ] Product list displays
- [ ] All products shown have a main_category
- [ ] Products grouped by correct category
- [ ] No "Uncategorized" section visible

### 4.2 Check Individual Product Details

Click on any product card to open ProductDetailPanel.

Verify product has:

- [ ] ✅ main_category displayed (e.g., "Studio Monitors")
- [ ] ✅ Product name, brand, specs
- [ ] ✅ Processed badge (if applicable)
- [ ] ✅ No category="undefined" or "Uncategorized"

### 4.3 Test Product-Category Mapping

For each of the 6 brands, navigate to its products and verify:

**ADAM Audio → Studio Monitors**

- [ ] A7X Monitor appears under "Studio Monitors" category
- [ ] Product has main_category="Studio Monitors"

**Amphion → Studio Monitors**

- [ ] Amphion One18 appears under "Studio Monitors" category
- [ ] Product has main_category="Studio Monitors"

**Bespeco → Audio Equipment**

- [ ] Microphone 01 appears under "Audio Equipment" category
- [ ] Product has main_category="Audio Equipment"

**Drumdots → Percussion**

- [ ] Percussion Instrument 1 appears under "Percussion" category
- [ ] Product has main_category="Percussion"

**Fzone → Audio Gear**

- [ ] F-Zone Speakers appears under "Audio Gear" category
- [ ] Product has main_category="Audio Gear"

**Test Brand → Testing**

- [ ] Test Product 1 appears under "Testing" category
- [ ] Product has main_category="Testing"

---

## Phase 5: Console Logging Verification

### 5.1 Monitor Debug Output

Open browser DevTools Console (F12) and reload page.

You should see logs in this order:

```
[GalaxyDashboard] Loading unified taxonomy...
[CatalogLoader] Starting to load all products...
[CatalogLoader] Loading brand: adam-audio
[CatalogLoader] Loading brand: amphion
[CatalogLoader] Loading brand: bespeco
[CatalogLoader] Loading brand: drumdots
[CatalogLoader] Loading brand: fzone
[CatalogLoader] Loading brand: test-brand
[CatalogLoader] ✅ Applied unified taxonomy to 6 products
[useProductCounts] Calculated: {
  "spectrum-audio-equipment": 1,
  "spectrum-audio-gear": 1,
  "spectrum-percussion": 1,
  "spectrum-studio-monitors": 2,
  "spectrum-testing": 1
}
[GalaxyDashboard] ✅ Taxonomy loaded: {
  version: "1.0",
  categories: (5) ["Audio Equipment", "Audio Gear", "Percussion", "Studio Monitors", "Testing"],
  brands: 6,
  products: 6
}
```

Verify:

- [ ] No RED error messages
- [ ] Product count shows 6 total
- [ ] Product distribution: 2 Studio Monitors, 1 each of others

### 5.2 Check for Errors

Look for any of these ERROR messages:

```
❌ Failed to apply taxonomy
❌ Failed to load taxonomy
❌ Taxonomy service error
```

If any errors appear, see Troubleshooting section.

---

## Phase 6: Search and Filter Integration

### 6.1 Test Global Search

Click on search bar (top of page) and search for product names:

- [ ] "A7X" returns A7X Monitor with Studio Monitors category
- [ ] "Amphion" returns Amphion One18 with Studio Monitors category
- [ ] "Microphone" returns Microphone 01 with Audio Equipment category
- [ ] Search results show correct categories

### 6.2 Test Category Filtering

In any product list view:

- [ ] Can filter by main_category
- [ ] Filtering updates product display
- [ ] Product count updates correctly

---

## Phase 7: Edge Case Testing

### 7.1 Missing main_category Fallback

Test the 5-step categorization fallback by manually modifying a product (for testing):

In browser Console:

```javascript
fetch("/data/test-brand.json")
  .then((r) => r.json())
  .then((d) => {
    // Remove main_category to test fallback
    d.products[0].main_category = undefined;
    return d;
  })
  .then((d) => console.log("Modified product:", d.products[0]));
```

Then refresh the page and verify:

- [ ] Product still appears in UI
- [ ] Product is categorized using fallback (spec → brand mapping → default)
- [ ] No "Uncategorized" label appears

### 7.2 Multiple Product Brands

Verify Studio Monitors category correctly shows both:

- [ ] ADAM Audio A7X Monitor
- [ ] Amphion One18

Both should appear together in the same category despite being different brands.

---

## Troubleshooting

### Issue: Red indicator "Taxonomy unavailable"

**Check 1: taxonomy.json exists**

```bash
ls -la frontend/public/data/taxonomy.json
```

If missing, regenerate:

```bash
python backend/ingestion/taxonomy_aggregator.py
```

**Check 2: Browser console for errors**
In DevTools Console, check for CORS or fetch errors.

**Check 3: Verify taxonomy.json is valid JSON**

```bash
python3 -m json.tool frontend/public/data/taxonomy.json > /dev/null && echo "Valid JSON" || echo "Invalid JSON"
```

### Issue: No products showing in categories

**Check 1: Product count is 0**
In Console, run:

```javascript
fetch("/data/index.json")
  .then((r) => r.json())
  .then((d) => {
    console.log("Brands:", d.brands);
    return Promise.all(
      d.brands.map((b) => fetch(`/data/${b.data_file}`).then((r) => r.json())),
    );
  })
  .then((catalogs) => {
    const total = catalogs.reduce(
      (sum, cat) => sum + (cat.products?.length || 0),
      0,
    );
    console.log("Total products:", total);
  });
```

If total is 0, data files are empty. Regenerate using pipeline.

**Check 2: Products not categorized**
Check if products have main_category set:

```javascript
fetch("/data/adam-audio.json")
  .then((r) => r.json())
  .then((d) => console.log("First product:", d.products[0]));
```

If main_category is missing/undefined, run taxonomy aggregator again.

### Issue: Some products "Uncategorized"

This shouldn't happen with the unified taxonomy (allow_uncategorized=false).

**Check 1: Verify categorization rules**
In Console:

```javascript
fetch("/data/taxonomy.json")
  .then((r) => r.json())
  .then((d) => console.log("Rules:", d.categorization_rules));
```

Confirm `allow_uncategorized: false` and `must_categorize: true`.

**Check 2: Verify fallback aliases**

```javascript
fetch("/data/taxonomy.json")
  .then((r) => r.json())
  .then((d) =>
    console.log("Aliases:", d.categorization_rules.category_aliases),
  );
```

All 6 aliases should be present.

**Check 3: Re-run taxonomy aggregator**

```bash
python backend/ingestion/taxonomy_aggregator.py
pnpm dev  # Restart frontend
```

### Issue: Wrong category for product

**Verify mapping**:

```javascript
fetch("/data/taxonomy.json")
  .then((r) => r.json())
  .then((d) => {
    const brand = "adam-audio"; // Change to test brand
    console.log(`${brand} maps to:`, d.brand_category_mapping[brand]);
  });
```

If mapping is wrong, regenerate taxonomy from brand catalogs.

---

## Success Criteria Checklist

**All of these should be ✅ true:**

- [ ] Page loads without errors
- [ ] Taxonomy loads (green indicator)
- [ ] 6 category sectors visible (2×3 grid)
- [ ] All 5 main categories present
- [ ] No "Uncategorized" products visible
- [ ] All 6 products appear in correct categories:
  - [ ] ADAM Audio → Studio Monitors
  - [ ] Amphion → Studio Monitors
  - [ ] Bespeco → Audio Equipment
  - [ ] Drumdots → Percussion
  - [ ] Fzone → Audio Gear
  - [ ] Test Brand → Testing
- [ ] Product count badges show correct numbers
- [ ] Console shows 6 products processed
- [ ] Click into category shows products with categories
- [ ] Search finds products by category
- [ ] No console errors (red messages)

**If all checkboxes are ✅, the integration is complete and working!**

---

## Next Steps

Once integration testing passes:

1. **Create test suite** - Write automated tests for categorization
2. **Add new brands** - Run pipeline with real brand data
3. **Monitor edge cases** - Watch for uncategorized products
4. **Performance test** - Verify load times with large product counts

See [TAXONOMY_EXTENSION_GUIDE.md](./TAXONOMY_EXTENSION_GUIDE.md) for adding new brands.
