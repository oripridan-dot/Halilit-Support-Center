# Ingestion — JIT Architecture

Lightweight ingestion utilities retained from the original pipeline. The heavy 7-phase pipeline
has been replaced by **skeleton sync** (fast inventory) + **JIT Agent** (on-demand intelligence).

## Full Ingestion Pipeline

| Step | Source | Conductor | What |
|------|--------|-----------|------|
| **Commercial** | Halilit.com | `commercial-ingest` | Golden List, prices, SKUs, product list |
| **Enrich** | Halilit product pages | `enrich` | Description, images, features, media (+ **visual validation** of hero images) |
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
| `visual_validator.py`                 | Image quality checks + ingestion gate (reject placeholders/low-quality hero) |
| `guardrails.py`                       | Data quality guardrails                          |
| `ingestion_database.py`               | SQLite storage for product state                 |
| `relationship_discovery.py`          | Commercial (variants + accessories) + spectrum (alternatives) |
| `relationship_enrichment_official.py` | Official brand-page relationship extraction      |
| `relationship_enrichment_contextual.py`| Contextual (review) relationship extraction      |
| `relationship_merge.py`               | Merge official + contextual candidates into graph |

## Full Golden List

The **Golden List** is the full set of products we know about: it is the union of all brand JSON files in `frontend/public/data/*.json` (e.g. `bespeco.json`, `roland.json`). There is no single “golden_list.json” by default; the list is implied by those files. The index at `frontend/public/data/index.json` reports total product count and per-brand counts.

To run **visual validation across the entire Golden List** and persist coherency/confidence (e.g. `visual_match_status`, `visual_match_confidence`; mismatches clear official data), use:

```bash
PYTHONPATH=. python backend/scripts/visual_validation_golden_list.py
PYTHONPATH=. python backend/scripts/visual_validation_golden_list.py --brand bespeco --dry-run
PYTHONPATH=. python backend/scripts/visual_validation_golden_list.py --export backend/data/golden_list.json  # export single file
```

This improves data coherency and confidence without re-scraping Halilit.

## Visual validation (ingestion)

Hero images are **validated during ingestion** so bad images are rejected at the source:

- When scraping a product page, the first image (and optionally the next in the gallery) is checked for resolution, file size, and visual content (e.g. solid-color placeholders fail).
- If the hero fails, the next candidate in the gallery is tried; if none pass, `image_url` is left empty and gallery URLs are kept for later.
- Enrich summary reports **Hero image rejected (visual validation)** for products where no candidate passed.

To **disable** visual validation (faster runs, e.g. in dev): set `INGESTION_SKIP_VISUAL_VALIDATION=1` in the environment.

**Commercial vs official match:** When a product has both a commercial hero image (Halilit) and official images (brand site), the pipeline compares them. If they don’t match the same product (similarity below threshold), official data is **rejected**. This runs in the product normalizer (with in-product and in-memory cache so the same image pair is not re-fetched on every catalog build), in `cross_validate_product` (source rules), and in the JIT agent (no official URL/images cached on mismatch).

**Halilit discovery:** Brands page and sitemap use longer timeouts (set in `.env`: `HALILIT_DISCOVERY_CONNECT`, `HALILIT_DISCOVERY_READ`) and 3 retries with backoff. If you see "Failed to fetch brands page" or "Sitemap page N failed", increase `HALILIT_DISCOVERY_READ` in `.env`. If you get the anti-bot page (`page_no_referer`) instead of real content, Halilit may be restricting your IP or network; try from a different network or use existing brand JSONs and run only **enrich** → **sync** → **rebuild-catalog**.

## Usage (v9.5)

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
