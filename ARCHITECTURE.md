# Halilit Support Center — Architecture

**Version**: 8.3.0  
**Updated**: February 11, 2026

---

## System Overview

AI-powered product catalog system using Google's Trinity Swarm (3 Gemini 2.0-flash agents) to harvest, enrich, validate, and deliver musical instrument data.

| Metric            | Value                                                                |
| ----------------- | -------------------------------------------------------------------- |
| Pipeline Products | 500+ (across 7 indexed brands)                                       |
| API Endpoints     | 15+                                                                  |
| Pipeline Phases   | 7 (Harvest → Enrich → Visuals → Tier → Prepare → Validate → Approve) |
| Source Code       | ~27k lines (lean repo, all generated data gitignored)                |

---

## Architecture Layers

```
┌──────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React 18 + Vite)                    │
│  Zustand state · React Query fetching · Tailwind CSS             │
│  Views: GalaxyDashboard · SpectrumModule · ProductPage           │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓  REST / SSE / WebSocket
┌──────────────────────────────────────────────────────────────────┐
│              API LAYER (FastAPI — port 8000)                      │
│  /api/conductor/*  Catalog, taxonomy, filtering                  │
│  /api/copilot/*    Pipeline, batch-ingest, skills                │
│  /api/tasks/*      Async queue submission & status               │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│           DATA SERVICE (ConductorDataService)                    │
│  get_unified_catalog() · get_taxonomy_schema()                   │
│  filter_products() · get_category_summary()                      │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│              CELERY TASK QUEUE (Redis broker)                     │
│  harvest_brand_products · enrich_product                         │
│  validate_product · record_learning_feedback                     │
│  Flower monitoring · Docker worker containers                    │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│          INGESTION PIPELINE (7 Phases)                            │
│  Harvest → Enrich → Visuals → Tier → Prepare → Validate → Approve│
│  Auto-Sync (SSE) · Learning Loop (feedback → next cycle)         │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────────────┐
│              TRINITY SWARM (3 Gemini 2.0-flash Agents)           │
│                                                                  │
│  CommercialScout   → Harvests from Halilit.com, categorizes      │
│  OfficialVerifier  → Enriches with specs, images, descriptions   │
│  ExternalValidator → Audits completeness, risk scoring (0–100)   │
│                                                                  │
│  Each agent: memory, learning, confidence scoring, audit trail   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Enriched Catalog

The `/api/conductor/catalog` endpoint returns products with:

- **Images**: Cascading fallback — `image_hero` → `image_gallery` → `official_images` → `display.hero_image` → `primary_source`
- **Descriptions**: `official_description` → `description_long` → `description_short`
- **Specs**: Merged from `official_specs` + `specifications`
- **Quality**: `quality_score`, `data_completeness`, price tier (entry/mid/pro)
- **Gallery**: Up to 20 images per product

### Data Flow

```
Brand JSON files (pipeline-generated, gitignored)
  → server.py normalize → enrich → filter (price > 0, has image) → dedup
    → /api/conductor/catalog
      → React Query → Zustand → UI
```

---

## Async Task Queue

| Component   | Technology | Purpose                  |
| ----------- | ---------- | ------------------------ |
| **Broker**  | Redis 7    | Message queue            |
| **Workers** | Celery 5.3 | Parallel agent execution |
| **Results** | Redis      | Task result storage      |
| **Monitor** | Flower     | Web UI (port 5555)       |

```bash
docker-compose up -d          # Start Redis + Postgres + Flower + Workers
```

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

### Skills & Pipeline

| Method | Path                         | Description          |
| ------ | ---------------------------- | -------------------- |
| POST   | `/api/copilot/pipeline`      | Run full pipeline    |
| POST   | `/api/copilot/batch-ingest`  | Batch processing     |
| POST   | `/api/copilot/execute-skill` | Execute single skill |
| GET    | `/api/copilot/skills`        | List skills          |

### Sync

| Method | Path                        | Description  |
| ------ | --------------------------- | ------------ |
| POST   | `/api/copilot/sync`         | Sync product |
| POST   | `/api/copilot/sync-batch`   | Batch sync   |
| GET    | `/api/copilot/sync/history` | Sync history |

### Task Queue

| Method | Path                     | Description |
| ------ | ------------------------ | ----------- |
| POST   | `/api/tasks/submit`      | Submit task |
| GET    | `/api/tasks/{id}/status` | Task status |
| GET    | `/api/tasks/queue/stats` | Queue stats |

---

## Core Components

| Module                 | File                            | Purpose                                  |
| ---------------------- | ------------------------------- | ---------------------------------------- |
| **Agent Orchestrator** | `unified_agent_orchestrator.py` | Trinity Swarm (3 agents + orchestration) |
| **Data Service**       | `unified_data_service.py`       | Normalization, aggregation, sync         |
| **Quality Gates**      | `unified_quality_gates.py`      | Audit, security, feedback, memory        |
| **Learning System**    | `unified_learning_system.py`    | Agent learning & improvement loops       |
| **Task Queue**         | `celery_config.py` + `tasks.py` | Async distributed execution              |
| **Ingestion Pipeline** | `ingestion/orchestrator.py`     | 7-phase pipeline orchestration           |
| **Visual Validator**   | `ingestion/visual_validator.py` | Image verification via Gemini 2.0-flash  |
| **API Server**         | `server.py`                     | FastAPI + enriched catalog               |
| **CLI**                | `conductor_main.py`             | Command-line interface                   |

---

## Troubleshooting

```bash
# Backend won't start
rm -rf backend/__pycache__ && PYTHONPATH=. python3 backend/server.py

# Frontend shows "No Products"
curl http://localhost:8000/api/conductor/catalog
# If empty: PYTHONPATH=. python3 backend/conductor_main.py sync

# Port in use
lsof -i :8000 && kill -9 <PID>
```

### Repo Strategy

- **Tracked**: Source code, static assets (thumbnails, logos, backgrounds), config
- **Gitignored**: Brand JSONs, shards, search indexes, pipeline data, `dist/`, `node_modules/`
- **Generated at runtime**: Product data from ingestion pipeline or `conductor_main.py sync`

---

**v8.5.0** · February 13, 2026
