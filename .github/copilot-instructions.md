# Repository Instructions & Context (v8.4)

## ⚠️ THE FUNDAMENTAL LAW — Three Source Rules (backend/source_rules.py)

**These rules are the FOUNDATION of the entire application. Without them, the app has NO VALUE.**

### The Three Authorized Data Sources

| # | Scout | Source | Owns | Rules |
|---|-------|--------|------|-------|
| 1 | **CommercialScout** | Halilit.com | Golden List, Prices (IL+Eilat), SKUs, Product existence | If not on Halilit → does NOT exist. Prices ONLY from here. |
| 2 | **OfficialScout** | Brand's official product page | Titles, Descriptions, Specs, Media, Documentation | Single source of truth for product knowledge. ONLY from official brand page. |
| 3 | **ContextualScout** | 3+ trusted review websites | Pros/Cons, Real-world experience, User insights, Ratings | AT LEAST 3 well-trusted review sites per product. Product-specific only. |

### Zero Tolerance Policy
- **NO synthesized/generated data** — empty fields are BETTER than fake fields
- **NO mock data** in any pipeline stage
- **NO AI-generated specs** presented as real specs
- **NO AI-generated reviews** presented as real reviews
- **NO fallback to simulated data** — if scraping fails, product stays incomplete
- Each source has **strict field ownership** — only the owner can set its fields
- **Cross-validation required** — all 3 sources must agree on product identity
- Confidence score requires data from **ALL 3 sources** to reach "HIGH"

### How It Works
1. CommercialScout scrapes Halilit → produces the **Golden List** (what exists + prices)
2. OfficialScout uses the Golden List → scrapes brand pages for **real specs, media, docs**
3. ContextualScout uses the Golden List → fetches **real reviews from 3+ trusted sites**
4. Cross-validation engine checks consistency across all 3 sources
5. Quality gates **BLOCK** any product with synthetic data

**See `backend/source_rules.py` for the full enforcement code.**

## Project Overview

**Halilit Support Center v8.4** — AI-powered product catalog system for musical instruments.

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
├── source_rules.py                # ⚠️ THE LAW — Three Source Rules (read first!)
├── server.py                      # FastAPI server + enriched catalog API
├── celery_config.py               # Celery + Redis configuration
├── tasks.py                       # Distributed agent tasks
├── unified_agent_orchestrator.py  # Trinity Swarm (CommercialScout, OfficialScout, ContextualScout)
├── unified_data_service.py        # Product normalization & data pipeline
├── unified_quality_gates.py       # Audit, security gates, SOURCE RULES gate, feedback engine
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

- **THE LAW**: Three Source Rules in `backend/source_rules.py` govern ALL data — read it first
- Agents work autonomously via Trinity Swarm (CommercialScout → OfficialScout → ContextualScout)
- **CommercialScout** = Halilit.com only → Golden List, prices, SKUs (IMMUTABLE)
- **OfficialScout** = Brand official pages only → specs, descriptions, media, docs
- **ContextualScout** = 3+ trusted review sites → real reviews, pros/cons, insights
- **ZERO TOLERANCE** for synthetic/mock/AI-generated data masquerading as real
- Cross-validation engine verifies consistency across all 3 sources
- SourceRulesGate in quality gates **BLOCKS** products with fake data
- Catalog API returns enriched data: images (hero+gallery), descriptions, merged specs, quality scores
- Real-time communication via SSE streams and WebSocket
- Type-safe data flow: Pydantic (backend) → generated.ts (frontend)
- All async work goes through Celery task queue
- Generated data is gitignored — only source code and static assets are tracked
