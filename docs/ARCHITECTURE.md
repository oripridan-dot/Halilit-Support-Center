# Halilit Support Center — Architecture (v9.7.6)

> **Dark Factory · Level 6** — Spec-driven, autonomous, self-healing, self-disrupting.

---

## System Overview

JIT (Just-in-Time) product intelligence platform for musical instruments. Three authorised data sources feed a Conductor pipeline; a FastAPI backend serves the catalog; a React SPA provides the Operator Console.

```
[Halilit.com]  → Commercial (prices, SKUs, stock)
[Brand pages]  → Official (specs, media, descriptions)
[Review sites] → Contextual (reviews, pros/cons)
       ↓
  Conductor CLI  →  product_normalizer.py  →  ProductGraph
       ↓
  FastAPI (port 8000)  →  React SPA (port 5173)
       ↓
  Operator Console  ( Dashboard | Inventory | ProductDetail )
```

---

## Frontend

| Layer | Tech |
|-------|------|
| Framework | React 18 + Vite 5 + TypeScript 5 |
| State (app) | Zustand 5 (`store/navigationStore.ts`) |
| State (server) | React Query 5 (`@tanstack/react-query`) |
| Styling | Tailwind CSS 3.4 (dark theme: slate-900, blue-500) |
| Motion | Framer Motion |
| Telemetry | Sovereign Nerve (`src/telemetry.ts`) — zero-vendor crash reporter |

### Views (3)

- **DashboardView** — Key metrics, ingestion status, quick links.
- **InventoryView** — Searchable grid with debounced search, sort, CFP filter, pagination.
- **ProductDetailView** — Header (image, title, SKU, brand, pricing, stock) → cockpit tabs (Ecosystem, Specifications, History, JIT Intelligence).

### Key Hooks

| Hook | Source | Purpose |
|------|--------|---------|
| `useConductorCatalog` | `/api/conductor/catalog` | Paginated product catalog |
| `useJITIntelligence` | `/api/jit/product/{id}` (SSE) | Streaming product intelligence |
| `useDashboardStats` | `/api/dashboard/stats` | Dashboard KPIs |

---

## Backend

| Layer | Tech |
|-------|------|
| Runtime | Python 3.11+ |
| API | FastAPI + Uvicorn |
| AI | `google-genai` SDK, `gemini-2.0-flash` |
| Models | Pydantic v2 |
| HTTP | httpx (async) + requests (sync) |

### Key Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/conductor/catalog` | Paginated product catalog |
| `GET /api/jit/product/{id}` | SSE streaming JIT intelligence |
| `GET /api/dashboard/stats` | Dashboard metrics |
| `GET /api/health` | Liveness check |
| `GET /api/health/deep` | Deep organ check (catalog, JIT cache, memory) |
| `POST /api/webhooks/sentry` | Sovereign Nerve crash ingestor |

### Key Modules

| Module | Purpose |
|--------|---------|
| `server.py` | FastAPI app, catalog API, JIT, health |
| `product_normalizer.py` | `build_catalog()` — normalise JSON → catalog + graph |
| `product_graph.py` | ProductGraph (families, relationships) |
| `jit_agent.py` | On-demand intelligence (SSE streaming, 7-day file cache) |
| `source_rules.py` | ⚠️ THE LAW — Three Source Rules enforcement |
| `conductor_main.py` | CLI: skeleton-sync, enrich, dev, server |
| `unified_data_service.py` | Sync engine |

---

## The Dark Factory (AI Agent Stack)

The factory is a multi-agent system. Agents are Python modules in `backend/factory/`.

### Level 6 — Agent Roster

| Agent | File | Role |
|-------|------|------|
| **Chief** v4.2 | `chief_agent.py` | Strategic router — translates intent to delegation queue |
| **Builder** | `builder_agent.py` | Spec → code materialisation |
| **Tech Lead** | `tech_lead_agent.py` | Pre-flight APPROVE/VETO gate (Bicameral Governance) |
| **Product Manager** | `product_manager.py` | Agile PM — reads `docs/ROADMAP.md`, surfaces priority |
| **Telemetry Agent** | `telemetry_agent.py` | Sovereign Nerve Reflex Arc — drafts HOTFIX_PROPOSAL on crash |
| **Darwin Agent** | `darwin_agent.py` | Architectural Red Team — hypothesis mutation in Shadow Cell |
| **Shadow Cell** | `shadow_cell.py` | Ephemeral isolated repo sandbox (outside workspace) |
| **Active Sonar** | `active_sonar.py` | Synthetic stack monitoring — pings backend + frontend + halilit.com |
| **Heartbeat Daemon** v2 | `heartbeat_daemon.py` | Nightly catalog scan + briefing + Darwin cycle |
| **Repo Agent** | `repo_agent.py` | Git branch management (evo/, sandbox/) |
| **Oracle Agent** | `oracle_agent.py` | Cold-boot rescue Oracle (LLM lifeline) |
| **Patch Agent** | `patch_agent.py` | Udiff-based surgical patch application |

### Execution Consoles

| Console | Entry | Purpose |
|---------|-------|---------|
| **Nexus** | `python nexus.py` | Interactive REPL Swarm Console — real-time Chief → Swarm |
| **Factory CLI** | `python factory.py <cmd>` | Unified lifecycle CLI |
| **MCP Server** | `backend/mcp/servers/factory_mcp_server.py` | MCP protocol v6.1.0, 50+ tools |

---

## Darwin Protocol (Level 10)

Architectural self-disruption loop:

1. Darwin Agent formulates a hypothesis about a bottleneck.
2. Spins up a **Shadow Cell** — isolated repo clone outside the workspace.
3. Mutates the architecture inside the cell.
4. Benchmarks old vs. new.
5. Destroys the cell.
6. Writes `PARADIGM_SHIFT_PROPOSAL.md` if improvement ≥ 20%.

Trigger: `python factory.py darwin "hypothesis" [--live]`

---

## Bicameral Governance

Every Builder-generated change must pass the **Tech Lead pre-flight gate**:

- **Tech Lead reviews** the diff for spec compliance, security, and data-source correctness.
- Returns **APPROVE** (merge), **VETO** (block + reason), or **REVISE** (rework instructions).
- Chiefs cannot override a Tech Lead VETO without a new spec update.

---

## Three Source Rules (THE LAW)

Every product field has exactly one authorised owner:

| Source | Owner | Fields |
|--------|-------|--------|
| **Commercial** | Halilit.com | Prices, SKUs, stock, product existence |
| **Official** | Brand official pages | Titles, specs, media, descriptions, docs |
| **Contextual** | 3+ trusted review sites | Reviews, pros/cons, ratings |

**ZERO TOLERANCE:** No synthetic, mock, or AI-generated data presented as real.
**See:** `backend/source_rules.py`

---

## Catalog Pipeline

```
Halilit.com scrape  →  skeleton_sync.py    →  frontend/public/data/*.json
Brand pages scrape  →  ingestion/           →  data/brands/*.json
Review sites        →  ingestion/           →  data/contextual/
                                    ↓
              product_normalizer.build_catalog()
                                    ↓
              ProductGraph (families, relationships)
                                    ↓
              /api/conductor/catalog  ←  React Query
```

Catalog is cached at `backend/data/catalog_cache.json.gz` (24 h TTL).

---

## Specs Structure

```
specs/
  interface/        ← CANONICAL UI SPECS (9 files)
  data_pipeline/    Ingestion rules, relationship logic
  behavior/         Search scenarios (Playwright)
  01_data/          Compliance, halilit_api, official_scout
  pricing_logic.md
  strategy/         Master plan, evolution proposals
  genomes/          Organism YAML specs (Bio-Swarm)
  archive/          Legacy / superseded specs (read-only)
```

---

## Runtime Artifacts (gitignored)

| File | Generated by |
|------|-------------|
| `HEARTBEAT.md` | `heartbeat_daemon.py` nightly |
| `DAILY_BRIEFING.md` | `tech_lead_agent.py` nightly |
| `PARADIGM_SHIFT_PROPOSAL.md` | `darwin_agent.py` on ≥ 20% gain |
| `docs/HOTFIX_PROPOSAL_*.md` | `telemetry_agent.py` on production crash |
| `backend/data/darwin_last_run.txt` | Heartbeat daemon |
| `halilit_shadow_cell/` | `shadow_cell.py` during experiment |

---

# Factory Pipeline — Halilit Support Center (v9.7.6)

> This document describes the end-to-end pipeline from raw data to Operator Console, and how `factory.py` orchestrates it.

---

## factory.py — Unified CLI

`factory.py` is the single entry point for all factory lifecycle operations.

```bash
source .venv/bin/activate
python factory.py <command> [args]
```

### Command Reference

| Command | Args | Purpose |
|---------|------|---------|
| `start` | `[--rebuild]` | Launch backend (8000) + frontend (5173) |
| `status` | — | Environment health: API key, venv, agent presence, spec count |
| `design` | `"description" [category]` | Architect Agent: generate spec → `specs/interface/<slug>.md` |
| `build` | `<spec_path>` | Builder Agent: materialise spec → code (Tech Lead reviewed) |
| `darwin` | `"hypothesis" [--live]` | Darwin Agent: mutation experiment in Shadow Cell |
| `heal` | — | Watchdog: scan errors, auto-repair (up to 3 cycles) |
| `diagnose` | — | Scan TypeScript/Python errors, no changes |
| `commit` | — | Stage all + semantic git commit message |
| `chief-plan` | `["instruction"]` | Chief: prioritised task queue from ROADMAP + current state |
| `scout` | `<brand_or_url>` | Official Scout: scrape brand page, enrich catalog |
| `init` | — | One-time: create data folder structure |

---

## Nexus — Interactive Swarm Console

For real-time multi-agent dialogue:

```bash
python nexus.py
```

**Nexus commands:**

```
> run sonar                          # Active Sonar synthetic check
> run darwin "hypothesis"            # Darwin mutation experiment
> build specs/interface/02_*.md     # Builder materialise + Tech Lead review
> consult product_manager           # PM: backlog, current sprint
> chief-plan "focus on search"      # Chief: task queue with instruction
> heal                               # Watchdog repair cycle
> commit                             # Semantic commit
> status                             # Environment health
> exit                               # Quit Nexus
```

---

## Data Pipeline

### Stage 1 — Commercial Ingestion (Halilit.com)

```
ingestion/halilit_page_scraper.py
    ↓
skeleton_sync.py  →  frontend/public/data/<brand>.json
```

Produces the **Golden List** — authoritative SKUs, prices (IL + Eilat), stock.

### Stage 2 — Official Enrichment (Brand Pages)

```
ingestion/official_scout.py
    ↓
backend/data/brands/<brand>_official.json
```

Adds: titles, descriptions, specs, media, documentation. Official source only — no AI generation.

### Stage 3 — Contextual Enrichment (Review Sites)

```
ingestion/contextual_scout.py
    ↓
backend/data/contextual/<brand>_reviews.json
```

3+ trusted review sites. Real reviews, real pros/cons. Zero AI-generated content.

### Stage 4 — Normalisation + Graph Build

```
product_normalizer.build_catalog()
    ↓
ProductGraph (product_graph.py)
    ↓
backend/data/catalog_cache.json.gz   (24 h TTL)
    ↓
GET /api/conductor/catalog
```

### Stage 5 — JIT Intelligence (On-Demand)

```
GET /api/jit/product/{id}  (SSE stream)
    ↓
jit_agent.py  →  Gemini 2.0 Flash
    ↓
backend/data/jit_cache/<id>.json  (7-day TTL)
```

---

## Conductor CLI (Legacy Direct Access)

```bash
PYTHONPATH=. python backend/conductor_main.py <subcommand>
```

| Subcommand | Purpose |
|------------|---------|
| `dev` | Start backend + frontend together |
| `server` | Start backend only |
| `skeleton-sync` | Re-sync Golden List from Halilit.com |
| `commercial-ingest` | Full commercial ingestion |
| `enrich` | Official + contextual enrichment pass |
| `sync` | Run full sync pipeline |

---

## Catalog Cache

- Location: `backend/data/catalog_cache.json.gz`
- TTL: 24 hours (auto-rebuilt by Heartbeat Daemon nightly)
- Force rebuild: `python factory.py start --rebuild`

---

## Three Source Rules (Pipeline Enforcement)

`backend/source_rules.py` enforces field ownership at every pipeline stage:

| Source | Fields it may write |
|--------|-------------------|
| Commercial | `sku`, `price_il`, `price_eilat`, `in_stock`, `commercial_url` |
| Official | `title`, `description`, `specs`, `images`, `documents` |
| Contextual | `reviews`, `pros`, `cons`, `expert_rating`, `user_rating` |

Any cross-source write raises `SourceViolationError`. No exceptions.
