"""
Central path configuration for Halilit Support Center.

All paths are derived from the project root so the codebase runs on any machine
(not only GitHub Codespaces). Override PROJECT_ROOT via env HALILIT_PROJECT_ROOT if needed.
"""

import os
from pathlib import Path

# Project root: directory containing backend/ and frontend/
_env_root = os.environ.get("HALILIT_PROJECT_ROOT")
if _env_root:
    PROJECT_ROOT = Path(_env_root).resolve()
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Backend paths
BACKEND_DIR = PROJECT_ROOT / "backend"
CONFIG_DIR = BACKEND_DIR / "config"
LOGS_DIR = BACKEND_DIR / "logs"
DATA_DIR = BACKEND_DIR / "data"
INGESTION_DATA_DIR = DATA_DIR / "ingestion"
INGESTION_VERSIONS_DIR = INGESTION_DATA_DIR / "versions"
BRANDS_DATA_DIR = DATA_DIR / "brands"
SPECTRUM_DATA_DIR = INGESTION_DATA_DIR / "spectrum"

# Log subdirs (for components that need a specific log folder)
LOGS_VERIFICATION = LOGS_DIR / "verification"
LOGS_AUDIT = LOGS_DIR / "audit"
LOGS_FEEDBACK = LOGS_DIR / "feedback"
LOGS_IMPROVEMENTS = LOGS_DIR / "improvements"

# Frontend paths
FRONTEND_DIR = PROJECT_ROOT / "frontend"
FRONTEND_PUBLIC_DATA = FRONTEND_DIR / "public" / "data"
FRONTEND_PUBLIC = FRONTEND_DIR / "public"
