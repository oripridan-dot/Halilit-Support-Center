# Ingestion Engine

This directory contains the tools for the "Ground Zero" ingestion phase of the Halilit Support Center.

## Components

- **`manifest.json`**: The central registry of all 82 tracked brands. Contains:
  - `commercial`: Link to Halilit brand page (Source of Truth for SKUs/Pricing).
  - `technical`: Link to Official manufacturer site (Source of Truth for Manuals/Firmware).
- **`raw_harvester.py`**: The "as-is" scraping engine.
  - Uses Playwright (Headless Chrome) to render JavaScript-heavy pages.
  - Saves full HTML and `meta.json` sidecars to `backend/data/raw/`.
  - Handles Halilit's S3 content injection automatically.

- **`update_manifest_urls.py`**: Utility to rescrape Halilit's "All Brands" page and update `manifest.json` URLs.

## Usage

### Prerequisites

Ensure Playwright dependencies are installed:

```bash
playwright install-deps
pip install -r backend/requirements.txt
```

### Running the Harvester

**Harvest a specific brand:**

```bash
PYTHONPATH=. python backend/ingestion/raw_harvester.py adam-audio
```

**Harvest ALL brands (Full Ingestion):**

```bash
PYTHONPATH=. python backend/ingestion/raw_harvester.py
```

_Note: This will take significant time as it iterates through 80+ brands and hundreds of products._

## specific Utilities

- `find_brand_url.py`: (Deprecated) Initial exploration script.
- `dump_home_links.py`: (Deprecated) Initial exploration script.
