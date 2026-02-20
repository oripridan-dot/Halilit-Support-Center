# Skill: Official Manufacturer Verification

**Trigger:** `verify_product_specs`  
**Compliance:** Use only for product specification lookup on official manufacturer sites. See COMPLIANCE.md. Do not access login, payment, or PII. Respect robots.txt and site ToS.

## Mission

1. Search Google for `site:{{brand_domain}} {{product_name}} specifications`.
2. Enter the first non-ad result.
3. **Visual Check:** Look for a "Specs" or "Specifications" tab/accordion and click it.
4. **Extraction:** Scrape the text of the specs table.
5. **Screenshot:** Take a screenshot of the "Back Panel" or "Connectivity" section if visible.
6. **Return:** JSON with `{ "specs_text": "...", "diagram_url": "..." }`.

## Parameters

- `brand_domain` — e.g. `roland.com`, `yamaha.com`
- `product_name` — e.g. `FP-30X`, `P-125`

## Constraints

- Reject pages that look like "Support" or "Downloads" (PDF lists).
- Prioritize pages with "Product" in the URL.
- Only navigate within the brand_domain provided by the system (no arbitrary URLs or external links).
- Do not submit forms, log in, or perform any account or payment actions.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- `pytest backend/tests/ -x -q`
