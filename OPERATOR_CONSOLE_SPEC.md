# Operator Console Specification (v9.7.6 · Level 6)

## Purpose

This document is the **Source of Truth** for what the Halilit Support Center Operator Console must do. The codebase is the **Artifact** produced to satisfy this spec. We approve outcomes, not code.

---

## Views (Three)

| # | View | File | Spec |
|---|------|------|------|
| 1 | **Dashboard** | `DashboardView.tsx` | `specs/interface/01_operator_dashboard.md` |
| 2 | **Inventory** | `InventoryView.tsx` | `specs/interface/02_inventory_grid.md` |
| 3 | **ProductDetail** | `ProductDetailView.tsx` | `specs/interface/03_product_intelligence.md` |

> **Deprecated names (do not use):** "Mission Control", "Inventory Master", "Arena", "Galaxy", "Spectrum".

---

## High-Level Workflows

1. **Dashboard** — Operator sees key metrics, ingestion status, and quick links.
2. **Inventory** — Operator filters, sorts, searches products; clicks a row to open ProductDetail.
3. **ProductDetail** — Operator sees product header (image, title, SKU, brand, pricing, stock), action toolbar, and cockpit tabs (Ecosystem, Specifications, History, JIT Intelligence).

---

## Dashboard Behavior

- KPI tiles: total products, brands, enriched count, stale count.
- Ingestion status panel: last run timestamp, source health indicator.
- Quick links: → Inventory, → search specific SKU, → run JIT for top-priority product.

---

## Inventory Behavior

- Searchable product grid with **debounced search** (300 ms).
- Sort by: name, brand, price (IL), price (Eilat), stock.
- Filter by: brand, CFP (Commercial/Full/Partial) status.
- Pagination: backend-driven (50 per page by default).
- Row click → navigate to ProductDetail.
- Low-stock rows highlight (stock = 0 → red; stock ≤ 3 → amber).
- Empty state: "No products found" with search reset button.

---

## ProductDetail Behavior (Critical Path)

**Trigger:** User clicks a row in Inventory or selects a result in Global Search.

**Navigation:** App shows ProductDetail with `activeProductId` set in `navigationStore`.

**Data:** View loads JIT stream from `/api/jit/product/{id}` (SSE).

**Layout:** Header card (hero image, title, SKU, brand badge, pricing, stock) → Sticky action toolbar → Tabs:
- **Ecosystem** (default): Verified Accessories (green badge), Alternatives. Empty state: "No verified accessories in graph."
- **Specifications**: Product specs table from Official source.
- **History**: Price and stock history chart.
- **JIT Intelligence**: Streaming AI analysis (Active Sonar + JIT Agent).

**Verified outcomes (acceptance criteria):**
- Tabs load without error.
- JIT stream starts within 1 s of view mount.
- Verified badges appear when catalog has verified relationships.
- 404 product → "Product not found" screen with "Back to Inventory" button.
- Loading state → skeleton layout matching final layout.

---

## Data Pipeline

- Catalog and relationships come from the Conductor.
- Cached at `backend/data/catalog_cache.json.gz` (24 h TTL, auto-rebuilt nightly).
- Pricing rules: `specs/pricing_logic.md`.
- Relationship rules: `specs/data_pipeline/02_relationship_logic.md`.
- Golden scenarios: `backend/tests/golden_scenarios.json`.
- Deep health check: `GET /api/health/deep`.

---

## Out of Scope (Frozen / Removed)

- Galaxy, Spectrum, Arena, and any "game" or visual-OS views.
- Static frontend catalog files (`catalog.json`, `skeleton.json`) — data comes from API only.
- V0 components and 3D assets.
- Any synthetic, mock, or AI-generated product data presented as real.

---

## Compliance

- **Interface:** Build must satisfy `specs/interface/*.md`.
- **Behavior:** Build must satisfy `specs/behavior/01_search_scenarios.md` (manual or Playwright).
- **Data:** Build must pass golden scenarios in `backend/tests/golden_scenarios.json`.
- **Three Source Rules:** Every data field must come from its authorised source. See `backend/source_rules.py`.

---

## Level 6 Delivery Workflow

1. **You** update or create a spec in `specs/interface/`.
2. **You** run: `python factory.py build specs/interface/<spec>.md`
3. **Tech Lead** pre-flight reviews the Builder output (APPROVE / VETO / REVISE).
4. **Patch Agent** applies on APPROVE.
5. **You** verify outcomes against Behavior Scenarios in the spec.
6. If it fails → fix the spec → re-run build. Do not debug code by hand.

---

## Agent Capabilities (v9.7.6)

| Agent | What it can do for the console |
|-------|-------------------------------|
| Chief v4.2 | Translates "add X to ProductDetail" into spec + build + verify tasks |
| Builder | Materialises any spec into TypeScript components |
| Tech Lead | Blocks spec-violating code before it reaches the repo |
| Darwin Agent | Proposes architectural improvements (e.g. pagination strategy) in isolation |
| Active Sonar | Synthetic E2E checks on Dashboard, Inventory, ProductDetail health |
| Telemetry Agent | Auto-drafts HOTFIX_PROPOSAL on frontend crash reports |
