# Spec: Sort Search Results by Stock Status

**Version:** 1.0
**Component:** `frontend/src/components/views/InventoryView.tsx`

## 1. Purpose

To prioritize "In Stock" items in search results, improving operator efficiency and preventing accidental sales of out-of-stock items. This directly supports the "Aggressive Out-of-Stock Signaling" and "Speed of Service" business goals.

## 2. Requirements

1.  **Default Sort Order:** The Inventory grid MUST sort search results by stock status by default.
2.  **"In Stock" Priority:** Products with `stock` greater than 0 MUST appear at the top of the search results.
3.  **"Call for Price" Secondary Sort:** Within the "In Stock" items, products with a valid price (`price` greater than 0) MUST appear above "Call for Price" (`price` equal to null or 0).
4.  **"Call for Price" Stock Sort:** Products with "Call for Price" should be sorted with In Stock > Unconfirmed > Out of Stock
5.  **Unconfirmed Stock:** Products with `stock` equal to `null` MUST appear after "In Stock" items but before "Out of Stock" items.
6.  **"Out of Stock" Last:** Products with `stock` equal to 0 MUST appear at the bottom of the search results.
7.  **Stable Sort:** The relative order of products with the same stock status and price MUST be preserved (e.g., by using the product `id` as a tie-breaker).
8.  **No UI Change:** There is no need to add a new sort UI control. This stock-based sort is the default and implicit.

## 3. Behavior Scenarios

1.  **Scenario:** The Inventory grid loads with a pre-filled search query (e.g., "keyboard").
    *   **Outcome:** The search results are sorted as follows:
        *   Products with `stock > 0` appear first, sorted by price (non-CfP before CfP).
        *   Products with `stock === null` appear next, sorted by price (non-CfP before CfP).
        *   Products with `stock === 0` appear last.

2.  **Scenario:** The user types a search term into the search input.
    *   **Outcome:** The search results are updated and sorted according to the stock status and price rules.

3.  **Scenario:** A product is added to the catalog with `stock: 10`.
    *   **Outcome:** After the catalog refreshes, the product appears higher in the search results (if it matches the search query) than products with `stock: null` or `stock: 0`.

4.  **Scenario:** A product's `stock` is updated from `null` to `0`.
    *   **Outcome:** After the catalog refreshes, the product appears lower in the search results (if it matches the search query).

5. **Scenario:** Two Products both are "Call for Price," one is "In Stock" and one is "Out of Stock".
    *   **Outcome:** The "In Stock" product appears earlier in the search result than the "Out of Stock" product.
