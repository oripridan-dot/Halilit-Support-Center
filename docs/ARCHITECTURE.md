# Halilit Support Center — Architecture

**Version:** Operator Console (spec-driven)  
**Updated:** February 2026

---

## System overview

AI-powered product intelligence platform using a **Just-in-Time (JIT)** architecture. Catalog is built from ingestion (Conductor); product graph provides families and relationships. Live intelligence is streamed on demand per product via Gemini 2.0 Flash.

| Metric            | Value |
| ----------------- | ----- |
| Catalog           | Built from backend/data (learned_taxonomy, catalog_cache); API serves it |
| Product graph     | Families + relationships (official → commercial → contextual → spectrum) |
| Intelligence      | JIT — live per-product research via Gemini 2.0 |
| Trusted sources   | Golden Circle (Sound On Sound, Sweetwater, …) |
| Cache             | Catalog: server TTL; JIT: 7-day file-based per product |

---

## Architecture layers

```
┌──────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React 18 + Vite)                     │
│  Zustand · React Query · Tailwind · Framer Motion                 │
│  Views: DashboardView · InventoryView · ProductDetailView          │
│  Data: useConductorCatalog() · useJITIntelligence(SSE)             │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓  REST / SSE
┌──────────────────────────────────────────────────────────────────┐
│              API (FastAPI — port 8000)                             │
│  /api/conductor/*   Catalog, taxonomy, filter, refresh            │
│  /api/jit/product/* Live product intelligence (SSE)               │
│  /api/products/search  Product search                             │
│  /api/mcp/*         MCP tools                                     │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│             CATALOG + PRODUCT GRAPH                               │
│  product_normalizer.build_catalog() · ProductGraph · GraphStore   │
│  Artifacts: learned_taxonomy.json, catalog_cache.json.gz          │
│  Indexes: by_brand, by_family, relationships                       │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│             RELATIONSHIP PIPELINE (priority order)                │
│  1. Official   — brand pages, accessories/related                 │
│  2. Commercial — variants + accessory links (catalog)             │
│  3. Contextual — reviews: "works with X"                          │
│  4. Spectrum   — alternatives by spectrum/tier                     │
│  Persisted: backend/data/graph/product_graph.json                 │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│             JIT AGENT (on-demand)                                 │
│  Trigger: user opens product. SSE: snap → intel → wisdom → explore│
│  Tools: read_halilit_page · search_trusted_reviews                 │
│  Cache: 7-day file-based TTL per product                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## Source rules (THE LAW)

| Source         | Owner   | Fields |
| -------------- | ------- | ------ |
| **Commercial** | Halilit | Price, SKU, catalog position, Golden List |
| **Official**   | Brand   | Specs, images, descriptions, official_url |
| **Contextual** | Reviews | Opinions, ratings (3+ trusted sources) |

- **Zero tolerance:** No synthetic data. Empty fields over fabricated.
- **Enforcement:** `backend/source_rules.py`.

---

## API reference

### Conductor (catalog)

| Method | Path                        | Description              |
| ------ | --------------------------- | ------------------------ |
| GET    | `/api/conductor/catalog`    | Full catalog + graph indexes |
| GET    | `/api/conductor/taxonomy`   | Category & brand schema  |
| GET    | `/api/conductor/refresh`    | Force catalog rebuild    |

### Products

| Method | Path                        | Description              |
| ------ | --------------------------- | ------------------------ |
| GET    | `/api/products/search?q=`   | Product search           |

### JIT

| Method | Path                     | Description              |
| ------ | ------------------------ | ------------------------ |
| POST   | `/api/jit/product/{id}`  | SSE stream of intelligence |

### System

| Method | Path                  | Description   |
| ------ | --------------------- | -------------- |
| GET    | `/api/health`         | Service health |

---

## Core components

| Module             | File / path              | Purpose |
| ------------------ | ------------------------ | ------- |
| API server         | `server.py`              | FastAPI, catalog, JIT, MCP |
| Catalog builder    | `product_normalizer.py`  | build_catalog(), graph pipeline |
| Product graph      | `product_graph.py`       | ProductGraph, families, relationships |
| Graph store        | `product_graph_store.py` | JSON snapshot, optional PostgreSQL |
| JIT agent          | `jit_agent.py`           | On-demand intelligence stream |
| Conductor CLI      | `conductor_main.py`      | ingest, sync, rebuild-catalog, dev |
| Source rules       | `source_rules.py`        | Commercial / Official / Contextual law |

### Frontend (Operator Console)

| Module         | Path / file                    | Purpose |
| -------------- | ------------------------------- | ------- |
| App shell      | `App.tsx`                       | Router: Dashboard, Inventory, Product Detail |
| Mission Control| `views/DashboardView.tsx`       | Key metrics, quick links |
| Inventory Master| `views/InventoryView.tsx`       | Grid, filters, sort, row → Detail |
| Product Intelligence | `views/ProductDetailView.tsx` | Header, toolbar, tabs (Ecosystem, Specs, History) |
| Catalog hook   | `hooks/useConductorCatalog.ts`  | React Query catalog |
| Global search  | `components/GlobalSearch.tsx`   | Search → API → navigate to Detail |

---

## Documentation

- **Workflow and specs:** [docs/README.md](README.md)
- **Quick start:** [docs/QUICK_START.md](QUICK_START.md)
- **Pipeline and Conductor:** [docs/FACTORY_PIPELINE.md](FACTORY_PIPELINE.md)
- **Operator behavior:** [OPERATOR_CONSOLE_SPEC.md](../OPERATOR_CONSOLE_SPEC.md)
