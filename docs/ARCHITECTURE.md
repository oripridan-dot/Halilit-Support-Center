## Overview

The Halilit Support Center is a web application designed as a data-forward console for managing product information and inventory. It features a dark, dense user interface inspired by Vercel and Linear, with a focus on providing power-user tools for product management and real-time intelligence.

## Frontend Views

- **DashboardView**: `/` or `DASHBOARD` state. Displays key statistics about products, calls, brands, and ingestion status. Uses data fetched from `/api/dashboard/stats`.
- **InventoryView**: `/inventory` or `INVENTORY` state. A dense data table for viewing and managing product inventory. Uses data fetched via `useConductorCatalog`.
- **ProductDetailView**: `/product/:id` or `PRODUCT_DETAIL` state. Shows detailed information about a single product, including pricing, stock, and related information. Uses `useConductorCatalog` and `useProductRelationships`.

## Hooks & State

- `useDashboardStats`: Fetches dashboard statistics from `/api/dashboard/stats`. Returns an object of type `DashboardStats`.
- `useConductorCatalog`: Fetches product catalog data from `/api/conductor/catalog`. Returns an array of `ConductorProduct` (type not shown).
- `useJITIntelligence`: Manages the JIT (Just-In-Time) intelligence process. Returns data of type `VerdictData`, `ReviewSource`, `FieldNotesData`, and `ExplorationPath`.
- `useDebounceValue`: (From `InventoryView.tsx`) Debounces a value.
- `navigationStore`: (`src/store/navigationStore.ts`) A `zustand` store managing the application's navigation state.
  - `currentView`: `DASHBOARD`, `INVENTORY`, `PRODUCT_DETAIL`, `INGESTION_STATUS`, or `EXPLORER`.
  - `activeProductId`: `string | null`.
  - `searchQuery`: `string | null`.
  - `initialCfpFilter`: `boolean | null`.

## Backend API

- `/api/dashboard/stats` (GET): Returns dashboard statistics.
- `/api/conductor/catalog` (GET): Returns product catalog data.
- `/` (serves static frontend assets)
- `/api/jit/product/{product_id}` (GET): Returns JIT intelligence data for a product.

## Data Pipeline

1.  A scraper (not shown in the code) collects product data.
2.  `product_normalizer.py` normalizes product data into a consistent format.
3.  The normalized data is used to build a catalog.
4.  The frontend fetches data from the `/api/conductor/catalog` endpoint and `/api/dashboard/stats`.

## Factory Agents

- `steerer_agent.py`: Identifies critical gaps in the product specs and generates/updates them.
- `scribe_agent.py`: Regenerates documentation to reflect the current codebase.
- `spec_writer.py`: Translates human intent into detailed Markdown specifications.
- `builder_agent.py`: Materializes code from a specification.
- `chief_agent.py`: Orchestrates the swarm — delegates to builder, optimizer, watchdog, and Bio-Swarm tools.
- `tech_lead_agent.py`: Validates output quality before promotion.

## Bio-Swarm — Algorithmic Biology (v9.7.2)

### Genome Specs (`specs/genomes/`)

DNA-like YAML files defining component fitness. Each genome has:

- **States** — FSM nodes with `visual_hint`, `required`, and `transitions`
- **Traits** — typed, inheritable behavioural traits (e.g. `SourceBadgePhenotype`, `StreamingPhenotype`)
- **Phenotype_Assertions** — testable correctness properties verified by the Ribosome
- **`extends`** — inherits from a parent genome (e.g. `base_cell`)

### Ribosome (`backend/factory/ribosome.py`)

Genome Interpreter Engine:

1. Loads and resolves genome YAML (inheritance, env context)
2. Calls LLM to fold genome into a **Synthesis Directive** (`specs/temp/synthesis_genome_*.md`)
3. Runs **PhenotypeVerifier** — LLM checks all assertions against real code; VIABLE ≥ 80/100

### Mutation Engine (`backend/factory/mutation_engine.py`)

Genetic Feedback Loop — OODA cycle:

- **Observe**: scans `factory_logs/` for agent execution records
- **Orient**: scores agents 0–1 (`FitnessLedger` at `backend/data/genome/fitness_ledger.json`)
- **Decide**: agents below `MUTATION_THRESHOLD=0.65` get micro-heuristic injections
- **Act**: appends evolved rules to `docs/LEARNED_GUIDELINES.md`

### OODA Integration

`nexus.py` captures `_SESSION_START_TS` at boot and calls `_run_ooda_mutation_cycle()` after every successful swarm batch, creating a continuous improvement feedback loop.

## Key Conventions

- **Imports**: Uses `lucide-react` for icons.
- **Naming**: Uses `PascalCase` for React components.
- **Tailwind**: Uses Tailwind CSS classes extensively.
- **Source Rules**: Enforced by `backend/source_rules.py`. Data must come from authorized sources, with no data synthesis.
