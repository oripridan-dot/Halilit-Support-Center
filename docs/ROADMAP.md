# 🗺️ Halilit Support Center Roadmap

> Managed by the Product Manager Agent. Last updated: 2026-02-21.
> **Usage:** Ask the PM "What's next?" — it reads this file and pitches the top priority.

---

## 🚀 Short-Term (Current Sprint)

- [ ] **Task 0 (Blocker):** TooLoo Workflow Alignment Refactor — execute spec `specs/interface/tooloo_workflow_alignment.md` before any feature sprint proceeds. Removes Git-Mind violations, relocates `local_autonomy/`, consolidates `docs/`, enforces branch protection.
- [ ] **Task 1:** Resolve Client-Side Data Crash — remove any remaining large JSON payloads served directly to the browser; implement backend pagination on `/api/conductor/catalog`.
- [ ] **Task 2:** Refactor ProductDetailView UI to modern Tailwind standards (flex-col layout, design-system tokens) without breaking JIT intelligence hooks.
- [ ] **Task 3:** Wire Backend Search API — replace local frontend array filtering with a proper `/api/search?q=` REST endpoint backed by the catalog index.
- [ ] **Task 4:** Strengthen Image Pipeline — expose `fast_pass_image_check` metrics in the operator dashboard so the team can monitor skip-rate vs. deep-check rate.
- [ ] **Task 5:** Spec-Driven Test Coverage — add Vitest / Playwright scenario files for InventoryView and GlobalSearch covering the "Empty State" and "Error Boundary" branches.

---

## 🔭 Long-Term (Epics)

- [ ] **Epic 1:** Omni-Channel ChatOps — connect Swarm to Telegram / Slack via Webhooks so the Operator can dispatch tasks from mobile.
- [ ] **Epic 2:** Cloud Compute Mitosis — spin up Dockerized scraper workers dynamically for large brand catalogs (100+ SKUs) without blocking the main pipeline.
- [ ] **Epic 3:** Graph Neural Network Recommendations — accessory suggestion engine based on ProductGraph topological data (families + relationships).
- [ ] **Epic 4:** Multi-Tenant Operator Console — role-based access (Admin / Viewer) with JWT auth so the console can be shared with the commercial team.
- [ ] **Epic 5:** Autonomous Nightly Enrichment — schedule the JIT Oracle to pre-warm intelligence for the top 50 products every night, reducing day-0 latency for operators.

---

## ✅ Completed

- [x] Installed Wolverine Self-Healing Protocol (Watchdog Agent).
- [x] Installed JIT Oracle Lifeline (cold-boot Oracle for trapped Swarms).
- [x] Implemented Bicameral Governance — Tech Lead pre-flight veto gate wired into Chief Agent.
- [x] Fast-Pass Image Heuristic — 2-stage HEAD / deep validation pipeline (99% I/O reduction).
- [x] Level 8 Liquid MCP Core — `apply_udiff_patch`, `execute_bash_command`, `git_isolate_workspace`, `git_merge_workspace`, `run_frontend_tests`, `consult_oracle` tools.
- [x] Genetic Feedback Loop — Mutation Engine + Fitness Ledger tracking agent performance.
- [x] Spec-driven V0 Design integration (`factory_v0_design` MCP tool).
- [x] Product Manager Backlog Engine — `read_roadmap` / `update_roadmap` MCP tools + PM Agent.
