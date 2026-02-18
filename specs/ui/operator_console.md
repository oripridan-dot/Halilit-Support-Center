# Specification: Operator Console UI

## Core Philosophy
- No 3D, no animations, no "Discovery Mode".
- High density data grid.
- Instant search.

## Route: / (Dashboard)
- **Component:** `DashboardView`
- **Content:** 3 Cards (Inventory Count, Active Alerts, System Status).

## Route: /inventory (Master Grid)
- **Component:** `InventoryView`
- **Columns:** Image (Thumb), SKU, Name, Brand, Category, Price IL, Price Eilat.
- **Action:** Row click -> Navigate to `/product/:id`

## Route: /product/:id (Intelligence)
- **Component:** `ProductDetailView`
- **Layout:**
  - Top: Header with Prices (IL + Eilat) and Stock Status.
  - Left: Specs Table.
  - Right: "Ecosystem" (Accessory Grid).
