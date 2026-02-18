# Inventory Grid Specification

## Goal
The Inventory Master view shows a filterable, sortable grid of products. Operator can find any product by SKU, brand, or name and open Product Detail.

## Data Requirements
- Source: Backend API (e.g. `/api/products` or catalog endpoint). No static `catalog.json` in frontend.
- Columns (minimal): SKU, Title, Brand, Category, IL Price, Eilat Price, Stock Status, Actions (e.g. Open).

## Layout
- **Toolbar:** Filters (brand, category, "Call for Price" toggle), sort dropdown (e.g. by name, price, SKU), search box.
- **Grid:** Table or card grid; responsive. Rows clickable → navigate to Product Detail (product id).
- **Performance:** Virtualization or pagination for large catalogs (e.g. 1000+ rows). No full load of 10k rows into DOM.

## Sorting & Filtering
- Sort: By name, SKU, price (asc/desc), brand. Missing price → bottom when sorting by price (per `pricing_logic.md`).
- Filter: By brand, category, stock status. URL or state can reflect filters for shareable links (optional).

## Behavior Scenarios
- **Scenario:** User selects "Call for Price" filter.
  - **Outcome:** Only products with no IL price (or flagged) are shown.
- **Scenario:** User clicks row.
  - **Outcome:** Navigate to Product Detail with that product's ID.
- **Scenario:** Grid has 0 results.
  - **Outcome:** Empty state: "No products match. Adjust filters or search."
- **Scenario:** Row has stock 0.
  - **Outcome:** Row may be styled (e.g. red tint or badge) per spec; see Product Intelligence or separate rule.

## Future (Spec Amendment)
- "Grid rows must turn red if stock is 0." → Add to this spec when approved; then implement.
