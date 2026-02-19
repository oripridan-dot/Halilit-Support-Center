# Spec: Product Detail - Accessory Recommendations

**Version:** 1.0
**Component:** `frontend/src/components/views/ProductDetailView.tsx`

## 1. Purpose

To display a list of recommended accessories on the Product Detail screen, satisfying the "Maximize Attachment Rate" business goal. This section MUST appear even if the backend graph is empty, showing a clear prompt to the operator.

## 2. Requirements

1.  **Accessory Section Display:** On the Product Detail View, a dedicated section labeled "Recommended Accessories" (or similar, e.g., "Pairs Well With") MUST be present, below the primary product details and above the specification table.
2.  **Accessory Loading State:** While accessory data is loading from `useProductRelationships`, a skeleton loading state MUST be displayed in the "Recommended Accessories" section. The skeleton should mimic the layout of the accessory list.
3.  **Accessory List Display:** When accessory data is loaded, the "Recommended Accessories" section MUST display a horizontal scrolling list of accessory product tiles.
    *   Each tile MUST show the accessory's `image_url`, `name`, and `price` (or "Call for Price" if `price` is null).
    *   Clicking an accessory tile MUST navigate the user to the Product Detail view for that accessory product, using `useNavigationStore().goToProduct(accessory.id)`.
4.  **No Accessories Message:** If the `useProductRelationships` hook returns an empty `accessories` array, the "Recommended Accessories" section MUST display a message: "No accessories found. Please check the product graph and add compatible accessories."
5.  **No Accessories Styling:** The "No accessories found" message MUST be styled distinctively to stand out to the operator (e.g., amber background, warning icon). It MUST NOT be styled as an error, since empty relationships are valid.
6.  **Image Fallback:** Each accessory tile MUST implement an image fallback using `/placeholder.png` if the accessory's `image_url` is missing or fails to load, satisfying the "Zero Broken Images" goal.
7. **"Call for Price" handling:** If the accessory product's `price` is `null`, display "Call for Price" instead of a numerical price.
8.  **Error Handling:** If the `useProductRelationships` hook returns an `error`, display an error message in the "Recommended Accessories" section: "Error loading accessories: [error message]". The error message must be styled to indicate an error state (e.g., red background). The error message MUST include a button to `refetch` the data from `useProductRelationships`.
9.  **Data Source:** The accessory data MUST be sourced from the `accessories` array returned by the `useProductRelationships` hook.
10. **Scroll Behavior:** The horizontal scrolling list of accessories must allow the user to scroll through the list using either a mousewheel or by dragging the list.
11. **Accessibility:** The accessory tiles must be keyboard navigable. Each tile MUST be focusable and selectable using the keyboard (Enter/Space).

## 3. Behavior Scenarios

1.  **Scenario:** Product A has 3 accessories defined in the product graph.
    *   **Outcome:** The "Recommended Accessories" section displays 3 accessory tiles, each showing the accessory's image, name, and price. Clicking a tile navigates to the corresponding accessory's Product Detail view.
2.  **Scenario:** Product B has no accessories defined in the product graph.
    *   **Outcome:** The "Recommended Accessories" section displays the message: "No accessories found. Please check the product graph and add compatible accessories." This message has an amber background and warning icon.
3.  **Scenario:** The `useProductRelationships` hook returns an error.
    *   **Outcome:** The "Recommended Accessories" section displays the message: "Error loading accessories: [error message]". This message has a red background. A button to `refetch` the data is displayed alongside the error message.
4.  **Scenario:** Accessory image fails to load.
    *   **Outcome:** The `/placeholder.png` image is displayed in place of the broken image.
5.  **Scenario:** An accessory product has a `price` of `null`.
    *   **Outcome:** The accessory tile displays "Call for Price" instead of a numerical price.
