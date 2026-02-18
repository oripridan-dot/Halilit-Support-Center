# Relationship Logic Specification

## Goal
Define rules for product relationships: Accessories, Compatible, Bundles, Alternatives. The pipeline must not "guess" in an unconstrained way—outcomes are validated by golden scenarios.

## Relationship Types
- **Accessory:** Officially recommended/sold-together (e.g., Roland KSC-70 for Roland FP-30X).
- **Compatible:** Works with; may be third-party or inferred.
- **Bundle:** Sold as a set.
- **Alternative:** Competing or similar product.

## Rules
- **Verified:** Only relationships that appear in official brand data or golden set get "Verified" badge.
- **Inferred:** AI- or rule-inferred relationships must be labeled as "Alternatives" or unverified; never as "Verified Accessories".
- **Cardinality:** Max N accessories per product (e.g., 20) to avoid UI noise.

## Golden Scenarios (Validation)
- Stored in `backend/tests/golden_scenarios.json`.
- Example: "Roland FP-30X MUST have Roland KSC-70 as an accessory."
- **Pipeline Rule:** If the factory build does not satisfy all golden scenarios, the build fails.
- We do not care *how* the code works—only that the artifact passes the scenario check.

## Outcomes
- **Scenario:** No official data for a product.
  - **Outcome:** "Verified Accessories" section empty. "Alternatives" may be populated from rules.
- **Scenario:** Golden scenario missing in artifact.
  - **Outcome:** Build fails. Compliance report lists missing scenario.
