# Repository Instructions & Context

## Project Overview

This repository hosts the **Halilit Support Center v5.1** - an AI-powered product catalog system built on **Google's Agent Development Kit (ADK)**.

- **Architecture**: Agentic Multi-Agent System (Trinity Swarm)
- **Frontend**: React 18 + CopilotKit for agent-UI communication
- **Backend**: Python + FastAPI + Google Gemini agents

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

## Code Standards

- **Backend**: All agent logic in `trinity_swarm.py`, FastAPI routes in `server.py`
- **Frontend**: CopilotKit integration via `useCopilotReadable` and `useCopilotAction`
- **Data Models**: Pydantic v2 (ProductDraft, AuditReport)
- **Testing**: Comprehensive test suite in `test_adk_coverage.py`

## Key Principles

- User commands agents via CopilotKit sidebar
- Agents work autonomously (no manual pipeline steps)
- Real-time communication via FastAPI bridge
- Type-safe data flow with Pydantic models
