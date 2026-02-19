# Operator Console Specification

## Purpose
This document is the **Source of Truth** for what the Halilit Support Center Operator Console must do. The codebase is the **Artifact** produced to satisfy this spec. We approve outcomes, not code.

## High-Level Workflows

1. **Mission Control (Dashboard)** — Operator sees key metrics and quick links. See `specs/interface/01_operator_dashboard.md`.
2. **Inventory Master** — Operator filters, sorts, searches products; clicks a row to open Product Detail. See `specs/interface/02_inventory_grid.md`.
3. **Product Intelligence (Detail View)** — Operator sees product header (image, title, SKU, brand, pricing, stock), action toolbar, and tabs (Ecosystem, Specifications, History). See `specs/interface/03_product_intelligence.md`.

## Product Detail View Behavior (Critical Path)

- **Trigger:** User clicks a row in Inventory or selects a result in Global Search.
- **Navigation:** App shows Product Detail view with `activeProductId` set.
- **Data:** View loads JIT data from `/api/jit/product/{id}`.
- **Layout:** Header card (image, title, SKU, brand badge, pricing, stock) → Sticky action toolbar → Tabs: Ecosystem (default), Specifications, History.
- **Ecosystem tab:** "Verified Accessories" (green badge) and "Alternatives". Empty state if no relations: "No verified accessories in graph."
- **Outcomes to verify (no debugging code):**
  - Tabs load.
  - JIT runs (data fetched).
  - Verified badges appear when the catalog has verified relationships.
  - 404 product → "404 Product" screen with "Back to Search".
  - Loading → Skeleton matching layout.

## Data Pipeline

- Catalog and relationships come from the Conductor. Artifact: `backend/data/learned_taxonomy.json` (or `catalog_cache.json.gz` after prebuild).
- Pricing rules: `specs/pricing_logic.md`.
- Relationship rules and golden scenarios: `specs/data_pipeline/02_relationship_logic.md`, `backend/tests/golden_scenarios.json`.

## Out of Scope (Frozen / Removed)

- Galaxy, Spectrum, Arena, and any "game" or visual-OS views.
- Static frontend catalog files (`catalog.json`, `skeleton.json`) — data comes from API.
- V0 components and 3D assets — removed from factory floor.

## Compliance

- **Interface:** Build must satisfy `specs/interface/*.md`.
- **Behavior:** Build must satisfy `specs/behavior/01_search_scenarios.md` (manual or Playwright).
- **Data:** Build must pass golden scenarios in `backend/tests/golden_scenarios.json` when validating the catalog artifact.

## Level 5 Workflow

1. **You** update a spec (e.g. `specs/interface/02_inventory_grid.md`).
2. **You** prompt: "Read the spec. Rewrite [component] to satisfy the spec. Produce the code artifact."
3. **You** verify the outcome in the app (e.g. row turns red when stock is 0). If it fails, fix the spec and re-prompt; do not debug the code by hand.
