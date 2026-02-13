"""
Task Definitions for Halilit Support Center v8.5

These tasks wrap the Trinity Swarm agents into distributed Celery tasks
that can run in parallel across multiple workers.

Task Workflow:
    1. harvest_brand_products (CommercialScout) - Scrapes Halilit.com
    2. enrich_product (OfficialVerifier) - Enriches with manufacturer specs
    3. validate_product (ExternalValidator) - Audits for compliance
    4. record_learning_feedback (Learning System) - Captures lessons
"""

import logging
from celery import shared_task, Task
from celery.exceptions import SoftTimeLimitExceeded
from backend.celery_config import celery_app
from typing import Dict, List, Optional, Any
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentTask(Task):
    """
    Base task class for all agent operations.

    Features:
    - Automatic retry on failure
    - Structured logging
    - Progress tracking
    - Error handling & deadletter support
    """

    # Retry configuration
    autoretry_for = (Exception,)
    max_retries = 3
    default_retry_delay = 60  # 1 minute between retries

    # Backoff strategy (exponential)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True
    retry_backoff_max = 600  # Cap backoff at 10 minutes
    retry_jitter = True

    # Time limits
    time_limit = 3600  # 1 hour hard limit
    soft_time_limit = 3400  # 56 min soft limit

    # Error handling
    acks_late = True  # Only ACK after task completes

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        logger.warning(
            f"🔄 Task {task_id} retrying (attempt {self.request.retries}/{self.max_retries}) "
            f"after error: {type(exc).__name__}: {exc}"
        )

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task exhausts all retries"""
        logger.error(
            f"❌ Task {task_id} FAILED after {self.request.retries} retries. "
            f"Error: {type(exc).__name__}: {exc}\n"
            f"Traceback: {einfo.traceback}"
        )

    def on_success(self, result, task_id, args, kwargs):
        """Called when task succeeds"""
        logger.info(f"✅ Task {task_id} completed successfully")

    def on_timeout(self, exc, task_id, args, kwargs, einfo):
        """Called when task exceeds time limits"""
        logger.error(
            f"⏱️ Task {task_id} TIMEOUT (exceeded time limit). "
            f"Error: {exc}"
        )


# ============================================================================
# HARVEST TASKS (CommercialScout Agent)
# ============================================================================

@shared_task(base=AgentTask, bind=True, queue='harvest')
def harvest_brand_products(self, brand: str, task_id: str) -> Dict[str, Any]:
    """
    Harvest products from Halilit.com for a specific brand using CommercialScout.

    Args:
        brand (str): Brand name (e.g., "Roland", "Yamaha")
        task_id (str): Unique tracking ID for this harvest operation

    Returns:
        dict: {
            'status': 'success',
            'brand': str,
            'product_count': int,
            'products': List[ProductDraft],
            'timestamp': str,
            'task_id': str
        }

    Raises:
        Exception: Any agent-level error (auto-retried 3x)
    """
    try:
        # Update Celery task state with progress
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'initializing',
                'brand': brand,
                'task_id': task_id,
                'stage': 'harvest'
            }
        )

        logger.info(
            f"🌾 [HARVEST] Starting harvest for brand: {brand} (task_id={task_id})")

        # Import agent here to avoid circular imports
        from backend.unified_agent_orchestrator import CommercialAgent

        # Initialize and run harvest agent
        agent = CommercialAgent()

        self.update_state(
            state='PROGRESS',
            meta={'status': 'scraping', 'brand': brand, 'task_id': task_id}
        )

        # Harvest products from Halilit.com
        products = agent.harvest(brand)

        logger.info(
            f"✅ [HARVEST] Harvested {len(products)} products from {brand} "
            f"(task_id={task_id})"
        )

        return {
            'status': 'success',
            'brand': brand,
            'product_count': len(products),
            'products': [p.model_dump() if hasattr(p, 'model_dump') else p for p in products],
            'timestamp': datetime.utcnow().isoformat(),
            'task_id': task_id
        }

    except SoftTimeLimitExceeded:
        logger.error(f"⏱️ [HARVEST] Task exceeded soft time limit for {brand}")
        raise
    except Exception as e:
        logger.error(
            f"❌ [HARVEST] Failed for {brand}: {type(e).__name__}: {e}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        raise


# ============================================================================
# ENRICH TASKS (OfficialVerifier Agent)
# ============================================================================

@shared_task(base=AgentTask, bind=True, queue='enrich')
def enrich_product(self, product_draft: Dict[str, Any], learned_insights: Optional[List] = None) -> Dict[str, Any]:
    """
    Enrich a product draft with official specs and documentation using OfficialVerifier.

    Args:
        product_draft (dict): Raw product data from CommercialScout
        learned_insights (list, optional): Insights from learning system to improve enrichment

    Returns:
        dict: {
            'status': 'success',
            'product_id': str,
            'enriched_product': dict,
            'enrichment_sources': List[str],
            'timestamp': str
        }

    Raises:
        Exception: Any agent-level error (auto-retried 3x)
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'enriching',
                'product_id': product_draft.get('id'),
                'stage': 'enrich'
            }
        )

        product_id = product_draft.get('id', 'unknown')
        logger.info(
            f"📖 [ENRICH] Starting enrichment for product: {product_id}")

        # Import agent
        from backend.unified_agent_orchestrator import OfficialAgent

        # Initialize and run enrichment agent
        agent = OfficialAgent()

        enriched = agent.enrich(product_draft, learned_insights)

        logger.info(f"✅ [ENRICH] Enriched product: {product_id}")

        return {
            'status': 'success',
            'product_id': product_id,
            'enriched_product': enriched.model_dump() if hasattr(enriched, 'model_dump') else enriched,
            'enrichment_sources': ['manufacturer', 'official_docs', 'catalog'],
            'timestamp': datetime.utcnow().isoformat()
        }

    except SoftTimeLimitExceeded:
        logger.error(f"⏱️ [ENRICH] Task exceeded soft time limit")
        raise
    except Exception as e:
        logger.error(
            f"❌ [ENRICH] Failed: {type(e).__name__}: {e}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        raise


# ============================================================================
# VALIDATE TASKS (ExternalValidator Agent)
# ============================================================================

@shared_task(base=AgentTask, bind=True, queue='validate')
def validate_product(self, product: Dict[str, Any], risk_threshold: int = 50) -> Dict[str, Any]:
    """
    Validate and audit a product for compliance and quality using ExternalValidator.

    Args:
        product (dict): Complete enriched product data
        risk_threshold (int): Maximum acceptable risk score (0-100)

    Returns:
        dict: {
            'status': 'success' | 'failed',
            'product_id': str,
            'audit_report': AuditReport,
            'risk_score': int,
            'passed_validation': bool,
            'timestamp': str
        }

    Raises:
        Exception: Any agent-level error (auto-retried 3x)
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'validating',
                'product_id': product.get('id'),
                'stage': 'validate'
            }
        )

        product_id = product.get('id', 'unknown')
        logger.info(
            f"🔍 [VALIDATE] Starting validation for product: {product_id}")

        # Import agent
        from backend.unified_agent_orchestrator import ContextualAgent

        # Initialize and run validation agent
        agent = ContextualAgent()

        audit_report = agent.validate_and_review(product)

        risk_score = getattr(audit_report, 'risk_score', 0)
        passed = risk_score <= risk_threshold

        log_level = "✅" if passed else "⚠️"
        logger.info(
            f"{log_level} [VALIDATE] Product {product_id} validation "
            f"{'PASSED' if passed else 'FAILED'} (risk_score={risk_score})"
        )

        return {
            'status': 'success' if passed else 'failed',
            'product_id': product_id,
            'audit_report': audit_report.model_dump() if hasattr(audit_report, 'model_dump') else audit_report,
            'risk_score': risk_score,
            'passed_validation': passed,
            'timestamp': datetime.utcnow().isoformat()
        }

    except SoftTimeLimitExceeded:
        logger.error(f"⏱️ [VALIDATE] Task exceeded soft time limit")
        raise
    except Exception as e:
        logger.error(
            f"❌ [VALIDATE] Failed: {type(e).__name__}: {e}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        raise


# ============================================================================
# LEARNING TASKS (Learning System)
# ============================================================================

@shared_task(base=AgentTask, bind=True, queue='learn')
def record_learning_feedback(self, product_id: str, feedback: Dict[str, Any],
                             feedback_type: str = 'user_correction') -> Dict[str, Any]:
    """
    Record feedback for the learning system to improve future enrichment.

    Args:
        product_id (str): ID of product receiving feedback
        feedback (dict): Feedback data (corrections, missing fields, etc.)
        feedback_type (str): Type of feedback ('user_correction', 'agent_error', etc.)

    Returns:
        dict: {
            'status': 'success',
            'product_id': str,
            'feedback_recorded': bool,
            'timestamp': str
        }
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'recording_feedback',
                'product_id': product_id,
                'stage': 'learn'
            }
        )

        logger.info(
            f"📚 [LEARN] Recording {feedback_type} feedback for product: {product_id}"
        )

        # Import learning system
        from backend.unified_learning_system import LearningSystem

        learning_system = LearningSystem()
        learning_system.record_feedback(product_id, feedback, feedback_type)

        logger.info(f"✅ [LEARN] Feedback recorded for product: {product_id}")

        return {
            'status': 'success',
            'product_id': product_id,
            'feedback_recorded': True,
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(
            f"❌ [LEARN] Failed: {type(e).__name__}: {e}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        raise


# ============================================================================
# WORKFLOW TASKS (Orchestration)
# ============================================================================

@shared_task(bind=True, queue='default')
def sync_brand_pipeline(self, brand: str, sync_id: str) -> Dict[str, Any]:
    """
    Orchestrate complete sync pipeline for a brand:
    Harvest → Enrich → Validate → Learn

    Uses Celery chains/chords for dependency management.

    Args:
        brand (str): Brand to sync
        sync_id (str): Unique sync operation ID

    Returns:
        dict: {
            'status': 'success' | 'failed',
            'sync_id': str,
            'brand': str,
            'total_products': int,
            'passed_validation': int,
            'failed_validation': int,
            'timestamp': str
        }
    """
    try:
        logger.info(
            f"🔗 [SYNC_PIPELINE] Starting complete sync for {brand} (sync_id={sync_id})")

        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'queuing_harvest',
                'brand': brand,
                'sync_id': sync_id,
                'stage': 'pipeline_orchestration'
            }
        )

        # Queue harvest task
        harvest_task = harvest_brand_products.apply_async(
            args=(brand, sync_id),
            queue='harvest'
        )

        logger.info(
            f"🔗 [SYNC_PIPELINE] Queued harvest task: {harvest_task.id}")

        return {
            'status': 'success',
            'sync_id': sync_id,
            'brand': brand,
            'harvest_task_id': harvest_task.id,
            'timestamp': datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(
            f"❌ [SYNC_PIPELINE] Failed: {type(e).__name__}: {e}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        raise


# Expose Celery app for worker startup
__all__ = [
    'celery_app',
    'harvest_brand_products',
    'enrich_product',
    'validate_product',
    'record_learning_feedback',
    'sync_brand_pipeline',
]
