```typescript
// Contract: Product Detail - Ecosystem Tab Placeholder

export const ECOSYSTEM_ENDPOINT = "/api/products/{product_id}/ecosystem";

export interface EcosystemResponse {
  related_products: RelatedProduct[];
  integrations: Integration[];
}

export interface RelatedProduct {
  product_id: string;
  name: string;
  description: string;
  image_url: string;
  product_url: string;
}

export interface Integration {
  integration_id: string;
  name: string;
  description: string;
  image_url: string;
  integration_url: string;
}
```