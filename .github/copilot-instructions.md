# Repository Instructions & Context (v2.0 - Skills Protocol)

## 🚨 CRITICAL RULE: NO DIRECT FILE OVERWRITES

You are **FORBIDDEN** from blindly overwriting frontend files (e.g., `App.tsx`, `GalaxyDashboard.tsx`) with unchecked code. You must assume the previous "DevAgent" has corrupted the filesystem with 0-byte files.

## Project Overview

This repository hosts the **Halilit Support Center v5.1** - an AI-powered product catalog system built on **Google's Agent Development Kit (ADK)**.

- **Architecture**: Agentic Multi-Agent System (Trinity Swarm) + Skills & Workflows
- **Frontend**: React 18 + CopilotKit for agent-UI communication
- **Backend**: Python + FastAPI + Google Gemini agents
- **Safety Layer**: Skills (verified capabilities) + Workflow Engine (state machines)

## ADK Architecture (v5.1)

### Trinity Swarm: Three Autonomous Agents

1. **CommercialScout** (`gemini-2.0-flash`)
   - Harvests product data from Halilit.com
   - Returns: ProductDraft with prices

2. **OfficialVerifier** (`gemini-2.0-flash`)
   - Enriches with manufacturer specs
   - Adds images, official data

3. **ExternalValidator** (`gemini-2.0-flash`)
   - Audits data for compliance
   - Returns: AuditReport with risk score (0-100)

### Running the System

```bash
# Backend (FastAPI + Trinity Swarm)
PYTHONPATH=. python3 backend/server.py

# Frontend (React + CopilotKit)
cd frontend && npm run dev
```

## Tech Stack

- **Backend**:
  - Python 3.11+
  - google.genai (Google Gemini SDK)
  - FastAPI (real-time bridge)
  - Pydantic v2 (data models)

- **Frontend**:
  - React 18.3.1
  - CopilotKit (@copilotkit/react-core, @copilotkit/react-ui)
  - TypeScript 5.x
  - Vite 7.x
  - Tailwind CSS

## File Structure

```
backend/
├── agents/
│   └── trinity_swarm.py          # All 3 agents + orchestrator
├── skills/                        # ⭐ NEW: Modular verified capabilities
│   ├── base_skill.py              # Abstract skill interface
│   └── frontend_builder.py        # Safe React builder with 0-byte prevention
├── workflow/                      # ⭐ NEW: State machine enforcement
│   └── engine.py                  # Workflow engine with verification gates
├── server.py                      # FastAPI bridge
└── tests/
    └── test_adk_coverage.py       # 31 comprehensive tests

frontend/
├── src/
│   ├── main.tsx                  # CopilotKit wrapper
│   ├── App.tsx                   # Agent-aware UI
│   └── components/               # React components
└── vite.config.ts                # Proxy to /api/copilot/chat
```

## Code Standards (Strict Enforcement)

### 1. Frontend (React/TypeScript)

- **NEVER** leave a file empty or < 100 bytes
- **ALWAYS** use strict TypeScript interfaces (defined in `frontend/src/types/`)
- **Visuals**: Use `slate-900` themes with `blue-500` accents (The "Galaxy" Theme)
- **Imports**: Always import React: `import React from 'react';`
- **Exports**: Every component must have an export statement

### 2. Backend (Python/Agents)

- **Modular Skills**: Do NOT hardcode capabilities into `Agent` classes. Use `backend/skills/` directory
- **State Machines**: Complex tasks MUST use `backend/workflow/engine.py` to enforce `Plan → Code → Verify` loops
- **Verification**: All file writes must pass through a Skill that verifies:
  - File exists after write
  - File size > 0 bytes
  - Content matches what was written

### 3. Skills Protocol

When building frontend features, you MUST:

1. Use `ReactComponentBuilder` from `backend/skills/frontend_builder.py`
2. Use `FeatureBuildWorkflow` from `backend/workflow/engine.py`
3. NEVER directly write files without verification
4. Create backups before overwriting existing files

Example correct usage:

```python
from backend.workflow.engine import FeatureBuildWorkflow

workflow = FeatureBuildWorkflow()
success = workflow.run_feature_build({
    'name': 'New Dashboard Component',
    'files': [
        {'path': 'frontend/src/components/Dashboard.tsx', 'content': code, 'type': 'react'}
    ]
})
```

## Code Standards

- **Backend**: All agent logic in `trinity_swarm.py`, FastAPI routes in `server.py`, capabilities in `skills/`
- **Frontend**: CopilotKit integration via `useCopilotReadable` and `useCopilotAction`
- **Data Models**: Pydantic v2 (ProductDraft, AuditReport)
- **Testing**: Comprehensive test suite in `test_adk_coverage.py`

## ⚠️ Known Issues to Fix

- **0-Byte Files**: The previous DevAgent wiped `index.html`, `vite.config.ts`, and `App.tsx`
- **Correction Strategy**: When asked to fix the UI, do NOT patch. **Rebuild the core file completely** using the standard boilerplate
- **Prevention**: ALL file writes now route through Skills with verification gates

## 📝 Commit Message Protocol

When suggesting code, your context description MUST include:

- `[SKILL USED]`: e.g., ReactComponentBuilder
- `[VERIFICATION]`: "Confirmed file will not be empty."
- `[WORKFLOW STATE]`: e.g., "CODING → VERIFYING → COMPLETE"

## Key Principles

- User commands agents via CopilotKit sidebar
- Agents work autonomously (no manual pipeline steps)
- Real-time communication via FastAPI bridge
- Type-safe data flow with Pydantic models
