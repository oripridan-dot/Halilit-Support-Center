"""
Load secrets from environment. .env is loaded once; keys are never logged or exposed.

Keep your real API keys only in .env (copy from .env.example). .env is in .gitignore
so it is never committed. One key in .env is enough — you won't need to rotate or
recreate keys unless you revoke them.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

_ENV_LOADED = False


def _ensure_env_loaded() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    try:
        from dotenv import load_dotenv
        root = Path(__file__).resolve().parent.parent
        env_path = root / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        _ENV_LOADED = True
    except Exception:
        _ENV_LOADED = True  # avoid retry if dotenv missing


def get_gemini_api_key() -> Optional[str]:
    """
    Return the Gemini API key from environment. Uses only GEMINI_API_KEY.
    Get a key from https://aistudio.google.com/app/apikey (Google AI Studio).
    Also clears GOOGLE_API_KEY from env so the google-genai library cannot use
    an old/expired key when both were set.
    """
    _ensure_env_loaded()
    # So the library never uses GOOGLE_API_KEY (it prefers it when both are set)
    os.environ.pop("GOOGLE_API_KEY", None)
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    # Strip whitespace and optional surrounding quotes (e.g. from copy-paste)
    key = key.strip().strip("'\"").strip()
    return key or None
