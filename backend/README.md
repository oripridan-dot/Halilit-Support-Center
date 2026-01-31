# Backend Pipeline v5.0

Unified data processing pipeline for the Halilit Support Center.

## Architecture

```
3 Sources → 3 Layers → Frontend JSON
```

### Three Data Sources (Harvesters)
- **Official**: Manufacturer data (specs, names, images, manuals)
- **Commercial**: Halilit website (prices, SKUs, stock status)
- **Contextual**: Expert reviews via web search + AI synthesis

### Three Processing Layers
1. **Normalize**: Merge & validate with Pydantic schemas
2. **Enrich**: Taxonomy mapping, tier assignment (Diamond/Gold/Silver/Bronze)
3. **Optimize**: UI-ready JSON with slugs, search text, render hints

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run full pipeline
python -m backend.pipeline run

# Check status
python -m backend.pipeline status

# Generate TypeScript types
python -m backend.pipeline types
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `run` | Full pipeline (ingest → process → deploy) |
| `ingest` | Run harvesters only |
| `process` | Run layers only |
| `deploy` | Deploy to frontend |
| `types` | Generate TypeScript types |
| `status` | Show pipeline status |

## Data Flow

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
