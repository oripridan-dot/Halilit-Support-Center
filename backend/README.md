# Backend Pipeline v5.0

✅ **Production Ready** - Unified data processing pipeline for the Halilit Support Center.

## 📚 Documentation

**Start with these guides** (in order):

1. **`../PIPELINE_v5_SUMMARY.md`** - Quick overview & status
2. **`../PIPELINE_PRODUCTION_GUIDE.md`** - Complete system guide
3. **`../PIPELINE_CLI_REFERENCE.md`** - Command reference
4. **`../REAL_DATA_INTEGRATION_GUIDE.md`** - Real data setup

## 🏗️ Architecture

```
3 SOURCES          3 LAYERS           FRONTEND OUTPUT
┌──────────┐      ┌──────────┐      ┌─────────────────┐
│ Official ├─────→│Normalize ├─────→│ Golden JSON     │
│Commercial│      │Enrich    │      │TypeScript Types │
│Contextual│      │Optimize  │      │Search Index     │
└──────────┘      └──────────┘      └─────────────────┘
```

### Three Data Sources (Harvesters)

- **Official**: Manufacturer specs, images, descriptions
- **Commercial**: Halilit prices, SKUs, stock status
- **Contextual**: Expert reviews, pros/cons, tips (from web search + AI)

### Three Processing Layers

1. **Normalize**: Merge & validate data with Pydantic schemas
2. **Enrich**: Taxonomy mapping, tier assignment (Bronze/Silver/Gold/Diamond)
3. **Optimize**: UI-ready JSON with slugs, search text, render hints

## 🚀 Quick Start

```bash
cd /workspaces/Halilit-Support-Center

# Test with mock data (no API keys needed)
PYTHONPATH=. python -m backend.pipeline run

# Expected: ✅ Pipeline complete: 6 brands, 6 products
```

## 💻 CLI Commands

```bash
# Full pipeline
PYTHONPATH=. python -m backend.pipeline run

# Individual stages
PYTHONPATH=. python -m backend.pipeline ingest    # Harvest only
PYTHONPATH=. python -m backend.pipeline process   # Process only
PYTHONPATH=. python -m backend.pipeline deploy    # Deploy only

# Utilities
PYTHONPATH=. python -m backend.pipeline status    # Check status
PYTHONPATH=. python -m backend.pipeline validate  # Validate data
PYTHONPATH=. python -m backend.pipeline types     # Generate types
```

See `../PIPELINE_CLI_REFERENCE.md` for full command reference.

## 🔧 Configuration

### Environment Variables (`.env`)

```bash
# Required for real data
SERP_API_KEY=your_serpapi_key           # Web search
OPENAI_API_KEY=your_openai_key          # AI synthesis

# Optional settings
SCRAPER_HEADLESS=true
SCRAPER_TIMEOUT_MS=30000
SCRAPER_RETRIES=3
LOG_LEVEL=INFO
```

See `../.env.example` for all options.

### Brands Configuration

Edit `ingestion/manifest.json` to add or update brands:

```json
{
  "brands": [
    {
      "id": "adam-audio",
      "name": "ADAM Audio",
      "official_url": "https://www.adam-audio.com",
      "commercial_url": "https://halilit.com/?s=adam+audio"
    }
  ]
}
```

## 📊 Data Flow

```
backend/data/
├── 1_official/     # Raw manufacturer data
├── 2_commercial/   # Raw commercial data
├── 3_contextual/   # Raw contextual data
├── 4_validated/    # Normalized + enriched
├── 5_golden/       # Final optimized catalogs
└── reports/        # Pipeline run reports

frontend/public/data/
├── index.json      # Catalog index
└── {brand}.json    # Per-brand catalogs
```

## Testing

```bash
python -m pytest backend/tests/test_pipeline_e2e.py -v
```
