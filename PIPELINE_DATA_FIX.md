# Pipeline Data Fix — Official Specs Missing

## Problem Identified

**Root Cause**: The `enrich` step only scrapes Halilit product pages. It does NOT fetch official brand pages, so products never get `official_specs` during ingestion.

**Current Flow**:
1. `commercial-ingest` → Gets products from Halilit sitemap (basic data)
2. `enrich` → Only scrapes Halilit product pages (description, images, features)
3. **Missing**: Official brand page scraping during ingestion
4. Official data only fetched on-demand via JIT agent (when viewing product)

**Result**: Most products have no `official_specs` because:
- JIT only runs when a user opens a product
- JIT might fail or timeout
- Official URLs might not be found
- Products never get official data during batch ingestion

## Fix Applied

Updated `backend/scripts/enrich_catalog.py` to:

1. **Fetch official brand pages during enrichment** (not just on-demand)
2. **Prioritize official data** over Halilit data (per Source Rules)
3. **Check for existing `official_url`** from inventory/catalog first
4. **Fallback to URL discovery** if `official_url` not found
5. **Async-compatible** using `run_in_executor` for blocking HTTP calls

### Changes Made

**File**: `backend/scripts/enrich_catalog.py`

- Added official page fetching in `_enrich_one_async()`
- Checks for `official_specs` completeness before skipping
- Fetches official data even if Halilit data exists
- Official specs take precedence (per Source Rules)
- Better stats tracking (halilit_scraped vs official_scraped)

## How to Run

After this fix, run enrichment to populate official specs:

```bash
# Enrich all brands (will now fetch official pages)
PYTHONPATH=. python backend/conductor_main.py enrich

# Or run full pipeline
PYTHONPATH=. python backend/conductor_main.py ingest-all
```

The enrichment will now:
- Scrape Halilit pages (as before)
- **Also fetch official brand pages** for specs
- Save `official_specs` and `official_url` to product JSONs
- Products will have official data available immediately (not just on-demand)

## Expected Results

After running `enrich`:
- Products should have `official_specs` populated
- `official_url` should be set when found
- Quick Analysis should use official data (not just Halilit data)
- Product Detail view should show "Official Specifications" instead of "No detailed specifications ingested"

## Verification

Check if products have official specs:

```bash
# Check a brand file
cat frontend/public/data/allen-heath.json | jq '.[0] | {name: .product_name, official_specs: .official_specs, official_url: .official_url}'
```

Or check catalog after rebuild:
```bash
curl http://localhost:8000/api/conductor/catalog | jq '.products[0] | {name: .name, specs: .specs, official_url: .official_url}'
```

## Performance Notes

- Official page fetching adds ~0.5-2s per product (HTTP requests)
- Uses async executor to avoid blocking
- Can be parallelized with `--concurrent-products` flag
- Consider rate limiting to avoid hammering brand sites
