# Repository Instructions & Context (v8.0)

## Project Overview

**Halilit Support Center v8.0** — AI-powered product catalog system for musical instruments.

- **Architecture**: Trinity Swarm (3 Gemini agents) + Celery async task queue
- **Frontend**: React 18 + Vite + TypeScript + Zustand + React Query + Tailwind CSS
- **Backend**: Python 3.11 + FastAPI + Google Gemini 2.0-flash agents
- **Task Queue**: Celery 5.3 + Redis (harvest/enrich/validate workers)

## Running the System

```bash
# Backend (FastAPI + Trinity Swarm)
PYTHONPATH=. python3 backend/server.py

# Frontend (React)
cd frontend && npm run dev

# Task Queue (Docker)
docker-compose up -d
```

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, google-genai SDK, Pydantic v2, Celery + Redis
- **Frontend**: React 18.3.1, TypeScript 5.x, Vite 5.x, Zustand 5, React Query 5, Tailwind CSS 3.4
- **Infrastructure**: Docker Compose (Redis 7, PostgreSQL 15, Celery workers, Flower monitor)

## File Structure

```
backend/
├── server.py                          # FastAPI main server (~780 lines)
├── celery_config.py                   # Celery + Redis configuration
├── tasks.py                           # Distributed agent tasks
├── unified_agent_orchestrator_v76.py  # Trinity Swarm (Scout, Verifier, Auditor)
├── unified_data_service_v76.py        # Product normalization & data pipeline
├── unified_quality_gates_v76.py       # Audit, security gates, feedback engine
├── unified_learning_system_v76.py     # Agent learning & improvement loops
├── conductor_main.py                  # CLI for all operations
├── auto_sync_engine.py                # Real-time SSE sync to frontend
├── api/
│   ├── copilot_router.py              # CopilotKit chat endpoint
│   ├── task_router.py                 # v8.0 async task queue API
│   ├── streams.py                     # SSE learning stream
│   └── websocket_manager.py           # WebSocket real-time updates
├── skills/                            # Modular verified capabilities
├── ingestion/                         # Data ingestion pipeline
└── tests/                             # Test suite

frontend/
├── src/
│   ├── main.tsx                       # React entry + QueryClient
│   ├── App.tsx                        # 3-view router (Galaxy, Spectrum, ProductPage)
│   ├── components/
│   │   ├── views/                     # GalaxyDashboard, SpectrumModule, ProductPage
│   │   └── ui/                        # Shared UI (Control, Surface, ErrorBoundary)
│   ├── hooks/                         # Data fetching hooks (React Query)
│   ├── store/                         # Zustand stores (navigation, products)
│   ├── types/                         # Single source of truth (generated.ts → index.ts)
│   └── lib/                           # Utilities (image resolver, data normalizer)
└── vite.config.ts                     # Dev proxy → localhost:8000
```

## Code Standards

### Frontend (React/TypeScript)

- **Types**: Import `Product` from `types/index.ts` (the canonical source, generated from backend)
- **State**: Zustand for app state, React Query for server state
- **Styling**: Tailwind CSS with `slate-900` dark theme, `blue-500` accents
- **Components**: Functional components with hooks only (class components only for ErrorBoundary)
- **NEVER** leave a file empty or < 100 bytes

### Backend (Python)

- **Agents**: Trinity Swarm in `unified_agent_orchestrator_v76.py` — do NOT hardcode into Agent classes
- **Skills**: Modular capabilities in `backend/skills/`
- **Tasks**: Async operations via Celery tasks in `tasks.py`
- **Data Models**: Pydantic v2 (`IngestionProductDraft`, `AuditReport`)
- **Imports**: Use `backend.` prefix for all internal imports (e.g., `from backend.celery_config import celery_app`)

### Key Principles

- Agents work autonomously via Trinity Swarm (CommercialScout → OfficialVerifier → ContextualAgent)
- Real-time communication via SSE streams and WebSocket
- Type-safe data flow: Pydantic (backend) → generated.ts (frontend)
- All async work goes through Celery task queue (v8.0)
