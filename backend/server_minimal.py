#!/usr/bin/env python3
"""
Minimal FastAPI server for maintenance workflows
Bypasses Trinity Swarm import issues
"""

import os
import json
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Halilit Support Center v5.1 (Minimal Mode)",
    description="Maintenance Workflows Server",
    version="5.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# REAL MAINTENANCE WORKFLOWS (Direct import to avoid __init__.py)
# ============================================================

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import workflows directly without going through __init__.py
from backend.workflow.real_maintenance import (
    RealCodeCleanupWorkflow,
    RealCodeSyncWorkflow,
    RealHealthCheckWorkflow
)

# ============================================================
# ENDPOINTS
# ============================================================

class HealthResponse(BaseModel):
    status: str
    message: str

class WorkflowResponse(BaseModel):
    status: str
    result: dict

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Server health check"""
    return {
        "status": "HEALTHY",
        "message": "Minimal server running - real maintenance workflows available"
    }

@app.post("/api/maintenance/health-check", response_model=WorkflowResponse)
async def run_health_check():
    """Run real health check on codebase"""
    try:
        workflow = RealHealthCheckWorkflow()
        result = workflow.execute()
        return {
            "status": "SUCCESS",
            "result": result
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/maintenance/code-cleanup", response_model=WorkflowResponse)
async def run_code_cleanup():
    """Run code cleanup on Python files"""
    try:
        workflow = RealCodeCleanupWorkflow()
        result = workflow.execute()
        return {
            "status": "SUCCESS",
            "result": result
        }
    except Exception as e:
        logger.error(f"Code cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/maintenance/sync-code", response_model=WorkflowResponse)
async def run_code_sync():
    """Synchronize exports and imports"""
    try:
        workflow = RealCodeSyncWorkflow()
        result = workflow.execute()
        return {
            "status": "SUCCESS",
            "result": result
        }
    except Exception as e:
        logger.error(f"Code sync failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/maintenance/full-cycle", response_model=WorkflowResponse)
async def run_full_cycle():
    """Run full maintenance cycle: health → cleanup → sync → health"""
    try:
        results = {}

        # Phase 1: Initial health check
        logger.info("Phase 1: Running initial health check...")
        health_workflow = RealHealthCheckWorkflow()
        results['initial_health'] = health_workflow.execute()

        # Phase 2: Code cleanup
        logger.info("Phase 2: Running code cleanup...")
        cleanup_workflow = RealCodeCleanupWorkflow()
        results['code_cleanup'] = cleanup_workflow.execute()

        # Phase 3: Code sync
        logger.info("Phase 3: Running code sync...")
        sync_workflow = RealCodeSyncWorkflow()
        results['code_sync'] = sync_workflow.execute()

        # Phase 4: Final health check
        logger.info("Phase 4: Running final health check...")
        final_health_workflow = RealHealthCheckWorkflow()
        results['final_health'] = final_health_workflow.execute()

        logger.info("✅ Full maintenance cycle complete!")

        return {
            "status": "SUCCESS",
            "result": {
                "phases": results,
                "summary": {
                    "total_phases": 4,
                    "status": "ALL PHASES COMPLETED"
                }
            }
        }
    except Exception as e:
        logger.error(f"Full cycle failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Halilit Support Center (Minimal Mode) on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
