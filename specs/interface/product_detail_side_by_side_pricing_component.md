# Spec: Product Detail - Side-by-Side Pricing Component
**Target:** src/components/ProductDetail/SideBySidePricing.tsx

## Overview
This component displays a side-by-side comparison of pricing information from different vendors for a specific product. It allows users to quickly compare prices and other relevant details to make an informed purchasing decision.

## Requirements
- [x] The component must fetch pricing data from a dedicated API endpoint.
- [x] The component must handle loading states gracefully, displaying a loading indicator while data is being fetched.
- [x] The component must display an error message if the API request fails.
- [x] The component should present the pricing information in a visually clear and easily comparable format, using a two-column layout.
- [x] Each pricing column should display the vendor name, price, shipping cost (if applicable), estimated delivery time (if available), and a link to the vendor's product page.
- [x] The vendor name should be prominently displayed and styled differently for each vendor (e.g., using distinct background colors derived from the slate-900/blue-500 palette).
- [x] The component should be responsive and adapt to different screen sizes.
- [x] Price should be displayed with currency symbol.

## Data Contract

**API Endpoint:** `/api/products/{product_id}/pricing` (Backend Service definition provided separately)

**Response (JSON):**

```json
[
  {
    "vendor_id": "vendor-a",
    "vendor_name": "Vendor A",
    "price": 24.99,
    "currency": "USD",
    "shipping_cost": 5.00,
    "estimated_delivery": "3-5 business days",
    "product_url": "https://vendor-a.com/product/123"
  },
  {
    "vendor_id": "vendor-b",
    "vendor_name": "Vendor B",
    "price": 22.50,
    "currency": "USD",
    "shipping_cost": 7.50,
    "estimated_delivery": "2-4 business days",
    "product_url": "https://vendor-b.com/product/456"
  }
]
```

**TypeScript Interface:**

```typescript
interface PricingData {
  vendor_id: string;
  vendor_name: string;
  price: number;
  currency: string;
  shipping_cost?: number; // Optional, can be null
  estimated_delivery?: string; // Optional, can be null
  product_url: string;
}

interface SideBySidePricingProps {
  productId: string;
}
```

## Behavior Scenarios

- **Scenario:** Initial Load
  - Input: Component mounts with `productId = "some-product-id"`.
  - Outcome: A loading indicator (e.g., a spinner) is displayed.

- **Scenario:** Successful Data Fetch
  - Input: API returns the pricing data for the specified product (see Data Contract).
  - Outcome: The component renders a two-column layout, displaying the vendor information, price, shipping cost (if applicable), estimated delivery time (if available), and a link to the vendor's product page for each vendor. Each column should have a visually distinct background color.

- **Scenario:** Failed Data Fetch
  - Input: API returns an error (e.g., 500 Internal Server Error).
  - Outcome: An error message is displayed (e.g., "Failed to load pricing data. Please try again later.").

- **Scenario:** No Pricing Data Available
  - Input: API returns an empty array.
  - Outcome: A message is displayed indicating that no pricing data is available (e.g., "No pricing information available for this product.").

- **Scenario:** Shipping Cost is Null
  - Input: API returns data with `shipping_cost: null`.
  - Outcome: The component should display "Free Shipping" instead of a price.

- **Scenario:** Estimated Delivery is Null
  - Input: API returns data with `estimated_delivery: null`.
  - Outcome: The component should display "Not available" for the delivery estimate.

## Out of Scope
- [Authentication/Authorization for the API endpoint]
- [Detailed error handling beyond displaying a generic error message]
- [Specific design of the loading indicator or error message.]
- [Backend API implementation — defined in a separate spec.]
- [Currency conversion.]
