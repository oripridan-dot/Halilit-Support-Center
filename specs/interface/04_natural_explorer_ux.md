# Spec 04 — Natural Explorer UX Overhaul

**Version:** 1.0 · Chief v9.7.1
**Component:** `frontend/src/components/views/ExplorerView.tsx`
**Route state:** `currentView === 'EXPLORER'`
**Data sources:** `useConductorCatalog` (catalog), `useTaxonomyTree` (hierarchy)

---

## 1. Purpose & Intent

Replace the flat, paginated inventory lists with a **Cascading Explorer** (Miller Columns style) that visually represents the natural hierarchy of the Halilit catalog:

```
Brand → Category → Family → Series → Product
```

The Operator navigates by clicking — not typing — and arrives at a specific product in 3–4 clicks. The view surfaces the rich hierarchy already computed by the backend taxonomy pipeline.

---

## 2. The Natural Explorer UX Strategy

### 2.1 Entry Point — The Brand/Category Hub

- User lands on a **Bento Box** of top-tier brands (Allen & Heath, Roland, RCF, etc.) and universal categories (Mixers, Keys, PA).
- Tapping a brand or category enters the first drill-down level.
- No search required — this is disambiguation by tapping.

### 2.2 Cascading Drill-Down (Miller Columns)

```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐
│ Brands / │  │ Families │  │  Series  │  │    Products      │
│ Categories│→ │          │→ │          │→ │  (cards + spec)  │
└──────────┘  └──────────┘  └──────────┘  └──────────────────┘
```

- Each column slides in from the right with a smooth animation.
- The active row in each column stays highlighted.
- A **Path Header** at the top shows the breadcrumb trail.

### 2.3 Ecosystem Context

Once a product is selected, the Product column shows:

- Specs, pricing, stock
- Verified accessories from the product graph (same data as Spec 03)
- Clicking a product navigates to `PRODUCT_DETAIL` view

---

## 3. Component: `ExplorerView.tsx`

**Route state:** `currentView === 'EXPLORER'`

### 3.1 Navigation State (Zustand)

The explorer drill-down state lives in `navigationStore`:

```ts
explorerPath: {
  brand?: string;       // selected brand slug
  category?: string;    // selected category
  family?: string;      // selected family
  series?: string;      // selected series
}
setExplorerPath: (path: Partial<ExplorerPath>) => void;
clearExplorerPath: () => void;
```

### 3.2 Column Definitions

| Column           | Content                                | Populated when             |
| ---------------- | -------------------------------------- | -------------------------- |
| Col 0 — Hub      | Brands + top categories                | Always visible             |
| Col 1 — Families | Families under selected brand/category | Brand or category selected |
| Col 2 — Series   | Series under selected family           | Family selected            |
| Col 3 — Products | Products in selected series            | Series selected            |

Columns slide in/out using **Framer Motion** `AnimatePresence` + `motion.div` with `x: 40 → 0` entry.

---

## 4. Data Contract

### 4.1 Taxonomy Tree (from `useTaxonomyTree`)

```ts
interface TaxonomyNode {
  id: string;
  label: string;
  icon?: string; // optional lucide icon name
  count: number; // product count in this node
  children?: TaxonomyNode[];
}

interface TaxonomyTree {
  brands: TaxonomyNode[]; // top-level brands
  categories: TaxonomyNode[]; // top-level categories
}
```

### 4.2 Hook: `useTaxonomyTree`

Located at `frontend/src/hooks/useTaxonomyTree.ts`.

Derives the taxonomy tree from the flat `ConductorProduct[]` returned by `useConductorCatalog`. Memoized computation — no additional API calls.

```ts
function useTaxonomyTree(): {
  tree: TaxonomyTree;
  isLoading: boolean;
};
```

Build the tree by grouping catalog products:

1. Group by `product.brand` → brand nodes
2. Under each brand, group by `product.category` → family nodes
3. Under each family, group by `product.subcategory` → series nodes
4. Leaf products are the items in each series node

---

## 5. Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│  ← Back  │  🔭 Explorer  │  [path header: Roland > Synths] │  Top bar
├──────────────────────────────────────────────────────────────┤
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌───────────────────────┐ │
│  │ Brands │ │Families│ │ Series │ │ Products (cards)      │ │
│  │        │ │        │ │        │ │                       │ │
│  │ • Allen│ │ • Mixers│ │ • Qu   │ │ [ Qu-16 card ]       │ │
│  │   & H  │ │ • Keys │ │ • SQ   │ │ [ Qu-32 card ]       │ │
│  │ • Roland│ │ • Drums│ │        │ │ [ Qu-SB card ]       │ │
│  │ • RCF  │ │        │ │        │ │                       │ │
│  └────────┘ └────────┘ └────────┘ └───────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Column Component Details

### 6.1 Hub Column (Col 0)

Two sections:

1. **Brands** — icon (first letter avatar) + brand name + product count badge
2. **Categories** — category icon (lucide) + name + count

Active row: `bg-emerald-500/10 border-l-2 border-emerald-500 text-white`
Inactive row: `text-zinc-400 hover:bg-zinc-800 hover:text-white`

Width: `w-56` fixed, full height, scrollable.

### 6.2 Family / Series Columns (Col 1, Col 2)

Same row style as Hub. Width: `w-48`. Full height, scrollable.

Empty state: `text-zinc-600 text-xs p-4 italic` — "No sub-categories found."

### 6.3 Product Cards Column (Col 3)

Width: `flex-1` (takes remaining width). Grid: `grid grid-cols-2 gap-3` (or single column if narrow).

Each card (`bg-zinc-900 border border-zinc-800 rounded-xl p-3`):

- Thumbnail (`w-16 h-16 bg-white rounded p-1 object-contain`)
- Name (`text-sm font-semibold text-white`)
- SKU (`text-xs font-mono text-zinc-500`)
- Price: `₪{price}` or "Call for Price"
- Stock dot (green/yellow/red)
- On click: `goToProduct(product.id)`

---

## 7. Path Header

Sticky below top bar. Shows breadcrumb trail.

```
🔭 Explorer  /  Roland  /  Synthesizers  /  Fantom
```

Each segment is a clickable link that resets the drill-down to that level.
Separator: `/` in zinc-600.

---

## 8. Visual Style

| Token          | Value                                             |
| -------------- | ------------------------------------------------- |
| Background     | `bg-zinc-950`                                     |
| Column surface | `bg-zinc-900 border-r border-zinc-800`            |
| Active row     | `bg-emerald-500/10 border-l-2 border-emerald-500` |
| Hover row      | `bg-zinc-800`                                     |
| Accent         | `emerald-500`                                     |
| Text primary   | `text-white`                                      |
| Text muted     | `text-zinc-400`                                   |
| Font mono      | SKU labels only                                   |

---

## 9. Entry Points

ExplorerView is accessible from:

1. **Dashboard** — "Explore Catalog" button / tile
2. **Sidebar/Nav** — persistent nav item
3. URL state: `currentView === 'EXPLORER'`

---

## 10. Behavior Scenarios

| Scenario              | Expected outcome                                          |
| --------------------- | --------------------------------------------------------- |
| First load            | Hub column shows brands + categories; other columns empty |
| Click brand           | Col 1 slides in with brand families/categories            |
| Click family          | Col 2 slides in with series                               |
| Click series          | Col 3 populates with product cards                        |
| Click product card    | Navigate to `PRODUCT_DETAIL` for that product             |
| Click path breadcrumb | Drill-down resets to that level                           |
| No children at level  | Empty state message in that column                        |
| Catalog loading       | Skeleton columns shown                                    |

---

## 11. Agent Checklist

- [ ] `useTaxonomyTree` hook implemented, derives tree from flat catalog
- [ ] ExplorerView renders Hub column on mount
- [ ] Columns animate in/out with Framer Motion
- [ ] Active row highlighting works per column
- [ ] Path header updates with drill-down breadcrumb
- [ ] Product cards show thumbnail, name, SKU, price, stock dot
- [ ] Clicking product card navigates to `PRODUCT_DETAIL`
- [ ] Navigator state (`explorerPath`) added to `navigationStore`
- [ ] `currentView === 'EXPLORER'` case handled in `App.tsx`
- [ ] Dashboard has visible entry point to ExplorerView
- [ ] `pnpm tsc --noEmit` passes

---

## 12. Stitch / V0 UI Prompt

> Copy this block verbatim into V0.dev or Google Stitch.

```text
Generate a modern, dark-mode React component called 'ExplorerView' using Tailwind CSS, Lucide icons, and Framer Motion for smooth slide-in animations.

Visual Style: Deep zinc backgrounds (bg-zinc-950), column surfaces (bg-zinc-900 with border-r border-zinc-800), and vibrant emerald accent highlights (emerald-500 for active states).

Layout Structure (Cascading Columns / Miller Columns):
1. Full-height flex row container with 3-4 vertical columns side by side.
2. Column 0 (Hub - Brands/Categories): w-56, scrollable list of clickable rows. Each row has an avatar (first letter), label, and count badge. Clicking highlights the row and triggers the next column.
3. Column 1 (Families): w-48, slides in from the right when Col 0 item is selected. Same row style.
4. Column 2 (Series): w-48, same pattern.
5. Column 3 (Products): flex-1, shows a 2-column grid of product cards. Each card: thumbnail (white bg, object-contain), product name, SKU in monospace, price, green/yellow/red stock dot. Cards are clickable.
6. A sticky Path Header bar at the top shows: "Explorer / [Brand] / [Family] / [Series]" as clickable breadcrumbs.

Animations: Use Framer Motion's AnimatePresence + motion.div. Each new column enters with x: 40 → 0 and opacity: 0→1 over 0.2s. Columns exit with x: -20, opacity: 0.

Active row style: bg-emerald-500/10 border-l-2 border-emerald-500 text-white font-medium
Inactive row style: text-zinc-400 hover:bg-zinc-800 hover:text-white px-4 py-2 rounded-r-lg cursor-pointer

DO NOT use react-router-dom, useEffect, useState, or any data fetching. Demonstrate the full layout with realistic dummy data (brands: Roland, Allen & Heath, RCF, Shure; families: Synthesizers, Digital Pianos, Mixers; series: Fantom, Juno; products: Fantom-06, Fantom-08).

This is a dense operator console — not a consumer store. Pack as much information as possible without feeling cluttered.
```

---

## Verification Commands

```bash
pnpm tsc --noEmit
pnpm run lint
```
