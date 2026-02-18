# Spec-Driven Development

How to write specs and use them to drive the AI Builder. No code review—only outcome verification.

---

## Where Specs Live

| Path | Purpose |
|------|---------|
| `OPERATOR_CONSOLE_SPEC.md` | Overall console behavior; Product Detail; compliance. |
| `specs/pricing_logic.md` | Price missing → "Call for Price"; sort order; Eilat rules. |
| `specs/data_pipeline/01_ingestion_rules.md` | Scraping, normalization, artifacts. |
| `specs/data_pipeline/02_relationship_logic.md` | Accessories, verified vs inferred; golden scenarios. |
| `specs/interface/01_operator_dashboard.md` | Mission Control layout and metrics. |
| `specs/interface/02_inventory_grid.md` | Grid columns, filters, sort, row click → Detail. |
| `specs/interface/03_product_intelligence.md` | Product Detail: header, toolbar, tabs, loading/404. |
| `specs/behavior/01_search_scenarios.md` | Search and navigation outcomes (for tests). |

---

## How to Write a Spec

- **Goal** — One sentence: what this artifact must achieve.
- **Data requirements** — Inputs, API or hook, schema if needed.
- **Layout / structure** — Order of sections, key components (no pixel-perfect mockups unless necessary).
- **Behavior scenarios** — "Scenario: X. Outcome: Y." Be specific enough that pass/fail is unambiguous.

**Example (from pricing_logic):**

```markdown
### Scenario: Product has no IL price
- **Outcome:** Item must be flagged as "Call for Price".
- **Outcome:** Item must sink to bottom of sort order (when sorting by price).
- **Outcome:** Eilat price must be calculated as 0 (or hidden).
```

**Bad:** "If price is missing, use 0." (vague; no sort order, no flag.)  
**Good:** The three outcomes above.

---

## Standard Prompts (Level 5)

### 1. Rewrite a component from a spec

> I have updated `specs/interface/02_inventory_grid.md`.  
> **Role:** You are the Factory Builder.  
> **Task:** Read the spec. Read `frontend/src/components/views/InventoryView.tsx`.  
> **Action:** Rewrite the component code to strictly satisfy the spec. Do not ask clarifying questions. Produce the code artifact.

### 2. Generate a new component from a spec

> I have created `specs/interface/03_product_intelligence.md` which describes the Product Detail view.  
> **Role:** You are the Factory Builder.  
> **Task:** Read the spec.  
> **Action:** Generate the full React component `ProductDetailView.tsx` that satisfies the spec. Do not explain the code. Output the file.

### 3. Verify behavior with scenarios

> Here is `specs/behavior/01_search_scenarios.md`. It contains 5 user stories (e.g. "User searches for SKU → Exact match opens Detail View").  
> **Task:** Write a Playwright test suite that verifies these 5 scenarios against the current build.

### 4. Compliance report (data only)

> Analyze `backend/data/learned_taxonomy.json` (or the current catalog artifact) against `backend/tests/golden_scenarios.json`.  
> **Do not show me code.** Output a **Compliance Report**: which brands failed to group correctly, which prices are missing. I will approve the data, not the script.

---

## When the Outcome Is Wrong

1. **Do not** start debugging the generated code.
2. **Do** check the spec: Is the scenario clear? Is the outcome testable?
3. **Refine the spec** — e.g. add "red = Tailwind class `bg-red-900/20`" so the Builder has no ambiguity.
4. **Re-prompt** with the same template; get a new artifact.
5. **Verify again** in the app or via scenarios.

If the same failure happens twice, the spec is still ambiguous—tighten it and try again.
