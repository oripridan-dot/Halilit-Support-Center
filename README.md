# Halilit Support Center v8.1 - Async Task Queue & Distributed Pipeline

**Status**: ✅ **PRODUCTION READY**  
**Version**: v8.1.0  
**Branch**: `v8.0`  
**Pipeline**: Trinity Swarm + Celery Async Workers  
**Product Catalog**: 1,200+ verified products

---

## What is Halilit Support Center?

An **AI-powered product intelligence platform** that automatically:

1. **Harvests** product data from Halilit.com (CommercialScout agent)
2. **Enriches** with manufacturer specs and categorization (OfficialVerifier agent)
3. **Validates** data quality and compliance (ExternalValidator agent)
4. **Syncs** approved products to the frontend in real-time (Unified Data Service)
5. **Learns** from every operation via agent memory (Trinity Swarm)

Uses **Google Gemini 2.0-flash** agents working in unison to ensure data accuracy.

### What's New in v8.1

- **Async Task Queue**: Celery + Redis distributed pipeline replaces synchronous agent execution
- **Parallel Workers**: Multiple Celery workers process products concurrently (15x+ throughput)
- **Docker Infrastructure**: Full `docker-compose.yml` with Redis, PostgreSQL, Flower monitoring
- **Stress Testing**: Comprehensive test harness for baseline comparisons
- **SSE Streaming**: Real-time Server-Sent Events for pipeline progress

---

## One-Minute Setup

```bash
# Prerequisites: Python 3.11+, Node.js 18+, GOOGLE_API_KEY

# 1. Install backend
cd /workspaces/Halilit-Support-Center
pip install -r backend/requirements.txt

# 2. Install frontend
cd frontend && pnpm install

# 3. Start backend (Terminal 1)
cd /workspaces/Halilit-Support-Center
PYTHONPATH=. python3 backend/server.py

# 4. Start frontend (Terminal 2)
cd frontend && pnpm dev

# Open http://localhost:5173
```

### Docker (for async workers)

```bash
docker-compose up -d redis postgres
# Start Celery workers
celery -A backend.tasks worker --loglevel=info --concurrency=4
# Monitor with Flower
celery -A backend.tasks flower --port=5555
```

---

## Documentation

| Document                                                       | Purpose                                              |
| -------------------------------------------------------------- | ---------------------------------------------------- |
| **[ARCHITECTURE.md](ARCHITECTURE.md)**                         | Technical architecture, API reference, system design |
| **[backend/ingestion/README.md](backend/ingestion/README.md)** | Ingestion pipeline details                           |

---

## System Architecture

```
┌────────────────────────────────────────┐
│ FRONTEND (React 18 + CopilotKit)       │
│ - GalaxyDashboard (category browser)   │
│ - SpectrumModule (product spectrum)    │
│ - ProductPage (full analysis)          │
│ - Zustand Store + React Query          │
└──────────────┬─────────────────────────┘
               │ SSE + REST
┌──────────────▼─────────────────────────┐
│ FASTAPI BACKEND (server.py)            │
│ - Conductor endpoints (/api/conductor) │
│ - Skills endpoints (/api/copilot)      │
│ - Sync endpoints (/api/copilot/sync)   │
│ - Task queue endpoints (/api/tasks)    │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│ ASYNC TASK QUEUE (v8.0)                │
│ - Celery + Redis broker                │
│ - Distributed worker pool              │
│ - Task monitoring (Flower)             │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│ TRINITY SWARM (3 Gemini Agents)        │
│ - CommercialScout (harvest)            │
│ - OfficialVerifier (enrich + images)   │
│ - ExternalValidator (audit + score)    │
│ + Learning System + Quality Gates      │
└────────────────────────────────────────┘
```

---

## The Trinity Swarm

Three specialized Gemini 2.0-flash agents:

| Agent                 | Role                                   | Output                      |
| --------------------- | -------------------------------------- | --------------------------- |
| **CommercialScout**   | Harvests product data from Halilit.com | ProductDraft with price     |
| **OfficialVerifier**  | Enriches with specs, images, taxonomy  | EnrichedProduct with images |
| **ExternalValidator** | Audits compliance, risk scoring 0-100  | AuditReport with risk score |

All agents have **learning capabilities** — they improve over time via feedback loops.

---

## Project Structure

```
backend/
├── server.py                      # FastAPI main server
├── conductor_main.py              # CLI interface
├── celery_config.py               # Celery task queue (v8.0)
├── tasks.py                       # Distributed task definitions (v8.0)
├── auto_sync_engine.py            # Real-time SSE sync
├── unified_agent_orchestrator_v76.py  # Trinity Swarm orchestration
├── unified_data_service_v76.py        # Data pipeline & normalization
├── unified_quality_gates_v76.py       # Quality gates & audit
├── unified_learning_system_v76.py     # Agent learning system
├── agents/                        # Multi-cycle runner, perfection map
├── api/                           # Routers (copilot, tasks, streams, ws)
├── ingestion/                     # 6-phase pipeline modules
├── skills/                        # Modular skill framework
├── scripts/                       # Utilities & stress tests
├── tests/                         # Test suites
└── config/                        # Brand tiers, DB schema

frontend/
├── src/
│   ├── App.tsx                    # Three-screen router
│   ├── components/views/          # Galaxy, Spectrum, ProductPage
│   ├── hooks/                     # React Query hooks
│   ├── lib/                       # Utilities
│   ├── store/                     # Zustand state
│   └── types/                     # TypeScript definitions
└── public/data/                   # Static product data (100+ brands)

docker-compose.yml                 # Redis + PostgreSQL + Workers
Dockerfile                         # Worker container image
```

---

## API Reference

### Conductor Endpoints

| Method | Path                        | Description             |
| ------ | --------------------------- | ----------------------- |
| GET    | `/api/conductor/catalog`    | All verified products   |
| GET    | `/api/conductor/taxonomy`   | Category & brand schema |
| POST   | `/api/conductor/filter`     | Filtered product query  |
| GET    | `/api/conductor/categories` | Category summary        |
| GET    | `/api/conductor/refresh`    | Force cache refresh     |

### Skills & Pipeline Endpoints

| Method | Path                         | Description           |
| ------ | ---------------------------- | --------------------- |
| GET    | `/api/copilot/skills`        | List available skills |
| POST   | `/api/copilot/execute-skill` | Execute single skill  |
| POST   | `/api/copilot/pipeline`      | Run full pipeline     |
| POST   | `/api/copilot/batch-ingest`  | Batch processing      |

### Task Queue Endpoints (v8.0)

| Method | Path                     | Description       |
| ------ | ------------------------ | ----------------- |
| POST   | `/api/tasks/submit`      | Submit async task |
| GET    | `/api/tasks/{id}/status` | Task status       |
| GET    | `/api/tasks/queue/stats` | Queue statistics  |

---

## Running Tests

```bash
PYTHONPATH=. python3 -m pytest backend/tests/ -v

# Stress test (requires Redis)
PYTHONPATH=. python3 backend/scripts/phase8b_stress_test.py
```

---

**Halilit Support Center v8.1**  
**Async Pipeline — Distributed Workers — Production Ready**  
Last Updated: February 9, 2026
