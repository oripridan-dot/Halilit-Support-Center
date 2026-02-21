```typescript
// Contract: Display "Verified" Badge on Accessory Cards

export const GET_PRODUCT_ECOSYSTEM_PATH = '/api/products/{product_id}/ecosystem';

export interface RelatedProduct {
  product_id: string;
  name: string;
  description: string;
  image_url: string;
  product_url: string;
  is_verified: boolean;
}

export interface Integration {
  integration_id: string;
  name: string;
  description: string;
  logo_url: string;
  integration_url: string;
  is_verified: boolean;
}

export interface GetProductEcosystemResponse {
  related_products: RelatedProduct[];
  integrations: Integration[];
}

export interface GetProductEcosystemRequestParams {
  product_id: string;
}
```