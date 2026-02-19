"""
VISUAL QA — backend/factory/visual_qa.py
=========================================
Playwright-backed screenshot capture + Gemini vision analysis for the
Gatekeeper's ``screenshot_description`` parameter.

Design
------
- **Auto-bootstrap**: Playwright is detected at runtime. If unavailable the
  module degrades gracefully to text-only mode without crashing the pipeline.
- **Single entry-point**: ``capture_and_describe(url, spec_text)`` — returns a
  plain-text UI-state description suitable for injecting into the Gatekeeper
  LLM prompt.
- **Composable**: can be called standalone (``python visual_qa.py``) for
  manual spot-checks, or imported by ``watchdog_agent.gatekeeper_review``.

Pipeline Role
-------------
  Builder inner-loop passes
        ↓
  gatekeeper_review(…, screenshot_description=capture_and_describe(url, spec))
        ↓
  APPROVED / REJECTED  →  improvement_cycle advances

Architecture Note
-----------------
Playwright auto-bootstraps on first use; the browser binary is cached by
Playwright itself. This file never writes any data to ``backend/data/`` (that
is the Three Source rules' domain).
"""

from __future__ import annotations

import base64
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Playwright availability probe
# ---------------------------------------------------------------------------

_PLAYWRIGHT_AVAILABLE: Optional[bool] = None  # cached after first check


def _playwright_available() -> bool:
    """Return True if playwright is importable and browsers are installed."""
    global _PLAYWRIGHT_AVAILABLE
    if _PLAYWRIGHT_AVAILABLE is not None:
        return _PLAYWRIGHT_AVAILABLE

    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
        _PLAYWRIGHT_AVAILABLE = True
    except ImportError:
        logger.warning(
            "visual_qa: playwright not installed — degrading to text-only mode. "
            "Run `pip install playwright && playwright install chromium` to enable."
        )
        _PLAYWRIGHT_AVAILABLE = False
    return _PLAYWRIGHT_AVAILABLE


def _bootstrap_playwright() -> bool:
    """
    Install playwright browsers on first use if the package is installed but
    browsers have never been downloaded.  Returns True if ready to use.
    """
    if not _playwright_available():
        return False

    # Test if at least chromium is usable
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        return True
    except Exception as exc:
        logger.info(
            "visual_qa: chromium not found — attempting `playwright install chromium`...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                logger.info("visual_qa: chromium installed successfully.")
                return True
            logger.warning(
                "visual_qa: playwright install failed (%s) — text-only mode.",
                result.stderr[:200],
            )
        except Exception as install_exc:
            logger.warning("visual_qa: browser install error: %s", install_exc)
        return False


# ---------------------------------------------------------------------------
# Screenshot capture
# ---------------------------------------------------------------------------

def take_screenshot(
    url: str = "http://localhost:5173",
    output_path: Optional[Path] = None,
    wait_ms: int = 2000,
) -> Optional[Path]:
    """
    Navigate to *url* with a headless Chromium browser and capture a full-page
    screenshot.

    Args:
        url:         Target URL (default: Vite dev-server).
        output_path: Where to save the PNG. Uses a temp file if None.
        wait_ms:     Milliseconds to wait after page-load for JS render.

    Returns:
        Path to the saved PNG, or None if capture fails.
    """
    if not _bootstrap_playwright():
        return None

    if output_path is None:
        fd, tmp = tempfile.mkstemp(suffix=".png", prefix="visual_qa_")
        os.close(fd)
        output_path = Path(tmp)

    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 900})
            try:
                page.goto(url, timeout=15_000, wait_until="networkidle")
            except PWTimeout:
                # Partial load — still worth screenshotting
                logger.info(
                    "visual_qa: page load timed-out, screenshotting partial state")

            if wait_ms > 0:
                page.wait_for_timeout(wait_ms)

            page.screenshot(path=str(output_path), full_page=True)
            browser.close()

        logger.info("visual_qa: screenshot saved → %s", output_path)
        return output_path

    except Exception as exc:
        logger.warning("visual_qa: screenshot failed — %s", exc)
        return None


# ---------------------------------------------------------------------------
# Gemini vision analysis
# ---------------------------------------------------------------------------

def _load_gemini_client():
    """Return a ``google.genai.Client`` or None if key is missing."""
    try:
        import google.genai as genai
        from dotenv import load_dotenv
        _root = Path(__file__).resolve().parent.parent.parent
        load_dotenv(_root / ".env")
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return None
        return genai.Client(api_key=api_key)
    except ImportError:
        return None


def analyse_screenshot(
    screenshot_path: Path,
    spec_text: str = "",
    hint: str = "",
) -> str:
    """
    Send *screenshot_path* to Gemini 2.0 Flash and return a structured
    UI-state description.

    Args:
        screenshot_path: PNG to analyse.
        spec_text:       Original spec — helps the model spot spec deviations.
        hint:            Optional extra instruction (e.g. "focus on the inventory grid").

    Returns:
        A plain-text description (~200–400 words) of what is visible.
        Falls back to a minimal stub if the API is unavailable.
    """
    client = _load_gemini_client()
    if client is None:
        return "[visual_qa: Gemini API key not set — no visual description available]"

    # Read image bytes and encode
    img_bytes = screenshot_path.read_bytes()
    img_b64 = base64.b64encode(img_bytes).decode()

    spec_snippet = spec_text[:800] if spec_text else "(no spec provided)"
    extra = f"\nExtra focus: {hint}" if hint else ""

    prompt = f"""You are a UI Quality Analyst reviewing a screenshot of a React web application.

SPEC SUMMARY (what the UI is supposed to show):
{spec_snippet}
{extra}

Describe what you see in the screenshot in 200–400 words. Cover:
1. Overall layout and visible sections.
2. Any obvious errors, blank panels, or broken elements.
3. Whether visible content matches the spec intent (if provided).
4. Any loading spinners, empty states, or placeholder text.

Be factual and objective. Do not guess at invisible state."""

    try:
        import google.genai.types as gtypes

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                gtypes.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                gtypes.Part.from_text(prompt),
            ],
        )
        return response.text or "[visual_qa: empty response from model]"

    except Exception as exc:
        logger.warning("visual_qa: Gemini vision call failed — %s", exc)
        return f"[visual_qa: vision analysis failed — {exc}]"


# ---------------------------------------------------------------------------
# Public entry-point
# ---------------------------------------------------------------------------

def capture_and_describe(
    url: str = "http://localhost:5173",
    spec_text: str = "",
    hint: str = "",
    cleanup: bool = True,
) -> str:
    """
    One-shot helper: take a screenshot of *url* and return a Gemini vision
    description.  Safe to call even when Playwright/Gemini are absent —
    returns an explanatory stub in that case.

    Args:
        url:       URL to screenshot (default: Vite dev-server on 5173).
        spec_text: Spec markdown so the model knows what to look for.
        hint:      Optional extra focus directive.
        cleanup:   Delete the temp PNG after analysis (default True).

    Returns:
        Plain-text UI description for use as ``screenshot_description`` in
        ``gatekeeper_review``.
    """
    screenshot = take_screenshot(url=url)
    if screenshot is None:
        return "[visual_qa: screenshot capture unavailable — no visual QA performed]"

    try:
        description = analyse_screenshot(
            screenshot_path=screenshot,
            spec_text=spec_text,
            hint=hint,
        )
        return description
    finally:
        if cleanup and screenshot.exists():
            try:
                screenshot.unlink()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Visual QA — capture & describe a page")
    parser.add_argument(
        "--url", default="http://localhost:5173", help="URL to screenshot")
    parser.add_argument("--spec", default="",
                        help="Path to spec file for context")
    parser.add_argument("--hint", default="",
                        help="Extra focus directive for the vision model")
    parser.add_argument("--save", default="",
                        help="Save screenshot to this path (skip cleanup)")
    args = parser.parse_args()

    spec_content = ""
    if args.spec:
        sp = Path(args.spec)
        if sp.exists():
            spec_content = sp.read_text(encoding="utf-8")
        else:
            print(f"⚠️  Spec file not found: {args.spec}")

    if args.save:
        shot = take_screenshot(url=args.url, output_path=Path(args.save))
        if shot:
            print(f"📸 Screenshot saved: {shot}")
            desc = analyse_screenshot(shot, spec_content, args.hint)
            print("\n=== VISUAL QA DESCRIPTION ===")
            print(desc)
        else:
            print("❌ Screenshot failed.")
    else:
        desc = capture_and_describe(
            url=args.url, spec_text=spec_content, hint=args.hint)
        print("\n=== VISUAL QA DESCRIPTION ===")
        print(desc)
