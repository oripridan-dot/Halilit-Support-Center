# Halilit Support Center v8.1 - Architecture & Operations

**Version**: 8.1 (Async Task Queue + Distributed Pipeline)  
**Release Date**: February 9, 2026  
**Status**: ✅ **PRODUCTION READY**

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Async Task Queue (v8.0)](#async-task-queue-v80)
4. [Quick Start](#quick-start)
5. [API Reference](#api-reference)
6. [Learning System](#learning-system)

---

## System Overview

### What is Halilit Support Center?

An **AI-powered product catalog intelligence system** using Google's multi-agent architecture (Trinity Swarm) to:

- **Harvest** product data from Halilit.com (CommercialScout)
- **Enrich** with vendor specifications and pricing (OfficialVerifier)
- **Resolve** and validate visual assets (VisualValidator)
- **Validate** data quality and compliance (ExternalValidator)
- **Deliver** verified data to the frontend in real-time

### Key Statistics

```
Verified Products:    1,200+
Brands Indexed:       100+
Visual Assets:        Resolved & Validated
Data Accuracy:        98.5% (Enriched Metadata)
API Endpoints:        15+
Pipeline Phases:      7 (Harvest → Enrich → Visuals → Tier → Prepare → Validate → Approve)
```

---

## Architecture

### System Layers

```
┌──────────────────────────────────────────────────────────────────┐
│                    USER LAYER (Frontend)                          │
│  Browser (React 18) → CopilotKit UI with Agent Chat             │
│  - GalaxyDashboard (category navigation)                        │
│  - SpectrumModule (product browsing)                            │
│  - ProductPage (full analysis view)                             │
│  - Real-time sync via SSE                                       │
└────────────────────────┬─────────────────────────────────────────┘
                         ↓  HTTP / SSE / WebSocket
┌────────────────────────────────────────────────────────────────────┐
│              API LAYER (FastAPI Server - Port 8000)                │
│                                                                    │
│  Conductor Endpoints:  /api/conductor/* (catalog, taxonomy, etc.)  │
│  Skills Endpoints:     /api/copilot/*  (pipeline, batch-ingest)    │
│  Sync Endpoints:       /api/copilot/sync/* (real-time sync)        │
│  Task Endpoints:       /api/tasks/*    (v8.0 async queue)          │
│  Learning Endpoint:    /api/learning/health                        │
└────────────────────────┬───────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────────────┐
│           DATA ACCESS LAYER (ConductorDataService)                 │
│  ├─ get_unified_catalog() - All verified products                  │
│  ├─ get_taxonomy_schema() - Dynamic categories                     │
│  ├─ filter_products() - Multi-criteria filtering                   │
│  └─ get_category_summary() - Navigation data                      │
└────────────────────────┬───────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────────────┐
│          ASYNC TASK QUEUE (v8.0 - Celery + Redis)                  │
│  ├─ harvest_brand_products  (CommercialScout task)                 │
│  ├─ enrich_product          (OfficialVerifier task)                │
│  ├─ validate_product        (ExternalValidator task)               │
│  └─ record_learning_feedback (Learning System task)                │
│                                                                    │
│  Infrastructure: Redis broker → Celery workers → Flower monitor    │
└────────────────────────┬───────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────────────┐
│          INGESTION PIPELINE (7 Phases + Learning)                  │
│                                                                    │
│  Phase 1: HARVEST      (CommercialScout extracts products)         │
│  Phase 2: ENRICH       (OfficialVerifier adds specs + images)      │
│  Phase 3: VISUALS      (VisualValidator resolves images)           │
│  Phase 4: TIER         (PricingEngine categorizes price tiers)     │
│  Phase 5: PREPARE      (DisplayEngine formats output)              │
│  Phase 6: VALIDATE     (ExternalValidator checks compliance)       │
│  Phase 7: APPROVE      (Final verification gate)                   │
│  → Auto-Sync to Frontend (real-time SSE updates)                   │
│  → Learning Loop (Feedback → Improvements → Next Cycle)            │
└────────────────────────┬───────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────────────┐
│              TRINITY SWARM (3 Gemini 2.0-flash Agents)             │
│                                                                    │
│  CommercialScout (Harvest)                                         │
│     → Harvests product data from Halilit.com                       │
│     → Categorizes into taxonomy                                    │
│     → Outputs: ProductDraft with price                             │
│                                                                    │
│  OfficialVerifier (Enrich)                                         │
│     → Enriches with manufacturer specs                             │
│     → Finds official images                                        │
│     → Outputs: EnrichedProduct with images                         │
│                                                                    │
│  ExternalValidator (Audit)                                         │
│     → Audits data completeness                                     │
│     → Identifies compliance issues                                 │
│     → Outputs: AuditReport with risk score (0-100)                 │
│                                                                    │
│  Each Agent Has: Memory, Learning, Confidence Scoring, Audit Trail │
└────────────────────────┬───────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────────────┐
│            STORAGE (IngestionDatabase + Cache)                      │
│  ├─ Approved Products (1,200+ verified)                            │
│  ├─ Rejected Products (with reasons)                               │
│  ├─ Agent Decisions (decision log)                                 │
│  ├─ Learning Feedback (30+ cycles)                                 │
│  ├─ Audit Trail (all operations)                                   │
│  └─ Performance Metrics                                            │
└────────────────────────────────────────────────────────────────────┘
```

---

## Async Task Queue (v8.0)

The key v8.0 enhancement: agent operations run as **distributed Celery tasks**.

### Components

| Component   | Technology       | Purpose                               |
| ----------- | ---------------- | ------------------------------------- |
| **Broker**  | Redis 7          | Message queue between API and workers |
| **Workers** | Celery 5.3       | Execute agent tasks in parallel       |
| **Results** | Redis/PostgreSQL | Store task results and status         |
| **Monitor** | Flower           | Web UI for task monitoring            |

### Task Flow

```
API Request → Celery Task Submitted → Redis Queue
                                         ↓
                              Worker Pool (N workers)
                                         ↓
                              Agent Execution (Gemini)
                                         ↓
                              Result → SSE → Frontend
```

### Docker Infrastructure

```bash
docker-compose up -d redis postgres
celery -A backend.tasks worker --loglevel=info --concurrency=4
celery -A backend.tasks flower --port=5555
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- `GOOGLE_API_KEY` environment variable

### Installation

```bash
cd /workspaces/Halilit-Support-Center
pip install -r backend/requirements.txt
cd frontend && pnpm install && cd ..
```

### Running

**Terminal 1: Backend**

```bash
PYTHONPATH=. python3 backend/server.py
# → http://localhost:8000
```

**Terminal 2: Frontend**

```bash
cd frontend && pnpm dev
# → http://localhost:5173
```

---

## API Reference

### Conductor Endpoints

```
GET  /api/conductor/catalog       # All verified products
GET  /api/conductor/taxonomy      # Category & brand schema
POST /api/conductor/filter        # Filtered product query
GET  /api/conductor/categories    # Category summary
GET  /api/conductor/refresh       # Force cache refresh
```

### Skills Endpoints

```
GET  /api/copilot/skills          # List available skills
POST /api/copilot/execute-skill   # Execute single skill
POST /api/copilot/pipeline        # Run full pipeline
POST /api/copilot/batch-ingest    # Batch processing
GET  /api/copilot/status          # Pipeline status
GET  /api/copilot/history         # Execution history
```

### Sync Endpoints

```
POST /api/copilot/sync            # Sync single product
POST /api/copilot/sync-batch      # Batch sync
GET  /api/copilot/sync/history    # Sync history
```

### Task Queue Endpoints (v8.0)

```
POST /api/tasks/submit            # Submit async task
GET  /api/tasks/{id}/status       # Task status
GET  /api/tasks/queue/stats       # Queue statistics
```

---

## Learning System

The learning system continuously improves agent accuracy through feedback loops:

```
Agent Decision → Outcome Observed → Pattern Analysis → Improvement → Next Cycle
```

### CLI Commands

```bash
PYTHONPATH=. python3 backend/conductor_main.py learning       # Learning status
PYTHONPATH=. python3 backend/conductor_main.py audit          # Audit trail
PYTHONPATH=. python3 backend/conductor_main.py catalog        # Catalog stats
PYTHONPATH=. python3 backend/conductor_main.py ingest [brand] # Run ingestion
PYTHONPATH=. python3 backend/conductor_main.py sync           # Sync to frontend
```

---

## Core Components

| Module                 | File                                | Purpose                                           |
| ---------------------- | ----------------------------------- | ------------------------------------------------- |
| **Agent Orchestrator** | `unified_agent_orchestrator_v76.py` | Trinity Swarm (3 agents + orchestration)          |
| **Data Service**       | `unified_data_service_v76.py`       | Product normalization, aggregation, frontend sync |
| **Quality Gates**      | `unified_quality_gates_v76.py`      | Audit, security, feedback, agent memory           |
| **Learning System**    | `unified_learning_system_v76.py`    | Agent learning loops & improvement tracking       |
| **Task Queue**         | `celery_config.py` + `tasks.py`     | v8.0 async distributed execution                  |
| **Ingestion Pipeline** | `ingestion/orchestrator.py`         | 7-phase pipeline orchestration                    |
| **Skills Framework**   | `skills/`                           | 6 modular, verifiable capabilities                |
| **API Server**         | `server.py`                         | FastAPI with all endpoints                        |
| **CLI**                | `conductor_main.py`                 | Command-line interface                            |

---

## Code Quality Standards

### Python

- Type hints on all functions and classes
- Docstrings for all modules, functions, classes
- Pydantic v2 for data validation
- Comprehensive error handling

### TypeScript

- Strict mode enabled
- Type definitions for all props and state
- Component composition over inheritance
- Error boundaries for resilience

---

## Troubleshooting

### Backend Won't Start

```bash
rm -rf backend/__pycache__
PYTHONPATH=. python3 backend/server.py
```

### Frontend Shows "No Products"

```bash
curl http://localhost:8000/api/conductor/catalog
# If empty, run: PYTHONPATH=. python3 backend/conductor_main.py sync
```

### Port Already in Use

```bash
lsof -i :8000 && kill -9 <PID>
```

---

**Version**: 8.1 (Async Task Queue + Distributed Pipeline)  
**Last Updated**: February 9, 2026  
**Status**: ✅ **PRODUCTION READY**
