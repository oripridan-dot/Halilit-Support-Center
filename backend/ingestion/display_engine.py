"""
DISPLAY PREPARATION ENGINE v8.2

Prepares products for display by:
- Determining display role (hero, cornerstone, specialist, entry)
- Organizing media assets by purpose
- Selecting hero images at the right resolution
- Assigning display tier levels
- Computing display prominence

This engine decides HOW products should be visually presented.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from backend.ingestion.data_models import (
    DisplayRole, PricingTier, MediaAsset, DisplayProperties,
    IngestionProductDraft, DataSourceConfidence
)
from backend.ingestion.visual_validator import get_visual_validator

logger = logging.getLogger("DisplayPreparationEngine")


@dataclass
class DisplayGuideline:
    """Guidelines for displaying a product"""
    role: DisplayRole
    tier_level: int  # 1-5, higher = more prominent
    should_highlight: bool
    suggested_color: Optional[str] = None
    description: str = ""


class DisplayPreparationEngine:
    """
    Master display strategy engine.

    Determines:
    - Visual presentation role (hero vs specialist vs entry)
    - Media asset selection and ordering
    - Display prominence in tier
    - Visual cues and highlights
    """

    def __init__(self):
        self.logger = logger

        # DISPLAY ROLE GUIDELINES
        self.role_guidelines = self._build_role_guidelines()

        # TIER-TO-DISPLAY mapping
        self.tier_display_levels = {
            PricingTier.ENTRY: 1,      # Bottom of display
            PricingTier.MID: 2,        # Middle
            PricingTier.PRO: 4,        # High
            PricingTier.FLAGSHIP: 5,   # Top priority
        }

    # ============================================================================
    # DISPLAY ROLE DETERMINATION
    # ============================================================================

    def _build_role_guidelines(self) -> Dict[DisplayRole, DisplayGuideline]:
        """Define display role guidelines"""
        return {
            DisplayRole.HERO: DisplayGuideline(
                role=DisplayRole.HERO,
                tier_level=5,
                should_highlight=True,
                suggested_color="bg-gradient-to-r from-blue-500 to-purple-600",
                description="Flagship/signature product of the brand",
            ),
            DisplayRole.CORNERSTONE: DisplayGuideline(
                role=DisplayRole.CORNERSTONE,
                tier_level=4,
                should_highlight=False,
                suggested_color="bg-blue-400",
                description="Key product in the tier",
            ),
            DisplayRole.SPECIALIST: DisplayGuideline(
                role=DisplayRole.SPECIALIST,
                tier_level=3,
                should_highlight=False,
                suggested_color="bg-green-400",
                description="Niche or specialized product",
            ),
            DisplayRole.ENTRY: DisplayGuideline(
                role=DisplayRole.ENTRY,
                tier_level=1,
                should_highlight=False,
                suggested_color="bg-gray-300",
                description="Gateway product for new users",
            ),
            DisplayRole.HIDDEN: DisplayGuideline(
                role=DisplayRole.HIDDEN,
                tier_level=0,
                should_highlight=False,
                suggested_color="bg-gray-200",
                description="Internal/archived - not displayed",
            ),
        }

    def determine_display_role(
        self,
        product_name: str,
        pricing_tier: PricingTier,
        data_completeness: float,
        is_official_spec: bool,
        is_flagship_product: bool,
    ) -> DisplayRole:
        """
        Determine display role based on product characteristics.

        Returns: DisplayRole
        """
        # FLAGSHIP PRODUCTS: Hero role
        if is_flagship_product or pricing_tier == PricingTier.FLAGSHIP:
            if data_completeness > 0.8 and is_official_spec:
                return DisplayRole.HERO

        # PROFESSIONAL TIER: Cornerstone or specialist
        if pricing_tier == PricingTier.PRO:
            if data_completeness > 0.7:
                return DisplayRole.CORNERSTONE
            else:
                return DisplayRole.SPECIALIST

        # MID TIER: Cornerstone or specialist
        if pricing_tier == PricingTier.MID:
            if data_completeness > 0.75:
                return DisplayRole.CORNERSTONE
            else:
                return DisplayRole.SPECIALIST

        # ENTRY TIER: Entry or specialist
        if pricing_tier == PricingTier.ENTRY:
            return DisplayRole.ENTRY

        # LEGACY: Hidden
        if pricing_tier == PricingTier.LEGACY:
            return DisplayRole.HIDDEN

        # Default: Specialist
        return DisplayRole.SPECIALIST

    # ============================================================================
    # VISUAL ENHANCEMENT TOOLS (v7.5)
    # ============================================================================
    def _enhance_image_presentation(self, image_url: str) -> str:
        """
        [FUTURE CAPABILITY]
        Refine and crop image, apply proper background and lighting.

        Planned Implementation:
        1. Smart Crop: Center subject using object detection.
        2. Background Removal: Use 'rembg' or Gemini Vision to isolate product.
        3. Studio Lighting: Generative fill to add professional lighting and shadows.
        """
        # Currently a pass-through until GenAI image editing is fully integrated
        return image_url

    # ============================================================================
    # MEDIA ASSET ORGANIZATION
    # ============================================================================

    def organize_media_assets(
        self,
        media_list: List[MediaAsset],
        hero_image_url: Optional[str] = None,
        display_role: DisplayRole = DisplayRole.SPECIALIST,
    ) -> Tuple[List[MediaAsset], Optional[str]]:
        """
        Organize and prioritize media assets for display.

        Returns: (sorted_media_list, selected_hero_image_url)
        """
        if not media_list:
            return [], hero_image_url

        # Categorize assets by type
        hero_candidates = []
        thumbnail_candidates = []
        gallery_assets = []
        spec_sheets = []

        for asset in media_list:
            if asset.display_purpose == "hero":
                hero_candidates.append(asset)
            elif asset.display_purpose == "thumbnail":
                thumbnail_candidates.append(asset)
            elif asset.display_purpose == "gallery":
                gallery_assets.append(asset)
            elif asset.display_purpose == "specification":
                spec_sheets.append(asset)

        # Select hero image if not provided
        if not hero_image_url and hero_candidates:
            # Prefer official sources
            official_heroes = [a for a in hero_candidates
                               if a.source == DataSourceConfidence.OFFICIAL]
            if official_heroes:
                hero_image_url = official_heroes[0].url
            else:
                hero_image_url = hero_candidates[0].url

        # Sort all assets by priority
        all_assets = hero_candidates + thumbnail_candidates + gallery_assets + spec_sheets
        sorted_assets = sorted(all_assets, key=lambda a: (-a.priority, a.type))

        return sorted_assets, hero_image_url

    def select_hero_image(
        self,
        media_assets: List[MediaAsset],
        display_role: DisplayRole,
        preferred_resolution: Tuple[int, int] = (2000, 1500),
    ) -> Optional[str]:
        """
        Select the best hero image based on role and specifications.

        Prefers:
        1. Official source
        2. Correct resolution
        3. Explicitly marked as hero
        """
        # Filter for image-type assets
        images = [a for a in media_assets if a.type == "image"]

        if not images:
            return None

        # Score each image
        candidates = []
        for img in images:
            score = 0

            # Prefer official
            if img.source == DataSourceConfidence.OFFICIAL:
                score += 50

            # Prefer correct resolution
            if img.resolution and preferred_resolution:
                w, h = preferred_resolution
                if f"{w}x{h}" in img.resolution:
                    score += 30

            # Prefer explicitly marked hero
            if img.display_purpose == "hero":
                score += 40

            # Prefer high priority
            score += img.priority

            candidates.append((img, score))

        # Return best candidate
        if candidates:
            best_image = max(candidates, key=lambda x: x[1])
            return best_image[0].url

        return None

    # ============================================================================
    # DISPLAY TIER LEVELS
    # ============================================================================

    def determine_display_tier_level(
        self,
        pricing_tier: PricingTier,
        data_completeness: float,
        display_role: DisplayRole,
    ) -> int:
        """
        Determine display tier level (1-5) for UI prominence.

        Higher number = more prominent display position
        """
        base_level = self.tier_display_levels.get(pricing_tier, 3)

        # Adjust based on data completeness
        if data_completeness > 0.9:
            base_level += 1
        elif data_completeness < 0.5:
            base_level -= 1

        # Adjust based on display role
        role_adjustments = {
            DisplayRole.HERO: 2,
            DisplayRole.CORNERSTONE: 1,
            DisplayRole.SPECIALIST: 0,
            DisplayRole.ENTRY: -1,
            DisplayRole.HIDDEN: -5,
        }
        base_level += role_adjustments.get(display_role, 0)

        # Clamp to 1-5 range
        return max(1, min(5, base_level))

    # ============================================================================
    # COLOR & VISUAL HINTS
    # ============================================================================

    def determine_color_scheme(
        self,
        brand: str,
        pricing_tier: PricingTier,
        display_role: DisplayRole,
    ) -> Optional[str]:
        """
        Determine visual color scheme for product.

        Considers brand colors and tier.
        """
        # Brand color overrides (in production, load from database)
        brand_colors = {
            "Nord": "#0084FF",          # Nord blue
            "Moog": "#FF6B6B",          # Moog red
            "Roland": "#00A4EF",        # Roland cyan
            "Elektron": "#FF1744",      # Elektron red
            "Yamaha": "#1F4A8B",        # Yamaha navy
            "Korg": "#333333",          # Korg dark
        }

        # Use brand color if available
        if brand in brand_colors:
            return brand_colors[brand]

        # Fallback to tier color
        role_guideline = self.role_guidelines.get(display_role)
        if role_guideline:
            return role_guideline.suggested_color

        return None

    # ============================================================================
    # DISPLAY TEXT GENERATION
    # ============================================================================

    def generate_display_description(
        self,
        product_name: str,
        description_short: Optional[str],
        description_long: Optional[str],
        feature_list: List[str],
        max_length: int = 150,
    ) -> str:
        """
        Generate appropriate display description based on available data.

        Prefers concise, marketing-friendly text.
        """
        # Preference order:
        # 1. Official short description
        if description_short and len(description_short) <= max_length:
            return description_short.strip()

        # 2. First paragraph of long description
        if description_long:
            first_para = description_long.split('\n')[0]
            if len(first_para) <= max_length:
                return first_para.strip()

        # 3. Generate from features
        if feature_list:
            features_text = "; ".join(feature_list[:3])
            if len(features_text) <= max_length:
                return features_text

        # 4. Generic fallback
        return f"{product_name} - Professional audio equipment"

    # ============================================================================
    # DISPLAY PROPERTIES ASSEMBLY
    # ============================================================================

    def build_display_properties(
        self,
        product_name: str,
        pricing_tier: PricingTier,
        brand: str,
        data_completeness: float,
        media_assets: List[MediaAsset],
        is_official: bool = False,
        is_flagship: bool = False,
    ) -> DisplayProperties:
        """
        Build complete display properties for a product.

        Orchestrates all display determination logic.
        """
        # Determine display role
        display_role = self.determine_display_role(
            product_name=product_name,
            pricing_tier=pricing_tier,
            data_completeness=data_completeness,
            is_official_spec=is_official,
            is_flagship_product=is_flagship,
        )

        # Organize media
        sorted_media, hero_image = self.organize_media_assets(
            media_assets,
            display_role=display_role,
        )

        # Determine tier level
        tier_level = self.determine_display_tier_level(
            pricing_tier,
            data_completeness,
            display_role,
        )

        # Determine color
        color_hint = self.determine_color_scheme(
            brand, pricing_tier, display_role)

        # Determine highlight status
        # Handle both Enum and string values due to Pydantic use_enum_values config
        display_role_str = display_role if isinstance(
            display_role, str) else display_role.value
        should_highlight = (
            display_role_str in [DisplayRole.HERO.value, DisplayRole.CORNERSTONE.value] and
            data_completeness > 0.75
        )

        # Visual Validation
        validator = get_visual_validator()
        _, issues = validator.validate_display_readiness(
            pricing_tier=pricing_tier,
            display_role=display_role,
            media_assets=sorted_media,
            hero_image_url=hero_image
        )

        if issues:
            self.logger.warning(
                f"Visual validation issues for {product_name}: {issues}")

        return DisplayProperties(
            display_role=display_role,
            hero_image=hero_image,
            thumbnail_image=self._extract_thumbnail(sorted_media),
            should_highlight=should_highlight,
            display_tier_level=tier_level,
            color_hint=color_hint,
            media_assets=sorted_media,
            visual_issues=issues
        )

    def _extract_thumbnail(self, media_assets: List[MediaAsset]) -> Optional[str]:
        """Extract thumbnail from media assets"""
        for asset in media_assets:
            if asset.display_purpose == "thumbnail":
                return asset.url
            if asset.display_purpose == "hero" and asset.resolution:
                # Can use hero as thumbnail if needed
                return asset.url

        # Fallback to any image
        images = [a for a in media_assets if a.type == "image"]
        if images:
            return images[0].url

        return None

    # ============================================================================
    # REPORTING & VISUALIZATION
    # ============================================================================

    def generate_display_report(self, products: List[IngestionProductDraft]) -> Dict:
        """Generate report on display properties across products"""
        by_role = {}
        by_tier_level = {}

        for product in products:
            role = product.display.display_role
            tier_level = product.display.display_tier_level

            if role not in by_role:
                by_role[role] = 0
            by_role[role] += 1

            if tier_level not in by_tier_level:
                by_tier_level[tier_level] = 0
            by_tier_level[tier_level] += 1

        return {
            'total_products': len(products),
            'by_display_role': {role.value: count for role, count in by_role.items()},
            'by_tier_level': by_tier_level,
            'has_hero_image_count': sum(1 for p in products if p.display.hero_image),
            'highlighted_count': sum(1 for p in products if p.display.should_highlight),
        }

    def export_display_guidelines(self) -> Dict:
        """Export display guidelines for frontend"""
        return {
            role.value: {
                'tier_level': guideline.tier_level,
                'should_highlight': guideline.should_highlight,
                'color': guideline.suggested_color,
                'description': guideline.description,
            }
            for role, guideline in self.role_guidelines.items()
        }


# Global singleton
_display_engine = None


def get_display_engine() -> DisplayPreparationEngine:
    """Get or create the global display engine"""
    global _display_engine
    if _display_engine is None:
        _display_engine = DisplayPreparationEngine()
        logger.info("✅ Display Preparation Engine initialized")
    return _display_engine
