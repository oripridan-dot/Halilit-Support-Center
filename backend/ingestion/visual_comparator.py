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

    def validate_single_image_claims(self, image_url: str, claims: Dict[str, str]) -> Tuple[bool, str, str, float]:
        """
        Validates if a single image supports the text claims provided.
        Returns: (is_consistent, evidence, discrepancy_details, confidence)
        """
        if not self.client or not image_url:
            return True, "Skipped", "No client or image", 0.0

        try:
            img_data = self._download_image(image_url)
            if not img_data:
                return True, "Skipped", "Image download failed", 0.0

            prompt = f"""
            You are an expert Visual Validator.
            Look at this product image and verify if it matches the following specific CLAIMS.
            
            CLAIMS:
            {claims}
            
            TASK:
            For each claim (e.g., Color=Black, Type=Drums), check if the image contradicts it.
            
            RESPONSE FORMAT (JSON ONLY):
            {{
                "is_consistent": boolean, 
                "confidence": float (0-1),
                "visual_evidence": "What you see explicitly in the image",
                "discrepancy": "Description of conflict if any, else 'None'"
            }}
            """

            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    types.Part.from_bytes(
                        data=img_data, mime_type="image/jpeg"),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json")
            )

            import json
            res = json.loads(response.text)
            return (
                res.get("is_consistent", True),
                res.get("visual_evidence", ""),
                res.get("discrepancy", ""),
                res.get("confidence", 0.0)
            )
        except Exception as e:
            logger.error(f"Single image validation failed: {e}")
            return True, "Error", str(e), 0.0

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
        Compare these two product images to verify they represent the SAME SKU/Model.
        Image 1: Commercial Product (Store)
        Image 2: Official Product (Manufacturer)
        
        TASK: Determine if these images refer to the same product model.
        
        CRITICAL RULES:
        1. IGNORE: Lighting, background, exact angle, or minor color variations (unless the product is SOLD by color).
        2. IGNORE: Presence of packaging/boxes in one image vs naked product in the other.
        3. IGNORE: Included accessories (cables, stands) shown in one image but not the other.
        4. FOCUS ON: Unique identifiers - Knob layouts, screen position, port definitions, logo placement, specific shape.
        5. REJECT: If one image is a generic "No Image Available" or placeholder logo.
        6. REJECT: If the products are clearly different models (e.g., 61 keys vs 88 keys, different button count).
        
        Respond ONLY with a JSON object:
        {
            "is_match": boolean,
            "confidence": float (0.0 to 1.0),
            "reasoning": "Concise explanation of key visual anchors matched or mismatched."
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
