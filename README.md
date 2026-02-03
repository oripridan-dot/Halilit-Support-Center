# Halilit Support Center v5.2.3

**An AI-Powered Product Catalog System Built on Google's Agent Development Kit (ADK)**

🆕 **v5.2.3 Features**: Full Maintenance Cycle, Data Pipeline Refinement, Category Taxonomy Fix, Code Consolidation, Production Ready

## 🚀 Quick Start

### Prerequisites

- Python 3.11+, Node.js 18+
- Google Gemini API Key

### 30-Second Setup

```bash
# 1. Export data from backend → frontend
python3 backend/export_to_frontend.py

# 2. Start backend
PYTHONPATH=. python3 backend/server.py &

# 3. Start frontend
cd frontend && npm run dev
```

Open http://localhost:5173 and explore 647 products across 6 galaxies with proper category hierarchy!

## 🤖 Trinity Swarm + DevAgent: 4 AI Agents with Learning

1. **CommercialScout** 🧠 - Harvests product data + learns patterns
2. **OfficialVerifier** 🧠 - Enriches with specs + learns enrichment strategies
3. **ExternalValidator** 🧠 - Audits & scores (0-100) + learns audit criteria
4. **DevAgent v3.0** ⭐ **CONTEXT-AWARE + LEARNING** - Complete development intelligence

**DevAgent v3.0 Features**:

- ✅ **v1.0**: Error analysis + AI fix suggestions
- ✅ **v2.0**: Auto-validation + Auto-apply with backups
- ✅ **v3.0**: Complete context management & proactive development
- 🆕 **v3.1**: **Agent Learning & Memory System**
  - **Functional Memory**: Every action recorded in `.agent_memory/`
  - **AI-Powered Patterns**: Gemini analyzes learning records
  - **Contextual Advice**: Agents query past learning before acting
  - **Self-Improvement**: Agents identify and fix their weaknesses
  - **Cross-Agent Learning**: All 4 agents learn and improve together

**Storage**:

- `.devagent/` - Development context (history, rules)
- `.agent_memory/` - Learning records & patterns

User commands agents via **CopilotKit sidebar** in real-time.  
DevAgent monitors automatically + all agents learn from every action.

## 🧠 Learning System

### How Agents Learn

1. **Action**: Agent performs task (analyze, fix, validate, etc.)
2. **Record**: Input/output/success/confidence automatically logged
3. **Pattern Analysis**: After 10+ actions, AI extracts patterns
4. **Contextual Advice**: Before next action, agent queries memory
5. **Improved Performance**: Success rates and confidence increase over time

### Memory API Endpoints

```bash
GET /api/memory/stats/{agent_name}           # Learning statistics
GET /api/memory/advice/{agent_name}?task=... # Get advice for task
GET /api/memory/insights/{agent_name}        # View learned patterns
GET /api/memory/improvements/{agent_name}    # Self-improvement suggestions
GET /api/memory/all-agents                   # All agents summary
```

See **[AGENT_LEARNING.md](AGENT_LEARNING.md)** for complete guide.

## 📊 Data Flow

```
Backend Golden Data (5_golden/)
         ↓
export_to_frontend.py (Transform)
         ↓
Frontend Public Data (public/data/)
         ↓
React UI (668 products ready!)
```

**Run export anytime**: `python3 backend/export_to_frontend.py`

## ✅ System Status

- **Tests**: 31/31 passing ✓
- **Agents**: All operational ✓
- **Data Export**: 668 products ✓
- **Code**: 100% synced (Backend + Frontend) ✓
- **Documentation**: Complete ✓

## 📖 Documentation

### Core Documentation

- **[README.md](README.md)** - This file (Quick start & overview)
- **[ADK_ARCHITECTURE.md](ADK_ARCHITECTURE.md)** - System architecture deep dive
- **[RELEASE_NOTES_v5.1.md](RELEASE_NOTES_v5.1.md)** ⭐ **NEW** - v5.1 release summary

### DevAgent Documentation

- **[DEVAGENT_V3_CONTEXT.md](DEVAGENT_V3_CONTEXT.md)** - Context management
- **[DEVAGENT_V2.md](DEVAGENT_V2.md)** - Auto-validation & auto-apply
- **[DEVAGENT_GUIDE.md](DEVAGENT_GUIDE.md)** - Complete guide
- **[DEVAGENT_QUICKREF.md](DEVAGENT_QUICKREF.md)** - Quick reference
- **[PREVENTION_GUIDE.md](PREVENTION_GUIDE.md)** - Prevention system

### Learning System Documentation

- **[AGENT_LEARNING.md](AGENT_LEARNING.md)** ⭐ **NEW** - Complete learning system guide (500+ lines)
- **[AUTO_LOGGING_STATUS.md](AUTO_LOGGING_STATUS.md)** - Automatic logging details

### System Status

- **[SYSTEM_STATUS.md](SYSTEM_STATUS.md)** - Production readiness checklist
- **[ADK_CLEANUP_REPORT.md](ADK_CLEANUP_REPORT.md)** - Cleanup details
- **[backend/tests/test_adk_coverage.py](backend/tests/test_adk_coverage.py)** - 31 comprehensive tests

## 🧪 Testing

```bash
python -m pytest backend/tests/test_adk_coverage.py -v
```

## 🛠️ Stack

**Backend**: Python + google.genai + FastAPI + Pydantic  
**Frontend**: React 18 + CopilotKit + TypeScript + Vite  
**Data**: 668 products across 9 brands

See [ADK_ARCHITECTURE.md](ADK_ARCHITECTURE.md) for full details.
