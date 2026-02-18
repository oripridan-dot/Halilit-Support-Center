# Halilit Support Center — Documentation

This folder is the **single source** for how we build and run the Operator Console. The old "fix" and "verification" docs have been removed; workflow is now **spec-driven** and **outcome-based**.

---

## Documentation Index

| Document | Purpose |
|----------|---------|
| **[QUICK_START.md](QUICK_START.md)** | Run the app: one command, first-time setup, optional catalog rebuild. |
| **[WORKFLOW.md](WORKFLOW.md)** | The new way of working: Factory Owner, Level 5, specs as source of truth. |
| **[SPEC_DRIVEN_DEVELOPMENT.md](SPEC_DRIVEN_DEVELOPMENT.md)** | How to write specs, prompt the AI Builder, and verify outcomes. |
| **[FACTORY_PIPELINE.md](FACTORY_PIPELINE.md)** | Factory scripts, Conductor commands, data validation, re-scrape. |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System layers, API, Operator Console views (no Galaxy/Spectrum). |
| **[MEMORY_MANAGEMENT.md](MEMORY_MANAGEMENT.md)** | Backend memory limits, catalog cache behavior, monitoring. |

---

## Specs (Source of Truth)

Interface and behavior are defined in **Markdown specs**, not in ad-hoc tickets:

- **Root:** [OPERATOR_CONSOLE_SPEC.md](../OPERATOR_CONSOLE_SPEC.md) — What the console must do; compliance rules.
- **Specs folder:** [specs/](../specs/) — Data pipeline, interface, and behavior specs.
  - `specs/interface/` — Dashboard, Inventory Grid, Product Intelligence.
  - `specs/data_pipeline/` — Ingestion rules, relationship logic.
  - `specs/behavior/` — Search and navigation scenarios (for tests).

You **edit specs** when requirements change; you **prompt the AI** to produce code that satisfies them. You **approve outcomes**, not diffs.
