# Halilit Support Center — Application Architecture

## The Level 5 Autonomous Factory Loop (v9.7.0)

1. **The Blackboard (Task Force):** Cross-domain features share a localized markdown file (`specs/temp/task_force_X.md`) for agents to collaborate on API contracts.
2. **Ephemeral Sandboxes:** The Supervisor spins up isolated Docker containers. Code is compiled and tested *before* it is returned to the user.
3. **Multi-Modal Verification:** Playwright tests are executed, and the Watchdog agent reviews DOM state and screenshots via Gemini 2.0 Flash vision tools.
4. **Auto-Rollback:** `repo_agent.py` branches before execution and automatically reverts if the improvement cycle fails to produce passing code within 5 rounds.
5. **Persistent Memory:** The Reflect Agent appends root causes of healed failures to `docs/LEARNED_GUIDELINES.md`. Every subsequent agent call receives this file injected into its context automatically via `get_project_context()`.

---

## Overview

The Halilit Support Center is a JIT product intelligence platform for musical instruments. It features a Dashboard, Inventory grid, and Product Detail view. The application uses a FastAPI backend and a React + TypeScript frontend. The backend includes a JIT intelligence engine (SSE streaming), a Dark Factory agent suite for autonomous development, and a Conductor CLI for the data pipeline.

## Frontend Views

- **DashboardView**: Dashboard statistics — total products, calls for price, top brands, last ingestion status.
- **InventoryView**: Filterable product grid with out-of-stock and unconfirmed visual cues.
- **ProductDetailView**: Full product cockpit — specs, media gallery, JIT intelligence stream, product relations.
- **IngestionStatusView**: Live ingestion run telemetry.

## Hooks & State

- **useConductorCatalog**: Fetches the product catalog from `/api/conductor/catalog` via React Query.
- **useJITIntelligence**: Manages JIT phases (`idle → snap → intel → wisdom → complete`); returns `signal_chain` and `cheat_sheet` for the cockpit UI.
- **navigationStore** (Zustand): App-wide navigation state — current view, active product ID, search query, call-for-price filter.

## Backend API

- `GET /api/conductor/catalog` — Serves the normalized product catalog.
- `GET /api/jit/{product_id}` — SSE stream for JIT product intelligence.
- `GET /api/hierarchy/*` — Product hierarchy endpoints.
- `POST /api/cycles/*` — Improvement Cycle lifecycle (start, advance, stream via SSE).

## Data Pipeline

1. **Commercial Ingest** (`halilit_page_scraper`): Pulls Golden List, prices, SKUs from Halilit.com.
2. **Product Normalizer** (`product_normalizer.py`): Transforms raw data → canonical `Product` shape; runs the graph pipeline (official → commercial → contextual → spectrum).
3. **ProductGraph** (`product_graph.py`): Families, relationships, spectrum IDs.
4. **JIT Agent** (`jit_agent.py`): On-demand intelligence via Gemini 2.0 Flash; 7-day file cache.

## Factory Agents

- **chief_agent.py**: The Supervisor — accepts plain-English commands, outputs a parallel task queue.
- **builder_agent.py**: Materializes code from a specification file.
- **steerer_agent.py**: Identifies spec gaps; generates or updates specs.
- **watchdog_agent.py**: Reviews code/DOM against spec; multi-modal (screenshot + Gemini vision).
- **reflect_agent.py**: Appends root-cause lessons to `docs/LEARNED_GUIDELINES.md`.
- **scribe_agent.py**: Regenerates documentation from the live codebase.
- **repo_agent.py**: Git operations (branch, commit, rollback).
- **sandbox_executor.py**: Compiles and tests code in an ephemeral environment before promotion.

## Key Conventions

- **Source Rules** (`backend/source_rules.py`): All data from Commercial, Official, or Contextual sources only. Zero tolerance for synthetic data.
- **Spec is Law**: No code is written without a corresponding spec in `specs/interface/` or `specs/data_pipeline/`.
- **Types**: Canonical frontend types in `frontend/src/types/index.ts`.
- **Styling**: Tailwind CSS dark theme — `slate-900`, `blue-500`, design tokens in `frontend/src/styles/design-tokens.css`.
