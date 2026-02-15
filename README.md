# Halilit Support Center v9.2

**JIT (Just-in-Time) product intelligence platform** for musical instruments.  
Skeleton catalog + full ingestion pipeline (commercial → enrich → sync → graph) + on-demand AI intelligence via Gemini 2.0 Flash.

**6k+ products** | **Product graph** (families, relationships: official → commercial → contextual → spectrum) | **Design Arena & Curation**

---

## Quick Start

```bash
# Prerequisites: Python 3.11+, Node.js 18+; optional: GOOGLE_API_KEY for JIT

# Install
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cd frontend && (pnpm install || npm install) && cd ..

# Run both servers (recommended)
PYTHONPATH=. python backend/conductor_main.py dev
# → Backend http://localhost:8000 · Frontend http://localhost:5173 (or next free port)

# Or run separately: Terminal 1 — PYTHONPATH=. python backend/server.py
#                   Terminal 2 — cd frontend && pnpm dev
```

### Populate catalog

```bash
source .venv/bin/activate
PYTHONPATH=. python backend/conductor_main.py skeleton-sync        # Fast (~30s)
PYTHONPATH=. python backend/conductor_main.py ingest-all           # Full: commercial → enrich → sync → graph
PYTHONPATH=. python backend/conductor_main.py rebuild-catalog      # Rebuild catalog + graph (brand hierarchy + discovery + purge)
PYTHONPATH=. python backend/conductor_main.py purge-graph         # One-off: remove weak relationships from persisted graph
```

---

## Architecture (v9.2)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  FRONTEND (React 18 + Vite + Zustand + React Query + Tailwind)          │
│  Views: GalaxyDashboard · SpectrumModule · ProductPage · Curation ·     │
│         DesignArena   Data: useConductorCatalog()                        │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │ REST / SSE
┌──────────────────────────────▼──────────────────────────────────────────┐
│  API (FastAPI — port 8000)                                              │
│  /api/conductor/*  Catalog, taxonomy, filter, refresh                   │
│  /api/jit/product/{id}  SSE stream (JIT intelligence)                  │
│  /api/curation/*   Relationships, families, pending review             │
│  /api/mcp/*        MCP tools (catalog, design_director, ui_bridge)      │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│  DATA LAYER                                                              │
│  · frontend/public/data/*.json  (brand product files, generated)         │
│  · product_normalizer.build_catalog()  → indexes, health, graph         │
│  · backend/data/graph/product_graph.json  (families + relationships)     │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│  INGESTION (Conductor CLI)                                               │
│  commercial-ingest → full_rescrape (Golden List from Halilit sitemap)   │
│  enrich → Halilit product pages (description, images, features)         │
│  sync → Rebuild index + artifacts                                       │
│  rebuild-catalog → build_catalog() + graph (relationship priority)      │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│  RELATIONSHIP GRAPH (priority order)                                    │
│  1. Official   — Brand page “accessories/related” + text                │
│  2. Commercial — Variant families + accessory links (catalog)            │
│  3. Contextual — Reviews: “works with X”                                │
│  4. Spectrum   — Same spectrum/tier alternatives (cross-brand)           │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│  JIT AGENT (on-demand, per product)                                     │
│  Trigger: user opens product. Streams: snap → intel → wisdom → explore   │
│  Tools: read_halilit_page, search_trusted_reviews. Cache: 7-day TTL      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Main application flow

1. **Galaxy** — Category tiles (galaxies/spectrums) with product counts.
2. **Spectrum** — Subcategory product grid (filter by brand, price).
3. **Product page** — Full detail; JIT stream fills specs, verdict, pros/cons when opened.
4. **Curation** — Review/confirm AI-discovered relationships.
5. **Design Arena** — Galaxy/Spectrum variant experiments.

All views use **useConductorCatalog()** (React Query); catalog is built once per server start (or on refresh) and includes product graph indexes.

---

## System overview

| Layer        | Technology / Location |
| ------------ | --------------------- |
| **Frontend** | React 18, TypeScript, Vite 5, Zustand, React Query, Tailwind, Framer Motion |
| **Backend**  | Python 3.11+, FastAPI, Pydantic v2, google-genai (Gemini 2.0 Flash) |
| **Catalog**  | build_catalog() in product_normalizer.py; reads frontend/public/data/*.json |
| **Graph**    | ProductGraph (product_graph.py), GraphStore (JSON snapshot + optional PostgreSQL) |
| **Ingestion**| Conductor CLI → full_rescrape, enrich_catalog, sync, rebuild-catalog |
| **JIT**      | jit_agent.py; SSE stream per product; file-based cache |

---

## Project structure

```
backend/
├── server.py              # FastAPI: catalog, JIT, curation, MCP, static
├── conductor_main.py      # CLI: skeleton-sync, commercial-ingest, enrich, ingest-all, sync, rebuild-catalog, catalog, dev, server
├── product_normalizer.py  # build_catalog(), normalize_product(), graph pipeline
├── product_graph.py       # ProductGraph, CanonicalProduct, ProductRelationship, families
├── product_graph_store.py # JSON snapshot + optional PostgreSQL
├── jit_agent.py           # On-demand product intelligence (SSE)
├── unified_data_service.py # Sync engine, search artifacts, index metadata
├── source_rules.py        # Three Source Rules (Commercial / Official / Contextual)
├── api/                   # curation_router, mcp_router
├── ingestion/             # halilit_page_scraper, relationship_*, taxonomy, data_models
├── mcp/                   # MCP servers (catalog_db, design_director, ui_bridge, …)
├── scripts/               # full_rescrape, enrich_catalog, generate_search_index, …
├── config/                # init_db.sql, mcp_servers.json
└── data/                  # graph/, ingestion/ (gitignored)

frontend/
├── src/
│   ├── App.tsx            # Router: Galaxy, Spectrum, ProductPage, Curation, DesignArena
│   ├── components/views/  # GalaxyDashboard, SpectrumModule, ProductPage, CurationDashboard, DesignArena
│   ├── hooks/             # useConductorCatalog, useJITIntelligence
│   ├── store/             # navigationStore
│   └── types/
├── public/data/           # Brand JSONs, index.json, search_index_min.json (generated)
└── vite.config.ts         # Proxy to backend :8000
```

---

## CLI (Conductor)

| Command           | Description |
| ----------------- | ----------- |
| `skeleton-sync`   | Fast inventory from Halilit.com (~30s) |
| `commercial-ingest` | Golden List (sitemap + optional page scrape) |
| `enrich`          | Enrich from Halilit product pages (delay, merge-dupes) |
| `ingest-all`      | Full pipeline: commercial-ingest → enrich → sync → rebuild-catalog |
| `sync`            | Rebuild frontend data and search index from brand JSONs |
| `rebuild-catalog` | Rebuild catalog and product graph (official→commercial→contextual→spectrum) |
| `catalog`         | Print catalog stats |
| `dev`             | Start backend + frontend |
| `server`          | API server only |

---

## API (summary)

| Area        | Path / method | Description |
| ----------- | ------------- | ----------- |
| Catalog     | GET `/api/conductor/catalog` | Full catalog (products, indexes, metadata, graph_stats) |
| Taxonomy    | GET `/api/conductor/taxonomy` | Category/brand schema |
| Refresh     | GET `/api/conductor/refresh` | Force catalog cache rebuild |
| JIT         | POST `/api/jit/product/{id}` | SSE stream of product intelligence |
| Curation    | GET/POST/DELETE `/api/curation/*` | Relationships, pending, confirm, reject |
| MCP         | POST `/api/mcp/*` | MCP tools |
| Health      | GET `/api/health` | Service health |

---

## Documentation

| Document | Purpose |
| -------- | -------- |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design, source rules, API reference |
| [START-HERE.md](START-HERE.md) | Open app in browser, first-time install |
| [WHAT-TO-DO.md](WHAT-TO-DO.md) | Get app running (v9.2), env, sync, ingest |
| [IMPLEMENTATION-COMPLETE.md](IMPLEMENTATION-COMPLETE.md) | Feature checklist, run/verify steps |
| [backend/ingestion/README.md](backend/ingestion/README.md) | Ingestion pipeline, relationship priority |

---

## Changelog

### v9.2 (February 2026)

- **Version**: Bumped to 9.2.0 across backend and docs.
- **Ingestion**: Full pipeline documented: commercial → enrich → sync → rebuild-catalog; relationship priority (official → commercial → contextual → spectrum).
- **CLI**: Added `rebuild-catalog` to rebuild catalog and product graph without re-scraping.
- **Docs**: README, ARCHITECTURE, WHAT-TO-DO, START-HERE, IMPLEMENTATION-COMPLETE, and copilot-instructions aligned to v9.2; removed obsolete Celery/Trinity/7-phase references.
- **Cleanup**: Removed one-time branch-cleanup doc; repo trimmed for current JIT + graph architecture.

### v9.1 / v9.0

- JIT architecture; product graph (families, relationships); Design Arena; Curation dashboard.

---

**v9.2.0** · Last updated: February 2026
