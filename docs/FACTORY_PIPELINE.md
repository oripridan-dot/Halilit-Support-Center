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
