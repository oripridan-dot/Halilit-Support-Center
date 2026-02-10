# Repository Instructions & Context (v8.2)

## Project Overview

**Halilit Support Center v8.2** — AI-powered product catalog system for musical instruments.

- **Architecture**: Trinity Swarm (3 Gemini 2.0-flash agents) + Celery async task queue
- **Frontend**: React 18 + Vite + TypeScript + Zustand + React Query + Tailwind CSS
- **Backend**: Python 3.11 + FastAPI + google-genai SDK + Pillow
- **Task Queue**: Celery 5.3 + Redis (harvest/enrich/validate workers)
- **Repo Strategy**: Lean — all generated data (brand JSONs, shards, pipeline outputs) is gitignored

## Running the System

```bash
# Backend (FastAPI + Trinity Swarm)
PYTHONPATH=. python3 backend/server.py

# Frontend (React)
cd frontend && pnpm dev

# Task Queue (Docker)
docker-compose up -d
```

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, google-genai SDK, Pydantic v2, Pillow, Celery + Redis
- **Frontend**: React 18.3.1, TypeScript 5.x, Vite 5.x, Zustand 5, React Query 5, Tailwind CSS 3.4
- **Infrastructure**: Docker Compose (Redis 7, PostgreSQL 15, Celery workers, Flower monitor)

## File Structure

```
backend/
├── server.py                      # FastAPI server + enriched catalog API
├── celery_config.py               # Celery + Redis configuration
├── tasks.py                       # Distributed agent tasks
├── unified_agent_orchestrator.py  # Trinity Swarm (Scout, Verifier, Auditor)
├── unified_data_service.py        # Product normalization & data pipeline
├── unified_quality_gates.py       # Audit, security gates, feedback engine
├── unified_learning_system.py     # Agent learning & improvement loops
├── product_normalizer.py          # Product shape normalization
├── conductor_main.py              # CLI for all operations
├── auto_sync_engine.py            # Real-time SSE sync to frontend
├── api/                           # Routers (copilot, tasks, streams, ws)
├── ingestion/                     # 7-phase pipeline + visual validator
├── skills/                        # Modular verified capabilities
├── agents/                        # Multi-cycle runner & perfection map
├── scripts/                       # Utilities (type gen, search index, workers)
├── data/                          # Generated pipeline data (gitignored)
└── tests/                         # Test suite

frontend/
├── src/
│   ├── main.tsx                   # React entry + QueryClient
│   ├── App.tsx                    # 3-view router (Galaxy, Spectrum, ProductPage)
│   ├── components/views/          # GalaxyDashboard, SpectrumModule, ProductPage
│   ├── hooks/                     # Data fetching hooks (React Query)
│   ├── store/                     # Zustand stores (navigation, products)
│   ├── types/                     # TypeScript definitions
│   ├── lib/                       # Utilities (categories, search, images)
│   └── workers/                   # Web Worker (search)
├── public/
│   ├── data/category_thumbnails/  # Static category images (tracked)
│   └── assets/                    # Logos, backgrounds (tracked)
└── vite.config.ts                 # Dev proxy → localhost:8000
```

## Code Standards

### Frontend (React/TypeScript)

- **Types**: Import `Product` from `types/index.ts` (canonical source, generated from backend)
- **State**: Zustand for app state, React Query for server state
- **Styling**: Tailwind CSS with `slate-900` dark theme, `blue-500` accents
- **Components**: Functional components with hooks only (class components only for ErrorBoundary)
- **Data**: All product data comes from `/api/conductor/catalog` (enriched catalog)
- **NEVER** leave a file empty or < 100 bytes

### Backend (Python)

- **Agents**: Trinity Swarm in `unified_agent_orchestrator.py` — do NOT hardcode into Agent classes
- **Skills**: Modular capabilities in `backend/skills/`
- **Tasks**: Async operations via Celery tasks in `tasks.py`
- **Data Models**: Pydantic v2 (`IngestionProductDraft`, `AuditReport`)
- **Imports**: Use `backend.` prefix for all internal imports (e.g., `from backend.celery_config import celery_app`)
- **Gemini SDK**: Use `google.genai` (not `google.generativeai`), model `gemini-2.0-flash`

### Key Principles

- Agents work autonomously via Trinity Swarm (CommercialScout → OfficialVerifier → ExternalValidator)
- Catalog API returns enriched data: images (hero+gallery), descriptions, merged specs, quality scores
- Real-time communication via SSE streams and WebSocket
- Type-safe data flow: Pydantic (backend) → generated.ts (frontend)
- All async work goes through Celery task queue
- Generated data is gitignored — only source code and static assets are tracked
