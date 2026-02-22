# Halilit Support Center — Workflow (v9.7.6 · Level 6)

> The Factory Owner defines intent via specs. The swarm executes, self-heals, self-disrupts.

---

## The Three Roles

| Role | Responsibilities |
|------|-----------------|
| **Factory Owner** (you) | Write / update specs. Review outcomes. Set priorities. |
| **Chief Agent** | Translates intent → delegation queue → assigns tasks to agents. |
| **Tech Lead Agent** | Pre-flight gate. APPROVEs or VETOs every Builder output (Bicameral Governance). |

---

## The Daily Workflow

### 1. Orient

```bash
python factory.py status          # Environment health check
cat HEARTBEAT.md                  # Nightly system self-report
cat DAILY_BRIEFING.md             # Tech Lead nightly briefing
python factory.py chief-plan      # Chief: prioritised task queue
```

### 2. Define Intent (Spec First)

Before writing any code, check for a relevant spec:

```
specs/interface/
  01_operator_dashboard.md   # Dashboard view
  02_inventory_grid.md       # InventoryView
  03_product_intelligence.md # ProductDetailView
  04_natural_explorer_ux.md  # Natural Explorer pattern
```

If no spec exists → generate one:

```bash
python factory.py design "New feature description" [category]
# Writes spec to specs/interface/<slug>.md
```

### 3. Build → Verify → Fix

```bash
python factory.py build specs/interface/02_inventory_grid.md
# Builder materialises code; Tech Lead pre-flight reviews; Patch Agent applies.
```

Open the app and verify against **Behavior Scenarios** in the spec.

If it fails → amend the spec → re-run build. **Never fix code by hand when the spec can be clarified.**

### 4. Heal Errors

```bash
python factory.py heal            # Watchdog: scan errors, auto-repair (3 cycles)
python factory.py diagnose        # Scan only, no changes
```

### 5. Commit

```bash
python factory.py commit          # Stage all + semantic git commit
```

---

## Nexus — Interactive Console

For multi-step queries or real-time Chief → Swarm dialogue:

```bash
python nexus.py
> run sonar
> consult product_manager
> run darwin "backend pagination bottleneck"
> build specs/interface/03_product_intelligence.md
```

---

## Views (Operator Console)

| View | Route | Key Purpose |
|------|-------|-------------|
| **Dashboard** | `/` or `/dashboard` | Metrics, ingestion status, quick links |
| **Inventory** | `/inventory` | Searchable product grid, sort, filter, pagination |
| **ProductDetail** | `/product/:id` | JIT intelligence cockpit per product |

> Old names **"Mission Control"** and **"Inventory Master"** are deprecated. Use the names above.

---

## Key Commands (factory.py)

| Command | Purpose |
|---------|---------|
| `python factory.py start` | Launch backend (8000) + frontend (5173) |
| `python factory.py status` | Environment health: API key, venv, agent presence |
| `python factory.py design "desc" [cat]` | Architect: generate a spec |
| `python factory.py build <spec_path>` | Builder: materialise spec → code |
| `python factory.py darwin "hypothesis"` | Darwin: architectural mutation in Shadow Cell |
| `python factory.py heal` | Watchdog: auto-repair errors (up to 3 cycles) |
| `python factory.py diagnose` | Scan TypeScript/Python errors, no changes |
| `python factory.py commit` | Stage all + semantic commit |
| `python factory.py chief-plan` | Chief: prioritised task queue |

---

## Spec Is Law

- If code conflicts with `specs/interface/` or `OPERATOR_CONSOLE_SPEC.md`, the **code is wrong**.
- Do not infer business logic — read it from `specs/data_pipeline/`.
- Do not write code without a spec.
- Do not fix code by hand when the spec can be clarified instead.

---

## Three Source Rules (Non-Negotiable)

| Source | Owns |
|--------|------|
| Commercial (Halilit.com) | Prices, SKUs, stock |
| Official (brand pages) | Titles, specs, media, docs |
| Contextual (3+ review sites) | Reviews, pros/cons, ratings |

Empty fields > synthetic fields. See `backend/source_rules.py`.

---

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
