# 🚀 Halilit Support Center v7.3 - Architecture & Operations

**Version**: 7.3 (Pure, Consolidated, Production-Ready)  
**Release Date**: February 7, 2026  
**Status**: ✅ **CONSOLIDATION COMPLETE**

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [API Reference](#api-reference)
5. [Learning System](#learning-system)
6. [Troubleshooting](#troubleshooting)

---

## System Overview

### What is Halilit Support Center?

An **AI-powered product catalog intelligence system** using Google's multi-agent architecture (Trinity Swarm) to:

- 🏪 Continuously harvest product data from sources
- 📊 Enrich with vendor specifications and pricing
- 🔍 Validate data quality and compliance
- 🧠 Learn from feedback to improve accuracy
- 📱 Deliver verified data to the frontend in real-time

### Key Statistics

```
✅ Verified Products:    1,219
✅ Brands Indexed:       104
✅ Categories:           8
✅ Data Accuracy:        35.5% (Learning towards 98%)
✅ API Endpoints:        13
✅ Learning Cycles:      30+ completed
✅ Pipeline Phases:      6 (Harvest → Enrich → Tier → Prepare → Validate → Approve)
✅ Agent Types:          3 (CommercialScout, OfficialVerifier, ExternalValidator)
```

---

## Architecture

### System Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER LAYERS (Frontend)                       │
│  Browser (React 18.3.1) → CopilotKit UI with Agent Chat       │
└────────────────────────┬────────────────────────────────────────┘
                         ↓      HTTP / WebSocket
┌────────────────────────────────────────────────────────────────┐
│              API Layer (FastAPI Server - Port 8000)             │
│  5 Core Endpoints: /api/conductor/*                            │
│  7 Skill Endpoints: /api/skills/*                              │
│  5 Auto-Sync Endpoints: /api/sync/*                            │
│  1 Learning Endpoint: /api/learning/health                     │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────────┐
│           Data Access Layer (ConductorDataService)              │
│  ├─ get_unified_catalog() - All verified products              │
│  ├─ get_taxonomy_schema() - Dynamic categories                 │
│  ├─ filter_products() - 7-way filtering                        │
│  └─ get_category_summary() - Navigation data                   │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────────┐
│          Ingestion Pipeline (6 Phases + Learning)               │
│                                                                 │
│  Phase 1: HARVEST      (CommercialScout extracts products)    │
│    ↓                                                            │
│  Phase 2: ENRICH       (OfficialVerifier adds specs)          │
│    ↓                                                            │
│  Phase 3: TIER         (PricingEngine categorizes tiers)       │
│    ↓                                                            │
│  Phase 4: PREPARE      (DisplayEngine formats output)          │
│    ↓                                                            │
│  Phase 5: VALIDATE     (ExternalValidator checks compliance)   │
│    ↓                                                            │
│  Phase 6: APPROVE      (Final verification gate)               │
│    ↓                                                            │
│  Auto-Sync to Frontend (ConductorDataService updates)          │
│    ↓                                                            │
│  Learning Loop (Feedback → Improvements → Next Cycle)          │
│                                                                 │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────────┐
│              Trinity Swarm (3 Gemini 2.0 Agents)                │
│                                                                 │
│  🤖 CommercialScout                                             │
│     → Harvests product data from sources                        │
│     → Categorizes into taxonomy                                 │
│     → Outputs: ProductDraft with price                          │
│                                                                 │
│  🤖 OfficialVerifier                                            │
│     → Enriches with manufacturer specs                          │
│     → Finds official images                                     │
│     → Validates pricing against sources                         │
│     → Outputs: EnrichedProduct with images                      │
│                                                                 │
│  🤖 ExternalValidator                                           │
│     → Audits data completeness                                  │
│     → Checks for compliance issues                              │
│     → Identifies unusual patterns                               │
│     → Outputs: AuditReport with risk score (0-100)              │
│                                                                 │
│  Each Agent Has:                                                │
│   - Memory of past decisions                                    │
│   - Learning from feedback                                      │
│   - Confidence scoring                                          │
│   - Audit trail                                                 │
│                                                                 │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────────────┐
│            Storage (IngestionDatabase + Cache)                  │
│                                                                 │
│  ├─ Approved Products (1,219 verified)                          │
│  ├─ Rejected Products (with reasons)                            │
│  ├─ Agent Decisions (decision log)                              │
│  ├─ Learning Feedback (30+ cycles)                              │
│  ├─ Audit Trail (all operations)                                │
│  └─ Performance Metrics                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. **Data Service** (`conductor_data_service.py`)

- Unified aggregation of all verified products
- 5-minute intelligent caching
- Flexible filtering (brand, category, price, etc.)
- Real-time taxonomy schema

#### 2. **Ingestion Pipeline** (`ingestion/`)

- **Orchestrator**: Coordinates 6-phase pipeline
- **TaxonomyManager**: Manages product categorization
- **DisplayEngine**: Formats output for UI
- **PricingEngine**: Categorizes price tiers
- **IngestionDatabase**: Stores approved products

#### 3. **Trinity Swarm** (`agents/trinity_swarm.py`)

- 3 specialized Gemini 2.0 agents
- Parallel execution with orchestration
- Learning from feedback loops
- Real-time confidence scoring

#### 4. **Learning System** (`agents/learning_system.py`)

- Tracks agent decisions and outcomes
- Analyzes patterns and improvements
- Measures accuracy and confidence
- Generates improvement recommendations

#### 5. **Skills Framework** (`skills/`)

- Modular, verifiable capabilities
- 6 ingestion skills with verification gates
- Reusable across agents and workflows
- Type-safe execution with error handling

#### 6. **Frontend Integration** (`frontend/src/`)

- React 18.3.1 with TypeScript
- 7 useConductor\* hooks for data loading
- Real-time product updates via React Query
- Responsive UI with Tailwind CSS

---

## Quick Start

### Prerequisites

```bash
# Python 3.11+
python3 --version

# Node.js 18+
node --version
npm --version
```

### Installation

```bash
# Clone repository
git clone https://github.com/oripridan-dot/Halilit-Support-Center.git
cd Halilit-Support-Center

# Install Python dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Running the System

**Terminal 1: Backend Server**

```bash
cd /workspaces/Halilit-Support-Center
PYTHONPATH=. python3 backend/server.py
# Listening on http://localhost:8000
```

**Terminal 2: Frontend Dev Server**

```bash
cd /workspaces/Halilit-Support-Center/frontend
npm run dev
# Frontend on http://localhost:5173
# Proxies API to http://localhost:8000
```

**Terminal 3: Run Learning Cycles** (Optional)

```bash
# Run N cycles of learning
PYTHONPATH=. python3 backend/conductor_main.py run-learning --cycles 10
```

---

## API Reference

### Core Data Endpoints

#### `GET /api/conductor/catalog`

Returns all 1,219 verified products.

```bash
curl http://localhost:8000/api/conductor/catalog \
  -H "Content-Type: application/json"
```

**Response**:

```json
{
  "status": "success",
  "data": {
    "products": [
      {
        "id": "fender-stratocaster-2024",
        "name": "Fender Stratocaster",
        "brand": "Fender",
        "category": "Guitars & Bass",
        "price": 799.99,
        "image": "https://...",
        "specs": {...}
      }
    ],
    "total_count": 1219,
    "metadata": {
      "cached": true,
      "cache_ttl": "5 minutes"
    }
  }
}
```

#### `GET /api/conductor/taxonomy`

Returns dynamic category and brand schema.

```bash
curl http://localhost:8000/api/conductor/taxonomy
```

#### `POST /api/conductor/filter`

Filter products with flexible criteria.

```bash
curl -X POST http://localhost:8000/api/conductor/filter \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "Fender",
    "category": "Guitars & Bass",
    "min_price": 500,
    "max_price": 1500
  }'
```

#### `GET /api/conductor/categories`

Get category summary for navigation.

```bash
curl http://localhost:8000/api/conductor/categories
```

#### `GET /api/conductor/refresh`

Force cache refresh (admin only).

```bash
curl http://localhost:8000/api/conductor/refresh \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Skills Endpoints

Run individual ingestion skills:

- `POST /api/skills/harvest` - Extract product data
- `POST /api/skills/enrich` - Add specifications
- `POST /api/skills/tier` - Categorize pricing
- `POST /api/skills/prepare` - Format for display
- `POST /api/skills/validate` - Check compliance
- `POST /api/skills/approve` - Final approval
- `GET /api/skills/status` - Check pipeline status

### Auto-Sync Endpoints

- `GET /api/sync/status` - Current sync status
- `POST /api/sync/products` - Sync specific products
- `GET /api/sync/history` - View sync history
- `POST /api/sync/batch` - Batch synchronization

### Learning Endpoints

- `GET /api/learning/health` - System health metrics
- View audit logs, security status, and performance

---

## Learning System

### How It Works

The learning system continuously improves agent accuracy through **feedback loops**:

```
1. Agent Decision
   ↓ (Logs decision + confidence)

2. Outcome Observed
   ↓ (Product approved/rejected + user feedback)

3. Pattern Analysis
   ↓ (Group similar decisions, find errors)

4. Improvement Application
   ↓ (Update prompts, thresholds, rules)

5. Next Cycle
   ↓ (Apply improvements to new decisions)
```

### Key Metrics

| Metric                     | Baseline | Current       | Target |
| -------------------------- | -------- | ------------- | ------ |
| Accuracy                   | 0%       | 35.5%         | 98%    |
| Cycles Completed           | 0        | 30            | 85     |
| Avg Improvement/Cycle      | -        | +1.14%        | -      |
| Estimated Cycles to Target | -        | ~55 remaining | -      |

### Running Learning Cycles

```bash
# Run single learning cycle
PYTHONPATH=. python3 backend/conductor_main.py run-learning --cycles 1

# Run 10 cycles
PYTHONPATH=. python3 backend/conductor_main.py run-learning --cycles 10

# View learning progress
PYTHONPATH=. python3 backend/conductor_main.py learning

# View audit trail
PYTHONPATH=. python3 backend/conductor_main.py audit --limit 100
```

### CLI Commands

```bash
# Learning status
python3 backend/conductor_main.py learning

# Audit information
python3 backend/conductor_main.py audit

# Security status
python3 backend/conductor_main.py security

# Performance metrics
python3 backend/conductor_main.py performance
```

---

## Frontend Integration

### React Hooks

**`useConductorCatalog()`**

```typescript
const { products, isLoading, error, totalProducts } = useConductorCatalog();
```

**`useConductorFilter(filters)`**

```typescript
const { products, isLoading } = useConductorFilter({
  brand: "Fender",
  max_price: 1000,
});
```

**`useConductorProductsByCategory(category)`**

```typescript
const { products, count, isLoading } =
  useConductorProductsByCategory("Guitars");
```

### Components

- **GalaxyDashboard**: Main product display with 6 category sectors
- **SpectrumModule**: Category-specific product browser
- **ProductPage**: Full product details and specifications

---

## File Structure (v7.3 - Consolidated)

```
backend/
├── server.py                           # FastAPI server (all endpoints)
├── conductor_main.py                   # CLI interface
├── conductor_data_service.py           # Data aggregation layer
├── auto_sync_engine.py                 # Frontend synchronization
├── __init__.py
├── requirements.txt
├── agents/
│   ├── trinity_swarm.py                # 3 Gemini agents + orchestration
│   ├── agent_system.py                 # Agent memory + improvements
│   ├── learning_system.py              # Learning loops + analysis
│   ├── validation_system.py            # Security + audit + feedback
│   └── __init__.py
├── ingestion/
│   ├── __init__.py                     # Orchestrator
│   ├── models.py                       # Pydantic models
│   ├── taxonomy.py                     # TaxonomyManager
│   ├── engine.py                       # DisplayEngine + PricingEngine
│   ├── database.py                     # IngestionDatabase
│   └── trinity_integration.py          # Trinity agent integration
├── skills/
│   ├── __init__.py                     # Skill registry
│   ├── base.py                         # BaseSkill
│   ├── ingestion.py                    # 6 ingestion skills
│   ├── builders.py                     # Frontend builder + other builders
│   └── validation.py                   # Verification gates
├── tests/
│   ├── test_integration.py             # Integration tests
│   ├── test_agents.py                  # Agent tests
│   ├── test_skills.py                  # Skills tests
│   └── test_api.py                     # API endpoint tests
├── data/
│   ├── brands/                         # Product database
│   └── ingestion/                      # Ingestion state
├── logs/
│   ├── conductor.log                   # Main log
│   ├── audit/                          # Audit logs
│   ├── learning_cycles/                # Learning cycle logs
│   └── feedback/                       # Feedback logs
└── __pycache__/

frontend/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.cjs
├── index.html
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── index.css
│   ├── components/
│   │   ├── views/
│   │   │   ├── GalaxyDashboard.tsx
│   │   │   ├── SpectrumModule.tsx
│   │   │   └── ProductPage.tsx
│   │   └── ui/
│   │       └── (UI components)
│   ├── hooks/
│   │   └── useConductorCatalog.ts       # 7 React Query hooks
│   ├── types/
│   │   ├── conductor.ts                # Type definitions
│   │   └── index.ts
│   ├── store/
│   │   └── productStore.ts             # Zustand store
│   └── styles/
│       └── globals.css
└── public/
    └── data/
        └── (Static data files)
```

---

## Code Quality Standards (v7.3)

### Python Standards

- ✅ Type hints on all functions and classes
- ✅ Docstrings for all modules, functions, classes
- ✅ Max 400 lines per file
- ✅ No circular imports
- ✅ Comprehensive error handling
- ✅ All functions used (no dead code)

### TypeScript Standards

- ✅ Strict mode enabled
- ✅ Type definitions for all props and state
- ✅ Component composition over inheritance
- ✅ Proper error boundaries
- ✅ Comprehensive prop validation

### No Duplications

- ✅ Single source of truth for each concept
- ✅ No duplicate function definitions across files
- ✅ Shared utilities in dedicated modules
- ✅ Imported and reused, never copy-pasted

---

## Troubleshooting

### ❌ **Frontend shows "No products"**

**Cause**: Backend not running or data not loaded  
**Solution**:

```bash
# Start backend
PYTHONPATH=. python3 backend/server.py

# Verify API is responding
curl http://localhost:8000/api/conductor/catalog

# Frontend may need refresh (Ctrl+Shift+R)
```

### ❌ **API returns 500 error**

**Cause**: Database error or missing data  
**Solution**:

```bash
# Check logs
tail -f backend/logs/conductor.log

# Rebuild ingestion data
PYTHONPATH=. python3 backend/conductor_main.py build

# Refresh catalog
curl http://localhost:8000/api/conductor/refresh
```

### ❌ **Learning cycles not running**

**Cause**: Agent configuration or API key  
**Solution**:

```bash
# Verify Gemini API key is set
echo $GOOGLE_API_KEY

# Run single cycle with debug
PYTHONPATH=. python3 backend/conductor_main.py run-learning --cycles 1 --verbose

# Check agent status
PYTHONPATH=. python3 backend/conductor_main.py learning
```

### ❌ **Port 8000/5173 already in use**

**Solution**:

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port by editing server.py or vite.config.ts
```

---

## Contributing

### Adding a New Skill

1. Create a subclass of `BaseSkill` in `backend/skills/ingestion.py`
2. Implement `execute()` method
3. Add validation gate
4. Register in `SkillRegistry`
5. Test with endpoint

### Adding API Endpoints

1. Add handler in `backend/server.py`
2. Define request/response Pydantic models
3. Add API documentation
4. Test with curl

### Improving Agent Performance

1. Edit Trinity agent prompts in `backend/agents/trinity_swarm.py`
2. Run learning cycle: `run-learning --cycles 1`
3. View improvements in learning logs
4. If positive, keep changes; if negative, revert

---

## Support

For issues or questions:

1. Check [V7.3_AUDIT_REPORT.md](V7.3_AUDIT_REPORT.md) for system overview
2. Review API logs: `backend/logs/conductor.log`
3. Check learning progress: `python3 backend/conductor_main.py learning`
4. Review [LEARNING_PIPELINE_GUIDE.md](LEARNING_PIPELINE_GUIDE.md) for learning details

---

**Version**: 7.3 (Consolidated, Pure, Production-Ready)  
**Last Updated**: February 7, 2026  
**Status**: ✅ **ACTIVE**
