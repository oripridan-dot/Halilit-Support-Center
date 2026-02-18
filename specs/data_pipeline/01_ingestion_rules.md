# Ingestion Rules Specification

## Goal
Define how product data is scraped, normalized, and stored. The Conductor reads this spec to generate or tune the ingestion pipeline.

## Sources
- Halilit website (primary).
- Any official brand/category pages as defined in catalog config.

## Rules

### Scraping
- Respect robots.txt and rate limits.
- Prefer structured data (JSON-LD, meta) over raw HTML when available.
- Store raw response for audit; normalized output for consumption.

### Normalization
- SKU: Trimmed, uppercase. Empty → flag for manual review.
- Brand: Mapped to canonical brand list. Unknown → "Other" or flag.
- Title: Max length as per UI spec; truncate with ellipsis.
- Prices: Per `specs/pricing_logic.md`.

### Output Artifacts
- `learned_taxonomy.json`: Canonical catalog used by Operator Console.
- Build fails if artifact is missing or schema-invalid.

## Scenarios
- **Scenario:** Source returns 404 for a product.
  - **Outcome:** Log; exclude from catalog; do not fail entire run.
- **Scenario:** Source returns malformed HTML.
  - **Outcome:** Log; skip item; increment error count. Build fails if error count exceeds threshold.
