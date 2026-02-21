# Spec: Refactor Product Intelligence View — Full Architecture Alignment + Ecosystem Tab

**Version:** 3.1
**Component:** `frontend/src/components/views/ProductDetailView.tsx`

## 1. Purpose & Intent

To fully integrate the `ProductDetailView` with the latest data contracts and components, ensuring proper display of data trust, sourcing information, and ecosystem relationships. This spec directly addresses a previous architectural violation and ensures that all child components render properly. It involves:

1.  Correctly fetching and displaying data from `useConductorCatalog`, `useJITIntelligence`, and the `/api/products/{product_id}/ecosystem` endpoint.
2.  Utilizing the `SourcingBadge` component to display sourcing information for different product attributes.
3.  Displaying stock and "Call for Price" indicators in the header.
4.  Rendering a carousel of product images.
5.  Displaying related products and integrations in the Ecosystem Tab.
6. Addressing missing "Verified Accessories" recommendations.
7.  Ensuring correct navigation.

This refactoring ensures alignment with the latest data models and component architecture, improving code maintainability, readability, and data integrity.

---

## 2. Data Contracts

### 2.1 Primary product — from `useConductorCatalog`

```ts
interface ConductorProduct {
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
```

### 2.2 JIT Intelligence — from `useJITIntelligence`

```ts
interface JITState {
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

### 2.3 Ecosystem Data — from `/api/products/{product_id}/ecosystem`

```ts
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

---

## 3. Component Requirements: ProductDetailView.tsx

### 3.1 Data Access Pattern

```tsx
import React, { useEffect, useState, useMemo } from "react";
import { useNavigationStore } from "../../store/navigationStore";
import { useConductorCatalog } from "../../hooks/useConductorCatalog";
import { ConductorProduct } from "../../types";
import ImageWithFallback from "../ImageWithFallback";
import JITBadge from "../ProductDetail/JITBadge";
import ProductImageCarousel from "../ProductDetail/ProductImageCarousel";
import EcosystemTab from "../ProductDetail/EcosystemTab";
import { ProductDetailHeader } from "../ProductDetail/ProductDetailHeader";

const ProductDetailView: React.FC = () => {
  const navigation = useNavigationStore();
  const { activeProductId } = navigation;
  const { products, isLoading, error } = useConductorCatalog();
  const [product, setProduct] = useState<ConductorProduct | undefined>(
    undefined,
  );

  useEffect(() => {
    if (products && activeProductId) {
      const foundProduct = products.find((p) => p.id === activeProductId);
      setProduct(foundProduct);
    }
  }, [products, activeProductId]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <svg
          className="animate-spin h-10 w-10 text-blue-500"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          ></circle>
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 6.627 5.373 12 12 12v-7.291z"
          ></path>
        </svg>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          <strong className="font-bold">Error!</strong> {error}
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-zinc-300">Product not found.</div>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 min-h-screen pb-6">
      <ProductDetailHeader product={product} />
      <div className="container mx-auto p-4 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="col-span-1 lg:col-span-1">
          <ImageWithFallback
            src={product.image_url || ""}
            alt={product.name}
            className="rounded-lg"
          />
        </div>
        <div className="col-span-1 lg:col-span-1">
          <div className="mb-4">
            <h1 className="text-2xl font-bold text-white">{product.name}</h1>
            <div className="flex items-center space-x-2 mt-2">
              <JITBadge productId={product.id} />
            </div>
            {product.description && (
              <p className="text-zinc-400">{product.description}</p>
            )}
          </div>
        </div>
      </div>
      <div className="container mx-auto p-4">
        <EcosystemTab productId={product.id} />
      </div>
    </div>
  );
};
export default ProductDetailView;

```

### 3.2 Component Wiring and Rendering

-   The `ProductDetailHeader` must render at the top, consuming the `product` object.
-   The `ImageWithFallback` component must display the `product.image_url` with `product.name` as the `alt` text.
-   The `JITBadge` component must be placed next to the `h1` tag in the header, receiving `product.id`.
-   The `EcosystemTab` component must render below the product information, receiving `product.id`.
- Add 'sku' field to ConductorProduct to fix "Cannot read properties of undefined (reading 'sku')".

### 3.3 Hero Image, Pricing, SKU Panel

These elements are displayed in the ProductDetailHeader as the same way as the last version. Refer to `frontend/src/components/ProductDetail/ProductDetailHeader.tsx`.

### 3.4 Ecosystem Tab

- Reuse the existing `EcosystemTab` component, passing the `product.id` prop.

## Verification Commands

- `pnpm tsc --noEmit`
- `pnpm run lint`
