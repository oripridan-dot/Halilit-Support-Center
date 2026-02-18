# Sample Pipeline Validation — Operator Console v9.6.0

This document demonstrates the complete data pipeline flow and validates each step.

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│  STEP 1: INGESTION                                                      │
│  Source: Halilit.com + Brand Websites                                   │
│  Output: frontend/public/data/*.json (brand files)                      │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│  STEP 2: CATALOG BUILD                                                   │
│  Function: product_normalizer.build_catalog()                           │
│  Input: frontend/public/data/*.json                                     │
│  Output: backend/data/catalog_cache.json.gz                             │
│  Structure: { products[], indexes{}, metadata{} }                       │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│  STEP 3: API SERVING                                                     │
│  Endpoint: GET /api/conductor/catalog                                    │
│  Source: catalog_cache.json.gz (or rebuilds if stale)                   │
│  Response: ConductorCatalog JSON                                         │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│  STEP 4: FRONTEND CONSUMPTION                                            │
│  Hook: useConductorCatalog()                                             │
│  Views: DashboardView, InventoryView, ProductDetailView                 │
│  Search: GlobalSearch → /api/products/search                             │
└─────────────────────────────────────────────────────────────────────────┘
```

## Sample Data Flow

### Input: Brand JSON File
```json
// frontend/public/data/roland.json
[
  {
    "halilit_id": "ROL-001",
    "product_name": "Roland JUNO-X",
    "brand": "Roland",
    "price_il": 8999,
    "price_eilat": 7649,
    "halilit_url": "https://halilit.com/roland-juno-x",
    "image_url": "https://cdn.halilit.com/images/roland-juno-x.jpg",
    "official_url": "https://www.roland.com/products/juno-x/",
    "official_specs": {
      "keys": 61,
      "polyphony": "128 voices",
      "weight": "6.2 kg"
    }
  }
]
```

### Processed: Catalog Product
```json
// After build_catalog() normalization
{
  "id": "ROL-001",
  "name": "Roland JUNO-X",
  "brand": "Roland",
  "galaxy_id": "keys-production",
  "spectrum_id": "synthesizers",
  "category": "Keys & Production",
  "subcategory": "Synthesizers",
  "price": 8999,
  "price_eilat": 7649,
  "currency": "ILS",
  "image_url": "https://cdn.halilit.com/images/roland-juno-x.jpg",
  "specs": {
    "keys": 61,
    "polyphony": "128 voices",
    "weight": "6.2 kg"
  },
  "halilit_url": "https://halilit.com/roland-juno-x",
  "official_url": "https://www.roland.com/products/juno-x/"
}
```

### API Response: /api/conductor/catalog
```json
{
  "products": [ /* array of normalized products */ ],
  "indexes": {
    "by_galaxy": {
      "keys-production": [0, 1, 2, ...]
    },
    "by_spectrum": {
      "synthesizers": [0, 5, 12, ...]
    },
    "by_brand": {
      "Roland": [0, 1, 2, ...]
    },
    "relationships": {
      "ROL-001": [ /* product relationships */ ]
    }
  },
  "metadata": {
    "total_products": 6500,
    "brands": ["Roland", "Nord", "Moog", ...],
    "galaxy_counts": {
      "keys-production": 1200,
      "guitars-bass": 1800,
      ...
    },
    "health_score": 87,
    "timestamp": "2026-02-18T10:30:00"
  }
}
```

### Frontend Consumption
```typescript
// DashboardView.tsx
const { totalProducts, isLoading } = useConductorCatalog();
// → totalProducts: 6500

// InventoryView.tsx
const { products } = useConductorCatalog();
// → products: ConductorProduct[] (6500 items)

// GlobalSearch.tsx
fetch('/api/products/search?q=juno')
// → { products: [{ id: "ROL-001", product_name: "Roland JUNO-X", ... }] }
```

## Validation Commands

### 1. Check Pipeline Structure
```bash
python3 test_pipeline.py
```

### 2. Quick Integration Check
```bash
./validate_integration.sh
```

### 3. Manual Pipeline Test
```bash
# Step 1: Ingest data (if needed)
python backend/conductor_main.py skeleton-sync

# Step 2: Build catalog
python backend/conductor_main.py rebuild-catalog

# Step 3: Start servers
./start_console.sh

# Step 4: Test API (in another terminal)
curl http://localhost:8000/api/health
curl http://localhost:8000/api/conductor/catalog | jq '.metadata.total_products'
curl "http://localhost:8000/api/products/search?q=juno" | jq '.products[0].product_name'

# Step 5: Open frontend
open http://localhost:5173
```

## Expected Results

### Test 1: File Structure ✅
- All required directories exist
- Key files present (server.py, conductor_main.py, etc.)

### Test 2: Brand JSON Files ✅
- At least one brand JSON file in `frontend/public/data/`
- Valid JSON structure (array or dict with products)

### Test 3: Catalog Build ✅
- `build_catalog()` completes without errors
- Catalog contains `products`, `indexes`, `metadata`
- Indexes include `by_galaxy`, `by_spectrum`, `by_brand`
- `total_products > 0`

### Test 4: API Endpoints ✅
- `/api/health` returns 200 OK
- `/api/conductor/catalog` returns valid JSON
- Response includes expected structure

### Test 5: Frontend Components ✅
- All required React components exist
- Hooks properly structured
- Navigation store has correct state

### Test 6: Navigation Store ✅
- Contains `searchQuery` state
- Has `goToInventory(searchQuery?)` function
- No camera/zoom logic

### Test 7: Pipeline Flow ✅
- Ingestion → JSON files
- JSON files → Catalog build
- Catalog → API serving
- API → Frontend consumption
- All steps connected

## Sample Test Output

```
======================================================================
  HALILIT OPERATOR CONSOLE — PIPELINE VALIDATION TEST
  Version 9.6.0
======================================================================

======================================================================
  TEST 1: File Structure
======================================================================
✅ PASS: Backend directory: backend
✅ PASS: Frontend directory: frontend
✅ PASS: Data directory: backend/data
✅ PASS: Frontend public data: frontend/public/data
✅ PASS: Server file: backend/server.py
✅ PASS: Conductor CLI: backend/conductor_main.py
✅ PASS: Startup script: start_console.sh

======================================================================
  TEST 2: Brand JSON Files
======================================================================
✅ PASS: Found 84 brand JSON file(s)
✅ PASS: Sample file 'roland.json': 156 products (list format)

======================================================================
  TEST 3: Catalog Build
======================================================================
Building catalog from frontend/public/data...
✅ PASS: Catalog built successfully
   • Products: 6500
   • Indexes: ['by_galaxy', 'by_spectrum', 'by_brand', 'relationships']
   • Metadata keys: ['total_products', 'brands', 'galaxy_counts', ...]
✅ PASS: All required indexes present
   • Total products: 6500
   • Brands: 84
✅ PASS: Catalog contains 6500 products

======================================================================
  TEST 4: API Endpoints
======================================================================
✅ PASS: Health check: /api/health (200 OK)
✅ PASS: Catalog endpoint: /api/conductor/catalog (200 OK)

======================================================================
  TEST 5: Frontend Components
======================================================================
✅ PASS: Main app component: App.tsx
✅ PASS: Global search component: components/GlobalSearch.tsx
✅ PASS: Dashboard view: components/views/DashboardView.tsx
✅ PASS: Inventory view: components/views/InventoryView.tsx
✅ PASS: Product detail view: components/views/ProductDetailView.tsx
✅ PASS: Catalog hook: hooks/useConductorCatalog.ts
✅ PASS: JIT intelligence hook: hooks/useJITIntelligence.ts
✅ PASS: Navigation store: store/navigationStore.ts

======================================================================
  TEST 6: Navigation Store
======================================================================
✅ PASS: ViewType definition
✅ PASS: searchQuery state
✅ PASS: goToInventory function
✅ PASS: setSearchQuery function
✅ PASS: No camera/zoom logic

======================================================================
  TEST 7: Pipeline Flow Validation
======================================================================
✅ PASS: 1. Ingestion: Brand JSONs in frontend/public/data
✅ PASS: 2. Catalog Build: build_catalog() function
✅ PASS: 3. API Serving: server.py mounts /api/conductor/catalog
✅ PASS: 4. Frontend Hook: useConductorCatalog uses /api/conductor/catalog
✅ PASS: 5. GlobalSearch: Uses /api/products/search

======================================================================
TEST SUMMARY
======================================================================
✅ PASS: File Structure
✅ PASS: Brand JSON Files
✅ PASS: Catalog Build
✅ PASS: API Endpoints
✅ PASS: Frontend Components
✅ PASS: Navigation Store
✅ PASS: Pipeline Flow

Total: 7/7 tests passed
✅ PASS: All tests passed! System is ready.
```

## Troubleshooting

### Issue: No brand JSON files
**Solution:** Run `python backend/conductor_main.py skeleton-sync`

### Issue: Catalog build fails
**Solution:** Check that `frontend/public/data/*.json` files exist and are valid JSON

### Issue: API returns 503
**Solution:** Catalog is still building. Wait 30-60 seconds or check `backend.log`

### Issue: Frontend shows "Catalog unavailable"
**Solution:** 
1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check browser console for errors
3. Verify Vite proxy is configured correctly

### Issue: Search doesn't work
**Solution:**
1. Check that `/api/products/search` endpoint exists
2. Verify GlobalSearch is using the API (not static files)
3. Check browser network tab for failed requests
