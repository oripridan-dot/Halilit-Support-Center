"""
Browser Agent Bridge — HQ ↔ OpenClaw Field Agent

RESTRICTED USE: This module is for authorized, internal product-spec verification
only. All requests are scoped to allowlisted manufacturer domains, rate-limited,
and time-bounded. No arbitrary URLs or user-controlled navigation.

Legal & compliance: See backend/agent_skills/COMPLIANCE.md.
"""

from __future__ import annotations

import logging
import os
import re
import time
from typing import Any, Dict, FrozenSet

logger = logging.getLogger("BrowserAgent")

OPENCLAW_URL = os.getenv("OPENCLAW_URL", "").rstrip("/")
OPENCLAW_KEY = os.getenv("OPENCLAW_KEY", "")
OPENCLAW_EXECUTE_PATH = os.getenv("OPENCLAW_EXECUTE_PATH", "/api/execute")
OPENCLAW_TIMEOUT = float(os.getenv("OPENCLAW_TIMEOUT", "60.0"))
# Rate limit: max requests per window (default 10 per 60 seconds per process)
OPENCLAW_RATE_LIMIT_N = int(os.getenv("OPENCLAW_RATE_LIMIT_N", "10"))
OPENCLAW_RATE_LIMIT_WINDOW = float(os.getenv("OPENCLAW_RATE_LIMIT_WINDOW", "60.0"))
# Max length for product_name to avoid abuse
OPENCLAW_MAX_PRODUCT_NAME_LEN = int(os.getenv("OPENCLAW_MAX_PRODUCT_NAME_LEN", "200"))

# Allowlisted manufacturer domains (lowercase, no protocol). Only these may be queried.
_ALLOWED_DOMAINS: FrozenSet[str] = frozenset(
    {
        "roland.com", "yamaha.com", "nordkeyboards.com", "korg.com", "casio.com",
        "boss.info", "fender.com", "gibson.com", "shure.com", "sennheiser.com",
        "focusrite.com", "native-instruments.com", "arturia.com", "moogmusic.com",
        "adam-audio.com", "genelec.com", "krk.com", "marshall.com", "orangeamps.com",
        "behringer.com", "presonus.com", "uaudio.com", "steinberg.net",
        "novationmusic.com", "akaipro.com",
        "audio-technica.com", "jbl.com", "harman.com", "pioneerdj.com",
        "mackie.com",
    }
)

_rate_timestamps: list[float] = []


def _normalize_domain(domain: str) -> str:
    """Return lowercase domain without protocol or path."""
    s = (domain or "").strip().lower()
    s = re.sub(r"^https?://", "", s)
    s = re.sub(r"/.*$", "", s)
    s = s.strip()
    return s


def _is_domain_allowed(domain: str) -> bool:
    normalized = _normalize_domain(domain)
    if not normalized:
        return False
    if normalized in _ALLOWED_DOMAINS:
        return True
    # Allow known www-prefixed
    if normalized.startswith("www.") and normalized[4:] in _ALLOWED_DOMAINS:
        return True
    return False


def _check_rate_limit() -> bool:
    """True if request is allowed under rate limit; drops old timestamps."""
    global _rate_timestamps
    now = time.monotonic()
    window = OPENCLAW_RATE_LIMIT_WINDOW
    n = OPENCLAW_RATE_LIMIT_N
    _rate_timestamps = [t for t in _rate_timestamps if now - t < window]
    if len(_rate_timestamps) >= n:
        return False
    _rate_timestamps.append(now)
    return True


def _is_available() -> bool:
    return bool(OPENCLAW_URL)


async def verify_official_specs(brand_domain: str, product_name: str) -> Dict[str, Any]:
    """
    Dispatch the Official Scout skill only for allowlisted manufacturer domains.
    Rate-limited and time-bounded. Returns dict with specs_text, diagram_url (or error).
    """
    if not _is_available():
        return {"error": "OpenClaw not configured", "specs_text": "", "diagram_url": ""}

    # Guard: allowlisted domains only
    if not _is_domain_allowed(brand_domain):
        logger.warning("OpenClaw: rejected domain (not allowlisted): %s", brand_domain[:80])
        return {"error": "domain_not_allowed", "specs_text": "", "diagram_url": ""}

    # Guard: product_name length
    pn = (product_name or "").strip()
    if len(pn) > OPENCLAW_MAX_PRODUCT_NAME_LEN:
        logger.warning("OpenClaw: product_name too long (max %s)", OPENCLAW_MAX_PRODUCT_NAME_LEN)
        return {"error": "product_name_too_long", "specs_text": "", "diagram_url": ""}
    if not pn:
        return {"error": "product_name_required", "specs_text": "", "diagram_url": ""}

    # Guard: rate limit
    if not _check_rate_limit():
        logger.warning("OpenClaw: rate limit exceeded (%s per %ss)", OPENCLAW_RATE_LIMIT_N, OPENCLAW_RATE_LIMIT_WINDOW)
        return {"error": "rate_limit_exceeded", "specs_text": "", "diagram_url": ""}

    try:
        import httpx
    except ImportError:
        return {"error": "httpx required", "specs_text": "", "diagram_url": ""}

    payload = {
        "skill": "verify_product_specs",
        "params": {
            "brand_domain": _normalize_domain(brand_domain),
            "product_name": pn,
        },
    }
    url = f"{OPENCLAW_URL}{OPENCLAW_EXECUTE_PATH}"
    headers: Dict[str, str] = {}
    if OPENCLAW_KEY:
        headers["Authorization"] = f"Bearer {OPENCLAW_KEY}"
        headers["X-API-Key"] = OPENCLAW_KEY

    try:
        async with httpx.AsyncClient(timeout=OPENCLAW_TIMEOUT) as client:
            resp = await client.post(url, json=payload, headers=headers or None)
            resp.raise_for_status()
            data = resp.json()
    except httpx.TimeoutException as e:
        logger.warning("OpenClaw verify_official_specs timeout: %s", e)
        return {"error": "timeout", "specs_text": "", "diagram_url": ""}
    except httpx.HTTPStatusError as e:
        logger.warning("OpenClaw verify_official_specs HTTP %s: %s", e.response.status_code, e)
        return {"error": f"http_{e.response.status_code}", "specs_text": "", "diagram_url": ""}
    except Exception as e:
        logger.warning("OpenClaw verify_official_specs failed: %s", e)
        return {"error": str(e), "specs_text": "", "diagram_url": ""}

    result = data.get("result", data)
    return {
        "specs_text": result.get("specs_text", ""),
        "diagram_url": result.get("diagram_url", ""),
        "raw": result,
    }


def get_browser_agent() -> "BrowserAgent":
    return _agent


class BrowserAgent:
    """
    Bridge between Python HQ and the OpenClaw Field Agent.
    All calls are restricted to allowlisted domains and rate-limited.
    """

    @property
    def available(self) -> bool:
        return _is_available()

    async def verify_official_specs(self, brand_domain: str, product_name: str) -> Dict[str, Any]:
        """Dispatch Official Scout; only allowlisted domains, rate-limited."""
        return await verify_official_specs(brand_domain, product_name)


_agent = BrowserAgent()
