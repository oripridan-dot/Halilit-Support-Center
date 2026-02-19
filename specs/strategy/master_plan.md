# Strategic Master Plan — Halilit Support Center v9.7.0

**Version:** 2.0 · Dark Factory (Librarian Architecture)
**Owner:** Operator
**Purpose:** The Spine of the Library. Injected into the Chief Agent on every cycle to provide global product context, Ubiquitous Language, and a Chapter Directory. The Chief uses this file to route agents to the exact specs they need — nothing more, nothing less.

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

---

## Chapter Directory (The Library)

> **Chief Routing Rule:** When a task maps to a Business Goal below, read the linked Chapter(s) — and only those — before routing agents. Do not guess spec paths; they are all listed here.

### Book 1 — The Data Engine (Source of Truth)
Covers how raw brand and Halilit data is fetched, validated, and stored. These chapters govern the backend pipeline and the Three Source Rules.

| Chapter | Spec Path | Governs |
|---|---|---|
| 1.1 Commercial Source (Halilit API) | `specs/01_data/halilit_api.md` | Golden List, SKUs, IL + Eilat prices |
| 1.2 Official Scout (Brand Pages) | `specs/01_data/official_scout.md` | Titles, descriptions, media, specs |
| 1.3 Catalog Organizer | `specs/01_data/catalog_organizer.md` | Normalization, taxonomy, graph |
| 1.4 Data Compliance | `specs/01_data/COMPLIANCE.md` | Three Source Rules enforcement |

### Book 2 — The Ingestion Pipeline
Covers the mechanics of getting data from raw scrape to normalized catalog.

| Chapter | Spec Path | Governs |
|---|---|---|
| 2.1 Ingestion Rules | `specs/data_pipeline/01_ingestion_rules.md` | Field mapping, deduplication, draft validation |
| 2.2 Relationship Logic | `specs/data_pipeline/02_relationship_logic.md` | Accessory, alternative, bundle graph edges |

### Book 3 — The Operator Experience (Canonical Views)
These are the three master UI specs. Every frontend component must satisfy its parent chapter before any feature spec is implemented.

| Chapter | Spec Path | Governs |
|---|---|---|
| 3.1 Dashboard | `specs/interface/01_operator_dashboard.md` | KPI tiles, catalog health, quick actions |
| 3.2 Inventory Grid | `specs/interface/02_inventory_grid.md` | Product rows, stock badges, search, sort, filter |
| 3.3 Product Intelligence (Detail View) | `specs/interface/03_product_intelligence.md` | Hero, pricing panel, JIT intelligence, ecosystem tab |

### Book 4 — Feature Specs (Generated)
Granular specs for individual features. Always implement against the parent Chapter 3 spec first. Grouped by Business Goal.

**Goal 1 — Maximize Attachment Rate**
- `specs/interface/accessory_recommendations_component.md`
- `specs/interface/product_detail_-_accessory_recommendations.md`
- `specs/interface/product_detail_-_ecosystem_tab.md`
- `specs/interface/product_detail_ecosystem_tab.md`

**Goal 2 — Zero Broken Images**
- `specs/interface/product_detail_-_hero_image_validation_service.md`
- `specs/interface/product_detail_-_image_fallback_implementation.md`
- `specs/interface/product_detail_-_image_sourcing.md`
- `specs/interface/product_image_fallback_and_validation.md`
- `specs/interface/product_tile_-_image_validation_and_fallback.md`
- `specs/interface/image_refresh_service.md`

**Goal 3 — Aggressive Out-of-Stock Signaling**
- `specs/interface/inventory_stock_status_indicators.md`
- `specs/interface/product_tile_-_out_of_stock_and_cfp_indicators.md`

**Goal 4 — Speed of Service**
- `specs/interface/inventory_search_debounce.md`
- `specs/interface/inventory_search_stock_cfp_sorting.md`
- `specs/interface/sort_search_results_by_stock_status.md`
- `specs/interface/global_search_-_prioritize_exact_sku_matches.md`
- `specs/behavior/01_search_scenarios.md`

**Goal 5 — Pricing Clarity**
- `specs/pricing_logic.md`
- `specs/interface/product_detail_-_side-by-side_pricing.md`
- `specs/interface/product_detail_side_by_side_pricing_component.md`
- `specs/interface/copy_sku_button_for_product_detail_page.md`
- `specs/interface/product_detail_-_copy_sku_button.md`

**Cross-Cutting Features**
- `specs/interface/product_detail_-_sourcing_badge.md` — Data trust / sourcing badges
- `specs/interface/sourcing_badge_data_trust.md`
- `specs/interface/product_detail_-_dynamic_jit_badge_updates.md` — JIT streaming
- `specs/interface/product_detail_-_halilit_url_button.md`

### Book 5 — Infrastructure & Fixes
Repair specs and internal service improvements.

- `specs/interface/fix_canonical_product_type.md`
- `specs/interface/fix_conductor_product_stock_field.md`
- `specs/interface/improvement_process_cycle_backend_service.md`
- `specs/interface/refactor_product_detail_view.md`
- `specs/interface/halilit_api_fetching_machine_status.md`

---

## Glossary (Ubiquitous Language)

All agents must use these terms exactly. Never substitute synonyms.

| Term | Definition |
|---|---|
| **Golden List** | The authoritative set of products Halilit.com sells. Owned by the Commercial source. If a product is not on the Golden List, it does not exist in this system. |
| **Verified Accessory** | A related product confirmed as compatible via the Relationship Graph (`02_relationship_logic.md`). Must show a green "Verified" badge in the UI. |
| **Alternative** | A product that can replace another (same category, different brand/model). Confirmed via the Relationship Graph. |
| **JIT Intelligence** | On-demand enrichment streamed via SSE for a single product. Generated by `jit_agent.py`. Never stored as ground truth — supplementary only. |
| **Sourcing Badge** | A UI indicator on every spec value showing which of the Three Sources provided it (Commercial / Official / Contextual). |
| **Call for Price (CfP)** | A product where `price === null`. Must display a "Call for Price" label + Copy SKU button instead of a price. |
| **The Artifact** | The compiled frontend (`frontend/dist/`) or the normalized catalog JSON. Always generated — never hand-edited. |
| **Skeleton** | A loading placeholder rendered within 200 ms while catalog data is in flight. Required for every view. |
| **The Spine** | This file (`specs/strategy/master_plan.md`). Injected into the Chief on every cycle. |
| **The Librarian** | The Chief Agent's role: reads the Spine, routes Builders to the exact Chapters needed. |
| **Task Force** | A 3-round Steerer → Builder → Watchdog cycle for cross-domain features requiring an API contract. |
| **Three Source Rules** | The fundamental law in `backend/source_rules.py`. Commercial owns prices/SKUs. Official owns specs/media. Contextual owns reviews. No field may be set by a source that does not own it. |
