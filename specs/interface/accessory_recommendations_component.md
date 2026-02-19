# Spec: Accessory Recommendations Component

**Target:** src/components/ProductDetail/AccessoryRecommendations.tsx

## Overview
This component displays a list of recommended accessories for a specific product. It fetches these recommendations from a backend API endpoint and renders them as a horizontal scrollable list. The component handles loading states and displays a message if no recommendations are available.

## Requirements
- The component must fetch accessory recommendations from the `GET /api/v1/products/{product_id}/accessories` endpoint.
- The component must display a loading indicator while fetching data.
- The component must display a message indicating that no recommendations are available if the API returns an empty list.
- Each accessory recommendation must display the accessory's name, image, and price.
- Clicking on an accessory should navigate the user to the accessory's product detail page (using the appropriate product ID).
- The component must be styled using Tailwind CSS with a dark theme (slate-900/blue-500 palette).
- The accessory list must be horizontally scrollable on smaller screens.
- The component should handle potential errors during API requests gracefully, displaying a generic error message to the user.
- The component must use `React.lazy` for image loading to improve performance.

## Data Contract

**API Endpoint:** `GET /api/v1/products/{product_id}/accessories`

**Request Parameters:**
- `product_id` (path parameter):  Integer. The ID of the product for which to retrieve accessory recommendations.

**Response (200 OK):**
```json
[
  {
    "id": 123,
    "name": "Protective Case",
    "imageUrl": "https://example.com/images/case.jpg",
    "price": 19.99
  },
  {
    "id": 456,
    "name": "Screen Protector",
    "imageUrl": "https://example.com/images/screen_protector.jpg",
    "price": 9.99
  }
]
```

**Response (204 No Content):**
Empty array `[]` indicates no recommendations are available.

**Response (500 Internal Server Error):**
```json
{
  "detail": "Internal Server Error"
}
```

**TypeScript Interface:**

```typescript
interface Accessory {
  id: number;
  name: string;
  imageUrl: string;
  price: number;
}
```

**Input Props:**

```typescript
interface AccessoryRecommendationsProps {
  productId: number;
}
```

## Behavior Scenarios

- **Scenario: Loading State**
  - Input: Component mounts with `productId = 123`. API request in progress.
  - Outcome: A loading indicator (e.g., spinner) is displayed.

- **Scenario: Recommendations Available**
  - Input: Component mounts with `productId = 123`. API returns a list of accessories as per the "Response (200 OK)" example above.
  - Outcome: The component renders a horizontally scrollable list of accessory cards, each displaying the accessory's name, image, and price.  Each card should be a link that navigates to the product detail page for the accessory (e.g., `/products/123` and `/products/456` in the example).

- **Scenario: No Recommendations Available**
  - Input: Component mounts with `productId = 123`. API returns an empty array `[]`.
  - Outcome: The component displays the message "No accessories recommended for this product."

- **Scenario: API Error**
  - Input: Component mounts with `productId = 123`. API returns a 500 Internal Server Error.
  - Outcome: The component displays the message "Failed to load accessory recommendations."

- **Scenario: Accessory Click**
  - Input: The user clicks on an accessory card (e.g., the "Protective Case" with `id = 123`).
  - Outcome: The user is navigated to the product detail page for the clicked accessory (e.g., `/products/123`).  Navigation should be handled using `next/link`.

## Out of Scope
- Implementation of the backend API endpoint.
- Detailed styling of the individual accessory cards beyond the specified Tailwind CSS palette.  Assume basic card styling (rounded corners, shadow).
- User authentication or authorization.
- Client-side caching of accessory recommendations.
