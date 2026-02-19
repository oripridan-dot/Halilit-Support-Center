# Spec: Product Detail - Dynamic JIT Badge Updates

**Version:** 1.0
**Component:** `frontend/src/components/views/ProductDetailView.tsx`

## 1. Purpose

To dynamically update the sourcing badges on the Product Detail screen when new data arrives from the JIT (Just-In-Time) intelligence stream. This ensures that the data source is always accurately reflected, supporting the "Data Integrity" technical standard and building operator trust. If JIT provides a higher-quality image, that image should be used with an "Inferred Scout" badge.

## 2. Requirements

1.  **JIT Data Override:** When the JIT stream (`useJITIntelligence`) provides new or updated values for `name`, `brand`, `price`, `price_eilat`, or `image_url`, these values MUST override the initially loaded values from the catalog.
2.  **Badge Update on Override:** When a JIT value overrides a catalog value, the corresponding sourcing badge MUST dynamically update to reflect the JIT stream as the data source.
3.  **JIT Source Mapping:**
    *   Name: "JIT Intelligence"
    *   Brand: "JIT Intelligence"
    *   Price (IL & Eilat): "JIT Intelligence"
	*	Image: "Inferred Scout"
4.  **Visual Transition:** The badge update MUST be visually smooth and non-disruptive to the user experience. Use a subtle animation (e.g., a fade-in effect) when the badge changes.
5.  **Fallback to Catalog:** If the JIT stream disconnects or encounters an error, the component MUST gracefully fallback to displaying the original catalog values with their corresponding "Official Scout" or "Commercial Scout" badges.
6. **Image Update Logic:** If `JITState.snap.thumbnail` is provided AND `JITState.status === "complete"`, then the product's image will use that thumbnail. Otherwise, use the existing image from `useConductorCatalog`. If a thumbnail is used, it will show an "Inferred Scout" badge.
7.  **No Badge for Unchanged Values:** If a value from the JIT stream is identical to the value from the catalog, the badge MUST NOT be unnecessarily updated.
8.  **Spec Table Update:** If the specs are sourced directly from JIT, those specs must also update dynamically and get a badge.

## 3. Behavior Scenarios

1.  **Scenario:** The Product Detail screen loads with data from the catalog. The JIT stream then starts streaming data, including a new `name` and `price`.
    *   **Outcome:** The displayed product name and price update to reflect the JIT values.
    *   **Outcome:** The sourcing badges next to the product name and price dynamically change to "JIT Intelligence".
2.  **Scenario:** The JIT stream disconnects after providing updated `name` and `price` values.
    *   **Outcome:** The displayed product name and price revert to the original catalog values.
    *   **Outcome:** The sourcing badges next to the product name and price revert to "Official Scout" and "Commercial Scout", respectively.
3.  **Scenario:** The JIT stream provides a value for `name` that is identical to the catalog value.
    *   **Outcome:** The displayed product name remains unchanged.
    *   **Outcome:** The sourcing badge next to the product name remains "Official Scout".
4. **Scenario:** The JIT State receives a valid `snap.thumbnail`.
	* **Outcome:** The product's image URL updates.
	* **Outcome:** The badge updates to "Inferred Scout".

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
