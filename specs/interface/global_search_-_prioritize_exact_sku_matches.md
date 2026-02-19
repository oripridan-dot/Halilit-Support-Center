# Spec: Global Search - Prioritize Exact SKU Matches

**Version:** 1.0
**Component:** `frontend/src/components/GlobalSearch.tsx`

## 1. Purpose

To prioritize exact SKU matches in the global search results, ensuring that operators can quickly find a specific product when searching by SKU. This directly supports the "Speed of Service" business goal. Currently global search might not return the exact SKU on top of the list.

## 2. Requirements

1. **Exact SKU Match Priority:** When the search query exactly matches a product's `id` (Halilit SKU), that product MUST be displayed as the first result in the global search dropdown list, regardless of other potential matches based on name or brand.
2. **Case-Insensitive Matching:** The SKU matching MUST be case-insensitive. Searching for "12345" should return the same result as searching for "12345" if a product with `id: "12345"` exists.
3. **Fallback to Existing Logic:** If there is no exact SKU match, the global search results MUST continue to be displayed according to the existing search logic (e.g., sorting by relevance of name and brand).
4. **Debouncing Integration:** This prioritization MUST work seamlessly with the existing search debouncing mechanism.
5. **Accessibility:** The prioritized SKU result MUST maintain accessibility standards, including keyboard navigation and screen reader compatibility.

## 3. Behavior Scenarios

1. **Scenario:** A product with `id: "HAL123"` exists in the catalog. The user types "HAL123" (or "hal123") into the global search input.
    * **Outcome:** The product with `id: "HAL123"` is displayed as the first result in the search dropdown.
2. **Scenario:** A product with `id: "HAL123"` exists. The user types "HAL" into the global search input.
    * **Outcome:** The search dropdown displays results matching "HAL" based on the existing logic (name, brand, etc.), with "HAL123" appearing based on that relevance.
3. **Scenario:** No product with an ID matching the search query exists.
    * **Outcome:** The search dropdown displays results based on the existing logic, as if no prioritization were implemented.
4. **Scenario:** Multiple products match the search term, and one is an exact SKU match.
    * **Outcome:** The exact SKU match appears first, followed by the other products sorted according to the original ranking logic.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
