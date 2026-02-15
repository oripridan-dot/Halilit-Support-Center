# Halilit Support Center — Architecture

**Version**: 9.2.0 (JIT + Product Graph)  
**Updated**: February 2026

---

## System overview

AI-powered product intelligence platform using a **Just-in-Time (JIT)** architecture. A lightweight skeleton or full catalog (from Halilit ingestion) is enriched with a **product graph** (families, relationships in priority order). Live intelligence is streamed on demand per product via Gemini 2.0 Flash.

| Metric            | Value |
| ----------------- | ----- |
| Catalog           | Built from `frontend/public/data/*.json` (commercial + enrich) |
| Product graph     | Families + relationships (official → commercial → contextual → spectrum) |
| Intelligence      | JIT — live per-product research via Gemini 2.0 |
| Trusted sources   | Golden Circle (Sound On Sound, Sweetwater, Thomann, …) |
| Cache             | Catalog: 5 min server TTL; JIT: 7-day file-based per product |

---

## Architecture layers

```
┌──────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React 18 + Vite)                    │
│  Zustand · React Query · Tailwind · Framer Motion                │
│  Views: GalaxyDashboard · SpectrumModule · ProductPage ·         │
│         CurationDashboard · DesignArena                          │
│  Data: useConductorCatalog() · useJITIntelligence(SSE)             │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓  REST / SSE
┌──────────────────────────────────────────────────────────────────┐
│              API (FastAPI — port 8000)                            │
│  /api/conductor/*   Catalog, taxonomy, filter, refresh            │
│  /api/jit/product/* Live product intelligence (SSE)             │
│  /api/curation/*    Relationships, pending, confirm/reject        │
│  /api/mcp/*         MCP tools                                    │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│             CATALOG + PRODUCT GRAPH                               │
│  product_normalizer.build_catalog(data_dir)                       │
│  → Normalize brand JSONs → ProductGraph.from_flat_products()      │
│  → Relationship pipeline (see below) → GraphStore.export_json()   │
│  → Indexes: by_galaxy, by_spectrum, by_brand, by_family,          │
│             relationships                                          │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│             RELATIONSHIP PIPELINE (priority order)                │
│  1. Official   — relationship_enrichment_official (brand pages)    │
│  2. Commercial — relationship_discovery (variants + accessories)   │
│  3. Contextual — relationship_enrichment_contextual (reviews)      │
│  4. Spectrum   — relationship_discovery (alternatives by spectrum)  │
│  Persisted: backend/data/graph/product_graph.json                 │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│             JIT AGENT (on-demand)                                 │
│  Trigger: user opens product. SSE: snap → intel → wisdom → explore│
│  Tools: read_halilit_page · search_trusted_reviews                │
│  Cache: 7-day file-based TTL per product                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## Source rules (THE LAW)

All data adheres to three authorized sources:

| Source         | Owner   | Fields |
| -------------- | ------- | ------ |
| **Commercial** | Halilit | Price, SKU, catalog position, Golden List |
| **Official**   | Brand   | Specs, images, descriptions, official_url |
| **Contextual** | Reviews | Opinions, ratings (3+ trusted sources) |

- **Zero tolerance**: No synthetic data. Empty fields over fabricated.
- **Golden Circle**: Only trusted review domains (e.g. Sound On Sound, Sweetwater, Thomann).
- **Enforcement**: `backend/source_rules.py`.

---

## API reference

### Conductor (catalog)

| Method | Path                        | Description              |
| ------ | --------------------------- | ------------------------ |
| GET    | `/api/conductor/catalog`    | Full catalog + graph indexes |
| GET    | `/api/conductor/taxonomy`   | Category & brand schema  |
| POST   | `/api/conductor/filter`     | Filtered product query   |
| GET    | `/api/conductor/categories` | Category summary         |
| GET    | `/api/conductor/refresh`    | Force catalog rebuild    |

### JIT

| Method | Path                     | Description              |
| ------ | ------------------------ | ------------------------ |
| POST   | `/api/jit/product/{id}`  | SSE stream of intelligence |

### Curation

| Method | Path                          | Description                |
| ------ | ----------------------------- | -------------------------- |
| GET    | `/api/curation/relationships/pending` | Pending relationships |
| GET    | `/api/curation/relationships/{product_id}` | Relationships for product |
| POST   | `/api/curation/relationships` | Create/confirm relationship |
| DELETE | `/api/curation/relationships` | Reject/remove relationship |

### System

| Method | Path                  | Description   |
| ------ | --------------------- | -------------- |
| GET    | `/api/health`         | Service health |
| GET    | `/api/catalog/health` | Data quality   |

---

## Core components

| Module             | File / path              | Purpose |
| ------------------ | ------------------------ | ------- |
| API server         | `server.py`              | FastAPI, catalog, JIT, curation, MCP |
| Catalog builder    | `product_normalizer.py` | build_catalog(), graph pipeline |
| Product graph      | `product_graph.py`       | ProductGraph, families, relationships |
| Graph store        | `product_graph_store.py` | JSON snapshot, optional PostgreSQL |
| JIT agent          | `jit_agent.py`           | On-demand intelligence stream |
| Conductor CLI      | `conductor_main.py`      | ingest, sync, rebuild-catalog, dev |
| Source rules       | `source_rules.py`        | Commercial / Official / Contextual law |
| MCP                | `mcp/`                   | catalog_db, design_director, ui_bridge, … |

### Frontend

| Module            | Path / file                  | Purpose |
| ----------------- | ---------------------------- | ------- |
| App router        | `App.tsx`                    | Galaxy, Spectrum, Product, Curation, DesignArena |
| Galaxy            | `views/GalaxyDashboard.tsx`   | Category browser |
| Spectrum          | `views/SpectrumModule.tsx`   | Product grid, filters |
| Product           | `views/ProductPage.tsx`      | Mission Control, JIT |
| Curation          | `views/CurationDashboard.tsx`| Relationship review |
| Design Arena      | `views/DesignArena.tsx`     | Variant experiments |
| Catalog hook      | `hooks/useConductorCatalog.ts` | React Query catalog |

---

## Troubleshooting

```bash
# Backend won't start
rm -rf backend/__pycache__ && PYTHONPATH=. python backend/server.py

# No products / empty catalog
PYTHONPATH=. python backend/conductor_main.py skeleton-sync
# or full: ingest-all then restart server

# Rebuild catalog + graph only (no scrape)
PYTHONPATH=. python backend/conductor_main.py rebuild-catalog

# Port in use
lsof -i :8000 && kill -9 <PID>
```

### Repo strategy

- **Tracked**: Source code, static assets (logos, backgrounds), config.
- **Gitignored**: Brand JSONs, inventory, search indexes, pipeline data, `dist/`, `node_modules/`, `backend/data/`.
- **Generated**: Catalog and graph built at runtime or via `rebuild-catalog`.

---

**v9.2.0** · February 2026
