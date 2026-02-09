# Halilit Support Center - Developer Handoff (v7.5)

**System Version:** v7.5  
**Date:** February 9, 2025  
**Status:** AI Agentic Swarm (Active)

## 🚀 System Overview

This repository contains the **Halilit Support Center v7.5**, an autonomous multi-agent system designed to ingest, verify, and display musical instrument product data. It operates on a **Python Backend (FastAPI)** and a **React Frontend (Vite)**.

## 📂 Core Architecture (v7.5)

The backend core logic has been consolidated into 4 primary "Unified" modules versioned `v7.5`.

| Module                 | File Path                                   | Description                                                                                                    |
| :--------------------- | :------------------------------------------ | :------------------------------------------------------------------------------------------------------------- |
| **Agent Orchestrator** | `backend/unified_agent_orchestrator_v75.py` | Manages the "Trinity Swarm" (Scout, Verifier, Validator agents). Controls agent lifecycle and task delegation. |
| **Data Service**       | `backend/unified_data_service_v75.py`       | Handles all file I/O, JSON read/writes, and state persistence. The "Source of Truth".                          |
| **Quality Gates**      | `backend/unified_quality_gates_v75.py`      | Enforces strict checks on data integrity, schema compliance, and content safety before allowing merges.        |
| **Learning System**    | `backend/unified_learning_system_v75.py`    | Self-improving module that tracks agent mistakes and updates the "Perfection Map" (Knowledge Graph).           |

## 🔌 Entry Points

- **CLI / Conductor**: `backend/conductor_main.py`
  - The main command-line interface for running ingestion cycles.
  - usage: `python backend/conductor_main.py ingest "Brand Name"`
- **API Server**: `backend/server.py`
  - FastAPI server bridge for the Frontend.
  - Exposes endpoints for the UI to request live agent actions.

## 🛠️ How to Resume Development

1. **Restore Python Environment**:

   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Run the Conductor (Test Run)**:

   ```bash
   python backend/conductor_main.py catalog
   ```

3. **Start the Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## ⚠️ Key Context for Gemini

- **Trinity Swarm**: The system uses 3 distinct agents. Do not merge them.
  - _CommercialScout_ (Prices, Raw Data)
  - _OfficialVerifier_ (Specs, Images)
  - _ExternalValidator_ (Compliance, Safety)
- **v7.5 Migration**: All imports now reference `_v75` instead of `_v73`. If you see a `_v73` import error, it is a legacy artifact—update it to `_v75`.
- **Zero-Byte Safety**: The `backend/skills/frontend_builder.py` skill is strictly enforced to prevent `0-byte` file overwrites. ALways use the "Skills" protocol when generating code.

## 🗺️ File Structure Snapshot

```text
backend/
├── conductor_main.py              # CLI Entry
├── server.py                      # API Server
├── unified_agent_orchestrator_v75.py
├── unified_data_service_v75.py
├── unified_quality_gates_v75.py
├── unified_learning_system_v75.py
├── ingestion_to_frontend.py       # Bridge script
└── skills/                        # Modular Capabilities
```
