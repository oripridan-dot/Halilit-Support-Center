# Ingestion — JIT Architecture

Lightweight ingestion utilities retained from the original pipeline. The heavy 7-phase pipeline
has been replaced by **skeleton sync** (fast inventory) + **JIT Agent** (on-demand intelligence).

## Full Ingestion Pipeline

| Step | Source | Conductor | What |
|------|--------|-----------|------|
| **Commercial** | Halilit.com | `commercial-ingest` | Golden List, prices, SKUs, product list |
| **Enrich** | Halilit product pages | `enrich` | Description, images, features, media |
| **Sync** | — | (part of `ingest-all`) | Rebuild index + catalog from JSONs |
| **Graph** | — | (part of `ingest-all`) | Build product graph with relationships in priority order |
| **Official** | Brand product pages | JIT agent on-demand | Specs, official_url, official_images |
| **Contextual** | 3+ review sites | JIT agent on-demand | Reviews, pros/cons, synthesis |

**Relationship priority (when building the graph):**  
1. **Primary — official** (brand page “accessories/related” and text)  
2. **Secondary — commercial** (catalog: variant families + accessory links from Halilit data)  
3. **Third — contextual** (reviews: “works with X”)  
4. **Fourth — spectrum** (same spectrum/tier alternatives, cross-brand)

Run full pipeline from project root:
`PYTHONPATH=. python backend/conductor_main.py ingest-all`

For **best data quality**: run with multiple workers and the pipeline review agent (validates each phase, retries on failure, suggests improvements):
`PYTHONPATH=. python backend/conductor_main.py ingest-all --workers 4 --with-review-agent`

## Active Modules

| Module                                | Purpose                                          |
| ------------------------------------- | ------------------------------------------------ |
| `data_models.py`                      | Pydantic models (`IngestionProductDraft`, enums) |
| `taxonomy_manager.py`                 | Category classification (8 cats, 32 subcats)     |
| `pricing_engine.py`                   | Price tier assignment & validation               |
| `display_engine.py`                   | Display roles, media assets, visual props        |
| `halilit_page_scraper.py`             | Halilit.com product scraping (skeleton + JIT)    |
| `guardrails.py`                       | Data quality guardrails                          |
| `ingestion_database.py`               | SQLite storage for product state                 |
| `relationship_discovery.py`          | Commercial (variants + accessories) + spectrum (alternatives) |
| `relationship_enrichment_official.py` | Official brand-page relationship extraction      |
| `relationship_enrichment_contextual.py`| Contextual (review) relationship extraction      |
| `relationship_merge.py`               | Merge official + contextual candidates into graph |

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
