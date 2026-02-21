# Halilit Support Center — Documentation (v9.7.6)

This folder is the **single source of truth** for how we build and run the Operator Console. The workflow is **spec-driven** and **outcome-based**. Read these before touching any code.

---

## Documentation Index

| Document | Purpose |
|----------|---------|
| **[QUICK_START.md](QUICK_START.md)** | Run the app: one command, first-time setup. |
| **[WORKFLOW.md](WORKFLOW.md)** | Level 6 workflow: Factory Owner, specs as law, autonomous self-healing. |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System layers, API, views, agent roster, Darwin Protocol, Three Source Rules. |
| **[SPEC_DRIVEN_DEVELOPMENT.md](SPEC_DRIVEN_DEVELOPMENT.md)** | How to write specs, prompt the Builder, verify outcomes. |
| **[FACTORY_PIPELINE.md](FACTORY_PIPELINE.md)** | `factory.py` commands, Conductor pipeline, Nexus console. |
| **[MEMORY_MANAGEMENT.md](MEMORY_MANAGEMENT.md)** | Backend memory limits, catalog cache behavior, monitoring. |
| **[ROADMAP.md](ROADMAP.md)** | Product Manager backlog — current sprint tasks and long-term epics. |
| **[LEARNED_GUIDELINES.md](LEARNED_GUIDELINES.md)** | Persistent agent memory — accumulated lessons from self-healing cycles. |

---

## Specs (Source of Truth)

Behavior is defined in **Markdown specs**, not in tickets:

- **Root:** [OPERATOR_CONSOLE_SPEC.md](../OPERATOR_CONSOLE_SPEC.md) — What the console must do; compliance rules.
- **Canonical UI specs:** `specs/interface/01_*` through `04_*` — Dashboard, Inventory, ProductDetail, Natural Explorer.
- **Data pipeline specs:** `specs/data_pipeline/` — Ingestion rules, relationship logic.
- **Behavior:** `specs/behavior/01_search_scenarios.md` — Playwright/E2E test scenarios.
- **Archive:** `specs/archive/` — Superseded specs (read-only reference).

---

## Key Principles (Level 6)

- **The Law:** `backend/source_rules.py` — Three Source Rules govern ALL data. Read before touching any pipeline code.
- **Spec is Law:** Edit specs when requirements change; the Builder materialises code. Never bypass the spec.
- **Never fake data:** Empty fields are better than synthetic/AI-generated product data.
- **Factory CLI:** `python factory.py <cmd>` — unified lifecycle entry point.
- **Autonomous healing:** Run `python factory.py heal` — Watchdog auto-repairs TypeScript/Python errors.
- **Darwin Protocol:** `python factory.py darwin "hypothesis"` — safe architectural experiments in isolation.
- **Bicameral Governance:** Tech Lead APPROVE/VETO gate on every Builder output.
