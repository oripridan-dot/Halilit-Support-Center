# Strategic Master Plan — Halilit Support Center v9.7.0

**Version:** 1.0 · Dark Factory
**Owner:** Operator
**Purpose:** High-level business goals that drive spec generation. The Steerer Agent reads this file and audits existing specs to find gaps.

---

## Business Goals

1. **Maximize Attachment Rate**
   Every major product (Guitar, Piano, Keyboard) MUST show compatible accessories (Stands, Cases, Pedals, Cables) immediately on the Product Detail screen. If no accessories are in the graph yet, show a placeholder prompt to the operator — never silence.

2. **Zero Broken Images**
   No product tile or detail view may show a broken `<img>` tag. Every image must have a professional dark placeholder fallback (`/placeholder.png` or an SVG inline fallback). Hero images in the catalog MUST be validated before display.

3. **Aggressive Out-of-Stock Signaling**
   Operators must never accidentally sell an out-of-stock item. Any product with `stock === 0` must render a **red border + "OUT OF STOCK" badge** in both InventoryView rows and ProductDetailView header. Unknown stock (`null`) must render an **amber "UNCONFIRMED"** badge.

4. **Speed of Service**
   Search results must sort "In Stock" items above "Call for Price" items by default. The search input must debounce at ≤ 150 ms. Catalog load must render a skeleton within 200 ms.

5. **Pricing Clarity**
   IL price and Eilat price must always appear side by side. "Call for Price" items must expose a one-tap **copy SKU** button so operators can quickly relay the SKU to the procurement team.

---

## Technical Standards

- **Latency:** All UI interactions (filter, sort, row click) must happen in < 100 ms.
- **Data Integrity:** No AI-generated specs or prices may be displayed as real data. Sourcing badge must be visible on all spec values.
- **Accessibility:** All interactive elements must be keyboard-navigable (Enter/Space to activate rows).
- **Resilience:** Every view must handle `isLoading`, `error`, and `empty` states explicitly — no blank white screens.

---

## Current Gaps (Steerer Audit Targets)

The Steerer Agent should flag any spec or component that does NOT satisfy the above. Typical gaps to look for:

- Inventory rows with no stock colour coding
- Product detail Ecosystem tab that shows nothing when `related_ids` is empty
- Missing image fallback logic in `<img>` tags
- Search that does not debounce
- Missing "Copy SKU" affordance for CfP products
