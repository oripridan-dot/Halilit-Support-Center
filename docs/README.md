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
- **Specs folder:** [specs/](../specs/) — Blueprints (inputs); code is the artifact (output).
  - **Factory floor:** `specs/01_data_ingestion/`, `specs/02_backend_logic/`, `specs/03_frontend_ui/`, `specs/04_end_to_end_scenarios/`.
  - Legacy layout: `specs/interface/`, `specs/data_pipeline/`, `specs/behavior/`, `specs/pricing_logic.md`.
- **Factory Supervisor:** `backend/factory_supervisor.py` — Compliance check, optional `--rebuild`, UI build. See [FACTORY_PIPELINE.md](FACTORY_PIPELINE.md).

You **edit specs** when requirements change; the AI **implements** them (Dark Factory Protocol in `.cursorrules`). You **approve outcomes**, not diffs.
