---
id: hsc_spec_product_intelligence
domain: operator_console
status: active
version: "2.1-holographic"
governance:
  - ZERO_CLICK_ECOSYSTEM_AWARENESS # UI must surface relations without user clicks
  - JIT_LOADING_STRICT # Never load full taxonomy into client memory
  - HSC_DESIGN_TOKENS_ONLY # No arbitrary hex codes — use Tailwind scale tokens
  - THREE_SOURCE_RULES_ENFORCED # Commercial/Official/Contextual boundaries must hold
api_contracts:
  - backend/ingestion/data_models.py # Python source of truth for Product entity
  - frontend/src/hooks/useJITIntelligence.ts # SSE streaming data contract
  - frontend/src/hooks/useConductorCatalog.ts # Catalog data-fetching contract
ui_dependencies:
  - frontend/src/types/index.ts # Canonical frontend types
  - frontend/src/store/navigationStore.ts # Navigation state (goToProduct, goToInventory, goBack)
golden_scenarios_validation: []
triggers_update_in:
  - specs/interface/02_inventory_grid.md
---

# Spec 03 — Product Intelligence View

**Version:** 2.1 · Chief v9.7.1 (Holographic)
**Component:** `frontend/src/components/views/ProductDetailView.tsx`
**Route state:** `currentView === 'PRODUCT_DETAIL'`, `activeProductId: string`
**Data sources:** `useConductorCatalog` (catalog), `useJITIntelligence` (SSE stream), `useProductRelationships` (graph)

---

## 1. Purpose & Intent

Product Intelligence answers:

> "Everything the operator needs to close a sale or resolve a support ticket for this product — right now."

This view combines three real data sources into a single coherent page:

1. Commercial (price, SKU) from catalog
2. Official (title, specs, media, brand page) from official scout
3. Contextual (relationships, accessories via graph) from product graph

No invented data. No AI-generated specs presented as real specs.

---

## 2. Data Contracts

### 2.1 Primary product — from `useConductorCatalog`

```ts
interface ConductorProduct {
  id: string; // SKU (Commercial Scout)
  name: string; // Title (Official Scout)
  brand: string;
  category?: string;
  subcategory?: string;
  price?: number | null; // IL ₪ price
  price_eilat?: number | null;
  image_url?: string;
  halilit_url?: string; // Halilit product page
  official_url?: string; // Official brand page
  specs?: Record<string, unknown>; // Official specs (catalog-cached)
  stock?: number; // Runtime stock; absent = unknown
}
```

### 2.2 JIT State — `useJITIntelligence(activeProductId)`

Streaming endpoint `/api/jit/product/{id}`. Resolves progressively:

```ts
interface JITState {
  status: "idle" | "loading" | "streaming" | "complete" | "error";
  snap?: {
    name?: string;
    brand?: string;
    price?: number;
    price_eilat?: number;
    thumbnail?: string;
  };
  officialSpecs?: {
    specs?: Record<string, unknown>; // Official specs (highest authority)
  };
  error?: string;
}
```

### 2.3 Relationships — `useProductRelationships(activeProductId)`

```ts
{
  accessories: RelatedProduct[];   // Verified accessories (green badge)
  compatible: RelatedProduct[];    // Compatible items
  alternatives: RelatedProduct[];  // Alternative products
  relationshipMeta: object;
  isLoading: boolean;
}
type RelatedProduct = { id: string; name: string; price?: number; image_url?: string; };
```

---

## 3. Layout Structure

```
┌──────────────────────────────────────────────────────────────────┐
│  ← Back                                                          │  Back button
├──────────────────────────────────────────────────────────────────┤
│  ┌────────────────┐  ┌──────────────────────────┐  ┌──────────┐ │
│  │  Hero Image    │  │  Title                   │  │ IL: ₪xxx │ │  Header Card
│  │  (contain,     │  │  Brand Badge             │  │ Eilat: - │ │
│  │   white bg)    │  │  SKU                     │  │ Stock ●  │ │
│  └────────────────┘  │  Category                │  └──────────┘ │
│                      └──────────────────────────┘               │
├──────────────────────────────────────────────────────────────────┤
│  [Copy Tech Specs]  [Generate Quote PDF]  [Open Official Page]  │  Action Toolbar (sticky)
├──────────────────────────────────────────────────────────────────┤
│  [Ecosystem ▼]   [Specifications]   [History]                   │  Tab bar
├──────────────────────────────────────────────────────────────────┤
│  Tab content (scrollable)                                       │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Product Resolution — Field Priority

| Field        | Primary source                                 | Fallback                                        |
| ------------ | ---------------------------------------------- | ----------------------------------------------- |
| Title        | `product.name`                                 | `jitState.snap?.name`                           |
| Brand        | `product.brand`                                | `jitState.snap?.brand`                          |
| IL Price     | `product.price`                                | `jitState.snap?.price`                          |
| Eilat Price  | `product.price_eilat`                          | `jitState.snap?.price_eilat`                    |
| Image        | `product.image_url`                            | `jitState.snap?.thumbnail` → `/placeholder.png` |
| Specs        | `jitState.officialSpecs?.specs` (if non-empty) | `product.specs` → `{}`                          |
| Official URL | `product.official_url`                         | — (button hidden)                               |

**Source rule:** Prices come from Commercial Scout only (`product.price`). Never display JIT price as primary price. JIT snap is only for display when catalog product is not yet loaded.

---

## 5. Header Card Details

### 5.1 Hero Image

- Container: white background, padding, `aspect-video` or fixed height
- `object-fit: contain` (preserve aspect ratio)
- `onError`: fade to `opacity-20` (no broken icon flash)
- src order: `product.image_url` → `jitState.snap?.thumbnail` → `/placeholder.png`

### 5.2 Title & Identity Block

- Large title (`text-2xl font-bold text-white`)
- Brand: clickable badge → `goToInventory()` with brand as filter (or pre-filled search: `goToInventory(displayBrand)`)

  **Brand click MUST use arrow wrapper:** `onClick={() => goToInventory(displayBrand)}`

- SKU: monospace, zinc-500
- Category/Subcategory: small zinc badge

### 5.3 Pricing Block

- IL Price: large (`text-3xl font-bold`) — `₪{price.toLocaleString()}` or "Call for Price" (amber)
- Eilat Price: smaller — `₪{price_eilat}` or "—"
- Both prices are from Commercial Scout only; never synthesize

### 5.4 Stock Status

- `stock === 0` → red dot + "Out of Stock"
- `stock > 0` → green dot + "In Stock"
- `stock == null` → gray dot + "Unknown"

---

## 6. Action Toolbar

All three buttons always visible (may be disabled/dimmed if action impossible):

| Button             | Label                | Behavior                                                                                                        |
| ------------------ | -------------------- | --------------------------------------------------------------------------------------------------------------- |
| Copy Tech Specs    | "Copy Tech Specs"    | Copies `formatSpecsAsText(specsRecord)` to clipboard; shows ✓ toast for 1.5s                                    |
| Generate Quote PDF | "Generate Quote PDF" | `window.print()` (mock); shows toast "Quote generated" for 1.5s                                                 |
| Open Official Page | "Open Official Page" | `window.open(product.official_url, "_blank", "noopener,noreferrer")`; button disabled/hidden if no official_url |

---

## 7. Tab System

### Tab A: Ecosystem (default)

Shows product relationships from the product graph.
Split into sections:

1. **Verified Accessories** (`accessories` array) — green "Verified" badge per item
2. **Alternatives** (`alternatives` array) — displayed without badge
3. **Compatible** (`compatible` array, if non-empty) — "Compatible" label

Each item: thumbnail + name + price (if available) + clickable → `goToProduct(item.id)`

**Empty state:** "No verified accessories found in the product graph."
**Loading:** skeleton cards while `relationsLoading === true`

### Tab B: Specifications

Key/value table from `specsRecord`:

```
| Spec name       | Value          |
```

Each row is striped (`even:bg-zinc-900/30`).
Empty state: "Official specifications not yet fetched. Run intelligence on this product."

### Tab C: History

Placeholder content:

```tsx
<p className="text-zinc-500 text-sm">
  Ticket history coming soon. No records for this product yet.
</p>
```

---

## 8. Skeleton Loader

Shown when `jitState.status === "loading" || jitState.status === "idle"`.
Must match layout:

- Left: image rectangle pulse
- Center: 3 lines (title wide, brand narrow, SKU narrow)
- Right: 2 price lines
- Toolbar: 3 button outlines
- Tab bar: 3 tab outlines
- Content: several rows of varying width

DO NOT show skeleton when product is found in catalog (`product !== null`) and JIT is still streaming — show catalog data immediately, update progressively.

---

## 9. 404 — Product Not Found

Shown when:

- `activeProductId` is null, OR
- Products are loaded AND `product === null` AND JIT returned error

```tsx
<div className="p-8 max-w-md">
  <p className="text-2xl font-bold text-zinc-400 mb-2">Product Not Found</p>
  <p className="text-sm text-zinc-500 mb-6">
    No product with ID "{activeProductId}" exists in the catalog.
  </p>
  <button onClick={goBack}>← Back to Search</button>
</div>
```

---

## 10. JIT Streaming Behavior

JIT intelligence (`useJITIntelligence`) streams progressively via SSE. The UI should:

1. Show catalog data immediately (never wait for JIT to complete)
2. Update specs when `jitState.officialSpecs` resolves (replace catalog specs if JIT specs non-empty)
3. Show a subtle loading indicator (spinner in tab header or status bar) while `status === "streaming"`
4. On `status === "error"`: show inline amber notice "Intelligence fetch failed" below toolbar — do NOT crash

---

## 11. Behavior Scenarios

| Scenario                     | Precondition                                            | Expected outcome                                      |
| ---------------------------- | ------------------------------------------------------- | ----------------------------------------------------- |
| Product found in catalog     | `products.find(p => p.id === activeProductId)` exists   | Header shows immediately; JIT streams in background   |
| Product not in catalog (new) | `product === null`, JIT loading                         | Skeleton shown; populates from JIT snap as it streams |
| Product not found anywhere   | `product === null`, JIT error                           | 404 screen with Back button                           |
| No official URL              | `product.official_url` absent                           | "Open Official Page" button disabled/hidden           |
| No specs                     | Both `product.specs` and `jitState.officialSpecs` empty | Specs tab shows empty state message                   |
| No relations                 | All relations arrays empty                              | Ecosystem tab shows empty state                       |
| Copy specs clicked           | Specs non-empty                                         | Clipboard written; "✓ Copied" toast for 1.5s          |
| Brand badge clicked          | `displayBrand` set                                      | Navigate to Inventory pre-filtered to that brand      |
| Related product clicked      | Any                                                     | Navigate to `PRODUCT_DETAIL` for that product ID      |

---

## 12. Agent Checklist

- [ ] Product from catalog loaded immediately (no waiting for JIT)
- [ ] JIT snap used only as fallback — catalog prices never overridden by JIT
- [ ] `specifications` tab reads `jitState.officialSpecs?.specs` first, then `product.specs`
- [ ] Action toolbar always rendered (buttons disabled, not hidden, when impossible)
- [ ] Brand badge click uses arrow wrapper: `onClick={() => goToInventory(brand)}`
- [ ] Thumbnail `onError` → opacity-20 (no broken image)
- [ ] 404 screen shown correctly (not a crash, not empty)
- [ ] Skeleton matches layout (image + pricing + toolbar + tabs)
- [ ] JIT streaming error shown inline, does not crash
- [ ] Related product cards are clickable via `() => goToProduct(item.id)`
- [ ] History tab shows placeholder (not empty, not an error)

## Stitch UI Prompt

> Copy this entire block into Google Stitch, Lovable, or v0.dev.

---

Build a **Product Intelligence View** React component in TypeScript using **Tailwind CSS**. This is a full-page operator console view — dark mode, professional, information-dense.

**Overall style:**

- Background: `bg-zinc-950`
- Surface cards: `bg-zinc-900` with `border border-zinc-800 rounded-xl`
- Accent color: `blue-500` for interactive elements
- Text hierarchy: `text-white` (titles), `text-zinc-300` (body), `text-zinc-500` (muted/labels)
- Icons: `lucide-react` only

---

**Layout (top to bottom, full width):**

### 1. Back Button Row

- Simple `← Back` text button, `text-zinc-400 hover:text-white`, top-left of page

### 2. Header Card (`bg-zinc-900 rounded-xl p-6 flex flex-row gap-6`)

Three columns inside:

**Column A — Hero Image (w-48 h-48, bg-white rounded-lg p-2)**

- `<img>` with `object-contain w-full h-full`
- Data slot: `{imageUrl}` (string URL placeholder)

**Column B — Identity Block (flex-1)**

- `<h1 className="text-2xl font-bold text-white">{productName}</h1>`
- Brand badge: `<span className="inline-block px-2 py-0.5 bg-blue-500/20 text-blue-400 text-sm rounded cursor-pointer">{brandName}</span>`
- SKU: `<p className="font-mono text-zinc-500 text-sm mt-1">{skuId}</p>`
- Category: `<span className="text-xs bg-zinc-800 text-zinc-400 px-2 py-0.5 rounded">{category}</span>`

**Column C — Pricing Block (w-40, text-right)**

- IL Price: `<p className="text-3xl font-bold text-white">₪{ilPrice}</p>` — if no price show `<p className="text-amber-400 text-lg">Call for Price</p>`
- Eilat Price: `<p className="text-sm text-zinc-400">Eilat: ₪{eilatPrice}</p>` — if no eilat show `—`
- Stock dot: green dot + "In Stock" / red dot + "Out of Stock" / gray dot + "Unknown" (small, bottom of block)

### 3. Action Toolbar (`flex flex-row gap-3 py-3 border-y border-zinc-800 sticky top-0 bg-zinc-950 z-10`)

Three buttons side by side:

- `[📋 Copy Tech Specs]` — `bg-zinc-800 hover:bg-zinc-700 text-white px-4 py-2 rounded-lg text-sm`
- `[🖨 Generate Quote PDF]` — same style
- `[🔗 Open Official Page]` — same style, visually dimmed (`opacity-50`) when disabled

### 4. Tab Bar (`flex flex-row gap-1 border-b border-zinc-800`)

Three tabs: **Ecosystem** | **Specifications** | **History**

- Active tab: `border-b-2 border-blue-500 text-white`
- Inactive: `text-zinc-500 hover:text-zinc-300`
- "Ecosystem" is selected by default

### 5. Tab Content Area (`mt-4 min-h-64`)

**Ecosystem tab:**
Three sections stacked:

- "Verified Accessories" heading + green `Verified` badge per item
- "Alternatives" heading
- "Compatible" heading (only if items exist)

Each related product: `bg-zinc-900 rounded-lg p-3 flex gap-3 cursor-pointer hover:bg-zinc-800`

- Small image (48×48, white bg, contain)
- Name (`text-white text-sm`) + price (`text-zinc-400 text-xs`)
- Use placeholders: `{accessoryName}`, `{accessoryPrice}`, `{accessoryImageUrl}`

Empty state: `<p className="text-zinc-500 text-sm">No verified accessories found in the product graph.</p>`

**Specifications tab:**
Table: `w-full text-sm`

- Rows: `even:bg-zinc-900/30`
- Left cell: `text-zinc-400 font-medium w-1/3`
- Right cell: `text-white`
- Data slot: array of `{ key: string; value: string }` placeholders
- Empty state: `<p className="text-zinc-500 text-sm">Official specifications not yet fetched.</p>`

**History tab:**
Just: `<p className="text-zinc-500 text-sm">Ticket history coming soon. No records for this product yet.</p>`

---

**Skeleton loader state** (show when loading):

- Pulse animation (`animate-pulse bg-zinc-800 rounded`) for all content areas
- Image: `w-48 h-48 rounded-lg`
- Title: `h-6 w-64 rounded`
- Brand: `h-4 w-32 rounded`
- Price: `h-8 w-24 rounded`
- Three toolbar button outlines
- Three tab outlines
- Several rows of varying width content lines

---

**DO NOT:**

- Hardcode any product names, prices, or SKUs — use placeholder variables only
- Use any library other than `lucide-react` for icons
- Use `react-router-dom`
- Add any `useEffect`, `useState`, or data fetching — UI only, no logic

---

## Verification Commands

- `pnpm tsc --noEmit`
- `pnpm run lint`
