# Spec: Integrate Ethically Sourcing Status into Product Detail View

**Version:** 1.2
**Component:** `frontend/src/components/views/ProductDetailView.tsx`

## 1. Purpose

To display ethically sourcing information on the product detail page, enhancing transparency and supporting informed decision-making by operators. While the `SourcingBadge` component exists, it's not integrated into the ProductDetailView. This spec focuses on integrating the `SourcingBadge` into the ProductDetailView, ensuring ethical sourcing information is prominently displayed. This integration aims to provide a comprehensive view of product sourcing, aligning with ethical considerations and empowering operators with relevant information.

## 2. Requirements

1.  **Data Source:** The `ProductDetailView` component MUST receive product data from `useConductorCatalog`, which includes the `id` used to call the `/api/products/{product_id}/sourcing` endpoint.

2.  **`SourcingBadge` Integration:** The `SourcingBadge` component MUST be integrated into the `ProductDetailView`, ideally near the product name, description, or other prominent product information. The `productId` must be passed as a prop to the `SourcingBadge` component.

3.  **API Endpoint:** Ensure that the `/api/products/{product_id}/sourcing` endpoint exists and returns the `status` field. The `status` field MUST return one of the values specified below.

4.  **Supported Statuses:** The `SourcingBadge` MUST support the following ethical sourcing statuses:
    -   `"Ethically Sourced"`: Display a green badge with the text "Ethically Sourced".
    -   `"Partially Sourced"`: Display a yellow badge with the text "Partially Sourced".
    -   `"Unknown Sourcing"`: Display a red badge with the text "Unknown Sourcing".

5.  **Loading State:** While fetching data from the API (inside the `SourcingBadge` component), display a loading indicator.

6.  **Error Handling:** If the API request fails (inside the `SourcingBadge` component), display an error message.

7.  **Styling:** Use Tailwind CSS to style the badges consistently with the dark theme, ensuring proper color contrast for readability.

8.  **Accessibility:** Ensure the badge has proper accessibility labels for screen readers and sufficient color contrast for readability.

## 3. Behavior Scenarios

1.  **Scenario:** Product A has `Ethically Sourced` status retrieved from the `/api/products/{product_id}/sourcing` endpoint.
    *   **Outcome:** The Product Detail View for Product A displays an "Ethically Sourced" badge with a green background and white text.

2.  **Scenario:** Product B has `Partially Sourced` status retrieved from the `/api/products/{product_id}/sourcing` endpoint.
    *   **Outcome:** The Product Detail View for Product B displays a "Partially Sourced" badge with a yellow background and dark text.

3.  **Scenario:** Product C has `Unknown Sourcing` status or the API returns an error.
    *   **Outcome:** The Product Detail View for Product C displays an "Unknown Sourcing" badge with a red background and white text.

4.  **Scenario:** The API is loading for a Product.
     *   **Outcome:** Loading indicator is shown.

## Stitch UI Prompt

```text
Design a React component for the ProductDetailView that integrates the SourcingBadge component.

The layout should be based on a dark mode aesthetic using Tailwind CSS:
- Background: slate-900
- Accents: blue-500 for interactive elements

The component structure:
1. A ProductDetailHeader component (existing)
2. Below the header, integrate a SourcingBadge, passing the productId. This should be placed near the header or description.
3. Below the header, show an ImageWithFallback, a JIT badge (if available), and product description.

Ensure proper spacing between elements for a clean, professional look.

Here's a breakdown of the desired elements:
- The component should fetch data from /api/products/{product_id}/sourcing and display a badge with the text: Ethically Sourced (green), Partially Sourced (yellow), or Unknown Sourcing (red).
- Show the loading state while the API is in flight.
- Show an error message if API has an error.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
- `pytest backend/tests/test_api.py -v` (if API endpoint needs testing)
