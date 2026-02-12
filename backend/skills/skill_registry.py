"""
Skill Registry & Execution Engine

Central registry for all available skills.
Manages skill lifecycle, verification gates, and execution flow.
"""

import logging
from typing import Dict, Any, Tuple, Optional
from .ingestion_skills import (
    HarvestSkill, EnrichSkill, TierSkill, PrepareSkill, ValidateSkill, ApproveSkill
)
from .mcp_tool_skill import MCPToolSkill
from .catalog_skills import CatalogValidateSkill, CatalogResolveSkill


class SkillRegistry:
    """
    Central registry for all agent skills.

    Usage:
        registry = SkillRegistry(orchestrator)
        success, output = registry.execute_skill('harvest', context)
    """

    def __init__(self, orchestrator=None):
        self.logger = logging.getLogger(__name__)
        self.orchestrator = orchestrator
        self.skills = {}
        self._register_default_skills()

    def _register_default_skills(self):
        """Register all built-in ingestion skills."""
        self.register('harvest', HarvestSkill(self.orchestrator))
        self.register('enrich', EnrichSkill(self.orchestrator))
        self.register('tier', TierSkill(self.orchestrator))
        self.register('prepare', PrepareSkill(self.orchestrator))
        self.register('validate', ValidateSkill(self.orchestrator))
        self.register('approve', ApproveSkill(self.orchestrator))
        # MCP bridge skill — routes to external MCP servers
        self.register('mcp_tool', MCPToolSkill(self.orchestrator))
        # Catalog validation & resolution skills
        self.register('catalog_validate',
                      CatalogValidateSkill(self.orchestrator))
        self.register('catalog_resolve',
                      CatalogResolveSkill(self.orchestrator))

    def register(self, name: str, skill):
        """Register a new skill."""
        if not hasattr(skill, 'execute'):
            raise ValueError(f"Skill must implement execute() method")
        self.skills[name.lower()] = skill
        self.logger.info(f"✓ Registered skill: {name}")

    def get_skill(self, name: str):
        """Get a registered skill by name."""
        skill = self.skills.get(name.lower())
        if not skill:
            raise KeyError(
                f"Skill not found: {name}. Available: {list(self.skills.keys())}")
        return skill

    def execute_skill(self, name: str, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """Execute a skill by name."""
        try:
            skill = self.get_skill(name)
            return skill.execute(context)
        except Exception as e:
            self.logger.error(f"Skill execution failed: {name} → {str(e)}")
            return False, str(e)

    def list_skills(self) -> Dict[str, str]:
        """List all registered skills."""
        return {name: skill.__class__.__name__ for name, skill in self.skills.items()}


class SkillPipeline:
    """
    Orchestrates 6-phase ingestion pipeline using skills.

    Execution flow:
    1. HARVEST - Extract raw product
    2. ENRICH - Add taxonomy + official data
    3. TIER - Calculate pricing tier
    4. PREPARE - Set display properties
    5. VALIDATE - Audit product
    6. APPROVE - Final decision

    Each phase is a skill with verification gates.
    """

    def __init__(self, registry: SkillRegistry):
        self.logger = logging.getLogger(__name__)
        self.registry = registry

    def execute_full_pipeline(self, raw_product: Dict[str, Any], brand: str) -> Dict[str, Any]:
        """
        Execute complete 6-phase pipeline for one product.

        Args:
            raw_product: Raw product data from source
            brand: Brand name

        Returns:
            Pipeline result with draft, status, and errors
        """
        result = {
            'product_name': raw_product.get('product_name', 'Unknown'),
            'brand': brand,
            'status': 'FAILED',
            'draft': None,
            'errors': [],
            'phase_results': {}
        }

        # Phase 1: HARVEST
        self.logger.info(f"🔄 Phase 1/6: HARVEST {result['product_name']}")
        success, draft = self.registry.execute_skill('harvest', {
            'raw_product': raw_product,
            'brand': brand
        })
        result['phase_results']['harvest'] = success
        if not success:
            result['errors'].append(f"Harvest failed: {draft}")
            self.logger.error(f"❌ HARVEST failed: {draft}")
            return result
        result['draft'] = draft

        # Phase 2: ENRICH
        self.logger.info(f"🔄 Phase 2/6: ENRICH")
        success, enriched = self.registry.execute_skill(
            'enrich', {'draft': draft})
        result['phase_results']['enrich'] = success
        if not success:
            result['errors'].append(f"Enrich failed: {enriched}")
            self.logger.error(f"❌ ENRICH failed: {enriched}")
            return result
        result['draft'] = enriched

        # Phase 3: TIER
        self.logger.info(f"🔄 Phase 3/6: TIER")
        success, tiered = self.registry.execute_skill(
            'tier', {'draft': enriched})
        result['phase_results']['tier'] = success
        if not success:
            result['errors'].append(f"Tier failed: {tiered}")
            self.logger.error(f"❌ TIER failed: {tiered}")
            return result
        result['draft'] = tiered

        # Phase 4: PREPARE
        self.logger.info(f"🔄 Phase 4/6: PREPARE")
        success, prepared = self.registry.execute_skill(
            'prepare', {'draft': tiered})
        result['phase_results']['prepare'] = success
        if not success:
            result['errors'].append(f"Prepare failed: {prepared}")
            self.logger.error(f"❌ PREPARE failed: {prepared}")
            return result
        result['draft'] = prepared

        # Phase 5: VALIDATE
        self.logger.info(f"🔄 Phase 5/6: VALIDATE")
        success, validation_result = self.registry.execute_skill(
            'validate', {'draft': prepared})
        result['phase_results']['validate'] = success
        if not success:
            result['errors'].append(f"Validate failed: {validation_result}")
            self.logger.error(f"❌ VALIDATE failed: {validation_result}")
            return result

        is_valid = validation_result.get('is_valid', False)
        validation_errors = validation_result.get('errors', [])

        # Phase 6: APPROVE
        self.logger.info(f"🔄 Phase 6/6: APPROVE")
        success, approval = self.registry.execute_skill('approve', {
            'draft': prepared,
            'is_valid': is_valid,
            'errors': validation_errors
        })
        result['phase_results']['approve'] = success
        if not success:
            result['errors'].append(f"Approve failed: {approval}")
            self.logger.error(f"❌ APPROVE failed: {approval}")
            return result

        # Update result with final status
        final_draft = approval.get('draft')
        result['draft'] = final_draft
        result['status'] = approval.get('status', 'UNKNOWN')
        result['errors'] = validation_errors

        if result['status'] == 'APPROVED':
            self.logger.info(f"✅ APPROVED: {result['product_name']}")
        else:
            self.logger.warning(f"⚠️ REJECTED: {result['product_name']}")

        return result

    def execute_single_phase(self, phase_name: str, context: Dict[str, Any]) -> Tuple[bool, Any]:
        """Execute a single pipeline phase."""
        return self.registry.execute_skill(phase_name, context)
