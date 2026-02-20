# Synthesis Directive — genome_product_explorer

## Target
Product Detail Page

## Fitness Goal
ZERO_CLICK_DISCOVERY

## Required States
- LOADING → `useState(true)` for initial load; `animate-pulse bg-slate-700 rounded`
- ERROR → `useState(null)` for error message; conditional render; `border border-red-500 text-red-400 bg-red-900/10 rounded p-4`
- EMPTY → `useState(false)` initially; conditional render if data is empty; `text-slate-400 italic text-center py-12`
- READY → `useState(false)` initially; `opacity-100 transition-opacity duration-300`; useEffect trigger on data arrival
- None → `useState(true)` initially, becomes false when a product is selected; Centered prompt: 'Select a product to begin' with CatalogIcon
- JIT_COMPUTING → `useState(false)` initially; `useEffect` trigger on product selection starts SSE; animated gradient border pulse on the product card. Streaming text appears token-by-token.
- RENDERED → `useState(false)` initially, set to true when SSE completes; Source badges: COMMERCIAL (green), OFFICIAL (blue), CONTEXTUAL (amber)
- RENDERED_PARTIAL → `useState(false)` initially, becomes true when SSE times out or has network error; Greyed-out source badge with lock icon and tooltip: 'Source unavailable'
- RELATED_OPEN → `useState(false)` initially; Side panel slides in from right, 320px width

## Required Traits
- ColorPhenotype → Apply dark mode slate/zinc palette from `design-tokens.css`.
- AccessibilityPhenotype → Implement `aria-labels` on interactive elements and ensure keyboard navigation.
- ErrorBoundaryPhenotype → Wrap the component in a `GlobalErrorBoundary`.
- EcosystemAwareness → Visually flag Verified Accessories and Compatible Products with a verified badge.
- MemoryPhenotype → Implement strict JIT memory management. Destroy off-screen nodes. Never cache more than one product's JIT data.
- SourceBadgePhenotype → Render distinct colored badges for each data source: Commercial (green), Official (blue), Contextual (amber).
- StreamingPhenotype → Implement token-by-token JIT text streaming using SSE.

## Phenotype Assertions (must ALL pass after build)
- JIT_COMPUTING state must show streaming text, not a spinner
- RENDERED_PARTIAL must clearly differentiate available vs unavailable sources
- SourceBadgePhenotype: all three badge types must be visually distinct
- STRICT_JIT: component must call cleanup on unmount to cancel SSE streams
- ZERO TOLERANCE: no synthetic/mock data in any render state

## Environment Contracts
- `data_models.py`: Models for product data, including `IngestionProductDraft`, `PricingData`, `MediaAsset`, `SourceProvenance`.
- `DataSourceConfidence`: Enum for data source confidence (OFFICIAL, TRUSTED, COMMERCIAL, USER, INFERRED).
- `PricingTier`: Enum for pricing tiers (ENTRY, MID, PRO, FLAGSHIP, LEGACY).
- SSE stream:  Assume a standard Server-Sent Events stream that delivers text tokens.

## Builder Instructions
1. Implement state transitions using `useEffect` hooks and event handlers. Ensure each state renders the correct UI elements as described in the STATE hints.
2. Prioritize correct badge implementation. Use the `SourceBadgePhenotype` trait to render distinct badges based on `DataSourceConfidence` from the ingested data.  Use Tailwind classes to produce the specified colors.
3. Implement memory management via `MemoryPhenotype` using `useEffect` with a return cleanup function. The cleanup MUST cancel the SSE stream on unmount.
4. Implement `EcosystemAwareness` by adding verified badges to verified accessories and compatible products.  Assume the product data contains a `verified` boolean field on related products.
5. Do not mock any data. Use real data flowing through the data models defined in `data_models.py`.
