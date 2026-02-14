"""
Halilit Support Center — JIT Architecture Backend
==================================================

Lightweight API server with:
- Skeleton inventory sync (fast Halilit.com listing scraper)
- JIT Agent (Gemini-powered live product intelligence)
- SSE streaming for progressive frontend loading
- Source Rules compliance (Commercial / Official / Contextual)

Version: 9.0.0 (JIT Architecture)
"""

import sys
from pathlib import Path

_parent_dir = str(Path(__file__).parent.parent)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

__version__ = "9.1.0"

__all__ = ["__version__"]
