"""
Image URL Validator — spec: evolution_clarifai_s_image_moderation_api.md

Goal: "Zero Broken Images — hero images MUST be validated before display."

Approach: HTTP reachability + Content-Type check using httpx (already in
requirements.txt). No Clarifai SDK or external AI service required — the
Three Source Rules prohibit presenting AI-generated data as real content,
so all checks are structural (network + MIME type + file header), not semantic.

Optional Pillow check: when the URL is reachable and the image can be
fetched, Pillow verifies that the binary is a valid image file.  Falls back
gracefully when Pillow is not installed.
"""
from __future__ import annotations

import io
import logging
from typing import TypedDict

import httpx

try:
    from PIL import Image, UnidentifiedImageError

    _PILLOW = True
except ImportError:
    _PILLOW = False

logger = logging.getLogger(__name__)

_VALID_CONTENT_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/svg+xml",
    "image/avif",
    "image/heic",
}

_HEADERS = {
    "User-Agent": (
        "HalilitImageValidator/1.0 (+https://halilit.co.il)"
    )
}


class ValidationResult(TypedDict):
    url: str
    valid: bool
    status_code: int | None
    content_type: str | None
    reason: str


def validate_image_url(
    url: str,
    *,
    timeout: float = 8.0,
    verify_bytes: bool = True,
) -> ValidationResult:
    """
    Validate that *url* points to a reachable, valid image.

    Steps:
    1. HEAD request — check HTTP 200 + image Content-Type.
    2. (Optional) GET first 64 KB and verify with Pillow.

    Returns a ValidationResult dict — never raises.
    """
    base: ValidationResult = {
        "url": url,
        "valid": False,
        "status_code": None,
        "content_type": None,
        "reason": "not-checked",
    }

    if not url or not url.startswith(("http://", "https://")):
        base["reason"] = "invalid-url-scheme"
        return base

    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            # Step 1: HEAD
            head = client.head(url, headers=_HEADERS)
            base["status_code"] = head.status_code
            content_type = (
                head.headers.get(
                    "content-type", "").split(";")[0].strip().lower()
            )
            base["content_type"] = content_type

            if head.status_code not in (200, 206):
                base["reason"] = f"http-{head.status_code}"
                return base

            if content_type and content_type not in _VALID_CONTENT_TYPES:
                base["reason"] = f"unexpected-content-type:{content_type}"
                return base

            # Step 2: Pillow byte verification (optional)
            if verify_bytes and _PILLOW:
                get = client.get(url, headers=_HEADERS)
                if get.status_code != 200:
                    base["reason"] = f"get-http-{get.status_code}"
                    return base
                try:
                    img = Image.open(io.BytesIO(get.content))
                    img.verify()
                    base["content_type"] = Image.MIME.get(
                        img.format or "", content_type)
                except (UnidentifiedImageError, Exception) as pex:  # noqa: BLE001
                    base["reason"] = f"pillow-verify-failed:{pex}"
                    return base

            base["valid"] = True
            base["reason"] = "ok"
            return base

    except httpx.TimeoutException:
        base["reason"] = "timeout"
        return base
    except Exception as exc:  # noqa: BLE001
        logger.debug("Image validation error for %s: %s", url, exc)
        base["reason"] = f"error:{exc}"
        return base


def validate_catalog_images(
    products: list[dict],
    *,
    timeout: float = 6.0,
) -> dict[str, ValidationResult]:
    """
    Validate hero image URLs for a list of product dicts.
    Returns {product_id: ValidationResult}.

    Three Source Rules: reads only from catalog (Commercial source).
    Never writes or mutates product data.
    """
    results: dict[str, ValidationResult] = {}
    for p in products:
        pid = p.get("id") or p.get("product_id") or ""
        hero = (
            p.get("hero_image")
            or p.get("imageUrl")
            or p.get("image_url")
            or ""
        )
        if not pid or not hero:
            continue
        results[pid] = validate_image_url(
            hero, timeout=timeout, verify_bytes=False)
    return results
