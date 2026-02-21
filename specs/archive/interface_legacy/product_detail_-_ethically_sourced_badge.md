# Spec: Product Detail - Ethically Sourced Badge

**Version:** 1.1
**Component:** `frontend/src/components/ProductDetail/ProductDetailHeader.tsx`

## 1. Purpose

To display the ethical sourcing status of a product within the Product Detail header, enhancing transparency and empowering operators to make informed decisions. While a general `SourcingBadge` component exists, it does not specifically address the "Ethically Sourced" status. This spec aims to integrate an ethical sourcing badge into the `ProductDetailHeader` to ensure its visibility.

## 2. Requirements

1.  **Data Source:** Fetch ethical sourcing data from the `/api/products/{product_id}/sourcing` endpoint. The endpoint MUST return a JSON response containing the ethical sourcing status.
2.  **Badge Display:** The `ProductDetailHeader` component MUST display the `SourcingBadge` component.
3.  **SourcingBadge Component:** Reuse the existing `SourcingBadge.tsx` component to display ethical sourcing status based on `status` field received from the API (as described below).
4.  **Supported Statuses:** The `SourcingBadge` MUST support the following ethical sourcing statuses (already implemented in SourcingBadge.tsx):
    -   `"Ethically Sourced"`: Display a green badge with the text "Ethically Sourced".
    -   `"Partially Sourced"`: Display a yellow badge with the text "Partially Sourced".
    -   `"Unknown Sourcing"`: Display a red badge with the text "Sourcing Unknown".
5.  **Loading State:** While fetching data from the API (inside the `SourcingBadge` component), display a loading indicator.
6.  **Error Handling:** If the API request fails (inside the `SourcingBadge` component), display an error message.
7.  **Styling:** Use Tailwind CSS to style the badges consistently with the dark theme, ensuring proper color contrast for readability.
8.  **API Endpoint:** The `/api/products/{product_id}/sourcing` endpoint MUST return one of the values specified in Requirement 4 in `status` field.
9.  **Accessibility:** Ensure the badge is accessible to users with disabilities, providing appropriate ARIA attributes and sufficient color contrast.
10. **Integration Point:** Add the `SourcingBadge` within the `ProductDetailHeader.tsx`, placing it next to the product name or in a suitable location within the header. The component will receive the `productId` to fetch the sourcing information.

## 3. Data Contract

**API Endpoint:** `/api/products/{product_id}/sourcing` (GET)

**Request:**

-   `product_id` (path parameter): The ID of the product for which to retrieve ethical sourcing information.

**Response (Success - 200 OK):**

```json
{
  "status": "Ethically Sourced" | "Partially Sourced" | "Unknown Sourcing"
}
```

**Response (Error - 500 Internal Server Error):**

```json
{
  "detail": "string"
}
```

## Stitch UI Prompt
```text
// Target Component: ProductDetailHeader
// Description: This prompt is for integrating an Ethically Sourced badge into the ProductDetailHeader component.

// Layout: The ProductDetailHeader should use a Flexbox layout. The components will flow horizontally.

// Visual Style:
// - Use the dark mode theme.
// - Background: slate-900 (already applied to the header)
// - Text: Use appropriate text colors for readability against the dark background
// - Font: Use the default Halilit font.

// Component Hierarchy:
// 1. Back Button: A button to navigate back to the previous page.
// 2. Product Name: The name of the product.
// 3. Sourcing Badge: Integrate the SourcingBadge component here. The badge displays the ethical sourcing status of the product.
// 4. Other header elements (existing): Stock status, JIT status, SKU...
// 5. Halilit URL Button: Button linking to the official halilit website.

// Spacing:
// - Use Tailwind CSS margin and padding classes for spacing.
// - Ensure there's consistent spacing between the product name, sourcing badge, and other header elements.
// - Badge should be placed to the right of the Product Name with a small margin (e.g., `ml-2`).

// Data Slots:
// - Product Name: "[Product Name]"
// - Sourcing Status: This data is fetched and handled by the SourcingBadge.

// Stitch Prompt:
// Create a React component for ProductDetailHeader. Use Flexbox layout. Display a back button, then the product name "[Product Name]", followed by the SourcingBadge component, all horizontally aligned. Add other necessary elements to display the stock status, JIT status, and SKU, then the Halilit URL button. Use appropriate dark theme styles and spacing.

// Color tokens:
// - bg-slate-900
// - text-blue-500
// - text-white
// - Appropriate colors from SourcingBadge component

// Reference the Halilit Support Center's existing components and Tailwind CSS styles.
```

## Verification Commands
- `pnpm tsc --noEmit`
- `pnpm run lint`
