# Architecture — Halilit Support Center v9.7.1 (Chief)

> **Last updated:** 2026-02-20  
> **Branch:** v9.7.0 → merging to `main` as v9.7.1

---

## Overview

Halilit Support Center is a JIT (Just-in-Time) product intelligence platform for musical instrument inventory. The UI is a React/TypeScript "Operator Console" served by a FastAPI backend and a real-time Gemini-driven intelligence pipeline.

Architecture pattern: **Spec-Driven Dark Factory** — markdown specs in `specs/` are the sole source of intent; agents materialise them into code. No code is written without a spec.

---

## Repository Layout (v9.7.1 — clean)

\`\`\`
Halilit-Support-Center/
├── backend/                     # Python 3.11+ FastAPI server + pipeline
│   ├── server.py                # FastAPI routes: catalog, JIT, MCP
│   ├── conductor_main.py        # CLI: dev, skeleton-sync, rebuild, enrich, server
│   ├── product_normalizer.py    # build_catalog() → normalized products + graph
│   ├── product_graph.py         # ProductGraph: families, relationships
│   ├── product_graph_store.py   # JSON snapshot persistence
│   ├── jit_agent.py             # SSE-streamed live product intelligence (Gemini)
│   ├── unified_data_service.py  # Brand sync engine
│   ├── source_rules.py          # ⚠️ THE LAW — Three Source Rules (read first!)
│   ├── factory/                 # AI agents: builder, chief, scribe, watchdog, etc.
│   ├── ingestion/               # Scrapers, data_models, relationship discovery
│   ├── hierarchy/               # Product hierarchy: models, service, API, validation
│   ├── mcp/                     # MCP servers (catalog_db, ui_bridge, web_search, …)
│   ├── api/                     # mcp_router (FastAPI)
│   ├── scripts/                 # One-shot ops: enrich, scrape, index, inspect
│   ├── services/                # improvement_cycle, product_image_validation
│   ├── config/                  # init_db.sql, mcp_servers.json
│   └── data/                    # graph/, ingestion/, jit_cache/ (gitignored)
│
├── frontend/                    # React 18 + Vite + TypeScript
│   └── src/
│       ├── App.tsx              # Shell: sidebar + 3-view router
│       ├── components/
│       │   ├── views/           # DashboardView, InventoryView, ProductDetailView, IngestionStatusView
│       │   ├── cockpit/         # ProductRelations, VerdictCard, TrustedConsensus, FieldNotes, ExplorationDock
│       │   ├── ProductDetail/   # EcosystemTab, JITBadge, ProductImageCarousel, SourcingBadge
│       │   ├── GlobalSearch.tsx
│       │   ├── ImageWithFallback.tsx
│       │   ├── ProductImage.tsx
│       │   ├── ProductTile.tsx
│       │   └── ui/              # GlobalErrorBoundary
│       ├── hooks/               # useConductorCatalog, useJITIntelligence, useDebounce[Value], useImageRefresh, useValidateHeroImage
│       ├── store/               # navigationStore (Zustand)
│       ├── lib/                 # brandLogoHelper, categoryConsolidator, smartTags, universalCategories, …
│       ├── styles/              # brandThemes, design-tokens
│       └── types/               # index.ts (canonical), generated.ts, componentUtils.ts
│
├── specs/
│   ├── interface/               # ← CANONICAL UI SPECS (34 files as of v9.7.1)
│   │   ├── 01_operator_dashboard.md
│   │   ├── 02_inventory_grid.md
│   │   └── 03_product_intelligence.md  ← primary three; rest are feature specs
│   ├── data_pipeline/           # Ingestion rules, relationship logic
│   ├── behavior/                # Playwright test scenarios
│   ├── 01_data/                 # Data compliance, halilit_api, official_scout
│   └── strategy/                # master_plan.md
│
├── docs/                        # Developer documentation
├── nexus.py                     # Nexus Swarm Console — parallel agent orchestrator
├── factory.py                   # Master Factory Controller CLI
├── OPERATOR_CONSOLE_SPEC.md     # Master spec — operators approve outcomes not code
└── CHANGELOG.md
\`\`\`

**Removed in v9.7.1 (cleanup):**
- Root `src/` directory — 8 orphaned components never connected to the Vite build
- Root `services/` — exact duplicate of `backend/catalog_organizer.py`
- `start_console.sh` — legacy startup script superseded by `factory.py start`
- `backend/scripts/archive/` — 3 archived one-off scripts
- 10 duplicate spec files (shorter dash-named variants superseded by fuller named equivalents)

---

## Frontend Views

| View | State Key | Purpose |
|---|---|---|
| `DashboardView` | `DASHBOARD` | Metrics: total products, CFP items, top brands, last ingestion |
| `InventoryView` | `INVENTORY` | Filterable/searchable product grid with stock & CFP indicators |
| `ProductDetailView` | `PRODUCT_DETAIL` | Full product card: image, sourcing badges, JIT badge, tabs (Ecosystem, Specs, History) |
| `IngestionStatusView` | `INGESTION_STATUS` | Live pipeline ingestion progress |

---

## Hooks

| Hook | Purpose |
|---|---|
| `useConductorCatalog` | Fetches `/api/conductor/catalog` (React Query) |
| `useJITIntelligence` | SSE-streams live Gemini intelligence per product |
| `useDebounce` / `useDebounceValue` | Debounces search inputs (≤150ms per SLA) |
| `useImageRefresh` | Triggers hero image re-validation |
| `useValidateHeroImage` | Validates hero image URL liveness |

---

## Backend API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/conductor/catalog` | Full normalized product catalog |
| GET | `/api/health` | Service health check |
| GET | `/api/jit/{product_id}` (SSE) | Live product intelligence stream |
| GET/POST | `/api/hierarchy/*` | Product hierarchy management |
| `*` | `/mcp/*` | MCP tool bridge |

---

## Data Pipeline (Three Source Rules)

All product data flows through `backend/source_rules.py`. Three authorized sources only:

1. **Commercial** (Halilit.com) → Golden List, prices (IL + Eilat), SKUs
2. **Official** (Brand pages) → Titles, descriptions, specs, media
3. **Contextual** (3+ trusted review sites) → Pros/cons, ratings, real-world use

**Zero tolerance for synthetic/mock/AI-generated data presented as real.**

Pipeline stages: `skeleton-sync` → `commercial-ingest` → `official-enrich` → `contextual-enrich` → `catalog-build` → `graph-build`.

---

## Factory Agents (`backend/factory/`)

| Agent | File | Role |
|---|---|---|
| Builder | `builder_agent.py` | Materialises specs → code |
| Chief | `chief_agent.py` | Strategic planner, produces task queue for Nexus |
| Watchdog | `watchdog_agent.py` | Scans & auto-repairs compilation errors (up to 3 cycles) |
| Scribe | `scribe_agent.py` | Regenerates ARCHITECTURE.md and docs |
| Steerer | `steerer_agent.py` | Identifies spec gaps, generates new/updated specs |
| Optimizer | `optimizer_agent.py` | Refactors source files for readability & typing |
| Repo Agent | `repo_agent.py` | Semantic git commits + changelog |
| Reflect | `reflect_agent.py` | Records lessons to `docs/LEARNED_GUIDELINES.md` |
| UI Validator | `ui_validator_agent.py` | Vite build + import verification |
| V0 Agent | `v0_agent.py` | Generates v0.dev-ready UI prompts |

---

## Nexus Swarm Console (`nexus.py`)

Orchestrates agents in **parallel batches** separated by **sequential barriers**. Pre-flight validation guards prevent dispatching `optimize` tasks to non-existent files (anti-hallucination, added v9.7.1).

Chief outputs a JSON task queue → Nexus executes it using `ThreadPoolExecutor` for parallel tasks and sequential barriers for `commit`, `heal`, `build`, `doc`.

---

## Key Conventions

- **Imports**: `lucide-react` for icons; `@tanstack/react-query` for server state; `zustand` for app state
- **Styling**: Tailwind CSS, dark theme (slate-900, blue-500 palette)
- **Types**: Always import from `frontend/src/types/index.ts` (canonical)
- **No empty files**: Every file must be ≥100 bytes
- **Spec first**: Never write code without a spec in `specs/`
