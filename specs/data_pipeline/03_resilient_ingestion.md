# Spec: Resilient Ingestion Engine (Semantic Extraction)
**Version:** 1.0
**Domain:** `backend/ingestion/`

## The Problem
The current scraping modules (`halilit_page_scraper.py`, `official_scraper.py`) are brittle. They rely on hardcoded HTML/CSS selectors that fail against DOM changes, Cloudflare protection, or JavaScript-heavy rendering.

## The Objective
Refactor the ingestion pipeline to abandon "Mechanical Extraction" (BeautifulSoup/CSS selectors) in favor of "Semantic Extraction" (LLM parsing) and API-sniffing.

## Architecture & Implementation Rules

### 1. The API-First Approach (Halilit)
Before attempting to scrape HTML from Halilit, the engine must attempt to query Halilit's underlying JSON endpoints (if they exist). 
- **Action for Builder:** Audit `halilit_page_scraper_async.py`. Modify it to test for standard e-commerce API endpoints (e.g., Shopify/Magento/WooCommerce standard routes) or extract the embedded `__NEXT_DATA__` or JSON payloads often hidden in the page source.

### 2. Semantic Extraction (LLM Fallback)
When HTML must be processed (especially for official brand sites like Roland or Allen & Heath):
- Do not use `soup.find()`.
- Use the existing Playwright infrastructure (or the `browser_agent` MCP) to fully load the page and render the JavaScript.
- Extract the `innerText` or convert the rendered DOM to Markdown.
- **The Core Upgrade:** Pass this Markdown to the Gemini LLM using `google.generativeai` with a strict `response_schema` (Structured Outputs). Ask Gemini to extract the `price`, `stock_status`, `sku`, and `specs`. 
- Gemini will understand the data structurally, making it immune to cosmetic website updates.

### 3. Graceful Degradation
If a page fails to load or blocks the bot, the system must NOT crash the pipeline. It should log an "Extraction Failure" to a dead-letter queue, retain the last known cached good data for that SKU, and move to the next item.

## Verification Commands
- `pytest backend/tests/test_ingestion.py -v` (Verify the fallback mechanisms work)
- `python backend/conductor_main.py --dry-run --target halilit` (Test the new semantic extraction without writing to the DB)
