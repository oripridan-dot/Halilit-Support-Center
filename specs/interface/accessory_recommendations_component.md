# Spec: Accessory Recommendations Component
**Target:** src/components/ProductDetail/AccessoryRecommendations.tsx

## Overview
This component displays a carousel of accessory product recommendations on a product detail page. Recommendations are fetched from a backend API endpoint and displayed as interactive cards.

## Requirements
- The component must fetch accessory recommendations from the `/api/products/{product_id}/accessories` endpoint.
- The component must handle loading states, displaying a loading indicator while data is being fetched.
- The component must handle error states, displaying an error message if the API call fails.
- The component must display the recommendations in a horizontal carousel, allowing users to scroll through them.
- Each recommendation card must display the product's name, a thumbnail image, and the product's price.
- Each recommendation card must be clickable, navigating the user to the product detail page for that accessory.
- The component must be responsive and adapt to different screen sizes.
- The component must use Tailwind CSS for styling, adhering to the dark theme (slate-900/blue-500 palette).
- The component must be implemented in React 18 with TypeScript.

## Data Contract

**API Endpoint:** `/api/products/{product_id}/accessories` (GET)

**Request:**

*   `product_id` (path parameter): Integer representing the ID of the main product.

**Response (JSON):**

```typescript
interface AccessoryProduct {
  id: number;
  name: string;
  imageUrl: string;
  price: number;
  url: string; // URL to the product detail page
}

interface AccessoryRecommendationsResponse {
  accessories: AccessoryProduct[];
}
```

**Error Response (JSON):**

```typescript
interface ErrorResponse {
  detail: string;
}
```

## Behavior Scenarios

- **Scenario:** Initial Load - No Recommendations
  - Input:  Component mounts, API returns an empty `accessories` array.
  - Outcome: Displays a message "No accessories available for this product."

- **Scenario:** Initial Load - Recommendations Available
  - Input: Component mounts, API returns a list of accessories.
  - Outcome: Displays a horizontal carousel of accessory product cards.  Each card displays the image, name, and price of the product.

- **Scenario:** Loading State
  - Input: Component mounts, API call is in progress.
  - Outcome: Displays a loading indicator (e.g., a spinner).

- **Scenario:** Error State
  - Input: Component mounts, API call returns an error (e.g., 500 status code).
  - Outcome: Displays an error message "Failed to load accessory recommendations."

- **Scenario:** Click Accessory Card
  - Input: User clicks on an accessory product card.
  - Outcome: The user is navigated to the accessory product's detail page using the `url` property from the API response.

## Out of Scope
- Implementing the backend API endpoint.
- User authentication or authorization.
- Detailed styling beyond basic layout and dark theme application.
- Advanced carousel features like autoplay or custom navigation.
