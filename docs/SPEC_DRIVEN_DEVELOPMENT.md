# Spec-Driven Development (v9.7.6 · Level 6)

> The spec is law. Code is just the implementation of a spec.

---

## The Workflow

```
1. Write (or update) the spec
2. Prompt the Builder: "Read <spec>. Implement <component>."
3. Tech Lead reviews output (APPROVE / VETO / REVISE)
4. Patch applied
5. Verify in browser against Behavior Scenarios in spec
6. If failing → amend spec → repeat from step 2
```

**Never fix code by hand. Never write code without a spec. If the spec is wrong, fix the spec.**

---

## Where Specs Live

| Folder | Contains |
|--------|---------|
| `specs/interface/` | UI specs (Dashboard, Inventory, ProductDetail, Explorer) |
| `specs/data_pipeline/` | Ingestion rules, relationship logic, enrichment |
| `specs/behavior/` | Playwright / E2E scenarios |
| `specs/01_data/` | Compliance, halilit_api, official_scout |
| `specs/strategy/` | Master plan, evolution proposals |
| `specs/pricing_logic.md` | Pricing decision rules |
| `specs/archive/` | Superseded specs — read-only |
| `OPERATOR_CONSOLE_SPEC.md` | Root-level behavior and compliance spec |

---

## Canonical UI Specs (specs/interface/)

| File | View |
|------|------|
| `01_operator_dashboard.md` | Dashboard |
| `02_inventory_grid.md` | InventoryView |
| `03_product_intelligence.md` | ProductDetailView |
| `04_natural_explorer_ux.md` | Natural Explorer pattern |

**Views have specific names. Use them exactly:**

| Correct | Deprecated (do not use) |
|---------|------------------------|
| Dashboard | Mission Control |
| Inventory / InventoryView | Inventory Master |
| ProductDetail / ProductDetailView | Product Cockpit, Arena |

---

## Generating a Spec (Architect Agent)

```bash
python factory.py design "Debounced search with trie index" search
# → writes specs/interface/debounced_search_with_trie_index.md
```

Or in Nexus:
```
> design "Add price history chart to ProductDetail"
```

---

## Building from a Spec (Builder Agent)

```bash
python factory.py build specs/interface/02_inventory_grid.md
```

Or in Nexus:
```
> build specs/interface/03_product_intelligence.md
```

The Tech Lead will pre-flight the output before the Patch Agent applies it.

---

## Example Prompt Templates

### Rewrite a view

```
Read specs/interface/02_inventory_grid.md.
Rewrite frontend/src/components/views/InventoryView.tsx to fully satisfy the spec.
Do not invent logic not in the spec.
```

### Fix a backend endpoint

```
Read specs/data_pipeline/pagination.md.
Rewrite backend/server.py GET /api/conductor/catalog to enforce backend pagination as specified.
```

### Heal + commit

```
Run heal cycle then commit.
```

---

## Behavior Scenarios

Every spec must include a `## Behavior Scenarios` or `## Scenes` section. These are the acceptance criteria.

Example (from `02_inventory_grid.md`):
```
Scene: Empty search
  Given the search input is empty
  Then all products are shown (paginated)

Scene: Search with no results
  Given the user types "xyzzy"
  Then an empty-state message is shown ("No products found")
  And the CFP filter is not applied
```

**After building, manually verify each scene in the browser.**

---

## Spec Quality Rules

1. **Authoritative fields only** — only specify fields that have an owner in source_rules.py.
2. **Concrete not aspirational** — "The image tag has `alt=product.title`" not "Images should be accessible".
3. **One spec per component** — do not combine Dashboard and Inventory in one spec.
4. **Behavior before styling** — define what happens before how it looks.
5. **No synthetic data in spec examples** — use real SKUs or placeholder tokens.
