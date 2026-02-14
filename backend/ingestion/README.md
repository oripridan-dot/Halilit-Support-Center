# Ingestion — JIT Architecture

Lightweight ingestion utilities retained from the original pipeline. The heavy 7-phase pipeline
has been replaced by **skeleton sync** (fast inventory) + **JIT Agent** (on-demand intelligence).

## Active Modules

| Module                    | Purpose                                          |
| ------------------------- | ------------------------------------------------ |
| `data_models.py`          | Pydantic models (`IngestionProductDraft`, enums) |
| `taxonomy_manager.py`     | Category classification (8 cats, 32 subcats)     |
| `pricing_engine.py`       | Price tier assignment & validation               |
| `display_engine.py`       | Display roles, media assets, visual props        |
| `halilit_page_scraper.py` | Halilit.com product scraping (skeleton + JIT)    |
| `guardrails.py`           | Data quality guardrails                          |
| `ingestion_database.py`   | SQLite storage for product state                 |

## Usage (v9.0)

```python
# Skeleton sync — fast inventory from Halilit.com
from backend.skeleton_sync import run_skeleton_sync
run_skeleton_sync()  # ~30 seconds for all brands

# JIT intelligence — on-demand per product
from backend.jit_agent import stream_product_intelligence
async for event in stream_product_intelligence("product-id"):
    print(event)
```

## Key Data Types

- `IngestionProductDraft` — unified product model
- `PricingTier` — Entry / Mid / Pro / Flagship / Legacy
- `DisplayRole` — Hero / Cornerstone / Specialist / Entry
- `IngestionStatus` — status tracking
