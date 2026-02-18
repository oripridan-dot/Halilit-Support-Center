# Re-scraping Commands with Fixed Data Extraction

## Quick Test (Single Brand)

Test the improved scraper with a single brand:

```bash
# Activate virtual environment
source .venv/bin/activate

# Test with "adam audio" brand (uses improved scraper with DOM fallbacks)
PYTHONPATH=. python backend/conductor_main.py commercial-ingest "adam audio" --try-scrape

# Or test with any other brand
PYTHONPATH=. python backend/conductor_main.py commercial-ingest "Roland" --try-scrape
```

## Full Re-scrape (All Brands)

**Warning: This will take a long time (hours) and will scrape all brands**

```bash
# Activate virtual environment
source .venv/bin/activate

# Re-scrape all brands with improved data extraction
PYTHONPATH=. python backend/conductor_main.py commercial-ingest --try-scrape

# Or with parallel workers (faster but more aggressive)
PYTHONPATH=. python backend/conductor_main.py commercial-ingest --try-scrape --workers 4
```

## What Changed

The scraper now:
- ✅ Extracts prices from DOM when JSON-LD is missing
- ✅ Extracts features/specs from product pages
- ✅ Extracts better descriptions
- ✅ Preserves listing prices when merging data
- ✅ Uses improved price pattern matching for Hebrew prices

## After Re-scraping

After re-scraping, rebuild the catalog to see the improvements:

```bash
# Rebuild catalog with new data
PYTHONPATH=. python backend/conductor_main.py rebuild-catalog

# Or sync to frontend
PYTHONPATH=. python backend/conductor_main.py sync
```

## Verify Data Quality

Check a brand file to see if prices and features are now populated:

```bash
# Check "adam audio" data
cat frontend/public/data/adam\ audio.json | python3 -m json.tool | head -50

# Look for:
# - "price_il": should be > 0 (not 0.0)
# - "features": should have entries (not empty array)
# - "description": should have real text (not empty or placeholder)
```
