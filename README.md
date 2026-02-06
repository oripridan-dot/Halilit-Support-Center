# Halilit Support Center v6.1.1 - Spectrum Enhancement

**An AI-Powered Product Catalog System with Trinity Ingestion Pipeline & Enhanced Visualizer**

## 🚀 Quick Start

### Prerequisites

- Python 3.11+, Node.js 18+

### 30-Second Setup

```bash
# Start everything with conductor CLI
python3 backend/conductor_main.py dev

# Or run individually:
# 1. Backend server
python3 backend/conductor_main.py server

# 2. Frontend (in another terminal)
cd frontend && npm run dev
```

## 📊 v6.0 Architecture - Single Pipeline

**The v6.0 system has ONE workflow:**

```
RAW DATA
   ↓
[INGESTION ORCHESTRATOR - 6 PHASES]
   ├─ Phase 1: HARVEST      (Normalize raw data → IngestionProductDraft)
   ├─ Phase 2: ENRICH       (Taxonomy classification)
   ├─ Phase 3: TIER         (Pricing strategy)
   ├─ Phase 4: PREPARE      (Display properties)
   ├─ Phase 5: VALIDATE     (Compliance checks)
   └─ Phase 6: APPROVE      (Final output)
   ↓
[CONDUCTOR SYNC]
   ├─ Extract approved products
   └─ Write to frontend/public/data/*.json
   ↓
[FRONTEND DISPLAY]
   ├─ GalaxyDashboard (category browser)
   ├─ SpectrumModule (product spectrum with brand swimlanes)
   └─ ProductPage (full product analysis)
```

## 📦 Data Flow - v6.0 Only

1. **Source**: `backend/data/brands/{brand}/products.json`
2. **Process**: `backend/ingestion/orchestrator.py` (6 phases)
3. **Output**: `backend/data/ingestion/products/{brand}/approved_products.json`
4. **Sync**: `backend/ingestion_to_frontend.py` → `frontend/public/data/{brand}.json`
5. **Display**: React components load from frontend/public/data/

## 🎯 Conductor CLI - Central Hub

All operations go through conductor:

```bash
# Ingestion
python3 backend/conductor_main.py ingest [brand]  # Run pipeline
python3 backend/conductor_main.py test [brand]    # Test a brand

# Synchronization
python3 backend/conductor_main.py sync            # Sync to frontend
python3 backend/conductor_main.py build           # Full build (ingest + sync)

# Development
python3 backend/conductor_main.py dev             # Start dev environment
python3 backend/conductor_main.py server          # Start API server
python3 backend/conductor_main.py catalog         # Show statistics

# Help
python3 backend/conductor_main.py --help
```

## 📊 System Components - v6.0 Only

### Backend Structure

```
backend/
├── ingestion/                 # ⭐ ONLY PIPELINE
│   ├── orchestrator.py        # 6-phase processor
│   ├── data_models.py         # IngestionProductDraft
│   ├── taxonomy_manager.py    # Category system
│   ├── pricing_engine.py      # Price tiers
│   ├── display_engine.py      # Display roles
│   ├── trinity_integration.py # Agent bridge
│   └── test_real_data_pipeline.py
├── ingestion_to_frontend.py    # Sync to frontend
├── conductor_main.py           # CLI entry point
├── conductor_orchestrator.py   # File watcher (optional)
├── server.py                   # FastAPI (minimal)
├── agents/
│   ├── trinity_swarm.py        # 3 AI agents
│   └── ...
└── data/
    ├── brands/                 # Source data
    └── ingestion/              # Output database
```

### Frontend Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── views/
│   │   │   ├── GalaxyDashboard.tsx (Screen 1: Category browser)
│   │   │   ├── SpectrumModule.tsx  (Screen 2: Product spectrum with swimlanes)
│   │   │   └── ProductPage.tsx     (Screen 3: Full product analysis)
│   │   └── ...
│   ├── lib/
│   │   ├── catalogLoader.ts
│   │   ├── categoryConsolidator.ts
│   │   └── ...
│   └── ...
└── public/data/
    ├── roland.json        # 648 products
    ├── nord.json          # from ingestion
    ├── moog.json
    └── ...
```

## ✅ System Status

- ✓ v6.0 Ingestion Pipeline - 6-phase orchestration
- ✓ Single unified data model (IngestionProductDraft)
- ✓ One workflow entry point (conductor_main.py)
- ✓ All legacy v5.x code removed
- ✓ 648 products ingested and synced
- ✓ Minimal FastAPI server
- ✓ v6.0-only documentation

## 📖 Documentation

## ⚙️ Configuration

### Environment Variables

No special setup needed for v6.0 - it works with local data files.

Optional:

```bash
PYTHONPATH=.                    # For running Python scripts
GOOGLE_API_KEY=...             # For Trinity AI agents (optional)
```

### Data Sources

Products are sourced from:

- `backend/data/brands/{brand}/products.json` - Source data
- `backend/data/ingestion/products/{brand}/approved_products.json` - Ingestion output
- `frontend/public/data/{brand}.json` - Frontend display format

## 🧪 Testing

```bash
# Test the complete pipeline with real data
python3 backend/ingestion/test_real_data_pipeline.py

# Test a single brand
python3 backend/ingestion/test_real_data_pipeline.py --single Nord
```

## 📈 Scaling

To add more brands:

1. Add products to `backend/data/brands/{brand}/products.json`
2. Run: `python3 backend/conductor_main.py ingest {brand}`
3. Sync: `python3 backend/conductor_main.py sync`

## 🐛 Troubleshooting

**Issue**: Frontend showing no products

- Solution: Run `python3 backend/conductor_main.py build`

**Issue**: Missing ingestion output

- Solution: Verify data file exists: `ls backend/data/brands/*/products.json`

**Issue**: Port already in use

- Backend: Change port in `backend/server.py`
- Frontend: Vite will auto-increment port

## 📝 License

Copyright 2024 - Halilit Support Center

- **[README.md](README.md)** - This file (Quick start & overview)
- **[backend/ingestion/README.md](backend/ingestion/README.md)** ⭐ **Master Documentation Index** - Complete v6.0 ingestion pipeline docs
- **[backend/ingestion/QUICKSTART.md](backend/ingestion/QUICKSTART.md)** - 30-minute developer guide
- **[backend/ingestion/ARCHITECTURE.md](backend/ingestion/ARCHITECTURE.md)** - Complete technical architecture

### v6.0 Ingestion Pipeline Documentation

- **[backend/ingestion/VISUAL_REFERENCE.md](backend/ingestion/VISUAL_REFERENCE.md)** - Visual diagrams and flows
- **[backend/ingestion/IMPLEMENTATION_SUMMARY.md](backend/ingestion/IMPLEMENTATION_SUMMARY.md)** - What was delivered
- **[INGESTION_REFACTOR_SUMMARY.txt](INGESTION_REFACTOR_SUMMARY.txt)** - Executive summary

### Legacy Documentation (Reference)

- **[docs/](docs/)** - Previous release documentation
- **[docs/archived/](docs/archived/)** - v5.3.0 and earlier

## 🧪 Testing

```bash
python -m pytest backend/tests/test_adk_coverage.py -v
```

## 🛠️ Stack

**Frontend**: React 18.3.1 + CopilotKit + TypeScript + Vite + Tailwind CSS  
**Backend**: Python 3.11+ + FastAPI + Google Gemini 2.0 Flash + Pydantic v2  
**Agents**: Trinity Swarm (3 autonomous agents with 6-phase ingestion pipeline)  
**Ingestion**: Universal taxonomy (8 categories, 32 subcategories), pricing strategy engine, display preparation  
**Spectrum Adapter**: Converts IngestionProductDraft to display format with price tiers  
**Database**: JSON-based file storage with ISO timestamps, analytics, and history tracking

See [backend/ingestion/README.md](backend/ingestion/README.md) for full architecture details.
