# Spec: Inventory Grid Component
**Target:** frontend/src/components/views/InventoryView.tsx

## Requirements
- Use `useConductorCatalog` hook to fetch data.
- Display a table with columns: Image, Name, Brand, Price IL, Price Eilat.
- If Price IL is 0 or missing, display "Call for Price" in yellow text.
- Include a search input at the top that filters the `product_name`.
