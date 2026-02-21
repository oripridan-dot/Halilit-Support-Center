```typescript
// Contract: Refactor Product Intelligence View — Full Architecture Alignment + Ecosystem Tab

// Shared Types
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
  integration_url: string;
  image_url: string;
}

// Request/Response Types

export const GET_PRODUCT_ECOSYSTEM_PATH = "/api/products/{product_id}/ecosystem";

export interface GetProductEcosystemResponse {
  related_products: RelatedProduct[];
  integrations: Integration[];
}

// Conductor Product Type
export interface ConductorProduct {
  id: string; // SKU (Commercial Scout)
  name: string; // Title (Official Scout)
  brand: string; // Brand name (Official Scout)
  category?: string;
  subcategory?: string;
  price?: number | null; // IL price (₪); null = Call for Price
  price_eilat?: number | null; // Eilat price; null = not applicable
  image_url?: string; // Hero image URL (Official Scout)
  official_url?: string; // Official brand page (verified if present)
  stock?: number | null; // 0 = OOS; null/absent = unknown
  description?: string;
  data_trust: {
    price_source: "halilit" | "official" | "estimated" | "none";
    specs_source: "halilit" | "official" | "none";
    description_source: "halilit" | "official" | "synthesized" | "none";
    image_source: "halilit" | "official" | "none";
    review_source: "contextual" | "none";
  };
  sku?: string; // Add SKU field.
}

// JIT State Type
export interface JITState {
  status: "idle" | "snap" | "intel" | "wisdom" | "complete" | "error";
  statusMessage: string | null;
  snap: {
    title: string | null;
    description: string | null;
    specs: Record<string, string> | null;
    related_products: string[] | null; // Array of product IDs
    thumbnail: string | null; // Add thumbnail field
  };
}
```