"""
Visual Validator & Comparator Engine
====================================
Central logic for image quality assurance and deduplication.
Used by:
1. Ingestion Pipeline (to reject bad images)
2. Catalog Validator (to score product health)
3. MCP Server (for AI agent tools)
4. AI-powered image audit (Gemini vision)
"""

import io
import json
import logging
import math
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx

logger = logging.getLogger("VisualValidator")

# When set (e.g. "1" or "true"), ingestion skips visual validation (faster, less safe).
INGESTION_SKIP_VISUAL_VALIDATION = os.environ.get(
    "INGESTION_SKIP_VISUAL_VALIDATION", "").lower() in ("1", "true", "yes")

# Default Gemini model for vision (image) analysis
GEMINI_VISION_MODEL = os.environ.get("GEMINI_VISION_MODEL", "gemini-2.0-flash")

try:
    from PIL import Image, ImageChops, ImageStat
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False
    logger.warning("Pillow not installed — visual validation will be limited.")

# Resampling constant (Pillow 9.1+ uses Image.Resampling.LANCZOS)
try:
    _LANCZOS = Image.Resampling.LANCZOS
except AttributeError:
    _LANCZOS = Image.LANCZOS  # type: ignore

# Known placeholder hashes or signatures could be added here
PLACEHOLDER_TEXTS = ["placeholder", "image not available", "no image"]

# ---------------------------------------------------------------------------
# Persistent URL validation cache — avoids re-fetching images across runs
# ---------------------------------------------------------------------------
_VALIDATION_CACHE_PATH = Path(__file__).resolve(
).parent.parent / "data" / "jit_cache" / "image_validation_cache.json"
_VALIDATION_CACHE_TTL = 7 * 24 * 3600  # 7 days in seconds
_validation_cache: Optional[Dict[str, Any]] = None  # loaded lazily


def _load_validation_cache() -> Dict[str, Any]:
    global _validation_cache
    if _validation_cache is not None:
        return _validation_cache
    try:
        if _VALIDATION_CACHE_PATH.exists():
            _validation_cache = json.loads(
                _VALIDATION_CACHE_PATH.read_text(encoding="utf-8"))
            return _validation_cache
    except Exception:
        pass
    _validation_cache = {}
    return _validation_cache


def _save_validation_cache(cache: Dict[str, Any]) -> None:
    try:
        _VALIDATION_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        cutoff = time.time() - _VALIDATION_CACHE_TTL
        pruned = {k: v for k, v in cache.items() if v.get("ts", 0) > cutoff}
        _VALIDATION_CACHE_PATH.write_text(
            json.dumps(pruned, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception as exc:
        logger.warning("visual_validator: could not save cache — %s", exc)


# Log once which key source we use (so user can confirm we're not using GOOGLE_API_KEY)
_gemini_key_logged = False


class VisualValidator:
    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    async def fetch_image(self, url: str) -> Tuple[Optional[bytes], Optional[str]]:
        """Fetch image bytes safely."""
        if not url:
            return None, None
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                resp = await client.get(url, timeout=self.timeout)
                if resp.status_code != 200:
                    return None, None
                return resp.content, resp.headers.get("content-type", "")
        except Exception as e:
            logger.debug("Fetch failed for %s: %s", url, e)
            return None, None

    def fetch_image_sync(self, url: str) -> Tuple[Optional[bytes], Optional[str]]:
        """Fetch image bytes synchronously (for ingestion pipeline)."""
        if not url:
            return None, None
        try:
            with httpx.Client(follow_redirects=True, timeout=self.timeout) as client:
                resp = client.get(url)
                if resp.status_code != 200:
                    return None, None
                return resp.content, resp.headers.get("content-type", "")
        except Exception as e:
            logger.debug("Fetch failed for %s: %s", url, e)
            return None, None

    def validate_quality(self, img_bytes: bytes, purpose: str = "hero") -> Dict[str, Any]:
        """
        Score image quality (0-100) based on resolution, size, and visual data.
        """
        if not HAS_PILLOW:
            return {"score": 50, "status": "UNKNOWN", "note": "Pillow missing"}

        try:
            img = Image.open(io.BytesIO(img_bytes))
            width, height = img.size
            fmt = img.format or "UNKNOWN"
            size_kb = len(img_bytes) / 1024

            score = 100
            issues = []

            # 1. Resolution Checks
            min_w, min_h = (800, 600) if purpose == "hero" else (200, 200)
            if width < min_w or height < min_h:
                score -= 30
                issues.append(f"Low resolution: {width}x{height}")

            # 2. File Size Checks
            if size_kb < 10:  # Suspiciously small
                score -= 40
                issues.append("Suspiciously small file size")
            elif size_kb > 5000:
                score -= 10
                issues.append("File too large (>5MB)")

            # 3. Visual Content (Entropy check for solid colors/placeholders)
            stat = ImageStat.Stat(img.convert("L"))
            if stat.stddev[0] < 10:  # Very low variance = solid color or simple graphic
                score -= 50
                issues.append(
                    "Low visual detail (likely placeholder or solid color)")

            # 4. Aspect Ratio (squarish or landscape preferred for products)
            aspect = width / height
            if aspect < 0.5 or aspect > 2.5:
                score -= 10
                issues.append(f"Extreme aspect ratio: {aspect:.2f}")

            return {
                "score": max(0, score),
                "status": "pass" if score > 60 else "fail",
                "width": width,
                "height": height,
                "format": fmt,
                "issues": issues,
            }

        except Exception as e:
            return {"score": 0, "status": "error", "error": str(e)}

    def compare_images(self, bytes_a: bytes, bytes_b: bytes) -> Dict[str, Any]:
        """
        Compare two images to check if they are visually identical or variants.
        Returns similarity score (0.0 to 1.0).
        """
        if not HAS_PILLOW:
            return {"similarity": 0.0, "error": "Pillow missing"}

        try:
            img_a = Image.open(io.BytesIO(bytes_a)).convert("L")
            img_b = Image.open(io.BytesIO(bytes_b)).convert("L")

            # 1. Resize to common thumbnail for comparison (ignoring slight aspect diffs)
            common_size = (64, 64)
            img_a_thumb = img_a.resize(common_size, _LANCZOS)
            img_b_thumb = img_b.resize(common_size, _LANCZOS)

            # 2. Calculate pixel-by-pixel difference (RMS)
            diff = ImageChops.difference(img_a_thumb, img_b_thumb)
            stat = ImageStat.Stat(diff)
            diff_val = math.sqrt(
                sum(s ** 2 for s in stat.mean) / len(stat.mean))

            # Normalize: 0 is identical, 255 is opposite
            similarity = 1.0 - (diff_val / 255.0)

            # 3. Decision Logic
            verdict = "different"
            if similarity > 0.98:
                verdict = "identical"
            elif similarity > 0.90:
                verdict = "similar"  # Likely same image, different compression/size

            return {
                "similarity": round(similarity, 4),
                "verdict": verdict,
                "diff_score": round(diff_val, 2),
            }

        except Exception as e:
            return {"similarity": 0.0, "error": str(e)}

    def _mime_from_bytes(self, img_bytes: bytes) -> str:
        """Infer MIME type from image bytes for Gemini API."""
        if not img_bytes:
            return "image/jpeg"
        if img_bytes[:8].startswith(b"\x89PNG"):
            return "image/png"
        if img_bytes[:4] == b"RIFF" and img_bytes[8:12] == b"WEBP":
            return "image/webp"
        if img_bytes[:2] == b"\xff\xd8":
            return "image/jpeg"
        return "image/jpeg"

    def audit_quality_ai(
        self,
        img_bytes: bytes,
        product_name: Optional[str] = None,
        brand: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        AI-powered image quality audit using Gemini vision.
        Assesses whether the image is a suitable product hero: real product photo,
        not a placeholder, good composition, readable.
        Returns same shape as validate_quality plus ai_verdict, ai_issues, is_placeholder.
        """
        # Ensure .env is loaded when running from CLI or other contexts
        from backend.env_secrets import get_gemini_api_key
        api_key = get_gemini_api_key()
        if not api_key:
            return {
                "score": 50,
                "status": "UNKNOWN",
                "note": "No Gemini API key — set GEMINI_API_KEY in .env (from aistudio.google.com/app/apikey)",
                "ai_verdict": None,
                "ai_issues": [],
                "is_placeholder": None,
            }
        global _gemini_key_logged
        if not _gemini_key_logged:
            logger.info(
                "Using GEMINI_API_KEY for vision (%d chars)", len(api_key))
            _gemini_key_logged = True

        context = ""
        if product_name or brand:
            context = f"\nProduct context: {brand or ''} {product_name or ''}".strip(
            )

        prompt = f"""You are a catalog quality auditor for a music instrument e-commerce site.
Look at this product image and decide if it is acceptable as a HERO image (main product photo).

Consider:
- Is it a real product photo (not a placeholder, "no image", or generic graphic)?
- Is the product clearly visible and well-framed?
- Is it blurry, too dark, or cropped badly?
- Would a customer trust this image?
{context}

Respond with ONLY a JSON object, no markdown or extra text:
{{
  "acceptable": true or false,
  "score": 0-100,
  "is_placeholder": true or false,
  "issues": ["short issue 1", "short issue 2"],
  "recommendation": "one short sentence"
}}"""

        try:
            from google import genai

            client = genai.Client(api_key=api_key)
            mime = self._mime_from_bytes(img_bytes)

            # Limit size for API (e.g. 4MB); resize if needed to avoid token limits
            max_bytes = 4 * 1024 * 1024
            payload = img_bytes
            if HAS_PILLOW and len(img_bytes) > max_bytes:
                img = Image.open(io.BytesIO(img_bytes))
                img.thumbnail((1024, 1024), _LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=85)
                payload = buf.getvalue()
                mime = "image/jpeg"

            contents = [
                {
                    "role": "user",
                    "parts": [
                        {"inline_data": {"mime_type": mime, "data": payload}},
                        {"text": prompt},
                    ],
                }
            ]

            response = client.models.generate_content(
                model=GEMINI_VISION_MODEL,
                contents=contents,
            )
            text = (response.text or "").strip()
            # Strip markdown code block if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            data = json.loads(text)
            score = int(data.get("score", 50))
            acceptable = data.get("acceptable", score >= 60)
            issues = data.get("issues") or []
            is_placeholder = data.get("is_placeholder", False)

            return {
                "score": score,
                "status": "pass" if acceptable else "fail",
                "issues": issues,
                "ai_verdict": data.get("recommendation", ""),
                "ai_issues": issues,
                "is_placeholder": is_placeholder,
                "source": "ai",
            }
        except json.JSONDecodeError as e:
            logger.warning("AI audit JSON parse failed: %s", e)
            return {
                "score": 50,
                "status": "UNKNOWN",
                "error": f"AI response parse failed: {e}",
                "ai_verdict": None,
                "ai_issues": [],
                "is_placeholder": None,
            }
        except Exception as e:
            logger.warning("AI audit failed: %s", e)
            return {
                "score": 0,
                "status": "error",
                "error": str(e),
                "ai_verdict": None,
                "ai_issues": [],
                "is_placeholder": None,
            }

    def classify_product_image(
        self,
        img_bytes: bytes,
        product_name: Optional[str] = None,
        brand: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Use vision AI to classify product type from image for grouping/verification.
        Returns a short label (e.g. "guitar bag", "microphone stand", "cable") so
        items can be visually verified and smartly grouped (e.g. all guitar bags under one item).
        """
        from backend.env_secrets import get_gemini_api_key
        api_key = get_gemini_api_key()
        if not api_key:
            return {
                "visual_type": None,
                "visual_type_normalized": None,
                "confidence": 0,
                "error": "No Gemini API key — set GEMINI_API_KEY in .env (from aistudio.google.com/app/apikey)",
            }
        global _gemini_key_logged
        if not _gemini_key_logged:
            logger.info(
                "Using GEMINI_API_KEY for vision (%d chars)", len(api_key))
            _gemini_key_logged = True

        context = ""
        if product_name or brand:
            context = f" Product name or brand: {brand or ''} {product_name or ''}".strip(
            )

        prompt = f"""You are a catalog classifier for a music instrument e-commerce site.
Look at this product image and choose ONE short product-type label (2-4 words) that best describes what the product IS for grouping with similar items.

Examples: "guitar soft case", "ukulele bag", "microphone stand", "keyboard stand", "instrument cable", "drum throne", "audio interface", "studio monitor", "effect pedal".
Use lowercase, no brand names. Be specific enough to group similar products (e.g. "guitar bag" not just "bag").{context}

Respond with ONLY a JSON object, no markdown:
{{ "label": "your 2-4 word type", "confidence": 0.0-1.0 }}"""

        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            mime = self._mime_from_bytes(img_bytes)
            max_bytes = 4 * 1024 * 1024
            payload = img_bytes
            if HAS_PILLOW and len(img_bytes) > max_bytes:
                img = Image.open(io.BytesIO(img_bytes))
                img.thumbnail((1024, 1024), _LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=85)
                payload = buf.getvalue()
                mime = "image/jpeg"

            contents = [{
                "role": "user",
                "parts": [
                    {"inline_data": {"mime_type": mime, "data": payload}},
                    {"text": prompt},
                ],
            }]
            response = client.models.generate_content(
                model=GEMINI_VISION_MODEL,
                contents=contents,
            )
            text = (response.text or "").strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            data = json.loads(text)
            label = (data.get("label") or "").strip().lower()
            confidence = float(data.get("confidence", 0.8))
            # Normalize for grouping: e.g. "guitar soft case" -> "cases-bags"
            visual_type_normalized = None
            if label:
                if any(x in label for x in ("case", "bag", "cover")):
                    visual_type_normalized = "cases-bags"
                elif "stand" in label:
                    visual_type_normalized = "stands"
                elif "pedal" in label:
                    visual_type_normalized = "pedals"
                else:
                    visual_type_normalized = label.replace(" ", "-")[:30]
            return {
                "visual_type": label or None,
                "visual_type_normalized": visual_type_normalized,
                "confidence": confidence,
            }
        except json.JSONDecodeError as e:
            logger.warning("Visual classify JSON parse failed: %s", e)
            return {"visual_type": None, "visual_type_normalized": None, "confidence": 0, "error": str(e)}
        except Exception as e:
            logger.warning("Visual classify failed: %s", e)
            return {"visual_type": None, "visual_type_normalized": None, "confidence": 0, "error": str(e)}


_validator: Optional[VisualValidator] = None


def get_visual_validator() -> VisualValidator:
    global _validator
    if _validator is None:
        _validator = VisualValidator()
    return _validator


# ─── Ingestion pipeline: validate hero before accepting ─────────────────────

def validate_hero_candidates(
    candidate_urls: List[str],
    purpose: str = "hero",
    product_name: Optional[str] = None,
    brand: Optional[str] = None,
) -> Tuple[Optional[str], List[str], List[Dict[str, Any]]]:
    """
    Try each candidate URL in order; return the first that passes quality checks.
    Used by the ingestion pipeline to reject placeholders and low-quality images at the source.

    Performance:
    - When INGESTION_SKIP_VISUAL_VALIDATION=1: no fetching at all — first URL wins.
    - Otherwise: results are cached on disk (7-day TTL) keyed by URL.  A URL
      that passed on a previous run is accepted immediately without re-fetching.

    Returns:
        (accepted_hero_url or None, gallery_order [hero first then rest], validation_results)
    """
    if INGESTION_SKIP_VISUAL_VALIDATION:
        if candidate_urls:
            return candidate_urls[0], candidate_urls, []
        return None, [], []

    cache = _load_validation_cache()
    now = time.time()
    cache_dirty = False

    validator = get_visual_validator()
    results: List[Dict[str, Any]] = []
    accepted: Optional[str] = None
    rest: List[str] = []

    for url in candidate_urls:
        if not url:
            continue

        # ── Cache hit: skip network fetch entirely ────────────────────────
        cached_entry = cache.get(url)
        if cached_entry and now - cached_entry.get("ts", 0) < _VALIDATION_CACHE_TTL:
            quality = cached_entry["result"]
            quality["url"] = url
            quality["_cached"] = True
            results.append(quality)
            if quality.get("status") == "pass":
                accepted = url
                rest = [u for u in candidate_urls if u != url and u]
                logger.debug("Ingestion: cache HIT (pass) for %s", url[:70])
                break
            rest.append(url)
            logger.debug("Ingestion: cache HIT (fail) for %s", url[:70])
            continue

        # ── Cache miss: fetch and validate ───────────────────────────────
        img_bytes, _ = validator.fetch_image_sync(url)
        if not img_bytes:
            results.append({"url": url, "status": "fetch_failed"})
            rest.append(url)
            continue
        quality = validator.validate_quality(img_bytes, purpose=purpose)
        quality["url"] = url
        results.append(quality)

        # Persist result (pass or fail) so the next run is instant
        cache[url] = {"result": {k: v for k,
                                 v in quality.items() if k != "url"}, "ts": now}
        cache_dirty = True

        if quality.get("status") == "pass":
            accepted = url
            rest = [u for u in candidate_urls if u != url and u]
            break
        rest.append(url)
        logger.debug(
            "Ingestion: rejected hero %s (score=%s) for %s",
            url[:60] + "..." if len(url) > 60 else url,
            quality.get("score"),
            (brand or "") + " " + (product_name or ""),
        )

    if cache_dirty:
        _save_validation_cache(cache)

    if accepted:
        gallery_order = [accepted] + rest
    else:
        gallery_order = rest  # Keep URLs for gallery even if no valid hero
    return accepted, gallery_order, results


# ─── Commercial vs official match: reject mismatches ───────────────────────

# In-memory cache for this process: (commercial_url, official_url) -> result.
# Avoids re-fetching the same image pair when normalizing many products in one catalog build.
_match_cache: Dict[Tuple[str, str], Dict[str, Any]] = {}


def validate_commercial_official_match(
    commercial_hero_url: str,
    official_hero_url: str,
    min_similarity: float = 0.85,
) -> Dict[str, Any]:
    """
    Compare commercial (Halilit) hero image with official (brand) hero image.
    Used to ensure we don't attach official data to the wrong product.

    Returns:
        match (bool), similarity (0–1), verdict, and optional error.
    """
    if INGESTION_SKIP_VISUAL_VALIDATION:
        return {"match": True, "similarity": 1.0, "verdict": "skipped", "note": "validation disabled"}

    commercial_hero_url = (commercial_hero_url or "").strip()
    official_hero_url = (official_hero_url or "").strip()
    if not commercial_hero_url or not official_hero_url:
        return {"match": False, "similarity": 0.0, "verdict": "missing", "error": "Missing commercial or official URL"}

    # Use in-memory cache so the same image pair is only fetched once per catalog build
    cache_key = (commercial_hero_url, official_hero_url)
    if cache_key in _match_cache:
        return _match_cache[cache_key]

    validator = get_visual_validator()
    bytes_commercial, _ = validator.fetch_image_sync(commercial_hero_url)
    bytes_official, _ = validator.fetch_image_sync(official_hero_url)
    if not bytes_commercial:
        return {"match": False, "similarity": 0.0, "verdict": "fetch_failed", "error": "Could not fetch commercial image"}
    if not bytes_official:
        return {"match": False, "similarity": 0.0, "verdict": "fetch_failed", "error": "Could not fetch official image"}

    comparison = validator.compare_images(bytes_commercial, bytes_official)
    similarity = comparison.get("similarity", 0.0)
    verdict = comparison.get("verdict", "different")
    match = similarity >= min_similarity
    if not match:
        logger.info(
            "Commercial vs official image mismatch (similarity=%.2f) — rejecting official data",
            similarity,
        )
    result = {
        "match": match,
        "similarity": similarity,
        "verdict": verdict,
        "min_similarity": min_similarity,
    }
    _match_cache[cache_key] = result
    return result


def reject_official_if_mismatch(product: Dict[str, Any], min_similarity: float = 0.85) -> Dict[str, Any]:
    """
    If product has both commercial hero (image_url) and official images, compare them.
    On mismatch: clear official_images and official_url so we don't treat them as the same product.
    Uses cached visual_match_status when present to avoid re-fetching images on every catalog build.
    Modifies product in place and returns it.
    """
    commercial_url = (product.get("image_url") or "").strip()
    official_list = product.get("official_images") or []
    official_hero_url = None
    if official_list:
        first = official_list[0]
        official_hero_url = (first.get("url") if isinstance(
            first, dict) else first) or ""

    # Only validate when a real official brand URL exists.
    # Without official_url, the "official_images" are just Halilit CDN images —
    # comparing them against themselves wastes time and produces no value.
    if not product.get("official_url"):
        return product

    if not official_hero_url and product.get("official_url"):
        # We have official_url but no official_images — can't compare; leave as-is
        return product
    if not commercial_url or not official_hero_url:
        return product

    # Use cached result from a previous run to avoid re-fetching on every sync/catalog build
    cached = product.get("visual_match_status")
    if cached == "matched":
        return product
    if cached == "mismatch":
        product["official_images"] = []
        product["official_url"] = ""
        return product

    result = validate_commercial_official_match(
        commercial_url, official_hero_url, min_similarity=min_similarity)
    if result.get("match"):
        product["visual_match_status"] = "matched"
        product["visual_match_confidence"] = result.get("similarity", 0.0)
        return product

    # Mismatch: reject official data for this product
    product["official_images"] = []
    product["official_url"] = ""
    product["visual_match_status"] = "mismatch"
    product["visual_match_confidence"] = result.get("similarity", 0.0)
    if "validation_warnings" not in product:
        product["validation_warnings"] = []
    product["validation_warnings"].append(
        "Official image did not match commercial image; official data cleared (visual validation)."
    )
    logger.debug(
        "Rejected official data for product (similarity=%.2f)",
        result.get("similarity", 0),
    )
    return product
