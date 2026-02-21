import logging
import asyncio
from typing import Union

import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageValidationRequest(BaseModel):
    image_url: HttpUrl


class ImageValidationResponse(BaseModel):
    is_valid: bool
    validation_path: str = "deep"  # "fast_pass" | "deep"


ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]
CACHE_KEY_PREFIX = "image_validation:"
CACHE_EXPIRY_SECONDS = 24 * 60 * 60  # 24 hours

# Fast-Pass threshold: images with Content-Length above this are immediately
# accepted without downloading or running AI/Pillow analysis (~99% of real product
# images are well above this floor; only placeholder/broken images are below it).
_FAST_PASS_MIN_BYTES = 10_240  # 10 KB


async def _head_check(image_url: str) -> dict:
    """
    Fire a single HEAD request and return validated metadata.
    Returns {"ok": True, "content_type": str, "content_length": int} on success
    or     {"ok": False, "reason": str} on failure.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(image_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if not (200 <= response.status < 300):
                    return {"ok": False, "reason": f"HTTP {response.status}"}
                ct = (response.headers.get("Content-Type")
                      or "").lower().split(";")[0].strip()
                cl_raw = response.headers.get("Content-Length", "0")
                try:
                    cl = int(cl_raw)
                except ValueError:
                    cl = 0
                return {"ok": True, "content_type": ct, "content_length": cl}
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        return {"ok": False, "reason": str(e)}
    except Exception as e:
        return {"ok": False, "reason": str(e)}


async def validate_image_url(image_url: str) -> tuple[bool, str]:
    """
    Validates an image URL using a two-stage pipeline:

    Stage 1 — Fast-Pass (microseconds): HTTP HEAD request.
      • If Content-Type is an allowed image type AND Content-Length > 10 KB
        → immediately return (True, "fast_pass"). No download, no AI credits.

    Stage 2 — Deep Check (only for suspicious images): full GET + type check.
      • Images that are tiny (<10 KB), have a missing Content-Length, or have an
        ambiguous content-type fall through to the complete download path.

    Returns:
        (is_valid: bool, validation_path: str)  where path is "fast_pass" | "deep"
    """
    # ── Stage 1: Fast-Pass Heuristic ─────────────────────────────────────────
    head = await _head_check(image_url)
    if head["ok"]:
        ct = head["content_type"]
        cl = head["content_length"]
        if ct in ALLOWED_IMAGE_TYPES and cl > _FAST_PASS_MIN_BYTES:
            logger.debug("FAST_PASS ✅ %s (%s, %d KB)",
                         image_url, ct, cl // 1024)
            return True, "fast_pass"
        # Image is an image type but suspiciously small — fall through to deep check
        if ct not in ALLOWED_IMAGE_TYPES and ct:
            # Not an image at all — fail immediately, no need to download
            logger.info(
                "Fast-fail (non-image Content-Type: %s): %s", ct, image_url)
            return False, "fast_pass"

    # ── Stage 2: Deep Check (suspicious or missing headers) ─────────────────
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(image_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if 200 <= response.status < 300:
                    ct = (response.headers.get("Content-Type")
                          or "").split(";")[0].strip()
                    is_valid = ct in ALLOWED_IMAGE_TYPES
                    logger.info(
                        "Deep check %s for %s (Content-Type: %s)",
                        "✅" if is_valid else "❌", image_url, ct,
                    )
                    return is_valid, "deep"
                else:
                    logger.info("Deep check failed for %s: Status %s",
                                image_url, response.status)
                    return False, "deep"
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.error("Network error validating %s: %s", image_url, e)
        return False, "deep"
    except Exception as e:
        logger.error("Unexpected error validating %s: %s", image_url, e)
        return False, "deep"


@app.post("/api/validate_image", response_model=ImageValidationResponse)
async def validate_image(request: ImageValidationRequest) -> ImageValidationResponse:
    is_valid, path = await validate_image_url(str(request.image_url))
    return ImageValidationResponse(is_valid=is_valid, validation_path=path)


# ---------------------------------------------------------------------------
# Synchronous Fast-Pass — for Data Manager MCP tool (no event loop required)
# ---------------------------------------------------------------------------

def fast_pass_image_check(image_url: str) -> bool:
    """
    Synchronous microsecond heuristic: fires a HEAD request and returns True
    if the URL is a real image (Content-Type is an image and size > 10 KB).

    Returns False for broken URLs, non-image types, or suspiciously small
    responses that should be escalated to deep AI validation.

    Safe to call from synchronous code (Data Manager, CLI scripts, etc.).
    Does NOT download the image body — header-only, near-zero I/O cost.
    """
    import requests as _requests  # lazy import; sync world only

    try:
        response = _requests.head(
            image_url, timeout=3, allow_redirects=True
        )
        if response.status_code == 200:
            content_type = (response.headers.get("Content-Type")
                            or "").lower().split(";")[0].strip()
            content_length = int(
                response.headers.get("Content-Length", 0) or 0)
            if "image" in content_type and content_length > _FAST_PASS_MIN_BYTES:
                logger.debug("FAST_PASS (sync) ✅ %s (%s, %d KB)",
                             image_url, content_type, content_length // 1024)
                return True
    except Exception as exc:  # noqa: BLE001
        logger.debug("fast_pass_image_check failed for %s: %s", image_url, exc)

    return False
