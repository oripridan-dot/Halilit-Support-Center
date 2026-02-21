# Spec: Inventory Search Stock + CfP Sorting

**Version:** 1.1
**Component:** `frontend/src/components/views/InventoryView.tsx`

## 1. Purpose

To refine the sorting logic in the Inventory grid search results. This will ensure "In Stock" items sort above "Call for Price", further enhancing the "Aggressive Out-of-Stock Signaling" and "Speed of Service" business goals. The previous version did not properly handle CfP items.

## 2. Requirements

1.  **Default Sort Order (Search Results):** The Inventory grid MUST sort search results by stock status and price by default. This is the *implicit* sort; there is no UI for changing the sort order.
2.  **"In Stock" Priority:** Products with `stock` greater than 0 MUST appear at the top of the search results.
3.  **"Non-CfP" > "Call for Price" Sorting:** Within the "In Stock" items, products with a valid price (`price` greater than 0) MUST appear above "Call for Price" (`price` equal to `null` or 0).
4.  **"Unconfirmed Stock" Placement:** Products with `stock` equal to `null` MUST appear after "In Stock" items but before "Out of Stock" items.
5.  **"Non-CfP" > "Call for Price" Sorting (Unconfirmed):** Within "Unconfirmed Stock" items, products with a valid price (`price` greater than 0) MUST appear above "Call for Price" (`price` equal to `null` or 0).
6.  **"Out of Stock" Last:** Products with `stock` equal to 0 MUST appear at the bottom of the search results.
7.  **"Non-CfP" > "Call for Price" Sorting (Out of Stock):** Within "Out of Stock" items, products with a valid price (`price` greater than 0) MUST appear above "Call for Price" (`price` equal to `null` or 0).
8.  **Stable Sort:** The relative order of products with the same stock status and price MUST be preserved (e.g., by using the product `id` as a tie-breaker).

## 3. Behavior Scenarios

1.  **Scenario:** The Inventory grid loads with a pre-filled search query (e.g., "keyboard").
    *   **Outcome:** The search results are sorted as follows:
        *   Products with `stock > 0` appear first, with non-CfP sorted above CfP.
        *   Products with `stock === null` appear next, with non-CfP sorted above CfP.
        *   Products with `stock === 0` appear last, with non-CfP sorted above CfP.

2.  **Scenario:** The user types a search term into the search input.
    *   **Outcome:** The search results are updated and sorted as described in Scenario 1.

3. **Scenario:** The user searches for "Roland". The catalog contains the following items:
    *   Roland Juno-DS61 (stock: 5, price: 799)
    *   Roland FP-30X (stock: 3, price: null)
    *   Roland XP-30 (stock: null, price: 1200)
    *   Roland AX-Edge (stock: null, price: null)
    *   Roland MC-101 (stock: 0, price: 299)
    *   Roland TB-303 (stock: 0, price: null)

    *   **Outcome:** The search results will be sorted as:
        1.  Roland Juno-DS61 (stock: 5, price: 799)
        2.  Roland FP-30X (stock: 3, price: null)
        3.  Roland XP-30 (stock: null, price: 1200)
        4.  Roland AX-Edge (stock: null, price: null)
        5.  Roland MC-101 (stock: 0, price: 299)
        6.  Roland TB-303 (stock: 0, price: null)

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
