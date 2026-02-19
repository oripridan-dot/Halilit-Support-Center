# Spec: Product Detail - Ecosystem Tab

**Target:** `frontend/src/components/ProductDetail/EcosystemTab.tsx`

## Overview
This component renders the "Ecosystem" tab within the product detail view. It displays a list of related products and integrations, fetched from the backend, enabling users to explore the wider Halilit ecosystem associated with the selected product.

## Requirements
- The component must fetch related products and integrations from the `/api/products/{product_id}/ecosystem` endpoint on initial mount.
- The component must display a loading state while fetching data.
- If the API returns an error, the component must display an error message to the user.
- The component must display related products as clickable cards, including the product name and a brief description.
- The component must display integrations as clickable cards, including the integration name and a brief description.
- Related products and integrations must be visually separated into distinct sections.
- The component should use Tailwind CSS for styling, adhering to the dark theme and slate-900/blue-500 palette.
- The component should be responsive and work well on different screen sizes.

## Data Contract

**API Endpoint:** `/api/products/{product_id}/ecosystem`

**Request:** `GET`

**Response (Success - 200 OK):**

```json
{
  "related_products": [
    {
      "product_id": "string",
      "name": "string",
      "description": "string",
      "image_url": "string",
      "product_url": "string"
    }
  ],
  "integrations": [
    {
      "integration_id": "string",
      "name": "string",
      "description": "string",
      "logo_url": "string",
      "integration_url": "string"
    }
  ]
}
```

**Response (Error - 500 Internal Server Error):**

```json
{
  "detail": "string"
}
```

**TypeScript Interface:**

```typescript
interface EcosystemData {
  related_products: RelatedProduct[];
  integrations: Integration[];
}

interface RelatedProduct {
  product_id: string;
  name: string;
  description: string;
  image_url: string;
  product_url: string;
}

interface Integration {
  integration_id: string;
  name: string;
  description: string;
  logo_url: string;
  integration_url: string;
}
```

## Behavior Scenarios

- **Scenario:** Initial Load - Success
  - Input: Component mounts with `product_id = "some_product_id"`. API returns `200 OK` with valid ecosystem data.
  - Outcome:
    - A "Related Products" section is displayed.
    - A "Integrations" section is displayed.
    - Each related product is rendered as a clickable card with its name, description, and image, linking to the `product_url`.
    - Each integration is rendered as a clickable card with its name, description, and logo, linking to the `integration_url`.

- **Scenario:** Initial Load - Loading State
  - Input: Component mounts with `product_id = "some_product_id"`. The API request is in progress.
  - Outcome: A loading indicator (e.g., a spinner) is displayed.

- **Scenario:** Initial Load - API Error
  - Input: Component mounts with `product_id = "some_product_id"`. The API returns `500 Internal Server Error` with `detail = "Failed to fetch ecosystem data"`.
  - Outcome: An error message "Failed to load ecosystem data" is displayed to the user.

- **Scenario:** No Related Products or Integrations
  - Input: Component mounts with `product_id = "some_product_id"`. The API returns `200 OK` with empty `related_products` and `integrations` arrays.
  - Outcome: The "Related Products" and "Integrations" sections are still rendered but display a message "No related products found" and "No integrations found" respectively.

## Out of Scope
- Implementing the actual product or integration detail pages. This component only provides the links to those pages.
- Authentication. The API is assumed to be publicly accessible.
- Search or filtering of related products or integrations.
