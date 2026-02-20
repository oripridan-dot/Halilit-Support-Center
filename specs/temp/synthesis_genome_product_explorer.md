**Component:** frontend/src/components/views/ExplorerView.tsx

# Synthesis Directive — genome_product_explorer

## Target
`frontend/src/components/views/ExplorerView.tsx`

## Fitness Goal
ZERO_CLICK_DISCOVERY

## Required States
- `LOADING` → `useState(true)` for initial load; `animate-pulse bg-slate-700 rounded` applied to loading elements.
- `ERROR` → Conditional rendering of error message; `border border-red-500 text-red-400 bg-red-900/10 rounded p-4` styling.
- `EMPTY` → Conditional rendering of empty state; `text-slate-400 italic text-center py-12` styling.
- `READY` → Conditional rendering of primary content; `opacity-100 transition-opacity duration-300` applied to the content wrapper.
- `None` → `useState(true)` initially; Render "Select a product" prompt with `CatalogIcon`. Transition to `JIT_COMPUTING` on product selection.
- `JIT_COMPUTING` →  `useState(false)` initially, toggled on product selection; Animated gradient border pulse on product card (CSS animation).  Use SSE to stream text token-by-token. Transition to `RENDERED` on stream completion or `RENDERED_PARTIAL` on timeout (10s).
- `RENDERED` → `useState(false)`, toggled on SSE stream success; Render source badges with `COMMERCIAL` (green), `OFFICIAL` (blue), `CONTEXTUAL` (amber) styling.
- `RENDERED_PARTIAL` → `useState(false)`, toggled on SSE timeout; Render available sources normally, unavailable sources as greyed-out badges with a lock icon and "Source unavailable" tooltip.
- `RELATED_OPEN` → `useState(false)`, toggled by user action; Side panel slides in from right (320px width). Transition to `RENDERED` on dock close.

## Required Traits
- `ColorPhenotype: HSC_DARK_MODE` → Use slate/zinc palette from `design-tokens.css`.
- `AccessibilityPhenotype: True` → Implement `aria-labels` and keyboard navigation for all interactive elements.
- `ErrorBoundaryPhenotype: True` → Wrap the component in a `GlobalErrorBoundary` or use a local `try/catch`.
- `EcosystemAwareness: True` → Visually flag Verified Accessories and Compatible Products with a verified badge.
- `MemoryPhenotype: STRICT_JIT` → Destroy off-screen nodes and NEVER cache more than one product's JIT data.
- `SourceBadgePhenotype: ['COMMERCIAL', 'OFFICIAL', 'CONTEXTUAL']` → Implement distinct visual styles for each source badge: `COMMERCIAL` (green), `OFFICIAL` (blue), `CONTEXTUAL` (amber).
- `StreamingPhenotype: True` → Use SSE to stream JIT text token-by-token.

## Phenotype Assertions (must ALL pass after build)
- JIT_COMPUTING state must show streaming text, not a spinner
- RENDERED_PARTIAL must clearly differentiate available vs unavailable sources
- SourceBadgePhenotype: all three badge types must be visually distinct
- STRICT_JIT: component must call cleanup on unmount to cancel SSE streams
- ZERO TOLERANCE: no synthetic/mock data in any render state

## Environment Contracts
- `PricingTier`: enum (`ENTRY`, `MID`, `PRO`, `FLAGSHIP`, `LEGACY`) from `backend/ingestion/data_models.py`
- `DataSourceConfidence`: enum (`OFFICIAL`, `TRUSTED`, `COMMERCIAL`, `USER`, `INFERRED`) from `backend/ingestion/data_models.py`
- `IngestionProductDraft`:  BaseModel from `backend/ingestion/data_models.py` representing the product data structure.

## Builder Instructions
1. Prioritize implementing the state transitions correctly, especially the `JIT_COMPUTING` state and its transitions. Use `useEffect` to manage the SSE connection.
2. Implement STRICT_JIT by using `useEffect` with a cleanup function that cancels the SSE stream on component unmount. This is critical for performance.
3. Ensure the `SourceBadgePhenotype` badges are visually distinct and accessible (color contrast, `aria-label`).
4. The `RENDERED_PARTIAL` state requires careful handling of missing data sources. Ensure the locked badges are visually clear and provide informative tooltips.
5. Enforce ZERO TOLERANCE for synthetic data. The component must only render data received from the backend SSE stream.
