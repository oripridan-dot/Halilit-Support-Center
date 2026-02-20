```markdown
## 🧬 The AI Cell Paradigm (Level 7 Architecture)

The Halilit Dark Factory is not a static script or a collection of tools. It is a **self-sustaining digital organism** — an Autopoietic AI Cell capable of perceiving its environment, synthesizing new structure, defending its integrity, and evolving its own capabilities without continuous human intervention.

This paradigm is the governing philosophy for all Level 7 architecture decisions. Every agent, every daemon, and every pipeline stage maps to a specific organelle with a defined biological role.

### Organelle Map

| Organelle         | Biological Role                                             | Factory Implementation                                                                           |
| ----------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| **Nucleus**       | Executive control; holds intent and routes instructions     | `chief_agent.py`, `frontend_manager.py`, `data_manager.py`                                       |
| **DNA**           | Abstract, mathematical blueprint of the system              | `specs/genomes/*.yaml` — holographic specifications                                              |
| **Ribosomes**     | Read DNA and synthesize structural proteins                 | `ribosome.py`, `ast_patcher.py` — React code and Python scrapers                                 |
| **Immune System** | Isolates mutations; kills failures before they reach `main` | TDD State Machine, `watchdog_agent.py`, atomic `evo/` branches                                   |
| **Mitochondria**  | Autonomous energy supply; keeps the cell alive              | `heartbeat_daemon.py`, cron jobs — overnight catalog polling                                     |
| **Lysosomes**     | Waste disposal; prevents metabolic suffocation              | `janitor_agent.py` — clears `.backup` files, temp phenotypes, log overflow                       |
| **Stem Cells**    | Dynamic capability generation                               | On-demand agent synthesis — the cell writes new Python agents when encountering unknown problems |

### Core Survival Protocols

These three protocols are the system's mandate for performance, efficiency, and cost-effectiveness. Every agent must reason within these constraints.

#### Evolve (Self-Optimization)

The system must continuously profile its own bottlenecks and refactor them using the Mutation Engine. If a scraper pipeline takes 10 seconds, the Cell must mutate its own code (e.g., introduce `asyncio`) to reduce that to 2 seconds. Performance regression is treated as a failed immune response.

> **Trigger:** Any pipeline stage exceeding its latency SLA defined in the Master Plan. The Mutation Engine proposes a patch; the Watchdog validates it in an isolated `evo/` branch before merge.

#### Combine (Dynamic Task Forces)

Agents must form temporary, cross-domain clusters to execute complex intents. When the Chief recognises a mandate that spans multiple domains (e.g., "Build a UI for new Allen & Heath products"), it combines the Data Manager (scrape) and the Frontend Manager (render) into a synchronous, short-lived swarm. Agents dissolve back to standby the moment the mandate is satisfied.

> **Trigger:** Any intent requiring sequential output from two or more manager-level agents. The Chief schedules a Task Force with a scoped contract; no agent may exceed its contract scope.

#### Detach (Ephemeral Compute — Apoptosis)

To optimise API and infrastructure costs, heavy workloads must spin up isolated sub-routines and terminate immediately upon success. This is the factory's implementation of **programmed cell death**: the process is born with a single purpose, fulfils it, and dies. Zero wasted compute.

> **Trigger:** Any task requiring cloud GPU, large-batch scraping, or external API saturation. The Cell spins up the sub-routine (Docker container or cloud function), collects the output, then issues a hard terminate signal. The main cell returns to low-power standby.

### Mitosis (Liquid Scaling)

When a single cell cannot handle the workload (e.g., 15,000 new products ingested simultaneously), the Chief triggers **Mitosis**: it spins up N identical Docker containers, partitions the workload evenly, allows all cells to process in parallel, merges results into the master database, and terminates the clones. Scaling is liquid — proportional to demand, never wasteful.

---

## Overview

The Halilit Support Center application is a web-based platform designed for product information and support. It features a dashboard, inventory, and product detail views, with real-time data integration and a focus on providing accurate and up-to-date product information. The application leverages a backend API to serve data, powered by a data pipeline that includes scraping, normalization, and catalog generation. A "Dark Factory" is used to generate and maintain code.

## Frontend Views

- **DashboardView:** Renders a mission control view with product statistics and ingestion status. Uses the `/api/dashboard/stats` endpoint.
- **InventoryView:** Displays a list of inventory items. Allows filtering based on a search query.
- **ProductDetailView:** Shows detailed information for a specific product, including images, an ecosystem tab, and a JIT badge.

## Hooks & State

- **useConductorCatalog:** Fetches and manages product catalog data from the `/api/catalog` endpoint. Returns data, loading state, error, and a refetch function.
- **useJITIntelligence:** Retrieves real-time product intelligence data. Returns JIT product data.
- **useNavigationStore:** Manages application navigation state, including the current view, active product ID, search query, and a flag for the call-for-price filter. Returns state and methods for navigation.
- **useDebounceThrottle:** Debounces and throttles a function call.

## Backend API

- **`/api/dashboard/stats` (GET):** Returns dashboard statistics (total products, calls for price, top brands count, last ingestion run details).
- **`/api/catalog` (GET):** Endpoint for the product catalog.
- **`/` (GET):** Serves static frontend assets.
- **`/api/jit/product/{product_id}` (GET):** JIT Intelligence endpoint (streams live product research via Gemini).

## Data Pipeline

1.  **Scraper:** (Not directly visible in the provided code, but implied) Extracts product data from external sources.
2.  **Product Normalizer:** Processes and standardizes the scraped data to create a consistent product shape.
3.  **Catalog:** Stores and serves the normalized product data.
4.  **Frontend:** Displays the product data in the various views.

## Factory Agents

- **backend/factory/builder_agent.py:** Materializes code from a specification.
- **backend/factory/steerer_agent.py:** Identifies critical gaps in existing specs and generates new or updated specifications.
- **backend/factory/scribe_agent.py:** Regenerates documentation to reflect the current state of the application.
- **backend/factory/spec_writer.py:** Translates human intent into "Dark Factory" Markdown specifications.

## Key Conventions

- **Imports:** Uses absolute imports (e.g., `@/components/common/ImageWithFallback`).
- **Source Rules:** Enforced by `backend/source_rules.py`. All data must come from one of three authorized sources.
- **Tailwind:** (Implied, not explicitly shown)
```
