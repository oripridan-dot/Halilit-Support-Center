# Synthesis Directive — genome_product_explorer

## Target
Product Detail Page

## Fitness Goal
ZERO_CLICK_DISCOVERY

## Required States
- LOADING → `useState(true)` for initial load; `useEffect` to fetch data.  visual_hint → `animate-pulse bg-slate-700 rounded`
- ERROR → `useState(null)` for error object; conditional rendering. visual_hint → `border border-red-500 text-red-400 bg-red-900/10 rounded p-4`
- EMPTY → `useState(false)` or check data length; conditional rendering. visual_hint → `text-slate-400 italic text-center py-12`
- READY → `useState(false)` initially; set to true on data hydration. visual_hint → `opacity-100 transition-opacity duration-300`
- None → `useState(true)` initially if no product selected; conditional rendering. visual_hint → `Centered prompt: 'Select a product to begin' with CatalogIcon`
- JIT_COMPUTING → `useState(false)` initially; set to true when product selected, SSE initiated. visual_hint → `Animated gradient border pulse on the product card. Streaming text appears token-by-token.`
- RENDERED → `useState(false)`; set to true on successful SSE completion. visual_hint → `Source badges: COMMERCIAL (green), OFFICIAL (blue), CONTEXTUAL (amber)`
- RENDERED_PARTIAL → `useState(false)`; set to true on SSE timeout/error. visual_hint → `Greyed-out source badge with lock icon and tooltip: 'Source unavailable'`
- RELATED_OPEN → `useState(false)`; toggled by user action. visual_hint → `Side panel slides in from right, 320px width`

## Required Traits
- ColorPhenotype → Apply dark mode styles using design-tokens.css or a Tailwind plugin.
- AccessibilityPhenotype → Add `aria-labels` to interactive elements and ensure keyboard navigation.
- ErrorBoundaryPhenotype → Wrap the component in a `GlobalErrorBoundary` or use local `try/catch` blocks.
- EcosystemAwareness → Use a visual badge (e.g., "Verified") to flag Verified Accessories and Compatible Products.
- MemoryPhenotype → On unmount, cancel any pending SSE streams and release cached product data.
- SourceBadgePhenotype → Render data source badges with distinct colors: Commercial (green), Official (blue), Contextual (amber).
- StreamingPhenotype → Implement token-by-token streaming using Server-Sent Events (SSE).

## Phenotype Assertions (must ALL pass after build)
- JIT_COMPUTING state must show streaming text, not a spinner
- RENDERED_PARTIAL must clearly differentiate available vs unavailable sources
- SourceBadgePhenotype: all three badge types must be visually distinct
- STRICT_JIT: component must call cleanup on unmount to cancel SSE streams
- ZERO TOLERANCE: no synthetic/mock data in any render state

## Environment Contracts
- **Data Models:** Use the `IngestionProductDraft` data model from `backend/ingestion/data_models.py` as the primary data structure.
- **PricingTier, DisplayRole, DataSourceConfidence:** Use enums defined in `backend/ingestion/data_models.py`.
- **SourceProvenance, FieldLineage:** Utilize these models for data origin tracking.
- **MediaAsset:** Ensure proper rendering and handling of media assets.
- **DisplayProperties:** Adhere to defined display properties.
- **ProductSpecifications:** Display tech specs appropriately.

## Builder Instructions
1.  Implement state transitions using `useEffect` hooks and event handlers for user interactions (e.g., product selection, dock closing).
2.  Prioritize SSE streaming for `JIT_COMPUTING` and ensure proper cleanup on unmount within `MemoryPhenotype`.
3.  Utilize Tailwind CSS for styling based on the `hint` property of each state.
4.  Implement error handling using `ErrorBoundaryPhenotype` and render informative error messages.
5.  Ensure that `SourceBadgePhenotype` is implemented and badges are displayed in the `RENDERED` and `RENDERED_PARTIAL` states.
