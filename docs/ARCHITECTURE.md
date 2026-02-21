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
