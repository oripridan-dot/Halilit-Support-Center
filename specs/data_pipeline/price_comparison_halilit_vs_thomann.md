# Spec: Price Comparison — Halilit vs Thomann (RCF · Mackie · Allen & Heath)
**Version:** 1.0  
**Target Files:**
- `backend/scripts/price_comparison/halilit_thomann_scraper.py`
- `backend/scripts/price_comparison/thomann_scraper.py`
- `backend/scripts/price_comparison/price_comparison_engine.py`
- `backend/scripts/price_comparison/pdf_report_generator.py`
- `backend/scripts/price_comparison/run_comparison.py`

---

## Overview

A **real-data** price intelligence pipeline that:
1. Scrapes **Halilit.com** for all products from the brands **RCF**, **Mackie**, and **Allen & Heath**.
2. Searches **Thomann.de** for each matching product (by model name / SKU).
3. Calculates a **fair total landed cost** for Thomann: `EUR price × live ILS/EUR rate + estimated IL shipping`.
4. Produces a **beautifully designed PDF report** (HTML-rendered via WeasyPrint) comparing both channels side-by-side, including price delta, savings indicator, and brand summary statistics.

**Zero Tolerance Policy:** All prices MUST come from real HTTP requests. NO fallback mock data. If a product cannot be matched, mark it `UNMATCHED` and include it in an appendix.

---

## Brands in Scope

| Brand         | Halilit search slug | Thomann brand filter |
|---------------|---------------------|----------------------|
| RCF           | `rcf`               | `rcf`                |
| Mackie        | `mackie`            | `mackie`             |
| Allen & Heath | `allen-heath`       | `allen-heath`        |

---

## Module 1 — `thomann_scraper.py`

### Purpose
Fetch product listings and prices from **Thomann.de** for a given brand, then attempt to match individual products by name.

### Key Functions

```python
def search_brand_products(brand_slug: str, max_pages: int = 10) -> list[dict]:
    """
    Search Thomann for all products of a brand.
    URL pattern: https://www.thomann.de/gb/search_dir.html?sw={brand_slug}&oa=article_relevance
    Paginate using &pg=N (1-indexed).
    
    Returns list of:
    {
        "name": str,
        "thomann_url": str,
        "price_eur": float,       # price on Thomann in EUR (ex. German VAT — shown to non-EU)
        "currency": "EUR",
        "sku": str | None,
        "in_stock": bool,
        "brand": str,
        "category": str | None,
        "thomann_product_id": str | None
    }
    """

def get_product_price(product_url: str) -> float | None:
    """
    Fetch the exact EUR price from a Thomann product detail page.
    Parses the price from the JSON-LD `Product` schema or the `.price` span.
    Returns None if page is unavailable or out of stock.
    """

def match_product(halilit_name: str, thomann_catalog: list[dict]) -> dict | None:
    """
    Fuzzy-match a Halilit product name against the Thomann catalog.
    Use difflib.SequenceMatcher with ratio > 0.72 as the threshold.
    Prefer exact model-number matches over fuzzy title matches.
    Returns the best matching Thomann product dict, or None.
    """
```

### HTTP Configuration
```python
THOMANN_BASE   = "https://www.thomann.de"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
REQUEST_DELAY  = 1.2   # seconds between requests (polite crawling)
REQUEST_TIMEOUT = 20
```

---

## Module 2 — `price_comparison_engine.py`

### Purpose
Compute fair landed-cost comparisons between Halilit (ILS) and Thomann (EUR → ILS).

### Key Functions

```python
def get_live_eur_ils_rate() -> float:
    """
    Fetch the live EUR/ILS exchange rate from the Bank of Israel public API:
      https://edge.boi.gov.il/FusionEdge/sdmx/v2/data/dataflow/BOI.STATISTICS/EXR/1.0/RER_EUR_ILS?format=csv&startperiod=-1&endperiod=-1
    Parse the CSV response and return the latest rate.
    Fallback: if the API is unreachable, use 3.92 and log a warning.
    """

def estimate_thomann_shipping_to_israel(product_weight_kg: float | None) -> float:
    """
    Estimate Thomann shipping cost to Israel in EUR based on item weight.
    
    Thomann Israel Shipping Tiers (actual published rates as of 2025):
      - 0–1 kg    : €19.90
      - 1–5 kg    : €29.90
      - 5–15 kg   : €49.90
      - 15–30 kg  : €79.90
      - 30+ kg    : €109.90
    
    If weight is None, use €29.90 (average estimate).
    Returns shipping cost in EUR.
    """

def compute_thomann_landed_cost_ils(
    price_eur: float,
    shipping_eur: float,
    eur_ils_rate: float,
    apply_customs: bool = False,
) -> dict:
    """
    Compute the total ILS cost of buying from Thomann.
    
    Formula:
      total_eur    = price_eur + shipping_eur
      total_ils    = total_eur × eur_ils_rate
      customs_ils  = total_ils × 0.12 if apply_customs else 0  (12% import duty)
      landed_cost  = total_ils + customs_ils
    
    Israel customs threshold: purchases under $500 USD are typically NOT subject
    to import tax for personal use. Flag apply_customs=False by default.
    Items over $500 USD equivalent: flag with `customs_risk=True` in output.
    
    Returns:
    {
        "price_eur": float,
        "shipping_eur": float,
        "total_eur": float,
        "eur_ils_rate": float,
        "total_ils_before_customs": float,
        "customs_ils": float,
        "landed_cost_ils": float,
        "customs_risk": bool,     # True if item exceeds $500 USD threshold
        "note": str               # human readable note
    }
    """

def compare_prices(
    halilit_price_ils: float,
    thomann_landed_cost_ils: float,
) -> dict:
    """
    Compute the price delta and verdict.
    
    Returns:
    {
        "halilit_ils": float,
        "thomann_landed_ils": float,
        "delta_ils": float,          # halilit - thomann (positive = halilit is more expensive)
        "delta_pct": float,          # delta / thomann * 100
        "verdict": "HALILIT_CHEAPER" | "THOMANN_CHEAPER" | "SIMILAR",  # SIMILAR if |delta_pct| < 5%
        "savings_ils": float,        # absolute savings by choosing cheaper option
        "cheaper_source": "Halilit" | "Thomann"
    }
    """
```

---

## Module 3 — `halilit_thomann_scraper.py`

### Purpose
Orchestration layer. Pulls Halilit data using the existing `HalilitPageScraper` (`scrape_brand_full(brand=brand_slug)`), then matches each product against the Thomann catalog.

```python
# Import: from backend.ingestion.halilit_page_scraper import HalilitPageScraper
# Usage:  scraper = HalilitPageScraper()
#         products = scraper.scrape_brand_full(brand="rcf")  # returns list of dicts
#         Each product dict contains: name, price_il, price_eilat, url, sku, brand, images, etc.

def run_comparison_for_brand(brand_slug: str, brand_display_name: str) -> list[dict]:
    """
    Returns a list of ComparisonRow dicts:
    {
        "brand": str,
        "product_name": str,
        "halilit_url": str,
        "halilit_sku": str | None,
        "halilit_price_ils": float | None,
        "thomann_url": str | None,
        "thomann_price_eur": float | None,
        "thomann_shipping_eur": float,
        "thomann_landed_cost_ils": float | None,
        "eur_ils_rate": float,
        "delta_ils": float | None,
        "delta_pct": float | None,
        "verdict": str,             # "HALILIT_CHEAPER" | "THOMANN_CHEAPER" | "SIMILAR" | "UNMATCHED" | "NO_HALILIT_PRICE"
        "savings_ils": float | None,
        "cheaper_source": str | None,
        "customs_risk": bool,
        "matched": bool
    }
    """
```

---

## Module 4 — `pdf_report_generator.py`

### Purpose
Generate a **premium-quality PDF** from the comparison data using **WeasyPrint** (HTML+CSS → PDF).

### Design Requirements

#### Cover Page
- Dark background (`#0f172a`) with gradient overlay
- Halilit branding: "HALILIT PRICE INTELLIGENCE REPORT" in white header
- Subtitle: "Competitive Analysis: Halilit vs Thomann"
- Brands covered: RCF · Mackie · Allen & Heath
- Report date and EUR/ILS rate used
- Summary KPIs grid (4 stats):
  - Total products compared
  - Products where Halilit is cheaper
  - Products where Thomann is cheaper
  - Average price delta %

#### Executive Summary Section
Per brand, a **summary card** showing:
- Brand logo placeholder / name in styled typography
- Total products matched
- Min / Max / Average delta %
- Verdict distribution bar (Halilit cheaper vs Thomann cheaper vs Similar)

#### Main Comparison Table (per brand)

For each brand, render an HTML table with these columns:

| # | Product Name | Halilit Price (₪) | Thomann Base (€) | Shipping (€) | Total Thomann (€) | Total Thomann (₪) | Δ (₪) | Δ % | Verdict |
|---|---|---|---|---|---|---|---|---|---|

Table row styling:
- `verdict = HALILIT_CHEAPER` → green left border (`#22c55e`), light green row tint
- `verdict = THOMANN_CHEAPER` → orange left border (`#f97316`), light orange row tint
- `verdict = SIMILAR` → grey border, neutral row
- `verdict = UNMATCHED` → grey italic row, "No match found on Thomann" note

Verdict badge styling:
- HALILIT_CHEAPER → `🟢 Halilit Wins`
- THOMANN_CHEAPER → `🟠 Thomann Cheaper`
- SIMILAR → `⚪ Similar Price`
- UNMATCHED → `— No Match`

#### Footer Notes Section
- Exchange rate used and timestamp
- Thomann shipping tiers legend
- Customs risk disclaimer paragraph
- "All prices are real-time scraped as of [date]. No mock data used."

### CSS Design
```css
/* Premium dark palette */
--bg-dark: #0f172a;
--bg-card: #1e293b;
--accent-blue: #3b82f6;
--accent-green: #22c55e;
--accent-orange: #f97316;
--text-primary: #f1f5f9;
--text-secondary: #94a3b8;
--border: #334155;

/* Typography */
font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
```

### Output
Write PDF to: `reports/price_comparison_halilit_vs_thomann_{YYYY-MM-DD}.pdf`
Create `reports/` directory if it doesn't exist.

---

## Module 5 — `run_comparison.py` (Entry Point)

```python
"""
Entry point for the Halilit vs Thomann Price Comparison Pipeline.

Usage:
    python -m backend.scripts.price_comparison.run_comparison
    
    Optional flags:
    --brands rcf mackie allen-heath   (default: all three)
    --no-pdf                          (skip PDF, dump JSON to reports/)
    --output /path/to/reports/        (override output directory)
"""
```

### Execution Flow
1. Print banner: `"🔍 HALILIT PRICE INTELLIGENCE — Starting real data acquisition..."`
2. Fetch live EUR/ILS rate (log the rate)
3. For each brand in parallel (ThreadPoolExecutor, max_workers=3):
   a. Scrape Halilit products for brand
   b. Scrape Thomann catalog for brand
   c. Match and compute comparisons
4. Aggregate all rows
5. Save raw JSON to `reports/price_comparison_{date}.json`
6. Generate PDF report
7. Print final summary table to terminal
8. Print path to generated PDF

---

## Dependencies

**System packages (already pre-installed in this dev container — no action needed):**
- `libpango-1.0-0`, `libpangoft2-1.0-0`, `libpangocairo-1.0-0`
- `libcairo2`, `libgdk-pixbuf-2.0-0`

**Python packages — install before running:**
```bash
pip install weasyprint
```
Or via: `pip install -r backend/requirements.txt` once the entry below is added.

Add to `backend/requirements.txt` if not already present:
```
weasyprint>=60.0
```
(`difflib` is stdlib — no install required)

---

## Behavior Scenarios

### Scenario 1: Full Run — All Brands
- Command: `python -m backend.scripts.price_comparison.run_comparison`
- Outcome: Scrapes Halilit + Thomann for RCF, Mackie, Allen & Heath. Generates PDF in `reports/`. Terminal shows summary. All prices are real.

### Scenario 2: Thomann Match Failure
- A Halilit product has no match on Thomann (e.g. Halilit-exclusive SKU).
- Outcome: Row is marked UNMATCHED with `matched: false`. It appears in the PDF appendix, not the main table.

### Scenario 3: Halilit Product Has No Price  
- A Halilit product has `price_il: null` (call for price).
- Outcome: verdict = `NO_HALILIT_PRICE`. Row is shown in PDF with "Call for Price" in the Halilit column.

### Scenario 4: BOI API Unavailable
- The Bank of Israel API is unreachable.
- Outcome: Uses fallback rate `3.92` and logs `WARNING: Using fallback EUR/ILS rate 3.92`.

### Scenario 5: PDF Generation
- WeasyPrint renders the HTML cleanly.
- Outcome: PDF is readable, tables don't overflow, dark theme is preserved.

---

## Quality Standards
- `mypy`-clean (type annotations throughout)
- Requests: polite rate limiting (1.2s between Thomann requests)
- Error handling: per-product try/except — one failure must not abort the whole run
- Logging: `logging.getLogger("PriceComparison")` throughout
- No CLI dependencies beyond stdlib + requests + beautifulsoup4 + weasyprint
