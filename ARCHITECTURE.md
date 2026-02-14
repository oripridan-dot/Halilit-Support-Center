# Halilit Support Center — Architecture

**Version**: 9.0.0 (JIT Architecture)  
**Updated**: February 14, 2026

---

## System Overview

AI-powered product intelligence platform using a **Just-in-Time (JIT)** architecture. Instead of heavy upfront ingestion, the system maintains a lightweight skeleton inventory and streams live intelligence on demand via Gemini 2.0 Flash.

| Metric            | Value                                              |
| ----------------- | -------------------------------------------------- |
| Products          | 500+ (skeleton inventory from Halilit.com)         |
| API Endpoints     | 10                                                 |
| Intelligence      | JIT — live per-product research via Gemini 2.0     |
| Trusted Sources   | 10 (Golden Circle — Sound On Sound, Sweetwater...) |
| Cache TTL         | 7 days (file-based per product)                    |

---

## Architecture Layers

```
┌──────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React 18 + Vite)                    │
│  Zustand state · React Query · Tailwind CSS · Framer Motion      │
│  Views: GalaxyDashboard · SpectrumModule · Product Cockpit       │
│  Hooks: useConductorCatalog · useJITIntelligence (SSE)           │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓  REST / SSE
┌──────────────────────────────────────────────────────────────────┐
│              API LAYER (FastAPI — port 8000)                      │
│  /api/conductor/*    Catalog, taxonomy, filtering                │
│  /api/jit/product/*  Live product intelligence (SSE stream)      │
│  /api/health         Service health check                        │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│             SKELETON INVENTORY (Nightly sync)                    │
│  skeleton_sync.py → inventory.json (ID, Name, Price, URL, Thumb)│
│  Zero AI calls — listing pages only — ~30 seconds for all brands│
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│              JIT AGENT (On-Demand Intelligence)                  │
│                                                                  │
│  Triggered when user clicks a product. Streams SSE events:       │
│                                                                  │
│  Phase 1 — SNAP:    Inventory data (instant, <200ms)             │
│  Phase 2 — INTEL:   Halilit page scrape (specs, images)          │
│  Phase 3 — WISDOM:  Gemini reasoning (verdict, pro tips)         │
│  Phase 4 — EXPLORE: Suggested next actions                       │
│                                                                  │
│  Tools: read_halilit_page · search_trusted_reviews               │
│  Cache: 7-day file-based TTL per product                         │
└──────────────────────────────────────────────────────────────────┘
```

---

## Source Rules (THE LAW)

All data strictly adheres to three authorized sources:

| Source             | Owner    | Fields                              |
| ------------------ | -------- | ----------------------------------- |
| **Commercial**     | Halilit  | Price, SKU, stock, catalog position |
| **Official**       | Brand    | Specs, images, descriptions         |
| **Contextual**     | Reviews  | Opinions, ratings (3+ sources)      |

- **Zero Tolerance**: If the JIT agent can't find data, the field stays empty — never fabricated.
- **Golden Circle**: Only trusted review domains (Sound On Sound, MusicRadar, Sweetwater, Thomann, Equipboard, Sonic State, etc.)

---

## API Reference

### Conductor (Catalog)

| Method | Path                        | Description              |
| ------ | --------------------------- | ------------------------ |
| GET    | `/api/conductor/catalog`    | Enriched product catalog |
| GET    | `/api/conductor/taxonomy`   | Category & brand schema  |
| POST   | `/api/conductor/filter`     | Filtered product query   |
| GET    | `/api/conductor/categories` | Category summary         |
| GET    | `/api/conductor/refresh`    | Force cache refresh      |

### JIT Intelligence

| Method | Path                           | Description                        |
| ------ | ------------------------------ | ---------------------------------- |
| POST   | `/api/jit/product/{id}`       | SSE stream of live intelligence    |

### System

| Method | Path                | Description        |
| ------ | ------------------- | ------------------ |
| GET    | `/api/health`       | Service health     |
| GET    | `/api/catalog/health` | Data quality     |

---

## Core Components

| Module               | File                        | Purpose                             |
| -------------------- | --------------------------- | ----------------------------------- |
| **API Server**       | `server.py`                 | FastAPI + catalog + JIT endpoint    |
| **JIT Agent**        | `jit_agent.py`              | Gemini-powered live intelligence    |
| **Trusted Sources**  | `trusted_sources.py`        | Golden Circle whitelist             |
| **Skeleton Sync**    | `skeleton_sync.py`          | Lightweight Halilit inventory fetch |
| **Source Rules**     | `source_rules.py`           | THE LAW — data provenance rules    |
| **Data Service**     | `unified_data_service.py`   | Catalog aggregation                 |
| **Product Normalizer** | `product_normalizer.py`   | Catalog building & normalization    |
| **CLI**              | `conductor_main.py`         | Command-line interface              |
| **MCP**              | `mcp/`                      | Model Context Protocol tools        |

### Frontend

| Module               | File                              | Purpose                          |
| -------------------- | --------------------------------- | -------------------------------- |
| **Galaxy Dashboard** | `views/GalaxyDashboard.tsx`       | Category browser                 |
| **Product Cockpit**  | `views/ProductPage.tsx`           | Mission Control product view     |
| **JIT Hook**         | `hooks/useJITIntelligence.ts`     | SSE consumer for JIT stream      |
| **Brand Themes**     | `styles/brandThemes.ts`           | Brand visual DNA                 |
| **Slot Backgrounds** | `lib/slotBackgrounds.ts`          | Category contextual backgrounds  |
| **Cockpit Cards**    | `components/cockpit/*`            | VerdictCard, FieldNotes, etc.    |

---

## Troubleshooting

```bash
# Backend won't start
rm -rf backend/__pycache__ && PYTHONPATH=. python3 backend/server.py

# Frontend shows "No Products"
curl http://localhost:8000/api/conductor/catalog
# If empty: PYTHONPATH=. python3 backend/conductor_main.py skeleton-sync

# Port in use
lsof -i :8000 && kill -9 <PID>
```

### Repo Strategy

- **Tracked**: Source code, static assets (logos, backgrounds), config
- **Gitignored**: Brand JSONs, inventory, search indexes, pipeline data, `dist/`, `node_modules/`
- **Generated at runtime**: inventory.json from skeleton-sync, JIT cache from agent

---

**v9.0.0** · February 14, 2026
