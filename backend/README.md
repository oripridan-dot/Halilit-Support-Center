# Backend Pipeline v4.1

Static-first data processing pipeline for the Halilit Support Center.

## Purpose
Generates static JSON catalogs from brand blueprints and Halilit raw data.

## Architecture
- **Input**: Raw brand data in `data/blueprints/` and `data/vault/`
- **Process**: Python scripts orchestrate scraping, normalization, and catalog generation
- **Output**: Static JSON files to `frontend/public/data/`

## Key Scripts
- **forge_backbone.py**: Main orchestrator - generates unified catalog.json
- **mass_ingest_protocol.py**: Brand data ingestion coordinator

## Services
- **Brand Scrapers**: Extract product data from manufacturer sites (Halilit, Boss, Moog, Nord, Roland)
- **Processors**: Transform raw data into standardized models
- **Generators**: Build static JSON catalogs for frontend consumption

## Data Flow
```
blueprints/ (raw brand data)
     ↓
services/scrapers → parsers → processors
     ↓
models/product_hierarchy → catalog_manager
     ↓
frontend/public/data/catalog.json
```

## Usage
```bash
# Generate static catalog
python forge_backbone.py

# Run mass ingestion
python mass_ingest_protocol.py
```

## Models
- **product_hierarchy.py**: Product, category, brand data structures
- **brand_taxonomy.py**: Brand classification system
- **category_consolidator.py**: Category normalization

## Environment
- Python 3.11+
- Dependencies in requirements.txt
- No runtime database - all data pre-compiled to static JSON
