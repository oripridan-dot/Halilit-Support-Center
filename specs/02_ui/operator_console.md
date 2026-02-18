# Specification: Operator Console Layout

## Goal
A high-density, low-latency interface for inventory management and support.

## Visual Language
- **Theme:** "Dark Factory" (Zinc-950 background, Zinc-800 borders).
- **Accent:** Blue-600 (Primary Actions), Emerald-500 (Verified Data).
- **Typography:** Inter/Sans (UI), JetBrains Mono (Pricing/SKUs).

## Views
1. **Inventory Master (Default)**
   - Component: `InventoryView`
   - Behavior: Infinite scroll or virtualized list.
   - Key Data: Image, Name, SKU, Brand, Category, Price (IL), Price (Eilat).
   - Interaction: Click row -> Open Product Detail.

2. **Product Intelligence**
   - Component: `ProductDetailView`
   - Header: Large price display, Stock indicator.
   - Tabs:
     - "Ecosystem": Grid of Accessories/Compatibles.
     - "Specs": Key-Value table.
     - "Intelligence": AI-generated sales pitch.

## Navigation
- **Sidebar:** Persistent left rail (64px collapsed / 240px expanded).
- **Global Search:** Always visible in header (Command+K).
