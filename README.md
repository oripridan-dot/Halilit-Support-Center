# Halilit Support Center v7.2 - Unified Pipeline & Enhanced UI

**An AI-Powered Product Catalog System with Trinity Ingestion Pipeline & Galaxy UI**

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

## 📊 v7.2 Architecture - Unified Pipeline

**The system is driven by a single Conductor Pipeline:**

```
RAW DATA (backend/data/brands/)
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
[FRONTEND DISPLAY (v7.2)]
   ├─ 🌌 GalaxyDashboard (Category browser)
   ├─ 🌈 SpectrumModule (Brand swimlanes)
   └─ 📄 ProductPage (Unified Product Detail View)
```

## 📦 Data Flow

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

## 📊 System Components

### Backend Structure

```
backend/
├── ingestion/                 # ⭐ CORE PIPELINE
│   ├── orchestrator.py        # 6-phase processor
│   ├── data_models.py         # IngestionProductDraft
│   ├── taxonomy_manager.py    # Category system
│   ├── pricing_engine.py      # Price tiers
│   ├── display_engine.py      # Display roles
│   ├── trinity_integration.py # Agent bridge
│   └── test_real_data_pipeline.py
├── ingestion_to_frontend.py    # Sync to frontend
├── conductor_main.py           # CLI entry point
├── server.py                   # FastAPI (v7.2)
├── agents/                     # AI Agent Logic
└── data/                       # Data Store
```

### Frontend Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── views/
│   │   │   ├── GalaxyDashboard.tsx # Home View
│   │   │   ├── SpectrumModule.tsx  # Brand/Spectrum View
│   │   │   └── ProductPage.tsx     # Product Detail View
│   │   └── ...
│   ├── lib/
│   │   ├── catalogLoader.ts
│   │   └── ...
│   └── ...
└── public/data/
    ├── roland.json
    ├── nord.json
    └── ...
```

## ✅ System Status (v7.2)

- ✓ **Unified Ingestion Pipeline** (6-Phase)
- ✓ **Conductor CLI** for all operations
- ✓ **v7.2 UI Architecture**: Galaxy → Spectrum → ProductPage
- ✓ **Legacy Cleanup**: Removed v5/v6 deprecated components (`ProductPopInterface`)
- ✓ **API**: FastAPI v7.2 with CopilotKit placeholder
- ✓ **Data**: 648 products fully ingested and synced

## 📖 Documentation

- **[backend/ingestion/README.md](backend/ingestion/README.md)** ⭐ **Master Pipeline Docs**
- **[DEVELOPER_STANDARDS.md](DEVELOPER_STANDARDS.md)** - Code standards & best practices
- **[backend/ingestion/QUICKSTART.md](backend/ingestion/QUICKSTART.md)** - Developer guide

## ⚙️ Configuration

### Environment Variables

No special setup needed for local development.

Optional:
```bash
PYTHONPATH=.                    # For running Python scripts
GOOGLE_API_KEY=...             # For Trinity AI agents (optional)
```

## 🧪 Testing

```bash
# Run comprehensive tests
python3 -m pytest backend/tests/test_adk_coverage.py -v
```

## 📝 License

Copyright 2024 - Halilit Support Center
