# Halilit Pipeline v5.0 - Architecture Guide

## Overview

Version 5.0 consolidates the previously fragmented data processing into a **single, unified pipeline** with clear separation between data sources and processing layers.

## Core Principles

### 1. Three Data Pillars

Each product's data comes from exactly three sources, each with distinct authority:

| Pillar         | Source                | Authority         | Data                          |
| -------------- | --------------------- | ----------------- | ----------------------------- |
| **Official**   | Manufacturer websites | Product identity  | Names, specs, images, manuals |
| **Commercial** | Halilit e-commerce    | Market reality    | Prices, SKUs, stock status    |
| **Contextual** | Expert reviews        | Real-world wisdom | Pros, cons, tips, issues      |

### 2. Three Processing Layers

Data flows through three sequential transformation layers:

```
Layer 1: NORMALIZE
├── Merge data from 3 pillars
├── Validate against Pydantic schemas
├── Compute content hashes
└── Output: NormalizedProduct

Layer 2: ENRICH
├── Map to standardized taxonomy
├── Assign quality tier (Diamond/Gold/Silver/Bronze)
├── Select hero/thumbnail images
├── Generate short descriptions
└── Output: EnrichedProduct

Layer 3: OPTIMIZE
├── Validate against UI component constraints
├── Generate URL slugs
├── Create search text
├── Produce filter tags
├── Add render hints
└── Output: OptimizedProduct (final)
```

### 3. Static Output

The pipeline produces static JSON files that the frontend loads directly:

```
frontend/public/data/
├── index.json           # Brand catalog index
├── adam-audio.json      # Products for ADAM Audio
├── amphion.json         # Products for Amphion
└── ...
```

## Data Models

All models are defined in `backend/pipeline/models.py` using Pydantic v2:

### Source Models (Input)

```python
# Pillar 1: Official
OfficialData(
    manufacturer_sku: str,
    official_name: str,
    brand_id: str,
    category: str,
    specifications: Dict[str, Dict[str, str]],
    images: List[Dict],
)

# Pillar 2: Commercial
CommercialData(
    halilit_sku: str,
    product_id: str,
    price_usd: float,
    stock_status: StockStatus,
)

# Pillar 3: Contextual
ContextualData(
    product_id: str,
    pros: List[str],
    cons: List[str],
    expert_tips: List[str],
    confidence_score: int,
)
```

### Output Model (Final)

```python
OptimizedProduct(
    id: str,
    name: str,
    slug: str,
    brand_id: str,
    category: str,
    subcategories: List[str],
    tier: str,  # diamond|gold|silver|bronze
    tier_score: int,
    description_short: str,
    description_full: str,
    price: Optional[float],
    stock_status: str,
    image_hero: Dict,
    image_gallery: List[Dict],
    specs: Dict[str, List[Dict]],
    pros: List[str],
    cons: List[str],
    expert_tips: List[str],
    search_text: str,
    filter_tags: List[str],
    render_hints: Dict[str, bool],
)
```

## Pipeline CLI

Single entry point: `python -m backend.pipeline`

```bash
# Full pipeline
python -m backend.pipeline run

# Specific stages
python -m backend.pipeline ingest     # Only harvest data
python -m backend.pipeline process    # Only process layers
python -m backend.pipeline deploy     # Only deploy to frontend

# Utilities
python -m backend.pipeline status     # Show data summary
python -m backend.pipeline types      # Generate TypeScript
```

### Options

```bash
# Process specific brands
python -m backend.pipeline run --brands adam-audio,amphion

# Skip stages
python -m backend.pipeline run --skip-ingest   # Use cached data
python -m backend.pipeline run --skip-deploy   # Don't update frontend

# Debug mode
python -m backend.pipeline run --debug
```

## Directory Structure

```
backend/
├── pipeline/                  # Main pipeline package
│   ├── __init__.py
│   ├── __main__.py           # CLI entry point
│   ├── config.py             # Configuration
│   ├── models.py             # Pydantic schemas
│   ├── runner.py             # Orchestrator
│   ├── typescript_generator.py
│   ├── harvesters/           # Data ingestion
│   │   ├── official.py       # Manufacturer scraper
│   │   ├── commercial.py     # Halilit scraper
│   │   └── contextual.py     # Review synthesizer
│   └── layers/               # Processing layers
│       ├── normalize.py      # Layer 1
│       ├── enrich.py         # Layer 2
│       └── optimize.py       # Layer 3
│
├── data/                     # Data storage
│   ├── 1_official/           # Raw official data
│   ├── 2_commercial/         # Raw commercial data
│   ├── 3_contextual/         # Raw contextual data
│   ├── 4_validated/          # Layer outputs
│   ├── 5_golden/             # Final catalogs
│   ├── brands/               # Brand metadata
│   ├── badges/               # Quality badges
│   └── reports/              # Pipeline reports
```

## Tier Scoring

Products are assigned quality tiers based on data completeness:

| Component      | Points | Criteria                               |
| -------------- | ------ | -------------------------------------- |
| Name           | 20     | 20 pts if ≥10 chars, 10 pts if present |
| Images         | 25     | 15 pts for hero, 10 pts for 3+ images  |
| Price          | 10     | 10 pts if price > 0                    |
| Description    | 15     | 15 pts if ≥100 chars, 8 pts if ≥30     |
| Specifications | 20     | 20 pts if ≥5 specs, 10 pts if ≥2       |
| Reviews        | 10     | 5 pts for pros/cons, 5 pts for tips    |

**Tier Thresholds:**

- 💎 Diamond: 75+
- 🥇 Gold: 60-74
- 🥈 Silver: 40-59
- 🥉 Bronze: 0-39

## TypeScript Integration

Types are auto-generated from Pydantic models:

```bash
python -m backend.pipeline types
```

Output: `frontend/src/types/generated.ts`

```typescript
export type TierLevel = "diamond" | "gold" | "silver" | "bronze";

export interface OptimizedProduct {
  id: string;
  name: string;
  slug: string;
  tier: TierLevel;
  // ...
}
```

## Context Agent

The Contextual Harvester uses real web search + AI synthesis:

1. **Search**: SerpAPI to find reviews on trusted domains
2. **Synthesize**: OpenAI to extract pros/cons/tips
3. **Score**: Confidence based on source count/quality

### Trusted Domains

- soundonsound.com
- musictech.com
- mixonline.com
- tapeop.com
- gearspace.com
- attackmagazine.com

### Configuration

```bash
export SERP_API_KEY=your_key
export OPENAI_API_KEY=your_key
```

When API keys are not set, mock data is used for development.

## Extending the Pipeline

### Adding a New Brand

1. Add to `backend/ingestion/manifest.json`
2. Run `python -m backend.pipeline run --brands new-brand`

### Adding a New Data Source

1. Create harvester in `backend/pipeline/harvesters/`
2. Register in `harvesters/__init__.py`
3. Update `runner.py` to call the new harvester

### Modifying Tier Rules

Edit thresholds in `backend/pipeline/config.py`:

```python
TIER_THRESHOLDS: dict = {
    "diamond": 75,
    "gold": 60,
    "silver": 40,
    "bronze": 0,
}
```

Modify scoring in `backend/pipeline/layers/enrich.py`.
