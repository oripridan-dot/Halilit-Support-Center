"""
CopilotKit Integration Layer

Exposes Skills Framework to frontend through CopilotKit agent interface.
Provides real-time skill execution, logging, and result streaming.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
from backend.skills import SkillRegistry, SkillPipeline
from backend.ingestion.orchestrator import get_ingestion_orchestrator


class CopilotSkillExecutor:
    """
    Bridges Skills Framework with CopilotKit agent interface.

    Manages:
    - Skill registration and availability
    - Execution context building
    - Result streaming to frontend
    - Error handling and logging
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.orchestrator = get_ingestion_orchestrator()
        self.registry = SkillRegistry(self.orchestrator)
        self.pipeline = SkillPipeline(self.registry)
        self.execution_history = []

    def get_available_skills(self) -> List[Dict[str, Any]]:
        """
        Get list of available skills with descriptions.

        Returns:
            List of skill descriptions for CopilotKit agent
        """
        skills = self.registry.list_skills()

        descriptions = {
            'harvest': {
                'name': 'harvest',
                'description': 'Extract and normalize raw product data',
                'parameters': {
                    'raw_product': 'Raw product data dict with halilit_id, product_name, price_il',
                    'brand': 'Brand name'
                },
                'phase': 1
            },
            'enrich': {
                'name': 'enrich',
                'description': 'Add taxonomy classification and official data from agents',
                'parameters': {
                    'draft': 'IngestionProductDraft from harvest phase'
                },
                'phase': 2
            },
            'tier': {
                'name': 'tier',
                'description': 'Calculate pricing tier and discount',
                'parameters': {
                    'draft': 'IngestionProductDraft from enrich phase'
                },
                'phase': 3
            },
            'prepare': {
                'name': 'prepare',
                'description': 'Prepare display properties for frontend',
                'parameters': {
                    'draft': 'IngestionProductDraft from tier phase'
                },
                'phase': 4
            },
            'validate': {
                'name': 'validate',
                'description': 'Audit product against compliance rules',
                'parameters': {
                    'draft': 'IngestionProductDraft from prepare phase'
                },
                'phase': 5
            },
            'approve': {
                'name': 'approve',
                'description': 'Final approval and recording',
                'parameters': {
                    'draft': 'IngestionProductDraft from validate phase',
                    'is_valid': 'Validation result',
                    'errors': 'List of validation errors'
                },
                'phase': 6
            }
        }

        return [descriptions.get(name, {'name': name, 'phase': 'unknown'})
                for name in skills]

    async def execute_skill(self, skill_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single skill.

        Args:
            skill_name: Name of skill to execute
            context: Execution context/parameters

        Returns:
            Execution result with status and output
        """
        execution_id = f"{datetime.now().isoformat()}-{skill_name}"

        self.logger.info(f"[CopilotKit] Executing skill: {skill_name}")

        try:
            # Execute the skill
            success, output = self.registry.execute_skill(skill_name, context)

            result = {
                'execution_id': execution_id,
                'skill': skill_name,
                'success': success,
                'timestamp': datetime.now().isoformat(),
                'output': output if success else {'error': output},
                'status': 'COMPLETED' if success else 'FAILED'
            }

            # Record in history
            self.execution_history.append(result)

            self.logger.info(
                f"[CopilotKit] Skill {skill_name} → {result['status']}")
            return result

        except Exception as e:
            error_msg = str(e)
            self.logger.error(
                f"[CopilotKit] Skill {skill_name} crashed: {error_msg}")

            result = {
                'execution_id': execution_id,
                'skill': skill_name,
                'success': False,
                'timestamp': datetime.now().isoformat(),
                'output': {'error': error_msg},
                'status': 'CRASHED'
            }

            self.execution_history.append(result)
            return result

    async def execute_full_pipeline(self,
                                    raw_product: Dict[str, Any],
                                    brand: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute full 6-phase pipeline with real-time streaming.

        Yields progress updates for each phase completion.

        Args:
            raw_product: Raw product data
            brand: Brand name

        Yields:
            Phase completion events with progress
        """
        execution_id = f"pipeline-{datetime.now().isoformat()}"

        self.logger.info(f"[CopilotKit] Starting pipeline: {execution_id}")

        # Phase 0: Initialization
        yield {
            'execution_id': execution_id,
            'type': 'pipeline_started',
            'timestamp': datetime.now().isoformat(),
            'product_name': raw_product.get('product_name', 'Unknown'),
            'brand': brand,
            'total_phases': 6
        }

        # Execute pipeline
        result = self.pipeline.execute_full_pipeline(raw_product, brand)

        # Yield phase-by-phase results
        for phase_num, (phase_name, success) in enumerate(result['phase_results'].items(), 1):
            yield {
                'execution_id': execution_id,
                'type': 'phase_completed',
                'phase': phase_num,
                'phase_name': phase_name,
                'success': success,
                'timestamp': datetime.now().isoformat(),
                'progress': f"{phase_num}/6"
            }

            # Small delay to prevent overwhelming frontend
            await asyncio.sleep(0.1)

        # Final result
        yield {
            'execution_id': execution_id,
            'type': 'pipeline_completed',
            'status': result['status'],
            'timestamp': datetime.now().isoformat(),
            'product_name': result['product_name'],
            'brand': result['brand'],
            'errors': result['errors'],
            'phase_results': result['phase_results'],
            'result': {
                'halilit_id': result['draft'].halilit_id if result['draft'] else None,
                'product_name': result['draft'].product_name if result['draft'] else None,
                'status': result['status'],
                'errors': len(result['errors'])
            }
        }

        self.logger.info(
            f"[CopilotKit] Pipeline completed: {result['status']}")

    def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent execution history.

        Args:
            limit: Maximum number of records to return

        Returns:
            Recent execution records
        """
        return list(reversed(self.execution_history[-limit:]))

    def clear_history(self):
        """Clear execution history."""
        self.execution_history = []

    async def stream_ingestion_progress(self,
                                        products: List[Dict[str, Any]],
                                        brand: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute multiple products through pipeline with progress streaming.

        Yields:
            Progress updates for each product and phase
        """
        batch_id = f"batch-{datetime.now().isoformat()}"

        yield {
            'type': 'batch_started',
            'batch_id': batch_id,
            'total_products': len(products),
            'brand': brand,
            'timestamp': datetime.now().isoformat()
        }

        approved_count = 0
        rejected_count = 0

        for product_num, raw_product in enumerate(products, 1):
            async for phase_event in self.execute_full_pipeline(raw_product, brand):
                yield {
                    **phase_event,
                    'batch_id': batch_id,
                    'product_number': product_num,
                    'product_total': len(products)
                }

                # Track approval status
                if phase_event.get('type') == 'pipeline_completed':
                    if phase_event.get('status') == 'APPROVED':
                        approved_count += 1
                    else:
                        rejected_count += 1

        # Batch complete
        yield {
            'type': 'batch_completed',
            'batch_id': batch_id,
            'total_products': len(products),
            'approved_count': approved_count,
            'rejected_count': rejected_count,
            'approval_rate': f"{(approved_count/len(products)*100):.0f}%" if products else "N/A",
            'timestamp': datetime.now().isoformat()
        }

    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get current pipeline status and capabilities.

        Returns:
            Status information for frontend
        """
        return {
            'status': 'ready',
            'available_skills': self.get_available_skills(),
            'execution_history_count': len(self.execution_history),
            'agents': {
                'commercial_scout': True,
                'official_verifier': True,
                'external_validator': True
            },
            'timestamp': datetime.now().isoformat()
        }
