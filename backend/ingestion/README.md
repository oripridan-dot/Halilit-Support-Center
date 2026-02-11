# Ingestion Pipeline

7-phase pipeline for harvesting, enriching, and validating product data.

## Pipeline Phases

```
Phase 1: HARVEST    → CommercialScout extracts products from Halilit.com
Phase 2: ENRICH     → OfficialVerifier adds specs, images, descriptions
Phase 3: VISUALS    → VisualValidator resolves & verifies images (Gemini 2.0-flash)
Phase 4: TIER       → PricingEngine assigns price tiers (entry/mid/pro/flagship)
Phase 5: PREPARE    → DisplayEngine formats for frontend display
Phase 6: VALIDATE   → ExternalValidator checks compliance & completeness
Phase 7: APPROVE    → Final verification gate
```

## Modules

| Module                   | Purpose                                     |
| ------------------------ | ------------------------------------------- |
| `orchestrator.py`        | Pipeline coordinator — runs all 7 phases    |
| `data_models.py`         | Pydantic models (`IngestionProductDraft`, enums) |
| `taxonomy_manager.py`    | Category classification (8 cats, 32 subcats)|
| `pricing_engine.py`      | Price tier assignment & validation          |
| `display_engine.py`      | Display roles, media assets, visual props   |
| `visual_validator.py`    | Image verification via Gemini 2.0-flash     |
| `visual_comparator.py`   | Image comparison utilities                  |
| `halilit_page_scraper.py`| Halilit.com product scraping                |
| `official_page_scraper.py`| Manufacturer page scraping                 |
| `spectrum_adapter.py`    | Frontend data adapter                       |
| `trinity_integration.py` | Trinity Swarm agent integration             |
| `guardrails.py`          | Data quality guardrails                     |
| `match_learning.py`      | Product matching & learning                 |
| `ingestion_database.py`  | SQLite storage for pipeline state           |

## Usage

```python
from backend.ingestion import get_ingestion_orchestrator, IngestionProductDraft, PricingTier

orchestrator = get_ingestion_orchestrator()
report = orchestrator.ingest_batch("Roland", raw_products)

# report.approved_products  → list of enriched products
# report.rejected_products  → list with rejection reasons
```

## Key Data Types

- `IngestionProductDraft` — unified product model through pipeline
- `PricingTier` — Entry / Mid / Pro / Flagship / Legacy
- `DisplayRole` — Hero / Cornerstone / Specialist / Entry
- `IngestionStatus` — status tracking through phases
- `IngestionReport` — pipeline execution results
