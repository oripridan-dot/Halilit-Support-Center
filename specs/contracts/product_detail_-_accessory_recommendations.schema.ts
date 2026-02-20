```typescript
// Contract: Product Detail - Accessory Recommendations

export const ACCESSORY_RECOMMENDATIONS_ENDPOINT = '/api/products/{product_id}/accessories';

export interface Accessory {
  id: string;
  name: string;
  imageUrl: string;
  price: number | null;
}

export interface AccessoriesResponse {
  accessories: Accessory[];
}

export interface AccessoriesErrorResponse {
  detail: string;
}
```