# Repository Instructions & Context (v9.5 — Openclaw)

## ⚠️ THE FUNDAMENTAL LAW — Three Source Rules (backend/source_rules.py)

**These rules are the FOUNDATION of the entire application. Without them, the app has NO VALUE.**

### The Three Authorized Data Sources

| #   | Source         | Owner   | Owns                                                                 |
| --- | -------------- | ------ | -------------------------------------------------------------------- |
| 1   | **Commercial** | Halilit | Golden List, prices (IL+Eilat), SKUs, product existence              |
| 2   | **Official**   | Brand   | Titles, descriptions, specs, media, documentation (official product page) |
| 3   | **Contextual** | Reviews | Pros/cons, real-world experience, ratings (3+ trusted review sites)   |

### Zero Tolerance Policy

- **NO synthesized/generated data** — empty fields are BETTER than fake fields
- **NO mock data** in any pipeline stage
- **NO AI-generated specs** presented as real specs
- **NO AI-generated reviews** presented as real reviews
- **NO fallback to simulated data** — if a source fails, the product stays incomplete
- Each source has **strict field ownership** — only the owner can set its fields
- **Cross-validation**: confidence benefits from multiple sources agreeing

**See `backend/source_rules.py` for enforcement.**

---

## Project Overview

**Halilit Support Center v9.5 (Openclaw)** — JIT product intelligence platform for musical instruments.

- **Architecture**: JIT (Just-in-Time) — skeleton or full catalog + on-demand Gemini 2.0 Flash intelligence. Product graph: families and relationships in priority order (official → commercial → contextual → spectrum).
- **Frontend**: React 18 + Vite + TypeScript + Zustand + React Query + Tailwind CSS. Views: GalaxyDashboard, SpectrumModule, ProductPage.
- **Backend**: Python 3.11+ + FastAPI + Pydantic v2 + google-genai (Gemini 2.0 Flash). No Celery/Trinity; ingestion via Conductor CLI (commercial-ingest, enrich, sync, rebuild-catalog).
- **Repo strategy**: Lean — generated data (brand JSONs, graph snapshot, search indexes) is gitignored. Only source code and static assets are tracked.

---

## Running the System

```bash
# From project root, with venv activated
PYTHONPATH=. python backend/conductor_main.py dev
# → Backend http://localhost:8000, Frontend http://localhost:5173 (or next free port)

# Or separately:
PYTHONPATH=. python backend/server.py    # Backend only
cd frontend && pnpm dev                  # Frontend only
```

---

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, google-genai SDK, Pydantic v2, Pillow
- **Frontend**: React 18, TypeScript 5, Vite 5, Zustand 5, React Query 5, Tailwind CSS 3.4, Framer Motion
- **Catalog**: Built by `product_normalizer.build_catalog()` from `frontend/public/data/*.json`
- **Graph**: ProductGraph (families, relationships); persisted to `backend/data/graph/product_graph.json`

---

## File Structure (v9.5)

```
backend/
├── source_rules.py           # ⚠️ THE LAW — Three Source Rules (read first!)
├── server.py                 # FastAPI: catalog, JIT, MCP
├── conductor_main.py         # CLI: skeleton-sync, commercial-ingest, enrich, ingest-all, sync, rebuild-catalog, catalog, dev, server
├── product_normalizer.py     # build_catalog(), graph pipeline
├── product_graph.py          # ProductGraph, families, relationships
├── product_graph_store.py    # JSON snapshot (+ optional PostgreSQL)
├── jit_agent.py              # On-demand product intelligence (SSE)
├── unified_data_service.py    # Sync engine, search artifacts
├── api/                      # mcp_router
├── ingestion/                # halilit_page_scraper, relationship_*, taxonomy, data_models
├── mcp/                      # MCP servers (catalog_db, ui_bridge, …)
├── scripts/                  # full_rescrape, enrich_catalog, generate_search_index, …
├── config/                   # init_db.sql, mcp_servers.json
└── data/                     # graph/, ingestion/ (gitignored)

frontend/
├── src/
│   ├── App.tsx               # Router: Galaxy, Spectrum, ProductPage
│   ├── components/views/     # GalaxyDashboard, SpectrumModule, ProductPage
│   ├── hooks/                # useConductorCatalog, useJITIntelligence
│   ├── store/                # navigationStore
│   └── types/
├── public/data/              # Brand JSONs, index (generated)
└── vite.config.ts            # Proxy to backend :8000
```

---

## Code Standards

### Frontend (React/TypeScript)

- **Types**: Import from `types/index.ts` (canonical; generated from backend when applicable).
- **State**: Zustand for app state, React Query for server state (catalog).
- **Styling**: Tailwind CSS; dark theme (e.g. slate-900, blue-500).
- **Components**: Functional components with hooks only (class only for ErrorBoundary).
- **Data**: All product data from `/api/conductor/catalog` (useConductorCatalog).
- **NEVER** leave a file empty or &lt; 100 bytes.

### Backend (Python)

- **Data models**: Pydantic v2 (e.g. IngestionProductDraft, ProductRelationship).
- **Imports**: Use `backend.` prefix for internal imports (e.g. `from backend.product_normalizer import build_catalog`).
- **Gemini**: Use `google.genai`, model `gemini-2.0-flash` (or current default in jit_agent).
- **Catalog**: Built by `build_catalog(frontend_public_data_dir)`; includes product graph pipeline (official → commercial → contextual → spectrum).

### Key Principles

- **THE LAW**: Three Source Rules in `backend/source_rules.py` govern ALL data — read it first.
- **Commercial** = Halilit.com only → Golden List, prices, SKUs (IMMUTABLE for price).
- **Official** = Brand official pages only → specs, descriptions, media, docs.
- **Contextual** = 3+ trusted review sites → real reviews, pros/cons.
- **ZERO TOLERANCE** for synthetic/mock/AI-generated data presented as real.
- Catalog API returns normalized products with images (hero+gallery), descriptions, specs, quality scores, graph indexes.
- JIT intelligence is streamed per product (SSE); 7-day file cache.
- Generated data is gitignored — only source code and static assets are tracked.

---

**v9.5.0 — Openclaw** · February 2026
