"""
UNIFIED INGESTION ORCHESTRATOR v6.0

Master orchestrator for the complete scraping & ingestion pipeline:

Phase 1: HARVEST - Scrape raw data
Phase 2: ENRICH - Apply taxonomy classification
Phase 3: TIER - Apply pricing strategy
Phase 4: PREPARE - Prepare for display
Phase 5: VALIDATE - Check compliance
Phase 6: APPROVE - Final decision

This is the conductor that orchestrates all the ingestion engines.
"""

import logging
import uuid
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

from backend.ingestion.data_models import (
    IngestionProductDraft, SourceProvenance, TaxonomyMapping,
    PricingData, DisplayProperties, IngestionBatch, IngestionReport,
    IngestionStatus, DataSourceConfidence, compute_data_completeness,
    validate_pricing_consistency, ProductDraft, ProductSpecifications
)
from backend.ingestion.taxonomy_manager import get_taxonomy_manager
from backend.ingestion.pricing_engine import get_pricing_engine
from backend.ingestion.display_engine import get_display_engine

logger = logging.getLogger("IngestionOrchestrator")


class IngestionOrchestrator:
    """
    Master orchestrator for the complete ingestion pipeline.

    Coordinates:
    1. Taxonomy classification
    2. Pricing strategy
    3. Display preparation
    4. Validation
    5. Approval workflow
    """

    def __init__(self):
        self.logger = logger
        self.taxonomy_manager = get_taxonomy_manager()
        self.pricing_engine = get_pricing_engine()
        self.display_engine = get_display_engine()

    # ============================================================================
    # MAIN ORCHESTRATION WORKFLOW
    # ============================================================================

    def ingest_batch(
        self,
        brand: str,
        raw_products: List[Dict[str, Any]],
        force_refresh: bool = False,
    ) -> IngestionReport:
        """
        Main entry point: Ingest a batch of raw products.

        Orchestrates the complete 6-phase pipeline:
        1. Harvest → 2. Enrich → 3. Tier → 4. Prepare → 5. Validate → 6. Approve

        Args:
            brand: Brand name
            raw_products: List of raw product dicts from scraper
            force_refresh: Skip cache if available

        Returns:
            IngestionReport with approved products
        """
        batch_id = str(uuid.uuid4())[:8]
        start_time = datetime.utcnow()

        self.logger.info(f"🚀 Starting ingestion batch {batch_id} for {brand}")
        self.logger.info(f"   Raw products: {len(raw_products)}")

        # PHASE 1: HARVEST - Normalize raw data
        drafted_products = []
        for raw_product in raw_products:
            try:
                draft = self._phase_harvest(raw_product, brand)
                drafted_products.append(draft)
            except Exception as e:
                self.logger.warning(
                    f"   ❌ Failed to harvest {raw_product.get('name', 'unknown')}: {e}")

        self.logger.info(
            f"   ✓ Phase 1 (HARVEST): {len(drafted_products)} products drafted")

        # PHASE 2: ENRICH - Apply taxonomy
        enriched_products = []
        for draft in drafted_products:
            try:
                enriched = self._phase_enrich_taxonomy(draft)
                enriched_products.append(enriched)
            except Exception as e:
                self.logger.warning(
                    f"   ❌ Taxonomy enrichment failed for {draft.product_name}: {e}")

        self.logger.info(
            f"   ✓ Phase 2 (ENRICH): {len(enriched_products)} products taxonomy-enriched")

        # PHASE 3: TIER - Apply pricing strategy
        tiered_products = []
        for product in enriched_products:
            try:
                tiered = self._phase_tier_pricing(product)
                tiered_products.append(tiered)
            except Exception as e:
                self.logger.warning(
                    f"   ❌ Pricing tier failed for {product.product_name}: {e}")

        self.logger.info(
            f"   ✓ Phase 3 (TIER): {len(tiered_products)} products priced and tiered")

        # PHASE 4: PREPARE - Prepare for display
        prepared_products = []
        for product in tiered_products:
            try:
                prepared = self._phase_prepare_display(product)
                prepared_products.append(prepared)
            except Exception as e:
                self.logger.warning(
                    f"   ❌ Display preparation failed for {product.product_name}: {e}")

        self.logger.info(
            f"   ✓ Phase 4 (PREPARE): {len(prepared_products)} products display-prepared")

        # PHASE 5: VALIDATE - Check compliance
        validated_products = []
        validation_failures = []
        for product in prepared_products:
            try:
                is_valid, errors = self._phase_validate(product)
                product.validation_status = IngestionStatus.VALIDATED if is_valid else IngestionStatus.REJECTED
                product.validation_errors = errors

                if is_valid:
                    validated_products.append(product)
                else:
                    validation_failures.append((product, errors))
            except Exception as e:
                self.logger.warning(
                    f"   ❌ Validation failed for {product.product_name}: {e}")
                validation_failures.append((product, [str(e)]))

        self.logger.info(f"   ✓ Phase 5 (VALIDATE): {len(validated_products)} products validated, "
                         f"{len(validation_failures)} rejected")

        # PHASE 6: APPROVE - Final approval
        approved_products = []
        for product in validated_products:
            product.validation_status = IngestionStatus.APPROVED
            approved_products.append(product)

        self.logger.info(
            f"   ✓ Phase 6 (APPROVE): {len(approved_products)} products approved")

        # Generate report
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        report = IngestionReport(
            batch_id=batch_id,
            brand=brand,
            total_products_processed=len(raw_products),
            approved_count=len(approved_products),
            rejected_count=len(validation_failures),
            approved_products=approved_products,
            rejected_products=validation_failures,
            execution_time_seconds=execution_time,
            recommendations=self._generate_recommendations(
                approved_products, validation_failures, len(raw_products)
            ),
        )

        self.logger.info(f"   ✅ Batch {batch_id} complete: "
                         f"{report.approved_count} approved, {report.rejected_count} rejected")

        return report

    # ============================================================================
    # PHASE IMPLEMENTATIONS: The 6-Phase Pipeline
    # ============================================================================

    def _phase_harvest(self, raw_product: Dict[str, Any], brand: str) -> IngestionProductDraft:
        """
        PHASE 1: HARVEST (v6.0 STRICT)

        Normalize raw scraped data into IngestionProductDraft structure.
        Enforces "The Golden List" rules:
        - Halilit ID, Name, Price are IMMUTABLE here.
        - Other fields are left empty for later agents.
        """
        # Generate or extract ID
        halilit_id = (
            raw_product.get('halilit_id') or
            raw_product.get('id') or
            raw_product.get('sku') or
            f"{brand}_{uuid.uuid4().hex[:8]}"
        )

        # Extract name variations
        product_name = (
            raw_product.get('product_name') or
            raw_product.get('name') or
            raw_product.get('title') or
            "Unknown Product"
        )

        # Extract prices (COMMERCIAL SOURCE OF TRUTH)
        price_il = float(raw_product.get('price_il')
                         or raw_product.get('price') or 0)
        price_eilat = float(raw_product.get('price_eilat') or 0)

        # Link
        halilit_url = raw_product.get('source_url') or raw_product.get(
            'url') or "https://halilit.com"

        # Extract content (If present in source - treat as "Official" seed)
        desc_short = raw_product.get('description_short')
        desc_full = raw_product.get(
            'description_full') or raw_product.get('description')

        # Extract images (If present - treat as "Official" seed)
        official_images = []
        raw_hero = raw_product.get('image_hero')
        if raw_hero:
            url = raw_hero.get('url') if isinstance(
                raw_hero, dict) else raw_hero
            if url:
                from backend.ingestion.data_models import MediaAsset  # Ensure import
                official_images.append(MediaAsset(
                    type="image",
                    url=url,
                    display_purpose="hero",
                    source=DataSourceConfidence.OFFICIAL,  # Assume file data is verified
                    priority=100
                ))

        # Parse gallery
        raw_gallery = raw_product.get('image_gallery') or []
        if isinstance(raw_gallery, list):
            for img in raw_gallery:
                url = img.get('url') if isinstance(img, dict) else img
                if url:
                    from backend.ingestion.data_models import MediaAsset
                    official_images.append(MediaAsset(
                        type="image",
                        url=url,
                        display_purpose="gallery",
                        source=DataSourceConfidence.OFFICIAL,
                        priority=50
                    ))

        # Extract official specs if present (from OfficialVerifier)
        official_specs = raw_product.get('official_specs') or {}
        if official_specs:
            self.logger.info(
                f"   📘 Found official specs for {product_name}: {list(official_specs.keys())}")
        else:
            # Debug why it is missing
            if 'Moog' in brand and product_name.startswith('סינתיסייזר Moog Mavis'):
                self.logger.warning(
                    f"   ⚠️ MISSING official specs for {product_name}. Keys in raw: {list(raw_product.keys())}")

        # Create draft with Strict Commercial Data + Seed Content
        draft = IngestionProductDraft(
            # Commercial
            halilit_id=halilit_id,
            product_name=product_name,
            brand=brand,
            price_il=price_il,
            price_eilat=price_eilat,
            halilit_url=halilit_url,

            # Content Seeding (Populate Official containers if data exists)
            official_specs=official_specs,
            official_description=desc_full,
            description_long=desc_full,  # Legacy fallback
            description_short=desc_short,
            official_images=official_images,

            # Legacy/Computed Containers (Initialized empty)
            taxonomy=TaxonomyMapping(
                canonical_category="Other",
                canonical_subcategory="Uncategorized",
            ),
            pricing=PricingData(
                price_il=price_il,
                price_eilat=price_eilat,
            ),
            display=DisplayProperties(),
            specifications=ProductSpecifications(
                specs_dict={},
                specs_source=DataSourceConfidence.COMMERCIAL
            ),
            # Source Tracking
            primary_source=SourceProvenance(
                source_name="Halilit",
                source_url=halilit_url,
                confidence=DataSourceConfidence.COMMERCIAL,
                extraction_method="web_scraper",
                extraction_notes=f"Scraped from {brand} catalog"
            ),
            status=IngestionStatus.HARVESTED,
            pipeline_phase="harvest"
        )

        self.logger.debug(
            f"   Harvested: {product_name} (ID: {halilit_id}, Price: {price_il} NIS)")
        return draft

    def _phase_enrich_taxonomy(self, draft: IngestionProductDraft) -> IngestionProductDraft:
        """
        PHASE 2: ENRICH - Apply Taxonomy Classification

        Uses TaxonomyManager to classify product into universal taxonomy.
        Updates taxonomy fields with confidence scores.
        """
        # Classify into taxonomy
        category, subcategory, confidence = self.taxonomy_manager.classify_product(
            product_name=draft.product_name,
            brand=draft.brand,
            description=draft.description_short or "",
            specifications=draft.specifications.specs_dict,
        )

        draft.taxonomy = TaxonomyMapping(
            canonical_category=category,
            canonical_subcategory=subcategory,
        )

        # Update validation status
        draft.validation_status = IngestionStatus.ENRICHED

        self.logger.debug(f"   Enriched: {draft.product_name} → {category} > {subcategory} "
                          f"(conf={confidence:.2f})")

        return draft

    def _phase_tier_pricing(self, draft: IngestionProductDraft) -> IngestionProductDraft:
        """
        PHASE 3: TIER - Apply Pricing Strategy

        Uses PricingStrategyEngine to:
        - Determine pricing tier
        - Validate prices
        - Calculate discounts
        - Suggest corrections
        """
        # Determine tier from price
        tier = self.pricing_engine.determine_tier_by_price(
            draft.pricing.price_il)
        draft.pricing.tier = tier

        # Compute Eilat discount
        discount = 0.0
        if draft.pricing.price_il > 0:
            discount = ((draft.pricing.price_il - draft.pricing.price_eilat) /
                        draft.pricing.price_il * 100)
            draft.pricing.eilat_discount_percent = discount

        # Validate pricing
        is_valid, errors = self.pricing_engine.validate_pricing(draft.pricing)
        if not is_valid:
            for error in errors:
                if error.startswith("❌"):
                    draft.validation_errors.append(f"Pricing: {error}")

        # Suggest tier
        suggested_tier = self.pricing_engine.suggest_tier(
            draft.pricing.price_il,
            draft.taxonomy.canonical_category,
        )
        draft.pricing.suggested_tier = suggested_tier

        draft.validation_status = IngestionStatus.ENRICHED

        self.logger.debug(f"   Tiered: {draft.product_name} → {tier.value} "
                          f"({draft.pricing.price_il} NIS, discount={discount:.1f}%)")

        return draft

    def _phase_prepare_display(self, draft: IngestionProductDraft) -> IngestionProductDraft:
        """
        PHASE 4: PREPARE - Prepare for Display

        Uses DisplayPreparationEngine to:
        - Determine display role
        - Organize media assets
        - Set display tier level
        - Assign visual properties
        """
        # Build complete display properties
        display_props = self.display_engine.build_display_properties(
            product_name=draft.product_name,
            pricing_tier=draft.pricing.tier,
            brand=draft.brand,
            data_completeness=compute_data_completeness(draft),
            media_assets=draft.display.media_assets,
            is_official=(draft.primary_source.confidence ==
                         DataSourceConfidence.OFFICIAL),
            is_flagship=("flagship" in draft.product_name.lower()),
        )

        draft.display = display_props
        draft.data_completeness = compute_data_completeness(draft)
        draft.quality_score = draft.data_completeness  # Simplified for now

        self.logger.debug(f"   Prepared: {draft.product_name} → "
                          f"role={display_props.display_role if isinstance(display_props.display_role, str) else display_props.display_role.value}, "
                          f"tier_level={display_props.display_tier_level}, "
                          f"completeness={draft.data_completeness:.1%}")

        return draft

    def _phase_validate(self, draft: IngestionProductDraft) -> Tuple[bool, List[str]]:
        """
        PHASE 5: VALIDATE - Compliance Check

        Validates product against all rules:
        - Required fields present
        - Data completeness threshold
        - Pricing rules
        - Taxonomy validity
        """
        errors = []

        # Check required fields
        if not draft.halilit_id:
            errors.append("❌ Missing required field: halilit_id")

        if not draft.product_name:
            errors.append("❌ Missing required field: product_name")

        # Check brand
        if not draft.brand:
            errors.append("❌ Missing required field: brand")

        # Check prices (Allow 0)
        if draft.pricing.price_il < 0:
            errors.append("❌ Invalid price_il (must be non-negative)")
        elif draft.pricing.price_il == 0:
            draft.validation_warnings.append("⚠ Price is 0 (TBD)")

        # Check taxonomy validity (warn but don't reject - user wants all products visible)
        if not self.taxonomy_manager.validate_category(
            draft.taxonomy.canonical_category,
            draft.taxonomy.canonical_subcategory,
        ):
            draft.validation_warnings.append(f"⚠ Category may not be standard: {draft.taxonomy.canonical_category} > "
                                             f"{draft.taxonomy.canonical_subcategory}")

        # Check data completeness threshold (relaxed to 10% - v6.0 focus on display)
        if draft.data_completeness < 0.1:
            draft.validation_warnings.append(
                f"⚠ Data completeness low ({draft.data_completeness:.0%})")

        # Check pricing consistency
        pricing_errors = validate_pricing_consistency(draft.pricing)
        errors.extend(pricing_errors)

        # Determine if valid (only critical errors = not valid)
        is_valid = len([e for e in errors if e.startswith("❌")]) == 0

        # Prepend status to errors
        errors = draft.validation_errors + errors

        self.logger.debug(f"   Validated: {draft.product_name} → "
                          f"valid={is_valid}, errors={len(errors)}")

        return is_valid, errors

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _generate_recommendations(
        self,
        approved: List[IngestionProductDraft],
        rejected: List[Tuple],
        total: int,
    ) -> List[str]:
        """Generate recommendations based on ingestion results"""
        recommendations = []

        approval_rate = len(approved) / total * 100 if total > 0 else 0
        if approval_rate < 70:
            recommendations.append(
                f"⚠ Low approval rate ({approval_rate:.0f}%) - review data quality"
            )

        if rejected:
            common_errors = {}
            for product, errors in rejected:
                for error in errors[:1]:  # First error
                    common_errors[error] = common_errors.get(error, 0) + 1

            top_errors = sorted(common_errors.items(),
                                key=lambda x: x[1], reverse=True)[:3]
            for error, count in top_errors:
                recommendations.append(
                    f"Most common issue ({count} products): {error[:60]}")

        if approved:
            avg_completeness = sum(
                p.data_completeness for p in approved) / len(approved)
            if avg_completeness < 0.6:
                recommendations.append(
                    f"Consider enriching data (avg completeness: {avg_completeness:.0%})"
                )

        if not recommendations:
            recommendations.append(
                "✅ Pipeline running smoothly - no issues detected")

        return recommendations

    # ============================================================================
    # LEGACY COMPATIBILITY
    # ============================================================================

    def ingest_legacy_products(
        self,
        brand: str,
        legacy_products: List[ProductDraft],
    ) -> IngestionReport:
        """
        Ingest legacy ProductDraft format.

        Converts to new unified model and processes through pipeline.
        """
        raw_products = []
        for legacy_product in legacy_products:
            raw_products.append({
                'id': legacy_product.id,
                'name': legacy_product.name,
                'brand': legacy_product.brand,
                'price_il': legacy_product.price_il,
                'price_eilat': legacy_product.price_eilat,
                'image_url': legacy_product.image_url,
                'source_url': legacy_product.source_url,
                'official_match': legacy_product.official_match,
            })

        return self.ingest_batch(brand, raw_products)


# Global singleton
_orchestrator = None


def get_ingestion_orchestrator() -> IngestionOrchestrator:
    """Get or create the global orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = IngestionOrchestrator()
        logger.info("✅ Ingestion Orchestrator initialized")
    return _orchestrator
