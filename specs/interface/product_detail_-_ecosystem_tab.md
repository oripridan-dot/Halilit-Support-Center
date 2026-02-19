# Spec: Product Detail - Ecosystem Tab

**Version:** 1.0
**Component:** `frontend/src/components/views/ProductDetailView.tsx`

## 1. Purpose

To display product relationships (accessories, compatibles, bundles, alternatives) in a dedicated "Ecosystem" tab on the Product Detail screen. This consolidates the accessory recommendations from the "Maximize Attachment Rate" goal with other relationship types, providing a comprehensive view of the product's connections. The Ecosystem tab MUST gracefully handle empty relationships and clearly indicate data sources.

## 2. Requirements

1.  **Ecosystem Tab:** The Product Detail View MUST include a new tab labeled "Ecosystem" or similar (e.g., "Related Products", "Connections").
2.  **Tab Placement:** The "Ecosystem" tab MUST be placed after the main product details and specifications tabs.
3.  **Relationship Categories:** The "Ecosystem" tab MUST display distinct sections for each relationship type:
    *   Accessories
    *   Compatibles
    *   Bundles
    *   Alternatives
4.  **Relationship Data Source:** Each relationship listed MUST display a clear "Source" badge or indicator:
    *   "Verified" - For relationships validated by official brand data or golden scenarios (as defined in `specs/data_pipeline/02_relationship_logic.md`).
    *   "Inferred" - For relationships suggested by AI or rules (Alternatives, or unverified Compatible).
5.  **Empty State Handling:** If any relationship category has no associated products, the corresponding section MUST display a clear message indicating that no relationships of that type were found. Example: "No accessories found for this product."
6.  **"No Accessories" Message Styling:** The "No accessories found" message MUST be styled distinctively, for example, with an amber background and a warning icon, to stand out to the operator but not indicate a system error.
7.  **Product Tiles:** Each related product MUST be displayed using a Product Tile component.
8.  **Product Tile Navigation:** Clicking on a related product tile MUST navigate the user to the Product Detail view for that product, using `useNavigationStore().goToProduct(relatedProductId)`.
9. **Loading State:** While relationship data is loading, a skeleton loading state MUST be displayed in each relationship section.
10. **Error Handling:** Display an error message if the `useProductRelationships` hook returns an error.
11. **Horizontal Scrolling:** Each relationship category's list of tiles should be displayed in a horizontally scrolling layout.
12. **Component Integration:** The "Ecosystem" tab MUST seamlessly integrate with the existing `ProductDetailView` component and data sources (catalog, JIT, relationships).

## 3. Behavior Scenarios

1.  **Scenario:** Product A has verified accessories, compatible products, and inferred alternatives.
    *   **Outcome:** The "Ecosystem" tab displays distinct sections for each category, with the appropriate "Source" badges.
2.  **Scenario:** Product B has no accessories.
    *   **Outcome:** The "Accessories" section displays a "No accessories found" message.
3.  **Scenario:** Product C has no relationships of any kind.
    *   **Outcome:** Each section (Accessories, Compatibles, Bundles, Alternatives) displays a "No [relationship type] found" message.
4.  **Scenario:** The `useProductRelationships` hook returns an error.
    *   **Outcome:** An error message is displayed in the "Ecosystem" tab.
5.  **Scenario:** The `useProductRelationships` hook is in a loading state.
    *   **Outcome:** Skeleton loading states are shown in each of the relationship sections.

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
