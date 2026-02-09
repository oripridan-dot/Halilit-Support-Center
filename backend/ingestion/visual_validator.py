"""
AI VISUAL VALIDATOR v7.3

The "Eyes" of the Conductor.
Uses Google Gemini 1.5 Flash (Multimodal) to verify that two products are 
identical matches by analyzing both their visual appearance and commercial context.

Key Features:
- Visual Matching: Compares shape, buttons, finish, and layout.
- Contextual Grounding: Uses official names/SKUs to prevent "look-alike" errors (e.g., Speaker vs Speaker Bag).
- Commercial Awareness: Ignores regional differences (plugs, voltages).
"""

import logging
import time
import json
import requests
import re
from io import BytesIO
from PIL import Image
from typing import Dict, Optional, Tuple, List
import google.generativeai as genai
from pydantic import BaseModel, Field

from backend.ingestion.data_models import (
    MediaAsset, PricingTier, DisplayRole, DataSourceConfidence
)

# Ensure you have this configured in your environment or config
import os
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure Gemini
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception as e:
        print(f"Warning: Failed to configure Gemini AI: {e}")


class VerificationResult(BaseModel):
    is_match: bool = Field(
        description="True if products are the exact same technical model")
    confidence: float = Field(description="0.0 to 1.0 confidence score")
    reason: str = Field(description="Explanation for the decision")
    flag: Optional[str] = Field(
        None, description="Warning flags (e.g., 'different_color', 'newer_version')")


class VisualValidator:
    def __init__(self):
        self.logger = logging.getLogger("VisualValidator")
        try:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            self.logger.warning(f"Could not initialize Gemini model: {e}")
            self.model = None

        # Browser-like headers for fetching images from Thomann/Halilit
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.url_pattern = re.compile(
            r'^(https?|ftp)://[^\s/$.?#].[^\s]*$', re.IGNORECASE)

    def _download_image(self, url: str) -> Optional[Image.Image]:
        """Downloads an image from a URL into memory."""
        if not url:
            return None
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
        except Exception as e:
            self.logger.warning(f"Failed to download image {url}: {e}")
        return None

    def verify_match(self,
                     reference: Dict,
                     candidate: Dict,
                     strict_mode: bool = True) -> VerificationResult:
        """
        Verifies if candidate (Thomann) matches reference (Halilit).

        Args:
            reference: Dict containing 'name', 'image_url', 'brand', 'description'
            candidate: Dict containing 'name', 'image_url', 'price'
        """
        if not self.model:
            return VerificationResult(is_match=False, confidence=0.0, reason="AI Model not initialized")

        # 1. Download Images
        img_ref = self._download_image(reference.get('image_url'))
        img_cand = self._download_image(candidate.get('image_url'))

        if not img_ref or not img_cand:
            return VerificationResult(is_match=False, confidence=0.0, reason="Missing Images")

        # 2. Construct Commercial Context
        context_prompt = f"""
        You are an Expert Audio Equipment Validator.
        Your task is to verify if 'Product A' and 'Product B' are the EXACT SAME commercial product.
        
        --- COMMERCIAL CONTEXT ---
        Product A (Reference / Local):
        - Name: {reference.get('name', 'Unknown')}
        - Brand: {reference.get('brand', 'Unknown')}
        - Description Snippet: {reference.get('description', '')[:200]}...
        
        Product B (Candidate / Import):
        - Name: {candidate.get('name', 'Unknown')}
        - Price: {candidate.get('price', 'Unknown')}
        
        --- STRICT VALIDATION RULES ---
        1. **Identity:** Must be the same model number and revision (e.g., MK2 vs MK3 are DIFFERENT).
        2. **Category Check:** A 'Speaker' and a 'Speaker Cover/Bag' are NOT a match, even if they look similar.
        3. **Visual Check:** Count knobs, faders, and inputs. They must match exactly.
        4. **Ignore:** Power plug types (EU vs IL/UK) or voltage differences.
        5. **Ignore:** Minor color variations unless it defines a completely different model ID.
        
        Output strictly in JSON: {{ "is_match": bool, "confidence": float, "reason": "string", "flag": "string|null" }}
        """

        try:
            # 3. AI Inference
            response = self.model.generate_content(
                [context_prompt, "Product A Image:",
                    img_ref, "Product B Image:", img_cand],
                generation_config={"response_mime_type": "application/json"}
            )

            # 4. Parse Result
            result_data = json.loads(response.text)

            # Enforce threshold
            is_match = result_data['is_match'] and result_data['confidence'] > 0.85

            return VerificationResult(
                is_match=is_match,
                confidence=result_data['confidence'],
                reason=result_data['reason'],
                flag=result_data.get('flag')
            )

        except Exception as e:
            self.logger.error(f"AI Verification Failed: {e}")
            return VerificationResult(is_match=False, confidence=0.0, reason=f"AI Error: {str(e)}")

    def validate_display_readiness(
        self,
        pricing_tier: PricingTier,
        display_role: DisplayRole,
        media_assets: List[MediaAsset],
        hero_image_url: Optional[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validates if the product is visually ready for the given tier/role.

        Returns: (is_valid, list_of_issues)
        """
        issues = []

        # 1. Hero Image Validation
        if not hero_image_url:
            if display_role in [DisplayRole.HERO, DisplayRole.CORNERSTONE]:
                issues.append(
                    f"Missing hero image for high-visibility role: {display_role}")
            elif pricing_tier in [PricingTier.FLAGSHIP, PricingTier.PRO]:
                issues.append(
                    f"Missing hero image for high-value tier: {pricing_tier}")
        else:
            if not self._is_valid_url(hero_image_url):
                issues.append(f"Invalid hero image URL: {hero_image_url}")

        # 2. Asset Quantity Check
        image_count = len([a for a in media_assets if a.type == 'image'])

        min_images = {
            PricingTier.FLAGSHIP: 3,
            PricingTier.PRO: 2,
            PricingTier.MID: 1,
            PricingTier.ENTRY: 0
        }

        required = min_images.get(pricing_tier, 0)
        if image_count < required:
            issues.append(
                f"Insufficient images for {pricing_tier} tier. Found {image_count}, required {required}")

        # 3. Source Quality Check for Heroes
        if display_role == DisplayRole.HERO and hero_image_url:
            hero_asset = next(
                (a for a in media_assets if a.url == hero_image_url), None)
            if hero_asset:
                if hero_asset.source not in [DataSourceConfidence.OFFICIAL, DataSourceConfidence.TRUSTED, DataSourceConfidence.COMMERCIAL]:
                    issues.append(
                        f"Hero image source low confidence: {hero_asset.source}")

        return len(issues) == 0, issues

    def _is_valid_url(self, url: str) -> bool:
        """Basic regex URL validation"""
        if not url:
            return False
        return re.match(self.url_pattern, url) is not None


# Singleton instance for easy import
visual_validator = VisualValidator()


def get_visual_validator() -> VisualValidator:
    return visual_validator
