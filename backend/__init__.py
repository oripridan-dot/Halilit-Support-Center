"""
Halilit Support Center v8.5 - ADK Backend (Trinity Swarm + Async Task Queue)
=============================================================================

Lightweight module exports for the Halilit Support Center API.
- Trinity Swarm: Three autonomous agents for data processing
- Async Task Queue: Celery + Redis distributed pipeline
- Ingestion Pipeline: Data normalization and persistence
- Skills & Workflow: Verified capabilities with state machines
- Security: Multi-layer protection

Version: 8.3.0 (Production-Ready)
"""

import sys
from pathlib import Path

# Ensure parent directory is in path for imports
_parent_dir = str(Path(__file__).parent.parent)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

__version__ = "8.3.0"
__adk_enabled__ = True

__all__ = [
    "__version__",
    "__adk_enabled__",
]
