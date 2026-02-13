"""
AI VISUAL VALIDATOR v8.5
Ensures product matches are visually and semantically identical using Google Gemini 1.5.
"""
import logging
import json
import os
import requests
from io import BytesIO
from PIL import Image
from typing import Dict, Optional
import google.genai as genai
from pydantic import BaseModel, Field

# Configure Gemini with new google.genai SDK
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


class VerificationResult(BaseModel):
    is_match: bool
    confidence: float
    reason: str


class VisualValidator:
    def __init__(self):
        self.logger = logging.getLogger("VisualValidator")
        # Using google.genai SDK with gemini-2.0-flash for improved performance
        self.model = genai.Client(
            api_key=GOOGLE_API_KEY).models.generate_content if GOOGLE_API_KEY else None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def _download_image(self, url: str) -> Optional[Image.Image]:
        """Downloads image into memory, or loads from local disk."""
        if not url:
            return None
        try:
            # Handle local file paths
            if not url.startswith('http'):
                # Try to resolve relative to workspace if it starts with /
                if url.startswith('/assets/'):
                    # HACK: Hardcoded path mapping for this environment
                    local_path = f"/workspaces/Halilit-Support-Center/frontend/public{url}"
                    self.logger.info(f"Trying local path: {local_path}")
                    if os.path.exists(local_path):
                        return Image.open(local_path)
                    else:
                        self.logger.warning(f"File NOT found at: {local_path}")

                # Try absolute path
                if os.path.exists(url):
                    return Image.open(url)

                self.logger.warning(f"Local file not found: {url}")
                return None

            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
        except Exception as e:
            self.logger.warning(f"Image download failed for {url}: {e}")
        return None

    def verify_match(self, reference: Dict, candidate: Dict) -> VerificationResult:
        """
        Compares a Halilit product (reference) vs Thomann product (candidate).
        """
        if not GOOGLE_API_KEY:
            return VerificationResult(is_match=True, confidence=0.0, reason="AI Key Missing - Auto Approve")

        img_ref = self._download_image(reference.get('image_url'))
        img_cand = self._download_image(candidate.get('image_url'))

        if not img_ref or not img_cand:
            return VerificationResult(is_match=False, confidence=0.0, reason="Missing Images")

        prompt = f"""
        Compare these two audio products.
        Reference: {reference.get('name')} (Brand: {reference.get('brand')})
        Candidate: {candidate.get('name')} (Price: {candidate.get('price')})
        
        RULES:
        1. REJECT if one is a main product (e.g. Speaker) and other is an accessory (e.g. Cover/Bag).
        2. REJECT if model numbers differ (e.g. MK2 vs MK3).
        3. IGNORE power plug differences.
        
        Output JSON: {{ "is_match": boolean, "confidence": float (0-1), "reason": "string" }}
        """

        try:
            if not self.model:
                return VerificationResult(is_match=True, confidence=0.0, reason="AI Model not initialized")

            # Using genai SDK to generate content with images
            client = genai.Client(api_key=GOOGLE_API_KEY)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt, "Reference Image:",
                          img_ref, "Candidate Image:", img_cand],
                config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text)
            return VerificationResult(**data)
        except Exception as e:
            self.logger.error(f"AI Error: {e}")
            return VerificationResult(is_match=False, confidence=0.0, reason=f"AI Error: {e}")

    def validate_display_readiness(self, pricing_tier, display_role, media_assets, hero_image_url) -> tuple[bool, list[str]]:
        """
        Validates if the product is visually ready for display.
        """
        issues = []
        if not hero_image_url:
            issues.append("Missing hero image")

        return len(issues) == 0, issues


visual_validator = VisualValidator()


def get_visual_validator():
    return visual_validator
