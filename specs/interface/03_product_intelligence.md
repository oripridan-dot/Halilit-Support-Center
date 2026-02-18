# Product Intelligence View Specification

## Goal
Provide the operator with immediate commercial and technical context to close a sale or solve a support ticket.

## Data Requirements
- Input: `activeProductId` (String)
- Source: `useJITIntelligence` hook via `/api/jit/product/{id}`

## Layout Structure (Vertical Hierarchy)
1. **Header Card:**
   - Left: Hero Image (Contain fit, white bg).
   - Center: Title, SKU, Brand Badge (Clickable to filter inventory).
   - Right: Pricing Block (Big IL Price, Small Eilat Price).
   - **CRITICAL:** Show "Stock Status" indicator here.

2. **Action Toolbar (Sticky):**
   - Button: "Copy Tech Specs" (Clipboard).
   - Button: "Generate Quote PDF" (Mock function).
   - Button: "Open Official Page" (External Link).

3. **Intelligence Tabs:**
   - **Tab A: Ecosystem (Default):**
     - Display `ProductRelations` component.
     - Split into "Verified Accessories" (Green Badge) and "Alternatives".
   - **Tab B: Specifications:**
     - Key/Value table of `official_specs`.
   - **Tab C: History:**
     - Placeholder for past tickets.

## Behavior Scenarios
- **Scenario:** Loading Data
  - Outcome: Show Skeleton loader matching layout.
- **Scenario:** Product Not Found
  - Outcome: Show "404 Product" screen with "Back to Search" button.
- **Scenario:** No Relations Found
  - Outcome: Show empty state in Ecosystem tab "No verified accessories in graph."
