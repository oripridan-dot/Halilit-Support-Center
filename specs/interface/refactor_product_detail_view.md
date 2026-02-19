# Spec: Refactor ProductDetailView — Full Architecture Alignment

**Version:** 1.0
**File:** `frontend/src/components/views/ProductDetailView.tsx`

## 1. Problem

`ProductDetailView` has three critical architectural violations:

1. **Wrong hook call**: `useConductorCatalog(productId)` — the hook takes NO arguments and
   returns the full catalog. The component must derive the product from the catalog array.
2. **Wrong field access**: reads `catalogData?.price`, `catalogData?.name`,
   `catalogData?.image_url`, `catalogData?.specifications` — treating the hook result as a
   single product. Must use `ConductorProduct` fields after looking up by `activeProductId`.
3. **Orphaned sub-components**: `EcosystemTab`, `ProductImageCarousel`, `SourcingBadge`,
   `JITBadge` exist but are NOT wired into the view. The layout is a bare `<div>`.

## 2. Requirements

### 2.1 Data Access Pattern

```tsx
const { products } = useConductorCatalog(); // no args
const { activeProductId } = useNavigationStore();
const product = useMemo(
  () => products.find((p) => p.id === activeProductId) ?? null,
  [products, activeProductId],
);
```

### 2.2 Field Mapping (ConductorProduct → UI)

| UI Element        | Field                                                                |
| ----------------- | -------------------------------------------------------------------- |
| Product name      | `product.name`                                                       |
| Brand             | `product.brand`                                                      |
| IL Price          | `product.price`                                                      |
| Eilat Price       | `product.price_eilat`                                                |
| Hero image        | `product.image_url`                                                  |
| Gallery           | `product.image_gallery`                                              |
| SKU               | `product.id`                                                         |
| Halilit URL       | `product.halilit_url`                                                |
| Specs table       | `product.specs`                                                      |
| Description       | `product.description`                                                |
| Short description | `product.description_short`                                          |
| Features          | `product.features`                                                   |
| Pros              | `product.pros`                                                       |
| Cons              | `product.cons`                                                       |
| Rating            | `product.rating`                                                     |
| Data quality      | `product.data_status`, `product.quality_score`                       |
| Source badges     | `product.data_trust.price_source`, `product.data_trust.specs_source` |

### 2.3 Layout Structure

The view MUST use a 2-column layout (on md+):

- **Left column (1/3):** Hero image → image carousel (use `ProductImageCarousel` or `ImageWithFallback`),
  SKU display + copy button, pricing block, Halilit URL button, data quality badge.
- **Right column (2/3):** Product name + brand, tabbed panel:
  - Tab 1 "Overview": `description`, `features` list, pros/cons
  - Tab 2 "Specs": `specs` key-value table
  - Tab 3 "Ecosystem": `<EcosystemTab productId={product.id} />`
  - Tab 4 "Reviews": rating + `review_synthesis_summary` + `real_world_insights`

### 2.4 Pricing Block (Side-by-Side)

- If `product.price > 0`: show `₪ {product.price.toLocaleString('he-IL')} (IL)`
- If `product.price_eilat > 0`: show `₪ {product.price_eilat.toLocaleString('he-IL')} (Eilat)`
- If `product.price === 0 || !product.price`: show `"Call for Price (IL)"`
- Source badge from `product.data_trust.price_source`

### 2.5 Copy SKU Button

- Displays `product.id` in a monospace chip
- Clicking copies to clipboard, icon changes to CheckIcon for 2 seconds

### 2.6 Halilit URL Button

- Only renders if `product.halilit_url` is truthy
- Opens in new tab with `target="_blank" rel="noopener noreferrer"`
- Icon: `ExternalLink` from lucide-react

### 2.7 Source Badge Logic

Replace custom `renderBadge()` with `data_trust`:

```tsx
const priceBadge = product.data_trust.price_source; // 'halilit' | 'official' | 'estimated' | 'none'
const specsBadge = product.data_trust.specs_source; // 'halilit' | 'official' | 'none'
```

Map to badge labels: `halilit` → "Commercial", `official` → "Official", `estimated` → "Estimated".

### 2.8 JIT Intelligence

- Import and use `useJITIntelligence(product.id)` hook.
- Overlay JIT streaming data on top of catalog data where available.
- Show `<JITBadge productId={product.id} />` near the header.

### 2.9 Loading / Error States

- Loading: skeleton placeholder with `animate-pulse` for image and text blocks.
- Product not found: centered message "Product not found" with back button.
- Error: alert banner with retry.

## 3. Styling

- Dark theme: `bg-zinc-950` page, `bg-zinc-900` cards.
- Tailwind only. No inline styles.
- Tab active state: `border-b-2 border-blue-500 text-blue-400`.
- Import only from `lucide-react`.

## 4. Behavior Scenarios

**S1 — Normal load:**
Product found in catalog → renders left + right columns with data.

**S2 — CfP product:**
`product.price === 0` → pricing block shows "Call for Price (IL)" badge.

**S3 — Unknown product ID:**
`activeProductId` not found in catalog → "Product not found" message.

**S4 — Copy SKU:**
User clicks copy → icon changes to check for 2s → clipboard has product.id value.
