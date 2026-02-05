#!/usr/bin/env python3
"""
Halilit Support Center v6.0 - FastAPI Server

Serves the frontend and provides data endpoints.
Data pipeline is orchestrated separately via conductor.

Usage:
    python3 backend/server.py
"""

import uvicorn
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(
    title="Halilit Support Center v6.0",
    description="AI-powered product catalog with Trinity Ingestion Pipeline",
    version="6.0.0",
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "6.0.0",
        "features": ["Trinity Ingestion", "Spectrum Catalog", "v6.0 Pipeline"]
    }


@app.get("/api/config")
def get_config():
    """Get application configuration."""
    return {
        "catalog": {
            "brands": ["Roland", "Nord", "Moog", "Rode", "Shure", "Universal Audio", "Drumdots"],
            "total_products": 648,
            "galaxies": 6,
            "last_sync": "2024-02-05T17:14:33"
        }
    }


@app.get("/")
def root():
    """Root endpoint redirects to frontend."""
    return {
        "message": "Halilit Support Center v6.0",
        "frontend": "http://localhost:5173",
        "api_docs": "http://localhost:8000/docs"
    }


if __name__ == "__main__":
    print("🚀 Starting Halilit Support Center v6.0")
    print("📖 API Docs:  http://localhost:8000/docs")
    print("🎨 Frontend:  http://localhost:5173")
    print("💾 Pipeline:  backend/ingestion/orchestrator.py")
    uvicorn.run(app, host="0.0.0.0", port=8000)
