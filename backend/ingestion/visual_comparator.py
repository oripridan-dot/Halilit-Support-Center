"""
VISUAL COMPARATOR v1.0

Performs AI-based visual comparison between Commercial (Halilit) and Official (Brand) 
product images to verify product identity.

This solves the "Same Name, Different Product" problem by looking at the pixels.
"""

import logging
import os
import requests
import base64
from typing import Dict, Tuple, Optional
from backend.ingestion.data_models import IngestionProductDraft, DataSourceConfidence
import google.genai as genai
from google.genai import types

# Configure logging
logger = logging.getLogger("VisualComparator")


class VisualComparator:
    """
    Compares two images using a Vision Model (Gemini 2.0 Flash) to determine
    if they represent the same product.
    """

    def __init__(self, client: Optional[genai.Client] = None):
        self.client = client
        if not self.client:
            try:
                self.client = genai.Client(
                    api_key=os.environ.get("GOOGLE_API_KEY"))
            except Exception as e:
                logger.warning(f"Could not initialize Genai client: {e}")

    def compare_product_images(self, draft: IngestionProductDraft) -> Tuple[float, str, str]:
        """
        Compares the commercial (Halilit) image with the Official image.

        Returns:
            (confidence_score, reasoning, status)
        """
        if not self.client:
            return 0.0, "Vision client not available", "skipped"

        # 1. Identify Images
        commercial_url = draft.display.hero_image
        official_url = None

        # Find official image in official_images list
        if draft.official_images:
            # Prefer ones marked as hero or high priority
            official_url = draft.official_images[0].url

        if not commercial_url and not official_url:
            return 0.0, "Missing both Commercial and Official images", "skipped"
        elif not commercial_url:
            return 0.0, "Missing Commercial (Halilit) image for comparison", "skipped"
        elif not official_url:
            return 0.0, "Missing Official (Brand) image for comparison", "skipped"

        # 2. Download Images (In-Memory)
        try:
            img1_data = self._download_image(commercial_url)
            img2_data = self._download_image(official_url)
        except Exception as e:
            return 0.0, f"Failed to download images: {str(e)}", "error"

        if not img1_data or not img2_data:
            return 0.0, "Failed to retrieve image data", "error"

        # 3. Compare with Gemini Vision
        try:
            return self._ask_gemini_vision(img1_data, img2_data)
        except Exception as e:
            logger.error(f"Gemini Vision error: {e}")
            return 0.0, f"Vision model error: {str(e)}", "error"

    def _download_image(self, url: str) -> Optional[bytes]:
        """Downloads image bytes from URL"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.warning(f"Image download failed for {url}: {e}")
            raise e

    def _ask_gemini_vision(self, img1_bytes: bytes, img2_bytes: bytes) -> Tuple[float, str, str]:
        """Sends images to Gemini for comparison"""

        prompt = """
        You are an expert Production Validator.
        Compare these two product images.
        Image 1: Commercial Product (Store)
        Image 2: Official Product (Manufacturer)
        
        Task: Determine if these two images show the EXACT SAME product model.
        Ignore minor differences in lighting, angle, or color (unless color defines the model).
        Focus on:
        - Knob/button layout
        - Screen placement
        - Text/Labels
        - Physical form factor
        
        Respond ONLY with a JSON object:
        {
            "is_match": boolean,
            "confidence": float (0.0 to 1.0),
            "reasoning": "string explanation"
        }
        """

        try:
            # Prepare contents
            # Assuming client.models.generate_content supports bytes directly or via typed Part

            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    # Assuming generic jpeg handling or auto-detect
                    types.Part.from_bytes(
                        data=img1_bytes, mime_type="image/jpeg"),
                    types.Part.from_bytes(
                        data=img2_bytes, mime_type="image/jpeg"),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            import json
            result = json.loads(response.text)

            confidence = result.get("confidence", 0.0)
            is_match = result.get("is_match", False)
            reasoning = result.get("reasoning", "No reasoning provided")

            status = "matched" if is_match and confidence > 0.8 else "mismatch"
            if is_match and confidence <= 0.8:
                status = "uncertain"

            return confidence, reasoning, status

        except Exception as e:
            logger.error(f"Error parsing vision response: {e}")
            raise e


# Global singleton
_visual_comparator = None


def get_visual_comparator_engine(client: Optional[genai.Client] = None) -> VisualComparator:
    global _visual_comparator
    if _visual_comparator is None:
        _visual_comparator = VisualComparator(client)
    return _visual_comparator
