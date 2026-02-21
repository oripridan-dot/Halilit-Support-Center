```typescript
// Contract: Refactor Product Intelligence View — Data Trust, Sourcing, and Ecosystem Integration

// Ecosystem Endpoint
export const ECOSYSTEM_ENDPOINT = "/api/products/{product_id}/ecosystem";

// Shared Types
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
  logo_url: string;
  integration_url: string;
}

// Request Type (None specified, assuming GET request with product_id in the path)
//export interface EcosystemRequest {}


// Response Type
export interface EcosystemData {
  related_products: RelatedProduct[];
  integrations: Integration[];
}

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
  }
}

export interface JITState {
  phase: "idle" | "snap" | "intel" | "wisdom" | "complete" | "error";
  statusMessage: string | null;
  snap: {
    thumbnail?: string;
    specs?: Record<string, string>;
  };
}
```