"""
Ingestion Configuration
======================
Configurable settings for scraping and data ingestion.

Override via environment variables:
- INGESTION_RATE_LIMIT_DELAY: Delay between requests (default: 0.1s for fast scraping)
- INGESTION_MAX_WORKERS: Parallel workers for scraping (default: 20)
- INGESTION_SCRAPE_BATCH_SIZE: Products per batch (default: 100)
- INGESTION_BATCH_DELAY_SECONDS: Delay between batches (default: 0.1s)
- INGESTION_MAX_PRODUCTS_PER_BRAND: Limit products per brand (0 = unlimited)
- INGESTION_SKIP_VISUAL_VALIDATION: Skip image validation (1/true = skip, faster)
"""

import os

# Rate limiting: delay between individual requests (seconds)
# Lower = faster but more aggressive. 0.1s is safe for most sites.
RATE_LIMIT_DELAY = float(os.environ.get("INGESTION_RATE_LIMIT_DELAY", "0.1"))

# Parallelism: number of concurrent workers for scraping
# Higher = faster but more server load. 20 is a good balance.
MAX_WORKERS = int(os.environ.get("INGESTION_MAX_WORKERS", "20"))

# Batch size: how many products to scrape in parallel per batch
# Higher = faster but more memory. 100 works well.
SCRAPE_BATCH_SIZE = int(os.environ.get("INGESTION_SCRAPE_BATCH_SIZE", "100"))

# Batch delay: seconds to wait between batches (to avoid overwhelming server)
# Lower = faster. 0.1s is minimal but safe.
BATCH_DELAY_SECONDS = float(os.environ.get("INGESTION_BATCH_DELAY_SECONDS", "0.1"))

# Max products per brand: limit scraping (0 = unlimited)
MAX_PRODUCTS_PER_BRAND = int(os.environ.get("INGESTION_MAX_PRODUCTS_PER_BRAND", "0"))

# Skip visual validation: set to "1" or "true" to skip image quality checks (much faster)
SKIP_VISUAL_VALIDATION = os.environ.get("INGESTION_SKIP_VISUAL_VALIDATION", "").lower() in ("1", "true", "yes")

# Async concurrency: max concurrent async requests (for async scraper)
ASYNC_CONCURRENCY = int(os.environ.get("INGESTION_ASYNC_CONCURRENCY", "50"))

def get_progress_dir():
    """Get directory for progress tracking files."""
    from pathlib import Path
    return Path(__file__).parent.parent.parent / "backend" / "data" / "progress"
