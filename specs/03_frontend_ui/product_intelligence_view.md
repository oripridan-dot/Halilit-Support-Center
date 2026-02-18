# Spec: Product Intelligence View

## Identity
- **Component Path:** `frontend/src/components/views/ProductDetailView.tsx`
- **Data Source:** `/api/jit/product/{id}`

## Layout Requirements (Strict)
1. **Header Zone:**
   - Must display Product Name (H1, White).
   - Must display Brand Badge (Small, Blue/Grey).
   - Must display Price IL (Large) and Price Eilat (Small, Muted).
   - **Constraint:** If stock is 0, entire header background must have subtle red tint.

2. **Tabs Zone:**
   - **Tab 1: Ecosystem (Default)**
     - Content: Grid of `ProductRelations`.
     - Sorting: "Verified" (Green Badge) items MUST appear first.
   - **Tab 2: Specs**
     - Content: Key/Value table of technical data.
   - **Tab 3: Files**
     - Content: List of PDF/Manual links found.

## Interaction Scenarios
1. **User clicks "Copy Specs":** - System formats specs as text and copies to clipboard.
   - Show temporary "Copied" toast.
2. **User clicks an Accessory:**
   - Navigate to that accessory's Detail View (Recursion).

## Failure Modes
- If API returns 404 -> Show "Product Not Found" with "Back to Grid" button.
- If Image is missing -> Use `/placeholder.png`.
