"""
Ingestion Pipeline Skills

Skills for the 6-phase ingestion pipeline:
- HarvestSkill: Extract products from sources
- EnrichSkill: Add official data
- TaxonomySkill: Classify products
- PricingSkill: Calculate pricing
- DisplaySkill: Prepare display properties
- ValidateSkill: Audit products

Each skill:
1. Wraps a pipeline operation
2. Includes verification gates
3. Returns (success, output) tuple
4. Logs all actions for debugging
"""

import json
from typing import Dict, Any, Tuple, List
from .base_skill import BaseSkill
from backend.ingestion.data_models import IngestionProductDraft, IngestionStatus


class HarvestSkill(BaseSkill):
    """
    PHASE 1: Harvests raw product data and normalizes to draft.

    Uses CommercialScout agent to validate golden list membership.
    Returns normalized IngestionProductDraft.
    """

    def __init__(self, orchestrator=None):
        super().__init__()
        self.orchestrator = orchestrator

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Harvest raw product to IngestionProductDraft.

        Required context:
        - raw_product: Dict with halilit_id, product_name, price_il
        - brand: Brand name

        Returns:
            (success: bool, draft: IngestionProductDraft or error_msg: str)
        """
        valid, error = self.validate_context(context, ['raw_product', 'brand'])
        if not valid:
            return False, error

        try:
            raw_product = context['raw_product']
            brand = context['brand']

            # Call orchestrator's harvest phase
            draft = self.orchestrator._phase_harvest(raw_product, brand)

            # Verify draft was created
            if not draft or not isinstance(draft, IngestionProductDraft):
                return False, "Harvest failed to produce valid draft"

            # Verify immutable fields
            if not draft.halilit_id or not draft.product_name or draft.price_il is None:
                return False, f"Draft missing immutable fields: id={draft.halilit_id}, name={draft.product_name}, price={draft.price_il}"

            self.log_execution(True, "HarvestSkill",
                               f"{draft.product_name} → Draft ready (Price: {draft.price_il} NIS)")

            return True, draft

        except Exception as e:
            error_msg = f"Harvest failed: {str(e)}"
            self.log_execution(False, "HarvestSkill", error_msg)
            return False, error_msg


class EnrichSkill(BaseSkill):
    """
    PHASE 2: Enriches with taxonomy and official data.

    Uses OfficialVerifier agent to add specs and images.
    Uses TaxonomyManager for classification.
    """

    def __init__(self, orchestrator=None):
        super().__init__()
        self.orchestrator = orchestrator

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Enrich draft with taxonomy and official data.

        Required context:
        - draft: IngestionProductDraft

        Returns:
            (success: bool, enriched_draft: IngestionProductDraft or error_msg: str)
        """
        valid, error = self.validate_context(context, ['draft'])
        if not valid:
            return False, error

        try:
            draft = context['draft']

            # Call orchestrator's enrich phase
            enriched = self.orchestrator._phase_enrich_taxonomy(draft)

            # Verify enrichment
            if not enriched or not isinstance(enriched, IngestionProductDraft):
                return False, "Enrich failed to produce valid draft"

            # Verify taxonomy was assigned
            if not enriched.taxonomy or enriched.taxonomy.canonical_category == "Other":
                return False, f"Enrich failed to classify: {enriched.product_name}"

            # Verify agent enrichment occurred
            if not enriched.official_specs and not enriched.official_images:
                self.logger.warning(
                    f"Enrich: No official data for {enriched.product_name}")

            self.log_execution(True, "EnrichSkill",
                               f"{enriched.product_name} → {enriched.taxonomy.canonical_category} / {enriched.taxonomy.canonical_subcategory}")

            return True, enriched

        except Exception as e:
            error_msg = f"Enrich failed: {str(e)}"
            self.log_execution(False, "EnrichSkill", error_msg)
            return False, error_msg


class TierSkill(BaseSkill):
    """
    PHASE 3: Calculate pricing tier and discount.

    Uses PricingEngine to assign tier level.
    """

    def __init__(self, orchestrator=None):
        super().__init__()
        self.orchestrator = orchestrator

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Assign pricing tier to draft.

        Required context:
        - draft: IngestionProductDraft

        Returns:
            (success: bool, tiered_draft: IngestionProductDraft or error_msg: str)
        """
        valid, error = self.validate_context(context, ['draft'])
        if not valid:
            return False, error

        try:
            draft = context['draft']

            # Call orchestrator's tier phase
            tiered = self.orchestrator._phase_tier_pricing(draft)

            # Verify tiering
            if not tiered or not tiered.pricing.tier:
                return False, "Tier assignment failed"

            self.log_execution(True, "TierSkill",
                               f"{tiered.product_name} → {tiered.pricing.tier.value} ({tiered.pricing.price_il} NIS)")

            return True, tiered

        except Exception as e:
            error_msg = f"Tier assignment failed: {str(e)}"
            self.log_execution(False, "TierSkill", error_msg)
            return False, error_msg


class PrepareSkill(BaseSkill):
    """
    PHASE 4: Prepare for display.

    Uses DisplayEngine to set visual properties.
    """

    def __init__(self, orchestrator=None):
        super().__init__()
        self.orchestrator = orchestrator

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Prepare draft for display.

        Required context:
        - draft: IngestionProductDraft

        Returns:
            (success: bool, prepared_draft: IngestionProductDraft or error_msg: str)
        """
        valid, error = self.validate_context(context, ['draft'])
        if not valid:
            return False, error

        try:
            draft = context['draft']

            # Call orchestrator's prepare phase
            prepared = self.orchestrator._phase_prepare_display(draft)

            # Verify preparation
            if not prepared or not prepared.display:
                return False, "Display preparation failed"

            self.log_execution(True, "PrepareSkill",
                               f"{prepared.product_name} → Role: {prepared.display.display_role}")

            return True, prepared

        except Exception as e:
            error_msg = f"Display preparation failed: {str(e)}"
            self.log_execution(False, "PrepareSkill", error_msg)
            return False, error_msg


class ValidateSkill(BaseSkill):
    """
    PHASE 5: Validate and audit product.

    Uses ExternalValidator agent to perform final audit.
    Uses guardrails for compliance checks.
    """

    def __init__(self, orchestrator=None):
        super().__init__()
        self.orchestrator = orchestrator

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Validate draft against all rules.

        Required context:
        - draft: IngestionProductDraft

        Returns:
            (success: bool, (is_valid: bool, errors: List[str]))
        """
        valid, error = self.validate_context(context, ['draft'])
        if not valid:
            return False, error

        try:
            draft = context['draft']

            # Call orchestrator's validate phase
            is_valid, errors = self.orchestrator._phase_validate(draft)

            # Verify validation ran
            if is_valid and errors:
                self.logger.warning(
                    f"Valid but has warnings: {len(errors)} issues")

            result = {
                'is_valid': is_valid,
                'errors': errors,
                'status': 'APPROVED' if is_valid else 'REJECTED',
                'product_name': draft.product_name,
                'halilit_id': draft.halilit_id
            }

            self.log_execution(True, "ValidateSkill",
                               f"{draft.product_name} → {'APPROVED' if is_valid else 'REJECTED'}")

            return True, result

        except Exception as e:
            error_msg = f"Validation failed: {str(e)}"
            self.log_execution(False, "ValidateSkill", error_msg)
            return False, error_msg


class ApproveSkill(BaseSkill):
    """
    PHASE 6: Final approval and recording.

    Writes approved product to output, rejects failed products.
    """

    def __init__(self, orchestrator=None):
        super().__init__()
        self.orchestrator = orchestrator

    def execute(self, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Approve or reject product.

        Required context:
        - draft: IngestionProductDraft
        - is_valid: bool (from ValidateSkill)
        - errors: List[str] (from ValidateSkill)

        Returns:
            (success: bool, approval_record: Dict)
        """
        valid, error = self.validate_context(
            context, ['draft', 'is_valid', 'errors'])
        if not valid:
            return False, error

        try:
            draft = context['draft']
            is_valid = context['is_valid']
            errors = context['errors']

            # Update draft status
            if is_valid:
                draft.validation_status = IngestionStatus.APPROVED
                status = 'APPROVED'
            else:
                draft.validation_status = IngestionStatus.REJECTED
                draft.validation_errors.extend(errors)
                status = 'REJECTED'

            # Create approval record
            record = {
                'halilit_id': draft.halilit_id,
                'product_name': draft.product_name,
                'brand': draft.brand,
                'status': status,
                'errors': errors,
                'validation_status': draft.validation_status.value if draft.validation_status else 'unknown'
            }

            self.log_execution(True, "ApproveSkill",
                               f"{draft.product_name} → {status}")

            return True, {
                'draft': draft,
                'record': record,
                'status': status
            }

        except Exception as e:
            error_msg = f"Approval failed: {str(e)}"
            self.log_execution(False, "ApproveSkill", error_msg)
            return False, error_msg
