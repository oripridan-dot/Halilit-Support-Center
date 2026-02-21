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
