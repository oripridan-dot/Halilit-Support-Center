# Gemini Codebase Review Bundle - v4.6 (DATA REFINERY & OPTIMIZATION)

**Date:** January 31, 2026
**Version:** 4.6.1
**Branch:** v4.6
**Status:** Production Ready - Full Data Sync & DB Optimization

## 1. Project Overview & Architecture

**Halilit Support Center** is a "Static First" web application with full database synchronization and optimization.

- **Goal:** Showcase musical instruments with high-fidelity visuals (2D) without a dynamic backend at runtime.
- **Architecture**: "Data Refinery with Full Sync".
  - **Ingestion**: Raw data is harvested via Playwright scripts (`backend/ingestion`).
  - **Refinement**: Raw JSONs are processed via `refine_brand.py`, injecting strict taxonomy and "Processed Badges".
  - **Validation**: Frontend strictly enforces data integrity. Only catalogs with the "Diamond" badge are loaded.
  - **Synchronization**: SQLite database (`ingestion_history.db`) tracks all ingestion runs and product snapshots, 100% synced with processed JSON cache.
  - **Optimization**: WAL mode enabled, indexes created on `product_snapshots`, DB vacuumed for peak performance.
- **Frontend**: React 18 + Vite + TypeScript. Consumes static JSONs with optimized caching.
- **Backend**: Python 3.x. Used for the ingestion, refinement pipeline, and monitoring (offline processing).

### Key Architectural Constraints

1.  **Strict Data Gating**: The frontend `catalogLoader` actively rejects any data that has not passed the full refinement pipeline.
2.  **Smart Taxonomy**: Products are mapped to a strict UI hierarchy via `taxonomy_matrix.py` rather than loose string matching.
3.  **Visual Integrity**: The UI (`CategorySlot`, `TierBar`) is context-aware, greying out empty slots and visually separating outliers.
4.  **Database Sync**: All ingestion runs are tracked in SQLite with full product snapshots, ensuring audit trail and change detection.
5.  **Optimization**: WAL mode + Indexes on `product_snapshots(product_id, run_id)` for high-concurrency read/write performance.

---

## 2. Directory Structure Snapshot

```
/workspaces/Halilit-Support-Center/
├── .version
├── README.md
├── backend/
│   ├── core/
│   │   ├── config.py       # Central Configuration
│   ├── ingestion/
│   │   ├── raw_harvester.py # Playwright Scraper
│   │   ├── brand_domains.py # Domain mappings
│   ├── models/
│   │   ├── core.py         # Pydantic Schemas
│   ├── monitoring/
│   │   ├── tracker.py      # SQLite Audit Logic
│   ├── processing/
│   │   ├── processor.py    # Formatting & Merging Logic
│   │   ├── media_optimizer.py # Image Conversion (WebP)
│   │   ├── taxonomy_matrix.py # UI Context Mapping Logic
│   ├── scripts/
│   │   ├── ingest_brand.py # Main Ingestion Script
│   │   ├── refine_brand.py # DATA REFINERY ORCHESTRATOR
├── frontend/
│   ├── public/
│   │   ├── data/           # Generated Catalog JSONs go here
│   │   ├── assets/         # Downloaded Images/Manuals go here
│   ├── src/
│   │   ├── types/
│   │   │   ├── index.ts    # Frontend Type Definitions
│   │   ├── lib/
│   │   │   ├── catalogLoader.ts # Strict Data Gatekeeper
│   │   ├── components/
│   │   │   ├── smart-views/
│   │   │   │   ├── TierBar.tsx # Physics-based Visualizer
```

---

## 3. Configuration & Versioning

### `.version`

```ini
VERSION=4.6.0
RELEASE_TAG=v4.6
BUILD_DATE=2026-01-30
BRANCH=v4.6
STATUS=data-refinement
```

### `backend/core/config.py`

```python
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    BACKEND_DIR: Path = BASE_DIR / "backend"
    FRONTEND_DIR: Path = BASE_DIR / "frontend"

    # Data Paths
    DATA_DIR: Path = BACKEND_DIR / "data"
    FRONTEND_PUBLIC_DIR: Path = FRONTEND_DIR / "public"
    FRONTEND_DATA_DIR: Path = FRONTEND_PUBLIC_DIR / "data"
    # Catalogs are stored directly in the data directory in the new workflow
    CATALOGS_DIR: Path = FRONTEND_DATA_DIR
    FRONTEND_CATALOGS_DIR: Path = FRONTEND_DATA_DIR
    FRONTEND_LOGOS_DIR: Path = FRONTEND_PUBLIC_DIR / "assets" / "logos"

    # Scraper Settings
    SCRAPER_HEADLESS: bool = True
    SCRAPER_TIMEOUT: int = 15000  # 15 seconds (reduced from 30s)
    SCRAPER_RETRIES: int = 2  # Reduced retries for faster failure
    SCRAPER_RETRY_DELAY: int = 1  # Reduced delay
    HALILIT_BASE_URL: str = "https://www.halilit.com"

    # Environment
    ENV: str = "development"

    class Config:
        case_sensitive = True


settings = Settings()

# Ensure critical directories exist


def ensure_dirs():
    dirs = [
        settings.DATA_DIR,
        settings.CATALOGS_DIR,
        settings.FRONTEND_DATA_DIR,
        settings.FRONTEND_CATALOGS_DIR,
        settings.FRONTEND_LOGOS_DIR
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    ensure_dirs()
    print(f"Configuration loaded. Base dir: {settings.BASE_DIR}")
```

---

## 4. Feature Implementation: Data Refinery Pipeline

### `backend/scripts/refine_brand.py` (New Orchestrator)

**Role:** Master script for the new "Refinery" workflow. It implements a **Quality Gate** that rejects "mixed salad" data.

```python
def calculate_quality_tier(product, taxonomy_context):
    """
    Determines the quality tier of a product.

    SILVER:  Has Name, Brand, Price, and Image.
    GOLD:    Silver + Description + Non-Trivial Taxonomy (Not Uncategorized).
    DIAMOND: Gold + Specs + Verified Context.
    """
    # ... logic ...
```

**Key Logic:**

- **Filters Garbage:** Removes items with no price/name.
- **Enforces Taxonomy:** Uses `taxonomy_matrix.py` to map raw categories to strict UI slots.
- **Stamps Badge:** Adds `processed_badge: { level: "DIAMOND", ... }` to the JSON root.

### `backend/ingestion/raw_harvester.py` (Commercial Data)

**Role:** Scrapes Halilit.com for pricing and availability.

```python
# Uses Playwright in headless mode
# Extracts:
# - Title
# - Price (Regular vs Member)
# - SKU
# - Status (In Stock / Out of Stock)
# - Product Page URL
```

### `frontend/src/lib/catalogLoader.ts` (Data Gate)

**Role:** Ensures only refined data enters the application.

```typescript
// ... imports

export const loadCatalog = async (brandId: string): Promise<BrandCatalog> => {
  // 1. Fetch JSON
  const response = await fetch(`/data/${brandId}.json`);
  const rawData = await response.json();

  // 2. Strict Refinery Check (Diamond Gate)
  const badge = rawData.processed_badge;

  if (!badge || badge.level !== "DIAMOND") {
    console.warn(
      `[CatalogLoader] ⛔ BLOCKED: ${brandId} has no Valid Processed Badge.`,
    );
    // Return empty catalog -> Prevents "Mixed Salad" display
    return {
      brand_id: brandId,
      brand_name: "Blocked",
      products: [],
    };
  }

  return rawData;
};
```

        # Check Rich Media (Images, Video, 3D)
        imgs = p.get("images", {}).get("gallery", [])
        media = p.get("media_files", [])
        if len(imgs) > 0 or len(media) > 0:
            with_media_count += 1

        # Check Categorization
        if p.get("category") and p.get("category") != "uncategorized":
            valid_categories += 1

    # Heuristic scoring
    score = {
        "total_products": total_products,
        "commercial_coverage": "100%",  # By definition if in processed list
        "technical_enrichment_rate": f"{round(enriched_count/total_products*100)}%",
        "specification_rate": f"{round(with_specs_count/total_products*100)}%",
        "manual_availability": f"{round(with_manuals_count/total_products*100)}%",
        "media_coverage": f"{round(with_media_count/total_products*100)}%",
        "categorization_health": f"{round(valid_categories/total_products*100)}%"
    }

    logger.info(f"📊 Ingestion Report for {brand_id}:")
    logger.info(json.dumps(score, indent=2))

    return score

def issue_badge(brand_id: str, score: dict):
"""
Issues a 'Raw Ingestion Badge' if the process completed successfully
and data structure is intact.
"""
BADGE_DIR.mkdir(parents=True, exist_ok=True)

    badge = {
        "brand_id": brand_id,
        "badge_type": "RAW_PASS",  # Certified Exhaustive Capture
        "issued_at": datetime.now().isoformat(),
        "status": "READY_FOR_VECTORIZATION",
        "digest": score,
        "pipeline_version": "v1.1"
    }

    badge_path = BADGE_DIR / f"{brand_id}_badge.json"
    with open(badge_path, "w") as f:
        json.dump(badge, f, indent=2)

    logger.info(f"🏅 BADGE ISSUED: {badge_path}")
    logger.info(
        "The brand is now certified as Raw Ingested and ready for next steps.")

def main():
parser = argparse.ArgumentParser(
description="Run the Full Ingestion Pipeline")
parser.add_argument(
"brand_id", help="The slug of the brand to ingest (e.g. adam-audio)")
args = parser.parse_args()

    brand = args.brand_id

    # Initialize Tracker
    tracker = IngestionTracker(brand)
    tracker.start_run()

    print("\n" + "="*60)
    print(f"   🌀 INGESTION PIPELINE STARTED: {brand.upper()}")
    print("="*60 + "\n")

    try:
        # Step 0: Brand Metadata Ingestion (Logos, Socials, Context)
        if not run_step("Brand Metadata Harvester", ["python3", "backend/scripts/ingest_brand_meta.py", brand]):
            logger.warning(
                "Brand Metadata ingestion failed or skipped (non-critical). Continuing...")

        # Step 1: Harvest Commercial (Halilit)
        if not run_step("Harvester: Commercial", ["python3", "backend/ingestion/raw_harvester.py", brand, "--step", "commercial"]):
            raise Exception("Commercial Harvest Failed")

        # Step 2: Processor Phase 1 (Generate Product List)
        if not run_step("Processor: Phase 1", ["python3", "backend/processing/processor.py", brand]):
            raise Exception("Processor Phase 1 Failed")

        # Step 3: Harvest Technical (Official - Depends on Phase 1)
        # We use "continueOnError" logic implicitly - checking output isn't easy here, but raw_harvester prints warnings if it skips
        run_step("Harvester: Technical", [
            "python3", "backend/ingestion/raw_harvester.py", brand, "--step", "technical"])

        # Step 4: Processor Phase 2 (Enrichment)
        if not run_step("Processor: Phase 2", ["python3", "backend/processing/processor.py", brand]):
            raise Exception("Processor Phase 2 Failed")

        # Step 5: Analysis & Badging
        score = validate_standards(brand)

        # Step 6: Historic Tracking Record
        processed_file = ROOT_DIR / "backend" / \
            "data" / "processed" / f"{brand}.json"
        if processed_file.exists():
            logger.info("📊 Recording historic snapshots...")
            with open(processed_file, "r") as f:
                data = json.load(f)
                for prod in data.get("products", []):
                    tracker.track_product(prod)

        if score:
            issue_badge(brand, score)
            tracker.finish_run("SUCCESS", score)
        else:
            logger.error("Analysis failed. No badge issued.")
            tracker.finish_run("FAILED", {"error": "Validation failed"})
            sys.exit(1)

    except Exception as e:
        logger.error(f"Pipeline Failed: {e}")
        tracker.finish_run("FAILED", {"error": str(e)})
        sys.exit(1)
    finally:
        tracker.close()

if **name** == "**main**":
main()

````

### `backend/ingestion/raw_harvester.py` (Scraper)

**Role:** Handles all network searching, downloading, and HTML parsing.
**Key Change v4.5**: Removed 3D model extensions (`.glb`, `.gltf`) from allowed downloads.

```python
# ... imports ...
class RawHarvester:
    # ... setup ...

    async def _download_asset(self, session, url: str, directory: Path):
            # ... checks ...
            # Include more valid extensions - 3D REMOVED
            valid_exts = [".pdf", ".jpg", ".jpeg", ".png", ".webp", ".mp4",
                          ".mov", ".webm", ".zip"]
            if not any(filename.lower().endswith(ext) for ext in valid_exts):
                return
            # ... download logic ...

    async def _process_single_product_deep(self, context: BrowserContext, product: dict, brand_name: str, base_url: str, official_dir: Path, sem: asyncio.Semaphore):
        # ... search logic ...

        # ... hunting for assets ...

                    # C. Videos (3D REMOVED)
                    media_links = await page.eval_on_selector_all("a", """
                        elements => elements.map(e => e.href)
                    """)

                    media_exts = [".mp4", ".mov", ".webm", ".zip"]
                    for link in media_links:
                        # ... download ...
````

### `backend/processing/processor.py` (Logic)

**Role:** Transforms raw JSONs into the frontend-ready catalog format.
**Key Change v4.5**: Logic for `official_images` vs `media_files`.

```python
# ... imports ...

def process_brand(brand_id: str):
    # ...
    # 2. Enrich with Technical Data (Official)
    official_dir = RAW_DATA_DIR / "official" / brand_id

    if official_dir.exists():
        for hid, product in catalog.items():
            # ... find specific product folder ...
            if product_dir.exists():
                # Process Assets
                for asset_file in product_dir.glob("*"):
                     ext = asset_file.suffix.lower()

                     if ext in [".jpg", ".jpeg", ".png", ".webp"]:
                        # Optimize and Add to Gallery
                        # ...

                     elif ext == ".pdf":
                        # Add to Manuals
                        # ...

                     # Handle Media (MP4, ZIP) - 3D REMOVED
                     elif ext in [".mp4", ".mov", ".webm", ".zip"]:
                        # Copy raw
                        # ...
```

## 5. Feature Implementation: Smart Visualization

To handle "display complexity" and visual noise, the frontend uses a **Relevance Engine**.

### `frontend/src/components/views/SpectrumModule.tsx`

**Role:** The main catalog view. It doesn't just list products; it scores them.

```typescript
// --- RELEVANCE ENGINE ---
// Calculates a 0-100 score for Y-Axis positioning
const calculateRelevance = (p: Product): number => {
  let score = 50;

  // 1. Data Quality Bonuses
  if (p.image || p.image_url) score += 20;
  if (p.verified) score += 15;
  if (p.pricing) score += 10;

  // 3. Penalty for "Ghost" items
  if (!p.image && !p.image_url) score -= 30;

  return Math.min(100, Math.max(0, score));
};
```

**Display Logic:**

- **X-Axis:** Price.
- **Y-Axis:** Relevance Score (calculated above).
- **Filtering:** Users can filter by "Tribe" (Category), but the core visibility is determined by the "Diamond" quality of the data.

---

## 6. Schema Definitions

### `backend/models/core.py` (Internal Data Model)

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class VendorData(BaseModel):
    """Path 2: Commercial Data (Source: Halilit)"""
    sku: str
    price: float
    stock_status: str
    purchase_url: str
    # ...

class TechnicalData(BaseModel):
    """Path 1: Technical & Media (Source: Brand/Manufacturer)"""
    specifications: Dict[str, str] = Field(default_factory=dict)
    assets: List[MediaAsset] = Field(default_factory=list)
    # ...

class Product(BaseModel):
    """Merged Product Entity"""
    id: str
    brand: str
    name: str
    commercial: VendorData
    technical: TechnicalData
    # ...
```

### `frontend/src/types/index.ts` (Public API / Frontend Model)

```typescript
export interface Product {
  // Core identification (required)
  id: string;
  name: string;
  brand: string;
  category: string;

  // Classification
  product_class?: "MI" | "PA" | "ACCESSORIES" | "CASES" | "CABLES";

  // Content
  description?: string;

  // Media
  image_url?: string;
  images?: ProductImagesType; // { main: string, gallery: string[] }
  manuals?: ProductManual[];

  // Technical
  specs?: Specification[];

  // Commerce
  pricing?: ProductPricing | number;
  availability?: "in-stock" | "pre-order" | "discontinued" | "unknown";

  // Knowledge base
  official_manuals?: OfficialMedia[];
}
```
