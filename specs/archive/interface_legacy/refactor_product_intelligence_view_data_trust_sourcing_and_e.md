# Spec: Refactor Product Intelligence View — Data Trust, Sourcing, and Ecosystem Integration

**Version:** 3.0
**Component:** `frontend/src/components/views/ProductDetailView.tsx`

## 1. Purpose & Intent

To fully integrate the `ProductDetailView` with the latest data contracts and components, ensuring proper display of data trust, sourcing information, and ecosystem relationships. This involves:

1.  Correctly fetching and displaying data from `useConductorCatalog`, `useJITIntelligence`, and the `/api/products/{product_id}/ecosystem` endpoint.
2.  Utilizing the `SourcingBadge` component to display sourcing information for different product attributes.
3.  Displaying stock and "Call for Price" indicators in the header.
4.  Rendering a carousel of product images.
5.  Displaying related products and integrations in the Ecosystem Tab.

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
  }
}
```

### 2.2 JIT Intelligence — from `useJITIntelligence`

```ts
interface JITState {
  phase: "idle" | "snap" | "intel" | "wisdom" | "complete" | "error";
  statusMessage: string | null;
  snap: {
    thumbnail?: string;
    specs?: Record<string, string>;
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

## 3. Requirements

1.  **Data Fetching:** Use `useConductorCatalog` to fetch the catalog data. Derive the current product from the `products` array using `activeProductId` from `useNavigationStore`.
2.  **Header Integration:** Integrate the `ProductDetailHeader` component to display the product name, stock status, and "Call for Price" indicator.
3.  **Image Display:** Use the `ResponsiveImage` component to display the product's hero image, sourced from `product.image_url`.
4.  **Sourcing Badges:** Integrate the `SourcingBadge` component to display sourcing information for the product description, specs, and price.
5.  **JIT Badge:** Integrate the `JITBadge` component to display the JIT processing status, passing the `productId` as a prop.
6.  **Image Carousel:** Integrate the `ProductImageCarousel` component to display a carousel of product images.
7.  **Ecosystem Tab:** Integrate the `EcosystemTab` component to display related products and integrations.
8.  **Loading State:** Display a loading indicator while the catalog data is being fetched.
9.  **Error Handling:** Display an error message if the product cannot be found in the catalog.

---

## Stitch UI Prompt

```text
// Target Component: ProductDetailView
// Description: A React component that displays detailed information about a product, including its name, description, images, specifications, and related products.

// Overall Layout:
// - Use a responsive grid layout with two columns on larger screens and a single column on smaller screens.
// - The left column should display the product image, and the right column should display the product information, specifications, and related products.
// - Use Tailwind CSS classes to style the component, adhering to a dark theme (slate-900 background, blue-500 accents).

// Data Slots:
// - Product Name: [Product Name] (string)
// - Product Description: [Product Description] (string)
// - Product Image URL: [Product Image URL] (string)
// - Price: [Price] (number)
// - Stock Status: [Stock Status] (string, either "IN STOCK", "OUT OF STOCK", or "UNCONFIRMED")
// - Related Products: [Related Products] (array of objects, each with a name, description, and image URL)
// - Specifications: [Specifications] (object, with key-value pairs representing the product's specifications)

// Visual Style:
// - Dark theme: slate-900 background, blue-500 accents.
// - Use Tailwind CSS classes for styling text, backgrounds, borders, and spacing.
// - Ensure proper color contrast for readability.
// - Use a modern and clean design aesthetic.
// - loading indicator should show if data is being fetched, else display the components that show product details.

// Component Hierarchy:

// ProductDetailView (Root component)
//   - ResponsiveImage: Displays the product image.
//     - Data Slot: [Product Image URL]
//     - Data Slot: [Product Name] for alt text
//   - div: Contains product information (name, description, price, specifications, related products).
//     - h1: Displays the product name.
//       - Data Slot: [Product Name]
//     - p: Displays the product description.
//       - Data Slot: [Product Description]
//     - div: Contains badges
//       - ProductBadge:
//         - Data Slot: The relevant Product from useConductorCatalog
//       - JITBadge: Displays JIT processing status.
//         - Data Slot: [Product ID]
//     - ProductImageCarousel: Displays a carousel of product images.
//       - Data Slot: The Product Object so that ProductId can be used to fetch image list.
//     - EcosystemTab: Displays related products and integrations.
//       - Data Slot: The Product Object so that ProductId can be used to fetch related objects.
// Spacing:
// - Use Tailwind CSS classes for spacing (e.g., mt-4, mb-2, ml-2, p-4).
// - Ensure consistent spacing between elements.
```

## Verification Commands

- `pnpm tsc --noEmit`
- `pnpm run lint`
