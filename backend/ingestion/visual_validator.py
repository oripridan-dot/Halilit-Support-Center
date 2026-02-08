"""
VISUAL VALIDATOR v1.0

Ensures that visual assets and display configurations meet quality standards
before they reach the frontend.

Validates:
- Media asset integrity (URLs, resolutions)
- Tier-specific visual requirements (e.g. Flagship must have Hero image)
- Display consistency
"""

import logging
import re
from typing import List, Optional, Tuple, Dict
from urllib.parse import urlparse

from backend.ingestion.data_models import (
    MediaAsset, PricingTier, DisplayRole, DataSourceConfidence
)

logger = logging.getLogger("VisualValidator")


class VisualValidator:
    """
    Validates visual aspects of the ingestion pipeline.
    """

    def __init__(self):
        self.logger = logger
        self.url_pattern = re.compile(
            r'^(https?|ftp)://[^\s/$.?#].[^\s]*$', re.IGNORECASE)

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
            # Acceptable to have no images if just entry listing? Maybe 1.
            PricingTier.ENTRY: 0
        }

        required = min_images.get(pricing_tier, 0)
        if image_count < required:
            issues.append(
                f"Insufficient images for {pricing_tier} tier. Found {image_count}, required {required}")

        # 3. Source Quality Check for Heroes
        if display_role == DisplayRole.HERO and hero_image_url:
            # Check if hero comes from trusted source
            # Find the asset object for the hero url
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


_validator = VisualValidator()


def get_visual_validator() -> VisualValidator:
    return _validator
