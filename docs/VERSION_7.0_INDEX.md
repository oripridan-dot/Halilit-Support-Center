# HALILIT SUPPORT CENTER v7.0 - UNIFIED DOCUMENTATION INDEX

**Last Updated**: February 6, 2026  
**Status**: ✅ PRODUCTION READY  
**System Version**: 7.0 - Unified Data Pipeline & ADK Integration

---

## 🎯 Quick Start

### For Users: Running the System

```bash
# Start Backend (Python + Trinity Swarm)
cd /workspaces/Halilit-Support-Center/backend
PYTHONPATH=. python3 server.py
# → Listening on http://localhost:8000

# Start Frontend (React + CopilotKit)
cd /workspaces/Halilit-Support-Center/frontend
npm run dev
# → Listening on http://localhost:5173
```

### For Developers: Architecture Overview

1. **3 Screens, 1 Data Source**
   - GalaxyDashboard (category browse)
   - SpectrumModule (price spectrum)
   - ProductPage (full analysis)
   - All consume: `catalogLoader.ts`

2. **Trinity Agent System (Backend)**
   - CommercialScout → OfficialVerifier → ExternalValidator
   - All built with Google Gemini 2.0 Flash
   - Orchestrated via `backend/agents/trinity_swarm.py`

3. **Type-Safe Data Pipeline**
   - Unified `Product` type (TypeScript)
   - Pydantic v2 validation (backend)
   - Skills protocol for safety

---

## 📚 Documentation Structure

### Tier 1: Core System Architecture

These documents explain how the system works:

#### 1. **[SYSTEM_AUDIT_v7.0.md](./SYSTEM_AUDIT_v7.0.md)** ⭐ START HERE

- **Purpose**: Complete system overview
- **Contents**:
  - Architecture breakdown
  - File structure summary
  - Technology stack
  - Operational features
  - Debugging guide
- **Best For**: New developers, system understanding
- **Length**: Comprehensive (2,500+ words)

#### 2. **[UNIFIED_DATA_PIPELINE_v7.md](./UNIFIED_DATA_PIPELINE_v7.md)**

- **Purpose**: Data flow & schema definition
- **Contents**:
  - Complete data architecture diagram
  - UnifiedProduct type definition
  - Data validation gates
  - Conductor verification system
  - Type mapping (frontend ↔ backend)
- **Best For**: Understanding data consistency
- **Length**: Detailed (513 lines)

#### 3. **[IMPLEMENTATION_COMPLETE_v7.md](./IMPLEMENTATION_COMPLETE_v7.md)**

- **Purpose**: What was implemented in v7.0
- **Contents**:
  - Screen synchronization
  - Field consolidation
  - Conductor enhancement
  - Type safety improvements
  - Naming consistency changes
- **Best For**: Upgrade path from v6.x
- **Length**: Technical (452 lines)

---

### Tier 2: Security & Production Readiness

#### 4. **[SECURITY_SHIELD_v7.md](./SECURITY_SHIELD_v7.md)**

- **Purpose**: Security architecture
- **Contents**:
  - Skills protocol implementation
  - Verification gates
  - Data protection
  - Agent isolation
  - Type safety enforcement
- **Best For**: Security review, compliance
- **Length**: Detailed (300+ lines)

#### 5. **[PRODUCTION_READY_CERTIFICATION.md](./PRODUCTION_READY_CERTIFICATION.md)**

- **Purpose**: Production readiness checklist
- **Contents**:
  - Feature completeness check
  - Performance benchmarks
  - Error handling verification
  - Documentation validation
  - Deployment prerequisites
- **Best For**: Pre-deployment review
- **Length**: Comprehensive (300+ lines)

---

### Tier 3: Implementation Details

#### 6. **[CONDUCTOR_DAEMON_ARCHITECTURE.md](./CONDUCTOR_DAEMON_ARCHITECTURE.md)**

- **Purpose**: Conductor validation system details
- **Contents**:
  - Conductor role in data pipeline
  - Verification gates implementation
  - Integration testing framework
  - Maintenance workflows
  - Automated validation
- **Best For**: Data validation deep-dive
- **Length**: Technical (12KB)

#### 7. **[CONDUCTOR_EXECUTION_SUMMARY.md](./CONDUCTOR_EXECUTION_SUMMARY.md)**

- **Purpose**: Execution logs and validation results
- **Contents**:
  - Validation runs
  - Error logs
  - Performance metrics
  - Test results
- **Best For**: Runtime debugging
- **Length**: Reference (8.7KB)

---

### Tier 4: Feature Documentation

#### 8. **[SPECTRUM_v5.4.0_RELEASE.md](./SPECTRUM_v5.4.0_RELEASE.md)**

- **Purpose**: SpectrumModule (TierBar) features
- **Contents**:
  - Price tier grouping
  - Brand-based filtering
  - UI/UX patterns
  - Integration points
- **Best For**: Understanding price spectrum
- **Length**: Feature guide (8.4KB)

---

### Tier 5: Legacy & Administrative

#### 9. **[CLEANUP_MANIFEST.md](./CLEANUP_MANIFEST.md)**

- **Purpose**: Historical cleanup operations
- **Contents**: Previous schema migrations, field removals
- **Best For**: Historical context only
- **Status**: Reference only (don't implement without review)

#### 10. **[v6_hierarchy.md](./v6_hierarchy.md)**

- **Purpose**: v6.x taxonomy structure
- **Contents**: Category hierarchy from v6
- **Best For**: Understanding legacy structure
- **Status**: Reference/comparison

#### 11. **[v6_spectrum_enhancement.md](./v6_spectrum_enhancement.md)**

- **Purpose**: v6 spectrum improvements
- **Contents**: v6 enhancements that became v7 baseline
- **Best For**: Upgrade history
- **Status**: Reference/comparison

---

## 🔄 Related System Documentation

**Note**: These files are not part of the main documentation but provide additional context:

- **[INDEX.md](./INDEX.md)** - Legacy index (to be deprecated)
- **Root-level docs**:
  - `/DATA_PIPELINE_FIX_SUMMARY.md` - v6.1 fixes
  - `/SYSTEM_STATUS_REPORT.md` - v6.1 status
  - `/RESOLUTION_REPORT.md` - Issue resolutions
  - `/IMPLEMENTATION_SUMMARY.md` - v6 summary

---

## 📊 System Components Map

### Frontend (React 18 + CopilotKit)

```
frontend/src/
├── App.tsx                           # Main router
├── components/
│   ├── views/
│   │   ├── GalaxyDashboard.tsx      # Screen 1: Category browse
│   │   ├── SpectrumModule.tsx       # Screen 2: Price spectrum
│   │   ├── ProductPage.tsx          # Screen 3: Full analysis
│   ├── GlobalSearch.tsx             # Search interface
│   ├── ui/                          # Base components
│   └── smart-views/                 # Advanced displays
├── hooks/
│   ├── useCategoryCatalog.ts        # Categories + products
│   ├── useGalaxyData.ts             # Galaxy stats
│   ├── useSpectrumData.ts           # Spectrum/tiers
│   ├── useBrandCatalog.ts           # Brand products
│   └── useCategoryProducts.ts       # Category products
├── lib/
│   ├── catalogLoader.ts             # ⭐ UNIFIED DATA SOURCE
│   ├── dataNormalizer.ts            # Type conversions
│   ├── schemas.ts                   # Type definitions
│   └── [utilities]
├── types/
│   ├── index.ts                     # Product interface
│   ├── Product.ts                   # Product type
│   └── [other types]
└── store/
    └── navigationStore.ts           # Navigation state
```

**Key File**: `lib/catalogLoader.ts` - All data flows through this

### Backend (Python + FastAPI + Trinity Swarm)

```
backend/
├── server.py                        # FastAPI entry point
├── agents/
│   ├── trinity_swarm.py             # ⭐ Trinity: CommercialScout +
│   │                                #   OfficialVerifier + ExternalValidator
│   ├── context_manager.py           # Agent memory
│   ├── auto_context.py              # Context enrichment
│   └── [workflows, memory]
├── ingestion/
│   ├── orchestrator.py              # Pipeline coordination
│   ├── data_models.py               # Pydantic models
│   ├── pricing_engine.py            # Price normalization
│   ├── taxonomy_manager.py          # Category management
│   └── [other pipeline]
├── skills/
│   ├── base_skill.py                # Skill interface
│   ├── frontend_builder.py          # Component builder
│   └── devagent_skills.py           # Dev utilities
├── workflow/
│   ├── engine.py                    # ⭐ STATE MACHINE for verification
│   └── maintenance_workflows.py     # Maintenance
└── requirements.txt                 # Dependencies
```

**Key Files**:

- `agents/trinity_swarm.py` - Agent orchestration
- `workflow/engine.py` - Verification state machine

---

## 🔑 Key Concepts

### 1. Unified Data Source (The "Single Source of Truth")

All three screens read from the same place:

```typescript
// All screens use this:
const products = await catalogLoader.loadAllProducts();

// One screen (ProductPage) also uses:
const product = await catalogLoader.findProductById(id);
```

This ensures **perfect consistency** - when data changes, all screens see the same change.

### 2. Trinity Agent System (The ADK Backend)

Three Gemini agents work in sequence:

```
CommercialScout          OfficialVerifier        ExternalValidator
(harvest prices)    →    (add specs/images)   →   (audit & score)
     ↓                        ↓                        ↓
ProductDraft with      ProductDraft with        AuditReport with
prices, basic info     enriched specs,           compliance score
                       manufacturer data         (0-100)
```

### 3. Unified Product Type (The Data Contract)

Both frontend and backend use the same type:

```typescript
// Frontend sees:
type Product = UnifiedProduct

// Backend defines:
class UnifiedProduct(BaseModel):  # Pydantic
  id: str
  name: str
  brand: str
  price_il: float
  pricing_tier: str
  images: List[ImageAsset]
  specifications: Dict
  taxonomy: Dict
  ...
```

### 4. Skills Protocol (The Safety Layer)

Modular, verified capabilities prevent corruption:

```python
# Before: hardcoded in agents
# Now: Verified skills with gates

skill = FrontendBuilderSkill()
success = skill.verify_and_execute(config)
# Returns: success=True only if file_exists && size > 0
```

### 5. State Machine (The Verification Engine)

Complex operations enforce verification:

```python
workflow = FeatureBuildWorkflow()
# Enforces: Plan → Code → Verify

# Each phase checks:
# - Plan: Requirements valid?
# - Code: Implementation correct?
# - Verify: File integrity OK?
```

---

## 🚀 Common Tasks

### Task: Add a New Product

1. Add JSON to `/frontend/public/data/brands/{brand}.json`
2. Ensure fields match `Product` interface
3. Run validator: checks schema compliance
4. Product appears on all 3 screens automatically (via catalogLoader)

### Task: Modify Agent Behavior

1. Edit `backend/agents/trinity_swarm.py`
2. Update agent prompts in CommercialScout/OfficialVerifier/ExternalValidator
3. Run validation test suite
4. Backend restarts automatically (uvicorn watch mode)

### Task: Add a New UI Component

1. Follow [COMPONENT_STANDARDS.ts](../frontend/src/COMPONENT_STANDARDS.ts)
2. Import from common lib (don't duplicate)
3. Use `Product` type from `types/index.ts`
4. Build using ReactComponentBuilder skill (if backend-generated)
5. Verify via Frontend Builder skill

### Task: Scale to Multiple Users

1. Add session management to `context_manager.py`
2. Modify WebSocket handler in `server.py` for multi-session
3. Add user context to agent memory
4. Update type definitions in `data_models.py`

---

## 🧪 Testing

### Run Backend Tests

```bash
cd backend
python -m pytest tests/
```

### Run Frontend Type Check

```bash
cd frontend
npx tsc --noEmit
```

### Manual Integration Test

```bash
# Terminal 1: Start backend
cd backend && PYTHONPATH=. python3 server.py

# Terminal 2: Start frontend
cd frontend && npm run dev

# Terminal 3: Test endpoints
curl http://localhost:8000/api/products
curl http://localhost:5173  # Frontend
```

---

## 📈 Performance Tips

### Frontend Optimization

- TanStack Query caches for 5 minutes (SWR)
- Components memoized to prevent re-renders
- Lazy loading for heavy components
- Virtual scrolling for large lists

**Check**: `/frontend/src/hooks/useCategoryCatalog.ts` for cache config

### Backend Optimization

- FastAPI auto-docs on `/docs`
- Uvicorn multi-worker (production)
- SQLite cache for product data
- Agent results cached in memory

**Check**: `backend/server.py` for worker config

---

## 🐛 Troubleshooting Quick Reference

| Problem              | Check                          | Fix                       |
| -------------------- | ------------------------------ | ------------------------- |
| Frontend won't load  | Backend port 8000              | Start `python3 server.py` |
| Products not showing | `/frontend/public/data/` files | Ensure JSON files exist   |
| Type errors          | `frontend/src/types/index.ts`  | Match Product interface   |
| Agents timeout       | GOOGLE_API_KEY                 | Set env var, check quota  |
| Search doesn't work  | `lib/instantSearch.ts`         | Check index file path     |

See [SYSTEM_AUDIT_v7.0.md](./SYSTEM_AUDIT_v7.0.md#debugging) for detailed debugging guide.

---

## 📋 Version History

| Version | Date        | Status        | Key Milestone                   |
| ------- | ----------- | ------------- | ------------------------------- |
| v7.0    | Feb 6, 2026 | ✅ Production | Unified pipeline, Trinity Swarm |
| v6.1    | Jan 2026    | ✅ Completed  | TanStack Query, Categories      |
| v5.4    | Dec 2025    | Archive       | Spectrum features               |
| v5.1    | Nov 2025    | Archive       | Initial ADK integration         |

---

## 🎓 Learning Path

### New to the Project?

1. **Start**: Read [SYSTEM_AUDIT_v7.0.md](./SYSTEM_AUDIT_v7.0.md)
2. **Understand**: Read [UNIFIED_DATA_PIPELINE_v7.md](./UNIFIED_DATA_PIPELINE_v7.md)
3. **Deep-dive**: Read specific docs based on interest:
   - **Security**: → [SECURITY_SHIELD_v7.md](./SECURITY_SHIELD_v7.md)
   - **Data**: → [CONDUCTOR_DAEMON_ARCHITECTURE.md](./CONDUCTOR_DAEMON_ARCHITECTURE.md)
   - **Features**: → [SPECTRUM_v5.4.0_RELEASE.md](./SPECTRUM_v5.4.0_RELEASE.md)

### Deploying to Production?

1. Read [PRODUCTION_READY_CERTIFICATION.md](./PRODUCTION_READY_CERTIFICATION.md)
2. Run all tests in `backend/tests/`
3. Build frontend: `npm run build`
4. Deploy backend to server
5. Verify all 3 screens work

### Extending the System?

1. Read [SYSTEM_AUDIT_v7.0.md](./SYSTEM_AUDIT_v7.0.md) section on Skills Protocol
2. Look at `backend/skills/frontend_builder.py` as example
3. Implement your skill following BaseSkill interface
4. Add verification gates in `backend/workflow/engine.py`

---

## 📞 Support

### For Technical Help

1. Check [SYSTEM_AUDIT_v7.0.md#troubleshooting](./SYSTEM_AUDIT_v7.0.md#troubleshooting)
2. Review error logs in terminal output
3. Check if .json data files exist
4. Verify environment variables (GOOGLE_API_KEY, PYTHONPATH)

### For Architecture Questions

- Consult [UNIFIED_DATA_PIPELINE_v7.md](./UNIFIED_DATA_PIPELINE_v7.md)
- Review actual code: `backend/agents/trinity_swarm.py`

### For Implementation Details

- Check specific doc for your topic
- Read code comments in relevant files
- Review test cases for examples

---

## 🏆 System Status

| Component           | Status         | Last Verified |
| ------------------- | -------------- | ------------- |
| **Frontend Build**  | ✅ Passing     | Feb 6, 2026   |
| **Backend Tests**   | ✅ Passing     | Feb 6, 2026   |
| **Data Validation** | ✅ 100%        | Feb 6, 2026   |
| **Agent System**    | ✅ Operational | Feb 6, 2026   |
| **Type Safety**     | ✅ Strict Mode | Feb 6, 2026   |
| **Documentation**   | ✅ Complete    | Feb 6, 2026   |

---

## 📝 License & Attribution

**Halilit Support Center v7.0**

- Architecture: Google's Agent Development Kit (ADK)
- Agents: Google Gemini 2.0 Flash
- Frontend: React 18 + CopilotKit
- Backend: Python + FastAPI
- Data: Halilit.com (primary source)

---

**Last Updated**: February 6, 2026  
**System Version**: 7.0  
**Status**: ✅ PRODUCTION READY
