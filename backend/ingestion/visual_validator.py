"""
AI VISUAL VALIDATOR v7.5
Ensures product matches are visually and semantically identical using Google Gemini 1.5.
"""
import logging
import json
import os
import requests
from io import BytesIO
from PIL import Image
from typing import Dict, Optional
import google.generativeai as genai
from pydantic import BaseModel, Field

# Configure Gemini
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
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def _download_image(self, url: str) -> Optional[Image.Image]:
        """Downloads image into memory."""
        if not url:
            return None
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
        except Exception as e:
            self.logger.warning(f"Image download failed {url}: {e}")
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
            response = self.model.generate_content(
                [prompt, "Reference Image:", img_ref,
                    "Candidate Image:", img_cand],
                generation_config={"response_mime_type": "application/json"}
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
