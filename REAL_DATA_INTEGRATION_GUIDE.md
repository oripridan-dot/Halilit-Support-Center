# Real Data Integration Guide

## Overview

This guide explains how to integrate real data from actual manufacturer websites, e-commerce platforms, and review sites into the Halilit Support Center pipeline.

---

## Phase 1: Data Source Configuration

### Step 1.1: Define Your Brands

Edit `backend/ingestion/manifest.json`:

```json
{
  "brands": [
    {
      "id": "your-brand-id",
      "name": "Your Brand Name",
      "official_url": "https://your-official-website.com",
      "official_products": [
        "https://your-official-website.com/product-1",
        "https://your-official-website.com/product-2"
      ],
      "commercial_url": "https://halilit.com/?s=your+brand",
      "category": "Your Category"
    }
  ]
}
```

**Fields**:

- `id`: lowercase, hyphenated, unique identifier
- `name`: Display name (full branding)
- `official_url`: Brand's official website
- `official_products`: List of specific product pages to scrape (optional - if not provided, auto-discovers)
- `commercial_url`: Halilit website search/category URL
- `category`: Primary category (e.g., "Studio Monitors", "Microphones")

---

### Step 1.2: Configure API Keys

Create or update `.env` file:

```bash
# SerpAPI for web search (required for contextual data)
SERP_API_KEY=your_serpapi_key

# OpenAI for AI synthesis (required for context synthesis)
OPENAI_API_KEY=your_openai_key

# Or use Google Gemini as alternative
GEMINI_API_KEY=your_gemini_key
```

**Get API Keys**:

#### SerpAPI

1. Visit https://serpapi.com
2. Sign up for free account (100 searches/month)
3. Get API key from dashboard
4. Set `SERP_API_KEY` in `.env`

#### OpenAI

1. Visit https://platform.openai.com
2. Create account and add payment method
3. Generate API key
4. Set `OPENAI_API_KEY` in `.env`
5. Recommended: Use `gpt-3.5-turbo` (cost-effective, ~$0.002 per request)

#### Google Gemini

1. Visit https://makersuite.google.com/app/apikey
2. Create new API key
3. Set `GEMINI_API_KEY` in `.env`
4. Free tier available

---

## Phase 2: Official Data Harvesting

### Step 2.1: Understand Official Data

Official data comes from manufacturer websites and includes:

- Product names and SKUs
- Technical specifications
- Product descriptions
- Product images and gallery
- Downloadable manuals
- Categories and subcategories

### Step 2.2: Configure Official Harvester

The `OfficialHarvester` uses Playwright to scrape manufacturer websites.

**Configuration** (in `backend/pipeline/config.py`):

```python
SCRAPER_HEADLESS = True          # Run browser headless (no GUI)
SCRAPER_TIMEOUT_MS = 30000       # Page load timeout
SCRAPER_RETRIES = 3              # Retry failed pages
SCRAPER_CONCURRENT = 3           # Parallel browser instances
```

### Step 2.3: Custom Scraping for Complex Sites

If automatic scraping doesn't work well, manually create `backend/data/1_official/{brand_id}.json`:

```json
{
  "brand_id": "adam-audio",
  "brand_name": "ADAM Audio",
  "harvested_at": "2026-01-31T12:00:00Z",
  "products": [
    {
      "manufacturer_sku": "T7V",
      "official_name": "ADAM Audio T7V",
      "category": "Studio Monitors",
      "description": "Compact 3-way active monitor for project studios",
      "specifications": {
        "Audio": [
          { "key": "Frequency Response", "value": "38Hz - 24kHz" },
          { "key": "Maximum SPL", "value": "105 dB" },
          { "key": "Woofer Size", "value": "6.5 inch" }
        ],
        "Connectivity": [{ "key": "Inputs", "value": "XLR, RCA" }]
      },
      "images": [
        {
          "url": "https://example.com/product/t7v/front.jpg",
          "alt": "Front view",
          "type": "hero"
        }
      ],
      "official_url": "https://www.adam-audio.com/en/pro-monitors/t7v"
    }
  ]
}
```

**Testing**:

```bash
# Run only official harvester (test mode)
PYTHONPATH=. python -m backend.pipeline ingest --brands adam-audio
```

---

## Phase 3: Commercial Data Integration

### Step 3.1: Understand Commercial Data

Commercial data from Halilit includes:

- Product prices (in multiple currencies)
- SKU/part numbers
- Stock status (In Stock, Pre-order, Discontinued)
- Product availability
- Last updated timestamp

### Step 3.2: Halilit Website Integration

The `CommercialHarvester` scrapes product prices and availability from Halilit.

**Configuration**:

```python
# backend/pipeline/config.py
HALILIT_BASE_URL = "https://halilit.com"
HALILIT_TIMEOUT = 30000
HALILIT_RETRIES = 3
```

### Step 3.3: Manual Commercial Data

If Halilit integration isn't complete, manually create `backend/data/2_commercial/{brand_id}.json`:

```json
{
  "brand_id": "adam-audio",
  "source": "halilit",
  "harvested_at": "2026-01-31T12:00:00Z",
  "products": [
    {
      "product_id": "adam-audio-t7v",
      "price": 799.0,
      "currency": "USD",
      "original_price": 899.0,
      "discount_percent": 11,
      "stock_status": "in_stock",
      "stock_quantity": 15,
      "product_url": "https://halilit.com/products/adam-audio-t7v",
      "seller": "halilit",
      "last_updated": "2026-01-31T12:00:00Z"
    }
  ]
}
```

**Testing**:

```bash
# Verify commercial data was harvested
cat backend/data/2_commercial/adam-audio.json | jq '.products[] | {price, stock_status}'
```

---

## Phase 4: Contextual Data Integration

### Step 4.1: Understand Contextual Data

Contextual data includes expert reviews and synthesis:

- Product pros and cons
- Practical tips and tricks
- Use-case recommendations
- Review sources
- Confidence scores

### Step 4.2: Web Search Configuration

The `ContextualHarvester` searches trusted review sites:

```
Trusted Domains:
- soundonsound.com      (SOS Magazine)
- musictech.net         (MusicTech Magazine)
- mixonline.com         (Mix Magazine)
- tapeop.com            (Tape OP Magazine)
- gearspace.com         (Gearspace Forum)
- attackmagazine.com    (Attack Magazine)
- residentadvisor.net   (Resident Advisor)
- pro-tools-expert.com  (Pro Tools Expert)
```

### Step 4.3: AI Synthesis Configuration

The pipeline uses AI to synthesize review data into structured format:

```python
# backend/pipeline/harvesters/contextual.py

# OpenAI configuration
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_TEMPERATURE = 0.7
OPENAI_MAX_TOKENS = 500

# Or use Gemini
GEMINI_MODEL = "gemini-pro"
```

### Step 4.4: Manual Contextual Data

If automatic search/synthesis doesn't work, manually create `backend/data/3_contextual/{brand_id}.json`:

```json
{
  "brand_id": "adam-audio",
  "source": "research",
  "harvested_at": "2026-01-31T12:00:00Z",
  "products": [
    {
      "product_id": "adam-audio-t7v",
      "product_name": "ADAM Audio T7V",
      "reviews": [
        {
          "source": "soundonsound.com",
          "source_url": "https://soundonsound.com/reviews/adam-audio-t7v",
          "excerpt": "Excellent compact monitors with punchy bass",
          "date": "2025-06-15"
        }
      ],
      "pros": [
        "Compact size ideal for small studios",
        "Accurate bass response for small room",
        "Great value for money",
        "Professional build quality"
      ],
      "cons": [
        "Limited low-end extension below 38Hz",
        "Not ideal for large room acoustics",
        "Requires near-field positioning"
      ],
      "tips": [
        "Position at ear level in triangle formation",
        "Use foam isolation pads to minimize reflections",
        "Give 30+ minutes warm-up time",
        "Best suited for rooms 100-200 sqft"
      ],
      "summary": "Professional-grade compact studio monitors with excellent accuracy",
      "confidence_score": 85
    }
  ]
}
```

---

## Phase 5: Testing the Integration

### Step 5.1: Test Single Brand

```bash
# Test with one brand (recommended)
PYTHONPATH=. python -m backend.pipeline run \
  --brands adam-audio \
  --log-level DEBUG

# Check ingestion output
cat backend/data/1_official/adam-audio.json | jq '.products | length'
cat backend/data/2_commercial/adam-audio.json | jq '.products | length'
cat backend/data/3_contextual/adam-audio.json | jq '.products | length'
```

### Step 5.2: Test Processing Layers

```bash
# Process (without re-harvesting)
PYTHONPATH=. python -m backend.pipeline process \
  --brands adam-audio \
  --skip-ingest

# Check processing output
cat backend/data/5_golden/adam-audio.json | jq '.products[0]'
```

### Step 5.3: Validate Output

```bash
# Validate final data
PYTHONPATH=. python -m backend.pipeline validate \
  --stage 5_golden \
  --brands adam-audio \
  --verbose
```

### Step 5.4: Check Frontend Data

```bash
# Check deployed frontend data
cat frontend/public/data/adam-audio.json | jq '.products[0] | {name, slug, tier, price}'

# Check search index
cat frontend/public/data/search_index.json | jq '.[] | select(.brand == "adam-audio")'

# Check TypeScript types
head -50 frontend/src/types/generated.ts
```

---

## Phase 6: Production Scaling

### Step 6.1: Add More Brands

Update `backend/ingestion/manifest.json` with additional brands:

```json
{
  "brands": [
    {
      "id": "adam-audio",
      "name": "ADAM Audio",
      ...
    },
    {
      "id": "neumann",
      "name": "Neumann",
      ...
    },
    {
      "id": "focal",
      "name": "Focal",
      ...
    }
  ]
}
```

### Step 6.2: Run Full Pipeline

```bash
# Process all brands
PYTHONPATH=. python -m backend.pipeline run

# Or process in batches
PYTHONPATH=. python -m backend.pipeline run --brands adam-audio neumann
PYTHONPATH=. python -m backend.pipeline run --brands focal rode

# Then deploy all
PYTHONPATH=. python -m backend.pipeline deploy
```

### Step 6.3: Monitor Quality

```bash
# View pipeline report
PYTHONPATH=. python -m backend.pipeline status

# Check for errors
cat backend/data/reports/pipeline-*.json | jq '.errors'

# Verify all products
PYTHONPATH=. python -m backend.pipeline validate --stage 5_golden
```

---

## Phase 7: Continuous Updates

### Step 7.1: Schedule Regular Updates

```bash
# Create cron job for daily updates (Linux/Mac)
crontab -e

# Add line:
0 2 * * * cd /workspaces/Halilit-Support-Center && PYTHONPATH=. python -m backend.pipeline run >> pipeline.log 2>&1
```

### Step 7.2: Incremental Updates

```bash
# Update only commercial data (prices/stock)
# Usually changes most frequently
PYTHONPATH=. python -m backend.pipeline ingest \
  --skip-official \
  --skip-contextual \
  --brands all

# Then process and deploy
PYTHONPATH=. python -m backend.pipeline process --skip-ingest
PYTHONPATH=. python -m backend.pipeline deploy
```

### Step 7.3: Backup Strategy

```bash
# Backup golden data before major runs
cp -r backend/data/5_golden backup/golden-$(date +%Y%m%d-%H%M%S)

# Or tag in git
git add backend/data/5_golden
git commit -m "Production: 50 brands, 1000 products"
```

---

## Troubleshooting Real Data Integration

### Issue: "Unable to scrape official website"

**Causes**:

- Website blocked scraping
- Dynamic content (JavaScript-rendered)
- Authentication required
- CAPTCHAs present

**Solutions**:

1. Manually create `1_official/{brand}.json` with data
2. Use Playwright's `wait_for_selector()` for dynamic content
3. Add custom selectors to official harvester
4. Check if website allows scraping (robots.txt)

### Issue: "Prices not found on Halilit"

**Solution**:
Manually create `2_commercial/{brand}.json` with pricing data

### Issue: "Insufficient sources found for contextual data"

**Cause**: No reviews found on trusted domains

**Solutions**:

1. Try more searches with different queries
2. Manually add review data to `3_contextual/{brand}.json`
3. Increase retry count: `SCRAPER_RETRIES=5`
4. Check if SerpAPI key is valid

### Issue: "AI synthesis uses mock data"

**Cause**: OPENAI_API_KEY not set

**Solutions**:

1. Set API key in `.env`: `OPENAI_API_KEY=sk-...`
2. Or use Gemini: `GEMINI_API_KEY=...`
3. Verify keys have sufficient credits/quota

---

## Data Quality Checklist

Before deploying to production, verify:

- [ ] All brands have official data (specs, images)
- [ ] All products have commercial data (prices, stock)
- [ ] All products have contextual data (reviews, pros/cons)
- [ ] All data passes validation
- [ ] Confidence scores are above 50%
- [ ] No sensitive data exposed
- [ ] Images are accessible and loading
- [ ] TypeScript types generated correctly
- [ ] Frontend search works correctly
- [ ] Price ranges are reasonable

---

## Performance Optimization for Real Data

### Optimize API Usage

```bash
# Use cache when possible
PYTHONPATH=. python -m backend.pipeline run --skip-ingest

# Process in batches to stay within rate limits
for brand in brand1 brand2 brand3; do
  PYTHONPATH=. python -m backend.pipeline run --brands $brand
  sleep 30  # Rate limit buffer
done
```

### Reduce Scraping Time

```bash
# Only scrape specific products (not all)
# In manifest.json, add specific product URLs:
"official_products": [
  "https://example.com/product-1",
  "https://example.com/product-2"
]

# Skip products that don't need updates
# (Use cache for unchanged products)
```

### Monitor Costs

```
SerpAPI: ~$50/month for 5000 searches
OpenAI: ~$0.002 per product synthesis (~$200/1000 products)
Playwright: Free (open source)
```

---

## Next Steps

1. **Configure APIs**: Get SerpAPI and OpenAI keys
2. **Update Manifest**: Add your brands to `manifest.json`
3. **Test One Brand**: Run full pipeline for single brand
4. **Validate Output**: Check quality and completeness
5. **Scale Up**: Add more brands gradually
6. **Deploy**: Push to production frontend
7. **Monitor**: Set up automated daily updates

---

**Last Updated**: 2026-01-31
**Version**: 5.0
