# Pricing Logic Specification

## Goal
Define deterministic rules for product pricing display and sort order. The operator must never see ambiguous or wrong prices.

## Scenarios & Outcomes

### Scenario: Product has no IL price
- **Outcome:** Item must be flagged as "Call for Price".
- **Outcome:** Item must sink to bottom of sort order (when sorting by price).
- **Outcome:** Eilat price must be calculated as 0 (or hidden).

### Scenario: Product has IL price but no Eilat price
- **Outcome:** Eilat price must be derived from IL price using VAT rules (Eilat 0% or reduced rate).
- **Outcome:** Display both IL and Eilat in pricing block.

### Scenario: Product has both IL and Eilat prices
- **Outcome:** Display both. No derivation needed.
- **Outcome:** Stock status and badges apply regardless.

### Scenario: Price is null or invalid (negative, non-numeric)
- **Outcome:** Treat as "Call for Price".
- **Outcome:** Sink to bottom of sort order.

## VAT Rules (Reference)
- IL: Standard VAT rate as configured.
- Eilat: Reduced/zero rate as per Israeli law. Calculation must be in `pricing_engine` or equivalent.

## Validation (Golden)
- Any artifact (catalog, grid data) that violates the above must fail compliance.
- Compliance report must list: "Products missing price", "Products with invalid price".
