# Skill: Catalog Organizer (Per-Brand Consolidation)

**Trigger:** `organize_brand_catalog`  
**Compliance:** Process only product data provided in the request. No web browsing. No PII. See COMPLIANCE.md.

## Purpose

Turn a raw list of products for one brand into a **unified, consolidated structure** so that:
- Every brand catalog has the same schema (easy to handle in code and UI).
- Categories are explicit (easy filter and browse).
- Search is trivial via a minimal `search_index`.

## Input (JSON)

```json
{
  "brand_slug": "roland",
  "brand_name": "Roland",
  "products": [
    { "halilit_id": "...", "product_name": "...", "taxonomy": { "canonical_category": "Keyboards & Synthesizers" }, ... }
  ]
}
```

## Output (JSON only — no browsing)

Return a single JSON object with this structure.

At minimum you MUST include `brand_identity`, `categories`, `products`, `search_index`, and `meta` as described below.

You SHOULD also include **optional** `families` and `relationships` sections so that the backend and UI can understand product lines, variants, and accessories without hard-coded Python heuristics.

```json
{
  "brand_identity": {
    "id": "roland",
    "name": "Roland",
    "slug": "roland",
    "logo_url": null,
    "website": null,
    "description": null
  },
  "families": [
    {
      "family_id": "fam_roland_td-27",
      "family_name": "TD-27 V-Drums",
      "series": "td",
      "brand": "Roland",
      "variant_ids": ["halilit-123", "halilit-456"],
      "is_accessory_family": false
    }
  ],
  "relationships": [
    {
      "source_id": "halilit-123",
      "target_id": "halilit-789",
      "relationship_type": "accessory_for"
    }
  ],
  "categories": [
    { "id": "keyboards-synthesizers", "label": "Keyboards & Synthesizers", "product_ids": ["halilit-123", "..."] }
  ],
  "products": [ ... same product objects as input, order preserved or by category ... ],
  "search_index": [
    { "id": "halilit_id", "t": "Product name", "s": "Category label", "b": "roland" }
  ],
  "meta": {
    "total_products": 42,
    "total_categories": 5,
    "organized_at": "2025-02-17T12:00:00Z"
  }
}
```

## Rules

1. **Do not browse the web.** Use only the `products` and brand fields from the input.
2. **Categories:** Derive from each product's `taxonomy.canonical_category`. Group product IDs by category. Use a slug for `id` (lowercase, hyphens). Use the human-readable category for `label`.
3. **search_index:** One entry per product: `id` = halilit_id, `t` = product name (short, for search), `s` = category label, `b` = brand_slug.
4. **products:** Return the same array (or reordered by category/name). Do not invent or remove fields.
5. **brand_identity:** Set from brand_slug and brand_name; leave logo_url, website, description null unless provided in input.
6. **families (recommended):** When possible, group products into logical product lines / families using only the input data:
   - Use shared model numbers, series names, or obvious naming patterns (e.g. “TD-27KV”, “TD-27K2”) to infer that products belong to the same family.
   - Each `family` MUST reference existing product IDs only (via `variant_ids`).
   - Mark `is_accessory_family: true` when all variants are clearly accessories (bags, cases, stands, pedals, covers, dust covers, flybars, etc.).
7. **relationships (recommended):** When possible, infer relationships between products using only fields from the input:
   - Supported `relationship_type` values: `"accessory_for"`, `"alternative_to"`, `"bundle_with"`, `"compatible_with"`, `"variant_of"`.
   - Only emit relationships when the intent is clear from names, SKUs, or taxonomy (e.g. a bag or case that clearly mentions a specific model).
   - `source_id` and `target_id` MUST both be valid product IDs from the input list.
   - Prefer simple, high-confidence relationships over speculative ones.

## Constraints

- Output must be valid JSON only. No markdown, no explanation outside the JSON.
- Do not add or infer data from external sources.
